from django import template
from django.template.defaultfilters import floatformat

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

@register.filter
def mask_email(email):
    """Ẩn một phần email, chỉ hiện 3 ký tự đầu và domain"""
    try:
        parts = email.split('@')
        if len(parts) != 2:
            return email
        username, domain = parts
        if len(username) <= 3:
            masked_username = username + '*' * 3
        else:
            masked_username = username[:3] + '*' * (len(username) - 3)
        return f"{masked_username}@{domain}"
    except:
        return email

# Thêm các filter khác từ accounts vào đây 