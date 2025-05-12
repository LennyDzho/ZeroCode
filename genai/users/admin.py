from django.contrib import admin
from .models import User, AdminUser


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "username", "role", "created_at")

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ("telegram_id",)
    search_fields = ("telegram_id",)