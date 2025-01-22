from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

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