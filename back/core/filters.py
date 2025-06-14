import django_filters
from django.db.models import Q
from .models import Discussion, Notification, ActivityLog, Announcement

class DiscussionFilter(django_filters.FilterSet):
    forum = django_filters.CharFilter(field_name='forum__uuid')
    author = django_filters.CharFilter(field_name='author__uuid')
    discussion_type = django_filters.ChoiceFilter(choices=Discussion.DISCUSSION_TYPE_CHOICES)
    is_pinned = django_filters.BooleanFilter()
    is_resolved = django_filters.BooleanFilter()
    search = django_filters.CharFilter(method='search_filter')
    
    class Meta:
        model = Discussion
        fields = ['forum', 'author', 'discussion_type', 'is_pinned', 'is_resolved']
    
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(content__icontains=value)
        )

class NotificationFilter(django_filters.FilterSet):
    notification_type = django_filters.ChoiceFilter(choices=Notification.NOTIFICATION_TYPE_CHOICES)
    is_read = django_filters.BooleanFilter()
    course = django_filters.CharFilter(field_name='course__uuid')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    
    class Meta:
        model = Notification
        fields = ['notification_type', 'is_read', 'course']

class ActivityLogFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name='user__uuid')
    activity_type = django_filters.ChoiceFilter(choices=ActivityLog.ACTIVITY_TYPE_CHOICES)
    course = django_filters.CharFilter(field_name='course__uuid')
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = ActivityLog
        fields = ['user', 'activity_type', 'course']