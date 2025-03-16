from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from . import views
from .views import dashboard, messaging, user_list, user_detail, user_edit, user_permissions
from .views import user_activity_log, user_login_history, terminate_session, terminate_all_sessions
from .views import toggle_user_status, user_add, user_delete, import_users, user_report, user_stats
from .views import order_management, order_detail, update_order_status, export_orders
from .views import warranty_management, warranty_detail, warranty_report, send_new_account
from .views import create_warranty, update_warranty_status, assign_warranty, add_warranty_note, delete_warranty
from .views import subscription_management, subscription_plans
from .views import source_dashboard, source_list, source_add, source_edit, source_delete, source_log_list, source_analytics
from .views import share_report, source_chart_data, add_source_redirect
from .views import chat_messages, chat_sessions
from .views import email_logs, email_templates, email_editor, email_save_template
from .views import discount_management, add_discount, edit_discount, delete_discount, toggle_discount, discount_report
from .views.product import update_product_status, manage_product_images, delete_product_image, set_primary_image
from .views.product import product_detail, product_history
from .views.banner import upload_banner_image, banner_list, add_banner, edit_banner, delete_banner, toggle_banner
from .views import api_settings, save_api_config, test_api
from .views import chatbot_api_settings, chatbot_save_api, chatbot_test_api, settings, logs, responses

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

app_name = 'dashboard'

urlpatterns = [
    # Dashboard home
    path('', dashboard, name='dashboard'),
    
    # User Management
    path('users/', user_list, name='users'),
    path('users/add/', user_add, name='add_user'),
    path('users/<int:user_id>/', user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', user_edit, name='edit_user'),
    path('users/<int:user_id>/permissions/', user_permissions, name='user_permissions'),
    path('users/<int:user_id>/activity/', user_activity_log, name='user_activity'),
    path('users/<int:user_id>/login-history/', user_login_history, name='user_login_history'),
    path('users/<int:user_id>/terminate-session/<str:session_key>/', terminate_session, name='terminate_session'),
    path('users/<int:user_id>/terminate-all-sessions/', terminate_all_sessions, name='terminate_all_sessions'),
    path('users/<int:user_id>/toggle-status/', toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/delete/', user_delete, name='delete_user'),
    path('users/import/', import_users, name='import_users'),
    path('users/report/', user_report, name='user_report'),
    path('users/stats/', user_stats, name='user_stats'),
    
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
    path('subscription/', subscription_management, name='subscription'),
    path('subscription/plans/', subscription_plans, name='subscription_plans'),
    
    # Source Management
    path('source/', source_dashboard, name='source_dashboard'),
    path('source/list/', source_list, name='source_list'),
    path('source/add/', source_add, name='source_add'),
    path('source/edit/<int:source_id>/', source_edit, name='source_edit'),
    path('source/delete/<int:source_id>/', source_delete, name='source_delete'),
    path('source/logs/', source_log_list, name='source_logs'),
    path('source/analytics/', source_analytics, name='source_analytics'),
    path('source/share-report/', share_report, name='share_report'),
    path('source/chart-data/', source_chart_data, name='source_chart_data'),
    path('add-source/', add_source_redirect, name='add_source_redirect'),
    
    # Product Management - Sử dụng trực tiếp các hàm đã import từ views/__init__.py
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
    
    # Categories - Sử dụng trực tiếp các hàm đã import
    path('products/categories/', category_list, name='categories'),
    path('products/categories/add/', add_category, name='add_category'),
    path('products/categories/<int:category_id>/edit/', edit_category, name='edit_category'),
    
    # Import Products - Sử dụng trực tiếp hàm đã import
    path('products/import/', import_products, name='import_products'),
    
    # Order Management
    path('orders/', order_management, name='orders'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', update_order_status, name='update_order_status'),
    path('orders/export/', export_orders, name='export_orders'),
    
    # Discount Management
    path('discounts/', discount_management, name='discounts'),
    path('discounts/add/', add_discount, name='add_discount'),
    path('discounts/<int:discount_id>/edit/', edit_discount, name='edit_discount'),
    path('discounts/<int:discount_id>/delete/', delete_discount, name='delete_discount'),
    path('discounts/<int:discount_id>/toggle/', toggle_discount, name='toggle_discount'),
    path('discounts/report/', discount_report, name='discount_report'),
    
    # Banner Management
    path('banners/', banner_list, name='banners'),
    path('banners/add/', add_banner, name='add_banner'),
    path('banners/<int:banner_id>/edit/', edit_banner, name='edit_banner'),
    path('banners/<int:banner_id>/delete/', delete_banner, name='delete_banner'),
    path('banners/<int:banner_id>/toggle/', toggle_banner, name='toggle_banner'),
    path('banners/upload-image/', upload_banner_image, name='upload_banner_image'),
    
    # Chat
    path('chat/messages/', chat_messages, name='chat_messages'),
    path('chat/sessions/', chat_sessions, name='chat_sessions'),
    
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
    path('chatbot/settings/', chatbot_api_settings, name='chatbot_settings'),
    path('chatbot/settings/save/', chatbot_save_api, name='chatbot_save_api'),
    path('chatbot/settings/test/', chatbot_test_api, name='chatbot_test_api'),
    path('chatbot/config/', settings, name='chatbot_config'),
    path('chatbot/logs/', logs, name='chatbot_logs'),
    path('chatbot/responses/', responses, name='chatbot_responses'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 