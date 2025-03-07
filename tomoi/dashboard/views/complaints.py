from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def complaints_list(request):
    """View danh sách khiếu nại từ người dùng"""
    context = {
        'title': 'Quản lý khiếu nại',
    }
    return render(request, 'dashboard/complaints/list.html', context) 