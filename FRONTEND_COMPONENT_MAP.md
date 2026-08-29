# FRONTEND COMPONENT MAP
## سلوی چوب (Selvi Wood) - Component Inventory & Relationships

---

## 1. LAYOUT COMPONENTS

### 1.1 Base Templates (Root Layouts)
```
templates/
├── base.html ............................. [SHOP ROOT]
│   ├── HTML: RTL, lang="fa"
│   ├── CSS: Tailwind + Bootstrap RTL (CONFLICT)
│   ├── JS: Alpine.js, HTMX, jQuery 3.7.1, Bootstrap Bundle
│   ├── Blocks: title, meta_description, breadcrumb, content, extra_css, extra_js
│   └── Children: 25+ templates
│
├── production/base.html .................. [ADMIN ROOT]
│   ├── HTML: RTL, lang="fa"
│   ├── CSS: Bootstrap RTL + inline styles
│   ├── JS: jQuery 3.7.1, Bootstrap Bundle
│   ├── Blocks: title, extra_css, content, extra_js
│   └── Children: 40+ templates
│
├── production/base_shop.html ............. [CUSTOMER PORTAL ROOT]
│   ├── HTML: RTL, lang="fa"
│   ├── CSS: Bootstrap RTL + inline styles
│   ├── JS: jQuery 3.6.4, Bootstrap Bundle
│   ├── Blocks: title, extra_css, content, extra_js
│   └── Children: 7 templates
│
└── production/painting_management/
    └── base.html ......................... [PAINTING ROOT]
        ├── HTML: RTL, lang="fa"
        ├── CSS: Bootstrap RTL + extensive inline CSS (195 lines)
        ├── JS: jQuery 3.7.1, Bootstrap Bundle, Select2
        ├── Blocks: title, extra_css, painting_content, extra_js, painting_js
        └── Children: 8 templates
```

### 1.2 Header Components
```
includes/
├── header.html ............................ [SHOP HEADER]
│   ├── Framework: Tailwind + Alpine.js
│   ├── Features: Logo, desktop nav, mobile menu, search, cart count, user dropdown
│   └── Alpine state: mobileMenuOpen, userMenuOpen
│
└── [IMPLICIT HEADERS in production templates]
    ├── production/base.html navbar ....... Bootstrap navbar, simple
    ├── production/base_shop.html navbar ... Bootstrap navbar, customer links
    └── painting_management/base.html ...... Custom CSS header, complex nav
```

### 1.3 Footer Components
```
includes/
└── footer.html ............................ [SHOP FOOTER]
    ├── Framework: Tailwind
    ├── Sections: About, Quick Links, Social Media, Contact
    └── Social Icons: Instagram, Telegram, WhatsApp (inline SVGs)

[NO FOOTER IN PRODUCTION BASE - missing in admin templates]
```

---

## 2. NAVIGATION COMPONENTS

### 2.1 Navbars
| Component | Location | Type | Responsive | User State |
|-----------|----------|------|------------|------------|
| Shop Header | `includes/header.html` | Alpine.js + Tailwind | Full mobile menu | Auth/Anon |
| Admin Navbar | `production/base.html` | Bootstrap collapse | Basic | Auth only |
| Customer Navbar | `production/base_shop.html` | Bootstrap collapse | Basic | Auth only |
| Painting Nav | `painting_management/base.html` | Custom CSS flex | Wraps at 992px | Auth only |

### 2.2 Breadcrumbs
| Component | Location | Pattern |
|-----------|----------|---------|
| Shop Breadcrumb | `catalog/product_list.html` | Inline `<nav>` with Tailwind |
| Product Breadcrumb | `catalog/product_detail.html` | Inline `<nav>` with Tailwind + Schema.org |
| Admin Breadcrumb | Not implemented | Missing |

