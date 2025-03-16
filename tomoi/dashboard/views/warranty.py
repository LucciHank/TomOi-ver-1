from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib import messages
from dashboard.models import (
    WarrantyRequest, WarrantyHistory, WarrantyReason, 
    WarrantyService, Source, WarrantyRequestHistory
)
from store.models import Order, OrderItem
from accounts.models import CustomUser
from dashboard.forms import WarrantyRequestForm, WarrantyProcessForm
import json
from datetime import timedelta

def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def warranty_list(request):
    """Trang quản lý yêu cầu bảo hành trong dashboard"""
    # Lấy các tham số filter
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    platform_filter = request.GET.get('platform', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Lấy tất cả yêu cầu bảo hành
    warranty_requests = WarrantyRequest.objects.all().select_related('user', 'source', 'reason').order_by('-created_at')
    
    # Áp dụng các bộ lọc
    if status_filter:
        warranty_requests = warranty_requests.filter(status=status_filter)
    
    if search_query:
        warranty_requests = warranty_requests.filter(
            Q(user__username__icontains=search_query) |
            Q(account_username__icontains=search_query) |
            Q(order__code__icontains=search_query) |
            Q(custom_reason__icontains=search_query)
        )
    
    if platform_filter:
        warranty_requests = warranty_requests.filter(platform=platform_filter)
    
    if date_from:
        try:
            date_from = timezone.datetime.strptime(date_from, '%Y-%m-%d')
            warranty_requests = warranty_requests.filter(created_at__gte=date_from)
        except:
            pass
    
    if date_to:
        try:
            date_to = timezone.datetime.strptime(date_to, '%Y-%m-%d')
            date_to = date_to + timedelta(days=1)  # Bao gồm cả ngày kết thúc
            warranty_requests = warranty_requests.filter(created_at__lt=date_to)
        except:
            pass
    
    # Thống kê
    total_requests = WarrantyRequest.objects.count()
    pending_requests = WarrantyRequest.objects.filter(status='pending').count()
    completed_requests = WarrantyRequest.objects.filter(status='completed').count()
    platform_stats = WarrantyRequest.objects.values('platform').annotate(count=Count('id'))
    
    # Phân trang
    paginator = Paginator(warranty_requests, 20)  # Hiển thị 20 yêu cầu mỗi trang
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh sách nguồn cung cấp và lý do bảo hành để hiển thị trong form
    sources = Source.objects.all()
    reasons = WarrantyReason.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'platform_filter': platform_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'completed_requests': completed_requests,
        'platform_stats': platform_stats,
        'sources': sources,
        'reasons': reasons,
        'active_tab': 'warranty',
        'title': 'Quản lý Bảo hành',
        'platform_choices': WarrantyRequest.PLATFORM_CHOICES,
        'status_choices': WarrantyRequest.STATUS_CHOICES,
    }
    
    return render(request, 'dashboard/warranty/list.html', context)

@login_required
@user_passes_test(is_admin)
def warranty_detail(request, request_id):
    """Chi tiết yêu cầu bảo hành"""
    warranty_request = get_object_or_404(WarrantyRequest, id=request_id)
    warranty_histories = warranty_request.warranty_histories.all().order_by('-created_at')
    
    # Lấy thông tin đơn hàng nếu có
    order_details = None
    if warranty_request.order:
        order_details = {
            'code': warranty_request.order.code,
            'date': warranty_request.order.created_at,
            'total': warranty_request.order.total_amount,
            'items': warranty_request.order.items.all()
        }
    
    # Lấy danh sách dịch vụ bảo hành
    warranty_services = WarrantyService.objects.filter(is_active=True)
    
    context = {
        'warranty_request': warranty_request,
        'warranty_histories': warranty_histories,
        'order_details': order_details,
        'warranty_services': warranty_services,
        'warranty_types': WarrantyRequestHistory.WARRANTY_TYPE_CHOICES,
        'active_tab': 'warranty',
        'title': f'Chi tiết bảo hành #{warranty_request.id}',
    }
    
    return render(request, 'dashboard/warranty/detail.html', context)

