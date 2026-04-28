from rest_framework import permissions


class IsBoardMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        board = obj.board
        user = request.user
        return user == board.owner or board.members.filter(id=user.id).exists()
    
class IsTaskOwnerOrBoardOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user == obj.created_by or user == obj.board.owner