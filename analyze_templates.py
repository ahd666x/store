import os, re, json

ROOT = r"C:\Users\Hossein Nezhad\Desktop\store\store\templates"
TEMPLATES_ROOT = ROOT

BS_PREFIXES = [
    'container','row','col','btn','card','form','input-group','list-group','modal','dropdown',
    'nav','navbar','page','pagination','breadcrumb','table','alert','badge','spinner','toast',
    'tooltip','popover','carousel','collapse','offcanvas','accordion','progress','placeholder',
    'd-','flex','justify','align','order','gap','grid','m-','mx','my','mt','mb','ms','me',
    'p-','px','py','pt','pb','ps','pe','text-','bg-','border','rounded','shadow','position',
    'fixed','sticky','float','fs-','fw-','lh-','w-','h-','vw','vh','link-','visible','invisible',
    'overflow','stack','vstack','hstack','ratio','figure','img-','g-','gx','gy','offset','row-cols',
    'was-validated','table-responsive','table-striped','table-bordered','table-hover','table-sm',
    'table-dark','table-group','dropend','dropstart','dropup','btn-close','visually-hidden',
]
BS_EXACT = {
    'container','container-fluid','row','show','fade','active','disabled','collapse','collapsing',
    'card-header','card-body','card-footer','card-title','card-text','card-img','card-link','card-subtitle',
    'modal-header','modal-body','modal-footer','modal-title','modal-content','modal-dialog','modal-static',
    'dropdown-menu','dropdown-item','dropdown-toggle','dropdown-divider','dropend','dropstart','dropup',
    'nav-link','nav-item','navbar-brand','navbar-nav','navbar-toggler','navbar-collapse','navbar-text',
    'list-group-item','breadcrumb-item','alert-heading','alert-link','spinner-border','spinner-grow',
    'form-switch','form-text','form-floating','form-range','form-label','form-control','form-select',
    'form-check','form-check-input','form-check-label','input-group-text','visually-hidden','img-fluid',
    'img-thumbnail','clearfix','mx-auto','d-none','d-inline','d-block','d-grid','d-table','d-flex',
    'd-inline-flex','text-white','text-dark','bg-light','bg-dark','bg-body','bg-transparent','text-muted',
    'text-center','text-start','text-end','text-uppercase','text-lowercase','text-wrap','text-break',
    'justify-content-start','justify-content-end','justify-content-center','justify-content-between',
    'justify-content-around','justify-content-evenly','align-items-start','align-items-end',
    'align-items-center','align-items-baseline','align-items-stretch','flex-fill','flex-grow','flex-shrink',
    'flex-wrap','flex-nowrap','flex-column','flex-row','flex-column-reverse','flex-row-reverse',
    'rounded','rounded-0','rounded-1','rounded-2','rounded-3','rounded-circle','rounded-pill',
    'shadow','shadow-sm','shadow-lg','shadow-none','position-static','position-relative',
    'position-absolute','position-fixed','position-sticky','float-start','float-end','float-none',
    'spinner-border-sm','spinner-grow-sm','placeholder-glow','placeholder-wave','btn-close-white',
    'was-validated','valid-feedback','invalid-feedback','form-control-sm','form-control-lg',
    'form-select-sm','form-select-lg','input-group-sm','input-group-lg','accordion-button',
    'accordion-collapse','accordion-body','accordion-header','accordion-flush','nav-pills','nav-tabs',
    'nav-justified','navbar-expand','breadcrumb','pagination','page-link','page-item','table-responsive',
    'captcha','g-recaptcha','row','col','row-cols','card','form','modal','dropdown','nav','navbar',
    'list-group','alert','badge','spinner','toast','tooltip','popover','carousel','collapse','offcanvas',
    'accordion','progress','placeholder','gap','grid','m','mx','my','mt','mb','ms','me','p','px','py',
    'pt','pb','ps','pe','text','bg','border','rounded','shadow','position','fixed','sticky','float',
    'fs','fw','lh','w','h','vw','vh','link','visible','invisible','overflow','stack','vstack','hstack',
    'ratio','figure','img','g','gx','gy','offset','d','flex','justify','align','order','btn',
    'container','table-striped','table-bordered','table-hover','table-sm','table-dark','table-group-divider',
    'col-form-label','col-auto','row-gap','column-gap','display-1','display-2','display-3','display-4',
    'display-5','display-6','lead','small','mark','blockquote','hr','list-unstyled','list-inline',
    'btn-toolbar','btn-group','btn-group-vertical','btn-outline-primary','btn-outline-secondary',
    'btn-outline-success','btn-outline-danger','btn-outline-warning','btn-outline-info','btn-outline-light',
    'btn-outline-dark','btn-primary','btn-secondary','btn-success','btn-danger','btn-warning','btn-info',
    'btn-light','btn-dark','btn-link','bg-primary','bg-secondary','bg-success','bg-danger','bg-warning',
    'bg-info','bg-white','text-primary','text-secondary','text-success','text-danger','text-warning',
    'text-info','text-body','border-primary','border-secondary','border-success','border-danger',
    'border-warning','border-info','border-light','border-dark','border-white','border-0','border-top',
    'border-end','border-bottom','border-start','justify-content','align-items','align-self','align-content',
    'order-first','order-last','bg-gradient','text-decoration-none','text-decoration-underline',
    'text-decoration-line-through','fst-italic','fst-normal','fw-bold','fw-bolder','fw-semibold','fw-medium',
    'fw-normal','fw-light','fw-lighter','text-truncate','text-nowrap','visible','invisible','w-25','w-50',
    'w-75','w-100','w-auto','h-25','h-50','h-75','h-100','h-auto','mw-100','mh-100','vw-100','vh-100',
    'min-vw-100','min-vh-100','gap-0','gap-1','gap-2','gap-3','gap-4','gap-5','top-0','top-50','top-100',
    'bottom-0','start-0','end-0','translate-middle','modal-backdrop','fade','show','active','disabled',
    'collapsed','aria-expanded','dropdown-toggle-split','nav-underline','link-primary','link-secondary',
    'link-success','link-danger','link-warning','link-info','link-light','link-dark','link-body-emphasis',
    'text-reset','text-opacity','bg-opacity','border-opacity','rounded-top','rounded-bottom','rounded-start',
    'rounded-end','rounded-0','shadow-sm','shadow','shadow-lg','shadow-none','position-absolute','z-index',
    'pe-none','pe-auto','user-select-all','user-select-auto','user-select-none','pointer-events-none',
    'pointer-events-auto','overflow-auto','overflow-hidden','overflow-visible','overflow-scroll',
    'd-inline-block','d-inline','d-block','d-grid','d-flex','d-inline-flex','d-none','d-table','d-table-row',
    'd-table-cell','visible','invisible','sr-only','visually-hidden-focusable','stretched-link','gap',
}

