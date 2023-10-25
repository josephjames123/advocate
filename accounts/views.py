# accounts/views.py
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect ,get_object_or_404 ,HttpResponseRedirect
from django.urls import reverse
from .models import CustomUser, LawyerProfile , CurrentCase  
from django.http import HttpResponseForbidden , Http404,HttpResponseNotFound , HttpResponse ,HttpResponseBadRequest
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
# from django.contrib.auth.forms import SetPasswordForm
from .forms import CustomPasswordResetForm  
from django.core.exceptions import ValidationError
from datetime import datetime
from .models import LawyerProfile, Internship , Task , Student , Day ,TimeSlot , LawyerDayOff , HolidayRequest , Case ,Appointment , CaseTracking , WorkAssignment , Payment
from .forms import InternshipForm ,CustomUserUpdateForm, LawyerProfileUpdateForm
import markdown
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm  # Import AuthenticationForm
from django.contrib import messages
import re  
import csv
from django.db import models  # Import the models module from Django's database module
import os
from django.utils import timezone
import pytz  # Import pytz module
from django.db.models import Q
from .forms import UserProfileUpdateForm  # Create a form for profile updates
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import date, timedelta
from pytz import timezone as pytz_timezone
from .utils import validate_date, validate_time
from django.http import HttpResponseServerError
import traceback
from django.utils.html import strip_tags
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import JsonResponse
import razorpay
from django.views.decorators.csrf import csrf_exempt
import logging
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
import json
from .constants import PaymentStatus
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from .models import Application


logger = logging.getLogger(__name__)


# login view #

def login_view(request):
    if request.user.is_authenticated:
        user = request.user  # Get the authenticated user
        if user.user_type == 'admin':
            return redirect(reverse('admin_dashboard'))
        elif user.user_type == 'client':
            return redirect(reverse('home'))
        elif user.user_type == 'lawyer':
            # Assuming you have a one-to-one relationship between CustomUser and LawyerProfile
            lawyer_profile = LawyerProfile.objects.get(user=user)
            if lawyer_profile.time_update is None or (timezone.now() - lawyer_profile.time_update).days > 14:
                return redirect(reverse('assign_working_hours'))
            else:
                return redirect(reverse('lawyer_dashboard'))
        elif user.user_type == 'student':
            return redirect(reverse('student_dashboard'))
    
    if request.method == 'POST':
        email = request.POST['email']  # Change this to 'email'
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)  # Use email for authentication
        if user is not None:
            login(request, user)
            if user.user_type == 'admin':
                return redirect(reverse('admin_dashboard'))
            elif user.user_type == 'client':
                return redirect(reverse('client_dashboard'))
            elif user.user_type == 'lawyer':
                # Assuming you have a one-to-one relationship between CustomUser and LawyerProfile
                lawyer_profile = LawyerProfile.objects.get(user=user)
                if lawyer_profile.time_update is None or (timezone.now() - lawyer_profile.time_update).days > 14:
                    return redirect(reverse('assign_working_hours'))
                else:
                    return redirect(reverse('lawyer_dashboard'))
            elif user.user_type == 'student':
                return redirect(reverse('student_dashboard'))
        else:
            messages.error(request, 'Invalid email or password. Please try again')
    
    return render(request, 'login.html')
    
# signup #
def signup_view(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'admin':
            return redirect(reverse('admin_dashboard'))
        elif request.user.user_type == 'client':
            return redirect(reverse('client_dashboard'))
        elif request.user.user_type == 'lawyer':
            return redirect(reverse('lawyer_dashboard'))
        elif request.user.user_type == 'student':
            return redirect(reverse('student_dashboard'))

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        # adharno = request.POST['adharno']
        address = request.POST['address']
        dob = request.POST['dob']
        pin = request.POST['pin']
        state = request.POST['state']
        phone = request.POST['phone']

        # Check if any field is empty
        if not (email and password and first_name and last_name  and address and dob and pin and state and phone):
            messages.error(request, 'All fields are required')
            return render(request, 'signup.html')

        # Check if the email is already in use
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'signup.html')
        
        # Check if the Aadhar number is already in use
        if CustomUser.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already exists')
            return render(request, 'signup.html')

        if password != confirm_password:
            messages.error(request, 'Password and confirm password do not match.')
            return render(request, 'signup.html')
        
        phone = phone.replace(" ", "")
        # adharno = adharno.replace(" ", "")
        
        # Check if the phone number exceeds 10 digits
        if len(phone) > 10:
            messages.error(request, 'Phone number cannot exceed 10 digits.')
            return render(request, 'signup.html')
        
        # Check if the phone number starts with a digit between 6 and 9
        if not re.match(r'^[6-9]\d{9}$', phone):
            messages.error(request, 'Phone number must start with a digit between 6 and 9 and be 10 digits long.')
            return render(request, 'signup.html')

        # Check if the password meets the complexity requirements
        if not (len(password) >= 8 and
                any(c.isdigit() for c in password) and
                any(c.islower() for c in password) and
                any(c.isupper() for c in password) and
                any(c in "!@#$%^&*()-_+=<>?/\|{}[]:;" for c in password)):
            messages.error(request, 'Password must be at least 8 characters long and include at least one digit, one lowercase letter, one uppercase letter, and one special character.')
            return render(request, 'signup.html')

        # Check if the user's age is equal or above 18
        today = datetime.today()
        birth_date = datetime.strptime(dob, "%Y-%m-%d")
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 18:
            messages.error(request, 'You must be 18 years or older to sign up.')
            return render(request, 'signup.html')
        
        # Check if first name and last name start with a digit
        if re.match(r'^\d', first_name) or re.match(r'^\d', last_name):
            messages.error(request, 'First name and last name cannot start with numbers.')
            return render(request, 'signup.html')
               

        user = CustomUser.objects.create_user(
            email=email,
            username=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            # adharno=adharno,
            address=address,
            dob=dob,
            pin=pin,
            state=state,
            phone=phone,

        )
        return redirect('login')

    return render(request, 'signup.html')

# logout #

def logout_view(request):
    logout(request)
    return redirect('login')

# dashboard  #

