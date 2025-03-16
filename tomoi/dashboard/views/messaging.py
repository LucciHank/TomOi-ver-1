from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator

@staff_member_required
def messaging(request):
    """Hiển thị trang quản lý tin nhắn"""
    context = {
        'title': 'Quản lý tin nhắn',
        'page': 'inbox'
    }
    return render(request, 'dashboard/messaging/index.html', context)

@staff_member_required
def inbox(request):
    """Hiển thị hộp thư đến"""
    context = {
        'title': 'Hộp thư đến',
        'page': 'inbox'
    }
    return render(request, 'dashboard/messaging/inbox.html', context)

@staff_member_required
def send_message(request):
    """Gửi tin nhắn mới"""
    if request.method == 'POST':
        # Xử lý gửi tin nhắn
        recipient_id = request.POST.get('recipient_id')
        content = request.POST.get('content')
        
        if not recipient_id or not content:
            messages.error(request, 'Vui lòng cung cấp người nhận và nội dung tin nhắn')
            return redirect('dashboard:messaging')
        
        # TODO: Lưu tin nhắn vào cơ sở dữ liệu
        
        messages.success(request, 'Đã gửi tin nhắn thành công')
        return redirect('dashboard:messaging')
    
    # Hiển thị form gửi tin nhắn
    context = {
        'title': 'Gửi tin nhắn mới',
        'page': 'send'
    }
    return render(request, 'dashboard/messaging/send.html', context)

@staff_member_required
def view_conversation(request, conversation_id):
    """Xem cuộc trò chuyện cụ thể"""
    # TODO: Lấy chi tiết cuộc trò chuyện
    
    context = {
        'title': 'Chi tiết cuộc trò chuyện',
        'page': 'conversation'
    }
    return render(request, 'dashboard/messaging/conversation.html', context)

@staff_member_required
def mark_as_read(request, message_id):
    """Đánh dấu tin nhắn đã đọc"""
    if request.method == 'POST':
        # TODO: Cập nhật trạng thái tin nhắn
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=405) 