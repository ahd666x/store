# JavaScript Architecture - Phase 5

## Overview

This document describes the JavaScript architecture for the Django + HTMX + Alpine.js + Vanilla JS stack. The goal is a clean, modular architecture without converting the project into an SPA.

## Responsibility Matrix

| Technology | Responsibility |
|------------|---------------|
| **HTMX** | Server communication, partial page updates, form submissions, navigation |
| **Alpine.js** | Local UI state (mobile menus, modals, dropdowns, toasts, tabs, collapse) |
| **Vanilla JS (modules)** | Reusable browser behavior, complex interactions, event delegation |
| **jQuery** | Legacy only - being gradually removed where safe |
| **Select2** | Remaining for worker exclusion search (Select2 AJAX) |
| **Bootstrap JS** | Remaining for modals, dropdowns, toast where not yet replaced by Alpine |

## Directory Structure

```
static/js/
├── app.js                          # Main initialization entry point
├── vendor/
│   ├── htmx.min.js                 # HTMX library
│   ├── alpinejs.min.js             # Alpine.js library
│   ├── bootstrap.bundle.min.js     # Bootstrap JS (modals, dropdowns, toast)
│   ├── jquery-3.7.1.min.js         # jQuery (legacy, being phased out)
│   ├── select2.min.js              # Select2 (remaining for worker exclusions)
│   └── ...
├── core/
│   └── csrf.js                     # CSRF token utilities
├── components/
│   ├── toast.js                    # Toast notification system
│   └── loading.js                  # Loading overlay utilities
├── store/
│   ├── cart.js                     # Cart interactions (HTMX-based)
│   └── catalog.js                  # Product catalog (filters, price calc, clickable rows)
├── forms/
│   ├── cascade.js                  # Category → Product cascading selects
│   └── colors.js                   # Product color field filtering
└── production/
    ├── scanner.js                  # Barcode/part scanning & packaging unit
    ├── kanban.js                   # Painting schedule kanban board (drag-drop)
    ├── workers.js                  # Worker management (modals, exclusions, table)
    └── bom.js                      # Bill of Materials (BOM) management
```

## Module Responsibilities

### Core (`static/js/core/`)

**csrf.js** - CSRF token management
- `Csrf.getToken()` - Read CSRF token from cookies
- `Csrf.getHeader()` - Get CSRF header object
- `Csrf.getFormData(form)` - Append CSRF token to FormData

### Components (`static/js/components/`)

**toast.js** - Toast notification system
- `Toast.show(message, type)` - Show toast with success/error/warning/info type
- Uses Alpine.js for animations where available, falls back to CSS transitions

**loading.js** - Loading overlay utilities
- `Loading.show()` / `Loading.hide()` - Toggle loading overlay
- `Loading.withPromise(asyncFn)` - Wrap async operations with loading state

### Store (`static/js/store/`)

**cart.js** - Shopping cart interactions
- `Cart.init()` - Initialize HTMX cart count synchronization
- `Cart.add(productId)` - Add product to cart via HTMX AJAX
- Listens to `htmx:afterSwap` for cart count updates across all badge locations

**catalog.js** - Product catalog interactions
- `Catalog.initPriceCalc()` - Live price calculation for custom dimensions
- `Catalog.initFilters()` - Product filter apply/reset via data attributes
- `Catalog.initClickableRows()` - Clickable table rows navigation

### Forms (`static/js/forms/`)

**cascade.js** - Category → Product cascading selects
- `CascadeSelect.init()` - Initialize via `data-cascade-url` attributes or `window.CascadeConfig`
- Auto-loads products when category changes
- Supports form auto-submit on change

**colors.js** - Product color field filtering
- `ColorFields.init()` - Initialize via `data-color-url` attributes or `window.ColorFieldsConfig`
- Shows/hides color fields based on product defaults
- Auto-loads colors when product changes

### Production (`static/js/production/`)

**scanner.js** - Barcode/part scanning interface
- `Scanner.init()` - Initialize scanner forms
- Handles CNC file download (`.cnc` barcodes)
- Handles DR/XML file download (`.xml` barcodes)
- Handles packaging unit shipping form (plate number assembly)
- Supports both `scan_part` and `scan_packaging_unit` pages

**kanban.js** - Painting schedule kanban board
- `Kanban.init()` - Initialize drag-drop kanban board
- Drag-drop task reassignment between workers
- AJAX assignment/unassignment with overtime confirmation
- Schedule reset functionality
- localStorage persistence for moved tasks

**workers.js** - Worker management (painting)
- `Workers.init()` - Initialize all worker management features
- `Workers.openWorkerCreate()`, `Workers.openWorkerEdit()` - Worker modal management
- `Workers.submitWorker()` - Worker create/update via AJAX
- `Workers.openExclusion()`, `Workers.submitExclusion()` - Product/item exclusion management
- `Workers.openDelete()`, `Workers.confirmDelete()` - Worker deletion
- `Workers.applyFilters()` - Filter/search/pagination
- `TableManager` - Table row CRUD operations
- Uses Bootstrap JS for modals (still required)
- Uses Select2 for exclusion search (still required)

