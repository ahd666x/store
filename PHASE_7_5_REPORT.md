# Phase 7.5 — Accessibility Report

## Audit Date
2026-08-31

## Audit Method
Code-based audit of HTML templates for accessibility patterns. No automated accessibility testing tools were used.

## 1. Semantic HTML
### Headings
- All major sections use semantic headings (`<h1>` through `<h3>`)
- Homepage has single `<h1>` per section
- Product detail has single `<h1>` for product name
- No skipped heading levels found

### Landmarks
- `<header>` used in `includes/header.html`
- `<nav>` used for navigation menus
- `<main>` content area present in layouts
- `<footer>` used in `includes/footer.html`
- Tables use `<thead>` and `<tbody>`

**Result:** Semantic HTML is good.

## 2. Labels & Form Associations
### Login Form (`accounts/login.html`)
- `<label for="id_username">` — correct association
- `<label for="id_password">` — correct association
- `autofocus` on username field

### Product Detail Form (`catalog/product_detail.html`)
- Dimension inputs have `<label>` elements but no `for` attributes
- `<label class="form-label">طول</label>` without `for="dim-length"` — **ISSUE**
- Same for width and height labels

### Review Form (`catalog/product_detail.html`)
- `<label for="comment">` — correct
- `<label for="review_image">` — correct
- Rating select has `<label>` without `for` — minor

### Workers Form (`production/painting_management/workers.html`)
- All inputs have associated labels via `for` attributes
- Checkbox inputs have `for` attributes on labels

**Result:** Minor label association issues in product detail form.

## 3. Buttons vs Links
- `<button>` used for form submissions and actions
- `<a>` used for navigation
- No buttons used as links or vice versa
- Icon-only buttons have `aria-label` attributes

**Result:** Correct button/link usage.

## 4. ARIA Labels
### Present
- Search inputs: `aria-label="جستجو"`
- Mobile menu button: `aria-label="منوی موبایل"`
- User menu button: `aria-label="منوی کاربر"`
- Toast: `role="alert" aria-live="assertive" aria-atomic="true"`
- Breadcrumb: `aria-label="breadcrumb"`
- Pagination: `aria-label="Page navigation"`

### Missing
- Icon-only action buttons in workers table (edit, delete, exclusion) — have `title` but no `aria-label`
- Product card quick-view button — no `aria-label`
- Size guide close button — no `aria-label`

**Result:** ARIA labels are mostly present; minor gaps in icon-only buttons.

## 5. aria-expanded / aria-controls
- User menu dropdown: `aria-expanded="false"` on toggle button
- Mobile menu: no `aria-expanded` on hamburger button
- Dropdown toggles in workers table: `aria-expanded="false"` — correct

**Result:** Mostly correct; mobile menu missing `aria-expanded`.

## 6. Focus States
- `*:focus-visible` styled in `tailwind-input.css` with `ring-2 ring-offset-2 ring-primary-500`
- Alpine modal component attempts to focus first focusable element on show
- No skip-to-content link found

**Result:** Focus states are styled; no skip link.

## 7. Keyboard Navigation
- Native form controls are keyboard accessible
- Dropdowns use Bootstrap's keyboard support
- Alpine dropdowns use click-outside but no explicit keyboard handling
- No custom keyboard traps found

**Result:** Keyboard navigation is functional.

## 8. Modal Focus
- Alpine modal component (`alpine-bootstrap.js`) focuses first focusable element on open
- Bootstrap modals trap focus by default
- No modal focus escape issues found

**Result:** Modal focus is handled.

## 9. Dropdown Keyboard Behavior
- Bootstrap dropdowns have built-in keyboard support (Enter, Space, Esc, Arrow keys)
- Alpine dropdowns do not have explicit keyboard handlers
- **Gap:** Alpine dropdowns may not close on Esc key

**Result:** Bootstrap dropdowns are accessible; Alpine dropdowns have minor keyboard gap.

## 10. Color Contrast
- No automated contrast testing performed
- Tailwind color palette uses stone neutrals with primary-600 for text
- Text colors appear to meet WCAG AA based on standard Tailwind palette
- Warning/info badges use Bootstrap colors

**Result:** Likely passes; no automated verification.

## 11. Error Messages
- Forms use Django's default error rendering
- `alert alert-danger` used for form errors
- No explicit `aria-describedby` linking errors to inputs
- Stock alert form uses `alert` for success/error states

**Result:** Error messages are visible; could be improved with `aria-describedby`.

## 12. Loading States
- Loading overlay component exists (`components/loading/loading_overlay.html`)
- Button loading state CSS (`.btn.is-loading`) exists in `tailwind-input.css`
- No loading states found on form submissions or async actions

**Result:** Loading infrastructure exists but not widely used.

## 13. Screen-Reader Text
- `visually-hidden` class used in spinner: `<span class="visually-hidden">در حال پردازش...</span>`
- No other `sr-only` or `visually-hidden` text found

**Result:** Minimal screen-reader text usage.

## Issues to Fix

### Confirmed Issues
1. **Product detail form labels missing `for` attributes** (`catalog/product_detail.html` lines 220, 228, 237)
   - Fix: Add `for="dim-length"`, `for="dim-width"`, `for="dim-height"` to labels

### Recommended (Low Priority)
1. Add `aria-label` to icon-only action buttons in workers table
2. Add `aria-expanded` to mobile menu toggle
3. Add `aria-describedby` to form inputs with error messages
4. Add skip-to-content link
5. Add keyboard handler (Esc) to Alpine dropdowns

## Summary
| Check | Status |
|-------|--------|
| Semantic HTML | PASS |
| Labels | Minor issues |
| Buttons vs links | PASS |
| aria-label | Mostly present |
| aria-expanded | Minor gaps |
| Focus states | PASS |
| Keyboard navigation | PASS |
| Modal focus | PASS |
| Dropdown keyboard | Minor gap |
| Color contrast | Likely PASS |
| Error messages | Visible, could improve |
| Loading states | Infrastructure exists |
| Screen-reader text | Minimal |
