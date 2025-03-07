from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import PremiumSubscription, CustomUser
from datetime import timedelta
import json

@staff_member_required
def calendar_events(request):
    today = timezone.now().date()
    start_date = today - timedelta(days=30)
    end_date = today + timedelta(days=30)

    events = PremiumSubscription.objects.filter(expiry_date__range=[start_date, end_date])

    data = [{
        "id": event.id,
        "title": f"{event.product_name} - {event.user.username}",
        "start": event.expiry_date.isoformat(),
        "status": event.status,
        "username": event.user.username,
        "backgroundColor": "#df2626" if event.is_expired() else "#1cc88a",
        "borderColor": "#c51d1d" if event.is_expired() else "#19b87a"
    } for event in events]

    return JsonResponse(data, safe=False)

@staff_member_required
def premium_subscriptions(request):
    today = timezone.now().date()
    
    # Lấy các subscription theo tab
    expired = PremiumSubscription.objects.filter(expiry_date__lt=today).order_by('-expiry_date')
    today_expiring = PremiumSubscription.objects.filter(expiry_date=today)
    upcoming = PremiumSubscription.objects.filter(expiry_date__gt=today, 
                                                 expiry_date__lte=today + timedelta(days=30))
    
    data = {
        'expired': [{
            'id': sub.id,
            'product_name': sub.product_name,
            'duration': sub.duration,
            'username': sub.user.username,
            'expiry_date': sub.expiry_date.strftime('%d/%m/%Y'),
            'status': sub.get_status_display(),
            'order_id': sub.order.id if sub.order else None,
            'days_past': (today - sub.expiry_date).days
        } for sub in expired],
        
        'today': [{
            'id': sub.id,
            'product_name': sub.product_name,
            'duration': sub.duration,
            'username': sub.user.username,
            'expiry_date': 'Hôm nay',
            'status': sub.get_status_display(),
            'order_id': sub.order.id if sub.order else None
        } for sub in today_expiring],
        
        'upcoming': [{
            'id': sub.id,
            'product_name': sub.product_name,
            'duration': sub.duration,
            'username': sub.user.username,
            'expiry_date': sub.expiry_date.strftime('%d/%m/%Y'),
            'status': sub.get_status_display(),
            'order_id': sub.order.id if sub.order else None,
            'days_remaining': (sub.expiry_date - today).days
        } for sub in upcoming]
    }
    
    return JsonResponse(data)

@staff_member_required
def send_reminder(request, subscription_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Phương thức không hợp lệ'})
    
    data = json.loads(request.body)
    methods = data.get('methods', [])
    
    if not methods:
        return JsonResponse({'status': 'error', 'message': 'Vui lòng chọn ít nhất một phương thức gửi'})
    
    subscription = get_object_or_404(PremiumSubscription, id=subscription_id)
    
    # Giả lập gửi thông báo
    sent_methods = []
    for method in methods:
        # Trong thực tế, tại đây sẽ gọi các service gửi thông báo tương ứng
        if method == 'email':
            # Gửi email
            sent_methods.append('Email')
        elif method == 'sms':
            # Gửi SMS
            sent_methods.append('SMS')
        elif method == 'zalo':
            # Gửi thông báo Zalo
            sent_methods.append('Zalo')
    
    # Cập nhật trạng thái subscription
    subscription.status = 'reminded'
    subscription.reminder_sent = True
    subscription.reminder_date = timezone.now().date()
    subscription.save()
    
    return JsonResponse({
        'status': 'success', 
        'message': f'Đã gửi nhắc nhở qua {", ".join(sent_methods)}', 
        'subscription': {
            'id': subscription.id,
            'status': subscription.get_status_display()
        }
    })

@staff_member_required
def add_calendar_event(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Phương thức không hợp lệ'})
    
    data = json.loads(request.body)
    title = data.get('title')
    start = data.get('start')
    end = data.get('end', start)
    
    # Lưu vào một model EventCalendar nếu cần
    # Trong trường hợp này, chúng ta chỉ trả về thông tin để hiển thị trên calendar
    
    event = {
        'id': f"custom-{timezone.now().timestamp()}",
        'title': title,
        'start': start,
        'end': end,
        'backgroundColor': '#4e73df',
        'borderColor': '#3a5dd9'
    }
    
    return JsonResponse({'status': 'success', 'event': event}) 