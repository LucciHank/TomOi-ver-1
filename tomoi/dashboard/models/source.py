from django.conf import settings
from django.db import models
from django.utils import timezone
from django.db.models import Avg
from django.contrib.auth import get_user_model

User = get_user_model()

class Source(models.Model):
    """Nguồn cung cấp sản phẩm"""
    PLATFORM_CHOICES = [
        ('netflix', 'Netflix'),
        ('spotify', 'Spotify'),
        ('youtube', 'YouTube'),
        ('disney', 'Disney+'),
        ('apple', 'Apple TV+'),
        ('hbo', 'HBO GO'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Cao'),
        (2, 'Trung bình'),
        (3, 'Thấp'),
    ]
    
    name = models.CharField(max_length=255, verbose_name="Tên nguồn")
    url = models.URLField(verbose_name="URL nguồn")
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, verbose_name="Nền tảng")
    product_type = models.CharField(max_length=50, verbose_name="Loại sản phẩm")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá chuẩn")
    availability_rate = models.IntegerField(default=100, verbose_name="Tỷ lệ có hàng (%)")
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2, verbose_name="Mức độ ưu tiên")
    notes = models.TextField(blank=True, verbose_name="Ghi chú")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
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
        verbose_name = "Nguồn cung cấp"
        verbose_name_plural = "Nguồn cung cấp"
        ordering = ['priority', 'name']

class SourceProduct(models.Model):
    """Sản phẩm từ nguồn cụ thể"""
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='products', verbose_name="Nguồn nhập")
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE, verbose_name="Sản phẩm")
    name = models.CharField(max_length=255, verbose_name="Tên sản phẩm tại nguồn")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    product_url = models.URLField(blank=True, verbose_name="URL sản phẩm")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá nhập")
    error_rate = models.IntegerField(default=0, verbose_name="Tỷ lệ lỗi (%)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.source.name} - {self.name}"
    
    def format_price(self):
        """Format giá với dấu phân cách hàng nghìn"""
        return "{:,.0f}".format(self.price)
    
    class Meta:
        verbose_name = "Sản phẩm từ nguồn"
        verbose_name_plural = "Sản phẩm từ nguồn"
        unique_together = ('source', 'product')

class SourceLog(models.Model):
    """Log hoạt động với nguồn"""
    LOG_TYPE_CHOICES = [
        ('check', 'Kiểm tra'),
        ('purchase', 'Mua hàng'),
        ('error', 'Lỗi'),
    ]
    
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='logs', verbose_name="Nguồn nhập")
    source_product = models.ForeignKey(SourceProduct, on_delete=models.CASCADE, related_name='logs', verbose_name="Sản phẩm nguồn")
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES, verbose_name="Loại log")
    has_stock = models.BooleanField(default=True, verbose_name="Có hàng")
    processing_time = models.IntegerField(help_text="Thời gian xử lý (giây)", verbose_name="Thời gian xử lý (giây)")
    notes = models.TextField(blank=True, verbose_name="Ghi chú")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.source.name} - {self.get_log_type_display()} - {self.created_at}"
    
    def format_price(self):
        """Format giá với dấu phân cách hàng nghìn"""
        return "{:,.0f}".format(self.price)
    
    class Meta:
        verbose_name = "Log nguồn"
        verbose_name_plural = "Log nguồn"
        ordering = ['-created_at'] 