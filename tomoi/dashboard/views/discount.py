from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count
import json
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import user_passes_test, login_required
from accounts.models import CustomUser
from store.models import Product, Category, Discount
from dashboard.models.discount import DiscountHistory, DiscountBackup
from dashboard.forms import DiscountImportForm, DiscountExportForm, DiscountBackupForm, DiscountRestoreForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, date, time
from django.conf import settings
from django.http import HttpResponse

# Giả sử chúng ta có model Discount, Product, Category, và User
# từ ứng dụng phù hợp trong dự án
from store.models import Discount
# Nếu không có model Discount, giả định chúng ta cần tạo nó

# Đảm bảo mẫu discount model đã được tạo
try:
    from store.models import Discount
    HAS_DISCOUNT_MODEL = True
except ImportError:
    HAS_DISCOUNT_MODEL = False

@staff_member_required
@login_required
def discount_list(request):
    context = {
        'active_menu': 'discounts',
    }
    
    if HAS_DISCOUNT_MODEL:
        discounts = Discount.objects.all().order_by('-created_at')
        context['discounts'] = discounts
    else:
        context['model_missing'] = True
        
    return render(request, 'dashboard/discounts/list.html', context)

@staff_member_required
@login_required
def discount_add(request):
    context = {
        'active_menu': 'discounts',
        'is_add': True
    }
    
    if not HAS_DISCOUNT_MODEL:
        messages.error(request, "Mô hình Discount chưa được cài đặt trong hệ thống.")
        return redirect('dashboard:discounts')
    
    # Lấy danh sách sản phẩm và danh mục cho form
    context['products'] = Product.objects.all()
    context['categories'] = Category.objects.all()
    context['users'] = CustomUser.objects.all()
    
    if request.method == 'POST':
        # Xử lý form dữ liệu
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        discount_type = request.POST.get('discount_type')
        value = request.POST.get('value')
        max_uses = request.POST.get('max_uses', 0)
        uses_per_customer = request.POST.get('uses_per_customer', 1)
        min_purchase = request.POST.get('min_purchase', 0)
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        is_active = 'is_active' in request.POST
        
        # Kiểm tra các trường bắt buộc
        if not all([code, discount_type, value, valid_from, valid_to]):
            messages.error(request, "Vui lòng điền đầy đủ các trường bắt buộc.")
            context['form'] = request.POST
            return render(request, 'dashboard/discounts/form.html', context)
        
        # Kiểm tra mã giảm giá đã tồn tại chưa
        if Discount.objects.filter(code=code).exists():
            messages.error(request, f"Mã giảm giá '{code}' đã tồn tại.")
            context['form'] = request.POST
            return render(request, 'dashboard/discounts/form.html', context)
        
        try:
            # Tạo mã giảm giá mới
            discount = Discount.objects.create(
                code=code,
                description=description,
                discount_type=discount_type,
                value=value,
                max_uses=max_uses,
                uses_per_customer=uses_per_customer,
                min_purchase=min_purchase,
                valid_from=valid_from,
                valid_to=valid_to,
                is_active=is_active
            )
            
            # Xử lý các sản phẩm được áp dụng
            products = request.POST.getlist('products')
            if products:
                discount.products.set(products)
            
            # Xử lý các danh mục được áp dụng
            categories = request.POST.getlist('categories')
            if categories:
                discount.categories.set(categories)
            
            # Xử lý người dùng được phép sử dụng
            allowed_users = request.POST.getlist('allowed_users')
            if 'all' not in allowed_users and allowed_users:
                # Nếu được chọn người dùng cụ thể
                discount.allowed_users.set(allowed_users)
            
            messages.success(request, f"Đã tạo mã giảm giá '{code}' thành công.")
            return redirect('dashboard:discounts')
            
        except Exception as e:
            messages.error(request, f"Lỗi khi tạo mã giảm giá: {str(e)}")
            context['form'] = request.POST
    
    return render(request, 'dashboard/discounts/form.html', context)

