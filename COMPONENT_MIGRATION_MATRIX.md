# Component Migration Matrix

> Analysis of reusable component templates and their actual usage across the codebase.

---

## Component Inventory

### Card Components

| Component | Path | Framework | Usage |
|-----------|------|-----------|-------|
| product_card.html | components/cards/ | Tailwind | Storefront product grids |
| category_card.html | components/cards/ | Tailwind | Category listings |
| stat_card.html | components/cards/ | Tailwind | Dashboard stats |
| order_card.html | components/cards/ | Tailwind | Order display |

### Data Display Components

| Component | Path | Framework | Usage |
|-----------|------|-----------|-------|
| table.html | components/data/ | Tailwind | Data tables |
| pagination.html | components/data/ | Tailwind | Pagination controls |
| badge.html | components/data/ | Bootstrap | Status badges (legacy) |
| progress_bar.html | components/data/ | Tailwind | Progress indicators |

### Feedback Components

| Component | Path | Framework | Usage |
|-----------|------|-----------|-------|
| alert.html | components/feedback/ | Tailwind | Alert messages |
| toast.html | components/feedback/ | Tailwind + Alpine | Toast notifications |
| modal.html | components/feedback/ | Bootstrap | Modal dialogs (legacy) |
| spinner.html | components/feedback/ | Tailwind | Loading spinner |

### Form Components

| Component | Path | Framework | Usage |
|-----------|------|-----------|-------|
| form_field.html | components/forms/ | Tailwind | Form input wrapper |
| form_select.html | components/forms/ | Tailwind | Select input |
| form_textarea.html | components/forms/ | Tailwind | Textarea input |
| form_checkbox.html | components/forms/ | Tailwind | Checkbox input |
| form_error.html | components/forms/ | Tailwind | Form error display |

### Loading Components

| Component | Path | Framework | Usage |
|-----------|------|-----------|-------|
| loading.html | components/loading/ | Tailwind | Full-page loading |
| skeleton.html | components/loading/ | Tailwind | Skeleton placeholder |
| button_loading.html | components/loading/ | Tailwind | Button loading state |

### Navigation Components

| Component | Path | Framework | Usage |
|-----------|------|-----------|-------|
| navbar.html | components/navigation/ | Tailwind | Main navigation |
| sidebar.html | components/navigation/ | Bootstrap | Production sidebar (legacy) |
| breadcrumb.html | components/navigation/ | Tailwind | Breadcrumb trail |
| tabs.html | components/navigation/ | Tailwind | Tab navigation |

### Table Components

| Component | Path | Framework | Usage |
|-----------|------|-----------|-------|
| table_header.html | components/tables/ | Tailwind | Sortable table header |
| table_row.html | components/tables/ | Tailwind | Table row |
| table_actions.html | components/tables/ | Tailwind | Row action buttons |
| table_empty.html | components/tables/ | Tailwind | Empty state |

---

## Component Usage Analysis

### Storefront Usage (GREEN)

