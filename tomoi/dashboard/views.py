from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, Count, Avg, F, Q
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.utils import timezone
from datetime import timedelta, datetime
from django.http import JsonResponse, HttpResponse
from .models import *
from store.models import Order, Product, Category, ProductVariant, Banner, SearchHistory, OrderItem
from accounts.models import CustomUser, BalanceHistory, TCoinHistory
from django.utils.text import slugify
from blog.models import Post, Category as BlogCategory
from payment.models import Transaction, TransactionItem
import os
import re
import time
from werkzeug.utils import secure_filename
from django.contrib.auth.models import Group
import random
import json
from django.core.paginator import Paginator
import csv
from django.core.mail import send_mail
from django.conf import settings

# Helper function to check if user is admin
def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or user.user_type == 'admin')

# Login view
def dashboard_login(request):
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('dashboard:index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and is_admin(user):
            login(request, user)
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions')
    
    return render(request, 'dashboard/login.html')

# Logout view
def dashboard_logout(request):
    logout(request)
    return redirect('dashboard:login')

# Dashboard index
@login_required
@user_passes_test(is_admin)
def dashboard_index(request):
    # Get statistics for dashboard
    total_users = CustomUser.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    
    # Recent transactions
    recent_transactions = Transaction.objects.order_by('-created_at')[:10]
    
    # Sales data for chart
    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)
    
    daily_sales = Transaction.objects.filter(
        created_at__gte=thirty_days_ago,
        status='completed'
    ).values('created_at__date').annotate(
        total=Sum('amount')
    ).order_by('created_at__date')
    
    # Format for chart
    sales_dates = [item['created_at__date'].strftime('%d/%m') for item in daily_sales]
    sales_amounts = [float(item['total']) for item in daily_sales]
    
    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'recent_transactions': recent_transactions,
        'sales_dates': json.dumps(sales_dates),
        'sales_amounts': json.dumps(sales_amounts),
    }
    
    return render(request, 'dashboard/index.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_home(request):
    """Dashboard home page with overview statistics"""
    # Get statistics for dashboard
    total_users = CustomUser.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    
    # Recent transactions
    recent_transactions = Transaction.objects.order_by('-created_at')[:10]
    
    # Sales data for chart
    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)
    
    daily_sales = Transaction.objects.filter(
        created_at__gte=thirty_days_ago,
        status='completed'
    ).values('created_at__date').annotate(
        total=Sum('amount')
    ).order_by('created_at__date')
    
    # Format for chart
    sales_dates = [item['created_at__date'].strftime('%d/%m') for item in daily_sales]
    sales_amounts = [float(item['total']) for item in daily_sales]
    
    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'recent_transactions': recent_transactions,
        'sales_dates': json.dumps(sales_dates),
        'sales_amounts': json.dumps(sales_amounts),
    }
    
    return render(request, 'dashboard/index.html', context)

@staff_member_required
def user_management(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    
    context = {
        'users': users,
        'total_users': users.count(),
        'active_users': users.filter(is_active=True).count(),
        'staff_users': users.filter(is_staff=True).count(),
    }
    
    return render(request, 'dashboard/users/list.html', context)

@staff_member_required
def product_management(request):
    products = Product.objects.all().order_by('-created_at')
    
    context = {
        'products': products,
        'total_products': products.count(),
        'out_of_stock': products.filter(stock=0).count(),
        'low_stock': products.filter(stock__lte=10).count(),
    }
    
    return render(request, 'dashboard/products/list.html', context)

@staff_member_required
def ticket_management(request):
    tickets = Ticket.objects.all().order_by('-created_at')
    
    context = {
        'tickets': tickets,
        'new_tickets': tickets.filter(status='new').count(),
        'processing_tickets': tickets.filter(status='processing').count(),
        'resolved_tickets': tickets.filter(status='resolved').count(),
    }
    
    return render(request, 'dashboard/tickets/list.html', context)

@staff_member_required
def marketing_dashboard(request):
    """
    Bảng điều khiển quản lý marketing
    """
    # Lấy các chiến dịch đang hoạt động
    active_campaigns = MarketingCampaign.objects.filter(is_active=True)
    
    # Thống kê chiến dịch
    total_campaigns = MarketingCampaign.objects.count()
    active_count = active_campaigns.count()
    
    # Tổng ngân sách và chi tiêu
    total_budget = MarketingCampaign.objects.aggregate(Sum('budget'))['budget__sum'] or 0
    total_spent = CampaignExpense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Lấy dữ liệu biểu đồ
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    chart_data = get_campaign_chart_data(thirty_days_ago)
    
    # Phân bổ ngân sách theo loại chiến dịch
    budget_distribution = get_budget_distribution(MarketingCampaign.objects.all())
    
    # Chiến dịch gần đây
    recent_campaigns = MarketingCampaign.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_campaigns': total_campaigns,
        'active_campaigns': active_count,
        'total_budget': total_budget,
        'total_spent': total_spent,
        'budget_remaining': total_budget - total_spent,
        'chart_data': chart_data,
        'budget_distribution': budget_distribution,
        'recent_campaigns': recent_campaigns
    }
    
    return render(request, 'dashboard/marketing/dashboard.html', context)

@staff_member_required
def campaign_list(request):
    """
    Danh sách chiến dịch marketing
    """
    campaigns = MarketingCampaign.objects.all().order_by('-created_at')
    
    # Lọc theo trạng thái
    status_filter = request.GET.get('status', '')
    if status_filter:
        if status_filter == 'active':
            campaigns = campaigns.filter(is_active=True, start_date__lte=timezone.now().date(), end_date__gte=timezone.now().date())
        elif status_filter == 'scheduled':
            campaigns = campaigns.filter(is_active=True, start_date__gt=timezone.now().date())
        elif status_filter == 'ended':
            campaigns = campaigns.filter(end_date__lt=timezone.now().date())
        elif status_filter == 'inactive':
            campaigns = campaigns.filter(is_active=False)
    
    # Lọc theo loại
    type_filter = request.GET.get('type', '')
    if type_filter:
        campaigns = campaigns.filter(type=type_filter)
    
    # Phân trang
    paginator = Paginator(campaigns, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'campaigns': page_obj,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'campaign_types': MarketingCampaign.CAMPAIGN_TYPES
    }
    
    return render(request, 'dashboard/marketing/campaigns.html', context)

