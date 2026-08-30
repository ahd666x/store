#!/usr/bin/env python3
"""Audit JS files for jQuery/Bootstrap usage."""
import re
from pathlib import Path

js_files = sorted(Path('static/js').rglob('*.js'))
for jf in js_files:
    content = jf.read_text(encoding='utf-8')
    if not content.strip():
        continue
    jquery = bool(re.search(r'\$\(|jQuery|\$\.ajax|\$\.get|\$\.post|\.on\(|\.val\(|\.find\(|\.modal\(|select2', content))
    bootstrap = bool(re.search(r'bootstrap\.\w+\(', content))
    print(f"{jf}: jQuery={jquery}, Bootstrap={bootstrap}")
