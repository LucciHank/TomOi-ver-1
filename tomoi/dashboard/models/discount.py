from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid

def get_default_expiry_date():
    from datetime import timedelta
    return timezone.now() + timedelta(days=30)

class Discount(models.Model):
    """Model for discount codes"""
    DISCOUNT_TYPES = [
        ('percentage', 'Phần trăm'),
        ('fixed', 'Giá trị cố định'),
    ]
    
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    
    # Ràng buộc sử dụng
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.IntegerField(null=True, blank=True, help_text="Số lần mã giảm giá có thể được sử dụng")
    used_count = models.IntegerField(default=0)
    
    # Thời gian hiệu lực
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(default=get_default_expiry_date)
    
    # Trạng thái
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.code

class UserDiscount(models.Model):
    """Discount assigned to specific users"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.discount.code}"

class DiscountUsage(models.Model):
    """Detailed record of discount usage"""
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey('store.Order', on_delete=models.SET_NULL, null=True)
    used_at = models.DateTimeField(auto_now_add=True)
    amount_saved = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.discount.code} used on {self.used_at}"