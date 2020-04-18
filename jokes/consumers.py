import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from jokes.models import Session, Player


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name'].replace(' ', '-')
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        await self.channel_layer.group_send(
            self.room_group_name,
            text_data_json
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Broadcast back to clients
        await self.send(text_data=json.dumps(event))

    async def user_joined(self, event):
        # Broadcast back to clients
        await self.send(text_data=json.dumps(event))

    async def player_readied(self, event):
        await self.ready_player(event["username"])
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def ready_player(self, player_name):
        player: Player = Player.objects.get(name=player_name)
        player.is_ready = True
        player.save()
