from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.utils import timezone

from dashboard.models.source import Source, SourceProduct, SourceLog
from dashboard.models.product import Product
from dashboard.models.source_history import SourceHistory

import logging
import datetime
import decimal
import json

logger = logging.getLogger(__name__)

@login_required
@permission_required('dashboard.view_source', raise_exception=True)
def source_list(request):
    """Danh sách nguồn cung cấp"""
    sources = Source.objects.all().order_by('-created_at')
    
    # Filters
    query = request.GET.get('q')
    if query:
        sources = sources.filter(
            Q(name__icontains=query) | 
            Q(url__icontains=query) | 
            Q(product_type__icontains=query)
        )
    
    # Lọc theo nền tảng
    platform = request.GET.get('platform')
    if platform:
        sources = sources.filter(platform=platform)
    
    # Lọc theo mức độ ưu tiên
    priority = request.GET.get('priority')
    if priority:
        sources = sources.filter(priority=priority)
    
    # Phân trang
    paginator = Paginator(sources, 10)
    page = request.GET.get('page')
    sources_page = paginator.get_page(page)
    
    # Lấy các tùy chọn để hiển thị bộ lọc
    platform_choices = Source.PLATFORM_CHOICES
    priority_choices = Source.PRIORITY_CHOICES
    
    context = {
        'sources': sources_page,
        'platform_choices': platform_choices,
        'priority_choices': priority_choices,
        'query': query,
        'platform': platform,
        'priority': priority,
    }
    
    return render(request, 'dashboard/sources/list.html', context)

@login_required
@permission_required('dashboard.add_source', raise_exception=True)
def source_add(request):
    """Thêm nguồn cung cấp mới"""
    # Xử lý form khi submit
    if request.method == 'POST':
        name = request.POST.get('name')
        url = request.POST.get('url')
        platform = request.POST.get('platform')
        product_type = request.POST.get('product_type')
        base_price = request.POST.get('base_price')
        availability_rate = request.POST.get('availability_rate', 100)
        priority = request.POST.get('priority')
        notes = request.POST.get('notes', '')
        
        try:
            # Chuyển đổi kiểu dữ liệu
            base_price = int(base_price) if base_price else 0
            availability_rate = int(availability_rate) if availability_rate else 100
            priority = int(priority) if priority else 3
            
            # Tạo mới nguồn cung cấp
            source = Source.objects.create(
                name=name,
                url=url,
                platform=platform,
                product_type=product_type,
                base_price=base_price,
                availability_rate=availability_rate,
                priority=priority,
                notes=notes,
                created_by=request.user
            )
            
            # Tạo nhật ký lịch sử
            SourceHistory.objects.create(
                source=source,
                log_type='source_created',
                notes=f'Nguồn cung cấp được tạo bởi {request.user.username}',
                created_by=request.user
            )
            
            messages.success(request, f'Đã thêm thành công nguồn cung cấp "{name}"')
            return redirect('dashboard:source_detail', pk=source.pk)
            
        except Exception as e:
            logger.error(f"Lỗi khi thêm nguồn cung cấp: {str(e)}")
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
    
    # Dữ liệu cho form
    platforms = Source.PLATFORM_CHOICES
    priorities = Source.PRIORITY_CHOICES
    
    context = {
        'platforms': platforms,
        'priorities': priorities,
        'title': 'Thêm nguồn cung cấp mới',
    }
    return render(request, 'dashboard/sources/add.html', context)

@login_required
@permission_required('dashboard.view_source', raise_exception=True)
def source_detail(request, pk):
    """Chi tiết nguồn cung cấp"""
    source = get_object_or_404(Source, pk=pk)
    source_products = SourceProduct.objects.filter(source=source)
    logs = SourceLog.objects.filter(source=source).order_by('-created_at')[:50]
    
    # Thống kê
    avg_price = source_products.aggregate(Avg('price'))['price__avg'] or 0
    
    # Lấy lịch sử nguồn
    source_histories = SourceHistory.objects.filter(source=source).order_by('-created_at')[:10]
    
    # Tỷ lệ lỗi (số lần nguồn không có hàng / tổng số lần kiểm tra)
    total_checks = source_histories.filter(log_type__in=['order', 'availability_check']).count()
    unavailable_count = source_histories.filter(log_type__in=['order', 'availability_check'], has_stock=False).count()
    error_rate = round((unavailable_count / total_checks) * 100, 2) if total_checks > 0 else 0
    
    context = {
        'source': source,
        'source_products': source_products,
        'logs': logs,
        'avg_price': avg_price,
        'source_histories': source_histories,
        'error_rate': error_rate,
    }
    
    return render(request, 'dashboard/sources/detail.html', context)

