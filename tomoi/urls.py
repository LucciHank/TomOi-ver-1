from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import (
    home, about, contact, login_view, register, logout_view, 
    profile, activate, password_reset_request, 
    password_reset_confirm, account_update,
    public_chatbot_config, public_chatbot_process  # đảm bảo có các view này
)

from store.views import (
    product_list, product_detail, add_to_cart, cart, update_cart, 
    checkout, search_products, category_products,
    api_search_products, api_category_products,
    log_chat_message, rate_chat_message, send_chat_feedback  # thêm các view cho chatbot
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Dashboard
    path('dashboard/', include('dashboard.urls')),
    
    # Main site routes
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    
    # Authentication
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile, name='profile'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('password-reset/', password_reset_request, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('account/update/', account_update, name='account_update'),
    
    # Store
    path('products/', include('store.urls')),
    
    # Cart & Checkout
    path('cart/', cart, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/update/', update_cart, name='update_cart'),
    path('checkout/', checkout, name='checkout'),
    
    # API
    path('api/products/search/', api_search_products, name='api_search_products'),
    path('api/products/category/<slug:category_slug>/', api_category_products, name='api_category_products'),
    path('api/log-chat/', log_chat_message, name='log_chat_message'),  # API endpoint để lưu lịch sử chat
    path('api/rate-chat/', rate_chat_message, name='rate_chat_message'),  # API endpoint để đánh giá chatbot
    path('api/feedback-chat/', send_chat_feedback, name='send_chat_feedback'),  # API endpoint để gửi góp ý
    
    # Chatbot API endpoints
    path('accounts/api/public/chatbot-config/', public_chatbot_config, name='public_chatbot_config'),
    path('accounts/api/public/chatbot-process/', public_chatbot_process, name='public_chatbot_process'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 