# FRONTEND_MIGRATION_STATUS
## سلوی چوب (Selvi Wood) — Migration Readiness Audit

**Audit Date:** 2026-08-30  
**Repository:** https://github.com/ahd666x/store  
**Phases Completed:** 0–5  
**Next Phase:** 6 (Admin Panel Migration) — **not started**  
**Method:** Full repository scan of `templates/`, `static/css/`, `static/js/`. Page status is evaluated **per template**, not inferred from parent layout alone.

---

## 1. EXECUTIVE SUMMARY

Phases 0–5 established the modern storefront stack (Tailwind + Alpine.js + HTMX), extracted most inline scripts into JS modules, and created a shared component library. **The admin/production panel, customer B2B portal, painting management module, and print/report views remain on Bootstrap markup** loaded through `layouts/dashboard.html`.

### Key Metrics

| Metric | Current | Phase 6 Target |
|--------|---------|----------------|
| Total HTML templates | **143** | 143 |
| **GREEN** (migrated) | **42** (29%) | 143 |
| **YELLOW** (partial) | **88** (62%) | 0 |
| **RED** (legacy) | **13** (9%) | 0 |
| Layouts using Bootstrap CSS | 1 (`dashboard.html`) | 0 |
| Layouts loading jQuery | 1 (`dashboard.html`) | 0 |
| Layouts loading Bootstrap JS | 1 (`dashboard.html`) | 0 |
| Templates loading Select2 | 1 (`workers.html`) | 0 |
| Inline `<style>` blocks | **15** templates | 0 |
| Inline `<script>` blocks (non-vendor) | **18** templates | 0 |
| Templates using `style=` attributes | **33** templates | 0 |
| App CSS files (excl. vendor) | 7 | 2–3 |
| App JS modules | 19 | consolidated |
| Pages using `components/` includes | **6** page templates | 90%+ |

### Critical Findings (vs. prior audit)

| Finding | Prior audit (2026-08-29) | Current state (2026-08-30) |
|---------|--------------------------|----------------------------|
| Bootstrap JS loaded | "NOWHERE — modals broken" | **Loaded in `layouts/dashboard.html`** (+ duplicated in `painting_management/base.html`) |
| jQuery loaded | "NOWHERE — Select2 broken" | **Loaded in `layouts/dashboard.html`** (+ duplicated in painting base) |
| Painting modals | Broken | **Functional via Bootstrap JS**, still legacy and must be migrated to Alpine |
| Duplicate vendor JS at repo root | Present | **Removed** — only `static/js/vendor/` copies remain |
| `style.css` | Referenced | **Present** at `static/css/style.css` (Tailwind build output) |

### What remains to migrate

1. **`layouts/dashboard.html`** — remove Bootstrap CSS, jQuery, Bootstrap JS; load Tailwind `style.css` instead.
2. **58 page templates** inheriting dashboard chain — replace Bootstrap grid/forms/tables/modals with Tailwind + Alpine.
3. **6 Bootstrap-dependent components** — table, pagination, modal, confirm_modal, alert, loading_overlay.
4. **13 RED print/standalone templates** — extract inline CSS to `print.css`, adopt `layouts/print.html`.
5. **Global `app.js` boot** — loads Scanner, Kanban, Orders, Select2 init on every dashboard page.
6. **7 legacy CSS files** — consolidate into `tailwind-input.css` after page migration.
7. **Painting module** — highest complexity (Bootstrap modals, Select2, kanban CSS, 5 dedicated JS modules).

---

## 2. TECHNOLOGY ADOPTION

### 2.1 Layouts

| Layout | Path | Current Stack | Target | Status |
|--------|------|---------------|--------|--------|
| Store | `layouts/store.html` | Tailwind (`style.css`), Alpine, HTMX, `components.css`, `product-grid.css` | Same (consolidate CSS) | **GREEN** |
| Dashboard | `layouts/dashboard.html` | Bootstrap RTL CSS, Bootstrap Icons, `dashboard.css`, `components.css`, jQuery, Bootstrap JS, Alpine, global `app.js` | Tailwind + Alpine + lazy JS | **YELLOW** |
| Print | `layouts/print.html` | Minimal HTML shell, no CSS framework | + shared `print.css` | **GREEN** |

### 2.2 Base Templates

| Base | Extends | Bootstrap in markup | Alpine | Status |
|------|---------|---------------------|--------|--------|
| `base.html` | `layouts/store.html` | No | Via layout | **GREEN** |
| `production/base.html` | `layouts/dashboard.html` | Yes (`btn-*`, `bi-*`, navbar) | Mobile nav toggle | **YELLOW** |
| `production/base_shop.html` | `layouts/dashboard.html` | Yes (`btn-*`, `shop-navbar`) | Mobile nav toggle | **YELLOW** |
| `production/painting_management/base.html` | `layouts/dashboard.html` | Via layout + `painting.css` | No | **YELLOW** |

### 2.3 Technology Matrix

