from django.urls import path
from . import views

urlpatterns = [
    path('my-reports/', views.user_reports, name='user_reports'),
    path('upload-report/<int:project_id>/', views.upload_weekly_report, name='upload_weekly_report_for_project'),
    path('my-projects/<int:project_id>/', views.user_project_tasks, name='user_project_tasks'),
    path('my-projects/', views.user_projects, name='user_projects'),
    path('my/', views.user_tasks, name='user_tasks'),
    path('complete/<int:task_id>/', views.complete_task, name='complete_task'),
    path('upload-report/', views.upload_weekly_report, name='upload_weekly_report'),
    path('assign/<int:user_id>/', views.assign_task, name='assign_task'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/add-task/', views.add_task_to_project, name='add_task_to_project'),
    path('tasks/kanban/', views.kanban_board, name='kanban_board'),
    path('tasks/<int:task_id>/comment/', views.add_task_comment, name='add_task_comment'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('admin/approve_project/<int:project_id>/', views.approve_project, name='approve_project'),
    path('admin/archive_project/<int:project_id>/', views.archive_project, name='archive_project'),
]
