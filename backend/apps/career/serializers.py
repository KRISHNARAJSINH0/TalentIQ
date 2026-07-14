from rest_framework import serializers
from .models import CareerProfile, CoverLetter, LearningProgressLog


class CareerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="profile.user.username", read_only=True)

    class Meta:
        model = CareerProfile
        fields = [
            "id",
            "username",
            "career_readiness",
            "growth_score",
            "learning_score",
            "industry_alignment",
            "skill_strength",
            "market_demand",
            "career_json",
            "roadmap_json",
            "created_at",
            "updated_at"
        ]


class CoverLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverLetter
        fields = [
            "id",
            "company",
            "position",
            "job_description",
            "tone",
            "cover_letter_type",
            "content",
            "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class LearningProgressLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningProgressLog
        fields = [
            "id",
            "milestone_title",
            "item_name",
            "category",
            "is_completed",
            "completed_at"
        ]
        read_only_fields = ["id"]