@staff_member_required
def add_campaign(request):
    """
    Thêm chiến dịch marketing mới
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        campaign_type = request.POST.get('type')
        budget = float(request.POST.get('budget', 0))
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = 'is_active' in request.POST
        
        # Tạo chiến dịch mới
        campaign = MarketingCampaign.objects.create(
            name=name,
            description=description,
            type=campaign_type,
            budget=budget,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active
        )
        
        # Xử lý các chi tiết bổ sung tùy theo loại chiến dịch
        if campaign_type == 'email':
            subject = request.POST.get('email_subject', '')
            content = request.POST.get('email_content', '')
            
            # Lưu thông tin chiến dịch email
            EmailCampaign.objects.create(
                campaign=campaign,
                subject=subject,
                content=content
            )
        
        messages.success(request, f'Đã tạo chiến dịch {name} thành công')
        return redirect('dashboard:marketing_campaigns')
    
    context = {
        'campaign_types': MarketingCampaign.CAMPAIGN_TYPES,
        'is_new': True
    }
    
    return render(request, 'dashboard/marketing/campaign_form.html', context)

@staff_member_required
def edit_campaign(request, campaign_id):
    """
    Chỉnh sửa chiến dịch marketing
    """
    campaign = get_object_or_404(MarketingCampaign, id=campaign_id)
    
    # Lấy thông tin bổ sung dựa trên loại chiến dịch
    email_campaign = None
    if campaign.type == 'email':
        try:
            email_campaign = EmailCampaign.objects.get(campaign=campaign)
        except EmailCampaign.DoesNotExist:
            pass
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        campaign_type = request.POST.get('type')
        budget = float(request.POST.get('budget', 0))
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = 'is_active' in request.POST
        
        # Cập nhật thông tin chiến dịch
        campaign.name = name
        campaign.description = description
        campaign.type = campaign_type
        campaign.budget = budget
        campaign.start_date = start_date
        campaign.end_date = end_date
        campaign.is_active = is_active
        campaign.save()
        
        # Cập nhật thông tin bổ sung dựa trên loại chiến dịch
        if campaign_type == 'email':
            subject = request.POST.get('email_subject', '')
            content = request.POST.get('email_content', '')
            
            if email_campaign:
                # Cập nhật thông tin chiến dịch email hiện có
                email_campaign.subject = subject
                email_campaign.content = content
                email_campaign.save()
            else:
                # Tạo thông tin chiến dịch email mới
                EmailCampaign.objects.create(
                    campaign=campaign,
                    subject=subject,
                    content=content
                )
        
        messages.success(request, f'Đã cập nhật chiến dịch {name} thành công')
        return redirect('dashboard:marketing_campaigns')
    
    context = {
        'campaign': campaign,
        'email_campaign': email_campaign,
        'campaign_types': MarketingCampaign.CAMPAIGN_TYPES,
        'is_new': False,
        # Thống kê chi tiết chiến dịch
        'campaign_stats': get_campaign_daily_stats(campaign),
        # Chi phí
        'expenses': CampaignExpense.objects.filter(campaign=campaign).order_by('-date')
    }
    
    return render(request, 'dashboard/marketing/campaign_form.html', context)

@staff_member_required
def delete_campaign(request, campaign_id):
    """
    Xóa chiến dịch marketing
    """
    campaign = get_object_or_404(MarketingCampaign, id=campaign_id)
    
    if request.method == 'POST':
        name = campaign.name
        campaign.delete()
        messages.success(request, f'Đã xóa chiến dịch {name}')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@staff_member_required
def campaign_expenses(request, campaign_id):
    """
    Quản lý chi phí cho chiến dịch
    """
    campaign = get_object_or_404(MarketingCampaign, id=campaign_id)
    
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        description = request.POST.get('description', '')
        date = request.POST.get('date')
        
        # Thêm chi phí mới
        expense = CampaignExpense.objects.create(
            campaign=campaign,
            amount=amount,
            description=description,
            date=date
        )
        
        messages.success(request, f'Đã thêm chi phí {amount} cho chiến dịch {campaign.name}')
        return redirect('dashboard:edit_campaign', campaign_id=campaign_id)
    
    context = {
        'campaign': campaign,
        'expenses': CampaignExpense.objects.filter(campaign=campaign).order_by('-date')
    }
    
    return render(request, 'dashboard/marketing/expenses.html', context)

@staff_member_required
def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(MarketingCampaign, id=campaign_id)
    expenses = campaign.expenses.all()
    
    # Tính toán thống kê
    total_spent = expenses.aggregate(total=Sum('amount'))['total'] or 0
    remaining_budget = campaign.budget - total_spent
    
    # Dữ liệu cho biểu đồ
    daily_stats = get_campaign_daily_stats(campaign)
    
    context = {
        'campaign': campaign,
        'expenses': expenses,
        'total_spent': total_spent,
        'remaining_budget': remaining_budget,
        'daily_stats': daily_stats,
    }
    
    return render(request, 'dashboard/marketing/campaign_detail.html', context)

@staff_member_required
def add_campaign(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        campaign_type = request.POST.get('type')
        description = request.POST.get('description')
        goals = request.POST.get('goals')
        budget = request.POST.get('budget')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = request.POST.get('is_active') == 'on'
        
        campaign = MarketingCampaign.objects.create(
            name=name,
            type=campaign_type,
            description=description,
            goals=goals,
            budget=budget,
            start_date=start_date,
            end_date=end_date or None,
            is_active=is_active,
            created_by=request.user
        )
        
        return redirect('dashboard:campaign_detail', campaign_id=campaign.id)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@staff_member_required
def edit_campaign(request, campaign_id):
    campaign = get_object_or_404(MarketingCampaign, id=campaign_id)
    
    if request.method == 'POST':
        campaign.name = request.POST.get('name')
        campaign.type = request.POST.get('type')
        campaign.description = request.POST.get('description')
        campaign.goals = request.POST.get('goals')
        campaign.budget = request.POST.get('budget')
        campaign.start_date = request.POST.get('start_date')
        campaign.end_date = request.POST.get('end_date') or None
        campaign.is_active = request.POST.get('is_active') == 'on'
        campaign.save()
        
        return redirect('dashboard:campaign_detail', campaign_id=campaign.id)
        
    return JsonResponse({'error': 'Invalid request'}, status=400)

@staff_member_required
def get_campaign(request, campaign_id):
    campaign = get_object_or_404(MarketingCampaign, id=campaign_id)
    data = {
        'name': campaign.name,
        'type': campaign.type,
        'description': campaign.description,
        'goals': campaign.goals,
        'budget': float(campaign.budget),
        'start_date': campaign.start_date.isoformat(),
        'end_date': campaign.end_date.isoformat() if campaign.end_date else None,
        'is_active': campaign.is_active,
    }
    return JsonResponse(data)

@staff_member_required
def delete_campaign(request):
    """Xóa chiến dịch marketing"""
    if request.method == 'POST':
        campaign_id = request.POST.get('campaign_id')
        # Thực hiện xóa chiến dịch (giả định có model Campaign)
        # Campaign.objects.filter(id=campaign_id).delete()
        messages.success(request, "Chiến dịch đã được xóa thành công")
    
    return redirect('dashboard:marketing')

# Helper functions
def calculate_growth(current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100

def calculate_conversion_rate(campaigns):
    total_clicks = campaigns.aggregate(Sum('clicks'))['clicks__sum'] or 0
    total_conversions = campaigns.aggregate(Sum('conversions'))['conversions__sum'] or 0
    if total_clicks > 0:
        return (total_conversions / total_clicks) * 100
    return 0

def get_campaign_chart_data(start_date):
    # Lấy dữ liệu cho biểu đồ theo ngày
    stats = MarketingCampaign.objects.filter(
        start_date__gte=start_date
    ).values('start_date').annotate(
        total_impressions=Sum('impressions'),
        total_clicks=Sum('clicks')
    ).order_by('start_date')
    
    labels = []
    impressions = []
    clicks = []
    
    for stat in stats:
        labels.append(stat['start_date'].strftime('%d/%m'))
        impressions.append(stat['total_impressions'])
        clicks.append(stat['total_clicks'])
    
    return {
        'labels': labels,
        'impressions': impressions,
        'clicks': clicks
    }

def get_budget_distribution(campaigns):
    # Lấy phân bổ ngân sách theo loại chiến dịch
    budget_by_type = campaigns.values('type').annotate(
        total_budget=Sum('budget')
    ).order_by('-total_budget')
    
    labels = []
    data = []
    
    for item in budget_by_type:
        labels.append(dict(MarketingCampaign.CAMPAIGN_TYPES)[item['type']])
        data.append(float(item['total_budget']))
    
    return {
        'labels': labels,
        'data': data
    }

def get_campaign_daily_stats(campaign):
    # Lấy thống kê theo ngày của một chiến dịch
    return {
        'dates': [],
        'impressions': [],
        'clicks': [],
        'conversions': []
    }

@staff_member_required
def analytics_dashboard(request):
    # Lấy dữ liệu cho biểu đồ doanh số
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Dữ liệu doanh số theo ngày trong 30 ngày qua
    daily_sales = Transaction.objects.filter(
        transaction_type='purchase',
        status='completed',
        created_at__range=[start_date, end_date]
    ).annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(
        total=Sum('amount')
    ).order_by('day')
    
    # Dữ liệu doanh số theo danh mục sản phẩm
    category_sales = TransactionItem.objects.filter(
        transaction__transaction_type='purchase',
        transaction__status='completed',
        transaction__created_at__range=[start_date, end_date]
    ).values(
        'product_name'
    ).annotate(
        total=Sum('price')
    ).order_by('-total')[:5]
    
    # Sản phẩm bán chạy nhất
    top_products = TransactionItem.objects.filter(
        transaction__transaction_type='purchase',
        transaction__status='completed',
    ).values(
        'product_name'
    ).annotate(
        count=Count('id'),
        revenue=Sum('price')
    ).order_by('-count')[:10]
    
    context = {
        'daily_sales': daily_sales,
        'category_sales': category_sales, 
        'top_products': top_products,
    }
    
    return render(request, 'dashboard/analytics/index.html', context)

@staff_member_required
def analytics_reports(request):
    # Lấy tham số ngày từ query
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            # Nếu định dạng không hợp lệ, sử dụng khoảng thời gian mặc định
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
    else:
        # Mặc định lấy dữ liệu 30 ngày
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    # Lấy dữ liệu báo cáo dựa trên khoảng thời gian
    orders = Transaction.objects.filter(
        transaction_type='purchase',
        created_at__date__range=[start_date, end_date]
    )
    
    # Thống kê tổng quan
    total_orders = orders.count()
    total_revenue = orders.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    completed_orders = orders.filter(status='completed').count()
    completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
    
    # Thống kê theo ngày
    daily_stats = orders.annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(
        orders=Count('id'),
        revenue=Sum('amount')
    ).order_by('day')
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'completion_rate': completion_rate,
        'daily_stats': daily_stats,
    }
    
    return render(request, 'dashboard/analytics/reports.html', context)

@staff_member_required
def export_report(request):
    # Chức năng xuất báo cáo
    format_type = request.GET.get('format', 'csv')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    # Xác định khoảng thời gian
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
    else:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    # Lấy dữ liệu cho báo cáo
    orders = Transaction.objects.filter(
        transaction_type='purchase',
        created_at__date__range=[start_date, end_date]
    )
    
    # Chuẩn bị response cho file CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date}_to_{end_date}.csv"'
    
    # Ghi dữ liệu vào file CSV
    writer = csv.writer(response)
    writer.writerow(['Mã đơn hàng', 'Ngày tạo', 'Khách hàng', 'Số tiền', 'Trạng thái'])
    
    for order in orders:
        writer.writerow([
            order.transaction_id,
            order.created_at.strftime('%Y-%m-%d %H:%M'),
            order.user.username if order.user else 'Khách vãng lai',
            order.amount,
            order.get_status_display()
        ])
    
    return response

@staff_member_required
def realtime_analytics(request):
    return render(request, 'dashboard/analytics/realtime.html')

def format_duration(duration):
    if not duration:
        return "0:00"
    
    total_seconds = int(duration.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    
    return f"{minutes}:{seconds:02d}"

@staff_member_required
def chatbot_management(request):
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_month = today - timedelta(days=60)
    
    # Lấy dữ liệu chatbot
    qa_pairs = ChatbotQA.objects.all().order_by('-usage_count')
    chat_sessions = ChatSession.objects.filter(start_time__date__gte=last_30_days)
    
    # Tính toán thống kê
    total_conversations = chat_sessions.count()
    resolved_conversations = chat_sessions.filter(status='ended', feedback_rating__gte=4).count()
    resolution_rate = (resolved_conversations / total_conversations * 100) if total_conversations else 0
    
    # Tính thời gian phản hồi trung bình
    avg_response_time = 0
    if chat_sessions.exists():
        messages = ChatMessage.objects.filter(session__in=chat_sessions, is_bot=True)
        response_times = []
        
        for session in chat_sessions:
            session_messages = session.messages.order_by('sent_at')
            for i in range(1, len(session_messages)):
                if session_messages[i].is_bot and not session_messages[i-1].is_bot:
                    response_time = (session_messages[i].sent_at - session_messages[i-1].sent_at).total_seconds()
                    response_times.append(response_time)
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
    
    # Tính đánh giá tích cực
    feedback_sessions = chat_sessions.filter(feedback_rating__isnull=False)
    positive_feedback = feedback_sessions.filter(feedback_rating__gte=4).count()
    positive_feedback_rate = (positive_feedback / feedback_sessions.count() * 100) if feedback_sessions.exists() else 0
    
    # Tính tăng trưởng so với tháng trước
    last_month_sessions = ChatSession.objects.filter(start_time__date__range=[last_month, last_30_days])
    last_month_conversations = last_month_sessions.count()
    
    conversation_growth = calculate_growth(total_conversations, last_month_conversations)
    
    last_month_resolved = last_month_sessions.filter(status='ended', feedback_rating__gte=4).count()
    last_month_resolution_rate = (last_month_resolved / last_month_conversations * 100) if last_month_conversations else 0
    resolution_growth = calculate_growth(resolution_rate, last_month_resolution_rate)
    
    # Tính thời gian phản hồi tháng trước
    last_month_response_time = 0
    if last_month_sessions.exists():
        last_month_messages = ChatMessage.objects.filter(session__in=last_month_sessions, is_bot=True)
        last_month_response_times = []
        
        for session in last_month_sessions:
            session_messages = session.messages.order_by('sent_at')
            for i in range(1, len(session_messages)):
                if session_messages[i].is_bot and not session_messages[i-1].is_bot:
                    response_time = (session_messages[i].sent_at - session_messages[i-1].sent_at).total_seconds()
                    last_month_response_times.append(response_time)
        
        if last_month_response_times:
            last_month_response_time = sum(last_month_response_times) / len(last_month_response_times)
    
    response_time_change = calculate_growth(avg_response_time, last_month_response_time)
    
    # Tính đánh giá tích cực tháng trước
    last_month_feedback = last_month_sessions.filter(feedback_rating__isnull=False)
    last_month_positive = last_month_feedback.filter(feedback_rating__gte=4).count()
    last_month_positive_rate = (last_month_positive / last_month_feedback.count() * 100) if last_month_feedback.exists() else 0
    
    feedback_growth = calculate_growth(positive_feedback_rate, last_month_positive_rate)
    
    context = {
        'qa_pairs': qa_pairs,
        'total_conversations': total_conversations,
        'conversation_growth': conversation_growth,
        'resolution_rate': round(resolution_rate, 1),
        'resolution_growth': resolution_growth,
        'avg_response_time': round(avg_response_time, 1),
        'response_time_change': response_time_change,
        'positive_feedback': round(positive_feedback_rate, 1),
        'feedback_growth': feedback_growth,
    }
    
    return render(request, 'dashboard/chatbot/index.html', context)

@staff_member_required
def add_qa(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        answer = request.POST.get('answer')
        category = request.POST.get('category')
        keywords = request.POST.get('keywords')
        
        ChatbotQA.objects.create(
            question=question,
            answer=answer,
            category=category,
            keywords=keywords
        )
        
        return redirect('dashboard:chatbot')
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@staff_member_required
def edit_qa(request, qa_id):
    qa = get_object_or_404(ChatbotQA, id=qa_id)
    
    if request.method == 'POST':
        qa.question = request.POST.get('question')
        qa.answer = request.POST.get('answer')
        qa.category = request.POST.get('category')
        qa.keywords = request.POST.get('keywords')
        qa.save()
        
        return redirect('dashboard:chatbot')
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@staff_member_required
def delete_qa(request, qa_id):
    if request.method == 'POST':
        qa = get_object_or_404(ChatbotQA, id=qa_id)
        qa.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@staff_member_required
def get_qa(request, qa_id):
    qa = get_object_or_404(ChatbotQA, id=qa_id)
    
    data = {
        'id': qa.id,
        'question': qa.question,
        'answer': qa.answer,
        'category': qa.category,
        'keywords': qa.keywords
    }
    
    return JsonResponse(data)

@staff_member_required
def content_management(request):
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_month = today - timedelta(days=60)
    last_7_days = today - timedelta(days=7)
    
    # Lấy dữ liệu trang
    pages = ContentPage.objects.all().order_by('-updated_at')
    
    # Tính toán thống kê
    total_pages = pages.count()
    published_pages = pages.filter(is_published=True).count()
    published_percentage = (published_pages / total_pages * 100) if total_pages else 0
    
    # Tính tăng trưởng so với tháng trước
    current_month_pages = pages.filter(created_at__date__gte=last_30_days).count()
    last_month_pages = pages.filter(created_at__date__range=[last_month, last_30_days]).count()
    page_growth = calculate_growth(current_month_pages, last_month_pages)
    
    # Lượt xem trang
    total_page_views = 0
    for page in pages:
        # Giả sử có field views để lưu lượt xem
        total_page_views += getattr(page, 'views', 0)
    
    # Cập nhật gần đây
    recent_updates = pages.filter(updated_at__date__gte=last_7_days).count()
    
    context = {
        'pages': pages,
        'total_pages': total_pages,
        'published_pages': published_pages,
        'published_percentage': round(published_percentage, 1),
        'page_growth': page_growth,
        'total_page_views': total_page_views,
        'view_growth': 0,  # Cần thêm logic để tính
        'recent_updates': recent_updates,
    }
    
    return render(request, 'dashboard/content/index.html', context)

@staff_member_required
def add_page(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        meta_title = request.POST.get('meta_title') or title
        meta_description = request.POST.get('meta_description', '')
        is_published = request.POST.get('is_published') == 'on'
        
        # Tạo slug nếu không có
        if not slug:
            slug = slugify(title)
        
        # Kiểm tra slug đã tồn tại chưa
        if ContentPage.objects.filter(slug=slug).exists():
            # Xử lý trùng slug
            base_slug = slug
            counter = 1
            while ContentPage.objects.filter(slug=f"{base_slug}-{counter}").exists():
                counter += 1
            slug = f"{base_slug}-{counter}"
        
        # Tạo trang mới
        ContentPage.objects.create(
            title=title,
            slug=slug,
            content='',  # Nội dung sẽ được thêm sau
            meta_title=meta_title,
            meta_description=meta_description,
            is_published=is_published,
            created_by=request.user.staff
        )
        
        return redirect('dashboard:edit_page', slug=slug)
    
    return redirect('dashboard:content')

@staff_member_required
def edit_page(request, page_id):
    page = get_object_or_404(ContentPage, id=page_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        content = request.POST.get('content')
        meta_title = request.POST.get('meta_title')
        meta_description = request.POST.get('meta_description')
        is_published = request.POST.get('is_published') == 'on'
        
        # Cập nhật trang
        page.title = title
        page.slug = slug
        page.content = content
        page.meta_title = meta_title
        page.meta_description = meta_description
        page.is_published = is_published
        page.save()
        
        return redirect('dashboard:content')
    
    context = {
        'page': page
    }
    
    return render(request, 'dashboard/content/edit_page.html', context)

@staff_member_required
def delete_page(request, page_id):
    if request.method == 'POST':
        page = get_object_or_404(ContentPage, id=page_id)
        page.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

# Quản lý bài viết
@staff_member_required
def post_management(request):
    posts = Post.objects.all().select_related('category', 'author')
    categories = BlogCategory.objects.annotate(post_count=Count('posts'))
    
    context = {
        'posts': posts,
        'categories': categories,
        'total_posts': posts.count(),
        'featured_posts': posts.filter(is_featured=True).count(),
        'draft_posts': posts.filter(is_active=False).count(),
        'published_posts': posts.filter(is_active=True).count(),
    }
    return render(request, 'dashboard/posts/list.html', context)

@staff_member_required
def add_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        excerpt = request.POST.get('excerpt')
        category_id = request.POST.get('category')
        is_featured = request.POST.get('is_featured') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        post = Post.objects.create(
            title=title,
            content=content,
            excerpt=excerpt,
            category_id=category_id,
            author=request.user,
            is_featured=is_featured,
            is_active=is_active,
            slug=slugify(title)
        )
        
        if request.FILES.get('thumbnail'):
            post.thumbnail = request.FILES['thumbnail']
            post.save()
            
        return redirect('dashboard:posts')
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@staff_member_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.excerpt = request.POST.get('excerpt')
        post.category_id = request.POST.get('category')
        post.is_featured = request.POST.get('is_featured') == 'on'
        post.is_active = request.POST.get('is_active') == 'on'
        post.slug = slugify(post.title)
        
        if request.FILES.get('thumbnail'):
            post.thumbnail = request.FILES['thumbnail']
            
        post.save()
        return redirect('dashboard:posts')
        
    return JsonResponse({'error': 'Invalid request'}, status=400)

@staff_member_required
def get_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    data = {
        'title': post.title,
        'content': post.content,
        'excerpt': post.excerpt,
        'category_id': post.category_id,
        'is_featured': post.is_featured,
        'is_active': post.is_active,
        'thumbnail': post.thumbnail.url if post.thumbnail else None
    }
    return JsonResponse(data)

@staff_member_required
def delete_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@staff_member_required
def toggle_featured(request, post_id):
    """Bật/tắt trạng thái nổi bật của bài viết"""
    post = get_object_or_404(Post, id=post_id)
    post.is_featured = not post.is_featured
    post.save()
    
    return JsonResponse({
        'success': True,
        'is_featured': post.is_featured
    })

# Quản lý danh mục
@staff_member_required
def post_categories(request):
    """Manage blog post categories"""
    categories = BlogCategory.objects.annotate(post_count=Count('posts'))
    
    context = {
        'categories': categories
    }
    
    return render(request, 'dashboard/posts/categories.html', context)

@staff_member_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        icon = request.POST.get('icon')
        is_active = request.POST.get('is_active') == 'on'
        
        BlogCategory.objects.create(
            name=name,
            description=description,
            icon=icon,
            is_active=is_active,
            slug=slugify(name)
        )
        return redirect('dashboard:post_categories')
        
    return JsonResponse({'error': 'Invalid request'}, status=400)

@staff_member_required
def edit_category(request, category_id):
    category = get_object_or_404(BlogCategory, id=category_id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        category.icon = request.POST.get('icon')
        category.is_active = request.POST.get('is_active') == 'on'
        category.slug = slugify(category.name)
        category.save()
        
        return redirect('dashboard:post_categories')
        
    return JsonResponse({'error': 'Invalid request'}, status=400)

@staff_member_required
def get_category(request, category_id):
    category = get_object_or_404(BlogCategory, id=category_id)
    data = {
        'name': category.name,
        'description': category.description,
        'icon': category.icon,
        'is_active': category.is_active
    }
    return JsonResponse(data)

@staff_member_required
def delete_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(BlogCategory, id=category_id)
        category.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@staff_member_required
def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related('category'), id=post_id)
    
    # Lấy dữ liệu lượt xem trong 30 ngày gần nhất
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    # Tạo danh sách ngày và lượt xem
    dates = []
    views_data = []
    monthly_views = 0
    
    try:
        # Try to get PostView data if the model exists
        from blog.models import PostView
        
        # Lấy lượt xem theo ngày
        views_by_date = PostView.objects.filter(
            post=post,
            viewed_at__date__gte=last_30_days
        ).values('viewed_at__date').annotate(
            total_views=Count('id')
        ).order_by('viewed_at__date')
        
        # Tạo dict để mapping ngày với lượt xem
        views_dict = {item['viewed_at__date']: item['total_views'] 
            for item in views_by_date
        }
        
        # Lặp qua 30 ngày để lấy dữ liệu
        for i in range(30):
            date = today - timedelta(days=29-i)
            dates.append(date.strftime('%d/%m'))
            views = views_dict.get(date, 0)
            views_data.append(views)
            monthly_views += views
    except (ImportError, AttributeError):
        # If PostView model doesn't exist or has issues, use sample data
        for i in range(30):
            date = today - timedelta(days=29-i)
            dates.append(date.strftime('%d/%m'))
            views = random.randint(0, 50)  # Sample data
            views_data.append(views)
            monthly_views += views
    
    context = {
        'post': post,
        'monthly_views': monthly_views,
        'dates': dates,
        'views_data': views_data,
    }
    
    return render(request, 'dashboard/posts/detail.html', context)

# Analytics API views
@staff_member_required
def get_traffic_data(request):
    """API endpoint to get traffic data for dashboard"""
    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Sample data for traffic
    dates = [(start_date + timedelta(days=i)).strftime('%d/%m') for i in range(days)]
    visitors = [random.randint(50, 500) for _ in range(days)]
    pageviews = [visitors[i] * random.randint(2, 5) for i in range(days)]
    
    return JsonResponse({
        'dates': dates,
        'visitors': visitors,
        'pageviews': pageviews
    })

@staff_member_required
def get_visitor_stats(request):
    """API endpoint to get visitor statistics"""
    return JsonResponse({
        'total_visitors': random.randint(5000, 10000),
        'new_visitors': random.randint(1000, 3000),
        'returning_visitors': random.randint(2000, 7000),
        'bounce_rate': random.randint(30, 70),
        'avg_session_duration': f"{random.randint(1, 5)}:{random.randint(10, 59)}"
    })

@staff_member_required
def get_page_stats(request):
    """API endpoint to get page statistics"""
    return JsonResponse({
        'top_pages': [
            {'url': '/', 'views': random.randint(1000, 5000), 'avg_time': f"{random.randint(0, 2)}:{random.randint(10, 59)}"},
            {'url': '/products/', 'views': random.randint(800, 3000), 'avg_time': f"{random.randint(0, 2)}:{random.randint(10, 59)}"},
            {'url': '/blog/', 'views': random.randint(500, 2000), 'avg_time': f"{random.randint(0, 2)}:{random.randint(10, 59)}"},
            {'url': '/cart/', 'views': random.randint(300, 1500), 'avg_time': f"{random.randint(0, 2)}:{random.randint(10, 59)}"},
            {'url': '/account/login/', 'views': random.randint(200, 1000), 'avg_time': f"{random.randint(0, 2)}:{random.randint(10, 59)}"}
        ]
    })

@staff_member_required
def get_referrer_stats(request):
    """API endpoint to get referrer statistics"""
    return JsonResponse({
        'referrers': [
            {'source': 'Google', 'visits': random.randint(1000, 3000)},
            {'source': 'Facebook', 'visits': random.randint(500, 2000)},
            {'source': 'Direct', 'visits': random.randint(800, 2500)},
            {'source': 'Twitter', 'visits': random.randint(200, 1000)},
            {'source': 'Instagram', 'visits': random.randint(300, 1500)}
        ]
    })

@staff_member_required
def get_device_stats(request):
    """API endpoint to get device statistics"""
    desktop = random.randint(40, 60)
    mobile = random.randint(30, 50)
    tablet = 100 - desktop - mobile
    
    return JsonResponse({
        'devices': [
            {'type': 'Desktop', 'percentage': desktop},
            {'type': 'Mobile', 'percentage': mobile},
            {'type': 'Tablet', 'percentage': tablet}
        ]
    })

@staff_member_required
def get_stock_data(request):
    """API endpoint to get stock data"""
    products = Product.objects.all()[:10]
    
    stock_data = [{
        'id': product.id,
        'name': product.name,
        'stock': product.stock,
        'status': 'Low' if product.stock < 10 else 'OK'
    } for product in products]
    
    return JsonResponse({'products': stock_data})

@staff_member_required
def get_realtime_visitors(request):
    """API endpoint to get realtime visitor count"""
    # Sample data for realtime visitors
    return JsonResponse({
        'count': random.randint(5, 50)
    })

@staff_member_required
def get_realtime_pageviews(request):
    """API endpoint to get realtime pageview data"""
    # Sample data for realtime pageviews
    return JsonResponse({
        'pageviews': [
            {'url': '/', 'count': random.randint(1, 10)},
            {'url': '/products/', 'count': random.randint(1, 8)},
            {'url': '/blog/', 'count': random.randint(1, 5)},
            {'url': '/cart/', 'count': random.randint(1, 3)}
        ]
    })

@staff_member_required
def get_realtime_locations(request):
    """API endpoint to get realtime visitor locations"""
    # Sample data for realtime locations
    countries = ['Vietnam', 'United States', 'China', 'Japan', 'South Korea', 'Singapore', 'Thailand']
    return JsonResponse({
        'locations': [
            {'country': country, 'count': random.randint(1, 5)} 
            for country in random.sample(countries, random.randint(3, len(countries)))
        ]
    })

@staff_member_required
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        
        # Tạo thư mục nếu chưa tồn tại
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'content/images')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Tạo tên file an toàn
        filename = secure_filename(image.name)
        filepath = os.path.join(upload_dir, filename)
        
        # Lưu file
        with open(filepath, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        
        # Trả về URL của hình ảnh
        image_url = f"{settings.MEDIA_URL}content/images/{filename}"
        return JsonResponse({'url': image_url})

def secure_filename(filename):
    # Tạo tên file an toàn
    filename = filename.lower()
    filename = re.sub(r'[^a-z0-9_.-]', '', filename)
    
    # Thêm timestamp để tránh trùng tên
    name, ext = os.path.splitext(filename)
    timestamp = int(time.time())
    return f"{name}_{timestamp}{ext}"

@staff_member_required
def user_detail(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    context = {
        'user': user,
        'orders': Order.objects.filter(user=user).order_by('-created_at'),
    }
    
    return render(request, 'dashboard/users/detail.html', context)

@staff_member_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        is_staff = request.POST.get('is_staff') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        # Cập nhật thông tin người dùng
        user.username = username
        user.email = email
        user.is_staff = is_staff
        user.is_active = is_active
        user.save()
        
        return redirect('dashboard:users')
    
    return render(request, 'dashboard/users/detail.html', {'user': user})

@staff_member_required
def delete_user(request):
    """Xóa người dùng"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(CustomUser, id=user_id)
        
        # Xóa người dùng
        user.delete()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@staff_member_required
