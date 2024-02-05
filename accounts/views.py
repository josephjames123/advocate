# accounts/views.py
from calendar import monthrange
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect ,get_object_or_404 ,HttpResponseRedirect
from django.urls import reverse
from .models import CustomUser, LawyerProfile , CurrentCase, StudentPayment  
from django.http import HttpResponseForbidden , Http404,HttpResponseNotFound , HttpResponse ,HttpResponseBadRequest
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
# from django.contrib.auth.forms import SetPasswordForm
from .forms import CustomPasswordResetForm, LeaveReportsFilterForm, LeaveRequestForm, TaskForm  
from django.core.exceptions import ValidationError
from datetime import datetime
from .models import LawyerProfile , ContactEntry , Internship , Task , Student , Application , Booking , Day ,TimeSlot , LawyerDayOff , HolidayRequest , Case ,Appointment , CaseTracking , WorkAssignment , Payment
from .forms import ContactForm , BookingForm , InternshipForm , BookingStatusForm ,CustomUserUpdateForm, LawyerProfileUpdateForm
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
from django.db.models import Q, F, Value, CharField
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
from twilio.rest import Client
import random



logger = logging.getLogger(__name__)

# # Replace these with your Twilio credentials
# TWILIO_ACCOUNT_SID = 'AC30860f145a25bb1043dafe33140671ac'
# TWILIO_AUTH_TOKEN = 'e8b78caf7b9f27f25c5fae1791abf5b7'
# TWILIO_PHONE_NUMBER = '+447360273978'

# def send_otp_via_twilio(phone_number, otp):
#     # Twilio client setup
#     client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

#     # Replace 'your_twilio_phone_number' with the Twilio phone number you've purchased
#     message = client.messages.create(
#         body=f'Your OTP is: {otp}',
#         from_=TWILIO_PHONE_NUMBER,
#         to=phone_number
#     )


def login_view(request):
    if request.user.is_authenticated:
        user = request.user  # Get the authenticated user
        if user.user_type == 'admin':
            return redirect(reverse('admin_dashboard'))
        elif user.user_type == 'client':
            return redirect(reverse('home'))
        elif user.user_type == 'lawyer':
            # # Assuming you have a one-to-one relationship between CustomUser and LawyerProfile
            # lawyer_profile = LawyerProfile.objects.get(user=user)
            # # if lawyer_profile.time_update is None or (timezone.now() - lawyer_profile.time_update).days > 14:
            # # Assuming lawyer_profile.time_update is a datetime object
            # if lawyer_profile.time_update:
            #     print(lawyer_profile.time_update)  # Check the entire datetime object
            #     print(lawyer_profile.time_update.month)
            # else:
            #     print("lawyer_profile.time_update is None or not a valid datetime object.")
            # if lawyer_profile.time_update is None or lawyer_profile.time_update.month != timezone.now().month:
            #     return redirect(reverse('assign_working_hours'))
            # else:
            return redirect(reverse('lawyer_dashboard'))
        elif user.user_type == 'student':
            return redirect(reverse('student_dashboard'))
    
    if request.method == 'POST':
        email = request.POST['email']  # Change this to 'email'
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if user.user_type == 'admin':
                return redirect(reverse('admin_dashboard'))
            elif user.user_type == 'client':
                return redirect(reverse('client_dashboard'))
            elif user.user_type == 'lawyer':
            # # Assuming you have a one-to-one relationship between CustomUser and LawyerProfile
            #     lawyer_profile = LawyerProfile.objects.get(user=user)
            #     # if lawyer_profile.time_update is None or (timezone.now() - lawyer_profile.time_update).days > 14:
            #     if lawyer_profile.time_update:
            #         print(lawyer_profile.time_update) 
            #         print(lawyer_profile.time_update.month)
            #     else:
            #         print("lawyer_profile.time_update is None or not a valid datetime object.")
            #     if lawyer_profile.time_update is None or lawyer_profile.time_update.month != timezone.now().month:
            #         return redirect(reverse('assign_working_hours'))
            #     else:
                return redirect(reverse('lawyer_dashboard'))
            elif user.user_type == 'student':
                return redirect(reverse('student_dashboard'))
        else:
            messages.error(request, 'Invalid email or password. Please try again')
    
    return render(request, 'login.html')

def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp(phone_number, otp):
    phone_number_with_country_code = '+91' + phone_number
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    try:
        message = client.messages.create(
            to=phone_number_with_country_code,
            from_=settings.TWILIO_PHONE_NUMBER,
            body=f'Your OTP is: {otp}'
        )
        print(message.sid) 
    except Exception as e:
        print(f"Error sending OTP: {e}")

