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
from django.http import JsonResponse
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
from .models import Order, Transaction  # Thêm import này ở đầu file
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
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Email đã tồn tại!',
                    'action': 'login'
                })
            
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

# Login view
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')  # Lấy giá trị của checkbox
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if remember_me:
                request.session.set_expiry(1209600)  # 14 ngày
            else:
                request.session.set_expiry(0)  # Hết khi đóng trình duyệt
            return redirect('profile')
        else:
            return render(request, 'accounts/login.html', {'error': 'Tên đăng nhập hoặc mật khẩu không chính xác.'})
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

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Đăng nhập thành công!')
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Invalid credentials'})
    return JsonResponse({'success': False, 'error': 'Invalid method'})

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
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Email đã tồn tại!',
                    'action': 'login'
                })
            
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
                    'message': 'Email không tồn tại! <a href="#" class="register-link" data-bs-toggle="modal" data-bs-target="#registerModal">Đăng ký ngay</a>',
                    'code': 'EMAIL_NOT_FOUND'
                })

            otp = random.randint(100000, 999999)
            request.session['otp'] = str(otp)
            request.session['otp_email'] = email

            send_mail(
                'Mã xác thực OTP',
                f'Mã OTP của bạn là: {otp}',
                'tomoivn2024@gmail.com',
                [email],
                fail_silently=False,
            )

            return JsonResponse({
                'success': True,
                'message': 'OTP đã được gửi qua email.'
            })
        except ValidationError:
            return JsonResponse({
                'success': False,
                'message': 'Địa chỉ email không hợp lệ.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Có lỗi xảy ra: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'message': 'Phương thức không hợp lệ.'
    })

@csrf_exempt
def resend_otp(request):
    # Hàm này có thể giống send_otp hoặc có logic khác nếu cần
    return send_otp(request)

@login_required
@require_http_methods(["POST"])
def verify_otp(request):
    try:
        data = json.loads(request.body)
        otp = data.get('otp')
        stored_otp = request.session.get('email_otp', {})
        
        # Kiểm tra OTP có tồn tại và còn hạn không
        if not stored_otp:
            return JsonResponse({
                'status': 'error',
                'message': 'OTP không tồn tại hoặc đã hết hạn'
            }, status=400)
            
        if float(stored_otp['expires']) < timezone.now().timestamp():
            del request.session['email_otp']
            return JsonResponse({
                'status': 'error',
                'message': 'OTP đã hết hạn'
            }, status=400)
            
        if otp != stored_otp['code']:
            return JsonResponse({
                'status': 'error',
                'message': 'Mã OTP không chính xác'
            }, status=400)
            
        # OTP hợp lệ
        del request.session['email_otp']
        request.user.two_factor_method = 'email'
        request.user.has_2fa = True
        request.user.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Xác thực thành công'
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
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'accounts/payment_history.html', {
        'transactions': transactions
    })

@login_required
def order_history(request):
    # Lấy cả đơn hàng từ accounts và store
    account_orders = Order.objects.filter(user=request.user).order_by('-date')
    store_orders = request.user.store_orders.all().order_by('-created_at')
    
    # Kết hợp và sắp xếp theo thời gian
    orders = sorted(
        list(account_orders) + list(store_orders),
        key=lambda x: x.date if hasattr(x, 'date') else x.created_at,
        reverse=True
    )
    
    return render(request, 'accounts/order_history.html', {
        'orders': orders
    })

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