@staff_member_required
@login_required
def discount_edit(request, discount_id):
    if not HAS_DISCOUNT_MODEL:
        messages.error(request, "Mô hình Discount chưa được cài đặt trong hệ thống.")
        return redirect('dashboard:discounts')
    
    discount = get_object_or_404(Discount, id=discount_id)
    
    context = {
        'active_menu': 'discounts',
        'is_add': False,
        'discount': discount,
        'products': Product.objects.all(),
        'categories': Category.objects.all(),
        'users': CustomUser.objects.all(),
        'form': {
            'code': discount.code,
            'description': discount.description,
            'discount_type': discount.discount_type,
            'value': discount.value,
            'max_uses': discount.max_uses,
            'uses_per_customer': discount.uses_per_customer,
            'min_purchase': discount.min_purchase,
            'valid_from': discount.valid_from,
            'valid_to': discount.valid_to,
            'is_active': discount.is_active,
            'products': [p.id for p in discount.products.all()],
            'categories': [c.id for c in discount.categories.all()],
            'allowed_users': ['all'] if not discount.allowed_users.exists() else [u.id for u in discount.allowed_users.all()]
        }
    }
    
    if request.method == 'POST':
        # Cập nhật thông tin mã giảm giá
        description = request.POST.get('description', '')
        discount_type = request.POST.get('discount_type')
        value = request.POST.get('value')
        max_uses = request.POST.get('max_uses', 0)
        uses_per_customer = request.POST.get('uses_per_customer', 1)
        min_purchase = request.POST.get('min_purchase', 0)
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        is_active = 'is_active' in request.POST
        
        # Kiểm tra các trường bắt buộc
        if not all([discount_type, value, valid_from, valid_to]):
            messages.error(request, "Vui lòng điền đầy đủ các trường bắt buộc.")
            return render(request, 'dashboard/discounts/form.html', context)
        
        try:
            # Cập nhật mã giảm giá
            discount.description = description
            discount.discount_type = discount_type
            discount.value = value
            discount.max_uses = max_uses
            discount.uses_per_customer = uses_per_customer
            discount.min_purchase = min_purchase
            discount.valid_from = valid_from
            discount.valid_to = valid_to
            discount.is_active = is_active
            discount.save()
            
            # Cập nhật sản phẩm được áp dụng
            products = request.POST.getlist('products')
            discount.products.clear()
            if products:
                discount.products.set(products)
            
            # Cập nhật danh mục được áp dụng
            categories = request.POST.getlist('categories')
            discount.categories.clear()
            if categories:
                discount.categories.set(categories)
            
            # Cập nhật người dùng được phép sử dụng
            allowed_users = request.POST.getlist('allowed_users')
            discount.allowed_users.clear()
            if 'all' not in allowed_users and allowed_users:
                # Nếu được chọn người dùng cụ thể
                discount.allowed_users.set(allowed_users)
            
            messages.success(request, f"Đã cập nhật mã giảm giá '{discount.code}' thành công.")
            return redirect('dashboard:discounts')
            
        except Exception as e:
            messages.error(request, f"Lỗi khi cập nhật mã giảm giá: {str(e)}")
    
    return render(request, 'dashboard/discounts/form.html', context)

@staff_member_required
@login_required
def discount_delete(request, discount_id):
    if not HAS_DISCOUNT_MODEL:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Mô hình Discount chưa được cài đặt.'})
        messages.error(request, "Mô hình Discount chưa được cài đặt trong hệ thống.")
        return redirect('dashboard:discounts')
    
    discount = get_object_or_404(Discount, id=discount_id)
    
    try:
        code = discount.code
        discount.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': f"Đã xóa mã giảm giá '{code}' thành công."})
        
        messages.success(request, f"Đã xóa mã giảm giá '{code}' thành công.")
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': f"Lỗi khi xóa mã giảm giá: {str(e)}"})
        
        messages.error(request, f"Lỗi khi xóa mã giảm giá: {str(e)}")
    
    return redirect('dashboard:discounts')

@staff_member_required
@login_required
def toggle_discount(request, discount_id):
    if not HAS_DISCOUNT_MODEL:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Mô hình Discount chưa được cài đặt.'})
        messages.error(request, "Mô hình Discount chưa được cài đặt trong hệ thống.")
        return redirect('dashboard:discounts')
    
    discount = get_object_or_404(Discount, id=discount_id)
    
    try:
        discount.is_active = not discount.is_active
        discount.save()
        
        status_text = "kích hoạt" if discount.is_active else "vô hiệu hóa"
        success_message = f"Đã {status_text} mã giảm giá '{discount.code}' thành công."
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success', 
                'message': success_message, 
                'is_active': discount.is_active
            })
        
        messages.success(request, success_message)
    except Exception as e:
        error_message = f"Lỗi khi thay đổi trạng thái mã giảm giá: {str(e)}"
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': error_message})
        
        messages.error(request, error_message)
    
    return redirect('dashboard:discounts')

