# CSS Architecture - سلوی چوب

## Overview

This document describes the CSS architecture for the سلوی چوب project after Phase 4 consolidation.

## Primary Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Utilities** | Tailwind CSS v3.4 | Primary utility framework |
| **Components** | Custom CSS + Tailwind `@layer components` | Reusable component classes |
| **Icons** | Bootstrap Icons | Icon font (vendor) |
| **JS Behaviors** | Alpine.js | Interactive components (modals, dropdowns, collapses) |

## File Structure

```
static/css/
├── tailwind-input.css      # Tailwind source + custom component classes (~16KB)
├── style.css               # Compiled Tailwind output (~115KB, auto-generated)
├── vazirmatn-fonts.css     # Vazirmatn font faces
├── dashboard.css           # Dashboard-specific quick-link card styles
├── components.css          # Shared component styles (navbar, cards, forms, shop, login)
├── product-grid.css        # Product listing grid (legacy, can be migrated)
├── pages/
│   └── shipped.css         # Shipped report page styles
└── vendor/
    ├── bootstrap.rtl.min.css      # Bootstrap RTL (legacy, for backward compat)
    ├── bootstrap-icons.css        # Bootstrap Icons CSS
    ├── select2.min.css            # Select2 widget
    ├── select2-bootstrap-5-theme.min.css
    └── fonts/
        ├── bootstrap-icons.woff
        └── bootstrap-icons.woff2

static/js/
├── vendor/
│   ├── alpinejs.min.js
│   ├── htmx.min.js
│   ├── bootstrap.bundle.min.js
│   ├── jquery-3.7.1.min.js
│   └── select2.min.js
└── alpine-bootstrap.js     # Alpine.js replacements for Bootstrap JS behaviors
```

## Layout System

| Layout | CSS Frameworks | Purpose |
|--------|---------------|---------|
| `layouts/store.html` | Tailwind + components.css | Public storefront (دکارو) |
| `layouts/dashboard.html` | Tailwind + components.css + vendor Bootstrap RTL | Admin/production (سلوی چوب) |
| `layouts/print.html` | Minimal | Print-optimized documents |

## Component Classes

### Buttons
- `.btn` - Base button styles
- `.btn-primary`, `.btn-secondary`, `.btn-success`, `.btn-danger`, `.btn-warning`, `.btn-info`, `.btn-dark`, `.btn-light`, `.btn-link`
- `.btn-outline-*` variants
- `.btn-sm`, `.btn-lg` - Size variants

### Cards
- `.card` - Base card
- `.card-hover` - Hover effect
- `.card-elevated` - Elevated shadow
- `.card-header`, `.card-body`, `.card-footer`, `.card-title`, `.card-text` - Bootstrap compatible

### Forms
- `.form-input` - Base input
- `.form-label`, `.form-error`, `.form-hint` - Form helpers
- `.form-select` - Select with custom arrow
- `.form-control`, `.form-control-sm`, `.form-control-lg` - Bootstrap compatible
- `.input-group`, `.input-group-text` - Input groups

### Badges
- `.badge` - Base badge
- `.badge-success`, `.badge-warning`, `.badge-danger`, `.badge-info`, `.badge-neutral`
- Bootstrap compatible: `.bg-success`, `.bg-warning`, `.bg-danger`, `.bg-info`, `.bg-secondary`, `.bg-light`, `.bg-dark`, `.text-dark`

### Alerts
- `.alert` - Base alert
- `.alert-success`, `.alert-warning`, `.alert-danger`, `.alert-info`, `.alert-light`, `.alert-dark`
- `.alert-dismissible` - Dismissible variant

### Tables
- `.table` - Base table
- `.table-modern` - Modern styled table
- Bootstrap compatible: `.table-hover`, `.table-bordered`, `.table-striped`, `.table-sm`, `.table-responsive`, `.thead-light`, `.thead-dark`

### Navigation
- `.navbar`, `.navbar-expand-lg`, `.navbar-toggler`, `.navbar-toggler-icon`
- `.navbar-brand`, `.navbar-nav`, `.nav-item`, `.nav-link`
- `.navbar-collapse` - Collapsible nav
- `.me-auto`, `.ms-auto` - Auto margins

