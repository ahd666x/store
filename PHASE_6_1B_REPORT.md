# PHASE 6.1B — BADGE COMPONENT MIGRATION REPORT

**Project:** store (دکارو / سلوی چوب)
**Scope:** Shared Badge component only
**Date:** 2026-08-30

---

## 1. Files Changed

| File | Change |
|------|--------|
| `templates/components/data/badge.html` | Rewritten: Bootstrap `badge bg-*` classes → Tailwind design-token utility classes |

No Python, models, views, URLs, APIs, business logic, DB, unrelated templates, or unrelated JS/CSS were modified. `static/css/style.css` was rebuilt via `npm run build:css` but produced byte-identical output (all referenced token utilities already existed), so it is **not** part of the diff.

---

## 2. Original Badge Implementation

`templates/components/data/badge.html` (16 lines) used Bootstrap class names:

```html
{% comment %} Variables: text, variant (default/primary/success/warning/danger/info), size (sm/lg) {% endcomment %}

<span class="badge 
    {% if variant == 'primary' %}bg-primary
    {% elif variant == 'success' %}bg-success
    {% elif variant == 'warning' %}bg-warning text-dark
    {% elif variant == 'danger' %}bg-danger
    {% elif variant == 'info' %}bg-info
    {% else %}bg-secondary
    {% endif %}
    {% if size == 'sm' %}badge-sm{% elif size == 'lg' %}badge-lg{% endif %}
">
    {{ text }}
</span>
```

Bootstrap dependency points:
- `badge` (Bootstrap component class)
- `bg-primary`, `bg-success`, `bg-warning`, `bg-danger`, `bg-info`, `bg-secondary` (Bootstrap background utilities)
- `text-dark` (Bootstrap text utility)
- `badge-sm` / `badge-lg` were referenced but **never defined** (no effect).

> Note: the project's design system (`static/css/tailwind-input.css`) redefines some `bg-*` names as Tailwind compatibility shims (e.g. `.bg-success { @apply bg-success-100 text-success-800; }`), so the rendered output was technically styled, but the markup still carried Bootstrap class **names**. Per the audit (`PHASE_5_6_VALIDATION_REPORT.md` flagged `templates/components/data/badge.html` with `bootstrap_classes: ["badge"]`), these Bootstrap-named classes must be removed from the component.

---

## 3. New Implementation

`templates/components/data/badge.html` now emits pure Tailwind utility classes built from the project's own design tokens (`tailwind.config.js` color scales: `primary`, `success`, `warning`, `danger`, `info`, `stone`):

```html
{% comment %} Variables: text, variant (default/primary/success/warning/danger/info), size (sm/lg), class {% endcomment %}

{% with primary_color='bg-primary-100 text-primary-800' success_color='bg-success-100 text-success-800' warning_color='bg-warning-100 text-warning-800' danger_color='bg-danger-100 text-danger-800' info_color='bg-info-100 text-info-800' neutral_color='bg-stone-100 text-stone-800' sm_size='px-2 py-0' lg_size='text-sm px-3 py-1' md_size='px-2.5 py-0.5' %}
<span class="inline-flex items-center rounded-full text-xs font-medium
    {% if variant == 'primary' %}{{ primary_color }}
    {% elif variant == 'success' %}{{ success_color }}
    {% elif variant == 'warning' %}{{ warning_color }}
    {% elif variant == 'danger' %}{{ danger_color }}
    {% elif variant == 'info' %}{{ info_color }}
    {% else %}{{ neutral_color }}
    {% endif %}
    {% if size == 'sm' %}{{ sm_size }}{% elif size == 'lg' %}{{ lg_size }}{% else %}{{ md_size }}{% endif %}
    {{ class|default:'' }}
">
    {{ text }}
</span>
{% endwith %}
```

