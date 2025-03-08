from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from django.contrib.admin.views.decorators import staff_member_required
import json
from django.utils import timezone

@staff_member_required
@require_GET
def google_calendar_auth_temp(request):
    """Tạm thời đây là API giả lập xác thực Google Calendar."""
    try:
        # Giả lập URL xác thực - trong triển khai thực tế sẽ sử dụng OAuth thật
        auth_url = 'https://accounts.google.com/o/oauth2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=https://www.googleapis.com/auth/calendar&response_type=code'
        
        # Trả về URL xác thực để frontend có thể chuyển hướng
        return JsonResponse({
            'status': 'success',
            'auth_url': auth_url,
            'message': 'Vui lòng xác thực với Google Calendar'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@staff_member_required
def google_calendar_callback_temp(request):
    """Tạm thời đây là callback giả lập khi OAuth hoàn thành."""
    try:
        # Trong triển khai thực tế, tại đây sẽ xử lý code từ Google và lấy token
        
        # Redirect về dashboard
        return redirect('/dashboard/')
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@staff_member_required
@require_GET
def google_calendar_status_temp(request):
    """Tạm thời đây là API giả lập kiểm tra trạng thái đồng bộ."""
    try:
        # Giả lập trạng thái đã đồng bộ
        return JsonResponse({
            'status': 'success',
            'is_synced': True,
            'last_sync': '2024-04-07 14:30:25'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@staff_member_required
@require_GET
def google_calendar_sync_events_temp(request):
    """Tạm thời đây là API giả lập đồng bộ sự kiện từ Google Calendar."""
    try:
        # Giả lập đồng bộ dữ liệu từ Google Calendar
        # Trong triển khai thực tế, tại đây sẽ gọi Google Calendar API để lấy sự kiện
        
        # Trả về kết quả đồng bộ thành công
        return JsonResponse({
            'status': 'success',
            'message': 'Đã đồng bộ dữ liệu từ Google Calendar',
            'events_count': 5,  # Giả lập số lượng sự kiện đã đồng bộ
            'last_sync': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500) 