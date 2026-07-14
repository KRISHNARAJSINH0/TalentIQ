from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import TimelineEvent, ResumeVersion
from .serializers import TimelineEventSerializer, ResumeVersionSerializer
from .services import TimelineService, ComparisonService, GrowthAnalyticsService


class TimelineEventCreateView(APIView):
    """
    POST /api/timeline/event/
    Log a custom timeline event.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        event_type = request.data.get("event_type")
        title = request.data.get("title")
        description = request.data.get("description", "")
        metadata = request.data.get("metadata", {})

        if not event_type or not title:
            return Response(
                {"error": "Both 'event_type' and 'title' are required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate event type choice
        valid_types = [choice[0] for choice in TimelineEvent.EventType.choices]
        if event_type not in valid_types:
            return Response(
                {"error": f"Invalid event_type. Must be one of {valid_types}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        event = TimelineService.log_event(
            user=request.user,
            event_type=event_type,
            title=title,
            description=description,
            metadata=metadata
        )
        serializer = TimelineEventSerializer(event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TimelineListView(APIView):
    """
    GET /api/timeline/
    List filtered, paginated timeline events for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = TimelineEvent.objects.filter(user=request.user)

        # Apply Filters
        event_type = request.query_params.get("event_type")
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(description__icontains=search)

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 15
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
        serializer = TimelineEventSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class TimelineHistoryView(APIView):
    """
    GET /api/timeline/history/
    Get time-series history metrics for chart renderers.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        analytics = GrowthAnalyticsService.get_growth_analytics(request.user)
        return Response(analytics)


class TimelineVersionsListView(APIView):
    """
    GET /api/timeline/versions/
    Get all resume/profile versions.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        versions = ResumeVersion.objects.filter(user=request.user)
        serializer = ResumeVersionSerializer(versions, many=True)
        return Response(serializer.data)


class TimelineCompareView(APIView):
    """
    GET /api/timeline/compare/
    Compare two or three selected versions.
    Requires query parameters 'v1' and 'v2', and optionally 'v3' (UUID strings).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        v1_id = request.query_params.get("v1")
        v2_id = request.query_params.get("v2")
        v3_id = request.query_params.get("v3")

        if not v1_id or not v2_id:
            return Response(
                {"error": "Query parameters 'v1' and 'v2' (UUIDs) are required for comparison."},
                status=status.HTTP_400_BAD_REQUEST
            )

        v1 = get_object_or_404(ResumeVersion, id=v1_id, user=request.user)
        v2 = get_object_or_404(ResumeVersion, id=v2_id, user=request.user)
        v3 = None
        if v3_id:
            v3 = get_object_or_404(ResumeVersion, id=v3_id, user=request.user)

        comparison_data = ComparisonService.compare_versions(v1, v2, v3)
        return Response(comparison_data)
