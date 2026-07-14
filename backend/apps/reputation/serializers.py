from rest_framework import serializers
from .models import ResumeReputation, Badge


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["id", "badge", "earned_at"]


class ResumeReputationSerializer(serializers.ModelSerializer):
    resume_title = serializers.CharField(source="resume.resume_title", read_only=True)

    class Meta:
        model = ResumeReputation
        fields = [
            "id",
            "resume",
            "resume_title",
            "score",
            "tier",
            "career_score",
            "growth_score",
            "market_score",
            "details_json",
            "created_at",
        ]