Key points:
- **No Bootstrap class names** (`badge`, `bg-primary`, `bg-success`, `text-dark`, `bg-secondary`, `btn-*`) appear in the markup.
- **Explicit mapping** (no dynamic `bg-{{ variant }}` construction) — satisfies the class-safety requirement and guarantees Tailwind compilation.
- Uses existing project design tokens (the `*-100`/`*-800` shade pairs mirror exactly what the design system's `.badge-success` etc. component classes used: e.g. `.badge-success { @apply bg-success-100 text-success-800; }`).
- `size`: `sm` → tighter pill (`px-2 py-0`), `lg` → larger (`text-sm px-3 py-1`), default → `px-2.5 py-0.5`. The old `badge-sm`/`badge-lg` classes were undefined, so this is a strict improvement with no behavioral regression.
- Added an **optional `class` passthrough** (`{{ class|default:'' }}`) for composability; additive, backward compatible.

---

## 4. API Preserved

| Parameter | Status |
|-----------|--------|
| `text` | ✅ Preserved (rendered via `{{ text }}`, auto-escaped as before) |
| `variant` | ✅ Preserved — supported values: `primary`, `success`, `warning`, `danger`, `info`, and any other value (including omitted) → neutral |
| `size` | ✅ Preserved — `sm`, `lg`, default |
| `class` | ➕ Added (optional) — extra classes appended to the badge; safe for existing callers |

`{% include 'components/data/badge.html' with text=... variant=... size=... %}` continues to work unchanged.

---

## 5. Consumers Found

**None (live).** A repository-wide search confirmed:

- No template performs `{% include 'components/data/badge.html' %}` / `{% include 'components/data/badge' %}`.
- `templates_analysis.json` lists `components/data/badge.html` with `"includes": []`.
- The only references to `components/data/badge` are in **documentation** (`COMPONENT_LIBRARY.md`, `COMPONENT_MIGRATION_MATRIX.md`, `FRONTEND_REFACTOR_ROADMAP.md`, `PHASE_5_6_VALIDATION_REPORT.md`) and the analysis JSON artifacts — not in executable templates.

Therefore the migration is a pure refactor with zero downstream impact.

> Out of scope (NOT migrated this phase):
> - `templates/components/data/status_badge.html` — a **separate** component. It uses `.badge`/`.badge-success` etc., which are the project's own Tailwind component classes (defined in `tailwind-input.css`, not the Bootstrap library), so it is already Bootstrap-library-free. Left untouched per task scope.
> - All inline `<span class="badge bg-...">` usages across production/orders/etc. templates — these are inline Bootstrap badges, explicitly excluded.

---

## 6. Variants Found

The component's own API supports these variants (from its comment + `if/elif` logic):

| Variant | Mapped Tailwind tokens | Visual |
|---------|------------------------|--------|
| `primary` | `bg-primary-100 text-primary-800` | primary brand tint |
| `success` | `bg-success-100 text-success-800` | green tint |
| `warning` | `bg-warning-100 text-warning-800` | amber tint |
| `danger` | `bg-danger-100 text-danger-800` | red tint |
| `info` | `bg-info-100 text-info-800` | blue tint |
| default / unknown | `bg-stone-100 text-stone-800` | neutral stone |

No additional variants were invented. The mapping reuses the exact shade pairs already established by the design system's `.badge-*` component classes, preserving visual parity.

---

## 7. Bootstrap Dependencies Removed

| Removed | Replaced with |
|---------|---------------|
| `badge` (Bootstrap component class) | `inline-flex items-center rounded-full text-xs font-medium` (standard Tailwind utilities) |
| `bg-primary` | `bg-primary-100 text-primary-800` |
| `bg-success` / `bg-warning text-dark` / `bg-danger` / `bg-info` | `bg-{color}-100 text-{color}-800` |
| `bg-secondary` (default) | `bg-stone-100 text-stone-800` |
| `badge-sm` / `badge-lg` (undefined) | `px-2 py-0` / `text-sm px-3 py-1` |
| Bootstrap JS | none (static markup) |
| jQuery | none |

---

## 8. Tests Performed

1. **Render test** — rendered the component via Django's template engine for every variant (`primary`, `success`, `warning`, `danger`, `info`, unknown) and `size` (`sm`, `lg`, default), plus `class` passthrough. All produced valid `<span>` markup with the correct token utility classes (verified class strings, e.g. `success -> ... bg-success-100 text-success-800 ... px-2.5 py-0.5`).
2. **Bootstrap leak test** — asserted the rendered output contains none of: `>badge<`, `badge `, `bg-primary `, `bg-success `, `text-dark`, `bg-secondary`, `btn-`, `class="badge`. Result: **no leaks**.
3. **CSS compilation** — ran `npm run build:css`; all referenced token utilities (`bg-primary-100`, `text-primary-800`, `bg-stone-100`, `py-0`, `text-sm`, `bg-success-100`, …) are present in `static/css/style.css`. Rebuild output was byte-identical to the committed `style.css` (tokens already compiled), so no spurious CSS diff.
4. **Grep** — confirmed `badge.html` contains no `badge`, `bg-primary`, `bg-success`, `bg-secondary`, `text-dark`, or `btn-` class tokens.
5. `python manage.py check` — **passed** (System check identified no issues).

---

## 9. Django Check Result

```
System check identified no issues (0 silenced).
```

---

## 10. Remaining Badge-Related Technical Debt

1. **Inline Bootstrap badges across the app** — many templates still use `<span class="badge bg-success">`, `<span class="badge bg-warning text-dark">`, `badge-danger`, `badge-info`, `badge-neutral`, etc. (e.g. `production/kanban.html`, `worker_list.html`, `discounts/discount_list.html`, `production/assign_painting.html`, `production/order_item.html`, `page_dump.html`, `home.html`, `catalog/includes/product_card.html`, `accounts/profile.html`'s status include, and the `bg-{% if ... %}success{% else %}danger{% endif %}` dynamic pattern in `painting_management/processes.html` / `_worker_rows.html`). These should be migrated in later phases (6.x) by either adopting this shared `badge.html` component or converting to token utilities. **Out of scope for 6.1B.**
2. **`status_badge.html`** uses `.badge`/`.badge-success` Bootstrap-named project component classes (Tailwind-based, library-free, but still Bootstrap-named). Candidate for a later standardization pass to use `badge.html` with a `status`→`variant` mapping.
3. **`COMPONENT_LIBRARY.md` / `COMPONENT_MIGRATION_MATRIX.md`** still describe the old `badge bg-*` API; they can be updated to document the token-based API in a follow-up doc task.
4. **Dynamic `bg-{{ color }}` construction** in `processes.html` (`bg-{% if process.is_active %}success{% else %}danger{% endif %}`) will not survive a strict Tailwind JIT scan and must be converted to explicit mapping when those pages are migrated.

---

## Conclusion

BADGE MIGRATION COMPLETE: YES
