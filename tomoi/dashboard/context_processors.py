def dashboard_settings(request):
    """
    Thêm cài đặt dashboard vào context
    """
    return {
        'use_new_sidebar': True
    } 