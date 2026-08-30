from django.test import TestCase
from channels.testing import WebsocketCommunicator
from chat.consumers import SupportConsumer
from chat.models import ClientSession, Message
import json
import asyncio


class SupportSystemTestCase(TestCase):
    """Test cases for support system."""

    @staticmethod
    def async_to_sync(coro):
        """Convert async function to sync for testing."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    def test_client_connection(self):
        """Test client can connect to WebSocket."""
        async def test():
            communicator = WebsocketCommunicator(
                SupportConsumer.as_asgi(),
                "/ws/support/client/",
                headers=[(b'origin', b'http://testserver')]
            )
            connected, subprotocol = await communicator.connect()
            self.assertTrue(connected)
            await communicator.disconnect()
        
        self.async_to_sync(test())

    def test_admin_connection(self):
        """Test admin can connect to WebSocket."""
        async def test():
            communicator = WebsocketCommunicator(
                SupportConsumer.as_asgi(),
                "/ws/support/admin/",
                headers=[(b'origin', b'http://testserver')]
            )
            connected, subprotocol = await communicator.connect()
            self.assertTrue(connected)
            await communicator.disconnect()
        
        self.async_to_sync(test())

    def test_client_join_creates_session(self):
        """Test client join creates ClientSession."""
        async def test():
            communicator = WebsocketCommunicator(
                SupportConsumer.as_asgi(),
                "/ws/support/client/",
                headers=[(b'origin', b'http://testserver')]
            )
            connected, subprotocol = await communicator.connect()
            self.assertTrue(connected)
            
            # Send client_join message
            await communicator.send_json_to({
                'type': 'client_join',
                'username': 'Test Client',
            })
            
            # Receive connection confirmation
            try:
                response = await asyncio.wait_for(
                    communicator.receive_json_from(), 
                    timeout=2.0
                )
                self.assertEqual(response['type'], 'connection_established')
            except asyncio.TimeoutError:
                self.fail("Did not receive connection_established message")
            
            # Check if ClientSession was created
            sessions = ClientSession.objects.filter(client_name='Test Client')
            self.assertTrue(sessions.exists())
            
            await communicator.disconnect()
        
        self.async_to_sync(test())


class ModelTestCase(TestCase):
    """Test cases for models."""

    def test_client_session_creation(self):
        """Test ClientSession model creation."""
        session = ClientSession.objects.create(
            client_name='Test User',
            is_active=True
        )
        self.assertEqual(session.client_name, 'Test User')
        self.assertTrue(session.is_active)

    def test_message_creation(self):
        """Test Message model creation."""
        session = ClientSession.objects.create(
            client_name='Test User',
            is_active=True
        )
        message = Message.objects.create(
            client_session=session,
            username='Test User',
            content='Test message',
            message_type='client'
        )
        self.assertEqual(message.content, 'Test message')
        self.assertEqual(message.message_type, 'client')
        self.assertEqual(message.client_session, session)

    def test_message_ordering(self):
        """Test messages are ordered by timestamp."""
        session = ClientSession.objects.create(
            client_name='Test User',
            is_active=True
        )
        msg1 = Message.objects.create(
            client_session=session,
            username='User',
            content='First',
            message_type='client'
        )
        msg2 = Message.objects.create(
            client_session=session,
            username='Admin',
            content='Second',
            message_type='admin'
        )
        
        messages = Message.objects.all()
        self.assertEqual(list(messages), [msg1, msg2])

    def test_active_clients_query(self):
        """Test filtering active clients."""
        # Create active client
        active = ClientSession.objects.create(
            client_name='Active User',
            is_active=True
        )
        # Create inactive client
        inactive = ClientSession.objects.create(
            client_name='Inactive User',
            is_active=False
        )
        
        active_clients = ClientSession.objects.filter(is_active=True)
        self.assertEqual(active_clients.count(), 1)
        self.assertEqual(active_clients.first(), active)

