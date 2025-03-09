from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from dashboard.models.conversation import ChatbotConversation
from django.contrib.auth import get_user_model

User = get_user_model()

def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def chat_history(request):
    """Trang quản lý lịch sử trò chuyện"""
    # Lọc theo người dùng
    user_id = request.GET.get('user_id')
    # Lọc theo ngày
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    # Lọc theo từ khóa
    keyword = request.GET.get('keyword')
    
    conversations = ChatbotConversation.objects.all().order_by('-created_at')
    
    # Áp dụng các bộ lọc
    if user_id:
        conversations = conversations.filter(user_id=user_id)
    
    if date_from:
        try:
            date_from = timezone.datetime.strptime(date_from, '%Y-%m-%d')
            conversations = conversations.filter(created_at__gte=date_from)
        except:
            pass
    
    if date_to:
        try:
            date_to = timezone.datetime.strptime(date_to, '%Y-%m-%d')
            date_to = date_to + timedelta(days=1)  # Bao gồm cả ngày kết thúc
            conversations = conversations.filter(created_at__lt=date_to)
        except:
            pass
    
    if keyword:
        conversations = conversations.filter(
            Q(history__icontains=keyword)
        )
    
    # Phân trang
    paginator = Paginator(conversations, 20)  # 20 cuộc trò chuyện mỗi trang
    page = request.GET.get('page', 1)
    conversations_page = paginator.get_page(page)
    
    # Thống kê
    total_conversations = ChatbotConversation.objects.count()
    total_users = ChatbotConversation.objects.values('user_id').distinct().count()
    
    # Danh sách người dùng có trò chuyện
    users_with_chats = User.objects.filter(
        id__in=ChatbotConversation.objects.values_list('user_id', flat=True).distinct()
    )
    
    context = {
        'conversations': conversations_page,
        'total_conversations': total_conversations,
        'total_users': total_users,
        'users': users_with_chats,
        'active_tab': 'chat_history',
        'filters': {
            'user_id': user_id,
            'date_from': date_from,
            'date_to': date_to,
            'keyword': keyword
        }
    }
    
    return render(request, 'dashboard/chat_history.html', context)

@login_required
@user_passes_test(is_admin)
def conversation_detail(request, conversation_id):
    """Xem chi tiết một cuộc trò chuyện"""
    try:
        conversation = ChatbotConversation.objects.get(id=conversation_id)
        
        # Lấy thông tin người dùng nếu có
        user = None
        if conversation.user_id:
            try:
                user = User.objects.get(id=conversation.user_id)
            except User.DoesNotExist:
                pass
        
        context = {
            'conversation': conversation,
            'user': user,
            'active_tab': 'chat_history'
        }
        
        return render(request, 'dashboard/conversation_detail.html', context)
        
    except ChatbotConversation.DoesNotExist:
        return render(request, 'dashboard/error.html', {
            'error_message': 'Cuộc trò chuyện không tồn tại'
        }) 