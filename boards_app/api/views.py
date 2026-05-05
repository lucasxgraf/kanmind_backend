from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from boards_app.models import Board
from .permissions import IsBoardOwner
from .serializers import BoardDetailSerializer, BoardSerializer


class BoardViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for Kanban boards.

    List and create are available to all authenticated users.
    Update and delete require the user to be the board owner.
    """

    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsBoardOwner]

    def get_serializer_class(self):
        """Use the detail serializer for retrieve, list serializer otherwise."""
        if self.action == 'retrieve':
            return BoardDetailSerializer
        return BoardSerializer

    def get_queryset(self):
        """Return only boards where the user is the owner or a member."""
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        """Set the current user as the owner when creating a board."""
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """Save the board and ensure the owner is not duplicated in members."""
        instance = serializer.save()
        instance.members.remove(instance.owner)
