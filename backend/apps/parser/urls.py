"""Parser URL configuration."""

from django.urls import path
from . import views

app_name = "parser"

urlpatterns = [
    path("", views.parser_root, name="parser-root"),
]
