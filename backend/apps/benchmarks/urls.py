from django.urls import path
from .views import (
    BenchmarkTriggerView,
    BenchmarkReportView,
    BenchmarkHistoryView,
    RankLeaderboardView,
)

urlpatterns = [
    path("benchmark/", BenchmarkTriggerView.as_view(), name="benchmark-trigger"),
    path("benchmark/report/", BenchmarkReportView.as_view(), name="benchmark-report"),
    path("benchmark/history/", BenchmarkHistoryView.as_view(), name="benchmark-history"),
    path("rank/", RankLeaderboardView.as_view(), name="rank-leaderboard"),
]
