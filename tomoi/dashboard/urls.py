from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    
    # User management
    path('users/', views.user_management, name='users'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/delete/', views.delete_user, name='delete_user'),
    path('users/suspend/', views.suspend_user, name='suspend_user'),
    path('users/unlock/', views.unlock_user, name='unlock_user'),
    
    # Role management
    path('users/roles/', views.role_management, name='roles'),
    path('users/roles/add/', views.add_role, name='add_role'),
    path('users/roles/<int:role_id>/edit/', views.edit_role, name='edit_role'),
    path('users/roles/<int:role_id>/delete/', views.delete_role, name='delete_role'),
    
    # Marketing
    path('marketing/', views.marketing_dashboard, name='marketing'),
    path('marketing/campaigns/add/', views.add_campaign, name='add_campaign'),
    path('marketing/campaigns/<int:campaign_id>/edit/', views.edit_campaign, name='edit_campaign'),
    path('marketing/campaigns/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('marketing/campaigns/get/', views.get_campaign, name='get_campaign'),
    path('marketing/campaigns/delete/', views.delete_campaign, name='delete_campaign'),
    
    # Orders
    path('orders/', views.order_management, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/cancel/', views.cancel_order, name='cancel_order'),
    
    # Products
    path('products/', views.product_management, name='products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('products/delete/', views.delete_product, name='delete_product'),
    path('products/get/', views.get_product, name='get_product'),
    
    # Categories
    path('products/categories/', views.category_management, name='categories'),
    path('products/categories/add/', views.add_category, name='add_category'),
    path('products/categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('products/categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    
    # Posts
    path('posts/', views.post_management, name='posts'),
    path('posts/add/', views.add_post, name='add_post'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/delete/', views.delete_post, name='delete_post'),
    
    # Post categories
    path('posts/categories/', views.post_category_management, name='post_categories'),
    path('posts/categories/add/', views.add_post_category, name='add_post_category'),
    path('posts/categories/<int:category_id>/edit/', views.edit_post_category, name='edit_post_category'),
    path('posts/categories/<int:category_id>/get/', views.get_post_category, name='get_post_category'),
    
    # Settings
    path('settings/', views.settings_dashboard, name='settings'),
    path('settings/clear-logs/', views.clear_logs, name='clear_logs'),
    
    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics'),
    
    # Tickets
    path('tickets/', views.ticket_management, name='tickets'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/<int:ticket_id>/assign/', views.assign_ticket, name='assign_ticket'),
    path('tickets/close/', views.close_ticket, name='close_ticket'),
    
    # API endpoints
    path('api/chart-data/', views.get_chart_data, name='chart_data'),
    path('api/traffic-data/', views.get_traffic_data, name='traffic_data'),
    path('api/visitor-stats/', views.get_visitor_stats, name='visitor_stats'),
    path('api/page-stats/', views.get_page_stats, name='page_stats'),
    path('api/referrer-stats/', views.get_referrer_stats, name='referrer_stats'),
    path('api/device-stats/', views.get_device_stats, name='device_stats'),
    path('api/realtime/visitors/', views.get_realtime_visitors, name='realtime_visitors'),
    path('api/realtime/pageviews/', views.get_realtime_pageviews, name='realtime_pageviews'),
    path('api/realtime/locations/', views.get_realtime_locations, name='realtime_locations'),
    path('api/stock-data/', views.get_stock_data, name='get_stock_data'),
] 