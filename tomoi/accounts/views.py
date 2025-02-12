from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
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
from accounts.models import CustomUser
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
from .models import Order  # Import Order từ accounts.models
from payment.models import Transaction  # Import Transaction từ payment.models
from store.models import Wishlist, Category  # Import Wishlist và Category từ store.models
import pyotp
import qrcode
import base64
from io import BytesIO
from django.contrib.auth.hashers import check_password
import time
from django.utils import timezone
import hashlib
from .utils import mask_email
from django.core.cache import cache
from django.utils import translation
from django.db.models import Q
import requests

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
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            # Tìm user theo username hoặc email
            if '@' in username:
                user = CustomUser.objects.get(email=username)
            else:
                user = CustomUser.objects.get(username=username)

            # Kiểm tra trạng thái tài khoản TRƯỚC
            if user.status == 'suspended':
                return JsonResponse({
                    'success': False,
                    'action': 'suspended',
                    'message': 'Tài khoản đã bị đình chỉ',
                    'reason': user.suspension_reason or 'Không có lý do được cung cấp'
                })
                
            # Sau đó mới kiểm tra mật khẩu
            if user.check_password(password):
                # Đăng nhập user
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                
                # Nếu đang chờ xác minh, chuyển đến trang xác thực
                if user.status == 'pending':
                    return JsonResponse({
                        'success': True,
                        'redirect': reverse('accounts:register_verify')
                    })
                    
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
            
    return JsonResponse({
        'success': False,
        'message': 'Phương thức không hợp lệ'
    })

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
        
        # Lấy thông tin OTP từ session
        otp_info = request.session.get('reset_password_otp')
        if not otp_info:
            return JsonResponse({
                'success': False,
                'message': 'OTP đã hết hạn hoặc không tồn tại'
            })
            
        if otp != otp_info['otp']:
            return JsonResponse({
                'success': False,
                'message': 'Mã OTP không chính xác'
            })
            
        # Xóa OTP khỏi session sau khi xác thực thành công
        del request.session['reset_password_otp']
        
        return JsonResponse({
            'success': True,
            'message': 'Xác thực thành công'
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
    context = {
        'user': request.user,
        'active_tab': 'security'  # Thêm để đánh dấu tab đang active
    }
    return render(request, 'accounts/security.html', context)

@login_required
@require_http_methods(["POST"])
def change_password(request):
    current_password = request.POST.get('current_password')
    new_password = request.POST.get('new_password')
    confirm_password = request.POST.get('confirm_password')
    
    # Validate current password
    if not request.user.check_password(current_password):
        return JsonResponse({
            'status': 'error',
            'message': 'Mật khẩu hiện tại không đúng'
        })
    
    # Validate new password
    if new_password != confirm_password:
        return JsonResponse({
            'status': 'error',
            'message': 'Mật khẩu mới không khớp'
        })
    
    # Change password
    request.user.set_password(new_password)
    request.user.save()
    
    return JsonResponse({
        'status': 'success',
        'message': 'Đổi mật khẩu thành công'
    })

@login_required
@require_http_methods(["POST"])
def setup_2fa(request):
    try:
        data = json.loads(request.body)
        method = data.get('method')
        
        if not method:
            return JsonResponse({
                'status': 'error',
                'message': 'Vui lòng chọn phương thức xác thực'
            }, status=400)

        # Cập nhật thông tin user
        request.user.has_2fa = True
        request.user.two_factor_method = method
        request.user.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Thiết lập mật khẩu cấp 2 thành công'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def send_otp_email(request):
    try:
        # Tạo OTP 6 số
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Lưu OTP vào session
        request.session['email_otp'] = {
            'code': otp,
            'expires': (timezone.now() + timedelta(minutes=5)).timestamp()
        }
        
        # Gửi email
        sent = send_mail(
            subject='Mã xác thực OTP - TomOi.vn',
            message=f'Mã OTP của bạn là: {otp}\nMã này sẽ hết hạn sau 5 phút.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email],
            fail_silently=False,
        )
        
        if not sent:
            return JsonResponse({
                'status': 'error',
                'message': 'Không thể gửi email'
            }, status=500)
            
        return JsonResponse({
            'status': 'success',
            'message': 'Mã OTP đã được gửi đến email của bạn'
        })
            
    except Exception as e:
        print(f"Email error: {str(e)}")  # Log lỗi
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def setup_google_authenticator(request):
    try:
        # Tạo secret key
        secret = pyotp.random_base32()
        
        # Tạo QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=request.user.email,
            issuer_name="TomOi.vn"
        )
        
        # Tạo QR code và chuyển thành base64
        img = qrcode.make(provisioning_uri)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Lưu secret vào session
        request.session['ga_secret'] = secret
        
        return JsonResponse({
            'status': 'success',
            'qr_code': f'data:image/png;base64,{qr_code_base64}',
            'secret': secret
        })
        
    except Exception as e:
        print(f"GA Error: {str(e)}")  # Log lỗi
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def verify_google_authenticator(request):
    try:
        data = json.loads(request.body)
        otp = data.get('otp')
        secret = request.session.get('ga_secret')
        
        if not secret:
            raise Exception('Không tìm thấy secret key')
            
        totp = pyotp.TOTP(secret)
        if totp.verify(otp):
            # Lưu method xác thực cho user
            request.user.two_factor_method = 'google_authenticator'
            request.user.two_factor_secret = secret
            request.user.save()
            
            # Xóa secret khỏi session
            del request.session['ga_secret']
            
            return JsonResponse({
                'status': 'success',
                'message': 'Xác thực thành công'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Mã OTP không chính xác'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def delete_2fa(request):
    if request.method == 'POST':
        try:
            # Xóa các thông tin 2FA
            request.user.has_2fa = False
            request.user.two_factor_method = None
            request.user.two_factor_secret = None
            request.user.require_2fa_purchase = False
            request.user.require_2fa_deposit = False
            request.user.require_2fa_password = False
            request.user.require_2fa_profile = False
            request.user.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Đã xóa mật khẩu cấp 2'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
            
    return JsonResponse({
        'status': 'error',
        'message': 'Phương thức không được hỗ trợ'
    })

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