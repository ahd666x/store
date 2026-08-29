# Production Migration Map

> Detailed analysis of production-critical pages and their migration requirements.

---

## Production Page Inventory

| Page | Template | URL | Priority | Status |
|------|----------|-----|----------|--------|
| Dashboard | production/dashboard.html | /production/ | P1 | YELLOW |
| Order List | production/order_list.html | /production/orders/ | P1 | YELLOW |
| Order Detail | production/orders/order_detail.html | /production/orders/<id>/ | P1 | YELLOW |
| Order Item | production/order_item.html | /production/items/<id>/ | P1 | YELLOW |
| Kanban Board | production/kanban.html | /production/kanban/ | P1 | YELLOW |
| Scan Part | production/scan_part.html | /production/scan/ | P2 | YELLOW |
| Worker List | production/worker_list.html | /production/workers/ | P0 | **RED** |
| Product BOM Edit | production/product_bom_edit.html | /production/bom/<id>/ | P2 | YELLOW |
| Product Create | production/product_create.html | /production/products/new/ | P2 | YELLOW |
| Create Order | production/create_order.html | /production/orders/new/ | P1 | YELLOW |
| Create Complete | production/create_complete.html | /production/orders/new/complete/ | P1 | YELLOW |
| Create Unified | production/create_unified.html | /production/orders/new/unified/ | P1 | YELLOW |
| Order Print | production/order_print.html | /production/orders/<id>/print/ | P3 | YELLOW |
| Report | production/report.html | /production/reports/ | P2 | YELLOW |
| Set Plate | production/set_plate.html | /production/set-plate/ | P2 | YELLOW |
| Scan Packaging | production/scan_packaging_unit.html | /production/scan-packaging/ | P2 | YELLOW |
| Select Shipment | production/select_shipment.html | /production/select-shipment/ | P2 | YELLOW |
| Print | production/print.html | /production/print/ | P3 | YELLOW |
| Admin Product List | production/admin_product_list.html | /production/admin/products/ | P2 | YELLOW |
| Admin Order Edit | production/admin_order_edit.html | /production/admin/orders/<id>/edit/ | P1 | YELLOW |
| Admin Edit Order Item | production/admin_edit_order_item.html | /production/admin/items/<id>/edit/ | P2 | YELLOW |
| Admin Order Tasks | production/admin_order_tasks.html | /production/admin/tasks/ | P2 | YELLOW |
| Admin Tasks Mgmt | production/admin_tasks_management.html | /production/admin/tasks/manage/ | P2 | YELLOW |
| Item Detail | production/item.html | /production/item/<id>/ | P1 | YELLOW |
| Create Step 1 | production/orders/create_step1.html | /production/orders/create/step1/ | P1 | YELLOW |
| Create Step 2 | production/orders/create_step2.html | /production/orders/create/step2/ | P1 | YELLOW |
| Add Item | production/orders/add_item.html | /production/orders/<id>/add-item/ | P1 | YELLOW |
| Add Colors | production/orders/add_colors.html | /production/items/<id>/colors/ | P1 | YELLOW |
| Assign Painting | production/assign_painting.html | /production/assign-painting/ | P2 | YELLOW |
| Import Data | production/import_data.html | /production/import/ | P3 | YELLOW |

---

## Painting Management Pages

| Page | Template | URL | Priority | Status |
|------|----------|-----|----------|--------|
| Painting Dashboard | production/painting_management/dashboard.html | /production/painting/ | P1 | YELLOW |
| Painting Schedule | production/painting_management/schedule.html | /production/painting/schedule/ | P1 | YELLOW |
| Painting Workers | production/painting_management/workers.html | /production/painting/workers/ | P0 | **RED** |
| Ready List | production/painting_management/ready_list.html | /production/painting/ready/ | P2 | YELLOW |
| Assignment Rules | production/painting_management/assignment_rules.html | /production/painting/rules/ | P2 | YELLOW |
| Processes | production/painting_management/processes.html | /production/painting/processes/ | P2 | YELLOW |

