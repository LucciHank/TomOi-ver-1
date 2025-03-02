from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.utils import timezone
import json
import time
import uuid
import requests
from .models.chatbot import (
    ChatbotConfig, APIIntegration, ChatLog, 
    AllowedCategory, ForbiddenKeyword
)
from store.models import Product, Category

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
            if keyword.strip():
                ForbiddenKeyword.objects.create(
                    config=config,
                    keyword=keyword.strip()
                )
        
        return redirect('dashboard:chatbot_dashboard')
    
    # Lấy tất cả danh mục
    all_categories = Category.objects.all()
    
    context = {
        'config': config,
        'all_categories': all_categories,
    }
    
    return render(request, 'dashboard/chatbot/config.html', context)

@staff_member_required
def api_integration(request, api_id=None):
    """Quản lý tích hợp API"""
    api = None
    if api_id:
        api = get_object_or_404(APIIntegration, id=api_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        api_type = request.POST.get('api_type')
        api_url = request.POST.get('api_url')
        api_key = request.POST.get('api_key')
        api_version = request.POST.get('api_version')
        timeout = int(request.POST.get('timeout', 30))
        is_active = request.POST.get('is_active') == 'on'
        
        if api:
            # Cập nhật API hiện có
            api.name = name
            api.api_type = api_type
            api.api_url = api_url
            if api_key:  # Chỉ cập nhật nếu có key mới
                api.api_key = api_key
            api.api_version = api_version
            api.timeout = timeout
            api.is_active = is_active
            api.save()
        else:
            # Tạo API mới
            api = APIIntegration.objects.create(
                name=name,
                api_type=api_type,
                api_url=api_url,
                api_key=api_key,
                api_version=api_version,
                timeout=timeout,
                is_active=is_active
            )
        
        return redirect('dashboard:api_integration')
    
    # Lấy tất cả tích hợp API
    all_apis = APIIntegration.objects.all()
    
    context = {
        'api': api,
        'all_apis': all_apis,
    }
    
    return render(request, 'dashboard/chatbot/api_integration.html', context)

@staff_member_required
def chat_logs(request):
    """Xem lịch sử chat"""
    logs_query = ChatLog.objects.all().order_by('-created_at')
    
    # Lọc theo status
    status = request.GET.get('status')
    if status:
        logs_query = logs_query.filter(status=status)
    
    # Lọc theo thời gian
    date_from = request.GET.get('date_from')
    if date_from:
        logs_query = logs_query.filter(created_at__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        logs_query = logs_query.filter(created_at__lte=date_to)
    
    # Lọc theo nội dung
    search = request.GET.get('search')
    if search:
        logs_query = logs_query.filter(
            Q(user_query__icontains=search) | 
            Q(response__icontains=search)
        )
    
    # Phân trang
    paginator = Paginator(logs_query, 20)
    page = request.GET.get('page', 1)
    logs = paginator.get_page(page)
    
    context = {
        'logs': logs,
    }
    
    return render(request, 'dashboard/chatbot/logs.html', context)

@csrf_exempt
def chat_api(request):
    """API endpoint để xử lý chat từ widget"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Phương thức không được hỗ trợ'}, status=405)
    
    try:
        data = json.loads(request.body)
        message = data.get('message')
        session_id = data.get('session_id')
        
        if not message:
            return JsonResponse({'error': 'Thiếu tin nhắn'}, status=400)
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Lấy cấu hình chatbot đang kích hoạt
        config = ChatbotConfig.objects.filter(is_active=True).first()
        if not config:
            return JsonResponse({'error': 'Chưa có cấu hình chatbot nào được kích hoạt'}, status=500)
        
        # Lấy tích hợp API đang kích hoạt
        api_integration = APIIntegration.objects.filter(is_active=True).first()
        if not api_integration:
            return JsonResponse({'error': 'Chưa có tích hợp API nào được kích hoạt'}, status=500)
        
        # Kiểm tra từ khóa cấm
        for keyword in config.forbidden_keywords.all():
            if keyword.keyword.lower() in message.lower():
                # Lưu log chat bị lọc
                ChatLog.objects.create(
                    session_id=session_id,
                    user=request.user if request.user.is_authenticated else None,
                    user_query=message,
                    full_prompt='',
                    response=config.rejection_message,
                    status='filtered',
                    filter_reason=f'Từ khóa cấm: {keyword.keyword}'
                )
                
                return JsonResponse({
                    'response': config.rejection_message,
                    'session_id': session_id
                })
        
        # Tạo prompt đầy đủ
        allowed_categories = config.allowed_categories.all()
        categories_text = ", ".join([cat.category.name for cat in allowed_categories])
        
        full_prompt = f"""
{config.base_prompt}

Danh mục sản phẩm được phép tư vấn: {categories_text}

Câu hỏi người dùng: {message}
"""
        
        # Gửi request đến API tương ứng
        start_time = time.time()
        
        try:
            if api_integration.api_type == 'gemini':
                api_response = send_gemini_request(api_integration, full_prompt)
            elif api_integration.api_type == 'openai':
                api_response = send_openai_request(api_integration, full_prompt)
            elif api_integration.api_type == 'anthropic':
                api_response = send_anthropic_request(api_integration, full_prompt)
            else:
                raise Exception(f"Loại API không được hỗ trợ: {api_integration.api_type}")
            
            response_text = api_response.get('response', '')
            api_response_time = (time.time() - start_time) * 1000  # ms
            
            # Lưu log chat thành công
            ChatLog.objects.create(
                session_id=session_id,
                user=request.user if request.user.is_authenticated else None,
                user_query=message,
                full_prompt=full_prompt,
                response=response_text,
                status='success',
                api_response_time=api_response_time
            )
            
            return JsonResponse({
                'response': response_text,
                'session_id': session_id
            })
            
        except Exception as e:
            # Lưu log chat lỗi
            ChatLog.objects.create(
                session_id=session_id,
                user=request.user if request.user.is_authenticated else None,
                user_query=message,
                full_prompt=full_prompt,
                response=str(e),
                status='error',
                filter_reason=f'Lỗi API: {str(e)}'
            )
            
            return JsonResponse({
                'error': 'Có lỗi xảy ra khi xử lý tin nhắn',
                'details': str(e),
                'session_id': session_id
            }, status=500)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Có lỗi xảy ra',
            'details': str(e)
        }, status=500)

@csrf_exempt
def chat_feedback(request):
    """API nhận feedback của người dùng về trò chuyện"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Phương thức không được hỗ trợ'}, status=405)
    
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        rating = data.get('rating')
        
        if not session_id or not rating:
            return JsonResponse({'error': 'Thiếu thông tin bắt buộc'}, status=400)
        
        # Cập nhật đánh giá cho phiên chat
        ChatLog.objects.filter(session_id=session_id).update(satisfaction_rating=rating)
        
        return JsonResponse({
            'success': True,
            'message': 'Đã ghi nhận đánh giá của bạn'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': 'Có lỗi xảy ra',
            'details': str(e)
        }, status=500)


def send_gemini_request(api_integration, prompt):
    """Gửi request đến Gemini API"""
    url = api_integration.api_url
    if not url or 'generativelanguage.googleapis.com' not in url:
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_integration.api_key}'
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        'contents': [
            {
                'parts': [
                    {
                        'text': prompt
                    }
                ]
            }
        ],
        'generationConfig': {
            'temperature': 0.7,
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