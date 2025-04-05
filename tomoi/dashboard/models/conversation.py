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

# Định nghĩa models mới cho hệ thống tin nhắn admin-user
class Conversation(models.Model):
    """Lưu trữ cuộc hội thoại giữa admin và người dùng"""
    admin = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='admin_conversations',
        null=True,
        verbose_name="Quản trị viên"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='user_conversations',
        verbose_name="Người dùng"
    )
    last_message_time = models.DateTimeField(auto_now=True, verbose_name="Thời gian tin nhắn cuối")
    
    class Meta:
        verbose_name = "Cuộc hội thoại"
        verbose_name_plural = "Cuộc hội thoại"
        ordering = ['-last_message_time']
        unique_together = ['admin', 'user']
        
    def __str__(self):
        admin_name = self.admin.username if self.admin else "Chưa được gán"
        return f"Hội thoại: {admin_name} - {self.user.username}"
    
    def unread_count_for_admin(self):
        """Số tin nhắn chưa đọc cho admin"""
        return self.messages.filter(sender=self.user, is_read=False).count()
    
    def unread_count_for_user(self):
        """Số tin nhắn chưa đọc cho người dùng"""
        return self.messages.filter(sender=self.admin, is_read=False).count()

class Message(models.Model):
    """Lưu trữ tin nhắn trong cuộc hội thoại"""
    MESSAGE_TYPES = (
        ('text', 'Văn bản'),
        ('image', 'Hình ảnh'),
        ('order', 'Đơn hàng'),
    )
    
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages',
        verbose_name="Cuộc hội thoại"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name="Người gửi"
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name="Người nhận"
    )
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPES,
        default='text',
        verbose_name="Loại tin nhắn"
    )
    content = models.TextField(verbose_name="Nội dung tin nhắn")
    order_data = models.JSONField(null=True, blank=True, verbose_name="Dữ liệu đơn hàng")
    is_read = models.BooleanField(default=False, verbose_name="Đã đọc")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian gửi")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian đọc")
    
    class Meta:
        verbose_name = "Tin nhắn"
        verbose_name_plural = "Tin nhắn"
        ordering = ['sent_at']
        
    def __str__(self):
        return f"Tin nhắn từ {self.sender.username} đến {self.receiver.username}: {self.content[:30]}"
    
    def mark_as_read(self):
        """Đánh dấu tin nhắn đã đọc"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

class UserNotification(models.Model):
    """Lưu trữ thông báo cho người dùng"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_notifications',
        verbose_name="Người dùng"
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        verbose_name="Tin nhắn"
    )
    is_read = models.BooleanField(default=False, verbose_name="Đã đọc")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian tạo")
    
    class Meta:
        verbose_name = "Thông báo"
        verbose_name_plural = "Thông báo"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Thông báo cho {self.user.username}: {self.message.content[:30]}" 