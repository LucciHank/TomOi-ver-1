from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from dashboard.models import UserSubscription, SubscriptionPlan
from accounts.models import PremiumSubscription, CustomUser
from django.contrib import messages
from store.models import Order

def is_admin(user):
    return user.is_superuser or user.is_staff

def check_expired_subscriptions(grace_period=7):
    """
    Kiểm tra và cập nhật trạng thái các gói đã hết hạn
    Tương tự như lệnh quản lý update_expired_subscriptions
    """
    today = timezone.now()
    grace_date = today - timedelta(days=grace_period)
    
    # Lấy các gói đã hết hạn quá thời gian ân hạn nhưng vẫn đang active
    expired_subscriptions = UserSubscription.objects.filter(
        end_date__lt=grace_date,
        status='active'
    )
    
    # Cập nhật trạng thái thành 'expired'
    count = expired_subscriptions.count()
    if count > 0:
        expired_subscriptions.update(status='expired')
        return count
    return 0

@login_required
@user_passes_test(is_admin)
def check_expired_subscriptions_ajax(request):
    """API endpoint để kiểm tra gói hết hạn thông qua AJAX"""
    grace_period = 7  # Số ngày ân hạn
    today = timezone.now()
    grace_date = today - timedelta(days=grace_period)
    
    # Lấy các gói đã hết hạn quá thời gian ân hạn nhưng vẫn đang active
    expired_subscriptions = UserSubscription.objects.filter(
        end_date__lt=grace_date,
        status='active'
    )
    
    # Đếm số lượng gói sắp hết hạn (trong vòng 7 ngày)
    expiring_soon = UserSubscription.objects.filter(
        end_date__gte=today,
        end_date__lte=today + timedelta(days=7),
        status='active'
    ).count()
    
    # Cập nhật trạng thái nếu có gói hết hạn
    count = expired_subscriptions.count()
    if count > 0:
        expired_subscriptions.update(status='expired')
    
    return JsonResponse({
        'expired_count': count,
        'expiring_soon': expiring_soon,
        'updated': count > 0
    })

@login_required
@user_passes_test(is_admin)
def subscription_list(request):
    """Trang quản lý gia hạn tài khoản premium"""
    
    # Tự động kiểm tra và cập nhật các gói hết hạn
    updated_count = check_expired_subscriptions()
    if updated_count > 0:
        messages.info(request, f'Đã tự động cập nhật {updated_count} gói thành trạng thái "Hết hạn".')
    
    # Lấy các tham số filter
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    days_left_filter = request.GET.get('days_left', '')
    expired_filter = request.GET.get('expired', '')
    
    # Lấy tất cả các subscription
    subscriptions = UserSubscription.objects.all().select_related('user', 'plan').order_by('end_date')
    
    # Áp dụng các bộ lọc
    if status_filter:
        subscriptions = subscriptions.filter(status=status_filter)
    
    if search_query:
        subscriptions = subscriptions.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(plan__name__icontains=search_query)
        )
    
    # Lọc theo số ngày còn lại
    today = timezone.now()
    if days_left_filter:
        days = int(days_left_filter)
        target_date = today + timedelta(days=days)
        subscriptions = subscriptions.filter(end_date__lte=target_date, end_date__gte=today)
    
    # Lọc theo subscription đã hết hạn
    if expired_filter == 'true':
        subscriptions = subscriptions.filter(end_date__lt=today)
    elif expired_filter == 'false':
        subscriptions = subscriptions.filter(end_date__gte=today)
    
    # Thống kê
    total_subscriptions = subscriptions.count()
    active_subscriptions = subscriptions.filter(status='active').count()
    expired_subscriptions = subscriptions.filter(end_date__lt=today).count()
    expiring_soon = subscriptions.filter(
        end_date__gte=today,
        end_date__lte=today + timedelta(days=7),
        status='active'
    ).count()
    
    # Phân trang
    paginator = Paginator(subscriptions, 20)  # Hiển thị 20 subscription mỗi trang
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Tính toán % và ngày còn lại cho mỗi subscription
    for subscription in page_obj:
        if subscription.status == 'active':
            total_days = (subscription.end_date - subscription.start_date).days
            if total_days <= 0:
                total_days = 30  # Mặc định nếu có lỗi
                
            days_left = (subscription.end_date - today).days
            if days_left < 0:
                days_left = 0
                percentage = 0
            else:
                percentage = min(100, round((days_left / total_days) * 100))
                
            subscription.days_left = days_left
            subscription.percentage = percentage
        else:
            subscription.days_left = 0
            subscription.percentage = 0
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'days_left_filter': days_left_filter,
        'expired_filter': expired_filter,
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'expired_subscriptions': expired_subscriptions,
        'expiring_soon': expiring_soon,
        'active_tab': 'subscriptions',
        'title': 'Quản lý gia hạn tài khoản',
    }
    
    return render(request, 'dashboard/subscriptions/list.html', context)

