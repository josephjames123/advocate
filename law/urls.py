# law/urls.py
from django.contrib import admin
from django.urls import path, include 
from accounts import views  
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('lawyerlist/', views.lawyer_list, name='lawyer_list'),
    path('about/', views.about, name='about'),
    path('practice/', views.practice, name='practice'),
    path('contact/', views.contact, name='contact'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')), 
    path('accounts/', include('allauth.urls')),
    # path('logout/', LogoutView.as_view(), name='logout'), 
    path('error/', views.error, name='error'),
    path('book/', views.book, name='book'),
    path('submit/', views.submit, name='submit'),
    path('book_lawyer/<int:lawyer_id>/', views.book_lawyer, name='book_lawyer'),
    path('booking/<int:booking_id>/', views.booking_details, name='booking_details'),
    path('internship/<int:internship_id>/', views.internship_detail, name='internship_detail'),
    path('mark_holiday/', views.mark_holiday, name='mark_holiday'),
    path('reschedule/<int:booking_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('bookings/', views.all_bookings, name='all_bookings'),
    path('bookings/lawyer/<int:lawyer_id>/', views.all_bookings, name='lawyer_bookings'),
    path('bookings/client/<int:client_id>/', views.all_bookings, name='client_bookings'),
    path('lawyers_list/', views.list_lawyers, name='list_lawyers'),
    path('admin_view_holiday_requests/', views.admin_view_holiday_requests, name='admin_view_holiday_requests'),
    path('admin_approve_reject_holiday/<int:request_id>/', views.admin_approve_reject_holiday, name='admin_approve_reject_holiday'),
    path('enter_client_email/', views.enter_client_email, name='enter_client_email'),
    path('enter_case_details/<int:client_id>/<int:lawyer_id>/', views.enter_case_details, name='enter_case_details'),
    path('case_detail/<int:case_id>/', views.case_detail, name='case_detail'),
    path('current_cases/', views.current_cases, name='current_cases'),
    path('list_cases/', views.list_cases, name='list_cases'),
    path('search-lawyers/', views.search_lawyers, name='search-lawyers'),
    path('assign-working-hours/', views.assign_working_hours, name='assign_working_hours'),
    path('select-date/<int:lawyer_id>/', views.select_date, name='select_date'),
    path('book_lawyer/<int:lawyer_id>/<str:selected_date>/', views.book_lawyer, name='book_lawyer'),
    # path('payment-confirmation/<str:order_id>/', views.payment_confirmation, name='payment_confirmation'),
    # path('payment-confirmation/<int:appointment_id>/', views.payment_confirmation, name='payment_confirmation'),
    path('google', TemplateView.as_view(template_name="auth.html")),
    path('intern/', views.intern, name='intern'),
    path('generate-pdf/<int:appointment_id>/', views.generate_appointment_pdf, name='generate_appointment_pdf'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    # path("callback/", views.callback, name="callback"),
    path('callback/<int:appointment_id>/', views.callback, name='callback'),
    path('case_detail/<int:case_number>/', views.case_detail, name='case_detail'),
    path('cases/<int:case_number>/add-update/', views.add_case_update, name='add_case_update'),
    path('students/', views.students, name='students'),
    path('hire_student/<int:student_id>/', views.hire_student, name='hire_student'),
    path('assign_work/', views.assign_work, name='assign_work'),
    path('work-assignments/', views.student_work_assignments, name='student_work_assignments'),
        # path('task-page/', views.task_page, name='task_page'),
    path('mark_casual_leave/', views.mark_leave_request, {'leave_type': 'casual_leave'}, name='mark_casual_leave'),
    path('leave_reports/', views.leave_reports, name='leave_reports'),
    path('download_leave_reports_pdf/', views.download_leave_reports_pdf, name='download_leave_reports_pdf'),
    path('generate_leave_reports_admin_pdf/', views.generate_leave_reports_admin_pdf, name='generate_leave_reports_admin_pdf'),
    path('business_laws',views.business_laws, name='business_laws'),
    path('tax_laws',views.tax_laws, name='tax_laws'),
    path('emp_laws',views.emp_laws, name='emp_laws'),
    path('ip_laws',views.ip_laws, name='ip_laws'),
    path('contract_laws',views.contract_laws, name='contract_laws'),
    path('realestate_laws',views.realestate_laws, name='realestate_laws'),
    path('security_laws',views.security_laws, name='security_laws'),
    path('consumer_laws',views.consumer_laws, name='consumer_laws'),
    path('health_laws',views.health_laws, name='health_laws'),
    path('common',views.common, name='common'),
    path('internship/payment/<int:student_id>/<int:internship_id>/', views.internship_payment, name='internship_payment'),
    # path('internship_payment_callback/<int:razorpay_order_id>/', views.internship_payment_callback, name='internship_payment_callback'),
    path('internship_payment_callback/<int:student_id>/', views.internship_payment_callback, name='internship_payment_callback'),
    path('student/<int:student_id>/', views.students_info, name='students_info'),
    path('fine/payment/<int:student_id>/<int:workassignment_id>/', views.pay_fine, name='pay_fine'),
    path('fine_payment_callback/<int:student_id>/', views.fine_payment_callback, name='fine_payment_callback'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)