from rest_framework import permissions


class IsBoardMember(permissions.BasePermission):
    """Allow access only to the board owner or an explicit board member."""

    def has_object_permission(self, request, view, obj):
        """Grant access if the user owns or is a member of the task's board."""
        board = obj.board
        user = request.user
        return user == board.owner or board.members.filter(id=user.id).exists()


class IsTaskOwnerOrBoardOwner(permissions.BasePermission):
    """Allow deletion only to the task creator or the board owner."""

    def has_object_permission(self, request, view, obj):
        """Grant access if the user created the task or owns its board."""
        user = request.user
        return user == obj.created_by or user == obj.board.owner
