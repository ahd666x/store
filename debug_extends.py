#!/usr/bin/env python3
import re
from pathlib import Path

for tf in sorted(Path('templates').rglob('*.html')):
    content = tf.read_text(encoding='utf-8')
    match = re.search(r'\{%\s*extends\s+[\'"]([^\'"]+)[\'"]\s*%\}', content)
    if match:
        print(tf.name, 'extends', match.group(1))