def dashboard_view(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html', {'user': request.user})
    else:
        return redirect('login')
    
# admin Dashboard #    
    
@login_required
def admin_dashboard(request):
    if request.user.user_type == 'admin':
        # Calculate the number of lawyers
        lawyer_count = LawyerProfile.objects.count()
        internship_count = Internship.objects.count()
        students_count = Student.objects.count()
        cases_count = Case.objects.count()
        
        
        # Retrieve the recent 5 bookings, ordered by pk in descending order (greatest to smallest)
        
        context = {
            'user': request.user,
            'lawyer_count': lawyer_count,
            'internship_count': internship_count,
            'students_count':students_count,
            'cases_count': cases_count,
            }
            
        
        # Pass the count and recent bookings to the template
        return render(request, 'admin/dashboard.html', context)
    else:
        return render(request, '404.html')

# client dashboard #    
    
@login_required
def client_dashboard(request):
    user = request.user

    # Get all bookings by the client
    all_bookings = Appointment.objects.filter(client=user)


    context = {
        'all_bookings': all_bookings,
    }

    return render(request, 'client/dashboard.html', context)

# lawyer dashboard #

@login_required
def lawyer_dashboard(request):
    if request.user.user_type == 'lawyer':
        
        # Check if the lawyer profile is complete based on specified fields
        profile = request.user.lawyer_profile
        user = request.user
        # if not all([profile.specialization, profile.start_date, profile.profile_picture, user.address, user.dob, user.pin, user.state, user.phone, profile.working_days, profile.working_time_start, profile.working_time_end]):
        if not all([profile.specialization, user.address, user.dob, user.phone,]):

            # Redirect to the lawyer_save view if any of the fields are missing
            return redirect('lawyer_save')
    
        # Get the current lawyer's profile
        lawyer_profile = LawyerProfile.objects.get(user=request.user)
        bookings = Appointment.objects.filter(lawyer=lawyer_profile).order_by('-pk')

        # Count the number of bookings for this lawyer
        case_count = Case.objects.filter(lawyer=lawyer_profile).count()
        
        return render(request, 'lawyer/dashboard.html', {'user': request.user,'bookings': bookings , 'case_count': case_count})
    else:
        return render(request, '404.html')

# add Lawyer #

@login_required    
def add_lawyer(request):
    if request.user.user_type != 'admin':
        return render(request, '404.html')

    if request.method == 'POST':
        # Get the input data from the form
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        license_no = request.POST['license_no']
        phone = request.POST['phone']

        # Check if the email already exists in the database
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'admin/add_lawyer.html')
        
        # Check if the phone already exists in the database
        if CustomUser.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone already exists.')
            return render(request, 'admin/add_lawyer.html')
        
        # Construct the absolute path to the CSV file
        project_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_file_path = os.path.join(project_directory, 'accounts', 'dataset.csv')

        # Load and search the CSV file for a matching license number and names
        
        license_number = None  # Initialize license_number as None

        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['first_name'] == first_name and row['last_name'] == last_name:
                    license_number = row['license_no']
                    break  # Exit the loop if a match is found

        if license_number is None:
            # No matching record found in the CSV file
            messages.error(request, 'Details Mismatch')
            return render(request, 'admin/add_lawyer.html') # You can customize this response as needed

        # Create a new user with user_type 'lawyer' if a match is found
        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            user_type='lawyer',
            first_name=first_name,
            last_name=last_name,
            phone = phone,
        )

        lawyer_profile = LawyerProfile.objects.create(
            user=user,
            license_no=license_no, 
            # Assign the license number from the CSV
        )

        # Generate a unique token for password reset
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        current_site = get_current_site(request)
        protocol = 'http'  # Change to 'https' if using HTTPS
        password_reset_url = f"{protocol}://{current_site.domain}/accounts/set/{uid}/{token}/"

        # Render the email body template
        message = render_to_string(
            'registration/password_set_email.html',
            {
                'user': user,
                'password_reset_url': password_reset_url,
            }
        )

        # Send the email with custom template
        send_mail(
            'Set Your Password',
            '',
            'noreply@example.com',  # Sender's email address
            [email],
            fail_silently=False,
            html_message=message  # Use the custom HTML template
        )

        return redirect('mail')  
    
    return render(request, 'admin/add_lawyer.html')

# custom password set #

def custom_password_set_confirm(request, uidb64, token):
    user_id = urlsafe_base64_decode(uidb64)
    user = CustomUser.objects.get(pk=user_id)
    
    if request.method == 'POST':
        form = CustomPasswordResetForm(user, request.POST)
        if form.is_valid():
            form.save()
            # Log the user in after setting the password
            user = authenticate(username=user.username, password=form.cleaned_data['new_password1'])
            login(request, user)
            return redirect('lawyer_save')  # Redirect to the dashboard or another page
    else:
        form = CustomPasswordResetForm(user)
    
    return render(request, 'registration/password_set_confirm.html', {'form': form, 'user': user})

# home #
def home(request):
    # Fetch the most recently added 3 lawyers from the database
    lawyers = LawyerProfile.objects.all().order_by('-user__date_joined')[:3]

    # Create a list to store lawyer names and specializations
    lawyer_info = []

    for lawyer in lawyers:
        lawyer_info.append({
            'name': f"{lawyer.user.first_name} {lawyer.user.last_name}",
            'specialization': lawyer.specialization,
            'profile_picture': lawyer.profile_picture.url,
            'id': lawyer.id,  # Add lawyer's ID
        })

    

    return render(request, 'index.html', {'lawyer_info': lawyer_info})

def practice(request):
    return render(request, 'practice.html')

    
def confirm(request):
    return render(request, 'confirm.html')

def about(request):
    return render(request, 'about.html')

# lawyer List #

def lawyer_list(request):
    # Fetch the most recently added 3 lawyers from the database
    lawyers = LawyerProfile.objects.all().order_by('-user__date_joined')[:3]

    # Create a list to store lawyer names and specializations
    lawyer_info = []

    for lawyer in lawyers:
        lawyer_info.append({
            'name': f"{lawyer.user.first_name} {lawyer.user.last_name}",
            'specialization': lawyer.specialization,
            'profile_picture': lawyer.profile_picture.url,
            'id': lawyer.id,  # Add lawyer's ID
        })

    

    return render(request, 'lawyer_list.html', {'lawyer_info': lawyer_info})


def lawyer_details(request, lawyer_id):
    # Retrieve the lawyer's details from the database
    lawyer = get_object_or_404(LawyerProfile, pk=lawyer_id)

    # Render a template with the lawyer's details
    return render(request, 'lawyer/lawyer_details.html', {'lawyer': lawyer})

def contact(request):


    return render(request, 'contact.html')

@login_required
def error(request):
    return render(request, '404.html')

def sorry(request):
    return render(request, '404.html')

def profile(request):
    return redirect('client_dashboard')

def update(request):
    return render(request, 'updated.html')

@login_required
def mail(request):
    return render(request, 'mail.html')
@login_required
def submit(request):
    return render(request, 'submitted.html')
