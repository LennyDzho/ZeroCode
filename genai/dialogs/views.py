import json

from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from users.models import User
from django.views import View
from django.http import JsonResponse, HttpResponseForbidden
from dialogs.models import Dialog
from models_app.models import Model
from users.models import User

from dialogs.models import Message
import requests
import os

from projects.models import Project

from projects.models import ProjectMember

from dialogs import models
from django.db.models import Max


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
        return render(request, "users/dialogs.html", {"user": user, "dialogs": dialogs})



@method_decorator(csrf_exempt, name='dispatch')
class CreateDialogView(View):
    def post(self, request):
        import json
        data = json.loads(request.body)
        telegram_id = request.session.get("telegram_id")

        if not telegram_id:
            return JsonResponse({"success": False, "error": "Not authorized"}, status=403)

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "User not found"}, status=404)

        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        model_id = data.get("model_id")
        project_id = data.get("project_id")

        if not title:
            return JsonResponse({"success": False, "error": "Title required"}, status=400)

        if not model_id:
            return JsonResponse({"success": False, "error": "Model is required"}, status=400)

        try:
            model = Model.objects.get(id=model_id, is_active=True)
        except Model.DoesNotExist:
            return JsonResponse({"success": False, "error": "Invalid or inactive model"}, status=404)

        project = None
        if project_id:
            project = Project.objects.filter(id=project_id, owner=user).first()

        dialog = Dialog.objects.create(
            user=user,
            model=model,
            title=title,
            project=project
        )

        return JsonResponse({"success": True, "dialog_id": str(dialog.id)})



class DialogDetailView(View):
    def get(self, request, dialog_id):
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            return HttpResponseForbidden("Unauthorized")

        user = get_object_or_404(User, telegram_id=telegram_id)

        dialog = get_object_or_404(Dialog.objects.select_related("project"), id=dialog_id)

        # Проверка: либо владелец диалога, либо участник проекта
        is_owner = dialog.user == user
        is_member = dialog.project and ProjectMember.objects.filter(
            project=dialog.project,
            user=user
        ).exists()

        if not is_owner and not is_member:
            return HttpResponseForbidden("Access denied")

        messages = dialog.messages.all()
        return render(request, "dialogs/detail.html", {
            "dialog": dialog,
            "messages": messages,
            "models": Model.objects.filter(is_active=True)
        })



def call_openrouter_model(model, history, project_description=None):
    """
    Отправка истории в выбранную модель через OpenRouter API
    """
    url = model.api_url  # например, https://openrouter.ai/api/v1/chat/completions
    api_key = model.api_key  # ключ сохранён в БД

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = []
    if project_description:
        messages.append({
            "role": "system",
            "content": project_description.strip()
        })
    messages += [
        {"role": msg["role"], "content": msg["content"]}
        for msg in history
    ]

    payload = {
        "model": model.name,  # например, "openrouter/gpt-4"
        "messages": messages,
        "temperature": model.temperature or 0.7,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        print("DEBUG:", response.status_code, response.text)
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Ошибка при вызове модели: {e}]"

@method_decorator(csrf_exempt, name='dispatch')
class SendMessageView(View):
    def post(self, request, dialog_id):
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            return JsonResponse({"success": False, "error": "Not authorized"}, status=403)

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "User not found"}, status=404)

        dialog = get_object_or_404(Dialog.objects.select_related("project"), id=dialog_id)

        is_owner = dialog.user == user
        is_member = dialog.project and ProjectMember.objects.filter(project=dialog.project, user=user).exists()

        if not is_owner and not is_member:
            return JsonResponse({"success": False, "error": "Access denied"}, status=403)

        data = json.loads(request.body)
        content = data.get("content", "").strip()

        if not content:
            return JsonResponse({"success": False, "error": "Empty content"}, status=400)

        last_order = dialog.messages.aggregate(max=Max("order"))["max"] or 0

        user_msg = Message.objects.create(
            dialog=dialog,
            role="user",
            content=content,
            order=last_order + 1
        )

        # вызываем модель
        history = list(dialog.messages.order_by("order").values("role", "content"))
        response = call_openrouter_model(dialog.model, history, project_description=dialog.project.description if dialog.project else None)

        model_msg = Message.objects.create(
            dialog=dialog,
            role="model",
            content=response,
            order=last_order + 2
        )

        return JsonResponse({
            "success": True,
            "reply": {
                "id": str(model_msg.id),
                "content": model_msg.content,
                "role": model_msg.role
            },
            "user_msg": {
                "id": str(user_msg.id),
                "content": user_msg.content,
                "role": user_msg.role
            }
        })


@method_decorator(csrf_exempt, name='dispatch')
class EditMessageView(View):
    def post(self, request, dialog_id, message_id):
        data = json.loads(request.body)
        content = data.get("content", "").strip()

        if not content:
            return JsonResponse({"success": False, "error": "Пустое сообщение"}, status=400)

        try:
            dialog = Dialog.objects.select_related("model").get(id=dialog_id)
            message = Message.objects.get(id=message_id, dialog=dialog)
        except (Dialog.DoesNotExist, Message.DoesNotExist):
            return JsonResponse({"success": False, "error": "Сообщение или диалог не найден"}, status=404)

        # Удаляем все последующие сообщения
        Message.objects.filter(dialog=dialog, order__gt=message.order).delete()

        # Обновляем сообщение
        message.content = content
        message.save()

        # Получаем всю историю (до этого сообщения + отредактированное)
        history = list(
            Message.objects
            .filter(dialog=dialog)
            .order_by("order")
            .values("role", "content")
        )

        # Вызов модели
        try:
            response_text = call_openrouter_model(dialog.model, history, project_description=dialog.project.description if dialog.project else None)
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Ошибка модели: {str(e)}"}, status=500)

        # Сохраняем ответ модели
        Message.objects.create(
            dialog=dialog,
            role="model",
            content=response_text,
            order=message.order + 1
        )

        return JsonResponse({"success": True, "response": response_text})

@method_decorator(csrf_exempt, name='dispatch')
class SetModelView(View):
    def post(self, request, dialog_id):
        data = json.loads(request.body)
        model_id = data.get("model_id")

        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            return JsonResponse({"success": False, "error": "Not authorized"}, status=403)

        user = get_object_or_404(User, telegram_id=telegram_id)
        dialog = get_object_or_404(Dialog, id=dialog_id, user=user)

        try:
            model = Model.objects.get(id=model_id, is_active=True)
            dialog.model = model
            dialog.save()
            return JsonResponse({"success": True})
        except Model.DoesNotExist:
            return JsonResponse({"success": False, "error": "Invalid model"}, status=404)
