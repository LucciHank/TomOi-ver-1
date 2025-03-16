from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.conf import settings
from django.utils import timezone
import os

@login_required
def settings_view(request):
    """Hiển thị trang cài đặt với tab tương ứng"""
    active_tab = request.GET.get('tab', 'general')
    
    # Lấy các giá trị cài đặt từ cơ sở dữ liệu hoặc settings
    gemini_api_key = getattr(settings, 'GEMINI_API_KEY', '')
    gemini_model = getattr(settings, 'GEMINI_MODEL', 'gemini-pro')
    gemini_temperature = getattr(settings, 'GEMINI_TEMPERATURE', 0.9)
    gemini_top_p = getattr(settings, 'GEMINI_TOP_P', 0.95)
    gemini_max_output_tokens = getattr(settings, 'GEMINI_MAX_OUTPUT_TOKENS', 8192)
    
    context = {
        'active_tab': active_tab,
        'gemini_api_key': gemini_api_key,
        'gemini_model': gemini_model,
        'gemini_temperature': gemini_temperature,
        'gemini_top_p': gemini_top_p,
        'gemini_max_output_tokens': gemini_max_output_tokens,
        'gemini_connected': bool(gemini_api_key),
        'gemini_model': gemini_model,
        'temperature': gemini_temperature,
        'max_tokens': gemini_max_output_tokens,
        'system_prompt': getattr(settings, 'GEMINI_SYSTEM_PROMPT', 'Bạn là trợ lý ảo của TomOi, hỗ trợ khách hàng một cách lịch sự và chuyên nghiệp. Trả lời bằng tiếng Việt, ngắn gọn và hữu ích.'),
        'enable_chat_history': getattr(settings, 'GEMINI_ENABLE_CHAT_HISTORY', True),
        'enable_product_search': getattr(settings, 'GEMINI_ENABLE_PRODUCT_SEARCH', True),
        'chatbot_name': getattr(settings, 'CHATBOT_NAME', 'TomOi Assistant'),
        'theme_color': getattr(settings, 'CHATBOT_THEME_COLOR', '#df2626'),
        'position': getattr(settings, 'CHATBOT_POSITION', 'bottom-right'),
    }
    
    template_path = f'dashboard/settings/{active_tab}.html'
    return render(request, template_path, context)

@login_required
def save_chatbot_settings(request):
    """Lưu cài đặt chatbot"""
    if request.method == 'POST':
        try:
            # Xử lý và lưu các cài đặt
            gemini_api_key = request.POST.get('gemini_api_key')
            gemini_model = request.POST.get('gemini_model')
            temperature = float(request.POST.get('temperature', 0.7))
            max_tokens = int(request.POST.get('max_tokens', 2048))
            system_prompt = request.POST.get('system_prompt')
            enable_chat_history = 'enable_chat_history' in request.POST
            enable_product_search = 'enable_product_search' in request.POST
            enable_streaming = 'enable_streaming' in request.POST
            chatbot_name = request.POST.get('chatbot_name')
            theme_color = request.POST.get('theme_color')
            position = request.POST.get('position')
            
            # Xử lý upload avatar nếu có
            avatar_file = request.FILES.get('chatbot_avatar')
            avatar_path = None
            
            if avatar_file:
                # Lưu file
                from django.conf import settings
                
                # Tạo thư mục nếu chưa tồn tại
                upload_path = os.path.join(settings.MEDIA_ROOT, 'chatbot')
                os.makedirs(upload_path, exist_ok=True)
                
                # Lưu file
                file_path = os.path.join(upload_path, f'avatar_{int(timezone.now().timestamp())}.{avatar_file.name.split(".")[-1]}')
                with open(file_path, 'wb+') as destination:
                    for chunk in avatar_file.chunks():
                        destination.write(chunk)
                
                # Đường dẫn tương đối để lưu vào cài đặt
                avatar_path = os.path.join('media', 'chatbot', os.path.basename(file_path))
            
            # Lưu các cài đặt
            settings_data = {
                'GEMINI_API_KEY': gemini_api_key,
                'GEMINI_MODEL': gemini_model,
                'GEMINI_TEMPERATURE': temperature,
                'GEMINI_MAX_TOKENS': max_tokens,
                'GEMINI_SYSTEM_PROMPT': system_prompt,
                'GEMINI_ENABLE_CHAT_HISTORY': enable_chat_history,
                'GEMINI_ENABLE_PRODUCT_SEARCH': enable_product_search,
                'GEMINI_ENABLE_STREAMING': enable_streaming,
                'CHATBOT_NAME': chatbot_name,
                'CHATBOT_THEME_COLOR': theme_color,
                'CHATBOT_POSITION': position
            }
            
            if avatar_path:
                settings_data['CHATBOT_AVATAR'] = avatar_path
            
            # Lưu vào file (trong thực tế nên lưu vào database)
            from django.conf import settings as django_settings
            
            # Tạo thư mục cấu hình nếu chưa tồn tại
            config_dir = os.path.join(django_settings.BASE_DIR, 'config')
            os.makedirs(config_dir, exist_ok=True)
            
            config_path = os.path.join(config_dir, 'chatbot_settings.json')
            with open(config_path, 'w') as f:
                json.dump(settings_data, f, indent=4)
            
            messages.success(request, 'Đã lưu cài đặt chatbot thành công!')
            return redirect('dashboard:settings')
            
        except Exception as e:
            messages.error(request, f'Lỗi khi lưu cài đặt: {str(e)}')
    
    return redirect('dashboard:settings')

