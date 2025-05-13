import json
from datetime import timezone

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, AdminUser
from .utils import verify_telegram_auth
from django.conf import settings
import urllib.parse
from django.apps import AppConfig

from dialogs.models import Dialog

from models_app.models import Model

from users.decorators import admin_required


class TelegramAuthView(APIView):
    def post(self, request):
        data = request.data
        telegram_id = data.get("id")

        if not telegram_id:
            return Response({"error": "Missing telegram_id"}, status=400)

        user, _ = User.objects.update_or_create(
            telegram_id=telegram_id,
            defaults={
                "username": data.get("username"),
                "avatar_url": data.get("photo_url"),
            }
        )

        # Сохраняем telegram_id в сессии
        request.session["telegram_id"] = telegram_id

        return Response({
            "id": str(user.id),
            "username": user.username,
            "role": user.role
        })

class TelegramEntryView(View):
    def get(self, request):
        import urllib.parse

        # Получаем initData из query-параметров Telegram
        query = request.META.get("QUERY_STRING")
        data = dict(urllib.parse.parse_qsl(query))

        telegram_id = data.get("id")
        username = data.get("username")
        avatar_url = data.get("photo_url")

        if not telegram_id:
            return render(request, "users/index.html", {"error": "Нет данных от Telegram"})

        # Создаём или обновляем пользователя в нашей таблице
        user, created = User.objects.update_or_create(
            telegram_id=telegram_id,
            defaults={
                "username": username,
                "avatar_url": avatar_url,
                "last_active_at": timezone.now(),
            }
        )

        # Можно отрисовать интерфейс с этим пользователем
        return render(request, "users/index.html", {"user": user})

@method_decorator(csrf_exempt, name='dispatch')
class SearchUserView(View):
    def post(self, request, project_id):
        data = json.loads(request.body)
        telegram_id = data.get("telegram_id", "").strip()
        try:
            user = User.objects.get(telegram_id=telegram_id)
            return JsonResponse({"success": True, "user_id": str(user.id), "username": user.username or "Без имени"})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "Пользователь не найден"}, status=404)


class DialogsView(View):
    def get(self, request):
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            return redirect("/")

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return redirect("/")

        dialogs = Dialog.objects.filter(user=user, project__isnull=True).order_by("-updated_at")
        models = Model.objects.filter(is_active=True)

        return render(request, "users/dialogs.html", {
            "user": user,
            "dialogs": dialogs,
            "models": models
        })



class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'ADMINISTRATION'


@admin_required
def admin_dashboard(request):
    models = Model.objects.all()
    return render(request, "adminpanel/dashboard.html", {"models": models})


class AdminDashboardView(View):
    def get(self, request):
        telegram_id = request.session.get("telegram_id")
        if not AdminUser.objects.filter(telegram_id=telegram_id).exists():
            return redirect("/")  # или вернуть 403
        models = Model.objects.all()
        return render(request, "admin_panel/dashboard.html", {"models": models})

class AdminModelCreateView(View):
    def post(self, request):
        from django.utils import timezone
        data = json.loads(request.body)
        name = data.get("name")
        provider = data.get("provider")
        endpoint = data.get("endpoint")
        if name and provider and endpoint:
            model = Model.objects.create(name=name, provider=provider, endpoint=endpoint, is_active=True)
            return JsonResponse({"success": True, "model_id": str(model.id)})
        return JsonResponse({"success": False, "error": "Недостаточно данных"})

class AdminModelDeleteView(View):
    def post(self, request, model_id):
        model = get_object_or_404(Model, id=model_id)
        model.delete()
        return JsonResponse({"success": True})

class AdminModelUpdateView(View):
    def post(self, request, model_id):
        model = get_object_or_404(Model, id=model_id)
        data = json.loads(request.body)

        model.name = data.get("name", model.name)
        model.provider = data.get("provider", model.provider)
        model.endpoint = data.get("endpoint", model.endpoint)
        model.save()

        return JsonResponse({"success": True})
