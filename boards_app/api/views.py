from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from boards_app.models import Board
from .serializers import BoardSerializer, BoardDetailSerializer
from .permissions import IsBoardOwner
from django.db.models import Q

class BoardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsBoardOwner]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BoardDetailSerializer
        return BoardSerializer

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.members.remove(instance.owner)