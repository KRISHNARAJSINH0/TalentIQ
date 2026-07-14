"""
Accounts URL configuration – Authentication routes.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", views.CurrentUserView.as_view(), name="current-user"),
    path("profile/", views.UpdateProfileView.as_view(), name="update-profile"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
]