@login_required
@user_passes_test(is_admin)
def process_warranty(request, request_id):
    """Xử lý yêu cầu bảo hành"""
    warranty_request = get_object_or_404(WarrantyRequest, id=request_id)
    
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        warranty_types = request.POST.getlist('warranty_types')
        added_days = request.POST.get('added_days', 0)
        refund_amount = request.POST.get('refund_amount', 0)
        new_account_username = request.POST.get('new_account_username', '')
        new_account_password = request.POST.get('new_account_password', '')
        notes = request.POST.get('notes', '')
        status = request.POST.get('status', 'processing')
        admin_notes = request.POST.get('admin_notes', '')
        
        try:
            # Cập nhật trạng thái yêu cầu bảo hành
            warranty_request.status = status
            warranty_request.admin_notes = admin_notes
            warranty_request.admin_user = request.user
            
            if status == 'completed':
                warranty_request.completed_at = timezone.now()
            
            warranty_request.save()
            
            # Tạo lịch sử bảo hành nếu hoàn thành
            if status == 'completed':
                new_account_info = {}
                if 'new_account' in warranty_types and new_account_username and new_account_password:
                    new_account_info = {
                        'username': new_account_username,
                        'password': new_account_password
                    }
                
                # Tạo lịch sử bảo hành
                WarrantyRequestHistory.objects.create(
                    warranty_request=warranty_request,
                    status=status,
                    warranty_types=warranty_types,
                    added_days=int(added_days) if added_days else 0,
                    refund_amount=float(refund_amount) if refund_amount else 0,
                    new_account_info=new_account_info,
                    notes=notes,
                    admin=request.user
                )
                
                # Nếu bù thêm ngày, cập nhật subscription
                if 'add_days' in warranty_types and int(added_days) > 0:
                    # Cập nhật subscription nếu có
                    from dashboard.models import UserSubscription
                    subscriptions = warranty_request.user.subscriptions.filter(status='active')
                    if subscriptions.exists():
                        subscription = subscriptions.first()
                        subscription.end_date = subscription.end_date + timedelta(days=int(added_days))
                        subscription.save()
                
                # Nếu hoàn tiền, cập nhật balance của người dùng
                if 'refund' in warranty_types and float(refund_amount) > 0:
                    user = warranty_request.user
                    user.balance += float(refund_amount)
                    user.save()
                    
                    # Tạo lịch sử balance
                    from accounts.models import BalanceHistory
                    BalanceHistory.objects.create(
                        user=user,
                        amount=float(refund_amount),
                        balance_after=user.balance,
                        description=f"Hoàn tiền từ bảo hành #{warranty_request.id}",
                        created_by=request.user
                    )
            
            messages.success(request, f'Đã xử lý yêu cầu bảo hành #{warranty_request.id} thành công!')
            return redirect('dashboard:warranty_detail', request_id=warranty_request.id)
            
        except Exception as e:
            messages.error(request, f'Lỗi khi xử lý bảo hành: {str(e)}')
    
    return redirect('dashboard:warranty_detail', request_id=warranty_request.id)

@login_required
def user_warranty_list(request):
    """Trang hiển thị danh sách bảo hành của người dùng"""
    # Chỉ lấy yêu cầu bảo hành của người dùng hiện tại
    warranty_requests = WarrantyRequest.objects.filter(user=request.user).order_by('-created_at')
    
    # Phân trang
    paginator = Paginator(warranty_requests, 10)  # Hiển thị 10 yêu cầu mỗi trang
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh sách lý do bảo hành cho form
    reasons = WarrantyReason.objects.filter(is_active=True)
    sources = Source.objects.filter(is_active=True)
    
    # Lấy đơn hàng của người dùng cho dropdown
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'page_obj': page_obj,
        'reasons': reasons,
        'sources': sources,
        'orders': orders,
        'platform_choices': WarrantyRequest.PLATFORM_CHOICES,
        'title': 'Lịch sử bảo hành của tôi',
    }
    
    return render(request, 'accounts/warranty/list.html', context)

@login_required
def create_warranty_request(request):
    """Tạo yêu cầu bảo hành mới từ người dùng"""
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        order_id = request.POST.get('order_id')
        account_username = request.POST.get('account_username')
        account_password = request.POST.get('account_password')
        account_type = request.POST.get('account_type')
        reason_id = request.POST.get('reason_id')
        custom_reason = request.POST.get('custom_reason', '')
        platform = request.POST.get('platform', 'website')
        source_id = request.POST.get('source_id')
        is_self_registered = request.POST.get('is_self_registered', 'off') == 'on'
        notes = request.POST.get('notes', '')
        
        error_screenshot = request.FILES.get('error_screenshot')
        
        try:
            # Kiểm tra đầu vào
            if not account_username or not account_password or not account_type:
                messages.error(request, 'Vui lòng nhập đầy đủ thông tin tài khoản!')
                return redirect('accounts:warranty_list')
            
            if not error_screenshot:
                messages.error(request, 'Vui lòng tải lên ảnh chụp lỗi!')
                return redirect('accounts:warranty_list')
            
            # Lấy đơn hàng nếu có
            order = None
            if order_id:
                try:
                    order = Order.objects.get(id=order_id, user=request.user)
                except Order.DoesNotExist:
                    pass
            
            # Lấy lý do nếu có
            reason = None
            if reason_id:
                try:
                    reason = WarrantyReason.objects.get(id=reason_id)
                except WarrantyReason.DoesNotExist:
                    pass
            
            # Lấy nguồn nếu có
            source = None
            if source_id:
                try:
                    source = Source.objects.get(id=source_id)
                except Source.DoesNotExist:
                    pass
            
            # Tạo yêu cầu bảo hành
            warranty_request = WarrantyRequest.objects.create(
                user=request.user,
                order=order,
                account_username=account_username,
                account_password=account_password,
                account_type=account_type,
                reason=reason,
                custom_reason=custom_reason if not reason else None,
                error_screenshot=error_screenshot,
                notes=notes,
                platform=platform,
                source=source,
                is_self_registered=is_self_registered,
                status='pending'
            )
            
            messages.success(request, f'Đã gửi yêu cầu bảo hành thành công! Mã yêu cầu: #{warranty_request.id}')
            
        except Exception as e:
            messages.error(request, f'Lỗi khi tạo yêu cầu bảo hành: {str(e)}')
    
    return redirect('accounts:warranty_list')

@login_required
def warranty_detail_user(request, request_id):
    """Chi tiết yêu cầu bảo hành cho người dùng"""
    warranty_request = get_object_or_404(WarrantyRequest, id=request_id, user=request.user)
    warranty_histories = warranty_request.warranty_histories.all().order_by('-created_at')
    
    context = {
        'warranty_request': warranty_request,
        'warranty_histories': warranty_histories,
        'title': f'Chi tiết yêu cầu bảo hành #{warranty_request.id}',
    }
    
    return render(request, 'accounts/warranty/detail.html', context) 