def login_otp(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')

        if not phone_number:
            messages.error(request, 'Phone number is required.')
            return render(request, 'login/login_via_otp.html')

        phone_number = phone_number.replace(" ", "")
        if len(phone_number) != 10 or not phone_number.isdigit():
            messages.error(request, 'Invalid phone number.')
            return render(request, 'login/login_via_otp.html')

        # Generate and send OTP
        otp = generate_otp()
        send_otp(phone_number, otp)

        # Save OTP and phone number in session for verification
        request.session['login_otp'] = otp
        request.session['login_phone'] = phone_number

        return redirect('otp_verification')  # Redirect to the OTP verification page

    return render(request, 'login/login_via_otp.html')

def otp_verification(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('entered_otp')
        stored_otp = request.session.get('login_otp')
        phone_number = request.session.get('login_phone')
        
        print(f"Entered OTP: {entered_otp}")
        print(f"Stored OTP: {stored_otp}")
        print(f"Phone Number: {phone_number}")

        if entered_otp == stored_otp:
            print("Entered authentication")
            User = get_user_model()
            user = authenticate(request, phone=phone_number)  # No need to provide a password

            if user:
                login(request, user)
                print("User authenticated and logged in:", user)
                
                if user.user_type == 'admin':
                    return redirect(reverse('admin_dashboard'))
                elif user.user_type == 'client':
                    return redirect(reverse('client_dashboard'))
                elif user.user_type == 'lawyer':
                    # Assuming you have a one-to-one relationship between CustomUser and LawyerProfile
                    lawyer_profile = LawyerProfile.objects.get(user=user)
                    if lawyer_profile.time_update is None or lawyer_profile.time_update.month != timezone.now().month:
                        return redirect(reverse('assign_working_hours'))
                    else:
                        return redirect(reverse('lawyer_dashboard'))
                elif user.user_type == 'student':
                    return redirect(reverse('student_dashboard'))
            else:
                messages.error(request, 'Invalid OTP. Please try again')

    return render(request, 'login/otp_verification.html')

# def otp_verification(request):
#     if request.method == 'POST':
#         entered_otp = request.POST.get('otp', '')
#         stored_otp = request.session.get('otp', '')
#         user_id = request.session.get('user_id', '')

#         if entered_otp == stored_otp and user_id:
#             # Clear session data
#             del request.session['otp']
#             del request.session['user_id']

#             # Log in the user
#             user = CustomUser.objects.get(pk=user_id)
#             login(request, user)

#             if user.user_type == 'admin':
#                 return redirect(reverse('admin_dashboard'))
#             elif user.user_type == 'client':
#                 return redirect(reverse('client_dashboard'))
#             elif user.user_type == 'lawyer':
#                 # Assuming you have a one-to-one relationship between CustomUser and LawyerProfile
#                 lawyer_profile = LawyerProfile.objects.get(user=user)
#                 if lawyer_profile.time_update is None or (timezone.now() - lawyer_profile.time_update).days > 14:
#                     return redirect(reverse('assign_working_hours'))
#                 else:
#                     return redirect(reverse('lawyer_dashboard'))
#             elif user.user_type == 'student':
#                 return redirect(reverse('student_dashboard'))
#         else:
#             messages.error(request, 'Invalid OTP. Please try again.')

#     return render(request, 'otp_verification.html')
    

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
        user_type = request.POST['user_type']

        # Check if any field is empty
        if not (email and password and first_name and last_name  and address and dob and pin and state and phone and user_type):
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
            user_type=user_type,
        )
        return redirect('login')

    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def dashboard_view(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html', {'user': request.user})
    else:
        return redirect('login')
    
@login_required
def admin_dashboard(request):
    if request.user.user_type == 'admin':
        # Calculate the number of lawyers
        lawyer_count = LawyerProfile.objects.count()
        booking_count = Booking.objects.count()
        internship_count = Internship.objects.count()
        students_count = Student.objects.count()
        cases_count = Case.objects.count()
        
        
        # Retrieve the recent 5 bookings, ordered by pk in descending order (greatest to smallest)
        recent_bookings = Booking.objects.order_by('-pk')[:5]
        recent_queries = ContactEntry.objects.order_by('-pk')[:5]
        
        context = {
            'user': request.user,
            'lawyer_count': lawyer_count,
            'booking_count': booking_count,
            'internship_count': internship_count,
            'students_count': students_count,
            'cases_count': cases_count,
            'recent_bookings': recent_bookings,
            'recent_queries': recent_queries,
}

            
        
        return render(request, 'admin/dashboard.html', context)
    else:
        return render(request, '404.html')
@login_required
def client_dashboard(request):
    user = request.user

    # Get all bookings by the client
    all_bookings = Appointment.objects.filter(client=user)


    context = {
        'all_bookings': all_bookings,
    }

    return render(request, 'client/dashboard.html', context)


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
        
        # Retrieve students associated with the lawyer
        students = lawyer_profile.student_set.all()
        
        # Count the number of students
        student_count = students.count()

        # Count the number of bookings for this lawyer
        booking_count = Booking.objects.filter(lawyer=lawyer_profile).count()
        case_count = Case.objects.filter(lawyer=lawyer_profile).count()
        current_month = timezone.now().month
        time_update = lawyer_profile.time_update  

        context = {
            'user': request.user,
            'booking_count': booking_count,
            'bookings': bookings,
            'case_count': case_count,
            'current_month': current_month,
            'time_update': time_update,
            'student_count':student_count
        }

        return render(request, 'lawyer/dashboard.html', context)
    else:
        return render(request, '404.html')


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
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the form data to the database
            contact_entry = ContactEntry(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message']
            )
            contact_entry.save()

            # Redirect to a thank you page or the same page with a success message
            return submit(request)
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})

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

