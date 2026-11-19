#!/usr/bin/env python3
"""unread-e214 (Q225) step 1g: which earlier lanes touched E214's committed data, and whether the same file names a measurement field.
Reads only lane scripts and result files under OUT (text files up to 3 MB): OUT/<lane>/scripts/**, OUT/<lane>/result.json, result.md, and
OUT/<lane>/logs/progress.txt. Opens no E214 data file and no E215 file of any card lane: lanes named card-e215a / card-e215b, and any path
naming an E215 data folder (rb-e215, data-e215, 2026-11-19-e215), are skipped. Desk; no device.
Prints, per lane, the files that name an E214 data token and whether the same file names a time or energy measurement field.
Run: /usr/bin/python3 -I -B s01g_search.py <OUT> <out json>
"""
import json
import os
import re
import sys

OUT = os.path.abspath(sys.argv[1])
DST = sys.argv[2]
TOK = re.compile(r'2026-11-18-e214-mmsweep3|data-e214-|e214-mmsweep3|ee-1118-mmsweep3|mmsweep3/sessions|(?<![0-9A-Fa-f])E214 (?:data|session|run)')
MEAS = re.compile(r'dP_w|p_mean_w|T_op_us|cyc_op_max|cyc_op_mean|kclock_mhz|J_op|pJ_mac|dP_corr|p_rest|W over idle|J over idle|cycles an op')
SKIP_LANE = re.compile(r'^card-e215|^unread-e214$')
SKIP_PATH = re.compile(r'rb-e215|data-e215|2026-11-19-e215|/box-e215|card-e215', re.I)
TEXT_EXT = ('.py', '.sh', '.json', '.md', '.txt', '.csv', '.js', '.log', '.tsv', '')
MAXB = 3 * 1024 * 1024
res = {}
nfiles = 0
for lane in sorted(os.listdir(OUT)):
    if SKIP_LANE.search(lane):
        continue
    lp = os.path.join(OUT, lane)
    if not os.path.isdir(lp):
        continue
    cand = [os.path.join(lp, f) for f in ('result.json', 'result.md', os.path.join('logs', 'progress.txt')) if os.path.isfile(os.path.join(lp, f))]
    root = os.path.join(lp, 'scripts')
    if os.path.isdir(root):
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if not SKIP_PATH.search(d) and d not in ('.git', '__pycache__', 'lab', 'clone', 'repo', 'scratch')]
            for f in fn:
                p = os.path.join(dp, f)
                if os.path.splitext(f)[1] in TEXT_EXT:
                    cand.append(p)
    for p in cand:
        if SKIP_PATH.search(os.path.relpath(p, OUT)):
            continue
        try:
            if os.path.getsize(p) > MAXB:
                continue
            t = open(p, 'r', errors='replace').read()
        except OSError:
            continue
        nfiles += 1
        m = TOK.search(t)
        if not m:
            continue
        res.setdefault(lane, []).append({'file': os.path.relpath(p, OUT), 'token': m.group(0), 'measurement_field_in_same_file': bool(MEAS.search(t))})
json.dump({'files_read': nfiles, 'lanes': res}, open(DST, 'w'), indent=1, sort_keys=True)
print('files read', nfiles, 'lanes with a hit', len(res))
for lane, rs in sorted(res.items()):
    e = sum(1 for r in rs if r['measurement_field_in_same_file'])
    print(f'{lane:28s} files {len(rs):3d}  with a measurement field {e:3d}  e.g. {rs[0]["file"]}')
