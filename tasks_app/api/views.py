from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from tasks_app.models import Task, Comment
from tasks_app.api.serializers import TaskSerializer, TaskUpdateSerializer, CommentSerializer
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
        if self.action == 'task_comments':
            return CommentSerializer
        return TaskSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(board__owner=user) | Q(board__members=user)
        ).distinct()

    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_tasks(self, request):
        user = request.user
        tasks = Task.objects.filter(assignee=user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewer_tasks(self, request):
        user = request.user
        tasks = Task.objects.filter(reviewer=user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'], url_path='comments')
    def task_comments(self, request, pk=None):
        task = self.get_object()
        user = request.user
        
        board = task.board
        if user != board.owner and not board.members.filter(id=user.id).exists():
            return Response({"detail": "Du musst Mitglied des Boards sein, um auf Kommentare zuzugreifen."}, status=403)
            
        if request.method == 'GET':
            comments = task.comments.all().order_by('created_at')
            serializer = self.get_serializer(comments, many=True)
            return Response(serializer.data)
            
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(task=task, author=user)
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)