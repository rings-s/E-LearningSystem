from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<discussion_id>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/live-lesson/(?P<lesson_id>[^/]+)/$', consumers.LiveLessonConsumer.as_asgi()),
]