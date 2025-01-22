# filters.py
from django import template

register = template.Library()

@register.filter
def div(value, arg):
    try:
        return value / arg
    except (TypeError, ZeroDivisionError):
        return 0
