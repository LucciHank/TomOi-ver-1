from django.utils.timezone import now
from .models import Banner, Category, Wishlist

def banners(request):
    banners = Banner.objects.filter(is_active=True)
    return {
        'main_banners': banners.filter(location='main'),
        'side1_banners': banners.filter(location='side1'),
        'side2_banners': banners.filter(location='side2'),
        'left_banners': banners.filter(location='left'),
        'right_banners': banners.filter(location='right'),
    }

def categories(request):
    return {
        'categories': Category.objects.all()
    }

def wishlist_status(request):
    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_products = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    
    return {
        'wishlist_products': wishlist_products
    } 