### Modals
- `.modal`, `.modal.show` - Modal container
- `.modal-dialog`, `.modal-content`, `.modal-header`, `.modal-body`, `.modal-footer`
- `.modal-lg`, `.modal-sm` - Size variants
- `.fade` - Transition
- `.btn-close`, `.btn-close-white`

### Dropdowns
- `.dropdown`, `.dropdown-toggle`, `.dropdown-menu`, `.dropdown-menu-end`
- `.dropdown-item`, `.dropdown-divider`, `.dropdown-header`

### Utilities
- `.shadow-sm`, `.shadow`, `.shadow-lg` - Bootstrap compatible shadows
- `.empty-state`, `.empty-state-icon`, `.empty-state-title`, `.empty-state-description`
- `.spinner`, `.spinner-lg`, `.spinner-sm`
- `.chip`, `.chip-active`, `.chip-inactive`
- `.skeleton`, `.skeleton-text`, `.skeleton-title`, `.skeleton-image`, `.skeleton-avatar`

## RTL Support

All components are RTL-aware:
- Logical properties (`margin-inline-start`, `padding-inline-end`, etc.)
- Bootstrap-compatible `.me-*`, `.ms-*`, `.pe-*`, `.ps-*` utilities
- `.border-s`, `.border-e`, `.rounded-s`, `.rounded-e`

## Bootstrap Migration Status

### Removed
- `static/css/bootstrap*.css` (root level, ~6.5MB unused files)
- `static/css/bootstrap-icons.css` (duplicate)
- `static/css/fonts/` (duplicate font files)
- `data-bs-*` attributes from: `layouts/dashboard.html`, `production/base.html`, `production/base_shop.html`, `components/modals/modal.html`, `components/feedback/alert.html`, `production/painting_management/base.html`
- Inline `<style>` blocks from: `production/base.html`, `production/base_shop.html`, `production/painting_management/base.html`, `production/registration/login.html`, `production/reports/shipped.html`

### Remaining (vendor)
- `static/css/vendor/bootstrap.rtl.min.css` - Loaded by `layouts/dashboard.html` for backward compatibility with existing admin templates
- `static/css/vendor/bootstrap-icons.css` - Icon font still in use
- `static/js/vendor/bootstrap.bundle.min.js` - Loaded for templates not yet migrated to Alpine.js
- `static/js/vendor/jquery-3.7.1.min.js` - Loaded for legacy scripts

## Build Process

```bash
npm run build:css    # Compile Tailwind: tailwind-input.css → style.css
npm run watch:css    # Watch mode for development
```

## Adding New Component Classes

1. Add class definitions to `static/css/tailwind-input.css` inside `@layer components`
2. Rebuild CSS with `npm run build:css`
3. Use in templates directly

## Known Issues

1. **Bootstrap CSS still loaded** - `vendor/bootstrap.rtl.min.css` is loaded by `layouts/dashboard.html` for backward compatibility. Can be removed once all admin templates are migrated to Tailwind classes.
2. **Bootstrap JS still loaded** - `bootstrap.bundle.min.js` is loaded by `layouts/dashboard.html` for templates not yet migrated to Alpine.js.
3. **Inline styles remain** - Some templates still have inline `style=` attributes that should be extracted.
4. **jQuery dependency** - Some legacy scripts still use jQuery. Can be removed once all scripts are migrated to vanilla JS or Alpine.js.

## Migration Guide

When migrating a template from Bootstrap to Tailwind:

1. Replace Bootstrap classes with Tailwind equivalents or existing component classes
2. Replace `data-bs-toggle="modal"` with Alpine.js `x-data` and `@click`
3. Replace `data-bs-toggle="dropdown"` with Alpine.js dropdown
4. Replace `data-bs-toggle="collapse"` with Alpine.js `x-show`
5. Replace `data-bs-dismiss="alert"` with Alpine.js `@click="visible = false"`
6. Test on mobile viewport

## References

- `DESIGN_SYSTEM.md` - Design tokens and color palette
- `LAYOUT_ARCHITECTURE.md` - Template layout hierarchy
- `COMPONENT_LIBRARY.md` - Django template components
