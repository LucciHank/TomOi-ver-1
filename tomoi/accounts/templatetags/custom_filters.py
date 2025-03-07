from django import template

register = template.Library()

@register.filter
def get_item(lst, i):
    try:
        return lst[i]
    except:
        return None

@register.filter(name='format_price')
def format_price(value):
    try:
        return "{:,.0f}".format(float(value)).replace(',', '.')
    except (ValueError, TypeError):
        return value 