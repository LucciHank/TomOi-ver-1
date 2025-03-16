from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.conf import settings
from social_django.utils import psa
from social_django.models import UserSocialAuth
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.crypto import get_random_string
from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomPasswordResetForm, CustomSetPasswordForm
from django.conf import settings
from accounts.models import CustomUser, LoginHistory, Deposit, TCoinHistory, DailyCheckin, CardTransaction, TCoin
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.utils.timezone import now, timedelta, datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import random
import json
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from .decorators import admin_required, staff_required
from django.views.decorators.http import require_POST, require_http_methods
from payment.models import Transaction  # Import Transaction từ payment.models
from store.models import Wishlist, Category, Order, OrderItem, CartItem  # Import Wishlist và Category từ store.models, thêm Order và OrderItem, CartItem
import pyotp
import qrcode
import base64
from io import BytesIO
from django.contrib.auth.hashers import check_password, make_password
import time
from django.utils import timezone
import hashlib
from .utils import mask_email, get_client_info, get_location_from_ip, create_vnpay_url, process_card_payment
from django.core.cache import cache
from django.utils import translation
from django.db.models import Q
import requests
import user_agents
import logging
import uuid
from django.db import transaction
from collections import OrderedDict
from urllib.parse import urlencode, quote_plus
import hmac
import urllib.parse
from accounts.vnpay import VNPay
from decimal import Decimal
from payment.vnpay import VnPay  # Thêm import VnPay
from payment.models import Transaction, TransactionItem
from django.utils.html import strip_tags
from payment.utils import send_payment_confirmation_email
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from dashboard.models.chatbot import ChatbotConfig
from dashboard.models.api import APIConfig

logger = logging.getLogger(__name__)

@csrf_exempt
def auth(request):
    action = request.POST.get('action')  # 'login', 'register', 'forgot_password', or 'reset_password'
    response = {}

    if action == 'login':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            response['success'] = True
            response['message'] = 'Đăng nhập thành công!'
        else:
            response['success'] = False
            response['message'] = 'Tên đăng nhập hoặc mật khẩu không chính xác.'

    elif action == 'register':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            response['success'] = False
            response['message'] = 'Tên đăng nhập đã tồn tại.'
        elif User.objects.filter(email=email).exists():
            response['success'] = False
            response['message'] = 'Email đã được sử dụng.'
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            response['success'] = True
            response['message'] = 'Tạo tài khoản thành công.'

    elif action == 'forgot_password':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = get_random_string(32)
            # Bạn cần lưu token trong một model hoặc cache để xác thực trong phần reset_password
            send_mail(
                'Quên mật khẩu',
                f'Dùng token này để đặt lại mật khẩu: {token}',
                'tomoivn2024@gmail.com',
                [email],
            )
            response['success'] = True
            response['message'] = 'Đã gửi token đặt lại mật khẩu qua email.'
        except User.DoesNotExist:
            response['success'] = False
            response['message'] = 'Không tìm thấy email.'

    elif action == 'reset_password':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            response['success'] = True
            response['message'] = 'Đặt lại mật khẩu thành công.'
        except User.DoesNotExist:
            response['success'] = False
            response['message'] = 'Tên người dùng không hợp lệ.'

    else:
        response['success'] = False
        response['message'] = 'Yêu cầu không hợp lệ.'

    return JsonResponse(response)

# Register view
@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')

            # Kiểm tra email và username tồn tại
            existing_user = CustomUser.objects.filter(email=email).first()
            if existing_user:
                # Chỉ báo email tồn tại nếu tài khoản đã được kích hoạt
                if existing_user.is_active:
                    return JsonResponse({
                        'success': False,
                        'error': 'Email đã tồn tại!',
                        'action': 'login'
                    })
                else:
                    # Nếu tài khoản chưa kích hoạt, xóa và tạo mới
                    existing_user.delete()
            
            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Tên đăng nhập đã tồn tại! Vui lòng chọn tên khác.'
                })

            # Tạo user mới (chưa active)
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=False
            )

            # Tạo token xác thực và thời gian hết hạn
            token = get_random_string(64)
            user.verification_token = token
            user.verification_token_expires = timezone.now() + timedelta(hours=24)
            user.save()

            # Gửi email xác thực
            send_verification_email(request, user)

            # Đăng nhập user
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            return JsonResponse({
                'success': True,
                'message': 'Đăng ký thành công! Vui lòng kiểm tra email để xác thực tài khoản.',
                'redirect': reverse('accounts:register_verify')
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return render(request, 'accounts/register.html')

def send_verification_email(request, user):
    verification_url = request.build_absolute_uri(
        reverse('accounts:verify_email', args=[user.verification_token])
    )
    
    html_message = render_to_string('accounts/email/verify_email.html', {
        'user': user,
        'verification_url': verification_url
    })

    send_mail(
        'Xác thực tài khoản TomOi.vn',
        '',
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=html_message,
        fail_silently=False
    )

@csrf_exempt
def resend_verification_email(request):
    if request.method == 'POST':
        try:
            user = request.user
            if not user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'message': 'Vui lòng đăng nhập'
                })

            # Tạo token mới
            user.verification_token = get_random_string(64)
            user.verification_token_expires = timezone.now() + timedelta(hours=24)
            user.save()

            # Gửi lại email
            send_verification_email(request, user)

            return JsonResponse({
                'success': True,
                'message': 'Đã gửi lại email xác thực'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })

    return JsonResponse({
        'success': False,
        'message': 'Phương thức không hợp lệ'
    })

def verify_email(request, token):
    try:
        user = CustomUser.objects.get(verification_token=token)
        
        # Kiểm tra token hết hạn
        if timezone.now() > user.verification_token_expires:
            # Xóa tài khoản nếu hết hạn
            user.delete()
            return render(request, 'accounts/verify_fail.html', {
                'message': 'Link xác thực đã hết hạn. Tài khoản của bạn đã bị xóa, vui lòng đăng ký lại.'
            })

        user.is_active = True
        user.verification_token = None
        user.verification_token_expires = None
        user.save()
        
        return render(request, 'accounts/verify_success.html')
        
    except CustomUser.DoesNotExist:
        return render(request, 'accounts/verify_fail.html', {
            'message': 'Link xác thực không hợp lệ'
        })

# Login view
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            # Xử lý AJAX request
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
            else:
                username = request.POST.get('username')
                password = request.POST.get('password')

            try:
                if '@' in username:
                    user = CustomUser.objects.filter(
                        models.Q(email=username) | 
                        models.Q(social_auth__uid=username)
                    ).first()
                else:
                    user = CustomUser.objects.get(username=username)

                if not user:
                    return JsonResponse({
                        'success': False,
                        'message': 'Tài khoản không tồn tại'
                    })

                if user.check_password(password) or user.social_auth.exists():
                    if user.social_auth.exists():
                        user.backend = 'social_core.backends.google.GoogleOAuth2'
                    else:
                        user.backend = 'django.contrib.auth.backends.ModelBackend'

                    login(request, user)
                    
                    # Lấy thông tin thiết bị và IP
                    device, browser = get_client_info(request)
                    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
                    if ',' in ip_address:
                        ip_address = ip_address.split(',')[0]

                    # Kiểm tra xem đã có bản ghi nào trong vòng 5 phút gần đây không
                    five_minutes_ago = timezone.now() - timedelta(minutes=5)
                    existing_login = LoginHistory.objects.filter(
                        user=user,
                        device_info=device,
                        browser_info=browser,
                        ip_address=ip_address,
                        login_time__gte=five_minutes_ago
                    ).first()

                    if not existing_login:
                        # Chỉ tạo bản ghi mới nếu không có bản ghi gần đây
                        LoginHistory.objects.create(
                            user=user,
                            ip_address=ip_address,
                            device_info=device,
                            browser_info=browser,
                            location=get_location_from_ip(ip_address),
                            status='confirmed' if user.social_auth.exists() else 'pending',
                            login_time=timezone.now()
                        )

                    return JsonResponse({
                        'success': True,
                        'message': 'Đăng nhập thành công!'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Mật khẩu không chính xác'
                    })

            except CustomUser.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Tài khoản không tồn tại'
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Có lỗi xảy ra: {str(e)}'
            })

    return render(request, 'accounts/login.html')

