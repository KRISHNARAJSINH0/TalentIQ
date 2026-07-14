import uuid
import os
from django.conf import settings
from django.db import models

# pyrefly: ignore [missing-import]
from apps.common.models import SoftDeleteModel


def resume_upload_path(instance, filename):
    """Generate dynamic upload path with UUID filenames under user's directory."""
    ext = os.path.splitext(filename)[1].lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    return f"resumes/{instance.user.id}/{unique_name}"


class Resume(SoftDeleteModel):
    """
    A resume document uploaded by a user.
    """

    class ParsingStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class ExtractionStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class RegexStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class SpacyStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class AIStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class ValidationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class UploadStatus(models.TextChoices):
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resumes",
        verbose_name="User",
    )
    resume_title = models.CharField(
        max_length=255,
        verbose_name="Resume Title",
        help_text="A descriptive title, e.g. 'Software Engineer – 2025'",
        db_index=True,
    )
    original_file = models.FileField(
        upload_to=resume_upload_path,
        verbose_name="Original File",
        help_text="Accepted formats: PDF, DOCX",
    )
    original_filename = models.CharField(
        max_length=255,
        default="",
        blank=True,
        verbose_name="Original Filename",
    )
    stored_filename = models.CharField(
        max_length=255,
        default="",
        blank=True,
        verbose_name="Stored Filename",
    )
    file_size = models.PositiveIntegerField(
        default=0,
        verbose_name="File Size (bytes)",
    )
    mime_type = models.CharField(
        max_length=100,
        default="",
        blank=True,
        verbose_name="MIME Type",
    )
    upload_status = models.CharField(
        max_length=20,
        choices=UploadStatus.choices,
        default=UploadStatus.COMPLETED,
        verbose_name="Upload Status",
    )
    version = models.PositiveIntegerField(
        default=1,
        verbose_name="Version",
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name="Is Active",
    )
    
    # Text extraction fields
    extracted_text = models.TextField(
        blank=True,
        verbose_name="Extracted Text",
        help_text="Raw text extracted from the uploaded file.",
    )
    extraction_status = models.CharField(
        max_length=20,
        choices=ExtractionStatus.choices,
        default=ExtractionStatus.PENDING,
        verbose_name="Extraction Status",
        db_index=True,
    )
    extraction_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Extraction Time",
    )
    processing_duration = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Processing Duration (seconds)",
    )
    error_message = models.TextField(
        blank=True,
        default="",
        verbose_name="Error Message",
    )
    
    # Old parsing fields retained for future compatibility
    parsed_json = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Parsed JSON",
        help_text="Structured data extracted by the AI parser.",
    )
    parsing_status = models.CharField(
        max_length=20,
        choices=ParsingStatus.choices,
        default=ParsingStatus.PENDING,
        verbose_name="Parsing Status",
        db_index=True,
    )
    
    # Regex extraction fields
    regex_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Regex Extracted JSON",
    )
    regex_status = models.CharField(
        max_length=20,
        choices=RegexStatus.choices,
        default=RegexStatus.PENDING,
        verbose_name="Regex Status",
        db_index=True,
    )
    regex_processing_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Regex Processing Time (seconds)",
    )
    regex_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Regex Completed At",
    )
    
    # spaCy extraction fields
    spacy_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="spaCy Extracted JSON",
    )
    spacy_status = models.CharField(
        max_length=20,
        choices=SpacyStatus.choices,
        default=SpacyStatus.PENDING,
        verbose_name="spaCy Status",
        db_index=True,
    )
    spacy_processing_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name="spaCy Processing Time (seconds)",
    )
    spacy_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="spaCy Completed At",
    )
    
    # AI extraction fields
    ai_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="AI Extracted JSON",
    )
    ai_status = models.CharField(
        max_length=20,
        choices=AIStatus.choices,
        default=AIStatus.PENDING,
        verbose_name="AI Status",
        db_index=True,
    )
    ai_processing_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name="AI Processing Time (seconds)",
    )
    ai_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="AI Completed At",
    )
    ai_model = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="AI Model Used",
    )
    ai_prompt_version = models.CharField(
        max_length=50,
        blank=True,
        default="v1",
        verbose_name="AI Prompt Version",
    )
    
    # Master profile fields
    master_resume_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Master Resume JSON",
    )
    validation_status = models.CharField(
        max_length=20,
        choices=ValidationStatus.choices,
        default=ValidationStatus.PENDING,
        verbose_name="Validation Status",
        db_index=True,
    )
    validation_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Validation Time",
    )
    completion_percentage = models.FloatField(
        default=0.0,
        verbose_name="Completion Percentage",
    )
    
    upload_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Upload Date",
    )

    class Meta(SoftDeleteModel.Meta):
        verbose_name = "Resume"
        verbose_name_plural = "Resumes"
        ordering = ["-upload_date"]
        indexes = [
            models.Index(fields=["user", "parsing_status"], name="idx_resume_user_status"),
            models.Index(fields=["user", "extraction_status"], name="idx_resume_user_extract"),
            models.Index(fields=["user", "is_active"], name="idx_resume_user_active"),
            models.Index(fields=["user", "regex_status"], name="idx_resume_user_regex"),
            models.Index(fields=["user", "ai_status"], name="idx_resume_user_ai"),
            models.Index(fields=["user", "validation_status"], name="idx_resume_user_validation"),
        ]

    def __str__(self):
        return f"{self.resume_title} (v{self.version}) – {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if self._state.adding:
            # Auto increment version for this user
            last_resume = Resume.objects.filter(user=self.user).order_by("-version").first()
            self.version = (last_resume.version + 1) if last_resume else 1
            
            # If is_active is True, deactivate all other resumes for this user
            if self.is_active:
                Resume.objects.filter(user=self.user).update(is_active=False)
        else:
            # Handle is_active status change for existing objects
            if self.is_active:
                Resume.objects.filter(user=self.user).exclude(pk=self.pk).update(is_active=False)
                
        super().save(*args, **kwargs)


