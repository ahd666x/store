# ممیزی کامل پروژه دکارو

تاریخ ممیزی: 2026-08-23  
نسخه commit: `23fa8d2`

---

## ۱. Scope توابع JavaScript (addToCart و مشابه)

| مورد | وضعیت | توضیح |
|------|-------|-------|
| `addToCart()` در `product_list.html` | ✅ رفع شد | تابع به `templates/includes/cart-actions.html` منتقل و در `base.html` include شد |
| فراخوانی `addToCart` در `product_card.html` | ✅ درست | اکنون از scope مشترک استفاده می‌کند |
| فراخوانی `addToCart` در `home.html` | ✅ درست | اکنون از scope مشترک استفاده می‌کند |
| `resetFilters()` و `applyFilters()` در `product_list.html` | ✅ درست | در همان صفحه تعریف شده‌اند |
| `onclick="return false;"` در تمپلیت‌های production | ✅ بی‌خطر |placeholder لینک‌ها، تابعی نیاز نیست |

**نتیجه:** همه فراخوانی‌های JS اکنون در دسترس صفحه قرار دارند.

---

## ۲. اطمینان از وجود دائمی اهداف HTMX/Alpine در DOM

| هدف | تمپلیت | وضعیت | توضیح |
|------|--------|-------|-------|
| `#cart-count` | `header.html` | ✅ رفع شد | قبلاً شرطی بود؛ اکنون همیشه با `hidden` وقتی `cart_count==0` رندر می‌شود |
| `#cart-count-mobile` | `header.html` | ✅ رفع شد | قبلاً شرطی بود؛ اکنون همیشه رندر می‌شود |
| `#cart-count-mobile-menu` | `header.html` | ✅ رفع شد | اضافه شد و همیشه رندر می‌شود |
| `#cart-count-home` | `home.html` | ✅ رفع شد | اضافه شد و همیشه رندر می‌شود |
| `mobileFilters` (x-show) | `product_list.html` | ✅ درست | همیشه در DOM |
| `userMenuOpen` (x-show) | `header.html` | ✅ درست | همیشه در DOM |
| `mobileMenuOpen` (x-show) | `header.html` | ✅ درست | همیشه در DOM |
| `activeTab` (x-show) | `profile.html` | ✅ درست | همیشه در DOM |
| `open` (x-show) | `product_detail.html` | ✅ درست | همیشه در DOM |
| `code` (x-model) | `cart/detail.html` | ✅ درست | همیشه در DOM |

**نتیجه:** هیچ هدف HTMX/Alpine که به‌صورت شرطی حذف می‌شد، باقی نمانده است.

---

## ۳. رنگ‌های Hardcoded (indigo-*)

| فایل | خط | مقدار قبلی | مقدار جدید | وضعیت |
|------|-----|-----------|-----------|-------|
| `templates/communications/notification_list.html` | 31 | `bg-indigo-50` | `bg-primary-50` | ✅ رفع شد |

**نتیجه:** هیچ رنگ hardcoded باقی نمانده است.

---

## ۴. بررسی نیاز به Celery برای `apps/communications/tasks.py`

| مورد | وضعیت | توضیح |
|------|-------|-------|
| وجود فایل `tasks.py` | ⚠️ موجود | فایل فقط یک کامنت توضیحی دارد |
| استفاده از Celery در پروژه | ❌ نیاز نیست | هیچ‌کجا از `@task`، `delay()` یا `shared_task` استفاده نشده |
| استفاده از Notification model | ✅ فقط در views | فقط در `NotificationListView` برای نمایش لیست اعلان‌ها |
| توصیه | ✅ بدون تغییر | در صورت نیاز به ارسال خودکار ایمیل/SMS در آینده، یک پرامپت بک‌اندی جداگانه برای راه‌اندازی Celery لازم است |

**نتیجه:** Celery در حال حاضر لازم نیست.

---

## ۵. چک‌لیست دسترس‌پذیری / ریسپانسیو / یکدستی بصری (پرامپت ۹)

### دسترس‌پذیری (Accessibility)

