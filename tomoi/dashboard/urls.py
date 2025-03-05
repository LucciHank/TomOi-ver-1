from django.urls import path
# Xóa import không hợp lệ
# from .views import index, dashboard_login, dashboard_logout
from . import views  # Import module views
from . import chatbot_views
from .main_views import index  # Import index từ main_views
from .auth_views import dashboard_login, dashboard_logout  # Import các hàm xác thực
from .order_views import order_management, order_detail, update_order_status, export_orders
from .views import (
    analytics, 
    reports, 
    performance,
    user_views,
    user
)

app_name = 'dashboard'

urlpatterns = [
    # Core URLs
    path('', index, name='home'),  # Sử dụng index từ main_views
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
    
    # Marketing URLs
    path('marketing/', views.marketing_dashboard, name='marketing'),
    path('marketing/campaigns/', views.campaign_list, name='campaigns'),
    path('marketing/campaigns/add/', views.add_campaign, name='add_campaign'),
    path('marketing/banners/', views.banner_list, name='banners'),
    path('marketing/banners/add/', views.add_banner, name='add_banner'),
    path('marketing/banners/<int:banner_id>/edit/', views.edit_banner, name='edit_banner'),
    
    # Settings URLs
    path('settings/', views.settings_dashboard, name='settings'),
    path('settings/general/', views.update_general_settings, name='update_general_settings'),
    path('settings/email/', views.email_settings, name='email_settings'),
    path('settings/email/update/', views.update_email_settings, name='update_email_settings'),
    path('settings/payment/', views.payment_settings, name='payment_settings'),
    path('settings/payment/update/', views.update_payment_settings, name='update_payment_settings'),
    
    # API URLs
    path('api/keys/', views.api_key_list, name='api_keys'),
    path('api/keys/add/', views.add_api_key, name='add_api_key'),
    path('api/keys/<int:key_id>/toggle/', views.toggle_api_key, name='toggle_api_key'),
    path('api/keys/<int:key_id>/delete/', views.delete_api_key, name='delete_api_key'),
    path('api/webhooks/', views.webhook_list, name='webhooks'),
    path('api/webhooks/add/', views.add_webhook, name='add_webhook'),
    path('api/webhooks/<int:webhook_id>/edit/', views.edit_webhook, name='edit_webhook'),
    path('api/webhooks/<int:webhook_id>/delete/', views.delete_webhook, name='delete_webhook'),
    path('api/logs/', views.api_logs, name='api_logs'),
    path('api/logs/<int:log_id>/details/', views.get_log_details, name='log_details'),
    path('api/sources/<int:source_id>/products/', views.api_source_products, name='api_source_products'),
    path('api/sources/<int:source_id>/base-price/', views.get_source_base_price, name='get_source_base_price'),
    
    # Chatbot URLs
    path('chatbot/dashboard/', chatbot_views.chatbot_dashboard, name='chatbot_dashboard'),
    path('chatbot/config/', chatbot_views.chatbot_config, name='chatbot_config'),
    path('chatbot/config/<int:config_id>/', chatbot_views.chatbot_config, name='edit_chatbot_config'),
    path('chatbot/api-integration/', chatbot_views.api_integration, name='api_integration'),
    path('chatbot/api-integration/<int:api_id>/', chatbot_views.api_integration, name='edit_api_integration'),
    path('chatbot/logs/', chatbot_views.chat_logs, name='chatbot_logs'),
    path('api/chat/', chatbot_views.chat_api, name='chat_api'),
    path('api/chat/feedback/', chatbot_views.chat_feedback, name='chat_feedback'),
    
    # User Management URLs
    path('users/', user_views.user_dashboard, name='user_dashboard'),
    path('users/list/', user.user_list, name='user_list'),
    path('users/add/', user_views.user_add, name='user_add'),
    path('users/<int:user_id>/', user_views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', user_views.user_edit, name='user_edit'),
    path('users/<int:user_id>/permissions/', user_views.user_permissions, name='user_permissions'),
    path('users/<int:user_id>/activity/', user_views.user_activity, name='user_activity'),
    path('users/<int:user_id>/transactions/', user_views.user_transactions, name='user_transactions'),
    path('users/<int:user_id>/notes/', user_views.user_notes, name='user_notes'),
    path('users/export/', views.export_users, name='export_users'),
    path('users/analytics/', user_views.user_analytics, name='user_analytics'),
    path('users/<int:user_id>/adjust-balance/', user.adjust_balance, name='adjust_balance'),
    path('users/<int:user_id>/adjust-tcoin/', user_views.adjust_tcoin, name='adjust_tcoin'),
    path('users/import/', user_views.import_users, name='import_users'),
    path('users/<int:user_id>/reset-password/', user_views.user_reset_password, name='user_reset_password'),
    path('users/activity/<int:activity_id>/rollback/', user.rollback_activity, name='rollback_activity'),
    path('users/check-username/', user.check_username, name='check_username'),
    path('users/<int:user_id>/delete/', user.user_delete, name='user_delete'),
    
    # Warranty Management
    path('warranty/', views.warranty_management, name='warranty_management'),
    path('warranty/<int:ticket_id>/', views.warranty_detail, name='warranty_detail'),
    path('warranty/report/', views.warranty_report, name='warranty_report'),
    path('warranty/<int:ticket_id>/send-account/', views.send_new_account, name='send_new_account'),
    path('warranty/create/', views.create_warranty, name='create_warranty'),
    path('warranty/<int:ticket_id>/status/', views.update_warranty_status, name='update_warranty_status'),
    path('warranty/<int:ticket_id>/assign/', views.assign_warranty, name='assign_warranty'),
    path('warranty/<int:ticket_id>/note/', views.add_warranty_note, name='add_warranty_note'),
    path('warranty/<int:ticket_id>/delete/', views.delete_warranty, name='delete_warranty'),
    
    # Subscription Management URLs
    path('subscriptions/', views.subscription_management, name='subscription_management'),
    path('subscriptions/plans/', views.subscription_plans, name='subscription_plans'),
    
    # Source Management URLs
    path('sources/', views.source_dashboard, name='source_dashboard'),
    path('sources/list/', views.source_list, name='source_list'),
    path('sources/add/', views.source_add, name='source_add'),
    path('sources/edit/<int:source_id>/', views.source_edit, name='source_edit'),
    path('sources/delete/<int:source_id>/', views.source_delete, name='source_delete'),
    path('sources/logs/', views.source_log_list, name='source_log_list'),
    path('sources/compare/', views.compare_sources, name='compare_sources'),
    path('sources/products/add/', views.add_source_product, name='add_source_product'),
    path('sources/logs/add/', views.add_source_log, name='add_source_log'),
    path('sources/analytics/', views.source_analytics, name='source_analytics'),
    path('sources/share-report/', views.share_report, name='share_report'),
    path('api/sources/chart-data/', views.source_chart_data, name='source_chart_data'),
    path('sources/add-source/', views.add_source_redirect, name='add_source'),
    
    # Reports URLs
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/products/', views.product_report, name='product_report'),
    path('reports/customers/', views.customer_report, name='customer_report'),
    path('reports/analysis/', views.reports_analysis, name='reports_analysis'),
    path('reports/revenue/', views.revenue_report, name='revenue_report'),
    path('reports/popular-products/', views.popular_products, name='popular_products'),
    path('reports/processing-time/', views.processing_time, name='processing_time'),
    
    # New URLs
    path('accounts/types/', views.account_types, name='account_types'),
    path('accounts/transactions/', views.account_transactions, name='account_transactions'),
    path('accounts/tcoin/', views.tcoin_accounts, name='tcoin_accounts'),
    path('chat/messages/', views.chat_messages, name='chat_messages'),
    path('chat/sessions/', views.chat_sessions, name='chat_sessions'),
    path('email/logs/', views.email_logs, name='email_logs'),
    path('email/templates/', views.email_templates, name='email_templates'),
    path('email/editor/', views.email_editor, name='email_editor'),
    path('email/editor/<int:template_id>/', views.email_editor, name='email_editor_edit'),
    path('email/save-template/', views.email_save_template, name='email_save_template'),
    
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
] 