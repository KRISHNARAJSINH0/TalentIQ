from django.urls import path
from .views import (
    ReputationView,
    ReputationHistoryView,
    ReputationBadgesView,
    ReputationBenchmarkView,
)

app_name = "reputation"

urlpatterns = [
    path("", ReputationView.as_view(), name="reputation-detail"),
    path("history/", ReputationHistoryView.as_view(), name="reputation-history"),
    path("badges/", ReputationBadgesView.as_view(), name="reputation-badges"),
    path("benchmark/", ReputationBenchmarkView.as_view(), name="reputation-benchmark"),
]
