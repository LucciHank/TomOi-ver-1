from django.contrib import admin
from django import forms
from django.db import models
from .models import (
    Category, Product, ProductImage, ProductVariant, 
    VariantOption, Order, Banner, ProductLabel, BlogPost, SearchHistory
)
from .forms import ProductAdminForm
from django.utils.text import slugify

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class VariantOptionInline(admin.TabularInline):
    model = VariantOption
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    inlines = [VariantOptionInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['name', 'brand', 'duration', 'price', 'is_active']
    list_filter = ['brand', 'duration', 'is_active']
    search_fields = ['name', 'description']
    inlines = [ProductImageInline, ProductVariantInline]
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'slug', 'brand', 'category', 'price', 'old_price', 'cost_price', 'stock', 'duration')
        }),
        ('Mô tả sản phẩm', {
            'fields': ('description', 'short_description', 'features_text')
        }),
        ('Tùy chọn nâng cao', {
            'fields': ('is_featured', 'label_type', 'is_cross_sale', 'cross_sale_products', 'cross_sale_discount')
        }),
        ('Yêu cầu thông tin khách hàng', {
            'fields': (
                'requires_email',
                'requires_account_password',
            ),
            'description': 'Chọn loại thông tin cần yêu cầu từ khách hàng'
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        })
    )
    filter_horizontal = ('cross_sale_products',)
    prepopulated_fields = {'slug': ('name',)}

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'requires_email':
            field.label = 'Yêu cầu Email'
        elif db_field.name == 'requires_account_password':
            field.label = 'Yêu cầu Tài khoản & Mật khẩu'
        return field

    class Media:
        css = {
            'all': [
                'django_ckeditor_5/dist/styles.css',
            ]
        }
        js = [
            'django_ckeditor_5/dist/bundle.js',
        ]

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'is_active')
    list_filter = ('product', 'is_active')
    inlines = [VariantOptionInline]

@admin.register(VariantOption)
class VariantOptionAdmin(admin.ModelAdmin):
    list_display = ('variant', 'duration', 'price', 'stock', 'is_active')
    list_filter = ('variant', 'is_active')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username',)

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'order', 'is_active']
    list_filter = ['location', 'is_active']
    search_fields = ['title']
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('title', 'image', 'link', 'location')
        }),
        ('Cài đặt hiển thị', {
            'fields': ('order', 'is_active')
        })
    )

@admin.register(ProductLabel)
class ProductLabelAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']
    
    class Media:
        css = {
            'all': ['admin/css/color-picker.css']
        }
        js = ['admin/js/color-picker.js']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['color'].widget.attrs['class'] = 'color-picker'
        return form

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('products',)

    class Media:
        css = {
            'all': [
                'django_ckeditor_5/dist/styles.css',
            ]
        }

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'user', 'created_at', 'ip_address')
    list_filter = ('created_at',)
    search_fields = ('keyword', 'user__username', 'ip_address')
    readonly_fields = ('created_at', 'ip_address', 'user_agent')
    date_hierarchy = 'created_at'
