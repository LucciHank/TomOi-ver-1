from django import template
from django.utils import timezone
from django.template.defaultfilters import floatformat, timesince
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='time_since_vi')
def time_since_vi(value):
    """Chuyển timesince sang tiếng Việt và chỉ hiển thị đơn vị lớn nhất"""
    if not value:
        return ''
    
    now = timezone.now()
    diff = now - value
    
    years = diff.days // 365
    months = diff.days // 30
    days = diff.days
    hours = diff.seconds // 3600
    minutes = diff.seconds // 60
    
    # Chỉ trả về đơn vị lớn nhất
    if years > 0:
        return f'{years} năm trước'
    if months > 0:
        return f'{months} tháng trước'
    if days > 0:
        return f'{days} ngày trước'
    if hours > 0:
        return f'{hours} giờ trước'
    if minutes > 0:
        return f'{minutes} phút trước'
    return 'Vừa xong'

@register.filter
def format_balance(value):
    try:
        return f"{int(value):,}₫"
    except (ValueError, TypeError):
        return "0₫"

@register.filter
def mask_email(email):
    """Ẩn một phần địa chỉ email"""
    if not email:
        return email

    parts = email.split('@')
    if len(parts) != 2:
        return email
        
    username = parts[0]
    domain = parts[1]
    
    if len(username) <= 2:
        masked_username = username[0] + '*'
    else:
        visible_chars = min(2, len(username))
        masked_username = username[:visible_chars] + '*' * (len(username) - visible_chars)
    
    return f"{masked_username}@{domain}"

@register.filter
def format_price(value):
    """Format giá tiền theo định dạng Việt Nam"""
    try:
        return f"{int(value):,}đ".replace(',', '.')
    except (ValueError, TypeError):
        return value 