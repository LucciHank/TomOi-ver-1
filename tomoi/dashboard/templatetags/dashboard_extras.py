from django import template
import random

register = template.Library()

@register.filter
def random_color(index):
    """Returns a random color from the predefined list based on the index"""
    colors = [
        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
        '#5a5c69', '#858796', '#6610f2', '#fd7e14', '#20c997'
    ]
    idx = int(index) % len(colors)
    return colors[idx] 