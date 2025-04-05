from accounts.models import CustomUser
from store.models import Order
from dashboard.models import WarrantyRequest, DashboardSummary
from django.utils import timezone
from django.db.models import Sum, Count, Q

def update_dashboard_summary():
    """Cập nhật bảng tổng hợp dữ liệu cho dashboard"""
    today = timezone.now().date()
    
    # Tìm hoặc tạo mới bản ghi cho ngày hôm nay
    summary, created = DashboardSummary.objects.get_or_create(date=today)
    
    # Cập nhật các thông số
    summary.total_users = CustomUser.objects.count()
    summary.active_users = CustomUser.objects.filter(is_active=True).count() 
    summary.new_users = CustomUser.objects.filter(date_joined__date=today).count()
    
    summary.total_orders = Order.objects.count()
    summary.completed_orders = Order.objects.filter(status='completed').count()
    
    # Tính tổng doanh thu
    revenue = Order.objects.filter(status='completed').aggregate(
        total=Sum('orderitem__price')
    )
    summary.total_revenue = revenue['total'] or 0
    
    # Tổng số TCoin trong hệ thống  
    tcoin_sum = CustomUser.objects.aggregate(total=Sum('tcoin'))
    summary.total_tcoin = tcoin_sum['total'] or 0
    
    # Số lượng yêu cầu bảo hành
    summary.warranty_requests = WarrantyRequest.objects.count()
    
    # Lưu lại các thay đổi
    summary.save()
