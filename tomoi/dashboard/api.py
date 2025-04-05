from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.utils import timezone
from store.models import Order
from accounts.models import CustomUser

def is_admin(user):
    """Kiểm tra user có phải là admin hoặc staff không"""
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def get_user_orders(request):
    """API lấy danh sách đơn hàng của người dùng"""
    user_id = request.GET.get('user_id')
    
    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Thiếu thông tin người dùng'}, status=400)
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy người dùng'}, status=404)
    
    orders = Order.objects.filter(user=user).order_by('-created_at')[:10]
    
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'code': order.code,
            'total': str(order.total),
            'status': order.status,
            'created_at': order.created_at.strftime('%d/%m/%Y %H:%M')
        })
    
    return JsonResponse({'status': 'success', 'orders': orders_data})

@login_required
@user_passes_test(is_admin)
def search_orders(request):
    """API tìm kiếm đơn hàng của người dùng"""
    user_id = request.GET.get('user_id')
    query = request.GET.get('query', '')
    
    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Thiếu thông tin người dùng'}, status=400)
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy người dùng'}, status=404)
    
    orders = Order.objects.filter(
        Q(user=user) & 
        (Q(code__icontains=query) | Q(status__icontains=query))
    ).order_by('-created_at')[:10]
    
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'code': order.code,
            'total': str(order.total),
            'status': order.status,
            'created_at': order.created_at.strftime('%d/%m/%Y %H:%M')
        })
    
    return JsonResponse({'status': 'success', 'orders': orders_data}) 