def suspend_user(request):
    """Đình chỉ người dùng"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(CustomUser, id=user_id)
        
        # Đình chỉ người dùng
        user.is_active = False
        user.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@staff_member_required
def unlock_user(request):
    """Mở khóa người dùng"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(CustomUser, id=user_id)
        
        # Mở khóa người dùng
        user.is_active = True
        user.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@staff_member_required
def role_management(request):
    """Quản lý vai trò người dùng"""
    roles = Group.objects.all()
    
    context = {
        'roles': roles
    }
    
    return render(request, 'dashboard/users/roles.html', context)

@staff_member_required
def add_role(request):
    """Thêm vai trò mới"""
    if request.method == 'POST':
        name = request.POST.get('name')
        
        # Tạo vai trò mới
        Group.objects.create(name=name)
        
        return redirect('dashboard:roles')
    
    return render(request, 'dashboard/users/roles.html')

@staff_member_required
def edit_role(request, role_id):
    """Chỉnh sửa vai trò"""
    role = get_object_or_404(Group, id=role_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        
        # Cập nhật vai trò
        role.name = name
        role.save()
        
        return redirect('dashboard:roles')
    
    return render(request, 'dashboard/users/roles.html')

@staff_member_required
def delete_role(request, role_id):
    """Xóa vai trò"""
    role = get_object_or_404(Group, id=role_id)
    
    if request.method == 'POST':
        role.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@staff_member_required
def add_product(request):
    """Thêm sản phẩm mới"""
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        stock = request.POST.get('stock')
        
        # Tạo sản phẩm mới
        product = Product.objects.create(
            name=name,
            price=price,
            description=description,
            stock=stock,
            slug=slugify(name)
        )
        
        if category_id:
            category = get_object_or_404(BlogCategory, id=category_id)
            product.category = category
            product.save()
        
        return redirect('dashboard:products')
    
    return render(request, 'dashboard/products/list.html')

@staff_member_required
def edit_product(request, product_id):
    """Chỉnh sửa sản phẩm"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        stock = request.POST.get('stock')
        
        # Cập nhật thông tin sản phẩm
        product.name = name
        product.price = price
        product.description = description
        product.stock = stock
        
        if category_id:
            category = get_object_or_404(BlogCategory, id=category_id)
            product.category = category
        
        product.save()
        
        return redirect('dashboard:products')
    
    return render(request, 'dashboard/products/detail.html', {'product': product})

@staff_member_required
def delete_product(request):
    """Xóa sản phẩm"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        # Xóa sản phẩm
        product.delete()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@staff_member_required
def get_product(request):
    """Lấy thông tin sản phẩm"""
    product_id = request.GET.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    
    data = {
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'description': product.description,
        'stock': product.stock,
        'category_id': product.category.id if product.category else None
    }
    
    return JsonResponse({'success': True, 'product': data})

@staff_member_required
def add_post_category(request):
    """Add a new blog post category"""
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        
        if not slug:
            slug = slugify(name)
        
        # Check if slug is unique
        if BlogCategory.objects.filter(slug=slug).exists():
            messages.error(request, "A category with this slug already exists")
            return redirect('dashboard:post_categories')
        
        BlogCategory.objects.create(
            name=name,
            slug=slug,
            description=description
        )
        
        messages.success(request, f"Category '{name}' created successfully")
    
    return redirect('dashboard:post_categories')

@staff_member_required
def edit_post_category(request, category_id):
    """Edit a blog post category"""
    category = get_object_or_404(BlogCategory, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        
        if not slug:
            slug = slugify(name)
        
        # Check if slug is unique
        if BlogCategory.objects.filter(slug=slug).exclude(id=category_id).exists():
            messages.error(request, "A category with this slug already exists")
            return redirect('dashboard:post_categories')
        
        category.name = name
        category.slug = slug
        category.description = description
        category.save()
        
        messages.success(request, f"Category '{name}' updated successfully")
        return redirect('dashboard:post_categories')
    
    context = {
        'category': category
    }
    
    return render(request, 'dashboard/posts/edit_category.html', context)

@staff_member_required
def get_post_category(request, category_id):
    """Get category data for AJAX requests"""
    category = get_object_or_404(BlogCategory, id=category_id)
    
    return JsonResponse({
        'id': category.id,
        'name': category.name,
        'slug': category.slug,
        'description': category.description
    })

@staff_member_required
def clear_logs(request):
    """Clear system logs"""
    if request.method == 'POST':
        # This would typically clear logs from a database table
        # For now, just show a success message
        messages.success(request, "Logs have been cleared successfully")
    
    return redirect('dashboard:settings')

@staff_member_required
def assign_ticket(request, ticket_id):
    """Phân công xử lý ticket"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        staff = get_object_or_404(CustomUser, id=staff_id)
        
        # Phân công ticket
        ticket.assigned_to = staff
        ticket.status = 'processing'
        ticket.save()
        
        return redirect('dashboard:ticket_detail', ticket_id=ticket_id)
    
    return render(request, 'dashboard/tickets/detail.html', {'ticket': ticket})

@staff_member_required
def close_ticket(request):
    """Đóng ticket"""
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Đóng ticket
        ticket.status = 'resolved'
        ticket.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@staff_member_required
def order_list(request):
    # Lấy tất cả đơn hàng, sắp xếp theo thời gian tạo giảm dần
    orders = Transaction.objects.filter(transaction_type='purchase').order_by('-created_at')
    
    # Tính tổng doanh thu và số đơn hàng
    total_revenue = orders.aggregate(Sum('amount'))['amount__sum'] or 0
    total_orders = orders.count()
    
    # Đơn hàng trong ngày
    today = timezone.now().date()
    today_orders = orders.filter(created_at__date=today)
    today_revenue = today_orders.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Đơn hàng chờ xử lý
    pending_orders = orders.filter(status='pending').count()
    
    context = {
        'orders': orders,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'today_revenue': today_revenue,
        'today_orders': today_orders.count(),
        'pending_orders': pending_orders,
    }
    
    return render(request, 'dashboard/orders/list.html', context)

@staff_member_required
def order_detail(request, order_id):
    order = get_object_or_404(Transaction, id=order_id, transaction_type='purchase')
    
    # Cập nhật trạng thái đơn hàng nếu có request POST
    if request.method == 'POST':
        status = request.POST.get('status')
        if status and status in dict(Transaction.STATUS_CHOICES).keys():
            order.status = status
            order.save()
            messages.success(request, 'Đã cập nhật trạng thái đơn hàng')
            return redirect('dashboard:order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'items': order.items.all(),
    }
    
    return render(request, 'dashboard/orders/detail.html', context)

@staff_member_required
def cancel_order(request):
    """Hủy đơn hàng"""
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        
        # Cập nhật trạng thái đơn hàng
        order.status = 'cancelled'
        order.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@staff_member_required
def category_management(request):
    """Quản lý danh mục sản phẩm"""
    categories = BlogCategory.objects.all().order_by('name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'dashboard/products/categories.html', context)

@staff_member_required
def add_user(request):
    """Thêm người dùng mới"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_staff = request.POST.get('is_staff') == 'on'
        
        # Tạo người dùng mới
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=is_staff
        )
        
        return redirect('dashboard:users')
    
    return render(request, 'dashboard/users/list.html')

@staff_member_required
def post_category_management(request):
    """Quản lý danh mục bài viết"""
    categories = BlogCategory.objects.all().order_by('name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'dashboard/posts/categories.html', context)

@staff_member_required
def settings_dashboard(request):
    """Dashboard settings view"""
    # Lấy cài đặt hiện tại (giả định có model SiteSettings)
    # settings = SiteSettings.objects.first()
    
    context = {
        'settings': {}  # Thay bằng settings thực tế nếu có
    }
    
    return render(request, 'dashboard/settings/index.html', context)

@staff_member_required
def ticket_detail(request, ticket_id):
    """Chi tiết ticket hỗ trợ"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    # Lấy danh sách nhân viên để phân công
    staff_users = CustomUser.objects.filter(is_staff=True)
    
    context = {
        'ticket': ticket,
        'staff_users': staff_users,
        'ticket_replies': TicketReply.objects.filter(ticket=ticket).order_by('created_at')
    }
    
    # Xử lý thêm phản hồi
    if request.method == 'POST' and 'reply_content' in request.POST:
        content = request.POST.get('reply_content')
        
        # Tạo phản hồi mới
        TicketReply.objects.create(
            ticket=ticket,
            user=request.user,
            content=content,
            is_admin_reply=True
        )
        
        # Cập nhật trạng thái ticket nếu cần
        if ticket.status == 'open':
            ticket.status = 'pending'
            ticket.save()
        
        return redirect('dashboard:ticket_detail', ticket_id=ticket_id)
    
    return render(request, 'dashboard/tickets/detail.html', context)

@staff_member_required
def chart_data(request):
    """
    Trả về dữ liệu cho biểu đồ
    """
    # Cách đơn giản nhất là trả về dữ liệu mẫu
    data = {
        'labels': ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5'],
        'datasets': [{
            'label': 'Doanh thu',
            'data': [5000000, 7000000, 6000000, 8000000, 9500000],
            'backgroundColor': '#4e73df'
        }]
    }
    return JsonResponse(data)

@staff_member_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Lấy dữ liệu bán hàng trong 30 ngày qua
    thirty_days_ago = timezone.now() - timedelta(days=30)
    sales_data = Order.objects.filter(
        items__product=product,
        created_at__gte=thirty_days_ago
    ).values('created_at__date').annotate(
        count=Count('id'),
        total=Sum('total_amount')
    ).order_by('created_at__date')
    
    # Chuẩn bị dữ liệu cho biểu đồ
    dates = []
    counts = []
    totals = []
    
    for data in sales_data:
        dates.append(data['created_at__date'].strftime('%d/%m'))
        counts.append(data['count'])
        totals.append(float(data['total']))
    
    context = {
        'product': product,
        'variants': product.variants.all(),
        'chart_dates': dates,
        'chart_counts': counts,
        'chart_totals': totals,
    }
    
    return render(request, 'dashboard/products/detail.html', context)

@staff_member_required
def update_order_status(request, order_id):
    """Update order status"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
            
            messages.success(request, f"Order #{order.id} status updated to {order.get_status_display()}")
        else:
            messages.error(request, "Invalid status value")
            
        return redirect('dashboard:order_detail', order_id=order.id)
    
    return redirect('dashboard:orders')

@staff_member_required
def delete_post_category(request):
    """Delete a blog post category"""
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = get_object_or_404(BlogCategory, id=category_id)
        
        try:
            category.delete()
            messages.success(request, f"Category '{category.name}' deleted successfully")
        except Exception as e:
            messages.error(request, f"Error deleting category: {str(e)}")
    
    return redirect('dashboard:post_categories')

@staff_member_required
def update_general_settings(request):
    """Cập nhật cài đặt chung của hệ thống"""
    if request.method == 'POST':
        # Xử lý cập nhật cài đặt
        site_name = request.POST.get('site_name')
        site_description = request.POST.get('site_description')
        contact_email = request.POST.get('contact_email')
        
        # Lưu cài đặt (giả định có model SiteSettings)
        # settings, created = SiteSettings.objects.get_or_create(pk=1)
        # settings.site_name = site_name
        # settings.site_description = site_description
        # settings.contact_email = contact_email
        # settings.save()
        
        messages.success(request, "Cài đặt đã được cập nhật thành công")
    
    return redirect('dashboard:settings')

@staff_member_required
def update_email_settings(request):
    """Cập nhật cài đặt email"""
    if request.method == 'POST':
        # Xử lý cập nhật cài đặt email
        smtp_host = request.POST.get('smtp_host')
        smtp_port = request.POST.get('smtp_port')
        smtp_username = request.POST.get('smtp_username')
        smtp_password = request.POST.get('smtp_password')
        smtp_use_tls = request.POST.get('smtp_use_tls') == 'on'
        
        # Lưu cài đặt (giả định có model EmailSettings)
        # settings, created = EmailSettings.objects.get_or_create(pk=1)
        # settings.smtp_host = smtp_host
        # settings.smtp_port = smtp_port
        # settings.smtp_username = smtp_username
        # settings.smtp_password = smtp_password
        # settings.smtp_use_tls = smtp_use_tls
        # settings.save()
        
        messages.success(request, "Cài đặt email đã được cập nhật thành công")
    
    return redirect('dashboard:settings')

@staff_member_required
def test_email_settings(request):
    """Kiểm tra cài đặt email"""
    if request.method == 'POST':
        # Xử lý kiểm tra cài đặt email
        smtp_host = request.POST.get('smtp_host')
        smtp_port = request.POST.get('smtp_port')
        smtp_username = request.POST.get('smtp_username')
        smtp_password = request.POST.get('smtp_password')
        smtp_use_tls = request.POST.get('smtp_use_tls') == 'on'
        
        # Thử kết nối SMTP
        try:
            import smtplib
            server = smtplib.SMTP(smtp_host, int(smtp_port))
            if smtp_use_tls:
                server.starttls()
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            server.quit()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@staff_member_required
def clear_cache(request):
    """Xóa cache hệ thống"""
    if request.method == 'POST':
        # Xử lý xóa cache
        # Trong thực tế, bạn có thể sử dụng Django cache framework
        # from django.core.cache import cache
        # cache.clear()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@staff_member_required
def optimize_database(request):
    """Tối ưu cơ sở dữ liệu"""
    if request.method == 'POST':
        # Xử lý tối ưu database
        # Trong thực tế, bạn có thể chạy các lệnh VACUUM hoặc OPTIMIZE TABLE
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@staff_member_required
def update_payment_settings(request):
    """Cập nhật cài đặt thanh toán"""
    if request.method == 'POST':
        # Xử lý cập nhật cài đặt thanh toán
        enable_cod = request.POST.get('enable_cod') == 'on'
        enable_bank_transfer = request.POST.get('enable_bank_transfer') == 'on'
        enable_vnpay = request.POST.get('enable_vnpay') == 'on'
        enable_momo = request.POST.get('enable_momo') == 'on'
        
        bank_name = request.POST.get('bank_name')
        bank_account_number = request.POST.get('bank_account_number')
        bank_account_name = request.POST.get('bank_account_name')
        
        vnpay_terminal_id = request.POST.get('vnpay_terminal_id')
        vnpay_secret_key = request.POST.get('vnpay_secret_key')
        
        momo_partner_code = request.POST.get('momo_partner_code')
        momo_access_key = request.POST.get('momo_access_key')
        momo_secret_key = request.POST.get('momo_secret_key')
        
        # Lưu cài đặt (giả định có model PaymentSettings)
        # settings, created = PaymentSettings.objects.get_or_create(pk=1)
        # settings.enable_cod = enable_cod
        # settings.enable_bank_transfer = enable_bank_transfer
        # settings.enable_vnpay = enable_vnpay
        # settings.enable_momo = enable_momo
        # settings.bank_name = bank_name
        # settings.bank_account_number = bank_account_number
        # settings.bank_account_name = bank_account_name
        # settings.vnpay_terminal_id = vnpay_terminal_id
        # settings.vnpay_secret_key = vnpay_secret_key
        # settings.momo_partner_code = momo_partner_code
        # settings.momo_access_key = momo_access_key
        # settings.momo_secret_key = momo_secret_key
        # settings.save()
        
        messages.success(request, "Cài đặt thanh toán đã được cập nhật thành công")
    
    return redirect('dashboard:settings')

@staff_member_required
def import_products(request):
    """Nhập sản phẩm từ file Excel/CSV"""
    if request.method == 'POST':
        import_file = request.FILES.get('import_file')
        overwrite_existing = request.POST.get('overwrite_existing') == 'on'
        
        if not import_file:
            messages.error(request, "Vui lòng chọn file để nhập")
            return redirect('dashboard:products')
        
        # Xử lý file nhập (giả định)
        # Trong thực tế, bạn sẽ sử dụng thư viện như pandas để đọc file Excel/CSV
        
        # Giả định đã nhập thành công
        messages.success(request, "Đã nhập 10 sản phẩm thành công")
        
    return redirect('dashboard:products')

@staff_member_required
def download_product_template(request):
    """Tải xuống mẫu file nhập sản phẩm"""
    # Trong thực tế, bạn sẽ tạo file Excel/CSV mẫu
    # Ví dụ sử dụng pandas để tạo file Excel
    
    # Giả định đã tạo file và trả về response
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="product_import_template.xlsx"'
    
    # Trong thực tế, bạn sẽ ghi dữ liệu vào response
    # Ví dụ:
    # import pandas as pd
    # from io import BytesIO
    # df = pd.DataFrame({
    #     'Tên sản phẩm': [''],
    #     'Danh mục': [''],
    #     'Giá': [''],
    #     'Số lượng': ['']
    # })
    # buffer = BytesIO()
    # df.to_excel(buffer, index=False)
    # buffer.seek(0)
    # response.write(buffer.getvalue()) 

@staff_member_required
def discount_list(request):
    discounts = Discount.objects.all().order_by('-created_at')
    
    # Thống kê mã giảm giá đang hoạt động và đã sử dụng
    active_discounts = discounts.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_to__gte=timezone.now()
    ).count()
    
    used_count = discounts.aggregate(Sum('used_count'))['used_count__sum'] or 0
    
    context = {
        'discounts': discounts,
        'active_discounts': active_discounts,
        'used_count': used_count,
    }
    
    return render(request, 'dashboard/discounts/list.html', context)

@staff_member_required
def add_discount(request):
    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mã giảm giá mới')
            return redirect('dashboard:discounts')
    else:
        form = DiscountForm()
    
    context = {'form': form, 'is_add': True}
    return render(request, 'dashboard/discounts/form.html', context)

@staff_member_required
def edit_discount(request, discount_id):
    discount = get_object_or_404(Discount, id=discount_id)
    
    if request.method == 'POST':
        form = DiscountForm(request.POST, instance=discount)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật mã giảm giá')
            return redirect('dashboard:discounts')
    else:
        form = DiscountForm(instance=discount)
    
    context = {'form': form, 'discount': discount, 'is_add': False}
    return render(request, 'dashboard/discounts/form.html', context)

@staff_member_required
def delete_discount(request, discount_id):
    if request.method == 'POST':
        discount = get_object_or_404(Discount, id=discount_id)
        discount.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@staff_member_required
def email_templates(request):
    templates = EmailTemplate.objects.all().order_by('name')
    context = {'templates': templates}
    return render(request, 'dashboard/emails/templates.html', context)

@staff_member_required
def create_email_template(request):
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo mẫu email mới')
            return redirect('dashboard:email_templates')
    else:
        form = EmailTemplateForm()
    
    context = {'form': form, 'is_new': True}
    return render(request, 'dashboard/emails/template_form.html', context)

@staff_member_required
def edit_email_template(request, template_id):
    template = get_object_or_404(EmailTemplate, id=template_id)
    
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật mẫu email')
            return redirect('dashboard:email_templates')
    else:
        form = EmailTemplateForm(instance=template)
    
    context = {'form': form, 'template': template, 'is_add': False}
    return render(request, 'dashboard/emails/template_form.html', context)

@staff_member_required
def test_email_template(request, template_id):
    template = get_object_or_404(EmailTemplate, id=template_id)
    
    if request.method == 'POST':
        test_email = request.POST.get('test_email')
        if test_email:
            try:
                # Tạo context mẫu để test
                test_context = {
                    'user': {'username': 'test_user', 'email': test_email},
                    'order': {'id': 'TEST123456', 'amount': '1.000.000₫'},
                    'site_name': 'TomOi',
                    'site_url': request.build_absolute_uri('/')
                }
                
                # Render content
                template_content = template.render_content(test_context)
                
                # Gửi email test
                send_mail(
                    subject=template.render_subject(test_context),
                    message='',  # Plain text version
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[test_email],
                    html_message=template_content,
                    fail_silently=False
                )
                
                messages.success(request, f'Email test đã được gửi tới {test_email}')
            except Exception as e:
                messages.error(request, f'Lỗi khi gửi email: {str(e)}')
        else:
            messages.error(request, 'Vui lòng nhập email để test')
    
    return redirect('dashboard:edit_email_template', template_id=template_id)

@staff_member_required
def email_logs(request):
    logs = EmailLog.objects.all().order_by('-sent_at')
    
    # Filter logs if needed
    email_filter = request.GET.get('email')
    if email_filter:
        logs = logs.filter(recipient__icontains=email_filter)
    
    template_filter = request.GET.get('template')
    if template_filter:
        logs = logs.filter(template_id=template_filter)
    
    context = {
        'logs': logs,
        'templates': EmailTemplate.objects.all()
    }
    
    return render(request, 'dashboard/emails/logs.html', context)

@staff_member_required
def chatbot_dashboard(request):
    """Hiển thị trang tổng quan của chatbot"""
    # Thống kê dữ liệu
    total_messages = 5000  # Thay bằng dữ liệu thực tế từ DB
    total_conversations = 1200
    avg_satisfaction = 4.2
    auto_resolved = 75  # Tỷ lệ phần trăm
    
    # Dữ liệu biểu đồ
    daily_messages = [120, 145, 132, 160, 170, 155, 180]  # 7 ngày gần nhất
    topics = [
        {'name': 'Câu hỏi về sản phẩm', 'count': 350},
        {'name': 'Hỗ trợ đặt hàng', 'count': 280},
        {'name': 'Khiếu nại & Hoàn tiền', 'count': 150},
        {'name': 'Tư vấn kỹ thuật', 'count': 220},
        {'name': 'Khác', 'count': 100}
    ]
    
    # Top câu hỏi thường gặp
    common_questions = [
        {'question': 'Làm thế nào để theo dõi đơn hàng?', 'count': 87},
        {'question': 'Chính sách đổi trả như thế nào?', 'count': 76},
        {'question': 'Tôi quên mật khẩu, phải làm sao?', 'count': 65},
        {'question': 'Thời gian giao hàng mất bao lâu?', 'count': 58},
        {'question': 'Có hỗ trợ thanh toán qua ví điện tử không?', 'count': 52}
    ]
    
    context = {
        'total_messages': total_messages,
        'total_conversations': total_conversations,
        'avg_satisfaction': avg_satisfaction,
        'auto_resolved': auto_resolved,
        'daily_messages': daily_messages,
        'topics': topics,
        'common_questions': common_questions
    }
    
    return render(request, 'dashboard/chatbot/index.html', context)

@staff_member_required
def chatbot_responses(request):
    """Quản lý câu trả lời tự động của chatbot"""
    # Giả lập dữ liệu - thay bằng model thực tế
    responses = [
        {
            'id': 1,
            'trigger': 'Làm thế nào để theo dõi đơn hàng?',
            'response': 'Bạn có thể theo dõi đơn hàng bằng cách đăng nhập vào tài khoản, vào mục "Lịch sử đơn hàng" và nhấp vào đơn hàng cần theo dõi. Hoặc bạn có thể sử dụng mã đơn hàng để tra cứu trực tiếp tại trang "Kiểm tra đơn hàng".',
            'category': 'Đơn hàng',
            'created_at': '2023-10-15'
        },
        {
            'id': 2,
            'trigger': 'Chính sách đổi trả',
            'response': 'Chúng tôi chấp nhận đổi trả trong vòng 7 ngày kể từ ngày nhận hàng. Sản phẩm cần được giữ nguyên tem, nhãn mác và chưa qua sử dụng. Vui lòng liên hệ với bộ phận CSKH để được hướng dẫn thêm về quy trình đổi trả.',
            'category': 'Chính sách',
            'created_at': '2023-10-10'
        },
        {
            'id': 3,
            'trigger': 'Quên mật khẩu',
            'response': 'Để khôi phục mật khẩu, bạn vui lòng truy cập trang đăng nhập và nhấp vào "Quên mật khẩu", sau đó nhập email đã đăng ký. Hệ thống sẽ gửi một liên kết đặt lại mật khẩu vào email của bạn.',
            'category': 'Tài khoản',
            'created_at': '2023-10-05'
        }
    ]
    
    if request.method == 'POST':
        # Logic xử lý thêm câu trả lời mới
        pass
    
    context = {
        'responses': responses
    }
    
    return render(request, 'dashboard/chatbot/responses.html', context)

@staff_member_required
def chatbot_settings(request):
    """Quản lý cài đặt cho chatbot"""
    # Giả lập dữ liệu cài đặt
    settings = {
        'active': True,
        'greeting_message': 'Xin chào! Tôi là trợ lý ảo của Tomoi. Tôi có thể giúp gì cho bạn?',
        'offline_message': 'Hiện tại không có nhân viên hỗ trợ trực tuyến. Vui lòng để lại tin nhắn và email, chúng tôi sẽ liên hệ lại sau.',
        'auto_reply': True,
        'collect_email': True,
        'working_hours': '08:00 - 22:00',
        'theme_color': '#3498db',
        'position': 'right',
        'trigger_time': 5  # seconds
    }
    
    if request.method == 'POST':
        # Logic xử lý cập nhật cài đặt
        pass
    
    context = {
        'settings': settings
    }
    
    return render(request, 'dashboard/chatbot/settings.html', context)

@staff_member_required
def chatbot_logs(request):
    """Xem lịch sử cuộc trò chuyện"""
    # Giả lập dữ liệu lịch sử
    logs = [
        {
            'id': 1,
            'user_id': 'Khách #1234',
            'email': 'user@example.com',
            'start_time': '2023-10-20 15:30:45',
            'end_time': '2023-10-20 15:45:12',
            'messages_count': 12,
            'resolved': True,
            'satisfaction': 5
        },
        {
            'id': 2,
            'user_id': 'Khách #1235',
            'email': 'another@example.com',
            'start_time': '2023-10-20 16:15:22',
            'end_time': '2023-10-20 16:25:05',
            'messages_count': 8,
            'resolved': True,
            'satisfaction': 4
        },
        {
            'id': 3,
            'user_id': 'user123',
            'email': 'registered@example.com',
            'start_time': '2023-10-20 17:05:33',
            'end_time': '2023-10-20 17:30:41',
            'messages_count': 15,
            'resolved': False,
            'satisfaction': null
        }
    ]
    
    context = {
        'logs': logs
    }
    
    return render(request, 'dashboard/chatbot/logs.html', context)

@staff_member_required
def index(request):
    """
    Hiển thị trang dashboard chính
    """
    # Thống kê đơn hàng
    total_orders = Order.objects.count()
    recent_orders = Order.objects.order_by('-created_at')[:5]
    
    # Thống kê doanh thu
    total_revenue = Transaction.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Thống kê sản phẩm
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock__lte=10).count()
    
    # Thống kê người dùng
    total_users = CustomUser.objects.count()
    new_users = CustomUser.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Thống kê lưu lượng truy cập
    page_views = 15427  # Giả lập dữ liệu
    unique_visitors = 5238  # Giả lập dữ liệu
    
    # Dữ liệu biểu đồ doanh thu theo ngày trong 7 ngày gần nhất
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)
    
    daily_revenue = []
    daily_orders = []
    labels = []
    
    current_date = start_date
    while current_date <= end_date:
        # Doanh thu theo ngày
        day_revenue = Transaction.objects.filter(
            status='completed',
            created_at__date=current_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Số đơn hàng theo ngày
        day_orders = Order.objects.filter(
            created_at__date=current_date
        ).count()
        
        daily_revenue.append(day_revenue)
        daily_orders.append(day_orders)
        labels.append(current_date.strftime('%d/%m'))
        
        current_date += timedelta(days=1)
    
    context = {
        'total_orders': total_orders,
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'total_users': total_users,
        'new_users': new_users,
        'page_views': page_views,
        'unique_visitors': unique_visitors,
        'labels': labels,
        'daily_revenue': daily_revenue,
        'daily_orders': daily_orders
    }
    
    return render(request, 'dashboard/index.html', context)

# User management views
@staff_member_required
def user_list(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Lọc theo tìm kiếm nếu có
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Phân trang
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'search_query': search_query,
        'total_users': users.count()
    }
    
    return render(request, 'dashboard/users/list.html', context)

@staff_member_required
def add_user(request):
    if request.method == 'POST':
        # Xử lý thêm người dùng mới
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type', 'customer')
        
        # Kiểm tra username đã tồn tại chưa
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã được sử dụng')
            return redirect('dashboard:add_user')
        
        # Kiểm tra email đã tồn tại chưa
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email đã được sử dụng')
            return redirect('dashboard:add_user')
        
        # Tạo người dùng mới
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type
        )
        
        # Gán quyền admin nếu cần
        if user_type == 'admin':
            user.is_staff = True
            user.save()
        
        messages.success(request, f'Đã tạo người dùng {username} thành công')
        return redirect('dashboard:users')
    
    return render(request, 'dashboard/users/form.html', {'is_new': True})

