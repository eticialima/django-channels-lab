import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, ClientSession


class SupportConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for support chat system."""

    async def connect(self):
        """Handle WebSocket connection."""
        # Extract room_type from URL path
        path = self.scope.get('path', '')
        user = self.scope.get('user')
        is_authenticated = user and user.is_authenticated
        is_staff = user and user.is_staff if is_authenticated else False
        
        if 'support/client' in path:
            self.room_type = 'client'
            self.room_group_name = 'support_clients'
            self.client_id = None
            self.is_admin = False
        elif 'support/admin' in path:
            self.room_type = 'admin'
            self.room_group_name = 'support_admin'
            self.client_id = None
            self.is_admin = is_staff
        elif 'support/chat' in path:
            self.room_type = 'chat'
            # Extract room_id from URL
            self.client_id = self.scope.get('url_route', {}).get('kwargs', {}).get('room_id', 'default')
            self.room_group_name = f'support_chat_{self.client_id}'
            # Admin connects via /support/admin/chat/{id} page, client via /support/
            self.is_admin = is_staff
        else:
            # Default to client mode
            self.room_type = 'client'
            self.room_group_name = 'support_clients'
            self.client_id = None
            self.is_admin = False
        
        self.username = None
        self.client_session = None

        # Log connection
        print(f"WebSocket: {self.room_type} connecting to {self.room_group_name}, is_admin={self.is_admin}")

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

        # Mark client session as inactive
        if self.client_session:
            await self.mark_session_inactive()

            # Notify admin that client disconnected
            await self.channel_layer.group_send(
                'support_admin',
                {
                    'type': 'client_disconnected',
                    'client_id': str(self.client_session.id),
                    'client_name': self.username,
                }
            )

    async def receive(self, text_data):
        """Receive message from WebSocket."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            print(f"ERROR: Invalid JSON received: {text_data}")
            return
        
        message_type = data.get('type')
        print(f"DEBUG: {self.room_type} received message type: {message_type}")

        # Support both 'client_join' (new) and 'user_join' (legacy)
        if message_type in ('client_join', 'user_join'):
            # Client joins support system
            self.username = data.get('username')
            print(f"DEBUG: Client joining as {self.username}")
            
            try:
                self.client_session = await self.create_client_session(self.username)
                print(f"DEBUG: ClientSession created: {self.client_session.id}")
            except Exception as e:
                print(f"ERROR creating ClientSession: {e}")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Failed to create session: {str(e)}',
                }))
                return
            
            # Add client to their own 1:1 chat group
            private_room = f'support_chat_{self.client_session.id}'
            await self.channel_layer.group_add(private_room, self.channel_name)
            print(f"DEBUG: Client added to private room: {private_room}")
            
            # Notify admin about new client
            await self.channel_layer.group_send(
                'support_admin',
                {
                    'type': 'new_client_joined',
                    'client_id': str(self.client_session.id),
                    'client_name': self.username,
                }
            )
            
            # Send confirmation to client
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'client_id': str(self.client_session.id),
                'message': 'Connected to support. Waiting for admin...',
            }))
            print(f"DEBUG: Connection confirmation sent to {self.username}")

        elif message_type == 'client_message':
            # Client sends message
            message = data.get('message')
            print(f"DEBUG: Client message from {self.username}: {message}")
            
            if self.client_session:
                try:
                    # Save message to database
                    await self.save_message(
                        self.client_session,
                        self.username,
                        message,
                        'client'
                    )
                except Exception as e:
                    print(f"ERROR saving message: {e}")
                
                # Send to admin in the 1:1 chat room
                # (client is also in this group, so they'll receive it too)
                await self.channel_layer.group_send(
                    f'support_chat_{self.client_session.id}',
                    {
                        'type': 'chat_message',
                        'username': self.username,
                        'message': message,
                        'sender_type': 'client',
                    }
                )
                print(f"DEBUG: Message sent to group")

        elif message_type == 'admin_message':
            # Admin sends message to client
            message = data.get('message')
            client_id = data.get('client_id')
            admin_name = data.get('admin_name', 'Admin')
            
            print(f"DEBUG: Admin message to {client_id}: {message}")
            
            try:
                # Save message to database
                client_session = await self.get_client_session(client_id)
                if client_session:
                    await self.save_message(
                        client_session,
                        admin_name,
                        message,
                        'admin'
                    )
            except Exception as e:
                print(f"ERROR saving admin message: {e}")
            
            # Send to client and admin chat room (even if DB save failed)
            await self.channel_layer.group_send(
                f'support_chat_{client_id}',
                {
                    'type': 'chat_message',
                    'username': admin_name,
                    'message': message,
                    'sender_type': 'admin',
                }
            )

        elif message_type == 'admin_get_clients':
            # Admin requests list of connected clients
            try:
                clients = await self.get_active_clients()
                print(f"DEBUG: Sending {len(clients)} active clients to admin")
                await self.send(text_data=json.dumps({
                    'type': 'clients_list',
                    'clients': clients,
                }))
            except Exception as e:
                print(f"ERROR getting active clients: {e}")
                await self.send(text_data=json.dumps({
                    'type': 'clients_list',
                    'clients': [],
                    'error': str(e),
                }))

    # Message handlers for group sends
    async def chat_message(self, event):
        """Receive message from room group."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'username': event['username'],
            'message': event['message'],
            'sender_type': event.get('sender_type', 'client'),
        }))

    async def new_client_joined(self, event):
        """Notify admin about new client."""
        await self.send(text_data=json.dumps({
            'type': 'new_client_joined',
            'client_id': event['client_id'],
            'client_name': event['client_name'],
        }))

    async def client_disconnected(self, event):
        """Notify admin about client disconnection."""
        await self.send(text_data=json.dumps({
            'type': 'client_disconnected',
            'client_id': event['client_id'],
            'client_name': event['client_name'],
        }))

    # Database operations
    @database_sync_to_async
    def create_client_session(self, client_name):
        """Create new client session."""
        return ClientSession.objects.create(
            client_name=client_name,
            is_active=True
        )

    @database_sync_to_async
    def mark_session_inactive(self):
        """Mark session as inactive."""
        if self.client_session:
            self.client_session.is_active = False
            self.client_session.save()

    @database_sync_to_async
    def save_message(self, client_session, username, content, message_type='client'):
        """Save message to database."""
        return Message.objects.create(
            client_session=client_session,
            username=username,
            content=content,
            message_type=message_type
        )

    @database_sync_to_async
    def get_client_session(self, client_id):
        """Get client session by ID."""
        try:
            return ClientSession.objects.get(id=client_id)
        except ClientSession.DoesNotExist:
            return None

    @database_sync_to_async
    def get_active_clients(self):
        """Get list of active clients."""
        clients = ClientSession.objects.filter(is_active=True).values(
            'id', 'client_name', 'connected_at'
        )
        return [
            {
                'id': str(c['id']),
                'name': c['client_name'],
                'connected_at': c['connected_at'].isoformat()
            }
            for c in clients
        ]
