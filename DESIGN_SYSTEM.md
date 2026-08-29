# DESIGN SYSTEM
## سلوی چوب (Selvi Wood) - Frontend Foundation

**Version:** 1.0.0
**Last Updated:** 2026-08-29
**Status:** Phase 1 - Foundation

---

## OVERVIEW

Unified design system for store, production dashboard, admin interfaces, forms, tables, reports, mobile, and print.

### Backward Compatibility

Bootstrap 5.3 classes are mapped to Tailwind equivalents in `static/css/tailwind-input.css`. Existing templates work whether Bootstrap CSS is loaded or not.

---

## COLORS

### Brand
- `primary`: walnut brown scale (50-950)
- `secondary`: warm gold scale (50-950)

### Semantic
- `success`: green scale
- `warning`: amber scale
- `danger`: red scale
- `info`: blue scale

### Neutral
- `stone`: warm gray scale (50-950)

---

## TYPOGRAPHY

- Font: Vazirmatn, Tahoma, system-ui
- Scale: xs (12px) through 6xl (60px)
- Line heights: 1.2–1.75 optimized for Persian

---

## SPACING

- Base: 0–24 (4px–96px)
- Extended: 18, 22, 30, 34, 38, 42, 46, 50
- Section: `.section-padding` / `.section-container`

---

## BORDER RADIUS

xs(2px) → sm(4px) → default(8px) → md(10px) → lg(14px) → xl(18px) → 2xl(24px) → full(9999px)

---

## SHADOWS / ELEVATION

- `elevation-1` through `elevation-5`
- Bootstrap compatibility: `.shadow-sm`, `.shadow`, `.shadow-lg`

---

## FOCUS STATES

Global: `*:focus-visible { outline-none ring-2 ring-offset-2 ring-primary-500 }`

---

## DISABLED STATES

Buttons/inputs/links: `disabled:opacity-50 disabled:cursor-not-allowed`

---

## HOVER STATES

Standard hover variants for buttons, cards, rows, nav links, chips.

---

## RESPONSIVE BREAKPOINTS

xs <640px | sm ≥640px | md ≥768px | lg ≥1024px | xl ≥1280px | 2xl ≥1536px

---

## RTL BEHAVIOR

- All templates: `dir="rtl" lang="fa"`
- Logical properties: `ms-*`, `me-*`, `ps-*`, `pe-*`, `border-s`, `border-e`
- RTL utilities defined in `tailwind-input.css`

---

## BUTTONS

Base: `.btn` + variants `.btn-primary`, `.btn-secondary`, `.btn-success`, `.btn-danger`, `.btn-warning`, `.btn-info`, `.btn-dark`, `.btn-light`, `.btn-ghost`, `.btn-link`

Outline variants: `.btn-outline-*` for all semantic colors

Sizes: `.btn-sm`, `.btn`, `.btn-lg`

States: `.btn.is-loading`, `disabled`, `:active`

---

## FORMS

- `.form-input` / `.form-control` (Bootstrap compat)
- `.form-label`
- `.form-error`, `.form-hint`
- `.form-select`
- Sizes: `.form-control-sm`, `.form-control-lg`
- `.input-group`, `.input-group-text`

---

## CARDS

- `.card`, `.card-hover`, `.card-elevated`
- Sub-components: `.card-header`, `.card-body`, `.card-footer`, `.card-title`, `.card-text`, `.card-img-top`

---

## BADGES

- `.badge`, `.badge-success`, `.badge-warning`, `.badge-danger`, `.badge-info`, `.badge-neutral`
- Bootstrap compat: `.badge-secondary` → `.badge-neutral`, `.badge-light` → `.bg-light`, etc.

---

## ALERTS

- `.alert`, `.alert-success`, `.alert-warning`, `.alert-danger`, `.alert-info`, `.alert-light`, `.alert-dark`
- `.alert-dismissible`, `.alert-heading`

---

## TABLES

- `.table`, `.table-modern`, `.table-hover`, `.table-bordered`, `.table-striped`, `.table-sm`
- `.thead-light`, `.thead-dark`
- Row colors: `.table-success`, `.table-warning`, `.table-danger`, `.table-info`, `.table-active`
- `.table-responsive`

---

## NAVIGATION

Bootstrap-compatible navbar classes supported.

---

## MODALS

Bootstrap modal structure supported via Bootstrap JS or Alpine.js.

---

## INPUT GROUPS

- `.input-group`, `.input-group-text`
- `.input-group-sm`, `.input-group-lg`

---

## PAGINATION

Bootstrap pagination classes supported.

---

## LOADING STATES

- `.spinner`, `.spinner-lg`, `.spinner-sm`
- `.btn.is-loading`
- `.skeleton`, `.skeleton-text`, `.skeleton-title`, `.skeleton-image`, `.skeleton-avatar`

---

## EMPTY STATES

- `.empty-state`, `.empty-state-icon`, `.empty-state-title`, `.empty-state-description`

---

## CHIPS / FILTERS

- `.chip`, `.chip-active`, `.chip-inactive`

---

## PRINT STYLES

- `.print-only`, `.no-print`

---

*Design System v1.0.0 - سلوی چوب*
