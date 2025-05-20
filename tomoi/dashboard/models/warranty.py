from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import uuid
from store.models import Product, Order
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

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

class WarrantyReason(models.Model):
    """
    Mô hình lưu trữ các lý do bảo hành
    """
    name = models.CharField(_('Tên lý do'), max_length=255)
    description = models.TextField(_('Mô tả'), blank=True, null=True)
    is_active = models.BooleanField(_('Đang hoạt động'), default=True)
    created_at = models.DateTimeField(_('Ngày tạo'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Ngày cập nhật'), auto_now=True)

    class Meta:
        verbose_name = _('Lý do bảo hành')
        verbose_name_plural = _('Lý do bảo hành')
        ordering = ['name']

    def __str__(self):
        return self.name

class WarrantyService(models.Model):
    """
    Mô hình lưu trữ các dịch vụ bảo hành
    """
    name = models.CharField(_('Tên dịch vụ'), max_length=255)
    description = models.TextField(_('Mô tả'), blank=True, null=True)
    price = models.DecimalField(_('Giá dịch vụ'), max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(_('Đang hoạt động'), default=True)
    created_at = models.DateTimeField(_('Ngày tạo'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Ngày cập nhật'), auto_now=True)

    class Meta:
        verbose_name = _('Dịch vụ bảo hành')
        verbose_name_plural = _('Dịch vụ bảo hành')
        ordering = ['name']

    def __str__(self):
        return self.name

class WarrantyRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
        ('rejected', 'Từ chối'),
        ('cancelled', 'Đã hủy')
    ]
    
    PLATFORM_CHOICES = [
        ('netflix', 'Netflix'),
        ('spotify', 'Spotify'),
        ('youtube', 'YouTube'),
        ('disney', 'Disney+'),
        ('apple', 'Apple TV+'),
        ('hbo', 'HBO GO')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey('store.Order', on_delete=models.CASCADE)
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE)
    account_username = models.CharField(max_length=255)
    account_password = models.CharField(max_length=255)
    account_type = models.CharField(max_length=50)
    reason = models.ForeignKey('WarrantyReason', on_delete=models.SET_NULL, null=True)
    custom_reason = models.TextField(blank=True, null=True)
    error_screenshot = models.ImageField(upload_to='warranty/screenshots/', null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    source = models.ForeignKey('dashboard.Source', on_delete=models.SET_NULL, null=True, blank=True)
    is_self_registered = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Yêu cầu bảo hành'
        verbose_name_plural = 'Yêu cầu bảo hành'
    
    def __str__(self):
        return f"Bảo hành - {self.user.username} - {self.product.name}"

class WarrantyRequestHistory(models.Model):
    """
    Mô hình lưu trữ lịch sử xử lý yêu cầu bảo hành, bao gồm các thông tin chi tiết về xử lý
    """
    WARRANTY_TYPE_CHOICES = (
        ('new_account', _('Cấp tài khoản mới')),
        ('fix', _('Sửa chữa')),
        ('refund', _('Hoàn tiền')),
        ('add_days', _('Bù thêm ngày')),
    )
    
    warranty_request = models.ForeignKey(
        WarrantyRequest,
        on_delete=models.CASCADE,
        related_name='request_histories',
        verbose_name=_('Yêu cầu bảo hành')
    )
    
    status = models.CharField(_('Trạng thái'), max_length=20, choices=WarrantyRequest.STATUS_CHOICES)
    notes = models.TextField(_('Ghi chú cho khách'), blank=True, null=True)
    admin_notes = models.TextField(_('Ghi chú nội bộ'), blank=True, null=True)
    
    # Các trường cho loại xử lý bảo hành
    warranty_types = models.JSONField(_('Loại bảo hành'), default=list, blank=True, null=True)
    
    # Thông tin bổ sung khi bù thêm ngày
    added_days = models.IntegerField(_('Số ngày bù thêm'), default=0)
    
    # Thông tin bổ sung khi hoàn tiền
    refund_amount = models.DecimalField(_('Số tiền hoàn trả'), max_digits=10, decimal_places=2, default=0)
    
    # Thông tin bổ sung khi cấp tài khoản mới
    new_account_info = models.JSONField(_('Thông tin tài khoản mới'), blank=True, null=True)
    
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='warranty_request_histories',
        verbose_name=_('Admin xử lý')
    )
    
    created_at = models.DateTimeField(_('Ngày tạo'), auto_now_add=True)

    class Meta:
        verbose_name = _('Lịch sử xử lý bảo hành')
        verbose_name_plural = _('Lịch sử xử lý bảo hành')
        ordering = ['-created_at']

    def __str__(self):
        return f"Lịch sử xử lý #{self.id} - {self.warranty_request}"

@receiver(post_save, sender=WarrantyRequest)
def update_warranty_status(sender, instance, created, **kwargs):
    """Tạo lịch sử khi trạng thái thay đổi"""
    if not created:
        # Lấy bản ghi cũ từ CSDL
        old_instance = WarrantyRequest.objects.get(id=instance.id)
        
        # Kiểm tra xem trạng thái có thay đổi không
        if old_instance.status != instance.status:
            # Tạo bản ghi lịch sử
            WarrantyHistory.objects.create(
                warranty_request=instance,
                status=instance.status,
                notes=f"Trạng thái đã thay đổi từ {old_instance.get_status_display()} sang {instance.get_status_display()}"
            ) 