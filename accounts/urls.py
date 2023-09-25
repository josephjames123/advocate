# accounts/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('lawyer/dashboard/', views.lawyer_dashboard, name='lawyer_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('add_lawyer/', views.add_lawyer, name='add_lawyer'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('set/<uidb64>/<token>/', views.custom_password_set_confirm, name='password_reset_confirm'),
    path('lawyer/<int:lawyer_id>/', views.lawyer_details, name='lawyer_details'),
    path('mail/', views.mail, name='mail'),
    path('update/', views.update, name='update'),
    path('add_internship/', views.add_internship, name='add_internship'),
    # path('approve_student/<int:student_id>/', views.approve_student, name='approve_student'),
    path('approve_students/', views.approve_students, name='approve_students'),
    path('student/save/', views.student_save, name='student_save'),
    path('lawyer/save/', views.lawyer_save, name='lawyer_save'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('case_saved/', views.case_saved, name='case_saved'),
    path('update_lawyer_profile/<int:user_id>/', views.update_lawyer_profile, name='update_lawyer_profile'),
    path('profile/', views.profile, name='profile'),
    path('client_bookings/<int:client_id>/', views.client_bookings, name='client_bookings'),
    path('list-student-requests/', views.list_student_requests, name='list_student_requests'),
    path('approve-student/<int:student_id>/', views.approve_student, name='approve_student'),
    path('reject-student/<int:student_id>/', views.reject_student, name='reject_student'),
    path('set_password/<str:uidb64>/<str:token>/', views.password_reset_confirm_student, name='password_reset_confirm_student'),
]



   
    

