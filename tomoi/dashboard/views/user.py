from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from accounts.models import CustomUser, TCoinHistory
from ..forms import UserFilterForm, UserEditForm, UserAddForm
from django.http import JsonResponse
import json
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from ..models.user_activity import UserActivityLog
import decimal
from django import forms
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage

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
    
    # Lấy lịch sử hoạt động
    user_activities = UserActivityLog.objects.filter(user=user).order_by('-created_at')[:20]
    
    # Thống kê đăng nhập theo ngày
    today = timezone.now()
    last_30_days = today - timedelta(days=30)
    
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
        'user': user,
        'user_activities': user_activities,
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
            # Lưu dữ liệu cũ trước khi cập nhật
            activity = UserActivityLog.objects.create(
                user=user,
                admin=request.user,
                action_type='update',
                description=f'Cập nhật thông tin người dùng {user.username}'
            )
            activity.save_old_data(user)
            
            # Lưu form
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
        try:
            permissions = json.loads(request.body)
            
            # Lưu permissions cũ trước khi cập nhật
            old_permissions = list(user.get_all_permissions())
            
            # Cập nhật permissions mới
            user.update_permissions(permissions)
            
            # Lấy permissions mới sau khi cập nhật
            new_permissions = list(user.get_all_permissions())
            
            # Tạo mô tả chi tiết những thay đổi
            changes = []
            added_perms = set(new_permissions) - set(old_permissions)
            removed_perms = set(old_permissions) - set(new_permissions)
            
            if added_perms:
                changes.append(f"Thêm quyền: {', '.join(added_perms)}")
            if removed_perms:
                changes.append(f"Xóa quyền: {', '.join(removed_perms)}")
                
            description = f"Cập nhật phân quyền cho {user.username}"
            if changes:
                description += "\n" + "\n".join(changes)
            
            # Tạo log hoạt động
            activity = UserActivityLog.objects.create(
                user=user,
                admin=request.user,
                action_type='permission',
                description=description,
                metadata={
                    'old_permissions': old_permissions,
                    'new_permissions': new_permissions
                }
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Cập nhật phân quyền thành công'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Lỗi khi cập nhật phân quyền: {str(e)}'
            }, status=400)
            
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
            user.phone_number,
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
        form = UserAddForm(request.POST)
        form.admin_user = request.user
        
        if form.is_valid():
            try:
                user = form.save()
                return JsonResponse({
                    'status': 'success',
                    'message': f'Tạo tài khoản {user.username} thành công!',
                    'redirect_url': reverse('dashboard:user_detail', args=[user.id])
                })
            except forms.ValidationError as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Lỗi hệ thống: {str(e)}'
                })
        else:
            errors = []
            for field, error_list in form.errors.items():
                field_name = form.fields[field].label or field
                for error in error_list:
                    errors.append(f"<strong>{field_name}</strong>: {error}")
            return JsonResponse({
                'status': 'error',
                'message': '<br>'.join(errors)
            })
    else:
        form = UserAddForm()
    
    return render(request, 'dashboard/users/add.html', {
        'form': form,
        'title': 'Thêm người dùng mới'
    })

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
    
    # Tạo log trước khi xóa
    activity = UserActivityLog.objects.create(
        user=user,
        admin=request.user,
        action_type='delete',
        description=f'Xóa người dùng {user.username}'
    )
    activity.save_old_data(user)
    
    # Soft delete
    user.is_active = False
    user.save()
    
    return JsonResponse({'status': 'success'})

@staff_member_required
def user_dashboard(request):
    """Trang tổng quan người dùng"""
    # Thống kê tổng quan
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    
    # Đếm số người dùng đăng ký mới trong 30 ngày
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_users_30d = CustomUser.objects.filter(date_joined__gte=thirty_days_ago).count()
    
    # Lấy danh sách người dùng mới đăng ký
    new_users = CustomUser.objects.filter(
        date_joined__gte=thirty_days_ago
    ).order_by('-date_joined')[:10]
    
    # Đếm số người đang online
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    online_users = CustomUser.objects.filter(last_activity__gte=five_minutes_ago).count()
    
    # Lấy lịch sử hoạt động gần đây
    user_activities = UserActivityLog.objects.select_related('user', 'admin').order_by('-created_at')[:50]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'new_users_30d': new_users_30d,
        'online_users': online_users,
        'new_users': new_users,
        'user_activities': user_activities,
    }
    
    return render(request, 'dashboard/users/dashboard.html', context)

