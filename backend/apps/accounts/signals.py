"""
Accounts signals – Auto-create Profile on User creation.
"""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.profiles.models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile when a new User is registered."""
    if created:
        Profile.objects.get_or_create(user=instance)