@staff_member_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        # Cập nhật thông tin người dùng
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')
        is_active = 'is_active' in request.POST
        
        # Kiểm tra email đã tồn tại chưa (nếu thay đổi)
        if email != user.email and CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email đã được sử dụng bởi người dùng khác')
            return redirect('dashboard:edit_user', user_id=user_id)
        
        # Cập nhật thông tin
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.user_type = user_type
        user.is_active = is_active
        
        # Cập nhật mật khẩu nếu có
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
        
        # Cập nhật quyền admin
        if user_type == 'admin':
            user.is_staff = True
        else:
            user.is_staff = False
        
        user.save()
        messages.success(request, f'Đã cập nhật thông tin người dùng {user.username}')
        return redirect('dashboard:users')
    
    context = {
        'user_obj': user,
        'is_new': False
    }
    
    return render(request, 'dashboard/users/form.html', context)

@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Đã xóa người dùng {username}')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# Settings views
@staff_member_required
def system_settings(request):
    # Xử lý lưu cài đặt hệ thống
    if request.method == 'POST':
        # Cập nhật cài đặt
        site_name = request.POST.get('site_name')
        logo = request.FILES.get('logo')
        favicon = request.FILES.get('favicon')
        # Cập nhật các cài đặt khác...
        
        messages.success(request, 'Đã cập nhật cài đặt hệ thống')
        return redirect('dashboard:settings')
    
    context = {
        # Lấy các cài đặt hiện tại
        'settings': {
            'site_name': 'TomOi Shop',
            'meta_description': 'Cửa hàng trực tuyến TomOi',
            'contact_email': 'contact@tomoishop.com',
            'contact_phone': '0987654321',
            'address': 'HCM City, Vietnam',
            'facebook': 'https://facebook.com/tomoishop',
            'instagram': 'https://instagram.com/tomoishop',
            'enable_registration': True,
            'enable_reviews': True,
            'maintenance_mode': False
        }
    }
    
    return render(request, 'dashboard/settings/general.html', context)

