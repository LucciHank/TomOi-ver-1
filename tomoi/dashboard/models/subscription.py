from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta

def get_default_expiry_date():
    return timezone.now() + timedelta(days=30)

class SubscriptionPlan(models.Model):
    """Mô hình gói đăng ký"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(help_text="Thời hạn sử dụng tính bằng ngày")
    features = models.JSONField(default=list, help_text="Danh sách tính năng của gói")
    max_warranty_count = models.IntegerField(default=3, help_text="Số lần bảo hành tối đa")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class UserSubscription(models.Model):
    """Gói đăng ký của người dùng"""
    STATUS_CHOICES = [
        ('active', 'Đang hoạt động'),
        ('pending', 'Chờ thanh toán'),
        ('expired', 'Đã hết hạn'),
        ('cancelled', 'Đã hủy')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=get_default_expiry_date)
    warranty_count = models.IntegerField(default=0, help_text="Số lần đã sử dụng bảo hành")
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    
    def is_active(self):
        return self.status == 'active' and self.end_date > timezone.now()
    
    def days_left(self):
        if not self.is_active():
            return 0
        delta = self.end_date - timezone.now()
        return max(0, delta.days)

class SubscriptionTransaction(models.Model):
    """Lịch sử giao dịch gói đăng ký"""
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Chuyển khoản ngân hàng'),
        ('credit_card', 'Thẻ tín dụng'),
        ('paypal', 'PayPal'),
        ('momo', 'Ví MoMo'),
        ('vnpay', 'VNPay'),
        ('zalopay', 'ZaloPay'),
        ('other', 'Khác')
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('completed', 'Hoàn thành'),
        ('failed', 'Thất bại'),
        ('refunded', 'Hoàn tiền')
    ]
    
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.subscription.user.username}" 