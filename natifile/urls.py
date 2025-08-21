from django.contrib import admin
from django.urls import path, include
from core.views import home, TeamLoginView
from core.views_admin import admin_user_list, admin_user_files
from core.views_admin2 import admin2_dashboard, admin2_projects, admin2_tasks, admin2_reports, admin2_files, delete_report
from django.contrib.auth.views import LogoutView
from files.views import upload_file, user_files, accessible_files, edit_file, delete_file, file_detail
from chat.views import chat_list, chat_detail, start_new_chat, chat_messages_api, unread_message_notification_api
from chat.views_heartbeat import heartbeat
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('tasks/', include('tasks.urls')),
    path('admin/', admin.site.urls),
    path('login/', TeamLoginView.as_view(), name='login'), # hanoozam ye bug to dark/light hast
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('upload/', upload_file, name='upload_file'), # path fix shod
    path('my-files/', user_files, name='user_files'),
    path('files/', accessible_files, name='accessible_files'),
    path('files/<int:file_id>/edit/', edit_file, name='edit_file'),
    path('files/<int:file_id>/', file_detail, name='file_detail'),
    path('files/<int:file_id>/delete/', delete_file, name='delete_file'),
    path('chats/', chat_list, name='chat_list'),
    path('chats/new/', start_new_chat, name='start_new_chat'),
    path('chats/<int:chat_id>/', chat_detail, name='chat_detail'),
    path('admin2/delete_report/<int:report_id>/', delete_report, name='delete_report'),
    path('upload/', upload_file, name='upload_file'), # path fix shod
    path('my-files/', user_files, name='user_files'),
    path('files/', accessible_files, name='accessible_files'),
    path('files/<int:file_id>/edit/', edit_file, name='edit_file'),
    path('files/<int:file_id>/', file_detail, name='file_detail'),
    path('files/<int:file_id>/delete/', delete_file, name='delete_file'),
    path('chats/', chat_list, name='chat_list'),
    path('chats/new/', start_new_chat, name='start_new_chat'),
    path('chats/<int:chat_id>/', chat_detail, name='chat_detail'),
    path('admin2/delete_report/<int:report_id>/', delete_report, name='delete_report'),
    path('chats/<int:chat_id>/api/messages/', chat_messages_api, name='chat_messages_api'),
    path('notifications/api/unread/', unread_message_notification_api, name='unread_message_notification_api'),
    path('heartbeat/', heartbeat, name='heartbeat'),
    path('admin2/', admin2_dashboard, name='admin2_dashboard'),
    path('admin2/projects/', admin2_projects, name='admin2_projects'),
    path('admin2/tasks/', admin2_tasks, name='admin2_tasks'),
    path('admin2/reports/', admin2_reports, name='admin2_reports'),
    path('admin2/files/', admin2_files, name='admin2_files'),
    path('admin2/users/', admin_user_list, name='admin_user_list'),
    path('admin2/users/<int:user_id>/files/', admin_user_files, name='admin_user_files'),
    path('', home, name='home'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
