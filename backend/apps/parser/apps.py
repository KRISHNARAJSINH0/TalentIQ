"""Parser app configuration."""

from django.apps import AppConfig


class ParserConfig(AppConfig):
    """Configuration for the parser application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.parser"
    verbose_name = "Parser"
