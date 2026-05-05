from django.contrib.auth.models import User
from django.db import models


class Board(models.Model):
    """A Kanban board owned by one user and shared with members."""

    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')
    members = models.ManyToManyField(User, related_name='member_boards', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'board'
        verbose_name_plural = 'boards'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
