from django.contrib import admin
from django import forms
from django.db import models
from .models import Category, Product, ProductImage, Variant, Option, Order

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}

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
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name',)
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
