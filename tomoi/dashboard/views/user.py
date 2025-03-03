from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from accounts.models import CustomUser
from ..forms import UserFilterForm, UserEditForm, UserAddForm
from django.http import JsonResponse
import json
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate
from django.conf import settings
from django.contrib.sessions.models import Session

@staff_member_required
def user_list(request):
    """Danh sách người dùng với bộ lọc"""
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Xử lý form lọc
    filter_form = UserFilterForm(request.GET)
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        user_type = filter_form.cleaned_data.get('user_type')
        source = filter_form.cleaned_data.get('source')
        search = filter_form.cleaned_data.get('search')
        
        if status:
            users = users.filter(is_active=(status == 'active'))
        if user_type:
            users = users.filter(user_type=user_type)
        if source:
            users = users.filter(source=source)
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone_number__icontains=search)
            )
    
    # Phân trang
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    context = {
        'users': users,
        'filter_form': filter_form
    }
    
    return render(request, 'dashboard/users/list.html', context)

@staff_member_required
def user_detail(request, user_id):
    """Chi tiết người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Thống kê hoạt động
    today = timezone.now()
    last_30_days = today - timedelta(days=30)
    
    # Thống kê đăng nhập theo ngày
    logins_by_date = user.login_history.filter(
        login_time__gte=last_30_days
    ).annotate(
        date=TruncDate('login_time')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Format dữ liệu cho biểu đồ
    dates = [entry['date'].strftime('%d/%m') for entry in logins_by_date]
    counts = [entry['count'] for entry in logins_by_date]
    
    context = {
        'user_obj': user,
        'login_dates': json.dumps(dates),
        'login_counts': json.dumps(counts)
    }
    
    return render(request, 'dashboard/users/detail.html', context)

@staff_member_required
def user_edit(request, user_id):
    """Chỉnh sửa thông tin người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật thông tin thành công')
            return redirect('dashboard:user_detail', user_id=user.id)
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'dashboard/users/edit.html', {'form': form, 'user': user})

@staff_member_required
def user_permissions(request, user_id):
    """Quản lý phân quyền người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        permissions = json.loads(request.body)
        user.update_permissions(permissions)
        return JsonResponse({'status': 'success'})
        
    current_permissions = user.get_all_permissions()
    return render(request, 'dashboard/users/permissions.html', {
        'user': user,
        'current_permissions': current_permissions
    })

@staff_member_required
def user_stats(request):
    """Thống kê về người dùng"""
    now = timezone.now()
    last_month = now - timedelta(days=30)
    
    # Tổng số người dùng
    total_users = CustomUser.objects.count()
    
    # Người dùng mới trong tháng
    new_users_month = CustomUser.objects.filter(date_joined__gte=last_month).count()
    
    # Tỷ lệ người dùng hoạt động
    active_users = CustomUser.objects.filter(is_active=True).count()
    active_rate = round((active_users / total_users * 100) if total_users > 0 else 0, 1)
    
    # Tỷ lệ chuyển đổi (người dùng có ít nhất 1 đơn hàng)
    users_with_orders = CustomUser.objects.annotate(
        order_count=Count('orders')
    ).filter(order_count__gt=0).count()
    conversion_rate = round((users_with_orders / total_users * 100) if total_users > 0 else 0, 1)
    
    # Dữ liệu cho biểu đồ người dùng mới
    new_users_data = CustomUser.objects.filter(
        date_joined__gte=last_month
    ).annotate(
        date=TruncDate('date_joined')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    chart_labels = [entry['date'].strftime('%d/%m') for entry in new_users_data]
    chart_data = [entry['count'] for entry in new_users_data]
    
    # Dữ liệu phân bố người dùng
    distribution_data = [
        CustomUser.objects.filter(user_type='customer').count(),
        CustomUser.objects.filter(user_type='vip').count(),
        CustomUser.objects.filter(user_type__in=['staff', 'admin']).count()
    ]
    
    context = {
        'total_users': total_users,
        'new_users_month': new_users_month,
        'active_rate': active_rate,
        'conversion_rate': conversion_rate,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'distribution_data': json.dumps(distribution_data)
    }
    
    return render(request, 'dashboard/users/stats.html', context)

@staff_member_required
def user_stats_data(request):
    """API để lấy dữ liệu thống kê theo khoảng thời gian"""
    period = request.GET.get('period', 'week')
    now = timezone.now()
    
    if period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    else:  # year
        start_date = now - timedelta(days=365)
    
    data = CustomUser.objects.filter(
        date_joined__gte=start_date
    ).annotate(
        date=TruncDate('date_joined')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    labels = [entry['date'].strftime('%d/%m') for entry in data]
    values = [entry['count'] for entry in data]
    
    return JsonResponse({
        'labels': labels,
        'values': values
    })

@staff_member_required
def export_users(request):
    """Xuất dữ liệu người dùng ra file"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="users-{datetime.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Email', 'Họ tên', 'Số điện thoại', 'Ngày tham gia', 
                    'Trạng thái', 'Loại tài khoản', 'Số đơn hàng', 'Tổng chi tiêu'])

    users = CustomUser.objects.annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total_amount')
    )

    for user in users:
        writer.writerow([
            user.id,
            user.username,
            user.email,
            user.get_full_name(),
            user.phone,
            user.date_joined.strftime('%d/%m/%Y'),
            'Hoạt động' if user.is_active else 'Vô hiệu',
            user.get_user_type_display(),
            user.order_count,
            user.total_spent or 0
        ])

    return response

