from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('user-info/', views.user_info, name='user_info'),
    path('security/', views.security_view, name='security'),
    path('settings/', views.settings_view, name='settings'),
    path('order-history/', views.order_history, name='order_history'),
    path('payment-history/', views.payment_history, name='payment_history'),
    # ... các URL khác
] 