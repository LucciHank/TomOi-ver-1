from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from accounts.models import PremiumSubscription, TCoinHistory
from django.utils import timezone
import json

@staff_member_required
@require_POST
def send_reminder(request, subscription_id):
    """Gửi lời nhắc gia hạn tới khách hàng"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Phương thức không hợp lệ'})
    
    data = json.loads(request.body)
    methods = data.get('methods', [])
    
    if not methods:
        return JsonResponse({'status': 'error', 'message': 'Vui lòng chọn ít nhất một phương thức gửi'})
    
    subscription = get_object_or_404(PremiumSubscription, id=subscription_id)
    
    # Giả lập gửi thông báo
    sent_methods = []
    for method in methods:
        # Trong thực tế, tại đây sẽ gọi các service gửi thông báo tương ứng
        if method == 'email':
            # Gửi email
            sent_methods.append('Email')
        elif method == 'sms':
            # Gửi SMS
            sent_methods.append('SMS')
        elif method == 'zalo':
            # Gửi thông báo Zalo
            sent_methods.append('Zalo')
    
    # Cập nhật trạng thái subscription
    subscription.status = 'reminded'
    subscription.reminder_sent = True
    subscription.reminder_date = timezone.now().date()
    subscription.save()
    
    return JsonResponse({
        'status': 'success', 
        'message': f'Đã gửi nhắc nhở qua {", ".join(sent_methods)}', 
        'subscription': {
            'id': subscription.id,
            'status': subscription.get_status_display()
        }
    })

@login_required
@require_POST
def cancel_subscription(request, subscription_id):
    """Xử lý khi khách hàng hủy gia hạn và điền khảo sát"""
    try:
        subscription = get_object_or_404(PremiumSubscription, id=subscription_id)
        
        # Kiểm tra quyền truy cập
        if not request.user.is_staff and request.user != subscription.user:
            return JsonResponse({
                'status': 'error',
                'message': 'Bạn không có quyền thực hiện hành động này'
            }, status=403)
        
        # Lấy dữ liệu lý do hủy từ form
        data = json.loads(request.body)
        reasons = data.get('reasons', [])
        other_reason = data.get('otherReason', '')
        
        # Lưu các lý do
        all_reasons = reasons
        if other_reason:
            all_reasons.append(f"Khác: {other_reason}")
        
        # Cập nhật trạng thái subscription
        subscription.status = 'no_renew'
        subscription.cancel_reasons = ', '.join(all_reasons)
        subscription.save()
        
        # Thêm TCoin cho người dùng (50 TCoin)
        user = subscription.user
        user.tcoin_balance += 50
        user.save()
        
        # Lưu lịch sử thêm TCoin
        TCoinHistory.objects.create(
            user=user,
            amount=50,
            balance_after=user.tcoin_balance,
            description="Hoàn thành khảo sát 'không gia hạn'",
            created_by=request.user if request.user.is_staff else user
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Hủy gia hạn thành công và đã thêm 50 TCoin vào tài khoản của bạn'
        })
        
    except PremiumSubscription.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Không tìm thấy thông tin tài khoản premium'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500) 