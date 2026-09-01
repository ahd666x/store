import re
import glob
from collections import Counter

ids = []
for f in glob.glob('templates/**/*.html', recursive=True):
    content = open(f, encoding='utf-8').read()
    ids.extend(re.findall(r'id="([^"]+)"', content))

dupes = [k for k, v in Counter(ids).items() if v > 1]
if dupes:
    for d in dupes:
        print(d)
else:
    print("No duplicates")
