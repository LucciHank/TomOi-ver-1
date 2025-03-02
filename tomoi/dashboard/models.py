from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from store.models import Product, Order
from blog.models import Post
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.apps import apps

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

class EmailTemplate(models.Model):
    """
    Model lưu trữ các mẫu email trong hệ thống
    """
    CATEGORY_CHOICES = (
        ('welcome', 'Chào mừng'),
        ('order', 'Đơn hàng'),
        ('promotion', 'Khuyến mãi'),
        ('notification', 'Thông báo'),
        ('password', 'Khôi phục mật khẩu'),
        ('other', 'Khác'),
    )
    
    name = models.CharField(max_length=255, verbose_name="Tên mẫu")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other', verbose_name="Danh mục")
    template_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Loại mẫu")
    subject = models.CharField(max_length=255, verbose_name="Tiêu đề")
    content = models.TextField(verbose_name="Nội dung HTML")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_templates", verbose_name="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    
    def __str__(self):
        return self.name

class Discount(models.Model):
    """Discount codes for products"""
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')], default='percentage')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField(default=get_default_time)
    end_date = models.DateTimeField(default=get_default_expiry_date)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usage_limit = models.IntegerField(default=0, help_text="0 means unlimited")
    times_used = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    products = models.ManyToManyField('store.Product', blank=True, related_name='discounts')
    categories = models.ManyToManyField('store.Category', blank=True, related_name='discounts')
    is_one_time_use = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.code

