from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import datetime
from datetime import datetime, timedelta ,time
from taggit.managers import TaggableManager
from django.contrib.auth import get_user_model  # Import the get_user_model function





class CustomUser(AbstractUser):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('lawyer', 'Lawyer'),
        ('student', 'Student'),
        ('client', 'Client'),
    )
    
    STATES = (
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
    ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
    ('Chandigarh', 'Chandigarh'),
    ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
    ('Lakshadweep', 'Lakshadweep'),
    ('Delhi', 'Delhi'),
    ('Puducherry', 'Puducherry'),
)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='client')
    
    email = models.EmailField(unique=True, default='')  # Change: Use email as the username
    first_name = models.CharField(max_length=30, default='')  # Added: First name field
    last_name = models.CharField(max_length=30, default='')  # Added: Last name field
    # adharno = models.CharField(max_length=12,  blank=True,unique=True)  # Added: Adhar number field
    address = models.TextField(default='',blank=True,)  # Added: Address field
    dob = models.DateField(default='2000-01-01',blank=True,)  # Added: Date of birth field
    pin = models.CharField(max_length=6, default='',blank=True,)  # Added: PIN code field
    state = models.CharField(max_length=50, choices=STATES, blank=True, null=False)
    # state = models.CharField(max_length=10, choices=STATES, default='kerala')  # Added: State field
    phone = models.CharField(max_length=15,blank=True, unique=True)  # Added: Phone number field
    
# class TimeSlot(models.Model):
#     start_time = models.TimeField()
#     # end_time = models.TimeField()
    
    
    
#     def __str__(self):
#         # return f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"
#         return f"{self.start_time.strftime('%I:%M %p')} "

# class TimeSlot(models.Model):
#     # name = models.CharField(max_length=30)
#     start_time = models.TimeField()

#     def __str__(self):
#         # Calculate the end time by adding one hour to the start_time
#         start_datetime = datetime.combine(datetime.today(), self.start_time)
#         end_datetime = start_datetime + timedelta(hours=1)

#         # Format the start and end times as "HH:MM AM/PM"
#         formatted_start_time = start_datetime.strftime("%I:%M %p")
#         formatted_end_time = end_datetime.strftime("%I:%M %p")

#         # Combine start and end times to create the name
#         name = f"{formatted_start_time} - {formatted_end_time}"

#         return name


# class TimeSlot(models.Model):
#     DAY_CHOICES = (
#         ('Monday', 'Monday'),
#         ('Tuesday', 'Tuesday'),
#         ('Wednesday', 'Wednesday'),
#         ('Thursday', 'Thursday'),
#         ('Friday', 'Friday'),
#         ('Saturday', 'Saturday'),
#         ('Sunday', 'Sunday'),
#     )

#     SLOT_CHOICES = (
#         ('8-10', '8:00 AM - 10:00 AM'),
#         ('10-12', '10:00 AM - 12:00 PM'),
#         ('1-3', '1:00 PM - 3:00 PM'),
#         ('3-5', '3:00 PM - 5:00 PM'),
#         ('8-8:15', '8:00 AM - 8:15 AM'),
#         ('8:15-8:30', '8:15 AM - 8:30 AM'),
#         ('8:30-8:45', '8:30 AM - 8:45 AM'),
#         # Add more 15-minute slots here
#     )

#     day = models.CharField(max_length=10, choices=DAY_CHOICES)
#     slot = models.CharField(max_length=10, choices=SLOT_CHOICES)

#     def _str_(self):
#         return f"{self.day} - {self.get_slot_display()}"

#     class Meta:
#         unique_together = ('day', 'slot')
    
# class TimeSlot(models.Model):
#     DAY_CHOICES = (
#         ('Monday', 'Monday'),
#         ('Tuesday', 'Tuesday'),
#         ('Wednesday', 'Wednesday'),
#         ('Thursday', 'Thursday'),
#         ('Friday', 'Friday'),
#         ('Saturday', 'Saturday'),
#         ('Sunday', 'Sunday'),
#     )

