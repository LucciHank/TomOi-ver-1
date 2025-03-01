from django import template
from django.template.defaultfilters import floatformat
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def format_balance(value):
    try:
        formatted = floatformat(float(value), 0)  # Thay đổi số thập phân thành 0
        parts = str(formatted).split('.')
        parts[0] = "{:,}".format(int(parts[0]))
        return f"{'.'.join(parts)}₫"  # Thêm ký hiệu tiền tệ
    except (ValueError, TypeError):
        return value

# ... các filter khác giữ nguyên 