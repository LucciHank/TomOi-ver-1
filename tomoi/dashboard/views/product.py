from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Sum, F
from django.core.paginator import Paginator

from store.models import Product, Category, Brand, ProductLabel
from dashboard.models.product import ProductImage, ProductChangeLog
from dashboard.models.source import SourceProduct

@staff_member_required
def update_product_status(request, product_id):
    """Cập nhật trạng thái sản phẩm (active/inactive)."""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Lấy trạng thái hiện tại để ghi log
        old_status = 'active' if product.is_active else 'inactive'
        
        # Cập nhật trạng thái mới
        product.is_active = not product.is_active
        product.save()
        
        new_status = 'active' if product.is_active else 'inactive'
        
        # Ghi log thay đổi
        ProductChangeLog.objects.create(
            product=product,
            user=request.user,
            action='status_change',
            description=f'Thay đổi trạng thái sản phẩm từ {old_status} thành {new_status}'
        )
        
        return JsonResponse({
            'success': True,
            'is_active': product.is_active,
            'message': f'Sản phẩm đã được {new_status}'
        })
    
    return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ'}, status=405)

@staff_member_required
def manage_product_images(request, product_id):
    """Quản lý ảnh sản phẩm"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # Xử lý thêm ảnh mới
        for image in request.FILES.getlist('images'):
            is_primary = request.POST.get('is_primary') == 'on'
            
            # Nếu đây là ảnh chính, đặt tất cả các ảnh khác thành không phải ảnh chính
            if is_primary:
                ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
            
            ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=is_primary
            )
        
        messages.success(request, 'Đã cập nhật ảnh sản phẩm')
        return redirect('dashboard:edit_product', product_id=product.id)
    
    # Lấy tất cả ảnh hiện tại của sản phẩm
    product_images = ProductImage.objects.filter(product=product)
    
    context = {
        'product': product,
        'product_images': product_images
    }
    
    return render(request, 'dashboard/products/manage_images.html', context)

@staff_member_required
def delete_product_image(request, image_id):
    """Xóa ảnh sản phẩm"""
    image = get_object_or_404(ProductImage, id=image_id)
    product_id = image.product.id
    
    # Xóa ảnh
    image.delete()
    
    messages.success(request, 'Đã xóa ảnh sản phẩm')
    return redirect('dashboard:manage_product_images', product_id=product_id)

@staff_member_required
def set_primary_image(request, image_id):
    """Đặt ảnh chính cho sản phẩm"""
    image = get_object_or_404(ProductImage, id=image_id)
    product = image.product
    
    # Đặt tất cả ảnh về không phải ảnh chính
    ProductImage.objects.filter(product=product).update(is_primary=False)
    
    # Đặt ảnh được chọn là ảnh chính
    image.is_primary = True
    image.save()
    
    messages.success(request, 'Đã đặt ảnh chính mới cho sản phẩm')
    return redirect('dashboard:manage_product_images', product_id=product.id)

@staff_member_required
def product_detail(request, product_id):
    """Chi tiết sản phẩm"""
    product = get_object_or_404(Product, id=product_id)
    
    # Lấy ảnh sản phẩm
    product_images = ProductImage.objects.filter(product=product)
    
    # Lấy biến thể sản phẩm nếu có model này
    variants = []
    try:
        from store.models import ProductVariant
        variants = ProductVariant.objects.filter(product=product)
    except ImportError:
        # Nếu không có model ProductVariant, bỏ qua
        pass
    
    # Lấy nguồn cung cấp liên kết với sản phẩm
    source_products = SourceProduct.objects.filter(linked_product=product)
    
    # Lấy lịch sử thay đổi
    change_logs = ProductChangeLog.objects.filter(product=product).order_by('-created_at')[:5]
    
    # Lấy dữ liệu bán hàng - bỏ qua nếu không có model OrderItem
    total_sales = 0
    total_revenue = 0
    try:
        from store.models import OrderItem
        total_sales = OrderItem.objects.filter(product=product).count()
        total_revenue = OrderItem.objects.filter(product=product).aggregate(
            revenue=Sum(F('price') * F('quantity'))
        )['revenue'] or 0
    except ImportError:
        # Nếu không có model OrderItem, bỏ qua
        pass
    
    context = {
        'product': product,
        'product_images': product_images,
        'variants': variants,
        'source_products': source_products,
        'change_logs': change_logs,
        'total_sales': total_sales,
        'total_revenue': total_revenue
    }
    
    return render(request, 'dashboard/products/detail.html', context)

@staff_member_required
def product_history(request, product_id):
    """Lịch sử thay đổi sản phẩm"""
    product = get_object_or_404(Product, id=product_id)
    
    # Lấy tất cả lịch sử thay đổi
    change_logs = ProductChangeLog.objects.filter(product=product).order_by('-created_at')
    
    # Phân trang
    paginator = Paginator(change_logs, 20)
    page_number = request.GET.get('page', 1)
    logs_page = paginator.get_page(page_number)
    
    context = {
        'product': product,
        'change_logs': logs_page
    }
    
    return render(request, 'dashboard/products/history.html', context)

@staff_member_required
def get_product(request, product_id):
    """Lấy thông tin sản phẩm dạng JSON cho AJAX"""
    product = get_object_or_404(Product, id=product_id)
    
    # Lấy ảnh chính
    primary_image = ProductImage.objects.filter(product=product, is_primary=True).first()
    image_url = primary_image.image.url if primary_image else None
    
    data = {
        'id': product.id,
        'name': product.name,
        'price': float(product.price),
        'old_price': float(product.old_price) if product.old_price else None,
        'description': product.description,
        'stock': product.stock,
        'category': product.category.name if product.category else '',
        'category_id': product.category.id if product.category else None,
        'brand': product.brand.name if product.brand else '',
        'brand_id': product.brand.id if product.brand else None,
        'product_code': product.product_code,
        'duration': product.duration,
        'duration_display': product.get_duration_display(),
        'image_url': image_url,
        'is_active': product.is_active
    }
    
    return JsonResponse(data)

@staff_member_required
def product_attributes(request):
    """
    Quản lý thuộc tính sản phẩm
    """
    context = {
        'title': 'Thuộc tính sản phẩm',
        'active_tab': 'products'
    }
    return render(request, 'dashboard/products/attributes.html', context)

@staff_member_required
def product_reviews(request):
    """
    Quản lý đánh giá sản phẩm
    """
    # Truy vấn tất cả đánh giá sản phẩm
    # Đây là phiên bản đơn giản, cần điều chỉnh theo model thực tế
    reviews = []  # Thay bằng truy vấn thật từ model ProductReview
    
    context = {
        'title': 'Đánh giá sản phẩm',
        'reviews': reviews,
        'active_tab': 'products'
    }
    return render(request, 'dashboard/products/reviews.html', context)

@staff_member_required
def export_products(request):
    """
    Xuất danh sách sản phẩm ra file Excel/CSV
    """
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    # Lấy tất cả sản phẩm
    products = Product.objects.all().order_by('id')
    
    # Tạo response với content type là text/csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="products_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    # Tạo writer CSV
    writer = csv.writer(response)
    
    # Viết header
    writer.writerow([
        'ID', 'Mã sản phẩm', 'Tên sản phẩm', 'Danh mục', 'Thương hiệu', 
        'Giá bán', 'Giá cũ', 'Tồn kho', 'Trạng thái', 'Ngày tạo'
    ])
    
    # Viết dữ liệu sản phẩm
    for product in products:
        writer.writerow([
            product.id, 
            product.product_code,
            product.name,
            product.category.name if product.category else '',
            product.brand.name if product.brand else '',
            product.price,
            product.old_price or '',
            product.stock,
            'Đang bán' if product.is_active else 'Ngừng bán',
            product.created_at.strftime('%d/%m/%Y') if hasattr(product, 'created_at') else ''
        ])
    
    return response 