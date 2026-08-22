import jdatetime
from django import template

register = template.Library()


@register.filter
def jformat(value, format_string='Y/m/d'):
    if value is None:
        return ''
    if isinstance(value, jdatetime.date):
        return value.strftime(format_string)
    if isinstance(value, jdatetime.datetime):
        return value.strftime(format_string)
    return value
