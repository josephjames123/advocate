from django import forms
from django.contrib.auth.forms import SetPasswordForm
from .models import Internship ,LawyerProfile, TimeSlot ,CustomUser
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

    
    


    
    

