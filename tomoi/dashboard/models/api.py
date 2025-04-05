from django.db import models
from django.utils import timezone

class APIConfig(models.Model):
    api_type = models.CharField(max_length=20, choices=[
        ('gemini', 'Google Gemini AI'),
    ], default='gemini')
    api_key = models.CharField(max_length=255)
    model = models.CharField(max_length=100, choices=[
        ('gemini-2.0-flash', 'Gemini 2.0 Flash - Nhanh và đa chức năng'),
        ('gemini-2.0-flash-lite', 'Gemini 2.0 Flash-Lite - Tiết kiệm, độ trễ thấp'),
        ('gemini-2.0-pro-exp-02-05', 'Gemini 2.0 Pro Experimental - Mạnh mẽ nhất'),
        ('gemini-1.5-flash', 'Gemini 1.5 Flash - Nhanh và linh hoạt'),
        ('gemini-1.5-flash-8b', 'Gemini 1.5 Flash-8B - Cho tác vụ đơn giản'),
        ('gemini-1.5-pro', 'Gemini 1.5 Pro - Suy luận phức tạp'),
        ('imagen-3.0-generate-002', 'Imagen 3 - Tạo hình ảnh')
    ], default='gemini-2.0-flash')
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=2048)
    endpoint = models.CharField(max_length=255, default='https://generativelanguage.googleapis.com/v1beta', blank=True, null=True)
    active = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, editable=False)
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
        # Đồng bộ hai chiều giữa active và is_active
        if hasattr(self, 'is_active'):
            if self.is_active != self.active:
                self.is_active = self.active
        else:
            self.is_active = self.active
        self.api_type = 'gemini'  # Luôn đảm bảo là gemini
        super().save(*args, **kwargs) 