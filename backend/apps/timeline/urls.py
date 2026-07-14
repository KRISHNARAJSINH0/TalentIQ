from django.urls import path

from .views import (
    TimelineEventCreateView,
    TimelineListView,
    TimelineHistoryView,
    TimelineVersionsListView,
    TimelineCompareView,
)

app_name = "timeline"

urlpatterns = [
    path("event/", TimelineEventCreateView.as_view(), name="timeline-event-create"),
    path("", TimelineListView.as_view(), name="timeline-list"),
    path("history/", TimelineHistoryView.as_view(), name="timeline-history"),
    path("versions/", TimelineVersionsListView.as_view(), name="timeline-versions"),
    path("compare/", TimelineCompareView.as_view(), name="timeline-compare"),
]
