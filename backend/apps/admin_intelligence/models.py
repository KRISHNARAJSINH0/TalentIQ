from django.conf import settings
from django.db import models
# pyrefly: ignore [missing-import]
from apps.common.models import BaseModel


class AdminMetrics(BaseModel):
    """Stores daily snapshots of key platform metrics."""
    recorded_date = models.DateField(auto_now_add=True, unique=True, verbose_name="Recorded Date")
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    uploaded_resumes = models.IntegerField(default=0)
    generated_portfolios = models.IntegerField(default=0)
    generated_cover_letters = models.IntegerField(default=0)
    average_ats_score = models.FloatField(default=0.0)
    average_career_score = models.FloatField(default=0.0)
    average_completion_percentage = models.FloatField(default=0.0)
    storage_consumption = models.BigIntegerField(default=0, help_text="Total resume storage used in bytes")
    ai_requests = models.IntegerField(default=0)
    api_calls = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Admin Metrics"
        verbose_name_plural = "Admin Metrics Snapshots"
        ordering = ["-recorded_date"]

    def __str__(self):
        return f"Metrics snapshot for {self.recorded_date}"


class UsageAnalytics(BaseModel):
    """Tracks individual API calls and AI processing requests."""
    class EventType(models.TextChoices):
        API_CALL = "api_call", "API Call"
        AI_PARSE = "ai_parse", "AI Parse"
        ATS_SCORE = "ats_score", "ATS Score"
        CAREER_ANALYSIS = "career_analysis", "Career Analysis"
        PORTFOLIO_GEN = "portfolio_gen", "Portfolio Generation"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usage_logs",
        verbose_name="User"
    )
    event_type = models.CharField(max_length=50, choices=EventType.choices, default=EventType.API_CALL)
    endpoint = models.CharField(max_length=255, db_index=True)
    status_code = models.IntegerField(default=200)
    processing_time = models.FloatField(default=0.0, help_text="Duration in seconds")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Usage Analytics Log"
        verbose_name_plural = "Usage Analytics Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["user", "event_type"]),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} on {self.endpoint} ({self.status_code})"


class SystemHealth(BaseModel):
    """Logs resource usage and service states."""
    cpu_usage = models.FloatField(default=0.0)
    memory_usage = models.FloatField(default=0.0)
    storage_used = models.BigIntegerField(default=0)
    storage_total = models.BigIntegerField(default=0)
    database_status = models.CharField(max_length=50, default="healthy")
    ai_service_status = models.CharField(max_length=50, default="healthy")
    queue_status = models.CharField(max_length=50, default="healthy")
    background_jobs_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = "System Health Log"
        verbose_name_plural = "System Health Logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"System Health ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class AuditLog(BaseModel):
    """Audit trails of administrative actions."""
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_audit_logs",
        verbose_name="Admin User"
    )
    action = models.CharField(max_length=100)
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_audit_targets",
        verbose_name="Target User"
    )
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.admin.username} performed {self.action} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class UserStatistics(BaseModel):
    """Aggregated user retention and registration metrics per month."""
    month = models.DateField(unique=True)
    new_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    growth_rate = models.FloatField(default=0.0, help_text="Percentage growth month-over-month")
    retention_rate = models.FloatField(default=0.0, help_text="Percentage active retention rate")

    class Meta:
        verbose_name = "User Statistic"
        verbose_name_plural = "User Statistics"
        ordering = ["-month"]

    def __str__(self):
        return f"Stats for {self.month.strftime('%Y-%m')}"


class IndustryStatistics(BaseModel):
    """Stores trending market roles, skills, and tools extracted from profiles."""
    class Category(models.TextChoices):
        ROLE = "role", "Job Role"
        SKILL = "skill", "Skill"
        CERTIFICATION = "certification", "Certification"
        TECHNOLOGY = "technology", "Technology"
        INDUSTRY = "industry", "Industry"

    category = models.CharField(max_length=50, choices=Category.choices, db_index=True)
    name = models.CharField(max_length=150, db_index=True)
    count = models.IntegerField(default=1)
    trend_score = models.FloatField(default=0.0, help_text="Growth rate or importance weight")

    class Meta:
        verbose_name = "Industry Statistic"
        verbose_name_plural = "Industry Statistics"
        unique_together = ("category", "name")
        ordering = ["-count"]

    def __str__(self):
        return f"[{self.get_category_display()}] {self.name} : {self.count}"
