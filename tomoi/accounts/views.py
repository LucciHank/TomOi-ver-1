from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm
from .models import PurchasedAccount
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'accounts/index.html')

# Đăng ký
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/store/')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

# Quản lý tài khoản đã mua
@login_required  # Đảm bảo rằng người dùng đã đăng nhập
def account_management(request):
    # Kiểm tra xem người dùng có đăng nhập không
    if request.user.is_authenticated:
        accounts = PurchasedAccount.objects.filter(user=request.user)
    else:
        accounts = []  # Hoặc bạn có thể redirect đến trang đăng nhập

    return render(request, 'account_management.html', {'accounts': accounts})