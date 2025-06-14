import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications"""
    
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.user_group = f"user_{self.user.uuid}"
        
        # Join user's personal notification group
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        
        await self.accept()
        
        # Send pending notifications
        await self.send_pending_notifications()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'mark_read':
            await self.mark_notification_read(data.get('notification_id'))
        elif action == 'mark_all_read':
            await self.mark_all_read()
    
    async def notification_send(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
    
    @database_sync_to_async
    def send_pending_notifications(self):
        from core.models import Notification
        notifications = Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).order_by('-created_at')[:10]
        
        for notification in notifications:
            self.send(text_data=json.dumps({
                'type': 'notification',
                'notification': {
                    'id': str(notification.uuid),
                    'type': notification.notification_type,
                    'title': notification.title,
                    'message': notification.message,
                    'created_at': notification.created_at.isoformat(),
                }
            }))
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        from core.models import Notification
        Notification.objects.filter(
            uuid=notification_id,
            recipient=self.user
        ).update(is_read=True, read_at=timezone.now())
    
    @database_sync_to_async
    def mark_all_read(self):
        from core.models import Notification
        Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for live discussions/chat"""
    
    async def connect(self):
        self.user = self.scope["user"]
        self.discussion_id = self.scope['url_route']['kwargs']['discussion_id']
        self.discussion_group = f"discussion_{self.discussion_id}"
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Check if user has access to this discussion
        if not await self.has_access():
            await self.close()
            return
        
        # Join discussion group
        await self.channel_layer.group_add(
            self.discussion_group,
            self.channel_name
        )
        
        await self.accept()
        
        # Notify others about user joining
        await self.channel_layer.group_send(
            self.discussion_group,
            {
                'type': 'user_join',
                'user': {
                    'id': str(self.user.uuid),
                    'name': self.user.get_full_name(),
                    'avatar': self.user.avatar.url if self.user.avatar else None,
                }
            }
        )
    
    async def disconnect(self, close_code):
        if hasattr(self, 'discussion_group'):
            # Notify others about user leaving
            await self.channel_layer.group_send(
                self.discussion_group,
                {
                    'type': 'user_leave',
                    'user_id': str(self.user.uuid)
                }
            )
            
            await self.channel_layer.group_discard(
                self.discussion_group,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'message':
            await self.handle_message(data)
        elif message_type == 'typing':
            await self.handle_typing(data)
    
    async def handle_message(self, data):
        """Handle new chat message"""
        content = data.get('content')
        parent_id = data.get('parent_id')
        
        # Save message to database
        reply = await self.save_reply(content, parent_id)
        
        # Broadcast to group
        await self.channel_layer.group_send(
            self.discussion_group,
            {
                'type': 'chat_message',
                'message': {
                    'id': str(reply.uuid),
                    'content': content,
                    'author': {
                        'id': str(self.user.uuid),
                        'name': self.user.get_full_name(),
                        'avatar': self.user.avatar.url if self.user.avatar else None,
                        'role': self.user.get_role_display(),
                    },
                    'parent_id': parent_id,
                    'created_at': reply.created_at.isoformat(),
                }
            }
        )
    
    async def handle_typing(self, data):
        """Handle typing indicator"""
        await self.channel_layer.group_send(
            self.discussion_group,
            {
                'type': 'user_typing',
                'user_id': str(self.user.uuid),
                'is_typing': data.get('is_typing', False)
            }
        )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def user_join(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def user_leave(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def user_typing(self, event):
        if event['user_id'] != str(self.user.uuid):
            await self.send(text_data=json.dumps(event))
    
    @database_sync_to_async
    def has_access(self):
        from core.models import Discussion
        try:
            discussion = Discussion.objects.get(uuid=self.discussion_id)
            course = discussion.forum.course
            
            # Check if user is enrolled or is instructor
            return (
                course.enrollments.filter(student=self.user, is_active=True).exists() or
                course.instructor == self.user or
                self.user in course.co_instructors.all() or
                self.user.is_staff
            )
        except Discussion.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_reply(self, content, parent_id=None):
        from core.models import Discussion, Reply
        
        discussion = Discussion.objects.get(uuid=self.discussion_id)
        parent = None
        if parent_id:
            parent = Reply.objects.get(uuid=parent_id)
        
        return Reply.objects.create(
            discussion=discussion,
            author=self.user,
            content=content,
            parent=parent,
            is_instructor_reply=self.user.role in ['teacher', 'moderator', 'manager']
        )


class LiveLessonConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for live lessons/webinars"""
    
    async def connect(self):
        self.user = self.scope["user"]
        self.lesson_id = self.scope['url_route']['kwargs']['lesson_id']
        self.lesson_group = f"live_lesson_{self.lesson_id}"
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Check access
        if not await self.has_lesson_access():
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.lesson_group,
            self.channel_name
        )
        
        await self.accept()
        
        # Track attendance
        await self.track_attendance(True)
    
    async def disconnect(self, close_code):
        if hasattr(self, 'lesson_group'):
            await self.track_attendance(False)
            await self.channel_layer.group_discard(
                self.lesson_group,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'question':
            await self.handle_question(data)
        elif action == 'poll_response':
            await self.handle_poll_response(data)
    
    @database_sync_to_async
    def has_lesson_access(self):
        from courses.models import Lesson
        try:
            lesson = Lesson.objects.get(uuid=self.lesson_id)
            course = lesson.module.course
            
            return (
                course.enrollments.filter(student=self.user, is_active=True).exists() or
                course.instructor == self.user or
                self.user.is_staff
            )
        except Lesson.DoesNotExist:
            return False
    
    @database_sync_to_async
    def track_att