---

## Critical Path Analysis

### P0: Worker Management (RED)

**Pages affected:**
- production/worker_list.html
- production/painting_management/workers.html

**Blockers:**
- Select2 jQuery plugin for worker dropdowns
- Bootstrap Modal for worker detail popups
- Bootstrap Tooltip for inline help
- jQuery event handlers for form interactions

**Migration steps:**
1. Create Alpine.js combobox component to replace Select2
2. Create Alpine modal component to replace Bootstrap Modal
3. Create Alpine tooltip component to replace Bootstrap Tooltip
4. Convert jQuery event handlers to Alpine directives
5. Remove select2 CSS/JS from templates
6. Test worker search, filter, and detail workflows

**Estimated effort:** 2-3 days

---

### P1: Order Management (YELLOW)

**Pages affected:**
- production/order_list.html
- production/orders/order_detail.html
- production/order_item.html
- production/create_order.html
- production/create_complete.html
- production/create_unified.html
- production/orders/create_step1.html
- production/orders/create_step2.html
- production/orders/add_item.html
- production/orders/add_colors.html
- production/admin_order_edit.html
- production/item.html

**Blockers:**
- Bootstrap grid and card components
- bootstrap.Modal for order detail preview
- Inline `<style>` blocks in create_step2.html
- Vanilla JS with fetch in create_step1.html (not Alpine)

**Migration steps:**
1. Convert Bootstrap grid to Tailwind grid (`row` → `flex`, `col-md-*` → `w-1/2`)
2. Convert Bootstrap cards to Tailwind (`card shadow` → `bg-white rounded-xl shadow-md`)
3. Convert Bootstrap buttons to Tailwind (`btn btn-primary` → `bg-primary text-white px-4 py-2 rounded`)
4. Convert Bootstrap form controls to Tailwind (`form-control` → `w-full border rounded px-3 py-2`)
5. Replace bootstrap.Modal with Alpine modal
6. Convert vanilla JS fetch to Alpine data + Fetch API
7. Remove inline `<style>` blocks

**Estimated effort:** 5-7 days

---

### P1: Kanban Board (YELLOW)

**Pages affected:**
- production/kanban.html

**Blockers:**
- HTML5 Drag and Drop API with localStorage
- Bootstrap card styling for kanban cards

**Migration steps:**
1. Convert Bootstrap cards to Tailwind
2. Replace localStorage with HTMX server sync
3. Add proper error handling for failed moves
4. Add loading states during HTMX requests

**Estimated effort:** 2-3 days

---

### P1: Painting Dashboard & Schedule (YELLOW)

**Pages affected:**
- production/painting_management/dashboard.html
- production/painting_management/schedule.html

**Blockers:**
- Custom painting.css classes
- Bootstrap grid and components
- Alpine.js already in use (partial migration)

**Migration steps:**
1. Audit painting.css for actually-used classes
2. Convert used classes to Tailwind utilities
3. Remove unused painting.css classes
4. Convert Bootstrap grid to Tailwind

**Estimated effort:** 3-4 days

---

### P2: Admin & Supporting Pages (YELLOW)

**Pages affected:**
- production/admin_product_list.html
- production/admin_edit_order_item.html
- production/admin_order_tasks.html
- production/admin_tasks_management.html
- production/product_bom_edit.html
- production/product_create.html
- production/scan_part.html
- production/set_plate.html
- production/scan_packaging_unit.html
- production/select_shipment.html
- production/painting_management/ready_list.html
- production/painting_management/assignment_rules.html
- production/painting_management/processes.html
- production/assign_painting.html

**Blockers:**
- Bootstrap grid and components
- bootstrap.Modal in bom.js
- Bootstrap JS in painting/processes.js

