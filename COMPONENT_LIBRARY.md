# Component Library Documentation - دکارو

## Overview

This document describes the reusable Django template component library for the دکارو storefront application. Components are organized by functional area and follow consistent conventions for parameters, responsive behavior, and accessibility.

## Directory Structure

```
templates/components/
├── cards/
│   ├── card.html
│   ├── quick_link_card.html
│   └── stat_card.html
├── data/
│   ├── badge.html
│   ├── date.html
│   ├── price.html
│   └── status_badge.html
├── feedback/
│   ├── alert.html
│   └── empty_state.html
├── forms/
│   ├── checkbox.html
│   ├── form_field.html
│   ├── input.html
│   ├── search.html
│   ├── select.html
│   └── textarea.html
├── loading/
│   └── loading_overlay.html
├── modals/
│   ├── confirm_modal.html
│   └── modal.html
├── navigation/
│   ├── breadcrumb.html
│   └── header.html
├── tables/
│   ├── pagination.html
│   ├── table.html
│   └── table_actions.html
```

## Design System

- **Storefront (Tailwind):** Uses `btn-primary`, `btn-secondary`, `card`, `form-input`, `form-select` CSS classes defined in `static/css/style.css`
- **Dashboard (Bootstrap):** Uses Bootstrap 5 RTL classes (`btn`, `card`, `form-control`, `table`, `modal`, etc.)
- **RTL Support:** All components support right-to-left layouts
- **Responsive:** Components use responsive Tailwind/Bootstrap utilities
- **Accessibility:** Components include proper ARIA labels, semantic HTML, and keyboard navigation support

---

## Components

### Feedback

#### `components/feedback/empty_state.html`

**Purpose:** Display when no data is available (empty cart, no search results, no products).

**Path:** `templates/components/feedback/empty_state.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `icon_svg` | string | - | Raw SVG markup for the icon |
| `message` | string | "هیچ موردی یافت نشد." | Message text |
| `action_url` | string | - | URL for primary action link |
| `action_text` | string | - | Text for primary action |
| `action_onclick` | string | - | JavaScript onclick for button action |
| `secondary_action_url` | string | - | URL for secondary action |
| `secondary_action_text` | string | - | Text for secondary action |

**Usage Example:**

```django
{% include 'components/feedback/empty_state.html' with 
    icon_svg='<svg>...</svg>' 
    message='سبد خرید شما خالی است.' 
    action_url=product_list_url 
    action_text='مشاهده محصولات' 
%}
```

**Responsive Behavior:** Centered layout with responsive spacing (`py-16`).

**Dependencies:** Tailwind CSS classes (`text-center`, `py-16`, `btn-primary`).

---

#### `components/feedback/alert.html`

**Purpose:** Display alert/notification messages for storefront.

**Path:** `templates/components/feedback/alert.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | string | "info" | Alert type: `success`, `danger`, `warning`, `info` |
| `message` | string | - | Alert message (can contain HTML) |
| `dismissible` | boolean | false | Show dismiss button |

**Usage Example:**

```django
{% include 'components/feedback/alert.html' with 
    type='danger' 
    message='خطا در پردازش درخواست' 
    dismissible=true 
%}
```

**Responsive Behavior:** Full-width responsive alert.

**Dependencies:** Bootstrap alert classes (`alert`, `alert-success`, `alert-dismissible`, `btn-close`).

---

### Data Display

#### `components/data/status_badge.html`

**Purpose:** Display order/task status with appropriate colors.

**Path:** `templates/components/data/status_badge.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | - | Status key: `paid`, `delivered`, `completed`, `shipped`, `producing`, `planned`, `cancelled`, `draft` |
| `display_text` | string | auto | Override display text |

**Usage Example:**

```django
{% include 'components/data/status_badge.html' with status=order.status %}
```

**Responsive Behavior:** Inline badge, scales with font size.

**Dependencies:** Bootstrap badge classes (`badge`, `badge-success`, `badge-warning`, etc.).

---

#### `components/data/badge.html`

**Purpose:** Generic badge for labels and statuses.

**Path:** `templates/components/data/badge.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | string | - | Badge text |
| `variant` | string | "default" | Variant: `default`, `primary`, `success`, `warning`, `danger`, `info` |
| `size` | string | - | Size: `sm`, `lg` |

**Usage Example:**

