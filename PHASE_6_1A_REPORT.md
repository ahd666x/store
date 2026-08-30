# PHASE 6.1A — MODAL COMPONENT MIGRATION REPORT

**Project:** store (دکارو / سلوی چوب)
**Scope:** Shared modal components only
**Date:** 2026-08-30

---

## 1. Files Changed

| File | Change |
|------|--------|
| `templates/components/modals/modal.html` | Rewritten: Bootstrap markup → Alpine.js + Tailwind |
| `templates/components/modals/confirm_modal.html` | Rewritten: `{% extends %}` the new `modal.html`, overrides body/footer blocks |
| `static/js/alpine-bootstrap.js` | Enhanced the existing `modal` Alpine component (`id`, `titleId`, focus-on-open) |
| `static/css/components.css` | Added 1-line `[x-cloak]{display:none!important}` rule (Alpine pre-init hide) |

No Python, models, views, URLs, APIs, business logic, DB, or unrelated templates were modified.

---

## 2. Old Bootstrap Behavior

`modal.html` (before) mixed Bootstrap classes with a half-working Alpine shell:

- `class="modal fade"`, `modal-dialog`, `modal-content`, `modal-header`, `modal-body`, `modal-footer`, `modal-title`
- `btn-close`, `btn btn-secondary`, `btn btn-primary`
- `x-data="{ open: false }" x-show="open" @keydown.escape.window="open = false"`
- Body injected via `{{ block.super }}` — **invalid inside an `{% include %}`**, so body content never rendered.
- `confirm_modal.html` did a **broken double `{% include %}`** (open tag with params, then a second `{% include %}` to "close" tags) and passed `submit_class` which `modal.html` never used.

Net: the old components were **non-functional** — there were no consumers anywhere in the repository, so no page depended on them.

---

## 3. New Implementation

### `modal.html` (Alpine + Tailwind, Bootstrap-free)

