from django import forms
from django.contrib.auth.forms import SetPasswordForm
from .models import Booking ,Internship ,LawyerProfile, TimeSlot ,CustomUser
from datetime import timedelta ,datetime


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
        
        # Use DateInput widget for the start_date field
        self.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date'})  # Set the input type to 'date'
        
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
        fields = ['profile_picture', 'working_days', 'working_time_start', 'working_time_end', 'locations']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_picture'].widget.attrs.update({'class': 'profile_picture'})

    
    

