from django.db import models
from django.utils.text import slugify


class ProductAttribute(models.Model):
    """Model lưu trữ thuộc tính sản phẩm (ví dụ: Loại, Màu sắc, Kích thước...)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên thuộc tính")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    display_order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Thuộc tính sản phẩm"
        verbose_name_plural = "Thuộc tính sản phẩm"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Đảm bảo tên thuộc tính là duy nhất"""
        self.name = self.name.strip()
        super().save(*args, **kwargs)
    
    def get_values(self):
        """Lấy danh sách giá trị của thuộc tính"""
        return self.attribute_values.filter(is_active=True).order_by('display_order')


class AttributeValue(models.Model):
    """Model cho giá trị của các thuộc tính"""
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='attribute_values')
    value = models.CharField(max_length=100, verbose_name="Giá trị")
    display_order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.attribute.name}: {self.value}"
    
    class Meta:
        ordering = ['display_order', 'value']
        verbose_name = "Giá trị thuộc tính"
        verbose_name_plural = "Giá trị thuộc tính"
        unique_together = ['attribute', 'value']


class ProductAttributeValue(models.Model):
    """Model liên kết sản phẩm với giá trị thuộc tính cụ thể"""
    product = models.ForeignKey('dashboard.Product', on_delete=models.CASCADE, related_name='product_attribute_values')
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE, related_name='product_attribute_values')
    
    class Meta:
        unique_together = ['product', 'attribute_value']
        verbose_name = "Giá trị thuộc tính sản phẩm"
        verbose_name_plural = "Giá trị thuộc tính sản phẩm"
    
    def __str__(self):
        return f"{self.product.name} - {self.attribute_value}" 
        return f"{self.product.name} - {self.attribute_value}"
    
    class Meta:
        unique_together = ['product', 'attribute_value'] 