# Logout view
def user_logout(request):
    logout(request)
    return redirect('login')

# Profile update view
@login_required
@require_http_methods(["POST"])
def update_profile(request):
    try:
        user = request.user
        
        # Lấy dữ liệu từ form
        username = request.POST.get('username')
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        gender = request.POST.get('gender')
        birth_day = request.POST.get('birth_day')
        birth_month = request.POST.get('birth_month')
        birth_year = request.POST.get('birth_year')

        # Cập nhật username nếu có thay đổi
        if username and username != user.username:
            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Tên đăng nhập đã tồn tại'
                })
            user.username = username

        # Cập nhật các thông tin khác
        if full_name:
            user.full_name = full_name
        if phone_number:
            user.phone_number = phone_number
        if gender:
            user.gender = gender

        # Xử lý ngày sinh
        if birth_day and birth_month and birth_year:
            try:
                user.birth_date = datetime(
                    int(birth_year),
                    int(birth_month),
                    int(birth_day)
                ).date()
            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ngày sinh không hợp lệ'
                })

        # Xử lý avatar
        if request.FILES.get('avatar'):
            user.avatar = request.FILES['avatar']

        user.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Cập nhật thông tin thành công',
            'data': {
                'username': user.username,
                'full_name': user.full_name,
                'phone': user.phone_number,
                'gender': user.gender,
                'birth_date': user.birth_date.strftime('%Y-%m-%d') if user.birth_date else None,
                'avatar_url': user.avatar.url if user.avatar else None
            }
        })

    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

# Forgot Password view
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/forgot_password.html'
    email_template_name = 'accounts/password_reset_email.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        send_mail(
            'Password Reset Request',
            'Click the link to reset your password.',
            'tomoi20204@gmail.com',
            [email],
        )
        return super().form_valid(form)

# Reset Password view
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/reset_password.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('login')

# Social Auth views
def social_login(request):
    try:
        # Lấy thông tin thiết bị và trình duyệt
        device, browser = get_client_info(request)
        
        # Lấy IP thật của user
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        if ',' in ip_address:
            ip_address = ip_address.split(',')[0]

        # Lưu lịch sử đăng nhập cho social account
        LoginHistory.objects.create(
            user=request.user,
            ip_address=ip_address, 
            device_info=device,
            browser_info=browser,
            location=get_location_from_ip(ip_address),
            status='confirmed'  # Social login tự động xác nhận
        )

        return JsonResponse({
            'success': True,
            'message': 'Đăng nhập thành công!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Có lỗi xảy ra: {str(e)}'
        })

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('store:home')

@ensure_csrf_cookie
def register(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')

            # Kiểm tra email và username tồn tại
            existing_user = CustomUser.objects.filter(email=email).first()
            if existing_user:
                # Chỉ báo email tồn tại nếu tài khoản đã được kích hoạt
                if existing_user.is_active:
                    return JsonResponse({
                        'success': False,
                        'error': 'Email đã tồn tại!',
                        'action': 'login'
                    })
                else:
                    # Nếu tài khoản chưa kích hoạt, xóa và tạo mới
                    existing_user.delete()
            
            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Tên đăng nhập đã tồn tại! Vui lòng chọn tên khác.'
                })

            # Tạo user mới (chưa active)
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=False
            )

            # Tạo token xác thực
            token = get_random_string(64)
            user.verification_token = token
            user.save()

            # Tạo URL xác thực
            verification_url = request.build_absolute_uri(
                reverse('accounts:verify_email', args=[token])
            )

            # Gửi email xác thực
            try:
                html_message = render_to_string('accounts/email/verify_email.html', {
                    'user': user,
                    'verification_url': verification_url
                })

                send_mail(
                    'Xác thực tài khoản TomOi.vn',
                    '',
                    'tomoivn2024@gmail.com',
                    [email],
                    html_message=html_message,
                    fail_silently=False
                )

                return JsonResponse({
                    'success': True,
                    'message': 'Đăng ký thành công! Vui lòng kiểm tra email để xác thực tài khoản.',
                    'redirect': reverse('accounts:register_verify')
                })

            except Exception as e:
                user.delete()  # Xóa user nếu gửi mail thất bại
                return JsonResponse({
                    'success': False,
                    'error': 'Có lỗi xảy ra khi gửi email xác thực.'
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return render(request, 'accounts/register.html')

def verify_email(request, token):
    try:
        user = CustomUser.objects.get(verification_token=token, is_active=False)
        user.is_active = True
        user.verification_token = None
        user.verification_token_expires = None
        user.save()
        
        # Tự động đăng nhập sau khi xác thực
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        
        return render(request, 'accounts/verify_success.html')
    except CustomUser.DoesNotExist:
        return render(request, 'accounts/verify_fail.html')

@login_required
def register_verify(request):
    if request.user.is_active:
        return redirect('store:home')
    return render(request, 'accounts/register_verify.html')

def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email, is_active=False)
            
            # Generate new verification token
            token = get_random_string(64)
            user.verification_token = token
            user.save()
            
            # Build verification URL
            verification_url = request.build_absolute_uri(
                reverse('store:verify_email', args=[token])
            )
            
            # Send verification email
            html_message = render_to_string('store/verify_email.html', {
                'user': user,
                'verification_url': verification_url
            })
            
            send_mail(
                'Xác thực tài khoản TomOi.vn',
                '',
                'tomoivn2024@gmail.com',
                [email],
                html_message=html_message,
                fail_silently=False
            )
            
            messages.success(request, 'Email xác thực đã được gửi lại.')
            return JsonResponse({'success': True})
            
        except CustomUser.DoesNotExist:
            messages.error(request, 'Không tìm thấy tài khoản chưa xác thực với email này.')
            return JsonResponse({'success': False})
    
    return render(request, 'store/register_verify.html')

@csrf_exempt
def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            validate_email(email)
            user = CustomUser.objects.filter(email=email).first()
            
            if not user:
                return JsonResponse({
                    'success': False,
                    'message': 'Email không tồn tại trong hệ thống',
                    'code': 'EMAIL_NOT_FOUND'
                })

            # Tạo OTP 6 số
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            # Lưu OTP vào session với thời gian hết hạn
            request.session['reset_password_otp'] = {
                'email': email,
                'otp': otp,
                'expires': (timezone.now() + timedelta(minutes=5)).timestamp()
            }

            # Gửi email
            send_mail(
                'Mã xác thực đặt lại mật khẩu - TomOi.vn',
                f'Mã xác thực của bạn là: {otp}\nMã có hiệu lực trong 5 phút.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return JsonResponse({
                'success': True,
                'message': f'Mã xác thực đã được gửi đến {mask_email(email)}'
            })

        except ValidationError:
            return JsonResponse({
                'success': False,
                'message': 'Email không hợp lệ'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Có lỗi xảy ra: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'message': 'Phương thức không hợp lệ'
    })

