"""
JD Analyzer models – Phase 22.

Two core models:
  - JobDescription: stores uploaded/pasted JD text and parsed extraction.
  - JobAnalysis:    stores the full comparison report (resume ↔ JD).
"""

from django.conf import settings
from django.db import models
from apps.common.models import BaseModel
from apps.resumes.models import Resume


class JobDescription(BaseModel):
    """
    A job description uploaded by the user for analysis.
    """

    class SourceType(models.TextChoices):
        TEXT = "text", "Plain Text"
        PDF = "pdf", "PDF Document"
        DOCX = "docx", "Word Document"
        URL = "url", "URL"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_descriptions",
        verbose_name="User",
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Job Title",
    )
    company = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Company Name",
    )
    industry = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Industry",
    )
    content = models.TextField(
        verbose_name="Raw JD Content",
    )
    parsed_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Parsed Data",
        help_text="Structured extraction: sections, skills, requirements, etc.",
    )
    source_type = models.CharField(
        max_length=10,
        choices=SourceType.choices,
        default=SourceType.TEXT,
        verbose_name="Source Type",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Job Description"
        verbose_name_plural = "Job Descriptions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title or 'Untitled'} @ {self.company or 'Unknown'}"


class JobAnalysis(BaseModel):
    """
    Stores the full resume-vs-JD comparison report.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jd_analyses",
        verbose_name="User",
    )
    job_description = models.ForeignKey(
        JobDescription,
        on_delete=models.CASCADE,
        related_name="analyses",
        verbose_name="Job Description",
    )
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="jd_analyses",
        verbose_name="Resume",
    )

    # ── Scores ──────────────────────────────────────────────────────
    match_score = models.IntegerField(default=0, verbose_name="Overall Match Score")
    ats_score = models.IntegerField(default=0, verbose_name="ATS Score")
    skills_match = models.IntegerField(default=0, verbose_name="Skills Match %")
    experience_match = models.IntegerField(default=0, verbose_name="Experience Match %")
    education_match = models.IntegerField(default=0, verbose_name="Education Match %")
    keyword_match = models.IntegerField(default=0, verbose_name="Keyword Match %")

    # ── Lists ───────────────────────────────────────────────────────
    missing_skills = models.JSONField(default=list, blank=True)
    matching_skills = models.JSONField(default=list, blank=True)
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    suggestions = models.JSONField(default=list, blank=True)

    # ── Structured blobs ────────────────────────────────────────────
    interview_readiness = models.JSONField(default=dict, blank=True)
    salary_estimate = models.JSONField(default=dict, blank=True)
    report = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        verbose_name = "Job Analysis"
        verbose_name_plural = "Job Analyses"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Analysis #{self.id} – {self.match_score}% match"