- Root: `x-data="modal"`, `x-init="id = '{{ modal_id }}'; titleId = '{{ modal_id }}Title'"`, `x-show="open"`, `x-cloak`.
- Listening model (replaces Bootstrap's global `data-bs-target`):
  - `@keydown.escape.window="hide()"` — ESC closes
  - `@modal:open.window="if ($event.detail === id) show()"` — open by id
  - `@modal:close.window="if ($event.detail === id) hide()"` — close by id
- Backdrop: `fixed inset-0 bg-black/50` with `@click="hide()"`.
- Dialog panel: `role="dialog" aria-modal="true" :aria-labelledby="titleId" tabindex="-1"` + `shadow-elevation-3`, `rounded-2xl`, size mapping (`sm`→`max-w-sm`, `lg`→`max-w-2xl`, `xl`→`max-w-4xl`, default→`max-w-lg`), `max-h-[90vh] overflow-y-auto`.
- Header: title (`id="{{ modal_id }}Title"`) + SVG close button (`@click="hide()"`, `focus-visible:ring-2`).
- Body: `{% block modal_body %}` (default renders `{{ body|default:''|safe }}`); override when extending.
- Footer: cancel button (`@click="hide()"`) + submit button (`type="submit"`); rendered only when `submit_text`/`cancel_text` provided.
- Optional `<form>` wrapper when `form_id` is set: includes `{% csrf_token %}` and `<input type="hidden" name="next" value="{{ form_action }}">`, preserving the original form/POST contract.
- `x-transition` enter/leave animations on backdrop and dialog.

### `confirm_modal.html`

- `{% extends 'components/modals/modal.html' %}` and overrides `modal_body` (renders `{{ message }}`) and `modal_footer` (cancel button + `<a href="{{ confirm_action }}">` confirm link, red Tailwind styling).
- The previous broken double-include is gone; it now reuses the single modal structure.

### Trigger contract (documented for future consumers)

Replace Bootstrap triggers:
```django
<!-- before -->
<button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#workerModal">...</button>
<!-- after -->
<button class="btn btn-primary" @click="$dispatch('modal:open', 'workerModal')">...</button>
```

---

## 4. Consumers of the Component

**None.** A full-repository search (`{% include 'components/modals/modal.html' %}`, `confirm_modal`, `modal_id=`) found references only inside the two component files themselves. No page, view, or JS file consumes the shared modal component. The migration is therefore pure refactor with zero downstream impact.

---

## 5. Compatibility Issues

| Item | Status |
|------|--------|
| Parameter names (`modal_id`, `title`, `size`, `form_id`, `form_action`, `csrf_token`, `submit_text`, `cancel_text`) | **Preserved** |
| `form_id` / `form_action` / CSRF / hidden `next` | **Preserved** |
| `modal_id` DOM id and `{{ modal_id }}Title` title id (used by `aria-labelledby`) | **Preserved** |
| `submit_class` | **Preserved** (still appended to submit button) |
| `confirm_class` default | **Changed** `btn-danger` → empty; the confirm link now uses Tailwind red classes (`bg-red-600 hover:bg-red-700`). Variable name kept. Safe because no consumer exists. |
| Body content injection | Old `{{ block.super }}` (invalid under `{% include %}`) replaced with a `body` variable **and** overridable `modal_body`/`modal_header`/`modal_footer` blocks (correct Django `extends` pattern). |
| Trigger mechanism | Bootstrap `data-bs-toggle`/`data-bs-target` → Alpine `$dispatch('modal:open', id)`. No existing consumer affected. |

**Prerequisite (not breaking, documented):** consuming templates/layouts must load the compiled Tailwind stylesheet (`static/css/style.css`). The dashboard/production layout currently loads Bootstrap only, so the component will not be styled there until Phase 6 adds Tailwind to that layout. Because no page consumes the component yet, this has no current effect.

---

## 6. Remaining Bootstrap Modal Usages (out of scope — NOT migrated this task)

These use **inline** Bootstrap modals on individual pages and their `bootstrap.Modal` JS, not the shared component. Left intact per task constraints:

**Templates (`data-bs-toggle="modal"` / `data-bs-dismiss="modal"`):**
- `templates/production/painting_management/workers.html`
- `templates/production/painting_management/stages.html`
- `templates/production/painting_management/processes.html`
- `templates/production/painting_management/holidays.html`
- `templates/production/painting_management/assignment_rules.html`
- `templates/production/product_create.html`

**JavaScript (`new bootstrap.Modal(...)`):**
- `static/js/production/painting/workers.js`
- `static/js/production/painting/stages.js`
- `static/js/production/painting/processes.js`
- `static/js/production/painting/assignment_rules.js`
- `static/js/production/bom.js`

These require per-page migration (Phase 6.x) and are explicitly excluded from this task.

---

## 7. Tests Performed

1. `python manage.py check` — **passed** (System check identified no issues).
2. Rendered `modal.html` with a full context (`modal_id`, `title`, `size='lg'`, `form_id`, `form_action`, `submit_text`, `cancel_text`):
   - emitted `x-data="modal"`, `role="dialog"`, `aria-modal="true"`, `:aria-labelledby="titleId"`
   - **no** `modal fade` / `btn-close` / `modal-content` Bootstrap classes present
   - form `action` and hidden `next` input present
3. Rendered `confirm_modal.html` (`{% extends %}` modal):
   - `{{ message }}` rendered, confirm `<a href="{{ confirm_action }}">` present
   - **no** Bootstrap classes present; correct `role="dialog"` structure inherited
4. Confirmed shared components contain **zero** `modal fade`, `btn-close`, `data-bs-*`, `modal-content`, `modal-dialog` tokens (grep).
5. Confirmed no consumers exist (no `{% include %}`/usage of the shared modals anywhere).

---

## 8. Django Check Result

```
System check identified no issues (0 silenced).
```

---

## Conclusion

SHARED MODAL MIGRATION COMPLETE: YES
