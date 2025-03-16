from django.db import models
from django.utils import timezone
from django.conf import settings

class SourceHistory(models.Model):
    """Lịch sử hoạt động của nguồn cung cấp."""
    
    LOG_TYPE_CHOICES = (
        ('source_created', 'Tạo nguồn mới'),
        ('source_updated', 'Cập nhật nguồn'),
        ('order', 'Đặt hàng'),
        ('availability_check', 'Kiểm tra hàng'),
        ('price_updated', 'Cập nhật giá'),
        ('other', 'Khác'),
    )
    
    ACCOUNT_TYPE_CHOICES = (
        ('new_account', 'Tài khoản cấp mới'),
        ('upgrade', 'Up chính chủ'),
        ('activation_code', 'Code kích hoạt'),
        ('other', 'Khác'),
    )
    
    source = models.ForeignKey(
        'dashboard.Source', 
        on_delete=models.CASCADE, 
        related_name='histories',
        verbose_name='Nguồn cung cấp'
    )
    source_product = models.ForeignKey(
        'dashboard.SourceProduct',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='histories',
        verbose_name='Sản phẩm nguồn'
    )
    products = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Danh sách sản phẩm'
    )
    log_type = models.CharField(
        max_length=20,
        choices=LOG_TYPE_CHOICES,
        default='other',
        verbose_name='Loại nhật ký'
    )
    has_stock = models.BooleanField(
        default=True,
        verbose_name='Có hàng'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Số lượng'
    )
    price = models.PositiveIntegerField(
        default=0,
        verbose_name='Giá'
    )
    processing_time = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Thời gian xử lý (phút)'
    )
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        default='new_account',
        blank=True,
        verbose_name='Hình thức nhập'
    )
    account_username = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Tài khoản chính chủ'
    )
    account_password = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Mật khẩu'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Ghi chú'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Thời gian tạo'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_histories',
        verbose_name='Người tạo'
    )
    
    class Meta:
        verbose_name = 'Lịch sử nguồn'
        verbose_name_plural = 'Lịch sử nguồn'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_log_type_display()} - {self.source.name} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def formatted_price(self):
        """Định dạng giá với dấu phân cách hàng nghìn."""
        return f"{self.price:,}" 