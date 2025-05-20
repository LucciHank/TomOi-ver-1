from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.utils.text import slugify

from dashboard.models.product_duration import ProductDuration


@staff_member_required
def product_durations(request):
    """Danh sách thời hạn sản phẩm"""
    durations = ProductDuration.objects.all().order_by('display_order', 'days')
    
    context = {
        'durations': durations,
        'title': 'Quản lý thời hạn sản phẩm',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/durations/list.html', context)


@staff_member_required
def add_product_duration(request):
    """Thêm mới thời hạn sản phẩm"""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        value = request.POST.get('value', '')
        days = request.POST.get('days', 0)
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        display_order = request.POST.get('display_order', 0)
        
        # Kiểm tra trường bắt buộc
        if not name or not value or not days:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin bắt buộc')
            return render(request, 'dashboard/products/durations/add.html', {
                'title': 'Thêm thời hạn sản phẩm',
                'active_tab': 'products',
                'name': name,
                'value': value,
                'days': days,
                'description': description,
                'is_active': is_active,
                'display_order': display_order
            })
        
        # Tạo slug tự động
        slug = slugify(name)
        
        # Kiểm tra trùng lặp
        if ProductDuration.objects.filter(slug=slug).exists():
            messages.error(request, f'Thời hạn với slug "{slug}" đã tồn tại. Vui lòng chọn tên khác.')
            return render(request, 'dashboard/products/durations/add.html', {
                'title': 'Thêm thời hạn sản phẩm',
                'active_tab': 'products',
                'name': name,
                'value': value,
                'days': days,
                'description': description,
                'is_active': is_active,
                'display_order': display_order
            })
            
        # Kiểm tra trùng lặp value
        if ProductDuration.objects.filter(value=value).exists():
            messages.error(request, f'Thời hạn với giá trị "{value}" đã tồn tại. Vui lòng chọn giá trị khác.')
            return render(request, 'dashboard/products/durations/add.html', {
                'title': 'Thêm thời hạn sản phẩm',
                'active_tab': 'products',
                'name': name,
                'value': value,
                'days': days,
                'description': description,
                'is_active': is_active,
                'display_order': display_order
            })
        
        # Tạo mới thời hạn
        product_duration = ProductDuration(
            name=name,
            slug=slug,
            value=value,
            days=days,
            description=description,
            is_active=is_active,
            display_order=display_order
        )
        
        try:
            product_duration.save()
            messages.success(request, f'Đã thêm thời hạn sản phẩm "{name}" thành công')
            return redirect('dashboard:product_durations')
        except Exception as e:
            messages.error(request, f'Lỗi khi lưu thời hạn sản phẩm: {str(e)}')
    
    context = {
        'title': 'Thêm thời hạn sản phẩm',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/durations/add.html', context)


@staff_member_required
def edit_product_duration(request, duration_id):
    """Chỉnh sửa thời hạn sản phẩm"""
    product_duration = get_object_or_404(ProductDuration, id=duration_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '')
        value = request.POST.get('value', '')
        days = request.POST.get('days', 0)
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        display_order = request.POST.get('display_order', 0)
        
        # Kiểm tra trường bắt buộc
        if not name or not value or not days:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin bắt buộc')
            return render(request, 'dashboard/products/durations/edit.html', {
                'title': 'Chỉnh sửa thời hạn sản phẩm',
                'active_tab': 'products',
                'duration': product_duration
            })
        
        # Tạo slug mới nếu tên thay đổi
        if name != product_duration.name:
            slug = slugify(name)
            # Kiểm tra trùng lặp
            if ProductDuration.objects.filter(slug=slug).exclude(id=duration_id).exists():
                messages.error(request, f'Thời hạn với slug "{slug}" đã tồn tại. Vui lòng chọn tên khác.')
                return render(request, 'dashboard/products/durations/edit.html', {
                    'title': 'Chỉnh sửa thời hạn sản phẩm',
                    'active_tab': 'products',
                    'duration': product_duration
                })
            product_duration.slug = slug
        
        # Kiểm tra trùng lặp value
        if value != product_duration.value and ProductDuration.objects.filter(value=value).exclude(id=duration_id).exists():
            messages.error(request, f'Thời hạn với giá trị "{value}" đã tồn tại. Vui lòng chọn giá trị khác.')
            return render(request, 'dashboard/products/durations/edit.html', {
                'title': 'Chỉnh sửa thời hạn sản phẩm',
                'active_tab': 'products',
                'duration': product_duration
            })
        
        # Cập nhật thông tin
        product_duration.name = name
        product_duration.value = value
        product_duration.days = days
        product_duration.description = description
        product_duration.is_active = is_active
        product_duration.display_order = display_order
        
        try:
            product_duration.save()
            messages.success(request, f'Đã cập nhật thời hạn sản phẩm "{name}" thành công')
            return redirect('dashboard:product_durations')
        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật thời hạn sản phẩm: {str(e)}')
    
    context = {
        'duration': product_duration,
        'title': f'Chỉnh sửa thời hạn: {product_duration.name}',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/durations/edit.html', context)


@staff_member_required
def delete_product_duration(request, duration_id):
    """Xóa thời hạn sản phẩm"""
    product_duration = get_object_or_404(ProductDuration, id=duration_id)
    
    if request.method == 'POST':
        duration_name = product_duration.name
        product_duration.delete()
        messages.success(request, f'Đã xóa thời hạn sản phẩm "{duration_name}" thành công')
        return redirect('dashboard:product_durations')
    
    context = {
        'duration': product_duration,
        'title': f'Xác nhận xóa thời hạn: {product_duration.name}',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/durations/delete.html', context) 
 
 