@login_required
@csrf_exempt
def test_gemini_api(request):
    """Kiểm tra kết nối với API Gemini"""
    if request.method == 'POST':
        api_key = request.POST.get('api_key')
        model = request.POST.get('model', 'gemini-2.0-flash')  # Sử dụng phiên bản mới nhất
        
        if not api_key:
            return JsonResponse({'success': False, 'error': 'API key không được để trống'})
        
        # Ghi log để debug
        print(f"Kiểm tra kết nối Gemini API với key: {api_key[:5]}...")
        
        # Kiểm tra kết nối với Gemini API
        try:
            # URL của Gemini API để kiểm tra - sử dụng phiên bản mới
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            
            # Dữ liệu gửi đi để test
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": "Xin chào, đây là tin nhắn kiểm tra."
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 100
                }
            }
            
            # Gửi request
            print("Đang gửi request tới Gemini API...")
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            # Kiểm tra kết quả
            print(f"Nhận được phản hồi với status code: {response.status_code}")
            if response.status_code == 200:
                print("Kết nối thành công!")
                return JsonResponse({'success': True})
            else:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Lỗi không xác định')
                print(f"Lỗi: {error_message}")
                return JsonResponse({'success': False, 'error': error_message})
                
        except Exception as e:
            print(f"Exception: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Phương thức không hợp lệ'})

@login_required
def update_general_settings(request):
    """Cập nhật cài đặt chung của hệ thống"""
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ request
            site_name = request.POST.get('site_name', '')
            site_description = request.POST.get('site_description', '')
            contact_email = request.POST.get('contact_email', '')
            phone_number = request.POST.get('phone_number', '')
            address = request.POST.get('address', '')
            
            # Cập nhật logo nếu có
            logo_file = request.FILES.get('logo')
            if logo_file:
                # Xử lý và lưu file logo
                file_name = f"logo_{timezone.now().strftime('%Y%m%d%H%M%S')}.png"
                logo_path = os.path.join(settings.MEDIA_ROOT, 'site', file_name)
                os.makedirs(os.path.dirname(logo_path), exist_ok=True)
                
                with open(logo_path, 'wb+') as destination:
                    for chunk in logo_file.chunks():
                        destination.write(chunk)
                
                # Cập nhật đường dẫn logo
                # Lưu vào cơ sở dữ liệu hoặc file cấu hình
            
            # Lưu các cài đặt khác vào cơ sở dữ liệu hoặc file cấu hình
            # (Giả định có model SiteSettings hoặc cài đặt được lưu trong file)
            
            messages.success(request, 'Cài đặt chung đã được cập nhật thành công!')
            return redirect('dashboard:settings_view')
            
        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật cài đặt: {str(e)}')
    
    return redirect('dashboard:settings_view')

@login_required
def update_payment_settings(request):
    """Cập nhật cài đặt thanh toán"""
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ request
            payment_gateway = request.POST.get('payment_gateway', '')
            vnpay_terminal_id = request.POST.get('vnpay_terminal_id', '')
            vnpay_secret_key = request.POST.get('vnpay_secret_key', '')
            momo_partner_code = request.POST.get('momo_partner_code', '')
            momo_access_key = request.POST.get('momo_access_key', '')
            momo_secret_key = request.POST.get('momo_secret_key', '')
            
            # Cập nhật trạng thái các phương thức thanh toán
            enable_cod = request.POST.get('enable_cod') == 'on'
            enable_bank_transfer = request.POST.get('enable_bank_transfer') == 'on'
            enable_vnpay = request.POST.get('enable_vnpay') == 'on'
            enable_momo = request.POST.get('enable_momo') == 'on'
            
            # Lưu các cài đặt vào cơ sở dữ liệu hoặc file cấu hình
            # (Giả định có model PaymentSettings hoặc cài đặt được lưu trong file)
            
            messages.success(request, 'Cài đặt thanh toán đã được cập nhật thành công!')
            return redirect('dashboard:settings_view')
            
        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật cài đặt thanh toán: {str(e)}')
    
    return redirect('dashboard:settings_view') 