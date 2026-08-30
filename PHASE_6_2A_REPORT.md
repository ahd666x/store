# PHASE 6.2A — STOREFRONT LAYOUT MIGRATION REPORT

**Project:** store (دکارو / سلوی چوب)
**Scope:** Storefront layout infrastructure only (no pages)
**Date:** 2026-08-30

---

## 1. Layout Inheritance — BEFORE

```
templates/layouts/store.html        (root storefront layout)
        ▲
        │  {% extends %}
templates/base.html                  (1-line shim: {% extends 'layouts/store.html' %})
        ▲
        │  {% extends 'base.html' %}
┌───────┴──────────────────────────────────────────────────────────────┐
accounts/*, orders/*, catalog/* (most), cart/detail.html,              │
discounts/*, communications/*, payments/*, catalog/stock_alerts.html    │
└──────────────────────────────────────────────────────────────────────┘

Directly extends layouts/store.html (bypassing base.html):
  templates/home.html
  templates/catalog/product_list.html
```

Included partials (shared layout chrome):
- `templates/includes/header.html` (logo, nav, search, user menu, cart indicator, mobile menu — Alpine.js)
- `templates/includes/footer.html`
- `templates/includes/toast.html` (Django `messages` → Alpine toast)
- `templates/includes/cart-actions.html` (loads `js/store/cart.js`)
- `templates/includes/icons.html` (SVG icon set)

## 2. Layout Inheritance — AFTER

**Unchanged.** No template-level restructuring was required — the storefront layout was already built on the modern stack (Tailwind + Alpine.js + HTMX). Inheritance tree and `{% extends %}` relationships are identical to BEFORE.

---

## 3. Assets — BEFORE

`layouts/store.html` `<head>`/`<body>` loaded:
- CSS: `css/style.css` (compiled Tailwind), `css/vazirmatn-fonts.css`, `css/product-grid.css`, `css/components.css`
- Inline: `[x-cloak]{display:none!important}`
- JS (vendor): `js/vendor/alpinejs.min.js`, `js/vendor/htmx.min.js`
- JS (app): `js/app.js` (module), `js/store/cart.js` (via `cart-actions.html`)
- `{% block extra_head %}` / `{% block extra_js %}` for page extensions

`js/app.js` contained an **inert** jQuery + Select2 block:
```js
document.querySelectorAll('.select2-ajax').forEach(select => {
    if (typeof $ !== 'undefined' && $.fn.select2) {
        $(select).select2({ theme: 'bootstrap-5', ... ajax ... });
    }
});
```
This was guarded (`typeof $ !== 'undefined'`), so it never executed under the storefront (jQuery/Select2 are **not** loaded by this layout), but it was the only jQuery/Bootstrap reference in any storefront-loaded asset.

## 4. Assets — AFTER

- **No** Bootstrap CSS, Bootstrap JS, or jQuery is loaded by the storefront layout (confirmed by exhaustive sweep).
- `js/app.js`: the guarded jQuery/Select2/`bootstrap-5` block was **removed**. The file now contains zero jQuery, Select2, or Bootstrap references and passes `node --check`.
- Remaining vendor JS in the layout: `alpinejs.min.js`, `htmx.min.js` — both part of the target modern architecture.
- All CSS, blocks, SEO meta, CSRF/HTMX config, and static asset loading are unchanged.

---

## 5. Bootstrap Dependencies Removed

| Where | Dependency | Status |
|-------|-----------|--------|
| `layouts/store.html` | Bootstrap CSS/JS | **Never loaded** — already absent |
| `base.html` | Bootstrap CSS/JS | **Never loaded** — just extends `store.html` |
| `includes/header|footer|toast|cart-actions|icons.html` | Bootstrap CSS/JS/jQuery | **None present** — already Alpine + Tailwind |
| `static/js/app.js` | jQuery + Select2 (`theme: 'bootstrap-5'`) | **REMOVED** (inert guarded block) |

