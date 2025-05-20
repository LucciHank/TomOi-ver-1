from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Q, Sum, F, Count
from django.core.paginator import Paginator
from django.utils.text import slugify
import os
from django.core.files.base import ContentFile
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
import csv
import json
from io import StringIO
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist

from store.models import Product, Category, Brand, ProductLabel, ProductImage, ProductVariant, VariantOption, VariantAttributeValue
from dashboard.models.product import ProductChangeLog
from dashboard.models.source import SourceProduct
from dashboard.forms import ProductForm, ProductVariantForm
from dashboard.models.product_duration import ProductDuration
from dashboard.models.product_attribute import ProductAttribute, AttributeValue
from django.conf import settings
from dashboard.models.supplier import Supplier
from dashboard.models.activity_log import ActivityLog

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
    """Hiển thị danh sách các thuộc tính sản phẩm"""
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
            return redirect('dashboard:attribute_list')
        
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
            return redirect('dashboard:attribute_list')
    
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
    """Thêm sản phẩm mới"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            
            # Xử lý ảnh chính nếu có
            primary_image = request.FILES.get('primary_image')
            if primary_image:
                ProductImage.objects.create(
                    product=product,
                    image=primary_image,
                    is_primary=True
                )
            
            # Xử lý ảnh bổ sung
            additional_images = request.POST.getlist('additional_images[]', [])
            for img_path in additional_images:
                if img_path and os.path.exists(img_path):
                    ProductImage.objects.create(
                        product=product,
                        image=img_path,
                        is_primary=False
                    )
            
            # Xử lý thuộc tính và biến thể sản phẩm
            variant_names = request.POST.getlist('variant_name[]', [])
            variant_prices = request.POST.getlist('variant_price[]', [])
            variant_stocks = request.POST.getlist('variant_stock[]', [])
            variant_active = request.POST.getlist('variant_active[]', [])
            
            for i in range(len(variant_names)):
                if i < len(variant_prices) and i < len(variant_stocks) and i < len(variant_active):
                    variant = ProductVariant.objects.create(
                product=product,
                        name=variant_names[i],
                        price=variant_prices[i],
                        stock=variant_stocks[i],
                        is_active=variant_active[i] == 'True'
                    )
                    
                    # Lưu thuộc tính cho biến thể
                    attribute_ids = request.POST.getlist(f'variant_attribute_{i}[]', [])
                    value_ids = request.POST.getlist(f'variant_value_{i}[]', [])
                    
                    for j in range(min(len(attribute_ids), len(value_ids))):
                        try:
                            attribute = ProductAttribute.objects.get(id=attribute_ids[j])
                            value = AttributeValue.objects.get(id=value_ids[j])
                            VariantAttributeValue.objects.create(
                                variant=variant,
                                attribute=attribute,
                                value=value
                            )
                        except (ProductAttribute.DoesNotExist, AttributeValue.DoesNotExist):
                            pass
            
            # Xử lý thông số kỹ thuật
            spec_names = request.POST.getlist('spec_name[]', [])
            spec_values = request.POST.getlist('spec_value[]', [])
            
            specifications = {}
            for i in range(min(len(spec_names), len(spec_values))):
                if spec_names[i] and spec_values[i]:
                    specifications[spec_names[i]] = spec_values[i]
            
            if specifications:
                product.specifications = specifications
                product.save()
                
            # Thêm thông báo
            messages.success(request, f'Đã thêm sản phẩm {product.name} thành công')
            
            # Chuyển hướng
            if 'save_continue' in request.POST:
                return redirect('dashboard:edit_product', product_id=product.id)
            return redirect('dashboard:products')
        else:
            # Hiển thị lỗi form
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Lỗi ở trường {field}: {error}')
    else:
        form = ProductForm()
    
    # Chuẩn bị dữ liệu cho form
    categories = Category.objects.all()
    brands = Brand.objects.all()
    durations = ProductDuration.objects.all().order_by('days')
    attributes = ProductAttribute.objects.filter(is_active=True)
    suppliers = Supplier.objects.filter(status='active')
    all_products = Product.objects.filter(is_active=True)
    
    context = {
        'form': form,
        'categories': categories,
        'brands': brands,
        'durations': durations,
        'attributes': attributes,
        'suppliers': suppliers,
        'all_products': all_products,
        'active_tab': 'products',
        'title': 'Thêm sản phẩm mới'
    }
    return render(request, 'dashboard/products/add.html', context)

@staff_member_required
def edit_product(request, product_id):
    """Chỉnh sửa sản phẩm"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            
            # Xử lý ảnh chính nếu được thay đổi
            primary_image = request.FILES.get('primary_image')
            if primary_image:
                # Nếu đã có ảnh chính, cập nhật; nếu không, tạo mới
                existing_primary = product.images.filter(is_primary=True).first()
                if existing_primary:
                    existing_primary.image = primary_image
                    existing_primary.save()
                else:
                    ProductImage.objects.create(
                        product=product,
                        image=primary_image,
                        is_primary=True
                )
            
            messages.success(request, f'Đã cập nhật sản phẩm {product.name} thành công')
            
            # Chuyển hướng
            if 'save_continue' in request.POST:
                return redirect('dashboard:edit_product', product_id=product.id)
            return redirect('dashboard:products')
    else:
        form = ProductForm(instance=product)
    
    # Chuẩn bị dữ liệu cho form
    categories = Category.objects.all()
    brands = Brand.objects.all()
    durations = ProductDuration.objects.all().order_by('days')
    attributes = ProductAttribute.objects.filter(is_active=True)
    suppliers = Supplier.objects.filter(status='active')
    
    # Lấy ảnh hiện tại của sản phẩm
    product_images = product.images.all()
    primary_image = product_images.filter(is_primary=True).first()
    
    context = {
        'form': form,
        'product': product,
        'categories': categories,
        'brands': brands,
        'durations': durations,
        'attributes': attributes,
        'suppliers': suppliers,
        'product_images': product_images,
        'primary_image': primary_image,
        'active_tab': 'products',
        'title': f'Chỉnh sửa sản phẩm: {product.name}'
    }
    return render(request, 'dashboard/products/edit.html', context)

