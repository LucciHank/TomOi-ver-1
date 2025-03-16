from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import requests

from dashboard.models.api import APIConfig
from dashboard.models.chatbot import ChatbotConfig

def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def api_settings(request):
    """Trang cài đặt API"""
    try:
        api_configs = APIConfig.objects.all()
        active_api_config = APIConfig.objects.filter(is_active=True, api_type='gemini').first()
        chatbot_configs = ChatbotConfig.objects.all()
        active_chatbot_config = ChatbotConfig.objects.filter(is_active=True).first()
    except Exception as e:
        print(f"Lỗi khi truy vấn API config: {str(e)}")
        api_configs = []
        active_api_config = None
        chatbot_configs = []
        active_chatbot_config = None
    
    context = {
        'api_configs': api_configs,
        'active_api_config': active_api_config,
        'chatbot_configs': chatbot_configs,
        'active_chatbot_config': active_chatbot_config,
        'active_tab': 'api'
    }
    
    return render(request, 'dashboard/settings/api.html', context)

@login_required
@user_passes_test(is_admin)
@require_POST
def save_api_config(request):
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
        if not api_key:
            return JsonResponse({
                'success': False,
                'message': 'API key không được để trống'
            })
        
        # Kiểm tra kết nối API
        test_result = test_api_connection(api_type, api_key, model, endpoint)
        if not test_result['success']:
            return JsonResponse(test_result)
        
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
@csrf_exempt
@require_POST
def test_api(request):
    """Kiểm tra kết nối API"""
    try:
        data = json.loads(request.body)
        api_type = data.get('api_type')
        api_key = data.get('api_key')
        model = data.get('model')
        endpoint = data.get('endpoint', '')
        
        result = test_api_connection(api_type, api_key, model, endpoint)
        return JsonResponse(result)
        
    except Exception as e:
        print(f"Lỗi khi kiểm tra API: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })

def test_api_connection(api_type, api_key, model, endpoint=''):
    """Kiểm tra kết nối đến API"""
    try:
        if not api_key:
            return {
                'success': False,
                'message': 'API key không được để trống'
            }
        
        if api_type == 'gemini':
            # Kiểm tra kết nối Gemini API
            api_url = endpoint or f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            data = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": "Hello, are you working?"}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 100
                }
            }
            
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Kết nối API thành công'
                }
            else:
                return {
                    'success': False,
                    'message': f'Lỗi API: {response.status_code} - {response.text}'
                }
        
        # Thêm các loại API khác nếu cần
        
        return {
            'success': False,
            'message': f'Loại API không được hỗ trợ: {api_type}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Lỗi kết nối: {str(e)}'
        } 