| Technology | Static Assets | Loaded From | Used By | Remove After |
|------------|---------------|-------------|---------|--------------|
| **Tailwind CSS** | `style.css`, `tailwind-input.css` | `layouts/store.html`, 2 standalone pages | Storefront (42 templates) | Never |
| **Alpine.js** | `vendor/alpinejs.min.js`, `alpine-bootstrap.js` | Store + dashboard layouts | Nav toggles, toasts, tabs, alerts | Never |
| **HTMX** | `vendor/htmx.min.js` | `layouts/store.html` | Cart add/update, partial swaps | Never |
| **Bootstrap CSS** | `vendor/bootstrap.rtl.min.css`, `bootstrap-icons.css` | `layouts/dashboard.html` | 58 dashboard-chain pages | Phase 6 Week 10 |
| **Bootstrap JS** | `vendor/bootstrap.bundle.min.js` | `layouts/dashboard.html`, painting base (dup) | Modals in painting, BOM, workers | Phase 6 Week 8 |
| **jQuery** | `vendor/jquery-3.7.1.min.js` | `layouts/dashboard.html`, painting base (dup) | Select2 in `app.js` + `workers.js` | Phase 6 Week 8 |
| **Select2** | `vendor/select2.min.js` + CSS themes | `workers.html` | Worker exclusion AJAX multi-select | Phase 6 Week 8 |
| **Legacy CSS** | `components.css`, `dashboard.css`, `product-grid.css`, `pages/*.css` | Various | Admin nav, painting, shipped report | Phase 6 Week 10 |

### 2.4 Inline Code Debt

| Type | Count | Notable Templates |
|------|-------|-------------------|
| `<style>` blocks | 15 | `reports/stages.html`, `order_combined_print.html`, `daily_schedule_print.html`, all print templates |
| `<script>` blocks (inline) | 18 | `order_list.html`, `product_create.html`, `admin_order_edit.html`, `create_unified.html`, `workers.html` |
| `style=` attributes | 33 | Print templates, `item.html`, `admin_order_tasks.html`, customer/shop pages |

---

## 3. COMPLETE MIGRATION MATRIX

**Legend**

- **Current layout:** immediate `{% extends %}` target; full chain shown where relevant.
- **Target layout:** intended end-state layout for Phase 6.
- **Status:** evaluated on **this file's markup**, not parent layout alone.
- **Complexity / Risk:** migration effort / production impact.

---

### 3.1 Layouts & Base Templates (7)

| Path | Current Layout | Target Layout | Bootstrap | jQuery | Inline CSS | Inline JS | Components Available | Components Used | Status | Complexity | Risk |
|------|----------------|---------------|-----------|--------|------------|-----------|---------------------|-------------------|--------|------------|------|
| `layouts/store.html` | — | — | No | No | x-cloak only | HTMX CSRF (6 lines) | All store components | header, footer, toast | **GREEN** | Low | Low |
| `layouts/dashboard.html` | — | — | **CSS+JS** | **Yes** | No | No | Partial | — | **YELLOW** | High | High |
| `layouts/print.html` | — | — | No | No | No | No | — | — | **GREEN** | Low | Low |
| `base.html` | `layouts/store.html` | same | No | No | No | No | All | — | **GREEN** | Low | Low |
| `production/base.html` | `layouts/dashboard.html` | Tailwind dashboard | **Classes** | Inherited | No | No | quick_link_card | — | **YELLOW** | Medium | Medium |
| `production/base_shop.html` | `layouts/dashboard.html` | Tailwind dashboard | **Classes** | Inherited | No | No | — | — | **YELLOW** | Medium | Low |
| `production/painting_management/base.html` | `layouts/dashboard.html` | Tailwind dashboard | Inherited + `painting.css` | **Dup load** | No | No | — | — | **YELLOW** | Medium | Medium |

---

### 3.2 Storefront Pages — `base.html` → `layouts/store.html` (30)