@login_required
def book(request):
    return render(request, 'book.html')

@login_required
def reschedule_appointment(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    user = request.user

    if request.method == 'POST':
        form = BookingForm(request.POST, lawyer=booking.lawyer)

        if form.is_valid():
            new_booking_date = form.cleaned_data['booking_date']
            new_time_slot = form.cleaned_data['time_slot']

            # Check if the selected date is marked as a day off for the lawyer
            if LawyerDayOff.objects.filter(lawyer=booking.lawyer, date=new_booking_date).exists():
                messages.error(request, 'The selected date is marked as a day off for the lawyer.')
            else:
                # Check for existing bookings on the selected date and time slot
                existing_booking = Booking.objects.filter(
                    lawyer=booking.lawyer,
                    booking_date=new_booking_date,
                    time_slot=new_time_slot,
                    status='pending'
                ).first()

                if existing_booking:
                    messages.error(request, 'This time slot is already booked by another user.')
                else:
                    # Update the booking with the new date and time slot
                    booking.booking_date = new_booking_date
                    booking.time_slot = new_time_slot
                    booking.status = 'pending'  # You can set the status to 'confirmed' here
                    booking.save()
                    messages.success(request, 'Appointment rescheduled successfully.')
                    return redirect('dashboard')  # Redirect to the client's dashboard or a success page
    else:
        # Exclude the 'details' field from the form
        form = BookingForm(lawyer=booking.lawyer, initial={'booking_date': booking.booking_date, 'time_slot': booking.time_slot})
        form.fields.pop('details')  # Remove the 'details' field from the form

    return render(request, 'reschedule_appointment.html', {'form': form, 'booking': booking})

## internship details #

@login_required
def internship_detail(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id)
    roles_html = markdown.markdown(internship.roles)

    if request.method == 'POST':
        if request.user.user_type == 'student':
            student = Student.objects.get(user=request.user)
            application, created = Application.objects.get_or_create(internship=internship, student=student)
            if created:
                messages.success(request, 'Application submitted successfully.')
            else:
                messages.warning(request, 'You have already applied to this internship.')

            return redirect('internship_detail', internship_id=internship_id)

    return render(request, 'student/internship_detail.html', {'internship': internship, 'roles_html': roles_html})

# add internship #

@login_required
def add_internship(request):
    if request.method == 'POST':
        form = InternshipForm(request.POST, request.FILES)  # Include request.FILES here
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')  # Redirect to the admin dashboard
    else:
        form = InternshipForm()

    return render(request, 'admin/add_internship.html', {'form': form})

# student dashboard #

@login_required
def student_dashboard(request):
    # Check if the user is logged in and is a student
    if request.user.is_authenticated and request.user.user_type == 'student':
        try:
            # Try to retrieve the student profile associated with the user
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            # If the student profile doesn't exist, render 'student_details.html'
            return render(request, 'student/student_details.html')  

        if student.is_approved:
            # Check if college and current CGPA fields are filled
            if student.course and student.cgpa is not None:
                recent_internships = Internship.objects.order_by('-pk')[:5]
                return render(request, 'student/dashboard.html', {'user': request.user, 'recent_internships': recent_internships})
            else:
                # Redirect to 'student_details.html' if college or CGPA fields are not filled
                return render(request, 'student/student_details.html')

        else:
            # Display a message or a separate template for unapproved students
            return render(request, 'student/not_approved.html')

    # If not a student or not logged in, return forbidden access
    return render(request, '404.html')

# approve student #

@login_required
def approve_students(request):
    # Check if the user is an admin
    if not request.user.user_type == 'admin':
        return render(request, '404.html')
    
    # Get a list of unapproved students
    unapproved_students = Student.objects.filter(is_approved=False)
    
    if request.method == 'POST':
        # Handle form submissions for approving/rejecting students
        for student in unapproved_students:
            student_id = str(student.id)
            approve_key = 'approve_' + student_id
            reject_key = 'reject_' + student_id
            
            if approve_key in request.POST:
                # Approve the student
                student.is_approved = True
                student.save()
            elif reject_key in request.POST:
                # Reject the student (optional)
                student.delete()
    
        # Redirect to the approve_students page after processing the submissions
        return redirect('approve_students')
    
    return render(request, 'admin/approve_students.html', {'unapproved_students': unapproved_students})
@login_required
def is_admin_or_student(user):
    return user.user_type in ['admin', 'student']

@login_required
def student_save(request):
    if request.method == 'POST':
        # Get the form data from the request
        college = request.POST.get('college')
        current_cgpa = request.POST.get('current_cgpa')

        # Check if college and current_cgpa are not empty
        if college and current_cgpa:
            # Update or create the student profile for the user
            Student.objects.update_or_create(user=request.user, defaults={'college': college, 'current_cgpa': current_cgpa})

            # Redirect to a success page or the dashboard
            return redirect('student_dashboard')  # Replace 'dashboard' with your dashboard URL name
        else:
            return HttpResponse("Please fill in all fields.")
    else:
        return render(request, 'student/student_details.html')

from datetime import datetime

def calculate_experience(experience_str):
    parts = experience_str.split()
    
    years = 0
    months = 0
    days = 0

    for i, part in enumerate(parts):
        if part == 'years' or part == 'year':
            years = int(parts[i - 1])
        elif part == 'months' or part == 'month':
            months = int(parts[i - 1])
        elif part == 'days' or part == 'day':
            days = int(parts[i - 1])

    total_days = years * 365 + months * 30 + days
    return total_days

def calculate_experience(experience_str):
    parts = experience_str.split()
    
    years = 0
    months = 0
    days = 0

    for i, part in enumerate(parts):
        if part == 'years' or part == 'year':
            years = int(parts[i - 1])
        elif part == 'months' or part == 'month':
            months = int(parts[i - 1])
        elif part == 'days' or part == 'day':
            days = int(parts[i - 1])

    total_days = years * 365 + months * 30 + days
    return total_days

# lawyer entry1 #

@login_required
def lawyer_save(request):
    if request.user.user_type != 'lawyer':
        return render(request, '404.html')

    available_time_slots = TimeSlot.objects.all()

    if request.method == 'POST':
        specialization = request.POST.get('specialization')
        dob = request.POST.get('dob')
        dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
        today = datetime.now().date()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))

        if age < 25:
            LawyerProfile.objects.filter(user=request.user).delete()
            return render(request, 'sorry.html')
         
        address = request.POST.get('address')
        total_cases_handeled = request.POST.get('total_cases_handeled')
        currendly_handling = request.POST.get('currendly_handling')
        experience_str = request.POST.get('experience')
        court = request.POST.get('court')

        # Calculate the total number of days of experience
        total_experience_days = calculate_experience(experience_str)

        # Create or update the user's details
        user = request.user
        user.address = address
        user.dob = dob
        
        user.save()
        print("User saved")

        lawyer_profile, created = LawyerProfile.objects.get_or_create(user=user)
        lawyer_profile.specialization = specialization
        lawyer_profile.total_cases_handeled = total_cases_handeled
        lawyer_profile.currendly_handling = currendly_handling
        lawyer_profile.experience = total_experience_days
        lawyer_profile.court = court

        lawyer_profile.save()
        print("Lawyer saved")

        return render(request, 'lawyer/dashboard.html')
     
    else:
        return render(request, 'lawyer/user_details_form.html', {'available_time_slots': available_time_slots})

