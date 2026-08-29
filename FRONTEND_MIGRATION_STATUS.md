# FRONTEND_MIGRATION_STATUS
## سلوی چوب (Selvi Wood) - Migration Readiness Audit

**Audit Date:** 2026-08-29  
**Repository:** https://github.com/ahd666x/store  
**Phases Completed:** 0-5  
**Phase:** 6 Execution (Week 1: Critical Bug Fixes + Foundation)  

---

## 1. EXECUTIVE SUMMARY

Phases 0-5 have modernized the storefront (shop) templates to a fully Tailwind + Alpine.js + HTMX architecture. However, the admin/production panel remains on a **hybrid Bootstrap + Tailwind** architecture with significant inline CSS and JS debt.

### Key Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Total templates | 102 | - |
| GREEN (migrated) | 44 (43%) | 100% |
| YELLOW (partial) | 38 (37%) | 0% |
| RED (legacy) | 20 (20%) | 0% |
| Bootstrap CSS loaded | 1 layout (`dashboard.html`) | 0 |
| Bootstrap JS loaded | 0 templates | 0 |
| jQuery loaded | 0 templates | 0 |
| Select2 loaded | 1 template (broken without jQuery) | 0 |
| Inline CSS blocks | ~15 templates | 0 |
| Inline JS blocks | ~20 templates | 0 |
| CSS files | 9 | 5-7 |
| JS modules | 13 (+ 6 vendor) | 5-7 |

### Critical Finding

**Bootstrap JS is NOT loaded anywhere**, yet 4 painting management templates use `bootstrap.Modal()` and `data-bs-toggle` attributes. These modals are **non-functional**. Additionally, Select2 is loaded in `workers.html` but jQuery is not loaded anywhere, making Select2 **non-functional**.

---

## 2. CURRENT STATE ANALYSIS

### 2.1 Layouts

| Layout | Path | Status | Tech Stack |
|--------|------|--------|------------|
| Store | `layouts/store.html` | **GREEN** | Tailwind, Alpine.js, HTMX, no Bootstrap, no jQuery |
| Dashboard | `layouts/dashboard.html` | **YELLOW** | Bootstrap CSS (`bootstrap.rtl.min.css`, `bootstrap-icons.css`), Alpine.js, app.js |
| Print | `layouts/print.html` | **GREEN** | Minimal, no dependencies |

### 2.2 Base Templates

| Base | Extends | Status | Notes |
|------|---------|--------|-------|
| `base.html` | `layouts/store.html` | **GREEN** | Pass-through |
| `production/base.html` | `layouts/dashboard.html` | **YELLOW** | Bootstrap navbar classes, Alpine mobile toggle |
| `production/base_shop.html` | `layouts/dashboard.html` | **YELLOW** | Bootstrap navbar classes, inline CSS in extra_css |
| `painting_management/base.html` | `layouts/dashboard.html` | **YELLOW** | Loads `painting.css`, custom header nav |

### 2.3 Technology Usage Summary

| Technology | Vendor Files | Loaded In Templates | Used By |
|------------|-------------|---------------------|---------|
| Tailwind CSS | `style.css` (compiled, 1248 lines) | All storefront + admin | All templates |
| Alpine.js | `vendor/alpinejs.min.js` | `store.html`, `dashboard.html` | Mobile menus, dropdowns, toasts, tabs |
| HTMX | `vendor/htmx.min.js` | `store.html` | Cart actions, partial updates |
| Bootstrap CSS | `vendor/bootstrap.rtl.min.css` | `dashboard.html` only | Admin panel |
| Bootstrap Icons | `vendor/bootstrap-icons.css` | `dashboard.html` only | Admin panel icons |
| Bootstrap JS | `vendor/bootstrap.bundle.min.js` | **NOWHERE** | **BROKEN** - painting modals |
| jQuery | `vendor/jquery-3.7.1.min.js` | **NOWHERE** | **BROKEN** - Select2 init in app.js |
| Select2 | `vendor/select2.min.js` | `workers.html` only | Worker exclusion modals |
| Custom CSS | `components.css` (136 lines), `dashboard.css` (23 lines), `product-grid.css` (16 lines), `pages/painting.css` | Various | Component overrides, painting pages |

---

## 3. PER-TEMPLATE MIGRATION MATRIX

### 3.1 Storefront Templates (extends `base.html` → `layouts/store.html`)

