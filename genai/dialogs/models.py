import uuid
from django.db import models
from users.models import User
from models_app.models import Model
from projects.models import Project

class Dialog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, on_delete=models.SET_NULL, null=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255, default="Новый диалог")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL, related_name="dialogs")
    def __str__(self):
        return self.title

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('model', 'Model')])
    content = models.TextField()
    order = models.PositiveIntegerField()  # номер сообщения в последовательности
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']