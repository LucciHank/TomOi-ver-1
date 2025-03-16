# Tạo file này để biến views thành một package 

# Đảm bảo package views được khởi tạo đúng
# Có thể import các hàm thường dùng ở đây để dễ truy cập 

import sys
import importlib
import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Avg, Q, F
from django.core.paginator import Paginator
from django.contrib import messages
from store.models import Order, Product, OrderItem, Category, Brand, ProductLabel
from accounts.models import CustomUser
from django.utils import timezone
from datetime import timedelta
from dashboard.models import SystemNotification
from dashboard.models.product import ProductChangeLog, ProductImage

# Import các module tự định nghĩa
from .marketing import *
from .settings import *
from .api import *
from .chatbot import *
from .source import *
from .user import (
    user_list,
    user_detail,
    user_edit,
    user_permissions,
    user_activity_log,
    user_login_history,
    terminate_session,
    terminate_all_sessions,
    toggle_user_status,
    user_add,
    user_delete,
    import_users,
    user_report,
    user_stats
)
from .user_views import *
from .user import *
from .marketing import *
from .source import *
from .discount import *
from .banner import *
from .api_settings import api_settings, save_api_config, test_api
from .chatbot import (
    dashboard, 
    chatbot_api_settings,
    chatbot_save_api,
    chatbot_test_api,
    settings,
    logs,
    responses
)

# Import các hàm quản lý sản phẩm từ module product
from .product import (
    update_product_status,
    manage_product_images,
    delete_product_image,
    set_primary_image,
    product_detail,
    product_history,
    get_product
)

# Hàm tạm thời cho các view chưa được triển khai
def not_implemented(request, *args, **kwargs):
    return render(request, 'dashboard/not_implemented.html', {
        'message': 'Chức năng này đang được phát triển'
    })

# Định nghĩa trực tiếp các hàm quản lý sản phẩm, sẽ được sử dụng nếu không import được từ views.py

# 1. Danh sách sản phẩm
@staff_member_required
def product_list(request):
    query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    brand = request.GET.get('brand', '')
    status = request.GET.get('status', '')
    sort = request.GET.get('sort', 'recent')
    
    products = Product.objects.all()
    
    # Tìm kiếm
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(product_code__icontains=query)
        )
    
    # Lọc theo danh mục
    if category_id and category_id.isdigit():
        products = products.filter(category_id=category_id)
    
    # Lọc theo thương hiệu
    if brand:
        products = products.filter(brand=brand)
        
    # Lọc theo trạng thái
    if status == 'active':
        products = products.filter(is_active=True)
    elif status == 'inactive':
        products = products.filter(is_active=False)
    
    # Sắp xếp
    if sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'name_desc':
        products = products.order_by('-name')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'stock_asc':
        products = products.order_by('stock')
    elif sort == 'stock_desc':
        products = products.order_by('-stock')
    else:  # recent
        products = products.order_by('-created_at')
    
    # Phân trang
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page', 1)
    products_page = paginator.get_page(page_number)
    
    # Lấy danh sách danh mục và thương hiệu để hiển thị bộ lọc
    categories = Category.objects.all()
    brands = [('', 'Tất cả thương hiệu')]
    for choice in Product.BRAND_CHOICES:
        brands.append(choice)
    
    context = {
        'products': products_page,
        'categories': categories,
        'brands': brands,
        'query': query,
        'category': category_id,
        'brand': brand,
        'status': status,
        'sort': sort
    }
    
    return render(request, 'dashboard/products/list.html', context)

# 2. Thêm sản phẩm
@staff_member_required
def add_product(request):
    from dashboard.forms import ProductForm
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            
            # Xử lý ảnh chính
            if 'image' in request.FILES:
                ProductImage.objects.create(
                    product=product,
                    image=request.FILES['image'],
                    is_primary=True
                )
            
            # Xử lý nhiều ảnh sản phẩm
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

# 3. Sửa sản phẩm
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
            
            # Xử lý nhiều ảnh sản phẩm
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

