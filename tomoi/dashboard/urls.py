from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
#from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from . import views
from .auth_views import dashboard_logout
from .views import user_management
from .views import dashboard, messaging, user_list, user_detail, user_edit, user_permissions
from .views import user_activity_log, user_login_history, terminate_session, terminate_all_sessions
from .views import toggle_user_status, user_add, user_delete, import_users, user_report, user_stats
from .views import order_management, order_detail, update_order_status, export_orders, cancel_order, refund_order, order_list, order_history, customer_orders
# Warranty functions are imported from views/__init__.py
from .views import subscription_management, subscription_plans
from .views import source_dashboard, source_list, source_add, source_edit, source_delete, source_log_list, source_analytics
from .views import share_report, source_chart_data, add_source_redirect
from .views import chat_messages, chat_sessions
from .views import email_logs, email_templates, email_editor, email_save_template
from .views import discount_list, discount_add, discount_edit, discount_delete, toggle_discount, discount_report
from .views.product import update_product_status, manage_product_images, delete_product_image, set_primary_image
from .views.product import product_detail, product_history
from .views.banner import upload_banner_image, banner_list, banner_add, banner_edit, banner_delete, toggle_banner
from .views import api_settings, save_api_config, test_api
from .views import chatbot_api_settings, chatbot_save_api, chatbot_test_api
from .views import settings as app_settings, logs, responses
from .views.user import user_dashboard
from .views.chatbot import dashboard as chatbot_dashboard  # Import chatbot_dashboard view
from .views.marketing import marketing, dashboard as marketing_dashboard, delete_campaign, marketing_analytics  # Import marketing, dashboard và delete_campaign từ marketing.py
from .views.compare import compare_sources  # Import compare_sources từ module compare chứ không phải source
from .views.product_source import add_source_product  # Import add_source_product từ module product_source
from .views.settings import settings_view, update_general_settings, update_payment_settings  # Import settings view
from .views.blog import delete_post_category  # Import delete_post_category từ module blog
from .views.email import create_email_template, edit_email_template  # Import create_email_template và edit_email_template từ module email

# Product functions - imported directly from views/__init__.py
from .views import (
    product_list,
    add_product,
    edit_product,
    delete_product,
    category_list,
    add_category,
    edit_category,
    import_products
)

# Import warranty functions from views
from .views import (
    warranty_management, warranty_detail, warranty_report, send_new_account,
    create_warranty, update_warranty_status, assign_warranty, add_warranty_note, delete_warranty
)

from .views import subscription_management, subscription_plans
from .views.subscription import check_expired_subscriptions_ajax
from .views import source_dashboard, source_list, source_add, source_edit, source_delete, source_log_list, source_analytics

app_name = 'dashboard'

