#!/usr/bin/env python3
"""Comprehensive Django template audit."""

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

# Layout dependencies
LAYOUT_BOOTSTRAP = {'layouts/dashboard.html'}
LAYOUT_JQUERY = {'layouts/dashboard.html'}
LAYOUT_STORE = {'layouts/store.html', 'base.html'}

# For tracking inheritance chains
inheritance_cache = {}

def get_layout_chain(path, content, all_templates):
    """Get the full layout inheritance chain."""
    extends = get_extends(content)
    if not extends:
        return [path]
    
    chain = [path]
    current = extends
    visited = {path}
    
    while current:
        if current in visited:
            break
        visited.add(current)
        chain.append(current)
        
        if current in inheritance_cache:
            current = inheritance_cache[current]
            continue
            
        # Find the template file
        template_path = TEMPLATES_DIR / current
        if not template_path.exists():
            # Try adding .html
            template_path = TEMPLATES_DIR / f"{current}.html"
        if not template_path.exists():
            break
            
        current_content = read_file(template_path)
        next_extends = get_extends(current_content)
        inheritance_cache[current] = next_extends
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
    has_alpine = 'alpine' in content.lower() or 'x-data' in content
    has_htmx = 'htmx' in content.lower() or 'hx-' in content
    
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
        matches = re.findall(rf'{p}[^\n]{{0,60}}', content)
        jquery_usage.extend(matches[:2])
    
    # Bootstrap Modal/JS direct calls
    bootstrap_modal_calls = re.findall(r'bootstrap\.\w+\([^)]*\)', content)
    
    # Classify
    if has_store_layout and not has_bootstrap_layout:
        classification = 'GREEN'
        if inline_styles > 0 or inline_scripts > 0 or event_handlers > 0:
            classification = 'YELLOW'
    elif has_bootstrap_layout:
        if direct_select2 or len(jquery_usage) >= 2 or len(bootstrap_modal_calls) >= 2:
            classification = 'RED'
        else:
            classification = 'YELLOW'
    else:
        classification = 'YELLOW' if (inline_styles > 0 or inline_scripts > 0 or event_handlers > 0) else 'GREEN'
    
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
        'classification': classification,
        'includes': includes,
        'content_preview': content[:200].replace('\n', ' ')
    })

# Count by layout type
storefront = [r for r in results if r['has_store_layout'] and not r['has_bootstrap_layout']]
production = [r for r in results if r['has_bootstrap_layout'] and not r['has_store_layout']]
components = [r for r in results if 'components/' in r['path']]
layouts = [r for r in results if 'layouts/' in r['path']]
includes = [r for r in results if 'includes/' in r['path']]

print(f"Total templates: {total_templates}")
print(f"Storefront (store layout): {len(storefront)}")
print(f"Production (dashboard layout): {len(production)}")
print(f"Components: {len(components)}")
print(f"Layouts: {len(layouts)}")
print(f"Includes/partials: {len(includes)}")
print()

greens = [r for r in results if r['classification'] == 'GREEN']
yellows = [r for r in results if r['classification'] == 'YELLOW']
reds = [r for r in results if r['classification'] == 'RED']

print(f"GREEN: {len(greens)}")
print(f"YELLOW: {len(yellows)}")
print(f"RED: {len(reds)}")
print()

print("=== RED TEMPLATES ===")
for r in reds:
    print(f"  {r['path']}")
    print(f"    Extends: {r['extends']}")
    print(f"    Chain: {r['chain']}")
    print(f"    Direct Bootstrap CSS: {r['direct_bootstrap_css']}")
    print(f"    Direct Bootstrap JS: {r['direct_bootstrap_js']}")
    print(f"    Direct jQuery: {r['direct_jquery']}")
    print(f"    Direct Select2: {r['direct_select2']}")
    print(f"    Inline styles: {r['inline_styles']}")
    print(f"    Inline scripts: {r['inline_scripts']}")
    print(f"    Event handlers: {r['event_handlers']}")
    print(f"    jQuery usage: {r['jquery_usage']}")
    print(f"    Bootstrap modal calls: {r['bootstrap_modal_calls']}")

print()
print("=== YELLOW STOREFRONT TEMPLATES (unexpected) ===")
for r in storefront:
    if r['classification'] == 'YELLOW':
        print(f"  {r['path']}")
        print(f"    Inline styles: {r['inline_styles']}, scripts: {r['inline_scripts']}, handlers: {r['event_handlers']}")

print()
print("=== STOREFRONT TEMPLATES WITH INLINE STYLES/SCRIPTS/HANDLERS ===")
for r in storefront:
    if r['inline_styles'] > 0 or r['inline_scripts'] > 0 or r['event_handlers'] > 0:
        print(f"  {r['path']}: styles={r['inline_styles']}, scripts={r['inline_scripts']}, handlers={r['event_handlers']}")

print()
print("=== PRODUCTION TEMPLATE CLASSIFICATIONS ===")
for r in sorted(production, key=lambda x: x['path']):
    print(f"  {r['classification']} - {r['path']}")

print()
print("=== INLINE STYLE INVENTORY (all templates) ===")
for r in results:
    if r['inline_styles'] > 0:
        print(f"  {r['path']}: {r['inline_styles']}")

print()
print("=== INLINE SCRIPT INVENTORY (all templates) ===")
for r in results:
    if r['inline_scripts'] > 0:
        print(f"  {r['path']}: {r['inline_scripts']}")

print()
print("=== EVENT HANDLER INVENTORY (all templates) ===")
for r in results:
    if r['event_handlers'] > 0:
        print(f"  {r['path']}: {r['event_handlers']}")

print()
print("=== SELECT2 INVENTORY ===")
for r in results:
    if r['direct_select2']:
        print(f"  {r['path']}: {r['direct_select2']}")

print()
print("=== JQUERY USAGE INVENTORY ===")
for r in results:
    if r['jquery_usage']:
        print(f"  {r['path']}:")
        for j in r['jquery_usage']:
            print(f"    {j}")

print()
print("=== BOOTSTRAP MODAL CALLS ===")
for r in results:
    if r['bootstrap_modal_calls']:
        print(f"  {r['path']}: {r['bootstrap_modal_calls']}")

import json
with open('audit_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("\nSaved to audit_results.json")