### 2.3 Sidebar Navigation
| Component | Location | Pattern |
|-----------|----------|---------|
| Shop Filters | `catalog/product_list.html` | Desktop sidebar + mobile drawer |
| Category Filters | `production/shop/product_list.html` | Bootstrap sidebar |
| Painting Nav | `painting_management/base.html` | Horizontal nav links |

---

## 3. CARD COMPONENTS

### 3.1 Product Cards
| Variant | Location | CSS | Features |
|---------|----------|-----|----------|
| Shop Product Card | `home.html` | Tailwind `card-hover` | Image, badge, quick view overlay, rating, price, actions |
| Shop Product Card (alt) | `production/shop/product_list.html` | Inline `.product-card` | Image, category, title, description, button |
| Catalog Product Card | `catalog/includes/product_card.html` | Tailwind | Includes, used in home.html |

### 3.2 Dashboard Cards
| Variant | Location | CSS | Features |
|---------|----------|-----|----------|
| Quick Link Card | `production/dashboard.html` | Inline `.quick-link-card` | Icon, title, hover lift |
| Painting Stat Card | `painting_management/dashboard.html` | Bootstrap `.card` + `.bg-*` | Stat number, label, subtitle |
| Feature Card | `home.html` | Tailwind `card-hover` | Icon, title, description |

### 3.3 Generic Cards
| Variant | Location | CSS | Features |
|---------|----------|-----|----------|
| Admin Card | `production/admin_product_list.html` | Inline `.product-card` | Shadow, hover lift |
| Form Card | Multiple templates | Bootstrap `.card` | Header, body, footer |
| Modal Card | Multiple templates | Bootstrap `.modal-content` | Header, body, footer |

---

## 4. FORM COMPONENTS

### 4.1 Input Styles
| System | Class | Pattern |
|--------|-------|---------|
| Tailwind | `.form-input` | Rounded, border, focus ring |
| Bootstrap | `.form-control` | Bootstrap default |
| Bootstrap | `.form-select` | Select with dropdown arrow |
| Custom | `.input-group` | Flex group with button |

### 4.2 Button Styles
| Variant | Tailwind Class | Bootstrap Class | Usage |
|---------|----------------|-----------------|-------|
| Primary | `.btn-primary` | `.btn-primary` | Both systems |
| Secondary | `.btn-secondary` | `.btn-secondary` | Both systems |
| Danger | `.btn-danger` | `.btn-outline-danger` | Different patterns |
| Ghost | `.btn-ghost` | `.btn-link` | Different patterns |
| Size | `.btn-sm`, `.btn-lg` | `.btn-sm` | Partial overlap |

### 4.3 Form Patterns
| Pattern | Location | Issues |
|---------|----------|--------|
| Product Filter | `catalog/product_list.html` | Mobile drawer + desktop sidebar |
| Order Filter | `production/order_list.html` | Bootstrap form-row |
| Search Input | 10+ templates | Inconsistent styling |
| Date Input | `production/reports/shipped.html` | Uses `fdatepicker` (jQuery) |

---

## 5. TABLE COMPONENTS

### 5.1 Table Variants
| Variant | Location | CSS | Features |
|---------|----------|-----|----------|
| Modern Table | `tailwind-input.css` | `.table-modern` | Hover, compact, RTL |
| Bootstrap Table | Production templates | `.table` + `.table-hover` | Standard Bootstrap |
| Worker Table | `painting_management/workers.html` | `.worker-table` | Custom cell padding |
| Print Table | `print.html` | Inline CSS | Borders, fixed sizes |

### 5.2 Table Features
| Feature | Implementation | Location |
|---------|----------------|----------|
| Clickable rows | `data-href` + JS | `order_list.html`, `admin_product_list.html` |
| Checkbox selection | Custom JS | `order_list.html` |
| Status badges | Inline badges | `order_list.html` |
| Pagination | Bootstrap pagination | `order_list.html`, `admin_product_list.html` |

---

## 6. MODAL COMPONENTS