| Template | Layout | Bootstrap | jQuery | Inline CSS | Inline JS | Components Used | Status | Complexity | Risk |
|----------|--------|-----------|--------|------------|-----------|-----------------|--------|------------|------|
| `home.html` | store | None | None | None | None | product_card, empty_state | **GREEN** | Low | Low |
| `catalog/product_list.html` | store | None | None | None | None | product_card, empty_state | **GREEN** | Low | Low |
| `catalog/product_detail.html` | store | None | None | ~10 lines | None | breadcrumb | **GREEN** | Low | Low |
| `catalog/category_list.html` | store | None | None | None | None | product_card | **GREEN** | Low | Low |
| `catalog/category_detail.html` | store | None | None | None | None | product_card | **GREEN** | Low | Low |
| `catalog/stock_alerts.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `catalog/comparison.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `cart/detail.html` | store | None | None | None | None | empty_state | **GREEN** | Low | Low |
| `accounts/login.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `accounts/register.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `accounts/otp_verify.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `accounts/otp_request.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `accounts/profile.html` | store | None | None | None | None | status_badge | **GREEN** | Low | Low |
| `accounts/profile_edit.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `accounts/wishlist.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `accounts/password_reset.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `accounts/password_reset_done.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `accounts/password_reset_complete.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `accounts/password_reset_confirm.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `orders/order_list.html` | store | None | None | None | None | status_badge | **GREEN** | Low | Low |
| `orders/order_detail.html` | store | None | None | None | None | status_badge, order_items | **GREEN** | Low | Low |
| `orders/order_form.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `orders/order_confirm.html` | store | None | None | None | None | order_items | **GREEN** | Low | Low |
| `orders/return_request_list.html` | store | None | None | None | None | return_status_badge | **GREEN** | Low | Low |
| `orders/return_request_form.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `orders/return_request_detail.html` | store | None | None | None | None | return_status_badge | **GREEN** | Low | Low |
| `payments/payment_create.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `payments/payment_error.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `discounts/discount_list.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `discounts/discount_form.html` | store | None | None | None | None | - | **GREEN** | Low | Low |
| `communications/notification_list.html` | store | None | None | None | None | - | **GREEN** | Low | Low |

### 3.2 Production Admin Templates (extends `production/base.html` → `layouts/dashboard.html`)

| Template | Bootstrap CSS | jQuery | Inline CSS | Inline JS | Bootstrap JS Needed? | Status | Complexity | Risk |
|----------|--------------|--------|------------|-----------|---------------------|--------|------------|------|
| `production/dashboard.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `production/order_list.html` | Yes | None | None | Yes | No | **YELLOW** | Medium | Low |
| `production/order_item.html` | Yes | None | None | Yes | No | **YELLOW** | Medium | Low |
| `production/admin_product_list.html` | Yes | None | Yes | None | No | **YELLOW** | Low | Low |
| `production/product_create.html` | Yes | None | Yes | None | Yes (Bootstrap Modal) | **YELLOW** | Medium | Medium |
| `production/product_bom_edit.html` | Yes | None | Yes | Yes | No | **YELLOW** | Medium | Low |
| `production/admin_order_edit.html` | Yes | None | Yes | None | No | **YELLOW** | Medium | Low |
| `production/admin_edit_order_item.html` | Yes | None | None | Yes | No | **YELLOW** | Medium | Low |
| `production/admin_order_tasks.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `production/task_list.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `production/worker_list.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `production/kanban.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `production/item.html` | Yes | None | Yes | None | No | **YELLOW** | Medium | Low |
| `production/scan_part.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `production/scan_packaging_unit.html` | Yes | None | Yes | None | No | **YELLOW** | Medium | Low |
| `production/create_unified.html` | Yes | None | None | Yes | No | **YELLOW** | Medium | Low |
| `production/orders/create_step1.html` | Yes | None | None | Yes | No | **YELLOW** | Medium | Low |
| `production/orders/create_step2.html` | Yes | None | Yes | Yes | No | **YELLOW** | Medium | Low |
| `production/orders/order_detail.html` | Yes | None | Yes | None | No | **YELLOW** | Medium | Low |
| `production/orders/add_item.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `production/orders/add_colors.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `production/import_data.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `production/upload.html` | No | None | None | None | No | **RED** | Low | Low |
| `production/test.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `production/create_order.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `production/create_complete.html` | Yes | None | Yes | None | No | **YELLOW** | Medium | Low |
| `production/set_plate.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `production/select_shipment.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `production/reports/stages.html` | Yes | None | Yes | Yes | No | **YELLOW** | High | Low |
| `production/reports/workers.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `production/reports/orders.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `production/reports/delayed.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |

### 3.3 Production Customer Shop Templates (extends `base_shop.html` → `layouts/dashboard.html`)

| Template | Bootstrap CSS | jQuery | Inline CSS | Inline JS | Status | Complexity | Risk |
|----------|--------------|--------|------------|-----------|--------|------------|------|
| `production/shop/product_list.html` | Yes | None | Yes | None | **YELLOW** | Medium | Low |
| `production/shop/product_detail.html` | Yes | None | Yes | Yes | **YELLOW** | Medium | Low |
| `production/shop/cart.html` | Yes | None | Yes | None | **YELLOW** | Medium | Low |
| `production/shop/checkout.html` | Yes | None | Yes | None | **YELLOW** | Medium | Low |
| `production/shop/order_tracking.html` | Yes | None | Yes | None | **YELLOW** | Medium | Low |
| `production/shop/order_history.html` | Yes | None | None | None | **YELLOW** | Low | Low |

### 3.4 Production Customer Order Templates (extends `base_shop.html`)

| Template | Bootstrap CSS | jQuery | Inline CSS | Inline JS | Status | Complexity | Risk |
|----------|--------------|--------|------------|-----------|--------|------------|------|
| `production/customer/step1.html` | Yes | None | None | None | **YELLOW** | Low | Low |
| `production/customer/step2.html` | Yes | None | None | Yes | **YELLOW** | Low | Low |
| `production/customer/order_list.html` | Yes | None | Yes | None | **YELLOW** | Medium | Low |
| `production/customer/order_detail.html` | Yes | None | Yes | Yes | **YELLOW** | Medium | Low |
| `production/customer/edit_order_item.html` | Yes | None | None | None | **YELLOW** | Low | Low |
| `production/customer/shipments.html` | Yes | None | Yes | None | **YELLOW** | Medium | Low |
| `production/customer/shipment_detail.html` | Yes | None | Yes | None | **YELLOW** | Medium | Low |

### 3.5 Painting Management Templates (extends `painting_management/base.html`)

| Template | Bootstrap CSS | jQuery | Inline CSS | Inline JS | Bootstrap JS | Status | Complexity | Risk |
|----------|--------------|--------|------------|-----------|--------------|--------|------------|------|
| `painting_management/dashboard.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |
| `painting_management/processes.html` | Yes | None | None | Yes | **Yes (BROKEN)** | **YELLOW** | Medium | **HIGH** |
| `painting_management/stages.html` | Yes | None | None | Yes | **Yes (BROKEN)** | **YELLOW** | Medium | **HIGH** |
| `painting_management/workers.html` | Yes | None | Yes | Yes | **Yes (BROKEN)** | **YELLOW** | Very High | **HIGH** |
| `painting_management/schedule.html` | Yes | None | Yes | None | No | **YELLOW** | High | Low |
| `painting_management/ready_list.html` | Yes | None | Yes | Yes | No | **YELLOW** | High | Low |
| `painting_management/assignment_rules.html` | Yes | None | None | Yes | **Yes (BROKEN)** | **YELLOW** | Medium | **HIGH** |
| `painting_management/holidays.html` | Yes | None | None | Yes | Yes | **YELLOW** | Medium | **HIGH** |
| `painting_management/_nav.html` | Yes | None | None | None | No | **YELLOW** | Low | Low |