```django
{% include 'components/data/badge.html' with text='فعال' variant='success' %}
```

**Responsive Behavior:** Inline badge.

**Dependencies:** Bootstrap badge classes.

---

#### `components/data/price.html`

**Purpose:** Reusable price display.

**Path:** `templates/components/data/price.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `amount` | string/number | - | Price amount |
| `currency` | string | "تومان" | Currency label |
| `size` | string | "base" | Size: `sm`, `base`, `lg` |
| `compare_price` | string/number | - | Original price for strikethrough |

**Usage Example:**

```django
{% include 'components/data/price.html' with 
    amount=product.price 
    currency='تومان' 
    size='lg' 
    compare_price=product.base_price 
%}
```

**Responsive Behavior:** Scales with size parameter.

**Dependencies:** Tailwind CSS classes (`text-primary-600`, `text-stone-400`, `line-through`).

---

#### `components/data/date.html`

**Purpose:** Reusable date display with jformat support.

**Path:** `templates/components/data/date.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `date` | datetime | - | Date object |
| `format` | string | "Y/m/d" | jformat pattern |
| `class` | string | - | Additional CSS classes |

**Usage Example:**

```django
{% include 'components/data/date.html' with date=order.created_at format='Y/m/d' class='text-sm text-stone-500' %}
```

**Responsive Behavior:** Inherits from parent.

**Dependencies:** `jformat` template tag library.

---

### Cards

#### `components/cards/card.html`

**Purpose:** Reusable card container for storefront (Tailwind).

**Path:** `templates/components/cards/card.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | string | - | Card header title |
| `footer` | string | - | Card footer content |
| `padding` | string | "p-6" | Padding class |
| `shadow` | string | "shadow-sm" | Shadow class |
| `border` | string | "border-stone-200" | Border class |
| `hover` | boolean | false | Add hover effects |

**Usage Example:**

```django
{% include 'components/cards/card.html' with title='اطلاعات کاربر' padding='p-6' hover=true %}
    Card content here
{% endinclude %}
```

**Responsive Behavior:** Full-width responsive.

**Dependencies:** Tailwind CSS classes.

---

#### `components/cards/quick_link_card.html`

**Purpose:** Dashboard navigation card with icon and label.

**Path:** `templates/components/cards/quick_link_card.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `icon` | string | "link-45deg" | Bootstrap Icon name |
| `title` | string | - | Card title |
| `href` | string | "#" | Link URL |

**Usage Example:**

```django
{% include 'components/cards/quick_link_card.html' with 
    icon='list-ul' 
    title='لیست سفارشات' 
    href=order_list_url 
%}
```

**Responsive Behavior:** Grid item, responsive columns (`col-6 col-md-3`).

**Dependencies:** Bootstrap Icons, `dashboard.css` (`quick-link-card` class).

---

#### `components/cards/stat_card.html`

**Purpose:** Dashboard statistic card with icon, title, and value.

**Path:** `templates/components/cards/stat_card.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | string | - | Card title |
| `value` | string | - | Statistic value |
| `subtitle` | string | - | Additional subtitle |
| `icon` | string | "graph-up" | Bootstrap Icon name |
| `color` | string | "primary" | Icon color theme |
| `href` | string | "#" | Link URL |

**Usage Example:**

```django
{% include 'components/cards/stat_card.html' with 
    title='سفارشات' 
    value='۱۲۳' 
    subtitle='این ماه' 
    icon='cart' 
    href=order_list_url 
%}
```

**Responsive Behavior:** Full-height grid item (`h-100`).

**Dependencies:** Bootstrap Icons, `dashboard.css` (`quick-link-card` class).

---

### Navigation

#### `components/navigation/breadcrumb.html`

**Purpose:** Navigation breadcrumb for storefront.

**Path:** `templates/components/navigation/breadcrumb.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `items` | list | - | List of dicts with `url` and `label` keys |

**Usage Example:**

```django
{% with breadcrumb_items=[{'url': url('home'), 'label': 'خانه'}, {'url': url('catalog:product_list'), 'label': 'محصولات'}, {'label': 'جزئیات'}] %}
    {% include 'components/navigation/breadcrumb.html' with items=breadcrumb_items %}
{% endwith %}
```

**Responsive Behavior:** Horizontal on desktop, scrollable on mobile.

**Dependencies:** Tailwind CSS classes (`section-container`, `py-3`, `flex`, `gap-2`).

