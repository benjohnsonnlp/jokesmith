import asyncio
import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import close_old_connections, transaction

from jokes.models import Session, Player, Prompt, Response, Vote


logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):

    def log(self, msg, level=logging.INFO):
        logger.log(level, msg)

    async def connect(self):
        room_name = self.scope['url_route']['kwargs']['room_name']
        player_name = self.scope['url_route']['kwargs']['player_name']
        self.room_name = room_name.replace(' ', '-')
        self.session: Session = await self.get_session(room_name)
        self.player: Player = await self.get_player(player_name)
        self.room_group_name = 'chat_%s' % self.room_name

        await self.reset_voting_status()
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.disconnect_db()
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        self.log("Received message: {}".format(text_data))
        text_data_json = json.loads(text_data)

        await self.channel_layer.group_send(
            self.room_group_name,
            text_data_json
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Broadcast back to clients
        await self.send(text_data=json.dumps(event))

    async def all_prompts_submitted(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_joined(self, event):
        # Broadcast back to clients
        await self.send(text_data=json.dumps(event))

    async def display_results(self, event):
        prompt, votes = await self.get_voting_results(event['response_id'])
        await self.send(text_data=json.dumps(
            {
                "type": "display_results",
                "prompt": prompt.dict(),
                "results": votes,
                "players": await self.get_session_players(),
            },
            indent=2
        ))

        await asyncio.sleep(15)
        await self.reset_voting_status()
        await self.remove_responses(prompt)
        if await self.still_voting():
            await self.send(text_data=json.dumps({
                "type": "begin_voting",
            }, indent=2))
        else:
            await self.reset_players()
            await self.send(text_data=json.dumps({
                "type": "reset_session",
            }, indent=2))

    async def vote_submission(self, event):
        player: Player = await self.get_player(event['player'])
        if player == self.player:
            await self.add_vote(event)
            if await self.all_voted():
                # await self.reset_voting_status()
                self.log("Telling clients to display results")
                await self.channel_layer.group_send(
                    self.room_group_name, {
                        "type": "display_results",
                        "response_id": event['response_id']
                    })

    async def player_readied(self, event):
        await self.ready_player(event["username"])

        await self.send(text_data=json.dumps(event))
        if await self.match_ready():
            await self.send(text_data=json.dumps({
                "type": "start_match",
            }))

    async def response_submission(self, event):
        player: Player = await self.get_player(event['player'])
        if player == self.player:
            unanswered = await self.save_responses(event)
            if unanswered:
                await self.send(text_data=json.dumps({
                    "type": "next_question",
                }))

        await self.send(text_data=json.dumps({
            "type": event["type"],
            "player": player.name,
        }))

        # check if all are submitted
        if await self.all_responses_submitted():
            self.log("Broadcasting that all responses were submitted")
            await self.reset_voting_status()
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "begin_voting",
                })

    async def begin_voting(self, event):
        await self.send(text_data=json.dumps(event))

    async def prompt_submission(self, event):
        player: Player = await self.get_player(event['player'])
        await self.send(text_data=json.dumps({
            "type": event["type"],
            "player": player.name,
        }))

        if player == self.player:
            print("Adding prompts {} to player {}".format(event['prompts'], player))
            if await self.record_prompts(event):
                print("Broadcasting that all prompts are submitted")
                await self.start_match()
                await self.channel_layer.group_send(
                    self.room_group_name, {
                        "type": "all_prompts_submitted",
                    })

    @database_sync_to_async
    def save_responses(self, event):
        self.log("Saving response for player {} from event {}".format(
            self.player.name,
            event['response_id']
        ))
        close_old_connections()
        response: Response = Response.objects.get(pk=event['response_id'])
        response.text = event['text']
        response.save()
        return self.player.get_unanswered_questions()

    @database_sync_to_async
    def ready_player(self, player_name):
        close_old_connections()
        player: Player = Player.objects.get(name=player_name)
        player.is_ready = True
        player.voted = False
        player.save()

    @database_sync_to_async
    def get_session(self, room_name) -> Session:
        close_old_connections()
        session: Session = Session.objects.get(pk=room_name)
        return session

    @database_sync_to_async
    def match_ready(self):
        close_old_connections()
        ready = True
        player: Player
        players = list(self.session.player_set.all())
        for player in players:
            if not player.is_ready:
                ready = False
        if len(players) > 2 and ready:
            self.session.started = True
            self.session.save()
            return True
        return False

    @database_sync_to_async
    def get_player(self, player_name):
        close_old_connections()
        player: Player = Player.objects.get(pk=player_name)
        return player

    @database_sync_to_async
    def disconnect_db(self):
        close_old_connections()
        self.player.session = None
        self.player.is_ready = False
        self.player.submitted_prompts = False
        self.player.save()
        players = list(self.session.player_set.all())
        if not players:
            self.log("Closing session {}...".format(self.session.name))
            self.session.delete()

    @database_sync_to_async
    def record_prompts(self, event):
        self.player.submitted_prompts = True
        self.player.save()
        for prompt_text in event['prompts']:
            if prompt_text:
                prompt: Prompt = Prompt(text=prompt_text, author=self.player)
                prompt.save()
        all_submitted = True
        for player in self.session.player_set.all():
            if not player.submitted_prompts:
                all_submitted = False
        return all_submitted

    @database_sync_to_async
    def start_match(self):
        self.session.build_responses()

    @database_sync_to_async
    def all_responses_submitted(self):
        if not self.session.response_set.filter(text=""):
            self.session.status = 'voting'
            self.session.save()
            return True
        return False

    @database_sync_to_async
    def add_vote(self, event):
        with transaction.atomic():
            response: Response = Response.objects.get(pk=event['response_id'])
            author: Player = response.player
            author.increase_score()
            self.player.refresh_from_db()
            self.player.voted = True
            self.player.save()
            vote: Vote = Vote(player=self.player, response_id=event['response_id'], session=self.session)
            vote.save()

    @database_sync_to_async
    def all_voted(self):
        total_players = 0
        voting_players = 0
        for player in self.session.player_set.all():
            total_players += 1
            if player.voted:
                voting_players += 1
        return total_players == voting_players + 2

    @database_sync_to_async
    def reset_voting_status(self):
        self.log("Resetting players to voted = False...")
        for player in self.session.player_set.all():
            player.voted = False
            player.save()
            self.log("{} reset.".format(player))

    @database_sync_to_async
    def get_voting_results(self, response_id):
        prompt: Prompt = Response.objects.get(pk=response_id).prompt
        votes = []
        for response in prompt.response_set.filter(session=self.session):
            votes.append({
                "response": response.dict(),
                "votes": [v.dict() for v in response.vote_set.all()]
            })
        return prompt, votes

    @database_sync_to_async
    def remove_responses(self, prompt):
        for response in prompt.response_set.filter(session=self.session):
            response.delete()

    @database_sync_to_async
    def still_voting(self):
        return list(self.session.response_set.all())

    @database_sync_to_async
    def reset_players(self):
        self.session.status = 'start'
        self.session.started = False
        self.session.save()
        self.log("Resetting players for new round...")
        response: Response
        for response in self.session.response_set.all():
            response.delete()
        for player in self.session.player_set.all():
            player.voted = False
            player.is_ready = False
            player.submitted_prompts = False

            player.save()
            self.log("{} reset.".format(player))

    @database_sync_to_async
    def get_session_players(self):
        return [p.dict() for p in self.session.player_set.all()]
