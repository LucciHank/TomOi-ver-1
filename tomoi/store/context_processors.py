from django.utils.timezone import now
from .models import Banner, Category, Wishlist, CartItem
from django.utils import timezone
from dashboard.models.conversation import Message
# Thay đổi import để phù hợp với cấu trúc thực tế của app dashboard
# Có thể class ChatbotConfig nằm trong một submodule cụ thể
try:
    # Thử các cách import khác nhau
    try:
        from dashboard.models.chatbot import ChatbotConfig
    except ImportError:
        try:
            from dashboard.models.api import ChatbotConfig
        except ImportError:
            try:
                from dashboard.models.settings import ChatbotConfig
            except ImportError:
                # Fallback - tạo một class giả nếu không tìm thấy
                class ChatbotConfig:
                    def __init__(self):
                        self.chatbot_name = "TomOi Assistant"
                        self.theme_color = "#df2626"
                        self.avatar = None
                        self.system_prompt = "Bạn là trợ lý ảo của TomOi, hỗ trợ khách hàng một cách lịch sự và chuyên nghiệp."
except Exception as e:
    print(f"Lỗi khi import ChatbotConfig: {e}")

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

def chatbot_config(request):
    """
    Thêm cấu hình chatbot vào context
    """
    try:
        # Kiểm tra xem ChatbotConfig có phải là class hay không
        if 'ChatbotConfig' in globals() and isinstance(ChatbotConfig, type):
            config = ChatbotConfig.objects.filter(is_active=True).first()
        else:
            # Nếu không phải class, tạo một đối tượng giả
            config = type('ChatbotConfig', (), {
                'chatbot_name': "TomOi Assistant",
                'theme_color': "#df2626",
                'avatar': None,
                'system_prompt': "Bạn là trợ lý ảo của TomOi, hỗ trợ khách hàng một cách lịch sự và chuyên nghiệp."
            })()
            
        return {
            'config': config,
            'current_time': timezone.now().strftime('%H:%M')
        }
    except Exception as e:
        print(f"Lỗi khi lấy cấu hình chatbot: {e}")
        # Tạo một đối tượng giả để tránh lỗi template
        config = type('ChatbotConfig', (), {
            'chatbot_name': "TomOi Assistant",
            'theme_color': "#df2626",
            'avatar': None
        })()
        return {
            'config': config,
            'current_time': timezone.now().strftime('%H:%M')
        }

def cart_processor(request):
    """Context processor để đếm số sản phẩm trong giỏ hàng"""
    if request.user.is_authenticated:
        # Sử dụng trực tiếp CartItem thay vì thông qua Cart
        cart_count = CartItem.objects.filter(user=request.user).count()
    else:
        # Trường hợp khách chưa đăng nhập, lấy từ session
        cart_count = 0
        session_key = request.session.session_key
        if session_key:
            cart_count = CartItem.objects.filter(session_key=session_key).count()
    
    return {'cart_count': cart_count}

def wishlist_count(request):
    """Context processor để đếm số sản phẩm trong wishlist"""
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    else:
        wishlist_count = 0
    
    return {'wishlist_count': wishlist_count}

def categories_processor(request):
    """Context processor để lấy danh sách các danh mục sản phẩm"""
    categories = Category.objects.all()
    return {'categories': categories}

def unread_messages_count(request):
    """Context processor để đếm số tin nhắn chưa đọc"""
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()
    else:
        unread_count = 0
    
    return {'unread_messages_count': unread_count} 