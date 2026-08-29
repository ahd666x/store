# CSS Migration Matrix

> Analysis of CSS files, their dependencies, and migration status.

---

## CSS File Inventory

| File | Size | Framework | Status | Used By |
|------|------|-----------|--------|---------|
| tailwind-input.css | ~5KB source | Tailwind | GREEN | Compiled to style.css for storefront |
| components.css | ~8KB | Mixed | YELLOW | All layouts (shared) |
| dashboard.css | ~6KB | Custom + Bootstrap override | YELLOW | Production dashboard layout |
| product-grid.css | ~3KB | Tailwind | GREEN | Storefront product grids |
| vazirmatn-fonts.css | ~2KB | @font-face | GREEN | All layouts |
| pages/painting.css | ~15KB | Custom CSS | RED | Painting management |
| pages/shipped.css | ~2KB | Custom CSS | YELLOW | Shipped orders page |

---

## CSS Architecture

### Tailwind Build Pipeline

```
tailwind-input.css (source)
    ↓ PostCSS + Tailwind
style.css (compiled, ~200KB)
    ↓
Storefront pages only
```

**tailwind-input.css contents:**
- `@tailwind base` — reset + base styles
- `@tailwind components` — component classes
- `@tailwind utilities` — utility classes
- Custom `@layer base` — CSS custom properties (colors, fonts)
- Custom `@layer components` — `.btn`, `.card`, `.input` etc.
- `@layer utilities` — custom utilities (`.scrollbar-hide`, `.text-balance`)

**Design System Variables:**
```css
:root {
  --color-primary: #1e40af;
  --color-secondary: #64748b;
  --color-success: #16a34a;
  --color-warning: #ca8a04;
  --color-danger: #dc2626;
  --font-sans: 'Vazirmatn', sans-serif;
}
```

---

### Bootstrap (Production)

```
bootstrap.rtl.min.css (CDN/vendored)
    ↓
Production dashboard pages
```

**Bootstrap CSS classes used in production:**
- Grid: `.container`, `.row`, `.col-md-*`, `.col-lg-*`, `.col-12`
- Components: `.card`, `.card-header`, `.card-body`, `.btn`, `.btn-*`, `.form-control`, `.form-label`, `.input-group`, `.list-group`, `.badge`, `.alert`, `.modal`, `.navbar`, `.nav`, `.navbar-nav`
- Utilities: `.d-flex`, `.d-none`, `.justify-content-*`, `.align-items-*`, `.mb-*`, `.mt-*`, `.p-*`, `.text-*`, `.bg-*`, `.border`, `.rounded`, `.shadow`, `.gap-*`

---

## Detailed CSS File Analysis

### tailwind-input.css — GREEN

| Aspect | Details |
|--------|---------|
| **Purpose** | Tailwind source file for storewind build |
| **Directives** | base, components, utilities |
| **Custom layers** | base (CSS vars), components (.btn, .card), utilities |
| **Imports** | vazirmatn-fonts.css (via @import) |
| **Output** | static/css/style.css |

**Migration status:** ✅ Fully migrated. No legacy dependencies.

---

### components.css — YELLOW

| Aspect | Details |
|--------|---------|
| **Purpose** | Shared component styles across all layouts |
| **Used by** | store.html, dashboard.html, print.html |
| **Contains** | Font definitions, button variants, card styles, form styles, modal styles |
| **Framework mix** | Tailwind-compatible + legacy Bootstrap-like classes |

**Legacy classes still present:**
- `.btn-primary`, `.btn-secondary` — Bootstrap-like button classes (not Tailwind)
- `.card-shadow` — custom shadow utility
- `.modal-backdrop` — custom modal overlay (redundant with Alpine)
- `.form-input` — custom form input (should use Tailwind `@apply`)

**Migration needed:**
- Replace `.btn-*` classes with Tailwind `bg-* text-* px-4 py-2 rounded`
- Remove `.modal-backdrop` (use Alpine x-show with transitions)
- Consolidate `.form-input` with Tailwind `@layer components`

---

### dashboard.css — YELLOW

| Aspect | Details |
|--------|---------|
| **Purpose** | Production dashboard custom styles |
| **Used by** | layouts/dashboard.html |
| **Contains** | Sidebar styles, card overrides, stats cards, table styles, print styles |

**Key sections:**
1. **Sidebar** — Fixed sidebar with nav links (`.sidebar`, `.sidebar-nav`, `.nav-link`)
2. **Dashboard cards** — Stat cards with icon, number, label (`.stat-card`, `.stat-icon`)
3. **Tables** — Table overrides for production tables
4. **Print** — `@media print` rules for production pages

**Bootstrap overrides:**
```css
.card { border-radius: 0.75rem; }
.card-header { background: var(--color-primary); }
.btn { border-radius: 0.5rem; }
```

**Migration needed:**
- Convert sidebar to Tailwind (`.sidebar` → `w-64 h-screen fixed`)
- Convert stat cards to Tailwind (`.stat-card` → `bg-white rounded-xl shadow`)
- Move print rules to dedicated print.css

---

### product-grid.css — GREEN