| Path | Current Layout | Target Layout | Bootstrap | jQuery | Inline CSS | Inline JS | Components Available | Components Used | Status | Complexity | Risk |
|------|----------------|---------------|-----------|--------|------------|-----------|---------------------|-------------------|--------|------------|------|
| `home.html` | `layouts/store.html` | same | No | No | No | No | empty_state, product_card | empty_state | **GREEN** | Low | Low |
| `catalog/product_list.html` | `layouts/store.html` | same | No | No | No | No | empty_state, product_card | empty_state | **GREEN** | Low | Low |
| `catalog/product_detail.html` | `base.html` | same | No | No | **Yes** | No | breadcrumb | — | **YELLOW** | Low | Low |
| `catalog/category_list.html` | `base.html` | same | No | No | No | No | product_card | — | **GREEN** | Low | Low |
| `catalog/category_detail.html` | `base.html` | same | No | No | No | No | product_card | — | **GREEN** | Low | Low |
| `catalog/stock_alerts.html` | `base.html` | same | No | No | No | No | — | — | **GREEN** | Low | Low |
| `catalog/comparison.html` | `base.html` | same | No | No | No | No | — | — | **GREEN** | Low | Low |
| `cart/detail.html` | `base.html` | same | No | No | No | No | empty_state | empty_state | **GREEN** | Low | **High** |
| `accounts/login.html` | `base.html` | same | No | No | No | No | form components | — | **GREEN** | Low | Low |
| `accounts/register.html` | `base.html` | same | No | No | No | No | form components | — | **GREEN** | Low | Low |
| `accounts/otp_request.html` | `base.html` | same | No | No | No | No | — | — | **GREEN** | Low | Low |
| `accounts/otp_verify.html` | `base.html` | same | No | No | No | Alpine | — | — | **GREEN** | Low | Low |
| `accounts/profile.html` | `base.html` | same | No | No | No | Alpine | status_badge | — | **GREEN** | Low | Low |
| `accounts/profile_edit.html` | `base.html` | same | No | No | No | No | form components | — | **GREEN** | Low | Low |
| `accounts/wishlist.html` | `base.html` | same | No | No | No | No | — | — | **GREEN** | Low | Low |
| `accounts/password_reset.html` | `base.html` | same | No | No | No | No | — | — | **GREEN** | Low | Low |
| `accounts/password_reset_done.html` | `base.html` | same | No | No | No | No | — | — | **GREEN** | Low | Low |
| `accounts/password_reset_complete.html` | `base.html` | same | No | No | No | No | — | — | **GREEN** | Low | Low |
| `accounts/password_reset_confirm.html` | `base.html` | same | No | No | No | No | — | — | **GREEN** | Low | Low |
| `orders/order_list.html` | `base.html` | same | No | No | No | No | status_badge | status_badge include | **GREEN** | Low | Medium |
| `orders/order_detail.html` | `base.html` | same | No | No | No | No | status_badge, order_items | includes | **GREEN** | Low | Medium |
| `orders/order_form.html` | `base.html` | same | No | No | No | No | form components | — | **GREEN** | Low | Low |
| `orders/order_confirm.html` | `base.html` | same | No | No | No | No | order_items | include | **GREEN** | Low | **High** |
| `orders/return_request_list.html` | `base.html` | same | No | No | No | No | return_status_badge | include | **GREEN** | Low | Low |
| `orders/return_request_form.html` | `base.html` | same | No | No | No | No | — | — | **GREEN** | Low | Low |
| `orders/return_request_detail.html` | `base.html` | same | No | No | No | No | return_status_badge | include | **GREEN** | Low | Low |
| `payments/payment_create.html` | `base.html` | same | No | No | No | No | — | — | **GREEN** | Low | **High** |
| `payments/payment_error.html` | `base.html` | same | No | No | No | No | — | — | **GREEN** | Low | Medium |
| `discounts/discount_list.html` | `base.html` | same | No | No | No | No | — | — | **GREEN** | Low | Low |
| `discounts/discount_form.html` | `base.html` | same | No | No | No | No | form components | — | **GREEN** | Low | Low |
| `communications/notification_list.html` | `base.html` | same | No | No | No | No | — | — | **GREEN** | Low | Low |

---

### 3.3 Store Includes & Partials (10)

| Path | Current Layout | Target Layout | Bootstrap | jQuery | Inline CSS | Inline JS | Components Available | Components Used | Status | Complexity | Risk |
|------|----------------|---------------|-----------|--------|------------|-----------|---------------------|-------------------|--------|------------|------|
| `includes/header.html` | include | — | No | No | No | No | — | Alpine nav | **GREEN** | Low | Low |
| `includes/footer.html` | include | — | No | No | No | No | — | — | **GREEN** | Low | Low |
| `includes/toast.html` | include | — | No | No | No | Alpine | — | — | **GREEN** | Low | Low |
| `includes/cart-actions.html` | include | — | No | No | No | HTMX | — | — | **GREEN** | Low | **High** |
| `includes/icons.html` | include | — | No | No | No | No | — | — | **GREEN** | Low | Low |
| `catalog/includes/product_card.html` | include | — | No | No | No | No | — | — | **GREEN** | Low | Low |
| `cart/includes/cart_item_row.html` | include | — | No | No | No | HTMX | — | — | **GREEN** | Low | **High** |
| `orders/includes/order_items.html` | include | — | No | No | No | No | — | — | **GREEN** | Low | Low |
| `orders/includes/status_badge.html` | include | — | No | No | No | No | badge | — | **GREEN** | Low | Low |
| `orders/includes/return_status_badge.html` | include | — | No | No | No | No | badge | — | **GREEN** | Low | Low |

---

### 3.4 Production Admin — `production/base.html` → `layouts/dashboard.html` (34)

