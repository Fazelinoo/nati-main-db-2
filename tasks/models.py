from django.db import models
from django.conf import settings


from users.models import Role, CustomUser

class Project(models.Model):

    STATUS_CHOICES = [
        ('pending', 'در انتظار تایید'),
        ('active', 'فعال'),
        ('archived', 'آرشیو شده'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.name

class ProjectRole(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_roles')
    role = models.CharField(max_length=20, choices=Role.choices)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='project_roles')

    def __str__(self):
        return f"{self.project.name} - {self.get_role_display()}"

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'در انتظار'),
        ('doing', 'در حال انجام'),
        ('done', 'انجام شده'),
        ('late', 'عقب‌افتاده'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='todo')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.project.name if self.project else ''}"

class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"نظر {self.user.username} روی {self.task.title}"


class WeeklyReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='weekly_reports')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='weekly_reports', null=True, blank=True)
    week_start = models.DateField()
    week_end = models.DateField()
    file = models.FileField(upload_to='weekly_reports/', blank=True, null=True)
    description = models.TextField(blank=True, help_text='توضیح مختصر درباره کارهای انجام شده (اختیاری)')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.user.username} ({self.week_start} - {self.week_end})"
