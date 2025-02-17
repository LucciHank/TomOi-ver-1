from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
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
from accounts.models import CustomUser, LoginHistory
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
from store.models import Wishlist, Category  # Import Wishlist và Category từ store.models
import pyotp
import qrcode
import base64
from io import BytesIO
from django.contrib.auth.hashers import check_password, make_password
import time
from django.utils import timezone
import hashlib
from .utils import mask_email
from django.core.cache import cache
from django.utils import translation
from django.db.models import Q
import requests
import user_agents
import logging

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
            # Xử lý form submit
            else:
                username = request.POST.get('username')
                password = request.POST.get('password')

            # Tìm user theo username hoặc email
            try:
                if '@' in username:
                    # Nếu đăng nhập bằng email, ưu tiên tài khoản không phải social
                    user = CustomUser.objects.filter(email=username).first()
                    if not user:
                        # Nếu không tìm thấy, thử tìm tài khoản social
                        user = CustomUser.objects.filter(
                            email=username,
                            social_auth__provider='google-oauth2'
                        ).first()
                else:
                    user = CustomUser.objects.get(username=username)

                if not user:
                    return JsonResponse({
                        'success': False,
                        'message': 'Tài khoản không tồn tại'
                    })

                # Kiểm tra mật khẩu
                if user.check_password(password):
                    # Chỉ định backend cụ thể khi đăng nhập
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    
                    # Lấy thông tin thiết bị và trình duyệt
                    device, browser = get_client_info(request)
                    
                    # Lấy IP thật của user
                    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
                    if ',' in ip_address:
                        ip_address = ip_address.split(',')[0].strip()
                    
                    # Kiểm tra xem đã có bản ghi nào với thông tin tương tự chưa
                    existing_login = LoginHistory.objects.filter(
                        user=user,
                        device_info=device,
                        browser_info=browser,
                        ip_address=ip_address,
                        status='pending'
                    ).first()
                    
                    if existing_login:
                        # Cập nhật bản ghi hiện có
                        existing_login.is_current = True
                        existing_login.login_time = timezone.now()
                        existing_login.save()
                        
                        # Đặt các bản ghi khác về is_current=False
                        LoginHistory.objects.filter(user=user).exclude(id=existing_login.id).update(is_current=False)
                    else:
                        # Tạo bản ghi mới
                        LoginHistory.objects.filter(user=user).update(is_current=False)
                        LoginHistory.objects.create(
                            user=user,
                            ip_address=ip_address,
                            device_info=device,
                            browser_info=browser,
                            is_current=True,
                            status='pending'
                        )

                    return JsonResponse({
                        'success': True,
                        'message': 'Đăng nhập thành công'
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
            print(f"Login error: {str(e)}")  # Debug log
            return JsonResponse({
                'success': False,
                'message': str(e)
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
        
        # Cập nhật thông tin cơ bản
        user.first_name = request.POST.get('full_name', '').strip()
        user.phone_number = request.POST.get('phone_number', '').strip()
        
        # Cập nhật giới tính
        gender = request.POST.get('gender')
        if gender in ['M', 'F', 'O']:
            user.gender = gender
            
        # Cập nhật ngày sinh
        birth_day = request.POST.get('birth_day')
        birth_month = request.POST.get('birth_month')
        birth_year = request.POST.get('birth_year')
        
        if birth_day and birth_month and birth_year:
            try:
                user.birth_date = datetime(
                    int(birth_year),
                    int(birth_month),
                    int(birth_day)
                ).date()
            except ValueError:
                pass
        
        # Xử lý avatar nếu có
        if request.FILES.get('avatar'):
            user.avatar = request.FILES['avatar']
        
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Cập nhật thông tin thành công'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
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
    return render(request, 'accounts/social_login.html')

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
        
        # Lấy OTP từ session
        stored_otp = request.session.get('email_otp')
        timestamp = request.session.get('email_otp_timestamp')
        
        if not stored_otp or not timestamp:
            return JsonResponse({
                'status': 'error',
                'message': 'OTP không tồn tại'
            }, status=400)
            
        # Kiểm tra thời gian hết hạn (5 phút)
        timestamp = datetime.fromisoformat(timestamp)
        if timezone.now() > timestamp + timedelta(minutes=5):
            # Xóa OTP hết hạn
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
            
        # OTP hợp lệ, cập nhật 2FA
        request.user.has_2fa = True
        request.user.two_factor_method = 'email'
        request.user.save()
        
        # Xóa OTP đã sử dụng
        del request.session['email_otp']
        del request.session['email_otp_timestamp']
        
        return JsonResponse({
            'status': 'success',
            'message': 'Xác thực thành công'
        })
        
    except Exception as e:
        logger.error(f"Error in verify_otp: {str(e)}")
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
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/payment_history.html', {
        'transactions': transactions
    })

@login_required
def order_history(request):
    purchase_transactions = Transaction.objects.filter(
        user=request.user,
        transaction_type='purchase'
    ).order_by('-created_at')
    
    deposit_transactions = Transaction.objects.filter(
        user=request.user,
        transaction_type='deposit'
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
@require_http_methods(["POST"])
def setup_2fa(request):
    try:
        data = json.loads(request.body)
        method = data.get('method')
        
        if method == 'password':
            password = data.get('password')
            
            if not password:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Vui lòng nhập mật khẩu'
                })
                
            # Mã hóa và lưu mật khẩu cấp 2
            request.user.two_factor_password = make_password(password)
            request.user.two_factor_method = 'password'
            request.user.has_2fa = True
            request.user.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Thiết lập mật khẩu cấp 2 thành công'
            })
            
        return JsonResponse({
            'status': 'error',
            'message': 'Phương thức không hợp lệ'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Dữ liệu không hợp lệ'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

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
    """Thiết lập Google Authenticator"""
    try:
        # Tạo secret key mới
        secret = pyotp.random_base32()
        
        # Tạo URI cho QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            request.user.email,
            issuer_name="TomOi"
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
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Lưu secret tạm thời vào cache
        cache.set(f'ga_secret_{request.user.id}', secret, 300)  # 5 phút
        
        return JsonResponse({
            'status': 'success',
            'qr_code': f'data:image/png;base64,{img_str}',
            'secret': secret
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
def verify_google_authenticator(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid method'
        })
        
    try:
        data = json.loads(request.body)
        otp = data.get('otp')
        
        # Lấy secret key từ session
        secret_key = request.session.get('temp_2fa_secret')
        if not secret_key:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy secret key'
            })
            
        # Debug log
        print(f"Verifying OTP with secret: {secret_key}")
        
        # Xác thực OTP
        totp = pyotp.TOTP(secret_key)
        if totp.verify(otp):
            # Lưu secret key vào user profile
            request.user.two_factor_secret = secret_key
            request.user.has_2fa = True
            request.user.two_factor_method = 'google'  # Sửa thành 'google' thay vì 'google_authenticator'
            request.user.save()
            
            # Debug log
            print(f"Saved 2FA settings: method={request.user.two_factor_method}, secret={request.user.two_factor_secret}")
            
            # Xóa secret key tạm thời khỏi session
            del request.session['temp_2fa_secret']
            
            return JsonResponse({
                'success': True,
                'message': 'Xác thực thành công'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Mã OTP không chính xác'
            })
            
    except Exception as e:
        print(f"Error in verify_google_authenticator: {str(e)}")  # Debug log
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@require_POST
def delete_2fa(request):
    try:
        # Xóa thông tin 2FA
        request.user.has_2fa = False
        request.user.two_factor_method = None
        request.user.two_factor_password = None
        request.user.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Đã xóa mật khẩu cấp 2'
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

def get_client_info(request):
    """Lấy thông tin thiết bị và trình duyệt"""
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = user_agents.parse(ua_string)
    
    # Xác định thiết bị
    if user_agent.is_mobile:
        device = "Mobile Device"
        if user_agent.is_tablet:
            device = "Tablet"
    elif user_agent.is_pc:
        device = "Desktop/Laptop"
    else:
        device = "Unknown Device"
            
    # Xác định trình duyệt và phiên bản
    browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
    
    return device, browser

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
    ip_address = request.META.get('REMOTE_ADDR')

    # Kiểm tra xem đã có login history với thông tin giống hệt không
    existing_login = LoginHistory.objects.filter(
        user=user,
        device_info=device,
        browser_info=browser,
        ip_address=ip_address,
        status='confirmed'
    ).first()

    if existing_login:
        # Cập nhật thời gian đăng nhập
        existing_login.login_time = timezone.now()
        existing_login.save()
    else:
        # Tạo mới nếu không tìm thấy
        LoginHistory.objects.create(
            user=user,
            device_info=device,
            browser_info=browser,
            ip_address=ip_address,
            status='pending'
        )