### 3.6 Print / Report Templates

| Template | Bootstrap | jQuery | Inline CSS | Inline JS | Status | Complexity | Risk |
|----------|-----------|--------|------------|-----------|--------|------------|------|
| `production/print.html` | No | None | Yes | None | **RED** | Low | Low |
| `production/order_print.html` | No | None | Yes | None | **RED** | Low | Low |
| `production/order_combined_print.html` | No | None | Yes | None | **RED** | Medium | Low |
| `production/order_invoice.html` | No | None | Yes | None | **RED** | Low | Low |
| `production/daily_schedule_print.html` | No | None | Yes | Yes | **RED** | Medium | Low |
| `production/print_lable.html` | No | None | Yes | None | **RED** | Low | Low |
| `production/print_lable_part.html` | No | None | Yes | None | **RED** | Low | Low |
| `production/reports/shipped.html` | No | None | None | None | **RED** | Low | Low |
| `production/reports/delivery_note.html` | No | None | Yes | None | **RED** | Low | Low |
| `production/lable_part.html` | Yes | None | Yes | None | **RED** | Medium | Low |

### 3.7 Component Templates

| Component | Bootstrap | jQuery | Inline CSS | Inline JS | Status | Complexity | Risk |
|-----------|-----------|--------|------------|-----------|--------|------------|------|
| `components/tables/table.html` | Yes | None | None | None | **YELLOW** | Low | Low |
| `components/tables/pagination.html` | Yes | None | None | None | **YELLOW** | Low | Low |
| `components/cards/card.html` | No | None | None | None | **GREEN** | Low | Low |
| `components/cards/stat_card.html` | No | None | None | None | **GREEN** | Low | Low |
| `components/cards/quick_link_card.html` | No | None | None | None | **GREEN** | Low | Low |
| `components/forms/form_field.html` | No | None | None | None | **GREEN** | Low | Low |
| `components/forms/input.html` | No | None | None | None | **GREEN** | Low | Low |
| `components/forms/select.html` | No | None | None | None | **GREEN** | Low | Low |
| `components/forms/textarea.html` | No | None | None | None | **GREEN** | Low | Low |
| `components/forms/search.html` | No | None | None | None | **GREEN** | Low | Low |
| `components/forms/checkbox.html` | No | None | None | None | **GREEN** | Low | Low |
| `components/modals/modal.html` | Yes | None | None | None | **YELLOW** | Medium | Low |
| `components/modals/confirm_modal.html` | Yes | None | None | None | **YELLOW** | Low | Low |
| `components/data/status_badge.html` | Yes | None | None | None | **YELLOW** | Low | Low |
| `components/data/badge.html` | Yes | None | None | None | **YELLOW** | Low | Low |
| `components/data/price.html` | No | None | None | None | **GREEN** | Low | Low |
| `components/data/date.html` | No | None | None | None | **GREEN** | Low | Low |
| `components/feedback/alert.html` | Yes | None | None | None | **YELLOW** | Low | Low |
| `components/feedback/empty_state.html` | No | None | None | None | **GREEN** | Low | Low |
| `components/loading/loading_overlay.html` | Yes | None | None | None | **YELLOW** | Low | Low |
| `components/navigation/header.html` | No | None | None | None | **GREEN** | Low | Low |
| `components/navigation/breadcrumb.html` | No | None | None | None | **GREEN** | Low | Low |

