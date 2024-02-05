from django import forms
from django.contrib.auth.forms import SetPasswordForm
from .models import Booking, HolidayRequest ,Internship ,LawyerProfile, Task, TimeSlot ,CustomUser
from datetime import timedelta ,datetime, timezone
from dateutil.relativedelta import relativedelta
from django.utils import timezone




class CustomPasswordResetForm(SetPasswordForm):
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput,
        help_text="Enter the same password as above, for verification."
    )
    
    
# class LoginForm(forms.Form):
#     email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}))
#     password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['details', 'booking_date', 'time_slot']

    booking_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time_slot = forms.ModelChoiceField(queryset=TimeSlot.objects.none())  # Use ModelChoiceField

    def __init__(self, *args, **kwargs):
        lawyer = kwargs.pop('lawyer', None)
        super().__init__(*args, **kwargs)
        
        if lawyer:
            # Convert lawyer's working end time to datetime.datetime and subtract 1 hour
            end_time = datetime.combine(datetime.today(), lawyer.working_time_end.start_time) - timedelta(hours=1)
            
            available_time_slots = TimeSlot.objects.filter(
                start_time__gte=lawyer.working_time_start.start_time,
                start_time__lt=end_time.time(),  # Convert back to datetime.time
            )
            self.fields['time_slot'].queryset = available_time_slots
          
        
class InternshipForm(forms.ModelForm):
    class Meta:
        model = Internship
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter lawyers with experience 5 or more years
        self.fields['lawyer_profile'].queryset = LawyerProfile.objects.filter(experience__gte=5)
        
        # Use DateInput widget for the start_date field and add 'form-control' class
        self.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        
        # Add 'form-control' class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
class BookingStatusForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['status']
        
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('reschedule', 'Reschedule'),
        ('notpaid', 'NotPaid'),
        # Add more status options as needed
    ]

    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    
class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['address', 'pin', 'state']  # Add other fields as needed
        
        
class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['address', 'pin', 'state']

class LawyerProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = LawyerProfile
        fields = ['profile_picture', 'locations']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_picture'].widget.attrs.update({'class': 'profile_picture'})
        
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['files', 'note']

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = True
            
            
class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = HolidayRequest
        fields = ['date', 'timing', 'reason', 'supporting_documents']

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'timing': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'supporting_documents': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super(LeaveRequestForm, self).clean()
        date = cleaned_data.get('date')
        timing = cleaned_data.get('timing')

        # Check maximum casual leave days for the current month
        if cleaned_data.get('type') == 'casual_leave' and timing == 'full_day':
            current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            current_month_end = (current_month_start + relativedelta(months=1)).replace(microsecond=0) - timedelta(days=1)

            total_leave_days = HolidayRequest.objects.filter(
                lawyer=cleaned_data.get('lawyer'),
                type='casual_leave',
                timing='full_day',
                date__range=(current_month_start, current_month_end)
            ).count()

            if total_leave_days >= 3:
                self.add_error('date', 'You can only request a maximum of 3 casual leave days per month.')

        return cleaned_data

    
    
class LeaveReportsFilterForm(forms.Form):
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
    ]

    current_month = timezone.now().month
    current_year = timezone.now().year

    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        initial=current_month,
        label='Month',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    year = forms.ChoiceField(
        choices=[(2023, '2023'), (2024, '2024')],
        initial=current_year,
        label='Year',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    
    


    
    

