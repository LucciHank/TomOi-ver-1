import re
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from .models import PageView, VisitorSession, DailyAnalytics, PageAnalytics, ReferrerAnalytics, APIKey, APILog
from user_agents import parse
from urllib.parse import urlparse
import uuid
import json
from django.http import JsonResponse
from django.core.cache import cache
import hmac
import hashlib
from django.conf import settings
from .models.base import PageView
from datetime import timedelta
from django.urls import resolve
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

class AnalyticsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Bỏ qua các request static files và admin
        if any(pattern.match(request.path) for pattern in [
            re.compile(r'^/static/'),
            re.compile(r'^/media/'),
            re.compile(r'^/admin/'),
            re.compile(r'^/api/'),
        ]):
            return None
            
        # Lưu lượt xem trang đơn giản
        try:
            if request.user.is_authenticated:
                PageView.objects.create(
                    url=request.path,
                    title=request.path,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    referrer=request.META.get('HTTP_REFERER', ''),
                    user=request.user
                )
        except Exception as e:
            # Log lỗi nhưng không làm gián đoạn request
            print(f"Error in analytics tracking: {str(e)}")
            
        return None
        
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
        
    def process_response(self, request, response):
        if hasattr(request, 'session') and 'analytics_session_id' in request.session:
            session = VisitorSession.objects.filter(
                session_id=request.session['analytics_session_id']
            ).first()
            
            if session:
                session.end_time = timezone.now()
                session.duration = session.end_time - session.start_time
                session.save()
                
        return response
        
    def get_page_title(self, request):
        # Implement logic to get page title
        return request.path
        
    def get_traffic_source(self, referrer):
        if not referrer:
            return 'direct'
            
        domain = urlparse(referrer).netloc.lower()
        
        search_engines = ['google', 'bing', 'yahoo']
        social_media = ['facebook', 'twitter', 'instagram', 'linkedin']
        
        if any(engine in domain for engine in search_engines):
            return 'organic'
        elif any(social in domain for social in social_media):
            return 'social'
        elif 'email' in domain or 'mail' in domain:
            return 'email'
        elif 'ad' in domain or 'ads' in domain:
            return 'paid'
        else:
            return 'referral'

class APILoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Chỉ log các request đến API endpoints
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        # Lấy API key từ header
        api_key = request.headers.get('X-API-Key')
        
        # Kiểm tra API key
        if api_key:
            try:
                api_key_obj = APIKey.objects.get(key=api_key, is_active=True)
            except APIKey.DoesNotExist:
                return JsonResponse({'error': 'Invalid API key'}, status=401)

            # Lưu request data
            try:
                request_data = json.loads(request.body) if request.body else None
            except json.JSONDecodeError:
                request_data = None

            start_time = timezone.now()
            response = self.get_response(request)
            end_time = timezone.now()

            # Tính thời gian xử lý
            response_time = (end_time - start_time).total_seconds() * 1000  # ms

            # Lưu response data
            try:
                response_data = json.loads(response.content) if response.content else None
            except json.JSONDecodeError:
                response_data = None

            # Tạo log
            APILog.objects.create(
                api_key=api_key_obj,
                endpoint=request.path,
                method=request.method,
                request_data=request_data,
                response_data=response_data,
                status_code=response.status_code,
                ip_address=request.META.get('REMOTE_ADDR'),
                response_time=response_time
            )

            # Cập nhật last_used cho API key
            api_key_obj.last_used = timezone.now()
            api_key_obj.save()

            return response
        else:
            # Nếu không có API key, chỉ trả về response mà không log
            return self.get_response(request)

class APIRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 100  # requests per minute
        self.window = 60  # seconds

    def __call__(self, request):
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return self.get_response(request)

        cache_key = f'rate_limit_{api_key}'
        requests = cache.get(cache_key, [])
        now = timezone.now()

        # Xóa các request cũ hơn window
        requests = [req for req in requests if (now - req).total_seconds() < self.window]

        if len(requests) >= self.rate_limit:
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'retry_after': self.window - (now - requests[0]).total_seconds()
            }, status=429)

        requests.append(now)
        cache.set(cache_key, requests, self.window)

        return self.get_response(request) 

class APISecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        # Kiểm tra signature
        signature = request.headers.get('X-API-Signature')
        timestamp = request.headers.get('X-Timestamp')
        
        if not all([signature, timestamp]):
            return JsonResponse({'error': 'Missing security headers'}, status=401)

        # Tạo signature để so sánh
        message = f"{request.path}{timestamp}{request.body.decode()}"
        expected_signature = hmac.new(
            settings.API_SIGNING_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            return JsonResponse({'error': 'Invalid signature'}, status=401)

        # Kiểm tra timestamp để tránh replay attack
        now = timezone.now().timestamp()
        if abs(float(timestamp) - now) > 300:  # 5 minutes
            return JsonResponse({'error': 'Request expired'}, status=401)

        return self.get_response(request) 

class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Xử lý request
        response = self.get_response(request)
        return response

    def process_request(self, request):
        # Vô hiệu hóa chức năng tracking tạm thời
        return None 

class APIAuthMiddleware:
    """Middleware kiểm tra xác thực API key cho các request API"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Kiểm tra xem yêu cầu có phải API không
        if request.path.startswith('/api/'):
            # Kiểm tra và xác thực API key
            api_key = request.headers.get('X-API-Key')

            # Nếu API key không được cung cấp, cho phép truy cập vào /api/cart/ không cần xác thực
            if request.path.startswith('/api/cart/') and not api_key:
                return self.get_response(request)

            # Nếu API key được cung cấp, kiểm tra tính hợp lệ
            if api_key:
                try:
                    api_key_obj = APIKey.objects.get(key=api_key, is_active=True)

                    # Gắn thông tin API key cho request
                    request.api_key = api_key_obj
                    
                    # Đặt flag API request
                    request.is_api_request = True

                    # Tiếp tục xử lý request
                    return self.get_response(request)
                except APIKey.DoesNotExist:
                    # API key không hợp lệ
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid API key'
                    }, status=401)
            else:
                # Không cung cấp API key cho các endpoint API khác
                return JsonResponse({
                    'success': False,
                    'message': 'API key required'
                }, status=401)
        
        # Nếu không phải API request, xử lý như bình thường
        return self.get_response(request)

class SubscriptionExpiryMiddleware:
    """
    Middleware kiểm tra và cập nhật trạng thái các gói đăng ký hết hạn
    mỗi khi có request đến dashboard
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Chỉ xử lý các request đến dashboard và từ admin
        if request.path.startswith('/dashboard/') and request.user.is_authenticated and request.user.is_staff:
            try:
                # Import ở đây để tránh circular import
                from dashboard.models import UserSubscription
                
                # Kiểm tra các gói hết hạn
                today = timezone.now()
                grace_period = 7  # Số ngày ân hạn
                grace_date = today - timedelta(days=grace_period)
                
                # Tìm các gói hết hạn cần cập nhật
                expired_subscriptions = UserSubscription.objects.filter(
                    end_date__lt=grace_date,
                    status='active'
                )
                
                # Cập nhật trạng thái
                count = expired_subscriptions.count()
                if count > 0:
                    expired_subscriptions.update(status='expired')
                    # Lưu thông báo vào session để hiển thị
                    # (chỉ hiển thị thông báo ở trang đầu tiên được truy cập)
                    if request.session.get('subscription_updated_shown') != today.strftime('%Y-%m-%d'):
                        messages.info(request, f'Hệ thống đã tự động cập nhật {count} gói hết hạn.')
                        request.session['subscription_updated_shown'] = today.strftime('%Y-%m-%d')
                        
            except Exception as e:
                logger.error(f"Lỗi khi kiểm tra gói hết hạn: {str(e)}")
        
        response = self.get_response(request)
        return response 