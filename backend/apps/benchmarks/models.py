from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import BaseModel
from apps.resumes.models import Resume


class BenchmarkReport(BaseModel):
    """
    Stores overall benchmark rankings, metrics comparison, strengths, weaknesses,
    and improvement estimations for a resume.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="benchmark_reports",
        verbose_name="Resume"
    )
    overall_rank = models.CharField(
        max_length=50,
        verbose_name="Overall Rank (e.g. Top 12%)"
    )
    profession_rank = models.CharField(
        max_length=50,
        verbose_name="Profession Rank"
    )
    industry_rank = models.CharField(
        max_length=50,
        verbose_name="Industry Rank"
    )
    country_rank = models.CharField(
        max_length=50,
        verbose_name="Country Rank"
    )
    experience_rank = models.CharField(
        max_length=50,
        verbose_name="Experience Rank"
    )
    
    # Store list of strengths and weaknesses as JSON lists
    strengths = models.JSONField(
        default=list,
        verbose_name="Strengths List"
    )
    weaknesses = models.JSONField(
        default=list,
        verbose_name="Weaknesses List"
    )
    
    # Stores percentiles for individual comparison metrics (Skills, Projects, etc.)
    comparison_metrics = models.JSONField(
        default=dict,
        verbose_name="Comparison Metrics"
    )
    
    # Stores projected improvements after acquiring skills or upgrading projects
    improvement_potential = models.JSONField(
        default=list,
        verbose_name="Improvement Potential"
    )
    
    # Raw detail json
    details_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Raw Details JSON"
    )
    
    class Meta:
        verbose_name = "Benchmark Report"
        verbose_name_plural = "Benchmark Reports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Benchmark for {self.resume.resume_title} ({self.overall_rank})"


class RankingHistory(BaseModel):
    """
    Tracks overall rank position improvements/changes over time.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="ranking_histories",
        verbose_name="Resume"
    )
    overall_rank = models.CharField(
        max_length=50,
        verbose_name="Overall Rank"
    )
    overall_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Overall Score"
    )
    recorded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Recorded At"
    )
    
    class Meta:
        verbose_name = "Ranking History"
        verbose_name_plural = "Ranking Histories"
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"History: {self.resume.resume_title} - {self.overall_rank} at {self.recorded_at}"


class CareerRanking(BaseModel):
    """
    Caches calculated ranking distributions by specific segment combinations.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="career_rankings",
        verbose_name="Resume"
    )
    profession = models.CharField(
        max_length=100,
        verbose_name="Profession"
    )
    experience_level = models.CharField(
        max_length=50,
        verbose_name="Experience Level"
    )
    industry = models.CharField(
        max_length=100,
        verbose_name="Industry"
    )
    country = models.CharField(
        max_length=100,
        verbose_name="Country"
    )
    percentile = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="Calculated Percentile Score"
    )
    
    class Meta:
        verbose_name = "Career Ranking"
        verbose_name_plural = "Career Rankings"
        ordering = ["-percentile"]

    def __str__(self):
        return f"{self.resume.resume_title}: {self.profession} - {self.percentile}%"
