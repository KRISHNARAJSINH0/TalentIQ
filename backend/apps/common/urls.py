"""Common URL configuration."""

from django.urls import path
from . import views

app_name = "common"

urlpatterns = [
    path("", views.common_root, name="common-root"),
]
