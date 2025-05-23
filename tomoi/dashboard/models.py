from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from store.models import Product, Order, Discount
from blog.models import Post
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid
import decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.apps import apps
import json

# Tham chiếu đến cấu trúc models mới để đảm bảo tương thích ngược
from .models.base import *
from .models.discount import *
from .models.subscription import *
from .models.warranty import *

User = get_user_model()

def get_default_time():
    return timezone.now()

def get_default_expiry_date():
    return timezone.now() + timedelta(days=30)

def get_default_from_date():
    return timezone.now()

def get_default_token():
    return uuid.uuid4().hex

# Định nghĩa các model chatbot
class ChatSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.session_id

class ChatbotIntent(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    keywords = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class ChatMessage(models.Model):
    TYPE_CHOICES = [
        ('user', 'Người dùng'),
        ('bot', 'Chatbot'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    message_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    intent = models.ForeignKey(ChatbotIntent, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_message_type_display()}: {self.content[:50]}"

class ChatbotResponse(models.Model):
    intent = models.ForeignKey(ChatbotIntent, on_delete=models.CASCADE, related_name='responses')
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.intent.name} - Response"

# Kiểm tra xem model đã được đăng ký chưa trước khi định nghĩa
class Ticket(models.Model):
    """Support ticket model"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('processing', 'Processing'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tickets'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class TicketReply(models.Model):
    """Reply to a support ticket"""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_staff_reply = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Reply to {self.ticket.title} by {self.user.username}"
        
    class Meta:
        ordering = ['created_at']

class Commission(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CommissionTransaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

class Staff(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('support', 'Nhân viên hỗ trợ'),
        ('sales', 'Nhân viên bán hàng'),
        ('content', 'Nhân viên nội dung')
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    joined_date = models.DateField()

class StaffActivity(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    action = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

class APIKey(models.Model):
    """API keys for external integration"""
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True, default=get_default_token)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='api_keys')
    permissions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class APILog(models.Model):
    """Log for API requests"""
    api_key = models.ForeignKey(APIKey, on_delete=models.SET_NULL, null=True, blank=True)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    request_data = models.JSONField(default=dict, blank=True, null=True)
    response_data = models.JSONField(default=dict, blank=True, null=True)
    status_code = models.IntegerField()
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"

class ChatConversation(models.Model):
    """Chat conversation between users and support"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations')
    subject = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('closed', 'Closed')], default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Cuộc hội thoại #{self.id}"

class Campaign(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

# Mô hình cho tài khoản premium
class SubscriptionPlan(models.Model):
    """Định nghĩa các gói đăng ký"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(help_text="Thời hạn sử dụng tính bằng ngày")
    features = models.JSONField(default=list, help_text="Danh sách tính năng của gói")
    max_warranty_count = models.IntegerField(default=3, help_text="Số lần bảo hành tối đa")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class UserSubscription(models.Model):
    """Đăng ký của người dùng"""
    STATUS_CHOICES = [
        ('active', 'Đang hoạt động'),
        ('pending', 'Chờ thanh toán'),
        ('expired', 'Hết hạn'),
        ('cancelled', 'Đã hủy'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order = models.ForeignKey('store.Order', on_delete=models.SET_NULL, null=True, blank=True)
    is_auto_renew = models.BooleanField(default=False)
    warranty_count = models.IntegerField(default=0, help_text="Số lần đã sử dụng bảo hành")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    
    def save(self, *args, **kwargs):
        # Tự động tính ngày hết hạn nếu chưa có
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)
    
    @property
    def days_remaining(self):
        """Số ngày còn lại đến khi hết hạn"""
        if self.status != 'active':
            return 0
        now = timezone.now()
        if now > self.end_date:
            return 0
        return (self.end_date - now).days
    
    @property
    def is_expiring_soon(self):
        """Kiểm tra xem gói có sắp hết hạn không (trong vòng 5 ngày)"""
        return 0 < self.days_remaining <= 5

class SubscriptionTransaction(models.Model):
    """Lịch sử giao dịch đăng ký"""
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=[
        ('new', 'Đăng ký mới'),
        ('renewal', 'Gia hạn'),
        ('upgrade', 'Nâng cấp'),
        ('refund', 'Hoàn tiền')
    ])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.subscription.user.username}"

# Thêm model cho bảo hành tài khoản
class WarrantyTicket(models.Model):
    """Yêu cầu bảo hành tài khoản"""
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('resolved', 'Đã xử lý'),
        ('rejected', 'Từ chối')
    ]
    
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='warranty_tickets')
    issue_description = models.TextField(verbose_name="Mô tả vấn đề")
    attachment = models.FileField(upload_to='warranty_attachments/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, verbose_name="Ghi chú của admin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Bảo hành #{self.id} - {self.subscription.user.username}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Nếu là yêu cầu mới, gửi email thông báo
        if is_new:
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            
            # Gửi email thông báo cho admin
            admin_email = getattr(settings, 'WARRANTY_EMAIL', settings.DEFAULT_FROM_EMAIL)
            subject = f"Yêu cầu bảo hành mới: {self.subscription.user.username} - #{self.id}"
            
            message = render_to_string('dashboard/emails/new_warranty_notification.html', {
                'ticket': self,
                'subscription': self.subscription,
                'user': self.subscription.user,
            })
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [admin_email],
                html_message=message,
                fail_silently=True
            )

class WarrantyHistory(models.Model):
    """Lịch sử xử lý bảo hành"""
    ticket = models.ForeignKey(WarrantyTicket, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=20, choices=WarrantyTicket.STATUS_CHOICES)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Cập nhật {self.ticket.id} - {self.status}"

class SystemNotification(models.Model):
    SEVERITY_CHOICES = [
        ('info', 'Thông tin'),
        ('warning', 'Cảnh báo'),
        ('critical', 'Khẩn cấp')
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='info')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class UserActivityLog(models.Model):
    ACTION_TYPES = (
        ('create', 'tạo mới'),
        ('update', 'cập nhật'),
        ('delete', 'xóa'),
        ('restore', 'khôi phục')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities_affected')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activities_performed')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    old_data = models.JSONField(null=True, blank=True)  # Lưu dữ liệu cũ để rollback
    created_at = models.DateTimeField(auto_now_add=True)
    can_rollback = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def save_old_data(self, user_obj):
        """Lưu trữ dữ liệu cũ của user để có thể rollback"""
        self.old_data = {
            'username': user_obj.username,
            'email': user_obj.email,
            'phone': user_obj.phone,
            'is_active': user_obj.is_active,
            'balance': str(user_obj.balance),
            'tcoin_balance': str(user_obj.tcoin_balance),
            # Thêm các trường khác nếu cần
        }
        self.save()

    def rollback(self):
        """Thực hiện rollback thay đổi"""
        if not self.can_rollback or not self.old_data:
            return False

        if self.action_type == 'delete':
            # Khôi phục user đã xóa
            self.user.is_active = True
            self.user.save()
        elif self.action_type in ['update', 'create']:
            # Khôi phục dữ liệu cũ
            user = self.user
            data = self.old_data
            
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.phone = data.get('phone', user.phone)
            user.is_active = data.get('is_active', user.is_active)
            user.balance = decimal.Decimal(data.get('balance', '0'))
            user.tcoin_balance = int(data.get('tcoin_balance', '0'))
            
            user.save()

        # Tạo log mới cho hành động rollback
        UserActivityLog.objects.create(
            user=self.user,
            admin=self.admin,
            action_type='restore',
            description=f'Hoàn tác thay đổi: {self.description}',
            can_rollback=False
        )

        return True

class GoogleCalendarSync(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_uri = models.CharField(max_length=200)
    client_id = models.CharField(max_length=200)
    client_secret = models.CharField(max_length=200)
    scopes = models.TextField()
    is_active = models.BooleanField(default=False)
    last_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Google Calendar Sync - {self.user.username}"

class CalendarEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    google_event_id = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_all_day = models.BooleanField(default=False)
    event_type = models.CharField(max_length=20, choices=[
        ('meeting', 'Cuộc họp'),
        ('deadline', 'Hạn chót'),
        ('reminder', 'Nhắc nhở'),
        ('other', 'Khác')
    ], default='other')
    is_from_google = models.BooleanField(default=False)
    is_synced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
        
    class Meta:
        ordering = ['-start_time']

class Event(models.Model):
    title = models.CharField(max_length=255)
    event_type = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#4e73df')  # Hex color code
    all_day = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']

class APIConfig(models.Model):
    """Model lưu trữ cấu hình API cho các dịch vụ bên ngoài"""
    name = models.CharField(max_length=100, verbose_name="Tên cấu hình")
    api_type = models.CharField(max_length=20, choices=[
        ('gemini', 'Google Gemini AI'),
    ], default='gemini')
    api_key = models.CharField(max_length=255)
    model = models.CharField(max_length=100, choices=[
        ('gemini-2.0-flash', 'Gemini 2.0 Flash'),
        # Các lựa chọn khác...
    ], default='gemini-2.0-flash')
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=2048)
    endpoint = models.CharField(max_length=255, default='https://generativelanguage.googleapis.com/v1beta', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cấu hình API"
        verbose_name_plural = "Cấu hình API"
        
    def __str__(self):
        return f"{self.name} ({self.api_type})"
        
    def save(self, *args, **kwargs):
        # Nếu cấu hình này được kích hoạt, vô hiệu hóa các cấu hình khác cùng loại
        if self.is_active:
            APIConfig.objects.filter(api_type=self.api_type).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
        
class ChatbotConfig(models.Model):
    """Model lưu trữ cấu hình chatbot"""
    name = models.CharField(max_length=100, verbose_name="Tên cấu hình")
    system_prompt = models.TextField(verbose_name="System Prompt", 
                                   help_text="Prompt hệ thống để định hướng chatbot")
    chatbot_name = models.CharField(max_length=100, verbose_name="Tên Chatbot", default="TomOi Assistant")
    theme_color = models.CharField(max_length=20, verbose_name="Màu chủ đề", default="#df2626")
    avatar = models.ImageField(upload_to='chatbot', verbose_name="Avatar chatbot", null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cấu hình Chatbot"
        verbose_name_plural = "Cấu hình Chatbot"
        
    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        # Nếu cấu hình này được kích hoạt, vô hiệu hóa các cấu hình khác
        if self.is_active:
            ChatbotConfig.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

class ChatbotConversation(models.Model):
    """Model lưu trữ lịch sử cuộc trò chuyện với chatbot"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True, 
                            verbose_name="Người dùng")
    session_id = models.CharField(max_length=100, verbose_name="Session ID")
    conversation_data = models.JSONField(verbose_name="Dữ liệu cuộc trò chuyện")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Lịch sử cuộc trò chuyện"
        verbose_name_plural = "Lịch sử cuộc trò chuyện"
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', 'created_at']),
        ]
        
    def __str__(self):
        return f"Cuộc trò chuyện {self.session_id}"
        
    @classmethod
    def create(cls, user_id, session_id, history):
        """Tạo hoặc cập nhật bản ghi lịch sử cuộc trò chuyện"""
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id) if user_id else None
        
        # Tìm hoặc tạo mới
        obj, created = cls.objects.get_or_create(
            session_id=session_id,
            defaults={
                'user': user,
                'conversation_data': history
            }
        )
        
        # Nếu đã tồn tại, cập nhật dữ liệu
        if not created:
            obj.conversation_data = history
            obj.save()
            
        return obj 

