from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from store.models import Product, Order
from blog.models import Post
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.conf import settings
from django.utils.translation import gettext_lazy as _

User = get_user_model()

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
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title

class TicketReply(models.Model):
    """Reply to a support ticket"""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        
    def __str__(self):
        return f"Reply to {self.ticket.title} by {self.user.username}"

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
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    rate_limit = models.IntegerField(default=1000)  # Requests per day

class APILog(models.Model):
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    response_code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

# Marketing & Analytics Models
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

# Chatbot Models
class ChatConversation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cuộc hội thoại #{self.id}"

class ChatMessage(models.Model):
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    from_user = models.BooleanField(default=True)  # True nếu từ người dùng, False nếu từ chatbot
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        sender = "Người dùng" if self.from_user else "Chatbot"
        return f"{sender}: {self.content[:50]}..."

class ChatbotResponse(models.Model):
    trigger = models.CharField(max_length=200)
    response = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Trigger: {self.trigger[:30]}..."

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

# Notification Models
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
    valid_to = models.DateTimeField(default=lambda: timezone.now() + timedelta(days=30))
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

class SupportTicket(models.Model):
    STATUS_CHOICES = (
        ('open', 'Đang mở'),
        ('pending', 'Đang chờ'),
        ('closed', 'Đã đóng'),
    )
    
    CATEGORY_CHOICES = (
        ('general', 'Câu hỏi chung'),
        ('order', 'Vấn đề đơn hàng'),
        ('product', 'Thông tin sản phẩm'),
        ('shipping', 'Vận chuyển'),
        ('return', 'Đổi trả'),
        ('technical', 'Kỹ thuật'),
        ('other', 'Khác'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    is_customer_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"

class TicketReply(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    is_admin_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reply to Ticket #{self.ticket.id}" 