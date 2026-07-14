from django.contrib import admin
from .models import JobDescription, JobAnalysis


@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "industry", "source_type", "user", "created_at")
    list_filter = ("source_type", "industry")
    search_fields = ("title", "company", "content")
    readonly_fields = ("parsed_data",)


@admin.register(JobAnalysis)
class JobAnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "match_score", "ats_score", "skills_match", "user", "created_at")
    list_filter = ("match_score", "ats_score")
    readonly_fields = ("report",)