class UserDiscount(models.Model):
    """Discount assigned to specific users"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    discount = models.ForeignKey('dashboard.Discount', on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.discount.code}"

class ReferralProgram(models.Model):
    """Referral program settings"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reward_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    reward_type = models.CharField(max_length=20, choices=[('fixed', 'Fixed Amount'), ('percentage', 'Percentage')], default='fixed')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class ReferralCode(models.Model):
    """Referral code generated for users"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referral_code')
    code = models.CharField(max_length=20, unique=True)
    program = models.ForeignKey(ReferralProgram, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s referral code: {self.code}"

class ReferralTransaction(models.Model):
    """Record of referral rewards"""
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referral_earnings')
    referred_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referred_by_transaction')
    program = models.ForeignKey(ReferralProgram, on_delete=models.CASCADE)
    order = models.ForeignKey('store.Order', on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Referral reward for {self.referrer.username} from {self.referred_user.username}"

class EmailLog(models.Model):
    subject = models.CharField(max_length=200)
    recipient = models.EmailField()
    content = models.TextField()
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    was_opened = models.BooleanField(default=False)
    was_clicked = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Email to {self.recipient} - {self.subject}"

# Analytics Models
class SalesReport(models.Model):
    date = models.DateField()
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_count = models.IntegerField(default=0)
    customer_count = models.IntegerField(default=0)
    avg_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-date']

class ProductPerformance(models.Model):
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE)
    period = models.CharField(max_length=20)  # daily, weekly, monthly, yearly
    start_date = models.DateField()
    end_date = models.DateField()
    sales_count = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['product', 'period', 'start_date']

# Discount Models (Nếu chưa có trong store app)
class DiscountUsage(models.Model):
    discount = models.ForeignKey('store.Discount', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey('store.Order', on_delete=models.CASCADE, null=True)
    used_at = models.DateTimeField(auto_now_add=True)
    amount_saved = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['-used_at']

# Reviews Models
class ProductReview(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Đang chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Đã từ chối'),
    ]
    
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_verified_purchase = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class ReviewComment(models.Model):
    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

# API Integration Models (Đã thấy có APIKey và APILog trong model của bạn)
class Webhook(models.Model):
    EVENT_CHOICES = [
        ('order.created', 'Đơn hàng mới'),
        ('order.completed', 'Đơn hàng hoàn thành'),
        ('user.registered', 'Người dùng đăng ký'),
        ('product.updated', 'Sản phẩm cập nhật'),
    ]
    
    name = models.CharField(max_length=100)
    url = models.URLField()
    events = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    secret_key = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class WebhookDelivery(models.Model):
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='deliveries')
    event = models.CharField(max_length=50)
    payload = models.JSONField()
    response_code = models.IntegerField(null=True)
    response_body = models.TextField(blank=True)
    successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

# Analytics Models
class PageView(models.Model):
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    referrer = models.URLField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=40)
    
    class Meta:
        ordering = ['-viewed_at']

class VisitorSession(models.Model):
    DEVICE_TYPES = (
        ('desktop', 'Desktop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet')
    )
    
    session_id = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    referrer = models.URLField(null=True, blank=True)
    landing_page = models.CharField(max_length=255)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    page_views = models.PositiveIntegerField(default=0)
    is_bounce = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-start_time']

class DailyAnalytics(models.Model):
    date = models.DateField(unique=True)
    page_views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    new_visitors = models.PositiveIntegerField(default=0)
    returning_visitors = models.PositiveIntegerField(default=0)
    total_sessions = models.PositiveIntegerField(default=0)
    bounce_sessions = models.PositiveIntegerField(default=0)
    total_duration = models.DurationField(default=timedelta())
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Daily analytics'
    
    @property
    def bounce_rate(self):
        if self.total_sessions > 0:
            return (self.bounce_sessions / self.total_sessions) * 100
        return 0
    
    @property
    def avg_session_duration(self):
        if self.total_sessions > 0:
            return self.total_duration / self.total_sessions
        return timedelta()

class PageAnalytics(models.Model):
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    date = models.DateField()
    views = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)
    total_duration = models.DurationField(default=timedelta())
    bounce_count = models.PositiveIntegerField(default=0)
    exit_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['url', 'date']
        ordering = ['-date', '-views']
        verbose_name_plural = 'Page analytics'
    
    @property
    def avg_time_on_page(self):
        if self.views > 0:
            return self.total_duration / self.views
        return timedelta()
    
    @property
    def bounce_rate(self):
        if self.views > 0:
            return (self.bounce_count / self.views) * 100
        return 0
    
    @property
    def exit_rate(self):
        if self.views > 0:
            return (self.exit_count / self.views) * 100
        return 0

class ReferrerAnalytics(models.Model):
    SOURCE_TYPES = (
        ('direct', 'Direct'),
        ('organic', 'Organic Search'),
        ('referral', 'Referral'),
        ('social', 'Social Media'),
        ('email', 'Email'),
        ('paid', 'Paid Ads')
    )
    
    source = models.CharField(max_length=20, choices=SOURCE_TYPES)
    referrer = models.URLField(null=True, blank=True)
    date = models.DateField()
    visits = models.PositiveIntegerField(default=0)
    new_visitors = models.PositiveIntegerField(default=0)
    bounce_count = models.PositiveIntegerField(default=0)
    total_duration = models.DurationField(default=timedelta())
    
    class Meta:
        unique_together = ['source', 'referrer', 'date']
        ordering = ['-date', '-visits']
        verbose_name_plural = 'Referrer analytics'
    
    @property
    def bounce_rate(self):
        if self.visits > 0:
            return (self.bounce_count / self.visits) * 100
        return 0
    
    @property
    def avg_session_duration(self):
        if self.visits > 0:
            return self.total_duration / self.visits
        return timedelta()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('system', 'System'),
        ('order', 'Order'),
        ('ticket', 'Support Ticket'),
        ('marketing', 'Marketing'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.notification_type}: {self.title}"

class ContentPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Trang nội dung'
        verbose_name_plural = 'Trang nội dung'
    
    def get_absolute_url(self):
        return f'/pages/{self.slug}/'

class ContentBlock(models.Model):
    BLOCK_TYPES = [
        ('text', 'Văn bản'),
        ('image', 'Hình ảnh'),
        ('video', 'Video'),
        ('html', 'HTML tùy chỉnh'),
        ('slider', 'Slider'),
        ('cta', 'Call to Action')
    ]
    
    name = models.CharField(max_length=100)
    identifier = models.SlugField(max_length=100, unique=True)
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Khối nội dung'
        verbose_name_plural = 'Khối nội dung'

class MarketingCampaign(models.Model):
    CAMPAIGN_TYPES = (
        ('email', 'Email Marketing'),
        ('social', 'Social Media'),
        ('banner', 'Banner Ads'),
        ('search', 'Search Ads'),
        ('other', 'Khác'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField(default='2023-01-01')
    end_date = models.DateField(default='2023-12-31')
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
        
    @property
    def ctr(self):
        """Click-through rate"""
        if self.impressions > 0:
            return (self.clicks / self.impressions) * 100
        return 0
        
    @property
    def conversion_rate(self):
        """Conversion rate"""
        if self.clicks > 0:
            return (self.conversions / self.clicks) * 100
        return 0
        
    @property
    def status(self):
        today = timezone.now().date()
        if not self.is_active:
            return 'inactive'
        if self.end_date and self.end_date < today:
            return 'ended'
        if self.start_date > today:
            return 'scheduled'
        return 'active'
        
    @property
    def duration_days(self):
        """Số ngày của chiến dịch"""
        if self.end_date:
            return (self.end_date - self.start_date).days
        return None
        
    @property
    def spent_budget(self):
        """Ngân sách đã chi tiêu"""
        return CampaignExpense.objects.filter(campaign=self).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
    @property
    def remaining_budget(self):
        """Ngân sách còn lại"""
        return self.budget - self.spent_budget

class CampaignExpense(models.Model):
    """Model để theo dõi chi tiêu của chiến dịch"""
    campaign = models.ForeignKey(MarketingCampaign, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.campaign.name} - {self.amount}"

class EmailCampaign(models.Model):
    campaign = models.ForeignKey(MarketingCampaign, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    template = models.FileField(upload_to='email_templates/')
    sent_count = models.IntegerField(default=0)
    open_rate = models.FloatField(default=0)
    click_rate = models.FloatField(default=0)

# CRM Models
class CustomerSegment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    criteria = models.JSONField()  # Lưu tiêu chí phân khúc
    created_at = models.DateTimeField(auto_now_add=True)

class CustomerInteraction(models.Model):
    INTERACTION_TYPES = [
        ('email', 'Email'),
        ('call', 'Cuộc gọi'),
        ('chat', 'Chat'),
        ('meeting', 'Gặp mặt'),
    ]
    
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# Analytics Models
class AnalyticsData(models.Model):
    date = models.DateField()
    page_views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    bounce_rate = models.FloatField(default=0)
    avg_session_duration = models.DurationField()
    
    class Meta:
        unique_together = ['date']

class SalesAnalytics(models.Model):
    date = models.DateField()
    total_sales = models.DecimalField(max_digits=12, decimal_places=2)
    order_count = models.IntegerField()
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    refund_count = models.IntegerField(default=0)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class SupportTicket(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'Chung'),
        ('account', 'Tài khoản'),
        ('payment', 'Thanh toán'),
        ('technical', 'Kỹ thuật'),
        ('other', 'Khác'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Đang mở'),
        ('in_progress', 'Đang xử lý'),
        ('closed', 'Đã đóng'),
        ('resolved', 'Đã giải quyết'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subject} - {self.user.username}"

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

# Content Management Models
class ContentPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Trang nội dung'
        verbose_name_plural = 'Trang nội dung'
    
    def get_absolute_url(self):
        return f'/pages/{self.slug}/'

class ContentBlock(models.Model):
    BLOCK_TYPES = [
        ('text', 'Văn bản'),
        ('image', 'Hình ảnh'),
        ('video', 'Video'),
        ('html', 'HTML tùy chỉnh'),
        ('slider', 'Slider'),
        ('cta', 'Call to Action')
    ]
    
    name = models.CharField(max_length=100)
    identifier = models.SlugField(max_length=100, unique=True)
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Khối nội dung'
        verbose_name_plural = 'Khối nội dung'

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('system', 'System'),
        ('order', 'Order'),
        ('ticket', 'Support Ticket'),
        ('marketing', 'Marketing'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.notification_type}: {self.title}"

class PageView(models.Model):
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    referrer = models.URLField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=40)
    
    class Meta:
        ordering = ['-viewed_at']

class VisitorSession(models.Model):
    DEVICE_TYPES = (
        ('desktop', 'Desktop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet')
    )
    
    session_id = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    referrer = models.URLField(null=True, blank=True)
    landing_page = models.CharField(max_length=255)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    page_views = models.PositiveIntegerField(default=0)
    is_bounce = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-start_time']

class DailyAnalytics(models.Model):
    date = models.DateField(unique=True)
    page_views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    new_visitors = models.PositiveIntegerField(default=0)
    returning_visitors = models.PositiveIntegerField(default=0)
    total_sessions = models.PositiveIntegerField(default=0)
    bounce_sessions = models.PositiveIntegerField(default=0)
    total_duration = models.DurationField(default=timedelta())
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Daily analytics'
    
    @property
    def bounce_rate(self):
        if self.total_sessions > 0:
            return (self.bounce_sessions / self.total_sessions) * 100
        return 0
    
    @property
    def avg_session_duration(self):
        if self.total_sessions > 0:
            return self.total_duration / self.total_sessions
        return timedelta()

class PageAnalytics(models.Model):
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    date = models.DateField()
    views = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)
    total_duration = models.DurationField(default=timedelta())
    bounce_count = models.PositiveIntegerField(default=0)
    exit_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['url', 'date']
        ordering = ['-date', '-views']
        verbose_name_plural = 'Page analytics'
    
    @property
    def avg_time_on_page(self):
        if self.views > 0:
            return self.total_duration / self.views
        return timedelta()
    
    @property
    def bounce_rate(self):
        if self.views > 0:
            return (self.bounce_count / self.views) * 100
        return 0
    
    @property
    def exit_rate(self):
        if self.views > 0:
            return (self.exit_count / self.views) * 100
        return 0

class ReferrerAnalytics(models.Model):
    SOURCE_TYPES = (
        ('direct', 'Direct'),
        ('organic', 'Organic Search'),
        ('referral', 'Referral'),
        ('social', 'Social Media'),
        ('email', 'Email'),
        ('paid', 'Paid Ads')
    )
    
    source = models.CharField(max_length=20, choices=SOURCE_TYPES)
    referrer = models.URLField(null=True, blank=True)
    date = models.DateField()
    visits = models.PositiveIntegerField(default=0)
    new_visitors = models.PositiveIntegerField(default=0)
    bounce_count = models.PositiveIntegerField(default=0)
    total_duration = models.DurationField(default=timedelta())
    
    class Meta:
        unique_together = ['source', 'referrer', 'date']
        ordering = ['-date', '-visits']
        verbose_name_plural = 'Referrer analytics'
    
    @property
    def bounce_rate(self):
        if self.visits > 0:
            return (self.bounce_count / self.visits) * 100
        return 0
    
    @property
    def avg_session_duration(self):
        if self.visits > 0:
            return self.total_duration / self.visits
        return timedelta()

class Discount(models.Model):
    DISCOUNT_TYPES = (
        ('percentage', 'Phần trăm'),
        ('fixed', 'Giảm trực tiếp'),
    )
    
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.IntegerField(default=0)  # 0 = không giới hạn
    used_count = models.IntegerField(default=0)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(default=get_default_expiry_date)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def is_valid(self):
        now = timezone.now()
        is_in_period = self.valid_from <= now <= self.valid_to
        not_maxed_out = self.max_uses == 0 or self.used_count < self.max_uses
        return is_in_period and not_maxed_out and self.is_active
    
    def __str__(self):
        return self.code

class EmailTemplate(models.Model):
    TEMPLATE_TYPES = (
        ('welcome', 'Chào mừng'),
        ('order_confirmation', 'Xác nhận đơn hàng'),
        ('shipping_confirmation', 'Xác nhận vận chuyển'),
        ('order_completed', 'Đơn hàng hoàn thành'),
        ('password_reset', 'Đặt lại mật khẩu'),
        ('newsletter', 'Bản tin'),
        ('custom', 'Tùy chỉnh'),
    )
    
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES, default='custom')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class EmailLog(models.Model):
    subject = models.CharField(max_length=200)
    recipient = models.EmailField()
    content = models.TextField()
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    was_opened = models.BooleanField(default=False)
    was_clicked = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Email to {self.recipient} - {self.subject}"

class SalesReport(models.Model):
    date = models.DateField()
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_count = models.IntegerField(default=0)
    customer_count = models.IntegerField(default=0)
    avg_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-date']

class ProductPerformance(models.Model):
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE)
    period = models.CharField(max_length=20)  # daily, weekly, monthly, yearly
    start_date = models.DateField()
    end_date = models.DateField()
    sales_count = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['product', 'period', 'start_date']

class DiscountUsage(models.Model):
    discount = models.ForeignKey('store.Discount', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey('store.Order', on_delete=models.CASCADE, null=True)
    used_at = models.DateTimeField(auto_now_add=True)
    amount_saved = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['-used_at']

class ProductReview(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Đang chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Đã từ chối'),
    ]
    
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_verified_purchase = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class ReviewComment(models.Model):
    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Webhook(models.Model):
    EVENT_CHOICES = [
        ('order.created', 'Đơn hàng mới'),
        ('order.completed', 'Đơn hàng hoàn thành'),
        ('user.registered', 'Người dùng đăng ký'),
        ('product.updated', 'Sản phẩm cập nhật'),
    ]
    
    name = models.CharField(max_length=100)
    url = models.URLField()
    events = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    secret_key = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class WebhookDelivery(models.Model):
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='deliveries')
    event = models.CharField(max_length=50)
    payload = models.JSONField()
    response_code = models.IntegerField(null=True)
    response_body = models.TextField(blank=True)
    successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

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