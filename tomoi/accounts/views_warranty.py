from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
import logging
import json

from dashboard.models import (
    WarrantyRequest, WarrantyReason, 
    WarrantyService, Source, WarrantyRequestHistory
)
from store.models import Order, OrderItem
from dashboard.forms import WarrantyRequestForm

@login_required
def user_warranty_list(request):
    """Trang hiển thị danh sách bảo hành của người dùng"""
    try:
        # Chỉ lấy yêu cầu bảo hành của người dùng hiện tại
        warranty_requests = WarrantyRequest.objects.filter(user=request.user).order_by('-created_at')
        
        # Phân trang
        paginator = Paginator(warranty_requests, 10)  # Hiển thị 10 yêu cầu mỗi trang
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Lấy danh sách lý do bảo hành cho form
        reasons = WarrantyReason.objects.filter(is_active=True)
        
        # Lấy danh sách đơn hàng của người dùng
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        
        # Tạo form bảo hành
        form = WarrantyRequestForm(user=request.user)
        
        context = {
            'page_obj': page_obj,
            'orders': orders,
            'reasons': reasons,
            'form': form,
            'platform_choices': WarrantyRequest.PLATFORM_CHOICES,
            'active_tab': 'warranty',
            'title': 'Bảo hành tài khoản',
            'status_choices': WarrantyRequest.STATUS_CHOICES,
        }
        
        return render(request, 'accounts/warranty/list.html', context)
    except Exception as e:
        logger.error(f"Error in user_warranty_list: {str(e)}")
        messages.error(request, 'Có lỗi xảy ra khi tải trang bảo hành. Vui lòng thử lại sau.')
        return redirect('accounts:profile')

@login_required
def create_warranty_request(request):
    """Tạo yêu cầu bảo hành mới từ người dùng"""
    if request.method == 'POST':
        form = WarrantyRequestForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            warranty_request = form.save(commit=False)
            warranty_request.user = request.user
            warranty_request.status = 'pending'
            warranty_request.save()
            
            # Tạo lịch sử bảo hành
            WarrantyRequestHistory.objects.create(
                warranty_request=warranty_request,
                status='pending',
                notes='Yêu cầu bảo hành được tạo.',
                user=request.user
            )
            
            messages.success(request, f'Đã gửi yêu cầu bảo hành thành công! Mã yêu cầu: #{warranty_request.id}')
            return redirect('accounts:warranty_detail', request_id=warranty_request.id)
        else:
            # Lấy lỗi đầu tiên để hiển thị
            error_message = next(iter(form.errors.values()))[0] if form.errors else 'Dữ liệu không hợp lệ'
            messages.error(request, f'Lỗi khi tạo yêu cầu bảo hành: {error_message}')
            return redirect('accounts:warranty_list')
    
    # Lấy danh sách lý do bảo hành cho form
    reasons = WarrantyReason.objects.filter(is_active=True)
    
    # Lấy danh sách đơn hàng của người dùng
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'form': WarrantyRequestForm(user=request.user),
        'orders': orders,
        'reasons': reasons,
        'platform_choices': WarrantyRequest.PLATFORM_CHOICES,
        'title': 'Tạo yêu cầu bảo hành',
        'status_choices': WarrantyRequest.STATUS_CHOICES,
    }
    
    return render(request, 'accounts/warranty/create.html', context)

@login_required
def warranty_detail_user(request, request_id):
    """Chi tiết yêu cầu bảo hành cho người dùng"""
    warranty = get_object_or_404(WarrantyRequest, id=request_id, user=request.user)
    warranty_history = warranty.request_histories.all().order_by('-created_at')
    
    # Khởi tạo các biến trước khi sử dụng
    new_username = None
    new_password = None
    warranty_types = []
    order_item = None
    
    # Nếu có order, lấy thông tin tài khoản từ đó
    order = warranty.order
    if order:
        order_item = OrderItem.objects.filter(order=order).first()
    
    # Lấy thông tin từ lịch sử bảo hành đã hoàn thành
    completed_history = warranty_history.filter(status='completed').first()
    if completed_history:
        # Lấy thông tin tài khoản mới nếu có
        if completed_history.new_account_info:
            try:
                account_info = completed_history.new_account_info
                if isinstance(account_info, str):
                    try:
                        account_info = json.loads(account_info)
                    except:
                        account_info = {}
                        
                if isinstance(account_info, dict):
                    new_username = account_info.get('username')
                    new_password = account_info.get('password')
            except Exception as e:
                logging.error(f"Lỗi khi xử lý thông tin tài khoản mới: {str(e)}")
        
        # Lấy loại bảo hành
        if hasattr(completed_history, 'warranty_types') and completed_history.warranty_types:
            warranty_types = completed_history.warranty_types
    
    # Lấy phản hồi mới nhất của quản trị viên
    last_response = warranty_history.exclude(notes__isnull=True).exclude(notes='').first()
    
    context = {
        'warranty': warranty,
        'warranty_history': warranty_history,
        'last_response': last_response,
        'status_choices': WarrantyRequest.STATUS_CHOICES,
        'platform_choices': WarrantyRequest.PLATFORM_CHOICES,
        'warranty_types': warranty_types,
        'completed_history': completed_history,
        'new_username': new_username,
        'new_password': new_password,
        'order_item': order_item,
        'title': f'Chi tiết yêu cầu bảo hành #{warranty.id}',
    }
    
    return render(request, 'accounts/warranty/detail.html', context) 