import json

from django.db import IntegrityError
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from projects.models import Project
from dialogs.models import Dialog

from users.models import User
from django.db.models import Q

from models_app.models import Model

from projects.models import ProjectMember


class ProjectListView(View):
    def get(self, request):
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            return render(request, "error.html", {"message": "Не авторизован"})

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return render(request, "error.html", {"message": "Пользователь не найден"})

        owned_projects = Project.objects.filter(owner=user)
        member_project_ids = ProjectMember.objects.filter(user=user).values_list("project_id", flat=True)
        shared_projects = Project.objects.filter(id__in=member_project_ids)

        projects = owned_projects.union(shared_projects).order_by("-updated_at")

        return render(request, "projects/list.html", {
            "projects": projects,
            "user": user
        })


class ProjectDetailView(View):
    def get(self, request, project_id):
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            return redirect("/")

        user = get_object_or_404(User, telegram_id=telegram_id)

        # Найдём проект, если пользователь — либо владелец, либо участник
        try:
            project = Project.objects.filter(
                Q(id=project_id),
                Q(owner=user) | Q(projectmember__user=user)
            ).first()

        except Project.DoesNotExist:
            return render(request, "error.html", {"message": "Проект не найден или нет доступа"}, status=404)

        dialogs = project.dialogs.order_by("-updated_at")
        models_list = Model.objects.filter(is_active=True)

        return render(request, "projects/detail.html", {
            "project": project,
            "dialogs": dialogs,
            "models": models_list,
            "user": user
        })



@method_decorator(csrf_exempt, name='dispatch')
class CreateProjectView(View):
    def post(self, request):
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            return JsonResponse({"success": False, "error": "Not authorized"}, status=403)

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "User not found"}, status=404)

        data = json.loads(request.body)
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()

        if not title:
            return JsonResponse({"success": False, "error": "Title required"}, status=400)

        Project.objects.create(owner=user, title=title, description=description)
        return JsonResponse({"success": True})

@method_decorator(csrf_exempt, name='dispatch')
class CreateDialogView(View):
    def post(self, request):
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            return JsonResponse({"success": False, "error": "Not authorized"}, status=403)

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "User not found"}, status=404)

        data = json.loads(request.body)
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        model_id = data.get("model_id")
        project_id = data.get("project_id")

        if not title:
            return JsonResponse({"success": False, "error": "Title required"}, status=400)

        model = Model.objects.filter(id=model_id, is_active=True).first()
        project = Project.objects.filter(id=project_id, owner=user).first() if project_id else None

        dialog = Dialog.objects.create(
            user=user,
            model=model,
            title=title,
            project=project
        )

        return JsonResponse({"success": True, "dialog_id": str(dialog.id)})

@method_decorator(csrf_exempt, name='dispatch')
class InviteToProjectView(View):
    def post(self, request, project_id):
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            return JsonResponse({"success": False, "error": "Not authorized"}, status=403)

        try:
            owner = User.objects.get(telegram_id=telegram_id)
            project = Project.objects.get(id=project_id, owner=owner)
        except (User.DoesNotExist, Project.DoesNotExist):
            return JsonResponse({"success": False, "error": "Project not found or access denied"}, status=404)

        data = json.loads(request.body)
        target_telegram_id = data.get("telegram_id")
        role = data.get("role", "viewer")

        try:
            target_user = User.objects.get(telegram_id=target_telegram_id)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "User not found"}, status=404)

        ProjectMember.objects.update_or_create(
            project=project,
            user=target_user,
            defaults={"role": role}
        )

        return JsonResponse({"success": True})

@method_decorator(csrf_exempt, name='dispatch')
class AddProjectMemberView(View):
    def post(self, request, project_id):
        data = json.loads(request.body)
        user_id = data.get("user_id")
        role = data.get("role", "viewer")

        telegram_id = request.session.get("telegram_id")
        project = get_object_or_404(Project, id=project_id, owner__telegram_id=telegram_id)

        try:
            user = User.objects.get(id=user_id)
            ProjectMember.objects.create(project=project, user=user, role=role)
            return JsonResponse({"success": True})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "Пользователь не найден"}, status=404)
        except IntegrityError:
            return JsonResponse({"success": False, "error": "Пользователь уже добавлен"}, status=400)