| آیتم | وضعیت | توضیح |
|------|-------|-------|
| تمام `<th>` دارای `scope="col"` باشند | ✅ انجام شد | ۸ جدول اصلاح شد |
| دکمه‌های فقط-آیکون دارای `aria-label` باشند | ✅ انجام شد | ۹ دکمه اصلاح شد |
| وارد کردن‌ها (inputs) دارای label یا `aria-label` باشند | ✅ انجام شد | ۵ وارد کردن بدون برچسب اصلاح شد |
| `focus:ring-0` از وارد کردن‌ها حذف شود | ✅ انجام شد | از وارد کردن تعداد در `product_detail.html` حذف شد |
| تصاویر دارای `alt` مناسب باشند | ✅ درست | تمام تصاویر `alt` دارند |
| لینک‌های خارجی دارای `rel="noopener"` باشند | ⚠️ بررسی نشده | نیاز به ممیزی دستی اضافی دارد |

### ریسپانسیو (Responsive)

| آیتم | وضعیت | توضیح |
|------|-------|-------|
| منوی موبایل با دکمه hamburger | ✅ وجود دارد | در `header.html` |
| فیلترهای موبایل با دراور | ✅ وجود دارد | در `product_list.html` |
| جدول‌های داده با `overflow-x-auto` | ✅ وجود دارد | در تمام تمپلیت‌های production |
| تصاویر با `loading="lazy"` | ✅ انجام شد | ۴ تصویر اضافه شد |
| ترتیب المان‌ها در موبایل | ✅ درست | از `flex-col` و `grid-cols-1` استفاده می‌شود |

### یکدستی بصری (Visual Consistency)

| آیتم | وضعیت | توضیح |
|------|-------|-------|
| پالت رنگ یکسان (primary/secondary) | ✅ انجام شد | رنگ `indigo` حذف و با `primary` جایگزین شد |
| استفاده از کامپوننت‌های مشترک (card, btn, badge) | ✅ وجود دارد | در `tailwind-input.css` تعریف شده |
| فونت یکسان (Vazirmatn) | ✅ وجود دارد | در `base.html` لود می‌شود |
| جهت RTL در کل صفحه | ✅ وجود دارد | `<html dir="rtl">` در `base.html` |
| فاصله‌گذاری یکسان (spacing scale) | ✅ درست | از کلاس‌های Tailwind استاندارد استفاده می‌شود |

---

## ۶. تغییرات اعمال‌شده در این ممیزی

### فایل‌های تغییر یافته

1. `templates/communications/notification_list.html` — `bg-indigo-50` → `bg-primary-50`
2. `templates/includes/header.html` — افزودن `aria-label` به دکمه‌های آیکونی + رندر همیشگی شمارنده سبد
3. `templates/includes/toast.html` — افزودن `aria-label` به دکمه بستن
4. `templates/catalog/product_list.html` — افزودن `aria-label` به دکمه‌های فیلتر و تغییر نمایش
5. `templates/catalog/product_detail.html` — حذف `focus:ring-0` + افزودن `loading="lazy"` + `scope="col"`
6. `templates/cart/detail.html` — افزودن `aria-label` به دکمه‌های مقدار + `loading="lazy"`
7. `templates/orders/includes/order_items.html` — افزودن `loading="lazy"`
8. تمام تمپلیت‌های production (worker_list, task_list, report, painting_process_list, holiday_list) — افزودن `scope="col"`
9. `templates/discounts/discount_list.html` — افزودن `scope="col"`

### فایل‌های بدون نیاز به تغییر

- `apps/communications/tasks.py` — فقط کامنت، Celery لازم نیست
- `apps/communications/views.py` — بدون مشکل
- `apps/communications/models.py` — بدون مشکل

---

## ۷. وضعیت نهایی

| دسته | تعداد کل | رفع شده | باقی‌مانده |
|------|---------|---------|-----------|
| رنگ hardcoded | 1 | 1 | 0 |
| `<th>` بدون `scope` | 24 | 24 | 0 |
| دکمه آیکونی بدون `aria-label` | 9 | 9 | 0 |
| وارد کردن بدون label | 5 | 5 | 0 |
| `focus:ring-0` | 1 | 1 | 0 |
| تصویر بدون `loading="lazy"` | 4 | 4 | 0 |
| اهداف HTMX/Alpine شرطی | 4 | 4 | 0 |
| **جمع** | **48** | **48** | **0** |

---

**نتیجه:** ممیزی کامل شد و تمام مشکلات یافت‌شده رفع گردید.