@staff_member_required
@login_required
def discount_report(request):
    context = {
        'active_menu': 'discounts',
        'active_submenu': 'discount_report',
    }
    
    if not HAS_DISCOUNT_MODEL:
        context['model_missing'] = True
        return render(request, 'dashboard/discounts/report.html', context)
    
    # Lấy tất cả mã giảm giá
    discounts = Discount.objects.all()
    
    # Tổng số mã giảm giá
    total_discounts = discounts.count()
    
    # Số mã đang hoạt động
    active_discounts = discounts.filter(is_active=True).count()
    
    # Số mã hết hạn
    expired_discounts = discounts.filter(valid_to__lt=timezone.now()).count()
    
    # Thống kê theo loại giảm giá
    discount_types = discounts.values('discount_type').annotate(count=Count('id'))

    # Mã giảm giá được sử dụng nhiều nhất (dự trù trong tương lai khi có thống kê lịch sử sử dụng)
    # top_discounts = Discount.objects.annotate(usage_count=Count('usage')).order_by('-usage_count')[:5]
    
    context.update({
        'total_discounts': total_discounts,
        'active_discounts': active_discounts,
        'expired_discounts': expired_discounts,
        'discount_types': discount_types,
        # 'top_discounts': top_discounts,
        'discounts': discounts,
    })
    
    return render(request, 'dashboard/discounts/report.html', context)

@staff_member_required
@login_required
def discount_dashboard(request):
    context = {
        'active_menu': 'discounts',
        'active_submenu': 'discount_dashboard',
    }
    
    if not HAS_DISCOUNT_MODEL:
        context['model_missing'] = True
        return render(request, 'dashboard/discounts/dashboard.html', context)
    
    # Lấy tất cả mã giảm giá
    discounts = Discount.objects.all()
    
    # Thống kê cơ bản
    total_discounts = discounts.count()
    active_discounts = discounts.filter(is_active=True).count()
    expired_discounts = discounts.filter(valid_to__lt=timezone.now()).count()
    
    # Mã giảm giá sắp hết hạn (trong vòng 7 ngày)
    now = timezone.now()
    next_week = now + timezone.timedelta(days=7)
    expiring_soon = discounts.filter(valid_to__range=[now, next_week]).count()
    
    # Mã giảm giá mới tạo (trong 30 ngày qua)
    last_month = now - timezone.timedelta(days=30)
    new_discounts = discounts.filter(created_at__gte=last_month).count()
    
    # Mã giảm giá gần đây nhất
    recent_discounts = discounts.order_by('-created_at')[:10]
    
    context.update({
        'total_discounts': total_discounts,
        'active_discounts': active_discounts,
        'inactive_discounts': total_discounts - active_discounts,
        'expired_discounts': expired_discounts,
        'expiring_soon': expiring_soon,
        'new_discounts': new_discounts,
        'recent_discounts': recent_discounts,
    })
    
    return render(request, 'dashboard/discounts/dashboard.html', context)

