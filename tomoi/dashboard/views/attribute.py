from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.text import slugify
from django.http import JsonResponse
from django.db.models import Count
from django.urls import reverse

from ..models.product_attribute import ProductAttribute, AttributeValue
from ..forms import ProductAttributeForm, AttributeValueForm


# Sử dụng tất cả các view từ product_attribute.py để đảm bảo nhất quán
from .product_attribute import (
    attribute_list, 
    add_attribute, 
    edit_attribute, 
    delete_attribute,
    attribute_values,
    add_attribute_value,
    edit_attribute_value,
    delete_attribute_value
) 
@staff_member_required
def attributes(request):
    """Quản lý thuộc tính sản phẩm"""
    if request.method == 'POST':
        # Xử lý thêm thuộc tính mới
        name = request.POST.get('name', '')
        slug = request.POST.get('slug', '')
        description = request.POST.get('description', '')
        values = request.POST.getlist('values[]', [])
        
        if not slug:
            slug = slugify(name)
        
        # Tạo thuộc tính mới
        attribute = ProductAttribute(
            name=name,
            slug=slug,
            description=description
        )
        attribute.save()
        
        # Thêm các giá trị thuộc tính
        for i, value in enumerate(values):
            if value.strip():
                AttributeValue.objects.create(
                    attribute=attribute,
                    value=value.strip(),
                    display_order=i
                )
        
        messages.success(request, f'Đã thêm thuộc tính {name} thành công')
        return redirect('dashboard:attributes')
    
    # Lấy danh sách thuộc tính
    attributes = ProductAttribute.objects.all()
    
    context = {
        'attributes': attributes,
        'title': 'Quản lý thuộc tính sản phẩm',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/attributes.html', context)


@staff_member_required
def add_attribute(request):
    """Thêm thuộc tính mới"""
    if request.method == 'POST':
        # Xử lý thêm thuộc tính mới
        name = request.POST.get('name', '')
        slug = request.POST.get('slug', '')
        description = request.POST.get('description', '')
        values = request.POST.getlist('values[]', [])
        
        if not slug:
            slug = slugify(name)
        
        # Tạo thuộc tính mới
        attribute = ProductAttribute(
            name=name,
            slug=slug,
            description=description
        )
        attribute.save()
        
        # Thêm các giá trị thuộc tính
        for i, value in enumerate(values):
            if value.strip():
                AttributeValue.objects.create(
                    attribute=attribute,
                    value=value.strip(),
                    display_order=i
                )
        
        return JsonResponse({'success': True, 'attribute_id': attribute.id})
    
    return JsonResponse({'success': False, 'error': 'Yêu cầu không hợp lệ'})


@staff_member_required
def edit_attribute(request, attribute_id):
    """Sửa thuộc tính"""
    attribute = get_object_or_404(ProductAttribute, id=attribute_id)
    
    if request.method == 'POST':
        # Cập nhật thông tin
        attribute.name = request.POST.get('name', attribute.name)
        attribute.description = request.POST.get('description', attribute.description)
        
        # Cập nhật slug nếu được cung cấp
        slug = request.POST.get('slug', '')
        if slug:
            attribute.slug = slug
            
        attribute.save()
        
        # Xử lý cập nhật giá trị thuộc tính
        current_values = list(attribute.values.all())
        updated_values = request.POST.getlist('values[]', [])
        existing_ids = request.POST.getlist('value_ids[]', [])
        
        # Cập nhật và thêm mới giá trị
        for i, value_text in enumerate(updated_values):
            if i < len(existing_ids) and existing_ids[i]:
                # Cập nhật giá trị hiện có
                value_id = int(existing_ids[i])
                value = get_object_or_404(AttributeValue, id=value_id)
                value.value = value_text
                value.display_order = i
                value.save()
            else:
                # Thêm giá trị mới
                if value_text.strip():
                    AttributeValue.objects.create(
                        attribute=attribute,
                        value=value_text.strip(),
                        display_order=i
                    )
        
        # Xóa giá trị bị loại bỏ
        value_ids_to_keep = [int(vid) for vid in existing_ids if vid]
        AttributeValue.objects.filter(attribute=attribute).exclude(id__in=value_ids_to_keep).delete()
        
        messages.success(request, f'Đã cập nhật thuộc tính {attribute.name} thành công')
        return redirect('dashboard:attributes')
    
    context = {
        'attribute': attribute,
        'values': attribute.values.all().order_by('display_order'),
        'title': f'Chỉnh sửa thuộc tính: {attribute.name}',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/edit_attribute.html', context)


@staff_member_required
def delete_attribute(request, attribute_id):
    """Xóa thuộc tính"""
    attribute = get_object_or_404(ProductAttribute, id=attribute_id)
    
    if request.method == 'POST':
        attribute_name = attribute.name
        attribute.delete()
        messages.success(request, f'Đã xóa thuộc tính {attribute_name} thành công')
        return redirect('dashboard:attributes')
    
    return JsonResponse({'success': True})


@staff_member_required
def add_attribute_value(request, attribute_id):
    """Thêm giá trị thuộc tính"""
    attribute = get_object_or_404(ProductAttribute, id=attribute_id)
    
    if request.method == 'POST':
        value = request.POST.get('value', '')
        if value.strip():
            # Xác định thứ tự hiển thị
            display_order = attribute.values.count()
            
            # Tạo giá trị mới
            attr_value = AttributeValue.objects.create(
                attribute=attribute,
                value=value.strip(),
                display_order=display_order
            )
            
            return JsonResponse({
                'success': True, 
                'value_id': attr_value.id,
                'value': attr_value.value
            })
    
    return JsonResponse({'success': False, 'error': 'Giá trị thuộc tính không hợp lệ'})


@staff_member_required
def delete_attribute_value(request, value_id):
    """Xóa giá trị thuộc tính"""
    value = get_object_or_404(AttributeValue, id=value_id)
    attribute_id = value.attribute.id
    
    if request.method == 'POST':
        value.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Yêu cầu không hợp lệ'}) 