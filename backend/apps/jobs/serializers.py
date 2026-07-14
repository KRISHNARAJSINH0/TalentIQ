from rest_framework import serializers
from .models import JobRecommendation, SkillGap


class JobRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRecommendation
        fields = [
            "id",
            "title",
            "score",
            "salary",
            "industry",
            "country",
            "remote",
            "missing_skills",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SkillGapSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillGap
        fields = [
            "id",
            "skill",
            "importance",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