# 4. Xóa sản phẩm
@staff_member_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # Ghi log trước khi xóa
        ProductChangeLog.objects.create(
            product=product,
            user=request.user,
            action='delete',
            description=f'Xóa sản phẩm: {product.name}'
        )
        
        product_name = product.name
        product.delete()
        messages.success(request, f'Đã xóa sản phẩm {product_name} thành công')
        return redirect('dashboard:products')
    
    context = {
        'product': product
    }
    
    return render(request, 'dashboard/products/delete_confirm.html', context)

# 5. Danh sách danh mục
@staff_member_required
def category_list(request):
    categories = Category.objects.all()
    
    context = {
        'categories': categories
    }
    
    return render(request, 'dashboard/products/categories.html', context)

# 6. Thêm danh mục mới
@staff_member_required
def add_category(request):
    from dashboard.forms import CategoryForm
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm danh mục mới thành công')
            return redirect('dashboard:categories')
        else:
            messages.error(request, 'Có lỗi xảy ra khi thêm danh mục')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Thêm danh mục mới'
    }
    
    return render(request, 'dashboard/products/add_category.html', context)

# 7. Sửa danh mục
@staff_member_required
def edit_category(request, category_id):
    from dashboard.forms import CategoryForm
    
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã cập nhật danh mục {category.name} thành công')
            return redirect('dashboard:categories')
        else:
            messages.error(request, 'Có lỗi xảy ra khi cập nhật danh mục')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': f'Chỉnh sửa danh mục: {category.name}'
    }
    
    return render(request, 'dashboard/products/edit_category.html', context)

# 8. Import sản phẩm
@staff_member_required
def import_products(request):
    if request.method == 'POST' and request.FILES.get('file'):
        import csv
        import io
        
        csv_file = request.FILES['file']
        
        # Kiểm tra file CSV
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Vui lòng tải lên file CSV')
            return redirect('dashboard:import_products')
        
        # Đọc file CSV
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string)  # Bỏ qua header
        
        # Đếm số sản phẩm được import
        count = 0
        
        for column in csv.reader(io_string, delimiter=',', quotechar='"'):
            try:
                # Tạo hoặc cập nhật sản phẩm
                product, created = Product.objects.update_or_create(
                    product_code=column[0],
                    defaults={
                        'name': column[1],
                        'description': column[2],
                        'price': float(column[3]),
                        'stock': int(column[4]),
                        'is_active': column[5].lower() in ('true', 'yes', '1'),
                    }
                )
                
                # Ghi log
                action = 'create' if created else 'update'
                ProductChangeLog.objects.create(
                    product=product,
                    user=request.user,
                    action=action,
                    description=f"{'Tạo' if created else 'Cập nhật'} sản phẩm từ import CSV"
                )
                
                count += 1
            except Exception as e:
                print(f"Error importing row: {e}")
                continue
        
        messages.success(request, f'Đã import thành công {count} sản phẩm')
        return redirect('dashboard:products')
    
    return render(request, 'dashboard/products/import.html')

# Gán các hàm tạm thời cho các view chưa triển khai
order_management = not_implemented
order_detail = not_implemented
update_order_status = not_implemented
export_orders = not_implemented
user_management = not_implemented
export_users = not_implemented
warranty_management = not_implemented

# Analytics
analytics_dashboard = not_implemented
sales_report = not_implemented
user_analytics = not_implemented
marketing_analytics = not_implemented
custom_report = not_implemented

# Marketing
marketing_dashboard = not_implemented
campaign_list = not_implemented
add_campaign = not_implemented
banner_list = not_implemented
add_banner = not_implemented
edit_banner = not_implemented

# Settings
settings_dashboard = not_implemented
update_general_settings = not_implemented
email_settings = not_implemented
update_email_settings = not_implemented
payment_settings = not_implemented
update_payment_settings = not_implemented

