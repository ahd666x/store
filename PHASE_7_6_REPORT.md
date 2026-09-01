# Phase 7.6 — Performance + Final Cleanup Report

## Audit Date
2026-08-31

## 1. CSS Bundle Size
- `static/css/style.css` — Compiled Tailwind output (minified). Size not measured in this environment.
- `static/css/tailwind-input.css` — Source: ~2481 lines
- Additional CSS files: `dashboard.css` (23 lines), `components.css` (148 lines), `product-grid.css`, `vazirmatn-fonts.css`, `pages/*.css`
- Vendor CSS: `bootstrap.rtl.min.css`, `bootstrap-icons.css`, `select2.min.css`, `select2-bootstrap-5-theme.min.css`

## 2. JS Bundle Size
- App entry: `app.js` (70 lines)
- Production modules: ~15 JS files averaging 100-200 lines each
- Vendor JS: `jquery-3.7.1.min.js`, `bootstrap.bundle.min.js`, `alpinejs.min.js`, `htmx.min.js`, `select2.min.js`
- Total custom JS: ~1500 lines across all modules

## 3. Duplicate Assets
No duplicate asset files found. Each CSS/JS file serves a distinct purpose.

## 4. Globally Loaded Modules
### Store Layout (`layouts/store.html`)
- Loads: `style.css`, `vazirmatn-fonts.css`, `components.css`, `alpinejs.min.js`, `htmx.min.js`, `app.js`
- Plus page-specific modules via `extra_js` block

### Dashboard Layout (`layouts/dashboard.html`)
- Loads: `style.css`, `dashboard.css`, `components.css`, `vazirmatn-fonts.css`, `bootstrap.rtl.min.css`, `bootstrap-icons.css`, `jquery-3.7.1.min.js`, `bootstrap.bundle.min.js`, `alpinejs.min.js`, `app.js`
- Plus page-specific modules

## 5. Unused Bootstrap CSS
Bootstrap CSS is still actively used in production templates. See Phase 7.2 report.

## 6. Unused jQuery
jQuery is used exclusively for Select2 in the workers management page. Select2 requires jQuery. jQuery is confirmed required.

## 7. Select2 Usage
- Select2 is loaded ONLY on `production/painting_management/workers.html`
- Used for the exclusion multi-select with AJAX search
- Confirmed required; cannot be removed without replacing with custom solution

## 8. Image Loading
- Product images use `loading="lazy"` attribute
- No responsive image attributes (`srcset`, `sizes`) found
- No WebP/AVIF formats detected
- Missing `static/images/` directory (templates reference `og-default.png` and `favicon.svg`)

## 9. Font Loading
- Vazirmatn fonts loaded via CSS (`vazirmatn-fonts.css`)
- 5 font files (TTF) for different weights/styles
- `font-display` not explicitly set — may cause FOIT (Flash of Invisible Text)
- No font subsetting

## 10. Render-Blocking Assets
- CSS files loaded in `<head>` — standard practice
- JS files loaded with `defer` attribute — good
- No render-blocking issues found

## 11. Unnecessary DOM
- No excessive wrapper divs found
- Template includes are used appropriately
- Component architecture is reasonable

## 12. Duplicated Markup
- Star rating SVG repeated in multiple templates (home.html, product_detail.html, product_card.html)
- Icon SVG includes via `includes/icons.html` — good reuse
- Product card markup duplicated between inline and include versions

## Dependencies Remaining
| Dependency | Status | Notes |
|------------|--------|-------|
| Bootstrap CSS | REQUIRED | Used in production templates |
| Bootstrap JS | REQUIRED | Modals, dropdowns in production |
| jQuery 3.7.1 | REQUIRED | Select2 dependency |
| Select2 | REQUIRED | Workers exclusion select |
| Alpine.js | REQUIRED | UI interactivity |
| HTMX | REQUIRED | Partial updates (cart) |
| Tailwind CSS | REQUIRED | Core styling |

## Performance Recommendations
1. **Font loading:** Add `font-display: swap` to Vazirmatn font-face declarations
2. **Responsive images:** Add `srcset`/`sizes` to product images
3. **Missing assets:** Add `static/images/og-default.png` and `static/images/favicon.svg`
4. **CSS purging:** Consider using Tailwind's `content` scanning more aggressively to reduce bundle size
5. **JS code splitting:** Not practical without a bundler; current approach is acceptable for project scale

## Cleanup Actions Taken
- Removed 3 dead templates (Phase 7.1)
- Removed duplicate template rows and fixed invalid HTML (Phase 7.1)
- Removed duplicate JS initialization listeners (Phase 7.3)

## Summary
| Check | Status |
|-------|--------|
| CSS bundle | Compiled successfully |
| JS bundle | No dead code found |
| Duplicate assets | None |
| Bootstrap CSS | Confirmed required |
| jQuery | Confirmed required |
| Select2 | Confirmed required |
| Image loading | lazy loading present; srcset missing |
| Font loading | Missing font-display: swap |
| Render-blocking | None |
| Unnecessary DOM | None |
| Duplicated markup | Minor (SVG stars) |
