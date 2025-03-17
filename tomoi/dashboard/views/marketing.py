from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator

from dashboard.utils import is_admin

def marketing(request):
    """Trang tổng quan cho marketing"""
    return render(request, 'dashboard/marketing/marketing.html')

def marketing_dashboard(request):
    """Dashboard cho marketing với các tab khác nhau"""
    tab = request.GET.get('tab', 'overview')
    action = request.GET.get('action', None)
    
    # Xử lý các tab khác nhau
    if tab == 'social':
        return social_marketing(request)
    elif tab == 'sms_push':
        return sms_push(request)
    elif tab == 'affiliate':
        return affiliate(request)
    elif tab == 'remarketing':
        return remarketing(request)
    elif tab == 'automation':
        return automation(request)
    
    # Xử lý các action
    if action == 'new_campaign':
        return campaign_add(request)
    elif action == 'campaigns':
        return campaign_list(request)
    
    # Mặc định hiển thị tổng quan
    context = {
        'tab': tab,
        # Thêm dữ liệu thống kê tổng quan
        'email_stats': {
            'total_sent': 1200,
            'open_rate': 25.5,
            'click_rate': 12.8
        },
        'social_stats': {
            'facebook_engagement': 450,
            'tiktok_views': 2800,
            'threads_interactions': 320,
            'telegram_members': 180
        },
        'website_stats': {
            'total_visits': 5600,
            'conversion_rate': 3.2,
            'ad_cost': 450,
            'roi': 2.5
        }
    }
    return render(request, 'dashboard/marketing/dashboard.html', context)

def campaign_list(request):
    # Thêm lọc theo loại chiến dịch nếu có
    campaign_type = request.GET.get('type', None)
    
    # Dữ liệu mẫu để hiển thị
    campaigns = [
        {
            'id': 1,
            'name': 'Khuyến mãi mùa hè',
            'type': 'email',
            'status': 'active',
            'start_date': timezone.now(),
            'end_date': timezone.now() + timezone.timedelta(days=30),
            'metrics': {'sent': 500, 'opened': 250, 'clicked': 120}
        },
        {
            'id': 2,
            'name': 'Giảm giá cuối tuần',
            'type': 'sms',
            'status': 'scheduled',
            'start_date': timezone.now() + timezone.timedelta(days=2),
            'end_date': timezone.now() + timezone.timedelta(days=4),
            'metrics': {'sent': 0, 'opened': 0, 'clicked': 0}
        }
    ]
    
    context = {
        'campaigns': campaigns,
        'campaign_type': campaign_type
    }
    return render(request, 'dashboard/marketing/campaign_list.html', context)

def campaign_add(request):
    if request.method == 'POST':
        # Xử lý thêm chiến dịch
        messages.success(request, 'Chiến dịch đã được tạo thành công')
        return redirect('dashboard:campaign_list')
    
    # Hiển thị form tạo chiến dịch
    context = {
        'campaign_types': [
            {'id': 'email', 'name': 'Email Marketing'},
            {'id': 'social', 'name': 'Social Media'},
            {'id': 'sms', 'name': 'SMS/Push Notification'},
            {'id': 'affiliate', 'name': 'Affiliate Marketing'},
            {'id': 'remarketing', 'name': 'Remarketing'},
        ]
    }
    return render(request, 'dashboard/marketing/campaign_add.html', context)

def campaign_detail(request, campaign_id):
    # Lấy thông tin chiến dịch theo ID
    campaign = {
        'id': campaign_id,
        'name': 'Chiến dịch mẫu',
        'type': 'email',
        'status': 'active',
        'metrics': {'sent': 500, 'opened': 250, 'clicked': 120}
    }
    
    context = {
        'campaign': campaign
    }
    return render(request, 'dashboard/marketing/campaign_detail.html', context)

def campaign_edit(request, campaign_id):
    if request.method == 'POST':
        # Xử lý cập nhật chiến dịch
        messages.success(request, 'Chiến dịch đã được cập nhật thành công')
        return redirect('dashboard:campaign_detail', campaign_id=campaign_id)
    
    # Lấy thông tin chiến dịch theo ID
    campaign = {
        'id': campaign_id,
        'name': 'Chiến dịch mẫu',
        'type': 'email',
        'status': 'active',
        'content': 'Nội dung chiến dịch...'
    }
    
    context = {
        'campaign': campaign,
        'is_edit': True,
        'campaign_types': [
            {'id': 'email', 'name': 'Email Marketing'},
            {'id': 'social', 'name': 'Social Media'},
            {'id': 'sms', 'name': 'SMS/Push Notification'},
            {'id': 'affiliate', 'name': 'Affiliate Marketing'},
            {'id': 'remarketing', 'name': 'Remarketing'},
        ]
    }
    return render(request, 'dashboard/marketing/campaign_add.html', context)

