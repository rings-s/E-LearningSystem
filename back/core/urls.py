from django.urls import path

from .views import (
    ForumListView, ForumDetailView,
    DiscussionListCreateView, DiscussionDetailView,
    DiscussionPinView, DiscussionLockView, DiscussionResolveView,
    ReplyListCreateView, ReplyDetailView, ReplyUpvoteView, ReplyMarkSolutionView,
    NotificationListView, NotificationDetailView,
    NotificationMarkAllReadView, NotificationUnreadCountView,
    ActivityLogListView,
    MediaContentListCreateView, MediaContentDetailView,
    AnnouncementListCreateView, AnnouncementDetailView,
    SupportTicketListCreateView, SupportTicketDetailView,
    DashboardView
)

app_name = 'core'

urlpatterns = [
    # Forums
    path('forums/', ForumListView.as_view(), name='forum-list'),
    path('forums/<uuid:uuid>/', ForumDetailView.as_view(), name='forum-detail'),
    
    # Discussions
    path('discussions/', DiscussionListCreateView.as_view(), name='discussion-list'),
    path('discussions/<uuid:uuid>/', DiscussionDetailView.as_view(), name='discussion-detail'),
    path('discussions/<uuid:uuid>/pin/', DiscussionPinView.as_view(), name='discussion-pin'),
    path('discussions/<uuid:uuid>/lock/', DiscussionLockView.as_view(), name='discussion-lock'),
    path('discussions/<uuid:uuid>/resolve/', DiscussionResolveView.as_view(), name='discussion-resolve'),
    
    # Replies
    path('replies/', ReplyListCreateView.as_view(), name='reply-list'),
    path('replies/<uuid:uuid>/', ReplyDetailView.as_view(), name='reply-detail'),
    path('replies/<uuid:uuid>/upvote/', ReplyUpvoteView.as_view(), name='reply-upvote'),
    path('replies/<uuid:uuid>/mark-solution/', ReplyMarkSolutionView.as_view(), name='reply-mark-solution'),
    
    # Notifications
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<uuid:uuid>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('notifications/unread-count/', NotificationUnreadCountView.as_view(), name='notification-unread-count'),
    
    # Activity Logs
    path('activities/', ActivityLogListView.as_view(), name='activity-list'),
    
    # Media Content
    path('media/', MediaContentListCreateView.as_view(), name='media-list'),
    path('media/<uuid:uuid>/', MediaContentDetailView.as_view(), name='media-detail'),
    
    # Announcements
    path('announcements/', AnnouncementListCreateView.as_view(), name='announcement-list'),
    path('announcements/<uuid:uuid>/', AnnouncementDetailView.as_view(), name='announcement-detail'),
    
    # Support Tickets
    path('support-tickets/', SupportTicketListCreateView.as_view(), name='support-ticket-list'),
    path('support-tickets/<uuid:uuid>/', SupportTicketDetailView.as_view(), name='support-ticket-detail'),
    
    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]