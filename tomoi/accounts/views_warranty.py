from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

from dashboard.models import (
    WarrantyRequest, WarrantyReason, 
    WarrantyService, Source, WarrantyRequestHistory
)
from store.models import Order
from dashboard.forms import WarrantyRequestForm

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
    
    # Tạo form
    form = WarrantyRequestForm(user=request.user)
    
    context = {
        'page_obj': page_obj,
        'reasons': reasons,
        'sources': sources,
        'orders': orders,
        'platform_choices': WarrantyRequest.PLATFORM_CHOICES,
        'form': form,
        'title': 'Bảo hành tài khoản',
    }
    
    return render(request, 'accounts/warranty/list.html', context)

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
                notes='Yêu cầu bảo hành được tạo.'
            )
            
            messages.success(request, f'Đã gửi yêu cầu bảo hành thành công! Mã yêu cầu: #{warranty_request.id}')
            return redirect('accounts:warranty_detail', request_id=warranty_request.id)
        else:
            errors = form.errors
            error_message = "\n".join([f"{field}: {error}" for field, error in errors.items()])
            messages.error(request, f'Lỗi khi tạo yêu cầu bảo hành: {error_message}')
            return redirect('accounts:warranty_list')
    
    # GET request - hiển thị form
    reasons = WarrantyReason.objects.filter(is_active=True)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'form': WarrantyRequestForm(user=request.user),
        'reasons': reasons,
        'orders': orders,
        'platform_choices': WarrantyRequest.PLATFORM_CHOICES,
        'title': 'Tạo yêu cầu bảo hành',
    }
    
    return render(request, 'accounts/warranty/create.html', context)

@login_required
def warranty_detail_user(request, request_id):
    """Chi tiết yêu cầu bảo hành cho người dùng"""
    warranty = get_object_or_404(WarrantyRequest, id=request_id, user=request.user)
    warranty_history = warranty.request_histories.all().order_by('-created_at')
    
    # Lấy thông tin bổ sung
    order = warranty.order
    warranty_types = []
    days_added = 0
    refund_amount = 0
    new_account_info = ""
    
    # Lấy thông tin từ lịch sử bảo hành đã hoàn thành
    completed_history = warranty_history.filter(status='completed').first()
    if completed_history:
        try:
            days_added = completed_history.added_days
            refund_amount = completed_history.refund_amount
            new_account_info = completed_history.new_account_info
            warranty_types = completed_history.warranty_types
        except:
            pass
    
    # Lấy response mới nhất
    last_response = warranty_history.exclude(notes='').first()
    
    context = {
        'warranty': warranty,
        'warranty_history': warranty_history,
        'order': order,
        'status_choices': WarrantyRequest.STATUS_CHOICES,
        'platform_choices': WarrantyRequest.PLATFORM_CHOICES,
        'warranty_types': warranty_types,
        'days_added': days_added,
        'refund_amount': refund_amount,
        'new_account_info': new_account_info,
        'last_response': last_response,
        'title': f'Chi tiết yêu cầu bảo hành #{warranty.id}',
    }
    
    return render(request, 'accounts/warranty/detail.html', context) 