from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def messaging_view(request):
    """View quản lý tin nhắn giữa admin và người dùng"""
    context = {
        'title': 'Quản lý tin nhắn',
    }
    return render(request, 'dashboard/messaging/index.html', context) 