| Template | Components Used |
|----------|-----------------|
| home.html | product_card, category_card, stat_card |
| catalog/product_list.html | product_card, pagination, badge |
| catalog/product_detail.html | breadcrumb, toast |
| cart/detail.html | table, table_row, table_actions |
| order_detail.html | order_card, badge, progress_bar |
| account/*.html | form_field, form_select, form_checkbox |

### Production Usage (YELLOW/RED)

| Template | Components Used | Notes |
|----------|----------------|-------|
| dashboard.html | stat_card | Mostly inline Bootstrap markup |
| order_list.html | table (partial) | Mix of component and inline |
| kanban.html | — | Fully inline markup |
| worker_list.html | — | Fully inline + Select2 |
| product_bom_edit.html | form_field | Some component usage |
| painting/*.html | — | Fully inline + custom CSS |

---

## Component Classification

### GREEN Components (Tailwind + Alpine)

| Component | Dependencies |
|-----------|--------------|
| product_card.html | Tailwind only |
| category_card.html | Tailwind only |
| stat_card.html | Tailwind only |
| order_card.html | Tailwind only |
| pagination.html | Tailwind only |
| progress_bar.html | Tailwind only |
| alert.html | Tailwind only |
| toast.html | Alpine.js |
| form_field.html | Tailwind only |
| form_select.html | Tailwind only |
| form_textarea.html | Tailwind only |
| form_checkbox.html | Tailwind only |
| form_error.html | Tailwind only |
| loading.html | Tailwind only |
| skeleton.html | Tailwind only |
| button_loading.html | Tailwind only |
| navbar.html | Alpine.js |
| breadcrumb.html | Tailwind only |
| tabs.html | Alpine.js |
| table_header.html | Tailwind only |
| table_row.html | Tailwind only |
| table_actions.html | Tailwind only |
| table_empty.html | Tailwind only |

### YELLOW Components (Mixed)

| Component | Dependencies | Issue |
|-----------|--------------|-------|
| spinner.html | Tailwind + Alpine | Minor: uses Alpine for show/hide |

### RED Components (Bootstrap/jQuery)

| Component | Dependencies | Issue |
|-----------|--------------|-------|
| badge.html | Bootstrap classes | Uses `badge bg-*` Bootstrap classes |
| modal.html | Bootstrap JS + jQuery | Uses `bootstrap.Modal` API |
| sidebar.html | Bootstrap classes | Uses Bootstrap nav classes |

---

## Component Migration Status

### Fully Migrated (GREEN)
- All card components
- All form components
- All loading components
- All table components
- Alert, toast, progress_bar
- Navbar, breadcrumb, tabs

### Needs Migration (RED → GREEN)

| Component | Current | Target | Effort |
|-----------|---------|--------|--------|
| badge.html | Bootstrap `badge bg-*` | Tailwind `inline-flex px-2 py-0.5 rounded-full text-xs` | Low |
| modal.html | `bootstrap.Modal` JS | Alpine `x-data` + `x-show` + transitions | Medium |
| sidebar.html | Bootstrap `nav flex-column` | Tailwind `space-y-1` + Alpine active state | Low |

---

## Component Replacement Map

| Legacy Pattern | Component | Replacement |
|----------------|-----------|-------------|
| `<div class="card shadow">` | card.html | `{% include 'components/cards/stat_card.html' %}` |
| `<span class="badge bg-primary">` | badge.html | `{% include 'components/data/badge.html' %}` |
| `<div class="modal fade">` | modal.html | `{% include 'components/feedback/modal.html' %}` |
| `<div class="spinner-border">` | spinner.html | `{% include 'components/feedback/spinner.html' %}` |
| `<nav class="nav flex-column">` | sidebar.html | `{% include 'components/navigation/sidebar.html' %}` |
| `<div class="alert alert-info">` | alert.html | `{% include 'components/feedback/alert.html' %}` |
| `<div class="skeleton-loader">` | skeleton.html | `{% include 'components/loading/skeleton.html' %}` |

---

## Component Usage Gap Analysis

### Underused Components

| Component | Expected Usage | Actual Usage | Gap |
|-----------|---------------|--------------|-----|
| form_field.html | All forms | Storefront only | Production forms use inline markup |
| table.html | All data tables | Storefront only | Production uses inline Bootstrap tables |
| badge.html | All status indicators | Storefront only | Production uses inline Bootstrap badges |
| pagination.html | All list pages | Storefront only | Production uses DataTables or custom |
| modal.html | All dialogs | Storefront only | Production uses bootstrap.Modal JS |

### Root Causes
1. **Production templates predate component library** — built before reusable components existed
2. **Different developer mental model** — production team used Bootstrap directly
3. **No enforcement** — no linting or CI check requiring component usage
4. **CSS framework mismatch** — Bootstrap components don't map 1:1 to Tailwind

---

## Recommendations

### Immediate Actions
1. Migrate `badge.html` to Tailwind (low effort, high impact)
2. Migrate `modal.html` to Alpine (medium effort, removes Bootstrap JS dependency)
3. Migrate `sidebar.html` to Tailwind (low effort)

### Medium-term Actions
4. Refactor production forms to use `form_field.html` component
5. Refactor production tables to use table components
6. Add component usage linting to CI

### Long-term Actions
7. Create production-specific component variants if needed
8. Deprecate inline markup in favor of components
9. Document component library with examples
