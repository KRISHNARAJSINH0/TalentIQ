import re
from rest_framework import serializers
from .models import Portfolio, PortfolioAnalyticsLog


class PortfolioSerializer(serializers.ModelSerializer):
    """
    Serializer for the Portfolio model.
    """
    username = serializers.CharField(source="profile.user.username", read_only=True)
    full_name = serializers.CharField(source="profile.user.get_full_name", read_only=True)

    class Meta:
        model = Portfolio
        fields = [
            "id",
            "profile",
            "username",
            "full_name",
            "theme",
            "is_public",
            "slug",
            "last_generated",
            "views",
            "likes",
            "downloads",
            "shares",
            "portfolio_json",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "profile",
            "last_generated",
            "views",
            "likes",
            "downloads",
            "shares",
            "created_at",
            "updated_at",
        ]

    def validate_slug(self, value):
        """Validate slug format and uniqueness."""
        if not value:
            return value
        if not re.match(r"^[-a-zA-Z0-9_]+$", value):
            raise serializers.ValidationError(
                "Slug must contain only alphanumeric characters, hyphens, or underscores."
            )

        # Check uniqueness
        qs = Portfolio.objects.filter(slug=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This portfolio URL slug is already taken.")
        return value


class PortfolioAnalyticsLogSerializer(serializers.ModelSerializer):
    """
    Serializer for PortfolioAnalyticsLog activity events.
    """
    class Meta:
        model = PortfolioAnalyticsLog
        fields = "__all__"
