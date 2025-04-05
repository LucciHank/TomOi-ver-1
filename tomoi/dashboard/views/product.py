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
from dashboard.forms import ProductForm

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
    """View xử lý quản lý thuộc tính sản phẩm"""
    if request.method == 'POST':
        # Kiểm tra loại form
        form_type = request.POST.get('form_type', '')
        
        if form_type == 'attribute':
            # Xử lý khi có submit form thuộc tính
            name = request.POST.get('name')
            slug = request.POST.get('slug')
            description = request.POST.get('description')
            
            # Thực hiện logic tạo thuộc tính sản phẩm mới
            # (Sẽ phát triển sau)
            
            messages.success(request, f'Đã tạo thuộc tính "{name}" thành công')
            return redirect('dashboard:attributes')
        
        elif form_type == 'brand':
            # Xử lý thêm thương hiệu mới
            name = request.POST.get('name', '')
            slug = request.POST.get('slug', '')
            description = request.POST.get('description', '')
            is_active = request.POST.get('is_active') == 'on'
            
            # Tạo thương hiệu mới
            brand = Brand(
                name=name,
                slug=slug,
                description=description,
                is_active=is_active
            )
            
            # Xử lý logo nếu có
            if 'logo' in request.FILES:
                brand.logo = request.FILES['logo']
                
            brand.save()
            messages.success(request, f'Đã thêm thương hiệu {name} thành công')
            return redirect('dashboard:attributes')
    
    # Lấy danh sách thương hiệu cho form
    brands = Brand.objects.all().order_by('name')
    
    # Xử lý hiển thị trang
    context = {
        'brands': brands,
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

@staff_member_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            
            # Xử lý ảnh chính
            if 'primary_image' in request.FILES:
                ProductImage.objects.create(
                    product=product,
                    image=request.FILES['primary_image'],
                    is_primary=True
                )
            
            # Xử lý nhiều ảnh sản phẩm
            if 'additional_images' in request.FILES:
                for image in request.FILES.getlist('additional_images'):
                    ProductImage.objects.create(
                        product=product,
                        image=image,
                        is_primary=False
                    )
            
            # Ghi log thêm mới
            ProductChangeLog.objects.create(
                product=product,
                user=request.user,
                action='create',
                description='Tạo sản phẩm mới'
            )
            
            messages.success(request, f'Đã thêm sản phẩm {product.name} thành công')
            return redirect('dashboard:products')
        else:
            messages.error(request, 'Có lỗi xảy ra khi thêm sản phẩm')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Thêm sản phẩm mới'
    }
    
    return render(request, 'dashboard/products/add.html', context)

@staff_member_required
def edit_product(request, product_id):
    from dashboard.forms import ProductForm
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # Lưu lại dữ liệu cũ để so sánh
        old_data = {
            'name': product.name,
            'price': product.price,
            'stock': product.stock,
            'is_active': product.is_active
        }
        
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # Lưu sản phẩm
            product = form.save()
            
            # Xử lý ảnh chính
            if 'primary_image' in request.FILES:
                # Xóa các ảnh chính cũ
                ProductImage.objects.filter(product=product, is_primary=True).delete()
                # Tạo ảnh chính mới
                ProductImage.objects.create(
                    product=product,
                    image=request.FILES['primary_image'],
                    is_primary=True
                )
            
            # Xử lý nhiều ảnh sản phẩm
            if 'additional_images' in request.FILES:
                for image in request.FILES.getlist('additional_images'):
                    ProductImage.objects.create(
                        product=product,
                        image=image,
                        is_primary=False
                    )
            
            # Ghi log thay đổi
            changes = []
            if old_data['name'] != product.name:
                changes.append(f"Tên: {old_data['name']} -> {product.name}")
            if old_data['price'] != product.price:
                changes.append(f"Giá: {old_data['price']} -> {product.price}")
            if old_data['stock'] != product.stock:
                changes.append(f"Tồn kho: {old_data['stock']} -> {product.stock}")
            if old_data['is_active'] != product.is_active:
                changes.append(f"Trạng thái: {'Hoạt động' if old_data['is_active'] else 'Tạm ngưng'} -> {'Hoạt động' if product.is_active else 'Tạm ngưng'}")
            
            if changes:
                ProductChangeLog.objects.create(
                    product=product,
                    user=request.user,
                    action='update',
                    description='Cập nhật: ' + ', '.join(changes)
                )
            
            messages.success(request, f'Đã cập nhật sản phẩm {product.name} thành công')
            return redirect('dashboard:products')
        else:
            messages.error(request, 'Có lỗi xảy ra khi cập nhật sản phẩm')
    else:
        form = ProductForm(instance=product)
    
    # Lấy các ảnh hiện tại của sản phẩm
    product_images = ProductImage.objects.filter(product=product)
    
    context = {
        'form': form,
        'product': product,
        'product_images': product_images,
        'title': f'Chỉnh sửa sản phẩm: {product.name}'
    }
    
    return render(request, 'dashboard/products/edit.html', context)

@staff_member_required
def brands(request):
    """Quản lý thương hiệu sản phẩm"""
    if request.method == 'POST':
        # Kiểm tra loại form
        form_type = request.POST.get('form_type', '')
        
        if form_type == 'brand':
            # Xử lý thêm thương hiệu mới
            name = request.POST.get('name', '')
            slug = request.POST.get('slug', '')
            description = request.POST.get('description', '')
            is_active = request.POST.get('is_active') == 'on'
            
            # Tạo thương hiệu mới
            brand = Brand(
                name=name,
                slug=slug,
                description=description,
                is_active=is_active
            )
            
            # Xử lý logo nếu có
            if 'logo' in request.FILES:
                brand.logo = request.FILES['logo']
                
            brand.save()
            messages.success(request, f'Đã thêm thương hiệu {name} thành công')
            return redirect('dashboard:brands')
            
        else:
            # Form không xác định
            messages.error(request, 'Form không hợp lệ')
    
    # Lấy danh sách thương hiệu
    brands = Brand.objects.all().order_by('name')
    
    context = {
        'brands': brands,
        'title': 'Quản lý thương hiệu',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/brands.html', context)

@staff_member_required
def edit_brand(request, brand_id):
    """Chỉnh sửa thương hiệu"""
    brand = get_object_or_404(Brand, id=brand_id)
    
    if request.method == 'POST':
        # Cập nhật thông tin
        brand.name = request.POST.get('name', brand.name)
        brand.description = request.POST.get('description', brand.description)
        brand.is_active = request.POST.get('is_active') == 'on'
        
        # Cập nhật slug nếu được cung cấp
        slug = request.POST.get('slug', '')
        if slug:
            brand.slug = slug
            
        # Cập nhật logo nếu có
        if 'logo' in request.FILES:
            brand.logo = request.FILES['logo']
            
        brand.save()
        messages.success(request, f'Đã cập nhật thương hiệu {brand.name} thành công')
        return redirect('dashboard:brands')
    
    context = {
        'brand': brand,
        'title': f'Chỉnh sửa thương hiệu: {brand.name}',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/edit_brand.html', context)

@staff_member_required
def delete_brand(request, brand_id):
    """Xóa thương hiệu"""
    brand = get_object_or_404(Brand, id=brand_id)
    
    if request.method == 'POST':
        brand_name = brand.name
        brand.delete()
        messages.success(request, f'Đã xóa thương hiệu {brand_name} thành công')
        return redirect('dashboard:brands')
    
    context = {
        'brand': brand,
        'title': f'Xác nhận xóa thương hiệu: {brand.name}',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/delete_brand.html', context) 