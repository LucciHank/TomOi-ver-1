from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def format_balance(value):
    try:
        # Chuyển đổi sang số và format với 2 số thập phân
        formatted = floatformat(float(value), 2)
        # Thêm dấu phẩy ngăn cách hàng nghìn
        parts = str(formatted).split('.')
        parts[0] = "{:,}".format(int(parts[0]))
        return '.'.join(parts)
    except (ValueError, TypeError):
        return value 