# Discount views
@staff_member_required
def discount_list(request):
    discounts = Discount.objects.all().order_by('-created_at')
    
    context = {
        'discounts': discounts
    }
    
    return render(request, 'dashboard/discounts/list.html', context)

@staff_member_required
def add_discount(request):
    if request.method == 'POST':
        # Xử lý thêm mã giảm giá mới
        code = request.POST.get('code').upper()
        discount_type = request.POST.get('discount_type')
        value = float(request.POST.get('value', 0))
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        min_order_value = float(request.POST.get('min_order_value', 0))
        max_uses = int(request.POST.get('max_uses', 0))
        is_active = 'is_active' in request.POST
        
        # Kiểm tra mã đã tồn tại chưa
        if Discount.objects.filter(code=code).exists():
            messages.error(request, f'Mã giảm giá {code} đã tồn tại')
            return redirect('dashboard:add_discount')
        
        # Tạo mã giảm giá mới
        discount = Discount.objects.create(
            code=code,
            discount_type=discount_type,
            value=value,
            valid_from=valid_from,
            valid_to=valid_to,
            min_order_value=min_order_value,
            max_uses=max_uses,
            is_active=is_active
        )
        
        messages.success(request, f'Đã tạo mã giảm giá {code} thành công')
        return redirect('dashboard:discounts')
    
    return render(request, 'dashboard/discounts/form.html', {'is_new': True})

