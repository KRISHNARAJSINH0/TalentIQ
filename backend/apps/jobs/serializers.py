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


from .models import JobATSReport, InterviewReadiness

class JobATSReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobATSReport
        fields = [
            "id",
            "resume",
            "job_title",
            "company_name",
            "job_description",
            "overall_match",
            "ats_score",
            "interview_readiness",
            "role_match",
            "skills_match",
            "experience_match",
            "education_match",
            "projects_match",
            "missing_skills",
            "recommendations",
            "metadata",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InterviewReadinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewReadiness
        fields = [
            "id",
            "resume",
            "job_title",
            "technical_score",
            "projects_score",
            "experience_score",
            "leadership_score",
            "communication_score",
            "overall_readiness",
            "feedback",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