@login_required
@permission_required('dashboard.change_source', raise_exception=True)
def source_edit(request, pk):
    """Chỉnh sửa nguồn cung cấp."""
    source = get_object_or_404(Source, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        url = request.POST.get('url')
        platform = request.POST.get('platform')
        product_type = request.POST.get('product_type')
        base_price = request.POST.get('base_price')
        availability_rate = request.POST.get('availability_rate', 100)
        priority = request.POST.get('priority')
        notes = request.POST.get('notes', '')
        
        try:
            # Lưu các giá trị trước khi cập nhật để so sánh
            old_values = {
                'name': source.name,
                'url': source.url,
                'platform': source.platform,
                'product_type': source.product_type,
                'base_price': source.base_price,
                'availability_rate': source.availability_rate,
                'priority': source.priority,
            }
            
            # Cập nhật nguồn
            source.name = name
            source.url = url
            source.platform = platform
            source.product_type = product_type
            source.base_price = int(base_price) if base_price else 0
            source.availability_rate = int(availability_rate) if availability_rate else 100
            source.priority = int(priority) if priority else 3
            source.notes = notes
            source.updated_at = timezone.now()
            source.updated_by = request.user
            source.save()
            
            # Tạo nhật ký thay đổi
            changes = []
            for key, old_value in old_values.items():
                new_value = getattr(source, key)
                if old_value != new_value:
                    changes.append(f"{key}: {old_value} -> {new_value}")
            
            if changes:
                change_text = ", ".join(changes)
                SourceHistory.objects.create(
                    source=source,
                    log_type='source_updated',
                    notes=f'Cập nhật bởi {request.user.username}: {change_text}',
                    created_by=request.user
                )
            
            messages.success(request, f'Đã cập nhật thành công nguồn cung cấp "{name}"')
            return redirect('dashboard:source_detail', pk=source.pk)
            
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật nguồn cung cấp: {str(e)}")
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
    
    # Lấy các tùy chọn cho dropdown
    platforms = Source.PLATFORM_CHOICES
    priorities = Source.PRIORITY_CHOICES
    
    context = {
        'source': source,
        'platforms': platforms,
        'priorities': priorities,
        'title': f'Chỉnh sửa nguồn "{source.name}"',
    }
    
    return render(request, 'dashboard/sources/edit.html', context)

@login_required
@permission_required('dashboard.delete_source', raise_exception=True)
def source_delete(request, pk):
    """Xóa nguồn cung cấp."""
    source = get_object_or_404(Source, pk=pk)
    
    if request.method == 'POST':
        try:
            source_name = source.name
            source.delete()
            messages.success(request, f'Đã xóa thành công nguồn cung cấp "{source_name}"')
            return redirect('dashboard:source_list')
        except Exception as e:
            logger.error(f"Lỗi khi xóa nguồn cung cấp: {str(e)}")
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
    
    context = {
        'source': source,
        'title': f'Xác nhận xóa nguồn "{source.name}"',
    }
    
    return render(request, 'dashboard/sources/delete.html', context)

@login_required
@permission_required('dashboard.view_source', raise_exception=True)
def source_dashboard(request):
    """Hiển thị trang tổng quan về nguồn cung cấp."""
    # Số lượng nguồn cung cấp
    total_sources = Source.objects.count()
    
    # Tổng chi phí đã nhập hàng
    total_spend = SourceHistory.objects.filter(log_type='order').aggregate(Sum('price'))['price__sum'] or 0
    
    # Tỷ lệ có hàng trung bình
    avg_availability = Source.objects.aggregate(Avg('availability_rate'))['availability_rate__avg'] or 0
    
    # Thời gian xử lý trung bình
    avg_processing_time = SourceHistory.objects.filter(log_type='order').aggregate(Avg('processing_time'))['processing_time__avg'] or 0
    
    # Lấy các sản phẩm phổ biến từ các nguồn
    popular_products = SourceProduct.objects.select_related('product', 'source')[:12]
    
    # Lịch sử lấy hàng gần đây
    logs = SourceHistory.objects.filter(log_type='order').select_related('source', 'created_by').order_by('-created_at')[:10]
    
    context = {
        'total_sources': total_sources,
        'total_spend': total_spend,
        'avg_availability': round(avg_availability, 1),
        'avg_processing_time': round(avg_processing_time, 1),
        'products': popular_products,
        'logs': logs,
    }
    
    return render(request, 'dashboard/sources/dashboard.html', context)

@login_required
@permission_required('dashboard.add_sourcehistory', raise_exception=True)
def add_source_log(request):
    """API để thêm nhật ký nguồn hàng."""
    if request.method == 'POST':
        try:
            source_id = request.POST.get('source_id')
            products_json = request.POST.get('products_json', '[]')
            quantity = int(request.POST.get('quantity', 1))
            has_stock = request.POST.get('has_stock') == 'on'
            processing_time = int(request.POST.get('processing_time', 0))
            notes = request.POST.get('notes', '')
            price = int(request.POST.get('price', 0))
            
            # Thông tin tài khoản
            account_type = request.POST.get('account_type', 'new_account')
            account_username = request.POST.get('account_username', '')
            account_password = request.POST.get('account_password', '')
            
            # Parse danh sách sản phẩm từ JSON
            try:
                products_data = json.loads(products_json)
            except json.JSONDecodeError:
                products_data = []
            
            source = get_object_or_404(Source, id=source_id)
            
            # Xác định sản phẩm chính cho quan hệ source_product (lấy cái đầu tiên)
            source_product = None
            if products_data:
                first_product_id = products_data[0].get('id')
                try:
                    product = Product.objects.get(id=first_product_id)
                    source_product, created = SourceProduct.objects.get_or_create(
                        source=source,
                        product=product,
                        defaults={
                            'price': source.base_price,
                            'created_by': request.user
                        }
                    )
                except Product.DoesNotExist:
                    pass
            
            # Tạo nhật ký
            log = SourceHistory.objects.create(
                source=source,
                source_product=source_product,
                products=products_data,  # Lưu danh sách sản phẩm dưới dạng JSON
                log_type='order',
                has_stock=has_stock,
                quantity=quantity,
                price=price,
                processing_time=processing_time,
                notes=notes,
                account_type=account_type,
                account_username=account_username,
                account_password=account_password,
                created_by=request.user
            )
            
            # Cập nhật thông tin nguồn
            # Nếu không có hàng, giảm tỷ lệ có hàng xuống
            if not has_stock:
                # Tính toán tỷ lệ có hàng mới dựa trên lịch sử
                total_checks = SourceHistory.objects.filter(source=source, log_type__in=['order', 'availability_check']).count()
                available_checks = SourceHistory.objects.filter(source=source, log_type__in=['order', 'availability_check'], has_stock=True).count()
                
                if total_checks > 0:
                    new_rate = int((available_checks / total_checks) * 100)
                    source.availability_rate = new_rate
                    source.save()
            
            messages.success(request, 'Đã thêm nhật ký nguồn thành công')
            return redirect('dashboard:source_log_list')
            
        except Exception as e:
            logger.error(f"Lỗi khi thêm nhật ký nguồn: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    # Xử lý request GET - hiển thị form thêm nhật ký
    sources = Source.objects.all()
    products = Product.objects.all()
    
    context = {
        'sources': sources,
        'products': products,
        'log_types': SourceHistory.LOG_TYPE_CHOICES,
        'account_types': SourceHistory.ACCOUNT_TYPE_CHOICES,
        'title': 'Thêm nhật ký nguồn',
    }
    
    return render(request, 'dashboard/sources/add_log.html', context)

@login_required
@permission_required('dashboard.view_sourcehistory', raise_exception=True)
def source_log_list(request):
    """Hiển thị danh sách nhật ký nguồn cung cấp."""
    logs = SourceHistory.objects.all().select_related('source', 'source_product', 'created_by').order_by('-created_at')
    
    # Tìm kiếm
    query = request.GET.get('q')
    if query:
        logs = logs.filter(
            Q(source__name__icontains=query) | 
            Q(source_product__product__name__icontains=query) | 
            Q(notes__icontains=query)
        )
    
    # Lọc theo nguồn
    source_id = request.GET.get('source')
    if source_id:
        logs = logs.filter(source_id=source_id)
    
    # Lọc theo loại log
    log_type = request.GET.get('log_type')
    if log_type:
        logs = logs.filter(log_type=log_type)
    
    # Lọc theo trạng thái có hàng
    has_stock = request.GET.get('has_stock')
    if has_stock is not None:
        has_stock_bool = has_stock == 'true'
        logs = logs.filter(has_stock=has_stock_bool)
    
    # Phân trang
    paginator = Paginator(logs, 20)
    page = request.GET.get('page')
    logs_page = paginator.get_page(page)
    
    # Lấy danh sách nguồn cho bộ lọc
    sources = Source.objects.all()
    log_types = SourceHistory.LOG_TYPE_CHOICES
    
    # Chuẩn bị dữ liệu sản phẩm từ JSON
    for log in logs_page:
        if log.products:
            try:
                if isinstance(log.products, str):
                    products_data = json.loads(log.products)
                else:
                    products_data = log.products
                log.products = products_data
            except (json.JSONDecodeError, TypeError):
                log.products = []
    
    context = {
        'logs': logs_page,
        'sources': sources,
        'log_types': log_types,
        'query': query,
        'source_id': source_id,
        'log_type': log_type,
        'account_types': SourceHistory.ACCOUNT_TYPE_CHOICES,
    }
    
    return render(request, 'dashboard/sources/logs.html', context)

@login_required
def api_search_products(request):
    """API để tìm kiếm sản phẩm."""
    query = request.GET.get('query', '')
    
    if len(query) < 2:
        return JsonResponse({'products': []})
    
    products = Product.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query)
    ).select_related('category')[:10]
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'category': product.category.name if product.category else 'Không phân loại',
            'image': product.get_image_url() if hasattr(product, 'get_image_url') else '',
        })
    
    return JsonResponse({'products': results})

