"""
Profiles admin – Admin configuration for all profile-related models.

Registers Profile, Skill, Education, Experience, Project,
Certification, and Language with customised list displays,
search fields, filters, and inline editing.
"""

from django.contrib import admin

from .models import (
    Certification,
    Education,
    Experience,
    Language,
    Profile,
    Project,
    Skill,
)


# ---------------------------------------------------------------------------
# Inlines – edit child records directly on the Profile page
# ---------------------------------------------------------------------------

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1
    fields = ("skill_name", "skill_level")


class EducationInline(admin.StackedInline):
    model = Education
    extra = 0
    fields = ("institute", "degree", "field_of_study", "start_date", "end_date", "grade")


class ExperienceInline(admin.StackedInline):
    model = Experience
    extra = 0
    fields = (
        "company", "designation", "employment_type",
        "start_date", "end_date", "description",
    )


class ProjectInline(admin.StackedInline):
    model = Project
    extra = 0
    fields = ("project_name", "technologies", "description", "github_url", "live_url")


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0
    fields = ("certificate_name", "organization", "issue_date", "credential_url")


class LanguageInline(admin.TabularInline):
    model = Language
    extra = 1
    fields = ("language_name", "proficiency")


# ---------------------------------------------------------------------------
# Model admins
# ---------------------------------------------------------------------------

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin view for the Profile model with inline child records."""

    list_display = (
        "user",
        "headline",
        "city",
        "country",
        "created_at",
    )
    list_filter = ("country", "city", "created_at")
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "headline",
        "city",
        "country",
    )
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)
    inlines = [
        SkillInline,
        EducationInline,
        ExperienceInline,
        ProjectInline,
        CertificationInline,
        LanguageInline,
    ]

    fieldsets = (
        ("User", {"fields": ("id", "user")}),
        ("Professional", {"fields": ("headline", "summary")}),
        (
            "Location",
            {"fields": ("address", "city", "state", "country", "postal_code")},
        ),
        (
            "Links",
            {"fields": ("website", "github", "linkedin", "portfolio_url")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("skill_name", "skill_level", "profile", "created_at")
    list_filter = ("skill_level",)
    search_fields = ("skill_name", "profile__user__email")
    ordering = ("skill_name",)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("degree", "institute", "field_of_study", "start_date", "end_date", "profile")
    list_filter = ("degree",)
    search_fields = ("institute", "degree", "field_of_study", "profile__user__email")
    ordering = ("-end_date", "-start_date")


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("designation", "company", "employment_type", "start_date", "end_date", "profile")
    list_filter = ("employment_type",)
    search_fields = ("company", "designation", "profile__user__email")
    ordering = ("-end_date", "-start_date")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("project_name", "technologies", "profile", "created_at")
    search_fields = ("project_name", "technologies", "profile__user__email")
    ordering = ("-created_at",)


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("certificate_name", "organization", "issue_date", "profile")
    list_filter = ("organization",)
    search_fields = ("certificate_name", "organization", "profile__user__email")
    ordering = ("-issue_date",)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("language_name", "proficiency", "profile")
    list_filter = ("proficiency",)
    search_fields = ("language_name", "profile__user__email")
    ordering = ("language_name",)
