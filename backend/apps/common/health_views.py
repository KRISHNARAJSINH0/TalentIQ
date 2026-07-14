import shutil
import time
from django.db import connection
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from config.celery import app as celery_app


class HealthCheckView(APIView):
    """General health check endpoint."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "status": "healthy",
            "timestamp": time.time(),
            "service": "ResumeAI Backend"
        }, status=status.HTTP_200_OK)


class DbHealthCheckView(APIView):
    """Database connectivity health check."""
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Execute simple query to test connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                row = cursor.fetchone()
                if row is None:
                    raise Exception("Database returned empty row")
            return Response({
                "status": "healthy",
                "database": "connected"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "unhealthy",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CacheHealthCheckView(APIView):
    """Redis cache connectivity health check."""
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Set and retrieve a dummy key
            cache.set("health_check", "ok", timeout=5)
            value = cache.get("health_check")
            if value != "ok":
                raise Exception("Cache write/read mismatch")
            return Response({
                "status": "healthy",
                "cache": "connected"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "unhealthy",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CeleryHealthCheckView(APIView):
    """Celery worker connectivity health check using ping."""
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Ping Celery workers
            insp = celery_app.control.inspect(timeout=1.0)
            ping_status = insp.ping()
            if not ping_status:
                raise Exception("No active Celery workers found")
            return Response({
                "status": "healthy",
                "workers": ping_status
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "unhealthy",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SystemHealthCheckView(APIView):
    """Host resource metrics health check."""
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Disk utilization
            total, used, free = shutil.disk_usage("/")
            disk_info = {
                "total_gb": round(total / (2**30), 2),
                "used_gb": round(used / (2**30), 2),
                "free_gb": round(free / (2**30), 2),
                "used_percent": round((used / total) * 100, 2)
            }
            return Response({
                "status": "healthy",
                "disk": disk_info,
                "uptime": time.clock_gettime(time.CLOCK_MONOTONIC) if hasattr(time, 'CLOCK_MONOTONIC') else time.time()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "unhealthy",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
