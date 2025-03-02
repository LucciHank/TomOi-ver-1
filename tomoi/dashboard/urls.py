from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Authentication
    path('login/', views.dashboard_login, name='login'),
    path('logout/', views.dashboard_logout, name='logout'),
    
    # Dashboard
    path('', views.index, name='home'),
    
    # Users
    path('users/', views.user_list, name='users'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    
    # Products
    path('products/', views.product_list, name='products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('products/<int:product_id>/variants/', views.product_variants, name='product_variants'),
    
    # Categories
    path('categories/', views.category_list, name='categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    
    # Orders
    path('orders/', views.order_list, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    # path('orders/export/', views.export_orders, name='export_orders'),
    
    # Marketing
    path('marketing/', views.marketing_dashboard, name='marketing'),
    # path('marketing/campaigns/', views.campaign_list, name='marketing_campaigns'),
    # path('marketing/campaigns/add/', views.add_campaign, name='add_campaign'),
    # path('marketing/campaigns/<int:campaign_id>/', views.edit_campaign, name='edit_campaign'),
    
    # Banners
    path('banners/', views.banner_list, name='banners'),
    # path('banners/add/', views.add_banner, name='add_banner'),
    # path('banners/<int:banner_id>/', views.edit_banner, name='edit_banner'),
    # path('banners/<int:banner_id>/delete/', views.delete_banner, name='delete_banner'),
    
    # Blog
    path('blogs/', views.blog_categories, name='blogs'),
    # path('blogs/categories/add/', views.add_blog_category, name='add_blog_category'),
    # path('blogs/categories/<int:category_id>/', views.edit_blog_category, name='edit_blog_category'),
    # path('blogs/categories/<int:category_id>/delete/', views.delete_blog_category, name='delete_blog_category'),
    # path('posts/', views.post_list, name='posts'),
    # path('posts/add/', views.add_post, name='add_post'),
    # path('posts/<int:post_id>/', views.edit_post, name='edit_post'),
    # path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    
    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics'),
    # path('analytics/reports/', views.analytics_reports, name='analytics_reports'),
    # path('analytics/export-report/', views.export_report, name='export_report'),
    
    # Settings
    path('settings/', views.system_settings, name='settings'),
    
    # Discounts
    path('discounts/', views.discount_list, name='discounts'),
    path('discounts/add/', views.add_discount, name='add_discount'),
    path('discounts/<int:discount_id>/', views.edit_discount, name='edit_discount'),
    path('discounts/<int:discount_id>/delete/', views.delete_discount, name='delete_discount'),
    
    # Email Templates
    path('email-templates/', views.email_templates, name='email_templates'),
    path('email-templates/add/', views.add_email_template, name='add_email_template'),
    path('email-templates/<int:template_id>/', views.edit_email_template, name='edit_email_template'),
    path('email-templates/<int:template_id>/delete/', views.delete_email_template, name='delete_email_template'),
    path('email-logs/', views.email_logs, name='email_logs'),
    
    # Chatbot
    path('chatbot/', views.chatbot_dashboard, name='chatbot'),
    path('chatbot/responses/', views.chatbot_responses, name='chatbot_responses'),
    path('chatbot/settings/', views.chatbot_settings, name='chatbot_settings'),
    path('chatbot/logs/', views.chatbot_logs, name='chatbot_logs'),
    
    # Tickets/Support
    path('tickets/', views.ticket_list, name='tickets'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/<int:ticket_id>/reply/', views.ticket_reply, name='ticket_reply'),
    path('tickets/<int:ticket_id>/close/', views.close_ticket, name='close_ticket'),
    
    # Chart Data
    path('chart-data/', views.chart_data, name='chart_data'),
] 