**Migration steps:**
1. Batch convert Bootstrap grid to Tailwind
2. Batch convert Bootstrap components to Tailwind
3. Replace bootstrap.Modal with Alpine modal
4. Replace Bootstrap JS with Alpine in painting/processes.js

**Estimated effort:** 5-7 days

---

### P3: Print & Import Pages (YELLOW)

**Pages affected:**
- production/order_print.html
- production/print.html
- production/report.html
- production/import_data.html

**Blockers:**
- Bootstrap grid for layout
- Inline styles in print templates

**Migration steps:**
1. Create Tailwind-based print layout
2. Convert Bootstrap grid to Tailwind
3. Extract inline styles to CSS

**Estimated effort:** 1-2 days

---

## Production Template Architecture

### Current Architecture (YELLOW/RED)

```
┌─────────────────────────────────────────────────┐
│ layouts/dashboard.html                          │
│ ├── bootstrap.rtl.min.css                       │
│ ├── bootstrap-icons.css                         │
│ ├── vazirmatn-fonts.css                         │
│ ├── dashboard.css (custom overrides)            │
│ ├── components.css (shared)                     │
│ ├── jQuery                                      │
│ ├── bootstrap.bundle.js                         │
│ ├── Alpine.js                                   │
│ ├── alpine-bootstrap.js (Bootstrap interop)     │
│ └── app.js (module initialization)              │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ production/base.html                            │
│ ├── Production navbar                           │
│ └── Production sidebar                          │
└─────────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────────┐
   │ Orders  │ │ Products│ │  Painting   │
   │ Pages   │ │ Pages   │ │  Management │
   └─────────┘ └─────────┘ └─────────────┘
```

### Target Architecture (GREEN)

```
┌─────────────────────────────────────────────────┐
│ layouts/dashboard_v2.html                       │
│ ├── style.css (Tailwind, extended)              │
│ ├── bootstrap-icons.css                         │
│ ├── vazirmatn-fonts.css                         │
│ ├── components.css (Tailwind @layer)            │
│ ├── Alpine.js                                   │
│ ├── HTMX                                        │
│ └── app.js (Alpine modules only)                │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ production/base_v2.html                         │
│ ├── Production navbar (Tailwind)                │
│ └── Production sidebar (Tailwind)               │
└─────────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────────┐
   │ Orders  │ │ Products│ │  Painting   │
   │ Pages   │ │ Pages   │ │  Management │
   │(Tailwind)│ │(Tailwind)│ │  (Tailwind) │
   └─────────┘ └─────────┘ └─────────────┘
```

---

## Production CSS Migration

### Current CSS Delivery

| File | Size | Purpose |
|------|------|---------|
| bootstrap.rtl.min.css | ~150KB | Bootstrap RTL stylesheet |
| bootstrap-icons.css | ~80KB | Icon font |
| vazirmatn-fonts.css | ~2KB | Font faces |
| dashboard.css | ~6KB | Custom overrides |
| components.css | ~8KB | Shared components |
| pages/painting.css | ~15KB | Painting-specific |

**Total:** ~261KB CSS

### Target CSS Delivery

| File | Size | Purpose |
|------|------|---------|
| style.css (extended) | ~220KB | Tailwind (includes production utilities) |
| bootstrap-icons.css | ~80KB | Icon font |
| vazirmatn-fonts.css | ~2KB | Font faces |
| components.css | ~5KB | Remaining custom components |

**Total:** ~307KB CSS (but cached, and no jQuery/Bootstrap JS)

**Net benefit:** Removing jQuery (~90KB JS) + Bootstrap JS (~60KB JS) = ~150KB JS savings

---

## Production JS Migration

### Current JS Delivery