---

## 4. COMPONENT DEPENDENCY ANALYSIS

### 4.1 Components Still Depending on Bootstrap

These components use Bootstrap CSS classes and need Tailwind equivalents:

| Component | Bootstrap Classes Used | Tailwind Equivalent Available? |
|-----------|----------------------|-------------------------------|
| `components/tables/table.html` | `table`, `table-hover`, `table-dark` | Yes (`table-modern`) |
| `components/tables/pagination.html` | `pagination`, `page-item`, `page-link` | Partial |
| `components/modals/modal.html` | `modal`, `modal-dialog`, `modal-content`, `modal-header`, `modal-body`, `modal-footer`, `btn-close` | Partial (needs Alpine modal) |
| `components/modals/confirm_modal.html` | Same as above | Partial |
| `components/data/status_badge.html` | `badge`, `badge-success`, `badge-info`, `badge-warning`, `badge-danger` | Yes (`badge` in tailwind-input.css) |
| `components/data/badge.html` | `badge`, `badge-sm`, `badge-lg` | Yes |
| `components/feedback/alert.html` | `alert`, `alert-success`, `alert-danger`, `alert-warning`, `alert-info`, `alert-dismissible` | Partial |
| `components/loading/loading_overlay.html` | `spinner-border` | Partial (needs custom CSS) |

### 4.2 Components Fully Migrated

These components use only Tailwind utilities:

| Component | Notes |
|-----------|-------|
| `components/cards/card.html` | Tailwind only |
| `components/cards/stat_card.html` | Tailwind only |
| `components/cards/quick_link_card.html` | Tailwind only |
| `components/forms/form_field.html` | Tailwind only |
| `components/forms/input.html` | Tailwind only |
| `components/forms/select.html` | Tailwind only |
| `components/forms/textarea.html` | Tailwind only |
| `components/forms/search.html` | Tailwind only |
| `components/forms/checkbox.html` | Tailwind only |
| `components/data/price.html` | Tailwind only |
| `components/data/date.html` | Tailwind only |
| `components/feedback/empty_state.html` | Tailwind only |
| `components/navigation/header.html` | Tailwind + Alpine |
| `components/navigation/breadcrumb.html` | Tailwind only |

