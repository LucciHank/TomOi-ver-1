from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.utils import timezone
import json
import time
import uuid
import requests
from ..models.chatbot import (
    ChatbotConfig, APIIntegration, ChatLog, 
    AllowedCategory, ForbiddenKeyword
)
from store.models import Product, Category
from dashboard.models.api import APIConfig

def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Trang tổng quan Chatbot"""
    # Lấy thông tin cấu hình hiện tại
    try:
        config = ChatbotConfig.objects.filter(is_active=True).first()
        api = APIConfig.objects.filter(is_active=True).first()
    except Exception as e:
        print(f"Lỗi khi lấy cấu hình chatbot: {str(e)}")
        config = None
        api = None
    
    # Thống kê cơ bản
    context = {
        'total_chats': 0,
        'resolution_rate': 0,
        'avg_response_time': 0,
        'avg_satisfaction': 0,
        'active_tab': 'chatbot',
        'config': config,
        'api_config': api
    }
    
    return render(request, 'dashboard/chatbot/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def chatbot_api_settings(request):
    """Trang cấu hình API Chatbot"""
    active_api_config = APIConfig.objects.filter(is_active=True, api_type='gemini').first()
    
    context = {
        'active_api_config': active_api_config,
        'active_tab': 'chatbot'
    }
    
    return render(request, 'dashboard/chatbot/api.html', context)

@login_required
@user_passes_test(is_admin)
@require_POST
def chatbot_save_api(request):
    """Lưu cấu hình API"""
    try:
        data = json.loads(request.body)
        api_type = data.get('api_type')
        api_key = data.get('api_key')
        model = data.get('model')
        temperature = float(data.get('temperature', 0.7))
        max_tokens = int(data.get('max_tokens', 2048))
        endpoint = data.get('endpoint', '')
        
        # Debug log
        print(f"Received API config: type={api_type}, key={api_key[:5]}..., model={model}")
        
        # Kiểm tra API key
        test_result = test_api_connection(api_type, api_key, model, endpoint)
        
        if not test_result.get('success'):
            return JsonResponse({
                'success': False,
                'message': f'Kiểm tra API thất bại: {test_result.get("message")}'
            })
        
        # Lưu cấu hình
        try:
            config = APIConfig.objects.filter(api_type=api_type).first()
            if config:
                config.api_key = api_key
                config.model = model
                config.temperature = temperature
                config.max_tokens = max_tokens
                config.endpoint = endpoint
                config.is_active = True
                config.save()
                print(f"Updated existing API config: {config.id}")
            else:
                config = APIConfig.objects.create(
                    api_type=api_type,
                    api_key=api_key,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    endpoint=endpoint,
                    is_active=True
                )
                print(f"Created new API config: {config.id}")
            
            # Vô hiệu hóa các cấu hình khác cùng loại
            APIConfig.objects.filter(api_type=api_type).exclude(id=config.id).update(is_active=False)
            
            return JsonResponse({
                'success': True,
                'message': 'Đã lưu cấu hình API thành công'
            })
        except Exception as e:
            print(f"Database error when saving API config: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Lỗi database: {str(e)}'
            })
            
    except Exception as e:
        print(f"Unexpected error when saving API config: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })

@login_required
@user_passes_test(is_admin)
@require_POST
def chatbot_test_api(request):
    """Kiểm tra kết nối API"""
    try:
        data = json.loads(request.body)
        api_type = data.get('api_type')
        api_key = data.get('api_key')
        model = data.get('model', 'gemini-pro')
        endpoint = data.get('endpoint', '')
        
        result = test_api_connection(api_type, api_key, model, endpoint)
        
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })

@login_required
@user_passes_test(is_admin)
def settings(request):
    """Trang cài đặt Chatbot"""
    # Lấy cấu hình hiện tại nếu có
    try:
        config = ChatbotConfig.objects.filter(is_active=True).first()
        api_config = APIConfig.objects.filter(is_active=True).first()
        
        # Log để kiểm tra
        if config:
            print(f"Đã tìm thấy cấu hình chatbot: {config.name}, is_active={config.is_active}")
        if api_config:
            print(f"Đã tìm thấy cấu hình API: {api_config.api_type}, model={api_config.model}")
            
    except Exception as e:
        print(f"Lỗi khi lấy cấu hình chatbot: {str(e)}")
        config = None
        api_config = None
    
    context = {
        'active_tab': 'chatbot',
        'config': config,
        'api_config': api_config
    }
    
    return render(request, 'dashboard/chatbot/settings.html', context)

@login_required
@user_passes_test(is_admin)
def logs(request):
    """Trang lịch sử trò chuyện"""
    context = {
        'logs': [],  # Thay bằng dữ liệu thực tế
        'active_tab': 'chatbot'
    }
    
    return render(request, 'dashboard/chatbot/logs.html', context)

@login_required
@user_passes_test(is_admin)
def responses(request):
    """Trang quản lý câu trả lời tự động"""
    context = {
        'responses': [],  # Thay bằng dữ liệu thực tế
        'active_tab': 'chatbot'
    }
    
    return render(request, 'dashboard/chatbot/responses.html', context)

def test_api_connection(api_type, api_key, model, endpoint=None):
    """Kiểm tra kết nối API"""
    print(f"Kiểm tra kết nối {api_type} API với key: {api_key[:5]}...")
    
    try:
        if api_type == 'gemini':
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model_obj = genai.GenerativeModel(model)
            response = model_obj.generate_content("Xin chào, đây là tin nhắn kiểm tra kết nối. Trả lời ngắn gọn.")
            
            if response and hasattr(response, 'text'):
                return {
                    'success': True,
                    'message': 'Kết nối Gemini API thành công'
                }
            return {
                'success': False,
                'message': 'Không nhận được phản hồi hợp lệ từ Gemini API'
            }
            
        elif api_type == 'openai':
            import openai
            openai.api_key = api_key
            if endpoint:
                openai.api_base = endpoint
                
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "user", "content": "Xin chào, đây là tin nhắn kiểm tra kết nối. Trả lời ngắn gọn."}
                ],
                max_tokens=20
            )
            
            if response and 'choices' in response and len(response['choices']) > 0:
                return {
                    'success': True,
                    'message': 'Kết nối OpenAI API thành công'
                }
            return {
                'success': False,
                'message': 'Không nhận được phản hồi hợp lệ từ OpenAI API'
            }
            
        # Thêm các loại API khác nếu cần
        
        return {
            'success': False,
            'message': f'Loại API không được hỗ trợ: {api_type}'
        }
        
    except Exception as e:
        print(f"Lỗi kết nối: {str(e)}")
        return {
            'success': False,
            'message': f'Lỗi kết nối: {str(e)}'
        }

@staff_member_required
def chatbot_dashboard(request):
    """Dashboard chính của chatbot"""
    # Lấy thống kê cho dashboard
    total_chats = ChatLog.objects.count()
    success_chats = ChatLog.objects.filter(status='success').count()
    filtered_chats = ChatLog.objects.filter(status='filtered').count()
    error_chats = ChatLog.objects.filter(status='error').count()
    
    # Tỷ lệ giải quyết
    resolution_rate = (success_chats / total_chats * 100) if total_chats > 0 else 0
    
    # Thời gian phản hồi trung bình (ms)
    avg_response_time = ChatLog.objects.filter(
        api_response_time__gt=0
    ).aggregate(Avg('api_response_time'))['api_response_time__avg'] or 0
    
    # Đánh giá trung bình của người dùng
    avg_satisfaction = ChatLog.objects.filter(
        satisfaction_rating__gt=0
    ).aggregate(Avg('satisfaction_rating'))['satisfaction_rating__avg'] or 0
    
    # Lấy 10 chat gần đây nhất
    recent_chats = ChatLog.objects.all().order_by('-created_at')[:10]
    
    context = {
        'total_chats': total_chats,
        'success_chats': success_chats,
        'filtered_chats': filtered_chats,
        'error_chats': error_chats,
        'resolution_rate': round(resolution_rate, 1),
        'avg_response_time': round(avg_response_time, 2),
        'avg_satisfaction': round(avg_satisfaction, 1),
        'recent_chats': recent_chats,
    }
    
    return render(request, 'dashboard/chatbot/dashboard.html', context)

@staff_member_required
def chatbot_config(request, config_id=None):
    """Tạo/chỉnh sửa cấu hình chatbot"""
    config = None
    if config_id:
        config = get_object_or_404(ChatbotConfig, id=config_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        base_prompt = request.POST.get('base_prompt')
        rejection_message = request.POST.get('rejection_message')
        is_active = request.POST.get('is_active') == 'on'
        
        if config:
            # Cập nhật cấu hình hiện có
            config.name = name
            config.base_prompt = base_prompt
            config.rejection_message = rejection_message
            config.is_active = is_active
            config.save()
        else:
            # Tạo cấu hình mới
            config = ChatbotConfig.objects.create(
                name=name,
                base_prompt=base_prompt,
                rejection_message=rejection_message,
                is_active=is_active
            )
        
        # Xử lý danh mục được phép
        allowed_categories = request.POST.getlist('allowed_categories[]')
        
        # Xóa các danh mục cũ
        config.allowed_categories.all().delete()
        
        # Thêm danh mục mới
        for category_id in allowed_categories:
            category = Category.objects.get(id=category_id)
            AllowedCategory.objects.create(
                config=config,
                category=category
            )
        
        # Xử lý từ khóa cấm
        forbidden_keywords = request.POST.get('forbidden_keywords', '').strip().split('\n')
        
        # Xóa các từ khóa cũ
        config.forbidden_keywords.all().delete()
        
        # Thêm từ khóa mới
        for keyword in forbidden_keywords:
            keyword = keyword.strip()
            if keyword:
                ForbiddenKeyword.objects.create(
                    config=config,
                    keyword=keyword
                )
        
        # Nếu cấu hình này được đánh dấu là active, hãy tắt các cấu hình khác
        if is_active:
            ChatbotConfig.objects.exclude(id=config.id).update(is_active=False)
        
        return redirect('dashboard:chatbot_dashboard')
    
    # Get all categories for dropdown
    all_categories = Category.objects.all()
    
    context = {
        'config': config,
        'all_categories': all_categories,
    }
    
    return render(request, 'dashboard/chatbot/config.html', context)

@staff_member_required
def api_integration(request):
    """Quản lý tích hợp API"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            integration_id = request.POST.get('integration_id')
            name = request.POST.get('name')
            api_type = request.POST.get('api_type')
            api_url = request.POST.get('api_url')
            api_key = request.POST.get('api_key')
            api_version = request.POST.get('api_version')
            timeout = int(request.POST.get('timeout', 30))
            is_active = request.POST.get('is_active') == 'on'
            
            if integration_id:
                # Cập nhật tích hợp hiện có
                integration = get_object_or_404(APIIntegration, id=integration_id)
                integration.name = name
                integration.api_type = api_type
                integration.api_url = api_url
                integration.api_key = api_key
                integration.api_version = api_version
                integration.timeout = timeout
                integration.is_active = is_active
                integration.save()
            else:
                # Tạo tích hợp mới
                integration = APIIntegration.objects.create(
                    name=name,
                    api_type=api_type,
                    api_url=api_url,
                    api_key=api_key,
                    api_version=api_version,
                    timeout=timeout,
                    is_active=is_active
                )
            
            # Nếu tích hợp này được đánh dấu là active, hãy tắt các tích hợp khác
            if is_active:
                APIIntegration.objects.exclude(id=integration.id).update(is_active=False)
            
            return redirect('dashboard:api_integration')
        
        elif action == 'delete':
            integration_id = request.POST.get('integration_id')
            if integration_id:
                integration = get_object_or_404(APIIntegration, id=integration_id)
                integration.delete()
            
            return redirect('dashboard:api_integration')
    
    # Lấy tất cả các tích hợp API
    integrations = APIIntegration.objects.all()
    
    context = {
        'integrations': integrations
    }
    
    return render(request, 'dashboard/chatbot/api_integration.html', context)

