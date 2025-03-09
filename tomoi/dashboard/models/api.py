from django.db import models
from django.utils import timezone

class APIConfig(models.Model):
    api_type = models.CharField(max_length=20, choices=[
        ('gemini', 'Google Gemini AI'),
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('cohere', 'Cohere'),
    ], default='gemini')
    api_key = models.CharField(max_length=255)
    model = models.CharField(max_length=100, default='gemini-pro')
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=2048)
    endpoint = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.api_type} - {self.model} ({'Kích hoạt' if self.active else 'Không kích hoạt'})"
    
    class Meta:
        verbose_name = "Cấu hình API"
        verbose_name_plural = "Cấu hình API"
        
    def save(self, *args, **kwargs):
        # Đảm bảo rằng API key đã được lưu
        print(f"Saving APIConfig: {self.api_type}, key={self.api_key[:5]}...")
        super().save(*args, **kwargs) 