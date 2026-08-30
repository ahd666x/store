#!/usr/bin/env python3
"""Audit script for Django templates."""

import os
import re
from pathlib import Path
from collections import defaultdict

TEMPLATES_DIR = Path("templates")
STATIC_DIR = Path("static")

BOOTSTRAP_CLASSES = {
    'btn', 'card', 'row', 'navbar', 'nav', 'alert', 'badge', 'modal', 'dropdown',
    'table', 'form-control', 'form-select', 'visually-hidden', 'spinner-border',
    'container', 'd-flex', 'd-none', 'd-block', 'd-inline', 'd-inline-block',
    'justify-content-between', 'justify-content-center', 'justify-content-end',
    'justify-content-around', 'justify-content-evenly',
    'align-items-center', 'align-items-end', 'align-items-start', 'align-items-stretch',
    'gap-', 'mb-', 'mt-', 'p-', 'shadow', 'border', 'rounded',
    'navbar-toggler', 'navbar-collapse', 'nav-item', 'nav-link', 'navbar-brand',
    'navbar-nav', 'navbar-expand-lg', 'collapse', 'fade', 'show', 'btn-close',
    'dropdown-toggle', 'dropdown-menu', 'dropdown-item', 'dropdown-divider',
    'toast-container', 'toast', 'toast-body', 'toast-header',
    'input-group', 'input-group-text', 'form-floating', 'form-label',
    'carousel', 'accordion', 'list-group', 'list-group-item',
    'breadcrumb', 'pagination', 'page-item', 'page-link'
}

JQUERY_PATTERNS = [
    r'\$\(', r'jQuery', r'\$\.ajax', r'\$\.get', r'\$\.post',
    r'\$\(document\)', r'\$\(function', r'\.on\(', r'\.val\(', r'\.find\(',
    r'\.modal\(', r'select2'
]

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def check_bootstrap_css(content):
    """Check if template directly loads Bootstrap CSS."""
    patterns = ["bootstrap.rtl.min.css", "bootstrap.min.css", "bootstrap.css"]
    return any(p in content for p in patterns)

def check_bootstrap_js(content):
    """Check if template directly loads Bootstrap JS."""
    patterns = ["bootstrap.bundle.min.js", "bootstrap.min.js", "bootstrap.js"]
    return any(p in content for p in patterns)

def check_jquery(content):
    """Check if template directly loads jQuery."""
    patterns = ["jquery", "jQuery"]
    # Exclude comments
    return any(p in content for p in patterns)

def extract_bootstrap_classes(content):
    """Find all HTML class attributes that contain Bootstrap-like classes."""
    classes = set()
    # Match class="..."
    for match in re.finditer(r'class="([^"]*)"', content):
        class_str = match.group(1)
        for cls in BOOTSTRAP_CLASSES:
            if cls in class_str:
                classes.add(cls)
    return sorted(classes)

def check_js_frameworks(content):
    frameworks = []
    if 'alpinejs.min.js' in content or 'alpine' in content.lower():
        frameworks.append('Alpine')
    if 'htmx.min.js' in content or 'htmx' in content.lower():
        frameworks.append('HTMX')
    return frameworks

def check_inline_style(content):
    return len(re.findall(r'style="[^"]*"', content))

def check_inline_script(content):
    return len(re.findall(r'<script[^>]*>', content))

def check_event_handlers(content):
    handlers = ['onclick', 'onchange', 'onsubmit', 'oninput', 'onkeydown', 'javascript:']
    count = 0
    for h in handlers:
        count += len(re.findall(rf'{h}=', content))
    return count

def check_jquery_usage(content):
    """Find actual jQuery usage patterns in template."""
    matches = []
    for pattern in JQUERY_PATTERNS:
        found = re.findall(rf'{pattern}[^\n]*', content)
        if found:
            matches.extend(found[:3])  # max 3 per pattern
    return matches

def check_extends(content):
    match = re.search(r'\{%\s*extends\s+[\'"]([^\'"]+)[\'"]\s*%\}', content)
    if match:
        return match.group(1)
    return None

def check_includes(content):
    includes = re.findall(r'\{%\s*include\s+[\'"]([^\'"]+)[\'"]\s*%\}', content)
    return includes

results = []
total_templates = 0
green_count = 0
yellow_count = 0
red_count = 0

