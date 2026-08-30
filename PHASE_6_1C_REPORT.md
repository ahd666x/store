# PHASE 6.1C — SHARED COMPONENTS VALIDATION & CONSOLIDATION REPORT

**Project:** store (دکارو / سلوی چوب)
**Scope:** Shared component library inspection after Modal (6.1A) and Badge (6.1B) migrations
**Date:** 2026-08-30

---

## 1. COMPONENT INVENTORY

**Total shared components inspected:** 23

| # | Component | Path |
|---|-----------|------|
| 1 | Modal | `templates/components/modals/modal.html` |
| 2 | Confirm Modal | `templates/components/modals/confirm_modal.html` |
| 3 | Badge | `templates/components/data/badge.html` |
| 4 | Status Badge | `templates/components/data/status_badge.html` |
| 5 | Price | `templates/components/data/price.html` |
| 6 | Date | `templates/components/data/date.html` |
| 7 | Stat Card | `templates/components/cards/stat_card.html` |
| 8 | Quick Link Card | `templates/components/cards/quick_link_card.html` |
| 9 | Card | `templates/components/cards/card.html` |
| 10 | Textarea | `templates/components/forms/textarea.html` |
| 11 | Select | `templates/components/forms/select.html` |
| 12 | Search | `templates/components/forms/search.html` |
| 13 | Input | `templates/components/forms/input.html` |
| 14 | Form Field | `templates/components/forms/form_field.html` |
| 15 | Checkbox | `templates/components/forms/checkbox.html` |
| 16 | Table Actions | `templates/components/tables/table_actions.html` |
| 17 | Table | `templates/components/tables/table.html` |
| 18 | Pagination | `templates/components/tables/pagination.html` |
| 19 | Header | `templates/components/navigation/header.html` |
| 20 | Breadcrumb | `templates/components/navigation/breadcrumb.html` |
| 21 | Empty State | `templates/components/feedback/empty_state.html` |
| 22 | Alert | `templates/components/feedback/alert.html` |
| 23 | Loading Overlay | `templates/components/loading/loading_overlay.html` |

---

## 2. CLASSIFICATION MATRIX

| Component | Classification | Bootstrap CSS | Bootstrap JS | jQuery | Alpine | HTMX | Tailwind | Bootstrap Icons |
|-----------|---------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Modal | GREEN | No | No | No | Yes | No | Yes | No |
| Confirm Modal | GREEN | No | No | No | Yes | No | Yes | No |
| Badge | GREEN | No | No | No | No | No | Yes | No |
| Status Badge | YELLOW | No* | No | No | No | No | Yes* | No |
| Price | GREEN | No | No | No | No | No | Yes | No |
| Date | GREEN | No | No | No | No | No | Yes | No |
| Stat Card | YELLOW | No | No | No | No | No | Yes | Yes |
| Quick Link Card | YELLOW | No | No | No | No | No | Yes | Yes |
| Card | GREEN | No | No | No | No | No | Yes | No |
| Textarea | GREEN | No | No | No | No | No | Yes | No |
| Select | GREEN | No | No | No | No | No | Yes | No |
| Search | GREEN | No | No | No | No | No | Yes | No |
| Input | GREEN | No | No | No | No | No | Yes | No |
| Form Field | RED | **Yes** | No | No | No | No | Yes | No |
| Checkbox | GREEN | No | No | No | No | No | Yes | No |
| Table Actions | RED | **Yes** | No | No | No | No | Yes | Yes |
| Table | YELLOW | No* | No | No | No | No | Yes* | No |
| Pagination | RED | **Yes** | No | No | No | No | Yes | No |
| Header | YELLOW | No | No | No | Yes | No | Yes | Yes |
| Breadcrumb | GREEN | No | No | No | No | No | Yes | No |
| Empty State | GREEN | No | No | No | No | No | Yes | No |
| Alert | YELLOW | No* | No | No | Yes† | No | Yes* | No |
| Loading Overlay | YELLOW | No* | No | No | No | No | Yes* | No |

\* Uses Bootstrap-named class names that are defined as project component classes in `tailwind-input.css` (not the Bootstrap library). These components work without loading Bootstrap CSS.
† Alpine is optional (only used for dismissible variant).

### Classification Rationale

