"""
Resumes admin – Resume model admin configuration.
"""

from django.contrib import admin

from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    """Admin view for the Resume model."""

    list_display = (
        "resume_title",
        "user",
        "version",
        "is_active",
        "upload_status",
        "upload_date",
        "is_deleted",
    )
    list_filter = (
        "is_active",
        "upload_status",
        "is_deleted",
        "upload_date",
    )
    search_fields = (
        "resume_title",
        "original_filename",
        "user__email",
        "user__username",
    )
    readonly_fields = (
        "id",
        "version",
        "stored_filename",
        "file_size",
        "mime_type",
        "upload_date",
        "created_at",
        "updated_at",
        "extracted_text",
        "parsed_json",
    )
    ordering = ("-upload_date",)

    fieldsets = (
        ("Resume Details", {"fields": ("id", "user", "resume_title", "original_file", "original_filename", "stored_filename")}),
        ("Metadata", {"fields": ("version", "is_active", "file_size", "mime_type", "upload_status")}),
        ("Parsing (Future)", {"fields": ("parsing_status", "extracted_text", "parsed_json")}),
        ("Status", {"fields": ("is_deleted", "deleted_at")}),
        ("Timestamps", {"fields": ("upload_date", "created_at", "updated_at")}),
    )
