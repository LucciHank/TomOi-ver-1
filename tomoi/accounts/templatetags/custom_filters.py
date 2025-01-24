from django import template

register = template.Library()

@register.filter
def format_balance(value):
    if value and value != '0':
        return f" {value}"  # Thêm dấu cách trước số tiền
    return " 0"  # Thêm dấu cách trước số 0 