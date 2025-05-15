from django.contrib import admin
from .models import Dialog, Message

@admin.register(Dialog)
class DialogAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "model", "project", "updated_at")


@admin.register(Message)
class DialogAdmin(admin.ModelAdmin):
    list_display = ("id", "dialog", "role", "content")
