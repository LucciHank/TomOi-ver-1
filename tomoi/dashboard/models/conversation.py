from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class ChatbotConversation(models.Model):
    """Lưu trữ lịch sử cuộc trò chuyện giữa người dùng và chatbot"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='chatbot_conversations')
    session_id = models.CharField(max_length=100, unique=True, verbose_name="Session ID")
    conversation_data = models.JSONField(default=dict, verbose_name="Dữ liệu cuộc trò chuyện")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    
    class Meta:
        verbose_name = "Lịch sử cuộc trò chuyện"
        verbose_name_plural = "Lịch sử cuộc trò chuyện"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self):
        if self.user:
            return f"Cuộc trò chuyện của {self.user.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
        return f"Cuộc trò chuyện khách - {self.created_at.strftime('%d/%m/%Y %H:%M')}" 