@login_required
@user_passes_test(is_admin)
def subscription_detail(request, subscription_id):
    """Chi tiết subscription và lịch sử gia hạn"""
    subscription = get_object_or_404(UserSubscription, id=subscription_id)
    
    # Kiểm tra xem subscription có hết hạn không
    today = timezone.now()
    grace_period = 7  # Số ngày ân hạn
    grace_date = today - timedelta(days=grace_period)
    
    # Nếu subscription đã hết hạn quá thời gian ân hạn nhưng vẫn đang active, cập nhật trạng thái
    if subscription.end_date < grace_date and subscription.status == 'active':
        subscription.status = 'expired'
        subscription.save()
        messages.warning(request, f'Gói đăng ký này đã hết hạn và được tự động cập nhật thành trạng thái "Hết hạn".')
    
    # Nếu sắp hết hạn (trong vòng 7 ngày), hiển thị cảnh báo
    elif subscription.end_date > today and subscription.end_date <= today + timedelta(days=7) and subscription.status == 'active':
        days_left = (subscription.end_date - today).days
        messages.warning(request, f'Gói đăng ký này sẽ hết hạn trong {days_left} ngày nữa. Vui lòng gia hạn nếu cần thiết.')
    
    # Tính toán % thời gian còn lại
    total_days = (subscription.end_date - subscription.start_date).days
    if total_days <= 0:
        total_days = 30  # Mặc định nếu có lỗi
        
    days_left = (subscription.end_date - today).days
    if days_left < 0:
        days_left = 0
        percentage = 0
    else:
        percentage = min(100, round((days_left / total_days) * 100))
    
    # Lấy lịch sử giao dịch của subscription
    transactions = subscription.transactions.all().order_by('-created_at')
    
    context = {
        'subscription': subscription,
        'days_left': days_left,
        'percentage': percentage,
        'transactions': transactions,
        'active_tab': 'subscriptions',
        'title': f'Chi tiết gói #{subscription.id}',
    }
    
    return render(request, 'dashboard/subscriptions/detail.html', context)

@login_required
@user_passes_test(is_admin)
def renew_subscription(request, subscription_id):
    """Gia hạn một subscription"""
    if request.method != 'POST':
        return redirect('dashboard:subscription_list')
    
    subscription = get_object_or_404(UserSubscription, id=subscription_id)
    duration_days = request.POST.get('duration_days', 30)
    
    try:
        duration_days = int(duration_days)
        if duration_days <= 0:
            raise ValueError("Thời hạn gia hạn phải lớn hơn 0")
        
        # Cập nhật ngày hết hạn
        if subscription.end_date < timezone.now():
            # Nếu đã hết hạn, tính từ ngày hiện tại
            subscription.end_date = timezone.now() + timedelta(days=duration_days)
        else:
            # Nếu chưa hết hạn, cộng thêm vào ngày hết hạn hiện tại
            subscription.end_date = subscription.end_date + timedelta(days=duration_days)
        
        subscription.status = 'active'
        subscription.save()
        
        # Lưu giao dịch gia hạn
        subscription.transactions.create(
            transaction_type='renewal',
            amount=subscription.plan.price,
            payment_method='manual',
            transaction_id=f'RENEW{timezone.now().strftime("%Y%m%d%H%M%S")}'
        )
        
        messages.success(request, f'Đã gia hạn thành công gói {subscription.plan.name} thêm {duration_days} ngày')
    except Exception as e:
        messages.error(request, f'Lỗi gia hạn: {str(e)}')
    
    return redirect('dashboard:subscription_detail', subscription_id=subscription_id)

@login_required
@user_passes_test(is_admin)
def cancel_subscription(request, subscription_id):
    """Hủy một subscription"""
    if request.method != 'POST':
        return redirect('dashboard:subscription_list')
    
    subscription = get_object_or_404(UserSubscription, id=subscription_id)
    
    subscription.status = 'cancelled'
    subscription.save()
    
    messages.success(request, f'Đã hủy gói {subscription.plan.name} của {subscription.user.username}')
    
    return redirect('dashboard:subscription_detail', subscription_id=subscription_id)