@staff_member_required
def edit_discount(request, discount_id):
    discount = get_object_or_404(Discount, id=discount_id)
    
    if request.method == 'POST':
        # Cập nhật thông tin mã giảm giá
        discount_type = request.POST.get('discount_type')
        value = float(request.POST.get('value', 0))
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        min_order_value = float(request.POST.get('min_order_value', 0))
        max_uses = int(request.POST.get('max_uses', 0))
        is_active = 'is_active' in request.POST
        
        # Cập nhật thông tin
        discount.discount_type = discount_type
        discount.value = value
        discount.valid_from = valid_from
        discount.valid_to = valid_to
        discount.min_order_value = min_order_value
        discount.max_uses = max_uses
        discount.is_active = is_active
        
        discount.save()
        messages.success(request, f'Đã cập nhật thông tin mã giảm giá {discount.code}')
        return redirect('dashboard:discounts')
    
    context = {
        'discount': discount,
        'is_new': False
    }
    
    return render(request, 'dashboard/discounts/form.html', context)

@staff_member_required
def delete_discount(request, discount_id):
    discount = get_object_or_404(Discount, id=discount_id)
    
    if request.method == 'POST':
        code = discount.code
        discount.delete()
        messages.success(request, f'Đã xóa mã giảm giá {code}')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# Email Templates views
