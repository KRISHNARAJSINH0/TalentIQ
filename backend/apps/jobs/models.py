from django.db import models
from apps.common.models import BaseModel
from apps.resumes.models import Resume


class JobRecommendation(BaseModel):
    """
    Stores a recommended job matching the candidate's active resume.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="job_recommendations",
        verbose_name="Resume"
    )
    title = models.CharField(max_length=255, verbose_name="Job Title")
    score = models.IntegerField(default=0, verbose_name="Match Score")
    salary = models.CharField(max_length=100, blank=True, verbose_name="Salary Range")
    industry = models.CharField(max_length=255, blank=True, verbose_name="Industry")
    country = models.CharField(max_length=100, blank=True, verbose_name="Country")
    remote = models.BooleanField(default=False, verbose_name="Remote Eligible")
    missing_skills = models.JSONField(default=list, blank=True, verbose_name="Missing Skills")

    class Meta(BaseModel.Meta):
        verbose_name = "Job Recommendation"
        verbose_name_plural = "Job Recommendations"
        ordering = ["-score", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.score}%) - Resume #{self.resume_id}"


class SkillGap(BaseModel):
    """
    Persists specific identified missing skill gaps for a candidate.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="skill_gaps",
        verbose_name="Resume"
    )
    skill = models.CharField(max_length=150, verbose_name="Skill Name")
    importance = models.CharField(
        max_length=50,
        default="Medium",
        verbose_name="Importance Level"
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Skill Gap"
        verbose_name_plural = "Skill Gaps"
        unique_together = ("resume", "skill")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.skill} ({self.importance}) - Resume #{self.resume_id}"
