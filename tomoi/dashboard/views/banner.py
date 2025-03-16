from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from dashboard.models.banner import Banner
import os
from django.conf import settings

@staff_member_required
def banner_list(request):
    banners = Banner.objects.all().order_by('order', '-created_at')
    
    # Phân trang
    paginator = Paginator(banners, 10)
    page_number = request.GET.get('page', 1)
    banners_page = paginator.get_page(page_number)
    
    context = {
        'banners': banners_page
    }
    return render(request, 'dashboard/banners/list.html', context)

@staff_member_required
def banner_add(request):
    if request.method == 'POST':
        # Xử lý form thêm banner
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        position = request.POST.get('position')
        url = request.POST.get('url', '')
        order = request.POST.get('order', 0)
        is_active = 'is_active' in request.POST
        
        banner = Banner(
            title=title,
            description=description,
            position=position,
            url=url,
            order=order,
            is_active=is_active
        )
        
        if 'image' in request.FILES:
            banner.image = request.FILES['image']
            
        banner.save()
        messages.success(request, f'Đã thêm banner "{title}" thành công')
        return redirect('dashboard:banners')
    
    return render(request, 'dashboard/banners/form.html')

@staff_member_required
def banner_edit(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)
    
    if request.method == 'POST':
        # Xử lý form sửa banner
        banner.title = request.POST.get('title')
        banner.description = request.POST.get('description', '')
        banner.position = request.POST.get('position')
        banner.url = request.POST.get('url', '')
        banner.order = request.POST.get('order', 0)
        banner.is_active = 'is_active' in request.POST
        
        if 'image' in request.FILES:
            # Xóa ảnh cũ nếu có
            if banner.image:
                try:
                    if os.path.isfile(banner.image.path):
                        os.remove(banner.image.path)
                except:
                    pass
            banner.image = request.FILES['image']
            
        banner.save()
        messages.success(request, f'Đã cập nhật banner "{banner.title}" thành công')
        return redirect('dashboard:banners')
    
    context = {
        'banner': banner
    }
    return render(request, 'dashboard/banners/form.html', context)

@staff_member_required
def banner_delete(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)
    
    # Xóa ảnh trước khi xóa banner
    if banner.image:
        try:
            if os.path.isfile(banner.image.path):
                os.remove(banner.image.path)
        except:
            pass
    
    title = banner.title
    banner.delete()
    messages.success(request, f'Đã xóa banner "{title}" thành công')
    return redirect('dashboard:banners')

@staff_member_required
def toggle_banner(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)
    banner.is_active = not banner.is_active
    banner.save()
    
    status = "kích hoạt" if banner.is_active else "tạm ngưng"
    messages.success(request, f'Đã {status} banner "{banner.title}"')
    return redirect('dashboard:banners')

@staff_member_required
def upload_banner_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES.get('image')
        # Lưu ảnh vào thư mục tạm
        from django.core.files.storage import default_storage
        filename = default_storage.save(f'banners/temp/{image.name}', image)
        file_url = default_storage.url(filename)
        
        return JsonResponse({'success': True, 'url': file_url})
    return JsonResponse({'success': False, 'error': 'Không có file được tải lên'})

# Thêm các view khác...
