from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.db import models
from django.utils.html import format_html
from django.contrib.auth.hashers import check_password
import random
from datetime import datetime
from django.utils import timezone
import json

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
    USER_TYPE_CHOICES = (
        ('customer', 'Khách hàng'),
        ('staff', 'Nhân viên'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Thêm các trường bổ sung
    address = models.TextField(blank=True, verbose_name="Địa chỉ")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    gender = models.CharField(max_length=10, choices=(
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác')
    ), blank=True)
    
    account_label = models.ForeignKey(
        AccountType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Loại tài khoản'
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
            ('password', 'Mật khẩu cấp 2'),
            ('email', 'Email OTP'),
            ('google', 'Google Authenticator')
        ],
        null=True,
        blank=True
    )
    two_factor_secret = models.CharField(max_length=100, null=True, blank=True)  # For Google Auth
    two_factor_password = models.CharField(max_length=128, null=True, blank=True)  # For password 2FA
    google_auth_secret = models.CharField(max_length=32, null=True, blank=True)  # Thêm field này
    
    # 2FA settings
    require_2fa_purchase = models.BooleanField(default=False)
    require_2fa_deposit = models.BooleanField(default=False)
    require_2fa_password = models.BooleanField(default=False)
    require_2fa_profile = models.BooleanField(default=False)

    tcoin_balance = models.IntegerField(default=0)

    # Thêm các field mới
    ACCOUNT_TYPE_CHOICES = [
        ('regular', 'Tài khoản thường'),
        ('vip', 'Tài khoản VIP'),
        ('premium', 'Tài khoản Premium')
    ]
    
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        default='regular',
        verbose_name='Loại tài khoản'
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Đã xác thực'
    )
    
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='Giới thiệu'
    )

    # Đổi tên trường notes thành user_notes
    user_notes = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Ghi chú',
        help_text='Ghi chú về người dùng'
    )

    bank_account = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name='Số tài khoản',
        help_text='Số tài khoản ngân hàng'
    )
    
    bank_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='Tên ngân hàng',
        help_text='Tên ngân hàng'
    )
    
    bank_branch = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='Chi nhánh',
        help_text='Chi nhánh ngân hàng'
    )

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
        return self.username

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

    # Các phương thức bổ sung
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'

    def get_full_address(self):
        return self.address or 'Chưa cập nhật'

    def get_account_type_display_name(self):
        return dict(self.ACCOUNT_TYPE_CHOICES).get(self.account_type, 'Không xác định')

    def get_verification_status(self):
        return 'Đã xác thực' if self.is_verified else 'Chưa xác thực'

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

class TCoin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='tcoin_account')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} TCoin"

    class Meta:
        verbose_name = 'TCoin Account'
        verbose_name_plural = 'TCoin Accounts'

class Deposit(models.Model):
    PAYMENT_METHODS = (
        ('vnpay', 'VNPay'),
        ('banking', 'Chuyển khoản'),
        ('card', 'Thẻ cào'),
    )
    STATUS_CHOICES = (
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
        ('failed', 'Thất bại'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount}đ - {self.get_payment_method_display()}"

class TCoinHistory(models.Model):
    ACTIVITY_TYPES = (
        ('checkin', 'Điểm danh'),
        ('purchase', 'Hoàn TCoin'),
        ('admin', 'Admin điều chỉnh'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.IntegerField()  # Có thể âm hoặc dương
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} TCoin - {self.get_activity_type_display()}"

class DailyCheckin(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    tcoin_earned = models.IntegerField()
    
    class Meta:
        unique_together = ('user', 'date')

class CardTransaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Đang xử lý'),
        ('success', 'Thành công'),
        ('failed', 'Thất bại')
    )

    TELCO_CHOICES = (
        ('VIETTEL', 'Viettel'),
        ('MOBIFONE', 'Mobifone'), 
        ('VINAPHONE', 'Vinaphone'),
        ('VIETNAMOBILE', 'Vietnamobile'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    request_id = models.CharField(max_length=50, unique=True)
    telco = models.CharField(max_length=20, choices=TELCO_CHOICES)
    serial = models.CharField(max_length=50)
    pin = models.CharField(max_length=50)
    amount = models.IntegerField()
    real_amount = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Giao dịch thẻ cào'
        verbose_name_plural = 'Giao dịch thẻ cào'

    def __str__(self):
        return f"{self.user.username} - {self.amount}đ - {self.get_status_display()}"

class BalanceHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=0)  # Số tiền thay đổi
    balance_after = models.DecimalField(max_digits=10, decimal_places=0)  # Số dư sau khi thay đổi
    description = models.CharField(max_length=255)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='balance_adjustments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lịch sử số dư'
        verbose_name_plural = 'Lịch sử số dư'

    def __str__(self):
        return f"{self.user.username} - {self.amount:+,}đ - {self.created_at}"

def generate_deposit_transaction_id():
    """Tạo mã giao dịch nạp tiền theo định dạng NT + năm + tháng + 6 số ngẫu nhiên + ngày"""
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    
    # Tạo 6 số ngẫu nhiên
    random_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Ghép mã theo định dạng
    transaction_id = f"NT{year}{month}{random_digits}{day}"
    
    return transaction_id

class UserActivity(models.Model):
    """Model lưu trữ lịch sử hoạt động của người dùng"""
    
    TYPE_CHOICES = [
        ('login', 'Đăng nhập'),
        ('order', 'Đơn hàng'),
        ('profile', 'Thông tin cá nhân'),
        ('security', 'Bảo mật'),
        ('other', 'Khác')
    ]
    
    SEVERITY_CHOICES = [
        ('normal', 'Bình thường'),
        ('warning', 'Cảnh báo'),
        ('danger', 'Nguy hiểm')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=255)
    action_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='normal')
    details = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def get_severity_class(self):
        return self.severity

    def get_type_color(self):
        colors = {
            'login': 'primary',
            'order': 'success', 
            'profile': 'info',
            'security': 'danger',
            'other': 'secondary'
        }
        return colors.get(self.action_type, 'secondary')

    def get_type_icon(self):
        icons = {
            'login': 'fa-sign-in-alt',
            'order': 'fa-shopping-cart',
            'profile': 'fa-user-edit',
            'security': 'fa-shield-alt',
            'other': 'fa-circle'
        }
        return icons.get(self.action_type, 'fa-circle')

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Hoạt động người dùng'
        verbose_name_plural = 'Hoạt động người dùng'

class UserNote(models.Model):
    """Model lưu trữ ghi chú về người dùng"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ghi chú người dùng'
        verbose_name_plural = 'Ghi chú người dùng'
