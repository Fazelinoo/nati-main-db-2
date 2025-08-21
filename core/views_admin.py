from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from users.models import CustomUser
from files.models import File
from django.utils import timezone
import pytz
import calendar

def is_admin(user):
    return (
        user.is_superuser or user.is_staff or
        getattr(user, 'role', None) in ['head_of_team', 'head_of_it']
    )

@user_passes_test(is_admin)
def admin_user_list(request):
    tehran = pytz.timezone('Asia/Tehran')
    now = timezone.now().astimezone(tehran)
    weekdays = list(calendar.day_name)
    users = CustomUser.objects.all()
    user_info = []
    for u in users:
        last_seen = getattr(u, 'last_seen', None)
        if last_seen:
            last_seen_tehran = last_seen.astimezone(tehran)
            delta = now - last_seen_tehran
            if delta < timezone.timedelta(minutes=3):
                online_status = 'Online'
            else:
                if last_seen_tehran.date() == now.date():
                    online_status = f"Last seen: Today, {last_seen_tehran.strftime('%H:%M')}"
                elif (now.date() - last_seen_tehran.date()).days == 1:
                    online_status = f"Last seen: Yesterday, {last_seen_tehran.strftime('%H:%M')}"
                elif (now - last_seen_tehran) < timezone.timedelta(days=7):
                    weekday = weekdays[last_seen_tehran.weekday()]
                    online_status = f"Last seen: {weekday}, {last_seen_tehran.strftime('%H:%M')}"
                else:
                    online_status = f"Last seen: {last_seen_tehran.strftime('%Y-%m-%d %H:%M')}"
        else:
            online_status = 'Unknown'
        user_info.append({'user': u, 'online_status': online_status})
    return render(request, 'core/admin_user_list.html', {'user_info': user_info})

@user_passes_test(is_admin)
def admin_user_files(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    files = File.objects.filter(uploader=user, access_level='public')
    return render(request, 'core/admin_user_files.html', {'files': files, 'user': user})
