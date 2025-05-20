from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, F

from dashboard.models.supplier import Supplier
from store.models import Product

@staff_member_required
def supplier_list(request):
    """Danh sách nhà cung cấp"""
    suppliers = Supplier.objects.all()
    
    # Tìm kiếm
    search_query = request.GET.get('search', '')
    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) | 
            Q(code__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Lọc theo trạng thái
    status_filter = request.GET.get('status', '')
    if status_filter:
        suppliers = suppliers.filter(status=status_filter)
    
    # Phân trang
    paginator = Paginator(suppliers, 10)
    page = request.GET.get('page', 1)
    suppliers = paginator.get_page(page)
    
    # Lấy số lượng sản phẩm từ mỗi nhà cung cấp
    product_counts = {}
    for supplier in suppliers:
        count = supplier.products.count()
        product_counts[supplier.id] = count
    
    context = {
        'suppliers': suppliers,
        'search_query': search_query,
        'status_filter': status_filter,
        'product_counts': product_counts,
        'active_tab': 'suppliers',
        'title': 'Danh sách nhà cung cấp'
    }
    
    return render(request, 'dashboard/suppliers/list.html', context)

@staff_member_required
def supplier_add(request):
    """Thêm nhà cung cấp mới"""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        code = request.POST.get('code', '')
        contact_person = request.POST.get('contact_person', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        website = request.POST.get('website', '')
        status = request.POST.get('status', 'active')
        payment_method = request.POST.get('payment_method', 'bank')
        payment_term = request.POST.get('payment_term', 0)
        notes = request.POST.get('notes', '')
        
        # Validate dữ liệu
        if not name:
            messages.error(request, 'Vui lòng nhập tên nhà cung cấp')
            return render(request, 'dashboard/suppliers/add.html', {
                'active_tab': 'suppliers',
                'title': 'Thêm nhà cung cấp',
                'form_data': request.POST
            })
        
        # Kiểm tra trùng lặp
        if code and Supplier.objects.filter(code=code).exists():
            messages.error(request, f'Mã nhà cung cấp "{code}" đã tồn tại')
            return render(request, 'dashboard/suppliers/add.html', {
                'active_tab': 'suppliers',
                'title': 'Thêm nhà cung cấp',
                'form_data': request.POST
            })
        
        # Tạo nhà cung cấp mới
        supplier = Supplier(
            name=name,
            code=code,
            contact_person=contact_person,
            phone=phone,
            email=email,
            address=address,
            website=website,
            status=status,
            payment_method=payment_method,
            payment_term=int(payment_term) if payment_term else 0,
            notes=notes
        )
        
        try:
            supplier.save()
            messages.success(request, f'Đã thêm nhà cung cấp "{name}" thành công')
            return redirect('dashboard:supplier_list')
        except Exception as e:
            messages.error(request, f'Lỗi khi lưu nhà cung cấp: {str(e)}')
    
    context = {
        'active_tab': 'suppliers',
        'title': 'Thêm nhà cung cấp'
    }
    
    return render(request, 'dashboard/suppliers/add.html', context)

@staff_member_required
def supplier_edit(request, supplier_id):
    """Chỉnh sửa nhà cung cấp"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '')
        code = request.POST.get('code', '')
        contact_person = request.POST.get('contact_person', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        website = request.POST.get('website', '')
        status = request.POST.get('status', 'active')
        payment_method = request.POST.get('payment_method', 'bank')
        payment_term = request.POST.get('payment_term', 0)
        notes = request.POST.get('notes', '')
        
        # Validate dữ liệu
        if not name:
            messages.error(request, 'Vui lòng nhập tên nhà cung cấp')
            return render(request, 'dashboard/suppliers/edit.html', {
                'active_tab': 'suppliers',
                'title': f'Chỉnh sửa nhà cung cấp: {supplier.name}',
                'supplier': supplier,
                'form_data': request.POST
            })
        
        # Kiểm tra trùng lặp mã
        if code and code != supplier.code and Supplier.objects.filter(code=code).exists():
            messages.error(request, f'Mã nhà cung cấp "{code}" đã tồn tại')
            return render(request, 'dashboard/suppliers/edit.html', {
                'active_tab': 'suppliers',
                'title': f'Chỉnh sửa nhà cung cấp: {supplier.name}',
                'supplier': supplier,
                'form_data': request.POST
            })
        
        # Cập nhật thông tin
        supplier.name = name
        supplier.code = code
        supplier.contact_person = contact_person
        supplier.phone = phone
        supplier.email = email
        supplier.address = address
        supplier.website = website
        supplier.status = status
        supplier.payment_method = payment_method
        supplier.payment_term = int(payment_term) if payment_term else 0
        supplier.notes = notes
        
        try:
            supplier.save()
            messages.success(request, f'Đã cập nhật nhà cung cấp "{name}" thành công')
            return redirect('dashboard:supplier_list')
        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật nhà cung cấp: {str(e)}')
    
    context = {
        'supplier': supplier,
        'active_tab': 'suppliers',
        'title': f'Chỉnh sửa nhà cung cấp: {supplier.name}'
    }
    
    return render(request, 'dashboard/suppliers/edit.html', context)

@staff_member_required
def supplier_detail(request, supplier_id):
    """Chi tiết nhà cung cấp"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    # Lấy danh sách sản phẩm từ nhà cung cấp này - sử dụng related_name products
    products = supplier.products.all()
    
    # Phân trang cho sản phẩm
    paginator = Paginator(products, 10)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)
    
    context = {
        'supplier': supplier,
        'products': products,
        'active_tab': 'suppliers',
        'title': f'Chi tiết nhà cung cấp: {supplier.name}'
    }
    
    return render(request, 'dashboard/suppliers/detail.html', context)

@staff_member_required
def supplier_delete(request, supplier_id):
    """Xóa nhà cung cấp"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        supplier_name = supplier.name
        
        # Kiểm tra xem có sản phẩm nào sử dụng nhà cung cấp này không
        products_count = supplier.products.count()
        if products_count > 0:
            messages.error(request, f'Không thể xóa nhà cung cấp "{supplier_name}" vì có {products_count} sản phẩm đang liên kết')
            return redirect('dashboard:supplier_detail', supplier_id=supplier_id)
        
        try:
            supplier.delete()
            messages.success(request, f'Đã xóa nhà cung cấp "{supplier_name}" thành công')
            return redirect('dashboard:supplier_list')
        except Exception as e:
            messages.error(request, f'Lỗi khi xóa nhà cung cấp: {str(e)}')
            return redirect('dashboard:supplier_detail', supplier_id=supplier_id)
    
    context = {
        'supplier': supplier,
        'active_tab': 'suppliers',
        'title': f'Xác nhận xóa nhà cung cấp: {supplier.name}'
    }
    
    return render(request, 'dashboard/suppliers/delete.html', context) 
 
 