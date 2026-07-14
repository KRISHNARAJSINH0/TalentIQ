"""
JD Analyzer serializers — Phase 22.
"""

from rest_framework import serializers
from .models import JobDescription, JobAnalysis


class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = [
            "id", "title", "company", "industry", "content",
            "parsed_data", "source_type", "created_at",
        ]
        read_only_fields = ["id", "parsed_data", "created_at"]


class JobDescriptionUploadSerializer(serializers.Serializer):
    content = serializers.CharField(
        required=True,
        min_length=50,
        help_text="The full job description text (min 50 characters).",
    )
    source_type = serializers.ChoiceField(
        choices=JobDescription.SourceType.choices,
        default="text",
        required=False,
    )


class JobAnalysisSerializer(serializers.ModelSerializer):
    jd_title = serializers.CharField(source="job_description.title", read_only=True)
    jd_company = serializers.CharField(source="job_description.company", read_only=True)

    class Meta:
        model = JobAnalysis
        fields = [
            "id", "jd_title", "jd_company",
            "match_score", "ats_score", "skills_match",
            "experience_match", "education_match", "keyword_match",
            "missing_skills", "matching_skills",
            "strengths", "weaknesses", "suggestions",
            "interview_readiness", "salary_estimate", "report",
            "created_at",
        ]
        read_only_fields = fields


class JobAnalysisListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for history list."""
    jd_title = serializers.CharField(source="job_description.title", read_only=True)
    jd_company = serializers.CharField(source="job_description.company", read_only=True)

    class Meta:
        model = JobAnalysis
        fields = [
            "id", "jd_title", "jd_company",
            "match_score", "ats_score", "skills_match",
            "created_at",
        ]
        read_only_fields = fields
