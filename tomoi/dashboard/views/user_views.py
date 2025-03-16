from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser, UserActivity, UserNote, BalanceHistory, TCoinHistory
from ..forms import UserForm, UserPermissionForm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import Group, Permission
from ..models.user_activity import UserActivityLog
import json
import csv
import random
import string
import decimal
from django.views.decorators.http import require_POST
from django.urls import reverse

@staff_member_required
def user_dashboard(request):
    """Dashboard tổng quan về người dùng"""
    today = timezone.now()
    
    # Thêm lịch sử hoạt động vào context
    activities = UserActivityLog.objects.select_related(
        'user', 'admin'
    ).order_by('-created_at')[:50]
    
    context = {
        'total_users': CustomUser.objects.count(),
        'active_users': CustomUser.objects.filter(is_active=True).count(),
        'pending_users': CustomUser.objects.filter(status='pending').count(),
        'blocked_users': CustomUser.objects.filter(is_active=False).count(),
        
        # Thống kê người dùng VIP/thường
        'vip_users': CustomUser.objects.filter(account_type='vip').count(),
        'regular_users': CustomUser.objects.filter(account_type='regular').count(),
        'new_users': CustomUser.objects.filter(
            date_joined__gte=today - timedelta(days=7)
        ).count(),

        # Dữ liệu biểu đồ đăng ký theo thời gian
        'chart_labels': [
            (today - timedelta(days=x)).strftime('%d/%m')
            for x in range(7, -1, -1)
        ],
        'registration_data': [
            CustomUser.objects.filter(
                date_joined__date=today.date() - timedelta(days=x)
            ).count()
            for x in range(7, -1, -1)
        ],

        # Danh sách người dùng mới nhất
        'users': CustomUser.objects.all().order_by('-date_joined')[:50],
        'activities': activities,
    }
    
    return render(request, 'dashboard/users/dashboard.html', context)

