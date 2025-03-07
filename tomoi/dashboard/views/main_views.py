from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser
from store.models import Order, Product
import logging

logger = logging.getLogger(__name__)

@staff_member_required
def index(request):
    """Dashboard index view"""
    try:
        # Thống kê cơ bản
        today = timezone.now()
        thirty_days_ago = today - timedelta(days=30)
        
        context = {
            'total_users': CustomUser.objects.count(),
            'active_users': CustomUser.objects.filter(is_active=True).count(),
            'total_orders': Order.objects.count(),
            'total_products': Product.objects.count(),
            
            # Thống kê doanh thu
            'revenue_today': Order.objects.filter(
                created_at__date=today.date(),
                status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
            
            'revenue_month': Order.objects.filter(
                created_at__gte=thirty_days_ago,
                status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
            
            # Thống kê đơn hàng gần đây
            'recent_orders': Order.objects.order_by('-created_at')[:5],
            
            # Thống kê người dùng mới
            'new_users': CustomUser.objects.order_by('-date_joined')[:5],
        }
        
        logger.info("Dashboard index view accessed")
        return render(request, 'dashboard/index.html', context)
    except Exception as e:
        logger.error(f"Error in dashboard index: {str(e)}")
        raise 