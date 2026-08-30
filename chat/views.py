from django.shortcuts import render
from .models import Message


def index(request):
    """Display home page where user enters their name."""
    return render(request, 'chat/index.html')


def room(request, room_name):
    """Display chat room."""
    messages = Message.objects.all()
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'messages': messages
    })
