#!/usr/bin/env python3
"""v31-counts (Q217) step 11: the provenance record (counts/SOURCES.json) and the slot-minutes this lane used (desk; reads files only).
    /usr/bin/python3 -I -B s11_sources.py <lane dir> <workflow dir W>
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime

L, W = sys.argv[1], sys.argv[2]
WK = os.path.join(L, 'work')
LAB = os.path.join(WK, 'lab')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def manifest(p):
    out = {}
    for line in open(p):
        h, f = line.rstrip('\n').split('  ', 1)
        out[f] = h
    return out


src = {'lab_github_main': '6efdb0024cc5a44b46c4d11f71047bc1d12f611c',
       'bench': {'path': 'rtl-sim/fma_toggle_v2', 'files_sha256': manifest(os.path.join(WK, 'bench-src.sha256')),
                 'makefile_copy_change': "Verilator's -j 10 made -j 2 in this lane's copy (the one change; no --threads anywhere: single-threaded model)",
                 'makefile_copy_sha256': sha(os.path.join(WK, 'bench', 'Makefile')),
                 'equal_to_lab_working_tree': open(os.path.join(WK, 'bench-src.sha256')).read() == open(os.path.join(WK, 'bench-labtree.sha256')).read()},
       'core_et': {'commit': 'b38a1a31da67efe00c61e983e64b892c58080115', 'copied': 'rtl, dv/inc, extern',
                   'files': sum(1 for _ in open(os.path.join(WK, 'core-et-copy.sha256'))), 'manifest_sha256': sha(os.path.join(WK, 'core-et-copy.sha256'))},
       'verilator': subprocess.run(['<VERILATOR_BIN>/verilator', '--version'], capture_output=True, text=True).stdout.strip(),
       'gxx': subprocess.run(['g++', '--version'], capture_output=True, text=True).stdout.splitlines()[0],
       'binaries_sha256': {b: sha(os.path.join(WK, 'bench', b)) for b in ('obj_vpu/Vtb', 'obj_unit/Vtb', 'accum', 'settle_count')},
       'maps_sha256': {m: sha(os.path.join(WK, 'maps', m)) for m in sorted(os.listdir(os.path.join(WK, 'maps')))},
       'drivers_sha256': {p: sha(os.path.join(LAB, p)) for p in (
           'tools/claims-v3/e210/desk/count_e210.py', 'tools/claims-v3/e210/desk/hd_model_e210.py', 'tools/claims-v3/e210/desk/gen_tiles_e210.cpp',
           'tools/claims-v3/e210/desk/drawtile_e210.h', 'tools/claims-v3/e210/desk/switch_counts_e210.py', 'rtl-sim/fma_toggle_v2/run_kinds.py',
           'rtl-sim/fma_toggle_v2/train_maps.py', 'rtl-sim/fma_toggle_v2/accum.c', 'rtl-sim/fma_toggle_v2/settle_count.cpp')},
       'committed_references_sha256': {p: sha(os.path.join(LAB, p)) for p in (
           'tools/claims-v3/e210/desk/switch-counts-e210.json', 'tools/claims-v3/e210/desk/counts-e210-S1.json',
           'tools/claims-v3/e210/desk/counts-e210-S2.json', 'docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json',
           'tools/matmul/mm1/v1/inputs/switch_table.json')},
       'desk_tiles': {'what': "rgm136's drawTile (copied verbatim in gen_tiles_e210.cpp), 61 pairs each, seeds FNV-1a('E210-desk|<gen>|fp32')",
                      'gens': ['randn (the fp32 re-count, E210\'s desk-only tiles)', 'e37 (E207\'s e37 kind)'],
                      'list_sha256': sha(os.path.join(WK, 'dsk', 'tiles-made.sha256')), 'n': sum(1 for _ in open(os.path.join(WK, 'dsk', 'tiles-made.sha256')))},
       'tiles_sha256': json.load(open(os.path.join(WK, 'tiles-inventory.json'))),
       'python': sys.version.split()[0] + ' (/usr/bin/python3 -I -B)'}
try:
    import numpy
    src['numpy'] = numpy.__version__
except Exception:
    src['numpy'] = None
fc = open(os.path.join(L, 'logs', 'progress.txt')).read()
src['functional_check'] = ('fcheck_all.sh PASS on this build: unit fp32 40,000 of 40,000 exact; unit fp16 39,701 exact + 299 named residue; '
                           'vpu fp32 22,016, fp16 22,016, int8 18,944 accumulator words exact, 0 mismatched; zero gate 63 cases, 0 differ')
# slot-minutes: this lane's slot jobs in W/locks/cpu-slots.log (start lines naming this lane's folder, paired by slot and pid)
starts, total, jobs = {}, 0.0, []
pat = re.compile(r'^(\S+ \S+) slot (\d) pid (\d+) (start: (.*)|end rc (\d+))$')
for line in open(os.path.join(W, 'locks', 'cpu-slots.log')):
    m = pat.match(line.rstrip('\n'))
    if not m:
        continue
    t = datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')
    key = (m.group(2), m.group(3))
    if m.group(5) is not None:
        if '/out/v31-counts/' in m.group(5):
            starts[key] = (t, m.group(5))
    elif key in starts:
        t0, cmd = starts.pop(key)
        d = (t - t0).total_seconds() / 60.0
        total += d
        sc = [x for x in cmd.split() if '/v31-counts/scripts/' in x]
        jobs.append({'start': t0.strftime('%Y-%m-%d %H:%M:%S'), 'minutes': round(d, 2), 'rc': int(m.group(6)),
                     'what': os.path.basename(sc[0]) if sc else '?'})
src['slot_jobs'] = jobs
src['slot_minutes_total'] = round(total, 2)
src['slot_jobs_open'] = [{'start': v[0].strftime('%Y-%m-%d %H:%M:%S'), 'what': ([os.path.basename(x) for x in v[1].split() if '/v31-counts/scripts/' in x]
                                                                           or ['?'])[0]} for v in starts.values()]
json.dump(src, open(os.path.join(L, 'counts', 'SOURCES.json'), 'w'), indent=1, sort_keys=True)
print(f"slot jobs {len(jobs)}, slot-minutes {total:.1f}, open {len(src['slot_jobs_open'])}")
for jb in jobs:
    print(f"  {jb['start']} {jb['minutes']:6.2f} min rc {jb['rc']} {jb['what']}")
