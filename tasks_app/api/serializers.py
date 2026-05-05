from rest_framework import serializers
from django.contrib.auth.models import User
from tasks_app.models import Task, Comment
from auth_app.api.serializers import UserDetailSerializer


def validate_board_membership(board, assignee=None, reviewer=None):
    """Shared validation: assignee and reviewer must be board owner or member."""
    if assignee and assignee != board.owner and not board.members.filter(id=assignee.id).exists():
        raise serializers.ValidationError({"assignee_id": "Der Assignee muss Mitglied des Boards sein."})

    if reviewer and reviewer != board.owner and not board.members.filter(id=reviewer.id).exists():
        raise serializers.ValidationError({"reviewer_id": "Der Reviewer muss Mitglied des Boards sein."})


class TaskSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewer', required=False, allow_null=True
    )
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 
            'priority', 'assignee_id', 'reviewer_id', 'due_date', 'comments_count'
        ]

    def validate(self, data):
        board = data.get('board')
        user = self.context['request'].user

        if user != board.owner and not board.members.filter(id=user.id).exists():
            raise serializers.ValidationError({"board": "Du musst Mitglied des Boards sein, um Tasks zu erstellen."})

        validate_board_membership(board, data.get('assignee'), data.get('reviewer'))
        return data
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    def to_representation(self, instance):
        return TaskDetailSerializer(instance).data


class TaskDetailSerializer(serializers.ModelSerializer):
    assignee = UserDetailSerializer(read_only=True)
    reviewer = UserDetailSerializer(read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date', 'comments_count']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']

    def get_author(self, obj):
        if hasattr(obj.author, 'userprofile') and obj.author.userprofile.fullname:
            return obj.author.userprofile.fullname
        if obj.author.first_name or obj.author.last_name:
            return f"{obj.author.first_name} {obj.author.last_name}".strip()
        return obj.author.username


class TaskUpdateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewer', required=False, allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 
            'priority', 'assignee_id', 'reviewer_id', 'due_date'
        ]

    def validate(self, data):
        instance = self.instance
        board = instance.board

        if 'board' in data:
            raise serializers.ValidationError({"board": "Das Ändern der Board-ID ist nicht erlaubt."})

        validate_board_membership(
            board,
            data.get('assignee', instance.assignee),
            data.get('reviewer', instance.reviewer),
        )
        return data

    def to_representation(self, instance):
        return TaskDetailSerializer(instance).data