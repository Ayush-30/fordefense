from .models import SendNotification


def notification_count(request):
    user = request.user
    if user.id is None:
        pass
        return {}
    else:
        not_viewed = SendNotification.objects.filter(user=user, viewed=False).count()
        return {'not_viewed': not_viewed}