from django.shortcuts import render
from .models import Message


def index(request):
    """Display home page where user enters their name."""
    return render(request, 'index.html')


def room(request, room_name):
    """Display chat room."""
    messages = Message.objects.all()
    
    # Convert room_name slug back to original format for display
    # Example: "leticia-teste1" -> "Leticia Teste1"
    display_name = room_name.replace('-', ' ').title()
    
    return render(request, 'room.html', {
        'room_name': room_name,
        'display_name': display_name,
        'messages': messages
    })