# mark Leave #
  
@login_required
def mark_holiday(request):
    user = request.user  # Get the current user

    # Check if the user is a lawyer
    if user.is_authenticated and user.user_type == 'lawyer':
        lawyer_profile = LawyerProfile.objects.get(user=user)  # Get the associated lawyer profile

        if request.method == 'POST':
            holiday_date = request.POST.get('holiday_date')

            # Check if the date is not already marked as a holiday
            if not HolidayRequest.objects.filter(lawyer=user, date=holiday_date).exists():
                # Create a holiday request
                holiday_request = HolidayRequest(lawyer=user, date=holiday_date)
                holiday_request.save()
                messages.success(request, 'Holiday request sent for review.')
            else:
                messages.warning(request, 'This date is already marked as a holiday.')

        # Retrieve holiday requests and their statuses for the logged-in lawyer
        holiday_requests = HolidayRequest.objects.filter(lawyer=user)

        context = {
            'holiday_requests': holiday_requests,
        }
        return render(request, 'lawyer/mark_holiday.html', context)

    else:
        messages.error(request, 'Only lawyers can request holidays.')
        return redirect('home')  # Redirect non-lawyers or unauthenticated users to the home page

# update profile #    

@login_required
def update_profile(request):
    user = request.user

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('client_dashboard')  # Redirect to the user's profile page after updating
    else:
        form = UserProfileUpdateForm(instance=user)

    return render(request, 'client/update_profile.html', {'form': form})


@login_required
def update_lawyer_profile(request, user_id):
    
    if request.user.id != user_id:
        return redirect('home')
    
    print("Reached update_lawyer_profile view")
    user = get_object_or_404(CustomUser, id=user_id)
    lawyer_profile, created = LawyerProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Update user fields if provided in the form, or keep the existing values
        user.address = request.POST.get('address', user.address)
        user.phone = request.POST.get('pin', user.phone)
        
        

        lawyer_profile.specialization = request.POST.get('specialization', lawyer_profile.specialization)
        lawyer_profile.court = request.POST.get('court', lawyer_profile.court)


        # Handle profile_picture file upload
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            lawyer_profile.profile_picture = profile_picture

        # Check if a new profile_picture is provided; otherwise, keep the existing image
        if not profile_picture and lawyer_profile.profile_picture:
            lawyer_profile.profile_picture = lawyer_profile.profile_picture  # Keep the existing image

        user.save()
        lawyer_profile.save()
        return redirect('login')  # Redirect to a success page

    # For GET request, retrieve and display the form
    context = {
        'user': user,
        'lawyer_profile': lawyer_profile,
        
    }

    return render(request, 'lawyer/update_lawyer_profile.html', context)


@login_required
def all_bookings(request, lawyer_id=None, client_id=None):
    # Define a base queryset with all bookings
    queryset = Appointment.objects.all()

    # Filter bookings by lawyer if lawyer_id is provided
    if lawyer_id is not None:
        lawyer = get_object_or_404(LawyerProfile, id=lawyer_id)
        queryset = queryset.filter(lawyer=lawyer)

    # Filter bookings by client if client_id is provided
    if client_id is not None:
        client = get_object_or_404(CustomUser, id=client_id)
        queryset = queryset.filter(client=client)

    # Retrieve payment information for each appointment
    appointments_with_payment = []
    for appointment in queryset:
        try:
            payment = Payment.objects.get(appointment=appointment)
        except Payment.DoesNotExist:
            payment = None
        appointments_with_payment.append({'appointment': appointment, 'payment': payment})

    # Pass the filtered bookings with payment details to the template
    context = {
        'bookings': appointments_with_payment,
    }

    # Render the template
    return render(request, 'bookings.html', context)

# client booking #

@login_required
def client_bookings(request, client_id):
    # Get the client object based on the client_id
    client = get_object_or_404(CustomUser, id=client_id)

    # Retrieve bookings for the specific client
    client_bookings = Appointment.objects.filter(client=client)

    # Pass the filtered bookings to the template
    context = {
        'client': client,
        'client_bookings': client_bookings,
    }

    return render(request, 'client_bookings.html', context)



def list_lawyers(request):
    # Fetch all lawyer profiles from the database
    lawyers = LawyerProfile.objects.all()

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        # Use Q objects to perform a case-insensitive search on concatenated names
        lawyers = lawyers.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )

    # Pagination
    page_number = request.GET.get('page')
    paginator = Paginator(lawyers, 10)  # Show 10 lawyers per page
    page = paginator.get_page(page_number)

    # Pass the lawyer profiles to the template
    context = {
        'lawyers': page,  # Use the paginated lawyers
        'search_query': search_query,
    }

    # Render the template
    return render(request, 'lawyerfulllist.html', context)

@login_required
def admin_view_holiday_requests(request):
    # Check if the user is an admin
    if not request.user.is_superuser:
        return redirect('home')  # Redirect to the home page or any other appropriate page

    # Query all pending holiday requests
    pending_requests = HolidayRequest.objects.filter(status='pending')

    # Render the template with the pending holiday requests data
    return render(request, 'admin/admin_view_holiday_requests.html', {'pending_requests': pending_requests})

@login_required
def admin_approve_reject_holiday(request, request_id):
    if request.method == 'POST':
        # Retrieve the holiday request object by its ID
        holiday_request = get_object_or_404(HolidayRequest, pk=request_id)

        if request.POST['action'] == 'approve':
            # If the admin approves the holiday request, mark it as accepted
            holiday_request.status = 'accepted'
            holiday_request.save()

            # Get the associated lawyer profile
            lawyer_profile = holiday_request.lawyer.lawyer_profile

            # Create a LawyerDayOff instance for the approved holiday
            LawyerDayOff.objects.create(lawyer=lawyer_profile, date=holiday_request.date)
            print("Request ID:", request_id)


            messages.success(request, 'Holiday request approved successfully.')

        elif request.POST['action'] == 'reject':
            # If the admin rejects the holiday request, mark it as rejected
            holiday_request.status = 'rejected'
            holiday_request.save()
            messages.success(request, 'Holiday request rejected successfully.')

    # Redirect back to the admin dashboard or any other appropriate view
    return redirect('admin_dashboard')  # Update this to the appropriate view name

