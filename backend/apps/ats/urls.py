"""
ATS URL configuration.
"""

from django.urls import path
from . import views

app_name = "ats"

urlpatterns = [
    path("analyze/", views.ATSAnalyzeView.as_view(), name="ats-analyze"),
    path("history/", views.ATSHistoryView.as_view(), name="ats-history"),
    path("report/<uuid:id>/", views.ATSReportDetailView.as_view(), name="ats-report-detail"),
    path("job-match/", views.ATSJobMatchView.as_view(), name="ats-job-match"),
    path("rules/", views.ATSRuleListView.as_view(), name="ats-rules-list"),
    path("rules/<int:pk>/", views.ATSRuleDetailView.as_view(), name="ats-rules-detail"),
    path("rules/import-export/", views.ATSRuleImportExportView.as_view(), name="ats-rules-import-export"),
    path("evaluate/", views.ATSEvaluateView.as_view(), name="ats-evaluate"),
    path("execution/", views.ATSRuleExecutionView.as_view(), name="ats-execution"),
    # Profession Profile Engine endpoints
    path("profiles/", views.ProfessionProfileListView.as_view(), name="ats-profiles-list"),
    path("profiles/seed/", views.ProfessionProfileSeedView.as_view(), name="ats-profiles-seed"),
    path("profile/<str:role>/", views.ProfessionProfileDetailView.as_view(), name="ats-profile-detail"),
    path("profile/", views.ProfessionProfileDetailView.as_view(), name="ats-profile-create"),
    path("<uuid:resume_id>/", views.ATSDetailView.as_view(), name="ats-detail"),
]
