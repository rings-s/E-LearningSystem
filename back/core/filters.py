# back/core/filters.py - Add UUID validation to filters

import django_filters
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import Discussion, Notification, ActivityLog, Announcement
from .utils import validate_uuid
import uuid  # Use built-in uuid module

class UUIDFilter(django_filters.CharFilter):
    """Custom filter for UUID fields with validation"""
    
    def filter(self, qs, value):
        if value:
            try:
                # Validate UUID format
                validate_uuid(value)
                return super().filter(qs, value)
            except ValidationError:
                # Return empty queryset for invalid UUIDs
                return qs.none()
        return qs

class DiscussionFilter(django_filters.FilterSet):
    forum = UUIDFilter(field_name='forum__uuid')  # Use custom UUID filter
    author = UUIDFilter(field_name='author__uuid')  # Use custom UUID filter
    discussion_type = django_filters.ChoiceFilter(choices=Discussion.DISCUSSION_TYPE_CHOICES)
    is_pinned = django_filters.BooleanFilter()
    is_resolved = django_filters.BooleanFilter()
    search = django_filters.CharFilter(method='search_filter')
    
    class Meta:
        model = Discussion
        fields = ['forum', 'author', 'discussion_type', 'is_pinned', 'is_resolved']
    
    def search_filter(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(title__icontains=value) | Q(content__icontains=value)
        )

class NotificationFilter(django_filters.FilterSet):
    notification_type = django_filters.ChoiceFilter(choices=Notification.NOTIFICATION_TYPE_CHOICES)
    is_read = django_filters.BooleanFilter()
    course = UUIDFilter(field_name='course__uuid')  # Use custom UUID filter
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    
    class Meta:
        model = Notification
        fields = ['notification_type', 'is_read', 'course']

class ActivityLogFilter(django_filters.FilterSet):
    user = UUIDFilter(field_name='user__uuid')  # Use custom UUID filter
    activity_type = django_filters.ChoiceFilter(choices=ActivityLog.ACTIVITY_TYPE_CHOICES)
    course = UUIDFilter(field_name='course__uuid')  # Use custom UUID filter
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = ActivityLog
        fields = ['user', 'activity_type', 'course']