@staff_member_required
def chat_logs(request):
    """Xem log chat"""
    logs = ChatLog.objects.all().order_by('-created_at')
    
    # Lọc theo trạng thái nếu có
    status_filter = request.GET.get('status')
    if status_filter:
        logs = logs.filter(status=status_filter)
    
    # Lọc theo thời gian nếu có
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        logs = logs.filter(created_at__gte=date_from)
    if date_to:
        logs = logs.filter(created_at__lte=date_to)
    
    # Phân trang
    paginator = Paginator(logs, 50)
    page = request.GET.get('page')
    logs = paginator.get_page(page)
    
    context = {
        'logs': logs,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to
    }
    return render(request, 'dashboard/chatbot/logs.html', context)

# API endpoints for chatbot interaction
@csrf_exempt
def chat_api(request):
    """API nhận và xử lý tin nhắn chat từ widget"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        message = data.get('message')
        
        if not session_id or not message:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Lấy cấu hình chatbot đang kích hoạt
        config = ChatbotConfig.objects.filter(is_active=True).first()
        if not config:
            return JsonResponse({'error': 'No active chatbot configuration found'}, status=500)
        
        # Lấy tích hợp API đang kích hoạt
        api_integration = APIIntegration.objects.filter(is_active=True).first()
        if not api_integration:
            return JsonResponse({'error': 'No active API integration found'}, status=500)
        
        # Kiểm tra từ khóa bị cấm
        for keyword in config.forbidden_keywords.all():
            if keyword.keyword.lower() in message.lower():
                # Lưu log chat bị lọc
                chat_log = ChatLog.objects.create(
                    session_id=session_id,
                    user=request.user if request.user.is_authenticated else None,
                    user_query=message,
                    full_prompt="",
                    response=config.rejection_message,
                    status='filtered',
                    filter_reason=f"Từ khóa bị cấm: {keyword.keyword}"
                )
                
                return JsonResponse({
                    'response': config.rejection_message
                })
        
        # Tạo prompt
        allowed_categories = config.allowed_categories.all()
        categories_text = ", ".join([f"{ac.category.name}" for ac in allowed_categories])
        
        # Lấy một số sản phẩm mẫu để đưa vào prompt
        products = []
        for ac in allowed_categories:
            category_products = Product.objects.filter(category=ac.category, is_active=True)[:5]
            for product in category_products:
                products.append({
                    'name': product.name,
                    'price': str(product.price),
                    'description': product.description[:200] + '...' if len(product.description) > 200 else product.description,
                    'category': ac.category.name
                })
        
        # Thêm dữ liệu sản phẩm vào prompt
        products_text = ""
        for product in products[:15]:  # Giới hạn số lượng sản phẩm để tránh prompt quá dài
            products_text += f"- {product['name']} - {product['price']} - {product['category']}\n"
        
        full_prompt = f"""
{config.base_prompt}

