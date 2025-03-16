from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from dashboard.models import ChatbotConversation
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

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
    
    conversations = ChatbotConversation.objects.all().order_by('-updated_at')
    
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
            Q(conversation_data__icontains=keyword)
        )
    
    # Phân trang
    paginator = Paginator(conversations, 10)  # 10 cuộc trò chuyện mỗi trang
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Thống kê
    total_conversations = ChatbotConversation.objects.count()
    total_users = ChatbotConversation.objects.values('user_id').distinct().count()
    
    # Danh sách người dùng có trò chuyện
    users_with_chats = User.objects.filter(
        id__in=ChatbotConversation.objects.values_list('user_id', flat=True).distinct()
    )
    
    context = {
        'page_obj': page_obj,
        'title': 'Lịch sử cuộc trò chuyện',
        'section': 'chat_history',
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
    
    return render(request, 'dashboard/chat_history/list.html', context)

@login_required
@user_passes_test(is_admin)
def conversation_detail(request, conversation_id):
    """Xem chi tiết một cuộc trò chuyện"""
    conversation = get_object_or_404(ChatbotConversation, id=conversation_id)
    
    # Load dữ liệu cuộc trò chuyện từ JSON
    try:
        conversation_data = conversation.conversation_data
        if isinstance(conversation_data, str):
            conversation_data = json.loads(conversation_data)
    except Exception as e:
        conversation_data = {"error": str(e)}
    
    context = {
        'conversation': conversation,
        'conversation_data': conversation_data,
        'title': f'Chi tiết cuộc trò chuyện #{conversation_id}',
        'section': 'chat_history',
        'active_tab': 'chat_history'
    }
    
    return render(request, 'dashboard/chat_history/detail.html', context)

@csrf_exempt
@require_POST
def chatbot_log_api(request):
    """API endpoint để lưu lịch sử chat từ chatbot gửi lên"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        user_message = data.get('user_message', '')
        bot_response = data.get('bot_response', '')
        metadata = data.get('metadata', '{}')
        
        # Tạo conversation_data để lưu vào model
        conversation_data = {
            'messages': [
                {'role': 'user', 'content': user_message},
                {'role': 'assistant', 'content': bot_response}
            ],
            'metadata': metadata
        }
        
        # Kiểm tra nếu đã có session_id này trong DB
        try:
            conversation = ChatbotConversation.objects.get(session_id=session_id)
            # Cập nhật thêm tin nhắn mới vào cuộc trò chuyện
            existing_data = conversation.conversation_data
            if isinstance(existing_data, str):
                existing_data = json.loads(existing_data)
            
            # Thêm tin nhắn mới vào danh sách messages
            if 'messages' in existing_data:
                existing_data['messages'].extend(conversation_data['messages'])
            else:
                existing_data['messages'] = conversation_data['messages']
            
            # Cập nhật metadata
            existing_data['metadata'] = metadata
            
            # Lưu lại vào DB
            conversation.conversation_data = existing_data
            conversation.updated_at = timezone.now()
            conversation.save()
            
        except ChatbotConversation.DoesNotExist:
            # Tạo mới nếu chưa có
            conversation = ChatbotConversation.objects.create(
                session_id=session_id,
                conversation_data=conversation_data,
                user=request.user if request.user.is_authenticated else None
            )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Đã lưu lịch sử chat thành công',
            'conversation_id': conversation.id
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Lỗi khi lưu lịch sử chat: {str(e)}'
        }, status=500) 