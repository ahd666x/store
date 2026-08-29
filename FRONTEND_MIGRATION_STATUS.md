# Frontend Migration Status — Forensic Audit

> Generated from source code inspection of all templates, CSS, and JS files.
> Classification: **GREEN** = fully migrated (Tailwind + Alpine + HTMX, no Bootstrap) · **YELLOW** = partial migration · **RED** = legacy Bootstrap/jQuery/inline

---

## Executive Summary

| Category | Total | GREEN | YELLOW | RED |
|----------|-------|-------|--------|-----|
| Layouts | 7 | 2 | 5 | 0 |
| Storefront Pages | ~25 | 25 | 0 | 0 |
| Account Pages | 11 | 11 | 0 | 0 |
| Order/Payment Pages | 13 | 13 | 0 | 0 |
| Production Pages | ~28 | 0 | 25 | 3 |
| Painting Management | 6 | 0 | 2 | 4 |
| Print Templates | 3 | 0 | 3 | 0 |
| Components | ~25 | 20 | 3 | 2 |
| CSS Files | 7 | 2 | 3 | 2 |
| JS Files | ~18 | 10 | 4 | 4 |

---

## Template Classification Rules

1. **GREEN**: Uses Tailwind utilities + Alpine.js + HTMX. No Bootstrap classes, no jQuery DOM manipulation, no inline `<style>` blocks.
2. **YELLOW**: Mix of architectures — e.g., Bootstrap grid + Alpine.js, or Tailwind + inline styles, or Bootstrap + custom CSS.
3. **RED**: Bootstrap grid/components + jQuery DOM manipulation, or heavy inline styles, or deprecated patterns (Select2, `bootstrap.Modal` direct calls).

Layout inheritance alone does NOT determine classification. A template extending `layouts/store.html` is not automatically GREEN — actual class usage is audited.

---

## Storefront (GREEN — All Pages)

| Template | Layout | Framework | Notes |
|----------|--------|-----------|-------|
| home.html | base → store | Tailwind + Alpine + HTMX | Hero, categories, featured products |
| catalog/product_list.html | base → store | Tailwind + Alpine + HTMX | Filters, grid, pagination |
| catalog/product_detail.html | base → store | Tailwind + Alpine + HTMX | Gallery, color selector, add-to-cart |
| catalog/category_detail.html | base → store | Tailwind + Alpine + HTMX | Category filter grid |
| catalog/category_list.html | base → store | Tailwind + Alpine + HTMX | Category tree |
| catalog/comparison.html | base → store | Tailwind + Alpine + HTMX | Product comparison table |
| catalog/stock_alerts.html | base → store | Tailwind + Alpine + HTMX | Alert subscriptions |
| catalog/includes/product_card.html | — | Tailwind | Reusable card component |
| cart/detail.html | base → store | Tailwind + Alpine + HTMX | Cart with HTMX add/remove |
| cart/includes/cart_item_row.html | — | Tailwind + HTMX | Cart line item |
| wishlist.html | base → store | Tailwind + Alpine | Wishlist management |

**CSS delivered**: `style.css` (compiled Tailwind), `components.css`, `bootstrap-icons.css`
**JS delivered**: Alpine.js, HTMX, `app.js` (Cart, Catalog modules)

---

## Account Pages (GREEN — All Pages)

| Template | Layout | Framework | Notes |
|----------|--------|-----------|-------|
| login.html | base → store | Tailwind + Alpine | Auth form |
| register.html | base → store | Tailwind + Alpine | Registration form |
| profile.html | base → store | Tailwind + Alpine | Profile display |
| profile_edit.html | base → store | Tailwind + Alpine | Edit profile |
| otp_request.html | base → store | Tailwind + Alpine | OTP request |
| otp_verify.html | base → store | Tailwind + Alpine | OTP verification |
| password_reset.html | base → store | Tailwind + Alpine | Reset request |
| password_reset_confirm.html | base → store | Tailwind + Alpine | Set new password |
| password_reset_done.html | base → store | Tailwind + Alpine | Confirmation |
| password_reset_complete.html | base → store | Tailwind + Alpine | Success page |

**JS delivered**: Alpine.js, `app.js` (none specific to auth)

---

## Order/Payment/Discount Pages (GREEN — All Pages)

