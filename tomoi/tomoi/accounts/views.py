from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Order, Product, ProductImage, Category, Transaction
# Bỏ PurchasedAccount vì chưa cần thiết cho chức năng settings

@login_required
def settings_view(request):
    context = {
        'current_theme': request.session.get('theme', 'light'),
        'snow_effect': request.session.get('snow_effect', False),
        'pet_effect': request.session.get('pet_effect', False),
        'font_size': request.session.get('font_size', 'medium'),
    }
    return render(request, 'accounts/settings.html', context) 