| File | Size | Framework |
|------|------|-----------|
| jquery.min.js | ~90KB | jQuery |
| bootstrap.bundle.min.js | ~60KB | Bootstrap JS |
| alpine.min.js | ~30KB | Alpine.js |
| alpine-bootstrap.js | ~2KB | Bootstrap interop |
| select2.min.js | ~60KB | Select2 (painting workers) |
| app.js | ~3KB | Module init |
| production/*.js | ~25KB | Production modules |
| painting/*.js | ~10KB | Painting modules |

**Total:** ~280KB JS

### Target JS Delivery

| File | Size | Framework |
|------|------|-----------|
| alpine.min.js | ~30KB | Alpine.js |
| htmx.min.js | ~15KB | HTMX |
| app.js | ~3KB | Module init |
| production/*.js | ~20KB | Production modules (no jQuery) |
| painting/*.js | ~8KB | Painting modules (no Bootstrap JS) |

**Total:** ~76KB JS

**Savings:** ~204KB JS (73% reduction)

---

## Production Migration Sequence

### Sprint 1: Foundation (Week 1)
1. Create `layouts/dashboard_v2.html` with Tailwind
2. Extend `tailwind-input.css` with production design tokens
3. Create `production/base_v2.html`
4. Test with simple production page

### Sprint 2: Worker Management (Week 2)
1. Build Alpine combobox component
2. Build Alpine modal component
3. Build Alpine tooltip component
4. Migrate worker_list.html
5. Migrate painting/workers.html
6. Remove Select2 dependency

### Sprint 3: Order Creation Flow (Week 3)
1. Migrate create_step1.html
2. Migrate create_step2.html
3. Migrate add_item.html
4. Migrate add_colors.html
5. Migrate create_order.html
6. Migrate create_complete.html
7. Migrate create_unified.html

### Sprint 4: Order Management (Week 4)
1. Migrate order_list.html
2. Migrate order_detail.html
3. Migrate order_item.html
4. Migrate admin_order_edit.html
5. Migrate item.html

### Sprint 5: Kanban & Products (Week 5)
1. Migrate kanban.html (with HTMX sync)
2. Migrate product_bom_edit.html
3. Migrate product_create.html
4. Migrate admin_product_list.html

### Sprint 6: Painting Management (Week 6)
1. Convert painting.css to Tailwind
2. Migrate painting/dashboard.html
3. Migrate painting/schedule.html
4. Migrate painting/ready_list.html
5. Migrate painting/assignment_rules.html
6. Migrate painting/processes.html

### Sprint 7: Remaining Pages (Week 7)
1. Migrate scan_part.html
2. Migrate set_plate.html
3. Migrate scan_packaging_unit.html
4. Migrate select_shipment.html
5. Migrate admin_edit_order_item.html
6. Migrate admin_order_tasks.html
7. Migrate admin_tasks_management.html
8. Migrate assign_painting.html

### Sprint 8: Print & Cleanup (Week 8)
1. Migrate print templates
2. Migrate import_data.html
3. Remove old dashboard.html
4. Remove old production/base.html
5. Remove old painting_management/base.html
6. Remove jQuery, Bootstrap JS, Select2
7. Remove dashboard.css, painting.css, shipped.css

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Select2 replacement breaks worker search | Medium | High | Thorough testing, feature parity |
| HTMX server sync adds latency | Low | Medium | Optimistic UI updates |
| Custom painting.css has hidden dependencies | High | Medium | Audit all class usage before removal |
| Production team resistance | Medium | High | Training, documentation, gradual rollout |
| Regression in order creation flow | Medium | High | Comprehensive test suite |
| Performance regression with large tables | Low | Medium | Virtual scrolling, pagination |

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Total CSS | ~261KB | ~307KB (but cached) |
| Total JS | ~280KB | ~76KB |
| jQuery dependency | Yes | No |
| Bootstrap JS dependency | Yes | No |
| Select2 dependency | Yes | No |
| Alpine.js coverage | ~60% | ~100% |
| HTMX usage | Storefront + 1 prod | All async operations |
| Template classification | 0% GREEN | 100% GREEN |
