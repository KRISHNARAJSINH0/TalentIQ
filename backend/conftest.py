import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import factory

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    first_name = "Test"
    last_name = "User"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        # Ensure password hashing
        password = kwargs.pop("password", "password123")
        user = manager.create_user(*args, **kwargs)
        user.set_password(password)
        user.save()
        return user


@pytest.fixture
def api_client():
    """Shared DRF API client."""
    return APIClient()


@pytest.fixture
def user_factory():
    """Helper user factory."""
    return UserFactory


@pytest.fixture
def test_user(db):
    """A standard authenticated user fixture."""
    return UserFactory.create(username="candidate1", email="candidate1@example.com")
