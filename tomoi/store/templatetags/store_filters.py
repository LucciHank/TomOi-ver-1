from django import template
from django.template.defaultfilters import stringfilter, floatformat
import re
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()

@register.filter
@stringfilter
def currency(value):
    """Định dạng số tiền theo kiểu Việt Nam"""
    try:
        value = float(value)
        return f"{value:,.0f}₫".replace(",", ".")
    except (ValueError, TypeError):
        return value

@register.filter
@stringfilter
def phone_format(value):
    """Định dạng số điện thoại Việt Nam"""
    if not value:
        return ""
    value = re.sub(r'\D', '', value)
    if len(value) == 10:
        return f"{value[:3]} {value[3:6]} {value[6:]}"
    return value

@register.filter
def format_balance(value):
    if not value:
        return "0"
    formatted = floatformat(float(value), 0)  # Thay đổi số thập phân thành 0
    parts = str(formatted).split('.')
    parts[0] = "{:,}".format(int(parts[0]))
    return f"{'.'.join(parts)}₫"  # Thêm ký hiệu tiền tệ

@register.filter
def format_price(value):
    try:
        return "{:,.0f}₫".format(float(value))
    except (ValueError, TypeError):
        return value

# Các filter khác từ custom_filters 