**GREEN (13):** Compatible with modern architecture. No unnecessary legacy dependencies. Pure Tailwind or project-defined component classes.

**YELLOW (7):**
- `status_badge.html`: Uses project-defined `.badge*` classes (Bootstrap-named but library-free).
- `stat_card.html` / `quick_link_card.html`: Depend on Bootstrap Icons (`bi bi-*`).
- `table.html`: Uses project-defined `.table*` classes (Bootstrap-named but library-free).
- `header.html`: Uses Bootstrap Icons + Alpine.
- `alert.html`: Uses project-defined `.alert*` / `.fade` / `.btn-close` classes. The `show` class lacks a standalone project definition, but Alpine handles visibility in the dismissible path.
- `loading_overlay.html`: Uses project-defined `.loading-overlay` / `.spinner` / `.visually-hidden` classes.

**RED (3):** Depend on Bootstrap CSS classes that are NOT defined in the project's Tailwind layer. Will break if Bootstrap CSS is not loaded.

---

## 3. REMAINING BOOTSTRAP CSS BLOCKERS

These shared components still depend on Bootstrap CSS classes with no project-defined equivalent:

| Rank | Component | Bootstrap Classes Used | Live Consumers |
|:---:|-----------|------------------------|:---:|
| 1 | `forms/form_field.html` | `text-danger` | 3 |
| 2 | `tables/pagination.html` | `pagination`, `justify-content-center`, `page-item`, `page-link` | 0 |
| 3 | `tables/table_actions.html` | `btn-group`, `btn-group-sm` | 0 |

**Total Bootstrap-dependent components:** 3
**Total with live consumers:** 1 (`form_field.html`)

### Class Origin Verification

- `text-danger`: Present in `static/css/vendor/bootstrap.rtl.min.css`. **Absent** from `static/css/tailwind-input.css`.
- `btn-group`, `btn-group-sm`: Present in Bootstrap CSS. **Absent** from `tailwind-input.css`.
- `pagination`, `page-item`, `page-link`, `justify-content-center`: Present in Bootstrap CSS. **Absent** from `tailwind-input.css`.

All other Bootstrap-named classes used by shared components (`badge`, `alert`, `table`, `btn`, `form-input`, `form-select`, etc.) are redefined in `tailwind-input.css` as project component classes and do not require the Bootstrap library.

---

## 4. REMAINING JQUERY BLOCKERS

**None.** No shared component depends on jQuery.

jQuery is loaded only by dashboard/production layouts (`layouts/dashboard.html`, `production/painting_management/base.html`) for inline page scripts, not by any shared component.

---

## 5. MODAL VALIDATION (`modals/modal.html`, `modals/confirm_modal.html`)

### API
| Parameter | Status | Notes |
|-----------|--------|-------|
| `modal_id` | Preserved | DOM id + Alpine component id |
| `title` | Preserved | Rendered in header |
| `size` | Preserved | `sm` / `lg` / `xl` / default |
| `form_id` | Preserved | Optional `<form>` wrapper |
| `form_action` | Preserved | Form action + hidden `next` input |
| `csrf_token` | Preserved | Defaults to `True` |
| `submit_text` | Preserved | Footer submit button |
| `cancel_text` | Preserved | Footer cancel button |
| `submit_class` | Preserved | Appended to submit button |
| `body` | Preserved | Default body content variable |
| `modal_body` block | Added | Overridable block for extends |
| `modal_header` block | Added | Overridable block for extends |
| `modal_footer` block | Added | Overridable block for extends |

### Open / Close Events
- **Open:** `@click="$dispatch('modal:open', '{{ modal_id }}')"` on trigger → `@modal:open.window="if ($event.detail === id) show()"`
- **Close:** ESC key (`@keydown.escape.window="hide()"`), backdrop click, close button, cancel button, `@modal:close.window`
- **Alpine behavior:** `x-data="modal"`, `x-show="open"`, `x-cloak`, `x-transition` enter/leave on backdrop and dialog

### Accessibility
- `role="dialog"`, `aria-modal="true"`, `:aria-labelledby="titleId"`
- `titleId` initialized from `{{ modal_id }}Title`
- Close button has `aria-label="بستن"`
- `tabindex="-1"` on dialog panel
- `focus-visible:ring-2` on close button