#     MAIN_SLOT_CHOICES = (
#         ('8-10', '8:00 AM - 10:00 AM'),
#         ('10-12', '10:00 AM - 12:00 PM'),
#         ('1-3', '1:00 PM - 3:00 PM'),
#         ('3-5', '3:00 PM - 5:00 PM'),
#     )

#     day = models.CharField(max_length=10, choices=DAY_CHOICES)
#     main_slot = models.CharField(max_length=10, choices=MAIN_SLOT_CHOICES)
#     lawyers = models.ManyToManyField('LawyerProfile', blank=True, related_name='working_slots')

#     def __str__(self):
#         return f"{self.get_day_display()} - {self.get_main_slot_display()}"

#     class Meta:
#         unique_together = ('day', 'main_slot')

from django.db import models
from django.contrib.auth import get_user_model

class TimeSlot(models.Model):
    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    )

    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    lawyers = models.ManyToManyField('LawyerProfile', blank=True, related_name='working_slots')

    def __str__(self):
        return f"{self.get_day_display()} - {self.start_time.strftime('%I:%M %p')} to {self.end_time.strftime('%I:%M %p')}"

    class Meta:
        unique_together = ('day', 'start_time', 'end_time')


# class TimeSlot(models.Model):
#     DAY_CHOICES = (
#         ('Monday', 'Monday'),
#         ('Tuesday', 'Tuesday'),
#         ('Wednesday', 'Wednesday'),
#         ('Thursday', 'Thursday'),
#         ('Friday', 'Friday'),
#         ('Saturday', 'Saturday'),
#         ('Sunday', 'Sunday'),
#     )

#     MAIN_SLOT_CHOICES = (
#         ('8-10', '8:00 AM - 10:00 AM'),
#         ('10-12', '10:00 AM - 12:00 PM'),
#         ('1-3', '1:00 PM - 3:00 PM'),
#         ('3-5', '3:00 PM - 5:00 PM'),
#     )

#     day = models.CharField(max_length=15, choices=DAY_CHOICES)
#     main_slot = models.CharField(max_length=10, choices=MAIN_SLOT_CHOICES)
#     lawyer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='working_hours')

