from django.urls import path
# Xóa import không hợp lệ
# from .views import index, dashboard_login, dashboard_logout
from . import views  # Import module views
from . import chatbot_views
from . import main_views  # Đảm bảo import này
from .auth_views import dashboard_login, dashboard_logout  # Import các hàm xác thực
from .order_views import order_management, order_detail, update_order_status, export_orders
from .views import (
    analytics, 
    reports, 
    performance,
    user_views,
    user,
    marketing,
    source,
    discount,
    banner,
    subscription
)
from .views.api_settings import api_settings, save_api_config, test_api
from .views.settings import settings_view, save_chatbot_settings, test_gemini_api

# Import các view mới
from .views.messaging import messaging_view
from .views.complaints import complaints_list
from .views.warranty import warranty_list
from .views.calendar import calendar_events, premium_subscriptions, send_reminder, add_calendar_event, cancel_subscription

# Import module mới cho Google Calendar
from . import calendar_views

from .temp_test_import import test_func
print("Import test_func OK:", test_func())

from . import views_temp

# Import views mới
from .views.premium_reminder import send_reminder, cancel_subscription
from .views import api
from .views.chat_history import chat_history, conversation_detail, chatbot_log_api
from .views.subscription import subscription_list, subscription_detail, renew_subscription, cancel_subscription

