from django.db import models
from django.conf import settings

class Notification(models.Model):
    """
    Main notification model storing standard notifications.
    """
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    class Type(models.TextChoices):
        RESUME_UPLOADED = "resume_uploaded", "Resume Uploaded"
        RESUME_PARSED = "resume_parsed", "Resume Parsed"
        ATS_IMPROVED = "ats_improved", "ATS Improved"
        ATS_DECREASED = "ats_decreased", "ATS Decreased"
        SKILL_RECOMMENDATION = "skill_recommendation", "Skill Recommendation"
        MISSING_SKILLS = "missing_skills", "Missing Skills"
        CAREER_SUGGESTION = "career_suggestion", "Career Suggestion"
        PORTFOLIO_VIEWED = "portfolio_viewed", "Portfolio Viewed"
        PORTFOLIO_SHARED = "portfolio_shared", "Portfolio Shared"
        COVER_LETTER_GENERATED = "cover_letter_generated", "Cover Letter Generated"
        NEW_RESUME_VERSION = "new_resume_version", "New Resume Version"
        ROADMAP_MILESTONE = "roadmap_milestone", "Roadmap Milestone"
        CERTIFICATE_REMINDER = "certificate_reminder", "Certificate Reminder"
        JOB_SUGGESTION = "job_suggestion", "Job Suggestion"
        WEEKLY_REPORT = "weekly_report", "Weekly Report"
        MONTHLY_REPORT = "monthly_report", "Monthly Report"
        SYSTEM_ANNOUNCEMENT = "system_announcement", "System Announcement"
        SECURITY_ALERT = "security_alert", "Security Alert"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
        help_text="Null represents a system-wide or global notification."
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=50, choices=Type.choices, default=Type.SYSTEM_ANNOUNCEMENT)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.NORMAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.type} - {self.title} ({self.user})"


class NotificationPreference(models.Model):
    """
    User settings toggles for notifications delivery preferences.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences"
    )
    enable_email = models.BooleanField(default=True)
    enable_ats_alerts = models.BooleanField(default=True)
    enable_career_alerts = models.BooleanField(default=True)
    enable_portfolio_alerts = models.BooleanField(default=True)
    enable_weekly_reports = models.BooleanField(default=True)
    enable_monthly_reports = models.BooleanField(default=True)
    enable_security_notifications = models.BooleanField(default=True)

    def __str__(self):
        return f"Preferences for {self.user.email}"


class EmailQueue(models.Model):
    """
    Buffer table for queueing outgoing notification emails.
    """
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_queue"
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Email {self.status} to {self.user.email}: {self.subject}"


class NotificationHistory(models.Model):
    """
    Archives logs of dispatched notifications and channels used.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_history"
    )
    notification_type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    delivered_at = models.DateTimeField(auto_now_add=True)
    delivery_method = models.CharField(max_length=50)  # In-App, Email, Push, SMS, Webhook

    def __str__(self):
        return f"History: {self.notification_type} via {self.delivery_method} to {self.user.email}"


class Reminder(models.Model):
    """
    Future scheduling of milestone completions or certificate updates.
    """
    class ReminderType(models.TextChoices):
        MILESTONE = "milestone", "Roadmap Milestone"
        CERTIFICATE = "certificate", "Certificate Renewal"
        OTHER = "other", "Other Reminder"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reminders"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    reminder_type = models.CharField(max_length=50, choices=ReminderType.choices, default=ReminderType.OTHER)
    due_date = models.DateTimeField()
    triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reminder: {self.title} due on {self.due_date}"


class Digest(models.Model):
    """
    Compiles aggregated dashboard activity metrics for periodic reports.
    """
    class DigestType(models.TextChoices):
        WEEKLY = "weekly", "Weekly Digest"
        MONTHLY = "monthly", "Monthly Digest"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="digests"
    )
    digest_type = models.CharField(max_length=20, choices=DigestType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.digest_type} for {self.user.email} ({self.start_date} - {self.end_date})"


class Announcement(models.Model):
    """
    Global system announcements published by administrators.
    """
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=Notification.Priority.choices,
        default=Notification.Priority.NORMAL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Announcement: {self.title}"
