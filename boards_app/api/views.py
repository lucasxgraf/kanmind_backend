from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from boards_app.models import Board
from .serializers import BoardSerializer
from django.db.models import Q

class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)