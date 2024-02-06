import datetime
from .models import *
from django.utils import timezone


def notifications(request):
    notifications = None
    lawyer_profile = None
    current_month = None
    time_update = None

    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
        if request.user.user_type == 'lawyer':
            try:
                lawyer_profile = LawyerProfile.objects.get(user=request.user)
                current_month = timezone.now().month
                # current_month = "03"
                time_update = lawyer_profile.time_update  
            except LawyerProfile.DoesNotExist:
                pass

    return {
        'notifications': notifications,
        'lawyer_profile': lawyer_profile,
        'current_month': current_month,
        'time_update': time_update,
    }
