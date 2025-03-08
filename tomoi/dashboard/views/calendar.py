from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import PremiumSubscription, CustomUser
from ..models.base import CalendarEvent
from datetime import timedelta, datetime
import json
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@staff_member_required
def calendar_events(request):
    """API trả về dữ liệu sự kiện cho lịch"""
    try:
        today = timezone.now().date()
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=60)  # Mở rộng khoảng thời gian

        # Có thể lấy từ model PremiumSubscription
        subscriptions = PremiumSubscription.objects.filter(
            expiry_date__range=[start_date, end_date]
        )
        
        events = []
        for sub in subscriptions:
            # Chuyển đổi thành định dạng sự kiện FullCalendar
            event = {
                'id': f'sub_{sub.id}',
                'title': f'{sub.product_name} - {sub.user.username}',
                'start': sub.expiry_date.isoformat(),
                'className': 'bg-danger' if sub.is_expired() else 'bg-warning',
                'extendedProps': {
                    'type': 'subscription',
                    'status': sub.status,
                    'user': sub.user.username
                }
            }
            events.append(event)
        
        # Thêm các sự kiện khác từ CalendarEvent nếu có
        calendar_events = CalendarEvent.objects.filter(
            start_time__date__range=[start_date, end_date]
        )
        
        for event in calendar_events:
            events.append({
                'id': f'event_{event.id}',
                'title': event.title,
                'start': event.start_time.isoformat(),
                'end': event.end_time.isoformat(),
                'allDay': event.is_all_day,
                'className': f'bg-primary',
                'extendedProps': {
                    'type': event.event_type,
                    'description': event.description
                }
            })
        
        # In ra số lượng sự kiện được trả về để debug
        print(f"Returning {len(events)} calendar events")
        
        return JsonResponse(events, safe=False)
    except Exception as e:
        # Log lỗi để dễ debug
        print(f"Error in calendar_events: {str(e)}")
        return JsonResponse([], safe=False)

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