from django.contrib import admin
from .models import Category, Post, PostView

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'published_at', 'is_featured', 'view_count', 'is_active']
    list_filter = ['category', 'is_featured', 'is_active', 'published_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ['-published_at']

@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ['post', 'ip_address', 'user_agent', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['post__title', 'ip_address']
    date_hierarchy = 'viewed_at' 