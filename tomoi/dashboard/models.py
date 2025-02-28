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
    STATUS_CHOICES = (
        ('new', _('Mới')),
        ('processing', _('Đang xử lý')),
        ('resolved', _('Đã giải quyết')),
        ('closed', _('Đã đóng')),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    title = models.CharField(_('Tiêu đề'), max_length=255)
    content = models.TextField(_('Nội dung'))
    status = models.CharField(_('Trạng thái'), max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(_('Ngày tạo'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Ngày cập nhật'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class TicketReply(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(_('Nội dung'))
    created_at = models.DateTimeField(_('Ngày tạo'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Phản hồi ticket')
        verbose_name_plural = _('Phản hồi ticket')
        ordering = ['created_at']
    
    def __str__(self):
        return f'Phản hồi cho {self.ticket.title}'

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
        ('display', 'Display Ads'),
        ('search', 'Search Ads'),
    )
    
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES)
    description = models.TextField(blank=True)
    goals = models.TextField(blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    conversions = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
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
class ChatbotQA(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'Thông tin chung'),
        ('product', 'Sản phẩm'),
        ('payment', 'Thanh toán'),
        ('shipping', 'Vận chuyển'),
        ('return', 'Đổi trả')
    ]
    
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True, null=True)
    keywords = models.CharField(max_length=255, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.question
    
    class Meta:
        verbose_name = 'Câu hỏi và trả lời'
        verbose_name_plural = 'Câu hỏi và trả lời'

class ChatSession(models.Model):
    STATUS_CHOICES = [
        ('active', 'Đang hoạt động'),
        ('ended', 'Đã kết thúc'),
        ('transferred', 'Đã chuyển cho nhân viên')
    ]
    
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    feedback_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    feedback_comment = models.TextField(blank=True)
    
    def __str__(self):
        return f"Chat {self.session_id} - {self.start_time}"
    
    class Meta:
        ordering = ['-start_time']

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    is_bot = models.BooleanField(default=False)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    qa_used = models.ForeignKey(ChatbotQA, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{'Bot' if self.is_bot else 'User'}: {self.message[:50]}"
    
    class Meta:
        ordering = ['sent_at']

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