@staff_member_required 
def user_detail(request, user_id):
    """Chi tiết người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    context = {
        'user': user,
        'user_activities': UserActivity.objects.filter(user=user).order_by('-timestamp')[:20],
        'notes': UserNote.objects.filter(user=user).order_by('-created_at'),
        'permissions': user.get_all_permissions()
    }
    
    return render(request, 'dashboard/users/detail.html', context)

@staff_member_required
def user_edit(request, user_id):
    """Chỉnh sửa thông tin người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        form_type = request.POST.get('form_type')
        
        # Debug thông tin request
        print(f"POST request received: action={action}, form_type={form_type}")
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        
        # Xử lý upload avatar
        if form_type == 'avatar_form' and request.FILES.get('avatar'):
            try:
                user.avatar = request.FILES['avatar']
                user.save(update_fields=['avatar'])
                
                # Log hoạt động
                UserActivityLog.objects.create(
                    user=user,
                    admin=request.user,
                    action_type='update',
                    description=f'Cập nhật avatar'
                )
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Avatar đã được cập nhật thành công'
                })
            except Exception as e:
                print(f"Error updating avatar: {str(e)}")
                return JsonResponse({
                    'status': 'error',
                    'message': f'Lỗi khi cập nhật avatar: {str(e)}'
                }, status=400)
        
        # Xử lý form thông thường
        elif not action:  # Không cần kiểm tra form_type, chỉ cần không phải action đặc biệt
            try:
                # Xử lý các trường boolean từ chuỗi 'true'/'false'
                boolean_fields = ['has_2fa', 'require_2fa', 'require_2fa_login', 
                                 'require_2fa_payment', 'require_2fa_profile', 
                                 'require_2fa_withdraw', 'is_active']
                
                post_data = request.POST.copy()
                
                for field in boolean_fields:
                    if field in post_data:
                        value = post_data[field].lower()
                        post_data[field] = value == 'true'
                    else:
                        post_data[field] = False
                
                # Xử lý 2FA
                two_factor_method = post_data.get('two_factor_method')
                if two_factor_method:
                    post_data['has_2fa'] = True
                    
                    # Xử lý mật khẩu cấp 2 (2FA password)
                    if two_factor_method == 'password' and post_data.get('two_factor_password'):
                        user.two_factor_password = post_data.get('two_factor_password')
                else:
                    post_data['has_2fa'] = False
                    post_data['two_factor_method'] = ''
                
                # Tạo form với dữ liệu đã xử lý
                form = UserForm(post_data, request.FILES, instance=user)
                form.admin_user = request.user
                
                if form.is_valid():
                    updated_user = form.save(commit=False)
                    
                    # Cập nhật các trường 2FA - đặt trực tiếp thay vì thông qua form
                    updated_user.has_2fa = post_data.get('has_2fa') == True
                    updated_user.two_factor_method = post_data.get('two_factor_method', '')
                    
                    # Xử lý mật khẩu 2FA
                    if two_factor_method == 'password' and post_data.get('two_factor_password'):
                        updated_user.two_factor_password = post_data.get('two_factor_password')
                    
                    # Xử lý Google Authenticator
                    if two_factor_method == 'google' and post_data.get('ga_secret_key'):
                        updated_user.ga_secret_key = post_data.get('ga_secret_key')
                    
                    # Cập nhật các trường require_2fa
                    updated_user.require_2fa = post_data.get('require_2fa') == True
                    updated_user.require_2fa_login = post_data.get('require_2fa_login') == True
                    updated_user.require_2fa_payment = post_data.get('require_2fa_payment') == True
                    updated_user.require_2fa_profile = post_data.get('require_2fa_profile') == True
                    updated_user.require_2fa_withdraw = post_data.get('require_2fa_withdraw') == True
                    
                    # Lưu lại các thay đổi
                    updated_user.save()
                    
                    # Log hoạt động
                    UserActivityLog.objects.create(
                        user=user,
                        admin=request.user,
                        action_type='update',
                        description=f'Cập nhật thông tin người dùng'
                    )
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Cập nhật thông tin thành công',
                        'redirect': reverse('dashboard:user_detail', args=[user.id])
                    })
                else:
                    print(f"Form errors: {form.errors}")
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Dữ liệu không hợp lệ',
                        'errors': dict(form.errors)
                    }, status=400)
            except Exception as e:
                print(f"Error in user_edit: {str(e)}")
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=400)
        elif action == 'adjust_balance':
            amount = request.POST.get('amount')
            reason = request.POST.get('reason', 'Admin cập nhật')
            adjustment_type = 'tăng' if float(amount) > 0 else 'giảm'
            
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
                
        elif action == 'adjust_tcoin':
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
    
    # GET request - hiển thị form
    form = UserForm(instance=user)
    
    context = {
        'user': user,
        'form': form,
    }
    
    return render(request, 'dashboard/users/edit.html', context)

