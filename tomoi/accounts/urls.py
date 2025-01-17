from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import account_management

urlpatterns = [
    path('', views.index, name='accounts_home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('account_management/', account_management, name='account_management'),
]
