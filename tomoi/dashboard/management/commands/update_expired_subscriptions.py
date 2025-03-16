from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import UserSubscription
from datetime import timedelta
import logging

class Command(BaseCommand):
    help = 'Cập nhật trạng thái các gói đã hết hạn'

    def add_arguments(self, parser):
        parser.add_argument(
            '--grace-period',
            type=int,
            default=7,
            help='Số ngày ân hạn sau khi hết hạn (mặc định: 7 ngày)'
        )

    def handle(self, *args, **options):
        grace_period = options['grace_period']
        today = timezone.now()
        grace_date = today - timedelta(days=grace_period)
        
        # Lấy các gói đã hết hạn quá thời gian ân hạn nhưng vẫn đang active
        expired_subscriptions = UserSubscription.objects.filter(
            end_date__lt=grace_date,
            status='active'
        )
        
        count = expired_subscriptions.count()
        if count > 0:
            self.stdout.write(f'Đang cập nhật {count} gói đã hết hạn và quá thời gian ân hạn {grace_period} ngày...')
            
            # Cập nhật trạng thái thành 'expired'
            expired_subscriptions.update(status='expired')
            
            self.stdout.write(self.style.SUCCESS(f'Đã cập nhật {count} gói thành trạng thái "Hết hạn".'))
        else:
            self.stdout.write('Không có gói nào cần cập nhật.')
        
        # Ghi log các gói sắp hết hạn
        expiring_soon = UserSubscription.objects.filter(
            end_date__gte=today,
            end_date__lte=today + timedelta(days=7),
            status='active'
        )
        
        if expiring_soon.count() > 0:
            self.stdout.write(f'Có {expiring_soon.count()} gói sẽ hết hạn trong 7 ngày tới:')
            for subscription in expiring_soon:
                days_left = (subscription.end_date - today).days
                self.stdout.write(f'- {subscription.user.username}: {subscription.plan.name} - Còn {days_left} ngày') 