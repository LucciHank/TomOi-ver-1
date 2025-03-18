from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from store.models import Category

User = get_user_model()

class ChatbotConfig(models.Model):
    """Cấu hình cho chatbot"""
    name = models.CharField(max_length=50, default="TomOi Assistant", verbose_name="Tên chatbot")
    chatbot_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tên hiển thị")
    base_prompt = models.TextField(blank=True, null=True, verbose_name="Prompt cơ bản")
    rejection_message = models.TextField(
        default="Xin lỗi, tôi không thể trả lời câu hỏi này. Vui lòng liên hệ với nhân viên hỗ trợ.",
        verbose_name="Thông báo từ chối"
    )
    avatar = models.ImageField(upload_to='chatbot/', blank=True, null=True, verbose_name="Ảnh đại diện")
    theme_color = models.CharField(max_length=20, default="#4e73df", verbose_name="Màu chủ đề")
    active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt (cũ)", editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    
    # Thêm cấu hình system prompt để nạp cho model NLP
    system_prompt = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Cấu hình chatbot"
        verbose_name_plural = "Cấu hình chatbot"

    def save(self, *args, **kwargs):
        # Đồng bộ hai chiều giữa active và is_active
        if hasattr(self, 'is_active'):
            if self.is_active != self.active:
                self.is_active = self.active
        else:
            self.is_active = self.active
        super().save(*args, **kwargs)

class AllowedCategory(models.Model):
    """Danh mục được phép tư vấn"""
    config = models.ForeignKey(ChatbotConfig, on_delete=models.CASCADE, related_name="allowed_categories")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('config', 'category')
        verbose_name = "Danh mục được phép"
        verbose_name_plural = "Danh mục được phép"
    
    def __str__(self):
        return f"{self.config.name} - {self.category.name}"

class ForbiddenKeyword(models.Model):
    """Từ khóa cấm trong tư vấn"""
    config = models.ForeignKey(ChatbotConfig, on_delete=models.CASCADE, related_name="forbidden_keywords")
    keyword = models.CharField(max_length=100)
    
    def __str__(self):
        return self.keyword
    
    class Meta:
        verbose_name = "Từ khóa cấm"
        verbose_name_plural = "Từ khóa cấm"

class APIIntegration(models.Model):
    """Cấu hình tích hợp API"""
    API_TYPES = (
        ('gemini', 'Google Gemini'),
        ('openai', 'OpenAI'),
        ('azure', 'Azure OpenAI'),
        ('anthropic', 'Anthropic Claude'),
        ('other', 'Khác'),
    )
    
    name = models.CharField(max_length=100)
    api_type = models.CharField(max_length=20, choices=API_TYPES)
    api_url = models.URLField()
    api_key = models.CharField(max_length=255)
    api_version = models.CharField(max_length=50, blank=True, null=True)
    timeout = models.IntegerField(default=30)  # Thời gian timeout tính bằng giây
    is_active = models.BooleanField(default=False)
    active = models.BooleanField(default=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.api_type})"
    
    class Meta:
        verbose_name = "Tích hợp API"
        verbose_name_plural = "Tích hợp API"
        
    def save(self, *args, **kwargs):
        # Đồng bộ giữa is_active và active
        self.active = self.is_active
        super().save(*args, **kwargs)

class ChatLog(models.Model):
    """Log chat và tư vấn"""
    STATUS_CHOICES = (
        ('success', 'Thành công'),
        ('filtered', 'Bị lọc'),
        ('error', 'Lỗi'),
    )
    
    session_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_query = models.TextField()
    full_prompt = models.TextField(null=True, blank=True)
    response = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    filter_reason = models.TextField(blank=True, null=True)
    api_response_time = models.FloatField(default=0)  # Thời gian phản hồi API tính bằng ms
    satisfaction_rating = models.PositiveSmallIntegerField(null=True, blank=True)  # Đánh giá từ 1-5
    metadata = models.JSONField(null=True, blank=True)  # Metadata như IP, user agent, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "Log trò chuyện"
        verbose_name_plural = "Log trò chuyện"

class ChatFeedback(models.Model):
    """Phản hồi và góp ý của người dùng về chatbot"""
    session_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    feedback_text = models.TextField(verbose_name="Nội dung góp ý")
    rating = models.PositiveSmallIntegerField(default=0, verbose_name="Đánh giá")  # Đánh giá từ 1-5 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    
    def __str__(self):
        return f"Góp ý {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "Góp ý chatbot"
        verbose_name_plural = "Góp ý chatbot" 