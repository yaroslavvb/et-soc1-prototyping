#!/usr/bin/env python3
"""citecheck.py REPO [--out FILE.json] [--md FILE.md]

Checks every "path:LINES" citation to a file of the lab repository in the chip diagram's facts (facts.json and
ladder-img/ladder-data.json): do the cited lines at HEAD still hold what the fact cites them for?

For each citation it scores the cited lines against the fact (shared numbers count double, words of five letters or
more once), at HEAD and in every committed version of the cited file. If HEAD's lines score below the best version's,
the citation has drifted: the best version's lines are followed to HEAD (the same text, found again; else difflib's
alignment of the two versions), and the new line numbers are proposed with how they were found. Citations into
external/ (pinned upstream clones) are only checked at HEAD.
"""
import json, os, re, subprocess, sys, difflib, collections

REPO = sys.argv[1]
OUT = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
MD = sys.argv[sys.argv.index('--md') + 1] if '--md' in sys.argv else None
OUT0 = os.path.abspath(OUT) if OUT else None
MD0 = os.path.abspath(MD) if MD else None
os.chdir(REPO)

F = json.load(open('docs/reports/data/2026-09-27-chip-diagram/facts.json'))['facts']
L = json.load(open('docs/reports/ladder-img/ladder-data.json'))['facts']
FACTS = dict(F); FACTS.update(L)

PATH = r'((?:docs|workloads|tools|scripts|external|rtl-sim|kernels|launchers|patches)/[\w./\-]+?\.(?:md|html|py|c|h|cpp|json|sh|txt|sv|v|vh|js|mjs|csv))'
LINES = r'(\d+(?:\s*[-–]\s*\d+)?(?:\s*,\s*\d+(?:\s*[-–]\s*\d+)?)*)'
RX = re.compile(PATH + ':' + LINES)
# a short alias the builders use: "05-claims.md:N" after a full path was given once in the same source
ALIAS = re.compile(r'(?<![\w/])((?:0\d|1\d|20)-[\w\-]+\.md|et-soc1-notes\.md|SYNTHESIS\.md):' + LINES)

def ranges(spec):
    out = []
    for part in re.split(r'\s*,\s*', spec.strip()):
        m = re.match(r'(\d+)(?:\s*[-–]\s*(\d+))?$', part)
        if m:
            a = int(m.group(1)); b = int(m.group(2) or a)
            if b < a or b - a > 40: b = a
            out.append((a, b))
    return out

NUM = re.compile(r'\d[\d,]*(?:\.\d+)?')
WORD = re.compile(r'[A-Za-z][A-Za-z0-9_\-]{4,}')
STOP = set('about which their there these those where while would could should other first after before since under every being three cards whole value values lines source table shown given'.split())

def toks(s):
    nums = {n.replace(',', '').rstrip('.') for n in NUM.findall(s)}
    nums = {n for n in nums if len(n) >= 2 or n not in '0123456789'}
    words = {w.lower() for w in WORD.findall(s)} - STOP
    return nums, words

def score(fact_t, text):
    fn, fw = fact_t; tn, tw = toks(text)
    return 2 * len(fn & tn) + len(fw & tw)

_cache = {}
def versions(path):
    """[(commit, date, [lines])] oldest first, HEAD last; external files: HEAD only"""
    if path in _cache: return _cache[path]
    vs = []
    if not path.startswith('external/'):
        log = subprocess.run(['git', 'log', '--format=%H %cs', '--', path], capture_output=True, text=True).stdout.split('\n')
        for ln in reversed([x for x in log if x.strip()]):
            h, d = ln.split()
            txt = subprocess.run(['git', 'show', f'{h}:{path}'], capture_output=True, text=True, errors='replace').stdout
            vs.append((h[:8], d, txt.split('\n')))
    try:
        vs.append(('HEAD', 'now', open(path, errors='replace').read().split('\n')))
    except FileNotFoundError:
        pass
    _cache[path] = vs
    return vs

def grab(lines, rs):
    return '\n'.join('\n'.join(lines[a - 1:b]) for a, b in rs if 0 < a <= len(lines))

def follow(old, head, a, b):
    """lines a..b of the old version, found in HEAD: (a', b', how)"""
    seg = old[a - 1:b]
    # exact text, unique in HEAD
    key = [x for x in seg if x.strip()]
    if key:
        hits = [i for i in range(len(head)) if head[i] == key[0]]
        if len(hits) == 1:
            i = hits[0] - (seg.index(key[0]))
            return i + 1, i + (b - a) + 1, 'same text'
    sm = difflib.SequenceMatcher(None, old, head, autojunk=False)
    def mapl(n):
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if i1 <= n - 1 < i2:
                if tag == 'equal': return j1 + (n - 1 - i1) + 1, 'aligned'
                return min(j1 + (n - 1 - i1), max(j2 - 1, j1)) + 1, 'aligned (changed block)'
        return None, 'lost'
    na, h1 = mapl(a); nb, h2 = mapl(b)
    if na is None or nb is None: return None, None, 'lost'
    return na, max(na, nb), h1 if h1 == h2 else h1 + '/' + h2

