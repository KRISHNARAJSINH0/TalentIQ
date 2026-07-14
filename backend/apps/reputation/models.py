from django.db import models
from apps.common.models import BaseModel
from apps.resumes.models import Resume


class ResumeReputation(BaseModel):
    """
    Persists career reputation, strength, and market fit metrics for a resume.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="reputations",
        verbose_name="Resume"
    )
    score = models.IntegerField(verbose_name="Reputation Score")
    tier = models.CharField(max_length=50, verbose_name="Reputation Tier")
    career_score = models.IntegerField(verbose_name="Career Score")
    growth_score = models.IntegerField(verbose_name="Growth Score")
    market_score = models.IntegerField(verbose_name="Market Score")
    
    # Stores the raw computed details for sub-scores (ATS, projects, portfolio, etc.)
    details_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Full Details JSON"
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Resume Reputation"
        verbose_name_plural = "Resume Reputations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Reputation {self.score}/100 ({self.tier}) - {self.resume.resume_title}"


class Badge(BaseModel):
    """
    Credentials and accolades earned by resumes meeting reputation criteria.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="badges",
        verbose_name="Resume"
    )
    badge = models.CharField(max_length=100, verbose_name="Badge Name")
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name="Earned At")

    class Meta(BaseModel.Meta):
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
        ordering = ["-earned_at"]
        unique_together = ("resume", "badge")

    def __str__(self):
        return f"{self.badge} - {self.resume.resume_title}"
