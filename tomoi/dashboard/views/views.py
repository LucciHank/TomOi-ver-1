from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
import random
import json

def discount_list(request):
    """
    Hiển thị trang danh sách mã giảm giá
    """
    discounts = Discount.objects.all().order_by('-created_at')
    total_discounts = discounts.count()
    active_discounts = discounts.filter(is_active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now()).count()
    total_usage = sum(discount.used_count for discount in discounts)
    
    # Determine if we're on the main dashboard or list view
    if 'dashboard' in request.path:
        # Chỉ lấy các mã giảm giá gần đây cho dashboard
        recent_discounts = discounts[:5]
        top_discounts = discounts.order_by('-used_count')[:5]
        
        # Dữ liệu giả mẫu cho biểu đồ thống kê (sẽ được thay thế bằng dữ liệu thực từ DB)
        # Thông thường sẽ có query thống kê thực tế tại đây
        
        context = {
            'total_discounts': total_discounts,
            'active_discounts': active_discounts,
            'total_usage': total_usage,
            'recent_discounts': recent_discounts,
            'top_discounts': top_discounts,
            'total_savings': 15000000,  # Giả lập dữ liệu, thực tế sẽ có query tính toán
        }
        return render(request, 'dashboard/discounts/dashboard.html', context)
    else:
        # Hiển thị toàn bộ danh sách
        context = {
            'discounts': discounts
        }
        return render(request, 'dashboard/discounts/list.html', context)

def discount_report(request):
    """
    Hiển thị báo cáo chi tiết về việc sử dụng mã giảm giá
    """
    # Lấy tất cả mã giảm giá cho dropdown chọn
    all_discounts = Discount.objects.all().order_by('code')
    
    # Xử lý các tham số lọc
    discount_code = request.GET.get('discount_code', '')
    period = request.GET.get('period', 'month')
    date_range = request.GET.get('date_range', '')
    
    # Thiết lập khoảng thời gian mặc định
    today = timezone.now()
    if period == 'week':
        start_date = today - timezone.timedelta(days=7)
        report_period = '7 ngày qua'
    elif period == 'month':
        start_date = today - timezone.timedelta(days=30)
        report_period = '30 ngày qua'
    elif period == 'quarter':
        start_date = today - timezone.timedelta(days=90)
        report_period = '3 tháng qua'
    elif period == 'year':
        start_date = today - timezone.timedelta(days=365)
        report_period = '1 năm qua'
    else:  # custom
        if date_range:
            try:
                dates = date_range.split(' - ')
                start_date = datetime.strptime(dates[0], '%d/%m/%Y')
                end_date = datetime.strptime(dates[1], '%d/%m/%Y')
                report_period = f"{dates[0]} - {dates[1]}"
            except (ValueError, IndexError):
                # Fallback nếu lỗi định dạng ngày
                start_date = today - timezone.timedelta(days=30)
                end_date = today
                report_period = '30 ngày qua'
        else:
            start_date = today - timezone.timedelta(days=30)
            report_period = '30 ngày qua'
    
    # Mặc định end_date là ngày hiện tại nếu không được đặt
    if not locals().get('end_date'):
        end_date = today
    
    # Query lấy dữ liệu sử dụng mã giảm giá trong khoảng thời gian
    # Đây là giả định, bạn cần điều chỉnh based on model thực tế
    usage_history = DiscountUsage.objects.filter(
        used_at__gte=start_date,
        used_at__lte=end_date
    )
    
    if discount_code:
        usage_history = usage_history.filter(discount__code=discount_code)
    
    # Tổng hợp dữ liệu
    total_orders = usage_history.count()
    total_order_value = sum(usage.original_price for usage in usage_history)
    total_discount_amount = sum(usage.discount_amount for usage in usage_history)
    
    # Tính tỷ lệ giảm trung bình
    if total_order_value > 0:
        average_discount_percentage = (total_discount_amount / total_order_value) * 100
    else:
        average_discount_percentage = 0
    
    # Thống kê theo loại giảm giá
    percentage_usages = usage_history.filter(discount__discount_type='percentage')
    fixed_usages = usage_history.filter(discount__discount_type='fixed')
    
    percentage_count = percentage_usages.count()
    fixed_count = fixed_usages.count()
    
    percentage_amount = sum(usage.discount_amount for usage in percentage_usages)
    fixed_amount = sum(usage.discount_amount for usage in fixed_usages)
    
    # Dữ liệu cho biểu đồ
    # Nếu là hiển thị theo ngày/tuần/tháng, group data tương ứng
    if period in ['week', 'custom'] and (end_date - start_date).days <= 31:
        # Group theo ngày nếu là khoảng ngắn
        date_labels = [(start_date + timezone.timedelta(days=x)).strftime('%d/%m') 
                      for x in range((end_date - start_date).days + 1)]
        
        # Giả lập dữ liệu cho biểu đồ
        usage_counts = [random.randint(0, 10) for _ in range(len(date_labels))]
        discount_amounts = [random.randint(50000, 500000) for _ in range(len(date_labels))]
    else:
        # Group theo tháng nếu là khoảng dài
        month_labels = []
        month_start = start_date.replace(day=1)
        while month_start <= end_date:
            month_labels.append(month_start.strftime('%m/%Y'))
            if month_start.month == 12:
                month_start = month_start.replace(year=month_start.year + 1, month=1)
            else:
                month_start = month_start.replace(month=month_start.month + 1)
        
        # Giả lập dữ liệu cho biểu đồ
        usage_counts = [random.randint(10, 100) for _ in range(len(month_labels))]
        discount_amounts = [random.randint(500000, 5000000) for _ in range(len(month_labels))]
        date_labels = month_labels
    
    context = {
        'all_discounts': all_discounts,
        'usage_history': usage_history,
        'total_orders': total_orders,
        'total_order_value': total_order_value,
        'total_discount_amount': total_discount_amount,
        'average_discount_percentage': average_discount_percentage,
        'percentage_count': percentage_count,
        'fixed_count': fixed_count,
        'percentage_amount': percentage_amount,
        'fixed_amount': fixed_amount,
        'chart_labels': json.dumps(date_labels),
        'usage_counts': json.dumps(usage_counts),
        'discount_amounts': json.dumps(discount_amounts),
        'report_period': report_period,
        'today': today,
    }
    
    return render(request, 'dashboard/discounts/report.html', context) 