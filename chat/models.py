from django.db import models
import uuid


class ClientSession(models.Model):
    """Tracks connected clients for support system."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_name = models.CharField(max_length=100)
    connected_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-connected_at']

    def __str__(self):
        return f"{self.client_name} - {self.connected_at}"


class Message(models.Model):
    """Chat message model."""
    client_session = models.ForeignKey(
        ClientSession, 
        on_delete=models.CASCADE, 
        related_name='messages',
        null=True,
        blank=True
    )
    username = models.CharField(max_length=100)
    content = models.TextField()
    message_type = models.CharField(
        max_length=20,
        choices=[
            ('client', 'Client Message'),
            ('admin', 'Admin Message'),
            ('system', 'System Message'),
        ],
        default='client'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.username}: {self.content[:50]}"
