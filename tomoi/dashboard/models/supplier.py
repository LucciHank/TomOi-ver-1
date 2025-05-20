from django.db import models
from django.utils import timezone

class Supplier(models.Model):
    """Model nhà cung cấp sản phẩm"""
    
    STATUS_CHOICES = (
        ('active', 'Đang hợp tác'),
        ('inactive', 'Ngừng hợp tác'),
        ('pending', 'Đang đàm phán'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('bank', 'Chuyển khoản ngân hàng'),
        ('cash', 'Tiền mặt'),
        ('credit', 'Công nợ'),
        ('other', 'Khác'),
    )
    
    name = models.CharField(max_length=255, verbose_name="Tên nhà cung cấp")
    code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã nhà cung cấp")
    contact_person = models.CharField(max_length=255, blank=True, null=True, verbose_name="Người liên hệ")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")
    website = models.URLField(blank=True, null=True, verbose_name="Website")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Trạng thái")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='bank', verbose_name="Phương thức thanh toán")
    payment_term = models.IntegerField(default=0, help_text="Số ngày thanh toán", verbose_name="Kỳ hạn thanh toán")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Tự động tạo mã nhà cung cấp nếu chưa có
        if not self.code:
            prefix = 'SUPP'
            date_str = timezone.now().strftime('%y%m')
            # Lấy mã cuối cùng và tăng lên 1
            last_supplier = Supplier.objects.filter(code__startswith=f"{prefix}{date_str}").order_by('-code').first()
            if last_supplier and last_supplier.code and len(last_supplier.code) >= 10:
                try:
                    num = int(last_supplier.code[-3:]) + 1
                except ValueError:
                    num = 1
            else:
                num = 1
            self.code = f"{prefix}{date_str}{num:03d}"
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Nhà cung cấp"
        verbose_name_plural = "Nhà cung cấp"
        ordering = ['name'] 
 
 