@staff_member_required
def user_activity_log(request, user_id):
    """Xem log hoạt động của người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Lấy tất cả hoạt động của user
    activities = user.get_all_activities()
    
    # Phân trang
    paginator = Paginator(activities, 20)
    page = request.GET.get('page')
    activities = paginator.get_page(page)
    
    return render(request, 'dashboard/users/activity_log.html', {
        'user': user,
        'activities': activities
    })

@staff_member_required
def user_login_history(request, user_id):
    """Xem lịch sử đăng nhập"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Lấy lịch sử đăng nhập
    login_history = user.get_login_history()
    
    # Phân trang
    paginator = Paginator(login_history, 20)
    page = request.GET.get('page')
    login_history = paginator.get_page(page)
    
    return render(request, 'dashboard/users/login_history.html', {
        'user': user,
        'login_history': login_history
    })

@staff_member_required
def reset_user_password(request, user_id):
    """Đặt lại mật khẩu cho người dùng"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Tạo mật khẩu ngẫu nhiên
    new_password = CustomUser.objects.make_random_password()
    user.set_password(new_password)
    user.save()
    
    # Gửi email thông báo mật khẩu mới
    try:
        user.email_user(
            'Mật khẩu mới của bạn',
            f'Mật khẩu mới của bạn là: {new_password}\nVui lòng đăng nhập và đổi mật khẩu ngay.',
            from_email=settings.DEFAULT_FROM_EMAIL
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@staff_member_required
def toggle_user_status(request, user_id):
    """Bật/tắt trạng thái hoạt động của người dùng"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    return JsonResponse({
        'success': True,
        'is_active': user.is_active
    })