### Existing Consumers
**None.** No template in the repository includes `modal.html` or `confirm_modal.html`.

### Defects Found
**None.** The migration from 6.1A is complete and correct.

---

## 6. BADGE VALIDATION (`data/badge.html`)

### API
| Parameter | Status | Notes |
|-----------|--------|-------|
| `text` | Preserved | Rendered content |
| `variant` | Preserved | `primary`, `success`, `warning`, `danger`, `info`, default → neutral |
| `size` | Preserved | `sm`, `lg`, default |
| `class` | Added | Optional passthrough for extra classes |

### Variants
| Variant | Tailwind Tokens | Visual |
|---------|-----------------|--------|
| `primary` | `bg-primary-100 text-primary-800` | Brand tint |
| `success` | `bg-success-100 text-success-800` | Green tint |
| `warning` | `bg-warning-100 text-warning-800` | Amber tint |
| `danger` | `bg-danger-100 text-danger-800` | Red tint |
| `info` | `bg-info-100 text-info-800` | Blue tint |
| default / unknown | `bg-stone-100 text-stone-800` | Neutral stone |

### Tailwind Compilation Safety
- **Explicit mapping** (no dynamic `bg-{{ variant }}` construction). All referenced token utilities are present in `static/css/style.css`.
- Render tests confirmed correct class strings for all variants and sizes.

### Existing Consumers
**None.** No live template includes `components/data/badge.html`.

### Defects Found
**None.** The migration from 6.1B is complete and correct.

---

## 7. DUPLICATION ANALYSIS

Meaningful reusable patterns found duplicated across application templates:

### 7.1 Inline Badges (~50 instances)
Templates use raw `<span class="badge bg-success">`, `<span class="badge bg-warning text-dark">`, etc.
- `production/worker_list.html`, `painting_process_list.html`, `order_list.html`, `order_item.html`
- `painting_management/_worker_rows.html`, `workers.html`, `processes.html`, `assignment_rules.html`
- `production/admin_order_edit.html`, `admin_tasks_management.html`, `admin_order_tasks.html`
- `catalog/product_detail.html`, `cart/detail.html`
- Dynamic variant construction: `bg-{% if process.is_active %}success{% else %}danger{% endif %}` in `processes.html`

**Recommendation:** Migrate to shared `components/data/badge.html`.

### 7.2 Inline Buttons (~50 instances)
Templates use raw `<button class="btn btn-primary">`, `<a class="btn btn-outline-secondary">`, etc.
- `production/painting_management/workers.html`, `stages.html`, `processes.html`
- `production/shop/product_list.html`, `product_detail.html`, `cart.html`, `checkout.html`
- `production/test.html`, `daily_schedule_print.html`

**Note:** The `btn` / `btn-primary` / `btn-outline-*` classes are project-defined in `tailwind-input.css`, so these are not Bootstrap-blocking. But they are still duplicated markup that could be wrapped in a shared button component.

### 7.3 Inline Alerts (29 instances)
Templates use raw `<div class="alert alert-{{ tags }}">` for Django messages and custom notifications.
- `accounts/login.html`, `register.html`, `profile_edit.html`, `password_reset*.html`
- `production/customer/order_detail.html`, `admin_tasks_management.html`
- `catalog/product_detail.html`, `orders/order_form.html`, `discounts/discount_form.html`
- `painting_management/worker_excluded_items.html`, `import_data.html`

**Recommendation:** Migrate to shared `components/feedback/alert.html`.

### 7.4 Inline Modals (7 instances)
Templates use inline Bootstrap modals with `data-bs-toggle="modal"` / `data-bs-target`.
- `production/painting_management/workers.html`, `stages.html`, `processes.html`, `holidays.html`, `assignment_rules.html`
- `production/product_create.html`
- `production/customer/order_detail.html` (collapse, not modal)

**Recommendation:** Migrate to shared `components/modals/modal.html`.

### 7.5 Inline Form Fields
Many templates render raw `<input>`, `<select>`, `<textarea>` without using shared form components.
- `components/forms/form_field.html` has only 3 consumers.

**Recommendation:** Increase adoption of shared form components.

### 7.6 Inline Pagination
No template uses the shared `pagination.html` component. Pagination is either inline or absent.

---