@login_required
def booking_details(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)

    # Check if the user making the request is the lawyer associated with the booking
    if request.user == booking.lawyer.user:
        if request.method == 'POST':
            form = BookingStatusForm(request.POST, instance=booking)
            if form.is_valid():
                # Debugging: Print the status before saving
                print("Status before saving:", booking.status)

                form.save()

                # Debugging: Print the status after saving
                print("Status after saving:", booking.status)

                # Redirect to a success page or display a success message
                return redirect('lawyer_dashboard')  # Replace 'success_page' with your actual success page URL

        else:
            form = BookingStatusForm(instance=booking)

        return render(request, 'booking_details.html', {'booking': booking, 'form': form})

    # If the user making the request is not the booking's lawyer, deny access
    else:
        # You can customize this part to display an error message or redirect to an error page
        return render(request, 'sorry.html')

@login_required
def internship_detail(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id)
    roles_html = markdown.markdown(internship.roles)
    student = Student.objects.get(user=request.user)
    # Print statements for debugging
    print("Student Lawyer:", student.lawyer)
    print("Student CGPA:", student.cgpa)
    print("Internship Minimum CGPA:", internship.min_cgpa)

    if request.method == 'POST':
        if request.user.user_type == 'student':
            application, created = Application.objects.get_or_create(internship=internship, student=student)
            if created:
                messages.success(request, 'Application submitted successfully.')
            else:
                messages.warning(request, 'You have already applied to this internship.')

            return redirect('internship_detail', internship_id=internship_id)

    return render(request, 'student/internship_detail.html', {'internship': internship, 'roles_html': roles_html , 'student': student})

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

@login_required
def student_dashboard(request):
    if request.user.is_authenticated and request.user.user_type == 'student':
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return render(request, 'student/student_details.html')  

        if student.is_approved:
            if student.course and student.cgpa is not None:
                work_assignment_count = WorkAssignment.objects.filter(student=student).count()
                
                recent_internships = Internship.objects.order_by('-pk')[:5]

                return render(request, 'student/dashboard.html', {
                    'user': request.user,
                    'recent_internships': recent_internships,
                    'work_assignment_count': work_assignment_count,  
                })
            else:
                return render(request, 'student/student_details.html')

        else:
            return render(request, 'student/not_approved.html')

    return render(request, '404.html')

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
    
