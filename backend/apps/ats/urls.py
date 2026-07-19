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
    # Category Scoring Engine endpoints
    path("categories/", views.CategoryListView.as_view(), name="ats-categories-list"),
    path("category-score/", views.CategoryScoreDetailView.as_view(), name="ats-category-score"),
    path("category-report/", views.CategoryReportView.as_view(), name="ats-category-report"),
    # Phase D Penalty & Bonus Engine endpoints
    path("adjustments/", views.ATSAdjustmentsView.as_view(), name="ats-adjustments"),
    path("penalties/", views.ATSPenaltiesView.as_view(), name="ats-penalties"),
    path("bonuses/", views.ATSBonusesView.as_view(), name="ats-bonuses"),
    # Phase G Explainable ATS Intelligence endpoints
    path("explain/", views.ExplainScoreView.as_view(), name="ats-explain"),
    path("explanation/", views.ExplanationDetailView.as_view(), name="ats-explanation"),
    path("simulate/", views.SimulateScoreView.as_view(), name="ats-simulate"),
    path("action-plan/", views.ActionPlanView.as_view(), name="ats-action-plan"),
    path("<uuid:resume_id>/", views.ATSDetailView.as_view(), name="ats-detail"),
    # Phase H Calibration & Validation endpoints
    path("calibrate/", views.CalibrateView.as_view(), name="ats-calibrate"),
    path("validate/", views.ValidateView.as_view(), name="ats-validate"),
    path("health/", views.EngineHealthView.as_view(), name="ats-health"),
    path("distribution/", views.DistributionView.as_view(), name="ats-distribution"),
    path("quality/", views.QualityReportView.as_view(), name="ats-quality"),
]


