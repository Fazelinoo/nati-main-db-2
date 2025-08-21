from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import get_user_model

@login_required
def heartbeat(request):
    User = get_user_model()
    User.objects.filter(pk=request.user.pk).update(last_seen=timezone.now())
    return JsonResponse({'status': 'ok'})
