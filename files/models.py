from django.conf import settings
from django.db import models
from users.models import Role

# Create your models here.

class File(models.Model):
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_files')

    file = models.FileField(upload_to='')
    description = models.CharField(max_length=255, blank=True)
    access_level = models.CharField(max_length=20, choices=[('private', 'Private'), ('public', 'Public')], default='private')
    allowed_roles = models.CharField(max_length=100, help_text='نقش‌هایی که می‌توانند این فایل را ببینند، با کاما جدا کنید')
    size = models.BigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} - {self.uploader.username}"

    def can_user_access(self, user):
        if self.access_level == 'private' and self.uploader != user:
            return False
        if self.allowed_roles:
            allowed = [r.strip() for r in self.allowed_roles.split(',')]
            return user.role in allowed or user == self.uploader
        return True
