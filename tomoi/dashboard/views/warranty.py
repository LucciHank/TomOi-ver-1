from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def warranty_list(request):
    """View danh sách bảo hành sản phẩm"""
    context = {
        'title': 'Quản lý bảo hành',
    }
    return render(request, 'dashboard/warranty/list.html', context) 