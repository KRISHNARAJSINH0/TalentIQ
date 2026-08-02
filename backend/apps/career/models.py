from django.conf import settings
from django.db import models

# pyrefly: ignore [missing-import]
from apps.common.models import BaseModel
# pyrefly: ignore [missing-import]
from apps.profiles.models import Profile


class CareerProfile(BaseModel):
    """
    Stores calculated career scores, roadmaps, and detailed analysis
    derived from the user's verified Profile.
    """
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name="career_profile",
        verbose_name="Profile"
    )
    
    # Career Score metrics (out of 100)
    career_readiness = models.IntegerField(default=70, verbose_name="Career Readiness Score")
    growth_score = models.IntegerField(default=70, verbose_name="Growth Score")
    learning_score = models.IntegerField(default=70, verbose_name="Learning Score")
    industry_alignment = models.IntegerField(default=70, verbose_name="Industry Alignment")
    skill_strength = models.IntegerField(default=70, verbose_name="Skill Strength")
    market_demand = models.IntegerField(default=70, verbose_name="Market Demand")

    # JSON Document stores
    career_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Career Analysis JSON",
        help_text="Stores current role, stage, strengths, weaknesses, directions, role suggestions."
    )
    roadmap_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Learning Roadmap JSON",
        help_text="Stores sequenced technologies, courses, books, certifications, duration details."
    )

    class Meta:
        verbose_name = "Career Profile"
        verbose_name_plural = "Career Profiles"

    def __str__(self):
        return f"Career Profile for {self.profile.user.username}"


class CoverLetter(BaseModel):
    """
    Stores history of cover letters generated for job applications.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cover_letters",
        verbose_name="User"
    )
    company = models.CharField(max_length=200, verbose_name="Company Name")
    position = models.CharField(max_length=200, verbose_name="Position/Job Role")
    job_description = models.TextField(blank=True, verbose_name="Job Description")
    tone = models.CharField(max_length=50, verbose_name="Cover Letter Tone")
    cover_letter_type = models.CharField(max_length=100, verbose_name="Letter Type")
    content = models.TextField(verbose_name="Cover Letter Body")

    class Meta:
        verbose_name = "Cover Letter"
        verbose_name_plural = "Cover Letters"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.cover_letter_type} for {self.position} at {self.company}"


class LearningProgressLog(BaseModel):
    """
    Tracks checkboxes completed by the candidate on their learning roadmap.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learning_progress",
        verbose_name="User"
    )
    milestone_title = models.CharField(max_length=200, verbose_name="Roadmap Milestone")
    item_name = models.CharField(max_length=200, verbose_name="Target Technology/Course")
    category = models.CharField(max_length=100, verbose_name="Category")
    is_completed = models.BooleanField(default=False, verbose_name="Completed")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Completed At")

    class Meta:
        verbose_name = "Learning Progress Log"
        verbose_name_plural = "Learning Progress Logs"
        unique_together = ("user", "milestone_title", "item_name")

    def __str__(self):
        status = "Completed" if self.is_completed else "Pending"
        return f"{self.item_name} under {self.milestone_title} - {status}"
