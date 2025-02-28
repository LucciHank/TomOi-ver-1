from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from .models import *
from store.models import Order, Product
from accounts.models import CustomUser
from django.utils.text import slugify
from blog.models import Post, Category
import os
import re
import time
from werkzeug.utils import secure_filename
from django.contrib.auth.models import Group
import random

@staff_member_required
def dashboard_home(request):
    # Thống kê chung
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    context = {
        # Thống kê đơn hàng
        'total_orders': Order.objects.count(),
        'recent_orders': Order.objects.order_by('-created_at')[:10],
        'monthly_orders': Order.objects.filter(created_at__date__gte=last_30_days).count(),
        
        # Thống kê doanh thu
        'total_revenue': Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0,
        'monthly_revenue': Order.objects.filter(
            created_at__date__gte=last_30_days
        ).aggregate(total=Sum('total_amount'))['total'] or 0,
        
        # Thống kê khách hàng
        'total_customers': CustomUser.objects.count(),
        'new_customers': CustomUser.objects.filter(date_joined__date__gte=last_30_days).count(),
        
        # Thống kê sản phẩm
        'total_products': Product.objects.count(),
        'low_stock_products': Product.objects.filter(stock__lte=10),
        
        # Thống kê ticket hỗ trợ
        'open_tickets': Ticket.objects.filter(status__in=['new', 'processing']).count(),
        'recent_tickets': Ticket.objects.order_by('-created_at')[:5],
        
        # Bỏ qua phần thống kê marketing
        'active_campaigns': 0,
        'campaign_performance': {},
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
    # Lấy dữ liệu cho thống kê tổng quan
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_month = today - timedelta(days=60)
    
    # Lấy chiến dịch và thống kê
    campaigns = MarketingCampaign.objects.all()
    active_campaigns = campaigns.filter(is_active=True, start_date__lte=today)
    
    # Tính tăng trưởng so với tháng trước
    current_month_stats = campaigns.filter(start_date__gte=last_30_days).aggregate(
        impressions=Sum('impressions'),
        clicks=Sum('clicks'),
        conversions=Sum('conversions')
    )
    
    last_month_stats = campaigns.filter(
        start_date__range=[last_month, last_30_days]
    ).aggregate(
        impressions=Sum('impressions'),
        clicks=Sum('clicks'),
        conversions=Sum('conversions')
    )
    
    # Tính phần trăm tăng trưởng
    campaign_growth = calculate_growth(
        active_campaigns.filter(start_date__gte=last_30_days).count(),
        active_campaigns.filter(start_date__range=[last_month, last_30_days]).count()
    )
    
    impression_growth = calculate_growth(
        current_month_stats['impressions'] or 0,
        last_month_stats['impressions'] or 0
    )
    
    click_growth = calculate_growth(
        current_month_stats['clicks'] or 0,
        last_month_stats['clicks'] or 0
    )
    
    conversion_growth = calculate_growth(
        current_month_stats['conversions'] or 0,
        last_month_stats['conversions'] or 0
    )
    
    # Dữ liệu cho biểu đồ
    chart_data = get_campaign_chart_data(last_30_days)
    budget_data = get_budget_distribution(campaigns)
    
    context = {
        'active_campaigns': active_campaigns.count(),
        'campaign_growth': campaign_growth,
        'total_impressions': campaigns.aggregate(Sum('impressions'))['impressions__sum'] or 0,
        'impression_growth': impression_growth,
        'total_clicks': campaigns.aggregate(Sum('clicks'))['clicks__sum'] or 0,
        'click_growth': click_growth,
        'conversion_rate': calculate_conversion_rate(campaigns),
        'conversion_growth': conversion_growth,
        
        'campaigns': campaigns,
        'chart_labels': chart_data['labels'],
        'impression_data': chart_data['impressions'],
        'click_data': chart_data['clicks'],
        'budget_labels': budget_data['labels'],
        'budget_data': budget_data['data'],
    }
    
    return render(request, 'dashboard/marketing/index.html', context)

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
    if request.method == 'POST':
        campaign_id = request.POST.get('campaign_id')
        # Xử lý xóa chiến dịch
        # ...
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

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
    """Dashboard phân tích dữ liệu"""
    # Lấy dữ liệu thống kê
    try:
        # Lấy thời điểm 30 ngày trước
        last_30_days = timezone.now().date() - timedelta(days=30)
        
        # Tạo dữ liệu mẫu nếu không có model DailyAnalytics
        daily_data = {
            'dates': [(last_30_days + timedelta(days=i)).strftime('%d/%m') for i in range(30)],
            'views': [random.randint(50, 200) for _ in range(30)],
            'visitors': [random.randint(20, 100) for _ in range(30)]
        }
        
        # Thống kê tháng hiện tại
        current_month_stats = {
            'views': sum(daily_data['views']),
            'visitors': sum(daily_data['visitors']),
            'sessions': sum(daily_data['visitors']) + random.randint(50, 200),
            'bounce_sessions': random.randint(20, 100),
            'duration': timedelta(minutes=random.randint(2, 10))
        }
        
        # Tính bounce rate từ bounce_sessions và total_sessions
        if current_month_stats['sessions'] and current_month_stats['bounce_sessions']:
            bounce_rate = (current_month_stats['bounce_sessions'] / current_month_stats['sessions']) * 100
        else:
            bounce_rate = 0
        
        # Thêm bounce_rate vào context
        context = {
            'stats': current_month_stats,
            'bounce_rate': bounce_rate,
            'daily_data': daily_data,
            'popular_pages': [
                {'url': '/', 'title': 'Trang chủ', 'total_views': random.randint(500, 1000)},
                {'url': '/products/', 'title': 'Sản phẩm', 'total_views': random.randint(300, 800)},
                {'url': '/blog/', 'title': 'Blog', 'total_views': random.randint(200, 600)},
            ]
        }
    except Exception as e:
        # Xử lý trường hợp không có dữ liệu hoặc lỗi
        context = {
            'stats': {},
            'bounce_rate': 0,
            'error': str(e),
            'daily_data': {
                'dates': [],
                'views': [],
                'visitors': [],
            },
            'popular_pages': [],
        }
    
    return render(request, 'dashboard/analytics/index.html', context)

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
    categories = Category.objects.annotate(post_count=Count('posts'))
    
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
def toggle_featured(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        post.is_featured = not post.is_featured
        post.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

# Quản lý danh mục
@staff_member_required
def post_categories(request):
    categories = Category.objects.annotate(post_count=Count('posts'))
    return render(request, 'dashboard/posts/categories.html', {'categories': categories})

@staff_member_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        icon = request.POST.get('icon')
        is_active = request.POST.get('is_active') == 'on'
        
        Category.objects.create(
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
    category = get_object_or_404(Category, id=category_id)
    
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
    category = get_object_or_404(Category, id=category_id)
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
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@staff_member_required
def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related('category', 'author'), id=post_id)
    
    # Lấy dữ liệu lượt xem trong 30 ngày gần nhất
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    # Tạo danh sách ngày và lượt xem
    dates = []
    views_data = []
    monthly_views = 0
    
    # Giả sử có model PostView để lưu lượt xem theo ngày
    views_by_date = PostView.objects.filter(
        post=post,
        viewed_at__date__gte=last_30_days
    ).values('viewed_at__date').annotate(
        total_views=Count('id')
    ).order_by('viewed_at__date')
    
    # Tạo dict để mapping ngày với lượt xem
    views_dict = {
        item['viewed_at__date']: item['total_views'] 
        for item in views_by_date
    }
    
    # Lặp qua 30 ngày để lấy dữ liệu
    for i in range(30):
        date = today - timedelta(days=29-i)
        dates.append(date.strftime('%d/%m'))
        views = views_dict.get(date, 0)
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
    days = int(request.GET.get('days', 7))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Lấy dữ liệu theo ngày
    daily_stats = DailyAnalytics.objects.filter(
        date__range=[start_date, end_date]
    ).order_by('date')
    
    data = {
        'labels': [stat.date.strftime('%d/%m') for stat in daily_stats],
        'views': [stat.page_views for stat in daily_stats],
        'visitors': [stat.unique_visitors for stat in daily_stats]
    }
    
    return JsonResponse(data)

@staff_member_required
def get_visitor_stats(request):
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    # Thống kê chung
    stats = DailyAnalytics.objects.filter(
        date__range=[last_30_days, today]
    ).aggregate(
        total_views=Sum('page_views'),
        total_visitors=Sum('unique_visitors'),
        total_sessions=Sum('total_sessions'),
        total_bounce=Sum('bounce_sessions'),
        total_duration=Sum('total_duration')
    )
    
    # Tính tỷ lệ
    bounce_rate = (stats['total_bounce'] / stats['total_sessions'] * 100) if stats['total_sessions'] else 0
    avg_duration = (stats['total_duration'] / stats['total_sessions']) if stats['total_sessions'] else timedelta()
    
    data = {
        'total_views': stats['total_views'] or 0,
        'total_visitors': stats['total_visitors'] or 0,
        'bounce_rate': round(bounce_rate, 2),
        'avg_duration': str(avg_duration)
    }
    
    return JsonResponse(data)

@staff_member_required
def get_page_stats(request):
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    # Lấy top trang phổ biến
    popular_pages = PageAnalytics.objects.filter(
        date__range=[last_30_days, today]
    ).values('url', 'title').annotate(
        total_views=Sum('views'),
        total_duration=Sum('total_duration'),
        total_bounces=Sum('bounce_count')
    ).order_by('-total_views')[:10]
    
    data = [{
        'url': page['url'],
        'title': page['title'],
        'views': page['total_views'],
        'avg_time': str(page['total_duration'] / page['total_views']) if page['total_views'] else '0:00',
        'bounce_rate': round((page['total_bounces'] / page['total_views'] * 100), 2) if page['total_views'] else 0
    } for page in popular_pages]
    
    return JsonResponse({'pages': data})

@staff_member_required
def get_referrer_stats(request):
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    # Thống kê theo nguồn truy cập
    stats = ReferrerAnalytics.objects.filter(
        date__range=[last_30_days, today]
    ).values('source').annotate(
        total_visits=Sum('visits'),
        total_new=Sum('new_visitors'),
        total_bounces=Sum('bounce_count')
    ).order_by('-total_visits')
    
    data = [{
        'source': stat['source'],
        'visits': stat['total_visits'],
        'new_visitors': stat['total_new'],
        'bounce_rate': round((stat['total_bounces'] / stat['total_visits'] * 100), 2) if stat['total_visits'] else 0
    } for stat in stats]
    
    return JsonResponse({'sources': data})

@staff_member_required
def get_device_stats(request):
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    # Thống kê theo thiết bị
    stats = VisitorSession.objects.filter(
        start_time__date__range=[last_30_days, today]
    ).values('device_type').annotate(
        total=Count('id')
    ).order_by('-total')
    
    data = {
        'labels': [s['device_type'] for s in stats],
        'data': [s['total'] for s in stats]
    }
    
    return JsonResponse(data)

@staff_member_required
def get_realtime_visitors(request):
    # Lấy số người đang online (active trong 5 phút gần nhất)
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    active_sessions = VisitorSession.objects.filter(
        end_time__gte=five_minutes_ago
    ).count()
    
    data = {
        'active_visitors': active_sessions,
        'timestamp': timezone.now().timestamp()
    }
    
    return JsonResponse(data)

@staff_member_required
def get_realtime_pageviews(request):
    # Lấy lượt xem trang trong 5 phút gần nhất
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    recent_views = PageView.objects.filter(
        viewed_at__gte=five_minutes_ago
    ).values('url').annotate(
        views=Count('id')
    ).order_by('-views')[:10]
    
    data = [{
        'url': view['url'],
        'views': view['views']
    } for view in recent_views]
    
    return JsonResponse({'pageviews': data})

@staff_member_required
def get_realtime_locations(request):
    # Lấy vị trí người dùng đang online
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    locations = VisitorSession.objects.filter(
        end_time__gte=five_minutes_ago
    ).values('ip_address').distinct()
    
    # Ở đây bạn có thể thêm logic để phân giải IP thành location
    
    data = {
        'total_locations': locations.count(),
        'locations': list(locations.values_list('ip_address', flat=True))
    }
    
    return JsonResponse(data)

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
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

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
            category = get_object_or_404(Category, id=category_id)
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
            category = get_object_or_404(Category, id=category_id)
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
    if request.method == 'POST':
        # Xử lý thêm danh mục bài viết
        # ...
        return redirect('dashboard:post_categories')
    return render(request, 'dashboard/posts/categories.html')

@staff_member_required
def edit_post_category(request, category_id):
    if request.method == 'POST':
        # Xử lý chỉnh sửa danh mục bài viết
        # ...
        return redirect('dashboard:post_categories')
    return render(request, 'dashboard/posts/categories.html')

@staff_member_required
def get_post_category(request, category_id):
    # Lấy thông tin danh mục bài viết
    # ...
    return JsonResponse({'success': True, 'category': {}})

@staff_member_required
def clear_logs(request):
    """Xóa logs hệ thống"""
    if request.method == 'POST':
        # Xử lý xóa logs
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

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
def get_stock_data(request):
    """Lấy dữ liệu tồn kho"""
    period = request.GET.get('period', '30')
    
    # Dữ liệu mẫu
    dates = [(timezone.now().date() - timedelta(days=i)).strftime('%d/%m') for i in range(int(period))]
    dates.reverse()
    
    import_data = [0] * len(dates)
    export_data = [0] * len(dates)
    
    return JsonResponse({
        'dates': dates,
        'import_data': import_data,
        'export_data': export_data
    })

@staff_member_required
def order_management(request):
    """Quản lý đơn hàng"""
    orders = Order.objects.all().order_by('-created_at')
    
    context = {
        'orders': orders,
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status='pending').count(),
        'completed_orders': orders.filter(status='completed').count(),
        'cancelled_orders': orders.filter(status='cancelled').count(),
    }
    
    return render(request, 'dashboard/orders/list.html', context)

@staff_member_required
def order_detail(request, order_id):
    """Chi tiết đơn hàng"""
    order = get_object_or_404(Order, id=order_id)
    
    context = {
        'order': order,
        'order_items': order.orderitem_set.all(),
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
    categories = Category.objects.all().order_by('name')
    
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
    categories = Category.objects.all().order_by('name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'dashboard/posts/categories.html', context)

@staff_member_required
def settings_dashboard(request):
    """Cài đặt hệ thống"""
    context = {}
    
    return render(request, 'dashboard/settings/index.html', context)

@staff_member_required
def ticket_detail(request, ticket_id):
    """Chi tiết ticket hỗ trợ"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
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
            content=content
        )
        
        # Cập nhật trạng thái ticket nếu cần
        if ticket.status == 'new':
            ticket.status = 'processing'
            ticket.save()
        
        return redirect('dashboard:ticket_detail', ticket_id=ticket_id)
    
    return render(request, 'dashboard/tickets/detail.html', context) 