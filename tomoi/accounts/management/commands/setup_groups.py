from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Tạo các nhóm người dùng và phân quyền'

    def handle(self, *args, **options):
        # Tạo nhóm Admin
        admin_group, created = Group.objects.get_or_create(name='Admin')
        admin_permissions = Permission.objects.all()
        admin_group.permissions.set(admin_permissions)
        self.stdout.write(self.style.SUCCESS('Đã tạo nhóm Admin'))

        # Tạo nhóm Staff với đầy đủ quyền quản lý user
        staff_group, created = Group.objects.get_or_create(name='Staff')
        staff_permissions = [
            "can_view_dashboard",
            "can_manage_products",
            "can_manage_orders",
            "can_view_reports",
            "can_manage_user_status",
            "can_change_account_label",
            "can_manage_balance",
            "change_customuser",
            "view_customuser",
            "add_customuser",
            "delete_customuser",
        ]
        permissions = Permission.objects.filter(codename__in=staff_permissions)
        staff_group.permissions.set(permissions)
        self.stdout.write(self.style.SUCCESS('Đã tạo nhóm Staff'))

        # Tạo nhóm Customer
        customer_group, created = Group.objects.get_or_create(name='Customer')
        customer_permissions = [
            "view_product",
            "add_order",
            "view_order",
            "change_order",
        ]
        permissions = Permission.objects.filter(codename__in=customer_permissions)
        customer_group.permissions.set(permissions)
        self.stdout.write(self.style.SUCCESS('Đã tạo nhóm Customer'))

        self.stdout.write(self.style.SUCCESS('Đã hoàn tất việc tạo nhóm và phân quyền')) 