@staff_member_required
def user_permissions(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        try:
            # Get the selected groups and permissions from the form data
            selected_groups = request.POST.getlist('groups')
            selected_permissions = request.POST.getlist('permissions')

            # Clear existing groups and add selected groups
            user.groups.clear()
            for group_id in selected_groups:
                try:
                    group = Group.objects.get(pk=group_id)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    messages.error(request, f'Không tìm thấy nhóm người dùng với ID {group_id}')
            
            # Clear existing permissions and add selected permissions
            user.user_permissions.clear()
            for perm_id in selected_permissions:
                try:
                    # Handle permissions with or without dots
                    if '.' in perm_id:
                        app_label, codename = perm_id.split('.')
                        perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
                    else:
                        perm = Permission.objects.get(pk=perm_id)
                    
                    user.user_permissions.add(perm)
                except Permission.DoesNotExist:
                    messages.error(request, f'Không tìm thấy quyền với ID {perm_id}')
            
            # Save the user object to update the permissions in the database
            user.save()
            
            # Log the activity
            UserActivityLog.objects.create(
                user=request.user,
                action_type='permission',
                description=f'Đã cập nhật quyền cho người dùng {user.email}'
            )
            
            messages.success(request, f'Cập nhật quyền thành công cho người dùng {user.email}')
            return redirect('dashboard:user_detail', user_id=user.id)
        
        except json.JSONDecodeError:
            messages.error(request, 'Dữ liệu quyền không hợp lệ')
        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật quyền: {str(e)}')
    
    # Prepare data for displaying the permissions page
    groups = Group.objects.all()
    user_groups = user.groups.all()
    user_permissions = user.user_permissions.all()
    
    # Prepare the context for rendering the template
    context = {
        'user': user,
        'groups': groups,
        'user_groups': user_groups,
        'user_permissions': user_permissions
    }
    
    return render(request, 'dashboard/users/permissions.html', context)

@staff_member_required
def user_activity(request, user_id):
    """Lịch sử hoạt động của người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    activities = UserActivity.objects.filter(user=user).order_by('-timestamp')
    
    return render(request, 'dashboard/users/activity.html', {
        'user': user,
        'activities': activities
    })

@staff_member_required
def user_transactions(request, user_id):
    """Lịch sử giao dịch của người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    transactions = user.get_transactions()
    
    return render(request, 'dashboard/users/transactions.html', {
        'user': user,
        'transactions': transactions
    })

@staff_member_required
def user_notes(request, user_id):
    """Hiển thị và quản lý ghi chú người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    notes = UserNote.objects.filter(user=user).order_by('-created_at')
    
    return render(request, 'dashboard/users/notes.html', {
        'user': user,
        'notes': notes
    })

@staff_member_required
def user_add_note(request, user_id):
    """Thêm ghi chú mới cho người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            note = UserNote.objects.create(
                user=user,
                content=content,
                created_by=request.user
            )
            
            # AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'id': note.id,
                    'content': note.content,
                    'created_by': note.created_by.username,
                    'created_at': note.created_at.strftime('%d/%m/%Y %H:%M')
                })
            
            messages.success(request, 'Đã thêm ghi chú thành công')
            
    return redirect('dashboard:user_notes', user_id=user.id)

@staff_member_required
def user_edit_note(request, user_id, note_id):
    """Sửa ghi chú người dùng"""
    note = get_object_or_404(UserNote, id=note_id, user_id=user_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            note.content = content
            note.updated_by = request.user
            note.updated_at = timezone.now()
            note.save()
            
            # AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'id': note.id,
                    'content': note.content,
                    'updated_by': note.updated_by.username,
                    'updated_at': note.updated_at.strftime('%d/%m/%Y %H:%M')
                })
            
            messages.success(request, 'Đã cập nhật ghi chú thành công')
    
    return redirect('dashboard:user_notes', user_id=user_id)

@staff_member_required
def user_delete_note(request, user_id, note_id):
    """Xóa ghi chú người dùng"""
    note = get_object_or_404(UserNote, id=note_id, user_id=user_id)
    note.delete()
    
    # AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Đã xóa ghi chú thành công'
        })
    
    messages.success(request, 'Đã xóa ghi chú thành công')
    return redirect('dashboard:user_notes', user_id=user_id)

@staff_member_required
def user_analytics(request):
    """Phân tích chi tiết về người dùng"""
    # Lấy thống kê cơ bản
    total_users = CustomUser.objects.count()
    new_users_month = CustomUser.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=30)
    ).count()
    active_users = CustomUser.objects.filter(
        last_login__gte=timezone.now() - timedelta(days=30)
    ).count()
    premium_users = CustomUser.objects.filter(
        account_type__in=['premium', 'vip']
    ).count()

    # Dữ liệu cho biểu đồ tăng trưởng
    growth_data = []
    growth_labels = []
    for i in range(12):
        date = timezone.now() - timedelta(days=i*30)
        count = CustomUser.objects.filter(date_joined__lte=date).count()
        growth_data.insert(0, count)
        growth_labels.insert(0, date.strftime('%m/%Y'))

    # Dữ liệu cho biểu đồ phân bố
    regular = CustomUser.objects.filter(account_type='regular').count()
    premium = CustomUser.objects.filter(account_type='premium').count()
    vip = CustomUser.objects.filter(account_type='vip').count()
    distribution_data = [regular, premium, vip]

    context = {
        'total_users': total_users,
        'new_users_month': new_users_month,
        'active_users': active_users,
        'premium_users': premium_users,
        'growth_labels': json.dumps(growth_labels),
        'growth_data': growth_data,
        'distribution_data': distribution_data
    }
    
    return render(request, 'dashboard/users/analytics.html', context)

