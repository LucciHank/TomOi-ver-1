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
from .views.product import product_detail, product_history, product_attributes, product_reviews, export_products
from .views.banner import upload_banner_image, banner_list, banner_add, banner_edit, banner_delete, toggle_banner
from .views import api_settings, save_api_config, test_api
from .views import chatbot_api_settings, chatbot_save_api, chatbot_test_api
from .views import settings as app_settings, logs, responses
from .views.user import user_dashboard
from .views.chatbot import (dashboard as chatbot_dashboard, 
                           chatbot_test_api, settings as chatbot_settings)
from .views.product_attribute import (attribute_list, add_attribute, edit_attribute, delete_attribute, 
                            attribute_values, add_attribute_value, edit_attribute_value, delete_attribute_value)

# Import các chức năng marketing từ module marketing
from .views.marketing import (
    marketing, marketing_dashboard, delete_campaign, marketing_analytics,
    campaign_list, campaign_add, campaign_detail, campaign_edit,
    email_templates, social_marketing, sms_push,
    affiliate, remarketing, automation, marketing_chart_data,
    remarketing_campaign
)

# Brand management
# Import directly from views.py instead of the views package
from . import views

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
    delete_category,
    import_products
)

# Import warranty functions from views
from .views import (
    warranty_management, warranty_detail, warranty_report, send_new_account,
    create_warranty, update_warranty_status, assign_warranty, add_warranty_note, delete_warranty,
    warranty_dashboard, warranty_by_status, warranty_settings
)

from .views import subscription_management, subscription_plans
from .views.subscription import check_expired_subscriptions_ajax
from .views import source_dashboard, source_list, source_add, source_edit, source_delete, source_log_list, source_analytics

