import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import close_old_connections

from jokes.models import Session, Player, Prompt, Response


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        room_name = self.scope['url_route']['kwargs']['room_name']
        player_name = self.scope['url_route']['kwargs']['player_name']
        self.room_name = room_name.replace(' ', '-')
        self.session: Session = await self.get_session(room_name)
        self.player: Player = await self.get_player(player_name)
        self.room_group_name = 'chat_%s' % self.room_name

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
        print("Received message: {}".format(text_data))
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
            await self.send(text_data=json.dumps({
                "type": "begin_voting",
            }))

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
        print("Saving response for player {} from event {}".format(
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
            print("Closing session {}...".format(self.session.name))
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
            return True
        return False
