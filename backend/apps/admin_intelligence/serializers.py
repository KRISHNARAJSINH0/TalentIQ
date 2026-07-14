from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import UsageAnalytics, SystemHealth, AuditLog, UserStatistics, IndustryStatistics

User = get_user_model()


class AdminUserSerializer(serializers.ModelSerializer):
    """Custom user serializer with roles and statuses for admin management."""
    full_name = serializers.CharField(source="get_full_name", read_only=True)
    resume_count = serializers.SerializerMethodField()
    portfolio_slug = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "is_active",
            "is_verified",
            "date_joined",
            "last_login",
            "resume_count",
            "portfolio_slug",
        ]
        read_only_fields = ["id", "email", "date_joined", "last_login"]

    def get_resume_count(self, obj):
        return obj.resumes.count()

    def get_portfolio_slug(self, obj):
        # Retrieve portfolio slug if exists
        portfolio = obj.profile.portfolios.first() if hasattr(obj, 'profile') else None
        return portfolio.slug if portfolio else None


class UsageAnalyticsSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UsageAnalytics
        fields = [
            "id",
            "user",
            "user_email",
            "event_type",
            "endpoint",
            "status_code",
            "processing_time",
            "ip_address",
            "user_agent",
            "created_at",
        ]


class SystemHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemHealth
        fields = "__all__"


class AuditLogSerializer(serializers.ModelSerializer):
    admin_email = serializers.EmailField(source="admin.email", read_only=True)
    target_user_email = serializers.EmailField(source="target_user.email", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "admin",
            "admin_email",
            "action",
            "target_user",
            "target_user_email",
            "description",
            "ip_address",
            "created_at",
        ]


class UserStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatistics
        fields = "__all__"


class IndustryStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndustryStatistics
        fields = "__all__"
