from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from httpcore import request
from .models import Task, Notification ,  CaseTracking, TrackerPayment ,TrackerNotification,Appointment
from .constants import PaymentStatus
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.http import HttpRequest




@receiver(post_save, sender=Task)
def task_notification(sender, instance, created, **kwargs):
    print("Signal triggered")
    if created:
        message = f"A task has been submitted by {instance.student.user.username}."
        Notification.objects.create(
            recipient=instance.work_assignment.case.lawyer.user,
            student=instance.student,
            work_assignment=instance.work_assignment,
            message=message
        )
    else:
        if instance.work_assignment.deadline_date < timezone.now() and not instance.files:
            message = f"The deadline for the task assigned to {instance.student.user.username} has passed."
            Notification.objects.create(
                recipient=instance.work_assignment.case.lawyer.user,
                student=instance.student,
                work_assignment=instance.work_assignment,
                message=message
            )
            
            


@receiver(post_save, sender=CaseTracking)
def create_tracker_payment(sender, instance, created, **kwargs):
    """
    Signal receiver function to create a TrackerPayment object when a CaseTracking object is created.
    """
    if created:
        
        
        tracker_payment = TrackerPayment.objects.create(
            client=instance.case.client,  
            casetracker=instance,
            status=PaymentStatus.PENDING  
            
        )
        
        if instance.amount == 0 or instance.amount == '0':
            tracker_payment.status = PaymentStatus.SUCCESS
            tracker_payment.save()
        
@receiver(post_save, sender=TrackerPayment)
def create_notification(sender, instance, **kwargs):
    if instance.status == "confirmed":
        print("Status changed to confirmed")

        notification = TrackerNotification.objects.create(
            lawyer=instance.casetracker.case.lawyer,
            recipient=instance.casetracker.case.lawyer,
            casetracking=instance.casetracker,
            payment=instance,
            message = f"The payment for {instance.casetracker} has been Paid "
        )
        print("Notification created:", notification)
        
        
@receiver(post_save, sender=Appointment)
def send_booking_confirmation(sender, instance, created, **kwargs):
    if created:
        meeting_link = f"http://127.0.0.1:8000/meeting/{instance.id}/?roomID={instance.token}"
        
        # Send confirmation email to client
        client_subject = 'Booking Confirmation'
        client_message = render_to_string('booking_confirmation_email.html', {
            'booking_date': instance.appointment_date,
            'booking_time': instance.time_slot,
            'lawyer': instance.lawyer.user.get_full_name(),
            'meeting_link': meeting_link,
        })
        send_mail(
            client_subject,
            strip_tags(client_message),
            'from@example.com',
            [instance.client.email],
            html_message=client_message,
            fail_silently=False,
        )

        # Send notification email to lawyer
        lawyer_subject = 'New Booking'
        lawyer_message = render_to_string('lawyer_notification_email.html', {
            'booking_date': instance.appointment_date,
            'booking_time': instance.time_slot,
            'client': instance.client.get_full_name(),
            'meeting_link': meeting_link,
        })
        send_mail(
            lawyer_subject,
            strip_tags(lawyer_message),
            'from@example.com',
            [instance.lawyer.user.email],
            html_message=lawyer_message,
            fail_silently=False,
        )