class WarrantyService(models.Model):
    """Model định nghĩa các dịch vụ bảo hành có sẵn"""
    name = models.CharField(max_length=100, verbose_name="Tên dịch vụ bảo hành")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Dịch vụ bảo hành"
        verbose_name_plural = "Dịch vụ bảo hành"


class WarrantyReason(models.Model):
    """Model định nghĩa các lý do bảo hành phổ biến"""
    name = models.CharField(max_length=255, verbose_name="Lý do bảo hành")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả chi tiết")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Lý do bảo hành"
        verbose_name_plural = "Lý do bảo hành"


class WarrantyRequest(models.Model):
    """Model lưu trữ yêu cầu bảo hành từ khách hàng"""
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Đã xử lý'),
        ('rejected', 'Từ chối')
    ]
    
    PLATFORM_CHOICES = [
        ('zalo', 'Zalo'),
        ('telegram', 'Telegram'),
        ('fanpage', 'Fanpage'),
        ('website', 'Website'),
        ('messenger', 'Messenger'),
        ('other', 'Khác')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='warranty_requests')
    order = models.ForeignKey('store.Order', on_delete=models.SET_NULL, null=True, blank=True)
    
    account_username = models.CharField(max_length=255, verbose_name="Tên đăng nhập tài khoản lỗi")
    account_password = models.CharField(max_length=255, verbose_name="Mật khẩu tài khoản lỗi")
    account_type = models.CharField(max_length=100, verbose_name="Loại tài khoản")
    
    reason = models.ForeignKey(WarrantyReason, on_delete=models.SET_NULL, null=True, verbose_name="Lý do lỗi")
    custom_reason = models.CharField(max_length=255, blank=True, null=True, verbose_name="Lý do khác")
    
    error_screenshot = models.ImageField(upload_to='warranty_screenshots/', verbose_name="Ảnh chụp lỗi")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='website', verbose_name="Nền tảng yêu cầu")
    source = models.ForeignKey('dashboard.Source', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Nguồn cung cấp")
    is_self_registered = models.BooleanField(default=False, verbose_name="Tự đăng ký")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    admin_notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú của admin")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày hoàn thành")
    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_warranty_requests')

    def __str__(self):
        return f"Yêu cầu bảo hành #{self.id} - {self.account_username}"

    class Meta:
        verbose_name = "Yêu cầu bảo hành"
        verbose_name_plural = "Yêu cầu bảo hành"
        ordering = ['-created_at']


