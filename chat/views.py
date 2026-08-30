from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
import json
from .models import Message, ClientSession


def support_client(request):
    """Support page for clients to enter their name and wait for admin."""
    return render(request, 'support/client.html')


@staff_member_required
def support_admin(request):
    """Admin dashboard showing all connected clients."""
    active_clients = ClientSession.objects.filter(is_active=True).order_by('-connected_at')
    
    return render(request, 'support/admin.html', {
        'clients': active_clients
    })


@staff_member_required
def support_admin_chat(request, client_id):
    """Admin chat interface with specific client."""
    client_session = get_object_or_404(ClientSession, id=client_id)
    messages = Message.objects.filter(client_session=client_session)
    
    return render(request, 'support/admin_chat.html', {
        'client_session': client_session,
        'messages': messages
    })


def get_client_messages(request, client_id):
    """API endpoint to get message history for a client."""
    try:
        client_session = ClientSession.objects.get(id=client_id)
        messages = Message.objects.filter(client_session=client_session).order_by('timestamp')
        
        messages_data = [
            {
                'username': msg.username,
                'content': msg.content,
                'message_type': msg.message_type,
                'timestamp': msg.timestamp.isoformat(),
            }
            for msg in messages
        ]
        
        return JsonResponse({
            'success': True,
            'client_name': client_session.client_name,
            'messages': messages_data,
        })
    except ClientSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Client session not found',
        }, status=404)
