from django.contrib import admin
from .models import Task, WeeklyReport, Project, TaskComment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'status', 'status_actions')
    search_fields = ('name',)
    list_filter = ('status',)
    actions = ['delete_selected']

    def status_actions(self, obj):
        if obj.status == 'pending':
            return '<a href="/admin/approve_project/{}/" class="button">تایید</a>'.format(obj.id)
        elif obj.status == 'active':
            return '<a href="/admin/archive_project/{}/" class="button">آرشیو</a>'.format(obj.id)
        return ''
    status_actions.allow_tags = True
    status_actions.short_description = 'عملیات'

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_users', 'project', 'start_date', 'due_date', 'status', 'is_completed')
    list_filter = ('status', 'is_completed', 'start_date', 'due_date', 'project')
    search_fields = ('title', 'project__name', 'users__username')

    def get_users(self, obj):
        return ", ".join([u.username for u in obj.users.all()])
    get_users.short_description = 'کاربران'
@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'created_at')
    search_fields = ('task__title', 'user__username', 'text')

@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'week_start', 'week_end', 'submitted_at')
    search_fields = ('user__username',)