# case registration #

@login_required
def enter_client_email(request):
    if request.user.user_type != 'lawyer':
        return render(request, 'sorry.html')
    
    # Reset the session variable
    request.session['case_submitted'] = False
    
    lawyer = request.user.lawyer_profile  # Access the associated lawyer profile

    if request.method == 'POST':
        client_email = request.POST.get('client_email')
        if client_email:
            try:
                # Assuming CustomUser model is used for clients
                client = CustomUser.objects.get(email=client_email, user_type='client')
                # Redirect to the case details form with the client's details
                return redirect('enter_case_details', client_id=client.id, lawyer_id=lawyer.id)
            except CustomUser.DoesNotExist:
                messages.error(request, 'Client with the provided email not found.')
        else:
            messages.error(request, 'Please enter a valid client email.')

    return render(request, 'lawyer/enter_client_email.html', {'lawyer': lawyer})

@login_required
def enter_case_details(request, client_id, lawyer_id):
    # Ensure that only lawyers can access this view
    if request.user.user_type != 'lawyer':
        return render(request, 'sorry.html')

    client = get_object_or_404(CustomUser, id=client_id, user_type='client')
    lawyer = get_object_or_404(LawyerProfile, id=lawyer_id)

    # Check if the case has already been submitted
    if request.session.get('case_submitted'):
        return render(request, 'case_already_submitted.html')

    if request.method == 'POST':
        incident_place = request.POST.get('incident_place')
        incident_date = request.POST.get('incident_date')
        incident_time = request.POST.get('incident_time')
        witness_name = request.POST.get('witness_name')
        witness_details = request.POST.get('witness_details')
        incident_description = request.POST.get('incident_description')
        client_adhar = request.POST.get('client_adhar')
        client_adhar_photo = request.FILES.get('client_adhar_photo')

        # Validate incident date and time in IST (Indian Standard Time)
        current_datetime = timezone.now()
        ist = pytz.timezone('Asia/Kolkata')  # Get the IST time zone
        current_datetime_ist = current_datetime.astimezone(ist)
        incident_datetime = timezone.datetime.combine(
            timezone.datetime.strptime(incident_date, '%Y-%m-%d').date(),
            timezone.datetime.strptime(incident_time, '%H:%M').time(),
            ist
        )

        if incident_datetime > current_datetime_ist:
            messages.error(request, 'Incident date and time cannot be in the future.')
        elif not all([incident_place, witness_name]):
            messages.error(request, 'Incident place and witness name are required fields.')
        elif not witness_name.replace(" ", "").isalpha():
            messages.error(request, 'Witness name should contain only letters without any numbers or special characters.')
        elif not client_adhar.isdigit() or len(client_adhar) != 12:
            messages.error(request, 'Client Aadhar should contain 12 numeric digits.')
        else:
            # Generate a unique case number
            case_number = generate_unique_case_number()

            # Create a new Case instance and save it
            case = Case.objects.create(
                case_number=case_number,
                client=client,
                client_name=client.get_full_name(),
                client_email=client.email,
                client_phone=client.phone,
                incident_place=incident_place,
                incident_date=incident_date,
                incident_time=incident_time,
                witness_name=witness_name,
                witness_details=witness_details,
                incident_description=incident_description,
                client_adhar=client_adhar,
                client_adhar_photo=client_adhar_photo,
                lawyer=lawyer,  # Assign the lawyer to the case
            )

            # Handle saving the Aadhar card photo file
            if client_adhar_photo:
                file_name = f'aadhar_photos/{case.id}_{client_adhar_photo.name}'
                default_storage.save(file_name, ContentFile(client_adhar_photo.read()))

            # Set the session variable to indicate case submission
            request.session['case_submitted'] = True

            messages.success(request, 'Case saved successfully.')
            return redirect('case_saved')

    return render(request, 'lawyer/enter_case_details.html', {'client': client})
@login_required
def case_saved(request):
    return render(request, 'case_saved.html')

@login_required
def case_detail(request, case_id):
    # Retrieve the case object by its ID or return a 404 error if not found
    case = get_object_or_404(Case, pk=case_id)

    # Retrieve the case tracking data associated with this case
    case_tracking_data = CaseTracking.objects.filter(case=case)

    # Render the 'case_detail.html' template with the case and case tracking data
    return render(request, 'lawyer/case_detail.html', {'case': case, 'case_tracking_data': case_tracking_data})

def generate_unique_case_number():
    # Generate a unique case number like 1001, 1002, ...
    last_case = Case.objects.order_by('-case_number').first()
    if last_case:
        last_case_number = int(last_case.case_number)
        return str(last_case_number + 1)
    else:
        return '1001'
    
    
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# current case #
@login_required
def current_cases(request):
    # Ensure that only lawyers can access this view
    if request.user.user_type != 'lawyer':
        return render(request, 'sorry.html')

    lawyer = request.user.lawyer_profile
    current_case_count = lawyer.current_cases.count()
    max_current_cases = lawyer.currendly_handling

    if request.method == 'POST':
        case_number = request.POST.get('case_number')
        client_name = request.POST.get('client_name')
        incident_description = request.POST.get('incident_description')
        incident_place = request.POST.get('incident_place')
        incident_date = request.POST.get('incident_date')
        incident_time = request.POST.get('incident_time')
        witness_name = request.POST.get('witness_name')
        witness_details = request.POST.get('witness_details')

        # Validate incident date and time
        if not validate_date(incident_date):
            messages.error(request, 'Incident date cannot be in the future.')
        elif not validate_time(incident_time):
            messages.error(request, 'Incident time cannot be in the future.')
        elif not client_name.replace(" ", "").isalpha():
            messages.error(request, 'Client name should contain only letters.')
        elif not witness_name.replace(" ", "").isalpha():
            messages.error(request, 'Witness name should contain only letters.')
        elif current_case_count >= max_current_cases:
            messages.warning(request, 'You have reached the maximum number of current cases.')
        else:
            try:
                CurrentCase.objects.get(case_number=case_number)  # Check if case number is unique
                messages.error(request, 'A case with this number already exists.')
            except ObjectDoesNotExist:
                CurrentCase.objects.create(
                    lawyer=lawyer,
                    case_number=case_number,
                    client_name=client_name,
                    incident_description=incident_description,
                    incident_place=incident_place,
                    incident_date=incident_date,
                    incident_time=incident_time,
                    witness_name=witness_name,
                    witness_details=witness_details,
                )
                messages.success(request, 'Current case added successfully.')
                return redirect('current_cases')

    current_cases = lawyer.current_cases.all()

    context = {
        'lawyer': lawyer,
        'current_cases': current_cases,
        'current_case_count': current_case_count,
        'max_current_cases': max_current_cases
    }
    
    return render(request, 'lawyer/current_cases.html', context)

