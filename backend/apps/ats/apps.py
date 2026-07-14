"""ATS app configuration."""

from django.apps import AppConfig


class AtsConfig(AppConfig):
    """Configuration for the ATS application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ats"
    verbose_name = "ATS"