@login_required
def mark_holiday(request):
    user = request.user  

    if user.is_authenticated and user.user_type == 'lawyer':
        lawyer_profile = LawyerProfile.objects.get(user=user)  

        if request.method == 'POST':
            holiday_date = request.POST.get('holiday_date')
            reason = request.POST.get('reason')
            supportingdocuments = request.POST.get('supportingdocuments')
            
            holiday_type = 'dutyleave'


            if not HolidayRequest.objects.filter(lawyer=user, date=holiday_date).exists():
                holiday_request = HolidayRequest(lawyer=user, date=holiday_date,reason = reason,supporting_documents=supportingdocuments,type=holiday_type)
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
        return redirect('home')  

    

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
        user.address = request.POST.get('address', user.address)
        user.phone = request.POST.get('pin', user.phone)
        
        lawyer_profile.specialization = request.POST.get('specialization', lawyer_profile.specialization)
        lawyer_profile.court = request.POST.get('court', lawyer_profile.court)
        lawyer_profile.additional_qualification = request.POST.get('additional_qualification', lawyer_profile.additional_qualification)

        # Handle profile_picture file upload
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            lawyer_profile.profile_picture = profile_picture

        # Check if a new profile_picture is provided; otherwise, keep the existing image
        if not profile_picture and lawyer_profile.profile_picture:
            lawyer_profile.profile_picture = lawyer_profile.profile_picture  # Keep the existing image

        # Handle additional_qualification_documents file upload
        additional_qualification_documents = request.FILES.get('additional_qualification_documents')
        if additional_qualification_documents:
            lawyer_profile.additional_qualification_documents = additional_qualification_documents
            
        user.save()
        lawyer_profile.save()
        return redirect('home')  # Redirect to a success page

    # For GET request, retrieve and display the form
    context = {
        'user': user,
        'lawyer_profile': lawyer_profile,
        
    }

    return render(request, 'lawyer/update_lawyer_profile.html', context)

# @login_required
# def all_bookings(request, lawyer_id=None, client_id=None):
#     # Define a base queryset with all bookings
#     queryset = Appointment.objects.all()

#     # Filter bookings by lawyer if lawyer_id is provided
#     if lawyer_id is not None:
#         lawyer = get_object_or_404(LawyerProfile, id=lawyer_id)
#         queryset = queryset.filter(lawyer=lawyer)

#     # Filter bookings by client if client_id is provided
#     if client_id is not None:
#         client = get_object_or_404(CustomUser, id=client_id)
#         queryset = queryset.filter(client=client)

#     # Pass the filtered bookings to the template
#     context = {
#         'bookings': queryset,
#     }

