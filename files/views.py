from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required

@login_required
def file_detail(request, file_id):
    file = get_object_or_404(File, id=file_id)
    if not file.can_user_access(request.user):
        return redirect('accessible_files')
    return render(request, 'files/file_detail.html', {'file': file})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django import forms
from .models import File
from django.db.models import Q
from users.models import Role

class FileUploadForm(forms.ModelForm):
    allowed_roles = forms.MultipleChoiceField(
        choices=Role.choices,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='نقش‌های مجاز',
        required=False
    )
    class Meta:
        model = File
        fields = ['file', 'description', 'access_level', 'allowed_roles']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'access_level': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_file(self):
        f = self.cleaned_data['file']
        if f.size > 2 * 1024 * 1024 * 1024:
            raise forms.ValidationError('حجم فایل نباید بیشتر از ۲ گیگابایت باشد.')
        return f

    def clean_allowed_roles(self):
        roles = self.cleaned_data.get('allowed_roles', [])
        return ','.join(roles)

    def initial_allowed_roles(self):
        if self.instance and self.instance.allowed_roles:
            return self.instance.allowed_roles.split(',')
        return []

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.uploader = request.user
            file_obj.size = file_obj.file.size
            file_obj.save()
            return render(request, 'files/upload_success.html', {'file': file_obj})
    else:
        form = FileUploadForm()
    return render(request, 'files/upload.html', {'form': form})

@login_required
def user_files(request):
    if request.user.is_superuser or getattr(request.user, 'role', None) in ['head_of_team', 'head_of_it']:
        # jadid tarin file nemiyavord fix shod
        files = File.objects.filter(
            Q(access_level='public') |
            Q(uploader=request.user)
        ).distinct().order_by('-uploaded_at')
    else:
        files = File.objects.filter(uploader=request.user).order_by('-uploaded_at')
    return render(request, 'files/user_files.html', {'files': files})

@login_required
def accessible_files(request):
    files = File.objects.exclude(uploader=request.user).order_by('-uploaded_at')
    visible_files = [f for f in files if f.can_user_access(request.user)]
    return render(request, 'files/accessible_files.html', {'files': visible_files})

@login_required
def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    if file.uploader == request.user or request.user.is_superuser or getattr(request.user, 'role', None) in ['head_of_team', 'head_of_it']:
        file.delete()
    return redirect(request.GET.get('next', 'user_files'))

class FileEditForm(FileUploadForm):
    class Meta(FileUploadForm.Meta):
        fields = ['file', 'description', 'access_level', 'allowed_roles']

@login_required
def edit_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    if not (file.uploader == request.user or request.user.is_superuser or getattr(request.user, 'role', None) in ['head_of_team', 'head_of_it']):
        return redirect('user_files')
    if request.method == 'POST':
        form = FileEditForm(request.POST, request.FILES, instance=file)
        if form.is_valid():
            file_obj = form.save(commit=False)
            if 'file' in form.changed_data:
                file_obj.size = file_obj.file.size
            file_obj.save()
            return redirect(request.GET.get('next', 'user_files'))
    else:
        form = FileEditForm(instance=file)
    return render(request, 'files/edit_file.html', {'form': form, 'file': file})
