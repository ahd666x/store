# JavaScript Migration Matrix

> Analysis of JavaScript files, their dependencies, and migration status.

---

## JS File Inventory

| File | Size | Framework | Status | Used By |
|------|------|-----------|--------|---------|
| app.js | ~3KB | ES6 modules | GREEN | All layouts |
| alpine-bootstrap.js | ~2KB | Alpine.js | YELLOW | dashboard.html |
| components/loading.js | ~1KB | Alpine.js | GREEN | Storefront |
| components/toast.js | ~1KB | Alpine.js | GREEN | Storefront |
| core/csrf.js | ~0.5KB | Vanilla JS | GREEN | All layouts |
| forms/cascade.js | ~2KB | Alpine.js | GREEN | Storefront + production |
| forms/colors.js | ~2KB | Alpine.js | GREEN | Storefront + production |
| store/cart.js | ~3KB | Alpine.js + HTMX | GREEN | Storefront |
| store/catalog.js | ~2KB | Alpine.js + HTMX | GREEN | Storefront |
| production/bom.js | ~3KB | Alpine.js + HTMX | YELLOW | Production BOM |
| production/kanban.js | ~4KB | Alpine.js + HTML5 DnD | YELLOW | Production kanban |
| production/order_item.js | ~2KB | Alpine.js | YELLOW | Production orders |
| production/orders.js | ~3KB | Alpine.js | YELLOW | Production orders |
| production/scanner.js | ~2KB | Alpine.js | YELLOW | Production scanning |
| production/workers.js | ~3KB | jQuery + Select2 | **RED** | Worker management |
| production/painting/assignment_rules.js | ~2KB | Alpine.js | YELLOW | Painting rules |
| production/painting/holidays.js | ~1KB | Alpine.js | YELLOW | Painting holidays |
| production/painting/processes.js | ~2KB | Bootstrap JS | **RED** | Painting processes |
| production/painting/ready_list.js | ~2KB | Alpine.js | YELLOW | Painting ready list |
| production/painting/stages.js | ~2KB | Bootstrap JS | **RED** | Painting stages |

---

## JS Architecture

### Module Initialization (app.js)

```javascript
// app.js — Main initialization
document.addEventListener('DOMContentLoaded', () => {
    // Storefront modules
    if (document.querySelector('[data-cart]')) new Cart();
    if (document.querySelector('[data-catalog]')) new Catalog();
    
    // Production modules
    if (document.querySelector('[data-scanner]')) new Scanner();
    if (document.querySelector('[data-kanban]')) new Kanban();
    if (document.querySelector('[data-orders]')) new Orders();
    if (document.querySelector('[data-order-item]')) new OrderItem();
    if (document.querySelector('[data-workers]')) new Workers();
    
    // Form modules
    if (document.querySelector('[data-cascade]')) new CascadeSelect();
    if (document.querySelector('[data-colors]')) new ColorFields();
    
    // Legacy
    if (document.querySelector('[data-select2]')) initSelect2();
});
```

### Dependency Map

```
app.js
├── store/cart.js ──────── Alpine.js + HTMX
├── store/catalog.js ───── Alpine.js + HTMX
├── production/bom.js ──── Alpine.js + HTMX
├── production/kanban.js ── Alpine.js + HTML5 DnD
├── production/orders.js ── Alpine.js
├── production/order_item.js ─ Alpine.js
├── production/scanner.js ── Alpine.js
├── production/workers.js ── jQuery + Select2 ← RED
├── forms/cascade.js ────── Alpine.js
├── forms/colors.js ─────── Alpine.js
└── painting/*.js ───────── Alpine.js + Bootstrap JS
```

---

## Detailed JS File Analysis

### app.js — GREEN

| Aspect | Details |
|--------|---------|
| **Purpose** | Module initialization and global setup |
| **Pattern** | ES6 class-based modules |
| **Dependencies** | None (vanilla JS) |
| **jQuery usage** | ❌ None |

**Migration status:** ✅ Fully migrated. No legacy dependencies.

---

### alpine-bootstrap.js — YELLOW

