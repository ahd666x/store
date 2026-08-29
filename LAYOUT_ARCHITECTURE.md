# Layout Architecture

## Overview

This document defines the Django template layout hierarchy for the سلوی چوب / دکارو project.

## Directory Structure

```
templates/
├── layouts/
│   ├── store.html       # Public storefront & customer pages
│   ├── dashboard.html   # Production & management interfaces
│   └── print.html       # Print-optimized documents
├── base.html            # Thin wrapper → layouts/store.html
├── home.html            # Directly extends layouts/store.html
├── catalog/
│   └── product_list.html # Directly extends layouts/store.html
├── production/
│   ├── base.html        # Extends layouts/dashboard.html
│   ├── base_shop.html   # Extends layouts/dashboard.html
│   ├── painting_management/
│   │   └── base.html    # Extends layouts/dashboard.html
│   ├── dashboard.html   # Extends production/base.html
│   ├── order_list.html  # Extends production/base.html
│   └── ...
└── ...
```

## Layouts

### 1. layouts/store.html

**Purpose:** Public storefront, customer-facing catalog, cart, checkout, and account pages.

**Brand:** دکارو

**Style System:** Tailwind CSS

**Includes:**
- `includes/header.html` — Sticky top navigation with search, cart count, user menu
- `includes/footer.html` — Multi-column footer with links, social media, contact info
- `includes/toast.html` — HTMX toast message container
- `includes/cart-actions.html` — Cart side-panel actions

**Available Blocks:**

| Block | Purpose | Required |
|-------|---------|----------|
| `title` | Page `<title>` | No (default: "دکارو") |
| `meta_description` | SEO description meta tag | No |
| `og_title` | Open Graph title | No |
| `og_description` | Open Graph description | No |
| `og_image` | Open Graph image URL | No |
| `twitter_title` | Twitter Card title | No |
| `twitter_description` | Twitter Card description | No |
| `twitter_image` | Twitter Card image URL | No |
| `extra_head` | Extra `<head>` content (styles, meta) | No |
| `breadcrumb` | Breadcrumb navigation HTML | No |
| `breadcrumb_schema` | Schema.org JSON-LD for breadcrumbs | No |
| `content` | Main page content | Yes |
| `extra_js` | Extra JavaScript before `</body>` | No |

**Scripts Loaded:**
- Alpine.js (deferred)
- HTMX
- HTMX CSRF configuration

**When to Use:**
- Home page
- Product catalog and detail pages
- Category pages
- Cart and checkout flows
- Customer account pages (profile, wishlist, order history)
- Authentication pages (login, register, password reset)
- Payment pages
- Discount pages
- Communication/notification pages
- Return request pages
- Any page that should share the public storefront chrome

**Migration Status:**
- `base.html` → thin wrapper extending `layouts/store.html` (backward compatible)
- `home.html` → directly extends `layouts/store.html`
- `catalog/product_list.html` → directly extends `layouts/store.html`
- Remaining store pages continue to extend `base.html` (which extends `layouts/store.html`)

---

### 2. layouts/dashboard.html

**Purpose:** Production, operational, management, and worker interfaces.

**Brand:** سلوی چوب

**Style System:** Bootstrap 5 RTL + Bootstrap Icons + Vazirmatn font

**Includes:**
- No fixed header/footer (provided by child templates via blocks)
- Messages area is built into the layout

**Available Blocks:**

| Block | Purpose | Required |
|-------|---------|----------|
| `title` | Page `<title>` | No (default: "سلوی چوب") |
| `extra_css` | Extra CSS in `<head>` | No |
| `navbar` | Top navigation bar HTML | Yes (for most pages) |
| `content` | Main page content | Yes |
| `painting_content` | Painting management content wrapper | No (alias for `content`) |
| `footer` | Page footer HTML | No |
| `extra_js` | Extra JavaScript before `</body>` | No |

**Scripts Loaded:**
- Bootstrap 5 Bundle (RTL)
- jQuery 3.7.1

**Special Behavior:**
- `painting_content` block wraps `content` by default. This allows painting management pages to continue using `painting_content` while other pages use `content`.
- Messages (`django.contrib.messages`) are rendered automatically at the top of `<body>`.

**When to Use:**
- Production dashboard
- Order management (list, detail, create, edit)
- Product management (list, create, edit, BOM)
- Worker management
- Task list and kanban board
- Production reports (workers, stages, orders, delayed, shipped)
- Scanning interfaces (part scan, packaging scan)
- Shipping and plate management
- Data import/export
- Painting management (schedule, processes, stages, workers, ready list)
- Management interfaces (admin order edit, task management)
- Any operational interface that requires the production chrome

**Child Templates:**

| Template | Extends | Notes |
|----------|---------|-------|
| `production/base.html` | `layouts/dashboard.html` | Production navbar with nav links, user badge |
| `production/base_shop.html` | `layouts/dashboard.html` | Customer shop navbar, footer |
| `production/painting_management/base.html` | `layouts/dashboard.html` | Custom header-nav, `painting_content` wrapper |
| 36 production pages | `production/base.html` | Order management, workers, tasks, reports, etc. |
| 13 customer shop pages | `production/base_shop.html` | Shop, cart, checkout, customer orders, shipments |
| 9 painting management pages | `painting_management/base.html` | Workers, schedule, processes, stages, etc. |

