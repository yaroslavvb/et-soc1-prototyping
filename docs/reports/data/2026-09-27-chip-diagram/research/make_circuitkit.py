#!/usr/bin/env python3
"""Write docs/reports/sources/circuitkit.js: the memory-levels page's drawing kit, its circuit drawings and the scenes
of its L1, shire-cache, mesh and DRAM chains, copied for the chip diagram's deep zoom (30 Sep 2026, DESIGN §3.3, D8).

    python3 docs/reports/data/2026-09-27-chip-diagram/research/make_circuitkit.py

Each copied declaration keeps its text and is preceded by a line naming where it came from (memory-levels.script.js
at the commit it was read at, lines a-b). They are wrapped in one closure, so that the copies' names (comp, part,
boxShape, frame, T ...) never meet the chip page's; ENV hands them what they used from the memory-levels page: the
SVG primitives, that page's numbers and facts (imported by the chip page's build with an ml: prefix, so every
data-f in a copied drawing names a fact the chip page has), its example address, and BAP. The memory-levels page
itself is not touched; folding it onto this kit is a later change on its own branch.
What is not copied: the accesses (lit paths, mos(), the callouts and waveforms): the chip page shows the drawings
still; and the L3 and scratchpad chip-scale scenes: the chip page has the die."""
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
SRC = os.path.join(ROOT, 'docs', 'reports', 'sources', 'memory-levels.script.js')
OUT = os.path.join(ROOT, 'docs', 'reports', 'sources', 'circuitkit.js')
lines = open(SRC).read().split('\n')
try:
    REV = subprocess.run(['git', 'log', '-1', '--format=%h', '--', SRC], cwd=ROOT, capture_output=True, text=True).stdout.strip() or '?'
except OSError:
    REV = '?'
decl = {}
for i, l in enumerate(lines):
    m = re.match(r'^(?:async )?function ([A-Za-z0-9_]+)\(|^(?:const|let) ([A-Za-z0-9_]+)\b', l)
    if m:
        decl.setdefault(m.group(1) or m.group(2), i)


def strip_comment(l):
    return re.sub(r'\s*//[^\'"`]*$', '', l)


def extent(i):
    l = lines[i]
    if l.startswith(('function', 'async function')):
        if l.rstrip().endswith('}') and l.count('{') == l.count('}'):
            return i
        j = i + 1
        while lines[j] != '}':
            j += 1
        return j
    if strip_comment(l).rstrip().endswith(';'):
        return i
    # a multi-line const ends at the first line that closes it: '};' (or '];', ');') at column 0, or, for a short
    # table whose last entry closes it on its own line, that line
    j = i + 1
    while True:
        t = strip_comment(lines[j]).rstrip()
        if re.match(r'^[}\])]', lines[j]) and t.endswith(';'):
            return j
        if t.endswith(('};', '];')) and j - i < 4 and t.count('{') < t.count('}'):
            return j
        j += 1


def take(names):
    out = []
    for nm in names:
        i = decl[nm]
        e = extent(i)
        k = i   # the comment block just above
        while k > 0 and lines[k - 1].startswith(('/*', '   ', '//')) and not lines[k - 1].startswith('    '):
            k -= 1
            if lines[k].startswith('/*'):
                break
        body = '\n'.join(lines[k:e + 1])
        # the parts dictionaries are assigned to the memory-levels page's SCENES; here they stand alone
        body = re.sub(r'^const (\w+) = SCENES\.\w+\.parts = ', r'const \1 = ', body, flags=re.M)
        out.append(f'// {nm}: memory-levels.script.js at {REV}, lines {k + 1}-{e + 1}\n{body}')
    return '\n'.join(out)


KIT = ['kickAs', 'KB_CLS', 'COL', 'DASH', 'BAND_FILL', 'FS_BASE', 'comp', 'boxShape', 'part', 'tagPill', 'frame', 'railBand', 'wire', 'jn', 'netLab',
       'rail', 'gnd', 'mosV', 'mosH', 'invSym', 'andSym', 'mux2', 'flopSym', 'icgSym', 'ringAll', 'fitTexts', 'kbTexts']
CIRC = ['draw6T', 'buildCell', 'buildPanel', 'buildXing', 'buildLatchCell', 'drawReadTree', 'buildComparator']
ADDRS = ['P40', 'ADDR', 'bits', 'mkPA', 'L1_HART', 'dec1', 'dec2', 'hex3', 'dec5']
CHAINS = ['STG', 'TLX', 'buildL1Cache', 'buildL1Block', 'buildL1Row', 'buildL1Latch', 'buildL1Cmp',
          'buildL2Bank', 'buildL2Sub', 'buildL2Panel', 'buildL2Cell', 'buildL2Xing',
          'buildHop', 'buildWire', 'buildL3Wire',
          'buildMS', 'buildChan', 'buildDBank', 'buildDCell', 'buildPHY', 'buildDQ']
PARTS = ['L1P', 'L2P', 'L3P', 'DP']   # (the scratchpad's parts, SP, and its Vmin inset are not drawn here)
missing = [n for n in KIT + CIRC + ADDRS + CHAINS + PARTS if n not in decl]
if missing:
    raise SystemExit('not in memory-levels.script.js: ' + ', '.join(missing))
# the L3 level's parts: only those of the mesh hop and its wire (the L3's own scenes are not drawn here), with the
# entries they borrow from
L3KEEP = {'bankR', 'tol3', 'vcdown', 'slave', 'router', 'router2', 'link', 'flits', 'hopE', 'nochop', 'rep1', 'rep2', 'lsin', 'ls'}


def keep_entries(text, name, keep):
    head, rest = text.split('= {\n', 1)
    body, tail = rest.rsplit('\n};', 1)
    ents, cur = [], None
    for ln in body.split('\n'):
        m = re.match(r'^  ([A-Za-z0-9_]+):', ln)
        if m:
            cur = [m.group(1), [ln]]
            ents.append(cur)
        elif cur:
            cur[1].append(ln)
    want = set(keep)
    while True:
        more = {r for k, ls in ents if k in want for r in re.findall(name + r'\.([A-Za-z0-9_]+)', '\n'.join(ls))} - want
        if not more:
            break
        want |= more
    return head + '= {\n' + '\n'.join('\n'.join(ls) for k, ls in ents if k in want) + '\n};' + tail


HEAD = open(os.path.join(HERE, 'circuitkit.head.js')).read()
TAIL = open(os.path.join(HERE, 'circuitkit.tail.js')).read()
body = '\n\n'.join([
    '/* ---- the drawing kit ---- */\n' + take(KIT),
    '/* ---- shared circuit drawings (generic textbook circuits; ET facts by counts and names) ---- */\n' + take(CIRC),
    '/* ---- the example address and its decoders ---- */\n' + take(ADDRS),
    '/* ---- the chains\' scenes ---- */\n' + take(CHAINS),
    '/* ---- the parts\' texts (each part\'s panel) ---- */\n' + take([p for p in PARTS if p != 'L3P']) + '\n' + keep_entries(take(['L3P']), 'L3P', L3KEEP),
])
open(OUT, 'w').write(HEAD + body + '\n' + TAIL)
print('wrote', OUT, len(HEAD + body + TAIL), 'bytes from', REV)
