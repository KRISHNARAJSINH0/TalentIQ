from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel
from apps.resumes.models import Resume


class ResumeVersion(BaseModel):
    """
    Tracks specific snapshots/versions of user resumes and profile data.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resume_versions"
    )
    resume = models.ForeignKey(
        Resume,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="versions"
    )
    version_number = models.IntegerField(default=1)
    ats_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    completion_score = models.FloatField(default=0.0)
    profile_snapshot = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True, default="")
    change_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)

    class Meta(BaseModel.Meta):
        verbose_name = "Resume Version"
        verbose_name_plural = "Resume Versions"
        ordering = ["-version_number"]

    def __str__(self):
        return f"Version {self.version_number} – {self.user.username}"


class TimelineEvent(BaseModel):
    """
    Generic model to store career timeline events.
    """
    class EventType(models.TextChoices):
        RESUME_UPLOADED = "resume_uploaded", "Resume Uploaded"
        RESUME_UPDATED = "resume_updated", "Resume Updated"
        ATS_IMPROVED = "ats_improved", "ATS Improved"
        SKILL_ADDED = "skill_added", "Skill Added"
        SKILL_REMOVED = "skill_removed", "Skill Removed"
        PROJECT_ADDED = "project_added", "Project Added"
        EXPERIENCE_ADDED = "experience_added", "Experience Added"
        CERTIFICATE_ADDED = "certificate_added", "Certificate Added"
        PORTFOLIO_PUBLISHED = "portfolio_published", "Portfolio Published"
        PORTFOLIO_UPDATED = "portfolio_updated", "Portfolio Updated"
        COVER_LETTER_GENERATED = "cover_letter_generated", "Cover Letter Generated"
        CAREER_ROADMAP_STARTED = "career_roadmap_started", "Career Roadmap Started"
        ROADMAP_COMPLETED = "roadmap_completed", "Roadmap Completed"
        RESUME_GENERATED = "resume_generated", "Resume Generated"
        RESUME_DOWNLOADED = "resume_downloaded", "Resume Downloaded"
        THEME_CHANGED = "theme_changed", "Theme Changed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="timeline_events"
    )
    event_type = models.CharField(
        max_length=50,
        choices=EventType.choices
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        verbose_name = "Timeline Event"
        verbose_name_plural = "Timeline Events"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_event_type_display()} – {self.title}"


class CareerProgress(BaseModel):
    """
    Snapshot of user's overall career health indicators.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="career_progress"
    )
    career_score = models.FloatField(default=0.0)
    growth_score = models.FloatField(default=0.0)
    learning_score = models.FloatField(default=0.0)
    industry_match = models.JSONField(default=dict, blank=True)
    market_alignment = models.FloatField(default=0.0)
    date = models.DateField(default=timezone.now)

    class Meta(BaseModel.Meta):
        verbose_name = "Career Progress"
        verbose_name_plural = "Career Progress entries"
        ordering = ["-date"]


class SkillHistory(BaseModel):
    """
    Tracks addition and removal dates of specific skills.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="skill_histories"
    )
    skill_name = models.CharField(max_length=100)
    added_date = models.DateField(default=timezone.now)
    removed_date = models.DateField(null=True, blank=True)
    skill_category = models.CharField(max_length=50, default="General")
    source = models.CharField(max_length=50, default="Manual") # AI, Manual, Import, Resume Upload
    is_active = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        verbose_name = "Skill History"
        verbose_name_plural = "Skill Histories"
        ordering = ["-added_date"]


class ATSHistory(BaseModel):
    """
    Tracks aggregate history of user's ATS scores.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ats_histories"
    )
    resume = models.ForeignKey(
        Resume,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ats_histories"
    )
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    keyword_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    industry_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    completion_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    date = models.DateField(default=timezone.now)

    class Meta(BaseModel.Meta):
        verbose_name = "ATS History"
        verbose_name_plural = "ATS Histories"
        ordering = ["-date"]


class LearningHistory(BaseModel):
    """
    Tracks courses, skill roadmaps, or learning items completed by the user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learning_histories"
    )
    topic = models.CharField(max_length=255)
    source = models.CharField(max_length=100, default="System")
    progress = models.IntegerField(default=0) # 0 to 100
    status = models.CharField(max_length=50, default="In Progress")
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        verbose_name = "Learning History"
        verbose_name_plural = "Learning Histories"
        ordering = ["-created_at"]


class ProfileSnapshot(BaseModel):
    """
    Stores historical backups of raw profile data.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile_snapshots"
    )
    profile_data = models.JSONField(default=dict, blank=True)
    date = models.DateTimeField(default=timezone.now)

    class Meta(BaseModel.Meta):
        verbose_name = "Profile Snapshot"
        verbose_name_plural = "Profile Snapshots"
        ordering = ["-date"]