class WarrantyHistory(models.Model):
    """Model lưu trữ lịch sử bảo hành cho các tài khoản"""
    WARRANTY_TYPE_CHOICES = [
        ('new_account', 'Cấp tài khoản mới'),
        ('fix', 'Sửa chữa'),
        ('refund', 'Hoàn tiền'),
        ('extra_days', 'Bù thêm ngày')
    ]
    
    warranty_request = models.ForeignKey(WarrantyRequest, on_delete=models.CASCADE, related_name='warranty_histories')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='warranty_histories')
    
    warranty_types = models.JSONField(default=list, verbose_name="Hình thức bảo hành")
    added_days = models.IntegerField(default=0, verbose_name="Số ngày bù thêm")
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Số tiền hoàn trả")
    new_account_info = models.JSONField(default=dict, blank=True, null=True, verbose_name="Thông tin tài khoản mới")
    
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='processed_warranty_histories')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    
    def __str__(self):
        warranty_types_str = ", ".join([dict(self.WARRANTY_TYPE_CHOICES).get(wt, wt) for wt in self.warranty_types])
        return f"Bảo hành #{self.id} - {self.user.username} - {warranty_types_str}"
    
    class Meta:
        verbose_name = "Lịch sử bảo hành"
        verbose_name_plural = "Lịch sử bảo hành"
        ordering = ['-created_at']

