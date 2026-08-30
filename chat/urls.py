from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Support system routes
    path('support/', views.support_client, name='support_client'),
    path('support/admin/', views.support_admin, name='support_admin'),
    path('support/admin/<uuid:client_id>/', views.support_admin_chat, name='support_admin_chat'),
    
    # API endpoints
    path('api/support/chat/<uuid:client_id>/messages/', views.get_client_messages, name='get_client_messages'),
]
