#!/usr/bin/env python3
"""unread-e212sw (Q218) step 1g: which earlier lanes touched the test runs, and whether the same file handles energy.
Reads only lane scripts and result files under OUT (text files up to 3 MB): OUT/<lane>/scripts/** , OUT/<lane>/result.json, result.md,
and every text file up to 3 MB under the MM1-v3 design and build lanes (v3-design-a/b/c, v3-spec, mm1-v3, verify-mm1v3, fix-mm1v3).
Prints, per lane, the files that name a test token, and whether the same file names an energy field. Opens no E213 file
(paths under card-e213a, card-e213b and any data folder named for E213 are skipped). Desk; no device.
Run: /usr/bin/python3 -I -B s01g_search.py <OUT> <out json>
"""
import json
import os
import re
import sys

OUT = os.path.abspath(sys.argv[1])
DST = sys.argv[2]
E212_TOK = re.compile(r'den16_10|den16_4|fld16_(?:exp|mant|sign)|i8_den[136]|i8_pm1|fld_mant|fld_sign|lanes2|den21|bf16trunc|fp16grid|'
                      r'sparse50f|sparse50i|pattern:(?:den|fld|lanes|pow2|bf16|fp16grid|i8_)')
E206_7_TOK = re.compile(r'real:blind4|blind3|a_colconst|\be37\b|E206[AB]?\|p11[0-5]\b|E207\|b(?:4[23]|49|5[012])\b|\bp11[2-5]\b|\bb49\b|\bb5[012]\b')
ENERGY = re.compile(r'dP_w|p_work_w|p_rest_w|w_over|W_over_idle|W over idle|J over idle|w_meas|energy_points|\bw_given_t\b|data share|share of D')
DESIGN = ('v3-design-a', 'v3-design-b', 'v3-design-c', 'v3-spec', 'mm1-v3', 'verify-mm1v3', 'fix-mm1v3')
SKIP = re.compile(r'e213', re.I)
TEXT_EXT = ('.py', '.sh', '.json', '.md', '.txt', '.csv', '.js', '.log', '.tsv', '')
MAXB = 3 * 1024 * 1024
res = {}
nfiles = 0
for lane in sorted(os.listdir(OUT)):
    if lane in ('unread-e212sw',) or SKIP.search(lane):
        continue
    lp = os.path.join(OUT, lane)
    if not os.path.isdir(lp):
        continue
    cand = []
    for f in ('result.json', 'result.md'):
        if os.path.isfile(os.path.join(lp, f)):
            cand.append(os.path.join(lp, f))
    roots = [os.path.join(lp, 'scripts')] + ([lp] if lane in DESIGN else [])
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if not SKIP.search(d) and d not in ('.git', 'node_modules', '__pycache__', 'lab', 'clone', 'repo', 'scratch')]
            for f in fn:
                p = os.path.join(dp, f)
                if os.path.splitext(f)[1] in TEXT_EXT and p not in cand:
                    cand.append(p)
    for p in cand:
        if SKIP.search(os.path.relpath(p, OUT)):
            continue
        try:
            if os.path.getsize(p) > MAXB:
                continue
            t = open(p, 'r', errors='replace').read()
        except OSError:
            continue
        nfiles += 1
        a = E212_TOK.search(t)
        b = E206_7_TOK.search(t)
        if not (a or b):
            continue
        en = bool(ENERGY.search(t))
        r = res.setdefault(lane, [])
        r.append({'file': os.path.relpath(p, OUT), 'e212_token': a.group(0) if a else None, 'e206_e207_token': b.group(0) if b else None,
                  'energy_field_in_same_file': en})
json.dump({'files_read': nfiles, 'lanes': res}, open(DST, 'w'), indent=1, sort_keys=True)
print('files read', nfiles, 'lanes with a hit', len(res))
for lane, rs in sorted(res.items()):
    e = sum(1 for r in rs if r['energy_field_in_same_file'])
    t1 = sum(1 for r in rs if r['e212_token'])
    t2 = sum(1 for r in rs if r['e206_e207_token'])
    print(f'{lane:28s} files {len(rs):3d}  e212-token {t1:3d}  e206/7-token {t2:3d}  with energy field {e:3d}')