| Path | Current Layout | Target Layout | Bootstrap | jQuery | Inline CSS | Inline JS | Components Available | Components Used | Status | Complexity | Risk |
|------|----------------|---------------|-----------|--------|------------|-----------|---------------------|-------------------|--------|------------|------|
| `production/dashboard.html` | dashboard chain | Tailwind dashboard | **Yes** | Inherited | No | No | quick_link_card | **9× quick_link_card** | **YELLOW** | Low | Low |
| `production/order_list.html` | dashboard chain | same | **Yes** | Inherited | No | **Yes** | table, pagination | — | **YELLOW** | Medium | **High** |
| `production/order_item.html` | dashboard chain | same | **Yes** | Inherited | No | module only | table | — | **YELLOW** | Medium | **High** |
| `production/admin_product_list.html` | dashboard chain | same | **Yes** | Inherited | No | No | table | — | **YELLOW** | Low | Low |
| `production/product_create.html` | dashboard chain | same | **Yes** | Inherited | **Yes** | **Yes** | modal, form_field | bom.js | **YELLOW** | High | **High** |
| `production/product_bom_edit.html` | dashboard chain | same | **Yes** | Inherited | No | **Yes** | — | bom patterns | **YELLOW** | Medium | Medium |
| `production/admin_order_edit.html` | dashboard chain | same | **Yes** | Inherited | style attr | **Yes** | form_field | — | **YELLOW** | High | **High** |
| `production/admin_edit_order_item.html` | dashboard chain | same | **Yes** | Inherited | No | **Yes** | — | order_item.js | **YELLOW** | Medium | **High** |
| `production/admin_order_tasks.html` | dashboard chain | same | **Yes** | Inherited | style attr | No | — | — | **YELLOW** | Low | Medium |
| `production/admin_tasks_management.html` | dashboard chain | same | **Yes** | Inherited | style attr | **Yes** | — | Alpine tabs | **YELLOW** | Medium | Medium |
| `production/task_list.html` | dashboard chain | same | **Yes** | Inherited | No | No | table | — | **YELLOW** | Low | Low |
| `production/worker_list.html` | dashboard chain | same | **Yes** | Inherited | No | No | table | — | **YELLOW** | Low | Low |
| `production/kanban.html` | dashboard chain | same | **Yes** | Inherited | No | No | — | kanban.js via app | **YELLOW** | Medium | Medium |
| `production/item.html` | dashboard chain | same | **Yes** | Inherited | style attr | No | — | — | **YELLOW** | Medium | **High** |
| `production/scan_part.html` | dashboard chain | same | **Yes** | Inherited | style attr | module | — | scanner.js | **YELLOW** | Medium | **High** |
| `production/scan_packaging_unit.html` | dashboard chain | same | **Yes** | Inherited | No | module | — | scanner.js | **YELLOW** | Medium | **High** |
| `production/create_unified.html` | dashboard chain | same | **Yes** | Inherited | No | **Yes** | form_field | cascade via app | **YELLOW** | High | **High** |
| `production/orders/create_step1.html` | dashboard chain | same | **Yes** | Inherited | No | **Yes** | form_field | **form_field×3** | **YELLOW** | Medium | **High** |
| `production/orders/create_step2.html` | dashboard chain | same | **Yes** | Inherited | **Yes** | **Yes** | — | colors via app | **YELLOW** | Medium | **High** |
| `production/orders/order_detail.html` | dashboard chain | same | **Yes** | Inherited | **Yes** | No | status_badge | — | **YELLOW** | Medium | **High** |
| `production/orders/add_item.html` | dashboard chain | same | **Yes** | Inherited | No | No | — | — | **YELLOW** | Low | Medium |
| `production/orders/add_colors.html` | dashboard chain | same | **Yes** | Inherited | No | No | — | — | **YELLOW** | Low | Medium |
| `production/import_data.html` | dashboard chain | same | **Yes** | Inherited | No | No | — | — | **YELLOW** | Low | Low |
| `production/upload.html` | **none** | dashboard or store | No | No | style attr | No | — | — | **RED** | Low | Low |
| `production/test.html` | dashboard chain | same | **Yes** | Inherited | No | No | — | — | **YELLOW** | Low | Low |
| `production/create_order.html` | dashboard chain | same | **Yes** | Inherited | No | No | — | — | **YELLOW** | Low | Medium |
| `production/create_complete.html` | dashboard chain | same | **Yes** | Inherited | No | No | — | — | **YELLOW** | Low | Low |
| `production/set_plate.html` | dashboard chain | same | **Yes** | Inherited | No | No | — | — | **YELLOW** | Low | Medium |
| `production/select_shipment.html` | dashboard chain | same | **Yes** | Inherited | No | No | — | — | **YELLOW** | Low | Medium |
| `production/lable_part.html` | dashboard chain | same | **Yes** | Inherited | style attr | No | — | — | **YELLOW** | Medium | Medium |
| `production/painting_process_list.html` | dashboard chain | same | **Yes** | Inherited | No | No | table | — | **YELLOW** | Low | Low |
| `production/holiday_list.html` | dashboard chain | same | **Yes** | Inherited | No | No | table | — | **YELLOW** | Low | Low |
| `production/report.html` | dashboard chain | same | **Yes** | Inherited | style attr | No | — | — | **YELLOW** | Low | Low |
| `production/assign_painting.html` | painting base | painting base | **Yes** | Inherited | No | No | — | — | **YELLOW** | Low | Medium |

**Admin reports (extend `production/base.html`):**

| Path | Bootstrap | Inline CSS | Inline JS | Status | Complexity | Risk |
|------|-----------|------------|-----------|--------|------------|------|
| `production/reports/stages.html` | Yes | **Yes** | **Yes (×2)** | **YELLOW** | **High** | Medium |
| `production/reports/workers.html` | Yes | No | No | **YELLOW** | Low | Low |
| `production/reports/orders.html` | Yes | No | No | **YELLOW** | Low | Low |
| `production/reports/delayed.html` | Yes | No | No | **YELLOW** | Low | Low |

---

