from django.contrib import admin
from .models import Category, Post, PostView

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published_at', 'is_active', 'view_count')
    list_filter = ('category', 'is_active', 'is_featured')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'

class PostViewAdmin(admin.ModelAdmin):
    # Đã xóa user_agent khỏi list_display vì trường này không tồn tại
    list_display = ('post', 'ip_address', 'viewed_at')
    list_filter = ('viewed_at',)
    date_hierarchy = 'viewed_at'
    search_fields = ('post__title', 'ip_address')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostView, PostViewAdmin) 