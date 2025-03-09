# Tạo file này để biến views thành một package 

# Đảm bảo package views được khởi tạo đúng
# Có thể import các hàm thường dùng ở đây để dễ truy cập 

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .marketing import *
from .settings import *
from .api import *
from .chatbot import *
from .source import *
from .user import (
    user_list,
    user_detail,
    user_edit,
    user_permissions,
    user_activity_log,
    user_login_history,
    terminate_session,
    terminate_all_sessions,
    toggle_user_status,
    user_add,
    user_delete,
    import_users,
    user_report,
    user_stats
)
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Avg
from store.models import Order, Product, OrderItem
from accounts.models import CustomUser
from django.utils import timezone
from datetime import timedelta
from dashboard.models import SystemNotification
# from .analytics import *
# from .reports import *
# from .performance import *1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
from .user_views import *
from .user import *
from .marketing import *
from .source import *
from .discount import *
from .banner import *
from .api_settings import api_settings, save_api_config, test_api
from .chatbot import (
    dashboard, 
    chatbot_api_settings,
    chatbot_save_api,
    chatbot_test_api,
    settings,
    logs,
    responses
)

# Hàm tạm thời cho các view chưa được triển khai
def not_implemented(request, *args, **kwargs):
    return render(request, 'dashboard/not_implemented.html', {
        'message': 'Chức năng này đang được phát triển'
    })

# Gán các hàm tạm thời cho các view chưa triển khai
order_management = not_implemented
order_detail = not_implemented
update_order_status = not_implemented
export_orders = not_implemented
user_management = not_implemented
export_users = not_implemented
warranty_management = not_implemented

# Analytics
analytics_dashboard = not_implemented
sales_report = not_implemented
user_analytics = not_implemented
marketing_analytics = not_implemented
custom_report = not_implemented

# Products
product_list = not_implemented
add_product = not_implemented
edit_product = not_implemented
delete_product = not_implemented
category_list = not_implemented
add_category = not_implemented
edit_category = not_implemented
import_products = not_implemented
product_detail = not_implemented
get_product = not_implemented

# Marketing
marketing_dashboard = not_implemented
campaign_list = not_implemented
add_campaign = not_implemented
banner_list = not_implemented
add_banner = not_implemented
edit_banner = not_implemented

# Settings
settings_dashboard = not_implemented
update_general_settings = not_implemented
email_settings = not_implemented
update_email_settings = not_implemented
payment_settings = not_implemented
update_payment_settings = not_implemented

# API
api_key_list = not_implemented
add_api_key = not_implemented
toggle_api_key = not_implemented
delete_api_key = not_implemented
webhook_list = not_implemented
add_webhook = not_implemented
edit_webhook = not_implemented
delete_webhook = not_implemented
api_logs = not_implemented
get_log_details = not_implemented
api_source_products = not_implemented
get_source_base_price = not_implemented

# User Management
add_user = not_implemented
delete_user = not_implemented

# Warranty Management
warranty_detail = not_implemented
warranty_report = not_implemented
send_new_account = not_implemented
create_warranty = not_implemented
update_warranty_status = not_implemented
assign_warranty = not_implemented
add_warranty_note = not_implemented
delete_warranty = not_implemented

# Subscription Management
subscription_management = not_implemented
subscription_plans = not_implemented

# Source Management
source_dashboard = not_implemented
source_list = not_implemented
source_add = not_implemented
source_edit = not_implemented
source_delete = not_implemented
source_log_list = not_implemented
compare_sources = not_implemented
add_source_product = not_implemented
add_source_log = not_implemented
source_analytics = not_implemented
share_report = not_implemented
source_chart_data = not_implemented
add_source_redirect = not_implemented

# Reports
product_report = not_implemented
customer_report = not_implemented
reports_analysis = not_implemented
revenue_report = not_implemented
popular_products = not_implemented
processing_time = not_implemented

# Accounts
account_types = not_implemented
account_transactions = not_implemented
tcoin_accounts = not_implemented

# Chat
chat_messages = not_implemented
chat_sessions = not_implemented

# Email
email_logs = not_implemented
email_templates = not_implemented
email_editor = not_implemented
email_save_template = not_implemented

@staff_member_required
def analytics(request):
    # Thống kê người dùng
    total_users = CustomUser.objects.count()
    new_users_24h = CustomUser.objects.filter(
        date_joined__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    # Tỷ lệ tăng trưởng người dùng
    users_last_week = CustomUser.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()
    user_growth_rate = ((new_users_24h - users_last_week) / users_last_week * 100) if users_last_week > 0 else 0

    # Nguồn truy cập
    traffic_sources = CustomUser.objects.values('registration_source').annotate(
        count=Count('id')
    )

    # Thiết bị sử dụng
    device_usage = CustomUser.objects.values('last_login_device').annotate(
        count=Count('id')
    )

    # Biểu đồ người dùng mới theo ngày
    user_growth_chart = CustomUser.objects.extra({
        'day': "date(date_joined)"
    }).values('day').annotate(
        count=Count('id')
    ).order_by('day')

    context = {
        'total_users': total_users,
        'new_users_24h': new_users_24h,
        'user_growth_rate': user_growth_rate,
        'traffic_sources': list(traffic_sources),
        'device_usage': list(device_usage),
        'user_growth_chart': list(user_growth_chart),
        'notifications': SystemNotification.objects.filter(is_active=True)[:5]
    }
    return render(request, 'dashboard/analytics.html', context)

@staff_member_required
def reports(request):
    """Trang báo cáo"""
    context = {
        'sales_report': generate_sales_report(),
        'user_activity_report': generate_user_activity_report(),
    }
    return render(request, 'dashboard/reports.html', context)

@staff_member_required
def performance(request):
    """Trang hiệu suất hệ thống"""
    context = {
        'server_metrics': get_server_performance_metrics(),
        'database_performance': analyze_database_performance(),
    }
    return render(request, 'dashboard/performance.html', context)

# Các hàm hỗ trợ (bạn cần triển khai chi tiết)
def calculate_user_growth_rate():
    # Logic tính toán tỷ lệ tăng trưởng người dùng
    pass

def calculate_bounce_rate():
    # Logic tính toán tỷ lệ thoát
    pass

def calculate_conversion_rate():
    # Logic tính toán tỷ lệ chuyển đổi
    pass

def generate_sales_report():
    # Logic tạo báo cáo doanh số
    pass

def generate_user_activity_report():
    # Logic tạo báo cáo hoạt động người dùng
    pass

def get_server_performance_metrics():
    # Logic lấy các chỉ số hiệu suất server
    pass

def analyze_database_performance():
    # Logic phân tích hiệu suất database
    pass 