### 3.5 Customer B2B Portal — `base_shop.html` → `layouts/dashboard.html` (13)

| Path | Current Layout | Target Layout | Bootstrap | jQuery | Inline CSS | Inline JS | Components Available | Components Used | Status | Complexity | Risk |
|------|----------------|---------------|-----------|--------|------------|-----------|---------------------|-------------------|--------|------------|------|
| `production/shop/product_list.html` | dashboard chain | `layouts/store.html` or Tailwind dashboard | **Yes** | Inherited | style attr | No | product_card | — | **YELLOW** | Medium | Low |
| `production/shop/product_detail.html` | dashboard chain | same | **Yes** | Inherited | style attr | **Yes** | — | — | **YELLOW** | Medium | Low |
| `production/shop/cart.html` | dashboard chain | same | **Yes** | Inherited | style attr | No | — | — | **YELLOW** | Medium | Medium |
| `production/shop/checkout.html` | dashboard chain | same | **Yes** | Inherited | style attr | No | — | — | **YELLOW** | Medium | **High** |
| `production/shop/order_tracking.html` | dashboard chain | same | **Yes** | Inherited | style attr | No | — | — | **YELLOW** | Medium | Low |
| `production/shop/order_history.html` | dashboard chain | same | **Yes** | Inherited | style attr | No | — | — | **YELLOW** | Low | Low |
| `production/customer/step1.html` | dashboard chain | same | **Yes** | Inherited | No | No | form_field | — | **YELLOW** | Low | **High** |
| `production/customer/step2.html` | dashboard chain | same | **Yes** | Inherited | No | **Yes** | — | — | **YELLOW** | Low | **High** |
| `production/customer/order_list.html` | dashboard chain | same | **Yes** | Inherited | No | No | table | — | **YELLOW** | Medium | Medium |
| `production/customer/order_detail.html` | dashboard chain | same | **Yes** | Inherited | **Yes** | **Yes (×2)** | — | — | **YELLOW** | Medium | **High** |
| `production/customer/edit_order_item.html` | dashboard chain | same | **Yes** | Inherited | **Yes** | **Yes** | — | — | **YELLOW** | Medium | Medium |
| `production/customer/shipments.html` | dashboard chain | same | **Yes** | Inherited | No | No | table | — | **YELLOW** | Medium | Medium |
| `production/customer/shipment_detail.html` | dashboard chain | same | **Yes** | Inherited | No | No | — | — | **YELLOW** | Low | Medium |

---

### 3.6 Painting Management — `painting_management/base.html` (13)

| Path | Bootstrap | jQuery | Select2 | Inline CSS | Inline JS | Bootstrap JS in JS modules | Status | Complexity | Risk |
|------|-----------|--------|---------|------------|-----------|---------------------------|--------|------------|------|
| `painting_management/dashboard.html` | Yes | Inherited | No | No | No | No | **YELLOW** | Low | Low |
| `painting_management/processes.html` | Yes | Inherited | No | No | module | **Yes** | **YELLOW** | Medium | **High** |
| `painting_management/stages.html` | Yes | Inherited | No | No | module | **Yes** | **YELLOW** | Medium | **High** |
| `painting_management/workers.html` | Yes | Inherited | **Yes** | style attr | **Yes** | **Yes** | **YELLOW** | **Very High** | **High** |
| `painting_management/schedule.html` | Yes | Inherited | No | style attr | module | kanban.js | **YELLOW** | **High** | **High** |
| `painting_management/ready_list.html` | Yes | Inherited | No | style attr | module | ready_list.js | **YELLOW** | **High** | Medium |
| `painting_management/assignment_rules.html` | Yes | Inherited | No | No | module | **Yes** | **YELLOW** | Medium | **High** |
| `painting_management/holidays.html` | Yes | Inherited | No | No | module | **Yes** | **YELLOW** | Medium | **High** |
| `painting_management/worker_excluded_items.html` | Yes | Inherited | No | No | No | No | **YELLOW** | Low | Low |
| `painting_management/_nav.html` | Yes | — | No | No | No | No | **YELLOW** | Low | Low |
| `painting_management/_pagination.html` | Yes | — | No | No | No | No | **YELLOW** | Low | Low |
| `painting_management/_worker_rows.html` | Yes | — | No | No | No | No | **YELLOW** | Low | Low |

---

### 3.7 Print & Standalone Report Templates (10)

| Path | Current Layout | Target Layout | Bootstrap | Inline CSS | Inline JS | Status | Complexity | Risk |
|------|----------------|---------------|-----------|------------|-----------|--------|------------|------|
| `production/print.html` | `layouts/print.html` | same + `print.css` | No | **Yes** | No | **RED** | Low | Low |
| `production/order_print.html` | `layouts/print.html` | same + `print.css` | No | **Yes** | No | **RED** | Low | Low |
| `production/order_invoice.html` | `layouts/print.html` | same + `print.css` | No | **Yes** | style attr | **RED** | Low | Low |
| `production/print_lable.html` | **none** | `layouts/print.html` | No | **Yes** | No | **RED** | Low | Low |
| `production/print_lable_part.html` | **none** | `layouts/print.html` | No | **Yes** | No | **RED** | Low | Low |
| `production/order_combined_print.html` | **none** | `layouts/print.html` | No | **Yes (350+ lines)** | No | **RED** | **High** | Low |
| `production/daily_schedule_print.html` | **none** | `layouts/print.html` | No | **Yes** | **Yes** | **RED** | Medium | Low |
| `production/reports/delivery_note.html` | **none** | `layouts/print.html` | No | **Yes** | No | **RED** | Low | Low |
| `production/reports/shipped.html` | **none** | Tailwind dashboard | Partial Tailwind | style attr | No | **YELLOW** | Low | Low |
| `production/registration/login.html` | **none** | `layouts/store.html` | Icons only | No | No | **YELLOW** | Low | Low |

