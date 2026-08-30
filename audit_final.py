#!/usr/bin/env python3
"""Comprehensive final audit."""
import re
import json
from pathlib import Path
from collections import defaultdict

TEMPLATES_DIR = Path("templates")
STATIC_DIR = Path("static")

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def get_extends(content):
    match = re.search(r'\{%\s*extends\s+[\'"]([^\'"]+)[\'"]\s*%\}', content)
    return match.group(1) if match else None

def get_includes(content):
    return re.findall(r'\{%\s*include\s+[\'"]([^\'"]+)[\'"]\s*%\}', content)

def count_pattern(content, pattern):
    return len(re.findall(pattern, content))

LAYOUT_BOOTSTRAP = {'layouts/dashboard.html'}
LAYOUT_STORE = {'layouts/store.html', 'base.html'}

inheritance_cache = {}

def resolve_template_path(extends_path, current_template_dir):
    p = TEMPLATES_DIR / extends_path
    if p.exists():
        return extends_path
    p = TEMPLATES_DIR / f"{extends_path}.html"
    if p.exists():
        return f"{extends_path}.html"
    if current_template_dir:
        p = TEMPLATES_DIR / Path(current_template_dir) / extends_path
        if p.exists():
            return str(Path(current_template_dir) / extends_path)
        p = TEMPLATES_DIR / Path(current_template_dir) / f"{extends_path}.html"
        if p.exists():
            return str(Path(current_template_dir) / f"{extends_path}.html")
    extends_filename = Path(extends_path).name
    candidates = list(TEMPLATES_DIR.rglob(extends_filename))
    if len(candidates) == 1:
        return str(candidates[0].relative_to(TEMPLATES_DIR))
    elif len(candidates) > 1:
        for c in candidates:
            rel = str(c.relative_to(TEMPLATES_DIR))
            if current_template_dir and rel.startswith(current_template_dir):
                return rel
        return str(candidates[0].relative_to(TEMPLATES_DIR))
    return extends_path

def get_layout_chain(path, content):
    extends = get_extends(content)
    if not extends:
        return [path]
    chain = [path]
    current = extends
    visited = {path}
    current_dir = str(Path(path).parent) if Path(path).parent != Path('.') else ''
    while current:
        if current in visited:
            break
        visited.add(current)
        chain.append(current)
        if current in inheritance_cache:
            current = inheritance_cache[current]
            continue
        resolved = resolve_template_path(current, current_dir)
        current_dir = str(Path(resolved).parent) if Path(resolved).parent != Path('.') else ''
        template_path = TEMPLATES_DIR / resolved
        if not template_path.exists():
            break
        current_content = read_file(template_path)
        next_extends = get_extends(current_content)
        inheritance_cache[resolved] = next_extends
        current = next_extends
    return chain

def uses_bootstrap_layout(chain):
    return any(l in LAYOUT_BOOTSTRAP for l in chain)

def uses_store_layout(chain):
    return any(l in LAYOUT_STORE for l in chain)

# Read all templates
template_files = {}
for tf in sorted(TEMPLATES_DIR.rglob("*.html")):
    rel = str(tf.relative_to(TEMPLATES_DIR))
    template_files[rel] = read_file(tf)

# Build cache
for path, content in template_files.items():
    get_layout_chain(path, content)

results = []
for path, content in template_files.items():
    chain = get_layout_chain(path, content)
    has_bootstrap_layout = uses_bootstrap_layout(chain)
    has_store_layout = uses_store_layout(chain)
    
    direct_bootstrap_css = any(p in content for p in ['bootstrap.rtl.min.css', 'bootstrap.min.css'])
    direct_bootstrap_js = any(p in content for p in ['bootstrap.bundle.min.js', 'bootstrap.min.js'])
    direct_jquery = any(p in content for p in ['jquery-3.7.1.min.js', 'jquery.min.js'])
    direct_select2 = any(p in content for p in ['select2.min.css', 'select2.min.js'])
    has_alpine = 'x-data' in content or 'x-show' in content or 'x-transition' in content
    has_htmx = 'hx-' in content or 'htmx' in content.lower()
    
    inline_styles = count_pattern(content, r'style="[^"]*"')
    inline_scripts = count_pattern(content, r'<script[^>]*>')
    event_handlers = count_pattern(content, r'\son(click|change|submit|input|keydown|focus|blur|mouseover|mouseout|scroll|resize|load|error|dblclick|keyup|keypress|mousedown|mouseup|touchstart|touchend|touchmove)="[^"]*"')
    
    data_bs = re.findall(r'data-bs-[a-zA-Z-]+', content)
    
    if has_store_layout and not has_bootstrap_layout:
        classification = 'GREEN' if (inline_styles == 0 and inline_scripts == 0 and event_handlers == 0 and not direct_select2) else 'YELLOW'
    elif has_bootstrap_layout:
        if direct_select2 or len(data_bs) >= 3:
            classification = 'RED'
        else:
            classification = 'YELLOW'
    else:
        classification = 'YELLOW' if (inline_styles > 0 or inline_scripts > 0 or event_handlers > 0 or direct_select2) else 'GREEN'
    
    includes = get_includes(content)
    results.append({
        'path': path,
        'extends': get_extends(content),
        'chain': ' -> '.join(chain),
        'has_bootstrap_layout': has_bootstrap_layout,
        'has_store_layout': has_store_layout,
        'direct_bootstrap_css': direct_bootstrap_css,
        'direct_bootstrap_js': direct_bootstrap_js,
        'direct_jquery': direct_jquery,
        'direct_select2': direct_select2,
        'has_alpine': has_alpine,
        'has_htmx': has_htmx,
        'inline_styles': inline_styles,
        'inline_scripts': inline_scripts,
        'event_handlers': event_handlers,
        'data_bs': data_bs,
        'classification': classification,
        'includes': includes,
    })

