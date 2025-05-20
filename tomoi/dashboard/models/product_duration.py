from django.db import models
from django.utils.text import slugify


class ProductDuration(models.Model):
    """Model quản lý thời hạn sản phẩm"""
    name = models.CharField(max_length=100, verbose_name="Tên thời hạn")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    value = models.CharField(max_length=20, unique=True, verbose_name="Giá trị")
    days = models.PositiveIntegerField(verbose_name="Số ngày")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    display_order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['display_order', 'days']
        verbose_name = 'Thời hạn sản phẩm'
        verbose_name_plural = 'Thời hạn sản phẩm' 
 
 