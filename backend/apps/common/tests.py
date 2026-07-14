from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch


class HealthCheckTests(APITestCase):
    """Test suite for the diagnostic health endpoints."""

    def test_general_health(self):
        url = reverse("health")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "healthy")

    def test_db_health(self):
        url = reverse("health-db")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "healthy")

    @patch("django.core.cache.cache.set")
    @patch("django.core.cache.cache.get")
    def test_cache_health(self, mock_get, mock_set):
        mock_set.return_value = True
        mock_get.return_value = "ok"
        url = reverse("health-cache")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "healthy")

    @patch("celery.app.control.Inspect.ping")
    def test_celery_health_mocked_success(self, mock_ping):
        mock_ping.return_value = {"worker1@hostname": "pong"}
        url = reverse("health-celery")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "healthy")

    @patch("celery.app.control.Inspect.ping")
    def test_celery_health_mocked_fail(self, mock_ping):
        mock_ping.return_value = None
        url = reverse("health-celery")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["status"], "unhealthy")

    def test_system_health(self):
        url = reverse("health-system")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "healthy")
        self.assertIn("disk", response.data)