@login_required
def rollback_activity(request, activity_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    activity = get_object_or_404(UserActivityLog, id=activity_id)
    
    if not activity.can_rollback:
        return JsonResponse({'error': 'Cannot rollback this activity'}, status=400)
        
    try:
        success = activity.rollback()
        if success:
            return JsonResponse({'message': 'Rollback successful'})
        else:
            return JsonResponse({'error': 'Could not rollback'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@staff_member_required
def adjust_balance(request, user_id):
    """Điều chỉnh số dư"""
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)
        amount = request.POST.get('amount')
        reason = request.POST.get('reason', 'Admin cập nhật')
        adjustment_type = 'tăng' if int(amount) > 0 else 'giảm'
        
        try:
            amount = decimal.Decimal(amount)
            old_balance = user.balance
            user.balance += amount
            user.save()
            
            # Tạo log điều chỉnh số dư
            BalanceHistory.objects.create(
                user=user,
                amount=amount,
                balance_after=user.balance,
                description=f"{adjustment_type} {abs(amount)}đ. Lý do: {reason}",
                created_by=request.user
            )
            
            # Log hoạt động
            UserActivityLog.objects.create(
                user=user,
                admin=request.user,
                action_type='update',
                description=f'{adjustment_type} số dư: {abs(amount):,}đ. Lý do: {reason}'
            )
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@staff_member_required
def check_username(request):
    """Kiểm tra username đã tồn tại chưa"""
    username = request.GET.get('username', '')
    exists = CustomUser.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

@staff_member_required
def adjust_tcoin(request, user_id):
    """Điều chỉnh TCoin của người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        reason = request.POST.get('reason', 'Admin cập nhật')
        adjustment_type = 'tăng' if int(amount) > 0 else 'giảm'
        
        try:
            amount = int(amount)
            old_tcoin = user.tcoin_balance
            user.tcoin_balance += amount
            user.save()
            
            # Tạo log điều chỉnh TCoin
            TCoinHistory.objects.create(
                user=user,
                amount=amount,
                balance_after=user.tcoin_balance,
                description=f"{adjustment_type} {abs(amount)} TCoin. Lý do: {reason}",
                created_by=request.user
            )
            
            # Log hoạt động
            UserActivityLog.objects.create(
                user=user,
                admin=request.user,
                action_type='update',
                description=f'{adjustment_type} TCoin: {abs(amount):,}. Lý do: {reason}'
            )
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def export_excel_report(users):
    """Xuất báo cáo dạng Excel"""
    import pandas as pd
    from django.http import HttpResponse
    from io import BytesIO
    
    # Tạo DataFrame từ dữ liệu người dùng
    data = []
    for user in users:
        data.append({
            'ID': user.id,
            'Username': user.username,
            'Email': user.email,
            'Họ tên': user.get_full_name(),
            'Số điện thoại': user.phone_number,
            'Ngày tham gia': user.date_joined.strftime('%d/%m/%Y'),
            'Trạng thái': 'Hoạt động' if user.is_active else 'Vô hiệu',
            'Loại tài khoản': user.get_user_type_display(),
        })
    
    df = pd.DataFrame(data)
    
    # Tạo file Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Users', index=False)
        
        # Tùy chỉnh định dạng
        workbook = writer.book
        worksheet = writer.sheets['Users']
        format_header = workbook.add_format({'bold': True, 'bg_color': '#D8E4BC'})
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, format_header)
            worksheet.set_column(col_num, col_num, 15)
    
    # Trả về response
    output.seek(0)
    filename = f'user_report_{timezone.now().strftime("%Y%m%d")}.xlsx'
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

def export_pdf_report(users):
    """Xuất báo cáo dạng PDF"""
    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from io import BytesIO
    
    # Tạo file PDF trong bộ nhớ
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Định dạng và style
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    
    # Thêm tiêu đề
    elements.append(Paragraph("Báo cáo người dùng", title_style))
    elements.append(Spacer(1, 12))
    
    # Tạo dữ liệu cho bảng
    data = [['ID', 'Username', 'Email', 'Họ tên', 'Số điện thoại', 'Ngày tham gia', 'Trạng thái']]
    
    for user in users:
        data.append([
            str(user.id),
            user.username,
            user.email,
            user.get_full_name(),
            user.phone_number,
            user.date_joined.strftime('%d/%m/%Y'),
            'Hoạt động' if user.is_active else 'Vô hiệu',
        ])
    
    # Tạo bảng và định dạng
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    
    # Tạo PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    # Trả về response
    response = HttpResponse(content_type='application/pdf')
    filename = f'user_report_{timezone.now().strftime("%Y%m%d")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf)
    
    return response

def get_default_avatar_url():
    return "/static/dashboard/images/default-avatar.png" 