from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/training/(?P<session_id>\w+)/$', consumers.TrainingConsumer.as_asgi()),
    re_path(r'ws/system-monitor/$', consumers.SystemMonitorConsumer.as_asgi()),
] 