---

## 5. CSS FILES CLEANUP TARGETS

### 5.1 Current CSS Files

| File | Lines | Purpose | Target |
|------|-------|---------|--------|
| `static/css/style.css` | 1 | Compiled Tailwind output | **KEEP** - single source of truth |
| `static/css/tailwind-input.css` | 1248 | Tailwind source + @layer components | **KEEP** - rebuild target |
| `static/css/components.css` | 136 | Shared component overrides | **CONSOLIDATE** into tailwind-input.css |
| `static/css/dashboard.css` | 23 | Dashboard quick-link-card | **CONSOLIDATE** into tailwind-input.css |
| `static/css/product-grid.css` | 16 | Product grid utilities | **CONSOLIDATE** into tailwind-input.css |
| `static/css/vendor/bootstrap.rtl.min.css` | - | Bootstrap RTL | **REMOVE** after admin migration |
| `static/css/vendor/bootstrap-icons.css` | - | Bootstrap Icons | **REMOVE** after admin migration |
| `static/css/vendor/select2.min.css` | - | Select2 | **REMOVE** after Select2 removal |
| `static/css/vendor/select2-bootstrap-5-theme.min.css` | - | Select2 theme | **REMOVE** after Select2 removal |
| `static/css/vazirmatn-fonts.css` | - | Font faces | **KEEP** |
| `static/css/pages/painting.css` | - | Painting page styles | **CONSOLIDATE** into tailwind-input.css |
| `static/css/pages/shipped.css` | - | Shipped report styles | **CONSOLIDATE** into tailwind-input.css |

### 5.2 CSS Cleanup Priority

1. **High Priority:** `components.css` (136 lines) - Contains `.navbar-custom`, `.product-card`, `.clickable-row`, `.form-section`, `.shop-navbar`, `.shop-footer`. These are used by admin templates.
2. **Medium Priority:** `dashboard.css` (23 lines) - `.quick-link-card` used by dashboard.
3. **Low Priority:** `product-grid.css` (16 lines) - Grid utilities.
4. **After Admin Migration:** Remove `bootstrap.rtl.min.css`, `bootstrap-icons.css`, `select2*.css`.

---

## 6. JS MODULES STATUS

### 6.1 Modular JS (Phase 5 Created)

| Module | Lines | Purpose | Used By | Status |
|--------|-------|---------|---------|--------|
| `static/js/app.js` | 94 | Main entry point, initializes all modules | All pages via base templates | **GLOBAL** - needs lazy loading |
| `static/js/core/csrf.js` | 30 | CSRF token utilities | app.js | Good |
| `static/js/components/toast.js` | 34 | Toast notifications | app.js | Good |
| `static/js/components/loading.js` | 18 | Loading overlays | app.js | Good |
| `static/js/store/cart.js` | 34 | Cart interactions | cart-actions.html | Good |
| `static/js/store/catalog.js` | 95 | Price calc, filters, clickable rows | app.js | Good |
| `static/js/forms/cascade.js` | 44 | Cascading selects | app.js | Good |
| `static/js/forms/colors.js` | 54 | Color field filtering | app.js | Good |
| `static/js/production/scanner.js` | 103 | Barcode scanning | scan_part.html | Good |
| `static/js/production/kanban.js` | 152 | Kanban board drag-drop | schedule.html | Good |
| `static/js/production/workers.js` | 90 | Worker CRUD, exclusion modals | workers.html | Good |
| `static/js/production/bom.js` | 243 | BOM management | product_create.html | Good |

### 6.2 Vendor JS Files

| File | Size | Used By | Status |
|------|------|---------|--------|
| `vendor/alpinejs.min.js` | - | All layouts | **KEEP** |
| `vendor/htmx.min.js` | - | store.html | **KEEP** |
| `vendor/select2.min.js` | - | workers.html | **BROKEN** - no jQuery loaded |
| `vendor/jquery-3.7.1.min.js` | - | **NOWHERE** | **ORPHANED** |
| `vendor/bootstrap.bundle.min.js` | - | **NOWHERE** | **ORPHANED** |

### 6.3 Legacy JS Files (to be removed)

