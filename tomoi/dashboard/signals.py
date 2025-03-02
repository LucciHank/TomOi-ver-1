from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.warranty import WarrantyTicket, WarrantyHistory
from .models.subscription import UserSubscription
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

@receiver(post_save, sender=WarrantyTicket)
def handle_warranty_ticket_update(sender, instance, created, **kwargs):
    """Xử lý khi yêu cầu bảo hành được cập nhật"""
    if not created and instance.status != 'pending':
        # Chỉ gửi email khi trạng thái thay đổi và không phải là yêu cầu mới
        
        # Gửi email thông báo cập nhật trạng thái cho khách hàng
        subject = f"Cập nhật trạng thái bảo hành #{instance.id}"
        
        context = {
            'ticket': instance,
            'user': instance.subscription.user,
            'subscription': instance.subscription,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else '',
        }
        
        message = render_to_string('dashboard/emails/warranty_status_update.html', context)
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.subscription.user.email],
            html_message=message,
            fail_silently=True
        )
        
        # Tăng số lần bảo hành nếu chưa được tăng
        if instance.status in ['resolved', 'rejected'] and not hasattr(instance, '_warranty_count_increased'):
            subscription = instance.subscription
            subscription.warranty_count += 1
            subscription.save(update_fields=['warranty_count'])
            instance._warranty_count_increased = True 