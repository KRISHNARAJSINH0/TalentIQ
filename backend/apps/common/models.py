"""
Common models – Shared abstract base models for the entire project.

Provides UUID primary keys, automatic timestamps, and soft-delete support
so every concrete model inherits a consistent foundation.
"""

import uuid

from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# Manager for soft-delete filtering
# ---------------------------------------------------------------------------

class ActiveManager(models.Manager):
    """Return only non-deleted rows by default."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    """Return all rows, including soft-deleted ones."""

    pass


# ---------------------------------------------------------------------------
# Abstract base models
# ---------------------------------------------------------------------------

class BaseModel(models.Model):
    """
    Abstract base providing UUID primary key and automatic timestamps.

    Every concrete model in the project should inherit from this (or from
    SoftDeleteModel which itself inherits BaseModel).
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SoftDeleteModel(BaseModel):
    """
    Extends BaseModel with soft-delete capability.

    Records are marked as deleted instead of being physically removed.
    The default manager (`objects`) excludes soft-deleted rows.
    Use `all_objects` to include them.
    """

    is_deleted = models.BooleanField(
        default=False,
        verbose_name="Is Deleted",
        db_index=True,
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Deleted At",
    )

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta(BaseModel.Meta):
        abstract = True

    def soft_delete(self):
        """Mark the record as deleted."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
