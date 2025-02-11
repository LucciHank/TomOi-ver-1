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
    """Ẩn phần giữa của email, chỉ hiện ký tự đầu và cuối trước @"""
    try:
        parts = email.split('@')
        if len(parts) != 2:
            return email
            
        username, domain = parts
        if len(username) <= 2:  # Nếu username quá ngắn
            masked_username = username + '*' * 3
        else:
            # Giữ lại ký tự đầu và cuối, thay phần giữa bằng 3 dấu *
            masked_username = username[0] + '*' * 3 + username[-1]
            
        return f"{masked_username}@{domain}"
    except:
        return email

@register.filter
def format_price(value):
    """Format giá tiền theo định dạng Việt Nam"""
    try:
        return f"{int(value):,}đ".replace(',', '.')
    except (ValueError, TypeError):
        return value

# Thêm các filter khác từ accounts vào đây 