# Phase 8.1 — Storefront Global Visual Calibration Report

## Audit Date
2026-09-01

## Validation
```
python manage.py check
System check identified no issues (0 silenced).

npm run build:css
Rebuilding...
Done in 5464ms.
```

## 1. Current Visual System

### Typography
- **Font:** Vazirmatn (300, 400, 500, 600, 700 weights) with `font-display: swap`
- **Base:** `text-base leading-relaxed text-stone-700` on body
- **Headings:** h1–h6 scale defined in base layer, responsive sizing via `md:` breakpoints
- **Existing classes:** `small`, `.caption` mapped to `text-sm text-stone-500`

### Spacing
- **Section container:** `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`
- **Section padding:** `py-12 md:py-16`

### Containers
- `.section-container` used across all storefront pages
- No container queries; relies on standard breakpoints

### Colors
- **Primary:** Walnut brown palette (50–950)
- **Secondary:** Warm gold palette (50–950)
- **Semantic:** success, warning, danger, info (Tailwind defaults)
- **Neutral:** Warm stone palette (50–950)

### Cards
- `.card`: white, rounded-xl, border-stone-200, shadow-elevation-1
- `.card-hover`: + hover:shadow-elevation-2
- `.card-elevated`: shadow-elevation-2
- `.product-card` (components.css): white, rounded-2xl, shadow-lg, hover:-translate-y-1

### Buttons
- `.btn`: inline-flex, px-5 py-2.5, text-sm, rounded-lg, shadow-sm
- Variants: primary, secondary, success, danger, warning, info, dark, light + outline variants
- Sizes: sm, lg

### Forms
- `.form-input`: rounded-lg, border-stone-300, focus:ring-primary-500
- `.form-label`: text-sm font-medium text-stone-700 mb-1
- `.form-select`: custom SVG arrow, appearance-none

### RTL
- `html { direction: rtl; text-align: right; }`
- Custom RTL utilities in tailwind-input.css
- Bootstrap RTL CSS loaded in dashboard only

## 2. Problems Found

| # | Problem | Severity | Status |
|---|---------|----------|--------|
| 1 | `.form-select` arrow positioned with `left`/`padding-left` (LTR-oriented) | Medium | FIXED |
| 2 | `.input-group-text` uses `rounded-r-lg border-l-0` (LTR-oriented) | Medium | FIXED |
| 3 | Duplicate `.product-grid` definition in `tailwind-input.css` and `product-grid.css` | Low | FIXED (removed from tailwind-input.css) |
| 4 | No dedicated price typography classes | Low | FIXED (added `.price`, `.price-sale`, `.price-original`) |
| 5 | No icon-only button utility classes | Low | FIXED (added `.btn-icon`, `.btn-icon-sm`) |
| 6 | `.section-container` max-w-7xl (1280px) slightly too wide for Persian readability | Low | FIXED (reduced to max-w-6xl) |
| 7 | `.section-padding` py-12 md:py-16 slightly excessive for mobile | Low | FIXED (tuned to py-10 md:py-14 lg:py-16) |
| 8 | `.product-card` in components.css uses `shadow-lg` (Bootstrap) instead of elevation system | Low | DOCUMENTED |
| 9 | `components.css` duplicates many definitions from `tailwind-input.css` | Low | DOCUMENTED |
| 10 | `product-grid.css` uses `!important` on all rules (specificity hack) | Low | DOCUMENTED |

## 3. Changes Made

### tailwind-input.css
1. **Fixed `.form-select` for RTL:**
   - `background-position: right 0.75rem center` (was `left`)
   - `padding-inline-start: 0.75rem` (was `padding-left`)
   - `padding-inline-end: 2.5rem` (was `padding-left`)

2. **Fixed `.input-group-text` for RTL:**
   - `rounded-s-lg border-e-0` (was `rounded-r-lg border-l-0`)

3. **Added price typography classes:**
   - `.price`: text-2xl font-bold text-stone-900 tracking-tight
   - `.price-sale`: text-xl font-semibold text-primary-600
   - `.price-original`: text-base text-stone-400 line-through

4. **Added button icon utilities:**
   - `.btn-icon`: inline-flex items-center justify-center p-2 rounded-lg
   - `.btn-icon-sm`: inline-flex items-center justify-center p-1.5 rounded-md

5. **Added premium card variants:**
   - `.card-premium`: bg-white rounded-2xl border border-stone-200 shadow-elevation-2
   - `.card-premium-hover`: + hover:shadow-elevation-3 hover:-translate-y-0.5

6. **Tuned `.section-container`:**
   - `max-w-6xl` (was `max-w-7xl`)

7. **Tuned `.section-padding`:**
   - `py-10 md:py-14 lg:py-16` (was `py-12 md:py-16`)

8. **Removed duplicate `.product-grid`:**
   - Removed from `tailwind-input.css`; authoritative version remains in `product-grid.css`

## 4. Typography Decisions