### 6.1 Modal Inventory
| Modal | Location | Trigger | Size |
|-------|----------|---------|------|
| Part Modal | `product_create.html` | Button click | Large |
| Worker Modal | `painting_management/workers.html` | Button click | Large |
| Exclusion Modal | `painting_management/workers.html` | Button click | Large |
| Delete Modal | `painting_management/workers.html` | Button click | Default |
| Stage Modal | `painting_management/stages.html` | Button click | Default |
| Process Modal | `painting_management/processes.html` | Button click | Default |
| Holiday Modal | `painting_management/holidays.html` | Button click | Default |
| Rule Modal | `painting_management/assignment_rules.html` | Button click | Default |

### 6.2 Modal Pattern
```html
<!-- Standard Bootstrap Modal Pattern -->
<div class="modal fade" id="modalId" tabindex="-1">
    <div class="modal-dialog modal-{size}">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Title</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">...</div>
            <div class="modal-footer">...</div>
        </div>
    </div>
</div>
```

### 6.3 Modal Issues
- **No Alpine.js modals**: All Bootstrap-dependent
- **No modal service**: Each modal independently managed
- **Inconsistent sizing**: `modal-lg`, `modal-dialog` (default), custom widths
- **Focus management**: Relies on Bootstrap defaults

---

## 7. DROPDOWN COMPONENTS

### 7.1 Dropdown Inventory
| Dropdown | Location | Type | Features |
|----------|----------|------|----------|
| User Menu | `includes/header.html` | Alpine.js | Click outside to close |
| Action Dropdown | `painting_management/workers.html` | Bootstrap | Icon button, menu items |
| Filter Dropdown | `production/reports/stages.html` | Bootstrap | Button + menu |
| Stage Dropdown | `painting_management/_worker_rows.html` | Bootstrap | Toggle button |

### 7.2 Dropdown Patterns
| Pattern | Framework | Implementation |
|---------|-----------|----------------|
| Alpine Dropdown | Alpine.js | `x-show`, `@click.away` |
| Bootstrap Dropdown | Bootstrap JS | `data-bs-toggle="dropdown"` |
| Custom Dropdown | Vanilla JS | `painting_management/workers.html` (dropdown action menu) |

---

## 8. BADGE & STATUS COMPONENTS

### 8.1 Badge Variants
| Variant | Tailwind | Bootstrap | Usage |
|---------|----------|-----------|-------|
| Success | `.badge-success` | `.bg-success` | Both |
| Warning | `.badge-warning` | `.bg-warning` | Both |
| Danger | `.badge-danger` | `.bg-danger` | Both |
| Info | `.badge-info` | `.bg-info` | Both |
| Neutral | `.badge-neutral` | `.bg-secondary` | Shop / Admin |
| Status | Custom | `.status-badge` | Order status in admin |

### 8.2 Status Badge Implementation
```
orders/includes/
├── status_badge.html ....................... Order status (Bootstrap)
└── return_status_badge.html ................ Return status (Bootstrap)
```

---

## 9. FEEDBACK COMPONENTS

### 9.1 Toast Notifications
| Component | Location | Framework | Features |
|-----------|----------|-----------|----------|
| Toast Container | `includes/toast.html` | Alpine.js | Auto-dismiss, icons, close button |
| Bootstrap Alert | `production/base.html` | Bootstrap | Dismissible, flash messages |
| Inline Toast | `includes/cart-actions.html` | Vanilla JS | Cart add confirmation |

### 9.2 Alert Patterns
| Pattern | Location | CSS |
|---------|----------|-----|
| Bootstrap Alert | `production/base.html` | `.alert`, `.alert-*` |
| Toast | `includes/toast.html` | Tailwind + Alpine |
| Inline Toast | `cart-actions.html` | Inline styles |

