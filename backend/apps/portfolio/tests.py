from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.profiles.models import Profile
from apps.portfolio.models import Portfolio, PortfolioAnalyticsLog

User = get_user_model()


class PortfolioAPITests(APITestCase):
    def setUp(self):
        # Create users
        self.user = User.objects.create_user(
            username="portfolio_user",
            email="portfolio@example.com",
            password="testpassword123",
            first_name="Krishna",
            last_name="Singh",
        )
        self.other_user = User.objects.create_user(
            username="other_user",
            email="other@example.com",
            password="testpassword123",
        )
        
        # Retrieve automatically created profile from signal and update it
        self.profile = Profile.objects.get(user=self.user)
        self.profile.headline = "Full Stack Architect"
        self.profile.summary = "Passionate developer."
        self.profile.is_verified = True
        self.profile.save()

        self.client.force_authenticate(user=self.user)

    def test_get_portfolio_auto_generates(self):
        """Test GET /api/portfolio/ retrieves or auto-generates portfolio."""
        url = reverse("portfolio:portfolio-detail")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "portfolio_user")
        self.assertEqual(response.data["theme"], "modern")
        self.assertIsNotNone(response.data["portfolio_json"])

    def test_post_portfolio_generate(self):
        """Test POST /api/portfolio/generate/ updates portfolio_json."""
        url = reverse("portfolio:portfolio-generate")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["portfolio_json"]["headline"], "Full Stack Architect")

    def test_patch_portfolio_theme(self):
        """Test PATCH /api/portfolio/theme/ updates theme and slug."""
        portfolio = Portfolio.objects.create(profile=self.profile, theme="modern", slug="krishna")
        url = reverse("portfolio:portfolio-theme")
        payload = {"theme": "glassmorphism", "slug": "new-krishna"}
        
        response = self.client.patch(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["theme"], "glassmorphism")
        self.assertEqual(response.data["slug"], "new-krishna")

    def test_patch_portfolio_privacy(self):
        """Test PATCH /api/portfolio/privacy/ updates is_public flag."""
        portfolio = Portfolio.objects.create(profile=self.profile, theme="modern", slug="krishna", is_public=True)
        url = reverse("portfolio:portfolio-privacy")
        payload = {"is_public": False}
        
        response = self.client.patch(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_public"])

    def test_get_public_portfolio_slug_and_logs_view(self):
        """Test GET /api/portfolio/<slug>/ fetches public page and logs VIEW activity."""
        portfolio = Portfolio.objects.create(profile=self.profile, theme="modern", slug="krishna", is_public=True)
        
        # Logout to fetch publicly
        self.client.force_authenticate(user=None)
        
        url = reverse("portfolio:portfolio-public-detail", kwargs={"slug": "krishna"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["slug"], "krishna")
        
        # Verify view counter incremented
        portfolio.refresh_from_db()
        self.assertEqual(portfolio.views, 1)

    def test_private_portfolio_access_denied(self):
        """Test private portfolio returns 403 Forbidden for anonymous or non-owners."""
        portfolio = Portfolio.objects.create(profile=self.profile, theme="modern", slug="krishna-private", is_public=False)
        
        # Anonymous
        self.client.force_authenticate(user=None)
        url = reverse("portfolio:portfolio-public-detail", kwargs={"slug": "krishna-private"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Other user
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Owner
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_log_client_activity(self):
        """Test POST /api/portfolio/analytics/log/ logs downloads and shares."""
        portfolio = Portfolio.objects.create(profile=self.profile, theme="modern", slug="krishna", is_public=True)
        url = reverse("portfolio:portfolio-log-activity")
        
        # Log download
        self.client.post(url, {"slug": "krishna", "event_type": "download"})
        portfolio.refresh_from_db()
        self.assertEqual(portfolio.downloads, 1)

        # Log section view
        self.client.post(url, {"slug": "krishna", "event_type": "section_view", "section_name": "projects"})
        self.assertTrue(
            PortfolioAnalyticsLog.objects.filter(
                portfolio=portfolio,
                event_type="section_view",
                section_name="projects"
            ).exists()
        )

    def test_get_portfolio_analytics(self):
        """Test GET /api/portfolio/analytics/ retrieves aggregated logs."""
        portfolio = Portfolio.objects.create(profile=self.profile, theme="modern", slug="krishna", is_public=True)
        # Log some activities
        PortfolioAnalyticsLog.objects.create(portfolio=portfolio, event_type="view")
        PortfolioAnalyticsLog.objects.create(portfolio=portfolio, event_type="section_view", section_name="projects")
        
        url = reverse("portfolio:portfolio-analytics")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_views", response.data)
        self.assertIn("section_views", response.data)
        self.assertIn("daily_trends", response.data)