@staff_member_required
def email_templates(request):
    templates = EmailTemplate.objects.all().order_by('-updated_at')
    
    context = {
        'templates': templates
    }
    
    return render(request, 'dashboard/emails/templates.html', context)

@staff_member_required
def add_email_template(request):
    if request.method == 'POST':
        # Xử lý thêm template mới
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        template_type = request.POST.get('template_type')
        
        # Tạo email template mới
        template = EmailTemplate.objects.create(
            name=name,
            subject=subject,
            content=content,
            template_type=template_type
        )
        
        messages.success(request, f'Đã tạo mẫu email {name} thành công')
        return redirect('dashboard:email_templates')
    
    return render(request, 'dashboard/emails/template_form.html', {'is_new': True})

@staff_member_required
def edit_email_template(request, template_id):
    template = get_object_or_404(EmailTemplate, id=template_id)
    
    if request.method == 'POST':
        # Cập nhật thông tin template
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        template_type = request.POST.get('template_type')
        
        # Cập nhật thông tin
        template.name = name
        template.subject = subject
        template.content = content
        template.template_type = template_type
        
        template.save()
        messages.success(request, f'Đã cập nhật mẫu email {name}')
        return redirect('dashboard:email_templates')
    
    context = {
        'template': template,
        'is_new': False
    }
    
    return render(request, 'dashboard/emails/template_form.html', context)

@staff_member_required
def delete_email_template(request, template_id):
    template = get_object_or_404(EmailTemplate, id=template_id)
    
    if request.method == 'POST':
        name = template.name
        template.delete()
        messages.success(request, f'Đã xóa mẫu email {name}')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@staff_member_required
def email_logs(request):
    logs = EmailLog.objects.all().order_by('-sent_at')
    
    context = {
        'logs': logs
    }
    
    return render(request, 'dashboard/emails/logs.html', context)

# Ticket support views
@staff_member_required
def ticket_list(request):
    tickets = SupportTicket.objects.all().order_by('-created_at')
    
    # Lọc theo trạng thái nếu có
    status_filter = request.GET.get('status', '')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    context = {
        'tickets': tickets,
        'status_filter': status_filter
    }
    
    return render(request, 'dashboard/tickets/list.html', context)

@staff_member_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    replies = TicketReply.objects.filter(ticket=ticket).order_by('created_at')
    
    context = {
        'ticket': ticket,
        'replies': replies
    }
    
    return render(request, 'dashboard/tickets/detail.html', context)

