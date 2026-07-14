from django.urls import path
from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.PortfolioDetailView.as_view(), name="portfolio-detail"),
    path("generate/", views.PortfolioGenerateView.as_view(), name="portfolio-generate"),
    path("theme/", views.PortfolioUpdateThemeView.as_view(), name="portfolio-theme"),
    path("privacy/", views.PortfolioUpdatePrivacyView.as_view(), name="portfolio-privacy"),
    path("analytics/", views.PortfolioAnalyticsView.as_view(), name="portfolio-analytics"),
    path("analytics/log/", views.PortfolioLogActivityView.as_view(), name="portfolio-log-activity"),
    path("<slug:slug>/", views.PortfolioPublicDetailView.as_view(), name="portfolio-public-detail"),
]
