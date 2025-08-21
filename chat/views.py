from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

@login_required
@require_GET
def unread_message_notification_api(request):
    """
    Returns info about the latest unread message for the current user (if any),
    only one notification per sender (not per message).
    """
    chats = Chat.objects.filter(participants=request.user)
    # Only messages not sent by user and not read by user
    unread_msgs = Message.objects.filter(
        chat__in=chats
    ).exclude(sender=request.user).exclude(read_by=request.user).order_by('-timestamp')
    notified = []
    senders = set()
    for msg in unread_msgs:
        if msg.sender_id not in senders:
            notified.append({
                'sender_id': msg.sender.id,
                'sender_username': msg.sender.username,
                'sender_fullname': msg.sender.get_full_name() or msg.sender.username,
                'chat_id': msg.chat.id,
                'message_id': msg.id,
                'text': msg.text,
                'timestamp': msg.timestamp.strftime('%H:%M'),
            })
            senders.add(msg.sender_id)
    return JsonResponse({'notifications': notified})
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from users.models import CustomUser
from .models import Chat, Message

@login_required
def chat_messages_api(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    messages = chat.messages.order_by('timestamp')
    data = [
        {
            'id': m.id,
            'sender': m.sender.username,
            'text': m.text,
            'timestamp': m.timestamp.strftime('%H:%M'),
            'is_me': m.sender == request.user
        }
        for m in messages
    ]
    return JsonResponse({'messages': data})

@login_required
def chat_list(request):
    from django.utils import timezone
    from datetime import timedelta
    import pytz
    import calendar
    chats = Chat.objects.filter(participants=request.user)
    chat_info = []
    tehran = pytz.timezone('Asia/Tehran')
    now = timezone.now().astimezone(tehran)
    weekdays = list(calendar.day_name)
    for chat in chats:
        unread = chat.messages.exclude(sender=request.user).exclude(read_by=request.user).exists()
        other = chat.participants.exclude(id=request.user.id).first()
        last_seen = getattr(other, 'last_seen', None)
        online_status = ''
        if last_seen:
            last_seen_tehran = last_seen.astimezone(tehran)
            delta = now - last_seen_tehran
            if delta < timedelta(minutes=3):
                online_status = 'Online'
            else:
                # Format: Today, Yesterday, Weekday, or time only
                if last_seen_tehran.date() == now.date():
                    online_status = f"Last seen: Today, {last_seen_tehran.strftime('%H:%M')}"
                elif (now.date() - last_seen_tehran.date()).days == 1:
                    online_status = f"Last seen: Yesterday, {last_seen_tehran.strftime('%H:%M')}"
                elif (now - last_seen_tehran) < timedelta(days=7):
                    weekday = weekdays[last_seen_tehran.weekday()]
                    online_status = f"Last seen: {weekday}, {last_seen_tehran.strftime('%H:%M')}"
                else:
                    online_status = f"Last seen: {last_seen_tehran.strftime('%Y-%m-%d %H:%M')}"
        else:
            online_status = 'Unknown'
        chat_info.append({
            'chat': chat,
            'other': other,
            'unread': unread,
            'online_status': online_status
        })
    return render(request, 'chat/chat_list.html', {'chat_info': chat_info})

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    # همه پیام‌هایی که توسط کاربر خوانده نشده و فرستنده‌شان کاربر نیست را خوانده شده علامت بزن
    unread_msgs = chat.messages.exclude(sender=request.user).exclude(read_by=request.user)
    for msg in unread_msgs:
        msg.read_by.add(request.user)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Message.objects.create(chat=chat, sender=request.user, text=text)
            return redirect('chat_detail', chat_id=chat.id)
    messages = chat.messages.order_by('timestamp')
    return render(request, 'chat/chat_detail.html', {'chat': chat, 'messages': messages})

@login_required
def start_new_chat(request):
    users = CustomUser.objects.exclude(id=request.user.id)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        other = get_object_or_404(CustomUser, id=user_id)
        chat = Chat.objects.filter(participants=request.user).filter(participants=other).first()
        if not chat:
            chat = Chat.objects.create()
            chat.participants.add(request.user, other)
        return redirect('chat_detail', chat_id=chat.id)
    return render(request, 'chat/start_new_chat.html', {'users': users})
