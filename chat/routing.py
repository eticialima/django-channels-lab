from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Support system routes
    re_path(r'ws/support/client/$', consumers.SupportConsumer.as_asgi()),
    re_path(r'ws/support/admin/$', consumers.SupportConsumer.as_asgi()),
    re_path(r'ws/support/chat/(?P<room_id>[\w-]+)/$', consumers.SupportConsumer.as_asgi()),
]
