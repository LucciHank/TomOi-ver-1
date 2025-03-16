from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from dashboard.models.source import Source, SourceProduct
from dashboard.models.product import Product

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