from django.urls import path
from .views import (
    CareerAnalysisView,
    CareerProfileDetailView,
    RoadmapDetailView,
    SkillGapDetailView,
    CoverLetterGenerateView,
    CoverLetterListView,
    LearningProgressUpdateView
)

app_name = "career"

urlpatterns = [
    path("analyze/", CareerAnalysisView.as_view(), name="career-analyze"),
    path("", CareerProfileDetailView.as_view(), name="career-detail"),
    path("roadmap/", RoadmapDetailView.as_view(), name="career-roadmap"),
    path("skills/", SkillGapDetailView.as_view(), name="career-skills"),
    path("cover-letter/", CoverLetterGenerateView.as_view(), name="career-cover-letter"),
    path("history/", CoverLetterListView.as_view(), name="career-history"),
    path("progress/", LearningProgressUpdateView.as_view(), name="career-progress"),
]