| Aspect | Details |
|--------|---------|
| **Purpose** | Alpine.js component definitions for Bootstrap interop |
| **Pattern** | Alpine.data() registrations |
| **Dependencies** | Alpine.js, Bootstrap JS |

**Components defined:**
- `navbar` — Navbar toggle and collapse
- `modal` — Bootstrap modal wrapper for Alpine
- `dropdown` — Bootstrap dropdown wrapper
- `alert` — Dismissible alert
- `toast` — Toast notification

**Issues:**
- Wraps Bootstrap JS components instead of replacing them
- Creates dual maintenance (Alpine + Bootstrap)
- `modal` component uses `bootstrap.Modal.getInstance()`

**Migration needed:**
- Replace `modal` with pure Alpine `x-show` + transitions
- Replace `dropdown` with Alpine `x-show` + `@click.outside`
- Remove Bootstrap JS dependency

---

### components/loading.js — GREEN

| Aspect | Details |
|--------|---------|
| **Purpose** | Loading state management |
| **Pattern** | Alpine.js component |
| **Dependencies** | Alpine.js only |

**Migration status:** ✅ Fully migrated.

---

### components/toast.js — GREEN

| Aspect | Details |
|--------|---------|
| **Purpose** | Toast notification system |
| **Pattern** | Alpine.js component with auto-dismiss |
| **Dependencies** | Alpine.js only |

**Migration status:** ✅ Fully migrated.

---

### core/csrf.js — GREEN

| Aspect | Details |
|--------|---------|
| **Purpose** | CSRF token handling for AJAX requests |
| **Pattern** | Vanilla JS |
| **Dependencies** | None |

**Migration status:** ✅ Fully migrated. Framework-agnostic.

---

### forms/cascade.js — GREEN

| Aspect | Details |
|--------|---------|
| **Purpose** | Cascade dropdown (category → product) |
| **Pattern** | Alpine.js + Fetch API |
| **Dependencies** | Alpine.js only |

**Migration status:** ✅ Fully migrated. Used in both storefront and production.

---

### forms/colors.js — GREEN

| Aspect | Details |
|--------|---------|
| **Purpose** | Dynamic color field generation |
| **Pattern** | Alpine.js + Fetch API |
| **Dependencies** | Alpine.js only |

**Migration status:** ✅ Fully migrated.

---

### store/cart.js — GREEN

| Aspect | Details |
|--------|---------|
| **Purpose** | Shopping cart management |
| **Pattern** | Alpine.js + HTMX |
| **Dependencies** | Alpine.js, HTMX |

**Features:**
- Add to cart via HTMX
- Update quantity via HTMX
- Cart total calculation
- Cart badge update

**Migration status:** ✅ Fully migrated.

---

### store/catalog.js — GREEN

| Aspect | Details |
|--------|---------|
| **Purpose** | Catalog filtering and sorting |
| **Pattern** | Alpine.js + HTMX |
| **Dependencies** | Alpine.js, HTMX |

**Features:**
- Price range filter
- Category filter
- Sort options
- HTMX partial reload

**Migration status:** ✅ Fully migrated.

---

### production/bom.js — YELLOW

| Aspect | Details |
|--------|---------|
| **Purpose** | Bill of Materials editing |
| **Pattern** | Alpine.js + HTMX |
| **Dependencies** | Alpine.js, HTMX |

**Issues:**
- Uses `bootstrap.Modal` for confirmation dialogs
- Mix of Alpine reactivity and Bootstrap components

**Migration needed:**
- Replace `bootstrap.Modal` with Alpine modal component

---

### production/kanban.js — YELLOW

| Aspect | Details |
|--------|---------|
| **Purpose** | Kanban board with drag-and-drop |
| **Pattern** | Alpine.js + HTML5 Drag and Drop API |
| **Dependencies** | Alpine.js only |

**Features:**
- Drag cards between columns
- Persist order via localStorage
- HTMX for server-side updates

**Issues:**
- Uses `localStorage` for moved task IDs (legacy pattern)
- Could use HTMX for full server sync

**Migration needed:**
- Replace localStorage with HTMX server sync
- Add proper error handling

---

### production/order_item.js — YELLOW

