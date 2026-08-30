import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for chat functionality."""

    async def connect(self):
        """Handle WebSocket connection."""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.username = None

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Notify other users that this user left
        if self.username:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'username': self.username,
                }
            )

    async def receive(self, text_data):
        """Receive message from WebSocket."""
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'user_join':
            # User joins the chat
            self.username = data.get('username')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'username': self.username,
                }
            )

        elif message_type == 'chat_message':
            # User sends a message
            message = data.get('message')

            # Save message to database
            await self.save_message(self.username, message)

            # Broadcast to all users in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'username': self.username,
                    'message': message,
                }
            )

    async def chat_message(self, event):
        """Receive message from room group."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'username': event['username'],
            'message': event['message'],
        }))

    async def user_joined(self, event):
        """Notify user joined."""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username'],
        }))

    async def user_left(self, event):
        """Notify user left."""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username'],
        }))

    @database_sync_to_async
    def save_message(self, username, content):
        """Save message to database."""
        Message.objects.create(username=username, content=content)
