# accounts/utils.py

from django.utils import timezone

def validate_date(date_str):
    """
    Validate that the given date string is not in the future.
    """
    try:
        input_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        current_date = timezone.now().date()
        return input_date <= current_date
    except ValueError:
        return False

def validate_time(time_str):
    """
    Validate that the given time string is not in the future.
    """
    try:
        input_time = timezone.datetime.strptime(time_str, '%H:%M').time()
        current_time = timezone.now().time()
        return input_time <= current_time
    except ValueError:
        return False
