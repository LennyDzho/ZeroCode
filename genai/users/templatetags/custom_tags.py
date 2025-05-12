from django import template
from users.models import AdminUser

register = template.Library()

@register.filter
def is_admin(telegram_id):
    return AdminUser.objects.filter(telegram_id=telegram_id).exists()