@staff_member_required
@login_required
def discount_history(request):
    """
    Hiển thị lịch sử thay đổi mã giảm giá
    """
    # Lấy các tham số lọc từ request
    code = request.GET.get('code', '')
    action_type = request.GET.get('action', '')
    user_id = request.GET.get('user', '')
    date = request.GET.get('date', '')
    
    # Truy vấn cơ bản
    history_query = DiscountHistory.objects.all().order_by('-created_at')
    
    # Áp dụng các bộ lọc
    if code:
        history_query = history_query.filter(discount_code__icontains=code)
    
    if action_type:
        history_query = history_query.filter(action_type=action_type)
    
    if user_id and user_id.isdigit():
        history_query = history_query.filter(user_id=int(user_id))
    
    if date:
        try:
            search_date = datetime.strptime(date, '%Y-%m-%d').date()
            history_query = history_query.filter(
                created_at__year=search_date.year,
                created_at__month=search_date.month,
                created_at__day=search_date.day
            )
        except ValueError:
            # Bỏ qua lỗi định dạng ngày
            pass
    
    # Phân trang
    paginator = Paginator(history_query, 20)  # 20 mục trên mỗi trang
    page = request.GET.get('page')
    
    try:
        history_entries = paginator.page(page)
    except PageNotAnInteger:
        history_entries = paginator.page(1)
    except EmptyPage:
        history_entries = paginator.page(paginator.num_pages)
    
    # Lấy danh sách người dùng cho bộ lọc
    users = CustomUser.objects.filter(
        id__in=DiscountHistory.objects.values_list('user', flat=True).distinct()
    )
    
    context = {
        'title': 'Lịch sử mã giảm giá',
        'history_entries': history_entries,
        'users': users,
        'is_paginated': history_entries.has_other_pages(),
        'page_obj': history_entries,
    }
    
    return render(request, 'dashboard/discounts/history.html', context)

@staff_member_required
@login_required
def import_discounts(request):
    """
    Nhập mã giảm giá từ file Excel hoặc CSV
    """
    if request.method == 'POST':
        form = DiscountImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            import_type = form.cleaned_data['import_type']
            skip_first_row = form.cleaned_data['skip_first_row']
            
            try:
                # Xử lý file Excel hoặc CSV
                if file.name.endswith('.xlsx'):
                    data = process_excel_file(file, skip_first_row)
                else:  # CSV
                    data = process_csv_file(file, skip_first_row)
                
                # Thay thế toàn bộ dữ liệu nếu chọn
                if import_type == 'replace':
                    Discount.objects.all().delete()
                
                # Nhập dữ liệu
                imported_count = 0
                error_count = 0
                error_messages = []
                
                for row in data:
                    try:
                        # Kiểm tra mã giảm giá đã tồn tại chưa
                        if Discount.objects.filter(code=row.get('code')).exists() and import_type == 'append':
                            error_count += 1
                            error_messages.append(f"Mã '{row.get('code')}' đã tồn tại.")
                            continue
                        
                        # Chuyển đổi giá trị
                        discount_value = float(row.get('discount_value', 0))
                        
                        # Xử lý ngày
                        start_date = None
                        if row.get('start_date'):
                            try:
                                start_date = parse_date(row.get('start_date'))
                            except ValueError:
                                start_date = None
                        
                        end_date = None
                        if row.get('end_date'):
                            try:
                                end_date = parse_date(row.get('end_date'))
                            except ValueError:
                                end_date = None
                        
                        # Tạo mã giảm giá mới
                        discount = Discount(
                            code=row.get('code'),
                            description=row.get('description', ''),
                            discount_type=row.get('discount_type', 'fixed'),
                            value=discount_value,
                            valid_from=start_date,
                            valid_to=end_date,
                            max_uses=int(row.get('usage_limit', 0) or 0),
                            min_purchase_value=float(row.get('min_purchase', 0) or 0),
                            is_active=bool(int(row.get('active', 1) or 1))
                        )
                        discount.save()
                        
                        # Ghi nhật ký
                        DiscountHistory.objects.create(
                            discount=discount,
                            discount_code=discount.code,
                            action_type='create',
                            user=request.user
                        )
                        
                        imported_count += 1
                    
                    except Exception as e:
                        error_count += 1
                        error_messages.append(f"Lỗi với mã '{row.get('code', 'không xác định')}': {str(e)}")
                
                # Hiển thị thông báo kết quả
                message = f"Đã nhập thành công {imported_count} mã giảm giá. "
                if error_count:
                    message += f"Có {error_count} lỗi xảy ra."
                    for error in error_messages[:5]:  # Chỉ hiển thị 5 lỗi đầu tiên
                        messages.warning(request, error)
                
                messages.success(request, message)
                
                if imported_count > 0 and error_count == 0:
                    return redirect('dashboard:discounts')
            
            except Exception as e:
                messages.error(request, f"Lỗi khi xử lý file: {str(e)}")
    else:
        form = DiscountImportForm()
    
    context = {
        'title': 'Nhập mã giảm giá',
        'form': form
    }
    
    return render(request, 'dashboard/discounts/import.html', context)

