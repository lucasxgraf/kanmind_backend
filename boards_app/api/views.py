from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from boards_app.models import Board
from .permissions import IsBoardOwner
from .serializers import BoardDetailSerializer, BoardSerializer, BoardUpdateSerializer


class BoardViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for Kanban boards.

    List and create are available to all authenticated users.
    Update and delete require the user to be the board owner.
    """

    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsBoardOwner]

    def get_serializer_class(self):
        """Use the appropriate serializer based on the action."""
        if self.action == 'retrieve':
            return BoardDetailSerializer
        if self.action in ('update', 'partial_update'):
            return BoardUpdateSerializer
        return BoardSerializer

    def get_queryset(self):
        """For list: only own/member boards. For detail actions: all boards so permissions can return 403."""
        user = self.request.user
        if self.action == 'list':
            return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        return Board.objects.all()

    def perform_create(self, serializer):
        """Set the current user as the owner when creating a board."""
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """Save the board and ensure the owner is not duplicated in members."""
        instance = serializer.save()
        instance.members.remove(instance.owner)
