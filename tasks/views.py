
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required
def user_reports(request):
    reports = request.user.weekly_reports.select_related('project').order_by('-week_start')
    return render(request, 'tasks/user_reports.html', {'reports': reports})


@login_required
def user_projects(request):
    user = request.user

    projects = Project.objects.filter(
        (Q(tasks__users=user) | Q(project_roles__user=user)) & ~Q(status='archived')
    ).distinct()
    
    projects = projects.filter(tasks__is_completed=False).distinct()

    from django.utils import timezone
    now = timezone.now()

    if is_admin(user):
        independent_tasks_doing = Task.objects.filter(project__isnull=True, is_completed=False).order_by('-created_at')
        independent_tasks_done = Task.objects.filter(project__isnull=True, is_completed=True).order_by('-created_at')
    else:
        independent_tasks_doing = Task.objects.filter(users=user, project__isnull=True, is_completed=False).order_by('-created_at')
        independent_tasks_done = Task.objects.filter(
            users=user,
            project__isnull=True,
            is_completed=True,
            created_at__gte=now - timezone.timedelta(days=1)
        ).order_by('-created_at')
    return render(request, 'tasks/user_projects.html', {
        'projects': projects,
        'independent_tasks_doing': independent_tasks_doing,
        'independent_tasks_done': independent_tasks_done,
    })

@login_required
def user_project_tasks(request, project_id):
    user = request.user
    project = get_object_or_404(Project, id=project_id)

    tasks = project.tasks.filter(users=user)
    return render(request, 'tasks/user_project_tasks.html', {'project': project, 'tasks': tasks})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Task, WeeklyReport, Project, TaskComment
from django.db import models
from .forms import WeeklyReportForm, ProjectForm, TaskForm, TaskCommentForm
import jdatetime
from datetime import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse

def is_admin(user):
    return (
        user.is_superuser or user.is_staff or
        getattr(user, 'role', None) in ['head_of_team', 'head_of_it']
    )

@login_required
def user_tasks(request):
    user = request.user
    user_role = getattr(user, 'role', None)

    projects_with_role = Project.objects.filter(project_roles__role=user_role).distinct() if user_role else Project.objects.none()

    tasks = Task.objects.filter(users=user).order_by('-created_at')
   
    project_tasks = Task.objects.filter(project__in=projects_with_role).exclude(users=user)
    reports = WeeklyReport.objects.filter(user=user).order_by('-week_start')
    return render(request, 'tasks/user_tasks.html', {
        'tasks': tasks,
        'project_tasks': project_tasks,
        'reports': reports,
        'projects_with_role': projects_with_role,
    })

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.is_completed = True
        task.save()
        return redirect('user_tasks')
    return render(request, 'tasks/complete_task.html', {'task': task})

@login_required
def upload_weekly_report(request, project_id=None):
    initial = {}
    if project_id:
        initial['project'] = project_id
    if request.method == 'POST':
        form = WeeklyReportForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            return redirect('user_reports')
    else:
        form = WeeklyReportForm(user=request.user, initial=initial)
    return render(request, 'tasks/upload_weekly_report.html', {'form': form})

