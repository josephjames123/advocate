# accounts/views.py
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect ,get_object_or_404 ,HttpResponseRedirect
from django.urls import reverse
from .models import CustomUser, LawyerProfile , CurrentCase  
from django.http import HttpResponseForbidden , HttpResponseNotFound , HttpResponse
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
from .models import LawyerProfile , ContactEntry , Internship , Student , Application , Booking , Day ,TimeSlot , LawyerDayOff , HolidayRequest , Case ,Appointment
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


def login_view(request):
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
                return redirect(reverse('lawyer_dashboard'))
            elif user.user_type == 'student':
                return redirect(reverse('student_dashboard'))
            
        else:
            messages.error(request, 'Invalid email or password. Please try again')
    
    return render(request, 'login.html')

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

        # # Check if the Aadhar number is already in use
        # if CustomUser.objects.filter(adharno=adharno).exists():
        #     messages.error(request, 'Aadhar number already exists')
        #     return render(request, 'signup.html')
        
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

        # # Check if the Aadhar number exceeds 12 digits
        # if len(adharno) != 12:
        #     messages.error(request, 'Aadhar number must be exactly 12 digits.')
        #     return render(request, 'signup.html')
        
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
            'recent_bookings': recent_bookings,
            'booking_count':booking_count,
            'recent_queries': recent_queries,
            'internship_count': internship_count,
            'students_count':students_count,
            'cases_count': cases_count,
            }
            
        
        # Pass the count and recent bookings to the template
        return render(request, 'admin/dashboard.html', context)
    else:
        return render(request, '404.html')

# def student_dashboard(request):
#     if request.user.user_type == 'student':
#         recent_internships = Internship.objects.order_by('-pk')[:5]
#         print(recent_internships)

        
#         return render(request, 'student/dashboard.html', {'user': request.user, 'recent_internships': recent_internships})
#     else:
#         return HttpResponseForbidden("Access Denied")

