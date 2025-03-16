from django.db import models
from django.utils import timezone

class Banner(models.Model):
    """Model cho banner quảng cáo"""
    POSITION_CHOICES = [
        ('home_top', 'Trang chủ - Trên cùng'),
        ('home_middle', 'Trang chủ - Giữa trang'),
        ('home_bottom', 'Trang chủ - Dưới cùng'),
        ('sidebar', 'Sidebar'),
        ('category', 'Trang danh mục'),
        ('product', 'Trang sản phẩm'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Tiêu đề")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    image = models.ImageField(upload_to='banners/', verbose_name="Hình ảnh")
    url = models.URLField(blank=True, null=True, verbose_name="Đường dẫn")
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, verbose_name="Vị trí hiển thị")
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Ngày bắt đầu")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Ngày kết thúc")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    
    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_expired(self):
        """Kiểm tra xem banner đã hết hạn chưa"""
        if not self.end_date:
            return False
        return timezone.now() > self.end_date 