def delete_campaign(request):
    """Xóa chiến dịch marketing"""
    if request.method == 'POST':
        campaign_id = request.POST.get('campaign_id')
        # Thực hiện xóa chiến dịch
        # Campaign.objects.filter(id=campaign_id).delete()
        messages.success(request, 'Chiến dịch đã được xóa thành công')
        
    return redirect('dashboard:campaign_list')

def marketing_analytics(request):
    """Phân tích tiếp thị"""
    # Lấy khoảng thời gian từ request nếu có
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    
    # Dữ liệu mẫu cho phân tích
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'metrics': {
            'total_campaigns': 10,
            'active_campaigns': 5,
            'total_engagement': 1500,
            'conversion_rate': 3.5,
            'roi': 2.8
        }
    }
    return render(request, 'dashboard/marketing/analytics.html', context)

def email_templates(request):
    """Quản lý các mẫu email"""
    context = {
        'templates': [
            {'id': 1, 'name': 'Mẫu thông báo', 'created_at': timezone.now()},
            {'id': 2, 'name': 'Mẫu khuyến mãi', 'created_at': timezone.now()}
        ]
    }
    return render(request, 'dashboard/marketing/email_templates.html', context)

# Các chức năng mới theo yêu cầu

@login_required
@user_passes_test(is_admin)
def social_marketing(request):
    """Quản lý chiến dịch social marketing"""
    context = {
        'social_posts': []  # Sẽ được thay thế bằng dữ liệu thực từ database
    }
    return render(request, 'dashboard/marketing/social_list.html', context)

@login_required
@user_passes_test(is_admin)
def sms_push(request):
    """Quản lý chiến dịch SMS và Push notification"""
    action = request.GET.get('action', 'list')
    
    if action == 'create':
        # Hiển thị form tạo tin nhắn
        return render(request, 'dashboard/marketing/sms_create.html')
    elif action == 'detail':
        message_id = request.GET.get('id')
        # Hiển thị chi tiết tin nhắn
        return render(request, 'dashboard/marketing/sms_detail.html', {'message_id': message_id})
    else:
        # Hiển thị danh sách tin nhắn
        context = {
            'messages': []  # Sẽ được thay thế bằng dữ liệu thực từ database
        }
        return render(request, 'dashboard/marketing/sms_push.html', context)

@login_required
@user_passes_test(is_admin)
def affiliate(request):
    """Quản lý chương trình tiếp thị liên kết"""
    context = {
        'affiliates': []  # Sẽ được thay thế bằng dữ liệu thực từ database
    }
    return render(request, 'dashboard/marketing/affiliate.html', context)

@login_required
@user_passes_test(is_admin)
def remarketing(request):
    """Quản lý chiến dịch remarketing"""
    context = {
        'campaigns': []  # Sẽ được thay thế bằng dữ liệu thực từ database
    }
    return render(request, 'dashboard/marketing/remarketing.html', context)

@login_required
@user_passes_test(is_admin)
def automation(request):
    """Quản lý tự động hóa marketing"""
    context = {
        'workflows': []  # Sẽ được thay thế bằng dữ liệu thực từ database
    }
    return render(request, 'dashboard/marketing/automation.html', context)

@login_required
@user_passes_test(is_admin)
def remarketing_campaign(request, campaign_id):
    """Chi tiết chiến dịch remarketing"""
    # Trong thực tế, bạn sẽ lấy chiến dịch từ database
    context = {
        'campaign': {
            'id': campaign_id,
            'name': 'Chiến dịch #' + str(campaign_id),
        }
    }
    return render(request, 'dashboard/marketing/remarketing_detail.html', context)

# API cho dữ liệu biểu đồ
@login_required
def marketing_chart_data(request):
    """API trả về dữ liệu cho biểu đồ marketing"""
    chart_type = request.GET.get('type', 'email')
    
    if chart_type == 'email':
        data = {
            'labels': ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
            'sent': [120, 150, 180, 130, 200, 90, 70],
            'opened': [80, 95, 110, 85, 130, 60, 45],
            'clicked': [40, 55, 70, 50, 85, 30, 25]
        }
    elif chart_type == 'social':
        data = {
            'labels': ['FB', 'TikTok', 'Threads', 'Telegram', 'Messenger'],
            'engagement': [250, 400, 150, 100, 180]
        }
    elif chart_type == 'conversion':
        data = {
            'labels': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'],
            'rate': [2.5, 3.1, 3.7, 3.2, 4.0, 3.8]
        }
    else:
        data = {}
    
    return JsonResponse(data)

# Thêm các view khác... 