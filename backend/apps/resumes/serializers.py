import os
from rest_framework import serializers
from .models import Resume, ResumeSection, ConfidenceScore
from .validators import validate_resume_file


class ResumeSerializer(serializers.ModelSerializer):
    """
    Serializer for listing, detailing, and updating Resumes.
    """
    class Meta:
        model = Resume
        fields = [
            "id",
            "resume_title",
            "original_filename",
            "stored_filename",
            "file_size",
            "mime_type",
            "upload_status",
            "version",
            "is_active",
            "upload_date",
            "extraction_status",
            "extraction_time",
            "processing_duration",
            "error_message",
            "regex_status",
            "regex_completed_at",
            "regex_processing_time",
            "spacy_status",
            "spacy_completed_at",
            "spacy_processing_time",
            "ai_status",
            "ai_completed_at",
            "ai_processing_time",
            "ai_model",
            "ai_prompt_version",
            "master_resume_json",
            "validation_status",
            "validation_time",
            "completion_percentage",
        ]
        read_only_fields = fields


class ResumeUploadSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for handling multipart/form-data upload.
    """
    original_file = serializers.FileField(required=True, write_only=True)
    resume_title = serializers.CharField(max_length=255, required=False, allow_blank=True)

    class Meta:
        model = Resume
        fields = [
            "id",
            "resume_title",
            "original_file",
            "original_filename",
            "stored_filename",
            "version",
            "upload_date",
            "upload_status",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "original_filename",
            "stored_filename",
            "version",
            "upload_date",
            "upload_status",
            "is_active",
        ]

    def validate_original_file(self, value):
        validate_resume_file(value)
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        uploaded_file = validated_data["original_file"]
        
        # Fallback for resume title
        original_filename = uploaded_file.name
        resume_title = validated_data.get("resume_title")
        if not resume_title:
            resume_title = os.path.splitext(original_filename)[0]

        # Construct the model instance
        resume = Resume(
            user=user,
            resume_title=resume_title,
            original_file=uploaded_file,
            original_filename=original_filename,
            file_size=uploaded_file.size,
            mime_type=uploaded_file.content_type,
            is_active=True,  # Set newly uploaded version as active
        )
        resume.save()

        # Update stored_filename with the generated UUID name
        resume.stored_filename = os.path.basename(resume.original_file.name)
        resume.save(update_fields=["stored_filename"])

        return resume


class ResumeSectionSerializer(serializers.ModelSerializer):
    """
    Serializer for the ResumeSection model.
    """
    class Meta:
        model = ResumeSection
        fields = [
            "id",
            "resume",
            "section_type",
            "title",
            "confidence",
            "position",
            "page",
            "content",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConfidenceScoreSerializer(serializers.ModelSerializer):
    """
    Serializer for the ConfidenceScore model.
    """
    class Meta:
        model = ConfidenceScore
        fields = [
            "id",
            "resume",
            "field",
            "value",
            "confidence",
            "source",
            "reason",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SemanticValidationSerializer(serializers.ModelSerializer):
    """
    Serializer for the SemanticValidation model.
    """
    class Meta:
        from .models import SemanticValidation
        model = SemanticValidation
        fields = [
            "id",
            "resume",
            "field",
            "value",
            "category",
            "expected_category",
            "semantic_score",
            "reason",
            "status",
            "action",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SemanticValidationRequestSerializer(serializers.Serializer):
    resume_id = serializers.UUIDField(required=False, allow_null=True)
    payload = serializers.JSONField(required=False, allow_null=True)


class ResumeErrorSerializer(serializers.ModelSerializer):
    """
    Serializer for the ResumeError model.
    """
    class Meta:
        from .models import ResumeError
        model = ResumeError
        fields = [
            "id",
            "resume",
            "type",
            "field",
            "value",
            "severity",
            "confidence",
            "action",
            "reason",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ResumeErrorRequestSerializer(serializers.Serializer):
    resume_id = serializers.UUIDField(required=False, allow_null=True)
    payload = serializers.JSONField(required=False, allow_null=True)
    confidence_map = serializers.JSONField(required=False, allow_null=True)


class RecoveryLogSerializer(serializers.ModelSerializer):
    """
    Serializer for the RecoveryLog model.
    """
    class Meta:
        from .models import RecoveryLog
        model = RecoveryLog
        fields = [
            "id",
            "resume",
            "field",
            "previous_value",
            "new_value",
            "reason",
            "confidence",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class RecoveryRequestSerializer(serializers.Serializer):
    resume_id = serializers.UUIDField(required=False, allow_null=True)
    payload = serializers.JSONField(required=False, allow_null=True)
    error_report = serializers.JSONField(required=False, allow_null=True)
    confidence_map = serializers.JSONField(required=False, allow_null=True)


class ConsistencyReportSerializer(serializers.ModelSerializer):
    """
    Serializer for the ConsistencyReport model.
    """
    class Meta:
        from .models import ConsistencyReport
        model = ConsistencyReport
        fields = [
            "id",
            "resume",
            "score",
            "score_label",
            "issues",
            "suggestions",
            "metrics",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConsistencyRequestSerializer(serializers.Serializer):
    resume_id = serializers.UUIDField(required=False, allow_null=True)
    payload = serializers.JSONField(required=False, allow_null=True)


class FieldSourceSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import FieldSource
        model = FieldSource
        fields = [
            "id",
            "resume",
            "field",
            "value",
            "source",
            "confidence",
            "status",
            "reason",
            "ui_color",
            "version",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FieldHistorySerializer(serializers.ModelSerializer):
    class Meta:
        from .models import FieldHistory
        model = FieldHistory
        fields = [
            "id",
            "resume",
            "field",
            "previous_value",
            "current_value",
            "source",
            "reason",
            "confidence",
            "user",
            "version",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp"]


class SourceTrackerRequestSerializer(serializers.Serializer):
    resume_id = serializers.UUIDField(required=False, allow_null=True)
    payload = serializers.JSONField(required=False, allow_null=True)
    engine_origins = serializers.JSONField(required=False, allow_null=True)
    recoveries = serializers.JSONField(required=False, allow_null=True)
    old_payload = serializers.JSONField(required=False, allow_null=True)


class SelfHealingReportSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import SelfHealingReport
        model = SelfHealingReport
        fields = [
            "id",
            "resume",
            "confidence",
            "issues_found",
            "issues_fixed",
            "needs_review",
            "recovered_fields_count",
            "decision",
            "approval_tier",
            "summary",
            "master_resume_output",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SelfHealingRequestSerializer(serializers.Serializer):
    resume_id = serializers.UUIDField(required=False, allow_null=True)
    payload = serializers.JSONField(required=False, allow_null=True)
    engine_origins = serializers.JSONField(required=False, allow_null=True)
    user_edits = serializers.JSONField(required=False, allow_null=True)


class CopilotConversationSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import CopilotConversation
        model = CopilotConversation
        fields = [
            "id",
            "user",
            "resume",
            "message",
            "response",
            "intent",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CopilotActionSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import CopilotAction
        model = CopilotAction
        fields = [
            "id",
            "resume",
            "user",
            "action",
            "previous_state",
            "new_state",
            "confidence",
            "is_undone",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CopilotChatRequestSerializer(serializers.Serializer):
    resume_id = serializers.UUIDField(required=False, allow_null=True)
    message = serializers.CharField(required=True)
    payload = serializers.JSONField(required=False, allow_null=True)


class CopilotActionRequestSerializer(serializers.Serializer):
    resume_id = serializers.UUIDField(required=True)
    action = serializers.CharField(required=True, help_text="undo, redo, add_skill, remove_skill, etc.")
    payload = serializers.JSONField(required=False, allow_null=True)








