import json
import uuid
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import requests
from django.shortcuts import render
from django.utils import timezone
# Thay đổi import để phù hợp với cấu trúc thực tế
try:
    try:
        from dashboard.models.chatbot import ChatbotConfig
        from dashboard.models.api import APIConfig
    except ImportError:
        try:
            from dashboard.models.api import ChatbotConfig, APIConfig
        except ImportError:
            try:
                from dashboard.models.settings import ChatbotConfig, APIConfig
            except ImportError:
                # Fallback - tạo các class giả
                class ChatbotConfig:
                    @classmethod
                    def objects(cls):
                        return type('Manager', (), {'filter': lambda **kwargs: [None]})()
                
                class APIConfig:
                    @classmethod
                    def objects(cls):
                        return type('Manager', (), {'filter': lambda **kwargs: [None]})()
except Exception as e:
    print(f"Lỗi khi import models: {e}")

try:
    from dashboard.models.conversation import ChatbotConversation
except ImportError:
    # Fallback
    class ChatbotConversation:
        @classmethod
        def create(cls, *args, **kwargs):
            pass

from django.contrib.auth import get_user_model
User = get_user_model()
from ..models import Product, Category

def get_active_api_config():
    """Lấy cấu hình API đang hoạt động từ database"""
    try:
        return APIConfig.objects.filter(is_active=True, api_type='gemini').first()
    except Exception as e:
        print(f"Lỗi khi lấy cấu hình API: {e}")
        return None

def get_active_chatbot_config():
    """Lấy cấu hình chatbot đang hoạt động từ database"""
    try:
        return ChatbotConfig.objects.filter(is_active=True).first()
    except Exception as e:
        print(f"Lỗi khi lấy cấu hình chatbot: {e}")
        return None

@require_POST
@csrf_exempt
def chatbot_api(request):
    """API endpoint cho chatbot"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        history = data.get('history', [])
        
        # Lấy cấu hình API và chatbot từ database
        api_config = get_active_api_config()
        chatbot_config = get_active_chatbot_config()
        
        if not api_config:
            return JsonResponse({
                'success': False,
                'error': 'Chưa cấu hình API cho chatbot'
            })
            
        # Xây dựng messages theo định dạng của Gemini
        messages = []
        
        # Thêm system prompt
        system_prompt = chatbot_config.system_prompt if chatbot_config else "Bạn là trợ lý ảo của TomOi, hỗ trợ khách hàng một cách lịch sự và chuyên nghiệp. Trả lời bằng tiếng Việt, ngắn gọn và hữu ích."
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Thêm lịch sử trò chuyện
        for msg in history:
            role = msg.get('role', '')
            content = msg.get('content', '')
            if role and content:
                messages.append({
                    "role": role,
                    "content": content
                })
        
        # API URL cho Gemini
        api_url = api_config.endpoint or f"https://generativelanguage.googleapis.com/v1beta/models/{api_config.model}:generateContent"
        
        # Xây dựng request data
        request_data = {
            "contents": messages,
            "generationConfig": {
                "temperature": api_config.temperature,
                "maxOutputTokens": api_config.max_tokens,
                "topP": 0.9
            }
        }
        
        # Gửi request đến API Gemini
        headers = {
            "Content-Type": "application/json"
        }
        
        # Thêm API key vào header hoặc params tùy theo cách thức
        if "googleapis.com" in api_url:
            api_url += f"?key={api_config.api_key}"
        else:
            headers["Authorization"] = f"Bearer {api_config.api_key}"
        
        response = requests.post(
            api_url,
            headers=headers,
            json=request_data,
            timeout=30
        )
        
        # Xử lý phản hồi từ API
        if response.status_code == 200:
            response_data = response.json()
            
            # Trích xuất phản hồi từ Gemini
            try:
                bot_response = response_data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                bot_response = "Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này."
            
            # Tìm kiếm sản phẩm nếu có yêu cầu
            products = []
            if "sản phẩm" in user_message.lower() or "mua" in user_message.lower():
                # Tìm kiếm sản phẩm dựa trên tin nhắn
                search_terms = user_message.lower().split()
                product_results = Product.objects.filter(is_active=True)[:5]
                
                # Chuyển đổi sang định dạng JSON
                for product in product_results:
                    products.append({
                        'id': product.id,
                        'name': product.name,
                        'price': str(product.price),
                        'thumbnail': product.thumbnail.url if product.thumbnail else '',
                        'url': f"/product/{product.id}/"
                    })
            
            # Trả về kết quả
            return JsonResponse({
                'success': True,
                'response': bot_response,
                'products': products
            })
        else:
            error_message = f"Lỗi API: {response.status_code} - {response.text}"
            print(error_message)
            return JsonResponse({
                'success': False,
                'error': 'Không thể kết nối đến dịch vụ AI'
            })
            
    except Exception as e:
        print(f"Lỗi chatbot: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_POST
@csrf_exempt
def log_chat(request):
    """API endpoint để lưu lịch sử chat"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id', '')
        history = data.get('history', [])
        
        if not session_id or not history:
            return JsonResponse({'success': False, 'error': 'Missing data'})
        
        # Lấy user_id nếu đã đăng nhập
        user_id = request.user.id if request.user.is_authenticated else None
        
        # Lưu vào database
        if user_id:
            ChatbotConversation.create(user_id, session_id, history)
        
        # Lưu vào file log (tùy chọn)
        import os
        log_dir = os.path.join(settings.BASE_DIR, 'logs', 'chatbot')
        os.makedirs(log_dir, exist_ok=True)
        
        now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        log_data = {
            'timestamp': now,
            'session_id': session_id,
            'user_id': user_id,
            'history': history
        }
        
        log_file = os.path.join(log_dir, f'chat_{timezone.now().strftime("%Y%m%d")}.log')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{json.dumps(log_data, ensure_ascii=False)}\n")
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        print(f"Lỗi khi lưu lịch sử chat: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}) 