# Output summary
total = len(results)
greens = [r for r in results if r['classification'] == 'GREEN']
yellows = [r for r in results if r['classification'] == 'YELLOW']
reds = [r for r in results if r['classification'] == 'RED']

print(f"TOTAL TEMPLATES: {total}")
print(f"GREEN: {len(greens)}")
print(f"YELLOW: {len(yellows)}")
print(f"RED: {len(reds)}")
print()

# Categorize
storefront = [r for r in results if r['has_store_layout'] and not r['has_bootstrap_layout']]
production = [r for r in results if r['has_bootstrap_layout'] and not r['has_store_layout']]
standalone = [r for r in results if not r['has_bootstrap_layout'] and not r['has_store_layout']]

print(f"Storefront (store layout): {len(storefront)}")
print(f"  GREEN: {sum(1 for r in storefront if r['classification']=='GREEN')}")
print(f"  YELLOW: {sum(1 for r in storefront if r['classification']=='YELLOW')}")
print(f"  RED: {sum(1 for r in storefront if r['classification']=='RED')}")
print()

print(f"Production (dashboard layout): {len(production)}")
print(f"  GREEN: {sum(1 for r in production if r['classification']=='GREEN')}")
print(f"  YELLOW: {sum(1 for r in production if r['classification']=='YELLOW')}")
print(f"  RED: {sum(1 for r in production if r['classification']=='RED')}")
print()

print(f"Standalone/no extends: {len(standalone)}")
print(f"  GREEN: {sum(1 for r in standalone if r['classification']=='GREEN')}")
print(f"  YELLOW: {sum(1 for r in standalone if r['classification']=='YELLOW')}")
print(f"  RED: {sum(1 for r in standalone if r['classification']=='RED')}")
print()

# Layouts
layouts = [r for r in results if r['path'].startswith('layouts/')]
print(f"Layout files: {len(layouts)}")
for l in layouts:
    print(f"  {l['path']}: {l['classification']}")
print()

# Components
components = [r for r in results if r['path'].startswith('components/')]
print(f"Component templates: {len(components)}")
for c in components:
    print(f"  {c['path']}: {c['classification']}")
print()

# Includes
includes = [r for r in results if r['path'].startswith('includes/')]
print(f"Include templates: {len(includes)}")
for i in includes:
    print(f"  {i['path']}: {i['classification']}")
print()

# Exact counts
print("=== EXACT METRICS ===")
print(f"Total templates: {total}")
print(f"GREEN: {len(greens)}")
print(f"YELLOW: {len(yellows)}")
print(f"RED: {len(reds)}")
print()

# Count components by actual filesystem
comp_files = list(TEMPLATES_DIR.rglob("components/*/*.html"))
comp_files += list(TEMPLATES_DIR.rglob("components/*.html"))
comp_files = sorted(set(comp_files))
print(f"Total component files: {len(comp_files)}")
for cf in comp_files:
    print(f"  {cf.relative_to(TEMPLATES_DIR)}")
print()

# Bootstrap CSS files
print("Bootstrap CSS files:")
for f in sorted(STATIC_DIR.rglob("*.css")):
    if 'bootstrap' in f.name.lower() or 'select2' in f.name.lower():
        print(f"  {f}")
print()

# Bootstrap JS files
print("Bootstrap JS files:")
for f in sorted(STATIC_DIR.rglob("*.js")):
    if 'bootstrap' in f.name.lower() or 'jquery' in f.name.lower() or 'select2' in f.name.lower():
        print(f"  {f}")
print()

# Templates using Bootstrap
templates_using_bootstrap = [r for r in results if r['has_bootstrap_layout'] or r['direct_bootstrap_css'] or r['direct_bootstrap_js'] or r['data_bs']]
print(f"Templates using Bootstrap (loaded or data-bs-*): {len(templates_using_bootstrap)}")
for t in templates_using_bootstrap:
    print(f"  {t['path']}")
print()

# Templates using jQuery
templates_using_jquery = [r for r in results if r['direct_jquery']]
print(f"Templates loading jQuery directly: {len(templates_using_jquery)}")
for t in templates_using_jquery:
    print(f"  {t['path']}")
print()

# Templates using Select2
templates_using_select2 = [r for r in results if r['direct_select2']]
print(f"Templates loading Select2 directly: {len(templates_using_select2)}")
for t in templates_using_select2:
    print(f"  {t['path']}")
print()

# Inline CSS
templates_with_inline_style = [r for r in results if r['inline_styles'] > 0]
print(f"Templates with inline <style> or style=\"\": {len(templates_with_inline_style)}")
for t in templates_with_inline_style:
    print(f"  {t['path']}: {t['inline_styles']}")
print()

# Inline JS
templates_with_inline_script = [r for r in results if r['inline_scripts'] > 0]
print(f"Templates with inline <script> blocks: {len(templates_with_inline_script)}")
for t in templates_with_inline_script:
    print(f"  {t['path']}: {t['inline_scripts']}")
print()

# Event handlers
templates_with_handlers = [r for r in results if r['event_handlers'] > 0]
print(f"Templates with inline event handlers: {len(templates_with_handlers)}")
for t in templates_with_handlers:
    print(f"  {t['path']}: {t['event_handlers']}")
print()

# data-bs usage
templates_with_data_bs = [r for r in results if r['data_bs']]
print(f"Templates with data-bs-* attributes: {len(templates_with_data_bs)}")
for t in templates_with_data_bs:
    print(f"  {t['path']}: {t['data_bs']}")
print()

# Save
with open('audit_final.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("Saved to audit_final.json")