def process_excel_file(file, skip_first_row=True):
    """
    Xử lý file Excel và trả về danh sách các dòng dữ liệu
    """
    import pandas as pd
    
    df = pd.read_excel(file)
    if skip_first_row:
        df = df.iloc[1:]
    
    # Chuẩn hóa tên cột
    df.columns = [col.lower().strip() for col in df.columns]
    
    # Chuyển DataFrame thành danh sách dict
    data = df.to_dict('records')
    return data

def process_csv_file(file, skip_first_row=True):
    """
    Xử lý file CSV và trả về danh sách các dòng dữ liệu
    """
    import csv
    from io import TextIOWrapper
    
    data = []
    csv_file = TextIOWrapper(file, encoding='utf-8-sig')
    reader = csv.DictReader(csv_file)
    
    # Chuẩn hóa tên cột
    fieldnames = [field.lower().strip() for field in reader.fieldnames]
    
    for row_num, row in enumerate(reader):
        if skip_first_row and row_num == 0:
            continue
        
        # Tạo dict mới với tên cột chuẩn hóa
        normalized_row = {key.lower().strip(): value for key, value in row.items()}
        data.append(normalized_row)
    
    return data

def parse_date(date_str):
    """
    Chuyển đổi chuỗi ngày thành đối tượng date
    """
    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y']:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    # Nếu không chuyển đổi được, thử tách số
    import re
    parts = re.findall(r'\d+', date_str)
    if len(parts) >= 3:
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        if year < 100:
            year += 2000
        try:
            return date(year, month, day)
        except ValueError:
            pass
    
    raise ValueError(f"Không thể chuyển đổi '{date_str}' thành ngày")

@staff_member_required
@login_required
def export_discounts(request):
    """
    Xuất danh sách mã giảm giá ra file Excel hoặc CSV
    """
    if request.method == 'POST':
        form = DiscountExportForm(request.POST)
        if form.is_valid():
            export_type = form.cleaned_data['export_type']
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            status = form.cleaned_data['status']
            include_history = form.cleaned_data['include_history']
            
            # Lọc dữ liệu
            discounts = Discount.objects.all()
            
            if date_from:
                discounts = discounts.filter(created_at__gte=datetime.combine(date_from, time.min))
            
            if date_to:
                discounts = discounts.filter(created_at__lte=datetime.combine(date_to, time.max))
            
            if status == 'active':
                discounts = discounts.filter(is_active=True)
            elif status == 'inactive':
                discounts = discounts.filter(is_active=False)
            
            # Xuất file
            if export_type == 'xlsx':
                response = export_to_excel(discounts, include_history)
            else:  # CSV
                response = export_to_csv(discounts, include_history)
            
            return response
    else:
        form = DiscountExportForm()
    
    context = {
        'title': 'Xuất mã giảm giá',
        'form': form
    }
    
    return render(request, 'dashboard/discounts/export.html', context)

def export_to_excel(discounts, include_history=False):
    """
    Xuất danh sách mã giảm giá ra file Excel
    """
    import pandas as pd
    from django.http import HttpResponse
    from io import BytesIO
    
    # Chuẩn bị dữ liệu
    data = []
    for discount in discounts:
        item = {
            'Mã giảm giá': discount.code,
            'Mô tả': discount.description,
            'Loại giảm giá': 'Phần trăm (%)' if discount.discount_type == 'percentage' else 'Số tiền cố định',
            'Giá trị': discount.value,
            'Ngày bắt đầu': discount.valid_from,
            'Ngày kết thúc': discount.valid_to,
            'Giới hạn sử dụng': discount.max_uses,
            'Đã sử dụng': discount.used_count,
            'Giá trị đơn hàng tối thiểu': discount.min_purchase_value,
            'Trạng thái': 'Đang hoạt động' if discount.is_active else 'Không hoạt động',
            'Ngày tạo': discount.created_at.strftime('%d/%m/%Y %H:%M'),
        }
        data.append(item)
    
    # Tạo DataFrame
    df = pd.DataFrame(data)
    
    # Tạo file Excel
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Mã giảm giá', index=False)
    
    # Thêm sheet lịch sử sử dụng nếu cần
    if include_history:
        history_data = []
        for discount in discounts:
            usages = discount.usages.all()
            for usage in usages:
                history_data.append({
                    'Mã giảm giá': discount.code,
                    'Người dùng': usage.user.get_full_name() if usage.user else 'Khách vãng lai',
                    'Đơn hàng': usage.order.order_number if usage.order else 'N/A',
                    'Giá trị giảm': usage.amount,
                    'Thời gian sử dụng': usage.created_at.strftime('%d/%m/%Y %H:%M'),
                })
        
        if history_data:
            history_df = pd.DataFrame(history_data)
            history_df.to_excel(writer, sheet_name='Lịch sử sử dụng', index=False)
    
    writer.save()
    output.seek(0)
    
    # Tạo response
    filename = f'ma_giam_gia_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

