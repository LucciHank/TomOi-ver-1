from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Q, Max, Count, F, Exists, OuterRef
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import os
from datetime import datetime
from ..models.conversation import Conversation, Message, UserNotification

User = get_user_model()

def is_admin(user):
    """Kiểm tra user có phải là admin hoặc staff không"""
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_chat_dashboard(request):
    """Trang dashboard quản lý tin nhắn"""
    # Lấy tất cả các cuộc trò chuyện mà admin này đã tham gia
    conversations = Conversation.objects.filter(
        Q(admin=request.user) | Q(admin__isnull=True)
    ).annotate(
        unread_count=Count('messages', filter=Q(messages__is_read=False, messages__receiver=request.user))
    ).order_by('-last_message_time')
    
    # Lấy tổng số tin nhắn chưa đọc
    total_unread = sum(conv.unread_count for conv in conversations)
    
    # Lấy người dùng được chọn và tin nhắn (nếu có)
    user_id = request.GET.get('user_id')
    selected_user = None
    messages_list = []
    selected_conversation = None
    
    if user_id:
        selected_user = get_object_or_404(User, id=user_id)
        
        # Kiểm tra xem đã có hội thoại chưa
        selected_conversation, created = Conversation.objects.get_or_create(
            admin=request.user,
            user=selected_user,
            defaults={'last_message_time': timezone.now()}
        )
        
        # Lấy tin nhắn
        messages_list = Message.objects.filter(conversation=selected_conversation).order_by('sent_at')
        
        # Đánh dấu các tin nhắn đã đọc (chỉ những tin nhắn mà admin nhận được)
        unread_messages = messages_list.filter(receiver=request.user, is_read=False)
        for msg in unread_messages:
            msg.mark_as_read()
    
    # Tìm kiếm người dùng (nếu có)
    search_query = request.GET.get('search', '')
    users = []
    
    if search_query:
        users = User.objects.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        ).exclude(is_staff=True).exclude(is_superuser=True)[:20]
    
    context = {
        'conversations': conversations,
        'total_unread': total_unread,
        'selected_user': selected_user,
        'messages': messages_list,
        'selected_conversation': selected_conversation,
        'search_query': search_query,
        'users': users,
    }
    
    return render(request, 'dashboard/chat/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def send_message(request):
    """API gửi tin nhắn từ admin đến người dùng"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ'}, status=400)
    
    # Lấy dữ liệu
    user_id = request.POST.get('user_id')
    message_content = request.POST.get('message')
    message_type = request.POST.get('message_type', 'text')
    order_id = request.POST.get('order_id')
    
    if not user_id or not message_content:
        return JsonResponse({'status': 'error', 'message': 'Thiếu thông tin người dùng hoặc nội dung tin nhắn'}, status=400)
    
    # Lấy user
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy người dùng'}, status=404)
    
    # Lấy cuộc trò chuyện, nếu chưa có thì tạo mới
    conversation, created = Conversation.objects.get_or_create(
        admin=request.user,
        user=user,
        defaults={'last_message_time': timezone.now()}
    )
    
    # Chuẩn bị dữ liệu đơn hàng nếu có
    order_data = None
    if message_type == 'order' and order_id:
        from store.models import Order
        try:
            order = Order.objects.get(id=order_id)
            order_data = {
                'id': order.id,
                'code': order.code,
                'total': str(order.total),
                'status': order.status,
                'created_at': order.created_at.strftime('%d/%m/%Y %H:%M')
            }
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Không tìm thấy đơn hàng'}, status=404)
    
    # Xử lý ảnh nếu có
    image_url = None
    if message_type == 'image' and request.FILES.get('image'):
        image = request.FILES['image']
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        
        # Tạo thư mục lưu trữ nếu chưa tồn tại
        upload_path = f'chat_images/{datetime.now().strftime("%Y/%m/%d")}/'
        if not os.path.exists(f'media/{upload_path}'):
            os.makedirs(f'media/{upload_path}', exist_ok=True)
        
        # Lưu file
        file_path = f'{upload_path}{image.name}'
        path = default_storage.save(file_path, ContentFile(image.read()))
        image_url = default_storage.url(path)
        
        # Cập nhật nội dung tin nhắn với URL ảnh
        message_content = image_url
    
    # Tạo tin nhắn mới
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        receiver=user,
        message_type=message_type,
        content=message_content,
        order_data=order_data
    )
    
    # Cập nhật thời gian tin nhắn cuối cùng
    conversation.last_message_time = timezone.now()
    conversation.save()
    
    # Tạo thông báo cho người dùng
    UserNotification.objects.create(
        user=user,
        message=message
    )
    
    # Trả về thông tin tin nhắn
    return JsonResponse({
        'status': 'success',
        'message': {
            'id': message.id,
            'content': message.content,
            'type': message.message_type,
            'sent_at': message.sent_at.strftime('%H:%M'),
            'is_admin': True,
            'order_data': order_data
        }
    })

@login_required
def user_chat_dashboard(request):
    """Trang chat cho người dùng"""
    # Lấy cuộc trò chuyện của người dùng với admin
    conversations = Conversation.objects.filter(user=request.user).order_by('-last_message_time')
    
    # Nếu chưa có cuộc trò chuyện nào, tạo mới với admin mặc định
    if not conversations.exists():
        # Lấy admin mặc định (ví dụ: superuser đầu tiên)
        try:
            default_admin = User.objects.filter(is_superuser=True).first()
            if default_admin:
                conversation = Conversation.objects.create(
                    admin=default_admin,
                    user=request.user,
                    last_message_time=timezone.now()
                )
                conversations = [conversation]
            else:
                # Không có admin, tạo cuộc trò chuyện không có admin
                conversation = Conversation.objects.create(
                    user=request.user,
                    last_message_time=timezone.now()
                )
                conversations = [conversation]
        except Exception as e:
            # Ghi log lỗi
            print(f"Error creating default conversation: {str(e)}")
            conversations = []
    
    # Lấy tin nhắn của cuộc trò chuyện đầu tiên (hoặc được chọn)
    conversation_id = request.GET.get('conversation_id')
    if conversation_id:
        selected_conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    else:
        selected_conversation = conversations.first() if conversations else None
    
    messages_list = []
    if selected_conversation:
        messages_list = Message.objects.filter(conversation=selected_conversation).order_by('sent_at')
        
        # Đánh dấu tin nhắn đã đọc
        unread_messages = messages_list.filter(receiver=request.user, is_read=False)
        for msg in unread_messages:
            msg.mark_as_read()
    
    # Lấy tổng số tin nhắn chưa đọc
    unread_count = Message.objects.filter(
        conversation__user=request.user,
        receiver=request.user,
        is_read=False
    ).count()
    
    context = {
        'conversations': conversations,
        'selected_conversation': selected_conversation,
        'messages': messages_list,
        'unread_count': unread_count
    }
    
    return render(request, 'store/chat/dashboard.html', context)

@login_required
def user_send_message(request):
    """API gửi tin nhắn từ người dùng đến admin"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ'}, status=400)
    
    # Lấy dữ liệu
    conversation_id = request.POST.get('conversation_id')
    message_content = request.POST.get('message')
    message_type = request.POST.get('message_type', 'text')
    
    if not conversation_id or not message_content:
        return JsonResponse({'status': 'error', 'message': 'Thiếu thông tin cuộc trò chuyện hoặc nội dung tin nhắn'}, status=400)
    
    # Lấy cuộc trò chuyện
    try:
        conversation = Conversation.objects.get(id=conversation_id, user=request.user)
    except Conversation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy cuộc trò chuyện'}, status=404)
    
    # Xử lý ảnh nếu có
    image_url = None
    if message_type == 'image' and request.FILES.get('image'):
        image = request.FILES['image']
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        
        # Tạo thư mục lưu trữ nếu chưa tồn tại
        upload_path = f'chat_images/{datetime.now().strftime("%Y/%m/%d")}/'
        if not os.path.exists(f'media/{upload_path}'):
            os.makedirs(f'media/{upload_path}', exist_ok=True)
        
        # Lưu file
        file_path = f'{upload_path}{image.name}'
        path = default_storage.save(file_path, ContentFile(image.read()))
        image_url = default_storage.url(path)
        
        # Cập nhật nội dung tin nhắn với URL ảnh
        message_content = image_url
    
    # Nếu không có admin được chỉ định, lấy superuser đầu tiên
    admin = conversation.admin
    if not admin:
        admin = User.objects.filter(is_superuser=True).first()
        if admin:
            conversation.admin = admin
            conversation.save()
        else:
            return JsonResponse({'status': 'error', 'message': 'Không tìm thấy admin để gửi tin nhắn'}, status=400)
    
    # Tạo tin nhắn mới
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        receiver=admin,
        message_type=message_type,
        content=message_content
    )
    
    # Cập nhật thời gian tin nhắn cuối cùng
    conversation.last_message_time = timezone.now()
    conversation.save()
    
    # Tạo thông báo cho admin
    UserNotification.objects.create(
        user=admin,
        message=message
    )
    
    # Trả về thông tin tin nhắn
    return JsonResponse({
        'status': 'success',
        'message': {
            'id': message.id,
            'content': message.content,
            'type': message.message_type,
            'sent_at': message.sent_at.strftime('%H:%M'),
            'is_admin': False
        }
    })

