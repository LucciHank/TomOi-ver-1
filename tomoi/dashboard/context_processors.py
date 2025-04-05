from django.db.models import Count, Q
from django.utils import timezone
from dashboard.models.conversation import Message

def dashboard_settings(request):
    """
    Thêm cài đặt dashboard vào context
    """
    return {
        'use_new_sidebar': True
    }

def admin_chat_stats(request):
    """Context processor để lấy thông tin chat cho admin"""
    context = {}
    
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        # Tổng số tin nhắn chưa đọc của admin
        total_unread = Message.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()
        
        context['total_unread'] = total_unread
    
    return context 