# API
api_key_list = not_implemented
add_api_key = not_implemented
toggle_api_key = not_implemented
delete_api_key = not_implemented
webhook_list = not_implemented
add_webhook = not_implemented
edit_webhook = not_implemented
delete_webhook = not_implemented
api_logs = not_implemented
get_log_details = not_implemented
api_source_products = not_implemented
get_source_base_price = not_implemented

# User Management
add_user = not_implemented
delete_user = not_implemented

# Warranty Management
warranty_detail = not_implemented
warranty_report = not_implemented
send_new_account = not_implemented
create_warranty = not_implemented
update_warranty_status = not_implemented
assign_warranty = not_implemented
add_warranty_note = not_implemented
delete_warranty = not_implemented

# Subscription Management
subscription_management = not_implemented
subscription_plans = not_implemented

# Source Management
source_dashboard = not_implemented
source_list = not_implemented
source_add = not_implemented
source_edit = not_implemented
source_delete = not_implemented
source_log_list = not_implemented
source_analytics = not_implemented
share_report = not_implemented
source_chart_data = not_implemented
add_source_redirect = not_implemented

# Reports
product_report = not_implemented
customer_report = not_implemented
reports_analysis = not_implemented
revenue_report = not_implemented
popular_products = not_implemented
processing_time = not_implemented

# Accounts
account_types = not_implemented
account_transactions = not_implemented
tcoin_accounts = not_implemented

# Chat
chat_messages = not_implemented
chat_sessions = not_implemented

# Email
email_logs = not_implemented
email_templates = not_implemented
email_editor = not_implemented
email_save_template = not_implemented

@staff_member_required
def analytics(request):
    # Thống kê người dùng
    total_users = CustomUser.objects.count()
    new_users_24h = CustomUser.objects.filter(
        date_joined__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    # Tỷ lệ tăng trưởng người dùng
    users_last_week = CustomUser.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()
    user_growth_rate = ((new_users_24h - users_last_week) / users_last_week * 100) if users_last_week > 0 else 0

    # Nguồn truy cập
    traffic_sources = CustomUser.objects.values('registration_source').annotate(
        count=Count('id')
    )

    # Thiết bị sử dụng
    device_usage = CustomUser.objects.values('last_login_device').annotate(
        count=Count('id')
    )

    # Biểu đồ người dùng mới theo ngày
    user_growth_chart = CustomUser.objects.extra({
        'day': "date(date_joined)"
    }).values('day').annotate(
        count=Count('id')
    ).order_by('day')

    context = {
        'total_users': total_users,
        'new_users_24h': new_users_24h,
        'user_growth_rate': user_growth_rate,
        'traffic_sources': list(traffic_sources),
        'device_usage': list(device_usage),
        'user_growth_chart': list(user_growth_chart),
        'notifications': SystemNotification.objects.filter(is_active=True)[:5]
    }
    return render(request, 'dashboard/analytics.html', context)

@staff_member_required
def reports(request):
    """Trang báo cáo"""
    context = {
        'sales_report': generate_sales_report(),
        'user_activity_report': generate_user_activity_report(),
    }
    return render(request, 'dashboard/reports.html', context)

@staff_member_required
def performance(request):
    """Trang hiệu suất hệ thống"""
    context = {
        'server_metrics': get_server_performance_metrics(),
        'database_performance': analyze_database_performance(),
    }
    return render(request, 'dashboard/performance.html', context)

# Các hàm hỗ trợ (bạn cần triển khai chi tiết)
def calculate_user_growth_rate():
    # Logic tính toán tỷ lệ tăng trưởng người dùng
    pass

def calculate_bounce_rate():
    # Logic tính toán tỷ lệ thoát
    pass

def calculate_conversion_rate():
    # Logic tính toán tỷ lệ chuyển đổi
    pass

def generate_sales_report():
    # Logic tạo báo cáo doanh số
    pass

def generate_user_activity_report():
    # Logic tạo báo cáo hoạt động người dùng
    pass

def get_server_performance_metrics():
    # Logic lấy các chỉ số hiệu suất server
    pass

def analyze_database_performance():
    # Logic phân tích hiệu suất database
    pass

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