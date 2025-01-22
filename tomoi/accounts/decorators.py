from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'admin':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('store:home')
    return wrapper

def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type in ['admin', 'staff']:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('store:home')
    return wrapper 