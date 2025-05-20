from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views  # Import file views.py gốc
from .chatbot_views import chatbot  # Import module chatbot từ thư mục views

app_name = 'store'
urlpatterns = [
    # API endpoints first
    path('api/search-suggestions/trending/', views.trending_suggestions, name='trending_suggestions'),
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),
    
    # Other URLs
    path('', views.home, name='home'),  # Trang chủ
    path('list/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/review/<int:product_id>/', views.add_review, name='add_review'),
    path('info/', views.user_info, name='user_info'),
    path('orders/', views.order_history, name='order_history'),
    path('recharge/', views.recharge, name='recharge'),
    path('order-history/', views.order_history, name='purchase_history'),
    path("payment-success/", views.payment_success, name="payment_success"),
    path('paypal/webhook/', views.paypal_webhook, name='paypal_webhook'),
    path('add_balance/<int:amount>/', views.add_balance, name='add_balance'),
    path('buy_premium/<str:account_type>/<int:price>/<int:duration_days>/', views.buy_premium_account, name='buy_premium'),
    path('purchased_accounts/', views.purchased_accounts, name='purchased_accounts'),
    # cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/api/', views.cart_api, name='cart_api'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('cart/check-stock/<int:product_id>/', views.check_stock, name='check_stock'),
    path('cart/count/', views.get_cart_count, name='cart_count'),
    path('cart/apply-tcoin/', views.apply_tcoin, name='apply_tcoin'),
    path('cart/apply-voucher/', views.apply_voucher, name='apply_voucher'),
    path('cart/apply-referral/', views.apply_referral, name='apply_referral'),
    path('cart/set-gift-recipient/', views.set_gift_recipient, name='set_gift_recipient'),
    path('cart/set-gift-message/', views.set_gift_message, name='set_gift_message'),
    path('gift-demo/', views.gift_demo, name='gift_demo'),
    path('api/get-price/', views.get_variant_price, name='get_variant_price'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
    path('toggle-wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('pay-with-balance/', views.pay_with_balance, name='pay_with_balance'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('search/', views.search_products, name='search_products'),
    path('wishlist/', views.wishlist, name='wishlist'),
    # path('payment/paypal/', views.paypal_payment, name='paypal_payment'),
    # path('payment/execute/', views.payment_execute, name='payment_execute'),
    
    # Chatbot API endpoints
    path('api/chatbot/', chatbot.chatbot_api, name='chatbot_api'),
    path('api/log-chat/', chatbot.log_chat, name='log_chat'),
    
    # Chat URLs
    path('chat/', include([
        path('', views.user_chat_dashboard, name='user_chat'),
        path('send-message/', views.user_send_message, name='user_send_message'),
        path('update-read-status/', views.update_read_status, name='update_read_status'),
        path('get-unread-count/', views.get_unread_count, name='get_unread_count'),
    ])),
    
    # URLs cho thanh toán ACB
    path('acb-payment/<int:order_id>/', views.acb_qr_payment, name='acb_qr_payment'),
    path('acb-payment-return/<int:order_id>/', views.acb_qr_return, name='acb_qr_return'),
    path('acb-payment-cancel/<int:order_id>/', views.acb_qr_cancel, name='acb_qr_cancel'),
    path('check-acb-payment/<int:transaction_id>/', views.check_acb_payment, name='check_acb_payment'),
    path('bestsellers/', views.bestsellers, name='bestsellers'),
    path('featured-products/', views.featured_products, name='featured_products'),
    path('newest-products/', views.newest_products, name='newest_products'),
    path('promotions/', views.promotions, name='promotions'),
    path('buying-guide/', views.buying_guide, name='buying_guide'),
    path('contact/', views.contact, name='contact'),
    path('news/', views.news, name='news'),
] 
