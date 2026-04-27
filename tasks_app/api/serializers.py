from rest_framework import serializers
from django.contrib.auth.models import User
from tasks_app.models import Task
from auth_app.api.serializers import UserDetailSerializer

class TaskSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewer', required=False, allow_null=True
    )
    comments_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 
            'priority', 'assignee_id', 'reviewer_id', 'due_date', 'comments_count'
        ]

    def get_comments_count(self, obj):
        return 0

    def validate(self, data):
        board = data.get('board')
        assignee = data.get('assignee')
        reviewer = data.get('reviewer')

        user = self.context['request'].user
        if user != board.owner and not board.members.filter(id=user.id).exists():
            raise serializers.ValidationError({"board": "Du musst Mitglied des Boards sein, um Tasks zu erstellen."})

        if assignee and assignee != board.owner and not board.members.filter(id=assignee.id).exists():
            raise serializers.ValidationError({"assignee_id": "Der Assignee muss Mitglied des Boards sein."})

        if reviewer and reviewer != board.owner and not board.members.filter(id=reviewer.id).exists():
            raise serializers.ValidationError({"reviewer_id": "Der Reviewer muss Mitglied des Boards sein."})

        return data

    def to_representation(self, instance):
        return TaskDetailSerializer(instance).data

class TaskDetailSerializer(serializers.ModelSerializer):
    assignee = UserDetailSerializer(read_only=True)
    reviewer = UserDetailSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date', 'comments_count']

    def get_comments_count(self, obj):
        return 0