Danh mục sản phẩm được phép tư vấn: {categories_text}

Thông tin sản phẩm mẫu:
{products_text}

Câu hỏi của người dùng: {message}

Lưu ý:
- Chỉ trả lời về sản phẩm trong các danh mục được liệt kê.
- Nếu câu hỏi nằm ngoài phạm vi, hãy trả lời: "{config.rejection_message}"
- Giữ câu trả lời ngắn gọn, dễ hiểu và thân thiện.
- Nếu người dùng hỏi về "ứng dụng giải trí", hãy hỏi họ muốn giải trí bằng hình thức nào (Nghe nhạc | Xem phim | Đọc sách).
- Nếu phát hiện cảm xúc tiêu cực từ người dùng (bất mãn, khó chịu), hãy đề nghị chuyển sang hỗ trợ trực tiếp.
"""
        
        # Gọi API
        start_time = time.time()
        try:
            response_data = call_ai_api(api_integration, full_prompt)
            end_time = time.time()
            
            api_response_time = round((end_time - start_time) * 1000)  # ms
            response_text = response_data['response']
            
            # Lưu log chat thành công
            chat_log = ChatLog.objects.create(
                session_id=session_id,
                user=request.user if request.user.is_authenticated else None,
                user_query=message,
                full_prompt=full_prompt,
                response=response_text,
                status='success',
                api_response_time=api_response_time
            )
            
            return JsonResponse({
                'response': response_text
            })
            
        except Exception as e:
            # Lưu log chat lỗi
            chat_log = ChatLog.objects.create(
                session_id=session_id,
                user=request.user if request.user.is_authenticated else None,
                user_query=message,
                full_prompt=full_prompt,
                response=str(e),
                status='error',
                filter_reason=f"Lỗi API: {str(e)}"
            )
            
            return JsonResponse({
                'response': "Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau."
            })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# API nhận phản hồi từ người dùng
@csrf_exempt
def chat_feedback(request):
    """API nhận đánh giá về cuộc trò chuyện"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        rating = data.get('rating')
        
        if not session_id or not rating:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Cập nhật đánh giá cho các log chat trong phiên
        ChatLog.objects.filter(session_id=session_id).update(satisfaction_rating=rating)
        
        return JsonResponse({
            'success': True,
            'message': 'Feedback received'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def call_ai_api(api_integration, prompt):
    """
    Hàm chung để gọi các API AI khác nhau dựa trên loại tích hợp
    """
    if api_integration.api_type == 'gemini':
        return send_gemini_request(api_integration, prompt)
    elif api_integration.api_type == 'openai':
        return send_openai_request(api_integration, prompt)
    elif api_integration.api_type == 'anthropic':
        return send_anthropic_request(api_integration, prompt)
    else:
        raise ValueError(f"Loại API không được hỗ trợ: {api_integration.api_type}")

def send_gemini_request(api_integration, prompt):
    """Gửi request đến Gemini API"""
    url = api_integration.api_url
    if 'generativelanguage.googleapis.com' not in url:
        url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    # Thêm API key vào URL nếu không có trong headers
    if '?' not in url:
        url += f'?key={api_integration.api_key}'
    
    data = {
        'contents': [
            {
                'parts': [
                    {'text': prompt}
                ]
            }
        ],
        'generationConfig': {
            'temperature': 0.4,
            'topK': 32,
            'topP': 0.95,
            'maxOutputTokens': 1024,
        }
    }
    
    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=api_integration.timeout
    )
    
    if response.status_code != 200:
        raise Exception(f"Lỗi API: {response.status_code} - {response.text}")
    
    response_data = response.json()
    
    try:
        text_content = response_data['candidates'][0]['content']['parts'][0]['text']
        return {'response': text_content}
    except (KeyError, IndexError) as e:
        raise Exception(f"Lỗi phân tích phản hồi: {str(e)}")

def send_openai_request(api_integration, prompt):
    """Gửi request đến OpenAI API"""
    url = api_integration.api_url
    if not url or 'api.openai.com' not in url:
        url = 'https://api.openai.com/v1/chat/completions'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_integration.api_key}'
    }
    
    model = api_integration.api_version
    if not model:
        model = 'gpt-3.5-turbo'
    
    data = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': 'Bạn là chatbot tư vấn sản phẩm. Bạn chỉ trả lời dựa trên thông tin sản phẩm được cung cấp.'},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.7,
        'max_tokens': 1024
    }
    
    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=api_integration.timeout
    )
    
    if response.status_code != 200:
        raise Exception(f"Lỗi API: {response.status_code} - {response.text}")
    
    response_data = response.json()
    
    try:
        text_content = response_data['choices'][0]['message']['content']
        return {'response': text_content}
    except (KeyError, IndexError) as e:
        raise Exception(f"Lỗi phân tích phản hồi: {str(e)}")

