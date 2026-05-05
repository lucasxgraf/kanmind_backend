from rest_framework import permissions


class IsBoardOwner(permissions.BasePermission):
    """Allow read access to all board participants; restrict writes to the owner."""

    def has_object_permission(self, request, view, obj):
        """Grant access if the request is safe or the user owns the board."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
