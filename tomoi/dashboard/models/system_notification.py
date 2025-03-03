from django.db import models

class SystemNotification(models.Model):
    SEVERITY_CHOICES = [
        ('info', 'Thông tin'),
        ('warning', 'Cảnh báo'),
        ('critical', 'Khẩn cấp')
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='info')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Thông Báo Hệ Thống'
        verbose_name_plural = 'Các Thông Báo Hệ Thống'
        ordering = ['-created_at'] 