@staff_member_required
def terminate_session(request, user_id):
    """Kết thúc một phiên đăng nhập cụ thể"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    user = get_object_or_404(CustomUser, id=user_id)
    session_id = request.POST.get('session_id')
    
    try:
        # Xóa phiên đăng nhập
        Session.objects.filter(session_key=session_id).delete()
        
        # Ghi log
        user.log_activity(
            description=f'Phiên đăng nhập {session_id} bị kết thúc bởi admin',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@staff_member_required
def terminate_all_sessions(request, user_id):
    """Kết thúc tất cả phiên đăng nhập của người dùng"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    user = get_object_or_404(CustomUser, id=user_id)
    
    try:
        # Xóa tất cả phiên đăng nhập
        Session.objects.filter(userloginhistory__user=user).delete()
        
        # Ghi log
        user.log_activity(
            description='Tất cả phiên đăng nhập bị kết thúc bởi admin',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@staff_member_required
def user_add(request):
    """Thêm người dùng mới"""
    if request.method == 'POST':
        form = UserAddForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Ghi log
            user.log_activity(
                description='Tài khoản được tạo bởi admin',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            # Gửi email thông báo
            try:
                user.email_user(
                    'Chào mừng bạn đến với hệ thống',
                    f'Tài khoản của bạn đã được tạo.\nTên đăng nhập: {user.username}\nMật khẩu: {form.cleaned_data["password1"]}',
                    from_email=settings.DEFAULT_FROM_EMAIL
                )
            except:
                messages.warning(request, 'Không thể gửi email thông báo')
                
            messages.success(request, 'Tạo người dùng mới thành công')
            return redirect('dashboard:user_detail', user_id=user.id)
    else:
        form = UserAddForm()
    
    return render(request, 'dashboard/users/add.html', {'form': form})

@staff_member_required
def import_users(request):
    """Import danh sách người dùng từ file Excel"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)
        
    file = request.FILES['file']
    send_email = request.POST.get('send_email') == 'on'
    
    try:
        # Đọc file Excel
        import pandas as pd
        df = pd.read_excel(file)
        
        # Validate dữ liệu
        required_columns = ['username', 'email', 'first_name', 'last_name', 'phone']
        if not all(col in df.columns for col in required_columns):
            return JsonResponse({'error': 'Invalid file format'}, status=400)
            
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Tạo mật khẩu ngẫu nhiên
                password = CustomUser.objects.make_random_password()
                
                # Tạo user mới
                user = CustomUser.objects.create_user(
                    username=row['username'],
                    email=row['email'],
                    password=password,
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    phone=row['phone'],
                    user_type=row.get('user_type', 'customer'),
                    is_active=True
                )
                
                # Gửi email thông báo
                if send_email:
                    user.email_user(
                        'Thông tin tài khoản của bạn',
                        f'Tài khoản của bạn đã được tạo.\nTên đăng nhập: {user.username}\nMật khẩu: {password}',
                        from_email=settings.DEFAULT_FROM_EMAIL
                    )
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f'Dòng {index + 2}: {str(e)}')
                
        return JsonResponse({
            'success': True,
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@staff_member_required
def user_report(request):
    """Báo cáo thống kê người dùng"""
    # Xử lý filter
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    user_type = request.GET.get('user_type')
    status = request.GET.get('status')
    
    users = CustomUser.objects.all()
    
    if from_date:
        users = users.filter(date_joined__gte=from_date)
    if to_date:
        users = users.filter(date_joined__lte=to_date)
    if user_type:
        users = users.filter(user_type=user_type)
    if status:
        users = users.filter(is_active=(status == 'active'))
        
    # Tính toán các chỉ số
    total_users = users.count()
    new_users = users.filter(date_joined__gte=timezone.now() - timedelta(days=30)).count()
    active_users = users.filter(is_active=True).count()
    active_rate = round((active_users / total_users * 100) if total_users > 0 else 0, 1)
    
    users_with_orders = users.annotate(
        order_count=Count('orders')
    ).filter(order_count__gt=0).count()
    conversion_rate = round((users_with_orders / total_users * 100) if total_users > 0 else 0, 1)
    
    # Dữ liệu cho biểu đồ
    growth_data = users.annotate(
        date=TruncDate('date_joined')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    chart_labels = [entry['date'].strftime('%d/%m') for entry in growth_data]
    chart_data = [entry['count'] for entry in growth_data]
    
    distribution_data = [
        users.filter(user_type='customer').count(),
        users.filter(user_type='vip').count(),
        users.filter(user_type__in=['staff', 'admin']).count()
    ]
    
    # Xử lý xuất báo cáo
    export_type = request.GET.get('export')
    if export_type:
        if export_type == 'excel':
            return export_excel_report(users)
        elif export_type == 'pdf':
            return export_pdf_report(users)
    
    context = {
        'total_users': total_users,
        'new_users': new_users,
        'active_rate': active_rate,
        'conversion_rate': conversion_rate,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'distribution_data': json.dumps(distribution_data)
    }
    
    return render(request, 'dashboard/users/report.html', context)

@staff_member_required
def user_delete(request, user_id):
    """Xóa người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        try:
            # Lưu thông tin để thông báo
            username = user.username
            
            # Xóa user
            user.delete()
            
            messages.success(request, f'Đã xóa người dùng {username}')
            return redirect('dashboard:user_list')
            
        except Exception as e:
            messages.error(request, f'Lỗi khi xóa người dùng: {str(e)}')
            return redirect('dashboard:user_detail', user_id=user_id)
    
    return render(request, 'dashboard/users/delete_confirm.html', {
        'user': user
    }) 