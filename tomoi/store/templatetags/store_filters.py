from django import template
from django.template.defaultfilters import stringfilter, floatformat
import re
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()

@register.filter
@stringfilter
def currency(value):
    """Format giá tiền theo định dạng Việt Nam"""
    if value is None:
        return '0₫'
    try:
        return f"{int(value):,}₫".replace(',', '.')
    except (ValueError, TypeError):
        return value

@register.filter
@stringfilter
def phone_format(value):
    """Định dạng số điện thoại Việt Nam"""
    if not value:
        return ''
    try:
        # Loại bỏ các ký tự không phải số
        value = re.sub(r'\D', '', str(value))
        # Định dạng: 0xxx xxx xxx
        if len(value) == 10:
            return f"{value[0:4]} {value[4:7]} {value[7:10]}"
        # Định dạng: +84 xxx xxx xxx
        elif len(value) == 11 and value.startswith('84'):
            return f"+84 {value[2:5]} {value[5:8]} {value[8:11]}"
        else:
            return value
    except Exception:
        return value

@register.filter
def format_balance(value):
    """Format số dư tài khoản theo kiểu Việt Nam"""
    try:
        return f"{int(value):,} VNĐ".replace(',', '.')
    except (ValueError, TypeError):
        return value

@register.filter
def format_price(value):
    """Format giá tiền theo định dạng Việt Nam"""
    try:
        return f"{int(value):,}₫".replace(',', '.')
    except (ValueError, TypeError):
        return value

@register.filter
def get_item(dictionary, key):
    """Lấy một phần tử từ dictionary theo key"""
    if dictionary is None:
        return None
    return dictionary.get(key, 0)

@register.filter
def percentage(value, total):
    """Tính phần trăm của một giá trị so với tổng"""
    try:
        if total <= 0:
            return 0
        return int((value / total) * 100)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def divide(value, arg):
    """Chia value cho arg"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def multiply(value, arg):
    """Nhân value với arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def subtract(value, arg):
    """Trừ arg từ value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

# Các filter khác từ custom_filters 