@login_required
def api_product_sources(request):
    """API để lấy danh sách nguồn cho sản phẩm."""
    product_id = request.GET.get('product_id')
    
    if not product_id:
        return JsonResponse({'error': 'Missing product_id'}, status=400)
    
    try:
        product = Product.objects.get(id=product_id)
        
        # Lấy các nguồn đã được kết nối với sản phẩm
        source_products = SourceProduct.objects.filter(product=product).select_related('source')
        
        # Nếu không có nguồn nào, lấy tất cả các nguồn
        if not source_products.exists():
            sources = Source.objects.all()
            source_list = []
            
            for source in sources:
                source_list.append({
                    'id': source.id,
                    'name': source.name,
                    'platform': source.get_platform_display(),
                    'formatted_price': f"{source.base_price:,}",
                    'availability_rate': source.availability_rate,
                    'priority': source.priority,
                    'priority_display': source.get_priority_display(),
                    'avg_processing_time': source.avg_processing_time or 0,
                    'error_rate': 0
                })
        else:
            source_list = []
            
            for sp in source_products:
                # Tính tỷ lệ lỗi cho nguồn này đối với sản phẩm cụ thể
                total_checks = SourceHistory.objects.filter(
                    source=sp.source, 
                    source_product=sp,
                    log_type__in=['order', 'availability_check']
                ).count()
                
                unavailable_count = SourceHistory.objects.filter(
                    source=sp.source, 
                    source_product=sp,
                    log_type__in=['order', 'availability_check'],
                    has_stock=False
                ).count()
                
                error_rate = round((unavailable_count / total_checks) * 100, 1) if total_checks > 0 else 0
                
                source_list.append({
                    'id': sp.source.id,
                    'name': sp.source.name,
                    'platform': sp.source.get_platform_display(),
                    'formatted_price': f"{sp.price:,}",
                    'availability_rate': sp.source.availability_rate,
                    'priority': sp.source.priority,
                    'priority_display': sp.source.get_priority_display(),
                    'avg_processing_time': sp.source.avg_processing_time or 0,
                    'error_rate': error_rate
                })
        
        product_data = {
            'id': product.id,
            'name': product.name,
            'category': product.category.name if product.category else 'Không phân loại',
        }
        
        return JsonResponse({
            'product': product_data,
            'sources': source_list
        })
        
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        logger.error(f"Lỗi khi lấy nguồn cho sản phẩm: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_source_log_detail(request):
    """API để lấy chi tiết nhật ký nguồn."""
    log_id = request.GET.get('log_id')
    
    if not log_id:
        return JsonResponse({'error': 'Missing log_id'}, status=400)
    
    try:
        log = SourceHistory.objects.get(id=log_id)
        
        # Xử lý danh sách sản phẩm từ JSON
        products_data = []
        if log.products:
            try:
                if isinstance(log.products, str):
                    products_data = json.loads(log.products)
                else:
                    products_data = log.products
            except (json.JSONDecodeError, TypeError):
                products_data = []
        
        log_data = {
            'id': log.id,
            'source_name': log.source.name,
            'product_name': log.source_product.product.name if log.source_product and log.source_product.product else None,
            'log_type': log.log_type,
            'log_type_display': log.get_log_type_display(),
            'has_stock': log.has_stock,
            'quantity': log.quantity,
            'price': log.price,
            'processing_time': log.processing_time,
            'created_at': log.created_at.strftime('%d/%m/%Y %H:%M'),
            'created_by': log.created_by.username if log.created_by else None,
            'notes': log.notes,
            'products': products_data,
            'account_type': log.account_type,
            'account_username': log.account_username,
            'account_password': log.account_password,
        }
        
        return JsonResponse({'success': True, 'log': log_data})
        
    except SourceHistory.DoesNotExist:
        return JsonResponse({'error': 'Log not found'}, status=404)
    except Exception as e:
        logger.error(f"Lỗi khi lấy chi tiết nhật ký nguồn: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# Thêm các view khác... 