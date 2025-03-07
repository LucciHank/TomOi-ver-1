from django.shortcuts import render

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

# Thêm các view khác... 