### 9.3 Loading States
| Component | Location | Implementation |
|-----------|----------|----------------|
| Skeleton Text | `tailwind-input.css` | `.skeleton-text` |
| Skeleton Title | `tailwind-input.css` | `.skeleton-title` |
| Skeleton Image | `tailwind-input.css` | `.skeleton-image` |
| Button Loading | `tailwind-input.css` | `.btn.is-loading` |
| Loading Overlay | `painting_management/workers.html` | Custom `.loading-overlay` |

### 9.4 Empty States
| Pattern | Location | Implementation |
|---------|----------|----------------|
| No Products | `home.html` | Icon + text + button |
| No Orders | `production/order_list.html` | Icon + text |
| No Results | `catalog/product_list.html` | Alert box |

---

## 10. INTERACTION COMPONENTS

### 10.1 Cart Components
| Component | Location | Technology | Features |
|-----------|----------|------------|----------|
| Cart Actions | `includes/cart-actions.html` | HTMX + Vanilla JS | Add to cart, count sync |
| Cart Count Badge | Header, mobile, home | Alpine/Tailwind | Multiple instances |
| Cart Drawer | Not implemented | - | Missing |
| Cart Page | `production/shop/cart.html` | Bootstrap | Quantity update, remove |

### 10.2 Search Components
| Component | Location | Pattern |
|-----------|----------|---------|
| Shop Search | `includes/header.html` | Desktop + mobile forms |
| Product Search | `catalog/product_list.html` | Sidebar input |
| Admin Search | `production/order_list.html` | Input group with button |

### 10.3 Filter Components
| Component | Location | Pattern |
|-----------|----------|---------|
| Category Filter | `catalog/product_list.html` | Select dropdown |
| Price Range | `catalog/product_list.html` | Two number inputs |
| Sort Filter | `catalog/product_list.html` | Select dropdown |
| Color Filter | `catalog/product_list.html` | Select dropdown |
| Status Filter | `production/order_list.html` | Button group |
| Date Filter | `production/reports/shipped.html` | Date picker (jQuery) |

---

## 11. PRINT COMPONENTS

### 11.1 Print Templates
| Template | Purpose | CSS |
|----------|---------|-----|
| `production/print.html` | Order production form (A5 on A4) | Inline print CSS |
| `production/order_print.html` | Single order print | Inline print CSS |
| `production/order_invoice.html` | Invoice/proforma | Inline print CSS |
| `production/order_combined_print.html` | Combined order print | Inline print CSS |
| `production/daily_schedule_print.html` | Daily schedule | Inline print CSS |
| `production/print_label.html` | Label print | Inline print CSS |
| `production/print_label_part.html` | Part label print | Inline print CSS |

### 11.2 Print CSS Pattern
- `@page` rules for paper size
- `transform: rotate(90deg)` for landscape
- Fixed `mm` units
- No page breaks control
- No print-specific media queries beyond `@page`

---

## 12. ICON SYSTEM

### 12.1 Icon Inventory
```
includes/icons.html (30 icons)
├── cart ................. Shopping cart
├── user ................. User profile
├── search ............... Magnifying glass
├── trash ................ Trash can
├── edit ................. Pencil
├── check ................ Checkmark
├── x .................... Close/X
├── filter ............... Funnel
├── heart ................ Heart
├── star ................. Star
├── phone ................ Phone
├── envelope ............. Email
├── map-pin ............... Location
├── truck ................ Truck
├── package .............. Package
├── qr-code .............. QR code
├── shield ............... Shield
├── clock ................ Clock
├── menu ................. Hamburger
├── chevron-down ......... Chevron
├── plus ................. Plus
├── minus ................ Minus
├── arrow-left ........... Arrow
├── arrow-right .......... Arrow
├── image ................ Image
├── logout ............... Logout
├── login ................ Login
├── percent .............. Percent
├── clipboard-list ....... Clipboard
├── factory .............. Factory
└── mail ................. Mail
```

### 12.2 Icon Issues
- **No tree-shaking**: All icons in one file, all rendered as inline SVG
- **No icon font**: Using raw SVGs (good for performance, bad for DX)
- **Bootstrap Icons also loaded**: `bootstrap-icons.css` (2,075 lines) for icons not in custom library

