from django.contrib import admin
from .models import Dialog

@admin.register(Dialog)
class DialogAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "model", "project", "updated_at")
