from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

class ActivityLog(models.Model):
    """
    Model lưu trữ các hoạt động của người dùng trong hệ thống
    """
    ACTION_CHOICES = (
        ('create', 'Tạo mới'),
        ('update', 'Cập nhật'),
        ('delete', 'Xóa'),
        ('login', 'Đăng nhập'),
        ('logout', 'Đăng xuất'),
        ('view', 'Xem'),
        ('export', 'Xuất dữ liệu'),
        ('import', 'Nhập dữ liệu'),
        ('other', 'Khác'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='activity_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Tham chiếu đến bất kỳ model nào
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        verbose_name = 'Nhật ký hoạt động'
        verbose_name_plural = 'Nhật ký hoạt động'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def log_activity(cls, user, action, description, content_object=None, ip_address=None):
        """
        Phương thức tiện ích để ghi log hoạt động
        """
        log = cls(
            user=user,
            action=action,
            description=description,
            ip_address=ip_address
        )
        
        if content_object:
            log.content_object = content_object
            
        log.save()
        return log 
 
 