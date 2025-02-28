from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def div(value, arg):
    """Chia hai số"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    """Nhân hai số"""
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0

@register.filter
def percentage(value, total):
    """Tính phần trăm"""
    try:
        return (float(value) / float(total)) * 100
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def currency(value):
    """Format số tiền"""
    try:
        return "{:,.0f}₫".format(float(value))
    except (ValueError, TypeError):
        return value

@register.filter
def status_color(status):
    """Màu cho trạng thái"""
    colors = {
        'active': 'success',
        'scheduled': 'info', 
        'ended': 'danger',
        'inactive': 'warning'
    }
    return colors.get(status, 'secondary') 