@login_required
@user_passes_test(is_admin)
def subscription_plans(request):
    """Quản lý các gói đăng ký subscription"""
    from ..models.subscription import SubscriptionPlan
    
    plans = SubscriptionPlan.objects.all().order_by('price')
    
    if request.method == 'POST':
        # Xử lý thêm/sửa gói đăng ký
        plan_id = request.POST.get('plan_id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        duration_days = request.POST.get('duration_days')
        max_warranty_count = request.POST.get('max_warranty_count', 0)
        is_active = request.POST.get('is_active') == 'on'
        
        if plan_id:
            # Cập nhật gói hiện có
            plan = get_object_or_404(SubscriptionPlan, id=plan_id)
            plan.name = name
            plan.description = description
            plan.price = price
            plan.duration_days = duration_days
            plan.max_warranty_count = max_warranty_count
            plan.is_active = is_active
            plan.save()
            messages.success(request, f'Đã cập nhật gói {name}')
        else:
            # Tạo gói mới
            SubscriptionPlan.objects.create(
                name=name,
                description=description,
                price=price,
                duration_days=duration_days,
                max_warranty_count=max_warranty_count,
                is_active=is_active
            )
            messages.success(request, f'Đã thêm gói {name}')
            
        return redirect('dashboard:subscription_plans')
    
    return render(request, 'dashboard/subscriptions/plans.html', {
        'plans': plans,
        'title': 'Quản lý gói đăng ký',
        'active_tab': 'subscriptions'
    })

@login_required
@user_passes_test(is_admin)
def delete_subscription_plan(request, plan_id):
    """Xóa gói đăng ký"""
    from ..models.subscription import SubscriptionPlan
    
    if request.method == 'POST':
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        plan_name = plan.name
        plan.delete()
        messages.success(request, f'Đã xóa gói {plan_name}')
        return redirect('dashboard:subscription_plans')
    
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    return render(request, 'dashboard/subscriptions/delete_plan.html', {
        'plan': plan,
        'title': 'Xóa gói đăng ký',
        'active_tab': 'subscriptions'
    })

@login_required
@user_passes_test(is_admin)
def create_subscription(request):
    """Tạo đăng ký mới cho người dùng"""
    from ..models.subscription import SubscriptionPlan, UserSubscription
    
    if request.method == 'POST':
        user_id = request.POST.get('user')
        plan_id = request.POST.get('plan')
        
        if not user_id or not plan_id:
            messages.error(request, 'Vui lòng chọn người dùng và gói đăng ký')
            return redirect('dashboard:create_subscription')
            
        user = get_object_or_404(CustomUser, id=user_id)
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        
        # Kiểm tra người dùng đã có gói đang hoạt động hay chưa
        active_sub = UserSubscription.objects.filter(user=user, status='active').first()
        if active_sub:
            messages.warning(request, f'Người dùng {user.username} đã có gói {active_sub.plan.name} đang hoạt động')
            return redirect('dashboard:subscription_list')
            
        # Tạo subscription mới
        start_date = timezone.now()
        end_date = start_date + timedelta(days=plan.duration_days)
        
        subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            status='active'
        )
        
        # Tạo transaction
        subscription.transactions.create(
            transaction_type='new',
            amount=plan.price,
            payment_method=request.POST.get('payment_method', 'manual'),
            transaction_id=f'NEW{timezone.now().strftime("%Y%m%d%H%M%S")}'
        )
        
        messages.success(request, f'Đã tạo gói đăng ký {plan.name} cho {user.username}')
        return redirect('dashboard:subscription_detail', subscription_id=subscription.id)
        
    # Lấy dữ liệu cho form
    users = CustomUser.objects.filter(is_active=True).order_by('username')
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    
    return render(request, 'dashboard/subscriptions/create.html', {
        'users': users,
        'plans': plans,
        'title': 'Tạo đăng ký mới',
        'active_tab': 'subscriptions'
    })

@login_required
@user_passes_test(is_admin)
def extend_all_subscriptions(request):
    """Gia hạn tất cả các gói đăng ký đang hoạt động"""
    from ..models.subscription import UserSubscription
    
    if request.method == 'POST':
        days = request.POST.get('days')
        try:
            days = int(days)
            if days <= 0:
                raise ValueError("Số ngày phải là số dương")
                
            active_subs = UserSubscription.objects.filter(status='active')
            count = 0
            
            for sub in active_subs:
                sub.end_date = sub.end_date + timedelta(days=days)
                sub.save()
                
                # Lưu giao dịch
                sub.transactions.create(
                    transaction_type='extension',
                    amount=0,  # Miễn phí
                    payment_method='system',
                    transaction_id=f'EXT{timezone.now().strftime("%Y%m%d%H%M%S")}'
                )
                count += 1
                
            messages.success(request, f'Đã gia hạn {count} gói đăng ký thêm {days} ngày')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            
    return redirect('dashboard:subscription_list')

@login_required
@user_passes_test(is_admin)
def export_subscriptions(request):
    """Xuất danh sách đăng ký ra CSV"""
    from ..models.subscription import UserSubscription
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="subscriptions.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Người dùng', 'Email', 'Gói', 'Ngày bắt đầu', 'Ngày kết thúc', 'Trạng thái'])
    
    subscriptions = UserSubscription.objects.all().select_related('user', 'plan')
    
    for sub in subscriptions:
        writer.writerow([
            sub.id,
            sub.user.username,
            sub.user.email,
            sub.plan.name,
            sub.start_date.strftime('%d/%m/%Y'),
            sub.end_date.strftime('%d/%m/%Y'),
            sub.status
        ])
        
    return response 