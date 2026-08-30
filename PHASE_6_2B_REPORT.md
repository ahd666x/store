# PHASE 6.2B — STOREFRONT HOME PAGE MIGRATION REPORT

**Project:** store (دکارو / سلوی چوب)
**Scope:** Storefront Home page only (`templates/home.html`)
**Date:** 2026-08-30

---

## 1. Files Changed

| File | Change |
|------|--------|
| `templates/home.html` | Removed inline `style=`, inline `onclick`, inline `onsubmit`/`alert`; rewired add-to-cart to the real `Cart.add()` via Alpine `@click`; replaced testimonials inline scrollbar style with the `scrollbar-thin` design-system class; converted the newsletter form to Alpine `@submit.prevent` + `x-show` message |

No Python, views, URLs, context, APIs, product queries, auth, or cart business logic were modified. No new components were created (existing ones reused).

The Home template was already on Tailwind + Alpine + the project design system; the work was to eliminate the **legacy inline CSS/JS** and a **broken global function call** that the page relied on.

---

## 2. Components Reused

- `templates/catalog/includes/product_card.html` — reused via `{% include %}` for the "پیشنهادهای ما برای شما" (recommendations) section. **No duplicate card markup created.**
- `templates/components/feedback/empty_state.html` — reused for the "no featured products" fallback (via `{% include %}` with `icon_svg`, `message`, `action_url`, `action_text`).
- Project design-system classes (defined in `static/css/tailwind-input.css` → compiled into `static/css/style.css`): `btn-primary`, `btn-secondary`, `btn-lg`, `badge-danger`, `badge-warning`, `card-hover`, `section-container`, `section-padding`, `scrollbar-thin`, `me-2`.

---

## 3. Bootstrap Removed

The page contained **no Bootstrap library CSS or JS** before or after. A targeted scan for classic Bootstrap utility classes returned **zero** matches: `container`, `row`, `col-*`, `d-flex`, `d-none`, `alert`, `modal`, `form-control`, `form-select`, `btn-close`, `navbar`, bare `badge`.

The remaining class names (`btn-primary`, `badge-danger`, `me-2`, `card-hover`, `section-container`, `section-padding`) are the **project's own Tailwind component/utility classes** (defined in `tailwind-input.css`), not Bootstrap. They were intentionally retained per the instructions to *use the existing design system* and *reuse components*, not duplicate them.

`data-bs-*` attributes: **none** in the page.

---

## 4. jQuery Removed

No jQuery was used on the page (no `$()` / `jQuery`). The add-to-cart button previously called a global `addToCart(...)`, which **did not exist anywhere** in the codebase (a latent bug). It now correctly invokes `Cart.add(productId)` (defined in `static/js/store/cart.js`, loaded globally by the layout) via Alpine `@click`. Still jQuery-free.

---

## 5. Inline CSS Removed

| Before | After |
|--------|-------|
| `<div ... style="scrollbar-width: thin;">` (testimonials scroller) | `<div ... scrollbar-thin">` (project class, equivalent behavior) |

No other `style=` attributes existed in the template.

---

## 6. Inline JS Removed

| Before | After |
|--------|-------|
| `<button onclick="addToCart({{ product.id }})">` (broken global) | `<button @click="Cart.add({{ product.id }})">` (Alpine; calls real cart API, updates `#cart-count-home`) |
| `<form ... onsubmit="event.preventDefault(); alert('این قابلیت به زودی فعال می‌شود.');">` | `<div x-data="{ comingSoon: false }"><form ... @submit.prevent="comingSoon = true"> … <p x-show="comingSoon" x-cloak>این قابلیت به زودی فعال می‌شود.</p></div>` |

The JSON-LD `<script type="application/ld+json">` SEO block was **preserved** (it is structured data, not behavioral JS, and is required SEO infrastructure per the preservation list).

---

## 7. Responsive Validation

- **Mobile → Tablet → Desktop:** section grids use `grid-cols-1` → `sm:grid-cols-2` → `lg:grid-cols-4` (featured/recommendations) and `md:grid-cols-4` (categories) / `md:grid-cols-3` (features); hero CTAs use `flex-col sm:flex-row`; testimonials use `min-w-[300px] md:min-w-[400px]` with `overflow-x-auto snap-x`.
- **RTL preserved:** `<html dir="rtl">` is set by the layout; the page uses logical/start-end utilities (`start-3`, `me-2`) and symmetric padding, so direction is unaffected.
- Horizontal testimonial scroller retains `overflow-x-auto` + `scrollbar-thin` for touch/desktop scrolling.

---

## 8. Django Check

```
System check identified no issues (0 silenced).
```

Additional validation performed:
- Rendered `home.html` with a request context (anonymous user, real session, stub `categories`/`featured_products`). Confirmed: compiles, `cart-count-home` present, `Cart.add(` wired, `addToCart` (old) absent, `@submit.prevent` + `comingSoon` present, `scrollbar-thin` present, **no** `style=`/`onclick`/`onsubmit`/`data-bs-`/jQuery leaks, JSON-LD SEO block retained, recommendations block correctly hidden for anonymous users, no classic Bootstrap utility classes.

---

## Conclusion

HOME MIGRATION COMPLETE: YES
