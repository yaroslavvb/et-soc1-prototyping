#!/usr/bin/env python3
"""counts-e217 (decl-e217 step 4; counts-e214's s11_sources.py with E217's registration copy) step 11: SOURCES.json, the provenance record (desk; reads files only): GitHub main, the bench's sources (each file's
sha256 at the commit), core-et's manifest, Verilator and g++, the binaries built and the maps trained (with v31-counts' for comparison),
the drivers, the committed references, every tile counted (with arms.json's registered sha256), the bench outputs, the scope record,
the re-count rule, and this lane's own slot jobs and slot-minutes (W/locks/cpu-slots.log: start lines naming this lane's folder, paired
by slot and pid).
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
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(L)), 'scripts', 'cnt'))
import inventory_e217 as I  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


bench_dir = os.path.join(LAB, 'rtl-sim', 'fma_toggle_v2')
v31src = json.load(open(os.path.join(LAB, 'tools/matmul/mm1/v3.1/counts/SOURCES.json')))
s = {'lane': 'counts-e217 (decl-e217 step 4, round Q228), Thu 19 Nov 2026, on aifoundry2: desk only, no card, no sys_emu, no fit, no commit',
     'lab_github_main': '8bde0182e66646cb67f9589b98c91a8b3a68b50e',
     'bench': {'path': 'rtl-sim/fma_toggle_v2', 'files_sha256': {f: sha(os.path.join(bench_dir, f)) for f in sorted(os.listdir(bench_dir))},
               'manifest_sha256': sha(os.path.join(WK, 'bench-src.sha256')),
               'manifest_equal_to_v31counts': open(os.path.join(WK, 'bench-src.sha256')).read() ==
               open(os.path.join(W, 'out', 'v31-counts', 'work', 'bench-src.sha256')).read(),
               'copy_change': "the Makefile's Verilator -j 10 made -j 2 (the copy's one change); make -j 1; no --threads (a single-threaded model)"},
     'core_et': {'commit': 'b38a1a31da67efe00c61e983e64b892c58080115', 'by': 'git archive of the commit: rtl, dv/inc, extern, LICENSE',
                 'files': sum(1 for _ in open(os.path.join(WK, 'core-et-copy.sha256'))), 'manifest_sha256': sha(os.path.join(WK, 'core-et-copy.sha256')),
                 'manifest_equal_to_v31counts': open(os.path.join(WK, 'core-et-copy.sha256')).read() ==
                 open(os.path.join(W, 'out', 'v31-counts', 'work', 'core-et-copy.sha256')).read()},
     'verilator': subprocess.run(['<VERILATOR_BIN>/verilator', '--version'], capture_output=True, text=True).stdout.strip(),
     'gxx': subprocess.run(['g++', '--version'], capture_output=True, text=True).stdout.splitlines()[0],
     'binaries_sha256': {b: sha(os.path.join(WK, 'bench', b)) for b in ('obj_vpu/Vtb', 'obj_unit/Vtb', 'accum', 'settle_count')},
     'binaries_v31counts_sha256': v31src['binaries_sha256'],
     'binaries_note': "obj_unit/Vtb, accum and settle_count are byte-equal to v31-counts'; obj_vpu/Vtb embeds its build paths (as the verifier of v31-counts found)",
     'maps_sha256': {m: sha(os.path.join(WK, 'maps', m)) for m in sorted(os.listdir(os.path.join(WK, 'maps')))},
     'maps_v31counts_sha256': v31src['maps_sha256'],
     'drivers_sha256': {p: sha(os.path.join(LAB, p)) for p in ('tools/claims-v3/e210/desk/count_e210.py', 'tools/claims-v3/e210/desk/hd_model_e210.py',
                                                               'rtl-sim/fma_toggle_v2/run_kinds.py', 'rtl-sim/fma_toggle_v2/accum.c',
                                                               'rtl-sim/fma_toggle_v2/settle_count.cpp', 'rtl-sim/fma_toggle_v2/train_maps.py',
                                                               'rtl-sim/fma_toggle_v2/fcheck_all.sh')},
     'committed_references_sha256': {p: sha(os.path.join(LAB, p)) for p in (
         'docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json', 'tools/claims-v3/e210/desk/switch-counts-e210.json',
         'tools/matmul/mm1/v1/inputs/switch_table.json', 'tools/matmul/mm1/v3.1/counts/SHA256SUMS',
         'tools/matmul/mm1/v3.1/counts/counts-fp32-gemm-states.json', 'tools/matmul/mm1/v3.1/counts/counts-fp16-int8-launch.json',
         'tools/matmul/mm1/v3.1/counts/raw/new-fp32-S1.json', 'tools/matmul/mm1/v3.1/counts/raw/new-fp32-S2.json',
         'tools/matmul/mm1/v3.1/counts/raw/new-launch.json', 'tools/matmul/mm1/v3.1/mm1_v31.py', 'tools/matmul/mm1/v3.1/energy_v31.py',
         'tools/matmul/mm1/v3/mm1_v3.py', 'tools/matmul/mm1/v3/energy_v3.py', 'tools/matmul/mm1/v3/data_v3.py')},
     'registration_sha256': {p: sha(os.path.join(os.path.dirname(os.path.abspath(L)), 'work', 'e217-src', p)) for p in (
         'SRC-SHA256SUMS.txt', 'src/arms.json', 'src/tiles_gen.py', 'src/rgm136/host/main.cpp', 'src/SRC-SHA256SUMS')},
     'registration_note': "E217's kit: the orchestrator's read-only copy of the model session's src (out/orch/e217-src, 11:12:05 PST; SRC-SHA256SUMS.txt 854bd075...), copied into decl-e217's work/e217-src and checked 75/75",
     'tiles_sha256': json.load(open(os.path.join(WK, 'tiles-inventory.json'))),
     'recount_tiles_sha256': {p: sha(os.path.join(LAB, p)) for p in ('tools/claims-v3/e212/proposal/src/tiles/fp32/fld_mant.bin',
                                                                     'tools/claims-v3/e212/proposal/src/tiles/fp32/den8.bin',
                                                                     'tools/claims-v3/e212/proposal/src/tiles/int8/i8_pm1.bin',
                                                                     'tools/claims-v3/e212/proposal/src/tiles/fp16/fld16_mant.bin')},
     'bench_outputs_sha256': {n: sha(os.path.join(WK, 'counts', n)) for n in sorted(os.listdir(os.path.join(WK, 'counts')))},
     'scope_sha256': sha(os.path.join(WK, 'scope-e217.json')),
     'recount_rule_sha256': sha(os.path.join(WK, 'recount-rule.txt')),
     'functional_check': open(os.path.join(L, 'logs', 'fcheck-summary.txt')).read().strip(),
     'python': sys.version.split()[0] + ' (/usr/bin/python3 -I -B)',
     'commands': {
         'new-fp32-S1.json': 'count_e210.py --kinds <the 10 fp32 kinds> --js 3,11,19,27 --tsel 0,1 --jobs 1 (one file each: tile 0)',
         'new-fp32-S2.json': 'count_e210.py --kinds <the 10 fp32 kinds> --js 15,47,79,111 --tsel 2 --jobs 1 (one file each: tile 0)',
         'new-launch.json': 'run_kinds.py --types fp16 --only __none__ --extra-tiles <the 11 fp16 and int8 tiles + xcheck.sparse50h> --jobs 1 --keep-going',
         'recount-fp32-S1-fld_mant.json': 'count_e210.py --kinds fp32.e212.fld_mant --js 3,11,19,27 --tsel 0,1 --jobs 1',
         'recount-fp32-S2-den8.json': 'count_e210.py --kinds fp32.e212.den8 --js 15,47,79,111 --tsel 2 --jobs 1',
         'recount-launch.json': 'run_kinds.py --types fp16 --only __none__ --extra-tiles <int8 i8_pm1, fp16 fld16_mant> --jobs 1'}}
try:
    import numpy
    s['numpy'] = numpy.__version__
except Exception:
    s['numpy'] = None
starts, total, jobs = {}, 0.0, []
pat = re.compile(r'^(\S+ \S+) slot (\d) pid (\d+) (start: (.*)|end rc (\d+))$')
for line in open(os.path.join(W, 'locks', 'cpu-slots.log')):
    m = pat.match(line.rstrip('\n'))
    if not m:
        continue
    t = datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')
    key = (m.group(2), m.group(3))
    if m.group(5) is not None:
        if '/out/decl-e217/scripts/cnt/' in m.group(5):   # counts-e217: this step's inner scripts live in decl-e217's scripts/cnt/
            starts[key] = (t, m.group(5))
    elif key in starts:
        t0, cmd = starts.pop(key)
        d = (t - t0).total_seconds() / 60.0
        total += d
        sc = [x for x in cmd.split() if '/decl-e217/scripts/cnt/' in x]
        jobs.append({'start': t0.strftime('%Y-%m-%d %H:%M:%S'), 'minutes': round(d, 2), 'rc': int(m.group(6)),
                     'what': os.path.basename(sc[0]) if sc else '?'})
s['slot_jobs'] = jobs
s['slot_minutes_total'] = round(total, 2)
s['slot_jobs_open'] = [{'start': v[0].strftime('%Y-%m-%d %H:%M:%S'),
                        'what': ([os.path.basename(x) for x in v[1].split() if '/decl-e217/scripts/cnt/' in x] or ['?'])[0]} for v in starts.values()]
for k in I.KINDS:
    assert s['tiles_sha256'][k['rel']]['equals_arms_json_sha256'], k['rel']
json.dump(s, open(os.path.join(L, 'counts', 'SOURCES.json'), 'w'), indent=1, sort_keys=True)
print(f"SOURCES.json: slot jobs {len(jobs)}, slot-minutes {total:.2f}, open {len(s['slot_jobs_open'])}; maps equal to v31-counts' "
      f"{s['maps_sha256'] == s['maps_v31counts_sha256']}; binaries equal (but obj_vpu) "
      f"{all(s['binaries_sha256'][b] == s['binaries_v31counts_sha256'][b] for b in ('obj_unit/Vtb', 'accum', 'settle_count'))}")
for jb in jobs:
    print(f"  {jb['start']} {jb['minutes']:6.2f} min rc {jb['rc']} {jb['what']}")
