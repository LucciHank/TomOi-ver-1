from django.db import models
from django.utils.timezone import now
from django import forms
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from datetime import timedelta

def default_expiry_date():
    return now() + timedelta(days=30)

# Mô hình danh mục sản phẩm (Category)
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name


# Mô hình sản phẩm (Product)
class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()


# Mô hình hình ảnh sản phẩm (ProductImage)
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, default=1)  # Thêm default=1
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} Image"


# Mô hình biến thể sản phẩm (Variant)
class Variant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # Ví dụ: "Tiết kiệm" hoặc "Cao cấp"

    def __str__(self):
        return f"{self.product.name} - {self.name}"


# Mô hình tùy chọn sản phẩm (Option)
class Option(models.Model):
    variant = models.ForeignKey(Variant, related_name="options", on_delete=models.CASCADE)
    duration = models.PositiveIntegerField()  # Thời gian (ví dụ: 1, 3, 6, 12)
    price = models.DecimalField(max_digits=10, decimal_places=0)  # Giá của tùy chọn

    def __str__(self):
        return f"{self.variant.product.name} - {self.variant.name} ({self.duration} tháng)"


# Form quản lý hình ảnh sản phẩm (ProductImageForm)
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ["image", "is_primary"]

    def clean(self):
        cleaned_data = super().clean()
        is_primary = cleaned_data.get("is_primary")
        product = self.instance.product
        if is_primary and product.images.filter(is_primary=True).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Only one primary image is allowed per product.")
        return cleaned_data


# Mô hình người dùng (CustomUser)
class CustomUser(AbstractUser):
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)


# Mô hình giỏ hàng (CartItem)
class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.option.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.option}"


# Mô hình đơn hàng (Order)
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(max_length=50, choices=[("Pending", "Pending"), ("Completed", "Completed")])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


# Mô hình tài khoản đã mua (PurchasedAccount)
class PurchasedAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=50, choices=[("Netflix", "Netflix"), ("Spotify", "Spotify")])
    expiry_date = models.DateField()

    def days_remaining(self):
        return max((self.expiry_date - now().date()).days, 0)
