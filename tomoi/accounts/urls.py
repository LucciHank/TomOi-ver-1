from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('social-login/', views.social_login, name='social_login'),
    path('auth/', views.auth, name='auth'),

    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('send-otp/', views.send_otp, name='send_otp'),

    path('register_verify/', views.register_verify, name='register_verify'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),

    path('profile/update/', views.update_profile, name='update_profile'),
]