class ResumeSection(models.Model):
    """
    Stores detected resume sections, boundaries, and metadata.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name="Resume",
    )
    section_type = models.CharField(
        max_length=50,
        verbose_name="Normalized Section Type",
        help_text="Normalized section type (e.g. experience, education, skills)",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Original Section Title",
        blank=True,
        default="",
    )
    confidence = models.FloatField(
        default=100.0,
        verbose_name="Confidence Score (0-100)",
    )
    position = models.PositiveIntegerField(
        default=0,
        verbose_name="Position Index",
    )
    page = models.PositiveIntegerField(
        default=1,
        verbose_name="Page Number",
    )
    content = models.TextField(
        blank=True,
        default="",
        verbose_name="Section Content",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    class Meta:
        ordering = ["position"]
        verbose_name = "Resume Section"
        verbose_name_plural = "Resume Sections"

    def __str__(self):
        return f"{self.section_type} ({self.confidence}%) - {self.resume.resume_title}"


class ConfidenceScore(models.Model):
    """
    Stores calculated confidence scores, sources, and audit rationale for parsed resume fields.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="confidence_scores",
        verbose_name="Resume",
    )
    field = models.CharField(
        max_length=100,
        verbose_name="Field Name",
        help_text="Name of the parsed field (e.g. name, email, phone)",
    )
    value = models.TextField(
        blank=True,
        default="",
        verbose_name="Extracted Value",
    )
    confidence = models.FloatField(
        default=0.0,
        verbose_name="Confidence Score (0-100)",
    )
    source = models.CharField(
        max_length=50,
        verbose_name="Extraction Source",
        help_text="Primary extraction source (e.g. regex, spacy, gemini, manual)",
    )
    reason = models.TextField(
        blank=True,
        default="",
        verbose_name="Scoring Rationale",
    )
    status = models.CharField(
        max_length=30,
        verbose_name="Calibration Status",
        help_text="Status based on confidence limits (e.g. accepted, review, warning, rejected)",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    class Meta:
        ordering = ["field"]
        verbose_name = "Confidence Score"
        verbose_name_plural = "Confidence Scores"

    def __str__(self):
        return f"{self.field}: {self.confidence}% ({self.status}) - {self.resume.resume_title}"


class SemanticValidation(models.Model):
    """
    Stores semantic validation results, anomaly detection metrics, action system flags,
    and category mappings per extracted resume field.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="semantic_validations",
        verbose_name="Resume",
    )
    field = models.CharField(
        max_length=100,
        verbose_name="Field Name",
        help_text="Extracted field key or sub-key",
    )
    value = models.TextField(
        blank=True,
        default="",
        verbose_name="Extracted Value",
    )
    category = models.CharField(
        max_length=50,
        verbose_name="Detected Category",
        help_text="Semantic category detected by ontology/classifier (e.g. University)",
    )
    expected_category = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Expected Category",
        help_text="Category expected based on resume section (e.g. Skill)",
    )
    semantic_score = models.FloatField(
        default=0.0,
        verbose_name="Semantic Score (0-100)",
    )
    reason = models.TextField(
        blank=True,
        default="",
        verbose_name="Semantic Explanation",
    )
    status = models.CharField(
        max_length=30,
        verbose_name="Validation Status",
        help_text="valid (90+), possible (75-90), suspicious (50-75), invalid (<50)",
    )
    action = models.CharField(
        max_length=50,
        verbose_name="Action Flag",
        help_text="accept, review, recover, move, move_to_<category>, reject",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    class Meta:
        ordering = ["-semantic_score", "field"]
        verbose_name = "Semantic Validation"
        verbose_name_plural = "Semantic Validations"

    def __str__(self):
        return f"{self.field}: {self.category} vs {self.expected_category} ({self.semantic_score}%)"


class ResumeError(models.Model):
    """
    Persists error detection results generated by ErrorDetector (Stage 8).
    Captures anomalies, inconsistencies, missing fields, timeline errors, and severity/action flags.
    """
    class SeverityChoices(models.TextChoices):
        CRITICAL = "critical", "Critical"
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"

    class ActionChoices(models.TextChoices):
        ACCEPT = "accept", "Accept"
        REVIEW = "review", "Review"
        RECOVER = "recover", "Recover"
        IGNORE = "ignore", "Ignore"
        MOVE = "move", "Move"
        REJECT = "reject", "Reject"

    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="error_detections",
        verbose_name="Resume",
    )
    type = models.CharField(
        max_length=50,
        verbose_name="Error Type",
        help_text="wrong_entity, timeline_error, duplicate_value, missing_contact, etc.",
    )
    field = models.CharField(
        max_length=100,
        verbose_name="Field / Target",
    )
    value = models.TextField(
        blank=True,
        default="",
        verbose_name="Extracted Value",
    )
    severity = models.CharField(
        max_length=20,
        choices=SeverityChoices.choices,
        default=SeverityChoices.MEDIUM,
        verbose_name="Severity Level",
    )
    confidence = models.FloatField(
        default=100.0,
        verbose_name="Detection Confidence (0-100)",
    )
    action = models.CharField(
        max_length=50,
        choices=ActionChoices.choices,
        default=ActionChoices.REVIEW,
        verbose_name="Recommended Action",
    )
    reason = models.TextField(
        blank=True,
        default="",
        verbose_name="Error Explanation / Rationale",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    class Meta:
        ordering = ["-created_at", "severity", "field"]
        verbose_name = "Resume Error"
        verbose_name_plural = "Resume Errors"

    def __str__(self):
        return f"[{self.severity.upper()}] {self.type} on {self.field}: {self.reason}"


class RecoveryLog(models.Model):
    """
    Persists recovery logs generated by RecoveryEngine (Stage 9 / Phase 9.5).
    Tracks auto-fixes, entity relocations, date swaps, deduplication, and user audit states.
    """
    class RecoveryStatusChoices(models.TextChoices):
        ACCEPTED = "accepted", "Accepted"
        REVIEWED = "reviewed", "Reviewed"
        RECOVERED = "recovered", "Recovered"
        SUGGESTED = "suggested", "Suggested"
        MANUAL = "manual", "Manual"
        REJECTED = "rejected", "Rejected"

    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="recovery_logs",
        verbose_name="Resume",
    )
    field = models.CharField(
        max_length=100,
        verbose_name="Field / Section",
    )
    previous_value = models.TextField(
        blank=True,
        default="",
        verbose_name="Previous Value",
    )
    new_value = models.TextField(
        blank=True,
        default="",
        verbose_name="Recovered Value",
    )
    reason = models.TextField(
        blank=True,
        default="",
        verbose_name="Recovery Explanation",
    )
    confidence = models.FloatField(
        default=100.0,
        verbose_name="Recovery Confidence (0-100)",
    )
    status = models.CharField(
        max_length=50,
        choices=RecoveryStatusChoices.choices,
        default=RecoveryStatusChoices.RECOVERED,
        verbose_name="Recovery Status",
        help_text="accepted, reviewed, recovered, suggested, manual, rejected",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    class Meta:
        ordering = ["-created_at", "field"]
        verbose_name = "Recovery Log"
        verbose_name_plural = "Recovery Logs"

    def __str__(self):
        return f"[{self.status.upper()}] {self.field}: '{self.previous_value[:30]}' -> '{self.new_value[:30]}'"


class ConsistencyReport(models.Model):
    """
    Persists consistency audit reports generated by ConsistencyChecker (Stage 9 / Phase 9.6).
    Tracks consistency scores (0-100), contradictions, timeline anomalies, and recommendations.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="consistency_reports",
        verbose_name="Resume",
    )
    score = models.FloatField(
        default=100.0,
        verbose_name="Consistency Score (0-100)",
    )
    score_label = models.CharField(
        max_length=50,
        default="Excellent",
        verbose_name="Score Label",
        help_text="Excellent, Strong, Average, Weak, Needs Review",
    )
    issues = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Detected Consistency Issues",
    )
    suggestions = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Recommended Skill & Profile Actions",
    )
    metrics = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Consistency Metrics",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    class Meta:
        ordering = ["-created_at", "-score"]
        verbose_name = "Consistency Report"
        verbose_name_plural = "Consistency Reports"

    def __str__(self):
        return f"[{self.score_label.upper()} {self.score:.1f}] Resume #{self.resume_id}: {len(self.issues)} issues"