---

## 13. STATE MANAGEMENT

### 13.1 Client-Side State
| State | Framework | Location | Scope |
|-------|-----------|----------|-------|
| Mobile menu | Alpine.js | `header.html` | Global |
| User dropdown | Alpine.js | `header.html` | Global |
| Product gallery | Alpine.js | `product_detail.html` | Page |
| Color selector | Alpine.js | `product_detail.html` | Page |
| Mobile filters | Alpine.js | `product_list.html` | Page |
| View toggle | Alpine.js | `product_list.html` | Page |
| Toast visibility | Alpine.js | `toast.html` | Global |
| Cart count | Vanilla JS | `cart-actions.html` | Global |
| Checkbox selection | Vanilla JS | `order_list.html` | Page |
| Modal state | Bootstrap JS | Painting templates | Page |

### 13.2 Server-Side State
| State | Mechanism | Location |
|-------|-----------|----------|
| CSRF Token | Django cookie | `base.html` |
| Flash messages | Django messages framework | All templates |
| User auth | Django session | All templates |
| Cart | Session/DB | Cart views |

### 13.3 State Issues
- **No centralized state**: Cart count updated in 4 places manually
- **No state persistence**: Filter selections lost on navigation
- **No URL state**: Some filters use query params, others don't

---

## 14. DATA FETCHING PATTERNS

### 14.1 HTMX (Shop Only)
| Action | Endpoint | Target | Location |
|--------|----------|--------|----------|
| Add to cart | `cart:cart_add` | `#cart-count` | `cart-actions.html` |

### 14.2 Vanilla Fetch (Production)
| Action | Endpoint | Location |
|--------|----------|----------|
| Generate tasks | `order_generate_tasks` | `order_list.html` |
| Worker CRUD | Various | `painting_management/workers.html` |
| Process CRUD | Various | `painting_management/processes.html` |

### 14.3 jQuery AJAX (Legacy)
| Action | Endpoint | Location |
|--------|----------|----------|
| Select2 AJAX | Various | `painting_management/workers.html` |
| Date picker | `fdatepicker` | `production/reports/shipped.html` |

### 14.4 Form Submissions
| Pattern | Framework | Usage |
|---------|-----------|-------|
| Standard POST | Django form | All CRUD operations |
| GET filters | Query params | Search, pagination, filters |
| HTMX POST | HTMX | Cart add only |

---

## 15. RESPONSIVE BREAKPOINTS

### 15.1 Breakpoint Mapping
| Breakpoint | Bootstrap | Tailwind | Custom CSS | Effective Width |
|------------|-----------|----------|------------|-----------------|
| xs | <576px | <640px | <480px | 0-480px |
| sm | ≥576px | ≥640px | - | 576-640px |
| md | ≥768px | ≥768px | 768px | 768px |
| lg | ≥992px | ≥1024px | 992px | 992-1024px |
| xl | ≥1200px | ≥1280px | - | 1200-1280px |

### 15.2 Responsive Patterns
| Pattern | Implementation | Usage |
|---------|----------------|-------|
| Mobile menu | Alpine.js `md:hidden` | Shop |
| Mobile menu | Bootstrap collapse | Admin |
| Sidebar filters | `lg:block` / mobile drawer | Shop |
| Grid columns | `grid-cols-1 sm:grid-cols-2` | Shop |
| Grid columns | `col-md-3 col-6` | Admin |
| Stack to row | `flex-col sm:flex-row` | Shop |
| Stack to row | `row` / `col-12 col-md-*` | Admin |

---

## 16. RTL IMPLEMENTATION