TW_PREFIXES = [
    'grid-cols','space-x','space-y','items-','justify-','self-','place-','object-','cursor-','select-',
    'opacity-','z-','inset-','top-','right-','bottom-','left-','scale-','rotate-','translate-','skew-',
    'ring-','blur-','tracking-','leading-','antialiased','font-','text-','bg-','p-','px-','py-','pt-',
    'pb-','pl-','pr-','m-','mx-','my-','mt-','mb-','ml-','mr-','w-','h-','max-w-','min-w-','max-h-',
    'min-h-','flex-','gap-','rounded','shadow','border','transition','transform','hover:','focus:',
    'active:','disabled:','md:','lg:','xl:','sm:','2xl:','group-hover','peer-','dark:','first:','last:',
    'odd:','even:','checked:','before:','after:','container','grid','flex','block','inline','hidden',
    'absolute','relative','fixed','sticky','table','flow-root','contents','list-item','overflow','truncate',
]

def classify_token(tok):
    if ':' in tok:
        return 'tw'
    # exact checks
    if tok in BS_EXACT:
        return 'bs'
    for p in BS_PREFIXES:
        if tok == p or tok.startswith(p):
            return 'bs'
    for p in TW_PREFIXES:
        if tok == p or tok.startswith(p):
            return 'tw'
    return None

