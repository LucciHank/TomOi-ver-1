from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def dashboard_login(request):
    # Nếu người dùng đã đăng nhập, chuyển thẳng đến dashboard
    if request.user.is_authenticated:
        return redirect('dashboard:index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            # Lưu session
            request.session.save()
            # Debug info
            print(f"User authenticated: {user.username}")
            print(f"Session key: {request.session.session_key}")
            # Chuyển hướng đến trang dashboard chính
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')
            
    # Debug info
    print(f"CSRF Cookie: {request.COOKIES.get('csrftoken')}")
    return render(request, 'dashboard/login.html')

@login_required
def dashboard_logout(request):
    logout(request)
    # Xóa session
    request.session.flush()
    return redirect('dashboard:login') 