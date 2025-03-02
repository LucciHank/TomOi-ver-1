from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count
from store.models import Order, OrderItem
import csv
from io import StringIO
from datetime import datetime

@staff_member_required
def order_management(request):
    """Quản lý đơn hàng"""
    orders = Order.objects.all().order_by('-created_at')
    
    # Lọc theo trạng thái nếu có
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Tìm kiếm theo từ khóa
    search = request.GET.get('search')
    if search:
        orders = orders.filter(order_id__icontains=search) | orders.filter(user__username__icontains=search)
    
    # Thống kê
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    completed_orders = orders.filter(status='completed').count()
    cancelled_orders = orders.filter(status='cancelled').count()
    
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'status': status,
        'search': search
    }
    
    return render(request, 'dashboard/orders/management.html', context)

@staff_member_required
def order_detail(request, order_id):
    """Chi tiết đơn hàng"""
    order = get_object_or_404(Order, id=order_id)
    order_items = order.orderitem_set.all()
    
    context = {
        'order': order,
        'order_items': order_items
    }
    
    return render(request, 'dashboard/orders/detail.html', context)

@staff_member_required
def update_order_status(request, order_id):
    """Cập nhật trạng thái đơn hàng"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Phương thức không được hỗ trợ'}, status=405)
    
    order = get_object_or_404(Order, id=order_id)
    status = request.POST.get('status')
    
    if status not in ['pending', 'processing', 'shipped', 'completed', 'cancelled']:
        return JsonResponse({'error': 'Trạng thái không hợp lệ'}, status=400)
    
    order.status = status
    order.save()
    
    return JsonResponse({'success': True, 'status': status})

@staff_member_required
def export_orders(request):
    """Xuất danh sách đơn hàng ra CSV"""
    # Lọc theo trạng thái nếu có
    status = request.GET.get('status')
    orders = Order.objects.all().order_by('-created_at')
    if status:
        orders = orders.filter(status=status)
    
    # Tạo file CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="orders_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Mã đơn hàng', 'Khách hàng', 'Ngày đặt', 'Tổng tiền', 'Trạng thái'])
    
    for order in orders:
        writer.writerow([
            order.order_id,
            order.user.username if order.user else 'Khách vãng lai',
            order.created_at.strftime('%d/%m/%Y %H:%M'),
            order.total_price,
            order.get_status_display()
        ])
    
    return response 