"""
Accounts models – Custom User model.

Extends Django's AbstractUser with UUID primary key, email-based login,
phone number, profile photo, role, and verification status.
"""

import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """
    Custom user model for the ResumeAI platform.

    Uses email as the primary identifier while retaining username support.
    """

    class Role(models.TextChoices):
        """Available user roles."""
        USER = "user", "User"
        RECRUITER = "recruiter", "Recruiter"
        ADMIN = "admin", "Admin"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email Address",
        help_text="Must be a valid, unique email address.",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Phone Number",
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Enter a valid phone number (9-15 digits, optional leading +).",
            )
        ],
    )
    profile_photo = models.ImageField(
        upload_to="profile_photos/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Profile Photo",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        verbose_name="Role",
        db_index=True,
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Email Verified",
    )

    # Timestamps (AbstractUser has date_joined; add updated_at)
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
    )

    # Use email for authentication
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"], name="idx_user_email"),
            models.Index(fields=["role"], name="idx_user_role"),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Return first_name + last_name, falling back to username."""
        full = super().get_full_name().strip()
        return full if full else self.username