class FieldSource(models.Model):
    """
    Persists data provenance & source origins for each field in a resume (Stage 9 / Phase 9.7).
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="field_sources",
        verbose_name="Resume",
    )
    field = models.CharField(
        max_length=255,
        verbose_name="Field Name",
    )
    value = models.TextField(
        blank=True,
        default="",
        verbose_name="Field Value",
    )
    source = models.CharField(
        max_length=100,
        default="spacy",
        verbose_name="Source Origin",
        help_text="regex, spacy, gemini, section_detector, semantic_validator, recovery_engine, consistency_checker, user_edit, manual",
    )
    confidence = models.FloatField(
        default=100.0,
        verbose_name="Confidence Score (0-100)",
    )
    status = models.CharField(
        max_length=50,
        default="extracted",
        verbose_name="Provenance Status",
        help_text="extracted, inferred, corrected, generated, recovered, edited, approved, imported, manual",
    )
    reason = models.TextField(
        blank=True,
        default="",
        verbose_name="Source Reason / Explanation",
    )
    ui_color = models.CharField(
        max_length=50,
        default="#3B82F6",
        verbose_name="UI Highlight Color",
    )
    version = models.IntegerField(
        default=1,
        verbose_name="Version Number",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
    )

    class Meta:
        ordering = ["resume", "field"]
        unique_together = ["resume", "field", "version"]
        verbose_name = "Field Source"
        verbose_name_plural = "Field Sources"

    def __str__(self):
        return f"[{self.source.upper()}] {self.field}: {self.value[:30]} ({self.confidence:.0f}%)"


class FieldHistory(models.Model):
    """
    Persists audit trail history for field-level modifications across resume versions.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="field_histories",
        verbose_name="Resume",
    )
    field = models.CharField(
        max_length=255,
        verbose_name="Field Name",
    )
    previous_value = models.TextField(
        blank=True,
        default="",
        verbose_name="Previous Value",
    )
    current_value = models.TextField(
        blank=True,
        default="",
        verbose_name="Current Value",
    )
    source = models.CharField(
        max_length=100,
        default="User Edit",
        verbose_name="Source / Engine",
    )
    reason = models.TextField(
        blank=True,
        default="",
        verbose_name="Modification Reason",
    )
    confidence = models.FloatField(
        default=100.0,
        verbose_name="Confidence Score (0-100)",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="field_history_edits",
        verbose_name="Modified By User",
    )
    version = models.IntegerField(
        default=1,
        verbose_name="Resume Version Number",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Timestamp",
    )

    class Meta:
        ordering = ["-timestamp", "field"]
        verbose_name = "Field History Log"
        verbose_name_plural = "Field History Logs"

    def __str__(self):
        return f"[{self.source}] {self.field}: '{self.previous_value[:20]}' -> '{self.current_value[:20]}'"


