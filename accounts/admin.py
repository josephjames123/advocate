from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# from .models import CurrentCase , HolidayRequest,Payment, Task
# from .models import CustomUser, LawyerProfile , ContactEntry , Booking , Student, Internship, Application ,TimeSlot , Day , LawyerDayOff , Case, Appointment, CaseTracking , WorkAssignment,TrackerPayment
from .models import *
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'user_type', 'address', 'dob', 'pin', 'state', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

# Register the CustomUser model with the updated admin class
admin.site.register(CustomUser, CustomUserAdmin)
@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'specialization', 'experience', 'start_date', 'profile_picture')
    
admin.site.register(Day)
admin.site.register(Student)
admin.site.register(Application)
admin.site.register(Appointment)
admin.site.register(TimeSlot)
admin.site.register(LawyerDayOff)
admin.site.register(Case)
admin.site.register(CaseTracking)
admin.site.register(WorkAssignment)
admin.site.register(CurrentCase)
admin.site.register(Payment)
admin.site.register(HolidayRequest)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'lawyer_profile', 'min_cgpa', 'start_date', 'duration')
    list_filter = ('lawyer_profile',)

    def get_form(self, request, obj=None, **kwargs):
        # Customize the form to include only lawyers with 5 or more years of experience
        form = super().get_form(request, obj, **kwargs)

        if form.base_fields.get('lawyer_profile'):
            form.base_fields['lawyer_profile'].queryset = LawyerProfile.objects.filter(experience__gte=5)

        return form

# Register the Internship model with the custom admin class
admin.site.register(Internship, InternshipAdmin)
admin.site.register(Task)
admin.site.register(StudentPayment)
admin.site.register(Notification)
admin.site.register(FinePayment)
admin.site.register(TrackerPayment)
admin.site.register(TrackerNotification)
admin.site.register(Feedback)



