from django.urls import path
from .views import (
    JDUploadView,
    JDAnalyzeView,
    JDHistoryView,
    JDReportView,
    JDGapsView,
    JDATSView,
)

app_name = "jd_analyzer"

urlpatterns = [
    path("upload/", JDUploadView.as_view(), name="upload"),
    path("analyze/", JDAnalyzeView.as_view(), name="analyze"),
    path("history/", JDHistoryView.as_view(), name="history"),
    path("report/<uuid:pk>/", JDReportView.as_view(), name="report"),
    path("gaps/<uuid:pk>/", JDGapsView.as_view(), name="gaps"),
    path("ats/<uuid:pk>/", JDATSView.as_view(), name="ats"),
]
