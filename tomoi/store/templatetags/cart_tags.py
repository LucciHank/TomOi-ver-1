from django import template
from django.db.models import Sum
from store.models import CartItem

register = template.Library()

@register.filter
def cart_count(user_or_request):
    try:
        # Nếu là user đã đăng nhập
        if hasattr(user_or_request, 'is_authenticated') and user_or_request.is_authenticated:
            cart_items = CartItem.objects.filter(user=user_or_request)
        # Nếu là request (user chưa đăng nhập)
        elif hasattr(user_or_request, 'session'):
            session_key = user_or_request.session.session_key
            if not session_key:
                user_or_request.session.create()
                session_key = user_or_request.session.session_key
            cart_items = CartItem.objects.filter(session_key=session_key)
        else:
            return 0

        # Tính tổng số lượng
        total = cart_items.aggregate(total=Sum('quantity'))['total']
        return total if total else 0
    except Exception as e:
        print(f"Error in cart_count: {str(e)}")
        return 0 