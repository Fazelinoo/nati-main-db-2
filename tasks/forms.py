from django import forms
from .models import WeeklyReport, Project, Task, TaskComment, ProjectRole
from users.models import Role


class WeeklyReportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            from django.db.models import Q
            self.fields['project'].queryset = Project.objects.filter(
                Q(tasks__users=user) | Q(project_roles__user=user)
            ).distinct()
        self.fields['file'].required = False

        import re
        for field in ['week_start', 'week_end']:
            val = self.data.get(field)
            if val:
                import jdatetime
                try:

                    parts = re.split(r'[-/]', val)
                    parts = [int(x) for x in parts]
                    if parts[0] > 1500:

                        continue
                    gdate = jdatetime.date(parts[0], parts[1], parts[2]).togregorian()
                    self.data = self.data.copy()
                    self.data[field] = gdate.strftime('%Y-%m-%d')
                except Exception:
                    pass

    class Meta:
        model = WeeklyReport
        fields = ['project', 'week_start', 'week_end', 'file', 'description']

class ProjectForm(forms.ModelForm):
    roles = forms.MultipleChoiceField(choices=Role.choices, widget=forms.CheckboxSelectMultiple, required=False, label='نقش‌های پروژه')
    class Meta:
        model = Project
        fields = ['name', 'description']

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            instance.save()

            ProjectRole.objects.filter(project=instance).delete()
            for role in self.cleaned_data['roles']:
                ProjectRole.objects.create(project=instance, role=role)
        return instance

class TaskForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple, label='اعضای پروژه')
    class Meta:
        model = Task
        fields = ['project', 'users', 'title', 'description', 'start_date', 'due_date']  # حذف status از فرم

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        if project:

            from users.models import CustomUser
            roles = ProjectRole.objects.filter(project=project).values_list('role', flat=True)
            self.fields['users'].queryset = CustomUser.objects.filter(role__in=roles)
        else:
            self.fields['users'].queryset = CustomUser.objects.none()

    def save(self, commit=True):
        instance = super().save(commit=False)

        instance.status = 'doing'
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ['text']
