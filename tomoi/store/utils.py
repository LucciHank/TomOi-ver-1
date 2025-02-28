from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal

def send_payment_confirmation_email(user, order):
    subject = "Xác nhận thanh toán thành công"
    message = f"Xin chào {user.username},\n\n"
    message += f"Bạn đã thanh toán thành công đơn hàng #{order.id}.\n"
    message += f"Tổng tiền: {order.total_amount} VND\n"
    message += f"Chi tiết tài khoản đã mua: {order.purchased_account.details}\n\n"
    message += "Cảm ơn bạn đã mua hàng tại cửa hàng của chúng tôi!"
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

def get_client_ip(request):
    """Lấy IP của client từ request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

