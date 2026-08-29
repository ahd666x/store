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

## PHASE 5: COMPONENT MIGRATION (Week 10-12)
**Goal:** Migrate all templates to use shared component library

### 5.1 Migration Order (Dependency-First)
1. **Base templates** → Unified base with shared partials
2. **Navbars** → Single navbar component with variants
3. **Footers** → Single footer component
4. **Cards** → Component library cards
5. **Forms** → Component library forms
6. **Tables** → Component library tables
7. **Modals** → Alpine.js modal component
8. **Filters** → Component library filters
9. **Pagination** → Component library pagination
10. **Empty/Loading states** → Component library states

### 5.2 Template-by-Template Migration
| Priority | Template | Effort | Dependencies |
|----------|----------|--------|--------------|
| 1 | `home.html` | Medium | Cards, hero, testimonials |
| 2 | `catalog/product_list.html` | High | Filters, product cards, pagination |
| 3 | `catalog/product_detail.html` | High | Gallery, variants, reviews |
| 4 | `production/dashboard.html` | Low | Quick link cards |
| 5 | `production/order_list.html` | Medium | Table, filters, pagination |
| 6 | `production/admin_product_list.html` | Medium | Table, filters |
| 7 | `production/product_create.html` | High | Form, formset, modal |
| 8 | `painting_management/workers.html` | Very High | Table, Select2, modals, complex JS |
| 9 | `painting_management/schedule.html` | High | Calendar, assignments |
| 10 | `production/shop/*.html` | Medium | Product cards, cart, checkout |

### 5.3 Component Library Documentation
Create `docs/components/` with:
- `navbar.md` - Usage, variants, props
- `card.md` - Usage, variants, props
- `form.md` - Usage, validation patterns
- `table.md` - Usage, sorting, pagination
- `modal.md` - Usage, sizes, triggers
- `filter.md` - Usage, URL state management

**Phase 5 Exit Criteria:**
- [ ] 50% of templates use component library
- [ ] Zero inline `<style>` blocks
- [ ] Zero inline `<script>` blocks
- [ ] Component documentation complete

---

## PHASE 6: ADVANCED FEATURES (Week 12-14)
**Goal:** Modern UX patterns, performance optimization

### 6.1 Loading & Empty States
| Component | Implementation | Usage |
|-----------|----------------|-------|
| `loading_spinner.html` | Alpine.js + CSS | Button loading, page loading |
| `skeleton_card.html` | Tailwind animate-pulse | Product list loading |
| `skeleton_table.html` | Tailwind animate-pulse | Table loading |
| `empty_state.html` | Icon + text + CTA | All empty lists |

### 6.2 Error Handling
| Component | Implementation | Usage |
|-----------|----------------|-------|
| `error_boundary.html` | Alpine.js component | Catch JS errors |
| `error_page.html` | Base template | 404, 500, 403 |
| `form_errors.html` | Include | Form validation display |

### 6.3 Performance Optimization
| Task | Action | Expected Gain |
|------|--------|---------------|
| Image optimization | Add `srcset`, `sizes`, lazy loading | 30-50% image weight |
| Font optimization | Add `preload` for Vazirmatn | 100ms FCP improvement |
| CSS purging | Verify Tailwind purge config | 60-70% CSS size |
| JS splitting | Code split by route | 40-50% JS initial load |
| CDN for vendor | Serve jQuery/Bootstrap from CDN | Faster cache hits |

### 6.4 Accessibility Audit
| Task | Tool | Action |
|------|------|--------|
| Automated audit | axe-core | Fix all critical issues |
| Keyboard navigation | Manual testing | Tab order, focus trap |
| Screen reader | NVDA/JAWS | ARIA labels, live regions |
| Color contrast | WAVE | Fix contrast ratios |
| Focus management | Manual | Focus trap in modals |

**Phase 6 Exit Criteria:**
- [ ] Lighthouse accessibility score > 90
- [ ] All interactive elements keyboard accessible
- [ ] Zero critical axe violations
- [ ] Page weight < 500KB initial load

---

## PHASE 7: POLISH & DOCUMENTATION (Week 14-16)
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
| Phase 6: Advanced Features | 2 weeks | 1-2 developers | Low |
| Phase 7: Polish & Docs | 2 weeks | 1 developer | Low |
| **Total** | **15 weeks** | **1-2 developers** | **Medium** |

---

## QUICK WINS (Can Do This Week)

1. **Remove duplicate jQuery**: Delete `static/js/jquery-3.6.4*` (saves 22K lines)
2. **Remove unminified Bootstrap**: Delete `static/js/bootstrap.bundle.js` etc. (saves 20K lines)
3. **Rebuild Tailwind**: Run `npm run build:css` (ensures style.css is current)
4. **Add `x-cloak` to CSS**: Move from inline to `tailwind-input.css`
5. **Extract `includes/toast.html`**: Already done - good example
6. **Extract `includes/icons.html`**: Already done - good example
7. **Remove Bootstrap from `base.html`**: Shop doesn't need it
8. **Standardize jQuery version**: Use 3.7.1 everywhere

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
