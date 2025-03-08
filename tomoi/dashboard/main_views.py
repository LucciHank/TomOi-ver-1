from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
import json
from accounts.models import CustomUser
from store.models import Order, Product, OrderItem
from .models.base import SupportTicket
from django.db.models.functions import TruncDate
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    """Dashboard trang chủ"""
    try:
        # Thống kê tổng quát
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        completed_orders = Order.objects.filter(status='completed').count()
        
        # Số lượng sản phẩm
        total_products = Product.objects.count()
        
        # Tổng doanh thu
        revenue = Order.objects.filter(status='completed').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Số lượng người dùng
        total_users = CustomUser.objects.count()
        
        # Đơn hàng gần đây
        recent_orders = Order.objects.all().order_by('-created_at')[:5]
        
        # Người dùng mới
        new_users = CustomUser.objects.all().order_by('-date_joined')[:5]
        
        # Sản phẩm bán chạy
        top_products = Product.objects.annotate(
            sold=Count('order_items')
        ).order_by('-sold')[:5]
        
        # Dữ liệu ticket hỗ trợ
        pending_tickets = SupportTicket.objects.filter(status='pending').count()
        total_tickets = SupportTicket.objects.count()
        
        # Dữ liệu giao dịch bảo hành
        warranty_requests = 0
        
        # Đơn hàng trong ngày
        today = timezone.now().date()
        orders_today = Order.objects.filter(created_at__date=today).count()
        
        # Dữ liệu cho biểu đồ doanh thu 7 ngày
        revenue_data = []
        revenue_labels = []
        
        # Lấy dữ liệu 7 ngày qua
        for i in range(6, -1, -1):
            day = timezone.now() - timedelta(days=i)
            day_revenue = Order.objects.filter(
                created_at__date=day.date()
            ).aggregate(Sum('total_amount')).get('total_amount__sum') or 0
            
            revenue_data.append(float(day_revenue))
            revenue_labels.append(day.strftime('%d/%m'))
        
        # Thống kê trạng thái đơn hàng
        order_status = Order.objects.values('status').annotate(count=Count('id'))
        order_status_labels = []
        order_status_data = []
        
        status_display = {
            'pending': 'Chờ xử lý',
            'processing': 'Đang xử lý',
            'shipping': 'Đang giao hàng',
            'completed': 'Hoàn thành',
            'cancelled': 'Đã hủy'
        }
        
        for status in order_status:
            order_status_labels.append(status_display.get(status['status'], status['status']))
            order_status_data.append(status['count'])
        
        context = {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'total_products': total_products,
            'revenue': revenue,
            'total_users': total_users,
            'recent_orders': recent_orders,
            'new_users': new_users,
            'top_products': top_products,
            'pending_tickets': pending_tickets,
            'total_tickets': total_tickets,
            'warranty_requests': warranty_requests,
            'orders_today': orders_today,
            'revenue_data': json.dumps(revenue_data),
            'revenue_labels': json.dumps(revenue_labels),
            'order_status_labels': json.dumps(order_status_labels),
            'order_status_data': json.dumps(order_status_data),
            'recent_orders_month': recent_orders,
            'recent_users_month': new_users,
        }
        
        return render(request, 'dashboard/index.html', context)
        
    except Exception as e:
        messages.error(request, f'Có lỗi xảy ra: {str(e)}')
        return redirect('dashboard:user_list')  # Redirect to user_list instead of index to avoid infinite loop 