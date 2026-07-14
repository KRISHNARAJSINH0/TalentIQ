from rest_framework import serializers
from .models import Notification, NotificationPreference, Reminder, Announcement

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializes Notification entries for lists.
    """
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "type",
            "type_display",
            "priority",
            "priority_display",
            "status",
            "read",
            "created_at",
            "scheduled_at",
            "delivered_at",
            "metadata"
        ]
        read_only_fields = ["id", "created_at", "delivered_at"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializes NotificationPreference toggles.
    """
    class Meta:
        model = NotificationPreference
        fields = [
            "enable_email",
            "enable_ats_alerts",
            "enable_career_alerts",
            "enable_portfolio_alerts",
            "enable_weekly_reports",
            "enable_monthly_reports",
            "enable_security_notifications"
        ]


class ReminderSerializer(serializers.ModelSerializer):
    """
    Serializes schedules for task reminders.
    """
    type_display = serializers.CharField(source="get_reminder_type_display", read_only=True)

    class Meta:
        model = Reminder
        fields = [
            "id",
            "title",
            "description",
            "reminder_type",
            "type_display",
            "due_date",
            "triggered",
            "created_at"
        ]
        read_only_fields = ["id", "triggered", "created_at"]


class AnnouncementSerializer(serializers.ModelSerializer):
    """
    Serializes system announcements.
    """
    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "message",
            "priority",
            "created_at",
            "expires_at"
        ]
