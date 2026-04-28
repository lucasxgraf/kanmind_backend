from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from tasks_app.models import Task
from tasks_app.api.serializers import TaskSerializer, TaskUpdateSerializer
from tasks_app.api.permissions import IsBoardMember, IsTaskOwnerOrBoardOwner
from django.db.models import Q

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsBoardMember()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsTaskOwnerOrBoardOwner()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(board__owner=user) | Q(board__members=user)
        ).distinct()