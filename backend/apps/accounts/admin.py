"""
Accounts admin – Custom User admin configuration.

Extends Django's UserAdmin with custom fields: phone, role, is_verified,
profile_photo, and UUID display.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin view for the custom User model."""

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "role",
        "is_verified",
        "is_active",
        "date_joined",
    )
    list_filter = (
        "role",
        "is_verified",
        "is_active",
        "is_staff",
        "date_joined",
    )
    search_fields = (
        "email",
        "username",
        "first_name",
        "last_name",
        "phone",
    )
    ordering = ("-date_joined",)
    readonly_fields = ("id", "date_joined", "updated_at")

    # Extend the default fieldsets with our custom fields
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "ResumeAI Info",
            {
                "fields": (
                    "id",
                    "phone",
                    "profile_photo",
                    "role",
                    "is_verified",
                    "updated_at",
                ),
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "phone",
                    "role",
                ),
            },
        ),
    )
