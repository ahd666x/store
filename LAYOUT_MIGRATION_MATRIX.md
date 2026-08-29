# Layout Migration Matrix

> Analysis of layout inheritance chains and their architectural implications.

---

## Layout Inheritance Tree

```
layouts/store.html (Tailwind + Alpine + HTMX)
├── base.html
│   ├── home.html
│   ├── catalog/*.html
│   ├── cart/*.html
│   ├── account/*.html
│   ├── order/*.html
│   ├── payment/*.html
│   ├── discount/*.html
│   └── notification_list.html

layouts/dashboard.html (Bootstrap + jQuery + Alpine)
├── production/base.html
│   ├── production/dashboard.html
│   ├── production/order_list.html
│   ├── production/order_item.html
│   ├── production/kanban.html
│   ├── production/scan_part.html
│   ├── production/worker_list.html
│   ├── production/product_bom_edit.html
│   ├── production/product_create.html
│   ├── production/create_order.html
│   ├── production/create_complete.html
│   ├── production/create_unified.html
│   ├── production/order_print.html
│   ├── production/report.html
│   ├── production/orders/*.html
│   ├── production/set_plate.html
│   ├── production/scan_packaging_unit.html
│   ├── production/select_shipment.html
│   ├── production/print.html
│   ├── production/admin_product_list.html
│   ├── production/admin_order_edit.html
│   ├── production/admin_edit_order_item.html
│   ├── production/admin_order_tasks.html
│   ├── production/admin_tasks_management.html
│   ├── production/item.html
│   └── production/import_data.html
│
├── production/base_shop.html
│   └── (shop-specific production pages)
│
└── production/painting_management/base.html
    ├── production/painting_management/dashboard.html
    ├── production/painting_management/schedule.html
    ├── production/painting_management/workers.html
    ├── production/painting_management/ready_list.html
    ├── production/painting_management/assignment_rules.html
    └── production/painting_management/processes.html

layouts/print.html (Minimal + inline)
└── (print-specific templates)
```

---

## Layout Details

### layouts/store.html — GREEN

| Aspect | Details |
|--------|---------|
| **CSS Framework** | Tailwind CSS (compiled to style.css) |
| **JS Framework** | Alpine.js + HTMX |
| **jQuery** | ❌ Not loaded |
| **Bootstrap** | ❌ Not loaded |
| **Icons** | Bootstrap Icons (CDN) |
| **Font** | Vazirmatn (via components.css) |
| **CSS Files** | style.css, components.css, bootstrap-icons.css |
| **JS Files** | alpinejs, htmx, app.js |

**Key characteristics:**
- Full RTL support via Tailwind RTL utilities
- Alpine.js for mobile menu, dropdowns, modals
- HTMX for cart operations, catalog filtering
- CSS custom properties for theming
- Responsive design with Tailwind breakpoints

---

### layouts/dashboard.html — YELLOW

| Aspect | Details |
|--------|---------|
| **CSS Framework** | Bootstrap 5 (RTL) + custom CSS |
| **JS Framework** | Alpine.js + jQuery |
| **jQuery** | ✅ Loaded |
| **Bootstrap** | ✅ Loaded (CSS + JS bundle) |
| **Icons** | Bootstrap Icons (CDN) |
| **Font** | Vazirmatn |
| **CSS Files** | bootstrap.rtl.min.css, bootstrap-icons.css, vazirmatn-fonts.css, dashboard.css, components.css |
| **JS Files** | jquery, bootstrap.bundle, alpinejs, alpine-bootstrap.js, app.js |

**Key characteristics:**
- Bootstrap grid system (`container`, `row`, `col-md-*`)
- Bootstrap components (card, navbar, modal, dropdown, alert)
- jQuery for DOM manipulation and event handling
- Alpine.js for navbar toggle, modal triggers
- Custom dashboard.css overriding Bootstrap variables
- Sidebar navigation with Bootstrap classes

---

### layouts/print.html — YELLOW