| Aspect | Details |
|--------|---------|
| **Purpose** | Order item detail management |
| **Pattern** | Alpine.js |
| **Dependencies** | Alpine.js only |

**Issues:**
- Minor: uses `bootstrap.Tooltip` for item details

**Migration needed:**
- Replace `bootstrap.Tooltip` with Alpine tooltip component

---

### production/orders.js — YELLOW

| Aspect | Details |
|--------|---------|
| **Purpose** | Order list management |
| **Pattern** | Alpine.js |
| **Dependencies** | Alpine.js only |

**Issues:**
- Uses `bootstrap.Modal` for order detail preview

**Migration needed:**
- Replace `bootstrap.Modal` with Alpine modal

---

### production/scanner.js — YELLOW

| Aspect | Details |
|--------|---------|
| **Purpose** | Barcode/QR code scanning |
| **Pattern** | Alpine.js + Camera API |
| **Dependencies** | Alpine.js only |

**Issues:**
- Minor: uses `bootstrap.Toast` for scan feedback

**Migration needed:**
- Replace `bootstrap.Toast` with Alpine toast component

---

### production/workers.js — RED

| Aspect | Details |
|--------|---------|
| **Purpose** | Worker management with Select2 |
| **Pattern** | jQuery + Select2 + Bootstrap Modal |
| **Dependencies** | jQuery, Select2, Bootstrap JS |

**Features:**
- Select2 for worker dropdown (with bootstrap-5 theme)
- Bootstrap Modal for worker detail
- jQuery event handlers for form submission

**Issues:**
- ❌ Uses jQuery for DOM manipulation
- ❌ Uses Select2 plugin (requires jQuery)
- ❌ Uses `bootstrap.Modal` API directly
- ❌ Uses `bootstrap.Tooltip` API directly

**Migration needed:**
- Replace Select2 with Alpine.js combobox component
- Replace jQuery event handlers with Alpine `@click`, `@change`
- Replace `bootstrap.Modal` with Alpine modal
- Replace `bootstrap.Tooltip` with Alpine tooltip

---

### production/painting/assignment_rules.js — YELLOW

| Aspect | Details |
|--------|---------|
| **Purpose** | Painting assignment rule management |
| **Pattern** | Alpine.js |
| **Dependencies** | Alpine.js only |

**Migration status:** ✅ Mostly migrated. Minor Bootstrap interop.

---

### production/painting/holidays.js — YELLOW

| Aspect | Details |
|--------|---------|
| **Purpose** | Holiday calendar management |
| **Pattern** | Alpine.js |
| **Dependencies** | Alpine.js only |

**Migration status:** ✅ Mostly migrated.

---

### production/painting/processes.js — RED

| Aspect | Details |
|--------|---------|
| **Purpose** | Painting process management |
| **Pattern** | Bootstrap JS + jQuery |
| **Dependencies** | Bootstrap JS, jQuery |

**Issues:**
- ❌ Uses `bootstrap.Modal` for process creation
- ❌ Uses `bootstrap.Tooltip` for stage info
- ❌ Uses jQuery for AJAX calls

**Migration needed:**
- Replace jQuery AJAX with Fetch API
- Replace Bootstrap components with Alpine equivalents

---

### production/painting/ready_list.js — YELLOW

| Aspect | Details |
|--------|---------|
| **Purpose** | Ready items list management |
| **Pattern** | Alpine.js |
| **Dependencies** | Alpine.js only |

**Migration status:** ✅ Mostly migrated.

---

### production/painting/stages.js — RED

| Aspect | Details |
|--------|---------|
| **Purpose** | Painting stage management |
| **Pattern** | Bootstrap JS + jQuery |
| **Dependencies** | Bootstrap JS, jQuery |

**Issues:**
- ❌ Uses `bootstrap.Modal` for stage editing
- ❌ Uses jQuery for DOM updates

**Migration needed:**
- Replace jQuery with Alpine.js reactivity
- Replace Bootstrap modal with Alpine modal

---

## JS Dependency Analysis

### jQuery Usage

