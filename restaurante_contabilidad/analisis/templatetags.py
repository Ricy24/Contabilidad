# analisis/templatetags.py
from django import template

register = template.Library()

@register.filter(name='divide')
def divide(value, arg):
    try:
        return value / arg
    except (ZeroDivisionError, TypeError):
        return value  # Devuelve el valor original si hay un error
