from django.contrib.auth.models import User
from rest_framework import serializers

from auth_app.api.serializers import UserDetailSerializer
from boards_app.models import Board
from tasks_app.api.serializers import TaskDetailSerializer


class BoardSerializer(serializers.ModelSerializer):
    """Serializer for the board list view with computed summary counts."""

    owner_id = serializers.ReadOnlyField(source='owner.id')
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'member_count', 'ticket_count',
            'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id', 'members',
        ]
        extra_kwargs = {'members': {'write_only': True}}

    def get_member_count(self, obj):
        """Return total participant count: members plus the owner."""
        return obj.members.count() + 1

    def get_ticket_count(self, obj):
        """Return total number of tasks on this board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Return number of tasks with status 'to-do'."""
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """Return number of high-priority tasks on this board."""
        return obj.tasks.filter(priority='high').count()


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Serializer for PATCH responses: returns nested owner_data and members_data."""

    owner_data = UserDetailSerializer(source='owner', read_only=True)
    members_data = UserDetailSerializer(source='members', many=True, read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data', 'members']


class BoardDetailSerializer(serializers.ModelSerializer):
    """Serializer for the board detail view including nested members and tasks."""

    owner_id = serializers.ReadOnlyField(source='owner.id')
    members = UserDetailSerializer(many=True, read_only=True)
    tasks = TaskDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    def to_representation(self, instance):
        """Prepend the owner to the members list if not already present."""
        rep = super().to_representation(instance)
        owner_data = UserDetailSerializer(instance.owner).data
        member_ids = [m['id'] for m in rep['members']]
        if instance.owner.id not in member_ids:
            rep['members'] = [owner_data] + rep['members']
        return rep
