from django.contrib import admin

from tasks_app.models import Comment, Task

admin.site.register(Task)
admin.site.register(Comment)