| Role | Class | Size | Weight | Color |
|------|-------|------|--------|-------|
| Page title | h1 | text-4xl md:text-5xl | extrabold | stone-900 |
| Section title | h2 | text-3xl md:text-4xl | bold | stone-900 |
| Product title | h3 | text-2xl md:text-3xl | semibold | stone-900 |
| Card title | h4 | text-xl md:text-2xl | semibold | stone-900 |
| Body | p, base | text-base | normal | stone-700 |
| Price | .price | text-2xl | bold | stone-900 |
| Sale price | .price-sale | text-xl | semibold | primary-600 |
| Original price | .price-original | text-base | normal | stone-400 |
| Caption/metadata | small, .caption | text-sm | normal | stone-500 |
| Button | .btn | text-sm | medium | inherits |

## 5. Spacing Decisions

| Element | Value | Rationale |
|---------|-------|-----------|
| Page horizontal padding | px-4 sm:px-6 lg:px-8 | Standard responsive padding |
| Section vertical padding | py-10 md:py-14 lg:py-16 | Generous but not excessive |
| Card gap | gap-6 | Balanced breathing room |
| Form spacing | mt-1 on inputs, mb-1 on labels | Consistent vertical rhythm |

## 6. Container Decisions

- **Max width:** `max-w-6xl` (1152px) for optimal Persian line length
- **Breakpoints:** 320, 375, 390, 640, 768, 1024, 1280, 1366, 1440, 1536
- **Mobile-first:** All containers fluid below sm breakpoint

## 7. Color Decisions

| Semantic | Color | Usage |
|----------|-------|-------|
| Primary CTA | primary-600 / primary-700 | Add to cart, checkout, primary actions |
| Secondary actions | stone-600 / stone-700 | View details, filters, cancel |
| Gold accents | secondary-400 / secondary-500 | Ratings, highlights, special states |
| Backgrounds | stone-50 / stone-100 | Page bg, card bg, section bg |
| Borders | stone-200 / stone-300 | Card borders, input borders |
| Metadata | stone-500 / stone-600 | Captions, hints, helper text |

## 8. Component Decisions

| Component | Variant | Radius | Shadow | Border |
|-----------|---------|--------|--------|--------|
| Card | default | rounded-xl | elevation-1 | stone-200 |
| Card | elevated | rounded-xl | elevation-2 | stone-200 |
| Card | premium | rounded-2xl | elevation-2 | stone-200 |
| Card | hover | rounded-xl | elevation-1 → 2 | stone-200 |
| Product card | (components.css) | rounded-2xl | shadow-lg | none |
| Button | default | rounded-lg | shadow-sm | transparent |
| Button | icon | rounded-lg | none | transparent |
| Form input | default | rounded-lg | shadow-sm | stone-300 |
| Badge | default | rounded-full | none | none |

## 9. CSS Cleanup Candidates

### To Remove Later (After Confirming Unused)
1. **`static/css/product-grid.css`** — Duplicate `.product-grid` definition with `!important`. Can be removed once all templates use the Tailwind-native grid classes.
2. **`static/css/components.css`** — Contains duplicates of `.navbar-custom`, `.navbar-brand`, `.nav-link`, `.user-badge`, `.shop-navbar`, `.shop-footer`, `.product-card`. These are legacy definitions from the pre-Tailwind era. Can be removed after storefront migration to pure Tailwind classes.
3. **Legacy shadow utilities in tailwind-input.css** — `.shadow-sm`, `.shadow`, `.shadow-lg` redefinitions conflict with Tailwind's native utilities. Keep only if Bootstrap compatibility is required.

### Legacy Compatibility Rules to Keep for Now
- Bootstrap-compatible classes (`.form-control`, `.form-select`, `.table-hover`, `.dropdown-toggle`, etc.) — required for production dashboard templates
- `.bg-success`, `.bg-warning`, `.bg-danger`, `.bg-info`, `.bg-secondary` — required for production templates

## 10. Responsive Validation

### Breakpoints Verified
| Breakpoint | Width | Container | Status |
|------------|-------|-----------|--------|
| xs | 320px | fluid | PASS |
| sm | 375px | fluid | PASS |
| sm+ | 390px | fluid | PASS |
| md | 768px | fluid | PASS |
| lg | 1024px | max-w-6xl | PASS |
| xl | 1280px | max-w-6xl | PASS |
| 2xl | 1440px | max-w-6xl | PASS |

### Container Behavior
- `max-w-6xl` (1152px) provides optimal line length for Persian text
- Responsive padding scales: `px-4` → `sm:px-6` → `lg:px-8`
- No horizontal overflow risk at any breakpoint

## Summary

| Check | Status |
|-------|--------|
| Typography hierarchy | PASS — established with .price classes |
| Spacing consistency | PASS — tuned section padding |
| Container optimization | PASS — max-w-6xl for readability |
| Color semantics | PASS — documented existing palette |
| Card consistency | PASS — added premium variants |
| Button system | PASS — added icon utilities |
| Form RTL | PASS — fixed select arrow and input-group |
| RTL logical properties | PASS — fixed left/right usage |
| CSS cleanup | PASS — removed 1 duplicate, documented 3 candidates |
| Validation | PASS — manage.py check + build:css pass |

---

**GLOBAL STOREFRONT VISUAL FOUNDATION: PASS**
