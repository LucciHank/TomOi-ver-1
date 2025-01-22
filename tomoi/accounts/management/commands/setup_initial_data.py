from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from accounts.models import AccountType

class Command(BaseCommand):
    help = 'Tạo dữ liệu ban đầu (Groups và Account Types)'

    def handle(self, *args, **options):
        # Tạo các nhóm
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        staff_group, _ = Group.objects.get_or_create(name='Staff')
        customer_group, _ = Group.objects.get_or_create(name='Customer')

        # Cấp tất cả quyền cho Admin
        admin_permissions = Permission.objects.all()
        admin_group.permissions.set(admin_permissions)
        self.stdout.write(self.style.SUCCESS('Đã tạo nhóm Admin'))

        # Cấp quyền cho Staff
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
        ]
        permissions = Permission.objects.filter(codename__in=staff_permissions)
        staff_group.permissions.set(permissions)
        self.stdout.write(self.style.SUCCESS('Đã tạo nhóm Staff'))

        # Tạo các loại tài khoản
        account_types = [
            {
                'code': 'retail',
                'name': 'Khách bán lẻ',
                'color_code': '#666666',
            },
            {
                'code': 'wholesale',
                'name': 'Khách bán sỉ',
                'color_code': '#1a75ff',
            },
            {
                'code': 'partner_l1',
                'name': 'Cộng tác viên cấp 1',
                'color_code': '#ff9933',
            },
            {
                'code': 'partner_l2',
                'name': 'Cộng tác viên cấp 2',
                'color_code': '#ff8000',
            },
            {
                'code': 'partner_l3',
                'name': 'Cộng tác viên cấp 3',
                'color_code': '#cc6600',
            },
            {
                'code': 'vip_l1',
                'name': 'Khách VIP cấp 1',
                'color_code': '#ffcc00',
            },
            {
                'code': 'vip_l2',
                'name': 'Khách VIP cấp 2',
                'color_code': '#ffd700',
            },
            {
                'code': 'vip_l3',
                'name': 'Khách VIP cấp 3',
                'color_code': '#ffa500',
            },
            {
                'code': 'supplier',
                'name': 'Nhà cung cấp',
                'color_code': '#009933',
            },
            {
                'code': 'partner',
                'name': 'Đối tác',
                'color_code': '#6600cc',
            },
        ]

        for type_data in account_types:
            AccountType.objects.get_or_create(
                code=type_data['code'],
                defaults={
                    'name': type_data['name'],
                    'color_code': type_data['color_code'],
                }
            )
        self.stdout.write(self.style.SUCCESS('Đã tạo xong các loại tài khoản')) 