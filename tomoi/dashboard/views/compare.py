from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from dashboard.models.source import Source

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