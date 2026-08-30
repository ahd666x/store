#!/usr/bin/env python3
"""Comprehensive Django template audit v2."""

import os
import re
from pathlib import Path
from collections import defaultdict

TEMPLATES_DIR = Path("templates")

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def get_extends(content):
    match = re.search(r'\{%\s*extends\s+[\'"]([^\'"]+)[\'"]\s*%\}', content)
    if match:
        return match.group(1)
    return None

def get_includes(content):
    return re.findall(r'\{%\s*include\s+[\'"]([^\'"]+)[\'"]\s*%\}', content)

def check_loads(content, patterns):
    for p in patterns:
        if p in content:
            return True
    return False

def count_pattern(content, pattern):
    return len(re.findall(pattern, content))

LAYOUT_BOOTSTRAP = {'layouts/dashboard.html'}
LAYOUT_STORE = {'layouts/store.html', 'base.html'}

inheritance_cache = {}

def resolve_template_path(extends_path, current_template_dir):
    """Resolve a template extends path to an absolute path under templates/."""
    # First try absolute path from templates dir as-is
    p = TEMPLATES_DIR / extends_path
    if p.exists():
        return extends_path
    # Try with .html
    p = TEMPLATES_DIR / f"{extends_path}.html"
    if p.exists():
        return f"{extends_path}.html"
    # Try relative to current template's directory
    if current_template_dir:
        p = TEMPLATES_DIR / Path(current_template_dir) / extends_path
        if p.exists():
            return str(Path(current_template_dir) / extends_path)
        # Try with .html
        p = TEMPLATES_DIR / Path(current_template_dir) / f"{extends_path}.html"
        if p.exists():
            return str(Path(current_template_dir) / f"{extends_path}.html")
    # Search by exact filename in all template dirs
    extends_filename = Path(extends_path).name
    candidates = list(TEMPLATES_DIR.rglob(extends_filename))
    if len(candidates) == 1:
        return str(candidates[0].relative_to(TEMPLATES_DIR))
    elif len(candidates) > 1:
        # Multiple matches - prefer one in the same app directory
        for c in candidates:
            rel = str(c.relative_to(TEMPLATES_DIR))
            if current_template_dir and rel.startswith(current_template_dir):
                return rel
        # Otherwise return first match
        return str(candidates[0].relative_to(TEMPLATES_DIR))
    return extends_path

def get_layout_chain(path, content, all_templates):
    """Get the full layout inheritance chain."""
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
            
        # Resolve the template path
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
    for layout in chain:
        if layout in LAYOUT_BOOTSTRAP:
            return True
    return False

def uses_store_layout(chain):
    for layout in chain:
        if layout in LAYOUT_STORE:
            return True
    return False

# Read all templates
template_files = {}
for tf in sorted(TEMPLATES_DIR.rglob("*.html")):
    rel = str(tf.relative_to(TEMPLATES_DIR))
    template_files[rel] = read_file(tf)

# Build inheritance cache
for path, content in template_files.items():
    get_layout_chain(path, content, template_files)

results = []
total_templates = len(template_files)

for path, content in template_files.items():
    chain = get_layout_chain(path, content, template_files)
    has_bootstrap_layout = uses_bootstrap_layout(chain)
    has_store_layout = uses_store_layout(chain)
    
    # Direct loads in template
    direct_bootstrap_css = check_loads(content, ['bootstrap.rtl.min.css', 'bootstrap.min.css'])
    direct_bootstrap_js = check_loads(content, ['bootstrap.bundle.min.js', 'bootstrap.min.js'])
    direct_jquery = check_loads(content, ['jquery-3.7.1.min.js', 'jquery.min.js'])
    direct_select2 = check_loads(content, ['select2.min.css', 'select2.min.js'])
    
    # Framework detection in content
    has_alpine = 'x-data' in content or 'alpine' in content.lower()
    has_htmx = 'hx-' in content or 'htmx' in content.lower()
    
    # Inline stuff
    inline_styles = count_pattern(content, r'style="[^"]*"')
    inline_scripts = count_pattern(content, r'<script[^>]*>')
    event_handlers = count_pattern(content, r'\son(click|change|submit|input|keydown|focus|blur|mouseover|mouseout|scroll|resize|load|error|dblclick|keyup|keypress|mousedown|mouseup|touchstart|touchend|touchmove)="[^"]*"')
    
    # jQuery patterns (actual jQuery usage, not .find())
    jquery_patterns = [
        r'\$\(document\)',
        r'\$\(function\b',
        r'\$\.ajax\(',
        r'\$\.get\(',
        r'\$\.post\(',
        r'\.on\([^)]*\)\s*=>',
        r'\.modal\(',
        r'select2',
    ]
    jquery_usage = []
    for p in jquery_patterns:
        matches = re.findall(rf'{p}[^\n]{{0,80}}', content)
        jquery_usage.extend(matches[:2])
    
    # Bootstrap Modal/JS direct calls
    bootstrap_modal_calls = re.findall(r'bootstrap\.\w+\([^)]*\)', content)
    
    # Select2 specific patterns
    select2_patterns = re.findall(r'select2[^<\n]{0,80}', content)
    
    # Classify
    if has_store_layout and not has_bootstrap_layout:
        if inline_styles > 0 or inline_scripts > 0 or event_handlers > 0 or direct_select2:
            classification = 'YELLOW'
        else:
            classification = 'GREEN'
    elif has_bootstrap_layout:
        if direct_select2 or len(jquery_usage) >= 3 or len(bootstrap_modal_calls) >= 2:
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
        'jquery_usage': jquery_usage,
        'bootstrap_modal_calls': bootstrap_modal_calls,
        'select2_patterns': select2_patterns,
        'classification': classification,
        'includes': includes,
    })