urlpatterns = [
    # Dashboard home
    path('', views.dashboard, name='index'),  # Dashboard chính, sử dụng tên là 'index'
    
    # User Management
    path('users/', user_list, name='user_list'),
    path('users/dashboard/', user_dashboard, name='user_dashboard'),
    path('users/management/', user_management, name='user_management'),
    path('users/add/', user_add, name='add_user'),
    path('users/add/', user_add, name='user_add'),  # Alias for add_user
    path('users/<int:user_id>/', user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', user_edit, name='edit_user'),
    path('users/<int:user_id>/edit/', user_edit, name='user_edit'),  # Alias for user_edit
    path('users/<int:user_id>/permissions/', user_permissions, name='user_permissions'),
    path('users/<int:user_id>/activity/', user_activity_log, name='user_activity'),
    path('users/<int:user_id>/login-history/', user_login_history, name='user_login_history'),
    path('users/<int:user_id>/terminate-session/<str:session_key>/', terminate_session, name='terminate_session'),
    path('users/<int:user_id>/terminate-all-sessions/', terminate_all_sessions, name='terminate_all_sessions'),
    path('users/<int:user_id>/toggle-status/', toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/delete/', user_delete, name='delete_user'),
    path('users/import/', import_users, name='import_users'),
    path('users/export/', views.user.export_users, name='export_users'),
    path('users/report/', user_report, name='user_report'),
    path('users/stats/', user_stats, name='user_stats'),
    path('users/<int:user_id>/adjust-balance/', views.user_views.adjust_balance, name='adjust_balance'),
    path('users/<int:user_id>/adjust-tcoin/', views.user_views.adjust_tcoin, name='adjust_tcoin'),
    path('users/<int:user_id>/reset-password/', views.user_views.user_reset_password, name='user_reset_password'),
    path('users/<int:user_id>/notes/', views.user_views.user_notes, name='user_notes'),
    path('users/<int:user_id>/notes/add/', views.user_views.user_add_note, name='user_add_note'),
    path('users/<int:user_id>/notes/<int:note_id>/edit/', views.user_views.user_edit_note, name='user_edit_note'),
    path('users/<int:user_id>/notes/<int:note_id>/delete/', views.user_views.user_delete_note, name='user_delete_note'),
    path('users/groups/', views.user_views.user_groups, name='user_groups'),
    path('users/groups/add/', views.user_views.add_group, name='add_group'),
    path('users/groups/<int:group_id>/edit/', views.user_views.edit_group, name='edit_group'),
    path('users/groups/<int:group_id>/delete/', views.user_views.delete_group, name='delete_group'),
    
    # Messaging
    path('messaging/', messaging, name='messaging'),
    
    # Warranty Management
    path('warranty/', warranty_management, name='warranty'),
    path('warranty/<int:warranty_id>/', warranty_detail, name='warranty_detail'),
    path('warranty/report/', warranty_report, name='warranty_report'),
    path('warranty/send-new-account/<int:user_id>/', send_new_account, name='send_new_account'),
    path('warranty/create/', create_warranty, name='create_warranty'),
    path('warranty/<int:warranty_id>/update-status/', update_warranty_status, name='update_warranty_status'),
    path('warranty/<int:warranty_id>/assign/', assign_warranty, name='assign_warranty'),
    path('warranty/<int:warranty_id>/add-note/', add_warranty_note, name='add_warranty_note'),
    path('warranty/<int:warranty_id>/delete/', delete_warranty, name='delete_warranty'),
    
    # Subscription Management
    path('subscription/', subscription_management, name='subscription_list'),
    path('subscription/plans/', subscription_plans, name='subscription_plans'),
    path('subscription/check-expired/', check_expired_subscriptions_ajax, name='check_expired_subscriptions'),
    path('subscription/create/', views.subscription.create_subscription, name='create_subscription'),
    path('subscription/<int:subscription_id>/', views.subscription.subscription_detail, name='subscription_detail'),
    path('subscription/<int:subscription_id>/renew/', views.subscription.renew_subscription, name='renew_subscription'),
    path('subscription/<int:subscription_id>/cancel/', views.subscription.cancel_subscription, name='cancel_subscription'),
    path('subscription/plans/delete/<int:plan_id>/', views.subscription.delete_subscription_plan, name='delete_subscription_plan'),
    path('subscription/extend-all/', views.subscription.extend_all_subscriptions, name='extend_all_subscriptions'),
    path('subscription/export/', views.subscription.export_subscriptions, name='export_subscriptions'),
    
    # Source Management
    path('source/', source_dashboard, name='source_dashboard'),
    path('source/list/', source_list, name='source_list'),
    path('source/add/', source_add, name='source_add'),
    path('source/edit/<int:pk>/', source_edit, name='source_edit'),
    path('source/delete/<int:pk>/', source_delete, name='source_delete'),
    path('source/logs/', source_log_list, name='source_logs'),
    path('source/analytics/', source_analytics, name='source_analytics'),
    path('source/compare/', compare_sources, name='compare_sources'),
    path('source/share-report/', share_report, name='share_report'),
    path('source/chart-data/', source_chart_data, name='source_chart_data'),
    path('source/log/add/', views.source.add_source_log, name='add_source_log'),
    path('source/log/detail/', views.source.api_source_log_detail, name='api_source_log_detail'),
    path('source/detail/<int:pk>/', views.source.source_detail, name='source_detail'),
    path('source/products/<int:product_id>/', views.source.api_product_sources, name='api_product_sources'),
    path('source/search-products/', views.source.api_search_products, name='api_search_products'),
    path('add-source/', add_source_redirect, name='add_source_redirect'),
    path('source/add-product/', add_source_product, name='add_source_product'),
    
    # Product Management
    path('products/', product_list, name='products'),
    path('products/add/', add_product, name='add_product'),
    path('products/<int:product_id>/edit/', edit_product, name='edit_product'),
    path('products/<int:product_id>/delete/', delete_product, name='delete_product'),
    path('products/<int:product_id>/', product_detail, name='product_detail'),
    path('products/<int:product_id>/update-status/', update_product_status, name='update_product_status'),
    path('products/<int:product_id>/images/', manage_product_images, name='manage_product_images'),
    path('products/images/<int:image_id>/delete/', delete_product_image, name='delete_product_image'),
    path('products/images/<int:image_id>/set-primary/', set_primary_image, name='set_primary_image'),
    path('products/<int:product_id>/history/', product_history, name='product_history'),
    path('products/check-sku/', product_detail, name='check_sku'),  # Tạm thời dùng product_detail
    path('products/upload-image/', upload_banner_image, name='upload_editor_image'),  # Tạm thời dùng upload_banner_image
    
    # Categories
    path('products/categories/', category_list, name='categories'),
    path('products/categories/add/', add_category, name='add_category'),
    path('products/categories/<int:category_id>/edit/', edit_category, name='edit_category'),
    
    # Import Products
    path('products/import/', import_products, name='import_products'),
    
    # Order Management
    path('orders/', order_management, name='order_management'),
    path('orders/', order_management, name='orders'),  # Alias for order_management
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', update_order_status, name='update_order_status'),
    path('orders/export/', export_orders, name='export_orders'),
    path('orders/<int:order_id>/print/', order_detail, name='print_order'),  # Tạm sử dụng order_detail
    path('orders/<int:order_id>/send-email/', order_detail, name='send_order_email'),  # Tạm sử dụng order_detail
    path('orders/update-status/', update_order_status, name='update_order_status'),  # Đã sửa để nhận order_id từ POST
    path('orders/cancel/', cancel_order, name='cancel_order'),
    path('orders/refund/', refund_order, name='refund_order'),
    path('orders/list/', order_list, name='order_list'),
    path('orders/history/', order_history, name='order_history'),
    path('users/<int:user_id>/orders/', customer_orders, name='customer_orders'),
    
    # Discount Management
    path('discounts/', discount_list, name='discounts'),
    path('discounts/add/', discount_add, name='add_discount'),
    path('discounts/<int:discount_id>/edit/', discount_edit, name='edit_discount'),
    path('discounts/<int:discount_id>/delete/', discount_delete, name='delete_discount'),
    path('discounts/<int:discount_id>/toggle/', toggle_discount, name='toggle_discount'),
    path('discounts/report/', discount_report, name='discount_report'),
    
    # Banner Management
    path('banners/', banner_list, name='banners'),
    path('banners/add/', banner_add, name='add_banner'),
    path('banners/<int:banner_id>/edit/', banner_edit, name='edit_banner'),
    path('banners/<int:banner_id>/delete/', banner_delete, name='delete_banner'),
    path('banners/<int:banner_id>/toggle/', toggle_banner, name='toggle_banner'),
    path('banners/upload-image/', upload_banner_image, name='upload_banner_image'),
    
    # Chat
    path('chat/messages/', chat_messages, name='chat_messages'),
    path('chat/sessions/', chat_sessions, name='chat_sessions'),
    path('chat/history/', chat_sessions, name='chat_history'),  # Alias for chat_sessions
    
    # Marketing
    path('marketing/', marketing, name='marketing'),  # URL pattern cho marketing
    path('marketing/dashboard/', marketing_dashboard, name='marketing_dashboard'),  # URL pattern cho marketing dashboard
    path('marketing/delete-campaign/', delete_campaign, name='delete_campaign'),  # URL pattern cho xóa chiến dịch
    path('marketing/analytics/', marketing_analytics, name='marketing_analytics'),  # URL pattern cho phân tích tiếp thị
    
    # Email
    path('email/logs/', email_logs, name='email_logs'),
    path('email/templates/', email_templates, name='email_templates'),
    path('email/templates/editor/', email_editor, name='email_editor'),
    path('email/templates/save/', email_save_template, name='email_save_template'),
    
    # API Settings
    path('api/settings/', api_settings, name='api_settings'),
    path('api/settings/save/', save_api_config, name='save_api_config'),
    path('api/settings/test/', test_api, name='test_api'),
    
    # Chatbot Settings
    path('chatbot/dashboard/', chatbot_dashboard, name='chatbot_dashboard'),
    path('chatbot/settings/', chatbot_api_settings, name='chatbot_settings'),
    path('chatbot/api/', chatbot_api_settings, name='chatbot_api'),  # Alias for chatbot_settings
    path('chatbot/settings/save/', chatbot_save_api, name='chatbot_save_api'),
    path('chatbot/settings/test/', chatbot_test_api, name='chatbot_test_api'),
    path('chatbot/config/', app_settings, name='chatbot_config'),
    path('chatbot/logs/', logs, name='chatbot_logs'),
    path('chatbot/responses/', responses, name='chatbot_responses'),
    
    # System Settings
    path('settings/', settings_view, name='settings'),
    path('settings/update-general/', update_general_settings, name='update_general_settings'),
    path('settings/update-payment/', update_payment_settings, name='update_payment_settings'),
    path('settings/update-email/', update_general_settings, name='email_settings_update'),  # Tạm dùng update_general_settings
    
    # Authentication
    path('logout/', dashboard_logout, name='logout'),
    
    # Blog Management
    path('posts/categories/delete/', delete_post_category, name='delete_post_category'),
    path('blogs/', marketing, name='blogs'),  # Tạm thời trỏ đến trang marketing
    
    # Content Management
    path('content/', marketing, name='content'),  # Tạm thời trỏ đến trang marketing
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),  # Tạm thời trỏ đến hàm analytics trong views/__init__.py
    path('analytics/chart-data/', views.analytics, name='chart_data'),  # Tạm thời trỏ đến hàm analytics
    
    # Calendar API endpoints
    path('api/events/', views.api.get_events, name='api_events'),
    path('api/events/create/', views.api.create_event, name='api_create_event'),
    path('api/events/<int:event_id>/update/', views.api.update_event, name='api_update_event'),
    path('api/events/<int:event_id>/delete/', views.api.delete_event, name='api_delete_event'),
    path('api/calendar/google-status/', views.calendar.calendar_events, name='api_calendar_google_status'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 