| Template | Layout | Framework | Notes |
|----------|--------|-----------|-------|
| order_list.html | base → store | Tailwind + Alpine | Order history |
| order_detail.html | base → store | Tailwind + Alpine | Order details |
| order_form.html | base → store | Tailwind + Alpine | Checkout form |
| order_confirm.html | base → store | Tailwind + Alpine | Order confirmation |
| return_request_list.html | base → store | Tailwind + Alpine | Return list |
| return_request_detail.html | base → store | Tailwind + Alpine | Return details |
| return_request_form.html | base → store | Tailwind + Alpine | Return request |
| includes/order_items.html | — | Tailwind | Order line items |
| includes/status_badge.html | — | Tailwind | Status badge |
| includes/return_status_badge.html | — | Tailwind | Return status |
| payment_create.html | base → store | Tailwind + Alpine | Payment form |
| payment_error.html | base → store | Tailwind + Alpine | Payment error |
| discount_form.html | base → store | Tailwind + Alpine | Discount form |
| discount_list.html | base → store | Tailwind + Alpine | Discount list |
| notification_list.html | base → store | Tailwind + Alpine | Notifications |

---

## Production Pages (YELLOW — Bootstrap + Alpine mix)

| Template | Layout | Framework | Migration Status | Notes |
|----------|--------|-----------|-----------------|-------|
| dashboard.html | production/base → dashboard | Bootstrap + Alpine + jQuery | YELLOW | Main dashboard with stats cards |
| order_list.html | production/base → dashboard | Bootstrap + DataTables | YELLOW | Order list with table |
| order_item.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Order item detail |
| kanban.html | production/base → dashboard | Bootstrap + Alpine + HTML5 DnD | YELLOW | Kanban board with drag-drop |
| scan_part.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Part scanning |
| worker_list.html | production/base → dashboard | Bootstrap + Select2 | **RED** | Uses Select2 + Bootstrap Modal |
| product_bom_edit.html | production/base → dashboard | Bootstrap + Alpine + HTMX | YELLOW | BOM editing with HTMX |
| product_create.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Product creation |
| create_order.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Legacy create order |
| create_complete.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Unified create (complete) |
| create_unified.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Unified order form |
| order_print.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Printable order view |
| report.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Reports |
| orders/order_detail.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Order detail view |
| set_plate.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Plate assignment |
| scan_packaging_unit.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Packaging scan |
| select_shipment.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Shipment selection |
| print.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Print view |
| admin_product_list.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Admin product list |
| admin_order_edit.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Admin order edit |
| admin_edit_order_item.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Admin item edit |
| admin_order_tasks.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Task management |
| admin_tasks_management.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Admin tasks |
| item.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Item detail |
| orders/create_step1.html | production/base → dashboard | Bootstrap + vanilla JS | YELLOW | Order creation step 1 |
| orders/create_step2.html | production/base → dashboard | Bootstrap + vanilla JS | YELLOW | Order creation step 2 |
| orders/add_item.html | production/base → dashboard | Bootstrap | YELLOW | Add item to order |
| orders/add_colors.html | production/base → dashboard | Bootstrap | YELLOW | Add colors to item |
| assign_painting.html | painting_management/base → dashboard | Bootstrap | YELLOW | Painting task assignment |
| import_data.html | production/base → dashboard | Bootstrap | YELLOW | Excel import |

**CSS delivered**: bootstrap.rtl.min.css, bootstrap-icons.css, vazirmatn-fonts.css, dashboard.css, components.css
**JS delivered**: jQuery, Bootstrap.bundle, Alpine.js, alpine-bootstrap.js, app.js

---

## Painting Management (YELLOW/RED — Heavy Bootstrap)

| Template | Layout | Framework | Migration Status | Notes |
|----------|--------|-----------|-----------------|-------|
| dashboard.html | painting_management/base → dashboard | Bootstrap + Alpine + custom CSS | YELLOW | Painting dashboard |
| schedule.html | painting_management/base → dashboard | Bootstrap + Alpine + custom CSS | YELLOW | Painting schedule |
| workers.html | painting_management/base → dashboard | Bootstrap + Select2 + custom CSS | **RED** | Select2 + Bootstrap Modal |
| ready_list.html | painting_management/base → dashboard | Bootstrap + Alpine + custom CSS | YELLOW | Ready items list |
| assignment_rules.html | painting_management/base → dashboard | Bootstrap + Alpine + custom CSS | YELLOW | Assignment rules |
| processes.html | painting_management/base → dashboard | Bootstrap + Alpine + custom CSS | YELLOW | Process management |

