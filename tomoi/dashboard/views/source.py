from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.http import JsonResponse

from dashboard.models.source import Source, SourceProduct, SourceLog
from dashboard.models.product import Product

@staff_member_required
def source_list(request):
    """Danh sách nguồn cung cấp"""
    sources = Source.objects.all().order_by('-priority', 'name')
    
    # Filters
    platform = request.GET.get('platform')
    if platform:
        sources = sources.filter(platform=platform)
    
    product_type = request.GET.get('product_type')
    if product_type:
        sources = sources.filter(product_type=product_type)
    
    context = {
        'sources': sources,
        'platforms': Source.objects.values_list('platform', flat=True).distinct(),
        'product_types': Source.objects.values_list('product_type', flat=True).distinct(),
    }
    
    return render(request, 'dashboard/sources/list.html', context)

@staff_member_required
def add_source(request):
    """Thêm nguồn cung cấp mới"""
    if request.method == 'POST':
        # Xử lý form
        name = request.POST.get('name')
        source_url = request.POST.get('source_url')
        platform = request.POST.get('platform')
        product_type = request.POST.get('product_type')
        base_price = request.POST.get('base_price')
        priority = request.POST.get('priority')
        notes = request.POST.get('notes')
        
        source = Source.objects.create(
            name=name,
            source_url=source_url,
            platform=platform,
            product_type=product_type,
            base_price=base_price,
            priority=priority,
            notes=notes
        )
        
        messages.success(request, f'Đã thêm nguồn "{name}"')
        return redirect('dashboard:source_detail', source_id=source.id)
    
    return render(request, 'dashboard/sources/add.html')

@staff_member_required
def source_detail(request, source_id):
    """Chi tiết nguồn cung cấp"""
    source = get_object_or_404(Source, id=source_id)
    source_products = SourceProduct.objects.filter(source=source)
    logs = SourceLog.objects.filter(source=source).order_by('-created_at')[:50]
    
    # Thống kê
    avg_price = source_products.aggregate(Avg('price'))['price__avg'] or 0
    
    context = {
        'source': source,
        'source_products': source_products,
        'logs': logs,
        'avg_price': avg_price,
    }
    
    return render(request, 'dashboard/sources/detail.html', context)

@staff_member_required
def compare_sources(request):
    """So sánh các nguồn cung cấp"""
    product_type = request.GET.get('product_type')
    search = request.GET.get('search', '')
    
    sources = Source.objects.all().order_by('base_price')
    if product_type:
        sources = sources.filter(product_type=product_type)
    
    if search:
        sources = sources.filter(
            Q(name__icontains=search) |
            Q(product_type__icontains=search)
        )
    
    context = {
        'sources': sources,
        'product_types': Source.objects.values_list('product_type', flat=True).distinct(),
        'selected_type': product_type,
        'search_query': search,
    }
    
    return render(request, 'dashboard/sources/compare.html', context)

@staff_member_required
def add_source_product(request):
    """Thêm sản phẩm từ nguồn"""
    if request.method == 'POST':
        source_id = request.POST.get('source_id')
        product_id = request.POST.get('product_id', None)
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        product_url = request.POST.get('product_url', '')
        price = request.POST.get('price')
        error_rate = request.POST.get('error_rate', 0)
        
        source = get_object_or_404(Source, id=source_id)
        product = None
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            
        source_product = SourceProduct.objects.create(
            source=source,
            product=product,
            name=name,
            description=description,
            product_url=product_url,
            price=price,
            error_rate=error_rate
        )
        
        messages.success(request, f'Đã thêm sản phẩm "{name}" cho nguồn {source.name}')
        return redirect('dashboard:source_detail', source_id=source.id)
    
    sources = Source.objects.all()
    products = Product.objects.all()
    
    return render(request, 'dashboard/sources/add_product.html', {
        'sources': sources,
        'products': products
    })

@staff_member_required
def add_source_log(request):
    """Thêm log hoạt động với nguồn"""
    if request.method == 'POST':
        source_id = request.POST.get('source_id')
        source_product_id = request.POST.get('source_product_id', None)
        log_type = request.POST.get('log_type')
        has_stock = request.POST.get('has_stock') == 'on'
        processing_time = request.POST.get('processing_time', None)
        notes = request.POST.get('notes', '')
        
        source = get_object_or_404(Source, id=source_id)
        source_product = None
        if source_product_id:
            source_product = get_object_or_404(SourceProduct, id=source_product_id)
            
        source_log = SourceLog.objects.create(
            source=source,
            source_product=source_product,
            log_type=log_type,
            has_stock=has_stock,
            processing_time=processing_time,
            notes=notes,
            created_by=request.user
        )
        
        messages.success(request, f'Đã thêm log {log_type} cho nguồn {source.name}')
        return redirect('dashboard:source_detail', source_id=source.id)
    
    sources = Source.objects.all()
    return render(request, 'dashboard/sources/add_log.html', {
        'sources': sources
    })

@staff_member_required
def api_source_products(request, source_id):
    """API trả về danh sách sản phẩm theo nguồn"""
    source = get_object_or_404(Source, id=source_id)
    products = SourceProduct.objects.filter(source=source)
    
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
        })
    
    return JsonResponse({'products': products_data}) 