**Important scope note:** Bootstrap remains intentionally present in the **Dashboard** layout (`layouts/dashboard.html` → `css/vendor/bootstrap.rtl.min.css`, `js/vendor/jquery-3.7.1.min.js`, `js/vendor/bootstrap.bundle.min.js`) and the **Production** area (`templates/production/**` loads jQuery + Bootstrap bundle + Select2). These are explicitly **out of scope** for this task and were **not** touched, per the instruction "Do not remove Bootstrap globally."

---

## 6. JS Dependencies (after migration)

`js/app.js` (loaded by the storefront layout) now wires only vanilla-JS + Alpine components, all guarded/self-contained:
- `Cart`, `Catalog` (price calc, filters, clickable rows), `Scanner`, `Kanban`, `Orders`, `OrderItem`
- `Workers` (only initializes if `#workerTableBody` + `WORKERS_BASE` exist)
- `CascadeSelect`, `ColorFields` (including the `.size-rule-preset` sync logic, kept intact)

Navigation/dropdowns are handled by the existing Alpine component in `includes/header.html` (`x-data="{ mobileMenuOpen, userMenuOpen }"`, `x-show`, `@click.away`) — reused, not duplicated. No new JS components were created.

---

## 7. Affected Templates / Files

| File | Change |
|------|--------|
| `static/js/app.js` | Removed inert jQuery/Select2/`bootstrap-5` block (only code change) |
| `templates/layouts/store.html` | No change (already Bootstrap-free) |
| `templates/base.html` | No change |
| `templates/includes/header.html` | No change (Alpine + Tailwind) |
| `templates/includes/footer.html` | No change (Tailwind) |
| `templates/includes/toast.html` | No change (Alpine + Tailwind) |
| `templates/includes/cart-actions.html` | No change |
| `templates/includes/icons.html` | No change |

No pages, models, views, URLs, APIs, business logic, or DB were modified.

---

## 8. Tests

1. **Exhaustive Bootstrap sweep** — grepped every `.html`/`.css`/`.js` under `templates/` and `static/` (excluding `node_modules`, `venv`, `worktrees`). The only `bootstrap`/`jquery`/`select2`/`popper` hits are in `dashboard.html`, `production/**`, and their `static/css|js/vendor` files — all out of scope. The storefront layout + its includes + `components/*` contain **zero** such references (only "Bootstrap-free" comments).
2. **`node --check static/js/app.js`** → OK (valid syntax after edit).
3. **`python manage.py check`** → *System check identified no issues (0 silenced).*
4. **Layout render test** — rendered `base.html` with a request context (anonymous user, real session, messages storage). Verified:
   - Alpine dropdowns present (`x-data`, `x-show`) ✅
   - Cart indicator (`cart-count`) present ✅
   - Auth links (`ورود` / `ثبت‌نام`) present ✅
   - Messages/toast container present (`z-[1100]` / `pointer-events-none`) ✅
   - CSRF/HTMX handler (`htmx:configRequest`) present ✅
   - Tailwind `css/style.css` loaded; Alpine + HTMX vendor scripts loaded ✅
   - **No leaks**: `bootstrap`, `jquery`, `select2`, `popper`, `data-bs-` absent from rendered HTML ✅
   - Only `js/vendor` scripts are Alpine.js and HTMX (allowed) ✅

---

## 9. Django Check

```
System check identified no issues (0 silenced).
```

---

## Conclusion

STOREFRONT LAYOUT MIGRATION COMPLETE: YES

*Notes:* The storefront layout was already on the modern Tailwind + Alpine.js + HTMX architecture; the only concrete change was removing an inert jQuery/Select2 block from the layout's `app.js`. Bootstrap/JQuery were confirmed absent from the entire storefront layout chain. Bootstrap remains only in the Dashboard and Production layouts, which are out of scope and were intentionally left intact.
