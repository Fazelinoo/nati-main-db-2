from django.urls import resolve
from files.models import File
from chat.models import Chat, Message

def notifications(request):
    user = request.user
    context = {}
    if not user.is_authenticated:
        return context

    # age payam jadid omad
    current_url = resolve(request.path_info).url_name
    if not current_url or not current_url.startswith('chat'):
        # payam hayi ke read nashode bashan
        unread_chats = Chat.objects.filter(participants=user)
        has_unread = Message.objects.filter(chat__in=unread_chats).exclude(sender=user).exists()
        if has_unread:
            context['has_unread_message'] = True

    files = File.objects.exclude(uploader=user)
    new_files = []
    for f in files:
        if f.can_user_access(user):

            new_files.append(f)
    if new_files:
        context['has_new_file'] = True
    return context
