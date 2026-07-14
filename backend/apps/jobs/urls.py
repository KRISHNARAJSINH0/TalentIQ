from django.urls import path
from .views import (
    JobMatchView,
    JobPredictView,
    JobRecommendationsView,
    JobMarketView,
    JobSalaryView,
    JobCompaniesView,
    JobSkillsGapView,
)

app_name = "jobs"

urlpatterns = [
    path("match/", JobMatchView.as_view(), name="match"),
    path("predict/", JobPredictView.as_view(), name="predict"),
    path("recommendations/", JobRecommendationsView.as_view(), name="recommendations"),
    path("market/", JobMarketView.as_view(), name="market"),
    path("salary/", JobSalaryView.as_view(), name="salary"),
    path("companies/", JobCompaniesView.as_view(), name="companies"),
    path("skills-gap/", JobSkillsGapView.as_view(), name="skills-gap"),
]
