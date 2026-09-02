from django import template

register = template.Library()

PERSIAN_DIGITS = '۰۱۲۳۴۵۶۷۸۹'
PERSIAN_THOUSANDS_SEP = '٬'


@register.filter
def price_fa(value):
    """قیمت را با جداکنندهٔ سه‌رقمی و اعداد فارسی نمایش می‌دهد. مثال: 1000000 -> ۱٬۰۰۰٬۰۰۰"""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value
    formatted = f"{value:,}"
    for i, digit in enumerate('0123456789'):
        formatted = formatted.replace(digit, PERSIAN_DIGITS[i])
    return formatted.replace(',', PERSIAN_THOUSANDS_SEP)


@register.filter
def fa_number(value):
    """اعداد را به فارسی تبدیل می‌کند بدون جداکنندهٔ سه‌رقمی. مناسط شمارش‌ها و شمارهٔ صفحه."""
    try:
        s = str(int(value))
    except (TypeError, ValueError):
        s = str(value)
    for i, digit in enumerate('0123456789'):
        s = s.replace(digit, PERSIAN_DIGITS[i])
    return s


@register.filter
def is_hex(value):
    """بررسی می‌کند که مقدار یک کد رنگ هگزادسیمال با پیشوند # معتبر باشد."""
    if not isinstance(value, str):
        return False
    v = value.strip()
    if not v.startswith('#'):
        return False
    hexpart = v[1:].lstrip('#')
    if len(hexpart) not in (3, 6, 8):
        return False
    try:
        int(hexpart, 16)
    except ValueError:
        return False
    return True
