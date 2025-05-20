from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count
from django.utils.text import slugify
from django.urls import reverse

from ..models.product_attribute import ProductAttribute, AttributeValue
from ..forms import ProductAttributeForm, AttributeValueForm

@staff_member_required
def attribute_list(request):
    """Hiển thị danh sách các thuộc tính sản phẩm"""
    attributes = ProductAttribute.objects.annotate(
        value_count=Count('attribute_values')
    ).order_by('display_order', 'name')
    
    context = {
        'attributes': attributes,
        'title': 'Quản lý thuộc tính sản phẩm',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/attributes/list.html', context)

@staff_member_required
def add_attribute(request):
    """Thêm thuộc tính sản phẩm mới"""
    if request.method == 'POST':
        form = ProductAttributeForm(request.POST)
        if form.is_valid():
            attribute = form.save()
            messages.success(request, f'Đã thêm thuộc tính "{attribute.name}" thành công')
            return redirect('dashboard:attribute_list')
    else:
        form = ProductAttributeForm(initial={'is_active': True, 'display_order': 0})
    
    context = {
        'form': form,
        'title': 'Thêm thuộc tính sản phẩm',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/attributes/add.html', context)

@staff_member_required
def edit_attribute(request, attribute_id):
    """Chỉnh sửa thuộc tính sản phẩm"""
    attribute = get_object_or_404(ProductAttribute, id=attribute_id)
    attribute_values = AttributeValue.objects.filter(attribute=attribute).order_by('display_order')
    
    if request.method == 'POST':
        form = ProductAttributeForm(request.POST, instance=attribute)
        print(f"Form data: {request.POST}")
        print(f"Form is valid: {form.is_valid()}")
        if form.is_valid():
            print(f"Form cleaned data: {form.cleaned_data}")
            try:
                attribute = form.save(commit=False)
                attribute.save()
                print(f"Attribute saved: {attribute.id}, {attribute.name}, active: {attribute.is_active}")
                messages.success(request, f'Đã cập nhật thuộc tính "{attribute.name}" thành công')
                return redirect('dashboard:attribute_list')
            except Exception as e:
                print(f"Error saving attribute: {e}")
                messages.error(request, f'Lỗi khi lưu thuộc tính: {e}')
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, f'Lỗi dữ liệu: {form.errors}')
    else:
        form = ProductAttributeForm(instance=attribute)
    
    context = {
        'form': form,
        'attribute': attribute,
        'attribute_values': attribute_values,
        'title': f'Chỉnh sửa thuộc tính: {attribute.name}',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/attributes/edit.html', context)

@staff_member_required
def delete_attribute(request, attribute_id):
    """Xóa thuộc tính sản phẩm"""
    attribute = get_object_or_404(ProductAttribute, id=attribute_id)
    attribute_values_count = AttributeValue.objects.filter(attribute=attribute).count()
    
    # Check if attribute is used in any products
    products_count = 0  # Implement this based on your data model
    
    if request.method == 'POST':
        attribute_name = attribute.name
        attribute.delete()
        messages.success(request, f'Đã xóa thuộc tính "{attribute_name}" thành công')
        return redirect('dashboard:attribute_list')
    
    context = {
        'attribute': attribute,
        'attribute_values_count': attribute_values_count,
        'products_count': products_count,
        'title': f'Xóa thuộc tính: {attribute.name}',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/attributes/delete.html', context)

@staff_member_required
def attribute_values(request, attribute_id):
    """Hiển thị danh sách các giá trị của thuộc tính"""
    attribute = get_object_or_404(ProductAttribute, id=attribute_id)
    attribute_values = AttributeValue.objects.filter(attribute=attribute).order_by('display_order')
    
    context = {
        'attribute': attribute,
        'attribute_values': attribute_values,
        'title': f'Giá trị của thuộc tính: {attribute.name}',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/attributes/values/list.html', context)

@staff_member_required
def add_attribute_value(request, attribute_id):
    """Thêm giá trị cho thuộc tính"""
    attribute = get_object_or_404(ProductAttribute, id=attribute_id)
    
    if request.method == 'POST':
        form = AttributeValueForm(request.POST)
        if form.is_valid():
            value = form.save(commit=False)
            value.attribute = attribute
            value.save()
            messages.success(request, f'Đã thêm giá trị "{value.value}" cho thuộc tính "{attribute.name}" thành công')
            return redirect('dashboard:edit_attribute', attribute_id=attribute.id)
    else:
        # Get the highest display_order and increment by 10
        last_order = AttributeValue.objects.filter(attribute=attribute).order_by('-display_order').first()
        initial_order = 10 if not last_order else last_order.display_order + 10
        
        form = AttributeValueForm(initial={
            'is_active': True,
            'display_order': initial_order
        })
    
    context = {
        'form': form,
        'attribute': attribute,
        'title': f'Thêm giá trị cho thuộc tính: {attribute.name}',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/attributes/values/add.html', context)

@staff_member_required
def edit_attribute_value(request, value_id):
    """Chỉnh sửa giá trị thuộc tính"""
    attribute_value = get_object_or_404(AttributeValue, id=value_id)
    attribute = attribute_value.attribute
    
    if request.method == 'POST':
        form = AttributeValueForm(request.POST, instance=attribute_value)
        print(f"Form data for attribute value: {request.POST}")
        print(f"Form is valid: {form.is_valid()}")
        if form.is_valid():
            print(f"Form cleaned data: {form.cleaned_data}")
            try:
                value = form.save(commit=False)
                value.attribute = attribute  # Đảm bảo thuộc tính được gán đúng
                value.save()
                print(f"Attribute value saved: {value.id}, {value.value}, active: {value.is_active}")
                messages.success(request, f'Đã cập nhật giá trị thuộc tính thành công')
                return redirect('dashboard:edit_attribute', attribute_id=attribute.id)
            except Exception as e:
                print(f"Error saving attribute value: {e}")
                messages.error(request, f'Lỗi khi lưu giá trị thuộc tính: {e}')
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, f'Lỗi dữ liệu: {form.errors}')
    else:
        form = AttributeValueForm(instance=attribute_value)
    
    context = {
        'form': form,
        'attribute_value': attribute_value,
        'attribute': attribute,
        'title': f'Chỉnh sửa giá trị thuộc tính: {attribute_value.value}',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/attributes/values/edit.html', context)

@staff_member_required
def delete_attribute_value(request, value_id):
    """Xóa giá trị thuộc tính"""
    attribute_value = get_object_or_404(AttributeValue, id=value_id)
    attribute = attribute_value.attribute
    
    # Check if value is used in any products
    products_count = 0  # Implement this based on your data model
    
    if request.method == 'POST':
        value_text = attribute_value.value
        attribute_value.delete()
        messages.success(request, f'Đã xóa giá trị "{value_text}" thành công')
        return redirect('dashboard:edit_attribute', attribute_id=attribute.id)
    
    context = {
        'attribute_value': attribute_value,
        'attribute': attribute,
        'products_count': products_count,
        'title': f'Xóa giá trị thuộc tính: {attribute_value.value}',
        'active_tab': 'products'
    }
    
    return render(request, 'dashboard/products/attributes/values/delete.html', context) 
 
 