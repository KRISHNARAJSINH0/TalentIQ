"""Resumes app configuration."""

from django.apps import AppConfig


class ResumesConfig(AppConfig):
    """Configuration for the resumes application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.resumes"
    verbose_name = "Resumes"