---

#### `components/navigation/header.html`

**Purpose:** Storefront site header with navigation, search, cart, and user menu.

**Path:** `templates/components/navigation/header.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `user` | User | - | Authenticated user object |
| `cart_count` | int | 0 | Number of items in cart |
| `current_path` | string | - | Current URL path |

**Usage Example:**

```django
{% include 'components/navigation/header.html' with user=user cart_count=cart_count %}
```

**Responsive Behavior:** Desktop navigation hidden on mobile, mobile menu with hamburger button.

**Dependencies:** Alpine.js (`x-data`, `x-show`, `x-transition`, `@click.away`), Tailwind CSS, Bootstrap Icons (`includes/icons.html`).

---

### Forms

#### `components/forms/form_field.html`

**Purpose:** Reusable form field with label, input, errors, and hint.

**Path:** `templates/components/forms/form_field.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `field` | BoundField | - | Django form field |
| `label` | string | field.label | Override label text |
| `hint` | string | field.help_text | Override help text |
| `wrapper_class` | string | - | Additional wrapper CSS classes |
| `required` | boolean | field.field.required | Mark as required |

**Usage Example:**

```django
{% include 'components/forms/form_field.html' with field=form.username label='نام کاربری' %}
```

**Responsive Behavior:** Full-width form field.

**Dependencies:** Bootstrap form classes (`form-label`, `form-error`, `form-text`).

---

#### `components/forms/input.html`

**Purpose:** Reusable form input.

**Path:** `templates/components/forms/input.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | - | Input name |
| `value` | string | "" | Input value |
| `placeholder` | string | "" | Placeholder text |
| `type` | string | "text" | Input type |
| `required` | boolean | false | Required attribute |
| `disabled` | boolean | false | Disabled attribute |
| `readonly` | boolean | false | Readonly attribute |
| `class` | string | - | Additional CSS classes |
| `id` | string | name | Element ID |

**Usage Example:**

```django
{% include 'components/forms/input.html' with 
    name='q' 
    placeholder='جستجو...' 
    value=request.GET.q 
%}
```

**Responsive Behavior:** Full-width by default.

**Dependencies:** Bootstrap form classes (`form-input`).

---

#### `components/forms/select.html`

**Purpose:** Reusable form select.

**Path:** `templates/components/forms/select.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | - | Select name |
| `value` | string | - | Selected value |
| `options` | list | - | List of `(value, label)` tuples |
| `required` | boolean | false | Required attribute |
| `disabled` | boolean | false | Disabled attribute |
| `class` | string | - | Additional CSS classes |
| `id` | string | name | Element ID |

**Usage Example:**

```django
{% include 'components/forms/select.html' with 
    name='category' 
    options=categories 
    value=selected_category 
%}
```

**Responsive Behavior:** Full-width by default.

**Dependencies:** Bootstrap form classes (`form-select`).

---

#### `components/forms/textarea.html`

**Purpose:** Reusable form textarea.

**Path:** `templates/components/forms/textarea.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | - | Textarea name |
| `value` | string | "" | Textarea value |
| `placeholder` | string | "" | Placeholder text |
| `rows` | int | 3 | Number of rows |
| `required` | boolean | false | Required attribute |
| `disabled` | boolean | false | Disabled attribute |
| `class` | string | - | Additional CSS classes |
| `id` | string | name | Element ID |

**Usage Example:**

```django
{% include 'components/forms/textarea.html' with 
    name='description' 
    placeholder='توضیحات...' 
    rows=4 
%}
```

**Responsive Behavior:** Full-width by default.

**Dependencies:** Bootstrap form classes (`form-input`).

---

#### `components/forms/search.html`

**Purpose:** Reusable search input with icon.

**Path:** `templates/components/forms/search.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `action_url` | string | "#" | Form action URL |
| `placeholder` | string | "جستجو..." | Input placeholder |
| `name` | string | "q" | Input name |
| `value` | string | "" | Input value |
| `class` | string | - | Additional wrapper CSS classes |

**Usage Example:**

```django
{% include 'components/forms/search.html' with 
    action_url=url('catalog:product_list') 
    placeholder='جستجوی محصولات...' 
    value=request.GET.q 
%}
```

**Responsive Behavior:** Full-width on mobile, fixed width on desktop.

**Dependencies:** Tailwind CSS classes.

---

#### `components/forms/checkbox.html`

