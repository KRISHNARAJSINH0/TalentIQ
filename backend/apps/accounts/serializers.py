"""
Accounts serializers – Registration, Login, Profile, Password change.

Production-ready serializers with field-level and cross-field validation,
proper error messages, and security best practices.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from apps.profiles.models import Profile


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

class RegisterSerializer(serializers.ModelSerializer):
    """
    Validates and creates a new user account.

    Automatically creates an associated Profile and returns JWT tokens.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=6,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "confirm_password",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
        }

    def validate_email(self, value):
        """Ensure email is unique (case-insensitive)."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate_username(self, value):
        """Ensure username is unique (case-insensitive)."""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate(self, attrs):
        """Ensure passwords match."""
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Create user with hashed password and auto-create profile."""
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        Profile.objects.get_or_create(user=user)
        return user

    def get_tokens(self, user):
        """Generate JWT token pair for the newly registered user."""
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class LoginSerializer(serializers.Serializer):
    """
    Authenticates a user by email or username + password.

    Returns JWT tokens and basic user details on success.
    """

    login = serializers.CharField(
        help_text="Email address or username.",
    )
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        login_value = attrs.get("login", "").strip()
        password = attrs.get("password", "")

        if not login_value or not password:
            raise serializers.ValidationError("Both login and password are required.")

        # Determine if login is email or username
        if "@" in login_value:
            user = User.objects.filter(email__iexact=login_value).first()
        else:
            user = User.objects.filter(username__iexact=login_value).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")

        attrs["user"] = user
        return attrs

    def get_tokens(self, user):
        """Generate JWT token pair."""
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

class LogoutSerializer(serializers.Serializer):
    """Blacklists the provided refresh token to log the user out."""

    refresh = serializers.CharField(
        help_text="The refresh token to blacklist.",
    )

    def validate_refresh(self, value):
        try:
            self._token = RefreshToken(value)
        except Exception:
            raise serializers.ValidationError("Invalid or expired refresh token.")
        return value

    def save(self):
        self._token.blacklist()


# ---------------------------------------------------------------------------
# User / Profile read
# ---------------------------------------------------------------------------

class ProfileReadSerializer(serializers.ModelSerializer):
    """Nested profile data for the user response."""

    class Meta:
        model = Profile
        fields = [
            "headline",
            "summary",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
            "website",
            "github",
            "linkedin",
            "portfolio_url",
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    Read-only user representation returned by the /me endpoint.

    Includes nested profile data.
    """

    profile = ProfileReadSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "profile_photo",
            "role",
            "is_verified",
            "date_joined",
            "profile",
        ]
        read_only_fields = fields


# ---------------------------------------------------------------------------
# Update Profile
# ---------------------------------------------------------------------------

class UpdateProfileSerializer(serializers.Serializer):
    """
    Updates both User and Profile fields in a single request.

    Explicitly lists allowed fields – ID, UUID, email, and password
    cannot be changed through this endpoint.
    """

    # User fields
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    profile_photo = serializers.ImageField(required=False, allow_null=True)

    # Profile fields
    headline = serializers.CharField(max_length=200, required=False, allow_blank=True)
    summary = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    country = serializers.CharField(max_length=100, required=False, allow_blank=True)
    postal_code = serializers.CharField(max_length=20, required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    github = serializers.URLField(required=False, allow_blank=True)
    linkedin = serializers.URLField(required=False, allow_blank=True)
    portfolio_url = serializers.URLField(required=False, allow_blank=True)

    def update(self, user, validated_data):
        """Split data and update User + Profile models."""
        user_fields = {"first_name", "last_name", "phone", "profile_photo"}
        profile_data = {}
        user_data = {}

        for key, value in validated_data.items():
            if key in user_fields:
                user_data[key] = value
            else:
                profile_data[key] = value

        # Update user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # Update profile
        if profile_data:
            profile, _ = Profile.objects.get_or_create(user=user)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return user


# ---------------------------------------------------------------------------
# Change Password
# ---------------------------------------------------------------------------

class ChangePasswordSerializer(serializers.Serializer):
    """
    Validates current password and sets a new one.

    Enforces Django's password validation rules.
    """

    current_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=6,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "New passwords do not match."}
            )
        return attrs

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
