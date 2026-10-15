#!/usr/bin/env python3
"""pdfpage.py TXT N [M]  -- print page N (to M) of a pdftotext file, pages split by form feeds (page 1 = the cover).
pdfpage.py TXT --find REGEX  -- list the pages (and lines) where REGEX matches."""
import re, sys

path = sys.argv[1]
pages = open(path, errors='replace').read().split('\f')
if sys.argv[2] == '--find':
    rx = re.compile(sys.argv[3], re.I)
    for i, p in enumerate(pages, 1):
        for ln in p.splitlines():
            if rx.search(ln):
                print(f'p.{i}: {ln.strip()[:200]}')
else:
    a = int(sys.argv[2]); b = int(sys.argv[3]) if len(sys.argv) > 3 else a
    for i in range(a, b + 1):
        print(f'===== page {i} of {len(pages)} =====')
        print(pages[i - 1] if 0 < i <= len(pages) else '(no such page)')
