from django.contrib import admin
from django import forms
from django.db import models
from .models import Category, Product, ProductImage, Variant, Option, Order, Banner, ProductLabel
from django.utils.text import slugify

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_featured')
    list_filter = ('category', 'is_featured')
    search_fields = ('name',)
    list_editable = ('is_featured',)
    inlines = [ProductImageInline, VariantInline]

@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'product')
    list_filter = ('product',)

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('variant', 'duration', 'price')
    list_filter = ('variant',)

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
