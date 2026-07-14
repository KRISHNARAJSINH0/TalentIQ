from rest_framework import status, permissions, views
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from .models import Notification, NotificationHistory, Announcement
from .serializers import (
    NotificationSerializer,
    NotificationPreferenceSerializer,
    ReminderSerializer,
    AnnouncementSerializer
)
from .services import NotificationService, PreferenceService

class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class NotificationListView(views.APIView):
    """
    GET /api/notifications/
    Retrieves user notifications (including global announcements).
    Supports filtering by read status (true/false) and type.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Fetch notifications belonging to this user, OR global system notifications (user is null)
        queryset = Notification.objects.filter(
            Q(user=request.user) | Q(user__isnull=True)
        ).order_by("-created_at")

        # Filters
        read_filter = request.query_params.get("read")
        type_filter = request.query_params.get("type")

        if read_filter is not None:
            is_read = read_filter.lower() == "true"
            queryset = queryset.filter(read=is_read)

        if type_filter:
            queryset = queryset.filter(type=type_filter)

        paginator = NotificationPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = NotificationSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = NotificationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationReadView(views.APIView):
    """
    POST /api/notifications/read/
    Marks notifications as read. Accepts a single id, list of ids, or all: true.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        notification_ids = request.data.get("ids", [])
        single_id = request.data.get("id")
        mark_all = request.data.get("all", False)

        if single_id:
            notification_ids = [single_id]

        if mark_all:
            # Mark all as read
            count = NotificationService.mark_as_read(request.user)
        elif notification_ids:
            count = NotificationService.mark_as_read(request.user, notification_ids)
        else:
            return Response(
                {"error": "Please provide 'id', 'ids', or set 'all' to true."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": f"Successfully marked {count} notifications as read."},
            status=status.HTTP_200_OK
        )


class NotificationDeleteView(views.APIView):
    """
    DELETE /api/notifications/<int:pk>/
    DELETE /api/notifications/delete/
    POST /api/notifications/delete/
    Deletes single, multiple, or all notifications for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk=None):
        return self._perform_delete(request, pk)

    def post(self, request, pk=None):
        return self._perform_delete(request, pk)

    def _perform_delete(self, request, pk=None):
        if pk:
            deleted_count, _ = Notification.objects.filter(
                Q(user=request.user) | Q(user__isnull=True),
                id=pk
            ).delete()
        else:
            single_id = request.data.get("id") or request.query_params.get("id")
            notification_ids = request.data.get("ids", [])
            delete_all = request.data.get("all", False) or request.query_params.get("all") == "true"

            if single_id:
                notification_ids = [single_id]

            if delete_all:
                deleted_count, _ = Notification.objects.filter(
                    Q(user=request.user) | Q(user__isnull=True)
                ).delete()
            elif notification_ids:
                deleted_count, _ = Notification.objects.filter(
                    Q(user=request.user) | Q(user__isnull=True),
                    id__in=notification_ids
                ).delete()
            else:
                return Response(
                    {"error": "Please provide notification 'id', 'ids', or set 'all' to true."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"message": f"Successfully deleted {deleted_count} notification(s)."},
            status=status.HTTP_200_OK
        )


class NotificationPreferencesView(views.APIView):
    """
    GET /api/notifications/preferences/ - Get preferences.
    POST /api/notifications/preferences/ - Update preferences.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pref = PreferenceService.get_preferences(request.user)
        serializer = NotificationPreferenceSerializer(pref)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = NotificationPreferenceSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            pref = PreferenceService.update_preferences(request.user, serializer.validated_data)
            return Response(
                NotificationPreferenceSerializer(pref).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationHistoryView(views.APIView):
    """
    GET /api/notifications/history/
    Retrieves delivery audit history logs.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        history = NotificationHistory.objects.filter(user=request.user).order_by("-delivered_at")
        paginator = NotificationPagination()
        page = paginator.paginate_queryset(history, request, view=self)
        
        data = [
            {
                "id": h.id,
                "type": h.notification_type,
                "title": h.title,
                "delivered_at": h.delivered_at.isoformat(),
                "method": h.delivery_method
            }
            for h in (page if page is not None else history)
        ]
        
        if page is not None:
            return paginator.get_paginated_response(data)
        return Response(data, status=status.HTTP_200_OK)


class NotificationUnreadCountView(views.APIView):
    """
    GET /api/notifications/unread/
    Returns count of unread notifications.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            Q(user=request.user) | Q(user__isnull=True),
            read=False
        ).count()
        return Response({"unread_count": count}, status=status.HTTP_200_OK)


class AnnouncementListView(views.APIView):
    """
    GET /api/notifications/announcements/
    List active global system announcements.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Admin announcements visible globally
        from django.utils import timezone
        now = timezone.now()
        queryset = Announcement.objects.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gte=now)
        ).order_by("-created_at")

        serializer = AnnouncementSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
