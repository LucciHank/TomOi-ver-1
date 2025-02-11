from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Các URL chỉ dành cho admin
            admin_urls = ['/admin/', '/dashboard/admin/']
            # Các URL chỉ dành cho staff
            staff_urls = ['/dashboard/staff/']

            path = request.path_info
            user_type = request.user.user_type

            if any(url in path for url in admin_urls) and user_type != 'admin':
                messages.error(request, 'Bạn không có quyền truy cập trang này.')
                return redirect('store:home')

            if any(url in path for url in staff_urls) and user_type not in ['admin', 'staff']:
                messages.error(request, 'Bạn không có quyền truy cập trang này.')
                return redirect('store:home')

        response = self.get_response(request)
        return response

class EmailVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            # Danh sách các URL được phép truy cập khi chưa xác minh
            allowed_urls = [
                reverse('accounts:register_verify'),
                reverse('accounts:verify_email', args=['dummy']).rsplit('dummy', 1)[0],
                reverse('accounts:resend_verification_email'),
                reverse('accounts:logout'),
                '/static/',
                '/media/',
                '/accounts/login/',  # Cho phép truy cập URL đăng nhập
            ]
            
            # Kiểm tra xem URL hiện tại có được phép không
            current_path = request.path
            if not any(current_path.startswith(url) for url in allowed_urls):
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Vui lòng xác thực email để tiếp tục',
                        'redirect': reverse('accounts:register_verify')
                    })
                return redirect('accounts:register_verify')

        return self.get_response(request) 