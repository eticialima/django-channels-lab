from django.db import models


class Message(models.Model):
    """Chat message model."""
    username = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.username}: {self.content[:50]}"
