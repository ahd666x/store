from django import template

register = template.Library()

PERSIAN_DIGITS = '۰۱۲۳۴۵۶۷۸۹'
PERSIAN_THOUSANDS_SEP = '٬'


@register.filter
def price_fa(value):
    """قیمت را با جداکنندهٔ سه‌رقمی و اعداد انگلیسی نمایش می‌دهد. مثال: 1000000 -> 1,000,000"""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value
    return f"{value:,}"


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