def export_to_csv(discounts, include_history=False):
    """
    Xuất danh sách mã giảm giá ra file CSV
    """
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    filename = f'ma_giam_gia_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Mã giảm giá', 'Mô tả', 'Loại giảm giá', 'Giá trị', 'Ngày bắt đầu', 'Ngày kết thúc',
        'Giới hạn sử dụng', 'Đã sử dụng', 'Giá trị đơn hàng tối thiểu', 'Trạng thái', 'Ngày tạo'
    ])
    
    for discount in discounts:
        writer.writerow([
            discount.code,
            discount.description,
            'Phần trăm (%)' if discount.discount_type == 'percentage' else 'Số tiền cố định',
            discount.value,
            discount.valid_from,
            discount.valid_to,
            discount.max_uses,
            discount.used_count,
            discount.min_purchase_value,
            'Đang hoạt động' if discount.is_active else 'Không hoạt động',
            discount.created_at.strftime('%d/%m/%Y %H:%M'),
        ])
    
    # Thêm lịch sử sử dụng nếu cần
    if include_history:
        writer.writerow([])
        writer.writerow(['Lịch sử sử dụng'])
        writer.writerow(['Mã giảm giá', 'Người dùng', 'Đơn hàng', 'Giá trị giảm', 'Thời gian sử dụng'])
        
        for discount in discounts:
            usages = discount.usages.all()
            for usage in usages:
                writer.writerow([
                    discount.code,
                    usage.user.get_full_name() if usage.user else 'Khách vãng lai',
                    usage.order.order_number if usage.order else 'N/A',
                    usage.amount,
                    usage.created_at.strftime('%d/%m/%Y %H:%M'),
                ])
    
    return response

@staff_member_required
@login_required
def backup_discounts(request):
    """
    Tạo bản sao lưu mã giảm giá
    """
    if request.method == 'POST':
        form = DiscountBackupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['backup_name']
            include_usage = form.cleaned_data['include_usage']
            download_backup = form.cleaned_data['download_backup']
            
            try:
                # Lấy dữ liệu mã giảm giá
                discounts = Discount.objects.all()
                
                # Chuẩn bị dữ liệu JSON
                data = {
                    'metadata': {
                        'created_at': datetime.now().isoformat(),
                        'created_by': request.user.username,
                        'count': discounts.count(),
                        'include_usage': include_usage
                    },
                    'discounts': []
                }
                
                for discount in discounts:
                    discount_data = {
                        'code': discount.code,
                        'description': discount.description,
                        'discount_type': discount.discount_type,
                        'value': float(discount.value),
                        'valid_from': discount.valid_from.isoformat() if discount.valid_from else None,
                        'valid_to': discount.valid_to.isoformat() if discount.valid_to else None,
                        'max_uses': discount.max_uses,
                        'uses_per_customer': discount.uses_per_customer,
                        'min_purchase_value': float(discount.min_purchase_value),
                        'is_active': discount.is_active,
                        'created_at': discount.created_at.isoformat()
                    }
                    
                    # Thêm thông tin về lịch sử sử dụng
                    if include_usage:
                        usages = discount.usages.all()
                        discount_data['usages'] = [
                            {
                                'user_id': usage.user.id if usage.user else None,
                                'order_id': usage.order.id if usage.order else None,
                                'amount': float(usage.amount),
                                'created_at': usage.created_at.isoformat()
                            }
                            for usage in usages
                        ]
                    
                    data['discounts'].append(discount_data)
                
                # Lưu vào cơ sở dữ liệu
                backup_json = json.dumps(data, ensure_ascii=False)
                backup = DiscountBackup(
                    name=name,
                    backup_data=backup_json,
                    include_usage=include_usage,
                    created_by=request.user
                )
                
                # Lưu vào file nếu cần
                if download_backup:
                    import os
                    filename = f"discount_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
                    filepath = os.path.join(settings.MEDIA_ROOT, 'backups', filename)
                    
                    # Đảm bảo thư mục tồn tại
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(backup_json)
                    
                    backup.file_path = os.path.join('backups', filename)
                
                backup.save()
                
                messages.success(request, f"Đã sao lưu {discounts.count()} mã giảm giá thành công.")
                
                # Tải xuống file nếu cần
                if download_backup:
                    return redirect('dashboard:download_backup', id=backup.id)
                
                return redirect('dashboard:backup_discounts')
            
            except Exception as e:
                messages.error(request, f"Lỗi khi tạo bản sao lưu: {str(e)}")
    else:
        form = DiscountBackupForm()
    
    # Lấy danh sách các bản sao lưu
    backups = DiscountBackup.objects.all().order_by('-created_at')
    
    context = {
        'title': 'Sao lưu mã giảm giá',
        'form': form,
        'backups': backups
    }
    
    return render(request, 'dashboard/discounts/backup.html', context)