def list_cases(request):
    user_type = request.user.user_type  # Assuming you have 'user_type' set in your CustomUser model
    
    if user_type == 'lawyer':
        cases = Case.objects.filter(lawyer=request.user.lawyer_profile)
    elif user_type == 'client':
        cases = Case.objects.filter(client=request.user)
    elif user_type == 'admin':
        cases = Case.objects.all()
    else:
        cases = None

    return render(request, 'case_list.html', {'cases': cases})


def search_lawyers(request):
    # Get the search query from the form
    query = request.GET.get('query')

    # Filter lawyers based on the search query (you can modify the filter condition)
    lawyers = LawyerProfile.objects.filter(
        models.Q(user__first_name__icontains=query) |  # Search by first name
        models.Q(user__last_name__icontains=query) |   # Search by last name
        models.Q(specialization__icontains=query)      # Search by specialization
    )

    # Pass the search results to the template
    return render(request, 'search.html', {'lawyers': lawyers, 'query': query})

# working hours #

@login_required
def assign_working_hours(request):
    if request.method == 'POST':
        print("Received a POST request")  # Debugging: Check if the request is received

        selected_time_slot_ids = request.POST.getlist('selected_time_slots')
        selected_time_slots = TimeSlot.objects.filter(id__in=selected_time_slot_ids)

        try:
            if request.user.is_authenticated and hasattr(request.user, 'lawyer_profile'):
                lawyer = request.user.lawyer_profile

                print(f"User {request.user.username} is authenticated and has a lawyer profile")  # Debugging: Check user profile

                # Clear existing working slots for the lawyer
                lawyer.working_slots.clear()
                lawyer.time_update = datetime.now()
                lawyer.save()  # Save the lawyer object to persist changeslawyer.time_update = datetime.now()

                # Add the selected time slots to the lawyer's working slots
                lawyer.working_slots.set(selected_time_slots)

                print("Working slots assigned successfully")  # Debugging: Check if slots are assigned successfully
                print("Selected slot IDs:", [slot.id for slot in selected_time_slots])  # Debugging: Check selected slot IDs

                # Check if the lawyer has selected at least one slot a day for a minimum of four days
                if validate_working_hours(selected_time_slots):
                    # Redirect to the dashboard or another page
                    return redirect('update')
                else:
                    messages.error(request, 'Please atlest take any 4 days slot.')
        except Exception as e:
            # Log the error
            traceback.print_exc()
            return HttpResponseServerError("An error occurred while saving data.")

    # Retrieve all available time slots to display in the form
    all_time_slots = TimeSlot.objects.all()
    
    # Check if the user is authenticated and has a lawyer profile
    if request.user.is_authenticated and hasattr(request.user, 'lawyer_profile'):
        lawyer = request.user.lawyer_profile
        selected_time_slot_ids = lawyer.working_slots.values_list('id', flat=True)
    else:
        selected_time_slot_ids = []

    breadcrumbs = [
        ("Home", reverse("home")),
        ("lawyer_dashboard", reverse("lawyer_dashboard")),
        ("assign_working_hours", None),  # Current page (no link)
    ]

    return render(request, 'assign_working_hours.html', {'all_time_slots': all_time_slots ,'breadcrumbs': breadcrumbs ,'selected_time_slot_ids': selected_time_slot_ids})

def validate_working_hours(selected_time_slots):
    # Create a dictionary to count slots for each day
    day_slot_count = {}

    for slot in selected_time_slots:
        day = slot.day  # Assuming you have a 'day_of_week' attribute for each TimeSlot
        if day in day_slot_count:
            day_slot_count[day] += 1
        else:
            day_slot_count[day] = 1

    # Check if at least one slot is selected for each day of the week for a minimum of four days
    days_with_slots = [day for day, count in day_slot_count.items() if count > 0]
    return len(days_with_slots) >= 4
    


@login_required
def select_date(request, lawyer_id):
    # Retrieve the lawyer using the lawyer_id parameter
    lawyer = get_object_or_404(LawyerProfile, id=lawyer_id)
    
    if request.method == 'POST':
        selected_date = request.POST.get('selected_date')
        
        # Check if it's a holiday for the lawyer
        if LawyerDayOff.objects.filter(lawyer=lawyer, date=selected_date).exists():
            messages.error(request, 'Booking is not possible on a day marked as a holiday for the lawyer.')
        else:
            # Check if the selected_date is within 7 days from the last update
            if not lawyer.is_within_7_days(datetime.strptime(selected_date, '%Y-%m-%d').date()):
                messages.error(request, 'Booking is only possible within 14 days from the last update of working hours.')
            else:
                return redirect('book_lawyer', lawyer_id=lawyer_id, selected_date=selected_date)
    
    return render(request, 'select_date.html', {'lawyer': lawyer })

def parse_time(time_str):
    try:
        # Parse the time string in the format "08:00 AM"
        parsed_time = datetime.strptime(time_str, '%I:%M %p').strftime('%H:%M:%S')
        return parsed_time
    except ValueError:
        return None

# book lawyer date and payment #