@csrf_exempt
def resend_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            validate_email(email)
            user = CustomUser.objects.filter(email=email).first()
            
            if not user:
                return JsonResponse({
                    'success': False,
                    'message': 'Email không tồn tại trong hệ thống'
                })

            # Tạo OTP mới
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            # Lưu OTP mới vào session
            request.session['reset_password_otp'] = {
                'email': email,
                'otp': otp,
                'expires': (timezone.now() + timedelta(minutes=5)).timestamp()
            }

            # Gửi email OTP mới
            send_mail(
                'Mã xác thực đặt lại mật khẩu - TomOi.vn',
                f'Mã xác thực mới của bạn là: {otp}\nMã có hiệu lực trong 5 phút.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return JsonResponse({
                'success': True,
                'message': 'Đã gửi lại mã xác thực'
            })

        except ValidationError:
            return JsonResponse({
                'success': False,
                'message': 'Email không hợp lệ'
            })
        except Exception as e:
            print(f"Error in resend_otp: {str(e)}")  # Log lỗi để debug
            return JsonResponse({
                'success': False,
                'message': f'Có lỗi xảy ra: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'message': 'Phương thức không hợp lệ'
    })

@csrf_exempt
def verify_otp(request):
    try:
        data = json.loads(request.body)
        otp = data.get('otp')
        login_id = data.get('login_id')
        action = data.get('action', 'confirm')  # Mặc định là confirm
        
        # Kiểm tra OTP
        stored_otp = request.session.get('email_otp')
        timestamp = request.session.get('email_otp_timestamp')
        
        if not stored_otp or not timestamp:
            return JsonResponse({
                'status': 'error',
                'message': 'OTP không tồn tại'
            }, status=400)
            
        # Kiểm tra thời gian hết hạn
        timestamp = datetime.fromisoformat(timestamp)
        if timezone.now() > timestamp + timedelta(minutes=5):
            del request.session['email_otp']
            del request.session['email_otp_timestamp']
            return JsonResponse({
                'status': 'error',
                'message': 'OTP đã hết hạn'
            }, status=400)
            
        # Kiểm tra OTP
        if otp != stored_otp:
            return JsonResponse({
                'status': 'error',
                'message': 'Mã OTP không chính xác'
            }, status=400)
            
        # Xử lý theo action
        login = LoginHistory.objects.get(id=login_id, user=request.user)
        if action == 'logout':
            # Xóa thiết bị
            login.delete()
        else:
            # Xác nhận thiết bị
            login.status = 'confirmed'
            login.save()
        
        # Xóa OTP đã sử dụng
        del request.session['email_otp']
        del request.session['email_otp_timestamp']
        
        return JsonResponse({
            'status': 'success',
            'message': 'Xác thực thành công'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def unauthorized_view(request):
    return JsonResponse({'error': 'Login required'}, status=401)

@login_required
def user_info(request):
    # Tạo danh sách năm từ 1970-2020
    current_year = 2020
    birth_years = range(current_year, 1969, -1)
    
    context = {
        'birth_years': birth_years,
        'user': request.user
    }
    return render(request, 'accounts/user_info.html', context)

@admin_required
def admin_dashboard(request):
    return render(request, 'accounts/admin/dashboard.html')

@staff_required
def staff_dashboard(request):
    return render(request, 'accounts/staff/dashboard.html')

@admin_required
def manage_users(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'accounts/admin/manage_users.html', {
        'users': users
    })

@staff_required
def manage_orders(request):
    orders = Order.objects.all()
    return render(request, 'accounts/staff/manage_orders.html', {'orders': orders})

@admin_required
def toggle_user_status(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = not user.is_active
            user.save()
            
            status_text = "hoạt động" if user.is_active else "không hoạt động"
            return JsonResponse({
                'success': True,
                'message': f'Đã chuyển trạng thái tài khoản sang {status_text}',
                'is_active': user.is_active
            })
        except CustomUser.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy người dùng'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Phương thức không hợp lệ'
    })

@login_required 
def payment_history(request):
    # Lấy tất cả giao dịch liên quan đến số dư
    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Lấy tổng số TCoin của user từ TCoinHistory
    total_tcoin = TCoinHistory.objects.filter(
        user=request.user
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Debug để kiểm tra
    print(f"User: {request.user.username}")
    print(f"Total TCoin: {total_tcoin}")
    print(f"TCoin histories: {TCoinHistory.objects.filter(user=request.user).values('amount')}")
    
    context = {
        'transactions': transactions,
        'user': request.user,
        'tcoin_balance': total_tcoin  # Sử dụng tổng số TCoin
    }
    
    return render(request, 'accounts/payment_history.html', context)

@login_required
def order_history(request):
    # Lấy lịch sử mua hàng (không còn dùng transaction_type)
    purchase_transactions = Transaction.objects.filter(
        user=request.user,
        order__isnull=False  # Chỉ lấy các giao dịch có liên kết với đơn hàng
    ).order_by('-created_at')
    
    # Lấy lịch sử nạp tiền
    deposit_transactions = Transaction.objects.filter(
        user=request.user,
        order__isnull=True,  # Các giao dịch nạp tiền không có order
        payment_method__in=['vnpay', 'card']  # Các phương thức nạp tiền
    ).order_by('-created_at')

    context = {
        'purchase_transactions': purchase_transactions,
        'deposit_transactions': deposit_transactions
    }
    
    return render(request, 'accounts/order_history.html', context)

@login_required
def security_view(request):
    login_history = LoginHistory.objects.filter(user=request.user)
    return render(request, 'accounts/security.html', {
        'login_history': login_history
    })

@login_required
@require_POST
def change_password(request):
    try:
        data = json.loads(request.body)
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # Kiểm tra mật khẩu hiện tại
        if not request.user.check_password(current_password):
            return JsonResponse({
                'error': 'current_password_incorrect',
                'message': 'Mật khẩu hiện tại không đúng'
            }, status=400)

        # Kiểm tra mật khẩu mới khác mật khẩu cũ
        if current_password == new_password:
            return JsonResponse({
                'error': 'same_password',
                'message': 'Mật khẩu mới phải khác mật khẩu hiện tại'
            }, status=400)

        # Đổi mật khẩu
        request.user.set_password(new_password)
        request.user.save()
        
        # Cập nhật session để giữ người dùng đăng nhập
        update_session_auth_hash(request, request.user)

        return JsonResponse({
            'message': 'Đổi mật khẩu thành công'
        })

    except Exception as e:
        print(f"Error in change_password: {str(e)}")  # Thêm log để debug
        return JsonResponse({
            'error': 'server_error',
            'message': str(e)
        }, status=500)

@login_required
@require_POST
def setup_2fa(request):
    try:
        data = json.loads(request.body)
        method = data.get('method')
        
        if method == 'google_authenticator':
            otp = data.get('otp', '').strip()
            secret_key = data.get('secret_key')
            
            print(f"Setup 2FA - Received OTP: {otp}")  # Debug log
            print(f"Setup 2FA - Secret Key: {secret_key}")  # Debug log
            
            if not otp:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Vui lòng nhập mã xác thực'
                }, status=400)
                
            if not secret_key:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Thiếu secret key'
                }, status=400)
            
            try:
                # Verify mã OTP với secret key
                totp = pyotp.TOTP(secret_key)
                is_valid = totp.verify(otp, valid_window=1)
                print(f"Setup 2FA - OTP verification result: {is_valid}")  # Debug log
                
                if not is_valid:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Mã xác thực không chính xác'
                    }, status=400)
                
                # Lưu secret key và cập nhật trạng thái 2FA
                request.user.ga_secret_key = secret_key
                request.user.has_2fa = True
                request.user.two_factor_method = 'google_authenticator'
                request.user.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Đã thiết lập Google Authenticator'
                })
                
            except Exception as e:
                print(f"Setup 2FA - TOTP verification error: {str(e)}")  # Debug log
                return JsonResponse({
                    'status': 'error',
                    'message': 'Lỗi xác thực mã OTP'
                }, status=400)
            
        # ... xử lý các phương thức khác
        
    except Exception as e:
        print(f"Setup 2FA - Error: {str(e)}")  # Debug log
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def send_otp_email(request):
    try:
        # Generate OTP
        otp = ''.join(random.choices('0123456789', k=6))
        
        # Save OTP to session
        request.session['email_otp'] = otp
        request.session['email_otp_timestamp'] = str(timezone.now())
        
        try:
            # Render email template
            html_message = render_to_string('accounts/emails/otp_email.html', {
                'otp': otp,
                'user': request.user,
                'expiry_minutes': 5
            })
            
            # Send email
            send_mail(
                'Mã OTP xác thực - TomOi.vn',
                f'Mã OTP của bạn là: {otp}\nMã có hiệu lực trong 5 phút.',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"OTP email sent successfully to {request.user.email}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Đã gửi mã OTP'
            })
            
        except Exception as e:
            logger.error(f"Failed to send OTP email: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Không thể gửi email. Vui lòng thử lại sau.'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error in send_otp_email: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def setup_google_authenticator(request):
    try:
        # Tạo secret key mới
        secret_key = pyotp.random_base32()
        
        # Tạo URI cho QR code
        totp = pyotp.TOTP(secret_key)
        provisioning_uri = totp.provisioning_uri(
            request.user.email,
            issuer_name="TomOi.vn"
        )
        
        # Tạo QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Chuyển QR code thành base64 image
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_code = base64.b64encode(buffered.getvalue()).decode()
        
        # Lưu secret key vào session
        request.session['ga_secret_key'] = secret_key
        
        return JsonResponse({
            'status': 'success',
            'qr_code': qr_code,
            'secret_key': secret_key
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_POST
def verify_ga(request):
    try:
        data = json.loads(request.body)
        otp = data.get('otp', '').strip()

        print(f"Received OTP: {otp}")  # Debug log
        print(f"User GA secret key: {request.user.ga_secret_key}")  # Debug log

        if not otp:
            return JsonResponse({
                'status': 'error',
                'message': 'Vui lòng nhập mã xác thực'
            }, status=400)

        if not request.user.ga_secret_key:
            return JsonResponse({
                'status': 'error',
                'message': 'Chưa thiết lập Google Authenticator'
            }, status=400)

        try:
            # Verify mã OTP
            totp = pyotp.TOTP(request.user.ga_secret_key)
            is_valid = totp.verify(otp, valid_window=1)  # Cho phép sai lệch 1 khoảng thời gian
            print(f"OTP verification result: {is_valid}")  # Debug log

            if not is_valid:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Mã xác thực không chính xác'
                }, status=400)

            return JsonResponse({
                'status': 'success',
                'message': 'Xác thực thành công'
            })

        except Exception as e:
            print(f"TOTP verification error: {str(e)}")  # Debug log
            return JsonResponse({
                'status': 'error',
                'message': 'Lỗi xác thực mã OTP'
            }, status=400)

    except Exception as e:
        print(f"Error in verify_ga: {str(e)}")  # Debug log
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_POST
def delete_2fa(request):
    try:
        # Xóa thông tin 2FA
        request.user.has_2fa = False
        request.user.two_factor_method = None
        request.user.two_factor_password = None
        request.user.ga_secret_key = None  # Thêm dòng này
        request.user.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Đã xóa xác thực 2 lớp'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def send_email_change_otp(request):
    try:
        current_email = request.POST.get('current_email')
        is_resend = request.POST.get('resend') == 'true'
        
        # Nếu là resend, sử dụng email đã lưu trong cache
        if is_resend:
            cached_email = cache.get(f'email_change_{request.user.id}')
            if not cached_email:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Phiên xác thực đã hết hạn'
                })
            current_email = cached_email
        
        # Kiểm tra email hiện tại
        if not is_resend and current_email != request.user.email:
            return JsonResponse({
                'status': 'error',
                'message': 'Email không khớp! Vui lòng nhập lại.'
            })
            
        # Tạo OTP và lưu vào cache
        otp = get_random_string(6, '0123456789')
        cache.set(f'email_change_otp_{request.user.id}', otp, 300)  # 5 phút
        cache.set(f'email_change_{request.user.id}', current_email, 300)
        
        # Gửi email OTP
        send_mail(
            'Mã OTP xác thực thay đổi email - TomOi.vn',
            f'Mã OTP của bạn là: {otp}\nMã có hiệu lực trong 5 phút.',
            settings.EMAIL_HOST_USER,
            [current_email],
            fail_silently=False
        )
        
        return JsonResponse({
            'status': 'success',
            'masked_email': mask_email(current_email)
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
@require_http_methods(["POST"])
def verify_email_change_otp(request):
    try:
        otp = request.POST.get('otp')
        
        # Lấy OTP từ cache
        cached_otp = cache.get(f'email_change_otp_{request.user.id}')
        if not cached_otp:
            return JsonResponse({
                'status': 'error',
                'message': 'OTP đã hết hạn'
            })
            
        # Kiểm tra OTP
        if otp != cached_otp:
            return JsonResponse({
                'status': 'error',
                'message': 'OTP không chính xác'
            })
            
        # Xóa OTP khỏi cache
        cache.delete(f'email_change_otp_{request.user.id}')
        cache.delete(f'email_change_{request.user.id}')
        
        return JsonResponse({
            'status': 'success',
            'message': 'Xác thực thành công'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
@require_http_methods(["POST"])
def update_email(request):
    try:
        new_email = request.POST.get('new_email')
        
        # Validate email
        try:
            validate_email(new_email)
        except ValidationError:
            return JsonResponse({
                'status': 'error',
                'message': 'Email không hợp lệ'
            })
            
        # Kiểm tra email đã tồn tại
        if CustomUser.objects.filter(email=new_email).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Email đã được sử dụng'
            })
            
        # Cập nhật email
        request.user.email = new_email
        request.user.save()
        
        # Gửi email thông báo
        send_mail(
            'Thông báo thay đổi email - TomOi.vn',
            'Email của bạn đã được thay đổi thành công.',
            settings.EMAIL_HOST_USER,
            [new_email],
            fail_silently=False
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Email đã được cập nhật thành công'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
def settings_view(request):
    context = {
        'current_theme': request.session.get('theme', 'light'),
        'snow_effect': request.session.get('snow_effect', False),
        'pet_effect': request.session.get('pet_effect', False),
        'font_size': request.session.get('font_size', 'medium'),
    }
    return render(request, 'accounts/settings.html', context)

@login_required
@require_http_methods(["POST"])
def update_language(request):
    try:
        data = json.loads(request.body)
        language = data.get('language')
        
        if language in ['en', 'vi']:
            # Lưu ngôn ngữ vào session
            request.session['language'] = language
            
            # Tạo response
            response = JsonResponse({'success': True})
            response.set_cookie(
                'googtrans', f'/vi/{language}',  # Từ tiếng Việt sang ngôn ngữ đích
                max_age=365 * 24 * 60 * 60  # Cookie hết hạn sau 1 năm
            )
            return response
            
    except Exception as e:
        print(f"Error updating language: {str(e)}")
        
    return JsonResponse({
        'success': False,
        'error': 'Invalid language selection'
    }, status=400)

def set_language(request):
    if request.method == 'POST':
        lang_code = request.POST.get('language', 'vi')
        response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie('django_language', lang_code)
        return response
    return redirect('home')

def profile(request):
    # ... code hiện tại ...
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'transactions': transactions,
        # ... context hiện tại ...
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    # Xử lý filter
    search = request.GET.get('search')
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    has_discount = request.GET.get('has_discount')
    
    if search:
        wishlist_items = wishlist_items.filter(
            Q(product__name__icontains=search) | 
            Q(product__product_code__icontains=search)
        )
    
    if category:
        wishlist_items = wishlist_items.filter(product__category_id=category)
        
    if min_price:
        wishlist_items = wishlist_items.filter(product__price__gte=min_price)
        
    if max_price:
        wishlist_items = wishlist_items.filter(product__price__lte=max_price)
        
    if has_discount:
        if has_discount == '1':
            wishlist_items = wishlist_items.filter(product__old_price__isnull=False)
        else:
            wishlist_items = wishlist_items.filter(product__old_price__isnull=True)
    
    context = {
        'wishlist_items': wishlist_items,
        'total_items': wishlist_items.count(),
        'categories': Category.objects.all()
    }
    return render(request, 'accounts/wishlist.html', context)

@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            new_password = data.get('new_password')
            
            user = CustomUser.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            # Tự động đăng nhập user
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'message': 'Đặt lại mật khẩu thành công'
            })
            
        except CustomUser.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy tài khoản'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
            
    return JsonResponse({
        'success': False,
        'message': 'Phương thức không hợp lệ'
    })

DEEPL_API_KEY = '893c70b4-e735-4e1c-b9cd-e27585166d17:fx'

@csrf_exempt
def translate_text(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed'
        }, status=405)

    try:
        data = json.loads(request.body)
        text = data.get('text')
        target_lang = data.get('target_lang')

        if not text or not target_lang:
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters'
            }, status=400)

        response = requests.post(
            'https://api-free.deepl.com/v2/translate',
            headers={
                'Authorization': f'DeepL-Auth-Key {settings.DEEPL_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'text': [text],
                'target_lang': target_lang
            }
        )

        if response.status_code == 200:
            translation_data = response.json()
            return JsonResponse({
                'success': True,
                'translation': translation_data['translations'][0]['text']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'DeepL API error: {response.status_code}'
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def check_2fa_password(request):
    """Kiểm tra xem user đã có 2FA chưa"""
    has_2fa = request.user.has_2fa
    method = request.user.two_factor_method
    
    # Debug log
    print(f"User 2FA status: has_2fa={has_2fa}, method={method}")
    print(f"User 2FA secret: {request.user.two_factor_secret}")
    
    return JsonResponse({
        'has_2fa_password': has_2fa,
        'method': method,
        'has_secret': bool(request.user.two_factor_secret)
    })

@login_required
@require_POST
def confirm_device(request):
    try:
        data = json.loads(request.body)
        login_id = data.get('login_id')
        password = data.get('password')

        # Kiểm tra mật khẩu cấp 2
        if not request.user.check_two_factor_password(password):
            return JsonResponse({
                'success': False,
                'message': 'Mật khẩu cấp 2 không chính xác'
            })

        # Lấy và cập nhật trạng thái login history
        login = LoginHistory.objects.get(id=login_id, user=request.user)
        login.status = 'confirmed'
        login.save()

        return JsonResponse({
            'success': True,
            'message': 'Đã xác nhận thiết bị thành công'
        })

    except LoginHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Không tìm thấy thông tin đăng nhập'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dữ liệu không hợp lệ'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
def logout_device(request):
    """Đăng xuất thiết bị và xóa khỏi lịch sử đăng nhập"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'})
        
    try:
        data = json.loads(request.body)
        login_id = data.get('login_id')
        method = data.get('method')
        
        # Debug log
        print(f"Logout device request: method={method}, login_id={login_id}")
        
        login = LoginHistory.objects.get(
            id=login_id,
            user=request.user
        )
        
        # Xác thực với 2FA
        if method == 'google':
            otp = data.get('otp')
            if not otp:
                return JsonResponse({
                    'success': False,
                    'message': 'Không tìm thấy mã OTP'
                })
                
            if not request.user.two_factor_secret:
                return JsonResponse({
                    'success': False,
                    'message': 'Chưa thiết lập Google Authenticator'
                })
                
            totp = pyotp.TOTP(request.user.two_factor_secret)
            if not totp.verify(str(otp).strip(), valid_window=1):
                return JsonResponse({
                    'success': False,
                    'message': 'Mã OTP không chính xác'
                })
        else:
            password = data.get('password')
            if not request.user.check_two_factor_password(password):
                return JsonResponse({
                    'success': False,
                    'message': 'Mật khẩu cấp 2 không chính xác'
                })
        
        # Xóa bản ghi đăng nhập
        login.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Đã đăng xuất thiết bị thành công'
        })
        
    except LoginHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Không tìm thấy thông tin đăng nhập'
        })
    except Exception as e:
        print(f"Logout device error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Có lỗi xảy ra: {str(e)}'
        })

@login_required
@require_POST
def change_2fa_password(request):
    try:
        data = json.loads(request.body)
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        # Kiểm tra mật khẩu cấp 2 hiện tại
        if not request.user.check_two_factor_password(current_password):
            return JsonResponse({
                'status': 'error',
                'message': 'Mật khẩu cấp 2 hiện tại không đúng'
            })

        # Cập nhật mật khẩu cấp 2 mới
        request.user.two_factor_password = make_password(new_password)
        request.user.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Đổi mật khẩu cấp 2 thành công'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

def save_login_history(user, request):
    device, browser = get_client_info(request)
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in ip_address:
        ip_address = ip_address.split(',')[0]

    # Kiểm tra xem có login history trong vòng 5 phút gần đây không
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    recent_login = LoginHistory.objects.filter(
        user=user,
        device_info=device,
        browser_info=browser,
        ip_address=ip_address,
        login_time__gte=five_minutes_ago
    ).first()

    if recent_login:
        # Cập nhật thời gian đăng nhập cho bản ghi gần nhất
        recent_login.login_time = timezone.now()
        recent_login.save()
    else:
        # Tạo bản ghi mới nếu không có bản ghi nào trong 5 phút gần đây
        LoginHistory.objects.create(
            user=user,
            ip_address=ip_address,
            device_info=device,
            browser_info=browser,
            location=get_location_from_ip(ip_address),
            status='pending',
            login_time=timezone.now()
        )

@login_required
def check_2fa_status(request):
    """
    Kiểm tra trạng thái 2FA của người dùng
    """
    print(f"User 2FA status: has_2fa={request.user.has_2fa}, method={request.user.two_factor_method}, ga_secret_key={request.user.ga_secret_key}")  # Debug log
    
    if not request.user.has_2fa:
        return JsonResponse({
            'has_2fa': False,
            'method': None,
            'ga_secret_key': None
        })

    if request.user.two_factor_method == 'google_authenticator' and not request.user.ga_secret_key:
        # Nếu phương thức là GA nhưng không có secret key
        request.user.has_2fa = False
        request.user.two_factor_method = None
        request.user.save()
        return JsonResponse({
            'has_2fa': False,
            'method': None,
            'ga_secret_key': None
        })

    return JsonResponse({
        'has_2fa': request.user.has_2fa,
        'method': request.user.two_factor_method,
        'ga_secret_key': request.user.ga_secret_key if request.user.two_factor_method == 'google_authenticator' else None
    })

@login_required
@require_POST 
def verify_2fa_password(request):
    """
    Xác thực mật khẩu cấp 2
    """
    try:
        data = json.loads(request.body)
        password = data.get('password')
        
        if not password:
            return JsonResponse({
                'status': 'error',
                'message': 'Vui lòng nhập mật khẩu'
            }, status=400)
            
        # Verify mật khẩu cấp 2
        if not request.user.check_two_factor_password(password):
            return JsonResponse({
                'status': 'error',
                'message': 'Mật khẩu cấp 2 không chính xác'
            }, status=400)
            
        return JsonResponse({
            'status': 'success',
            'message': 'Xác thực thành công'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_POST
def verify_device(request):
    """
    Xác thực thiết bị đăng nhập
    """
    try:
        data = json.loads(request.body)
        login_id = data.get('login_id')
        password = data.get('password')
        
        # Verify mật khẩu cấp 2
        if not request.user.check_two_factor_password(password):
            return JsonResponse({
                'status': 'error',
                'message': 'Mật khẩu cấp 2 không chính xác'
            }, status=400)
            
        # Xác nhận thiết bị
        login = LoginHistory.objects.get(id=login_id, user=request.user)
        login.status = 'confirmed'
        login.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Đã xác nhận thiết bị'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def deposit_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = int(data.get('amount', 0))
            payment_method = data.get('payment_method')
            
            if amount < 10000:
                return JsonResponse({
                    'success': False,
                    'message': 'Số tiền tối thiểu là 10.000đ'
                })
                
            # Tạo giao dịch nạp tiền
            deposit = Deposit.objects.create(
                user=request.user,
                amount=amount,
                payment_method=payment_method,
                transaction_id=str(uuid.uuid4())
            )
            
            # Xử lý theo từng phương thức thanh toán
            if payment_method == 'vnpay':
                # Tạo URL thanh toán VNPay
                vnpay_url = create_vnpay_url(request, amount)
                return JsonResponse({
                    'success': True,
                    'redirect_url': vnpay_url
                })
            elif payment_method == 'banking':
                # Trả về thông tin chuyển khoản
                return JsonResponse({
                    'success': True,
                    'bank_info': {
                        'account_number': '123456789',
                        'bank_name': 'VietComBank',
                        'account_name': 'CONG TY TNHH TOMOI',
                        'amount': amount,
                        'content': f'NAP {request.user.username} {deposit.transaction_id}'
                    }
                })
            elif payment_method == 'card':
                # Chuyển sang trang nạp thẻ
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('accounts:card_deposit', args=[deposit.transaction_id])
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
            
    return render(request, 'accounts/deposit.html')

@login_required
def tcoin_view(request):
    if request.method == 'POST':
        try:
            today = timezone.now().date()
            # Kiểm tra xem đã điểm danh chưa
            if DailyCheckin.objects.filter(user=request.user, date=today).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Bạn đã điểm danh hôm nay'
                })

            is_sunday = today.weekday() == 6
            tcoin_amount = 10 if is_sunday else 5
            
            with transaction.atomic():
                DailyCheckin.objects.create(
                    user=request.user,
                    date=today,
                    tcoin_earned=tcoin_amount
                )
                
                request.user.tcoin += tcoin_amount
                request.user.save()
                
                TCoinHistory.objects.create(
                    user=request.user,
                    amount=tcoin_amount,
                    activity_type='checkin',
                    description='Điểm danh hàng ngày'
                )
                
            return JsonResponse({
                'success': True,
                'message': 'Điểm danh thành công!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })

    today = timezone.now().date()
    current_weekday = today.weekday()  # 0 = Monday, 6 = Sunday
    
    # Tính ngày thứ 2 (đầu tuần)
    monday = today - timedelta(days=current_weekday)
    
    days = []
    weekdays = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
    
    # Tạo list 7 ngày từ thứ 2 đến chủ nhật
    for i in range(7):
        current_date = monday + timedelta(days=i)
        is_sunday = i == 6
        days.append({
            'name': weekdays[i],
            'date': current_date,
            'is_today': current_date == today,
            'is_sunday': is_sunday,
            'tcoin': 10 if is_sunday else 5,
            'checked_in': DailyCheckin.objects.filter(
                user=request.user,
                date=current_date
            ).exists()
        })

    context = {
        'days': days,
        'can_checkin': not DailyCheckin.objects.filter(
            user=request.user,
            date=today
        ).exists(),
        'is_sunday': today.weekday() == 6,
        'tcoin_history': TCoinHistory.objects.filter(
            user=request.user
        ).order_by('-created_at')
    }
    
    return render(request, 'accounts/tcoin.html', context)

def payment_history_view(request):
    context = {
        'user': request.user,  # Đảm bảo user được pass vào context
        'transactions': ...
    }
    return render(request, 'accounts/payment_history.html', context)

@login_required
@require_http_methods(["POST"])
def card_deposit(request):
    try:
        data = json.loads(request.body)
        telco = data.get('telco')
        serial = data.get('serial')
        pin = data.get('pin')
        amount = int(data.get('amount'))

        # Tạo request_id ngẫu nhiên
        request_id = f"CARD_{int(time.time())}_{random.randint(1000,9999)}"

        # Lưu thông tin giao dịch
        transaction = CardTransaction.objects.create(
            user=request.user,
            request_id=request_id,
            telco=telco,
            serial=serial,
            pin=pin,
            amount=amount
        )

        # Gọi API nạp thẻ
        result = process_card_payment({
            'transaction_id': request_id,
            'telco': telco,
            'serial': serial,
            'pin': pin,
            'amount': amount
        })

        if result.get('status') == 1:  # Thẻ đúng
            return JsonResponse({
                'success': True,
                'message': 'Thẻ đang được xử lý'
            })
        else:
            transaction.status = 'failed'
            transaction.message = result.get('message')
            transaction.save()
            return JsonResponse({
                'success': False,
                'message': result.get('message')
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@csrf_exempt
def card_callback(request):
    """Callback URL để nhận kết quả từ DoiThe.vn"""
    try:
        data = json.loads(request.body)
        
        # Verify callback signature
        sign_string = f"{settings.DOITHE_PARTNER_KEY}{data['request_id']}{data['status']}"
        check_sign = hashlib.md5(sign_string.encode()).hexdigest()
        
        if data.get('sign') != check_sign:
            return HttpResponse('Invalid signature', status=400)
            
        # Tìm giao dịch
        transaction = CardTransaction.objects.get(request_id=data['request_id'])
        
        if data['status'] == 1: # Thẻ đúng
            transaction.status = 'success'
            transaction.real_amount = data.get('real_amount', transaction.amount)
            
            # Cộng tiền vào tài khoản
            transaction.user.balance += transaction.real_amount
            transaction.user.save()
            
            # Ghi log giao dịch thành công
            print(f"Card charged successfully: {transaction.request_id}")
            
        else: # Thẻ sai
            transaction.status = 'failed'
            transaction.message = data.get('message', 'Thẻ không hợp lệ')
            
        transaction.save()
        
        return HttpResponse('OK')
        
    except Exception as e:
        print(f"Callback error: {str(e)}")
        return HttpResponse(str(e), status=500)

@login_required
@require_http_methods(["POST"])
def create_payment(request):
    try:
        data = json.loads(request.body)
        amount = int(data.get('amount', 0))
        payment_method = data.get('payment_method')

        if amount < 10000:
            return JsonResponse({
                'success': False,
                'message': 'Số tiền nạp tối thiểu là 10.000đ'
            })

        if payment_method == 'vnpay':
            try:
                # Tạo mã giao dịch unique
                txn_ref = f"VNP{int(time.time())}"

                # Tạo instance của VNPay
                vnpay = VNPay()
                
                # Cấu hình các tham số theo thứ tự alphabet
                vnpay.requestData = {
                    'vnp_Amount': str(amount * 100),
                    'vnp_BankCode': 'NCB',
                    'vnp_Command': 'pay',
                    'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
                    'vnp_CurrCode': 'VND',
                    'vnp_IpAddr': get_client_ip(request),
                    'vnp_Locale': 'vn',
                    'vnp_OrderInfo': f'Nap tien tai khoan {request.user.username}',
                    'vnp_OrderType': 'billpayment',
                    'vnp_TmnCode': settings.VNPAY_TMN_CODE,
                    'vnp_TxnRef': txn_ref,
                    'vnp_Version': '2.1.0'
                }

                # Tạo URL thanh toán với is_deposit=True
                payment_url = vnpay.get_payment_url(
                    settings.VNPAY_PAYMENT_URL,
                    settings.VNPAY_HASH_SECRET_KEY,
                    is_deposit=True
                )

                # Lưu thông tin giao dịch
                Deposit.objects.create(
                    user=request.user,
                    amount=amount,
                    transaction_id=txn_ref,
                    payment_method='vnpay',
                    status='pending'
                )

                return JsonResponse({
                    'success': True,
                    'payment_url': payment_url
                })

            except Exception as e:
                print(f"Error creating VNPay URL: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': f'Lỗi tạo URL thanh toán: {str(e)}'
                })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dữ liệu không hợp lệ'
        })

    return JsonResponse({
        'success': False,
        'message': 'Phương thức không được hỗ trợ'
    })

@csrf_exempt
def vnpay_return(request):
    """Xử lý kết quả trả về từ VNPay cho nạp tiền"""
    if request.method == 'GET':
        vnpay = VNPay()
        vnpay.responseData = request.GET.dict()

        if vnpay.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            response_code = vnpay.responseData.get('vnp_ResponseCode')
            amount = Decimal(int(vnpay.responseData.get('vnp_Amount', 0)) / 100)
            
            if response_code == '00':
                try:
                    with transaction.atomic():
                        # Cập nhật số dư
                        user = request.user
                        user.balance += amount
                        user.save()
                        
                        # Tạo lịch sử nạp tiền
                        Transaction.objects.create(
                            user=user,
                            amount=amount,
                            transaction_id=f"NT{int(time.time())}",  # NT = Nạp Tiền
                            payment_method='vnpay',
                            status='success',
                            description=f'Nạp {amount:,}đ qua VNPay'
                        )
                        
                        return render(request, 'accounts/deposit_success.html', {
                            'amount': amount,
                            'user': user
                        })
                except Exception as e:
                    print(f"Error processing deposit: {str(e)}")
                    return redirect('accounts:deposit')
            else:
                return redirect('accounts:deposit')
        else:
            return redirect('accounts:deposit')
    
    return redirect('accounts:deposit')

def get_client_ip(request):
    """Lấy IP của client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def create_vnpay_url(request, amount):
    """Tạo URL thanh toán VNPay"""
    # Tạo mã giao dịch unique
    txn_ref = f"VNP{int(time.time())}"
    
    # Tạo các tham số cho VNPay
    vnp_params = {
        'vnp_Version': '2.1.0',
        'vnp_Command': 'pay',
        'vnp_TmnCode': settings.VNPAY_TMN_CODE,
        'vnp_Amount': str(amount * 100),  # Số tiền * 100
        'vnp_CurrCode': 'VND',
        'vnp_TxnRef': txn_ref,
        'vnp_OrderInfo': f'Nap tien tai khoan {request.user.username}',
        'vnp_OrderType': 'billpayment',
        'vnp_Locale': 'vn',
        'vnp_ReturnUrl': settings.VNPAY_RETURN_URL,
        'vnp_IpAddr': get_client_ip(request),
        'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
        'vnp_BankCode': 'NCB'
    }

    # Sắp xếp các tham số theo thứ tự a-z
    vnp_params = OrderedDict(sorted(vnp_params.items()))

    # Tạo chuỗi hash data theo đúng format của VNPay
    hash_data = ""
    i = 0
    for key, value in vnp_params.items():
        if i == 1:
            hash_data += '&' + urlencode({key: value})
        else:
            hash_data += urlencode({key: value})
            i = 1

    # Tạo secure hash
    secure_hash = hmac.new(
        bytes(settings.VNPAY_HASH_SECRET_KEY, 'utf-8'),
        bytes(hash_data, 'utf-8'),
        hashlib.sha512
    ).hexdigest()

    # Thêm secure hash vào params
    vnp_params['vnp_SecureHash'] = secure_hash

    # Tạo URL thanh toán
    query_string = ""
    i = 0
    for key, value in vnp_params.items():
        if i == 1:
            query_string += '&' + urlencode({key: value})
        else:
            query_string += urlencode({key: value})
            i = 1

    payment_url = f"{settings.VNPAY_PAYMENT_URL}?{query_string}"

    # Debug log
    print("Hash Data:", hash_data)
    print("Secure Hash:", secure_hash)
    print("Payment URL:", payment_url)

    # Lưu thông tin giao dịch
    Deposit.objects.create(
        user=request.user,
        amount=amount,
        transaction_id=txn_ref,
        payment_method='vnpay',
        status='pending'
    )

    return payment_url

import random
from datetime import datetime

def generate_deposit_transaction_id():
    """Tạo mã giao dịch nạp tiền theo định dạng NT + năm + tháng + 6 số ngẫu nhiên + ngày"""
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    
    # Tạo 6 số ngẫu nhiên
    random_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Ghép mã theo định dạng
    transaction_id = f"NT{year}{month}{random_digits}{day}"
    
    return transaction_id

@csrf_exempt
def vnpay_deposit_return(request):
    """Xử lý kết quả trả về từ VNPay cho nạp tiền"""
    if request.method == 'GET':
        vnpay = VNPay()
        vnpay.responseData = request.GET.dict()

        if vnpay.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            response_code = vnpay.responseData.get('vnp_ResponseCode')
            amount = Decimal(int(vnpay.responseData.get('vnp_Amount', 0)) / 100)
            txn_ref = vnpay.responseData.get('vnp_TxnRef')
            
            if response_code == '00':
                try:
                    with transaction.atomic():
                        # Cập nhật số dư
                        user = request.user
                        user.balance += amount
                        user.save()
                        
                        # Tạo lịch sử giao dịch nạp tiền
                        Transaction.objects.create(
                            user=user,
                            amount=amount,
                            transaction_id=generate_deposit_transaction_id(),  # Sử dụng hàm mới
                            payment_method='vnpay',
                            status='completed',
                            description=f'Nạp {amount:,}đ qua VNPay'
                        )
                        
                        return render(request, 'accounts/deposit_success.html', {
                            'amount': amount,
                            'user': user
                        })
                        
                except Exception as e:
                    print(f"Error processing deposit: {str(e)}")
                    return redirect('accounts:deposit')
            else:
                return redirect('accounts:deposit')
        else:
            return redirect('accounts:deposit')
    
    return redirect('accounts:deposit')

@csrf_exempt 
def vnpay_order_return(request):
    try:
        logger.info("Processing VNPAY return")
        # Chuyển QueryDict sang dict thường
        vnp_response = dict(request.GET.items())
        
        # Khởi tạo VNPay và kiểm tra tính hợp lệ của response
        vnpay = VnPay()
        if vnpay.validate_response(vnp_response):
            # Lấy các tham số cần thiết
            vnp_response_code = vnp_response.get('vnp_ResponseCode')
            vnp_transaction_status = vnp_response.get('vnp_TransactionStatus')

            if vnp_response_code == '00' and vnp_transaction_status == '00':
                logger.info("Payment successful, redirecting to success page")
                return redirect('store:payment_success')
            else:
                logger.info("Payment failed, redirecting to failed page")
                return redirect('store:payment_failed')
        else:
            logger.error("Invalid VNPAY response")
            return redirect('store:payment_failed')
            
    except Exception as e:
        logger.error(f"Error in vnpay_order_return: {str(e)}")
        return redirect('store:payment_failed')

def verify_2fa(user, auth_type, auth_value):
    """Xác thực 2FA"""
    try:
        if auth_type == 'password':
            return user.check_password(auth_value)
        elif auth_type == '2fa':
            if user.two_factor_method == 'password':
                return check_password(auth_value, user.two_factor_password)
            elif user.two_factor_method == 'google':
                # Debug logs
                print(f"Verifying Google OTP for user: {user.username}")
                print(f"Input OTP: {auth_value}")
                print(f"User two_factor_method: {user.two_factor_method}")
                print(f"User two_factor_secret: {user.two_factor_secret}")
                
                # Kiểm tra secret key tồn tại
                if not user.two_factor_secret:  # Sửa từ ga_secret_key thành two_factor_secret
                    print("No 2FA secret key found")
                    return False

                try:
                    # Đảm bảo auth_value là string và loại bỏ khoảng trắng
                    auth_value = str(auth_value).strip()
                    
                    # Tạo TOTP object với secret key của user
                    totp = pyotp.TOTP(user.two_factor_secret)  # Sửa từ ga_secret_key thành two_factor_secret
                    
                    # Lấy mã OTP hiện tại để debug
                    current_otp = totp.now()
                    print(f"Current OTP: {current_otp}")
                    print(f"Input OTP: {auth_value}")
                    
                    # Verify với valid_window=1 (chấp nhận mã trước và sau 30 giây)
                    is_valid = totp.verify(auth_value, valid_window=1)
                    
                    print(f"OTP verification result: {is_valid}")
                    return is_valid
                    
                except Exception as e:
                    print(f"Error verifying TOTP: {str(e)}")
                    return False
                    
            elif user.two_factor_method == 'email':
                stored_otp = cache.get(f'email_otp_{user.id}')
                return stored_otp and stored_otp == auth_value
                
    except Exception as e:
        print(f"Error in verify_2fa: {str(e)}")
        return False
        
    return False

@login_required
@require_POST
def apply_tcoin(request):
    try:
        data = json.loads(request.body)
        tcoin_amount = int(data.get('amount', 0))
        
        # Kiểm tra số TCoin hợp lệ
        if tcoin_amount <= 0:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng nhập số TCoin hợp lệ'
            })
            
        # Kiểm tra số dư TCoin
        if tcoin_amount > request.user.tcoin:
            return JsonResponse({
                'success': False,
                'message': 'Số TCoin không đủ'
            })
            
        # Lấy giỏ hàng hiện tại
        cart_total = request.session.get('cart_total', 0)
        
        # Tính giá trị TCoin
        tcoin_value = tcoin_amount * 100  # 1 TCoin = 100đ
        if tcoin_value > cart_total:
            return JsonResponse({
                'success': False,
                'message': 'Số TCoin vượt quá giá trị đơn hàng'
            })
            
        # Lưu thông tin vào session
        request.session['used_tcoin'] = tcoin_amount
        request.session['tcoin_discount'] = tcoin_value
        
        return JsonResponse({
            'success': True,
            'message': f'Đã áp dụng {tcoin_amount} TCoin',
            'tcoin_discount': tcoin_value
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@require_POST
def apply_referral(request):
    try:
        data = json.loads(request.body)
        code = data.get('code')
        
        # Kiểm tra mã giới thiệu
        if not code:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng nhập mã giới thiệu'
            })
            
        # TODO: Thêm logic xử lý mã giới thiệu
        
        return JsonResponse({
            'success': True,
            'message': 'Đã áp dụng mã giới thiệu'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@require_POST
def apply_voucher(request):
    try:
        data = json.loads(request.body)
        code = data.get('code')
        
        # Kiểm tra mã giảm giá
        if not code:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng nhập mã giảm giá'
            })
            
        # TODO: Thêm logic xử lý mã giảm giá
        
        return JsonResponse({
            'success': True,
            'message': 'Đã áp dụng mã giảm giá'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@require_POST
def apply_gift(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        # Kiểm tra email
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng nhập email người nhận'
            })
            
        # TODO: Thêm logic xử lý tặng quà
        
        return JsonResponse({
            'success': True,
            'message': 'Đã lưu thông tin người nhận quà'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

# API endpoint để lấy chi tiết giao dịch
@login_required
def get_transaction_detail(request, transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id, user=request.user)
        
        data = {
            'id': transaction.id,
            'transaction_id': transaction.transaction_id,
            'created_at': transaction.created_at.strftime('%d/%m/%Y %H:%M'),
            'payment_method': transaction.payment_method,
            'amount': float(transaction.amount),
            'status': transaction.status,
            'description': transaction.description
        }
        
        return JsonResponse(data)
    except Transaction.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy giao dịch'}, status=404)

@csrf_exempt
def public_chatbot_config(request):
    """API endpoint công khai để lấy cấu hình chatbot"""
    try:
        print("=== PUBLIC CHATBOT CONFIG API CALLED ===")
        # Lấy cấu hình chatbot và API đang hoạt động
        config = ChatbotConfig.objects.filter(is_active=True).first()
        api_config = APIConfig.objects.filter(is_active=True).first()
        
        print(f"Config found: {config is not None}")
        print(f"API config found: {api_config is not None}")
        
        if config:
            print(f"Chatbot name: {config.chatbot_name}")
            print(f"Is active: {config.is_active}")
        
        if api_config:
            print(f"API type: {api_config.api_type}")
            print(f"API key: {api_config.api_key[:5]}...")
            print(f"Model: {api_config.model}")
            print(f"Active: {api_config.active}")
        
        if not config or not api_config:
            print("Missing config or API config")
            return JsonResponse({
                'success': False,
                'message': 'Chưa cấu hình chatbot hoặc API'
            })
        
        response_data = {
            'success': True,
            'config': {
                'chatbot_name': config.chatbot_name,
                'base_prompt': config.base_prompt,
                'api_type': api_config.api_type,
                'api_key': api_config.api_key,
                'model': api_config.model,
                'temperature': float(api_config.temperature),
                'endpoint': api_config.endpoint
            }
        }
        
        print(f"Response data: {response_data}")
        return JsonResponse(response_data)
    except Exception as e:
        print(f"Lỗi khi lấy cấu hình public chatbot: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })

@csrf_exempt
def public_chatbot_process(request):
    """API endpoint công khai để xử lý tin nhắn chatbot"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        print("=== CHATBOT PROCESS API CALLED ===")
        print(f"URL path: {request.path}")
        data = json.loads(request.body)
        message = data.get('message', '')
        
        print(f"Received message: {message}")
        
        # Lấy cấu hình API
        config = ChatbotConfig.objects.filter(is_active=True).first()
        api_config = APIConfig.objects.filter(is_active=True).first()
        
        print(f"Config found: {config is not None}")
        print(f"API config found: {api_config is not None}")
        
        if not config or not api_config:
            return JsonResponse({
                'success': False,
                'message': 'Chưa cấu hình chatbot hoặc API'
            })
        
        # Xử lý tin nhắn với API
        chatbot_name = config.chatbot_name or "TomOi Assistant"
        
        return JsonResponse({
            'success': True,
            'response': f"Đây là phản hồi từ {chatbot_name}. Tin nhắn của bạn: {message}"
        })
    except Exception as e:
        print(f"Lỗi khi xử lý tin nhắn chatbot: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })

@csrf_exempt
def log_chat(request):
    """API endpoint để log chat"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Log tin nhắn nếu cần
        return JsonResponse({
            'success': True,
            'message': 'Chat logged successfully'
        })
    except Exception as e:
        print(f"Lỗi khi log chat: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })