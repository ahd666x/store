# FRONTEND REFACTOR ROADMAP
## سلوی چوب (Selvi Wood) - Migration Plan

**Target State:** Unified Tailwind CSS architecture, shared component library, no jQuery/Bootstrap dependency  
**Current State:** Dual system (Shop: Tailwind+Alpine+HTMX, Admin: Bootstrap+jQuery), 40+ inline styles, 40+ inline scripts  
**Estimated Duration:** 12-16 weeks (part-time), or 6-8 weeks (full-time)

---

## PHASE 0: FOUNDATION (Week 1-2)
**Goal:** Stabilize current state, fix critical issues, establish build pipeline

### 0.1 Static Asset Cleanup
| Task | Action | Validation |
|------|--------|------------|
| Remove unminified vendor JS | Delete `static/js/jquery-3.6.4.js`, `jquery-3.6.4.slim.js`, `jquery-3.6.4-vsdoc.js`, `bootstrap.bundle.js`, `bootstrap.js`, `bootstrap.esm.js` | `ls static/js/` shows only `.min.js` files |
| Remove duplicate Bootstrap CSS | Delete `static/css/bootstrap*.css` (keep only `vendor/bootstrap.rtl.min.css`) | `ls static/css/bootstrap*` shows only vendor files |
| Standardize jQuery version | Remove `static/js/vendor/jquery-3.6.4*`, keep only `jquery-3.7.1.min.js` | All templates reference 3.7.1 |
| Remove vsdoc files | Delete any `*-vsdoc.js` files | No vsdoc in static/ |

### 0.2 Build Pipeline Verification
| Task | Action | Validation |
|------|--------|------------|
| Rebuild Tailwind output | Run `npm run build:css` | `style.css` is rebuilt from `tailwind-input.css` |
| Verify Tailwind purge | Check `tailwind.config.js` content paths include all templates | Build output size < 500KB |
| Add CSS source map | Enable source maps in PostCSS config | Dev tools shows original class names |
| Add CSS linting | Install `stylelint` with Tailwind plugin | `npm run lint:css` passes |

### 0.3 Critical Bug Fixes
| Task | Action | Validation |
|------|--------|------------|
| Remove Bootstrap from shop | In `templates/base.html`, remove Bootstrap CSS/JS links | Shop pages load without Bootstrap |
| Remove Bootstrap from base_shop | In `production/base_shop.html`, remove Bootstrap CSS/JS | Customer portal works |
| Fix CSRF for fetch calls | Add CSRF token meta tag to base templates | All fetch calls include X-CSRFToken |
| Add `x-cloak` globally | Move `[x-cloak]{display:none!important}` to `tailwind-input.css` | No flash of Alpine content |

**Phase 0 Exit Criteria:**
- [ ] `static/` contains only minified vendor files
- [ ] `style.css` is rebuilt and readable (or source maps available)
- [ ] Shop templates work without Bootstrap CSS
- [ ] No 404s for vendor files

---

## PHASE 1: EXTRACTION (Week 2-4)
**Goal:** Extract all inline styles and scripts to static files

### 1.1 Inline CSS Extraction
**Strategy:** Create `static/css/` modules for each template group

| File | Contents | Source Templates |
|------|----------|------------------|
| `admin.css` | Admin panel styles | `production/base.html` + children |
| `shop.css` | Shop-specific styles | `production/shop/*.html` |
| `painting.css` | Painting management styles | `painting_management/base.html` + children |
| `print.css` | Shared print styles | All print templates |
| `login.css` | Login page styles | `registration/login.html` |

**Process per template:**
1. Identify `<style>` block content
2. Move to appropriate CSS file
3. Replace `<style>` with `<link rel="stylesheet" href="{% static 'css/admin.css' %}">`
4. Convert custom classes to Tailwind utilities where possible
5. Test visually

### 1.2 Inline JavaScript Extraction
**Strategy:** Create `static/js/` modules by feature

| File | Contents | Source Templates |
|------|----------|------------------|
| `admin.js` | Admin interactions | `production/order_list.html`, etc. |
| `shop.js` | Shop interactions | `home.html`, `catalog/*.html` |
| `painting.js` | Painting interactions | `painting_management/*.html` |
| `cart.js` | Cart logic (merge with HTMX) | `cart-actions.html` |
| `print.js` | Print-specific JS | Print templates |
| `vendor-extensions.js` | jQuery plugin inits (Select2, etc.) | Various |

**Process per template:**
1. Identify `<script>` block content
2. Move to appropriate JS file
3. Wrap in `DOMContentLoaded` or module pattern
4. Add to base template `extra_js` block
5. Test functionality

### 1.3 Template Partial Extraction
**Strategy:** Extract repeated markup into Django includes

| Partial | Extract From | Used In |
|---------|--------------|---------|
| `includes/admin_nav.html` | `production/base.html` | All admin templates |
| `includes/admin_footer.html` | `production/base.html` | All admin templates |
| `includes/shop_nav.html` | `includes/header.html` | All shop templates |
| `includes/shop_footer.html` | `includes/footer.html` | All shop templates |
| `includes/breadcrumb.html` | `catalog/*.html` | All catalog pages |
| `includes/pagination.html` | `order_list.html` | All paginated lists |
| `includes/filter_form.html` | Multiple | All filtered lists |
| `includes/status_badge.html` | `order_list.html` | Order templates |
| `includes/empty_state.html` | Multiple | All list pages |
| `includes/loading_spinner.html` | New | All async operations |

**Phase 1 Exit Criteria:**
- [ ] Zero inline `<style>` blocks in templates
- [ ] Zero inline `<script>` blocks (except `cart-actions.html` which uses HTMX)
- [ ] All repeated markup extracted to includes
- [ ] Visual regression: 100% feature parity

---

## PHASE 2: BASE TEMPLATE UNIFICATION (Week 4-6)
**Goal:** Create unified base templates that share common infrastructure

### 2.1 Create Shared Base Layer
```
templates/
└── _base/
    ├── _html_head.html ............... Shared <head>, meta, CSS links
    ├── _body_open.html ............... <body> open, global scripts
    ├── _messages.html ................ Flash messages component
    ├── _footer.html .................. Shared footer
    └── _body_close.html .............. Closing scripts, </body>
```

### 2.2 Unify Shop Base
**Action:** Refactor `templates/base.html` to use shared partials

```
templates/base.html (NEW)
{% extends '_base/_html_head.html' %}
{% block extra_head %}{% endblock %}
</head>
{% include '_base/_body_open.html' %}
{% include '_base/_messages.html' %}
{% block content %}{% endblock %}
{% include '_base/_footer.html' %}
{% include '_base/_body_close.html' %}
```

### 2.3 Unify Admin Base
**Action:** Refactor `production/base.html` similarly

**Challenge:** Admin uses Bootstrap, shop uses Tailwind
**Solution:** Create two CSS layers:
1. `admin-layout.css` - Bootstrap grid + reset
2. `admin-components.css` - Tailwind-like component classes

### 2.4 Create Component Library
```
templates/components/
├── navbar/
│   ├── shop.html .................... Alpine.js navbar
│   └── admin.html ................... Bootstrap navbar
├── cards/
│   ├── product_card.html ............ Product display
│   ├── stat_card.html ............... Dashboard stats
│   └── quick_link_card.html ......... Dashboard links
├── forms/
│   ├── text_input.html .............. Standard text input
│   ├── select_input.html ............ Standard select
│   ├── search_form.html ............. Search with button
│   └── filter_sidebar.html .......... Filter panel
├── tables/
│   ├── data_table.html .............. Sortable, paginated table
│   └── clickable_row_table.html ..... Row-click navigation
├── modals/
│   ├── confirm_modal.html ........... Delete confirm
│   └── form_modal.html .............. Form in modal
└── feedback/
    ├── toast.html ................... Notification toast
    ├── alert.html ................... Inline alert
    ├── empty_state.html ............. Empty list message
    └── loading.html ................. Spinner/skeleton
```

**Phase 2 Exit Criteria:**
- [ ] All base templates use shared partials
- [ ] Component library has 80% of common patterns
- [ ] No duplicate `<head>` or `<body>` markup
- [ ] Both shop and admin can switch layouts by changing one template

---

## PHASE 3: CSS CONSOLIDATION (Week 6-8)
**Goal:** Single CSS architecture, eliminate framework conflicts

### 3.1 Remove Bootstrap Dependency
**Approach:** Gradual replacement, template by template

| Week | Templates | Action |
|------|-----------|--------|
| 6 | `production/base_shop.html` + children | Replace Bootstrap with Tailwind |
| 7 | `production/painting_management/*` | Replace Bootstrap with Tailwind |
| 8 | `production/*.html` (remaining) | Replace Bootstrap with Tailwind |

### 3.2 Bootstrap → Tailwind Mapping
| Bootstrap Class | Tailwind Equivalent | Notes |
|-----------------|---------------------|-------|
| `.container` | `.section-container` | Already defined |
| `.row` | `.grid` / `.flex` | Direct mapping |
| `.col-md-3` | `.md:w-1/4` | Direct mapping |
| `.card` | `.card` | Already defined in tailwind-input.css |
| `.btn` | `.btn` | Already defined |
| `.form-control` | `.form-input` | Already defined |
| `.table` | `.table-modern` | Already defined |
| `.alert` | `.alert` | Already defined |
| `.badge` | `.badge` | Already defined |
| `.navbar` | Custom header | Needs Alpine.js rewrite |

### 3.3 CSS File Structure (Target)
```
static/css/
├── style.css ......................... Compiled Tailwind (single source of truth)
├── tailwind-input.css ................ Tailwind source + @layer components
├── admin.css ......................... Admin-only overrides (temporary)
├── shop.css .......................... Shop-only overrides (temporary)
├── print.css ......................... Print styles
├── fonts/
│   └── vazirmatn-fonts.css ........... Font faces
└── vendor/ ........................... Only minified vendor files
    ├── bootstrap.rtl.min.css ......... (kept for gradual migration)
    └── select2.min.css ............... (kept for painting module)
```

### 3.4 Purge Unused CSS
| Action | Tool | Validation |
|--------|------|------------|
| Run PurgeCSS | `@fullhuman/postcss-purgecss` | Output < 100KB |
| Remove unused Bootstrap | Manual audit after purge | No `.row`/`.col` in shop CSS |
| Verify RTL support | Test all pages in RTL | No LTR artifacts |

**Phase 3 Exit Criteria:**
- [ ] `bootstrap.css` removed from shop templates
- [ ] `style.css` rebuilt and < 200KB gzipped
- [ ] No `!important` in production CSS
- [ ] Zero inline `<style>` blocks

---

## PHASE 4: JAVASCRIPT CONSOLIDATION (Week 8-10)
**Goal:** Single JS architecture, eliminate jQuery dependency

### 4.1 Remove jQuery Dependency
**Strategy:** Replace jQuery with vanilla JS or Alpine.js

| jQuery Pattern | Replacement | Complexity |
|----------------|-------------|------------|
| `$(document).ready()` | `DOMContentLoaded` | Low |
| `$('.class').click()` | `document.querySelectorAll` | Low |
| `$('.class').on('click')` | `addEventListener` | Low |
| `$('#id').val()` | `document.getElementById().value` | Low |
| `$('#id').html()` | `element.innerHTML` | Low |
| `$.ajax()` | `fetch()` | Medium |
| `$.each()` | `forEach` | Low |
| Select2 initialization | Alpine.js component | High |
| Bootstrap modal trigger | Alpine.js modal | Medium |

### 4.2 Create JS Modules
```
static/js/
├── main.js ............................ App initialization
├── cart.js ............................ Cart logic (HTMX + vanilla)
├── filters.js ......................... Filter forms, URL state
├── tables.js .......................... Sortable tables, row clicks
├── modals.js .......................... Modal management (Alpine)
├── forms.js ........................... Form validation, AJAX submit
├── print.js ........................... Print triggers
└── vendor-extensions.js ............... Select2 init (if kept)
```

### 4.3 Alpine.js Components
| Component | Replaces | Location |
|-----------|----------|----------|
| `x-data="modal"` | Bootstrap modal | All modals |
| `x-data="dropdown"` | Bootstrap dropdown | All dropdowns |
| `x-data="carousel"` | Bootstrap carousel | If used |
| `x-data="tabs"` | Bootstrap tabs | If used |
| `x-data="select2"` | Select2 | Painting workers |

### 4.4 Remove jQuery
| Step | Action | Validation |
|------|--------|------------|
| 1 | Remove jQuery from `base.html` | Shop works without jQuery |
| 2 | Remove jQuery from `production/base.html` | Admin works without jQuery |
| 3 | Replace `$()` calls in extracted JS | All tests pass |
| 4 | Delete `static/js/jquery-*` | No jQuery files remain |
| 5 | Remove Bootstrap JS | No Bootstrap JS files remain |

**Phase 4 Exit Criteria:**
- [ ] Zero jQuery usage in templates
- [ ] Zero Bootstrap JS usage
- [ ] All interactions work with Alpine.js + vanilla JS
- [ ] `static/js/` contains only app code + 2 vendor files (HTMX, Alpine)

---

## PHASE 5: COMPONENT MIGRATION (Week 10-12) ✅ COMPLETED
**Goal:** Migrate all templates to use shared component library

**Completed:**
- Modular JS architecture established (12 modules)
- Inline scripts removed from 31 templates
- Phase 5 committed as `1df77c2` to `origin/main`
- Migration Readiness Audit performed across 102 templates
- `FRONTEND_MIGRATION_STATUS.md` created with per-template matrix
- `JAVASCRIPT_ARCHITECTURE.md` created

**Phase 5 Exit Criteria:**
- [x] 50% of templates use component library (43% GREEN)
- [x] Zero inline `<style>` blocks in migrated templates
- [x] Zero inline `<script>` blocks in migrated templates
- [x] Component documentation complete

---

## PHASE 6: ADMIN PANEL MIGRATION (Week 12-21) ✅ IN PROGRESS
**Goal:** Migrate admin/production panel from Bootstrap to Tailwind while maintaining production-critical workflows

### Phase 6 Goal: Complete Admin Panel Migration

The admin/production panel must be migrated from Bootstrap to Tailwind while maintaining production-critical workflows.

### Execution Order

#### Week 1: Critical Bug Fixes + Foundation

1. **Fix painting management modals (P0)**
   - Load `bootstrap.bundle.min.js` in `painting_management/base.html` temporarily
   - OR rewrite modals using Alpine.js (preferred for long-term)
   - Validate all 5 painting modal templates work

2. **Fix Select2 (P0)**
   - Load jQuery in `painting_management/base.html` temporarily
   - OR replace Select2 with Alpine.js multi-select (preferred)

3. **Remove orphaned vendor files**
   - Delete all duplicate jQuery/Bootstrap JS files
   - Validate no 404s

#### Week 2: Layout Consolidation

4. **Migrate `layouts/dashboard.html`**
   - Remove Bootstrap CSS links
   - Add Tailwind utilities for any Bootstrap-dependent styles
   - Update `components.css` classes to Tailwind

5. **Migrate `production/base.html`**
   - Replace Bootstrap navbar classes with Tailwind
   - Keep Alpine mobile toggle

6. **Migrate `production/base_shop.html`**
   - Replace Bootstrap navbar classes with Tailwind
   - Remove inline CSS from `extra_css`

7. **Migrate `painting_management/base.html`**
   - Remove `painting.css` dependency
   - Migrate custom nav to Tailwind

#### Week 3: Component Library Completion

8. **Migrate Bootstrap-dependent components**
   - `components/tables/table.html` → Tailwind table classes
   - `components/tables/pagination.html` → Tailwind pagination
   - `components/modals/modal.html` → Alpine.js modal
   - `components/data/status_badge.html` → Tailwind badges
   - `components/data/badge.html` → Tailwind badges
   - `components/feedback/alert.html` → Tailwind alerts
   - `components/loading/loading_overlay.html` → Tailwind spinner

9. **Update `orders/includes/status_badge.html`**
   - Replace Bootstrap badge classes with Tailwind

#### Week 4: Low-Risk Admin Templates

10. **Migrate simple admin templates**
    - `production/dashboard.html`
    - `production/task_list.html`
    - `production/worker_list.html`
    - `production/kanban.html`
    - `production/admin_order_tasks.html`
    - `production/reports/workers.html`
    - `production/reports/orders.html`
    - `production/reports/delayed.html`

#### Week 5: Medium-Risk Admin Templates

11. **Migrate order/item templates**
    - `production/order_list.html` (inline JS → module)
    - `production/order_item.html` (inline JS → module)
    - `production/admin_product_list.html` (inline CSS → utility)
    - `production/item.html` (inline CSS → utility)

12. **Migrate report templates**
    - `production/reports/stages.html` (complex inline CSS + JS)

#### Week 6: High-Risk Production Templates

13. **Migrate critical production workflows**
    - `production/scan_part.html` (validate scanner.js)
    - `production/scan_packaging_unit.html` (validate scanner.js)
    - `production/product_create.html` (BOM formset, part modal)
    - `production/product_bom_edit.html` (inline JS for BOM rows)

14. **Migrate order creation flow**
    - `production/create_unified.html`
    - `production/orders/create_step1.html`
    - `production/orders/create_step2.html`
    - `production/orders/order_detail.html`

#### Week 7: High-Risk Admin Edit Templates

15. **Migrate admin edit templates**
    - `production/admin_order_edit.html`
    - `production/admin_edit_order_item.html`

#### Week 8: Painting Management (Highest Complexity)

16. **Migrate painting management templates**
    - `painting_management/processes.html` (fix Bootstrap Modal first)
    - `painting_management/stages.html` (fix Bootstrap Modal first)
    - `painting_management/holidays.html` (fix Bootstrap Modal first)
    - `painting_management/assignment_rules.html` (fix Bootstrap Modal first)
    - `painting_management/workers.html` (fix Bootstrap Modal + Select2 first)
    - `painting_management/schedule.html` (kanban CSS migration)
    - `painting_management/ready_list.html` (inline CSS migration)

#### Week 9: Print Templates + Shop Admin

17. **Migrate print/report templates**
    - `production/print.html`
    - `production/order_print.html`
    - `production/order_combined_print.html`
    - `production/order_invoice.html`
    - `production/daily_schedule_print.html`
    - `production/print_lable.html`
    - `production/print_lable_part.html`
    - `production/reports/shipped.html`
    - `production/reports/delivery_note.html`

18. **Migrate customer shop templates**
    - `production/shop/*.html`
    - `production/customer/*.html`

#### Week 10: CSS/JS Cleanup

19. **Remove Bootstrap CSS completely**
    - Delete `bootstrap.rtl.min.css`, `bootstrap-icons.css`
    - Remove from `layouts/dashboard.html`

20. **Remove Select2 and jQuery**
    - Replace with Alpine.js alternatives
    - Delete vendor files

21. **Consolidate CSS files**
    - Merge `components.css`, `dashboard.css`, `product-grid.css`, `pages/*.css` into `tailwind-input.css`

**Phase 6 Exit Criteria:**
- [ ] 100% templates migrated to Tailwind (0% RED, 0% YELLOW)
- [ ] Zero Bootstrap CSS files
- [ ] Zero jQuery usage
- [ ] Zero inline `<style>` blocks
- [ ] Zero inline `<script>` blocks
- [ ] CSS size < 150KB gzipped
- [ ] All production-critical workflows validated

---

## PHASE 7: POLISH & DOCUMENTATION (Week 21-24)
**Goal:** Final polish, documentation, handoff

### 7.1 Documentation
| Document | Purpose |
|----------|---------|
| `FRONTEND_ARCHITECTURE.md` | System overview, base templates |
| `COMPONENT_LIBRARY.md` | All components, usage examples |
| `STYLE_GUIDE.md` | Design tokens, spacing, typography |
| `MIGRATION_GUIDE.md` | How to add new pages |
| `JS_PATTERNS.md` | Alpine.js patterns, vanilla JS helpers |

### 7.2 Developer Experience
| Task | Action |
|------|--------|
| VS Code snippets | Create snippets for common components |
| ESLint config | Add Alpine.js, HTML linting |
| Prettier config | Format HTML, CSS, JS |
| Git hooks | Pre-commit linting |
| Storybook | Optional: Component explorer |

### 7.3 Testing
| Test Type | Scope | Tool |
|-----------|-------|------|
| Visual regression | All pages | Percy/Chromatic |
| E2E tests | Critical flows | Playwright |
| Unit tests | JS modules | Vitest |
| Accessibility tests | All pages | axe-playwright |

### 7.4 Performance Monitoring
| Metric | Target | Tool |
|--------|--------|------|
| LCP | < 2.5s | Web Vitals |
| FID | < 100ms | Web Vitals |
| CLS | < 0.1 | Web Vitals |
| Bundle size | < 200KB initial | Bundle analyzer |

**Phase 7 Exit Criteria:**
- [ ] Documentation complete
- [ ] All tests passing
- [ ] Performance targets met
- [ ] Code review approved

---

## MIGRATION SAFEGUARDS

### 1. Backward Compatibility
- **Never break existing URLs**: All URL patterns remain unchanged
- **Progressive enhancement**: New features degrade gracefully
- **Feature flags**: Use Django settings for new vs old templates

### 2. Rollback Strategy
```
# Enable old templates via settings
FRONTEND_VERSION = 'v1'  # or 'v2'

# urls.py
if settings.FRONTEND_VERSION == 'v2':
    urlpatterns = [new_patterns]
else:
    urlpatterns = [old_patterns]
```

### 3. Testing Protocol
| Step | Action | Gate |
|------|--------|------|
| 1 | Run existing tests | Must pass |
| 2 | Visual regression test | Must match baseline |
| 3 | Manual QA on staging | Sign-off required |
| 4 | Deploy to production | Canary 10% → 100% |
| 5 | Monitor errors | 24h observation |

### 4. Risk Mitigation
| Risk | Mitigation |
|------|------------|
| CSS conflicts during migration | Use CSS modules scoping temporarily |
| JS breakage | Feature flags, gradual rollout |
| Template regression | Git branches per phase |
| Performance regression | Lighthouse CI in pipeline |
| Team confusion | Documentation, training sessions |

---

## ESTIMATED EFFORT

| Phase | Duration | Team | Risk |
|-------|----------|------|------|
| Phase 0: Foundation | 1 week | 1 developer | Low |
| Phase 1: Extraction | 2 weeks | 1-2 developers | Medium |
| Phase 2: Unification | 2 weeks | 1-2 developers | Medium |
| Phase 3: CSS Consolidation | 2 weeks | 1-2 developers | High |
| Phase 4: JS Consolidation | 2 weeks | 1-2 developers | High |
| Phase 5: Component Migration | 2 weeks | 2 developers | Medium |
| Phase 6: Admin Panel Migration | 10 weeks | 1 developer | High |
| Phase 7: Polish & Docs | 2 weeks | 1 developer | Low |
| **Total** | **23 weeks** | **1-2 developers** | **Medium** |

---

## PHASE 6 QUICK WINS

1. **Fix painting management modals**: Load `bootstrap.bundle.min.js` temporarily or rewrite with Alpine.js
2. **Fix Select2**: Load jQuery temporarily or replace with Alpine.js multi-select
3. **Remove orphaned vendor files**: Delete all duplicate jQuery/Bootstrap JS files
4. **Migrate `layouts/dashboard.html`**: Remove Bootstrap CSS, add Tailwind utilities
5. **Migrate `production/base.html`**: Replace Bootstrap navbar with Tailwind
6. **Consolidate CSS files**: Merge `components.css`, `dashboard.css`, `product-grid.css` into `tailwind-input.css`

---

## ANTI-PATTERNS TO AVOID

| Anti-Pattern | Why Bad | Alternative |
|---------------|---------|-------------|
| Adding more inline styles | Increases technical debt | Extract to CSS/utility classes |
| Copy-pasting components | Creates maintenance burden | Use Django includes |
| Mixing Bootstrap and Tailwind | CSS conflicts, bloat | Choose one per template |
| Inline event handlers | Hard to maintain, no reusability | Alpine.js or addEventListener |
| jQuery for simple DOM | Unnecessary dependency | Vanilla JS |
| Hardcoded URLs in JS | Breaks on deploy | Use data attributes |
| Magic numbers in CSS | Inconsistent spacing | Use design tokens |
| Commented-out code | Clutters templates | Delete or use version control |

---

## SUCCESS METRICS

| Metric | Current | Target |
|--------|---------|--------|
| CSS files | 25+ | 5-7 |
| JS files | 15+ | 5-7 |
| Inline styles | 40+ | 0 |
| Inline scripts | 40+ | 0 |
| Base templates | 4 | 2 (shop, admin) |
| CSS size (gzipped) | ~500KB+ | < 150KB |
| JS size (gzipped) | ~300KB+ | < 100KB |
| jQuery usage | 100% of templates | 0% |
| Bootstrap usage | 80% of templates | 0% |
| Component library coverage | 0% | 90% |
| Lighthouse Performance | Unknown | > 80 |
| Lighthouse Accessibility | Unknown | > 90 |

---

## DEPENDENCIES & PREREQUISITES

### External Dependencies
- **Node.js**: For Tailwind CSS build (already installed)
- **npm packages**: tailwindcss, postcss, autoprefixer (already in package.json)
- **Optional**: @fullhuman/postcss-purgecss for CSS purging

### Internal Dependencies
- **Django template tags**: No changes needed
- **URL patterns**: No changes needed
- **Views/APIs**: No changes needed
- **Models**: No changes needed

### Team Prerequisites
- Familiarity with Tailwind CSS
- Understanding of Alpine.js reactivity
- Django template inheritance knowledge
- Basic understanding of CSS architecture

---

## CONCLUSION

This roadmap provides a structured approach to modernizing the سلوی چوب frontend. The key principles are:

1. **Incremental migration**: Never break existing functionality
2. **Extract before replace**: Pull out inline code before changing architecture
3. **Unify foundations**: Shared base templates reduce duplication
4. **Component-driven**: Reusable components ensure consistency
5. **Measure everything**: Performance and accessibility targets

The estimated 15-week timeline is realistic for a single developer working part-time, or 6-8 weeks for a dedicated frontend developer. All work can be done without any backend changes.

---

*Roadmap generated by Kilo Frontend Audit - Phase 0*