@staff_member_required
def brands(request):
    """Danh sách thương hiệu"""
    brand_list = Brand.objects.all().order_by('name')
    
    context = {
        'brands': brand_list,
        'title': 'Quản lý thương hiệu',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/brands/list.html', context)

@staff_member_required
def add_brand(request):
    """Thêm mới thương hiệu"""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        logo = request.FILES.get('logo')
        is_active = request.POST.get('is_active') == 'on'
        
        # Kiểm tra trường bắt buộc
        if not name:
            messages.error(request, 'Vui lòng nhập tên thương hiệu')
            return render(request, 'dashboard/products/brands/add.html', {
                'title': 'Thêm thương hiệu',
                'active_tab': 'products',
                'name': name,
                'description': description,
                'is_active': is_active
            })
        
        # Tạo slug tự động
        slug = slugify(name)
        
        # Kiểm tra trùng lặp
        if Brand.objects.filter(slug=slug).exists():
            messages.error(request, f'Thương hiệu với slug "{slug}" đã tồn tại. Vui lòng chọn tên khác.')
            return render(request, 'dashboard/products/brands/add.html', {
                'title': 'Thêm thương hiệu',
                'active_tab': 'products',
                'name': name,
                'description': description,
                'is_active': is_active
            })
        
        # Tạo mới thương hiệu
        brand = Brand(
            name=name,
            slug=slug,
            description=description,
            logo=logo,
            is_active=is_active
        )
        
        try:
            brand.save()
            messages.success(request, f'Đã thêm thương hiệu "{name}" thành công')
            return redirect('dashboard:brand_list')
        except Exception as e:
            messages.error(request, f'Lỗi khi lưu thương hiệu: {str(e)}')
    
    context = {
        'title': 'Thêm thương hiệu',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/brands/add.html', context)

@staff_member_required
def edit_brand(request, brand_id):
    """Chỉnh sửa thương hiệu"""
    brand = get_object_or_404(Brand, id=brand_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        logo = request.FILES.get('logo')
        is_active = request.POST.get('is_active') == 'on'
        
        # Kiểm tra trường bắt buộc
        if not name:
            messages.error(request, 'Vui lòng nhập tên thương hiệu')
            return render(request, 'dashboard/products/brands/edit.html', {
                'title': f'Chỉnh sửa thương hiệu: {brand.name}',
                'active_tab': 'products',
                'brand': brand
            })
        
        # Tạo slug mới nếu tên thay đổi
        if name != brand.name:
            slug = slugify(name)
            # Kiểm tra trùng lặp
            if Brand.objects.filter(slug=slug).exclude(id=brand_id).exists():
                messages.error(request, f'Thương hiệu với slug "{slug}" đã tồn tại. Vui lòng chọn tên khác.')
                return render(request, 'dashboard/products/brands/edit.html', {
                    'title': f'Chỉnh sửa thương hiệu: {brand.name}',
                    'active_tab': 'products',
                    'brand': brand
                })
            brand.slug = slug
            
        # Cập nhật thông tin
        brand.name = name
        brand.description = description
        if logo:
            brand.logo = logo
        brand.is_active = is_active
        
        try:
            brand.save()
            messages.success(request, f'Đã cập nhật thương hiệu "{name}" thành công')
            return redirect('dashboard:brand_list')
        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật thương hiệu: {str(e)}')
    
    context = {
        'brand': brand,
        'title': f'Chỉnh sửa thương hiệu: {brand.name}',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/brands/edit.html', context)

@staff_member_required
def delete_brand(request, brand_id):
    """Xóa thương hiệu"""
    brand = get_object_or_404(Brand, id=brand_id)
    
    if request.method == 'POST':
        brand_name = brand.name
        brand.delete()
        messages.success(request, f'Đã xóa thương hiệu "{brand_name}" thành công')
        return redirect('dashboard:brand_list')
    
    context = {
        'brand': brand,
        'title': f'Xác nhận xóa thương hiệu: {brand.name}',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/brands/delete.html', context)

@staff_member_required
def delete_category(request, category_id):
    """Xóa danh mục sản phẩm"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Đã xóa danh mục {category_name} thành công')
        return redirect('dashboard:categories')
    
    context = {
        'category': category
    }
    
    return render(request, 'dashboard/products/delete_category_confirm.html', context)

@staff_member_required
def products(request):
    """Quản lý sản phẩm"""
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    brands = Brand.objects.all()
    labels = ProductLabel.objects.all()
    
    # Phân trang
    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'labels': labels,
        'duration_choices': Product.DURATION_CHOICES,
    }
    
    return render(request, 'dashboard/products/list.html', context)

@staff_member_required
def manage_product_variants(request, product_id):
    """Quản lý biến thể sản phẩm và tùy chọn thời hạn"""
    product = get_object_or_404(Product, id=product_id)
    variants = ProductVariant.objects.filter(product=product).order_by('order')
    
    context = {
        'product': product,
        'variants': variants,
        'title': f'Quản lý biến thể - {product.name}'
    }
    
    return render(request, 'dashboard/products/variants/list.html', context)

@staff_member_required
def add_product_variant(request, product_id):
    """Thêm biến thể sản phẩm"""
    from dashboard.forms import ProductVariantForm
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductVariantForm(request.POST)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            variant.save()
            
            messages.success(request, f'Đã thêm biến thể {variant.name} thành công')
            return redirect('dashboard:manage_product_variants', product_id=product.id)
        else:
            messages.error(request, 'Có lỗi xảy ra khi thêm biến thể')
    else:
        form = ProductVariantForm()
    
    context = {
        'form': form,
        'product': product,
        'title': f'Thêm biến thể - {product.name}'
    }
    
    return render(request, 'dashboard/products/variants/add.html', context)

@staff_member_required
def edit_product_variant(request, variant_id):
    """Chỉnh sửa biến thể sản phẩm"""
    from dashboard.forms import ProductVariantForm
    
    variant = get_object_or_404(ProductVariant, id=variant_id)
    product = variant.product
    
    if request.method == 'POST':
        form = ProductVariantForm(request.POST, instance=variant)
        if form.is_valid():
            variant = form.save()
            
            messages.success(request, f'Đã cập nhật biến thể {variant.name} thành công')
            return redirect('dashboard:manage_product_variants', product_id=product.id)
        else:
            messages.error(request, 'Có lỗi xảy ra khi cập nhật biến thể')
    else:
        form = ProductVariantForm(instance=variant)
    
    context = {
        'form': form,
        'variant': variant,
        'product': product,
        'title': f'Chỉnh sửa biến thể - {variant.name}'
    }
    
    return render(request, 'dashboard/products/variants/edit.html', context)

@staff_member_required
def delete_product_variant(request, variant_id):
    """Xóa biến thể sản phẩm"""
    variant = get_object_or_404(ProductVariant, id=variant_id)
    product = variant.product
    
    if request.method == 'POST':
        variant_name = variant.name
        variant.delete()
        
        messages.success(request, f'Đã xóa biến thể {variant_name} thành công')
        return redirect('dashboard:manage_product_variants', product_id=product.id)
    
    context = {
        'variant': variant,
        'product': product,
        'title': f'Xóa biến thể - {variant.name}'
    }
    
    return render(request, 'dashboard/products/variants/delete.html', context)

@staff_member_required
def manage_variant_options(request, variant_id):
    """Quản lý các tùy chọn của biến thể sản phẩm"""
    variant = get_object_or_404(ProductVariant, id=variant_id)
    product = variant.product
    options = variant.options.all().order_by('duration')
    
    context = {
        'variant': variant,
        'product': product,
        'options': options,
        'title': f'Quản lý tùy chọn - {variant.name}'
    }
    
    return render(request, 'dashboard/products/variants/options/list.html', context)

@staff_member_required
def add_variant_option(request, variant_id):
    """Thêm tùy chọn cho biến thể sản phẩm"""
    from dashboard.forms import VariantOptionForm
    
    variant = get_object_or_404(ProductVariant, id=variant_id)
    product = variant.product
    
    if request.method == 'POST':
        form = VariantOptionForm(request.POST)
        if form.is_valid():
            option = form.save(commit=False)
            option.variant = variant
            option.save()
            
            messages.success(request, f'Đã thêm tùy chọn thời hạn {option.duration} tháng thành công')
            return redirect('dashboard:manage_variant_options', variant_id=variant.id)
        else:
            messages.error(request, 'Có lỗi xảy ra khi thêm tùy chọn')
    else:
        form = VariantOptionForm()
    
    context = {
        'form': form,
        'variant': variant,
        'product': product,
        'title': f'Thêm tùy chọn - {variant.name}'
    }
    
    return render(request, 'dashboard/products/variants/options/add.html', context)

@staff_member_required
def edit_variant_option(request, option_id):
    """Chỉnh sửa tùy chọn của biến thể sản phẩm"""
    from dashboard.forms import VariantOptionForm
    
    option = get_object_or_404(VariantOption, id=option_id)
    variant = option.variant
    product = variant.product
    
    if request.method == 'POST':
        form = VariantOptionForm(request.POST, instance=option)
        if form.is_valid():
            option = form.save()
            
            messages.success(request, f'Đã cập nhật tùy chọn thời hạn {option.duration} tháng thành công')
            return redirect('dashboard:manage_variant_options', variant_id=variant.id)
        else:
            messages.error(request, 'Có lỗi xảy ra khi cập nhật tùy chọn')
    else:
        form = VariantOptionForm(instance=option)
    
    context = {
        'form': form,
        'option': option,
        'variant': variant,
        'product': product,
        'title': f'Chỉnh sửa tùy chọn - {option.duration} tháng'
    }
    
    return render(request, 'dashboard/products/variants/options/edit.html', context)

@staff_member_required
def delete_variant_option(request, option_id):
    """Xóa tùy chọn của biến thể sản phẩm"""
    option = get_object_or_404(VariantOption, id=option_id)
    variant = option.variant
    product = variant.product
    
    if request.method == 'POST':
        duration = option.duration
        option.delete()
        
        messages.success(request, f'Đã xóa tùy chọn thời hạn {duration} tháng thành công')
        return redirect('dashboard:manage_variant_options', variant_id=variant.id)
    
    context = {
        'option': option,
        'variant': variant,
        'product': product,
        'title': f'Xóa tùy chọn - {option.duration} tháng'
    }
    
    return render(request, 'dashboard/products/variants/options/delete.html', context) 