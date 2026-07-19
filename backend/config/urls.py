"""
ResumeAI URL Configuration.

Root URL router for all API endpoints and admin.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes as perm_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@perm_classes([AllowAny])
def api_root(request):
    """API health check endpoint."""
    return Response({
        "status": "online",
        "message": "Welcome to ResumeAI API",
        "version": "1.0.0",
    })


from apps.common.health_views import (
    HealthCheckView,
    DbHealthCheckView,
    CacheHealthCheckView,
    CeleryHealthCheckView,
    SystemHealthCheckView,
)
from apps.resumes.views import (
    ResumeSectionDetectionView,
    ResumeConfidenceView,
    ResumeConfidenceDetailView,
    ResumeSemanticValidationView,
    ResumeSemanticDetailView,
    ResumeErrorDetectionView,
    ResumeErrorDetailView,
    ResumeErrorSummaryView,
    ResumeRecoveryView,
    ResumeRecoveryDetailView,
    ResumeRecoveryHistoryView,
    ResumeConsistencyView,
    ResumeConsistencyDetailView,
    ResumeConsistencyHistoryView,
    ResumeSourceView,
    ResumeSourceDetailView,
    ResumeSourceHistoryView,
    ResumeSourceAuditView,
    ResumeSelfHealingView,
    ResumeSelfHealingDetailView,
    ResumeSelfHealingReportView,
    ResumeCopilotChatView,
    ResumeCopilotActionView,
    ResumeCopilotHistoryView,
    ResumeCopilotSuggestionsView,
    ResumeCopilotChangesView,
)
from apps.jobs.views import JobATSView, JobATSReportView, JobATHistoryView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_root, name="api-root"),
    
    # Health checks
    path("api/health/", HealthCheckView.as_view(), name="health"),
    path("api/health/db/", DbHealthCheckView.as_view(), name="health-db"),
    path("api/health/cache/", CacheHealthCheckView.as_view(), name="health-cache"),
    path("api/health/celery/", CeleryHealthCheckView.as_view(), name="health-celery"),
    path("api/health/system/", SystemHealthCheckView.as_view(), name="health-system"),

    path("api/auth/", include("apps.accounts.urls")),
    path("api/profiles/", include("apps.profiles.urls")),
    path("api/profile/", include("apps.profiles.urls")),
    path("api/resume/sections/", ResumeSectionDetectionView.as_view(), name="resume-sections"),
    path("api/resume/confidence/", ResumeConfidenceView.as_view(), name="resume-confidence"),
    path("api/resume/confidence/<uuid:pk>/", ResumeConfidenceDetailView.as_view(), name="resume-confidence-detail"),
    path("api/resume/semantic/", ResumeSemanticValidationView.as_view(), name="resume-semantic"),
    path("api/resume/semantic/<uuid:pk>/", ResumeSemanticDetailView.as_view(), name="resume-semantic-detail"),

    # Error Detection Engine Endpoints (Stage 8)
    path("api/resume/errors/", ResumeErrorDetectionView.as_view(), name="resume-errors"),
    path("api/ai/errors/", ResumeErrorDetectionView.as_view(), name="ai-errors"),
    path("api/resume/errors/summary/", ResumeErrorSummaryView.as_view(), name="resume-errors-summary"),
    path("api/ai/errors/summary/", ResumeErrorSummaryView.as_view(), name="ai-errors-summary"),
    path("api/resume/errors/<uuid:pk>/", ResumeErrorDetailView.as_view(), name="resume-errors-detail"),
    path("api/ai/errors/<uuid:pk>/", ResumeErrorDetailView.as_view(), name="ai-errors-detail"),

    # AI Recovery Engine Endpoints (Stage 9 / Phase 9.5)
    path("api/recovery/", ResumeRecoveryView.as_view(), name="recovery"),
    path("api/recovery/history/", ResumeRecoveryHistoryView.as_view(), name="recovery-history"),
    path("api/recovery/<uuid:pk>/", ResumeRecoveryDetailView.as_view(), name="recovery-detail"),

    # Consistency Checker Endpoints (Stage 9 / Phase 9.6)
    path("api/consistency/", ResumeConsistencyView.as_view(), name="consistency"),
    path("api/consistency/history/", ResumeConsistencyHistoryView.as_view(), name="consistency-history"),
    path("api/consistency/<uuid:pk>/", ResumeConsistencyDetailView.as_view(), name="consistency-detail"),

    # Source Tracking Engine Endpoints (Stage 9 / Phase 9.7)
    path("api/source/", ResumeSourceView.as_view(), name="source"),
    path("api/source/history/", ResumeSourceHistoryView.as_view(), name="source-history"),
    path("api/source/audit/", ResumeSourceAuditView.as_view(), name="source-audit"),
    path("api/source/<uuid:pk>/", ResumeSourceDetailView.as_view(), name="source-detail"),

    # Self-Healing Parser Endpoints (Stage 9 / Phase 9.8)
    path("api/self-healing/", ResumeSelfHealingView.as_view(), name="self-healing"),
    path("api/self-healing/report/", ResumeSelfHealingReportView.as_view(), name="self-healing-report"),
    path("api/self-healing/<uuid:pk>/", ResumeSelfHealingDetailView.as_view(), name="self-healing-detail"),

    # Resume Copilot Endpoints (Stage 9 / Phase 9.9)
    path("api/copilot/chat/", ResumeCopilotChatView.as_view(), name="copilot-chat"),
    path("api/copilot/action/", ResumeCopilotActionView.as_view(), name="copilot-action"),
    path("api/copilot/history/", ResumeCopilotHistoryView.as_view(), name="copilot-history"),
    path("api/copilot/suggestions/", ResumeCopilotSuggestionsView.as_view(), name="copilot-suggestions"),
    path("api/copilot/changes/", ResumeCopilotChangesView.as_view(), name="copilot-changes"),

    path("api/resumes/", include("apps.resumes.urls")),
    path("api/parser/", include("apps.parser.urls")),
    path("api/portfolio/", include("apps.portfolio.urls")),
    path("api/ats/", include("apps.ats.urls")),
    path("api/career/", include("apps.career.urls")),
    path("api/common/", include("apps.common.urls")),
    path("api/timeline/", include("apps.timeline.urls")),
    path("api/admin/", include("apps.admin_intelligence.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/jobs/", include("apps.jobs.urls")),
    path("api/jd/", include("apps.jd_analyzer.urls")),
    path("api/ai/reputation/", include("apps.reputation.urls")),
    
    # Phase F: Benchmark & Ranking Engine routes
    path("api/", include("apps.benchmarks.urls")),

    # Phase E: Job-Specific ATS routes
    path("api/job-ats/", include([
        path("", JobATSView.as_view(), name="job-ats-evaluate"),
        path("report/", JobATSReportView.as_view(), name="job-ats-report"),
        path("history/", JobATHistoryView.as_view(), name="job-ats-history"),
    ])),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
