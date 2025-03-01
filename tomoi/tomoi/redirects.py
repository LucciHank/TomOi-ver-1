from django.shortcuts import redirect
from django.http import JsonResponse

def blog_redirect(request):
    return redirect('dashboard:blogs')

def banner_redirect(request):
    return redirect('dashboard:banners')

def chart_data_redirect(request):
    # Tạo dữ liệu mẫu
    data = {
        'labels': ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5'],
        'datasets': [{
            'label': 'Doanh thu',
            'data': [5000000, 7000000, 6000000, 8000000, 9500000],
            'backgroundColor': '#4e73df'
        }]
    }
    return JsonResponse(data) 