---

### 3.8 Component Library — `templates/components/` (23)

| Path | Bootstrap | jQuery | Inline CSS/JS | Status | Migration Action |
|------|-----------|--------|---------------|--------|------------------|
| `components/cards/card.html` | No | No | No | **GREEN** | Keep |
| `components/cards/stat_card.html` | No | No | No | **GREEN** | Keep |
| `components/cards/quick_link_card.html` | No | No | No | **GREEN** | Keep |
| `components/forms/form_field.html` | No | No | No | **GREEN** | Keep |
| `components/forms/input.html` | No | No | No | **GREEN** | Keep |
| `components/forms/select.html` | No | No | No | **GREEN** | Keep |
| `components/forms/textarea.html` | No | No | No | **GREEN** | Keep |
| `components/forms/search.html` | No | No | No | **GREEN** | Keep |
| `components/forms/checkbox.html` | No | No | No | **GREEN** | Keep |
| `components/data/price.html` | No | No | No | **GREEN** | Keep |
| `components/data/date.html` | No | No | No | **GREEN** | Keep |
| `components/data/status_badge.html` | No | No | No | **GREEN** | Keep (Tailwind badges) |
| `components/data/badge.html` | No | No | No | **GREEN** | Keep |
| `components/feedback/empty_state.html` | No | No | No | **GREEN** | Keep |
| `components/navigation/header.html` | No | No | Alpine | **GREEN** | Keep |
| `components/navigation/breadcrumb.html` | No | No | No | **GREEN** | Keep |
| `components/tables/table.html` | **Yes** | No | No | **YELLOW** | → `table-modern` |
| `components/tables/pagination.html` | **Yes** | No | No | **YELLOW** | Tailwind pagination |
| `components/tables/table_actions.html` | Partial | No | No | **YELLOW** | Tailwind buttons |
| `components/modals/modal.html` | **Yes** | No | No | **YELLOW** | Alpine modal |
| `components/modals/confirm_modal.html` | **Yes** | No | No | **YELLOW** | Alpine confirm |
| `components/feedback/alert.html` | **Yes** | No | Alpine option | **YELLOW** | Tailwind alert |
| `components/loading/loading_overlay.html` | **Yes** | No | style attr | **YELLOW** | Tailwind spinner |

---

## 4. COMPONENTS STILL DEPENDING ON BOOTSTRAP

| Component / Area | Bootstrap Dependency | Blocks Migration Of |
|------------------|---------------------|---------------------|
| `components/tables/table.html` | `table`, `table-hover`, `table-dark` | All admin list pages |
| `components/tables/pagination.html` | `pagination`, `page-item`, `page-link` | Paginated admin lists |
| `components/modals/modal.html` | `modal`, `modal-dialog`, `btn-close`, `data-bs-dismiss` | BOM part modal, confirm flows |
| `components/modals/confirm_modal.html` | wraps Bootstrap modal | Delete confirmations |
| `components/feedback/alert.html` | `alert`, `alert-*`, `alert-dismissible` | Flash message patterns |
| `components/loading/loading_overlay.html` | `spinner-border` | Async operations |
| `layouts/dashboard.html` flash messages | `alert`, `btn-close` | All dashboard pages |
| `static/js/production/bom.js` | `bootstrap.Modal` | `product_create.html` |
| `static/js/production/workers.js` | `bootstrap.Modal`, Select2 | `workers.html` |
| `static/js/production/painting/*.js` (4 files) | `bootstrap.Modal` | processes, stages, holidays, assignment_rules |
| `static/js/app.js` | Select2 + jQuery | Worker exclusion selects |

---

## 5. CSS FILES — KEEP vs. REMOVE

| File | Lines (approx.) | Status | Action |
|------|-----------------|--------|--------|
| `static/css/style.css` | compiled | **KEEP** | Tailwind output |
| `static/css/tailwind-input.css` | 1248+ | **KEEP** | Source of truth |
| `static/css/vazirmatn-fonts.css` | — | **KEEP** | Fonts |
| `static/css/components.css` | 136 | **REMOVE LATER** | Admin/shop shared overrides → merge into Tailwind `@layer` |
| `static/css/dashboard.css` | 23 | **REMOVE LATER** | `.quick-link-card` → Tailwind |
| `static/css/product-grid.css` | 16 | **REMOVE LATER** | Grid utilities → Tailwind |
| `static/css/pages/painting.css` | — | **REMOVE LATER** | Painting nav/kanban → Tailwind |
| `static/css/pages/shipped.css` | — | **REMOVE LATER** | Shipped report → Tailwind |
| `static/css/vendor/bootstrap.rtl.min.css` | vendor | **REMOVE** | After dashboard migration |
| `static/css/vendor/bootstrap-icons.css` | vendor | **REMOVE** | Replace with Heroicons/SVG or Tailwind icons |
| `static/css/vendor/select2.min.css` | vendor | **REMOVE** | After Select2 replacement |
| `static/css/vendor/select2-bootstrap-5-theme.min.css` | vendor | **REMOVE** | After Select2 replacement |

