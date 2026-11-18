#!/usr/bin/env python3
"""unread-e212sw (Q218) step 1h: what an earlier lane's file says next to a test token, with EVERY DIGIT MASKED ('#'), so the lane
learns what was read without reading any value (the declaration comes before any read of the test runs' power, energy or seconds).
Run: /usr/bin/python3 -I -B s01h_context.py <file> <regex> [max hits] [width]
"""
import re
import sys

p, rx = sys.argv[1], re.compile(sys.argv[2])
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 6
wd = int(sys.argv[4]) if len(sys.argv) > 4 else 160
t = open(p, errors='replace').read()
n = 0
for m in rx.finditer(t):
    a, b = max(0, m.start() - wd), min(len(t), m.end() + wd)
    s = re.sub(r'\d', '#', t[a:b]).replace('\n', ' / ')
    print(f'[{n}] ...{s}...')
    n += 1
    if n >= mx:
        break
print(f'hits shown {n}; total {len(rx.findall(t))}')