# def client_dashboard(request):
#     return render(request, 'client/dashboard.html', {'user': request.user})
@login_required
def client_dashboard(request):
    user = request.user

    # Get all bookings by the client
    all_bookings = Booking.objects.filter(user=user)

    # Filter bookings by status
    confirmed_bookings = all_bookings.filter(status='confirmed')
    pending_bookings = all_bookings.filter(status='pending')
    canceled_bookings = all_bookings.filter(status='canceled')
    rescheduled_bookings = all_bookings.filter(status='reschedule')
    notpaid_bookings = all_bookings.filter(status='notpaid')

    context = {
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
        'canceled_bookings': canceled_bookings,
        'rescheduled_bookings':rescheduled_bookings,
        'notpaid_bookings':notpaid_bookings,
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

        # Count the number of bookings for this lawyer
        booking_count = Booking.objects.filter(lawyer=lawyer_profile).count()
        case_count = Case.objects.filter(lawyer=lawyer_profile).count()
        
        return render(request, 'lawyer/dashboard.html', {'user': request.user, 'booking_count': booking_count,'bookings': bookings , 'case_count': case_count})
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

# def custom_password_set_confirm(request, uidb64, token):
#     user_id = urlsafe_base64_decode(uidb64)
#     user = CustomUser.objects.get(pk=user_id)
    
#     if request.method == 'POST':
#         form = SetPasswordForm(user, request.POST)
#         if form.is_valid():
#             form.save()
#             # Log the user in after setting the password
#             user = authenticate(username=user.username, password=form.cleaned_data['new_password1'])
#             login(request, user)
#             return redirect('dashboard')  # Redirect to the dashboard or another page
#     else:
#         form = SetPasswordForm(user)
    
#     return render(request, 'registration/password_set_confirm.html', {'form': form, 'user': user})


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

# def contact(request):
#     return render(request, 'contact.html')




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
# def book_lawyer(request, lawyer_id):
#     lawyer = get_object_or_404(LawyerProfile, pk=lawyer_id)
#     user = request.user

#     if request.method == 'POST':
#         form = BookingForm(request.POST, lawyer=lawyer)

#         if form.is_valid():
#             booking_date = form.cleaned_data['booking_date']
            
#             # Check if the booking date is in the future
#             if booking_date <= timezone.localdate():
#                 messages.error(request, 'You can only book for future dates.')
#             else:
#                 selected_day = booking_date.weekday() + 1

#                 if not lawyer.working_days.filter(name=selected_day).exists():
#                     messages.error(request, 'This lawyer does not work on the selected day.')
#                 else:
#                     # Check if the selected date is marked as a day off for the lawyer
#                     if LawyerDayOff.objects.filter(lawyer=lawyer, date=booking_date).exists():
#                         messages.error(request, 'This date is marked as a day off for the lawyer.')
#                     else:
#                         # Continue with booking logic
#                         booking = form.save(commit=False)
#                         booking.user = user
#                         booking.lawyer = lawyer
#                         booking.status = 'pending'
                        
#                         # Assign the selected TimeSlot instance to the booking
#                         selected_time_slot = form.cleaned_data['time_slot']
#                         booking.time_slot = selected_time_slot
                        
#                         # Check for existing bookings and user's existing bookings (as previously implemented)
#                         existing_booking = Booking.objects.filter(
#                             lawyer=lawyer,
#                             booking_date=booking.booking_date,
#                             time_slot=selected_time_slot,
#                         ).exclude(status='canceled').first()

#                         user_existing_booking = Booking.objects.filter(
#                             user=user,
#                             booking_date=booking.booking_date,
#                             time_slot=selected_time_slot,
#                         ).exclude(status='canceled').first()

#                         if existing_booking:
#                             messages.error(request, 'This time slot is already booked by another user.')
#                         elif user_existing_booking:
#                             messages.error(request, 'You have already booked a lawyer at this time slot.')
#                         else:
#                             booking.save()
#                             # Redirect to a success page or display a success message
#                             return redirect('home')
#     else:
#         form = BookingForm(lawyer=lawyer)

#     return render(request, 'book_lawyer.html', {'form': form, 'lawyer': lawyer})

# def reschedule_appointment(request, booking_id):
#     # Get the booking object for the provided booking_id
#     booking = get_object_or_404(Booking, pk=booking_id)
#     user = request.user

#     # Check if the user making the request is the owner of the booking (client)
#     if user != booking.user:
#         # Customize this part to handle unauthorized access, e.g., show an error message or redirect to an error page
#         return render(request, 'access_denied.html')

#     if request.method == 'POST':
#         # If the form is submitted, process the rescheduling request
#         form = BookingForm(request.POST, lawyer=booking.lawyer)

#         if form.is_valid():
#             new_booking_date = form.cleaned_data['booking_date']
#             new_time_slot = form.cleaned_data['time_slot']

#             # Check if the selected date is marked as a day off for the lawyer
#             if LawyerDayOff.objects.filter(lawyer=booking.lawyer, date=new_booking_date).exists():
#                 messages.error(request, 'The selected date is marked as a day off for the lawyer.')
#             else:
#                 # Check for existing bookings on the selected date and time slot
#                 existing_booking = Booking.objects.filter(
#                     lawyer=booking.lawyer,
#                     booking_date=new_booking_date,
#                     time_slot=new_time_slot,
#                     status='confirmed'
#                 ).first()

#                 if existing_booking:
#                     messages.error(request, 'This time slot is already booked by another user.')
#                 else:
#                     # Update the booking with the new date and time slot
#                     booking.booking_date = new_booking_date
#                     booking.time_slot = new_time_slot
#                     booking.status = 'pending'  # You can set the status to 'confirmed' here
#                     booking.save()
#                     messages.success(request, 'Appointment rescheduled successfully.')
#                     return redirect('client_dashboard')  # Redirect to the client's dashboard or a success page
#     else:
#         # If the request is a GET request, display the rescheduling form with initial data from the original booking
#         form = BookingForm(lawyer=booking.lawyer, initial={'booking_date': booking.booking_date, 'time_slot': booking.time_slot})

#     return render(request, 'reschedule_appointment.html', {'form': form, 'booking': booking})


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


# def student_dashboard(request):
#     if request.user.user_type == 'student':
#         try:
#             # Check if the user is a student and if they are approved
#             student = Student.objects.get(user=request.user)
#             if student.is_approved:
#                 recent_internships = Internship.objects.order_by('-pk')[:5]
#                 return render(request, 'student/dashboard.html', {'user': request.user, 'recent_internships': recent_internships})
#             else:
#                 # Display a message or a separate template for unapproved students
#                 return render(request, 'student/not_approved.html')
#         except Student.DoesNotExist:
#             # User is a student but doesn't exist as a student in the database
#             pass

#     return HttpResponseForbidden("Access Denied")

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
            if student.college and student.current_cgpa is not None:
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
    
# @login_required
# def lawyer_save(request):
#     if request.user.user_type != 'lawyer':
#         return render(request, '404.html')

#     if request.method == 'POST':
#         # email = request.POST['email']
#         specialization = request.POST['specialization']
#         start_date_str = request.POST['start_date']
#         start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
#         profile_picture = request.FILES.get('profile_picture')
#         address = request.POST['address']
#         dob = request.POST['dob']
#         pin = request.POST['pin']
#         state = request.POST['state']
#         phone = request.POST['phone']
#         working_days = request.POST.getlist('working_days')  # Get a list of selected day values
#         working_time_start = request.POST['working_time_start']
#         working_time_end = request.POST['working_time_end']

#         if not all([specialization, start_date_str, profile_picture, address, dob, pin, state, phone]):
#             return HttpResponse("Please fill in all fields.")

#         # Create a new user with user_type 'lawyer'
#         user = CustomUser.objects.create_user(
#             username = request.user.email,
#             user_type='lawyer',
#             address=address,
#             dob=dob,
#             pin=pin,
#             state=state,
#             phone=phone,
#         )

#         lawyer_profile = LawyerProfile.objects.create(
#             user=user,
#             specialization=specialization,
#             start_date=start_date,
#             profile_picture=profile_picture,
#             working_days=working_days,
#             working_time_start=working_time_start,
#             working_time_end=working_time_end
#         )

#         # Redirect to a success page or the dashboard
#         return redirect('lawyer_dashboard')  # Replace 'student_dashboard' with your dashboard URL name
#     else:
#         return render(request, 'lawyer/user_details_form.html')


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
    


    

# def lawyer_save(request):
#     if request.user.user_type != 'lawyer':
#         return render(request, '404.html')

#     available_time_slots = TimeSlot.objects.all()

#     if request.method == 'POST':
#         specialization = request.POST['specialization']
#         # start_date_str = request.POST['start_date']
#         # start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

#         # Calculate age based on the provided date of birth
#         dob = request.POST['dob']
#         dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
#         today = datetime.now().date()
#         age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))

#         if age < 25:
            
#             LawyerProfile.objects.filter(user=request.user).delete()
#             return render(request, 'sorry.html')
         
#         # if (start_date - dob_date).days < 25 * 365:
#         #     return HttpResponse("You must be at least 25 years old to set the start date.")

#         # profile_picture = request.FILES.get('profile_picture')
#         address = request.POST['address']
#         total_cases_handeled = request.POST['total_cases_handeled']
#         currendly_handling = request.POST['currendly_handling']
#         experience = request.POST['experience']
#         court = request.POST['court']
#         # pin = request.POST['pin']
#         # state = request.POST['state']

#         # working_day_values = request.POST.getlist('working_days')
#         # working_time_start_id = request.POST['working_time_start']  # Get the selected TimeSlot ID
#         # working_time_end_id = request.POST['working_time_end']  # Get the selected TimeSlot ID
#         # budget = request.POST['budget']
#         # cases_won = request.POST['cases_won']
#         # cases_lost = request.POST['cases_lost']  # Extract budget, cases_won, and cases_lost from form data

#         # Handle the locations field without using a form
#         # input_str = request.POST['locations']
#         # locations = input_str.split(",")

#         if not all([specialization,  address, dob,total_cases_handeled,currendly_handling,experience]):
#             return HttpResponse("Please fill in all fields.")

#         # Create or update the user's details
#         user = request.user
#         user.address = address
#         user.dob = dob
#         # user.pin = pin
#         # user.state = state
#         user.save()
#         print("User saved")

#         # Create or update the lawyer profile
#         lawyer_profile, created = LawyerProfile.objects.get_or_create(user=user)
#         lawyer_profile.specialization = specialization
#         # lawyer_profile.start_date = start_date
#         # lawyer_profile.profile_picture = profile_picture
#         # lawyer_profile.budget = budget
#         # lawyer_profile.cases_won = cases_won
#         # lawyer_profile.cases_lost = cases_lost  # Assign budget, cases_won, and cases_lost
#         lawyer_profile.total_cases_handeled=total_cases_handeled
#         lawyer_profile.currendly_handling=currendly_handling
#         lawyer_profile.experience=experience
#         lawyer_profile.court = court

#         # # Clear existing working days and set new ones based on selected values
#         # lawyer_profile.working_days.clear()
#         # for day_value in working_day_values:
#         #     day, created = Day.objects.get_or_create(name=day_value)
#         #     lawyer_profile.working_days.add(day)

#         # # # Retrieve the selected TimeSlot instances based on their IDs
#         # # working_time_start = get_object_or_404(TimeSlot, id=working_time_start_id)
#         # # working_time_end = get_object_or_404(TimeSlot, id=working_time_end_id)

#         # # lawyer_profile.working_time_start = working_time_start
#         # # lawyer_profile.working_time_end = working_time_end

#         # Set the locations field based on the input
#         # lawyer_profile.locations.set(locations)

#         lawyer_profile.save()

#         # Redirect to a success page or the dashboard
#         return redirect('lawyer_dashboard')
#     else:
#         return render(request, 'lawyer/user_details_form.html', {'available_time_slots': available_time_slots})

    
# def mark_holiday(request):
#     if request.method == 'POST':
#         holiday_date = request.POST.get('holiday_date')
#         user = request.user  # Get the current user

#         if user.user_type == 'lawyer':
#             lawyer = user.lawyer_profile  # Access the associated lawyer profile (use 'lawyer_profile' here)
#             # Check if the date is not already marked as a holiday
#             if not LawyerDayOff.objects.filter(lawyer=lawyer, date=holiday_date).exists():
#                 LawyerDayOff.objects.create(lawyer=lawyer, date=holiday_date)
#                 messages.success(request, 'Holiday marked successfully.')
#             else:
#                 messages.warning(request, 'This date is already marked as a holiday.')
#         else:
#             messages.error(request, 'Only lawyers can mark holidays.')

#     # return redirect('lawyer_dashboard')  # Redirect back to the lawyer's dashboard
#     return render(request, 'lawyer/mark_holiday.html')

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



# def update_lawyer_profile(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     lawyer_profile, created = LawyerProfile.objects.get_or_create(user=user)

#     if request.method == 'POST':
#         user_form = CustomUserUpdateForm(request.POST, instance=user)
#         profile_form = LawyerProfileUpdateForm(request.POST, request.FILES, instance=lawyer_profile)

#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             return redirect('home')  # Redirect to a success page

#     else:
#         user_form = CustomUserUpdateForm(instance=user)
#         profile_form = LawyerProfileUpdateForm(instance=lawyer_profile)

#     context = {
#         'user_form': user_form,
#         'profile_form': profile_form,
#     }

#     return render(request, 'lawyer/update_lawyer_profile.html', context)


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
        
        # user.state = request.POST.get('state', user.state)
        # Get the choices for the 'state' field
        # state_choices = LawyerProfile.SPECIALIZATIONS

        # Parse the 'locations' input as a list of tags
        # locations_input = request.POST.get('locations', '')
        # locations = [location.strip() for location in locations_input.split(',') if location.strip()]

        # # Use the 'set()' method to update the working_days M2M field
        # working_days_input = request.POST.getlist('working_days')
        # if working_days_input:
        #     lawyer_profile.working_days.set(working_days_input)

        lawyer_profile.specialization = request.POST.get('specialization', lawyer_profile.specialization)
        lawyer_profile.court = request.POST.get('court', lawyer_profile.court)

        # # If locations are provided in the form, update them; otherwise, keep existing values
        # if locations:
        #     lawyer_profile.locations.set(locations)

        # Handle profile_picture file upload
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            lawyer_profile.profile_picture = profile_picture

        # Check if a new profile_picture is provided; otherwise, keep the existing image
        if not profile_picture and lawyer_profile.profile_picture:
            lawyer_profile.profile_picture = lawyer_profile.profile_picture  # Keep the existing image

        user.save()
        lawyer_profile.save()
        return redirect('home')  # Redirect to a success page

    # For GET request, retrieve and display the form
    context = {
        'user': user,
        'lawyer_profile': lawyer_profile,
        
    }

    return render(request, 'lawyer/update_lawyer_profile.html', context)


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

    # Pass the filtered bookings to the template
    context = {
        'bookings': queryset,
    }

    # Render the template
    return render(request, 'bookings.html', context)


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


def admin_view_holiday_requests(request):
    # Check if the user is an admin
    if not request.user.is_superuser:
        return redirect('home')  # Redirect to the home page or any other appropriate page

    # Query all pending holiday requests
    pending_requests = HolidayRequest.objects.filter(status='pending')

    # Render the template with the pending holiday requests data
    return render(request, 'admin/admin_view_holiday_requests.html', {'pending_requests': pending_requests})


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

def case_saved(request):
    return render(request, 'case_saved.html')


def case_detail(request, case_id):
    # Retrieve the case object by its ID or return a 404 error if not found
    case = get_object_or_404(Case, pk=case_id)

    # Render the 'case_detail.html' template with the case object
    return render(request, 'lawyer/case_detail.html', {'case': case})

# def case_saved(request):
#     return render(request, 'case_saved.html')



# def case_saved(request):
#     # Check if the session variable indicating case submission exists
#     if request.session.get('case_submitted'):
#         # Case has already been submitted, show a message or redirect to a different page
#         return render(request, 'case_already_submitted.html')
    
#     return render(request, 'case_saved.html')

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


# def assign_working_hours(request):
#     lawyer = request.user.lawyer_profile

#     if request.method == 'POST':
#         selected_time_slots = request.POST.getlist('selected_time_slots')
        
#         # Clear existing working slots for the lawyer
#         lawyer.working_slots.clear()

#         # Add selected time slots to the lawyer's working hours
#         for time_slot_id in selected_time_slots:
#             time_slot = TimeSlot.objects.get(pk=time_slot_id)
#             lawyer.working_slots.add(time_slot)

#         return redirect('home')  # Redirect to a success page

#     all_time_slots = TimeSlot.objects.all()
#     return render(request, 'assign_working_hours.html', {'all_time_slots': all_time_slots})


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

                # Add the selected time slots to the lawyer's working slots
                lawyer.working_slots.set(selected_time_slots)

                print("Working slots assigned successfully")  # Debugging: Check if slots are assigned successfully
                print("Selected slot IDs:", [slot.id for slot in selected_time_slots])  # Debugging: Check selected slot IDs

                # Redirect to the dashboard or another page
                return redirect('update')
        except Exception as e:
            # Log the error
            traceback.print_exc()
            return HttpResponseServerError("An error occurred while saving data.")

    # Retrieve all available time slots to display in the form
    all_time_slots = TimeSlot.objects.all()
    breadcrumbs = [
        ("Home", reverse("home")),
        ("lawyer_dashboard", reverse("lawyer_dashboard")),
        ("assign_working_hours", None),  # Current page (no link)
    ]

    return render(request, 'assign_working_hours.html', {'all_time_slots': all_time_slots ,'breadcrumbs': breadcrumbs})
    

# def book_lawyer(request, lawyer_id):
#     lawyer = LawyerProfile.objects.get(pk=lawyer_id)
#     user = request.user

#     if request.method == 'POST':
#         appointment_date = request.POST.get('appointment_date')
#         time_slot_id = request.POST.get('time_slot')
#         time_slot = TimeSlot.objects.get(pk=time_slot_id)

#         # Check if the selected time slot is available for booking
#         if not Appointment.objects.filter(
#             Q(time_slot=time_slot, appointment_date=appointment_date, lawyer=lawyer) |
#             Q(time_slot=time_slot, appointment_date=appointment_date, client=user)
#         ).exists():
#             appointment = Appointment(
#                 lawyer=lawyer,
#                 client=user,
#                 time_slot=time_slot,
#                 appointment_date=appointment_date
#             )
#             appointment.save()
#             return redirect('home')  # Redirect to a success page or appointment list

#     # Get available time slots based on lawyer's working hours for the current date
#     today = datetime.today().date()
#     available_time_slots = TimeSlot.objects.filter(
#         Q(lawyers=lawyer) & Q(day=today.strftime("%A"))
#     )

#     return render(request, 'book_appointment.html', {'lawyer': lawyer, 'available_time_slots': available_time_slots})


def select_date(request, lawyer_id):
    # Retrieve the lawyer using the lawyer_id parameter
    lawyer = get_object_or_404(LawyerProfile, id=lawyer_id)
    
    if request.method == 'POST':
        selected_date = request.POST.get('selected_date')
        
        # Check if it's a holiday for the lawyer
        if LawyerDayOff.objects.filter(lawyer=lawyer, date=selected_date).exists():
            messages.error(request, 'Booking is not possible on a day marked as a holiday for the lawyer.')
        else:
            return redirect('book_lawyer', lawyer_id=lawyer_id, selected_date=selected_date)
    
    return render(request, 'select_date.html', {'lawyer': lawyer})

def parse_time(time_str):
    try:
        # Parse the time string in the format "08:00 AM"
        parsed_time = datetime.strptime(time_str, '%I:%M %p').strftime('%H:%M:%S')
        return parsed_time
    except ValueError:
        return None

def book_lawyer(request, lawyer_id, selected_date):
    try:
        # Convert selected_date to a Python date object
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        
        # Get the current date
        current_date = timezone.now().date()

        # Check if the selected_date is in the past
        if selected_date < current_date:
            messages.error(request, 'Booking is not possible for past dates.')
            

        # Get the lawyer object
        lawyer = LawyerProfile.objects.get(id=lawyer_id)
        
        
        

        # Retrieve the lawyer's working time slots for the selected date
        working_time_slots = TimeSlot.objects.filter(lawyers=lawyer, day=selected_date.strftime('%A')).order_by('start_time')

        # Initialize a list to store available appointment slots
        appointment_slots = []

        # Iterate through the working time slots and generate appointment slots
        for time_slot in working_time_slots:
            start_time = datetime.combine(selected_date, time_slot.start_time)
            end_time = datetime.combine(selected_date, time_slot.end_time)

            current_time = start_time
            while current_time <= end_time:
                appointment_slots.append(current_time.strftime('%I:%M %p'))
                current_time += timedelta(minutes=15)

        if request.method == 'POST':
            # Handle the form submission when the client books an appointment
            selected_slot = request.POST.get('selected_slot')

            # Check if the selected slot is still available
            if selected_slot and selected_slot in appointment_slots:
                # Check if the selected slot is available for booking
                if lawyer.is_available(selected_date, selected_slot):
                    try:
                        # Check if the selected slot is in the correct time format
                        selected_time = datetime.strptime(selected_slot, '%I:%M %p').time()
                    except ValueError:
                        messages.error(request, 'Invalid time format. Please choose a valid time from the list (e.g., 08:45 AM).')
                        return render(request, 'book_lawyer.html', {'selected_date': selected_date, 'appointment_slots': appointment_slots})

                    # Create an Appointment record
                    appointment = Appointment(
                        lawyer=lawyer,
                        client=request.user,
                        appointment_date=selected_date,
                        time_slot=selected_time  # Use the selected_time instead of selected_slot
                    )
                    appointment.save()

                    messages.success(request, 'Appointment booked successfully!')
                    return redirect('home')  # Redirect to a success page
                else:
                    messages.error(request, 'Selected slot is not available. Please choose another slot.')
            else:
                messages.error(request, 'Invalid selected slot format. Please choose a valid slot from the list.')

        return render(request, 'book_lawyer.html', {'selected_date': selected_date, 'appointment_slots': appointment_slots})
    except LawyerProfile.DoesNotExist:
        messages.error(request, 'Lawyer not found.')
        return redirect('home')
