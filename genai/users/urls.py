from django.urls import path
from .views import TelegramAuthView, TelegramEntryView, DialogsView, SearchUserView
from dialogs.views import CreateDialogView
from .views import AdminDashboardView, AdminModelCreateView, AdminModelDeleteView
from dialogs.views import DialogDetailView

from dialogs.views import SendMessageView, EditMessageView

from projects.views import ProjectListView, ProjectDetailView

from projects.views import CreateProjectView

from projects.views import InviteToProjectView

from projects.views import AddProjectMemberView

from dialogs.views import SetModelView

urlpatterns = [
    path('', TelegramEntryView.as_view(), name='entry'),
    path('auth/telegram/', TelegramAuthView.as_view(), name='telegram_auth'),
    path('dialogs/', DialogsView.as_view(), name='dialogs'),
    path('dialogs/create/', CreateDialogView.as_view(), name='dialog_create'),
    path("dialog/<uuid:dialog_id>/", DialogDetailView.as_view(), name="dialog_detail"),
    path("dialog/<uuid:dialog_id>/send/", SendMessageView.as_view(), name="dialog_send"),
    path("dialog/<uuid:dialog_id>/edit/<uuid:message_id>/", EditMessageView.as_view(), name="dialog_edit"),
    path('projects/', ProjectListView.as_view(), name='project_list'),
    path('projects/<uuid:project_id>/', ProjectDetailView.as_view(), name='project_detail'),
    path("projects/create/", CreateProjectView.as_view(), name="project_create"),
    path('projects/<uuid:project_id>/invite/', InviteToProjectView.as_view(), name='project_invite'),
    path('projects/<uuid:project_id>/search_user/', SearchUserView.as_view(), name='project_search_user'),
    path('projects/<uuid:project_id>/add_member/', AddProjectMemberView.as_view(), name='project_add_member'),
    path("admin-panel/", AdminDashboardView.as_view(), name="admin_panel"),
    path("admin-panel/create-model/", AdminModelCreateView.as_view(), name="admin_model_create"),
    path("admin-panel/delete-model/<uuid:model_id>/", AdminModelDeleteView.as_view(), name="admin_model_delete"),
    path("dialog/<uuid:dialog_id>/set_model/", SetModelView.as_view(), name="set_model"),

]