| File | Status | Action |
|------|--------|--------|
| `static/js/jquery-3.6.4.js` | Duplicate | Delete |
| `static/js/jquery-3.6.4.slim.js` | Duplicate | Delete |
| `static/js/jquery-3.6.4.min.js` | Duplicate | Delete |
| `static/js/jquery-3.6.4.slim.min.js` | Duplicate | Delete |
| `static/js/jquery-3.6.4-vsdoc.js` | Duplicate | Delete |
| `static/js/jquery-3.6.4.min.map` | Source map | Delete |
| `static/js/jquery-3.6.4.slim.min.map` | Source map | Delete |
| `static/js/bootstrap.js` | Duplicate | Delete |
| `static/js/bootstrap.min.js` | Duplicate | Delete |
| `static/js/bootstrap.js.map` | Source map | Delete |
| `static/js/bootstrap.min.js.map` | Source map | Delete |
| `static/js/bootstrap.esm.js` | Duplicate | Delete |
| `static/js/bootstrap.esm.min.js` | Duplicate | Delete |
| `static/js/bootstrap.esm.js.map` | Source map | Delete |
| `static/js/bootstrap.esm.min.js.map` | Source map | Delete |
| `static/js/bootstrap.bundle.js` | Duplicate | Delete |
| `static/js/bootstrap.bundle.min.js` | Duplicate | Delete |
| `static/js/bootstrap.bundle.js.map` | Source map | Delete |
| `static/js/bootstrap.bundle.min.js.map` | Source map | Delete |

---

## 7. PAGES REQUIRING SPECIAL CARE

### 7.1 Production-Critical Workflows

These pages handle active business workflows and must maintain 100% uptime:

| Page | Workflow | Risk Level | Notes |
|------|----------|------------|-------|
| `production/scan_part.html` | Barcode scanning, task completion | **HIGH** | Core production workflow |
| `production/scan_packaging_unit.html` | Packaging/shipping | **HIGH** | Uses scanner.js, plate input |
| `production/painting_management/schedule.html` | Daily painting schedule | **HIGH** | Kanban drag-drop, complex JS |
| `production/painting_management/workers.html` | Worker management | **HIGH** | Broken modals, Select2 broken |
| `production/order_list.html` | Order management | **HIGH** | Batch export, task generation |
| `production/admin_order_edit.html` | Order editing | **HIGH** | Item management, cascade selects |
| `production/product_create.html` | Product/BOM creation | **HIGH** | Formset, modals |
| `production/kanban.html` | Production kanban | **MEDIUM** | Visual workflow board |
| `production/item.html` | Item detail, packaging/shipping status | **HIGH** | QR codes, print links |
| `cart/detail.html` | Cart checkout | **HIGH** | Payment flow |

### 7.2 High-Complexity Migrations

| Page | Complexity | Reason |
|------|------------|--------|
| `painting_management/workers.html` | **Very High** | Select2, Bootstrap modals, Bootstrap dropdowns, inline CSS, complex JS |
| `painting_management/schedule.html` | **High** | Kanban CSS (180+ lines), drag-drop, worker columns |
| `painting_management/ready_list.html` | **High** | Inline CSS (176 lines), complex filter logic, inline JS |
| `production/product_create.html` | **High** | BOM formset, part modal, size rule presets, inline CSS |
| `production/create_unified.html` | **High** | Cascade selects, color fields, customer selection |
| `production/admin_order_edit.html` | **High** | Multiple inline sections, item management |
| `production/order_combined_print.html` | **Medium** | Massive inline CSS (350 lines), print-specific |

---

## 8. CRITICAL BUGS IDENTIFIED

### 8.1 Broken Painting Management Modals

**Affected Templates:**
- `painting_management/workers.html`
- `painting_management/stages.html`
- `painting_management/processes.html`
- `painting_management/assignment_rules.html`
- `painting_management/holidays.html`

**Issue:** These templates use Bootstrap modal patterns (`data-bs-toggle="modal"`, `new bootstrap.Modal()`) but Bootstrap JS (`bootstrap.bundle.min.js`) is NOT loaded in any template.

**Impact:** All modals in painting management are non-functional. Worker creation/editing, stage management, process management, assignment rules, and holiday management are all broken.

**Fix Required:** Either load Bootstrap JS in `painting_management/base.html` temporarily or rewrite modals using Alpine.js (preferred for long-term).

### 8.2 Broken Select2 in Workers Page

**Affected Templates:**
- `painting_management/workers.html`

**Issue:** Select2 (`select2.min.js`) is loaded but jQuery (`jquery-3.7.1.min.js`) is NOT loaded anywhere in templates. Select2 requires jQuery.

