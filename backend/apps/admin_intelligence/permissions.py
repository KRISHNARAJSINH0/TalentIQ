from rest_framework import permissions
from apps.accounts.models import User


class IsAdminUserRole(permissions.BasePermission):
    """
    Allows access only to users who have their role set to 'admin' or are superusers.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.role == User.Role.ADMIN
                or request.user.is_superuser
            )
        )