#     def __str__(self):
#         return f"{self.day} - {self.main_slot}"


    
class LawyerProfile(models.Model):
    SPECIALIZATIONS = (
        ('family', 'Family Lawyer'),
        ('criminal', 'Criminal Lawyer'),
        ('consumer', 'Consumer Lawyer'),
        ('coperatelawyer', 'Coperate Lawyer'),
        ('civilrightlawyer', 'Civil Right Lawyer'),
        ('divorcelawyer', 'Divorce Lawyer'),
        # Add more as needed
    )
    COURT = (
        ('jfcmcchangancherry', 'Judicial First Class Magistrate Court  Changancherry'),
        ('munsiff', 'Munsiff Court Changancherry'),
        ('jfcmcKanjirapally', 'Judicial First Class Magistrate Court  Kanjirapally'),
        ('munsifcourtkanjirapally', 'Munsiff Court Kanjirapally'),
        ('districtcourtkottayam', 'District Court Kottayam'),
        ('highcourtkochi', 'High Court Kochi'),
        # Add more as needed
    )
    id = models.AutoField(primary_key=True)

    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='lawyer_profile')
    # lawyer_id = models.AutoField(primary_key=True)
    specialization = models.CharField(max_length=20, choices=SPECIALIZATIONS,blank=True)
    start_date = models.DateField(null=True)  # Date profession started
    experience = models.IntegerField(blank=True)  # Experience in years
    
    # Define a default profile picture path
    DEFAULT_PROFILE_PICTURE_PATH = 'uploads/default_profile_picture.png'
    
    profile_picture = models.ImageField(
        upload_to='uploads/',
        default=DEFAULT_PROFILE_PICTURE_PATH,  # Set the default profile picture path
        blank=True,
        null=True
    )
    # bar_enrollment_number = models.CharField(max_length=50,blank=True)  # Bar enrollment number
    certificates = models.ManyToManyField('Certificate', blank=True)
    license_no = models.CharField(max_length=30,blank=False)
    # working_days = models.ManyToManyField('Day', blank=True)
    # working_time_start = models.ForeignKey(TimeSlot, on_delete=models.SET_NULL, null=True, blank=True, related_name='lawyer_start_time')
    # working_time_end = models.ForeignKey(TimeSlot, on_delete=models.SET_NULL, null=True, blank=True, related_name='lawyer_end_time')
    locations = TaggableManager()
    # budget = models.CharField(max_length=30,blank=False)
    cases_won = models.IntegerField(null=True, blank=True)
    cases_lost = models.IntegerField(null=True, blank=True)
    total_cases_handeled = models.IntegerField(null=True, blank=True)
    currendly_handling = models.IntegerField(null=True, blank=True)
    experience = models.IntegerField(null=True, blank=True)
    court = models.CharField(max_length=200, choices=COURT,blank=True)
    working_hours = models.ManyToManyField(TimeSlot, blank=True)
    
    def get_available_time_slots(self, day_of_week):
        # Retrieve the time slots associated with this lawyer for the given day_of_week
        time_slots = self.working_slots.filter(day=day_of_week).order_by('main_slot')

        # Initialize a list to store available time slots
        available_time_slots = []

        # Iterate through the time slots and generate available slots
        for time_slot in time_slots:
            main_slot_parts = time_slot.main_slot.split(' - ')

            # Ensure that there are two parts (start time and end time)
            if len(main_slot_parts) == 2:
                start_time_str, end_time_str = main_slot_parts

                # Remove leading/trailing spaces
                start_time_str = start_time_str.strip()
                end_time_str = end_time_str.strip()

                # Parse the start and end times
                start_time = datetime.strptime(start_time_str, '%I:%M %p')
                end_time = datetime.strptime(end_time_str, '%I:%M %p')

                while start_time < end_time:
                    available_time_slots.append(start_time.strftime('%I:%M %p'))
                    start_time += timedelta(minutes=15)  # Adjust the slot duration as needed

        return available_time_slots

    # def is_available(self, date, time_slot):
    #     # Check if the selected slot is available for booking on a specific date
    #     return not Appointment.objects.filter(
    #         lawyer=self,
    #         appointment_date=date,
    #         time_slot=time_slot,
    #     ).exists()

    # working_time_start = models.TimeField(null=True, blank=True)
    # working_time_end = models.TimeField(null=True, blank=True)
    # working_time_start = models.ForeignKey(TimeSlot, on_delete=models.SET_NULL, null=True, blank=True, related_name='lawyer_start_time')
    # working_time_end = models.ForeignKey(TimeSlot, on_delete=models.SET_NULL, null=True, blank=True, related_name='lawyer_end_time')

    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.specialization}"
    
    
    
    
    
    
    # def calculate_experience(self):
    #     today = timezone.now().date()
    #     experience = (today - self.start_date).days // 365
    #     return experience
    
    # def calculate_experience(self):
    #     today = timezone.now().date()

    #     if self.start_date:
    #         experience = (today - self.start_date).days // 365
    #     else:
    #         experience = 0

    #     return experience
    
    def is_available(self, selected_date, selected_slot):
        try:
            selected_time = datetime.strptime(selected_slot, '%I:%M %p').time()
        except ValueError:
            return False

        conflicting_appointments = self.appointments.filter(
            appointment_date=selected_date,
            time_slot=selected_time
        )

        return not conflicting_appointments.exists()

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.specialization}"
    
    @property
    def appointments(self):
        return Appointment.objects.filter(lawyer=self)

    def save(self, *args, **kwargs):
        # self.experience = self.calculate_experience()
        super().save(*args, **kwargs)
    