**Migration Status:**
- Fixed pages that incorrectly extended `base.html` (store layout) to extend `production/base.html`:
  - `production/worker_list.html`
  - `production/kanban.html`
  - `production/task_list.html`
  - `production/report.html`
  - `production/lable_part.html`
  - `production/holiday_list.html`
  - `production/painting_process_list.html`

---

### 3. layouts/print.html

**Purpose:** Print-optimized documents including invoices, production forms, labels, barcode/QR pages, and reports intended for printing.

**Style System:** None (child templates provide all print-specific CSS inline)

**Available Blocks:**

| Block | Purpose | Required |
|-------|---------|----------|
| `title` | Document title | No |
| `extra_css` | Print-specific CSS | No (but typically used) |
| `content` | Document body content | Yes |

**When to Use:**
- A4/A5 production documents
- Invoices (pre-invoices, final invoices)
- Production forms (per-item production sheets)
- Barcode/QR label pages
- Packaging labels
- Combined print pages (order summary + production sheets + labels)
- Daily schedule printouts
- Shipped units reports

**Migration Status:**
- `production/print.html` → extends `layouts/print.html`
- `production/order_print.html` → extends `layouts/print.html`
- `production/order_invoice.html` → extends `layouts/print.html`
- Other print templates remain standalone (intentionally not migrated yet)

---

## Inheritance Rules

1. **Store pages** should extend `layouts/store.html` directly, or extend `base.html` (which extends `layouts/store.html`).
2. **Dashboard/production pages** should extend `production/base.html` (which extends `layouts/dashboard.html`).
3. **Customer shop pages** extend `production/base_shop.html` (which extends `layouts/dashboard.html`).
4. **Painting management pages** extend `production/painting_management/base.html` (which extends `layouts/dashboard.html`).
5. **Print documents** should extend `layouts/print.html`.
6. **Never** extend `base.html` for production/management pages. The store layout has a different brand, style system, and chrome.

## Block Resolution

Django resolves blocks by searching the template inheritance chain from child to parent. With the new hierarchy:

```
child.html
  → production/base.html
    → layouts/dashboard.html
      → (Bootstrap CSS, jQuery, messages, content block)
```

A `content` block defined in `child.html` overrides the `content` block in `layouts/dashboard.html`, regardless of intermediate templates.

For `painting_content`:
- `layouts/dashboard.html` defines: `{% block painting_content %}{% block content %}{% endblock %}{% endblock %}`
- `painting_management/base.html` overrides: `{% block painting_content %}<div class="fade-in">{% block content %}{% endblock %}</div>{% endblock %}`
- Painting pages define either `painting_content` or `content` and it resolves correctly.

## Shared Includes

| Include | Used By | Purpose |
|---------|---------|---------|
| `includes/header.html` | `layouts/store.html` | Store top navigation |
| `includes/footer.html` | `layouts/store.html` | Store footer |
| `includes/toast.html` | `layouts/store.html` | HTMX toast notifications |
| `includes/cart-actions.html` | `layouts/store.html` | Cart slide-out panel |
| `includes/icons.html` | `includes/header.html` | SVG icon partial |

## Responsive Behavior

### Store Layout
- Mobile: Hamburger menu, mobile search, mobile cart icon
- Tablet/Desktop: Full navigation, search bar, user dropdown
- RTL-aware with logical CSS properties

### Dashboard Layout
- Bootstrap responsive grid (`container-fluid`, `row`, `col-*`)
- Collapsible navbar (Bootstrap navbar-toggler)
- Painting management: Responsive header-nav with flex-wrap

### Print Layout
- No responsive concerns (print media only)
- Child templates define `@media print` rules

## RTL Support

All layouts use `<html dir="rtl" lang="fa">`. The store layout uses Tailwind's RTL-aware utilities (e.g., `me-*`, `ms-*`, `border-s`, `border-e`). The dashboard layout uses Bootstrap RTL (`bootstrap.rtl.min.css`).

## Authentication States

### Store Layout
- **Anonymous:** Shows login/register buttons in header
- **Authenticated:** Shows user menu dropdown with profile, return requests, logout
- Cart count badge updates via HTMX

### Dashboard Layout
- **Anonymous:** Shows login button in navbar
- **Authenticated:** Shows username badge, admin panel link (if staff), logout button
- Customer shop layout shows customer-specific nav links when authenticated

## Technical Debt

1. **Customer shop pages** (`base_shop.html` and 13 child templates) currently use Bootstrap RTL under `layouts/dashboard.html`. In a future phase, these could be migrated to `layouts/store.html` for a unified customer experience, but this requires careful design alignment.
2. **Print templates** (`order_combined_print.html`, `daily_schedule_print.html`, `reports/shipped.html`) remain standalone. They should be migrated to `layouts/print.html` in a follow-up.
3. **Inline CSS** in `production/base.html`, `production/base_shop.html`, and `painting_management/base.html` could be extracted into dedicated CSS files in a future phase.
4. **`base.html` wrapper** is kept for backward compatibility. Once all store pages migrate directly to `layouts/store.html`, `base.html` can be removed.
