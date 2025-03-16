from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator
from store.models import Order, OrderItem
from accounts.models import CustomUser
import csv
import json
from io import StringIO
from datetime import datetime, timedelta

@staff_member_required
def order_management(request):
    """Quản lý đơn hàng"""
    orders = Order.objects.all().order_by('-created_at')
    
    # Lọc theo trạng thái nếu có
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Lọc theo phương thức thanh toán
    payment_method = request.GET.get('payment_method')
    if payment_method:
        orders = orders.filter(payment_method=payment_method)
    
    # Lọc theo khoảng thời gian
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            orders = orders.filter(created_at__gte=date_from)
        except:
            pass
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            date_to = date_to + timedelta(days=1)  # Bao gồm cả ngày kết thúc
            orders = orders.filter(created_at__lt=date_to)
        except:
            pass
    
    # Tìm kiếm theo từ khóa
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(id__icontains=search) | 
            Q(transaction_id__icontains=search) | 
            Q(user__username__icontains=search) | 
            Q(user__email__icontains=search)
        )
    
    # Phân trang
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)
    
    # Thống kê
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    processing_orders = orders.filter(status='processing').count()
    completed_orders = orders.filter(status='completed').count()
    cancelled_orders = orders.filter(status='cancelled').count()
    
    # Tính toán doanh thu
    total_revenue = orders.filter(status__in=['completed', 'processing']).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Tính toán tỷ lệ tăng trưởng
    now = timezone.now()
    last_month = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)
    
    current_month_orders = orders.filter(created_at__gte=last_month).count()
    previous_month_orders = orders.filter(created_at__gte=two_months_ago, created_at__lt=last_month).count()
    
    if previous_month_orders > 0:
        order_growth = ((current_month_orders - previous_month_orders) / previous_month_orders) * 100
    else:
        order_growth = 100 if current_month_orders > 0 else 0
    
    current_month_revenue = orders.filter(created_at__gte=last_month, status__in=['completed', 'processing']).aggregate(total=Sum('total_amount'))['total'] or 0
    previous_month_revenue = orders.filter(created_at__gte=two_months_ago, created_at__lt=last_month, status__in=['completed', 'processing']).aggregate(total=Sum('total_amount'))['total'] or 0
    
    if previous_month_revenue > 0:
        revenue_growth = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100
    else:
        revenue_growth = 100 if current_month_revenue > 0 else 0
    
    # Biểu đồ doanh thu theo thời gian (7 ngày)
    dates = []
    revenue_data = []
    for i in range(6, -1, -1):
        date = now - timedelta(days=i)
        dates.append(date.strftime('%d/%m'))
        day_revenue = orders.filter(
            created_at__date=date.date(),
            status__in=['completed', 'processing']
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        revenue_data.append(day_revenue)
    
    # Biểu đồ phương thức thanh toán
    payment_data = list(orders.filter(status__in=['completed', 'processing']).values('payment_method').annotate(count=Count('id')).order_by('-count'))
    payment_labels = [item['payment_method'] or 'Unknown' for item in payment_data]
    payment_counts = [item['count'] for item in payment_data]
    payment_colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b']
    
    # Trung bình giá trị đơn hàng
    if total_orders > 0:
        avg_order_value = total_revenue / orders.filter(status__in=['completed', 'processing']).count() if orders.filter(status__in=['completed', 'processing']).count() > 0 else 0
    else:
        avg_order_value = 0
    
    context = {
        'orders': orders_page,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'order_growth': round(order_growth, 1),
        'revenue_growth': round(revenue_growth, 1),
        'order_trend_icon': 'arrow-up' if order_growth >= 0 else 'arrow-down',
        'order_trend_color': 'success' if order_growth >= 0 else 'danger',
        'revenue_trend_icon': 'arrow-up' if revenue_growth >= 0 else 'arrow-down',
        'revenue_trend_color': 'success' if revenue_growth >= 0 else 'danger',
        'dates': json.dumps(dates),
        'revenue_data': revenue_data,
        'payment_labels': json.dumps(payment_labels),
        'payment_data': payment_counts,
        'payment_colors': json.dumps(payment_colors),
        'status': status,
        'search': search,
        'payment_method': payment_method,
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', '')
    }
    
    # Sử dụng template khác nhau tùy theo request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'dashboard/orders/partials/order_table.html', context)
    else:
        return render(request, 'dashboard/orders/management.html', context)

@staff_member_required
def order_list(request):
    """Danh sách đơn hàng dạng list đơn giản"""
    orders = Order.objects.all().order_by('-created_at')
    
    # Lọc theo id
    order_id = request.GET.get('order_id')
    if order_id:
        orders = orders.filter(id__icontains=order_id)
    
    # Lọc theo khách hàng
    customer = request.GET.get('customer')
    if customer:
        orders = orders.filter(
            Q(user__username__icontains=customer) | 
            Q(user__email__icontains=customer) |
            Q(user__full_name__icontains=customer)
        )
    
    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Phân trang
    paginator = Paginator(orders, 30)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)
    
    context = {
        'orders': orders_page,
        'order_id': order_id,
        'customer': customer,
        'status': status
    }
    
    return render(request, 'dashboard/orders/list.html', context)

