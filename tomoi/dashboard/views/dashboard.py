from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser
from store.models import Order, Product
from ..models.base import SupportTicket
from django.db.models.functions import TruncDate

@staff_member_required 
def index(request):
    """Dashboard trang chủ với các thống kê và biểu đồ"""
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_week = now - timedelta(days=7)
    last_month = now - timedelta(days=30)

    # Thống kê người dùng
    total_users = CustomUser.objects.count()
    new_users_24h = CustomUser.objects.filter(date_joined__gte=last_24h).count()
    new_users_week = CustomUser.objects.filter(date_joined__gte=last_week).count()
    new_users_month = CustomUser.objects.filter(date_joined__gte=last_month).count()

    # Tính tỷ lệ tăng trưởng
    previous_month = CustomUser.objects.filter(
        date_joined__gte=now - timedelta(days=60),
        date_joined__lt=last_month
    ).count()
    growth_rate = ((new_users_month - previous_month) / previous_month * 100) if previous_month > 0 else 0

    # Thống kê thiết bị truy cập
    device_stats = CustomUser.objects.values('last_login_device').annotate(
        count=Count('id')
    ).order_by('-count')

    # Biểu đồ người dùng mới theo ngày
    new_users_chart = CustomUser.objects.filter(
        date_joined__gte=last_month
    ).annotate(
        date=TruncDate('date_joined')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    # Thống kê tương tác
    avg_session_time = CustomUser.objects.aggregate(
        avg=Avg('average_session_duration')
    )['avg'] or 0

    # Cảnh báo hệ thống
    alerts = []
    if new_users_24h < (new_users_month / 30) * 0.5:  # Giảm 50% so với trung bình
        alerts.append({
            'type': 'warning',
            'message': 'Số lượng người dùng mới trong 24h giảm mạnh'
        })

    context = {
        'total_users': total_users,
        'new_users_24h': new_users_24h,
        'new_users_week': new_users_week,
        'new_users_month': new_users_month,
        'growth_rate': round(growth_rate, 2),
        'device_stats': device_stats,
        'new_users_chart': list(new_users_chart),
        'avg_session_time': round(avg_session_time / 60, 2),  # Chuyển sang phút
        'alerts': alerts,
    }

    return render(request, 'dashboard/index.html', context) 