**Impact:** Worker exclusion modals (product/item exclusions) do not work.

**Fix Required:** Either load jQuery before Select2 temporarily or replace Select2 with a vanilla JS alternative (preferred).

### 8.3 Orphaned Vendor Files

**Files:**
- `static/js/jquery-3.6.4*.js` (6 files + 2 maps)
- `static/js/jquery-3.6.4-vsdoc.js`
- `static/js/bootstrap*.js` (12 files)
- `static/js/jquery-3.6.4.slim.min.map`

**Issue:** These duplicate files exist alongside the vendor versions but are not referenced by any template.

**Action:** Delete all orphaned files.

---

## 9. RECOMMENDED PHASE 6 EXECUTION ORDER

### Phase 6 Goal: Complete Admin Panel Migration

The admin/production panel must be migrated from Bootstrap to Tailwind while maintaining production-critical workflows.

### Execution Order

#### Week 1: Critical Bug Fixes + Foundation

1. **Fix painting management modals (P0)**
   - Load `bootstrap.bundle.min.js` in `painting_management/base.html` temporarily
   - OR rewrite modals using Alpine.js (preferred for long-term)
   - Validate all 5 painting modal templates work

2. **Fix Select2 (P0)**
   - Load jQuery in `painting_management/base.html` temporarily
   - OR replace Select2 with Alpine.js multi-select (preferred)

3. **Remove orphaned vendor files**
   - Delete all duplicate jQuery/Bootstrap JS files
   - Validate no 404s

#### Week 2: Layout Consolidation

4. **Migrate `layouts/dashboard.html`**
   - Remove Bootstrap CSS links
   - Add Tailwind utilities for any Bootstrap-dependent styles
   - Update `components.css` classes to Tailwind

5. **Migrate `production/base.html`**
   - Replace Bootstrap navbar classes with Tailwind
   - Keep Alpine mobile toggle

6. **Migrate `production/base_shop.html`**
   - Replace Bootstrap navbar classes with Tailwind
   - Remove inline CSS from `extra_css`

7. **Migrate `painting_management/base.html`**
   - Remove `painting.css` dependency
   - Migrate custom nav to Tailwind

#### Week 3: Component Library Completion

8. **Migrate Bootstrap-dependent components**
   - `components/tables/table.html` → Tailwind table classes
   - `components/tables/pagination.html` → Tailwind pagination
   - `components/modals/modal.html` → Alpine.js modal
   - `components/data/status_badge.html` → Tailwind badges
   - `components/data/badge.html` → Tailwind badges
   - `components/feedback/alert.html` → Tailwind alerts
   - `components/loading/loading_overlay.html` → Tailwind spinner

9. **Update `orders/includes/status_badge.html`**
   - Replace Bootstrap badge classes with Tailwind

#### Week 4: Low-Risk Admin Templates

10. **Migrate simple admin templates**
    - `production/dashboard.html`
    - `production/task_list.html`
    - `production/worker_list.html`
    - `production/kanban.html`
    - `production/admin_order_tasks.html`
    - `production/reports/workers.html`
    - `production/reports/orders.html`
    - `production/reports/delayed.html`

#### Week 5: Medium-Risk Admin Templates

11. **Migrate order/item templates**
    - `production/order_list.html` (inline JS → module)
    - `production/order_item.html` (inline JS → module)
    - `production/admin_product_list.html` (inline CSS → utility)
    - `production/item.html` (inline CSS → utility)

12. **Migrate report templates**
    - `production/reports/stages.html` (complex inline CSS + JS)

#### Week 6: High-Risk Production Templates

13. **Migrate critical production workflows**
    - `production/scan_part.html` (validate scanner.js)
    - `production/scan_packaging_unit.html` (validate scanner.js)
    - `production/product_create.html` (BOM formset, part modal)
    - `production/product_bom_edit.html` (inline JS for BOM rows)

14. **Migrate order creation flow**
    - `production/create_unified.html`
    - `production/orders/create_step1.html`
    - `production/orders/create_step2.html`
    - `production/orders/order_detail.html`

#### Week 7: High-Risk Admin Edit Templates

15. **Migrate admin edit templates**
    - `production/admin_order_edit.html`
    - `production/admin_edit_order_item.html`

#### Week 8: Painting Management (Highest Complexity)