@staff_member_required
def order_detail(request, order_id):
    """Chi tiết đơn hàng"""
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    
    # Lấy tổng giá trị đơn hàng của user này (nếu có)
    total_spent = 0
    orders_count = 0
    if order.user:
        orders_count = Order.objects.filter(user=order.user, status='completed').count()
        total_spent = Order.objects.filter(user=order.user, status='completed').aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'order': order,
        'order_items': order_items,
        'orders_count': orders_count,
        'total_spent': total_spent
    }
    
    return render(request, 'dashboard/orders/detail.html', context)

@staff_member_required
def update_order_status(request):
    """Cập nhật trạng thái đơn hàng"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Phương thức không được hỗ trợ'}, status=405)
    
    order_id = request.POST.get('order_id')
    status = request.POST.get('status')
    notes = request.POST.get('notes', '')
    notify_customer = request.POST.get('notify_customer') == 'on'
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Đơn hàng không tồn tại'}, status=404)
    
    if status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        return JsonResponse({'error': 'Trạng thái không hợp lệ'}, status=400)
    
    # Lưu trạng thái cũ để kiểm tra thay đổi
    old_status = order.status
    
    # Cập nhật đơn hàng
    order.status = status
    if notes:
        # Thêm ghi chú nếu có mô hình OrderNote
        try:
            from store.models import OrderNote
            note = OrderNote(order=order, note=notes, created_by=request.user)
            note.save()
        except ImportError:
            # Nếu không có model OrderNote thì bỏ qua
            pass
    
    order.save()
    
    # Xử lý thông báo email cho khách hàng nếu được chọn
    if notify_customer and order.user and order.user.email:
        try:
            send_order_status_email(order, old_status, notes)
        except Exception as e:
            # Log lỗi nhưng không ảnh hưởng đến việc cập nhật trạng thái
            print(f"Error sending email notification: {str(e)}")
    
    messages.success(request, f'Đã cập nhật trạng thái đơn hàng #{order.id} thành {order.get_status_display()}')
    
    # Trả về URL redirect tùy theo nguồn gọi API
    referer = request.META.get('HTTP_REFERER', '')
    if 'order_detail' in referer:
        redirect_url = f'/dashboard/orders/{order.id}/'
    else:
        redirect_url = '/dashboard/orders/'
    
    return JsonResponse({
        'success': True, 
        'status': status,
        'redirect': redirect_url
    })

@staff_member_required
def cancel_order(request):
    """Hủy đơn hàng"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Phương thức không được hỗ trợ'}, status=405)
    
    order_id = request.POST.get('order_id')
    reason = request.POST.get('reason', 'Hủy bởi quản trị viên')
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Đơn hàng không tồn tại'}, status=404)
    
    # Chỉ cho phép hủy đơn hàng đang chờ xử lý
    if order.status not in ['pending', 'processing']:
        return JsonResponse({'error': 'Không thể hủy đơn hàng đã xử lý'}, status=400)
    
    order.status = 'cancelled'
    order.notes = f"{order.notes or ''}\n\nĐã hủy: {reason}"
    order.save()
    
    messages.success(request, f'Đã hủy đơn hàng #{order.id}')
    
    return JsonResponse({'success': True})

