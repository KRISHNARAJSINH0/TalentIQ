"""
ATS Serializers – serialization for all ATS-related scoring and rule engine models.
"""

from rest_framework import serializers

from .models import (
    ATSScore,
    ATSReport,
    ATSBenchmark,
    ATSRecommendation,
    ATSHistory,
    RuleCategory,
    ATSRule,
    RuleExecution
)


class ATSScoreSerializer(serializers.ModelSerializer):
    """Serializer for legacy ATSScore model compatibility."""
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


class RuleCategorySerializer(serializers.ModelSerializer):
    """Serializer for RuleCategory model."""
    class Meta:
        model = RuleCategory
        fields = "__all__"


class ATSRuleSerializer(serializers.ModelSerializer):
    """Serializer for ATSRule model."""
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = ATSRule
        fields = [
            "id",
            "rule_code",
            "name",
            "category",
            "category_name",
            "description",
            "condition",
            "points",
            "severity",
            "profession",
            "enabled",
            "recommendation",
            "explanation",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RuleExecutionSerializer(serializers.ModelSerializer):
    """Serializer for RuleExecution model."""
    rule_code = serializers.CharField(source="rule.rule_code", read_only=True)
    rule_name = serializers.CharField(source="rule.name", read_only=True)
    category_name = serializers.CharField(source="rule.category.name", read_only=True)
    severity = serializers.CharField(source="rule.severity", read_only=True)

    class Meta:
        model = RuleExecution
        fields = [
            "id",
            "resume",
            "rule",
            "rule_code",
            "rule_name",
            "category_name",
            "severity",
            "status",
            "score_impact",
            "reason",
            "recommendation",
            "executed_at",
        ]


class ATSRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for ATSRecommendation model."""
    class Meta:
        model = ATSRecommendation
        fields = "__all__"


class ATSBenchmarkSerializer(serializers.ModelSerializer):
    """Serializer for ATSBenchmark model."""
    class Meta:
        model = ATSBenchmark
        fields = "__all__"


class ATSReportSerializer(serializers.ModelSerializer):
    """Serializer for ATSReport model."""
    resume_title = serializers.CharField(source="resume.resume_title", read_only=True)

    class Meta:
        model = ATSReport
        fields = "__all__"


class ATSHistorySerializer(serializers.ModelSerializer):
    """Serializer for ATSHistory model."""
    resume_title = serializers.CharField(source="resume.resume_title", read_only=True)
    report_details = ATSReportSerializer(source="report", read_only=True)
    ats_score = serializers.IntegerField(source="overall_score", read_only=True)

    class Meta:
        model = ATSHistory
        fields = [
            "id",
            "resume",
            "resume_title",
            "overall_score",
            "ats_score",
            "report",
            "report_details",
            "completed_at",
        ]
