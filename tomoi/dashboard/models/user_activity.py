from django.db import models
from django.contrib.auth import get_user_model
import decimal
import json

User = get_user_model()

class UserActivityLog(models.Model):
    ACTION_TYPES = (
        ('create', 'tạo mới'),
        ('update', 'cập nhật'),
        ('delete', 'xóa'),
        ('restore', 'khôi phục'),
        ('permission', 'phân quyền')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities_affected')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activities_performed')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    old_data = models.JSONField(null=True, blank=True)  # Lưu dữ liệu cũ để rollback
    metadata = models.JSONField(null=True, blank=True)  # Lưu metadata bổ sung
    created_at = models.DateTimeField(auto_now_add=True)
    can_rollback = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Nhật ký hoạt động'
        verbose_name_plural = 'Nhật ký hoạt động'

    def __str__(self):
        return f"{self.admin} {self.get_action_type_display()} {self.user} - {self.created_at}"

    def save_old_data(self, user_obj):
        """Lưu dữ liệu cũ trước khi thay đổi"""
        self.old_data = {
            'username': user_obj.username,
            'email': user_obj.email,
            'first_name': user_obj.first_name,
            'last_name': user_obj.last_name,
            'phone_number': getattr(user_obj, 'phone_number', ''),
            'is_active': user_obj.is_active,
            'balance': str(getattr(user_obj, 'balance', 0)),
            'tcoin_balance': str(getattr(user_obj, 'tcoin_balance', 0)),
            'user_group': getattr(user_obj, 'user_group', ''),
            'permissions': list(user_obj.get_all_permissions()) if hasattr(user_obj, 'get_all_permissions') else []
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
        elif self.action_type in ['update', 'create', 'permission']:
            # Khôi phục dữ liệu cũ
            user = self.user
            data = self.old_data
            
            # Cập nhật các trường cơ bản
            for field in ['username', 'email', 'first_name', 'last_name', 'is_active', 'user_group']:
                if field in data:
                    setattr(user, field, data[field])
            
            # Cập nhật các trường số
            if 'balance' in data:
                user.balance = decimal.Decimal(data['balance'])
            if 'tcoin_balance' in data:
                user.tcoin_balance = int(data['tcoin_balance'])
            
            # Cập nhật phone_number nếu có
            if 'phone_number' in data and hasattr(user, 'phone_number'):
                user.phone_number = data['phone_number']
            
            # Lưu thay đổi
            user.save()
            
            # Nếu là rollback phân quyền
            if self.action_type == 'permission' and 'permissions' in data:
                if hasattr(user, 'update_permissions'):
                    user.update_permissions(data['permissions'])

        # Tạo log mới cho hành động rollback
        UserActivityLog.objects.create(
            user=self.user,
            admin=self.admin,
            action_type='restore',
            description=f'Hoàn tác thay đổi: {self.description}',
            can_rollback=False
        )

        return True 