@login_required
def book_lawyer(request, lawyer_id, selected_date):
    try:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        current_date = datetime.now().date()

        if selected_date < current_date:
            messages.error(request, 'Booking is not possible for past dates.')
            return redirect('home')

        lawyer = LawyerProfile.objects.get(id=lawyer_id)
        working_time_slots = TimeSlot.objects.filter(
            lawyers=lawyer,
            day=selected_date.strftime('%A')
        ).order_by('start_time')

        appointment_slots = []

        for time_slot in working_time_slots:
            start_time = datetime.combine(selected_date, time_slot.start_time)
            end_time = datetime.combine(selected_date, time_slot.end_time)

            current_time = start_time
            while current_time <= end_time:
                appointment_slots.append(current_time.strftime('%I:%M %p'))
                current_time += timedelta(minutes=15)

        if request.method == 'POST':
            selected_slot = request.POST.get('selected_slot')

            if not lawyer.is_within_7_days(selected_date):
                return HttpResponseBadRequest("Selected date is not within 7 days from the last update.")

            if selected_slot and selected_slot in appointment_slots:
                try:
                    selected_time = datetime.strptime(selected_slot, '%I:%M %p').time()
                except ValueError:
                    messages.error(request, 'Invalid time format. Please choose a valid time from the list (e.g., 08:45 AM).')
                    return render(request, 'book_lawyer.html', {'selected_date': selected_date, 'appointment_slots': appointment_slots})

                appointment = Appointment(
                    lawyer=lawyer,
                    client=request.user,
                    appointment_date=selected_date,
                    time_slot=selected_time
                )
                appointment.save()

                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

                order_amount = 10000  # Amount in paise (Change as needed)
                order_currency = 'INR'
                order_payload = {
                    'amount': order_amount,
                    'currency': order_currency,
                    'notes': {
                        'appointment_id': appointment.id,
                    },
                    'payment_capture': "1"
                }
                order = client.order.create(data=order_payload)

                appointment.order_id = order.get('id')
                appointment.save()

                return render(
                    request,
                    "razorpay_payment.html",
                    {
                        "callback_url": "http://" + "127.0.0.1:8000" + f"/callback/{appointment.id}/",
                        "razorpay_key": "rzp_test_QtI3zIbpa2Kcyl",
                        "order": order,
                        'appointment': appointment,
                        'lawyer_id': lawyer_id,
                        'selected_date': selected_date,
                    },
                )
            else:
                messages.error(request, 'Selected slot is not available. Please choose another slot.')
        return render(request, 'book_lawyer.html', {'selected_date': selected_date, 'appointment_slots': appointment_slots})
    except LawyerProfile.DoesNotExist:
        messages.error(request, 'Lawyer not found.')
        return redirect('home')

# Define the verify_signature function
def verify_signature(response_data):
    client = razorpay.Client(auth=("rzp_test_QtI3zIbpa2Kcyl", "TGxT70N3Nw3Si5Ys3RF5MpY0"))
    return client.utility.verify_payment_signature(response_data)

