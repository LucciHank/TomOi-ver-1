from django.conf import settings
from django.db import models
from store.models import Product
from django.utils import timezone
from django.db.models import Avg
from django.contrib.auth import get_user_model

User = get_user_model()

class Source(models.Model):
    """Nguồn cung cấp sản phẩm"""
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('zalo', 'Zalo'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('discord', 'Discord'),
        ('telegram', 'Telegram'),
        ('other', 'Khác'),
    ]
    
    PRIORITY_CHOICES = [
        (1, '1 - Cao nhất'),
        (2, '2 - Cao'),
        (3, '3 - Trung bình'),
        (4, '4 - Thấp'),
        (5, '5 - Thấp nhất'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Tên nguồn")
    url = models.URLField(blank=True, verbose_name="URL nguồn")
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='other', verbose_name="Nền tảng")
    product_type = models.CharField(max_length=100, blank=True, verbose_name="Loại sản phẩm")
    base_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Giá chuẩn")
    availability_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Tỷ lệ có hàng (%)")
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3, verbose_name="Mức độ ưu tiên")
    notes = models.TextField(blank=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_avg_processing_time(self):
        """Tính thời gian xử lý trung bình"""
        avg_time = self.logs.aggregate(avg_time=Avg('processing_time'))['avg_time']
        return avg_time or 0
    
    def get_availability_status(self):
        """Trả về trạng thái có hàng dựa trên tỷ lệ"""
        if self.availability_rate >= 80:
            return "Cao"
        elif self.availability_rate >= 50:
            return "Trung bình"
        else:
            return "Thấp"
    
    def format_base_price(self):
        """Format giá với dấu phân cách hàng nghìn"""
        return "{:,.0f}".format(self.base_price)

    @property
    def last_contact(self):
        """Thời gian liên hệ cuối cùng"""
        last_log = SourceLog.objects.filter(source=self).order_by('-created_at').first()
        if last_log:
            return last_log.created_at
        return None

    class Meta:
        verbose_name = "Nguồn nhập"
        verbose_name_plural = "Nguồn nhập"
        ordering = ['priority', 'name']

class SourceProduct(models.Model):
    """Sản phẩm từ nguồn cụ thể"""
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='products', verbose_name="Nguồn nhập")
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE, related_name='source_products', verbose_name="Sản phẩm")
    name = models.CharField(max_length=255, verbose_name="Tên sản phẩm tại nguồn")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    product_url = models.URLField(blank=True, verbose_name="URL sản phẩm")
    price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Giá nhập")
    error_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Tỷ lệ lỗi (%)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.source.name} - {self.name}"
    
    def format_price(self):
        """Format giá với dấu phân cách hàng nghìn"""
        return "{:,.0f}".format(self.price)
    
    class Meta:
        verbose_name = "Sản phẩm nguồn"
        verbose_name_plural = "Sản phẩm nguồn"
        unique_together = ('source', 'product')

class SourceLog(models.Model):
    """Log hoạt động với nguồn"""
    STATUS_CHOICES = [
        ('available', 'Có hàng'),
        ('unavailable', 'Không có hàng'),
        ('pending', 'Đang chờ'),
        ('processing', 'Đang xử lý'),
    ]
    
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='logs', verbose_name="Nguồn nhập")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Giá")
    processing_time = models.IntegerField(default=0, verbose_name="Thời gian xử lý (phút)")
    notes = models.TextField(blank=True, verbose_name="Ghi chú")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.source.name} - {self.get_status_display()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    def format_price(self):
        """Format giá với dấu phân cách hàng nghìn"""
        return "{:,.0f}".format(self.price)
    
    class Meta:
        verbose_name = "Nhật ký nguồn"
        verbose_name_plural = "Nhật ký nguồn"
        ordering = ['-created_at'] 