from django.db import models
from django.utils.timezone import now
from django import forms
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from datetime import timedelta
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.urls import reverse
import uuid

def default_expiry_date():
    return now() + timedelta(days=30)

# Mô hình danh mục sản phẩm (Category)
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:category_detail', args=[self.slug])

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


# Mô hình thương hiệu sản phẩm (Brand)
class Brand(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        verbose_name = 'Thương hiệu'
        verbose_name_plural = 'Thương hiệu'


# Mô hình sản phẩm (Product)
class Product(models.Model):
    DURATION_CHOICES = [
        ('1_DAY', '1 ngày'),
        ('1_WEEK', '1 tuần'),
        ('1_MONTH', '1 tháng'),
        ('3_MONTHS', '3 tháng'),
        ('6_MONTHS', '6 tháng'),
        ('12_MONTHS', '1 năm'),
    ]
    
    LABEL_CHOICES = [
        ('new_account', 'Tài khoản cấp'),
        ('upgrade', 'Nâng cấp chính chủ'),
    ]

    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True, blank=True)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    description = CKEditor5Field('Mô tả', config_name='default', blank=True)
    short_description = models.TextField(blank=True, null=True, verbose_name="Mô tả ngắn")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Giá gốc")
    label_type = models.CharField(max_length=20, choices=LABEL_CHOICES, null=True, blank=True, verbose_name="Loại nhãn")
    category = models.ForeignKey('Category', related_name="products", on_delete=models.CASCADE, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0, verbose_name="Số lượng đã bán")
    features = models.JSONField(default=list)
    specifications = models.JSONField(default=dict, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    requires_email = models.BooleanField(default=False, verbose_name="Yêu cầu Email")
    requires_account_password = models.BooleanField(default=False, verbose_name="Yêu cầu Tài khoản & Mật khẩu")
    is_cross_sale = models.BooleanField(default=False)
    cross_sale_products = models.ManyToManyField('self', blank=True)
    cross_sale_discount = models.IntegerField(default=0, help_text="Phần trăm giảm giá khi mua kèm")
    is_active = models.BooleanField(default=True)
    suppliers = models.ManyToManyField('dashboard.Supplier', blank=True, related_name='products', verbose_name="Nhà cung cấp")
    
    # SEO fields
    meta_title = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tiêu đề SEO")
    meta_description = models.TextField(blank=True, null=True, verbose_name="Mô tả SEO")
    meta_keywords = models.CharField(max_length=255, blank=True, null=True, verbose_name="Từ khóa SEO")
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.id])

    def get_primary_image(self):
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary.image
        # Trả về ảnh đầu tiên hoặc None
        first_image = self.images.first()
        if first_image:
            return first_image.image
        return None

    def get_display_price(self):
        """Trả về giá hiển thị của sản phẩm"""
        return self.price
    
    def get_discount_percentage(self):
        """Tính phần trăm giảm giá của sản phẩm"""
        if self.old_price and self.old_price > self.price:
            return int(((self.old_price - self.price) / self.old_price) * 100)
        return 0

    def format_price(self):
        return "{:,}".format(self.price)

    def format_old_price(self):
        if self.old_price:
            return "{:,}".format(self.old_price)
        return None

    def get_variants_with_options(self):
        """Lấy tất cả variants và options của sản phẩm"""
        variants = self.variants.filter(is_active=True)
        result = []
        for variant in variants:
            options = variant.options.filter(is_active=True).order_by('duration')
            if options:
                result.append({
                    'variant': variant,
                    'options': options
                })
        return result

    def get_all_durations(self):
        """Lấy tất cả các thời hạn có sẵn từ các tùy chọn biến thể"""
        durations = set()
        for variant in self.variants.all():
            for option in variant.options.all():
                durations.add(option.duration)
        return sorted(list(durations))

    def save(self, *args, **kwargs):
        # Tạo slug từ tên nếu chưa có
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Sử dụng sku thay cho product_code
        if not self.sku:
            self.sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
            
        super().save(*args, **kwargs)

    def get_main_image_url(self):
        main_image = self.images.filter(is_primary=True).first()
        if main_image:
            return main_image.image.url
        # Trả về ảnh mặc định nếu không có ảnh chính
        return '/static/images/default-product.jpg'

    def get_features(self):
        """Trả về danh sách tính năng của sản phẩm"""
        return self.features

    def get_duration_display(self):
        """Trả về text hiển thị thời hạn"""
        return dict(self.DURATION_CHOICES).get(self.duration, self.duration)

    @property
    def discount(self):
        """Tính % giảm giá"""
        if self.old_price and self.old_price > self.price:
            return int(((self.old_price - self.price) / self.old_price) * 100)
        return None

    def get_rating_count(self):
        """Đếm số lượng đánh giá cho từng mức điểm"""
        result = {}
        for i in range(1, 6):
            result[str(i)] = self.reviews.filter(rating=i).count()
        return result

    @property
    def average_rating(self):
        """Tính điểm đánh giá trung bình"""
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / reviews.count()