@require_POST
@csrf_exempt
def update_read_status(request):
    """API cập nhật trạng thái đã đọc tin nhắn"""
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        
        message = get_object_or_404(Message, id=message_id, receiver=request.user)
        message.mark_as_read()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def get_unread_count(request):
    """API lấy số lượng tin nhắn chưa đọc"""
    if request.user.is_staff or request.user.is_superuser:
        # Đối với admin, lấy tổng số tin nhắn chưa đọc từ tất cả người dùng
        unread_count = Message.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()
    else:
        # Đối với người dùng thông thường
        unread_count = Message.objects.filter(
            conversation__user=request.user,
            receiver=request.user,
            is_read=False
        ).count()
    
    return JsonResponse({'unread_count': unread_count})

@login_required
@user_passes_test(is_admin)
def user_chat_history(request, user_id):
    """Xem lịch sử chat với một người dùng cụ thể"""
    user = get_object_or_404(User, id=user_id)
    
    # Lấy cuộc trò chuyện
    conversation = get_object_or_404(Conversation, admin=request.user, user=user)
    
    # Lấy tin nhắn
    messages_list = Message.objects.filter(conversation=conversation).order_by('sent_at')
    
    # Đánh dấu đã đọc các tin nhắn chưa đọc
    unread_messages = messages_list.filter(receiver=request.user, is_read=False)
    for msg in unread_messages:
        msg.mark_as_read()
    
    context = {
        'user': user,
        'conversation': conversation,
        'messages': messages_list
    }
    
    return render(request, 'dashboard/chat/user_chat_history.html', context) 