---

## 6. JS MODULES — GLOBAL vs. MODULAR

### 6.1 Global entry (loaded on every dashboard page)

| Module | Path | Issue |
|--------|------|-------|
| `app.js` | `static/js/app.js` | Non-module script; initializes Cart, Catalog, Scanner, Kanban, Orders, Select2 on **all** dashboard pages |
| `alpine-bootstrap.js` | `static/js/alpine-bootstrap.js` | Alpine data components for legacy Bootstrap patterns |

**Store layout** loads `app.js` as `type="module"` — inconsistent with dashboard.

### 6.2 Feature modules (page-specific, should be lazy-loaded)

| Module | Used By | Bootstrap/jQuery |
|--------|---------|------------------|
| `production/scanner.js` | scan_part, scan_packaging_unit | No |
| `production/kanban.js` | schedule.html | No |
| `production/bom.js` | product_create | **bootstrap.Modal** |
| `production/workers.js` | workers.html | **bootstrap.Modal**, **Select2** |
| `production/orders.js` | order_list (inline boot) | No |
| `production/order_item.js` | order_item, admin_edit_order_item | No |
| `production/painting/processes.js` | processes.html | **bootstrap.Modal** |
| `production/painting/stages.js` | stages.html | **bootstrap.Modal** |
| `production/painting/holidays.js` | holidays.html | **bootstrap.Modal** |
| `production/painting/assignment_rules.js` | assignment_rules.html | **bootstrap.Modal** |
| `production/painting/ready_list.js` | ready_list.html | No |
| `store/cart.js` | store layout | HTMX |
| `store/catalog.js` | store layout | No |
| `forms/cascade.js`, `forms/colors.js` | order creation flows | No |

### 6.3 Vendor JS (remove after Phase 6)

| File | Loaded From | Replace With |
|------|-------------|--------------|
| `vendor/jquery-3.7.1.min.js` | dashboard + painting base | Remove |
| `vendor/bootstrap.bundle.min.js` | dashboard + painting base | Alpine modals |
| `vendor/select2.min.js` | workers.html | Alpine combobox or native `<select multiple>` + fetch |

---

## 7. PAGES REQUIRING SPECIAL CARE

### 7.1 Production-critical workflows

| Page | Workflow | Why Special |
|------|----------|-------------|
| `production/scan_part.html` | Barcode scan → task completion | Factory floor; cannot break autofocus/scanner |
| `production/scan_packaging_unit.html` | Packaging scan | Same as above |
| `production/order_list.html` | Batch ops, export, task generation | Inline JS + high traffic |
| `production/admin_order_edit.html` | Order/item editing | Complex forms, cascade selects |
| `production/product_create.html` | Product + BOM formset + modal | Bootstrap modal + bom.js |
| `production/painting_management/schedule.html` | Daily kanban scheduling | Drag-drop + custom CSS |
| `production/painting_management/workers.html` | Worker CRUD + exclusions | Select2 + 4 modals |
| `production/orders/create_step1/2.html` | Order creation funnel | Cascade + color fields |
| `cart/detail.html` | Store checkout | HTMX cart (already GREEN) |
| `production/shop/checkout.html` | B2B checkout | Payment-adjacent |

### 7.2 Highest migration complexity

1. `painting_management/workers.html` — Select2 + Bootstrap modals + inline JS + 11 `btn-*` patterns  
2. `painting_management/schedule.html` — kanban layout CSS in `painting.css` + drag-drop  
3. `painting_management/ready_list.html` — filters + inline styles  
4. `production/reports/stages.html` — inline CSS + dual inline scripts  
5. `production/order_combined_print.html` — 350+ lines print CSS  
6. `production/admin_order_edit.html` — largest admin edit surface  
7. `production/product_create.html` — BOM formset + Bootstrap modal  

---

## 8. SUMMARY STATISTICS

| Status | Templates | % |
|--------|-----------|---|
| **GREEN** | 42 | 29% |
| **YELLOW** | 88 | 62% |
| **RED** | 13 | 9% |
| **Total** | **143** | 100% |

| Layout Chain | Page Templates | Dominant Status |
|--------------|----------------|-----------------|
| `layouts/store.html` | 30 storefront | GREEN (29), YELLOW (1) |
| `layouts/dashboard.html` | 58 admin/customer/painting | YELLOW |
| `layouts/print.html` | 3 | RED (inline CSS) |
| Standalone / no layout | 10 | RED (8), YELLOW (2) |
| Includes & components | 42 | GREEN (31), YELLOW (11) |

