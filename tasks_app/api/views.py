from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
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
        if self.action in ['update', 'partial_update', 'task_comments', 'comment_detail']:
            return [IsAuthenticated(), IsBoardMember()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsTaskOwnerOrBoardOwner()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        if self.action in ['task_comments', 'comment_detail']:
            return CommentSerializer
        return TaskSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(board__owner=user) | Q(board__members=user)
        ).distinct()

    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_tasks(self, request):
        tasks = Task.objects.filter(assignee=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewer_tasks(self, request):
        tasks = Task.objects.filter(reviewer=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'], url_path='comments')
    def task_comments(self, request, pk=None):
        task = self.get_object()
            
        if request.method == 'GET':
            comments = task.comments.all().order_by('created_at')
            serializer = self.get_serializer(comments, many=True)
            return Response(serializer.data)
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'delete'], url_path=r'comments/(?P<comment_id>\d+)')
    def comment_detail(self, request, pk=None, comment_id=None):
        task = self.get_object()
            
        try:
            comment = Comment.objects.get(id=comment_id, task=task)
        except (Comment.DoesNotExist, ValueError):
            return Response({"detail": "Kommentar nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
            
        if request.method == 'GET':
            serializer = self.get_serializer(comment)
            return Response(serializer.data)
            
        if comment.author != request.user:
            return Response({"detail": "Nur der Ersteller des Kommentars darf ihn löschen."}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)