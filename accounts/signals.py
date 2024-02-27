from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Task, Notification ,  CaseTracking, TrackerPayment
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
        TrackerPayment.objects.create(
            client=instance.case.client,  
            casetracker=instance,
            status=PaymentStatus.PENDING  
            
        )