# Các hàm hỗ trợ
def get_registration_stats():
    """Thống kê đăng ký theo thời gian"""
    pass

def get_engagement_stats():
    """Thống kê tương tác người dùng"""
    pass

def get_retention_stats():
    """Thống kê tỷ lệ giữ chân người dùng"""
    pass

def user_add(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Người dùng đã được tạo thành công.')
            return redirect('dashboard:user_detail', user_id=user.id)
    else:
        form = UserForm()
    
    return render(request, 'dashboard/users/add.html', {'form': form}) 

@staff_member_required
def export_users(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="users.csv"'},
    )
    response.write('\ufeff'.encode('utf-8'))  # BOM for Excel UTF-8
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Email', 'Số điện thoại', 'Ngày tham gia', 'Trạng thái'])
    
    users = CustomUser.objects.all()
    for user in users:
        writer.writerow([
            user.id,
            user.username,
            user.email,
            user.phone_number or 'Chưa cập nhật',
            user.date_joined.strftime('%d/%m/%Y'),
            'Hoạt động' if user.is_active else 'Đã khóa'
        ])
    
    return response

@staff_member_required
def user_groups(request):
    """Quản lý nhóm người dùng"""
    groups = Group.objects.all()
    return render(request, 'dashboard/users/groups.html', {'groups': groups})

@staff_member_required
def add_group(request):
    """Thêm nhóm người dùng mới"""
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            group = Group.objects.create(name=name)
            messages.success(request, f'Đã tạo nhóm {name} thành công')
            return redirect('dashboard:edit_group', group_id=group.id)
    return redirect('dashboard:user_groups')

@staff_member_required
def edit_group(request, group_id):
    """Chỉnh sửa nhóm người dùng"""
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        permissions = request.POST.getlist('permissions')
        
        if name:
            group.name = name
            group.save()
            
            # Cập nhật quyền
            group.permissions.clear()
            for perm_codename in permissions:
                app_label, codename = perm_codename.split('.')
                perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
                group.permissions.add(perm)
                
            messages.success(request, f'Đã cập nhật nhóm {name} thành công')
            return redirect('dashboard:user_groups')
    
    # Chuẩn bị dữ liệu cho template
    all_permissions = Permission.objects.all()
    group_permissions = set([f"{perm.content_type.app_label}.{perm.codename}" 
                           for perm in group.permissions.all()])
    
    context = {
        'group': group,
        'all_permissions': all_permissions,
        'group_permissions': group_permissions
    }
    
    return render(request, 'dashboard/users/edit_group.html', context)

@staff_member_required
def delete_group(request, group_id):
    """Xóa nhóm người dùng"""
    group = get_object_or_404(Group, id=group_id)
    name = group.name
    group.delete()
    messages.success(request, f'Đã xóa nhóm {name} thành công')
    return redirect('dashboard:user_groups')

@staff_member_required
def delete_user(request, user_id):
    """Xóa người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    name = user.get_full_name() or user.username
    user.delete()
    messages.success(request, f'Đã xóa người dùng {name} thành công')
    return redirect('dashboard:user_list')

@staff_member_required
def adjust_balance(request, user_id):
    """Điều chỉnh số dư của người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        try:
            amount = request.POST.get('amount')
            reason = request.POST.get('reason', 'Admin cập nhật')
            
            print(f"Adjusting balance for user {user.id}: amount={amount}, reason={reason}")
            
            amount = int(amount)
            old_balance = user.balance
            user.balance = old_balance + amount
            user.save(update_fields=['balance'])
            
            print(f"Balance updated: old={old_balance}, new={user.balance}")
            
            # Tạo log điều chỉnh số dư
            adjustment_type = 'tăng' if amount > 0 else 'giảm'
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
            
            return JsonResponse({
                'status': 'success',
                'message': 'Số dư đã được cập nhật thành công',
                'old_balance': old_balance,
                'new_balance': user.balance,
                'amount': amount
            })
        except ValueError as e:
            print(f"ValueError in adjust_balance: {str(e)}")
            return JsonResponse({
                'status': 'error', 
                'message': 'Số tiền không hợp lệ'
            }, status=400)
        except Exception as e:
            print(f"Exception in adjust_balance: {str(e)}")
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error', 
        'message': 'Phương thức không được hỗ trợ'
    }, status=405)

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

