from .models import Notification, LawyerProfile

def notifications(request):
    notifications = None
    lawyer_profile = None

    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
        if request.user.user_type == 'lawyer':
            try:
                lawyer_profile = LawyerProfile.objects.get(user=request.user)
            except LawyerProfile.DoesNotExist:
                pass

    return {'notifications': notifications, 'lawyer_profile': lawyer_profile}