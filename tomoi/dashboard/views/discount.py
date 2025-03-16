from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def discount_list(request):
    return render(request, 'dashboard/discounts/list.html')

@staff_member_required
def discount_add(request):
    return render(request, 'dashboard/discounts/form.html')

@staff_member_required
def discount_edit(request, discount_id):
    return render(request, 'dashboard/discounts/form.html')

@staff_member_required
def discount_delete(request, discount_id):
    # Xóa mã giảm giá
    messages.success(request, 'Đã xóa mã giảm giá thành công')
    return redirect('dashboard:discounts')

@staff_member_required
def toggle_discount(request, discount_id):
    # Bật/tắt trạng thái mã giảm giá
    messages.success(request, 'Đã thay đổi trạng thái mã giảm giá')
    return redirect('dashboard:discounts')

@staff_member_required
def discount_report(request):
    # Báo cáo mã giảm giá
    return render(request, 'dashboard/discounts/report.html')

# Thêm các view khác...
