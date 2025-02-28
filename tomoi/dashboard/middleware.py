import re
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from .models import PageView, VisitorSession, DailyAnalytics, PageAnalytics, ReferrerAnalytics
from user_agents import parse
from urllib.parse import urlparse
import uuid

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
            
        # Lấy hoặc tạo session_id
        session_id = request.session.get('analytics_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['analytics_session_id'] = session_id
            
        # Lấy thông tin thiết bị
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user_agent_info = parse(user_agent)
        
        if user_agent_info.is_mobile:
            device_type = 'mobile'
        elif user_agent_info.is_tablet:
            device_type = 'tablet'
        else:
            device_type = 'desktop'
            
        # Lấy thông tin referrer
        referrer = request.META.get('HTTP_REFERER')
        source = self.get_traffic_source(referrer)
        
        # Lưu thông tin session
        session = VisitorSession.objects.get_or_create(
            session_id=session_id,
            defaults={
                'ip_address': self.get_client_ip(request),
                'user_agent': user_agent,
                'device_type': device_type,
                'referrer': referrer,
                'landing_page': request.path,
                'user': request.user if request.user.is_authenticated else None
            }
        )[0]
        
        # Cập nhật thông tin session
        session.page_views += 1
        session.is_bounce = False if session.page_views > 1 else True
        session.save()
        
        # Lưu lượt xem trang
        PageView.objects.create(
            url=request.path,
            title=self.get_page_title(request),
            ip_address=self.get_client_ip(request),
            user_agent=user_agent,
            referrer=referrer,
            session_id=session_id,
            user=request.user if request.user.is_authenticated else None
        )
        
        # Cập nhật thống kê theo ngày
        today = timezone.now().date()
        daily_stats = DailyAnalytics.objects.get_or_create(date=today)[0]
        daily_stats.page_views += 1
        
        if not VisitorSession.objects.filter(
            start_time__date=today,
            ip_address=self.get_client_ip(request)
        ).exists():
            daily_stats.unique_visitors += 1
            
        daily_stats.save()
        
        # Cập nhật thống kê trang
        page_stats = PageAnalytics.objects.get_or_create(
            url=request.path,
            date=today,
            defaults={'title': self.get_page_title(request)}
        )[0]
        page_stats.views += 1
        page_stats.save()
        
        # Cập nhật thống kê nguồn truy cập
        referrer_stats = ReferrerAnalytics.objects.get_or_create(
            source=source,
            referrer=referrer,
            date=today
        )[0]
        referrer_stats.visits += 1
        referrer_stats.save()
        
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
        
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
        
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