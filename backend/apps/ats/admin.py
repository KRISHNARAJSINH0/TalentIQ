"""
ATS admin – ATSScore model admin configuration.
"""

from django.contrib import admin

from .models import ATSScore


@admin.register(ATSScore)
class ATSScoreAdmin(admin.ModelAdmin):
    """Admin view for the ATSScore model."""

    list_display = (
        "resume",
        "ats_score",
        "ats_completed_at",
        "ats_processing_time",
        "created_at",
    )
    list_filter = ("ats_completed_at", "created_at")
    search_fields = (
        "resume__resume_title",
        "resume__user__email",
    )
    readonly_fields = ("id", "ats_completed_at", "created_at", "updated_at")
    ordering = ("-ats_completed_at",)

    fieldsets = (
        ("Resume", {"fields": ("id", "resume")}),
        (
            "Analysis Meta",
            {"fields": ("ats_score", "ats_processing_time", "ats_completed_at")},
        ),
        (
            "Detailed Analysis",
            {"fields": ("industry_match", "missing_skills", "suggestions", "ats_json")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