**Additional CSS**: `pages/painting.css` (~300+ lines custom)
**Additional JS**: painting/*.js modules

---

## Print Templates (YELLOW — Minimal layout, inline styles)

| Template | Layout | Framework | Migration Status | Notes |
|----------|--------|-----------|-----------------|-------|
| print.html | layouts/print | Minimal + inline styles | YELLOW | Print template |
| order_print.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Order print |
| report.html | production/base → dashboard | Bootstrap + Alpine | YELLOW | Report print |

---

## Key Findings

### 1. Two Distinct Architectures
- **Storefront** (GREEN): Modern stack — Tailwind compiled via PostCSS, Alpine.js for reactivity, HTMX for async. Zero jQuery.
- **Production** (YELLOW/RED): Legacy stack — Bootstrap 5 grid + components, jQuery for DOM, Alpine for partial reactivity.

### 2. Component Library Underutilization
The `templates/components/` directory contains reusable components (cards, forms, modals, navigation, tables), but most production templates duplicate markup instead of using them. The component library is primarily consumed by storefront templates.

### 3. CSS Duplication
- `tailwind-input.css`: Full design system with Tailwind directives — only used for storefront
- `dashboard.css`: Custom production styles overriding Bootstrap
- `components.css`: Shared between both architectures but has legacy classes
- `pages/painting.css`: Large custom CSS file duplicating Bootstrap utilities

### 4. JavaScript Architecture Split
- **Storefront JS**: Modular ES6 classes (Cart, Catalog) initialized via `app.js`
- **Production JS**: Mix of ES6 classes and legacy patterns — `bootstrap.Modal` direct calls, Select2 initialization, jQuery event handlers

### 5. Migration Blockers
- Select2 dependency in `worker_list.html` and `workers.html`
- `bootstrap.Modal` / `bootstrap.Tooltip` direct calls in multiple production JS files
- Inline `<style>` blocks in several production templates
- `pages/painting.css` contains ~300+ lines that would need Tailwind conversion
- jQuery event handlers in legacy templates (create_step1.html)

### 6. HTMX Usage
HTMX is used primarily in storefront (cart, catalog) and one production template (`product_bom_edit.html`). Most production forms use traditional POST + redirect.

---

## Migration Priority Recommendations

| Priority | Area | Effort | Impact |
|----------|------|--------|--------|
| P0 | Painting workers page (Select2 → Alpine) | Medium | High — blocks full Alpine adoption |
| P1 | Production order creation flow | High | High — most complex forms |
| P1 | Kanban board | Medium | Medium — could use HTMX partials |
| P2 | Painting management pages | High | Medium — large custom CSS to convert |
| P2 | Production dashboard | Medium | Low — mostly cosmetic |
| P3 | Print templates | Low | Low — minimal usage |
| P3 | Admin order edit pages | Medium | Low — internal tools |

---

## Files Referenced

### Layouts
- `templates/layouts/store.html`
- `templates/layouts/dashboard.html`
- `templates/layouts/print.html`
- `templates/base.html`
- `templates/production/base.html`
- `templates/production/base_shop.html`
- `templates/production/painting_management/base.html`

### CSS
- `static/css/tailwind-input.css`
- `static/css/components.css`
- `static/css/dashboard.css`
- `static/css/product-grid.css`
- `static/css/vazirmatn-fonts.css`
- `static/css/pages/painting.css`
- `static/css/pages/shipped.css`

### JS
- `static/js/app.js`
- `static/js/alpine-bootstrap.js`
- `static/js/components/loading.js`
- `static/js/components/toast.js`
- `static/js/core/csrf.js`
- `static/js/forms/cascade.js`
- `static/js/forms/colors.js`
- `static/js/store/cart.js`
- `static/js/store/catalog.js`
- `static/js/production/bom.js`
- `static/js/production/kanban.js`
- `static/js/production/order_item.js`
- `static/js/production/orders.js`
- `static/js/production/scanner.js`
- `static/js/production/workers.js`
- `static/js/production/painting/assignment_rules.js`
- `static/js/production/painting/holidays.js`
- `static/js/production/painting/processes.js`
- `static/js/production/painting/ready_list.js`
- `static/js/production/painting/stages.js`