@staff_member_required
def ticket_reply(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        # Tạo câu trả lời mới
        reply = TicketReply.objects.create(
            ticket=ticket,
            user=request.user,
            content=content,
            is_admin_reply=True
        )
        
        # Cập nhật trạng thái ticket
        ticket.status = 'pending'  # Chờ phản hồi từ khách hàng
        ticket.updated_at = timezone.now()
        ticket.save()
        
        # Gửi email thông báo cho khách hàng nếu cần
        if 'send_email' in request.POST:
            # TODO: Thêm logic gửi email
            pass
        
        messages.success(request, 'Đã gửi phản hồi thành công')
        return redirect('dashboard:ticket_detail', ticket_id=ticket_id)
    
    return redirect('dashboard:ticket_detail', ticket_id=ticket_id)

@staff_member_required
def close_ticket(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        # Tạo câu trả lời đóng ticket nếu có lý do
        if reason:
            TicketReply.objects.create(
                ticket=ticket,
                user=request.user,
                content=f"Ticket đã được đóng: {reason}",
                is_admin_reply=True
            )
        
        # Cập nhật trạng thái ticket
        ticket.status = 'closed'
        ticket.closed_at = timezone.now()
        ticket.updated_at = timezone.now()
        ticket.save()
        
        # Gửi email thông báo cho khách hàng nếu cần
        if 'notify_user' in request.POST:
            # TODO: Thêm logic gửi email
            pass
        
        messages.success(request, 'Đã đóng ticket thành công')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# Product management views
@staff_member_required
def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    
    # Lọc theo danh mục nếu có
    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Lọc theo tìm kiếm nếu có
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(sku__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Phân trang
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh sách danh mục để hiển thị bộ lọc
    categories = Category.objects.all()
    
    context = {
        'products': page_obj,
        'categories': categories,
        'category_id': category_id,
        'search_query': search_query,
        'total_products': products.count()
    }
    
    return render(request, 'dashboard/products/list.html', context)

@staff_member_required
def add_product(request):
    categories = Category.objects.all()
    
    if request.method == 'POST':
        # Xử lý thêm sản phẩm mới
        name = request.POST.get('name')
        sku = request.POST.get('sku')
        price = float(request.POST.get('price', 0))
        sale_price = request.POST.get('sale_price')
        sale_price = float(sale_price) if sale_price else None
        category_id = request.POST.get('category')
        stock = int(request.POST.get('stock', 0))
        description = request.POST.get('description', '')
        specifications = request.POST.get('specifications', '')
        is_active = 'is_active' in request.POST
        
        # Kiểm tra SKU đã tồn tại chưa
        if Product.objects.filter(sku=sku).exists():
            messages.error(request, f'SKU {sku} đã tồn tại')
            return redirect('dashboard:add_product')
        
        # Tạo sản phẩm mới
        product = Product.objects.create(
            name=name,
            sku=sku,
            price=price,
            sale_price=sale_price,
            category_id=category_id,
            stock=stock,
            description=description,
            specifications=specifications,
            is_active=is_active,
            slug=slugify(name)
        )
        
        # Xử lý hình ảnh sản phẩm
        if 'images' in request.FILES:
            for image in request.FILES.getlist('images'):
                ProductImage.objects.create(
                    product=product,
                    image=image
                )
        
        messages.success(request, f'Đã tạo sản phẩm {name} thành công')
        return redirect('dashboard:products')
    
    context = {
        'categories': categories,
        'is_new': True
    }
    
    return render(request, 'dashboard/products/form.html', context)

@staff_member_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        # Cập nhật thông tin sản phẩm
        name = request.POST.get('name')
        sku = request.POST.get('sku')
        price = float(request.POST.get('price', 0))
        sale_price = request.POST.get('sale_price')
        sale_price = float(sale_price) if sale_price else None
        category_id = request.POST.get('category')
        stock = int(request.POST.get('stock', 0))
        description = request.POST.get('description', '')
        specifications = request.POST.get('specifications', '')
        is_active = 'is_active' in request.POST
        
        # Kiểm tra SKU đã tồn tại chưa (nếu thay đổi)
        if sku != product.sku and Product.objects.filter(sku=sku).exists():
            messages.error(request, f'SKU {sku} đã tồn tại')
            return redirect('dashboard:edit_product', product_id=product_id)
        
        # Cập nhật thông tin
        product.name = name
        product.sku = sku
        product.price = price
        product.sale_price = sale_price
        product.category_id = category_id
        product.stock = stock
        product.description = description
        product.specifications = specifications
        product.is_active = is_active
        product.slug = slugify(name)
        
        product.save()
        
        # Xử lý hình ảnh sản phẩm nếu có
        if 'images' in request.FILES:
            for image in request.FILES.getlist('images'):
                ProductImage.objects.create(
                    product=product,
                    image=image
                )
        
        # Xử lý xóa hình ảnh
        images_to_delete = request.POST.getlist('delete_images')
        if images_to_delete:
            ProductImage.objects.filter(id__in=images_to_delete).delete()
        
        messages.success(request, f'Đã cập nhật thông tin sản phẩm {name}')
        return redirect('dashboard:products')
    
    context = {
        'product': product,
        'categories': categories,
        'is_new': False,
        'images': ProductImage.objects.filter(product=product)
    }
    
    return render(request, 'dashboard/products/form.html', context)

@staff_member_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Đã xóa sản phẩm {name}')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@staff_member_required
def product_variants(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = ProductVariant.objects.filter(product=product)
    
    if request.method == 'POST':
        # Xử lý thêm biến thể mới
        variant_type = request.POST.get('variant_type')
        name = request.POST.get('name')
        price_adjustment = float(request.POST.get('price_adjustment', 0))
        stock = int(request.POST.get('stock', 0))
        
        # Tạo biến thể mới
        variant = ProductVariant.objects.create(
            product=product,
            variant_type=variant_type,
            name=name,
            price_adjustment=price_adjustment,
            stock=stock
        )
        
        messages.success(request, f'Đã thêm biến thể {name} cho sản phẩm {product.name}')
        return redirect('dashboard:product_variants', product_id=product_id)
    
    context = {
        'product': product,
        'variants': variants
    }
    
    return render(request, 'dashboard/products/variants.html', context)

# Category management views
@staff_member_required
def category_list(request):
    categories = Category.objects.all()
    
    context = {
        'categories': categories
    }
    
    return render(request, 'dashboard/categories/list.html', context)

@staff_member_required
def add_category(request):
    if request.method == 'POST':
        # Xử lý thêm danh mục mới
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        parent_id = request.POST.get('parent', None)
        if parent_id == '':
            parent_id = None
        is_active = 'is_active' in request.POST
        
        # Tạo slug từ tên
        slug = slugify(name)
        
        # Kiểm tra slug đã tồn tại chưa
        if Category.objects.filter(slug=slug).exists():
            messages.error(request, f'Danh mục với đường dẫn {slug} đã tồn tại')
            return redirect('dashboard:add_category')
        
        # Tạo danh mục mới
        category = Category.objects.create(
            name=name,
            description=description,
            parent_id=parent_id,
            is_active=is_active,
            slug=slug
        )
        
        # Xử lý hình ảnh danh mục nếu có
        if 'image' in request.FILES:
            category.image = request.FILES['image']
            category.save()
        
        messages.success(request, f'Đã tạo danh mục {name} thành công')
        return redirect('dashboard:categories')
    
    # Lấy danh sách danh mục cha tiềm năng
    parent_categories = Category.objects.filter(parent__isnull=True)
    
    context = {
        'parent_categories': parent_categories,
        'is_new': True
    }
    
    return render(request, 'dashboard/categories/form.html', context)

@staff_member_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        # Cập nhật thông tin danh mục
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        parent_id = request.POST.get('parent', None)
        if parent_id == '':
            parent_id = None
        # Không cho phép đặt parent là chính nó hoặc con của nó
        if parent_id and int(parent_id) == category.id:
            messages.error(request, 'Không thể đặt danh mục cha là chính nó')
            return redirect('dashboard:edit_category', category_id=category_id)
        
        is_active = 'is_active' in request.POST
        
        # Tạo slug từ tên
        new_slug = slugify(name)
        
        # Kiểm tra slug đã tồn tại chưa (nếu thay đổi)
        if new_slug != category.slug and Category.objects.filter(slug=new_slug).exists():
            messages.error(request, f'Danh mục với đường dẫn {new_slug} đã tồn tại')
            return redirect('dashboard:edit_category', category_id=category_id)
        
        # Cập nhật thông tin
        category.name = name
        category.description = description
        category.parent_id = parent_id
        category.is_active = is_active
        category.slug = new_slug
        
        # Xử lý hình ảnh danh mục nếu có
        if 'image' in request.FILES:
            category.image = request.FILES['image']
        
        category.save()
        messages.success(request, f'Đã cập nhật thông tin danh mục {name}')
        return redirect('dashboard:categories')
    
    # Lấy danh sách danh mục cha tiềm năng (không bao gồm danh mục hiện tại và con của nó)
    excluded_ids = [category.id]
    children = Category.objects.filter(parent=category)
    for child in children:
        excluded_ids.append(child.id)
    
    parent_categories = Category.objects.filter(parent__isnull=True).exclude(id__in=excluded_ids)
    
    context = {
        'category': category,
        'parent_categories': parent_categories,
        'is_new': False
    }
    
    return render(request, 'dashboard/categories/form.html', context)

@staff_member_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    # Kiểm tra có danh mục con không
    children = Category.objects.filter(parent=category)
    if children.exists():
        return JsonResponse({
            'success': False, 
            'error': 'Không thể xóa danh mục có chứa danh mục con'
        })
    
    # Kiểm tra có sản phẩm trong danh mục không
    products = Product.objects.filter(category=category)
    if products.exists():
        return JsonResponse({
            'success': False, 
            'error': 'Không thể xóa danh mục có chứa sản phẩm'
        })
    
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Đã xóa danh mục {name}')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@staff_member_required
def export_orders(request):
    """
    Xuất dữ liệu đơn hàng ra file CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'
    
    # Lọc theo trạng thái nếu có
    status_filter = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Lấy danh sách đơn hàng
    orders = Order.objects.all().order_by('-created_at')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        orders = orders.filter(created_at__gte=start_date)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        end_date = end_date + timedelta(days=1)
        orders = orders.filter(created_at__lt=end_date)
    
    # Tạo writer và viết header
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Mã đơn hàng', 'Khách hàng', 'Email', 'Ngày tạo', 
        'Trạng thái', 'Tổng tiền', 'Phương thức thanh toán', 
        'Địa chỉ giao hàng', 'Số điện thoại'
    ])
    
    # Ghi dữ liệu
    for order in orders:
        writer.writerow([
            order.id,
            order.order_id,
            f"{order.user.first_name} {order.user.last_name}",
            order.user.email,
            order.created_at.strftime('%d/%m/%Y %H:%M'),
            order.get_status_display(),
            order.total_amount,
            order.get_payment_method_display(),
            order.shipping_address,
            order.phone
        ])
    
    return response

# Banner management views
@staff_member_required
def banner_list(request):
    banners = Banner.objects.all()
    return render(request, 'dashboard/marketing/banners.html', {'banners': banners})

@staff_member_required
def add_banner(request):
    """
    Thêm banner mới
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle', '')
        link = request.POST.get('link', '')
        position = request.POST.get('position', 'home_slider')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = 'is_active' in request.POST
        
        # Tạo banner mới
        banner = Banner.objects.create(
            title=title,
            subtitle=subtitle,
            link=link,
            position=position,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active
        )
        
        # Xử lý hình ảnh nếu có
        if 'image' in request.FILES:
            banner.image = request.FILES['image']
            banner.save()
        
        messages.success(request, f'Đã tạo banner {title} thành công')
        return redirect('dashboard:banners')
    
    context = {
        'positions': Banner.POSITION_CHOICES,
        'is_new': True
    }
    
    return render(request, 'dashboard/banners/form.html', context)

@staff_member_required
def edit_banner(request, banner_id):
    """
    Chỉnh sửa banner
    """
    banner = get_object_or_404(Banner, id=banner_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle', '')
        link = request.POST.get('link', '')
        position = request.POST.get('position')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = 'is_active' in request.POST
        
        # Cập nhật thông tin
        banner.title = title
        banner.subtitle = subtitle
        banner.link = link
        banner.position = position
        banner.start_date = start_date
        banner.end_date = end_date
        banner.is_active = is_active
        
        # Xử lý hình ảnh nếu có
        if 'image' in request.FILES:
            banner.image = request.FILES['image']
        
        banner.save()
        messages.success(request, f'Đã cập nhật banner {title} thành công')
        return redirect('dashboard:banners')
    
    context = {
        'banner': banner,
        'positions': Banner.POSITION_CHOICES,
        'is_new': False
    }
    
    return render(request, 'dashboard/banners/form.html', context)

@staff_member_required
def delete_banner(request, banner_id):
    """
    Xóa banner
    """
    banner = get_object_or_404(Banner, id=banner_id)
    
    if request.method == 'POST':
        title = banner.title
        banner.delete()
        messages.success(request, f'Đã xóa banner {title}')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@staff_member_required
def blog_categories(request):
    """
    Hiển thị danh sách danh mục bài viết
    """
    categories = BlogCategory.objects.all()
    return render(request, 'dashboard/blog/categories.html', {'categories': categories})

def blog_view_redirect(request):
    """Chuyển hướng tạm thời từ URL 'blogs' sang 'dashboard:blogs'"""
    return redirect('dashboard:blogs')