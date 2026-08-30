#!/usr/bin/env python3
"""Verify component usage and layout inheritance."""
import re
import json
import sys
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
TEMPLATES_DIR = Path("templates")

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def get_includes(content):
    return re.findall(r'\{%\s*include\s+[\'"]([^\'"]+)[\'"]\s*%\}', content)

# Read all templates
template_files = {}
for tf in sorted(TEMPLATES_DIR.rglob("*.html")):
    rel = str(tf.relative_to(TEMPLATES_DIR))
    template_files[rel] = read_file(tf)

# Component usage tracking
component_usage = defaultdict(list)

for path, content in template_files.items():
    includes = get_includes(content)
    for inc in includes:
        component_usage[inc].append(path)

# Print component usage
print("=== COMPONENT USAGE ===\n")
for comp_path in sorted(component_usage.keys()):
    usages = component_usage[comp_path]
    print(f"{comp_path}: {len(usages)} usages")
    for u in usages:
        print(f"  - {u}")
    print()

# Layout inheritance tree
print("=== LAYOUT INHERITANCE TREE ===\n")

def get_extends(content):
    match = re.search(r'\{%\s*extends\s+[\'"]([^\'"]+)[\'"]\s*%\}', content)
    return match.group(1) if match else None

# Build tree
tree = defaultdict(list)
roots = []

for path, content in template_files.items():
    extends = get_extends(content)
    if extends:
        tree[extends].append(path)
    else:
        roots.append(path)

def print_tree(node, prefix="", is_last=True, visited=None):
    if visited is None:
        visited = set()
    if node in visited:
        print(f"{prefix}{'└── ' if is_last else '├── '}{node} (CYCLE)")
        return
    visited.add(node)
    connector = '└── ' if is_last else '├── '
    print(f"{prefix}{connector}{node}")
    children = sorted(tree.get(node, []))
    for i, child in enumerate(children):
        is_last_child = (i == len(children) - 1)
        extension = "    " if is_last_child else "│   "
        print_tree(child, prefix + extension, is_last_child, visited.copy())

for root in sorted(roots):
    print_tree(root)

# Check for orphaned layouts
print("\n=== ORPHANED LAYOUTS ===")
layout_files = [p for p in template_files.keys() if p.startswith('layouts/')]
for layout in layout_files:
    content = template_files[layout]
    extends = get_extends(content)
    if extends:
        print(f"  {layout} extends {extends}")
    else:
        # Check if any template extends this layout
        used_by = [p for p, c in template_files.items() if get_extends(c) == layout or layout in get_extends(c) if get_extends(c)]
        if not used_by:
            print(f"  {layout}: NOT EXTENDED BY ANY TEMPLATE")
        else:
            print(f"  {layout}: used by {len(used_by)} templates")

# Legacy base templates
print("\n=== LEGACY BASE TEMPLATES ===")
for path in sorted(template_files.keys()):
    if 'base.html' in path and path != 'base.html':
        content = template_files[path]
        extends = get_extends(content)
        print(f"  {path}: extends {extends}")

# Component files count
print("\n=== COMPONENT FILES ===")
comp_files = list(TEMPLATES_DIR.rglob("components/*/*.html"))
comp_files += list(TEMPLATES_DIR.rglob("components/*.html"))
comp_files = sorted(set(comp_files))
print(f"Total component files: {len(comp_files)}")
for cf in comp_files:
    rel = str(cf.relative_to(TEMPLATES_DIR))
    usage_count = len(component_usage.get(rel, []))
    print(f"  {rel}: {usage_count} usages")
