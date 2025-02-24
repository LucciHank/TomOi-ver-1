from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'store'
urlpatterns = [
    path('', views.home, name='home'),  # Trang chủ
    path('list/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
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
    path('api/get-price/', views.get_variant_price, name='get_variant_price'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
    path('toggle-wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('pay-with-balance/', views.pay_with_balance, name='pay_with_balance'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),


    # path('payment/paypal/', views.paypal_payment, name='paypal_payment'),
    # path('payment/execute/', views.payment_execute, name='payment_execute'),
] 