def fmt(rs):
    return ', '.join(f'{a}' if a == b else f'{a}-{b}' for a, b in rs)

rows = []
for fid, f, field in sorted([(k, v, fl) for k, v in FACTS.items() for fl in ('source', 'note') if v.get(fl)]):
    src = (f.get(field) or '')
    text = f.get('statement', '') + ' ' + (f.get('note') or '')
    ft = toks(text)
    last_full = {}
    cites = []
    for m in RX.finditer(src):
        cites.append((m.group(1), m.group(2), m.group(0)))
        last_full[os.path.basename(m.group(1))] = m.group(1)
    for m in ALIAS.finditer(src):
        base = m.group(1)
        full = last_full.get(base) or {'et-soc1-notes.md': 'docs/et-soc1-notes.md', 'SYNTHESIS.md': 'docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md'}.get(base) or ('docs/findings/' + base)
        if any(c[2].endswith(m.group(0)) for c in cites): continue
        cites.append((full, m.group(2), m.group(0)))
    for path, spec, raw in cites:
        rs = ranges(spec)
        vs = versions(path)
        if not vs or not rs:
            rows.append(dict(fact=fid, field=field, path=path, cited=spec, raw=raw, status='no-file' if not vs else 'unparsed')); continue
        head = vs[-1][2]
        r = dict(fact=fid, field=field, path=path, cited=spec, raw=raw)
        new, how, olds, st = [], [], [], 'ok'
        sh_all = score(ft, grab(head, rs))
        for a, b in rs:
            sc = [(score(ft, grab(v[2], [(a, b)])), i) for i, v in enumerate(vs)]
            top = max(x[0] for x in sc)
            bi = max(i for x, i in sc if x == top)          # ties: the latest version
            v = vs[bi]; shh = score(ft, grab(head, [(a, b)]))
            if v[0] == 'HEAD' or shh >= top:
                new.append((a, b)); how.append('kept'); continue
            na, nb, h = follow(v[2], head, a, b)
            new.append((na, nb) if na else (a, b)); how.append(f'{h} from {v[0]} {v[1]}'); olds.append(grab(v[2], [(a, b)])[:200])
            st = 'drifted'
        r['head_score'] = sh_all
        r['new_score'] = score(ft, grab(head, new))
        # method B: the best window of HEAD for a short citation
        span = max(b - a + 1 for a, b in rs)
        if len(rs) == 1 and span <= 3:
            best = max(((score(ft, '\n'.join(head[i:i + span])), i) for i in range(len(head))), default=(0, 0))
            if best[0] >= max(r['new_score'], sh_all) + 3:
                r['better_elsewhere'] = f"{best[1] + 1}" + (f"-{best[1] + span}" if span > 1 else '') + f" (score {best[0]})"
                r['better_text'] = '\n'.join(head[best[1]:best[1] + span])[:300]
                if st == 'ok': st = 'better-elsewhere'
        if st == 'ok' and sh_all < 2: st = 'weak'
        r['status'] = st
        if st != 'ok':
            r['proposed'] = fmt(new); r['how'] = '; '.join(how)
            r['old_text'] = '\n---\n'.join(olds); r['new_text'] = grab(head, new)[:300]
        else:
            r['head_text'] = grab(head, rs)[:200]
        rows.append(r)

cnt = collections.Counter(r['status'] for r in rows)
print('citations', len(rows), dict(cnt))
if OUT: json.dump(rows, open(OUT0, 'w'), indent=1, ensure_ascii=False)
if MD:
    with open(MD0, 'w') as fh:
        fh.write(f'# Line citations in the chip diagram\'s facts\n\n{dict(cnt)}\n\n')
        for r in rows:
            if r['status'] in ('ok',): continue
            fh.write(f"## {r['fact']} · {r['path']}:{r['cited']} · {r['status']}\n")
            for k in ('head_score', 'proposed', 'how', 'new_score', 'better_elsewhere'):
                if k in r: fh.write(f'- {k}: {r[k]}\n')
            for k in ('old_text', 'new_text', 'better_text', 'head_text'):
                if k in r: fh.write(f"- {k}:\n```\n{r[k]}\n```\n")
            fh.write('\n')
