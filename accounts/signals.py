from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Task, Notification ,  CaseTracking, TrackerPayment ,TrackerNotification
from .constants import PaymentStatus

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