template_files = sorted(TEMPLATES_DIR.rglob("*.html"))
for tf in template_files:
    total_templates += 1
    rel_path = tf.relative_to(TEMPLATES_DIR)
    content = read_file(tf)
    
    extends = check_extends(content)
    includes = check_includes(content)
    
    has_bootstrap_css = check_bootstrap_css(content)
    has_bootstrap_js = check_bootstrap_js(content)
    has_jquery = check_jquery(content)
    boot_classes = extract_bootstrap_classes(content)
    frameworks = check_js_frameworks(content)
    inline_style_count = check_inline_style(content)
    inline_script_count = check_inline_script(content)
    event_handler_count = check_event_handlers(content)
    jquery_usage = check_jquery_usage(content)
    
    # Determine classification
    is_green = True
    reasons = []
    
    if has_bootstrap_css:
        is_green = False
        reasons.append("loads Bootstrap CSS")
    if has_bootstrap_js:
        is_green = False
        reasons.append("loads Bootstrap JS")
    if has_jquery:
        is_green = False
        reasons.append("loads jQuery")
    
    # Check for actual Bootstrap-dependent classes
    # Classes defined in components.css are not Bootstrap-dependent
    custom_bootstrap_classes = {'btn', 'card', 'alert', 'badge', 'table', 'modal', 
                                 'navbar', 'nav', 'form-control', 'form-select', 
                                 'visually-hidden', 'spinner-border', 'dropdown',
                                 'collapse', 'fade', 'show', 'input-group', 'form-floating',
                                 'navbar-toggler', 'navbar-collapse', 'nav-item', 'nav-link',
                                 'navbar-brand', 'navbar-nav', 'navbar-expand-lg',
                                 'toast-container', 'toast', 'toast-body', 'toast-header',
                                 'btn-close', 'dropdown-toggle', 'dropdown-menu', 'dropdown-item',
                                 'breadcrumb', 'carousel', 'accordion', 'list-group'}
    
    actual_boot_classes = [c for c in boot_classes if c not in custom_bootstrap_classes]
    
    # Check for actual Bootstrap classes not reimplemented
    boot_grid_classes = [c for c in boot_classes if c.startswith('col-') or c in ('container', 'row')]
    if boot_grid_classes:
        is_green = False
        reasons.append(f"uses Bootstrap grid classes: {boot_grid_classes}")
    
    boot_display_classes = [c for c in boot_classes if c.startswith(('justify-content-', 'align-items-', 'd-'))]
    if boot_display_classes:
        is_green = False
        reasons.append(f"uses Bootstrap display classes: {boot_display_classes}")
    
    if inline_style_count > 0:
        is_green = False
        reasons.append(f"has {inline_style_count} inline style attributes")
    if inline_script_count > 0:
        is_green = False
        reasons.append(f"has {inline_script_count} inline script blocks")
    if event_handler_count > 0:
        is_green = False
        reasons.append(f"has {event_handler_count} inline event handlers")
    
    if is_green:
        green_count += 1
    else:
        # Check if it's RED (heavily legacy) or YELLOW (partial)
        if has_bootstrap_css or has_bootstrap_js or has_jquery:
            red_count += 1
        elif len(reasons) >= 3:
            red_count += 1
        else:
            yellow_count += 1
    
    results.append({
        'path': str(rel_path),
        'extends': extends,
        'bootstrap_css': has_bootstrap_css,
        'bootstrap_js': has_bootstrap_js,
        'jquery': has_jquery,
        'bootstrap_classes': boot_classes,
        'actual_bootstrap_classes': actual_boot_classes + boot_grid_classes + boot_display_classes,
        'frameworks': frameworks,
        'inline_styles': inline_style_count,
        'inline_scripts': inline_script_count,
        'event_handlers': event_handler_count,
        'jquery_usage': jquery_usage,
        'classification': 'GREEN' if is_green else ('RED' if red_count > yellow_count else 'YELLOW'),
        'reasons': reasons,
        'includes': includes
    })

print(f"Total templates: {total_templates}")
print(f"GREEN: {green_count}")
print(f"YELLOW: {yellow_count}")
print(f"RED: {red_count}")
print()
print("=== TEMPLATE DETAILS ===")
for r in results:
    print(f"\n{r['path']}")
    print(f"  Extends: {r['extends']}")
    print(f"  Bootstrap CSS: {r['bootstrap_css']}")
    print(f"  Bootstrap JS: {r['bootstrap_js']}")
    print(f"  jQuery: {r['jquery']}")
    print(f"  Bootstrap classes: {r['bootstrap_classes']}")
    print(f"  Actual Bootstrap classes: {r['actual_bootstrap_classes']}")
    print(f"  Frameworks: {r['frameworks']}")
    print(f"  Inline styles: {r['inline_styles']}")
    print(f"  Inline scripts: {r['inline_scripts']}")
    print(f"  Event handlers: {r['event_handlers']}")
    print(f"  Classification: {r['classification']}")
    if r['reasons']:
        print(f"  Reasons: {r['reasons']}")
    if r['jquery_usage']:
        print(f"  jQuery usage: {r['jquery_usage']}")
    if r['includes']:
        print(f"  Includes: {r['includes']}")

# Save detailed results
import json
with open('audit_templates.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("\nSaved to audit_templates.json")
