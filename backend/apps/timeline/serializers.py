from rest_framework import serializers

from .models import (
    ResumeVersion,
    TimelineEvent,
    CareerProgress,
    SkillHistory,
    ATSHistory,
    LearningHistory,
    ProfileSnapshot
)


class ResumeVersionSerializer(serializers.ModelSerializer):
    created_at_formatted = serializers.DateTimeField(source="created_at", format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = ResumeVersion
        fields = [
            "id",
            "version_number",
            "ats_score",
            "completion_score",
            "profile_snapshot",
            "summary",
            "change_count",
            "is_active",
            "created_at",
            "created_at_formatted",
        ]


class TimelineEventSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source="get_event_type_display", read_only=True)
    created_at_formatted = serializers.DateTimeField(source="created_at", format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = TimelineEvent
        fields = [
            "id",
            "event_type",
            "event_type_display",
            "title",
            "description",
            "metadata",
            "created_at",
            "created_at_formatted",
        ]


class CareerProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerProgress
        fields = [
            "id",
            "career_score",
            "growth_score",
            "learning_score",
            "industry_match",
            "market_alignment",
            "date",
        ]


class SkillHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillHistory
        fields = [
            "id",
            "skill_name",
            "added_date",
            "removed_date",
            "skill_category",
            "source",
            "is_active",
        ]


class ATSHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ATSHistory
        fields = [
            "id",
            "resume",
            "overall_score",
            "keyword_score",
            "industry_score",
            "completion_score",
            "date",
        ]


class LearningHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningHistory
        fields = [
            "id",
            "topic",
            "source",
            "progress",
            "status",
            "completed_at",
        ]


class ProfileSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileSnapshot
        fields = [
            "id",
            "profile_data",
            "date",
        ]
