from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    product_code = models.CharField(max_length=50, blank=True, null=True)
    label = models.ForeignKey('ProductLabel', on_delete=models.SET_NULL, null=True, blank=True)
    duration = models.CharField(max_length=20, choices=[
        ('1_DAY', '1 ngày'),
        ('1_WEEK', '1 tuần'),
        ('1_MONTH', '1 tháng'),
        ('3_MONTHS', '3 tháng'),
        ('6_MONTHS', '6 tháng'),
        ('12_MONTHS', '1 năm'),
    ], default='1_MONTH')
    features = models.JSONField(default=list, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    requires_email = models.BooleanField(
        default=False,
        verbose_name="Yêu cầu Email",
        help_text="Khách hàng cần cung cấp email để nâng cấp"
    )
    requires_account_password = models.BooleanField(
        default=False,
        verbose_name="Yêu cầu Tài khoản & Mật khẩu",
        help_text="Khách hàng cần cung cấp tài khoản và mật khẩu để nâng cấp"
    )
    is_cross_sale = models.BooleanField(default=False)
    cross_sale_products = models.ManyToManyField('self', blank=True)
    cross_sale_discount = models.IntegerField(default=0, help_text="Phần trăm giảm giá khi mua kèm")

    class Meta:
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'

    def __str__(self):
        return self.name
        
    def get_duration_display(self):
        """Trả về text hiển thị thời hạn"""
        duration_dict = dict([
            ('1_DAY', '1 ngày'),
            ('1_WEEK', '1 tuần'),
            ('1_MONTH', '1 tháng'),
            ('3_MONTHS', '3 tháng'),
            ('6_MONTHS', '6 tháng'),
            ('12_MONTHS', '1 năm'),
        ])
        return duration_dict.get(self.duration, self.duration)
        
    def get_discount_percentage(self):
        """Tính phần trăm giảm giá"""
        if self.old_price and self.price:
            discount = ((self.old_price - self.price) / self.old_price) * 100
            return round(discount)
        return 0
        
    def get_main_image_url(self):
        main_image = self.images.filter(is_primary=True).first()
        if main_image:
            return main_image.image.url
        # Trả về ảnh mặc định nếu không có ảnh chính
        return '/static/images/default-product.jpg'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Hình ảnh sản phẩm'
        verbose_name_plural = 'Hình ảnh sản phẩm'

    def __str__(self):
        return f"Ảnh cho {self.product.name} {'(Chính)' if self.is_primary else ''}"


class ProductChangeLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Tạo mới'),
        ('update', 'Cập nhật'),
        ('delete', 'Xóa'),
        ('status_change', 'Thay đổi trạng thái'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='change_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Lịch sử thay đổi sản phẩm'
        verbose_name_plural = 'Lịch sử thay đổi sản phẩm'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_action_display()} sản phẩm {self.product.name} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Thương hiệu'
        verbose_name_plural = 'Thương hiệu'

    def __str__(self):
        return self.name


class ProductLabel(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default='primary')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Nhãn sản phẩm'
        verbose_name_plural = 'Nhãn sản phẩm'
    
    def __str__(self):
        return self.name 