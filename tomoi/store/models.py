from django.db import models
from django.utils.timezone import now
from django import forms
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from datetime import timedelta
from django.utils import timezone
from django.utils.text import slugify

def default_expiry_date():
    return now() + timedelta(days=30)

# Mô hình danh mục sản phẩm (Category)
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# Mô hình nhãn sản phẩm (ProductLabel)
class ProductLabel(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#df2626')

    def __str__(self):
        return self.name


# Mô hình sản phẩm (Product)
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    old_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    label = models.ForeignKey(ProductLabel, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_primary_image(self):
        """Lấy ảnh chính của sản phẩm"""
        primary_image = self.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image
        # Nếu không có ảnh chính, lấy ảnh đầu tiên
        first_image = self.images.first()
        if first_image:
            return first_image.image
        return None

    def get_discount_percentage(self):
        """Tính phần trăm giảm giá"""
        if self.old_price and self.price:
            discount = ((self.old_price - self.price) / self.old_price) * 100
            return round(discount)
        return 0

    def format_price(self):
        return "{:,}".format(self.price)

    def format_old_price(self):
        if self.old_price:
            return "{:,}".format(self.old_price)
        return None


# Mô hình hình ảnh sản phẩm (ProductImage)
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, 
        related_name='images',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
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


# # Mô hình người dùng (CustomUser)
# class CustomUser(AbstractUser):
#     avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
#     phone_number = models.CharField(max_length=15, null=True, blank=True)
#     birth_date = models.DateField(null=True, blank=True)
#     customer_type = models.CharField(max_length=50, choices=[('retail', 'Khách lẻ'), ('wholesale', 'Khách sỉ'), ('supplier', 'Nhà cung cấp')], default='retail')
#     balance = models.DecimalField(max_digits=10, decimal_places=0, default=0)
#     join_date = models.DateField(auto_now_add=True)
#     groups = models.ManyToManyField(Group, related_name="accounts_customuser_set", blank=True)
#     user_permissions = models.ManyToManyField(Permission, related_name="accounts_customuser_permissions_set", blank=True)
#     groups = models.ManyToManyField(Group, related_name="accounts_customuser_set", blank=True,help_text="The groups this user belongs to.",related_query_name="user")
#     user_permissions = models.ManyToManyField(Permission, related_name="accounts_customuser_permissions_set", blank=True,help_text="Specific permissions for this user.",related_query_name="user")


# Mô hình đơn hàng (Order)
class Order(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='store_orders')
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


class Banner(models.Model):
    LOCATION_CHOICES = [
        ('main', 'Banner Chính'),
        ('side1', 'Banner Phụ 1'),
        ('side2', 'Banner Phụ 2'),
        ('left', 'Banner Trái'),
        ('right', 'Banner Phải'),
    ]
    
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True)
    location = models.CharField(
        max_length=20,
        choices=LOCATION_CHOICES,
        default='main'
    )
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['location', 'order']

    def __str__(self):
        return f"{self.title} ({self.get_location_display()})"

    @property
    def is_valid(self):
        """Kiểm tra xem banner có đang trong thời gian hiển thị không"""
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

# Mô hình giỏ hàng (CartItem)
class CartItem(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Đảm bảo mỗi sản phẩm chỉ xuất hiện một lần cho mỗi user hoặc session
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                condition=models.Q(user__isnull=False),
                name='unique_user_product'
            ),
            models.UniqueConstraint(
                fields=['session_key', 'product'],
                condition=models.Q(session_key__isnull=False),
                name='unique_session_product'
            )
        ]

    def total_price(self):
        """Tính tổng tiền của item"""
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def total_price(self):
        return self.price * self.quantity

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'