| Aspect | Details |
|--------|---------|
| **CSS Framework** | Minimal custom CSS + inline styles |
| **JS Framework** | None |
| **jQuery** | ❌ Not loaded |
| **Bootstrap** | ❌ Not loaded |
| **Icons** | None |
| **CSS Files** | Inline only |
| **JS Files** | None |

**Key characteristics:**
- Stripped-down layout for print output
- `@media print` CSS rules
- No navigation, no footer
- Content block only

---

### base.html — GREEN

| Aspect | Details |
|--------|---------|
| **Extends** | layouts/store.html |
| **Blocks** | content, extra_css, extra_js |
| **Includes** | header.html, footer.html, toast.html |

**Key characteristics:**
- Standard storefront inheritance
- Includes toast notification system
- Loads cart-actions.html for floating cart button

---

### production/base.html — YELLOW

| Aspect | Details |
|--------|---------|
| **Extends** | layouts/dashboard.html |
| **Blocks** | content, extra_css, extra_js, sidebar |
| **Includes** | production navbar |

**Key characteristics:**
- Production-specific navbar with quick links
- Extends dashboard layout with all Bootstrap+jQuery
- Adds production-specific menu items

---

### production/base_shop.html — YELLOW

| Aspect | Details |
|--------|---------|
| **Extends** | layouts/dashboard.html |
| **Blocks** | content, extra_css, extra_js |
| **Includes** | shop-specific navbar |

**Key characteristics:**
- Shop-specific variant of production layout
- Same underlying architecture as production/base.html

---

### production/painting_management/base.html — YELLOW

| Aspect | Details |
|--------|---------|
| **Extends** | layouts/dashboard.html |
| **Blocks** | painting_content, extra_css, extra_js |
| **Includes** | painting-specific sidebar |

**Key characteristics:**
- Painting-specific navigation
- Loads additional painting.css
- Same Bootstrap+jQuery foundation

---

## Layout Migration Blockers

| Layout | Blocker | Impact |
|--------|---------|--------|
| dashboard.html | jQuery + Bootstrap bundle required by 25+ templates | Cannot remove until all child templates migrated |
| dashboard.html | Select2 CSS/JS loaded for worker pages | Blocks jQuery removal |
| dashboard.html | bootstrap.Modal/Tooltip used in production JS | Blocks Bootstrap JS removal |
| painting_management/base.html | Custom painting.css (~300+ lines) | Must be converted to Tailwind |
| print.html | Inline styles in child templates | Must be extracted to CSS |

---

## Migration Path for Layouts

### Phase 1: Storefront (Already GREEN)
- No action needed. Storefront is fully migrated.

### Phase 2: Production Dashboard
1. Create new `layouts/dashboard_v2.html` based on Tailwind
2. Migrate production templates one by one
3. Remove jQuery and Bootstrap dependencies
4. Replace Select2 with Alpine.js combobox
5. Replace bootstrap.Modal with Alpine modal component

### Phase 3: Painting Management
1. Convert `pages/painting.css` to Tailwind utilities
2. Migrate painting templates to new dashboard layout
3. Remove painting-specific base template

### Phase 4: Print Templates
1. Create Tailwind-based print layout
2. Migrate print templates
3. Remove old print layout

---

## CSS Delivery by Layout

| Layout | CSS Files Delivered |
|--------|---------------------|
| store.html | style.css (Tailwind), components.css, bootstrap-icons.css |
| dashboard.html | bootstrap.rtl.min.css, bootstrap-icons.css, vazirmatn-fonts.css, dashboard.css, components.css |
| print.html | (inline only) |
| painting_management/base.html | All dashboard CSS + pages/painting.css |

---

## JS Delivery by Layout

| Layout | JS Files Delivered |
|--------|-------------------|
| store.html | alpinejs, htmx, app.js |
| dashboard.html | jquery, bootstrap.bundle, alpinejs, alpine-bootstrap.js, app.js |
| print.html | (none) |
| painting_management/base.html | All dashboard JS + painting/*.js modules |
