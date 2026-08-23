"""
منطق مشترک محاسبه قیمت بر اساس تغییر ابعاد سفارشی محصول (طول/عرض/ارتفاع).
تنها منبع محاسبه قیمت ابعاد سفارشی در کل پروژه — هم در apps/cart (نمایش لحظه‌ای
در سبد) و هم در apps/orders (هنگام ثبت نهایی سفارش) باید از همین تابع استفاده
شود تا قیمت هرگز بین سبد و سفارش نهایی مغایرت نداشته باشد.

فرمول: مجموع اختلاف هر بعد (طول + عرض + ارتفاع) نسبت به ابعاد پیش‌فرض محصول،
ضربدر درصد افزایش قیمت به ازای هر سانتی‌متر (price_increment_per_cm).
"""


def _dimension_diff(custom, default):
    """اختلاف یک بعد را نسبت به مقدار پیش‌فرض محصول برمی‌گرداند.
    اگر بعد پیش‌فرض یا بعد سفارشی مشخص نباشد، آن بعد اصلاً در قیمت تاثیر
    ندارد (اختلاف صفر در نظر گرفته می‌شود)."""
    if custom is None or default is None:
        return 0
    try:
        return int(custom) - int(default)
    except (TypeError, ValueError):
        return 0


def calculate_dimension_price(
    base_price,
    price_increment_per_cm,
    default_length=None,
    default_width=None,
    default_height=None,
    length=None,
    width=None,
    height=None,
):
    """قیمت نهایی را بر اساس ابعاد سفارشی محاسبه می‌کند.

    - base_price / price_increment_per_cm: از Product
    - default_length/width/height: ابعاد پیش‌فرض محصول (Product.length/width/height)
    - length/width/height: ابعاد انتخابی مشتری

    خروجی: عدد صحیح غیرمنفی
    """
    base_price_int = int(base_price or 0)
    increment_percent = float(price_increment_per_cm or 0)

    total_diff_cm = (
        _dimension_diff(length, default_length)
        + _dimension_diff(width, default_width)
        + _dimension_diff(height, default_height)
    )

    diff_percent = (total_diff_cm * increment_percent) / 100
    price_increase = base_price_int * diff_percent
    final_price = base_price_int + price_increase

    if final_price < 0:
        return 0
    return int(round(final_price))