### 16.1 RTL Status
| Aspect | Implementation | Issues |
|--------|----------------|--------|
| HTML dir | `dir="rtl"` | ✓ All templates |
| HTML lang | `lang="fa"` | ✓ All templates |
| Bootstrap RTL | `bootstrap.rtl.min.css` | ✓ Production |
| Tailwind RTL | Logical properties (`ms-*`, `me-*`) | ✓ Shop |
| Font | Vazirmatn | ✓ Both systems |
| Text align | `text-right` / `text-start` | Mixed |

### 16.2 RTL Issues
- **Bootstrap RTL loaded in shop** despite using Tailwind
- **Inconsistent logical properties**: Some `margin-left`, some `ms-*`
- **No RTL-specific styles**: Relies entirely on framework RTL support

---

## 17. PRINT STYLES

### 17.1 Print Templates
| Template | Paper Size | Orientation | CSS Location |
|----------|------------|-------------|--------------|
| `print.html` | A5 on A4 | Landscape rotated | Inline |
| `order_print.html` | A4 | Portrait | Inline |
| `order_invoice.html` | A4 | Portrait | Inline |
| `order_combined_print.html` | A4 | Portrait | Inline |
| `daily_schedule_print.html` | A4 | Portrait | Inline |
| `print_label.html` | Label | Portrait | Inline |
| `print_label_part.html` | Label | Portrait | Inline |

### 17.2 Print CSS Issues
- **No shared print stylesheet**: Each template duplicates print CSS
- **Hardcoded dimensions**: `width: 148mm`, `height: 210mm`
- **No print media query**: Uses `@page` only
- **Browser print defaults not reset**: May cause unexpected margins

---

## 18. COMPONENT DEPENDENCY GRAPH

```
base.html (Shop Root)
├── includes/header.html
│   ├── includes/icons.html
│   └── [Alpine.js state]
├── includes/toast.html
│   ├── includes/icons.html
│   └── [Alpine.js transitions]
├── includes/cart-actions.html
│   └── [HTMX]
└── [Tailwind CSS]

production/base.html (Admin Root)
├── [Bootstrap CSS]
├── [Bootstrap JS]
├── [jQuery]
└── [No shared includes with shop]

painting_management/base.html (Painting Root)
├── [Bootstrap CSS]
├── [Bootstrap JS]
├── [jQuery]
├── [Select2]
└── [195 lines inline CSS]
```

---

## 19. COMPONENT REUSABILITY MATRIX

| Component | Reusable? | Used In | Duplicated? |
|-----------|-----------|---------|-------------|
| Icon SVG | ✓ Yes | 30+ templates | No (single source) |
| Toast | Partial | Shop only | Yes (Bootstrap alerts in admin) |
| Navbar | No | 4 different versions | Yes (4x) |
| Footer | No | Shop only | Partial (missing in admin) |
| Card | No | 10+ custom versions | Yes |
| Button | Partial | Both systems | Yes (different classes) |
| Table | No | 5+ versions | Yes |
| Modal | Partial | 8 modals | Yes (markup duplicated) |
| Pagination | No | 2+ versions | Yes |
| Form Input | Partial | Both systems | Yes (different classes) |
| Badge | Partial | Both systems | Yes |
| Breadcrumb | No | 2 templates | Yes (missing in admin) |
| Filter Form | No | 10+ templates | Yes |

---

## 20. MISSING COMPONENTS

| Component | Needed For | Impact |
|-----------|------------|--------|
| Unified Base Template | All pages | **Critical** |
| Shared Navbar | Navigation consistency | **High** |
| Shared Footer | Legal, contact, links | **Medium** |
| Error Page (404/500) | Error handling | **High** |
| Loading Skeleton | Async operations | **Medium** |
| Empty State | List pages | **Medium** |
| Confirm Dialog | Destructive actions | **Medium** |
| File Upload | Product images | **Low** |
| Image Gallery | Product detail | **Medium** |
| Pagination Component | All lists | **Medium** |
| Date Picker | Reports | **Low** (fdatepicker exists) |
| Chart Components | Dashboard, reports | **Low** |

---

*Component Map generated by Kilo Frontend Audit - Phase 0*