@staff_member_required
def refund_order(request):
    """Hoàn tiền đơn hàng"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Phương thức không được hỗ trợ'}, status=405)
    
    order_id = request.POST.get('order_id')
    amount = request.POST.get('amount')
    reason = request.POST.get('reason', '')
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Đơn hàng không tồn tại'}, status=404)
    
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Số tiền không hợp lệ'}, status=400)
    
    # Logic xử lý hoàn tiền tùy thuộc vào phương thức thanh toán
    # Đây chỉ là mẫu, cần điều chỉnh theo logic thực tế
    try:
        # Ghi lại thông tin hoàn tiền
        order.status = 'refunded'
        order.notes = f"{order.notes or ''}\n\nĐã hoàn tiền: {amount}đ - Lý do: {reason}"
        order.save()
        
        # Tạo refund record nếu có model Refund
        try:
            from store.models import Refund
            refund = Refund(
                order=order,
                amount=amount,
                reason=reason,
                created_by=request.user
            )
            refund.save()
        except ImportError:
            # Nếu không có model Refund thì bỏ qua
            pass
        
        messages.success(request, f'Đã hoàn tiền {amount}đ cho đơn hàng #{order.id}')
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': f'Lỗi khi hoàn tiền: {str(e)}'}, status=500)

@staff_member_required
def customer_orders(request, user_id):
    """Xem đơn hàng của một khách hàng cụ thể"""
    customer = get_object_or_404(CustomUser, id=user_id)
    orders = Order.objects.filter(user=customer).order_by('-created_at')
    
    # Thống kê đơn hàng của khách
    total_spent = orders.filter(status='completed').aggregate(total=Sum('total_amount'))['total'] or 0
    order_count = orders.count()
    completed_count = orders.filter(status='completed').count()
    cancelled_count = orders.filter(status='cancelled').count()
    
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)
    
    context = {
        'customer': customer,
        'orders': orders_page,
        'total_spent': total_spent,
        'order_count': order_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count
    }
    
    return render(request, 'dashboard/orders/customer_orders.html', context)

@staff_member_required
def order_history(request):
    """Lịch sử đơn hàng và hoạt động"""
    # Lấy tất cả đơn hàng và các hoạt động liên quan
    orders = Order.objects.all().order_by('-created_at')[:100]  # Giới hạn 100 đơn hàng gần nhất
    
    # Lấy lịch sử thay đổi trạng thái đơn hàng
    try:
        from store.models import OrderStatusHistory
        status_history = OrderStatusHistory.objects.all().order_by('-created_at')[:100]
    except ImportError:
        status_history = []
    
    # Lấy các ghi chú về đơn hàng
    try:
        from store.models import OrderNote
        notes = OrderNote.objects.all().order_by('-created_at')[:100]
    except ImportError:
        notes = []
    
    # Kết hợp tất cả hoạt động thành một dòng thời gian
    activities = []
    
    for order in orders:
        activities.append({
            'type': 'order_created',
            'order': order,
            'timestamp': order.created_at,
            'description': f'Đơn hàng #{order.id} được tạo'
        })
    
    for history in status_history:
        activities.append({
            'type': 'status_changed',
            'order': history.order,
            'timestamp': history.created_at,
            'description': f'Đơn hàng #{history.order.id} thay đổi trạng thái từ {history.old_status} thành {history.new_status}',
            'user': history.created_by
        })
    
    for note in notes:
        activities.append({
            'type': 'note_added',
            'order': note.order,
            'timestamp': note.created_at,
            'description': f'Ghi chú cho đơn hàng #{note.order.id}: {note.note[:50]}...' if len(note.note) > 50 else f'Ghi chú cho đơn hàng #{note.order.id}: {note.note}',
            'user': note.created_by
        })
    
    # Sắp xếp theo thời gian mới nhất
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    context = {
        'activities': activities[:100]  # Giới hạn 100 hoạt động gần nhất
    }
    
    return render(request, 'dashboard/orders/history.html', context)

@staff_member_required
def export_orders(request):
    """Xuất danh sách đơn hàng ra CSV hoặc Excel"""
    # Lọc đơn hàng
    orders = Order.objects.all().order_by('-created_at')
    
    # Lọc theo trạng thái nếu có
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Lọc theo khoảng thời gian
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            orders = orders.filter(created_at__gte=date_from)
        except:
            pass
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            date_to = date_to + timedelta(days=1)  # Bao gồm cả ngày kết thúc
            orders = orders.filter(created_at__lt=date_to)
        except:
            pass
    
    export_format = request.GET.get('format', 'csv')
    
    if export_format == 'excel':
        try:
            import xlsxwriter
            from io import BytesIO
            
            # Tạo file Excel
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Orders')
            
            # Định dạng
            header_format = workbook.add_format({'bold': True, 'bg_color': '#4e73df', 'color': 'white'})
            date_format = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm'})
            money_format = workbook.add_format({'num_format': '#,##0 ₫'})
            
            # Header
            headers = [
                'Mã đơn hàng', 'Mã giao dịch', 'Khách hàng', 'Email', 'Ngày đặt', 
                'Tổng tiền', 'Trạng thái', 'Phương thức thanh toán', 'Ghi chú'
            ]
            
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
            
            # Data
            for row, order in enumerate(orders, start=1):
                worksheet.write(row, 0, order.id)
                worksheet.write(row, 1, order.transaction_id or '')
                worksheet.write(row, 2, order.user.username if order.user else 'Khách vãng lai')
                worksheet.write(row, 3, order.user.email if order.user else '')
                worksheet.write_datetime(row, 4, order.created_at.replace(tzinfo=None), date_format)
                worksheet.write_number(row, 5, float(order.total_amount), money_format)
                worksheet.write(row, 6, order.get_status_display() if hasattr(order, 'get_status_display') else order.status)
                worksheet.write(row, 7, order.get_payment_method_display() if hasattr(order, 'get_payment_method_display') else (order.payment_method or ''))
                worksheet.write(row, 8, order.notes or '')
            
            # Điều chỉnh độ rộng cột
            worksheet.set_column(0, 0, 10)  # Mã đơn hàng
            worksheet.set_column(1, 1, 15)  # Mã giao dịch
            worksheet.set_column(2, 2, 20)  # Khách hàng
            worksheet.set_column(3, 3, 25)  # Email
            worksheet.set_column(4, 4, 18)  # Ngày đặt
            worksheet.set_column(5, 5, 15)  # Tổng tiền
            worksheet.set_column(6, 6, 15)  # Trạng thái
            worksheet.set_column(7, 7, 20)  # Phương thức thanh toán
            worksheet.set_column(8, 8, 30)  # Ghi chú
            
            workbook.close()
            
            # Chuẩn bị response
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="orders_{datetime.now().strftime("%Y%m%d")}.xlsx"'
            
            return response
        except ImportError:
            # Fallback to CSV if xlsxwriter not available
            export_format = 'csv'
    
    if export_format == 'csv':
        # Tạo file CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="orders_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Mã đơn hàng', 'Mã giao dịch', 'Khách hàng', 'Email', 'Ngày đặt', 
            'Tổng tiền', 'Trạng thái', 'Phương thức thanh toán', 'Ghi chú'
        ])
        
        for order in orders:
            writer.writerow([
                order.id,
                order.transaction_id or '',
                order.user.username if order.user else 'Khách vãng lai',
                order.user.email if order.user else '',
                order.created_at.strftime('%d/%m/%Y %H:%M'),
                order.total_amount,
                order.get_status_display() if hasattr(order, 'get_status_display') else order.status,
                order.get_payment_method_display() if hasattr(order, 'get_payment_method_display') else (order.payment_method or ''),
                order.notes or ''
            ])
        
        return response
    
    # Default fallback
    messages.error(request, f'Định dạng xuất {export_format} không được hỗ trợ')
    return redirect('dashboard:orders')

def send_order_status_email(order, old_status, notes=''):
    """Gửi email thông báo thay đổi trạng thái đơn hàng"""
    # Đây là mẫu, cần được thay thế bằng logic gửi email thực tế
    print(f"Would send email notification for order #{order.id} status change from {old_status} to {order.status}")
    # Gọi hàm gửi email thực tế tại đây 