@csrf_exempt
def callback(request, appointment_id):
    if request.method == 'POST':
        try:
            razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            razorpay_signature = request.POST.get('razorpay_signature', '')

            is_signature_valid = verify_signature({
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_order_id': razorpay_order_id,
                'razorpay_signature': razorpay_signature,
            })

            if is_signature_valid:
                try:
                    appointment = Appointment.objects.get(id=appointment_id)
                    payment = Payment(order_id=razorpay_order_id, appointment=appointment)
                    payment.status = PaymentStatus.SUCCESS
                    payment.razorpay_payment_id = razorpay_payment_id
                    payment.razorpay_signature = razorpay_signature
                    payment.save()

                    return render(request, 'payment_confirmation.html', {'appointment': appointment})
                except Appointment.DoesNotExist:
                    return JsonResponse({"error": "Appointment not found"}, status=404)
            else:
                return JsonResponse({"status": "failure"})

        except Exception as e:
            logger.error(f"Error in Razorpay callback: {str(e)}")
            return JsonResponse({"error": "An error occurred during payment processing"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

# intern details #

def intern(request):
    if request.method == 'POST':
        # Assuming all these fields are present in your HTML form
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']  # Updated field name
        phnno = request.POST['phone']
        dob = request.POST['dob']
        address = request.POST['address']
        course = request.POST['course']
        course_place = request.POST['course_place']  # Updated field name
        duration_of_course = request.POST['duration_of_course']  # Updated field name
        specialization = request.POST['specialization']  # Updated field name
        year_of_pass = request.POST['year_of_pass']  # Updated field name
        cgpa = request.POST['cgpa']
        experience = request.POST['experience']
        adhaar_no = request.POST['adhaar_no']  # Updated field name
        pic_of_aadhaar = request.FILES['adhaar_pic']  # Assuming it's a file input
        
        # Check if the email is already in use
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'student/intern.html')
        # Check if the email is already in use
        if Student.objects.filter(adhaar_no=adhaar_no).exists():
            messages.error(request, 'Adhar Number already exists.')
            return render(request, 'student/intern.html')
        
         # Check if the email is already in use
        if CustomUser.objects.filter(phone=phnno).exists():
            messages.error(request, 'Phone already exists.')
            return render(request, 'student/intern.html')
        
        # Check if phnno contains only numeric digits
        if not re.match("^[0-9]+$", phnno):
            messages.error(request, 'Phone should only contain numeric digits.')
            return render(request, 'student/intern.html')
        
        # Calculate age based on the provided DOB
        try:
            dob_date = date.fromisoformat(dob)
            today = date.today()
            age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
            return render(request, 'student/intern.html')

        # Check if the age is less than 18
        if age < 18:
            messages.error(request, 'You must be at least 18 years old to sign up.')
            return render(request, 'student/intern.html')
            
        

        # Create a new CustomUser instance
        user = CustomUser.objects.create_user(username=email,email=email)
        user.first_name = first_name
        user.last_name = last_name
        user.phone = phnno
        user.dob = dob
        user.address = address
        user.user_type='student'
        user.save()
        
        # user = CustomUser.objects.create_user(
        #     username=email,
        #     email=email,
        #     user_type='lawyer',
        #     first_name=first_name,
        #     last_name=last_name,
        #     phone = phone,
        # )

        # Create a new Student instance and link it to the CustomUser
        student = Student.objects.create(user=user)
        student.course = course  # Updated field name
        student.course_place = course_place
        student.duration_of_course = duration_of_course
        student.specialization = specialization
        student.year_of_pass = year_of_pass
        student.cgpa = cgpa
        student.experience = experience
        student.adhaar_no = adhaar_no
        student.adhaar_pic = pic_of_aadhaar
        student.save()
        return render(request,'application_successful.html')  # Replace 'success_page' with your actual success page URL

        
    return render(request, 'student/intern.html')  # Replace 'intern_form.html' with your actual template name


User = get_user_model()

@login_required
def approve_student(request, student_id):
    if not request.user.user_type == 'admin':
        return render(request, '404.html')
    
    try:
        student = Student.objects.get(id=student_id)
        student.is_approved = True
        student.save()
        
        # Send an email to the approved student with a link to set the password
        subject = 'Welcome to Our Platform'
        from_email = 'your_email@gmail.com'  # Change to your email
        recipient_list = [student.user.email]
        
        # Create a unique password reset link
        uid = urlsafe_base64_encode(force_bytes(student.user.pk))
        token = default_token_generator.make_token(student.user)
        password_reset_url = f'http://127.0.0.1:8000/accounts/set_password/{uid}/{token}/'
        
        context = {
            'user': student.user,
            'password_reset_url': password_reset_url,
        }
        
        html_message = render_to_string('password_reset_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
        
        return redirect('list_student_requests')
    except Student.DoesNotExist:
        return render(request, '404.html')

@login_required
def reject_student(request, student_id):
    if not request.user.user_type == 'admin':
        return render(request, '404.html')
    
    try:
        student = Student.objects.get(id=student_id)
        student.delete()  # You can choose to delete the student's record or mark them as rejected
        student.user.delete()
        
        
        # Send a rejection email to the student
        subject = 'Application Status: Rejected'
        from_email = 'your_email@gmail.com'  # Change to your email
        recipient_list = [student.user.email]
        
        context = {
            'user': student.user,
        }
        
        html_message = render_to_string('rejection_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
        
        return redirect('list_student_requests')
    except Student.DoesNotExist:
        return render(request, '404.html')

@login_required
def list_student_requests(request):
    if not request.user.user_type == 'admin':
        return render(request, '404.html')
    
    # Get all student requests
    student_requests = Student.objects.filter(is_approved=False)
    
    # Determine which students are eligible for approval
    eligible_students = [student for student in student_requests if student.cgpa is not None and student.cgpa >= 7.5]
    
    # Determine which students need to be rejected
    rejected_students = [student for student in student_requests if student.cgpa is not None and student.cgpa < 7.5]

    
    context = {
        'eligible_students': eligible_students,
        'rejected_students': rejected_students,
    }
    
    return render(request, 'admin/list_student_requests.html', context)


def password_reset_confirm_student(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('login')  # Redirect to the login page after a successful reset
        else:
            form = SetPasswordForm(user)

        return render(request, 'password_reset_confirm_student.html', {'form': form})
    else:
        return render(request, '404.html')

# pdf generator #
    
def generate_appointment_pdf(request, appointment_id):
    # Get the appointment object from the database
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Access the related Payment object for this appointment
    payment = Payment.objects.get(appointment=appointment)

    # Prepare context data to be passed to the template
    context = {
        'appointment': appointment,
        'payment': payment,
        'client_name': f"{appointment.client.first_name} {appointment.client.last_name}",
        'client_address': appointment.client.address,
        'client_email': appointment.client.email,
        'lawyer_name': f"{appointment.lawyer.user.first_name} {appointment.lawyer.user.last_name}",
        'appointment_date': appointment.appointment_date,
        'appointment_id': appointment.id,
        'appointment_time': appointment.time_slot,
        'amount': '100 INR',  # You can fetch this dynamically if needed
    }

    # Render the HTML template with the context
    template = get_template('receipt.html')
    html = template.render(context)

    # Convert the HTML content to bytes using UTF-8 encoding
    html_bytes = html.encode('UTF-8')

    # Create a BytesIO buffer to receive the PDF data
    buffer = BytesIO()

    # Create the PDF file
    pdf = pisa.pisaDocument(BytesIO(html_bytes), buffer)

    if not pdf.err:
        # Set the response content type and filename
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="appointment_{appointment.id}.pdf'

        # Get the value of the BytesIO buffer and add it to the response
        pdf_data = buffer.getvalue()
        buffer.close()
        response.write(pdf_data)

        return response

    return HttpResponse('PDF generation error')


def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    context = {
        'student': student,
    }
    return render(request, 'student_detail.html', context)


# case tracker #

def add_case_update(request, case_number):
    # Retrieve the corresponding Case object based on the case_number
    case = get_object_or_404(Case, case_number=case_number)

    if request.method == 'POST':
        # Extract form data from request.POST
        activity = request.POST.get('activity')
        description = request.POST.get('description')
        date = request.POST.get('date')
        
        # Create a new CaseUpdate object associated with the Case
        case_update = CaseTracking.objects.create(
            case=case,
            activity=activity,
            description=description,
            date=date
        )
        
        # Save the case update
        case_update.save()
        
        # Redirect to the case detail page
        return redirect('list_cases')
    
    return render(request, 'add_case_update_form.html', {'case': case})

# unassigned student #

def unassigned_students(request):
    unassigned_students = Student.objects.filter(is_approved=True, lawyer__isnull=True)
    return render(request, 'unassigned_students.html', {'unassigned_students': unassigned_students})

# hire student #

def hire_student(request, student_id):
    if request.method == 'POST':
        student = Student.objects.get(id=student_id)

        # Check if the student is already hired
        if student.lawyer:
            messages.error(request, 'This student is already hired.')
        else:
            # Assign the lawyer to the student
            student.lawyer = request.user.lawyer_profile
            student.save()
            messages.success(request, f'You have hired {student.user.first_name} {student.user.last_name}.')

    return redirect('unassigned_students')

# assign work #

def assign_work(request):
    # Get the currently logged-in lawyer
    current_lawyer = request.user.lawyer_profile

    # Query students who are hired by the current lawyer
    hired_students = Student.objects.filter(lawyer=current_lawyer, is_approved=True)

    # Query cases associated with the current lawyer
    lawyer_cases = Case.objects.filter(lawyer=current_lawyer)

    if request.method == 'POST':
        description = request.POST.get('description')
        deadline_date = request.POST.get('deadline_date')
        student_id = request.POST.get('student_id')
        case_id = request.POST.get('case_id')  # Get the selected case (optional)

        try:
            # Check if the student_id exists and is eligible for work assignment
            student = Student.objects.get(id=student_id, is_approved=True, lawyer=current_lawyer)
        except Student.DoesNotExist:
            return render(request, 'assign_work.html', {'error_message': 'Invalid student selection'})

        # Create a new WorkAssignment object and assign it to the current lawyer
        work_assignment = WorkAssignment(
            description=description,
            deadline_date=deadline_date,
            student=student,
            case_id=case_id  # Assign the selected case (optional)
        )
        work_assignment.save()
        
        # Redirect to a success page or another appropriate view
        return render(request, 'work_assigned.html')

    context = {
        'hired_students': hired_students,
        'lawyer_cases': lawyer_cases,
    }

    return render(request, 'assign_work.html', context)



@login_required
def student_work_assignments(request):
    if request.user.user_type != 'student':
        # Redirect to an appropriate page or display an error message
        # because only students are allowed to access this view.
        return render(request, '404.html')

    # Retrieve work assignments for the current student
    student = request.user.student_profile
    work_assignments = WorkAssignment.objects.filter(student=student)

    return render(request, 'student_work_assignments.html', {'work_assignments': work_assignments})