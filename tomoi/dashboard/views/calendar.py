from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
# from accounts.models import PremiumSubscription, CustomUser  # Tạm thời comment lại
from datetime import timedelta, datetime
import json
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@staff_member_required
def calendar_events(request):
    """API trả về dữ liệu sự kiện cho lịch"""
    # Tạm thời trả về danh sách sự kiện giả lập thay vì truy vấn DB
    events = [
        {
            'id': 'event1',
            'title': 'Họp nhóm phát triển',
            'start': '2025-03-15',
            'className': 'bg-primary',
            'extendedProps': {
                'type': 'meeting',
                'description': 'Thảo luận về tính năng mới'
            }
        },
        {
            'id': 'event2',
            'title': 'Hạn chót dự án',
            'start': '2025-03-25',
            'className': 'bg-danger',
            'extendedProps': {
                'type': 'deadline',
                'description': 'Hoàn thành module thanh toán'
            }
        },
        {
            'id': 'event3',
            'title': 'Nhắc nhở: Gia hạn dịch vụ',
            'start': '2025-03-10',
            'className': 'bg-warning',
            'extendedProps': {
                'type': 'reminder',
                'description': 'Gửi email nhắc nhở khách hàng'
            }
        }
    ]
    
    return JsonResponse(events, safe=False)

@staff_member_required
def premium_subscriptions(request):
    """API trả về danh sách subscription gần hết hạn"""
    # Tạm thời trả về dữ liệu giả lập
    result = [
        {
            'id': 1,
            'username': 'user1',
            'product': 'Gói Premium',
            'expiry_date': '15/03/2025',
            'days_left': 10,
            'status': 'not_reminded',
            'reminder_sent': False
        },
        {
            'id': 2,
            'username': 'user2',
            'product': 'Gói VIP',
            'expiry_date': '20/03/2025',
            'days_left': 15,
            'status': 'not_reminded',
            'reminder_sent': False
        }
    ]
    
    return JsonResponse(result, safe=False)

@staff_member_required
@require_POST
def send_reminder(request, subscription_id):
    """Gửi email nhắc nhở gia hạn"""
    # Giả lập việc gửi email nhắc nhở
    return JsonResponse({'status': 'success', 'message': 'Đã gửi email nhắc nhở'})

@staff_member_required
@require_POST
def add_calendar_event(request):
    """Thêm sự kiện vào lịch"""
    data = json.loads(request.body)
    # Giả lập việc lưu sự kiện vào DB
    event_id = f"custom-{timezone.now().timestamp()}"
    
    return JsonResponse({
        'status': 'success',
        'event': {
            'id': event_id,
            'title': data.get('title'),
            'start': data.get('start'),
            'end': data.get('end'),
            'allDay': data.get('allDay', False),
            'className': 'bg-primary',
            'extendedProps': {
                'description': data.get('description', ''),
                'type': 'custom'
            }
        }
    })

@staff_member_required
@require_POST
def cancel_subscription(request, subscription_id):
    """Hủy đăng ký premium"""
    data = json.loads(request.body)
    reasons = data.get('reasons', [])
    
    # Giả lập việc cập nhật trạng thái đăng ký trong DB
    return JsonResponse({'status': 'success'}) 