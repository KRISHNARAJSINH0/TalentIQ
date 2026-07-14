"""
ATS Serializers – serialization for the ATSScore model.
"""

from rest_framework import serializers

from .models import ATSScore


class ATSScoreSerializer(serializers.ModelSerializer):
    """Serializer for ATSScore model."""

    resume_title = serializers.CharField(source="resume.resume_title", read_only=True)

    class Meta:
        model = ATSScore
        fields = [
            "id",
            "resume",
            "resume_title",
            "ats_score",
            "ats_json",
            "ats_completed_at",
            "ats_processing_time",
            "industry_match",
            "missing_skills",
            "suggestions",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "resume_title",
            "ats_completed_at",
            "created_at",
        ]