@staff_member_required
@login_required
def download_backup(request, id):
    """
    Tải xuống file sao lưu
    """
    try:
        backup = get_object_or_404(DiscountBackup, id=id)
        
        # Kiểm tra xem file có tồn tại trên đĩa không
        if backup.file_path:
            return redirect(f"{settings.MEDIA_URL}{backup.file_path}")
        
        # Nếu không có file, tạo response trực tiếp
        response = HttpResponse(
            backup.backup_data,
            content_type='application/json'
        )
        filename = f"discount_backup_{backup.created_at.strftime('%Y%m%d_%H%M')}.json"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    except Exception as e:
        messages.error(request, f"Lỗi khi tải file: {str(e)}")
        return redirect('dashboard:backup_discounts')

@staff_member_required
@login_required
def delete_backup(request, id):
    """
    Xóa bản sao lưu
    """
    if request.method == 'POST':
        try:
            backup = get_object_or_404(DiscountBackup, id=id)
            
            # Xóa file nếu có
            if backup.file_path:
                import os
                filepath = os.path.join(settings.MEDIA_ROOT, backup.file_path)
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            backup.delete()
            messages.success(request, "Đã xóa bản sao lưu thành công.")
        
        except Exception as e:
            messages.error(request, f"Lỗi khi xóa bản sao lưu: {str(e)}")
    
    return redirect('dashboard:backup_discounts')

