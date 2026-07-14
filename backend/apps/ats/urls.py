"""
ATS URL configuration.
"""

from django.urls import path
from . import views

app_name = "ats"

urlpatterns = [
    path("analyze/", views.ATSAnalyzeView.as_view(), name="ats-analyze"),
    path("history/", views.ATSHistoryView.as_view(), name="ats-history"),
    path("<uuid:resume_id>/", views.ATSDetailView.as_view(), name="ats-detail"),
]
