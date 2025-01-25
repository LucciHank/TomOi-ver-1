from django import template
from ..utils import mask_email as mask_email_util
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def format_balance(value):
    try:
        # Chuyển đổi sang số và format với 2 số thập phân
        formatted = floatformat(float(value), 0)
        # Thêm dấu phẩy ngăn cách hàng nghìn
        parts = str(formatted).split('.')
        parts[0] = "{:,}".format(int(parts[0]))
        return '.'.join(parts) + 'đ'
    except (ValueError, TypeError):
        return value

@register.filter
def mask_email(value):
    return mask_email_util(value) 