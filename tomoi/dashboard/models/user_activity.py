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
        """Lưu dữ liệu cũ trước khi thay đổi"""
        self.old_data = {
            'username': user_obj.username,
            'email': user_obj.email,
            'first_name': user_obj.first_name,
            'last_name': user_obj.last_name,
            'phone_number': getattr(user_obj, 'phone_number', ''),
            'status': getattr(user_obj, 'status', ''),
            'account_type': getattr(user_obj, 'account_type', ''),
            'is_active': user_obj.is_active,
            'balance': str(user_obj.balance),
            'tcoin_balance': str(getattr(user_obj, 'tcoin_balance', 0))
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
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.phone_number = data.get('phone_number', getattr(user, 'phone_number', ''))
            user.status = data.get('status', getattr(user, 'status', ''))
            user.account_type = data.get('account_type', user.account_type)
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