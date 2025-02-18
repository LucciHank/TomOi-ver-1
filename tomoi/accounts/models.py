from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.db import models
from django.utils.html import format_html
from django.contrib.auth.hashers import check_password

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email là bắt buộc')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser phải có is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser phải có is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class AccountType(models.Model):
    code = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name='Mã loại tài khoản'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Tên loại tài khoản'
    )
    color_code = models.CharField(
        max_length=7, 
        default='#666666',
        verbose_name='Mã màu hiển thị'
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Mô tả'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Đang sử dụng'
    )

    class Meta:
        verbose_name = 'Loại tài khoản'
        verbose_name_plural = 'Quản lý loại tài khoản'
        ordering = ['code']

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Nam'),
        ('F', 'Nữ'),
        ('O', 'Khác')
    ]
    gender = models.CharField(
        max_length=1, 
        choices=GENDER_CHOICES,
        null=True,
        blank=True
    )
    USER_TYPE_CHOICES = (
        ('admin', 'Quản trị viên'),
        ('staff', 'Nhân viên'),
        ('customer', 'Khách hàng'),
    )
    
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES, 
        default='customer',
        verbose_name='Chức vụ'
    )
    
    account_label = models.ForeignKey(
        AccountType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Loại tài khoản'
    )
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True,
        verbose_name='Ảnh đại diện'
    )
    phone_number = models.CharField(
        max_length=15, 
        null=True, 
        blank=True,
        verbose_name='Số điện thoại'
    )
    birth_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name='Ngày sinh'
    )
    balance = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        default=0,
        verbose_name='Số dư'
    )
    join_date = models.DateField(
        auto_now_add=True,
        verbose_name='Ngày tham gia'
    )
    STATUS_CHOICES = [
        ('active', 'Hoạt động'),
        ('pending', 'Chờ xác minh'),
        ('suspended', 'Ngừng hoạt động')
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Trạng thái'
    )
    suspension_reason = models.TextField(
        null=True, 
        blank=True,
        verbose_name='Lý do ngừng hoạt động'
    )
    verification_token = models.CharField(max_length=64, null=True, blank=True)
    verification_token_expires = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(
        null=True, 
        blank=True,
        verbose_name='IP đăng nhập cuối'
    )
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name='Số lần đăng nhập thất bại'
    )

    # 2FA fields
    ga_secret_key = models.CharField(max_length=32, null=True, blank=True)
    has_2fa = models.BooleanField(default=False)
    two_factor_method = models.CharField(
        max_length=20,
        choices=[
            ('password', 'Password'),
            ('email', 'Email OTP'),
            ('google', 'Google Authenticator')
        ],
        null=True,
        blank=True
    )
    two_factor_secret = models.CharField(max_length=100, null=True, blank=True)  # For Google Auth
    two_factor_password = models.CharField(max_length=128, null=True, blank=True)  # For password 2FA
    
    # 2FA settings
    require_2fa_purchase = models.BooleanField(default=False)
    require_2fa_deposit = models.BooleanField(default=False)
    require_2fa_password = models.BooleanField(default=False)
    require_2fa_profile = models.BooleanField(default=False)

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Tài khoản'
        verbose_name_plural = 'Quản lý tài khoản'
        permissions = [
            ("can_view_dashboard", "Có thể xem dashboard"),
            ("can_manage_users", "Có thể quản lý người dùng"),
            ("can_manage_products", "Có thể quản lý sản phẩm"),
            ("can_manage_orders", "Có thể quản lý đơn hàng"),
            ("can_view_reports", "Có thể xem báo cáo"),
            ("can_manage_user_status", "Có thể quản lý trạng thái người dùng"),
            ("can_change_account_label", "Có thể thay đổi loại tài khoản"),
            ("can_manage_balance", "Có thể quản lý số dư tài khoản"),
        ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and not self.account_label:
            # Lấy hoặc tạo loại tài khoản mặc định
            default_type, _ = AccountType.objects.get_or_create(
                code='retail',
                defaults={
                    'name': 'Khách bán lẻ',
                    'color_code': '#666666'
                }
            )
            self.account_label = default_type
        super().save(*args, **kwargs)
        
        if is_new:
            self.assign_default_group()

    def assign_default_group(self):
        if self.user_type == 'admin':
            group, _ = Group.objects.get_or_create(name='Admin')
        elif self.user_type == 'staff':
            group, _ = Group.objects.get_or_create(name='Staff')
        else:
            group, _ = Group.objects.get_or_create(name='Customer')
        self.groups.add(group)

    def get_status_display(self):
        if self.is_active:
            return format_html('<span style="color: green;">Hoạt động</span>')
        return format_html('<span style="color: red;">Ngừng hoạt động</span>')

    get_status_display.short_description = 'Trạng thái'

    def __str__(self):
        return f"{self.username} ({self.get_full_name() or self.email})"

    def get_user_type_display(self):
        USER_TYPE_CHOICES = {
            'admin': 'Quản trị viên',
            'staff': 'Nhân viên',
            'customer': 'Khách hàng'
        }
        return USER_TYPE_CHOICES.get(self.user_type, 'Khách hàng')

    def check_two_factor_password(self, password):
        """Kiểm tra mật khẩu cấp 2"""
        if not self.two_factor_password:
            return False
        return check_password(password, self.two_factor_password)

class Order(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='account_orders')
    code = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Thành công')

    class Meta:
        ordering = ['-date']

class Transaction(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='account_transactions')
    code = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Thành công')

    class Meta:
        ordering = ['-date']

class EmailChangeOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']

class LoginHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    device_info = models.CharField(max_length=255)  # Thông tin thiết bị
    browser_info = models.CharField(max_length=255)  # Thông tin trình duyệt
    location = models.CharField(max_length=255, null=True, blank=True)  # Vị trí dựa trên IP
    login_time = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=False)  # Đánh dấu thiết bị hiện tại
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Chưa xác nhận'),
            ('confirmed', 'Đã xác nhận')
        ],
        default='pending'
    )

    class Meta:
        ordering = ['-login_time']