16. **Migrate painting management templates**
    - `painting_management/processes.html` (fix Bootstrap Modal first)
    - `painting_management/stages.html` (fix Bootstrap Modal first)
    - `painting_management/holidays.html` (fix Bootstrap Modal first)
    - `painting_management/assignment_rules.html` (fix Bootstrap Modal first)
    - `painting_management/workers.html` (fix Bootstrap Modal + Select2 first)
    - `painting_management/schedule.html` (kanban CSS migration)
    - `painting_management/ready_list.html` (inline CSS migration)

#### Week 9: Print Templates + Shop Admin

17. **Migrate print/report templates**
    - `production/print.html`
    - `production/order_print.html`
    - `production/order_combined_print.html`
    - `production/order_invoice.html`
    - `production/daily_schedule_print.html`
    - `production/print_lable.html`
    - `production/print_lable_part.html`
    - `production/reports/shipped.html`
    - `production/reports/delivery_note.html`

18. **Migrate customer shop templates**
    - `production/shop/*.html`
    - `production/customer/*.html`

#### Week 10: CSS/JS Cleanup

19. **Remove Bootstrap CSS completely**
    - Delete `bootstrap.rtl.min.css`, `bootstrap-icons.css`
    - Remove from `layouts/dashboard.html`

20. **Remove Select2 and jQuery**
    - Replace with Alpine.js alternatives
    - Delete vendor files

21. **Consolidate CSS files**
    - Merge `components.css`, `dashboard.css`, `product-grid.css`, `pages/*.css` into `tailwind-input.css`

---

## 10. SUMMARY STATISTICS

### Template Count by Status

| Status | Count | Percentage |
|--------|-------|------------|
| GREEN | 44 | 43% |
| YELLOW | 38 | 37% |
| RED | 20 | 20% |
| **Total** | **102** | **100%** |

### Template Count by Layout

| Layout | Count | Status |
|--------|-------|--------|
| `layouts/store.html` | 44 | Mostly GREEN |
| `layouts/dashboard.html` | 38 | All YELLOW |
| `layouts/print.html` | 3 | All RED |
| No layout | 17 | Mixed RED/YELLOW |

### Inline Code Debt

| Type | Count | Total Lines |
|------|-------|-------------|
| Inline CSS blocks | ~15 templates | ~800+ lines |
| Inline JS blocks | ~20 templates | ~600+ lines |

### Bootstrap Dependency

| Dependency | Templates Affected |
|------------|-------------------|
| Bootstrap CSS | 1 layout (`dashboard.html`) → 58 templates |
| Bootstrap JS | **0 loaded** → 5 templates broken |
| Bootstrap Icons | 1 layout → 58 templates |

### jQuery Dependency

| Dependency | Templates Affected | Status |
|------------|-------------------|--------|
| jQuery core | **0 loaded** | Orphaned |
| Select2 | 1 template | Broken (no jQuery) |

---

## 11. RISK ASSESSMENT

### High-Risk Areas

1. **Painting Management Module** - BROKEN modals, Select2 broken, highest complexity
2. **Production Scanning** - Core business workflow, must not break
3. **Order Management** - High traffic, complex inline JS
4. **Product Creation/BOM** - Complex formsets, modals

### Medium-Risk Areas

1. **Customer Shop Templates** - Bootstrap → Tailwind migration
2. **Report Templates** - Print-specific, many inline styles
3. **Admin Edit Flows** - Cascade selects, color fields

### Low-Risk Areas

1. **Storefront Templates** - Already fully migrated
2. **Account Templates** - Simple forms, no complex JS
3. **Component Library** - Mostly migrated

---

## 12. RESOURCE ESTIMATE

### Phase 6 Timeline: 10 Weeks (1 developer)

| Week | Focus | Templates | Effort |
|------|-------|-----------|--------|
| 1 | Critical bugs + foundation | 5 painting templates | 5 days |
| 2 | Layout consolidation | 3 layouts | 3 days |
| 3 | Component library | 7 components | 4 days |
| 4 | Low-risk admin | 8 templates | 4 days |
| 5 | Medium-risk admin | 4 templates | 5 days |
| 6 | High-risk production | 4 templates | 5 days |
| 7 | Admin edit flows | 2 templates | 3 days |
| 8 | Painting management | 7 templates | 5 days |
| 9 | Print + customer shop | 12 templates | 5 days |
| 10 | CSS/JS cleanup + validation | All | 3 days |

**Total:** ~42 days of work

---

*Audit generated by Kilo Frontend Audit - Phase 6 Planning*