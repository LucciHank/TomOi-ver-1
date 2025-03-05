from django.db import models
from django.contrib.auth import get_user_model
import decimal

User = get_user_model()

class UserActivityLog(models.Model):
    ACTION_TYPES = (
        ('create', 'tạo mới'),
        ('update', 'cập nhật'),
        ('delete', 'xóa'),
        ('restore', 'khôi phục')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities_affected')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activities_performed')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    old_data = models.JSONField(null=True, blank=True)  # Lưu dữ liệu cũ để rollback
    created_at = models.DateTimeField(auto_now_add=True)
    can_rollback = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def save_old_data(self, user_obj):
        """Lưu trữ dữ liệu cũ của user để có thể rollback"""
        self.old_data = {
            'username': user_obj.username,
            'email': user_obj.email,
            'phone': user_obj.phone,
            'is_active': user_obj.is_active,
            'balance': str(user_obj.balance),
            'tcoin_balance': str(user_obj.tcoin_balance),
        }
        self.save()

    def rollback(self):
        """Thực hiện rollback thay đổi"""
        if not self.can_rollback or not self.old_data:
            return False

        if self.action_type == 'delete':
            # Khôi phục user đã xóa
            self.user.is_active = True
            self.user.save()
        elif self.action_type in ['update', 'create']:
            # Khôi phục dữ liệu cũ
            user = self.user
            data = self.old_data
            
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.phone = data.get('phone', user.phone)
            user.is_active = data.get('is_active', user.is_active)
            user.balance = decimal.Decimal(data.get('balance', '0'))
            user.tcoin_balance = int(data.get('tcoin_balance', '0'))
            
            user.save()

        # Tạo log mới cho hành động rollback
        UserActivityLog.objects.create(
            user=self.user,
            admin=self.admin,
            action_type='restore',
            description=f'Hoàn tác thay đổi: {self.description}',
            can_rollback=False
        )

        return True 