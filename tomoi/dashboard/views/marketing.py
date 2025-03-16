from django.shortcuts import render, redirect

def marketing(request):
    """Trang tổng quan cho marketing"""
    return render(request, 'dashboard/marketing/marketing.html')

def dashboard(request):
    return render(request, 'dashboard/marketing/dashboard.html')

def campaign_list(request):
    return render(request, 'dashboard/marketing/campaign_list.html')

def campaign_add(request):
    return render(request, 'dashboard/marketing/campaign_form.html')

def campaign_detail(request, campaign_id):
    return render(request, 'dashboard/marketing/campaign_detail.html')

def campaign_edit(request, campaign_id):
    return render(request, 'dashboard/marketing/campaign_form.html')

def delete_campaign(request):
    """Xóa chiến dịch marketing"""
    if request.method == 'POST':
        campaign_id = request.POST.get('campaign_id')
        # Thực hiện xóa chiến dịch
        # Campaign.objects.filter(id=campaign_id).delete()
        
    return redirect('dashboard:marketing')

def marketing_analytics(request):
    """Phân tích tiếp thị"""
    return render(request, 'dashboard/marketing/analytics.html')

# Thêm các view khác... 