| Aspect | Details |
|--------|---------|
| **Purpose** | Product grid layouts for storefront |
| **Used by** | catalog templates |
| **Contains** | Grid layouts, responsive columns, hover effects |

**Migration status:** ✅ Fully migrated. Uses CSS Grid + Tailwind utilities.

---

### vazirmatn-fonts.css — GREEN

| Aspect | Details |
|--------|---------|
| **Purpose** | Vazirmatn Persian font @font-face declarations |
| **Used by** | All layouts |
| **Contains** | @font-face for weights 100-900 |

**Migration status:** ✅ Fully migrated. Framework-agnostic.

---

### pages/painting.css — RED

| Aspect | Details |
|--------|---------|
| **Purpose** | Painting management custom styles |
| **Used by** | production/painting_management/base.html |
| **Size** | ~15KB, 300+ lines |
| **Contains** | Custom classes, Bootstrap overrides, paint-specific colors |

**Custom classes defined:**
```css
.painting-card { ... }
.painting-status { ... }
.painting-timeline { ... }
.painting-badge { ... }
.painting-table th { ... }
.painting-table td { ... }
.stage-indicator { ... }
.color-swatch { ... }
.worker-avatar { ... }
/* ... 30+ more custom classes */
```

**Issues:**
1. Duplicates Bootstrap utilities (`.painting-badge` ≈ `.badge`)
2. Duplicates Tailwind utilities (`.painting-card` ≈ `.bg-white .rounded .shadow`)
3. Uses hardcoded colors instead of CSS variables
4. No responsive design patterns
5. Specificity wars with Bootstrap

**Migration needed:**
- Audit each class for actual usage
- Replace with Tailwind utilities in templates
- Move remaining custom CSS to `@layer components` in tailwind-input.css
- Delete file after migration

---

### pages/shipped.css — YELLOW

| Aspect | Details |
|--------|---------|
| **Purpose** | Shipped orders page styles |
| **Used by** | Production shipped page |
| **Contains** | Timeline styles, status indicators |

**Migration needed:**
- Convert to Tailwind utilities
- Merge into dashboard.css or delete

---

## CSS Delivery by Page Type

| Page Type | CSS Files |
|-----------|-----------|
| Storefront | style.css (Tailwind), components.css, bootstrap-icons.css |
| Production | bootstrap.rtl.min.css, bootstrap-icons.css, vazirmatn-fonts.css, dashboard.css, components.css |
| Painting | All production CSS + pages/painting.css |
| Print | Inline styles only |

---

## CSS Duplication Analysis

| Pattern | Tailwind | Bootstrap | Custom | Location |
|---------|----------|-----------|--------|----------|
| Card | `.card` (via @apply) | `.card` | `.painting-card` | 3 definitions |
| Button | `.btn` (via @apply) | `.btn` | — | 2 definitions |
| Badge | — | `.badge` | `.painting-badge` | 2 definitions |
| Form input | `.form-input` (via @apply) | `.form-control` | — | 2 definitions |
| Modal | — | `.modal` | `.modal-backdrop` | 2 definitions |
| Table | — | `.table` | `.painting-table` | 2 definitions |

**Recommendation:** Consolidate on Tailwind utilities. Remove Bootstrap and custom duplicates.

---

## CSS Custom Properties Audit

### Defined in tailwind-input.css
```css
:root {
  --color-primary: #1e40af;
  --color-secondary: #64748b;
  --color-success: #16a34a;
  --color-warning: #ca8a04;
  --color-danger: #dc2626;
  --font-sans: 'Vazirmatn', sans-serif;
}
```

### Used in dashboard.css
```css
.card-header { background: var(--color-primary); }
.btn-primary { background: var(--color-primary); }
```

### Used in painting.css
```css
/* Hardcoded colors — NOT using CSS variables */
.painting-status-pending { background: #fef3c7; color: #92400e; }
.painting-status-done { background: #d1fae5; color: #065f46; }
```

**Issue:** painting.css uses hardcoded colors instead of CSS variables. Must be fixed during migration.

---

## CSS Migration Priority

| Priority | File | Effort | Impact |
|----------|------|--------|--------|
| P0 | pages/painting.css | High | Removes 15KB custom CSS |
| P1 | components.css | Medium | Unifies component styling |
| P1 | dashboard.css | Medium | Enables Bootstrap removal |
| P2 | pages/shipped.css | Low | Small file, easy win |

---

## Migration Strategy

### Phase 1: Consolidate Design Tokens
1. Extend CSS custom properties with all colors, spacing, typography
2. Update tailwind.config.js to use CSS variables
3. Replace hardcoded colors in painting.css with CSS variables

### Phase 2: Convert Custom CSS
1. Move dashboard.css custom classes to Tailwind @layer components
2. Convert painting.css classes to Tailwind utilities
3. Delete pages/painting.css and pages/shipped.css

### Phase 3: Remove Bootstrap CSS
1. Remove bootstrap.rtl.min.css from dashboard.html
2. Update all production templates to use Tailwind classes
3. Remove Bootstrap override styles from dashboard.css
4. Delete dashboard.css

### Phase 4: Final Cleanup
1. Audit components.css for remaining legacy classes
2. Consolidate into tailwind-input.css
3. Delete components.css if empty