**bom.js** - Bill of Materials management
- `BOM.init()` - Initialize BOM formset
- Add/edit/delete part rows via modal
- Size rule preset dropdown with custom formula support
- Dynamic formset row cloning with index management

## Global Events

### HTMX Events
- `htmx:configRequest` - CSRF token injection (defined in `layouts/store.html`)
- `htmx:afterSwap` - Cart count synchronization (defined in `store/cart.js`)

### Custom Events
- None currently defined - modules use direct function calls

## Configuration Pattern

Templates that need module configuration use `window.*Config` objects before loading modules:

```html
{% block extra_js %}
<script>
window.CascadeConfig = [
    {
        categorySelector: '#id_category',
        productSelector: '#id_product',
        url: '{% url "ajax_load_products" %}',
        onSubmit: true
    }
];
window.ColorFieldsConfig = [
    {
        productSelector: '#id_product',
        url: '{% url "ajax_load_product_colors" %}',
        initialProduct: '{{ item_form.product.value|default:"" }}'
    }
];
</script>
<script src="{% static 'js/forms/cascade.js' %}"></script>
<script src="{% static 'js/forms/colors.js' %}"></script>
{% endblock %}
```

## Removed Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| jQuery (inline usage) | **Removed from 15+ templates** | Still loaded in `static/js/vendor/` for Select2 |
| Duplicated AJAX helpers | **Removed** | Replaced with `Csrf`, `Loading`, `Toast` modules |
| Duplicated cascade select | **Removed** | Replaced with `CascadeSelect` module |
| Duplicated color filtering | **Removed** | Replaced with `ColorFields` module |
| Duplicated price calculator | **Removed** | Replaced with `Catalog.initPriceCalc()` |
| Duplicated clickable rows | **Removed** | Replaced with `Catalog.initClickableRows()` |
| Duplicated scanner logic | **Removed** | Replaced with `Scanner` module |
| Duplicated kanban logic | **Removed** | Replaced with `Kanban` module |
| Inline cart actions | **Removed** | Replaced with `Cart` module |
| Bootstrap JS dropdowns | **Replaced with Alpine** | In navbar/menus |
| Bootstrap JS modals | **Replaced with Alpine** | In confirm/modals where simple |
| Bootstrap JS collapse | **Replaced with Alpine** | In navbar collapse |

## Remaining Dependencies

| Dependency | Usage | Reason |
|------------|-------|--------|
| **jQuery** | Select2 initialization, legacy Select2 plugin | Select2 requires jQuery |
| **Select2** | Worker exclusion search (AJAX multi-select) | Complex searchable multi-select |
| **Bootstrap JS** | Modals in painting management, admin forms | Complex modal workflows |
| **Bootstrap CSS** | Dashboard/production layouts | RTL support, grid system |
| **Alpine.js** | Mobile menus, dropdowns, tabs, collapse, toasts | Lightweight local state |
| **HTMX** | Cart actions, partial updates, form submissions | Server-driven partial updates |

## Template Load Order

Templates extending dashboard layout:
1. `vendor/alpinejs.min.js` (defer)
2. `vendor/htmx.min.js`
3. `js/alpine-bootstrap.js` (Alpine data definitions)
4. `js/app.js` (main initialization)

Templates extending store layout:
1. `vendor/alpinejs.min.js` (defer)
2. `vendor/htmx.min.js`
3. `js/app.js` (main initialization)

## Event Delegation

Used in:
- `cart.js` - `htmx:afterSwap` for cart count updates
- `workers.js` - Click delegation for edit/delete/exclusion buttons
- `catalog.js` - Click delegation for clickable rows via `data-href`
- `scanner.js` - Form submit delegation for scan forms

## Browser Support

- Modern browsers (ES6+)
- No IE11 support
- Uses `fetch`, `FormData`, `async/await`, `const/let`
- CSS Grid and Flexbox

## Validation

- `python manage.py check` passes (0 issues)
- Tested: login, registration, product browsing, search, cart, checkout, toast messages, modals, dropdowns, production dashboard, barcode/scanner workflows, HTMX partial updates, mobile navigation

## Migration Path

1. **Completed**: Core modules (csrf, toast, loading)
2. **Completed**: Store modules (cart, catalog)
3. **Completed**: Form modules (cascade, colors)
4. **Completed**: Production modules (scanner, kanban, workers, bom)
5. **Future**: Remove jQuery when Select2 is replaced
6. **Future**: Replace remaining Bootstrap JS modals with Alpine
7. **Future**: Migrate Select2 to native searchable select or Alpine component
