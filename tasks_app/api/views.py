from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from tasks_app.models import Task
from tasks_app.api.serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]