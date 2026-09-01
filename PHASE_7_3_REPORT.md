# Phase 7.3 — JavaScript QA Report

## Audit Date
2026-08-31

## Files Audited
- `static/js/app.js` — Entry point
- `static/js/alpine-bootstrap.js` — Alpine components
- `static/js/core/csrf.js` — CSRF helper
- `static/js/store/catalog.js` — Catalog logic
- `static/js/store/cart.js` — Cart logic
- `static/js/production/scanner.js` — Scanner
- `static/js/production/kanban.js` — Kanban board
- `static/js/production/workers.js` — Workers management
- `static/js/production/orders.js` — Orders batch actions
- `static/js/production/order_item.js` — Order item cascading selects
- `static/js/production/bom.js` — BOM editor
- `static/js/production/painting/*.js` — Painting modules
- `static/js/vendor/*` — Vendored libraries

## Issues Found & Fixed

### 1. Duplicate Initialization (FIXED)
Multiple modules had their own `DOMContentLoaded` listeners AND were also initialized from `app.js`, causing duplicate execution.

| File | Issue | Fix |
|------|-------|-----|
| `store/catalog.js` | `DOMContentLoaded` listener calling `Catalog.initPriceCalc()`, `initFilters()`, `initClickableRows()` — same methods called from `app.js` | Removed duplicate listener |
| `production/workers.js` | `DOMContentLoaded` listener calling `Workers.init()` — also called conditionally from `app.js` | Removed duplicate listener; kept `change` listener for `updateSkillsHidden()` |
| `production/orders.js` | `DOMContentLoaded` listener calling `Orders.init()` — also called from `app.js` | Removed duplicate listener |
| `production/order_item.js` | `DOMContentLoaded` listener calling `OrderItem.init()` — also called from `app.js` | Removed duplicate listener |

### 2. Race Conditions
No race conditions found. All async operations use proper promise chains with error handling.

### 3. Global Variables
Confirmed globals (intentional pattern):
- `window.WorkersModal` — Modal helper for workers page
- `window.WORKERS_BASE` — API base URL for workers
- `window.SEARCH_PRODUCTS_URL` — Search API URL
- `window.SEARCH_ITEMS_URL` — Search API URL
- `window.BOMConfig` — BOM configuration
- `Cart`, `Catalog`, `Scanner`, `Kanban`, `Orders`, `OrderItem`, `Workers`, `BOM`, `PaintingStages`, `PaintingReadyList`, `PaintingHolidays`, `PaintingProcesses`, `PaintingAssignmentRules` — Module singletons

No unintended globals found.

### 4. HTMX Usage
- `cart.js` correctly uses `htmx.ajax()` for cart add
- `cart.js` correctly listens to `htmx:afterSwap` to sync cart counts across badges
- HTMX partial swap reinitialization: No additional reinitialization needed for cart (handled by afterSwap)
- No HTMX-related race conditions found

### 5. Alpine.js
- `alpine-bootstrap.js` defines `navbar`, `modal`, `dropdown`, `alert`, `toast` components
- Global click-outside handler for dropdowns uses `[x-data*="dropdown"]` selector — works but is broad
- No Alpine initialization issues found

### 6. jQuery Usage
- jQuery 3.7.1 is vendored and loaded in `dashboard.html`
- Used exclusively for Select2 initialization in `workers.js`
- No other jQuery usage found in custom JS

### 7. Select2
- Select2 is loaded only on the workers management page (`production/painting_management/workers.html`)
- Initialized via `$(exclusionSelect).select2(...)` with AJAX search
- Properly guarded with `typeof $.fn.select2 !== 'undefined'`
- Select2 is confirmed required for the exclusion multi-select

### 8. Bootstrap JS
- Bootstrap JS is loaded in `dashboard.html` and `painting_management/base.html`
- Used for: modals (`bootstrap.Modal`), dropdowns (`data-bs-toggle="dropdown"`)
- No other Bootstrap JS usage found

### 9. Scanner Module
- `scanner.js` handles barcode scanning for CNC and DR files
- Uses `fetch` with FormData
- Properly handles blob downloads
- Error handling includes network errors and reloads page on failure
- No race conditions; each form has its own submit handler

### 10. Kanban Module
- Drag-and-drop implementation using native HTML5 drag events
- `localStorage` persistence for moved task IDs
- Proper cleanup on dragend
- Reset button uses fetch with CSRF token
- No race conditions

### 11. Workers Module
- CRUD operations via fetch API
- Select2 integration for exclusion management
- Table row updates via `TableManager` helper
- Proper error handling
- No console.error calls

### 12. BOM Module
- Dynamic row cloning with proper form field renaming
- Size-rule preset logic duplicated from `app.js` (both work independently)
- Modal integration with Bootstrap
- No race conditions

### 13. Console Errors
No `console.error`, `console.warn`, or `console.log` calls found in any custom JS module.

## Summary
| Check | Status |
|-------|--------|
| Duplicate initialization | FIXED (4 modules) |
| Race conditions | None found |
| Global variables | Intentional only |
| HTMX events | Correct usage |
| Alpine initialization | Correct |
| jQuery usage | Select2 only (confirmed required) |
| Select2 | Confirmed required |
| Bootstrap JS | Confirmed required |
| Scanner | No issues |
| Kanban | No issues |
| Workers | No issues |
| BOM | No issues |
| Console errors | None |
