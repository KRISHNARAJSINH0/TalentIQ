"""
ATS models – Applicant Tracking System scoring.

Stores ATS analysis results for each resume including
overall score, detailed json data, processing details, and suggestions.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import BaseModel
from apps.resumes.models import Resume


class ATSScore(BaseModel):
    """
    ATS analysis result for a resume.

    Foreign key with Resume to support analysis history.
    """

    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="ats_analyses",
        verbose_name="Resume",
    )
    ats_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Overall ATS Score",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall ATS compatibility score (0-100).",
    )
    ats_json = models.JSONField(
        verbose_name="ATS Analysis JSON",
        help_text="Detailed JSON containing all sub-scores, keyword analyses, grammar notes, and stats.",
    )
    ats_completed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Completed At",
    )
    ats_processing_time = models.FloatField(
        verbose_name="Processing Time (Seconds)",
        help_text="Time taken to perform the ATS analysis in seconds.",
    )
    industry_match = models.JSONField(
        verbose_name="Industry Matches",
        help_text="List/dict of industry match percentages.",
    )
    missing_skills = models.JSONField(
        verbose_name="Missing Skills",
        help_text="Suggested skills based on detected primary industry.",
    )
    suggestions = models.JSONField(
        verbose_name="Suggestions",
        help_text="Actionable suggestions categorized by priority.",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "ATS Score"
        verbose_name_plural = "ATS Scores"
        ordering = ["-ats_completed_at"]

    def __str__(self):
        return f"ATS {self.ats_score}/100 – {self.resume.resume_title} (Completed: {self.ats_completed_at})"