**Purpose:** Reusable checkbox with label.

**Path:** `templates/components/forms/checkbox.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | - | Checkbox name |
| `id` | string | name | Element ID |
| `label` | string | - | Label text |
| `checked` | boolean | false | Checked state |
| `disabled` | boolean | false | Disabled state |
| `class` | string | - | Additional CSS classes |

**Usage Example:**

```django
{% include 'components/forms/checkbox.html' with 
    name='remember-me' 
    id='remember_me' 
    label='مرا به خاطر بسپار' 
%}
```

**Responsive Behavior:** Inline flex layout.

**Dependencies:** Tailwind CSS classes.

---

### Tables

#### `components/tables/table.html`

**Purpose:** Reusable Bootstrap table for dashboard/production.

**Path:** `templates/components/tables/table.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `headers` | list | - | List of column header strings |
| `rows` | list | - | List of rows (each row is a list of cell strings) |
| `empty_message` | string | "هیچ داده‌ای یافت نشد" | Message when no rows |
| `clickable` | boolean | false | Add clickable row behavior |
| `table_class` | string | "table-hover" | Additional table classes |

**Usage Example:**

```django
{% with 
    headers=['شماره', 'نماینده', 'وضعیت'] 
    rows=order_rows 
%}
    {% include 'components/tables/table.html' with headers=headers rows=rows clickable=true %}
{% endwith %}
```

**Responsive Behavior:** Wrapped in `table-responsive` for horizontal scroll on mobile.

**Dependencies:** Bootstrap table classes.

---

#### `components/tables/pagination.html`

**Purpose:** Server-side pagination for list views.

**Path:** `templates/components/tables/pagination.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page_obj` | Page | - | Django Page object |
| `paginator` | Paginator | - | Django Paginator object |
| `url_params` | dict | - | Additional URL parameters to preserve |

**Usage Example:**

```django
{% include 'components/tables/pagination.html' with 
    page_obj=page_obj 
    paginator=page_obj.paginator 
    url_params=request.GET 
%}
```

**Responsive Behavior:** Centered pagination, wraps on small screens.

**Dependencies:** Bootstrap pagination classes.

---

#### `components/tables/table_actions.html`

**Purpose:** Reusable action buttons for table rows.

**Path:** `templates/components/tables/table_actions.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `actions` | list | - | List of dicts with `url`, `icon`, `title`, `class`, `target` keys |

**Usage Example:**

```django
{% with actions=[
    {'url': edit_url, 'icon': 'pencil', 'title': 'ویرایش'},
    {'url': delete_url, 'icon': 'trash', 'title': 'حذف', 'class': 'btn-outline-danger'}
] %}
    {% include 'components/tables/table_actions.html' with actions=actions %}
{% endwith %}
```

**Responsive Behavior:** Button group, wraps on very small screens.

**Dependencies:** Bootstrap button group classes, Bootstrap Icons.

---

### Modals

#### `components/modals/modal.html`

**Purpose:** Reusable Bootstrap modal for dashboard/production.

**Path:** `templates/components/modals/modal.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `modal_id` | string | - | Modal DOM ID |
| `title` | string | - | Modal title |
| `size` | string | "" | Size: `sm`, `lg`, `xl` |
| `form_id` | string | - | Form ID (wraps content in form) |
| `form_action` | string | - | Form action URL |
| `csrf_token` | boolean | true | Include CSRF token |
| `submit_text` | string | - | Submit button text |
| `cancel_text` | string | "انصراف" | Cancel button text |

**Usage Example:**

```django
{% include 'components/modals/modal.html' with 
    modal_id='workerModal' 
    title='کارگر جدید' 
    form_id='workerForm' 
    submit_text='ذخیره' 
%}
    <div class="mb-3">
        <label class="form-label">نام</label>
        <input type="text" name="name" class="form-input">
    </div>
{% endinclude %}
```

**Responsive Behavior:** Responsive dialog sizing.

**Dependencies:** Bootstrap modal classes (`modal`, `modal-dialog`, `modal-content`, `modal-header`, `modal-body`, `modal-footer`), Bootstrap JS.

---

#### `components/modals/confirm_modal.html`

**Purpose:** Reusable confirmation dialog.

