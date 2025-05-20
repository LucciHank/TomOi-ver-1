import json
import uuid
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import requests
from ..models import Product, Category
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# Giả định model để lưu trữ lịch sử cuộc trò chuyện
class ChatbotConversation:
    @classmethod
    def create(cls, user_id, session_id, history):
        # Tạo mới bản ghi lịch sử
        # Trong triển khai thực tế, sử dụng Model Django thật
        pass

@require_POST
@csrf_exempt
def chatbot_api(request):
    """API endpoint cho chatbot"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        chat_history = data.get('history', [])
        
        if not user_message:
            return JsonResponse({'success': False, 'error': 'Không có tin nhắn'})
            
        # Lấy API key từ cấu hình động (từ database)
        from tomoi.dashboard.models import APIConfig
        try:
            api_config = APIConfig.objects.filter(is_active=True, api_type='gemini').first()
            api_key = api_config.api_key if api_config else ''
            model = api_config.model if api_config else 'gemini-2.0-flash'
            temperature = api_config.temperature if api_config else 0.7
            max_tokens = api_config.max_tokens if api_config else 2048
        except Exception as e:
            # Nếu không lấy được từ model, sử dụng cài đặt fallback
            api_key = getattr(settings, 'GEMINI_API_KEY', '')
            model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')
            temperature = getattr(settings, 'GEMINI_TEMPERATURE', 0.7)
            max_tokens = getattr(settings, 'GEMINI_MAX_TOKENS', 2048)
        
        if not api_key:
            return JsonResponse({'success': False, 'error': 'API key chưa được cấu hình'})
        
        # Kiểm tra xem người dùng đang tìm kiếm theo thể loại không
        category_search = any(keyword in user_message.lower() for keyword in [
            'tìm ứng dụng', 'tìm sản phẩm', 'muốn mua', 'các loại', 'thể loại'
        ])
        
        # Kiểm tra xem người dùng đang tìm kiếm ứng dụng giải trí không
        entertainment_search = 'giải trí' in user_message.lower()
        
        # Nếu người dùng đang tìm kiếm ứng dụng giải trí
        if entertainment_search:
            # Trả về các thể loại giải trí
            categories = [
                {'id': 'music', 'name': 'Nghe nhạc'},
                {'id': 'video', 'name': 'Xem phim'},
                {'id': 'book', 'name': 'Đọc sách'},
                {'id': 'game', 'name': 'Chơi game'}
            ]
            
            return JsonResponse({
                'success': True,
                'response': 'Bạn muốn giải trí bằng hình thức nào?',
                'categories': categories
            })
            
        # Kiểm tra xem người dùng đã chọn thể loại cụ thể chưa
        music_search = any(keyword in user_message.lower() for keyword in ['nghe nhạc', 'âm nhạc', 'nhạc', 'spotify', 'youtube music'])
        video_search = any(keyword in user_message.lower() for keyword in ['xem phim', 'phim', 'netflix', 'youtube premium'])
        book_search = any(keyword in user_message.lower() for keyword in ['đọc sách', 'sách', 'ebook', 'kindle'])
        game_search = any(keyword in user_message.lower() for keyword in ['chơi game', 'game', 'trò chơi'])
        
        # Nếu người dùng tìm sản phẩm nghe nhạc
        if music_search:
            # Lấy sản phẩm từ database
            products = Product.objects.filter(category__name__icontains='nhạc')[:3]
            
            # Nếu không có trong DB, dùng mẫu
            if not products:
                products_data = [
                    {
                        'name': 'Spotify Premium 1 tháng',
                        'price': '59.000 VNĐ',
                        'image': '/static/store/images/products/spotify.jpg',
                        'url': '/products/spotify-premium/'
                    },
                    {
                        'name': 'YouTube Music Premium',
                        'price': '79.000 VNĐ',
                        'image': '/static/store/images/products/youtube-music.jpg',
                        'url': '/products/youtube-music/'
                    },
                    {
                        'name': 'Apple Music 3 tháng',
                        'price': '165.000 VNĐ',
                        'image': '/static/store/images/products/apple-music.jpg',
                        'url': '/products/apple-music/'
                    }
                ]
            else:
                # Chuyển đổi Queryset thành list dicts
                products_data = []
                for product in products:
                    products_data.append({
                        'name': product.name,
                        'price': f"{product.price:,.0f} VNĐ",
                        'image': product.image.url if product.image else '/static/store/images/default-product.jpg',
                        'url': f'/products/{product.slug}/'
                    })
            
            return JsonResponse({
                'success': True,
                'response': 'Đây là một số gói dịch vụ nghe nhạc phổ biến:',
                'products': products_data
            })
            
        # Tương tự cho video, sách và game
        if video_search:
            # Lấy sản phẩm từ database
            products = Product.objects.filter(category__name__icontains='phim')[:3]
            
            # Nếu không có trong DB, dùng mẫu
            if not products:
                products_data = [
                    {
                        'name': 'Netflix Standard 1 tháng',
                        'price': '180.000 VNĐ',
                        'image': '/static/store/images/products/netflix.jpg',
                        'url': '/products/netflix-standard/'
                    },
                    {
                        'name': 'YouTube Premium',
                        'price': '119.000 VNĐ',
                        'image': '/static/store/images/products/youtube-premium.jpg',
                        'url': '/products/youtube-premium/'
                    },
                    {
                        'name': 'Disney+ 3 tháng',
                        'price': '239.000 VNĐ',
                        'image': '/static/store/images/products/disneyplus.jpg',
                        'url': '/products/disney-plus/'
                    }
                ]
            else:
                # Chuyển đổi Queryset thành list dicts
                products_data = []
                for product in products:
                    products_data.append({
                        'name': product.name,
                        'price': f"{product.price:,.0f} VNĐ",
                        'image': product.image.url if product.image else '/static/store/images/default-product.jpg',
                        'url': f'/products/{product.slug}/'
                    })
            
            return JsonResponse({
                'success': True,
                'response': 'Đây là một số dịch vụ xem phim phổ biến:',
                'products': products_data
            })
            
        # Tạo prompt cho Gemini API
        from tomoi.dashboard.models import ChatbotConfig
        try:
            chatbot_config = ChatbotConfig.objects.filter(is_active=True).first()
            system_prompt = chatbot_config.system_prompt if chatbot_config else None
        except:
            system_prompt = None
            
        if not system_prompt:
            system_prompt = getattr(settings, 'GEMINI_SYSTEM_PROMPT', 
                """Bạn là chatbot tư vấn sản phẩm của TomOi, chỉ trả lời dựa trên thông tin sản phẩm và dịch vụ. 
                Nếu người dùng đặt câu hỏi nằm ngoài phạm vi này, hãy lịch sự chuyển hướng họ về các dịch vụ hiện có. 
                Giữ câu trả lời ngắn gọn, thân thiện và hữu ích. Không bao giờ tự giới thiệu là AI.""")
        
        # Chuẩn bị dữ liệu gửi đến Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        # Tạo tin nhắn với lịch sử
        messages = []
        # Thêm prompt hệ thống
        messages.append({
            "role": "system",
            "parts": [{"text": system_prompt}]
        })
        
        # Thêm lịch sử trò chuyện (chỉ lấy tối đa 10 tin nhắn gần nhất để tránh quá nhiều tokens)
        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
        for msg in recent_history:
            role = "user" if msg["role"] == "user" else "model"
            messages.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        # Thêm tin nhắn hiện tại của người dùng nếu chưa có trong lịch sử
        if not chat_history or chat_history[-1]["role"] != "user" or chat_history[-1]["content"] != user_message:
            messages.append({
                "role": "user",
                "parts": [{"text": user_message}]
            })
        
        data = {
            "contents": messages,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.9,
                "topK": 40
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        print("Gửi yêu cầu đến Gemini API...")
        response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        response_data = response.json()
        
        # Xử lý phản hồi
        if response.status_code == 200:
            try:
                ai_message = response_data['candidates'][0]['content']['parts'][0]['text']
                
                # Thêm vào lịch sử
                chat_history.append({
                    "role": "assistant",
                    "content": ai_message
                })
                
                # Lưu lịch sử chat nếu có user đăng nhập
                user_id = request.user.id if request.user.is_authenticated else None
                if user_id:
                    ChatbotConversation.create(user_id, session_id, chat_history)
                
                return JsonResponse({
                    'success': True,
                    'response': ai_message
                })
            except (KeyError, IndexError) as e:
                print(f"Lỗi khi phân tích phản hồi: {e}")
                print(f"Phản hồi nhận được: {response_data}")
                return JsonResponse({
                    'success': False,
                    'error': 'Không thể xử lý phản hồi từ chatbot'
                })
        else:
            error_message = response_data.get('error', {}).get('message', 'Lỗi từ API')
            print(f"Lỗi API: {error_message}")
            return JsonResponse({
                'success': False,
                'error': error_message
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dữ liệu không hợp lệ'})
    except Exception as e:
        print(f"Lỗi không xác định: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
@csrf_exempt
def log_chat(request):
    """API endpoint để lưu lịch sử chat"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id', '')
        history = data.get('history', [])
        
        if not session_id or not history:
            return JsonResponse({'success': False, 'message': 'Thiếu thông tin'})
        
        # Lưu lịch sử chat nếu có user đăng nhập
        user_id = request.user.id if request.user.is_authenticated else None
        
        # Lưu vào database hoặc file log
        now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        log_data = {
            'timestamp': now,
            'session_id': session_id,
            'user_id': user_id,
            'history': history
        }
        
        if user_id:
            ChatbotConversation.create(user_id, session_id, history)
        
        # Lưu vào file log (tùy chọn)
        import os
        log_dir = os.path.join(settings.BASE_DIR, 'logs', 'chatbot')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'chat_{timezone.now().strftime("%Y%m%d")}.log')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{json.dumps(log_data, ensure_ascii=False)}\n")
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        print(f"Lỗi khi lưu lịch sử chat: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})