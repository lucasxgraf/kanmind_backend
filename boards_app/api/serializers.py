from rest_framework import serializers
from boards_app.models import Board
from auth_app.api.serializers import UserDetailSerializer
from tasks_app.api.serializers import TaskDetailSerializer

class BoardSerializer(serializers.ModelSerializer):
    owner_id = serializers.ReadOnlyField(source='owner.id')
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id', 'members']
        extra_kwargs = {
            'members': {'write_only': True}
        }

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()

    def create(self, validated_data):
        members_data = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        
        if members_data:
            board.members.set(members_data)
        return board

    def update(self, instance, validated_data):
        members_data = validated_data.pop('members', None)
        instance = super().update(instance, validated_data)
        
        if members_data is not None:
            instance.members.set(members_data)
            
        return instance

class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.ReadOnlyField(source='owner.id')
    members = UserDetailSerializer(many=True, read_only=True)
    tasks = TaskDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']