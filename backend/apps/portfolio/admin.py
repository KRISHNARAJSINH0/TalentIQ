"""
Portfolio admin – Portfolio model admin configuration.
"""

from django.contrib import admin

from .models import Portfolio


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    """Admin view for the Portfolio model."""

    list_display = (
        "profile",
        "theme",
        "slug",
        "is_public",
        "created_at",
    )
    list_filter = (
        "theme",
        "is_public",
        "created_at",
    )
    search_fields = (
        "slug",
        "profile__user__email",
        "profile__user__first_name",
    )
    prepopulated_fields = {"slug": ()}
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        ("Portfolio", {"fields": ("id", "profile", "theme", "slug", "is_public")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
