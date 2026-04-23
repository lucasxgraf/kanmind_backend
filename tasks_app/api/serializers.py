from rest_framework import serializers
from tasks_app.models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at']
        read_only_fields = ['created_at']