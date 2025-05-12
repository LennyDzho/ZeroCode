from django.shortcuts import redirect
from users.models import AdminUser

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        telegram_id = request.session.get("telegram_id")
        if not telegram_id or not AdminUser.objects.filter(telegram_id=telegram_id).exists():
            return redirect("/")  # или 403
        return view_func(request, *args, **kwargs)
    return wrapper