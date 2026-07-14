"""
Profiles URL configuration.
"""

from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    path("master/", views.ProfileMasterView.as_view(), name="profile-master"),
    path("section/", views.ProfileSectionView.as_view(), name="profile-section"),
    path("verify/", views.ProfileVerifyView.as_view(), name="profile-verify"),
    path("export/", views.ProfileExportView.as_view(), name="profile-export"),
]