class DiscountHistory(models.Model):
    """
    Lưu trữ lịch sử thay đổi mã giảm giá
    """
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, related_name='history', null=True, blank=True)
    discount_code = models.CharField(max_length=50)  # Lưu trữ mã trong trường hợp discount bị xóa
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=20, choices=(
        ('create', 'Tạo mới'),
        ('update', 'Cập nhật'),
        ('delete', 'Xóa'),
        ('activate', 'Kích hoạt'),
        ('deactivate', 'Hủy kích hoạt'),
    ))
    changes_json = models.TextField(null=True, blank=True)  # Lưu trữ các thay đổi dưới dạng JSON
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lịch sử mã giảm giá'
        verbose_name_plural = 'Lịch sử mã giảm giá'
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.discount_code} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class DiscountBackup(models.Model):
    """
    Lưu trữ bản sao lưu mã giảm giá
    """
    name = models.CharField(max_length=100)
    backup_data = models.TextField()  # Lưu trữ dữ liệu dưới dạng JSON
    include_usage = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=255, null=True, blank=True)  # Đường dẫn tới file backup (nếu có)
    
    class Meta:
        verbose_name = "Bản sao lưu mã giảm giá"
        verbose_name_plural = "Bản sao lưu mã giảm giá"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
        
    def get_discount_count(self):
        """
        Trả về số lượng mã giảm giá trong bản sao lưu
        """
        try:
            import json
            data = json.loads(self.backup_data)
            return len(data.get('discounts', []))
        except:
            return 0 

# Nguồn cung cấp
class Source(models.Model):
    PLATFORM_CHOICES = (
        ('shopee', 'Shopee'),
        ('lazada', 'Lazada'),
        ('tiki', 'Tiki'),
        ('other', 'Khác'),
    )
    
    PRIORITY_CHOICES = (
        (1, 'Cao'),
        (2, 'Trung bình'),
        (3, 'Thấp'),
    )
    
    name = models.CharField(max_length=255)
    url = models.URLField()
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    product_type = models.CharField(max_length=100)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    availability_rate = models.IntegerField(default=100)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Nguồn cung cấp'
        verbose_name_plural = 'Nguồn cung cấp'

# Mã giảm giá (có thể kết nối với store.Product)
class DiscountCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=10, choices=[
        ('percent', 'Phần trăm'),
        ('fixed', 'Cố định')
    ])
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    usage_limit = models.IntegerField(default=0)  # 0 = không giới hạn
    usage_count = models.IntegerField(default=0)
    
    # Kết nối với sản phẩm (nếu giảm giá cụ thể sản phẩm)
    products = models.ManyToManyField('store.Product', blank=True, related_name='discount_codes')
    
    # Kết nối với danh mục (nếu giảm giá theo danh mục)
    categories = models.ManyToManyField('store.Category', blank=True, related_name='discount_codes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Mã giảm giá'
        verbose_name_plural = 'Mã giảm giá'

# Bảng tổng hợp Dashboard
class DashboardSummary(models.Model):
    date = models.DateField(unique=True)
    total_users = models.IntegerField(default=0) 
    active_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    total_orders = models.IntegerField(default=0)
    completed_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    total_tcoin = models.IntegerField(default=0)
    warranty_requests = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Thống kê hệ thống'
        verbose_name_plural = 'Thống kê hệ thống' 