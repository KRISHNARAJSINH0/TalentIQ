"""Profiles app configuration."""

from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    """Configuration for the profiles application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.profiles"
    verbose_name = "Profiles"
