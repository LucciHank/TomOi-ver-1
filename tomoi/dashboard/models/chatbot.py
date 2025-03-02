from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from store.models import Category

User = get_user_model()

class ChatbotConfig(models.Model):
    """Cấu hình chung của chatbot"""
    name = models.CharField(max_length=100, verbose_name="Tên cấu hình")
    is_active = models.BooleanField(default=False, verbose_name="Kích hoạt")
    base_prompt = models.TextField(verbose_name="Prompt cơ bản")
    rejection_message = models.CharField(max_length=255, default="Xin lỗi, tôi không thể hỗ trợ câu hỏi này.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Cấu hình Chatbot"
        verbose_name_plural = "Cấu hình Chatbot"

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.api_type})"
    
    class Meta:
        verbose_name = "Tích hợp API"
        verbose_name_plural = "Tích hợp API"

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
    full_prompt = models.TextField()
    response = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    filter_reason = models.TextField(blank=True, null=True)
    api_response_time = models.FloatField(default=0)  # Thời gian phản hồi API tính bằng ms
    satisfaction_rating = models.PositiveSmallIntegerField(null=True, blank=True)  # Đánh giá từ 1-5
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "Log trò chuyện"
        verbose_name_plural = "Log trò chuyện" 