| Adoption | Store Layout | Dashboard Layout |
|----------|--------------|------------------|
| Tailwind (`style.css`) | **Yes** | **No** (Bootstrap CSS) |
| Alpine.js | **Yes** | Partial (nav, alerts) |
| HTMX | **Yes** | **No** |
| Component library | 4 pages | 2 pages (dashboard, create_step1) |

---

## 9. RECOMMENDED PHASE 6 EXECUTION ORDER

**Goal:** Migrate admin/production panel to Tailwind + Alpine while preserving production-critical workflows. Fix functional regressions first, then layout, then components, then pages by risk.

### Week 1 — Foundation & functional baseline

1. **Validate vendor load order** on painting pages (jQuery → Bootstrap → Select2 → feature modules). Remove duplicate jQuery/Bootstrap from `painting_management/base.html` once confirmed dashboard layout loads them.
2. **Migrate `layouts/dashboard.html`** to Tailwind: swap Bootstrap CSS for `style.css`; keep jQuery/Bootstrap JS temporarily behind a feature flag or conditional block.
3. **Extract inline HTMX CSRF script** from `layouts/store.html` into `static/js/core/csrf.js` (store already loads module — align patterns).
4. **Migrate `production/upload.html`** to extend `production/base.html` (quick RED → YELLOW win).

### Week 2 — Base nav & shared CSS

5. **`production/base.html`** — replace Bootstrap navbar/buttons with Tailwind + Alpine (keep URLs/permissions identical).
6. **`production/base_shop.html`** — same treatment for customer portal nav.
7. **`production/painting_management/base.html`** — migrate header nav from `painting.css` to Tailwind utilities.
8. Begin merging **`components.css`** / **`dashboard.css`** into `tailwind-input.css`.

### Week 3 — Component library (unblocks bulk page migration)

9. Migrate **`components/tables/table.html`**, **`pagination.html`**, **`table_actions.html`**.
10. Migrate **`components/modals/modal.html`** + **`confirm_modal.html`** to Alpine (update `alpine-bootstrap.js`).
11. Migrate **`components/feedback/alert.html`**, **`loading/loading_overlay.html`**, dashboard flash messages.
12. Update **`static/js/production/bom.js`** and painting JS modules to use Alpine modals instead of `bootstrap.Modal`.

### Week 4 — Low-risk admin pages

13. `production/dashboard.html`, `task_list.html`, `worker_list.html`, `kanban.html`, `admin_order_tasks.html`
14. `production/reports/workers.html`, `reports/orders.html`, `reports/delayed.html`
15. `production/import_data.html`, `test.html`, `create_order.html`, `create_complete.html`, `set_plate.html`, `select_shipment.html`

### Week 5 — Medium-risk admin pages

16. `production/order_list.html` — remove inline script; wire `orders.js` via `extra_js`
17. `production/order_item.html`, `admin_product_list.html`, `item.html`, `lable_part.html`
18. `production/reports/stages.html` — extract inline CSS/JS to static files first

### Week 6 — High-risk production workflows

19. `production/scan_part.html`, `scan_packaging_unit.html` — visual migration only; **do not alter scanner.js behavior**
20. `production/product_create.html`, `product_bom_edit.html`
21. Order creation: `create_unified.html`, `orders/create_step1.html`, `orders/create_step2.html`, `orders/order_detail.html`

### Week 7 — Admin edit flows

22. `production/admin_order_edit.html`, `admin_edit_order_item.html`, `admin_tasks_management.html`

### Week 8 — Painting management (highest complexity)

23. Replace Select2 in **`workers.html`** with Alpine multi-select + fetch API
24. Migrate **`processes.html`**, **`stages.html`**, **`holidays.html`**, **`assignment_rules.html`** modals to Alpine
25. Migrate **`workers.html`**, **`schedule.html`**, **`ready_list.html`**, remaining painting partials
26. Remove jQuery, Bootstrap JS, Select2 vendor files

### Week 9 — Customer portal & print

27. Migrate **`production/shop/*.html`** (6) and **`production/customer/*.html`** (7)
28. Migrate print templates: extract inline CSS to **`static/css/print.css`**, adopt **`layouts/print.html`**
29. Migrate **`production/reports/shipped.html`**, **`registration/login.html`**

### Week 10 — Cleanup & validation

30. Remove **`bootstrap.rtl.min.css`**, **`bootstrap-icons.css`**, **`select2*.css`**
31. Delete **`components.css`**, **`dashboard.css`**, **`product-grid.css`**, **`pages/painting.css`**, **`pages/shipped.css`** after merge
32. Split **`app.js`** into lazy-loaded modules; load only per-page bundles
33. Manual QA on production-critical workflows (scan, order create, painting schedule, workers, checkout)
34. Run `npm run build:css`; verify gzipped CSS target (< 150KB)

### Phase 6 Exit Criteria

- [ ] 0% RED, 0% YELLOW templates  
- [ ] Zero Bootstrap CSS/JS and jQuery in templates or static vendor  
- [ ] Zero inline `<style>` / `<script>` blocks (except JSON-LD)  
- [ ] All pages use Tailwind design tokens from `tailwind-input.css`  
- [ ] Production-critical workflows manually validated  

---

*Audit performed 2026-08-30 against commit working tree. No application code was modified during this audit.*