class Certificate(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='certificates/', blank=True, null=True)

    def __str__(self):
        return self.name

class Day(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name    
    
        
        
class ContactEntry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

    
    
class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE)
    details = models.TextField()
    booking_date = models.DateField()
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default="pending")
    original_booking_date = models.DateField(null=True, blank=True)

    def is_confirmed(self):
        return self.status == "confirmed"

    def __str__(self):
        return self.user.email
    
class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    college = models.CharField(max_length=100)
    current_cgpa = models.DecimalField(max_digits=3, decimal_places=2, null=False)
    is_approved = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    
class Internship(models.Model):
    name = models.CharField(max_length=100)
    lawyer_profile = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE, related_name='internships')
    min_cgpa = models.DecimalField(max_digits=3, decimal_places=2)
    start_date = models.DateField()
    duration = models.CharField(max_length=50)
    description = models.TextField()
    roles = models.TextField(help_text="Enter roles as bullet points (one per line)")
    image = models.ImageField(upload_to='internship_images/', blank=False, null=True)


    def __str__(self):
        return self.name
    

class Application(models.Model):
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    application_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student.user.username} - {self.internship.name}'
    
# class StudentUser(CustomUser):
#     is_approved = models.BooleanField(default=False)

class LawyerDayOff(models.Model):
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.lawyer} - {self.date}"
    
    
class HolidayRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    lawyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f'{self.lawyer.username} - {self.date} ({self.status})'
    
    
class Case(models.Model):
    CASE_STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )

    # Auto-generate a unique case number like 1001, 1002, ...
    case_number = models.CharField(max_length=10, unique=True)
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cases', blank=True, null=True)

    # Client information (taken from the CustomUser model)
    client_name = models.CharField(max_length=100, blank=True)
    client_email = models.EmailField(blank=True)
    client_phone = models.CharField(max_length=15, blank=True)
    client_adhar = models.CharField(max_length=12)
    client_adhar_photo = models.ImageField(upload_to='aadhar_photos/', blank=True, null=True)

    # Lawyer details associated with the case
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE, related_name='cases', blank=True, null=True)

    # Incident details
    incident_place = models.CharField(max_length=100)
    incident_date = models.DateField()
    incident_time = models.TimeField()
    witness_name = models.CharField(max_length=100, blank=True)
    witness_details = models.TextField(blank=True)
    incident_description = models.TextField()

    # Case status
    status = models.CharField(max_length=10, choices=CASE_STATUS_CHOICES, default='open')

    def __str__(self):
        return f"Case {self.case_number} ({self.client_name})"
    
    
from django.db import models

class CurrentCase(models.Model):
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE, related_name='current_cases')
    case_number = models.CharField(max_length=10)
    client_name = models.CharField(max_length=100)
    email = models.EmailField()
    phnno = models.CharField(max_length=15)
    incident_description = models.TextField()
    # # Incident details
    incident_place = models.CharField(max_length=100)
    incident_date = models.DateField()
    incident_time = models.TimeField()
    witness_name = models.CharField(max_length=100, blank=True)
    witness_details = models.TextField(blank=True)
    
    

    def __str__(self):
        return f"Case {self.case_number} - {self.client_name}"
    
    
# class Appointment(models.Model):
#     lawyer = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE)
#     client = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
#     appointment_date = models.DateField()
#     status = models.CharField(max_length=20)

#     def __str__(self):
#         return f"Appointment with {self.lawyer.user.first_name} on {self.appointment_date}"

class Appointment(models.Model):
    lawyer = models.ForeignKey('LawyerProfile', on_delete=models.CASCADE)
    client = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=20)# Use TimeSlot model here

    # Add any other fields or methods related to appointments

    def __str__(self):
        return f'Appointment with {self.lawyer} on {self.appointment_date} at {self.time_slot}'