# Supplier URLs
from .views.supplier import supplier_list, supplier_add, supplier_detail, supplier_edit, supplier_delete

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
    path('warranty/dashboard/', warranty_dashboard, name='warranty_dashboard'),
    path('warranty/<int:warranty_id>/', warranty_detail, name='warranty_detail'),
    path('warranty/report/', warranty_report, name='warranty_report'),
    path('warranty/send-new-account/<int:user_id>/', send_new_account, name='send_new_account'),
    path('warranty/create/', create_warranty, name='create_warranty'),
    path('warranty/create/', create_warranty, name='warranty_request_add'),  # Alias for create_warranty
    path('warranty/<int:warranty_id>/update-status/', update_warranty_status, name='update_warranty_status'),
    path('warranty/<int:warranty_id>/assign/', assign_warranty, name='assign_warranty'),
    path('warranty/<int:warranty_id>/add-note/', add_warranty_note, name='add_warranty_note'),
    path('warranty/<int:warranty_id>/delete/', delete_warranty, name='delete_warranty'),
    path('warranty/status/', warranty_by_status, name='warranty_by_status'),  # Thêm URL mới để hiển thị tất cả yêu cầu
    path('warranty/pending/', warranty_by_status, {'status': 'pending'}, name='warranty_pending'),
    path('warranty/processing/', warranty_by_status, {'status': 'in_progress'}, name='warranty_processing'),
    path('warranty/resolved/', warranty_by_status, {'status': 'resolved'}, name='warranty_resolved'),
    path('warranty/closed/', warranty_by_status, {'status': 'closed'}, name='warranty_closed'),
    path('warranty/settings/', warranty_settings, name='warranty_settings'),
    
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
    path('products/', product_list, name='product_list'),  # Alias for products
    path('products/add/', add_product, name='add_product'),
    path('products/<int:product_id>/edit/', edit_product, name='edit_product'),
    path('products/<int:product_id>/delete/', delete_product, name='delete_product'),
    path('products/<int:product_id>/', product_detail, name='product_detail'),
    path('products/<int:product_id>/update-status/', update_product_status, name='update_product_status'),
    path('products/<int:product_id>/images/', manage_product_images, name='manage_product_images'),
    path('products/images/<int:image_id>/delete/', delete_product_image, name='delete_product_image'),
    path('products/images/<int:image_id>/set-primary/', set_primary_image, name='set_primary_image'),
    path('products/<int:product_id>/history/', product_history, name='product_history'),
    path('products/check-sku/', product_detail, name='check_sku'),  # Tạm thởi dùng product_detail
    path('products/upload-image/', upload_banner_image, name='upload_editor_image'),  # Tạm thởi dùng upload_banner_image
    path('products/upload-product-image/', upload_banner_image, name='upload_product_image'),  # Tạo URL cho upload_product_image
    
    # Categories
    path('products/categories/', category_list, name='categories'),
    path('products/categories/add/', add_category, name='add_category'),
    path('products/categories/<int:category_id>/edit/', edit_category, name='edit_category'),
    path('products/categories/<int:category_id>/delete/', views.product.delete_category, name='delete_category'),
    
    # Variants and Options
    path('products/<int:product_id>/variants/', views.product.manage_product_variants, name='manage_product_variants'),
    path('products/<int:product_id>/variants/add/', views.product.add_product_variant, name='add_product_variant'),
    path('products/variants/<int:variant_id>/edit/', views.product.edit_product_variant, name='edit_product_variant'),
    path('products/variants/<int:variant_id>/delete/', views.product.delete_product_variant, name='delete_product_variant'),
    path('products/variants/<int:variant_id>/options/', views.product.manage_variant_options, name='manage_variant_options'),
    path('products/variants/<int:variant_id>/options/add/', views.product.add_variant_option, name='add_variant_option'),
    path('products/options/<int:option_id>/edit/', views.product.edit_variant_option, name='edit_variant_option'),
    path('products/options/<int:option_id>/delete/', views.product.delete_variant_option, name='delete_variant_option'),
    
    # Brands
    path('products/brands/', views.product.brands, name='brand_list'),
    path('products/brands/add/', views.product.add_brand, name='add_brand'),
    path('products/brands/<int:brand_id>/edit/', views.product.edit_brand, name='edit_brand'),
    path('products/brands/<int:brand_id>/delete/', views.product.delete_brand, name='delete_brand'),
    
    # Product Durations
    path('products/durations/', views.product_duration.product_durations, name='product_durations'),
    path('products/durations/add/', views.product_duration.add_product_duration, name='add_product_duration'),
    path('products/durations/<int:duration_id>/edit/', views.product_duration.edit_product_duration, name='edit_product_duration'),
    path('products/durations/<int:duration_id>/delete/', views.product_duration.delete_product_duration, name='delete_product_duration'),
    
    # Attributes (added to fix NoReverseMatch error)
    path('products/attributes/', attribute_list, name='attribute_list'),
    path('products/attributes/add/', add_attribute, name='add_attribute'),
    path('products/attributes/edit/<int:attribute_id>/', edit_attribute, name='edit_attribute'),
    path('products/attributes/delete/<int:attribute_id>/', delete_attribute, name='delete_attribute'),
    path('products/attributes/<int:attribute_id>/values/', attribute_values, name='attribute_values'),
    path('products/attributes/<int:attribute_id>/values/add/', add_attribute_value, name='add_attribute_value'),
    path('products/attributes/values/edit/<int:value_id>/', edit_attribute_value, name='edit_attribute_value'),
    path('products/attributes/values/delete/<int:value_id>/', delete_attribute_value, name='delete_attribute_value'),
    
    # Product Reviews (added to fix NoReverseMatch error)
    path('products/reviews/', product_reviews, name='product_reviews'),
    
    # Import Products
    path('products/import/', import_products, name='import_products'),
    path('products/import/', import_products, name='product_import'),  # Alias for import_products

    # Export Products
    path('products/export/', export_products, name='product_export'),
    
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
    
    # Order status tabs
    path('orders/pending/', order_list, {'status': 'pending'}, name='order_pending'),
    path('orders/processing/', order_list, {'status': 'processing'}, name='order_processing'),
    path('orders/completed/', order_list, {'status': 'completed'}, name='order_completed'),
    path('orders/cancelled/', order_list, {'status': 'cancelled'}, name='order_cancelled'),
    path('orders/shipped/', order_list, {'status': 'shipped'}, name='order_shipped'),
    path('orders/returned/', order_list, {'status': 'returned'}, name='order_returned'),
    path('orders/refunded/', order_list, {'status': 'refunded'}, name='order_refunded'),
    
    # Order reports
    path('orders/reports/', order_list, name='order_reports'),
    
    # Discount Management
    path('discounts/', views.discount.discount_list, name='discounts'),
    path('discounts/add/', views.discount.discount_add, name='add_discount'),
    path('discounts/add/', views.discount.discount_add, name='discount_add'),  # Alias for add_discount
    path('discounts/edit/<int:discount_id>/', views.discount.discount_edit, name='edit_discount'),
    path('discounts/delete/<int:discount_id>/', views.discount.discount_delete, name='delete_discount'),
    path('discounts/dashboard/', views.discount.discount_dashboard, name='discount_dashboard'),
    path('discounts/report/', views.discount.discount_report, name='discount_report'),
    path('discounts/history/', views.discount.discount_history, name='discount_history'),
    path('discounts/import/', views.discount.import_discounts, name='import_discounts'),
    path('discounts/export/', views.discount.export_discounts, name='export_discounts'),
    path('discounts/backup/', views.discount.backup_discounts, name='backup_discounts'),
    path('discounts/restore/', views.discount.restore_discounts, name='restore_discounts'),
    
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
    
    # Thêm URLs mới cho hệ thống chat
    path('chat/', views.chat.admin_chat_dashboard, name='admin_chat'),
    path('chat/send-message/', views.chat.send_message, name='admin_send_message'),
    path('chat/update-read-status/', views.chat.update_read_status, name='update_read_status'),
    path('chat/get-unread-count/', views.chat.get_unread_count, name='get_unread_count'),
    path('chat/history/<int:user_id>/', views.chat.user_chat_history, name='user_chat_history'),
    
    # Marketing
    path('marketing/', marketing, name='marketing'),  # URL pattern cho marketing
    path('marketing/dashboard/', marketing_dashboard, name='marketing_dashboard'),  # URL pattern cho marketing dashboard
    path('marketing/delete-campaign/', delete_campaign, name='delete_campaign'),  # URL pattern cho xóa chiến dịch
    path('marketing/analytics/', marketing_analytics, name='marketing_analytics'),  # URL pattern cho phân tích tiếp thị
    
    # Bổ sung các URL cho các tính năng marketing mới
    path('marketing/campaigns/', campaign_list, name='campaign_list'),  # Danh sách chiến dịch
    path('marketing/campaigns/add/', campaign_add, name='campaign_add'),  # Thêm chiến dịch
    path('marketing/campaigns/<int:campaign_id>/', campaign_detail, name='campaign_detail'),  # Chi tiết chiến dịch
    path('marketing/campaigns/<int:campaign_id>/edit/', campaign_edit, name='campaign_edit'),  # Sửa chiến dịch
    
    # Email marketing
    path('marketing/email-templates/', email_templates, name='email_templates'),  # Các mẫu email
    
    # Social marketing
    path('marketing/social/', social_marketing, name='social_marketing'),
    path('marketing/sms-push/', sms_push, name='sms_push'),
    path('marketing/affiliate/', affiliate, name='affiliate'),
    path('marketing/remarketing/', remarketing, name='remarketing'),
    path('marketing/automation/', automation, name='automation'),
    path('marketing/remarketing/campaign/<int:campaign_id>/', remarketing_campaign, name='remarketing_campaign'),
    
    # API cho dữ liệu biểu đồ
    path('marketing/chart-data/', marketing_chart_data, name='marketing_chart_data'),  # API dữ liệu biểu đồ
    
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
    path('chatbot/settings/', chatbot_settings, name='chatbot_settings'),
    path('chatbot/api/', chatbot_api_settings, name='chatbot_api'),  # Alias for chatbot_settings
    path('chatbot/settings/save/', chatbot_save_api, name='chatbot_save_api'),
    path('chatbot/settings/test/', chatbot_test_api, name='chatbot_test_api'),
    path('chatbot/config/', app_settings, name='chatbot_config'),
    path('chatbot/logs/', logs, name='chatbot_logs'),
    path('chatbot/responses/', responses, name='chatbot_responses'),
    
    # Chat API
    path('api/user-orders/', views.api.get_user_orders, name='get_user_orders'),
    path('api/search-orders/', views.api.search_orders, name='search_orders'),
    
    # System Settings
    path('settings/', settings_view, name='settings'),
    path('settings/update-general/', update_general_settings, name='update_general_settings'),
    path('settings/update-payment/', update_payment_settings, name='update_payment_settings'),
    path('settings/update-email/', update_general_settings, name='email_settings_update'),  # Tạm dùng update_general_settings
    
    # Authentication
    path('logout/', dashboard_logout, name='logout'),
    
    # Blog Management
    path('posts/categories/delete/', delete_post_category, name='delete_post_category'),
    path('blogs/', marketing, name='blogs'),  # Tạm thởi trỏ đến trang marketing
    
    # Content Management
    path('content/', marketing, name='content'),  # Tạm thởi trỏ đến trang marketing
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),  # Tạm thởi trỏ đến hàm analytics trong views/__init__.py
    path('analytics/chart-data/', views.analytics, name='chart_data'),  # Tạm thởi trỏ đến hàm analytics
    
    # Calendar API endpoints
    path('api/events/', views.api.get_events, name='api_events'),
    path('api/events/create/', views.api.create_event, name='api_create_event'),
    path('api/events/<int:event_id>/update/', views.api.update_event, name='api_update_event'),
    path('api/events/<int:event_id>/delete/', views.api.delete_event, name='api_delete_event'),
    path('api/calendar/google-status/', views.calendar.calendar_events, name='api_calendar_google_status'),

    # Thêm endpoint mới cho Chatbot test API
    path('chatbot/settings/test-gemini/', views.api.test_api, name='test_gemini_api'),
    
    # API cho lịch sử trò chuyện
    path('api/chatbot/logs/<str:chat_id>/detail/', views.api.get_chat_detail, name='api_chat_detail'),

    # Supplier URLs
    path('suppliers/', supplier_list, name='supplier_list'),
    path('suppliers/add/', supplier_add, name='supplier_add'),
    path('suppliers/<int:supplier_id>/', supplier_detail, name='supplier_detail'),
    path('suppliers/<int:supplier_id>/edit/', supplier_edit, name='supplier_edit'),
    path('suppliers/<int:supplier_id>/delete/', supplier_delete, name='supplier_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 