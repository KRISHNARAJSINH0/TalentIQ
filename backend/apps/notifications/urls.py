from django.urls import path
from .views import (
    NotificationListView,
    NotificationReadView,
    NotificationDeleteView,
    NotificationPreferencesView,
    NotificationHistoryView,
    NotificationUnreadCountView,
    AnnouncementListView
)

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path("read/", NotificationReadView.as_view(), name="notification-read"),
    path("delete/", NotificationDeleteView.as_view(), name="notification-delete-bulk"),
    path("<int:pk>/", NotificationDeleteView.as_view(), name="notification-delete"),
    path("preferences/", NotificationPreferencesView.as_view(), name="notification-preferences"),
    path("history/", NotificationHistoryView.as_view(), name="notification-history"),
    path("unread/", NotificationUnreadCountView.as_view(), name="notification-unread"),
    path("announcements/", AnnouncementListView.as_view(), name="announcement-list"),
]