class SelfHealingReport(models.Model):
    """
    Persists self-healing parsing reports, decision states, and Master Resume outputs (Stage 9 / Phase 9.8).
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="self_healing_reports",
        null=True,
        blank=True,
        verbose_name="Resume",
    )
    confidence = models.FloatField(
        default=95.0,
        verbose_name="Final Confidence Score",
    )
    issues_found = models.IntegerField(
        default=0,
        verbose_name="Issues Found",
    )
    issues_fixed = models.IntegerField(
        default=0,
        verbose_name="Issues Fixed",
    )
    needs_review = models.IntegerField(
        default=0,
        verbose_name="Needs Review Count",
    )
    recovered_fields_count = models.IntegerField(
        default=0,
        verbose_name="Recovered Fields Count",
    )
    decision = models.CharField(
        max_length=50,
        default="accept",
        verbose_name="Decision Status",
        help_text="accept, review, recover, reject, escalate",
    )
    approval_tier = models.CharField(
        max_length=50,
        default="auto_approve",
        verbose_name="Approval Tier",
        help_text="auto_approve, approve, ask_confirmation, manual_verification",
    )
    summary = models.TextField(
        blank=True,
        default="",
        verbose_name="Healing Summary",
    )
    master_resume_output = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Master Resume JSON Payload",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Self Healing Report"
        verbose_name_plural = "Self Healing Reports"

    def __str__(self):
        return f"[{self.decision.upper()}] Confidence: {self.confidence:.1f}% ({self.issues_fixed}/{self.issues_found} fixed)"


class CopilotConversation(models.Model):
    """
    Persists conversational chat messages between User and Resume Copilot (Stage 9 / Phase 9.9).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="copilot_conversations",
        verbose_name="User",
    )
    resume = models.ForeignKey(
        Resume,
        on_delete=models.SET_NULL,
        related_name="copilot_conversations",
        null=True,
        blank=True,
        verbose_name="Resume",
    )
    message = models.TextField(
        verbose_name="User Message",
    )
    response = models.TextField(
        verbose_name="Copilot Response",
    )
    intent = models.CharField(
        max_length=100,
        default="chat",
        verbose_name="Classified Intent",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Copilot Conversation"
        verbose_name_plural = "Copilot Conversations"

    def __str__(self):
        return f"[{self.user.username}] ({self.intent}): '{self.message[:30]}...'"


class CopilotAction(models.Model):
    """
    Persists executable AI action history and state snapshots for Undo/Redo operations.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="copilot_actions",
        verbose_name="Resume",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="copilot_actions",
        null=True,
        blank=True,
        verbose_name="User",
    )
    action = models.CharField(
        max_length=100,
        verbose_name="Action Type",
        help_text="add_skill, remove_skill, update_education, improve_summary, etc.",
    )
    previous_state = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Previous State Snapshot",
    )
    new_state = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="New State Snapshot",
    )
    confidence = models.FloatField(
        default=95.0,
        verbose_name="Action Confidence",
    )
    is_undone = models.BooleanField(
        default=False,
        verbose_name="Is Undone",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Copilot Action Log"
        verbose_name_plural = "Copilot Action Logs"

    def __str__(self):
        return f"[{self.action}] Resume: {self.resume.id} (Undone: {self.is_undone})"









