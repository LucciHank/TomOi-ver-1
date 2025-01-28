from django.utils.timezone import now
from .models import Banner

def banners(request):
    banners = Banner.objects.filter(is_active=True)
    return {
        'main_banners': banners.filter(location='main'),
        'side1_banners': banners.filter(location='side1'),
        'side2_banners': banners.filter(location='side2'),
        'left_banners': banners.filter(location='left'),
        'right_banners': banners.filter(location='right'),
    } 