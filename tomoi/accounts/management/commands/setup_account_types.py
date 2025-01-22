from django.core.management.base import BaseCommand
from accounts.models import AccountType

class Command(BaseCommand):
    help = 'Tạo các loại tài khoản mặc định'

    def handle(self, *args, **options):
        default_types = [
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

        for type_data in default_types:
            AccountType.objects.get_or_create(
                code=type_data['code'],
                defaults={
                    'name': type_data['name'],
                    'color_code': type_data['color_code'],
                }
            )

        self.stdout.write(self.style.SUCCESS('Đã tạo xong các loại tài khoản mặc định')) 