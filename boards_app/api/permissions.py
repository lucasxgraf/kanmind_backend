from rest_framework import permissions


class IsBoardOwner(permissions.BasePermission):
    """Allow read access to board participants; restrict writes based on action."""

    def has_permission(self, request, view):
        """Require authentication for all requests."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Safe methods: owner or member only.
        DELETE: owner only.
        PATCH/PUT: owner or member.
        """
        is_owner = obj.owner == request.user
        is_member = obj.members.filter(id=request.user.id).exists()

        if request.method in permissions.SAFE_METHODS:
            return is_owner or is_member
        if view.action == 'destroy':
            return is_owner
        return is_owner or is_member