#     # Render the template
#     return render(request, 'bookings.html', context)


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

    # Pagination
    page_number = request.GET.get('page')
    paginator = Paginator(lawyers, 10)  # Show 10 lawyers per page
    page = paginator.get_page(page_number)

    # Pass the lawyer profiles to the template
    context = {
        'lawyers': page,  # Use the paginated lawyers
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
        # Fetch cases for the lawyer
        cases = Case.objects.filter(lawyer=request.user.lawyer_profile)

        # Fetch work assignments and tasks for each case
        for case in cases:
            case.work_assignments = WorkAssignment.objects.filter(case=case)
            for work_assignment in case.work_assignments:
                work_assignment.tasks = Task.objects.filter(work_assignment=work_assignment)
    elif user_type == 'client':
        cases = Case.objects.filter(client=request.user)
    elif user_type == 'admin':
        cases = Case.objects.all()
        
        # Fetch work assignments and tasks for each case
        for case in cases:
            case.work_assignments = WorkAssignment.objects.filter(case=case)
            for work_assignment in case.work_assignments:
                work_assignment.tasks = Task.objects.filter(work_assignment=work_assignment)
    else:
        cases = None

    return render(request, 'case_list.html', {'cases': cases})


def view_tasks_for_assignment(request, work_assignment_id):
    # Fetch the WorkAssignment object based on the work_assignment_id
    work_assignment = get_object_or_404(WorkAssignment, pk=work_assignment_id)
    
    # Fetch tasks for the work assignment
    tasks = Task.objects.filter(work_assignment=work_assignment)

    return render(request, 'case_list.html', {'work_assignment': work_assignment, 'tasks': tasks})


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
    


# @login_required
# def select_date(request, lawyer_id):
#     # Retrieve the lawyer using the lawyer_id parameter
#     lawyer = get_object_or_404(LawyerProfile, id=lawyer_id)
    
#     if request.method == 'POST':
#         selected_date = request.POST.get('selected_date')
        
#         # Check if it's a holiday for the lawyer
#         if LawyerDayOff.objects.filter(lawyer=lawyer, date=selected_date).exists():
#             messages.error(request, 'Booking is not possible on a day marked as a holiday for the lawyer.')
#         else:
#             selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()

#             if lawyer.time_update.month != selected_date_obj.month:
#                 messages.error(request, 'Booking is only possible when the selected date is in the same month as the last update of working hours.')
#             # Check if the selected_date is within 7 days from the last update
#             # if not lawyer.is_within_7_days(datetime.strptime(selected_date, '%Y-%m-%d').date()):
#             #     messages.error(request, 'Booking is only possible within 14 days from the last update of working hours.')
#             else:
#                 return redirect('book_lawyer', lawyer_id=lawyer_id, selected_date=selected_date)
    
#     return render(request, 'select_date.html', {'lawyer': lawyer })


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
            selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()

            if lawyer.time_update.month != selected_date_obj.month:
                messages.error(request, 'Booking is only possible when the selected date is in the same month as the last update of working hours.')
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
                        "razorpay_key": 'rzp_test_cvGs8NAQTlqQrP',
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
    client = razorpay.Client(auth=("rzp_test_cvGs8NAQTlqQrP", "hNPvcoyR5F1mKYlgG60C2GW6"))
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

def intern(request):
    cgpa = request.session.get('cgpa', '')
    course = request.session.get('course', '')


    if request.method == 'POST':
        # Retrieve form data
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phnno = request.POST['phone']
        dob = request.POST['dob']
        address = request.POST['address']
        course_place = request.POST['course_place']
        duration_of_course = request.POST['duration_of_course']
        specialization = request.POST['specialization']
        year_of_pass = request.POST['year_of_pass']
        experience = request.POST['experience']
        adhaar_no = request.POST['adhaar_no']
        pic_of_aadhaar = request.FILES['adhaar_pic']
        cgpa = request.session.get('cgpa', '')
        course = request.session.get('course', '')

        # Check if email, adhaar number, and phone are already in use
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'student/submit_cgpa.html')
        if Student.objects.filter(adhaar_no=adhaar_no).exists():
            messages.error(request, 'Adhar Number already exists.')
            return render(request, 'student/submit_cgpa.html')
        if CustomUser.objects.filter(phone=phnno).exists():
            messages.error(request, 'Phone already exists.')
            return render(request, 'student/submit_cgpa.html')

        # Check if phnno contains only numeric digits
        if not re.match("^[0-9]+$", phnno):
            messages.error(request, 'Phone should only contain numeric digits.')
            return render(request, 'student/submit_cgpa.html')

        # Calculate age based on the provided DOB
        try:
            dob_date = date.fromisoformat(dob)
            today = date.today()
            age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
            return render(request, 'student/submit_cgpa.html')

        # Check if the age is less than 18
        if age < 18:
            messages.error(request, 'You must be at least 18 years old to sign up.')
            return render(request, 'student/submit_cgpa.html')

        # Create a new CustomUser instance
        user = CustomUser.objects.create_user(username=email, email=email)
        user.first_name = first_name
        user.last_name = last_name
        user.phone = phnno
        user.dob = dob
        user.address = address
        user.user_type = 'student'
        user.save()

        # Create a new Student instance and link it to the CustomUser
        student = Student.objects.create(user=user)
        student.course = course
        student.course_place = course_place
        student.duration_of_course = duration_of_course
        student.specialization = specialization
        student.year_of_pass = year_of_pass
        student.cgpa = cgpa
        student.experience = experience
        student.adhaar_no = adhaar_no
        student.adhaar_pic = pic_of_aadhaar
        student.save()
        return render(request, 'application_successful.html')

    print(course)
    print(cgpa)
    return render(request, 'student/intern.html', {'course': course ,'cgpa': cgpa})




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
    merit_students = []
    nonmerit_students = []
    
    # for student in student_requests:
    #     if student.course == 'LLB' and student.cgpa is not None and student.cgpa >= 8.0:
    #         merit_students.append(student)
    #     elif student.course == 'LLM' and student.cgpa is not None and student.cgpa >= 7.0:
    #         merit_students.append(student)
    #     else:
    #         nonmerit_students.append(student)

    # context = {
    #     'merit_students': merit_students,
    #     'nonmerit_students': nonmerit_students,
    # }
    context = {
        'student_requests':student_requests,
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


# def unassigned_students(request):
#     unassigned_students = Student.objects.filter(is_approved=True, lawyer__isnull=True)
#     return render(request, 'unassigned_students.html', {'unassigned_students': unassigned_students})

@login_required
def unassigned_students(request):
    # Retrieve the currently logged-in lawyer
    lawyer_profile = request.user.lawyer_profile
    # Filter students who have applied for internships under the logged-in lawyer
    applied_students = Student.objects.filter(is_approved=True, application__internship__lawyer_profile=lawyer_profile)

    # Filter students who are already enrolled in internships under the logged-in lawyer
    enrolled_students = Student.objects.filter(is_approved=True, lawyer=lawyer_profile)

    return render(request, 'unassigned_students.html', {'applied_students': applied_students, 'enrolled_students': enrolled_students})

# def hire_student(request, student_id):
#     if request.method == 'POST':
#         student = Student.objects.get(id=student_id)

#         # Check if the student is already hired
#         if student.lawyer:
#             messages.error(request, 'This student is already hired.')
#         else:
#             # Assign the lawyer to the student
#             student.lawyer = request.user.lawyer_profile
#             student.save()
#             messages.success(request, f'You have hired {student.user.first_name} {student.user.last_name}.')

#     return redirect('unassigned_students')

def hire_student(request, student_id):
    if request.method == 'POST':
        student = Student.objects.get(id=student_id)

        # Check if the student is already hired
        if student.lawyer:
            messages.error(request, 'This student is already hired.')
        else:
            # Check if the lawyer has reached the maximum number of hired students (5 in this example)
            max_students = 5
            current_hired_students = Student.objects.filter(lawyer=request.user.lawyer_profile).count()

            if current_hired_students >= max_students:
                messages.error(request, 'You have reached the maximum limit of hired students.')
            else:
                # Assign the lawyer to the student
                student.lawyer = request.user.lawyer_profile
                student.save()
                messages.success(request, f'You have hired {student.user.first_name} {student.user.last_name}.')

    return redirect('unassigned_students')

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


def auth(request):
    if request.user.user_type == 'admin':
        # Calculate the number of lawyers
        lawyer_count = LawyerProfile.objects.count()
        booking_count = Booking.objects.count()
        internship_count = Internship.objects.count()
        students_count = Student.objects.count()
        cases_count = Case.objects.count()
        
        
        # Retrieve the recent 5 bookings, ordered by pk in descending order (greatest to smallest)
        recent_bookings = Booking.objects.order_by('-pk')[:5]
        recent_queries = ContactEntry.objects.order_by('-pk')[:5]
        
        context = {
            'user': request.user,
            'lawyer_count': lawyer_count,
            'booking_count': booking_count,
            'internship_count': internship_count,
            'students_count': students_count,
            'cases_count': cases_count,
            'recent_bookings': recent_bookings,
            'recent_queries': recent_queries,
}

            
        
        # Pass the count and recent bookings to the template
        return render(request, 'admin/dash.html', context)
    else:
        return render(request, '404.html')
    

@login_required
def work_assignment_tasks(request, work_assignment_id):
    work_assignment = get_object_or_404(WorkAssignment, pk=work_assignment_id)

    if request.user == work_assignment.student.user or request.user == work_assignment.case.lawyer.user:
        tasks = Task.objects.filter(work_assignment=work_assignment)

        return render(request, 'tasks/work_assignment_tasks.html', {'work_assignment': work_assignment, 'tasks': tasks})

    return render(request, '404.html')  


@login_required
def create_task(request, work_assignment_id):
    work_assignment = get_object_or_404(WorkAssignment, pk=work_assignment_id)

    if request.user != work_assignment.student.user:
        return render(request, '404.html')

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = Task(
                work_assignment=work_assignment,
                files=form.cleaned_data['files'],
                note=form.cleaned_data['note'],
                student=work_assignment.student
            )
            task.save()

            # You can add a success message if needed
            # messages.success(request, 'Task submitted successfully.')

            # Redirect to the same page with a GET request
            return redirect('create_task', work_assignment_id=work_assignment.id)
    else:
        form = TaskForm()

    return render(request, 'task_create.html', {'form': form, 'work_assignment': work_assignment})

@login_required
def mark_leave_request(request, leave_type):
    user = request.user

    if user.is_authenticated and user.user_type == 'lawyer':
        if request.method == 'POST':
            form = LeaveRequestForm(request.POST)

            if form.is_valid():
                leave_request = form.save(commit=False)
                leave_request.lawyer = user
                leave_request.status = 'pending'
                leave_request.type = leave_type

                if leave_type == 'casual_leave':
                    # Calculate the total leave days for the current month
                    current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    current_month_end = (current_month_start + timedelta(days=32)).replace(microsecond=0) - timedelta(days=1)

                    # Check if there's already a leave request for the same day
                    existing_leave_requests = HolidayRequest.objects.filter(
                        lawyer=user,
                        type=leave_type,
                        date=leave_request.date
                    )

                    if existing_leave_requests.exists():
                        messages.warning(request, 'You have already marked leave for this day.')
                        return redirect('mark_casual_leave', leave_type=leave_type)

                    # Count leave days only for the month of the requested date
                    total_leave_days = HolidayRequest.objects.filter(
                        lawyer=user,
                        type=leave_type,
                        date__year=leave_request.date.year,
                        date__month=leave_request.date.month
                    ).count()

                    # Allow only three casual leave days in the specific month
                    if total_leave_days >= 3:
                        messages.warning(request, 'You can only request a maximum of 3 casual leave days in this month.')
                        return redirect('mark_casual_leave', leave_type=leave_type)

                leave_request.save()

                messages.success(request, 'Leave request sent')
                return redirect('mark_casual_leave', leave_type=leave_type)

        form = LeaveRequestForm()

        # Retrieve leave requests and their statuses for the logged-in lawyer
        leave_requests = HolidayRequest.objects.filter(lawyer=user, type=leave_type)

        context = {
            'leave_requests': leave_requests,
            'form': form,
            'leave_type': leave_type,
        }
        return render(request, 'lawyer/mark_leave_request.html', context)

    else:
        messages.error(request, 'Only lawyers can request leave.')
        return redirect('home')
    
@login_required    
def leave_reports(request):
    user = request.user

    if user.is_authenticated and user.user_type == 'lawyer':
        lawyer_profile = LawyerProfile.objects.get(user=user)

        # Handle the form
        form = LeaveReportsFilterForm(request.GET)
        if form.is_valid():
            selected_month = int(form.cleaned_data['month'])
            selected_year = int(form.cleaned_data['year'])
            first_day = timezone.datetime(selected_year, selected_month, 1)
            last_day = timezone.datetime(selected_year, selected_month, monthrange(selected_year, selected_month)[1], 23, 59, 59, 999999)

            # Get leave reports for the selected month and year
            leave_reports = HolidayRequest.objects.filter(lawyer=user, date__range=(first_day, last_day))
        else:
            # If form is not valid, get leave reports for the current month and year
            today = timezone.now()
            first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_day = today.replace(day=monthrange(today.year, today.month)[1], hour=23, minute=59, second=59, microsecond=999999)

            leave_reports = HolidayRequest.objects.filter(lawyer=user, date__range=(first_day, last_day))

        context = {
            'leave_reports': leave_reports,
            'form': form,
        }

        return render(request, 'lawyer/leave_reports.html', context)

    else:
        messages.error(request, 'Only lawyers can view leave reports.')
        return redirect('home')
    
    
def generate_leave_report_pdf(leave_reports, lawyer_name):
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()

    # Generate HTML content with style
    html_content = get_template('pdf_template.html').render({'leave_reports': leave_reports, 'lawyer_name': lawyer_name})

    # Create PDF document
    pisa_status = pisa.CreatePDF(html_content, dest=buffer)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    # FileResponse sets the Content-Disposition header for PDF download
    buffer.seek(0)
    return HttpResponse(buffer.read(), content_type='application/pdf')

def download_leave_reports_pdf(request):
    user = request.user

    if user.is_authenticated and user.user_type == 'lawyer':
        # Fetch all holiday requests of the logged-in lawyer, newest first
        leave_reports = HolidayRequest.objects.filter(lawyer=user).order_by('-date')

        # Get lawyer details
        lawyer_name = f"{user.first_name} {user.last_name}"

        # Generate PDF report
        pdf_response = generate_leave_report_pdf(leave_reports, lawyer_name)

        # Set the response headers for PDF download
        pdf_response['Content-Disposition'] = 'attachment; filename="leave_reports.pdf"'
        return pdf_response

    else:
        # You can customize the error response based on your requirements
        return HttpResponse("Unauthorized access", status=401)

   
def generate_leave_reports_admin_pdf(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        print("Provided email:", email)

        # Check if the email is associated with a lawyer
        user = CustomUser.objects.filter(username=email, user_type='lawyer').first()
        print("Found user:", user)

        if user:
            # Fetch all holiday requests of the lawyer, newest first
            leave_reports = HolidayRequest.objects.filter(lawyer=user).order_by('-date')

            # Get lawyer details
            lawyer_name = f"{user.first_name} {user.last_name}"

            # Generate PDF report
            pdf_response = generate_leave_report_pdf(leave_reports, lawyer_name)

            # Set the response headers for PDF download
            pdf_response['Content-Disposition'] = 'attachment; filename="leave_reports.pdf"'
            return pdf_response
        else:
            messages.error(request, "No lawyer found with the provided email.")
            return render(request, 'admin/leave_reports.html')

    else:
        # Render a form for inputting the email
        return render(request, 'admin/leave_reports.html',)

def business_laws(request):
    return render (request,'admin/laws/business.html')

def tax_laws(request):
    return render (request,'admin/laws/tax.html')


def emp_laws(request):
    return render (request,'admin/laws/emp.html')


def ip_laws(request):
    return render (request,'admin/laws/ip.html')

def contract_laws(request):
    return render (request,'admin/laws/contract.html')

def realestate_laws(request):
    return render (request,'admin/laws/realestate.html')

def security_laws(request):
    return render (request,'admin/laws/security.html')

def consumer_laws(request):
    return render (request,'admin/laws/consumer.html')

def health_laws(request):
    return render (request,'admin/laws/health.html')

def common(request):
    return render (request,'common.html')


from django.shortcuts import render
from .models import Internship

def internships(request):
    # Query all internships and order them by start_date in descending order (latest first)
    internships = Internship.objects.order_by('-start_date')

    return render(request, 'student/internship_list.html', {'internships': internships})


def submit_cgpa(request):
    if request.method == 'POST':
        cgpa_str = request.POST.get('cgpa')
        course = request.POST.get('course')
        if cgpa_str and course:
            try:
                cgpa = float(cgpa_str)
                if 8 <= cgpa <= 10:
                    request.session['cgpa'] = cgpa
                    request.session['course'] = course
                elif 4 <= cgpa < 8:
                    request.session['cgpa'] = cgpa
                    request.session['course'] = course
            except ValueError:
                pass

        # Pass the values to step 2 template
        return render(request, 'student/intern.html', {'cgpa': request.session.get('cgpa', ''), 'course': request.session.get('course', '')})

    return render(request, 'student/submit_cgpa.html')


def internship_payment(request, student_id, internship_id):
    # Retrieve student and internship
    student = Student.objects.get(id=student_id)
    internship = Internship.objects.get(id=internship_id)

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
        # Create a Razorpay order
        order_amount = 1000  # You can customize the order amount
        order_currency = 'INR'
        order_payload = {
            'amount': order_amount,
            'currency': order_currency,
            'notes': {
                'student_id': student.id,
                'internship_id': internship.id
            },
            'payment_capture': "1"
        }
        order = client.order.create(data=order_payload)

        # Create a StudentPayment entry
        student_payment = StudentPayment.objects.create(
            student=student,
            internship=internship,
            order_id=order.get('id'),
            status=PaymentStatus.PENDING  
        )

        # Render the payment template with necessary details
        return render(
            request,
            "internship_razorpay_payment.html",
            {
                "callback_url": f"http://127.0.0.1:8000/internship_payment_callback/{student.id}/",
                "razorpay_key": 'rzp_test_cvGs8NAQTlqQrP',
                "student": student,
                "internship": internship,
                "order": order,
                "student_payment": student_payment,  
            }
        )

    except Exception as e:
        print(str(e))
        return render(
            request,
            "payment_error.html",
            {
                "error_message": str(e),
                
            }
        )

@csrf_exempt
def internship_payment_callback(request, student_id):
    if request.method == 'POST':
        try:
            razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            razorpay_signature = request.POST.get('razorpay_signature', '')

            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Verify the payment signature
            is_signature_valid = client.utility.verify_payment_signature({
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_order_id': razorpay_order_id,
                'razorpay_signature': razorpay_signature
            })

            if is_signature_valid:
                try:
                    # Retrieve student payment
                    student_payment = StudentPayment.objects.get(order_id=razorpay_order_id)

                    # Update payment status and details
                    student_payment.razorpay_payment_id = razorpay_payment_id
                    student_payment.razorpay_signature = razorpay_signature
                    student_payment.status = PaymentStatus.SUCCESS
                    student_payment.save()
                    
                    # Create an application with status 'accepted'
                    application, created = Application.objects.get_or_create(internship=student_payment.internship, student=student_payment.student)
                    if created:
                        application.status = 'accepted'
                        application.save()


                    # Render payment confirmation template
                    return render(request, 'payment_confirm.html', {'student_payment': student_payment})
                except StudentPayment.DoesNotExist:
                    return JsonResponse({"error": "Student payment not found"}, status=404)
            else:
                return JsonResponse({"status": "failure"})

        except Exception as e:
            # Handle exceptions
            logger.error(f"Error in Razorpay callback: {str(e)}")
            return JsonResponse({"error": "An error occurred during payment processing"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


