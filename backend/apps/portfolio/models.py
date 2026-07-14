"""
Portfolio models – Generated portfolio websites.

Each portfolio is linked to a user profile and represents
a public-facing portfolio page with a unique slug.
"""

from django.db import models
from django.utils.text import slugify

from apps.common.models import BaseModel
from apps.profiles.models import Profile


class Portfolio(BaseModel):
    """
    A generated portfolio website for a user profile.

    Supports multiple themes and public/private visibility.
    The slug is used for the public URL.
    """

    class Theme(models.TextChoices):
        MODERN = "modern", "Modern"
        MINIMAL = "minimal", "Minimal"
        DEVELOPER = "developer", "Developer"
        CORPORATE = "corporate", "Corporate"
        CREATIVE = "creative", "Creative"
        DARK = "dark", "Dark"
        LIGHT = "light", "Light"
        GLASSMORPHISM = "glassmorphism", "Glassmorphism"
        PROFESSIONAL = "professional", "Professional"
        STUDENT = "student", "Student"
        RESEARCHER = "researcher", "Researcher"

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="portfolios",
        verbose_name="Profile",
    )
    theme = models.CharField(
        max_length=20,
        choices=Theme.choices,
        default=Theme.MODERN,
        verbose_name="Theme",
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name="Is Public",
        db_index=True,
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="URL Slug",
        help_text="Unique slug for the public portfolio URL.",
    )
    last_generated = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Generated At",
    )
    views = models.IntegerField(
        default=0,
        verbose_name="Views Count",
    )
    likes = models.IntegerField(
        default=0,
        verbose_name="Likes Count",
    )
    downloads = models.IntegerField(
        default=0,
        verbose_name="Downloads Count",
    )
    shares = models.IntegerField(
        default=0,
        verbose_name="Shares Count",
    )
    portfolio_json = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Portfolio JSON Data",
        help_text="Snapshot of verified master resume profile JSON.",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Portfolio"
        verbose_name_plural = "Portfolios"
        indexes = [
            models.Index(fields=["slug"], name="idx_portfolio_slug"),
        ]

    def __str__(self):
        return f"{self.profile.user.get_full_name()} – {self.get_theme_display()} Portfolio"

    def save(self, *args, **kwargs):
        """Auto-generate slug from username if not provided."""
        if not self.slug:
            base_slug = slugify(self.profile.user.username)
            slug = base_slug
            counter = 1
            while Portfolio.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class PortfolioAnalyticsLog(BaseModel):
    """
    Detailed logs for portfolio views, downloads, shares, and section views.
    """
    class EventType(models.TextChoices):
        VIEW = "view", "View"
        DOWNLOAD = "download", "Download"
        SHARE = "share", "Share"
        SECTION_VIEW = "section_view", "Section View"

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="activity_logs",
        verbose_name="Portfolio"
    )
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.VIEW,
        verbose_name="Event Type"
    )
    section_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Section Name"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP Address"
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name="User Agent"
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Portfolio Analytics Log"
        verbose_name_plural = "Portfolio Analytics Logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.portfolio.slug} – {self.get_event_type_display()} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