# Import trực tiếp hàm compare_sources từ views.py
from .views.compare import compare_sources
from .views.product_source import add_source_product

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard views
    path('', main_views.index, name='index'),  # Đảm bảo view này tồn tại
    
    # User Management URLs
    path('users/', user.user_list, name='user_list'),
    path('users/dashboard/', user.user_dashboard, name='user_dashboard'),
    path('users/<int:user_id>/', user.user_detail, name='user_detail'),
    path('users/add/', user_views.user_add, name='user_add'),
    path('users/<int:user_id>/edit/', user_views.user_edit, name='user_edit'),
    path('users/<int:user_id>/permissions/', user_views.user_permissions, name='user_permissions'),
    path('users/<int:user_id>/activity/', user_views.user_activity, name='user_activity'),
    path('users/<int:user_id>/transactions/', user_views.user_transactions, name='user_transactions'),
    path('users/<int:user_id>/notes/', user_views.user_notes, name='user_notes'),
    path('users/export/', views.export_users, name='export_users'),
    path('users/analytics/', user_views.user_analytics, name='user_analytics'),
    path('users/<int:user_id>/adjust-balance/', user.adjust_balance, name='adjust_balance'),
    path('users/<int:user_id>/adjust-tcoin/', user.adjust_tcoin, name='adjust_tcoin'),
    path('users/import/', user_views.import_users, name='import_users'),
    path('users/<int:user_id>/reset-password/', user_views.user_reset_password, name='user_reset_password'),
    path('users/activity/<int:activity_id>/rollback/', user.rollback_activity, name='rollback_activity'),
    path('users/check-username/', user.check_username, name='check_username'),
    path('users/<int:user_id>/delete/', user.user_delete, name='user_delete'),

    # Marketing URLs
    path('marketing/', marketing.dashboard, name='marketing'),
    path('marketing/campaigns/', marketing.campaign_list, name='campaign_list'),
    path('marketing/campaigns/add/', marketing.campaign_add, name='campaign_add'),
    path('marketing/campaigns/<int:campaign_id>/', marketing.campaign_detail, name='campaign_detail'),
    path('marketing/campaigns/<int:campaign_id>/edit/', marketing.campaign_edit, name='campaign_edit'),
    
    # Banner URLs
    path('banners/', banner.banner_list, name='banners'),
    path('banners/add/', banner.banner_add, name='banner_add'),
    path('banners/<int:banner_id>/edit/', banner.banner_edit, name='banner_edit'),
    path('banners/<int:banner_id>/delete/', banner.banner_delete, name='banner_delete'),
    
    # Discount URLs
    path('discounts/', discount.discount_list, name='discounts'),
    path('discounts/add/', discount.discount_add, name='discount_add'),
    path('discounts/<int:discount_id>/edit/', discount.discount_edit, name='discount_edit'),
    path('discounts/<int:discount_id>/delete/', discount.discount_delete, name='discount_delete'),

    # Source Management URLs
    path('sources/', source.source_list, name='source_list'),
    path('sources/dashboard/', source.source_dashboard, name='source_dashboard'),
    path('sources/add/', source.source_add, name='source_add'),
    path('sources/logs/', source.source_log_list, name='source_log_list'),
    path('sources/compare/', compare_sources, name='compare_sources'),
    path('sources/logs/add/', source.add_source_log, name='add_source_log'),
    path('sources/products/add/', add_source_product, name='add_source_product'),
    path('sources/analytics/', source.source_dashboard, name='source_analytics'),
    path('sources/<int:source_id>/edit/', source.source_add, name='source_edit'),
    path('sources/<int:source_id>/delete/', source.source_add, name='source_delete'),
    path('sources/<int:source_id>/', source.source_detail, name='source_detail'),

    # Core URLs
    path('login/', dashboard_login, name='login'),
    path('logout/', dashboard_logout, name='logout'),
    
    # Order Management URLs
    path('orders/', order_management, name='orders'),
    path('orders/management/', order_management, name='order_management'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', update_order_status, name='update_order_status'),
    path('orders/export/', export_orders, name='export_orders'),
    
    # Analytics URLs
    path('analytics/', analytics, name='analytics'),
    path('analytics/sales/', views.sales_report, name='sales_report'),
    path('analytics/users/', views.user_analytics, name='user_analytics'),
    path('analytics/marketing/', views.marketing_analytics, name='marketing_analytics'),
    path('analytics/custom/', views.custom_report, name='custom_report'),
    
    # Products URLs
    path('products/', views.product_list, name='products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('products/categories/', views.category_list, name='categories'),
    path('products/categories/add/', views.add_category, name='add_category'),
    path('products/categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('products/import/', views.import_products, name='import_products'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/get/<int:product_id>/', views.get_product, name='get_product'),
    path('products/list/', views.product_list, name='product_list'),

    # Settings URLs
    path('settings/', settings_view, name='settings'),
    path('settings/save-chatbot/', save_chatbot_settings, name='save_chatbot_settings'),
    path('settings/test-gemini-api/', test_gemini_api, name='test_gemini_api'),
    
    # Tab phụ Dashboard
    path('reports/', reports, name='reports'),
    path('performance/', performance, name='performance'),
    
    # User group management
    path('user-groups/', user_views.user_groups, name='user_groups'),
    path('user-groups/add/', user_views.add_group, name='add_group'),
    path('user-groups/<int:group_id>/edit/', user_views.edit_group, name='edit_group'),
    path('user-groups/<int:group_id>/delete/', user_views.delete_group, name='delete_group'),
    path('users/<int:user_id>/delete/', user_views.delete_user, name='delete_user'),
    path('users/<int:user_id>/notes/add/', user_views.user_add_note, name='user_add_note'),
    path('users/<int:user_id>/notes/<int:note_id>/edit/', user_views.user_edit_note, name='user_edit_note'),
    path('users/<int:user_id>/notes/<int:note_id>/delete/', user_views.user_delete_note, name='user_delete_note'),
    path('users/notes/<int:note_id>/update/', user_views.user_edit_note, name='update_user_note'),
    path('users/notes/<int:note_id>/delete/', user_views.user_delete_note, name='delete_user_note'),
    
    # Các chức năng mới
    path('messaging/', messaging_view, name='messaging'),
    path('complaints/', complaints_list, name='complaints'),
    path('warranty/', warranty_list, name='warranty'),
    path('warranty/<int:request_id>/', views.warranty.warranty_detail, name='warranty_detail'),
    path('warranty/<int:request_id>/process/', views.warranty.process_warranty, name='process_warranty'),

    # API URLs
    path('api/calendar/events/', calendar_events, name='calendar_events'),
    path('api/premium-subscriptions/', premium_subscriptions, name='premium_subscriptions'),
    path('api/premium-subscriptions/<int:subscription_id>/send-reminder/', send_reminder, name='send_reminder'),
    path('api/premium-subscriptions/<int:subscription_id>/cancel/', cancel_subscription, name='cancel_subscription'),
    path('api/calendar/add-event/', add_calendar_event, name='add_calendar_event'),

    # New URLs
    path('settings/test-email/', settings_view, name='test_email_settings'),
    path('settings/clear-cache/', settings_view, name='clear_cache'),
    path('settings/optimize-database/', settings_view, name='optimize_database'),
    path('settings/clear-logs/', settings_view, name='clear_logs'),

    # Thêm URL cho xác thực và đồng bộ Google Calendar - sử dụng module mới
    path('google-auth/', views_temp.google_calendar_auth_temp, name='google_calendar_auth'),
    path('google-callback/', views_temp.google_calendar_callback_temp, name='google_callback'),
    path('google-status/', views_temp.google_calendar_status_temp, name='google_status'),

    # Thêm các URLs mới
    path('api/calendar/google-auth/', views_temp.google_calendar_auth_temp, name='google_auth'),
    path('api/calendar/google-callback/', views_temp.google_calendar_callback_temp, name='google_callback'),
    path('api/calendar/google-status/', views_temp.google_calendar_status_temp, name='google_status'),
    path('api/calendar/sync-events/', views_temp.google_calendar_sync_events_temp, name='sync_events'),

    path('api/events/', api.get_events, name='get_events'),
    path('api/events/create/', api.create_event, name='create_event'),
    path('api/events/<int:event_id>/update/', api.update_event, name='update_event'),
    path('api/events/<int:event_id>/delete/', api.delete_event, name='delete_event'),

    # Thêm các URL patterns này
    path('settings/api/', api_settings, name='api_settings'),
    path('settings/api/save/', save_api_config, name='save_api_config'),
    path('settings/api/test/', test_api, name='test_api'),

    # Thêm các URL cho Chatbot - sửa lại cho đúng với tên hàm trong chatbot.py
    path('chatbot/', views.chatbot.dashboard, name='chatbot_dashboard'),
    path('chatbot/settings/', views.chatbot.settings, name='chatbot_settings'),
    path('chatbot/api/', api_settings, name='chatbot_api'),
    path('chatbot/logs/', views.chatbot.logs, name='chatbot_logs'),
    path('chatbot/chat-logs/', views.chatbot.chat_logs, name='chat_logs'),
    path('chatbot/responses/', views.chatbot.responses, name='chatbot_responses'),

    # API endpoints cho Chatbot
    path('chatbot/api/save/', save_api_config, name='chatbot_save_api'),
    path('chatbot/api/test/', test_api, name='chatbot_test_api'),

    # Thêm URL pattern cho save_chatbot_settings
    path('chatbot/settings/save/', views.chatbot.save_chatbot_settings, name='chatbot_settings_save'),

    # Thêm endpoint cho việc lấy cấu hình chatbot từ frontend
    path('api/chatbot-config/', views.chatbot.get_chatbot_config, name='get_chatbot_config'),

    # Chat history
    path('chat-history/', chat_history, name='chat_history'),
    path('chat-history/detail/<int:conversation_id>/', conversation_detail, name='conversation_detail'),
    
    # API endpoints
    path('api/chatbot/log/', chatbot_log_api, name='chatbot_log_api'),

    # Quản lý gia hạn
    path('subscriptions/', subscription_list, name='subscription_list'),
    path('subscriptions/<int:subscription_id>/', subscription_detail, name='subscription_detail'),
    path('subscriptions/<int:subscription_id>/renew/', renew_subscription, name='renew_subscription'),
    path('subscriptions/<int:subscription_id>/cancel/', cancel_subscription, name='cancel_subscription'),
    path('api/check-expired-subscriptions/', subscription.check_expired_subscriptions_ajax, name='check_expired_subscriptions'),

    # Source API endpoints
    path('api/sources/add-log/', source.add_source_log, name='add_source_log'),
    path('api/sources/search-products/', source.api_search_products, name='api_search_products'),
    path('api/sources/product-sources/', source.api_product_sources, name='api_product_sources'),
    path('api/sources/log-detail/', source.api_source_log_detail, name='api_source_log_detail'),
] 