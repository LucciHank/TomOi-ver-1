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
from django.views.decorators.csrf import csrf_exempt
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
from django.views.decorators.http import require_POST

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
@require_POST
def update_profile(request):
    try:
        user = request.user
        
        # Cập nhật avatar nếu có
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            
        # Cập nhật các thông tin khác
        full_name = request.POST.get('full_name', '')
        name_parts = full_name.split(maxsplit=1)
        user.first_name = name_parts[0] if name_parts else ''
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        user.phone_number = request.POST.get('phone_number', '')
        user.email = request.POST.get('email', '')
        user.username = request.POST.get('username', '')
        
        # Xử lý ngày sinh
        try:
            day = int(request.POST.get('birth_day', 0))
            month = int(request.POST.get('birth_month', 0))
            year = int(request.POST.get('birth_year', 0))
            if all([day, month, year]):
                from datetime import date
                user.birth_date = date(year, month, day)
        except (ValueError, TypeError):
            pass
            
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Cập nhật thông tin thành công'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

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

@csrf_exempt
def verify_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            otp_entered = data.get('otp')
            otp_stored = request.session.get('otp')
            email = request.session.get('otp_email')

            if not otp_stored or not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Phiên làm việc đã hết hạn. Vui lòng yêu cầu OTP mới.'
                })

            if str(otp_entered) == str(otp_stored):
                # Xóa OTP đã sử dụng
                del request.session['otp']
                return JsonResponse({
                    'success': True,
                    'message': 'Xác thực OTP thành công.'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Mã OTP không chính xác. Vui lòng thử lại.'
                })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Dữ liệu không hợp lệ.'
            })
        except Exception as e:
            print(f"Error in verify_otp: {str(e)}")  # Debug log
            return JsonResponse({
                'success': False,
                'message': f'Có lỗi xảy ra: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'message': 'Phương thức không được hỗ trợ.'
    })

def unauthorized_view(request):
    return JsonResponse({'error': 'Login required'}, status=401)

@login_required
def user_info(request):
    user = request.user
    context = {
        'user_profile': {
            'profile_picture': {
                'url': user.avatar.url if user.avatar else '/static/images/default-avatar.png'
            },
            'full_name': user.get_full_name() or user.username,
            'phone_number': user.phone_number or 'Chưa cập nhật',
            'gender': user.gender if hasattr(user, 'gender') else 'Chưa cập nhật',
        }
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