## 8. CONSUMER SUMMARY

| Component | Consumer Count | Consumer Templates |
|-----------|:---:|-------------------|
| `quick_link_card.html` | 11 | `production/dashboard.html` |
| `empty_state.html` | 3 | `home.html`, `catalog/product_list.html`, `cart/detail.html` |
| `form_field.html` | 3 | `production/orders/create_step1.html` |
| All other components | 0 | — |

---

## 9. LAYOUT / LIBRARY LOADING CONTEXT

### `layouts/store.html` (storefront)
- Loads: `style.css` (Tailwind), `vazirmatn-fonts.css`, `product-grid.css`, `components.css`, Alpine.js, HTMX, `app.js`
- **Does NOT load:** Bootstrap CSS, Bootstrap JS, jQuery

### `layouts/dashboard.html` (production / admin)
- Loads: `bootstrap.rtl.min.css`, `bootstrap-icons.css`, `vazirmatn-fonts.css`, `dashboard.css`, `components.css`, Alpine.js, jQuery, `bootstrap.bundle.min.js`, `alpine-bootstrap.js`, `app.js`
- **Loads:** Bootstrap CSS, Bootstrap JS, jQuery

**Implication:** Shared components that depend on Bootstrap CSS classes (`form_field.html`, `table_actions.html`, `pagination.html`) will render unstyled on the storefront if ever used there. Currently they are only consumed within the dashboard layout, so there is no active breakage.

---

## 10. RECOMMENDED NEXT MIGRATION TARGET

Priority order for the next migration phase:

1. **`forms/form_field.html`** — Only 1 component with live consumers (3 usages). Replace `text-danger` with the project-defined `text-danger-600` token class. This removes the last Bootstrap CSS dependency from a consumed shared component.

2. **`tables/pagination.html`** — 0 consumers, but a clear candidate for a pure-Tailwind rewrite using the project's design tokens. Replace Bootstrap pagination classes with Tailwind utilities.

3. **`tables/table_actions.html`** — 0 consumers. Replace `btn-group` / `btn-group-sm` with Tailwind flex/gap utilities.

4. **Inline badges → `data/badge.html`** — 50+ duplicate badge patterns across production templates. High-impact consolidation.

5. **Inline alerts → `feedback/alert.html`** — 29 duplicate alert patterns. The shared component already exists but has 0 consumers.

---

## 11. CONCLUSION

### Component Count
**23** shared components inspected.

### GREEN / YELLOW / RED Breakdown
| Status | Count | Components |
|--------|:---:|-----------|
| GREEN | 13 | Modal, Confirm Modal, Badge, Price, Date, Card, Textarea, Select, Search, Input, Checkbox, Breadcrumb, Empty State |
| YELLOW | 7 | Status Badge, Stat Card, Quick Link Card, Table, Header, Alert, Loading Overlay |
| RED | 3 | Form Field, Table Actions, Pagination |

### Remaining Bootstrap Components
**3** shared components still depend on Bootstrap CSS classes not defined in the project's Tailwind layer:
1. `forms/form_field.html` (`text-danger`) — 3 consumers
2. `tables/pagination.html` (`pagination`, `page-item`, `page-link`, `justify-content-center`) — 0 consumers
3. `tables/table_actions.html` (`btn-group`, `btn-group-sm`) — 0 consumers

### Remaining jQuery Components
**0** shared components depend on jQuery.

### Duplicate UI Patterns
- **Badges:** ~50 inline instances
- **Buttons:** ~50 inline instances
- **Alerts:** ~29 inline instances
- **Modals:** ~7 inline instances
- **Form fields:** Many inline instances

### Recommended Next Migration Target
1. `forms/form_field.html` — remove `text-danger` Bootstrap dependency (3 live consumers)
2. `tables/pagination.html` — rewrite with Tailwind (0 consumers, clear scope)
3. Inline badges → adopt `data/badge.html` (highest duplication impact)

---

**SHARED COMPONENT LIBRARY READY: CONDITIONAL**

The library is structurally sound. 13 of 23 components are fully GREEN. The 3 RED components are isolated, have no cross-cutting dependencies, and two of them have zero live consumers. The modal and badge migrations from 6.1A/6.1B are validated and complete. No application code modifications are required to proceed.