@staff_member_required
@login_required
def restore_discounts(request):
    """
    Khôi phục mã giảm giá từ bản sao lưu
    """
    # Lấy danh sách bản sao lưu
    backups = DiscountBackup.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = DiscountRestoreForm(request.POST, request.FILES)
        if form.is_valid():
            restore_type = form.cleaned_data['restore_type']
            restore_option = form.cleaned_data['restore_option']
            include_usage = form.cleaned_data['include_usage']
            
            try:
                # Lấy dữ liệu từ nguồn
                if restore_type == 'existing':
                    backup_id = form.cleaned_data['backup_id']
                    if not backup_id:
                        messages.error(request, "Vui lòng chọn bản sao lưu để khôi phục.")
                        return redirect('dashboard:restore_discounts')
                    
                    backup = get_object_or_404(DiscountBackup, id=backup_id.id)
                    json_data = backup.backup_data
                
                else:  # upload
                    backup_file = request.FILES['backup_file']
                    json_data = backup_file.read().decode('utf-8')
                
                # Phân tích dữ liệu JSON
                data = json.loads(json_data)
                
                # Xác nhận đây là file sao lưu hợp lệ
                if 'metadata' not in data or 'discounts' not in data:
                    messages.error(request, "File sao lưu không hợp lệ.")
                    return redirect('dashboard:restore_discounts')
                
                # Xóa tất cả mã giảm giá hiện có nếu chọn thay thế
                if restore_option == 'replace':
                    Discount.objects.all().delete()
                
                # Khôi phục mã giảm giá
                restored_count = 0
                error_count = 0
                
                for discount_data in data['discounts']:
                    try:
                        code = discount_data['code']
                        
                        # Kiểm tra mã đã tồn tại chưa
                        if Discount.objects.filter(code=code).exists():
                            if restore_option == 'append':
                                # Bỏ qua nếu chọn thêm vào
                                continue
                            else:
                                # Xóa mã cũ nếu chọn thay thế
                                Discount.objects.filter(code=code).delete()
                        
                        # Chuyển đổi ngày
                        valid_from = None
                        if discount_data.get('valid_from'):
                            valid_from = datetime.fromisoformat(discount_data['valid_from']).date()
                        
                        valid_to = None
                        if discount_data.get('valid_to'):
                            valid_to = datetime.fromisoformat(discount_data['valid_to']).date()
                        
                        # Tạo mã giảm giá mới
                        discount = Discount(
                            code=code,
                            description=discount_data.get('description', ''),
                            discount_type=discount_data.get('discount_type', 'fixed'),
                            value=discount_data.get('value', 0),
                            valid_from=valid_from,
                            valid_to=valid_to,
                            max_uses=discount_data.get('max_uses', 0),
                            uses_per_customer=discount_data.get('uses_per_customer', 0),
                            min_purchase_value=discount_data.get('min_purchase_value', 0),
                            is_active=discount_data.get('is_active', False)
                        )
                        
                        if 'created_at' in discount_data:
                            discount.created_at = datetime.fromisoformat(discount_data['created_at'])
                        
                        discount.save()
                        
                        # Khôi phục lịch sử sử dụng nếu cần
                        if include_usage and 'usages' in discount_data:
                            for usage_data in discount_data['usages']:
                                try:
                                    from orders.models import Order
                                    
                                    user = None
                                    if usage_data.get('user_id'):
                                        try:
                                            user = CustomUser.objects.get(id=usage_data['user_id'])
                                        except CustomUser.DoesNotExist:
                                            pass
                                    
                                    order = None
                                    if usage_data.get('order_id'):
                                        try:
                                            order = Order.objects.get(id=usage_data['order_id'])
                                        except Order.DoesNotExist:
                                            pass
                                    
                                    # Tạo usage mới
                                    DiscountUsage.objects.create(
                                        discount=discount,
                                        user=user,
                                        order=order,
                                        amount=usage_data.get('amount', 0),
                                        created_at=datetime.fromisoformat(usage_data['created_at'])
                                    )
                                
                                except Exception as e:
                                    # Bỏ qua lỗi khi khôi phục usage
                                    pass
                        
                        # Ghi nhật ký
                        DiscountHistory.objects.create(
                            discount=discount,
                            discount_code=discount.code,
                            action_type='create',
                            user=request.user,
                            changes_json=json.dumps({
                                'note': 'Khôi phục từ bản sao lưu'
                            })
                        )
                        
                        restored_count += 1
                    
                    except Exception as e:
                        error_count += 1
                
                # Hiển thị thông báo kết quả
                if restored_count > 0:
                    messages.success(request, f"Đã khôi phục thành công {restored_count} mã giảm giá. Có {error_count} lỗi.")
                    return redirect('dashboard:discounts')
                else:
                    if error_count > 0:
                        messages.error(request, f"Không thể khôi phục dữ liệu. Có {error_count} lỗi xảy ra.")
                    else:
                        messages.warning(request, "Không có mã giảm giá nào được khôi phục. Có thể các mã đã tồn tại.")
            
            except Exception as e:
                messages.error(request, f"Lỗi khi khôi phục dữ liệu: {str(e)}")
    else:
        # Xem có preset backup_id không
        backup_id = request.GET.get('backup_id')
        initial = {}
        
        if backup_id and backup_id.isdigit():
            try:
                backup = DiscountBackup.objects.get(id=int(backup_id))
                initial = {'backup_id': backup, 'restore_type': 'existing'}
            except DiscountBackup.DoesNotExist:
                pass
        
        form = DiscountRestoreForm(initial=initial)
    
    context = {
        'title': 'Khôi phục mã giảm giá',
        'form': form,
        'backups': backups
    }
    
    return render(request, 'dashboard/discounts/restore.html', context)

# Thêm các view khác...
