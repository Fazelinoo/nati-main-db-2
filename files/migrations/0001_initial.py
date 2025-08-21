

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='uploads/')),
                ('description', models.CharField(blank=True, max_length=255)),
                ('access_level', models.CharField(choices=[('private', 'خصوصی'), ('team', 'تیمی')], default='team', max_length=20)),
                ('allowed_roles', models.CharField(help_text='نقش\u200cهایی که می\u200cتوانند این فایل را ببینند، با کاما جدا کنید', max_length=100)),
                ('size', models.BigIntegerField()),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('uploader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_files', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
