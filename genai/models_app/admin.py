from django.contrib import admin
from .models import Model

@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ("name", "api_url", "is_active")
