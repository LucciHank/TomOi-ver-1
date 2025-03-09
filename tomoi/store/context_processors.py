from django.utils.timezone import now
from .models import Banner, Category, Wishlist
from django.utils import timezone
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
            config = ChatbotConfig.objects.filter(active=True).first()
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