def main():
    results = []
    for dirpath, dirnames, filenames in os.walk(TEMPLATES_ROOT):
        for fn in filenames:
            if not fn.endswith('.html') and not fn.endswith('.xml'):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, TEMPLATES_ROOT).replace(os.sep, '/')
            with open(full, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            lines = content.splitlines()
            line_count = len(lines)

            bs_classes = set()
            tw_classes = set()
            bs_data = set()
            inline_style = False
            inline_script = False

            # inline style/script blocks
            if re.search(r'<%s\s+[^>]*\bstyle\b', content) or re.search(r'<style', content, re.I):
                # <style ...> or <... style="..."> -- we count actual <style> blocks as inline_style
                pass
            style_blocks = re.findall(r'<style\b', content, re.I)
            script_blocks = re.findall(r'<script\b', content, re.I)
            # inline style attribute
            has_style_attr = bool(re.search(r'\bstyle\s*=\s*["\']', content))
            inline_style = (len(style_blocks) > 0) or has_style_attr
            inline_script = len(script_blocks) > 0

            # class attributes
            for m in re.finditer(r'\bclass\s*=\s*["\'](.*?)["\']', content, re.S):
                val = m.group(1)
                for tok in re.split(r'[\s"\'>+~]+', val):
                    tok = tok.strip()
                    if not tok:
                        continue
                    # ignore django var tokens
                    if '{' in tok or '}' in tok:
                        continue
                    cat = classify_token(tok)
                    if cat == 'bs':
                        bs_classes.add(tok)
                    elif cat == 'tw':
                        tw_classes.add(tok)

            # data-bs-* attributes
            for m in re.finditer(r'\b(data-bs-[a-zA-Z0-9\-]+)', content):
                bs_data.add(m.group(1).lower())

            # extends
            ext = None
            m = re.search(r'{%\s*extends\s+["\']([^"\']+)["\']', content)
            if m:
                ext = m.group(1)

            # includes
            includes = []
            for m in re.finditer(r'{%\s*include\s+["\']([^"\']+)["\']', content):
                includes.append(m.group(1))

            # alpine
            alpine = bool(re.search(r'\bx-data\b|\bx-show\b|\bx-transition\b|\bx-click\b|\bx-model\b|\bx-for\b|\bx-if\b|\bx-bind\b|\bx-on\b|@click\b|@submit\b|x-init\b|x-text\b|x-html\b|x-ref\b', content))
            # htmx
            htmx = bool(re.search(r'\bhx-get\b|\bhx-post\b|\bhx-put\b|\bhx-delete\b|\bhx-target\b|\bhx-swap\b|\bhx-trigger\b|\bhx-vals\b|\bhx-indicator\b', content))
            # jquery
            jquery = bool(re.search(r'\bjQuery\b|\$\.\s*(ajax|get|post|getJSON|getScript)|\$\s*\(|\$\.|jquery', content, re.I))
            # select2
            select2 = bool(re.search(r'select2', content, re.I))

            # assets
            custom_css = []
            custom_js = []
            vendor_js = []
            vendor_css = []
            for m in re.finditer(r'<link\b[^>]*\bhref\s*=\s*["\']([^"\']+)["\'][^>]*>', content, re.I):
                href = m.group(1)
                if re.search(r'\.css', href, re.I):
                    if re.search(r'vendor|cdn|jsdelivr|unpkg|cloudflare|bootstrap|font-?awesome|fontawesome|bootstrap-icons|googleapis|gstatic', href, re.I) or href.startswith('http'):
                        vendor_css.append(href)
                    else:
                        custom_css.append(href)
            for m in re.finditer(r'<script\b[^>]*\bsrc\s*=\s*["\']([^"\']+)["\'][^>]*>', content, re.I):
                src = m.group(1)
                if re.search(r'vendor|cdn|jsdelivr|unpkg|cloudflare|bootstrap|jquery|popper|select2|alpine|htmx|chart|font-?awesome|fontawesome|bootstrap-icons', src, re.I) or src.startswith('http'):
                    vendor_js.append(src)
                else:
                    custom_js.append(src)

            # status guess
            uses_components = rel.startswith('components/') or rel.startswith('layouts/') or any(i.strip().startswith('components/') for i in includes)
            if rel.startswith('components/') or rel.startswith('layouts/'):
                status = 'GREEN'
            elif uses_components:
                status = 'GREEN'
            elif bs_classes or tw_classes or (alpine or htmx or jquery or select2):
                status = 'YELLOW'
            else:
                status = 'RED'

            results.append({
                'path': rel,
                'line_count': line_count,
                'extends': ext,
                'includes': includes,
                'inline_style': inline_style,
                'inline_script': inline_script,
                'bootstrap_classes': sorted(bs_classes),
                'bootstrap_data_attributes': sorted(bs_data),
                'tailwind_classes': sorted(tw_classes),
                'alpine_usage': alpine,
                'htmx_usage': htmx,
                'jquery_usage': jquery,
                'select2_usage': select2,
                'custom_css_files': custom_css,
                'custom_js_files': custom_js,
                'vendor_js_files': vendor_js,
                'status_guess': status,
            })

    results.sort(key=lambda r: r['path'])
    byp = {r['path']: r for r in results}

    # Transitive include closure: a template "uses" the design system if it (or any
    # template it includes, transitively) lives under components/ or layouts/.
    seed = set()
    for r in results:
        p = r['path']
        if p.startswith('components/') or p.startswith('layouts/'):
            seed.add(p)
    green = set(seed)
    changed = True
    while changed:
        changed = False
        for r in results:
            p = r['path']
            if p in green:
                continue
            for inc in r['includes']:
                inc = inc.strip()
                if inc in green:
                    green.add(p)
                    changed = True
                    break

    for r in results:
        p = r['path']
        if p in green:
            r['status_guess'] = 'GREEN'
        elif r['bootstrap_classes'] or r['tailwind_classes'] or (r['alpine_usage'] or r['htmx_usage'] or r['jquery_usage'] or r['select2_usage']):
            r['status_guess'] = 'YELLOW'
        else:
            r['status_guess'] = 'RED'

    out = os.path.join(r"C:\Users\Hossein Nezhad\Desktop\store\store", 'templates_analysis.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("WROTE", out, "templates:", len(results), "GREEN:", len(green))

if __name__ == '__main__':
    main()
