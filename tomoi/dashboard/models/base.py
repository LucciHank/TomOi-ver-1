from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator

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
    message_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    intent = models.ForeignKey(ChatbotIntent, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_message_type_display()}: {self.content[:50]}"

class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('in_progress', 'Đang xử lý'),
        ('resolved', 'Đã giải quyết'),
        ('closed', 'Đã đóng'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao'),
        ('urgent', 'Khẩn cấp'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subject} - {self.user.username}"

class TicketReply(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reply to {self.ticket.subject}"

class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class EmailLog(models.Model):
    recipient = models.EmailField()
    subject = models.CharField(max_length=200)
    body = models.TextField()
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='sent')
    
    def __str__(self):
        return f"Email to {self.recipient}: {self.subject}"

class APIKey(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    key = models.CharField(max_length=64, unique=True, default=get_default_token)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"

class APILog(models.Model):
    api_key = models.ForeignKey(APIKey, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)
    status_code = models.IntegerField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"

class Webhook(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    url = models.URLField()
    events = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    secret = models.CharField(max_length=64, default=get_default_token)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Webhook for {self.user.username} - {self.url}"

class WebhookDelivery(models.Model):
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)
    event = models.CharField(max_length=100)
    payload = models.JSONField()
    response = models.TextField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    delivered_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Delivery to {self.webhook.url} - {self.status_code}"

# Định nghĩa các model phân tích/thống kê
class PageView(models.Model):
    path = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.path} - {self.timestamp}"

class VisitorSession(models.Model):
    """Theo dõi thông tin phiên truy cập của người dùng"""
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.CharField(max_length=45, blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=20, choices=[
        ('desktop', 'Desktop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet')
    ], default='desktop')
    referrer = models.URLField(blank=True, null=True)
    landing_page = models.CharField(max_length=255, blank=True)
    page_views = models.IntegerField(default=0)  # Thêm trường page_views
    duration = models.IntegerField(default=0)  # Thời gian phiên (giây)
    is_bounce = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_visit = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.user:
            return f"Session {self.session_id} - {self.user.username}"
        return f"Session {self.session_id}"

class DailyAnalytics(models.Model):
    date = models.DateField(unique=True)
    unique_visitors = models.IntegerField(default=0)
    page_views = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    total_orders = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Analytics for {self.date}"

class PageAnalytics(models.Model):
    path = models.CharField(max_length=255)
    date = models.DateField()
    views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    average_time = models.FloatField(default=0)  # In seconds
    
    class Meta:
        unique_together = ('path', 'date')
    
    def __str__(self):
        return f"{self.path} - {self.date}"

class ReferrerAnalytics(models.Model):
    referrer_domain = models.CharField(max_length=255)
    date = models.DateField()
    visits = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('referrer_domain', 'date')
    
    def __str__(self):
        return f"{self.referrer_domain} - {self.date}"

class Campaign(models.Model):
    """Chiến dịch marketing"""
    name = models.CharField(max_length=100, verbose_name="Tên chiến dịch")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã chiến dịch")
    start_date = models.DateTimeField(verbose_name="Ngày bắt đầu")
    end_date = models.DateTimeField(verbose_name="Ngày kết thúc")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    click_count = models.IntegerField(default=0, verbose_name="Số lượt click")
    conversion_count = models.IntegerField(default=0, verbose_name="Số lượt chuyển đổi")
    # Thêm trường created_at
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    
    def __str__(self):
        return self.name

# Models for content management
class ContentPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    meta_description = models.CharField(max_length=160, blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class ContentBlock(models.Model):
    BLOCK_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('html', 'HTML'),
    ]
    
    page = models.ForeignKey(ContentPage, on_delete=models.CASCADE, related_name='blocks')
    block_type = models.CharField(max_length=10, choices=BLOCK_TYPES)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.get_block_type_display()} block for {self.page.title}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class ReferralProgram(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reward_type = models.CharField(max_length=20, choices=[('fixed', 'Fixed Amount'), ('percentage', 'Percentage')])
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=get_default_time)
    end_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class ReferralCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True)
    program = models.ForeignKey(ReferralProgram, on_delete=models.CASCADE)
    used_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.user.username}"

class ReferralTransaction(models.Model):
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referrer_transactions')
    referred = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referred_transactions')
    code = models.ForeignKey(ReferralCode, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.referrer.username} referred {self.referred.username}"

# Thêm model CalendarEvent nếu chưa có
class CalendarEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
        
    class Meta:
        ordering = ['-start_time'] 