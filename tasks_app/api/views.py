from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
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

    @action(detail=False, methods=['get'], url_path='reviewer-tasks')
    def reviewer_tasks(self, request):
        user = request.user
        tasks = Task.objects.filter(reviewer=user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)