@user_passes_test(is_admin)
def assign_task(request, user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = persian_to_gregorian(request.POST.get('start_date'))
        due_date = persian_to_gregorian(request.POST.get('due_date'))
        if title and due_date:
            task = Task.objects.create(title=title, description=description or '', start_date=start_date or timezone.now().date(), due_date=due_date, status='doing')
            task.users.add(user)
            return redirect('/admin2/users/')
    return render(request, 'tasks/assign_task.html', {'user': user})

from django.contrib.auth.decorators import login_required
@login_required
def project_list(request):
    user = request.user
    user_role = getattr(user, 'role', None)
   
    projects = Project.objects.filter(
        Q(project_roles__user=user) | Q(project_roles__role=user_role)
    ).distinct().order_by(
        models.Case(
            models.When(status='active', then=0),
            models.When(status='pending', then=1),
            models.When(status='archived', then=2),
            default=3,
            output_field=models.IntegerField(),
        ),
        '-created_at'
    )
    return render(request, 'tasks/project_list.html', {'projects': projects})

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            if request.user.is_superuser or request.user.is_staff or getattr(request.user, 'role', None) in ['head_of_team', 'head_of_it']:
                project.status = 'active'
                msg = 'پروژه با موفقیت ثبت و فعال شد.'
            else:
                project.status = 'pending'
                msg = 'پروژه با موفقیت ثبت شد و در انتظار تایید است.'
            project.save()

            for role in form.cleaned_data['roles']:
                from .models import ProjectRole
                ProjectRole.objects.create(project=project, role=role)
            messages.success(request, msg)
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'tasks/project_create.html', {'form': form})

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all().order_by('-created_at')

    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        task = get_object_or_404(Task, id=task_id, project=project)
        if request.user in task.users.all():
            task.is_completed = not task.is_completed
            task.save()
            messages.success(request, 'وضعیت تسک با موفقیت تغییر کرد.')
        else:
            messages.error(request, 'شما مجاز به تغییر وضعیت این تسک نیستید.')
        return redirect('project_detail', project_id=project.id)
    return render(request, 'tasks/project_detail.html', {'project': project, 'tasks': tasks})

@login_required
def kanban_board(request):
    tasks = Task.objects.select_related('project').all()
    return render(request, 'tasks/kanban_board.html', {'tasks': tasks})

@login_required
def add_task_comment(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            return redirect('project_detail', project_id=task.project.id)
    else:
        form = TaskCommentForm()
    return render(request, 'tasks/add_task_comment.html', {'form': form, 'task': task})

def persian_to_gregorian(date_str):

    try:
        parts = [int(x) for x in date_str.replace('-', '/').split('/')]
        if len(parts) == 3:
            jd = jdatetime.date(parts[0], parts[1], parts[2])
            return jd.togregorian().strftime('%Y-%m-%d')
    except Exception:
        return date_str
    return date_str

@login_required
def add_task_to_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['start_date'] = persian_to_gregorian(post_data.get('start_date', ''))
        post_data['due_date'] = persian_to_gregorian(post_data.get('due_date', ''))
        form = TaskForm(post_data, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            form.save_m2m()
            messages.success(request, 'تسک جدید با موفقیت به پروژه اضافه شد.')
            return redirect('project_detail', project_id=project.id)
        else:
            messages.error(request, 'خطا در ثبت تسک. لطفاً اطلاعات را بررسی کنید.')
    else:
        form = TaskForm(project=project)
    return render(request, 'tasks/add_task_to_project.html', {'form': form, 'project': project})

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if task.project:
        user_roles = task.project.project_roles.values_list('role', flat=True)
    else:
        user_roles = []
    can_edit = (request.user in task.users.all()) or is_admin(request.user)
    if request.method == 'POST':
        if can_edit:
            if task.status == 'doing':
                task.status = 'done'
                task.is_completed = True
            elif task.status == 'done':
                task.status = 'doing'
                task.is_completed = False
            elif task.status == 'late':
                task.status = 'doing'
                task.is_completed = False
            task.save()
            messages.success(request, 'وضعیت تسک با موفقیت تغییر کرد.')
        else:
            messages.error(request, 'شما مجاز به تغییر وضعیت این تسک نیستید.')
        return redirect('task_detail', task_id=task.id)
    return render(request, 'tasks/task_detail.html', {'task': task, 'can_edit': can_edit})

@user_passes_test(is_admin)
def approve_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.status = 'active'
    project.save()
    messages.success(request, 'پروژه با موفقیت تایید و فعال شد.')
    return HttpResponseRedirect(reverse('admin:tasks_project_changelist'))

@user_passes_test(is_admin)
def archive_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.status = 'archived'
    project.save()
    messages.success(request, 'پروژه با موفقیت آرشیو شد.')
    return HttpResponseRedirect(reverse('admin:tasks_project_changelist'))