# Mô hình hình ảnh sản phẩm (ProductImage)
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} Image"


# Mô hình biến thể sản phẩm
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    sku = models.CharField(max_length=50, blank=True, null=True)
    shared_stock_id = models.CharField(max_length=50, blank=True, null=True, help_text="ID để nhóm các biến thể sử dụng chung kho")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"{self.product.sku}-{uuid.uuid4().hex[:4].upper()}"
        super().save(*args, **kwargs)
    
    def get_discount_percentage(self):
        """Tính phần trăm giảm giá của biến thể"""
        if self.old_price and self.old_price > self.price:
            discount = ((self.old_price - self.price) / self.old_price) * 100
            return round(discount)
        return 0


# Mô hình giá trị thuộc tính cho biến thể
class VariantAttributeValue(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='attribute_values')
    attribute = models.ForeignKey('dashboard.ProductAttribute', on_delete=models.CASCADE)
    value = models.ForeignKey('dashboard.AttributeValue', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('variant', 'attribute')
    
    def __str__(self):
        return f"{self.variant.name} - {self.attribute.name}: {self.value.value}"


# Mô hình tùy chọn sản phẩm (Option)
class VariantOption(models.Model):
    variant = models.ForeignKey(ProductVariant, related_name='options', on_delete=models.CASCADE)
    duration = models.IntegerField()  # Số tháng
    price = models.DecimalField(max_digits=10, decimal_places=0)
    old_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    shared_stock_id = models.CharField(max_length=50, blank=True, null=True, help_text="ID để nhóm các tùy chọn sử dụng chung kho")

    class Meta:
        ordering = ['duration']
    
    def __str__(self):
        return f"{self.variant.name} - {self.duration} tháng"
    
    def get_discount_percentage(self):
        """Tính phần trăm giảm giá của tùy chọn"""
        if self.old_price and self.old_price > self.price:
            discount = ((self.old_price - self.price) / self.old_price) * 100
            return round(discount)
        return 0


# # Mô hình người dùng (CustomUser)
# class CustomUser(AbstractUser):


# Mô hình đơn hàng (Order)
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('shipped', 'Đã giao hàng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Chờ thanh toán'),
        ('paid', 'Đã thanh toán'),
        ('failed', 'Thanh toán thất bại'),
        ('refunded', 'Đã hoàn tiền'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cod', 'Thanh toán khi nhận hàng'),
        ('bank_transfer', 'Chuyển khoản ngân hàng'),
        ('vnpay', 'VNPay'),
        ('momo', 'MoMo'),
        ('zalopay', 'ZaloPay'),
        ('balance', 'Số dư tài khoản'),
        ('acb_qr', 'QR ACB'),
    )
    
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='store_orders')
    order_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

    def save(self, *args, **kwargs):
        # Tạo order_number nếu chưa có
        if not self.order_number:
            # Format: ORD-YYMMDDxxxx
            prefix = "ORD-"
            date_str = timezone.now().strftime('%y%m%d')
            
            # Lấy số đơn hàng trong ngày
            last_order = Order.objects.filter(order_number__startswith=f"{prefix}{date_str}").order_by('-order_number').first()
            
            if last_order:
                # Lấy số cuối cùng và tăng lên 1
                last_number = int(last_order.order_number[-4:])
                new_number = last_number + 1
            else:
                new_number = 1
                
            self.order_number = f"{prefix}{date_str}{new_number:04d}"
            
        super().save(*args, **kwargs)


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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    duration = models.IntegerField(null=True, blank=True)
    upgrade_email = models.EmailField(null=True, blank=True)
    account_username = models.CharField(max_length=255, null=True, blank=True)

    def get_price(self):
        """Lấy giá của variant và duration tương ứng"""
        try:
            if self.variant and self.duration:
                # Lấy giá từ VariantOption tương ứng với variant và duration
                variant_option = self.variant.options.get(duration=self.duration)
                return variant_option.price
            elif self.variant:
                # Nếu không có duration, lấy giá nhỏ nhất của variant
                return self.variant.options.order_by('price').first().price
            else:
                # Nếu không có variant, lấy giá của product
                return self.product.price
        except Exception:
            # Nếu có lỗi, trả về 0
            return 0

    def get_total_price(self):
        """Tính tổng giá của item dựa trên variant, số lượng và thời hạn"""
        unit_price = self.get_price()
        return unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    class Meta:
        unique_together = [
            ('user', 'product', 'variant', 'duration', 'upgrade_email'),
            ('session_key', 'product', 'variant', 'duration', 'upgrade_email')
        ]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    product_name = models.CharField(max_length=255)
    variant_name = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(null=True, blank=True)
    upgrade_email = models.EmailField(null=True, blank=True)
    account_username = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product_name} - {self.order.id}"

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = CKEditor5Field(
        'Nội dung',
        config_name='default',
        blank=True
    )
    products = models.ManyToManyField(Product, related_name='blog_posts')
    image = models.ImageField(upload_to='blog/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

# Thêm model Wishlist
class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    keyword = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Lịch sử tìm kiếm'
        verbose_name_plural = 'Lịch sử tìm kiếm'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.keyword} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Phần trăm'),
        ('fixed', 'Số tiền cố định'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    value = models.DecimalField(max_digits=10, decimal_places=2)
    max_uses = models.IntegerField(default=0)  # 0 = không giới hạn
    uses_per_customer = models.IntegerField(default=1)  # Số lần mỗi khách hàng có thể sử dụng
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Giá trị đơn hàng tối thiểu
    used_count = models.IntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    products = models.ManyToManyField(Product, blank=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='discount_codes')
    allowed_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='available_discounts')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Mã giảm giá'
        verbose_name_plural = 'Mã giảm giá'
    
    def __str__(self):
        return self.code
    
    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False
        if now < self.valid_from or now > self.valid_to:
            return False
        return True
    
    def is_valid_for_user(self, user, amount=0):
        """Kiểm tra xem mã giảm giá có hợp lệ cho người dùng và giá trị đơn hàng không"""
        # Kiểm tra tính hợp lệ cơ bản
        if not self.is_valid():
            return False
            
        # Kiểm tra giá trị đơn hàng tối thiểu
        if self.min_purchase > 0 and amount < self.min_purchase:
            return False
            
        # Kiểm tra người dùng được phép
        if self.allowed_users.exists() and (user is None or not self.allowed_users.filter(id=user.id).exists()):
            return False
            
        # Nếu người dùng đã đăng nhập, kiểm tra số lần đã sử dụng
        if user and self.uses_per_customer > 0:
            usage_count = user.discount_usages.filter(discount=self).count()
            if usage_count >= self.uses_per_customer:
                return False
                
        return True
    
    def get_discount_amount(self, amount):
        if self.discount_type == 'percentage':
            return (amount * self.value) / 100
        return self.value if amount > self.value else amount

class DiscountUsage(models.Model):
    """Lưu lịch sử sử dụng mã giảm giá"""
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discount_usages')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='discount_usages', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Số tiền được giảm
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Lịch sử sử dụng mã giảm giá'
        verbose_name_plural = 'Lịch sử sử dụng mã giảm giá'
        
    def __str__(self):
        return f"{self.user.username} - {self.discount.code} - {self.amount}"

class Review(models.Model):
    """Đánh giá sản phẩm"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Đánh giá sản phẩm'
        verbose_name_plural = 'Đánh giá sản phẩm'
        ordering = ['-created_at']

    def __str__(self):
        return f"Đánh giá {self.rating}/5 cho {self.product.name} bởi {self.user.username}"
