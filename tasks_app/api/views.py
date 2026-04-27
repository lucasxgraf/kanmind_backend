from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from tasks_app.models import Task
from tasks_app.api.serializers import TaskSerializer
from django.db.models import Q

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(board__owner=user) | Q(board__members=user)
        ).distinct()