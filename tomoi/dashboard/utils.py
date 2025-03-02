from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_order_status_email(order):
    """Send email notification when order status changes"""
    subject = f'Cập nhật trạng thái đơn hàng #{order.id}'
    
    context = {
        'order': order,
        'status': order.get_status_display()
    }
    
    html_message = render_to_string('dashboard/emails/order_status.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        html_message=html_message
    ) 