| File | jQuery Usage | Migration Effort |
|------|--------------|------------------|
| production/workers.js | `$(selector).on()`, `$.ajax()`, `$(el).modal()` | High |
| production/painting/processes.js | `$(selector).on()`, `$.ajax()` | Medium |
| production/painting/stages.js | `$(selector).on()`, `$(el).html()` | Medium |

### Bootstrap JS Usage

| File | Bootstrap JS Usage | Migration Effort |
|------|-------------------|------------------|
| alpine-bootstrap.js | `bootstrap.Modal`, `bootstrap.Dropdown` | Medium |
| production/bom.js | `bootstrap.Modal.getInstance()` | Low |
| production/order_item.js | `bootstrap.Tooltip` | Low |
| production/orders.js | `bootstrap.Modal` | Low |
| production/scanner.js | `bootstrap.Toast` | Low |
| production/workers.js | `bootstrap.Modal`, `bootstrap.Tooltip` | Medium |
| production/painting/processes.js | `bootstrap.Modal`, `bootstrap.Tooltip` | Medium |
| production/painting/stages.js | `bootstrap.Modal` | Low |

### Select2 Usage

| File | Select2 Usage | Migration Effort |
|------|---------------|------------------|
| production/workers.js | `$(el).select2({ theme: 'bootstrap-5' })` | Medium |

---

## JS Migration Priority

| Priority | File | Effort | Impact |
|----------|------|--------|--------|
| P0 | production/workers.js | High | Removes jQuery + Select2 dependency |
| P0 | production/painting/processes.js | Medium | Removes Bootstrap JS dependency |
| P0 | production/painting/stages.js | Medium | Removes Bootstrap JS dependency |
| P1 | alpine-bootstrap.js | Medium | Removes Bootstrap JS interop layer |
| P1 | production/bom.js | Low | Removes bootstrap.Modal usage |
| P1 | production/orders.js | Low | Removes bootstrap.Modal usage |
| P2 | production/order_item.js | Low | Removes bootstrap.Tooltip usage |
| P2 | production/scanner.js | Low | Removes bootstrap.Toast usage |

---

## Migration Strategy

### Phase 1: Remove jQuery
1. Replace `production/workers.js` with Alpine.js combobox
2. Replace jQuery AJAX with Fetch API in painting modules
3. Remove jQuery event handlers, use Alpine `@click`, `@change`

### Phase 2: Remove Bootstrap JS
1. Replace `bootstrap.Modal` with Alpine `x-show` + transitions
2. Replace `bootstrap.Tooltip` with Alpine tooltip component
3. Replace `bootstrap.Toast` with existing toast.js component
4. Replace `bootstrap.Dropdown` with Alpine `x-show` + `@click.outside`

### Phase 3: Remove Select2
1. Create Alpine.js combobox component
2. Replace Select2 in worker dropdowns
3. Remove select2 CSS/JS from painting workers template

### Phase 4: Cleanup
1. Remove alpine-bootstrap.js
2. Remove Select2 CSS/JS files
3. Update app.js to remove legacy module initialization

---

## Replacement Patterns

### Bootstrap Modal → Alpine Modal

**Before:**
```javascript
const modal = new bootstrap.Modal(document.getElementById('myModal'));
modal.show();
```

**After:**
```html
<div x-data="{ open: false }">
    <button @click="open = true">Open</button>
    <div x-show="open" x-transition @click.outside="open = false">
        <!-- Modal content -->
    </div>
</div>
```

### Select2 → Alpine Combobox

**Before:**
```javascript
$('#worker-select').select2({
    theme: 'bootstrap-5',
    ajax: { url: '/api/workers', ... }
});
```

**After:**
```html
<div x-data="combobox('/api/workers')">
    <input @input="search($event.target.value)" />
    <template x-for="item in results">
        <div @click="select(item)" x-text="item.name"></div>
    </template>
</div>
```

### jQuery AJAX → Fetch API

**Before:**
```javascript
$.ajax({
    url: '/api/data',
    method: 'POST',
    data: { id: 1 },
    success: function(response) { ... }
});
```

**After:**
```javascript
fetch('/api/data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: 1 })
}).then(r => r.json()).then(data => { ... });
```
