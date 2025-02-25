from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_payment_confirmation_email(transaction):
    """Gửi email xác nhận thanh toán"""
    try:
        # Chuẩn bị context cho template email
        context = {
            'user': transaction.user,
            'transaction_id': transaction.transaction_id,
            'amount': transaction.amount,
            'payment_method': transaction.get_payment_method_display(),
            'created_at': transaction.created_at,
            'items': transaction.items.all() if hasattr(transaction, 'items') else [],
            'settings': settings
        }

        # Render email template
        html_message = render_to_string('payment/email/payment_confirmation.html', context)
        plain_message = strip_tags(html_message)

        # Gửi email
        send_mail(
            subject=f'Xác nhận thanh toán - {transaction.transaction_id}',
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[transaction.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Failed to send payment confirmation email: {str(e)}")
        return False

def get_client_ip(request):
    """Lấy IP của client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def format_currency(amount):
    """Format số tiền theo định dạng tiền tệ VND"""
    try:
        return f"{int(amount):,}đ".replace(',', '.')
    except (ValueError, TypeError):
        return "0đ" 