# Print summaries
print(f"Total templates: {total_templates}")
greens = [r for r in results if r['classification'] == 'GREEN']
yellows = [r for r in results if r['classification'] == 'YELLOW']
reds = [r for r in results if r['classification'] == 'RED']

print(f"GREEN: {len(greens)}")
print(f"YELLOW: {len(yellows)}")
print(f"RED: {len(reds)}")

print("\n=== RED TEMPLATES ===")
for r in reds:
    print(f"  {r['path']}")
    print(f"    Chain: {r['chain']}")
    print(f"    Direct Select2: {r['direct_select2']}")
    print(f"    jQuery usage count: {len(r['jquery_usage'])}")
    print(f"    Bootstrap modal calls: {len(r['bootstrap_modal_calls'])}")
    print(f"    Inline styles: {r['inline_styles']}, scripts: {r['inline_scripts']}, handlers: {r['event_handlers']}")

print("\n=== STOREFRONT (store layout) TEMPLATES ===")
for r in results:
    if r['has_store_layout'] and not r['has_bootstrap_layout']:
        print(f"  {r['classification']} - {r['path']}")

print("\n=== PRODUCTION (dashboard layout) TEMPLATES ===")
for r in sorted([r for r in results if r['has_bootstrap_layout'] and not r['has_store_layout']], key=lambda x: x['path']):
    print(f"  {r['classification']} - {r['path']}")

print("\n=== STANDALONE TEMPLATES (no extends) ===")
for r in sorted([r for r in results if not r['has_bootstrap_layout'] and not r['has_store_layout']], key=lambda x: x['path']):
    print(f"  {r['classification']} - {r['path']}")

print("\n=== SELECT2 INVENTORY ===")
for r in results:
    if r['direct_select2'] or r['select2_patterns']:
        print(f"  {r['path']}")
        for p in r['select2_patterns']:
            print(f"    {p}")

print("\n=== JQUERY USAGE INVENTORY ===")
for r in results:
    if r['jquery_usage']:
        print(f"  {r['path']}:")
        for j in r['jquery_usage']:
            print(f"    {j}")

print("\n=== BOOTSTRAP MODAL CALLS ===")
for r in results:
    if r['bootstrap_modal_calls']:
        print(f"  {r['path']}: {r['bootstrap_modal_calls']}")

print("\n=== INLINE STYLE TOTALS ===")
total_inline_styles = sum(r['inline_styles'] for r in results)
templates_with_inline_styles = sum(1 for r in results if r['inline_styles'] > 0)
print(f"Total inline style attributes: {total_inline_styles}")
print(f"Templates with inline styles: {templates_with_inline_styles}")

print("\n=== INLINE SCRIPT TOTALS ===")
total_inline_scripts = sum(r['inline_scripts'] for r in results)
templates_with_inline_scripts = sum(1 for r in results if r['inline_scripts'] > 0)
print(f"Total inline script blocks: {total_inline_scripts}")
print(f"Templates with inline scripts: {templates_with_inline_scripts}")

print("\n=== EVENT HANDLER TOTALS ===")
total_event_handlers = sum(r['event_handlers'] for r in results)
templates_with_event_handlers = sum(1 for r in results if r['event_handlers'] > 0)
print(f"Total inline event handlers: {total_event_handlers}")
print(f"Templates with event handlers: {templates_with_event_handlers}")

# Storefront specific totals
storefront = [r for r in results if r['has_store_layout'] and not r['has_bootstrap_layout']]
sf_green = sum(1 for r in storefront if r['classification'] == 'GREEN')
sf_yellow = sum(1 for r in storefront if r['classification'] == 'YELLOW')
sf_inline_styles = sum(r['inline_styles'] for r in storefront)
sf_inline_scripts = sum(r['inline_scripts'] for r in storefront)
sf_event_handlers = sum(r['event_handlers'] for r in storefront)

print(f"\n=== STOREFRONT DETAILS ===")
print(f"Total: {len(storefront)}, GREEN: {sf_green}, YELLOW: {sf_yellow}")
print(f"Inline styles: {sf_inline_styles}, scripts: {sf_inline_scripts}, handlers: {sf_event_handlers}")

# Production specific totals
production = [r for r in results if r['has_bootstrap_layout'] and not r['has_store_layout']]
prod_green = sum(1 for r in production if r['classification'] == 'GREEN')
prod_yellow = sum(1 for r in production if r['classification'] == 'YELLOW')
prod_red = sum(1 for r in production if r['classification'] == 'RED')
prod_inline_styles = sum(r['inline_styles'] for r in production)
prod_inline_scripts = sum(r['inline_scripts'] for r in production)
prod_event_handlers = sum(r['event_handlers'] for r in production)

print(f"\n=== PRODUCTION DETAILS ===")
print(f"Total: {len(production)}, GREEN: {prod_green}, YELLOW: {prod_yellow}, RED: {prod_red}")
print(f"Inline styles: {prod_inline_styles}, scripts: {prod_inline_scripts}, handlers: {prod_event_handlers}")

import json
with open('audit_results_v2.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("\nSaved to audit_results_v2.json")
