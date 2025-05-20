from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid
from django.contrib.auth import get_user_model
import json

User = get_user_model()

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
    discount = models.ForeignKey('store.Discount', on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.discount.code}"

class DiscountUsage(models.Model):
    """Detailed record of discount usage"""
    discount = models.ForeignKey('store.Discount', on_delete=models.CASCADE, related_name='dashboard_usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey('store.Order', on_delete=models.SET_NULL, null=True)
    used_at = models.DateTimeField(auto_now_add=True)
    amount_saved = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.discount.code} used on {self.used_at}"

class DiscountHistory(models.Model):
    """Lưu trữ lịch sử thay đổi của mã giảm giá"""
    ACTION_CHOICES = (
        ('create', 'Tạo mới'),
        ('update', 'Cập nhật'),
        ('delete', 'Xóa'),
        ('activate', 'Kích hoạt'),
        ('deactivate', 'Vô hiệu hóa'),
    )
    
    discount = models.ForeignKey('store.Discount', on_delete=models.CASCADE, related_name='history', null=True, blank=True)
    discount_code = models.CharField(max_length=50, verbose_name="Mã giảm giá")
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Loại hành động", default='update')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người thực hiện")
    changes_json = models.TextField(blank=True, null=True, verbose_name="Chi tiết thay đổi (JSON)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian thực hiện")
    
    class Meta:
        verbose_name = "Lịch sử mã giảm giá"
        verbose_name_plural = "Lịch sử mã giảm giá"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.discount_code} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def changes(self):
        if not self.changes_json:
            return {}
        try:
            return json.loads(self.changes_json)
        except json.JSONDecodeError:
            return {}

class DiscountBackup(models.Model):
    """Lưu trữ bản sao lưu mã giảm giá"""
    name = models.CharField(max_length=100, verbose_name="Tên bản sao lưu")
    backup_data = models.TextField(verbose_name="Dữ liệu sao lưu (JSON)")
    include_usage = models.BooleanField(default=False, verbose_name="Bao gồm lịch sử sử dụng")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian tạo")
    file_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="Đường dẫn file")
    
    class Meta:
        verbose_name = "Bản sao lưu mã giảm giá"
        verbose_name_plural = "Bản sao lưu mã giảm giá"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    def get_discount_count(self):
        """Trả về số lượng mã giảm giá trong bản sao lưu"""
        try:
            data = json.loads(self.backup_data)
            return len(data.get('discounts', []))
        except json.JSONDecodeError:
            return 0
        except Exception:
            return 0