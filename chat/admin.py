from django.contrib import admin
from .models import Message, ClientSession


@admin.register(ClientSession)
class ClientSessionAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'is_active', 'connected_at', 'last_activity')
    list_filter = ('is_active', 'connected_at')
    search_fields = ('client_name',)
    readonly_fields = ('id', 'connected_at', 'last_activity')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('username', 'message_type', 'client_session', 'timestamp')
    list_filter = ('message_type', 'timestamp')
    search_fields = ('username', 'content')
    readonly_fields = ('timestamp',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('client_session')
