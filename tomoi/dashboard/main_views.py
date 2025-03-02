from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser
from store.models import Order, Product
from .models.base import SupportTicket

@staff_member_required
def index(request):
    """Dashboard trang chủ"""
    # Thống kê tổng quát
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    completed_orders = Order.objects.filter(status='completed').count()
    
    # Số lượng sản phẩm
    total_products = Product.objects.count()
    
    # Tổng doanh thu
    revenue = Order.objects.filter(status='completed').aggregate(
        total=Sum('total_price')
    )['total'] or 0
    
    # Số lượng người dùng
    total_users = CustomUser.objects.count()
    
    # Đơn hàng gần đây
    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    
    # Người dùng mới
    new_users = CustomUser.objects.all().order_by('-date_joined')[:5]
    
    # Sản phẩm bán chạy
    top_products = Product.objects.annotate(
        sold=Count('orderitem')
    ).order_by('-sold')[:5]
    
    # Dữ liệu ticket hỗ trợ
    pending_tickets = SupportTicket.objects.filter(status='pending').count()
    total_tickets = SupportTicket.objects.count()
    
    # Dữ liệu giao dịch bảo hành - bỏ qua phần này
    warranty_requests = 0  # Giá trị mặc định
    
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
        'warranty_requests': warranty_requests
    }
    
    return render(request, 'dashboard/index.html', context) 