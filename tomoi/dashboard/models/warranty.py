from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import uuid
from store.models import Product, Order

class WarrantyTicket(models.Model):
    """Vé bảo hành sản phẩm"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='warranty_tickets', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='warranty_tickets')
    issue_description = models.TextField(verbose_name="Mô tả vấn đề")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Đang chờ xử lý'),
        ('in_progress', 'Đang xử lý'),
        ('resolved', 'Đã giải quyết'),
        ('closed', 'Đã đóng')
    ], default='pending')
    resolution = models.TextField(blank=True, null=True, verbose_name="Cách giải quyết")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                               null=True, blank=True, related_name='assigned_tickets')
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.customer.username} - {self.status}"

class WarrantyHistory(models.Model):
    """Lịch sử xử lý bảo hành"""
    ticket = models.ForeignKey(WarrantyTicket, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=100, verbose_name="Hành động")
    notes = models.TextField(blank=True, verbose_name="Ghi chú")
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.action} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        # Ghi đè phương thức save để không gọi các hàm không còn tồn tại
        super().save(*args, **kwargs)
        
    def send_new_ticket_notification(self):
        """Gửi thông báo khi có ticket bảo hành mới"""
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        
        # Gửi email thông báo cho admin
        admin_email = getattr(settings, 'WARRANTY_EMAIL', settings.DEFAULT_FROM_EMAIL)
        subject = f"Yêu cầu bảo hành mới: {self.subscription.user.username} - #{self.ticket_id}"
        
        context = {
            'ticket': self,
            'subscription': self.subscription,
            'user': self.subscription.user,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else '',
        }
        
        message = render_to_string('dashboard/emails/new_warranty_notification.html', context)
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            html_message=message,
            fail_silently=True
        )
        
        # Gửi email xác nhận cho khách hàng
        customer_subject = f"Đã nhận yêu cầu bảo hành #{self.ticket_id}"
        customer_message = render_to_string('dashboard/emails/warranty_confirmation.html', context)
        
        send_mail(
            customer_subject,
            customer_message,
            settings.DEFAULT_FROM_EMAIL,
            [self.subscription.user.email],
            html_message=customer_message,
            fail_silently=True
        ) 