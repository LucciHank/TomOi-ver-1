# API views sẽ được triển khai sau 
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from dashboard.models.event import Event
import json

@csrf_exempt
@require_http_methods(["GET"])
def get_events(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse([], safe=False)  # Trả về mảng rỗng thay vì lỗi 401
            
        events = Event.objects.all()
        data = [{
            'id': event.id,
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'allDay': event.all_day,
            'backgroundColor': event.color,
            'borderColor': event.color,
            'extendedProps': {
                'type': event.event_type,
                'description': event.description
            }
        } for event in events]
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(f"Lỗi khi lấy sự kiện: {str(e)}")
        return JsonResponse([], safe=False)

@csrf_exempt
@require_http_methods(["POST"])
def create_event(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    try:
        data = json.loads(request.body)
        event = Event.objects.create(
            title=data['title'],
            event_type=data['type'],
            start_time=data['start'],
            end_time=data['end'],
            description=data.get('description', ''),
            all_day=data.get('allDay', False),
            color=get_event_color(data['type'])
        )
        return JsonResponse({
            'id': event.id,
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

def get_event_color(event_type):
    colors = {
        'meeting': '#4e73df',
        'deadline': '#e74a3b',
        'reminder': '#f6c23e',
        'other': '#1cc88a'
    }
    return colors.get(event_type, '#4e73df') 

@csrf_exempt
@require_http_methods(["PUT"])
def update_event(request, event_id):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
            
        data = json.loads(request.body)
        event = Event.objects.get(id=event_id)
        
        # Cập nhật thông tin
        event.title = data['title']
        event.event_type = data['type']
        event.start_time = data['start']
        event.end_time = data['end']
        event.description = data.get('description', '')
        event.all_day = data.get('allDay', False)
        event.color = get_event_color(data['type'])
        event.save()
        
        return JsonResponse({
            'id': event.id,
            'status': 'success'
        })
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_event(request, event_id):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
            
        event = Event.objects.get(id=event_id)
        event.delete()
        
        return JsonResponse({
            'status': 'success'
        })
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400) 