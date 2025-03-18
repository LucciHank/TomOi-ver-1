# API views sẽ được triển khai sau 
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from dashboard.models.event import Event
from ..models.chatbot import ChatLog
from django.utils import timezone
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

def test_api(request):
    """
    API Endpoint để kiểm tra kết nối Gemini API
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Chỉ hỗ trợ phương thức POST'})
    
    try:
        # Xử lý cả Content-Type: application/json và application/x-www-form-urlencoded
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        api_key = data.get('api_key')
        model = data.get('model', 'gemini-1.5-flash')
        
        if not api_key:
            return JsonResponse({'success': False, 'message': 'Thiếu API key'})
            
        print(f"Test API với key: {api_key[:5]}... và model: {model}")
        
        # Sử dụng thư viện chính thức từ Google
        from google import genai
        
        try:
            # Khởi tạo client và thử gọi API
            client = genai.Client(api_key=api_key)
            
            # Trình kiểm tra mô hình trước để tránh lỗi model không tồn tại
            available_models = [model.name for model in client.models.list()]
            print(f"Các mô hình có sẵn: {available_models}")
            
            # Sử dụng model_name đầy đủ
            model_name = model
            if not model.startswith("models/"):
                model_name = f"models/{model}"
                
            # Tạo nội dung đơn giản để kiểm tra
            response = client.models.generate_content(
                model=model_name,
                contents=["Xin chào, đây là tin nhắn kiểm tra kết nối. Trả lời ngắn gọn."]
            )
            
            if response and hasattr(response, 'text'):
                return JsonResponse({
                    'success': True,
                    'message': f'Kết nối thành công với model {model}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Không nhận được phản hồi hợp lệ từ API'
                })
                
        except Exception as api_error:
            error_message = str(api_error)
            print(f"Lỗi API: {error_message}")
            
            if "API key not valid" in error_message:
                return JsonResponse({
                    'success': False,
                    'message': 'API key không hợp lệ. Vui lòng kiểm tra lại.'
                })
            elif "model not found" in error_message.lower():
                return JsonResponse({
                    'success': False,
                    'message': f'Không tìm thấy model {model}. Vui lòng thử model khác.'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'Lỗi API: {error_message}'
                })
                
    except ImportError:
        return JsonResponse({
            'success': False,
            'message': 'Thiếu thư viện google-generativeai. Vui lòng cài đặt: pip install google-generativeai'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dữ liệu JSON không hợp lệ'
        })
    except Exception as e:
        print(f"Lỗi kiểm tra API không xác định: {str(e)}")
        return JsonResponse({
            'success': False, 
            'message': f'Lỗi: {str(e)}'
        })

def get_chat_detail(request, chat_id):
    """API để lấy chi tiết cuộc trò chuyện"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Không có quyền truy cập'}, status=403)
    
    try:
        # Lấy thông tin log chat
        chat_logs = ChatLog.objects.filter(session_id=chat_id).order_by('created_at')
        
        if not chat_logs.exists():
            return JsonResponse({'success': False, 'message': 'Không tìm thấy cuộc trò chuyện'}, status=404)
        
        # Chuẩn bị dữ liệu trả về
        messages = []
        
        for log in chat_logs:
            # Thêm tin nhắn người dùng
            messages.append({
                'role': 'user',
                'content': log.user_query,
                'timestamp': log.created_at.strftime('%H:%M:%S %d/%m/%Y')
            })
            
            # Thêm tin nhắn bot
            messages.append({
                'role': 'bot',
                'content': log.response,
                'timestamp': log.created_at.strftime('%H:%M:%S %d/%m/%Y')
            })
        
        # Trả về dữ liệu
        return JsonResponse({
            'success': True,
            'session_id': chat_id,
            'user': chat_logs.first().user.username if chat_logs.first().user else 'Khách vãng lai',
            'start_time': chat_logs.first().created_at.strftime('%H:%M:%S %d/%m/%Y'),
            'end_time': chat_logs.last().created_at.strftime('%H:%M:%S %d/%m/%Y'),
            'messages': messages
        })
        
    except Exception as e:
        print(f"Lỗi khi lấy chi tiết trò chuyện: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Lỗi: {str(e)}'}, status=500) 