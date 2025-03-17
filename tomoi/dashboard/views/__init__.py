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
from .marketing import marketing, social_marketing, sms_push, affiliate, remarketing, automation, remarketing_campaign
from .settings import *
from .api import *
from .chatbot import *
from .source import *
from .messaging import messaging
from .warranty import *
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
from .source import *
from .discount import *
# Import banner views đúng tên
from .banner import banner_list, banner_add, banner_edit, banner_delete, toggle_banner, upload_banner_image
from .api_settings import api_settings, save_api_config, test_api
from .chatbot import (
    chatbot_dashboard, 
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

# Nhập các view từ order_views
from ..order_views import (
    order_management,
    order_detail,
    update_order_status,
    export_orders,
    cancel_order,
    refund_order,
    order_list,
    order_history,
    customer_orders
)

# Định nghĩa hàm messaging
@staff_member_required
def messaging(request):
    """View cho chức năng messaging"""
    return render(request, 'dashboard/messaging/index.html')

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
    
    # Lấy danh sách thương hiệu từ BRAND_CHOICES hoặc từ cơ sở dữ liệu
    brands = [('', 'Tất cả thương hiệu')]
    
    # Sử dụng BRAND_CHOICES nếu có, ngược lại lấy danh sách brands từ cơ sở dữ liệu
    if hasattr(Product, 'BRAND_CHOICES'):
        for choice in Product.BRAND_CHOICES:
            brands.append(choice)
    else:
        # Lấy danh sách thương hiệu từ model Brand
        brand_list = Brand.objects.all()
        for brand_obj in brand_list:
            brands.append((brand_obj.id, brand_obj.name))
    
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

# Import các module tự định nghĩa
from .marketing import marketing, social_marketing, sms_push, affiliate, remarketing, automation, remarketing_campaign
from .settings import *
from .api import *
from .chatbot import *
from .source import *
from .messaging import messaging
from .calendar import *
try:
    from ..order_views import order_management, order_detail, update_order_status, export_orders
except ImportError:
    # Nếu không import được, sẽ sử dụng hàm not_implemented
    pass

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

# Settings
settings_dashboard = not_implemented
# update_general_settings = not_implemented - Đã được triển khai trong settings.py
email_settings = not_implemented
update_email_settings = not_implemented
payment_settings = not_implemented
# update_payment_settings = not_implemented - Đã được triển khai trong settings.py

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
# add_user = not_implemented - Đã được import từ module user
# delete_user = not_implemented - Đã được import từ module user

# Warranty Management
# Định nghĩa các hàm tự triển khai cho bảo hành
@staff_member_required
def warranty_management(request):
    """Quản lý các yêu cầu bảo hành"""
    from ..models.warranty import WarrantyTicket
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Lấy danh sách các yêu cầu bảo hành
    tickets = WarrantyTicket.objects.all().select_related('order', 'product', 'customer', 'assigned_to')
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    if search_query:
        from django.db.models import Q
        tickets = tickets.filter(
            Q(customer__username__icontains=search_query) |
            Q(customer__email__icontains=search_query) |
            Q(issue_description__icontains=search_query)
        )
    
    # Sắp xếp theo mới nhất trước
    tickets = tickets.order_by('-created_at')
    
    # Phân trang
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page', 1)
    tickets_page = paginator.get_page(page_number)
    
    context = {
        'tickets': tickets_page,
        'status_filter': status_filter,
        'search_query': search_query
    }
    
    return render(request, 'dashboard/warranty/management.html', context)

@staff_member_required
def warranty_detail(request, warranty_id):
    """Chi tiết yêu cầu bảo hành"""
    from ..models.warranty import WarrantyTicket, WarrantyHistory
    ticket = get_object_or_404(WarrantyTicket, id=warranty_id)
    history = WarrantyHistory.objects.filter(ticket=ticket).order_by('-created_at')
    
    context = {
        'ticket': ticket,
        'history': history
    }
    
    return render(request, 'dashboard/warranty/detail.html', context)

@staff_member_required
def warranty_report(request):
    """Báo cáo bảo hành"""
    from ..models.warranty import WarrantyTicket
    from django.db.models import Count
    
    # Thống kê theo trạng thái
    status_stats = WarrantyTicket.objects.values('status').annotate(count=Count('id'))
    
    # Thống kê theo sản phẩm
    product_stats = WarrantyTicket.objects.filter(product__isnull=False).values('product__name').annotate(count=Count('id'))
    
    context = {
        'status_stats': status_stats,
        'product_stats': product_stats
    }
    
    return render(request, 'dashboard/warranty/report.html', context)

@staff_member_required
def create_warranty(request):
    """Tạo yêu cầu bảo hành mới"""
    if request.method == 'POST':
        # Xử lý form tạo bảo hành
        from ..models.warranty import WarrantyTicket
        
        customer_id = request.POST.get('customer')
        product_id = request.POST.get('product')
        issue_description = request.POST.get('issue_description')
        
        customer = get_object_or_404(CustomUser, id=customer_id)
        product = get_object_or_404(Product, id=product_id) if product_id else None
        
        ticket = WarrantyTicket.objects.create(
            customer=customer,
            product=product,
            issue_description=issue_description,
            status='pending'
        )
        
        messages.success(request, f'Đã tạo yêu cầu bảo hành #{ticket.id} thành công')
        return redirect('dashboard:warranty_detail', warranty_id=ticket.id)
    
    # Hiển thị form tạo bảo hành
    # Lấy danh sách khách hàng và sản phẩm cho form
    customers = CustomUser.objects.filter(is_active=True).order_by('username')
    products = Product.objects.filter(is_active=True).order_by('name')
    
    context = {
        'customers': customers,
        'products': products
    }
    
    return render(request, 'dashboard/warranty/create.html', context)

@staff_member_required
def update_warranty_status(request, warranty_id):
    """Cập nhật trạng thái bảo hành"""
    from ..models.warranty import WarrantyTicket, WarrantyHistory
    
    if request.method == 'POST':
        ticket = get_object_or_404(WarrantyTicket, id=warranty_id)
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        # Cập nhật trạng thái
        old_status = ticket.status
        ticket.status = new_status
        ticket.save()
        
        # Ghi nhật ký
        WarrantyHistory.objects.create(
            ticket=ticket,
            action=f'Thay đổi trạng thái từ {old_status} thành {new_status}',
            notes=notes,
            performed_by=request.user
        )
        
        messages.success(request, f'Đã cập nhật trạng thái bảo hành #{ticket.id} thành công')
    
    return redirect('dashboard:warranty_detail', warranty_id=warranty_id)

@staff_member_required
def assign_warranty(request, warranty_id):
    """Phân công xử lý bảo hành"""
    from ..models.warranty import WarrantyTicket, WarrantyHistory
    
    if request.method == 'POST':
        ticket = get_object_or_404(WarrantyTicket, id=warranty_id)
        assigned_to_id = request.POST.get('assigned_to')
        
        if assigned_to_id:
            assigned_to = get_object_or_404(CustomUser, id=assigned_to_id)
            
            # Cập nhật người phụ trách
            old_assigned = ticket.assigned_to.username if ticket.assigned_to else 'Chưa phân công'
            ticket.assigned_to = assigned_to
            ticket.save()
            
            # Ghi nhật ký
            WarrantyHistory.objects.create(
                ticket=ticket,
                action=f'Phân công từ {old_assigned} cho {assigned_to.username}',
                performed_by=request.user
            )
            
            messages.success(request, f'Đã phân công yêu cầu bảo hành #{ticket.id} cho {assigned_to.username}')
    
    return redirect('dashboard:warranty_detail', warranty_id=warranty_id)

@staff_member_required
def add_warranty_note(request, warranty_id):
    """Thêm ghi chú cho yêu cầu bảo hành"""
    from ..models.warranty import WarrantyTicket, WarrantyHistory
    
    if request.method == 'POST':
        ticket = get_object_or_404(WarrantyTicket, id=warranty_id)
        notes = request.POST.get('notes', '')
        
        if notes:
            # Ghi nhật ký
            WarrantyHistory.objects.create(
                ticket=ticket,
                action='Thêm ghi chú',
                notes=notes,
                performed_by=request.user
            )
            
            messages.success(request, f'Đã thêm ghi chú cho yêu cầu bảo hành #{ticket.id}')
    
    return redirect('dashboard:warranty_detail', warranty_id=warranty_id)

@staff_member_required
def send_new_account(request, user_id):
    """Gửi thông tin tài khoản mới cho khách hàng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Xử lý gửi thông tin
    messages.success(request, f'Đã gửi thông tin tài khoản cho {user.username}')
    
    return redirect('dashboard:user_detail', user_id=user_id)

@staff_member_required
def delete_warranty(request, warranty_id):
    """Xóa yêu cầu bảo hành"""
    from ..models.warranty import WarrantyTicket
    
    ticket = get_object_or_404(WarrantyTicket, id=warranty_id)
    
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, f'Đã xóa yêu cầu bảo hành #{warranty_id}')
        return redirect('dashboard:warranty')
    
    context = {'ticket': ticket}
    return render(request, 'dashboard/warranty/delete_confirm.html', context)

# Subscription Management
from .subscription import subscription_list as subscription_management, subscription_plans

# Source Management
from .source import (
    source_dashboard,
    source_list,
    source_add,
    source_edit,
    source_delete,
    source_log_list,
    source_analytics,
    share_report,
    source_chart_data,
    add_source_redirect
)

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

# Thêm hàm user_management
def user_management(request):
    """Trang quản lý người dùng"""
    # Chuyển hướng đến trang danh sách người dùng
    from django.shortcuts import redirect
    return redirect('dashboard:user_list')

# Định nghĩa hàm dashboard chính cho trang chủ
@staff_member_required
def dashboard(request):
    """Dashboard chính của ứng dụng"""
    # Thống kê người dùng
    total_users = CustomUser.objects.count()
    new_users_24h = CustomUser.objects.filter(
        date_joined__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    # Thống kê đơn hàng
    total_orders = Order.objects.count()
    new_orders_24h = Order.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    # Thống kê doanh thu
    total_revenue = Order.objects.filter(status='completed').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Thống kê sản phẩm
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    
    # Lấy 5 thông báo hệ thống mới nhất
    notifications = SystemNotification.objects.filter(
        is_active=True
    ).order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'new_users_24h': new_users_24h,
        'total_orders': total_orders,
        'new_orders_24h': new_orders_24h,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'active_products': active_products,
        'notifications': notifications
    }
    
    return render(request, 'dashboard/index.html', context) 