def send_anthropic_request(api_integration, prompt):
    """Gửi request đến Anthropic Claude API"""
    url = api_integration.api_url
    if not url or 'api.anthropic.com' not in url:
        url = 'https://api.anthropic.com/v1/messages'
    
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_integration.api_key,
        'anthropic-version': '2023-06-01'
    }
    
    model = api_integration.api_version
    if not model:
        model = 'claude-3-opus-20240229'
    
    data = {
        'model': model,
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'max_tokens': 1024
    }
    
    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=api_integration.timeout
    )
    
    if response.status_code != 200:
        raise Exception(f"Lỗi API Anthropic: {response.status_code} - {response.text}")
    
    response_data = response.json()
    
    try:
        text_content = response_data['content'][0]['text']
        return {'response': text_content}
    except (KeyError, IndexError) as e:
        raise Exception(f"Lỗi phân tích phản hồi Anthropic: {str(e)}")

@login_required
@user_passes_test(is_admin)
@require_POST
def save_chatbot_settings(request):
    """Lưu cấu hình Chatbot và API"""
    try:
        data = json.loads(request.body)
        
        # Lấy dữ liệu từ request
        api_type = data.get('api_type', 'gemini')
        api_key = data.get('api_key')
        model = data.get('model', 'gemini-1.5-pro')  # Mặc định là 1.5 pro thay vì 2.0 pro
        temperature = float(data.get('temperature', 0.7))
        chatbot_name = data.get('chatbot_name')
        base_prompt = data.get('base_prompt')
        endpoint = data.get('endpoint', '')
        
        print(f"Saving APIConfig: {api_type}, key={api_key[:5]}..., model={model}")
        
        # Cập nhật hoặc tạo mới cấu hình API
        api_config, created = APIConfig.objects.update_or_create(
            api_type=api_type,
            defaults={
                'api_key': api_key,
                'model': model,
                'temperature': temperature,
                'endpoint': endpoint,
                'is_active': True
            }
        )
        
        # Vô hiệu hóa các cấu hình API khác
        APIConfig.objects.exclude(id=api_config.id).update(is_active=False)
        
        # Kiểm tra các trường có trong model trước khi cập nhật
        chatbot_config_fields = {
            'chatbot_name': chatbot_name,
            'base_prompt': base_prompt,
            'is_active': True
        }
        
        # Cập nhật hoặc tạo mới cấu hình Chatbot
        chatbot_config, created = ChatbotConfig.objects.update_or_create(
            name=chatbot_name,
            defaults=chatbot_config_fields
        )
        
        # Vô hiệu hóa các cấu hình Chatbot khác
        ChatbotConfig.objects.exclude(id=chatbot_config.id).update(is_active=False)
        
        print(f"Đã lưu cấu hình Chatbot thành công: {chatbot_config.name}, API: {api_config.api_type}")
        
        return JsonResponse({
            'success': True,
            'message': 'Đã lưu cấu hình Chatbot thành công'
        })
        
    except Exception as e:
        print(f"Lỗi khi lưu cấu hình Chatbot: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })

@csrf_exempt
def get_chatbot_config(request):
    """Trả về cấu hình chatbot cho frontend"""
    try:
        # Lấy cấu hình chatbot và API đang hoạt động
        config = ChatbotConfig.objects.filter(is_active=True).first()
        api_config = APIConfig.objects.filter(is_active=True).first()
        
        if not config or not api_config:
            return JsonResponse({
                'success': False,
                'message': 'Chưa cấu hình chatbot hoặc API'
            })
        
        # Trả về thông tin cấu hình
        return JsonResponse({
            'success': True,
            'config': {
                'chatbot_name': config.chatbot_name,
                'base_prompt': config.base_prompt,
                'api_type': api_config.api_type,
                'api_key': api_config.api_key,
                'model': api_config.model,
                'temperature': api_config.temperature,
                'endpoint': api_config.endpoint
            }
        })
    except Exception as e:
        print(f"Lỗi khi lấy cấu hình chatbot: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }) 