@staff_member_required
def import_users(request):
    """Nhập danh sách người dùng từ file Excel"""
    if request.method == 'POST' and request.FILES.get('excel_file'):
        file = request.FILES.get('excel_file')
        try:
            # Xử lý file Excel
            import pandas as pd
            
            df = pd.read_excel(file)
            created_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Kiểm tra các trường bắt buộc
                    if not row.get('username') or not row.get('email'):
                        continue
                        
                    username = row.get('username')
                    email = row.get('email')
                    
                    # Kiểm tra trùng lặp
                    if CustomUser.objects.filter(username=username).exists():
                        continue
                    
                    # Tạo người dùng mới
                    user = CustomUser.objects.create_user(
                        username=username,
                        email=email,
                        password=row.get('password', 'tomoi2023'),  # Mật khẩu mặc định
                        first_name=row.get('first_name', ''),
                        last_name=row.get('last_name', ''),
                        phone=row.get('phone', ''),
                        account_type=row.get('account_type', 'regular'),
                    )
                    
                    # Gửi email thông báo nếu có yêu cầu
                    if request.POST.get('send_notification'):
                        # Thêm code gửi email thông báo tại đây
                        pass
                        
                    created_count += 1
                    
                except Exception as e:
                    error_count += 1
                    
            # Thông báo kết quả
            if created_count > 0:
                messages.success(request, f'Đã tạo thành công {created_count} người dùng.')
            if error_count > 0:
                messages.warning(request, f'Có {error_count} người dùng không thể tạo do lỗi dữ liệu.')
                
        except Exception as e:
            messages.error(request, f'Lỗi khi xử lý file Excel: {str(e)}')
            
    else:
        messages.error(request, 'Vui lòng chọn file Excel để tải lên.')
        
    return redirect('dashboard:user_list')

@staff_member_required
@require_POST
def user_reset_password(request, user_id):
    """Reset user password and return new password"""
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        
        # Nếu có mật khẩu mới được gửi lên
        if 'new_password' in request.POST and request.POST['new_password']:
            new_password = request.POST['new_password']
            generated_password = None
        else:
            # Tạo mật khẩu ngẫu nhiên
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            generated_password = new_password
        
        # Đặt lại mật khẩu
        user.set_password(new_password)
        user.save()
        
        # Log hoạt động
        UserActivityLog.objects.create(
            user=user,
            admin=request.user,
            action_type='password_reset',
            description='Mật khẩu người dùng đã được đặt lại'
        )
        
        # Trả về kết quả dạng JSON
        return JsonResponse({
            'status': 'success',
            'message': 'Mật khẩu đã được đặt lại thành công',
            'generated_password': generated_password
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@staff_member_required
@require_POST
def update_user_note(request, note_id):
    """Update user note"""
    try:
        note = get_object_or_404(UserNote, id=note_id)
        content = request.POST.get('content', '').strip()
        
        if not content:
            return JsonResponse(
                {'success': False, 'message': 'Nội dung ghi chú không được để trống'}, 
                status=400
            )
        
        note.content = content
        note.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Đã cập nhật ghi chú thành công'
        })
    except Exception as e:
        return JsonResponse(
            {'success': False, 'message': str(e)}, 
            status=500
        )

@staff_member_required
@require_POST
def delete_user_note(request, note_id):
    """Delete user note"""
    try:
        note = get_object_or_404(UserNote, id=note_id)
        note.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Đã xóa ghi chú thành công'
        })
    except Exception as e:
        return JsonResponse(
            {'success': False, 'message': str(e)}, 
            status=500
        )