**Path:** `templates/components/modals/confirm_modal.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `modal_id` | string | - | Modal DOM ID |
| `title` | string | - | Modal title |
| `message` | string | - | Confirmation message |
| `confirm_text` | string | "بله، حذف کن" | Confirm button text |
| `cancel_text` | string | "انصراف" | Cancel button text |
| `confirm_action` | string | - | URL for confirm action |
| `confirm_class` | string | "btn-danger" | Confirm button style |

**Usage Example:**

```django
{% include 'components/modals/confirm_modal.html' with 
    modal_id='deleteModal' 
    title='حذف آیتم' 
    message='آیا از حذف این آیتم اطمینان دارید؟' 
    confirm_action=delete_url 
%}
```

**Responsive Behavior:** Responsive dialog sizing.

**Dependencies:** Bootstrap modal classes, Bootstrap JS.

---

### Loading

#### `components/loading/loading_overlay.html`

**Purpose:** Loading spinner overlay.

**Path:** `templates/components/loading/loading_overlay.html`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `show` | boolean | true | Show/hide overlay |
| `size` | string | "3rem" | Spinner size (CSS value) |
| `message` | string | - | Screen reader text |

**Usage Example:**

```django
{% include 'components/loading/loading_overlay.html' with 
    show=true 
    size='3rem' 
    message='در حال بارگذاری...' 
%}
```

**Responsive Behavior:** Fixed overlay, centered spinner.

**Dependencies:** Bootstrap spinner classes (`spinner-border`).

---

## Migration Examples

### Example 1: Empty State (home.html)

**Before:**
```django
<div class="text-center py-16">
    <div class="w-24 h-24 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg class="w-12 h-12 text-stone-400">...</svg>
    </div>
    <p class="text-stone-500 text-lg mb-4">هنوز محصولی اضافه نشده است.</p>
    <a href="{% url 'catalog:product_list' %}" class="btn-primary">
        مشاهده همه محصولات
    </a>
</div>
```

**After:**
```django
{% url 'catalog:product_list' as product_list_url %}
{% include 'components/feedback/empty_state.html' with 
    icon_svg='<svg class="w-12 h-12 text-stone-400">...</svg>' 
    message='هنوز محصولی اضافه نشده است.' 
    action_url=product_list_url 
    action_text='مشاهده همه محصولات' 
%}
```

---

### Example 2: Dashboard Quick Links (production/dashboard.html)

**Before:**
```django
{% block extra_css %}
<style>
    .quick-link-card { background: #fff; border-radius: 18px; ... }
    .quick-link-icon { font-size: 2.4rem; color: #2563eb; }
</style>
{% endblock %}

<div class="col-6 col-md-3">
    <a href="{% url 'order_list' %}" class="quick-link-card">
        <div class="quick-link-icon"><i class="bi bi-list-ul"></i></div>
        <h6 class="fw-bold">لیست سفارشات</h6>
    </a>
</div>
```

**After:**
```django
{% url 'order_list' as order_list_url %}
{% include 'components/cards/quick_link_card.html' with 
    icon='list-ul' 
    title='لیست سفارشات' 
    href=order_list_url 
%}
```

CSS extracted to `static/css/dashboard.css`.

---

### Example 3: Form Fields (production/orders/create_step1.html)

**Before:**
```django
<div class="row mb-3">
    <div class="col-md-6">
        {{ form.new_customer_name.label_tag }}
        {{ form.new_customer_name }}
    </div>
</div>
```

**After:**
```django
<div class="row mb-3">
    <div class="col-md-6">
        {% include 'components/forms/form_field.html' with field=form.new_customer_name %}
    </div>
</div>
```

---

## Best Practices

1. **Preserve existing behavior:** Never change business logic when replacing markup with components.
2. **Use `{% url ... as ... %}` for URLs:** Django templates don't support `url()` function in include statements.
3. **Keep Alpine/HTMX intact:** Components should not interfere with existing JavaScript behavior.
4. **Test after each migration:** Validate template compilation and page rendering.
5. **Document parameters:** Every component should have clear parameter documentation.

---

## Related Files

- `LAYOUT_ARCHITECTURE.md` - Template layout system documentation
- `static/css/dashboard.css` - Dashboard-specific styles
- `static/css/style.css` - Storefront Tailwind design system

---

## Version

- **Phase 3.1:** Initial component library with 25 components
- **Migrated Pages:** home.html, catalog/product_list.html, cart/detail.html, production/dashboard.html, production/orders/create_step1.html
