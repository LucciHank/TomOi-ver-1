from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('vnpay/', views.vnpay_payment, name='vnpay_payment'),
    path('vnpay/return/', views.vnpay_return, name='vnpay_return'),
    path('installment/info/', views.get_installment_info, name='installment_info'),
    path('installment/init/', views.init_installment, name='init_installment'),
    path('installment-return/', views.installment_return, name='installment_return'),
    path('installment-cancel/', views.installment_cancel, name='installment_cancel'),
    path('installment-ipn/', views.installment_ipn, name='installment_ipn'),
    path('qr-payment/', views.qr_payment, name='qr_payment'),
    path('check-status/<str:order_id>/', views.check_payment_status, name='check_payment_status'),
] 