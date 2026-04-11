# notifications/views.py
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Notification

# Lister toutes les notifications
@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).values(
        'id', 'type', 'title', 'message', 'is_read', 'created_at'
    )
    return JsonResponse({'notifications': list(notifications)}, safe=False)

# Marquer une notification comme lue
@login_required
@require_http_methods(['PATCH', 'POST'])
def mark_as_read(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'notification marquée comme lue'})
    except Notification.DoesNotExist:
        return JsonResponse({'error': 'Notification introuvable'}, status=404)

# Marquer toutes comme lues
@login_required
@require_http_methods(['POST'])
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'toutes les notifications sont lues'})

# Nombre de non lues
@login_required
def unread_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})