#!/usr/bin/env python3
"""fix-v31counts (Q217) step 6: SOURCES.json = v31-counts' provenance record, unchanged, plus a 'fix_v31counts' entry for this lane's
re-counts (desk; reads files only): the binaries and maps it ran (copies of v31-counts', sha256 equal), the drivers and tiles, its bench
outputs, and its own slot jobs and slot-minutes (W/locks/cpu-slots.log: start lines naming this lane's folder, paired by slot and pid).
    /usr/bin/python3 -I -B s06_sources.py <lane dir> <workflow dir W>
"""
import hashlib
import json
import os
import re
import sys
from datetime import datetime

L, W = sys.argv[1], sys.argv[2]
WK = os.path.join(L, 'work')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


src = json.load(open(os.path.join(WK, 'old', 'SOURCES.json')))
assert 'fix_v31counts' not in src
f = {'lane': 'fix-v31counts (Q217), Wed 18 Nov 2026, on aifoundry2: desk only, no card, no sys_emu, no build, no fit',
     'what': ("the re-counts that answer verify-v31counts' findings: fp32 real:blind4 at the S2 states with both files of its two-file pool "
              "(8 points; finding 1) and the e37 bound's two points (G4, G7; finding 2), each by E210's committed count_e210.py, unchanged"),
     'lab_github_main': src['lab_github_main'],
     'binaries_sha256': {b: sha(os.path.join(WK, 'bench', b)) for b in ('obj_vpu/Vtb', 'settle_count')},
     'binaries_note': "v31-counts' build, copied (not rebuilt): each sha256 equal to binaries_sha256 above",
     'maps_sha256': {m: sha(os.path.join(WK, 'maps', m)) for m in sorted(os.listdir(os.path.join(WK, 'maps')))},
     'drivers_sha256': {p: sha(os.path.join(WK, 'lab', p)) for p in ('tools/claims-v3/e210/desk/count_e210.py', 'tools/claims-v3/e210/desk/hd_model_e210.py',
                                                                      'rtl-sim/fma_toggle_v2/run_kinds.py')},
     'tiles_sha256': {p: sha(os.path.join(WK, 'lab', p)) for p in ('tools/claims-v3/kinds/blind4/tiles/fp32/fp32.real_pythia_embed_qkv.bin',
                                                                   'tools/claims-v3/kinds/blind4/tiles/fp32/fp32.real_qwen_q_down.bin',
                                                                   'tools/claims-v3/kinds/tiles/fp32/randn.bin')},
     'desk_tiles': {'e37': "v31-counts' 61 desk e37 tiles, copied, each equal to its desk list (raw/desk-tiles.sha256)",
                    'hybrid randnA_e37x03B.bin': {'sha256': sha(os.path.join(WK, 'dsk', 'hybrid', 'randnA_e37x03B.bin')),
                                                  'what': "randn.bin's A (words 0-255) + e37_03's B (words 256-511); equal to verify-v31counts' hybrid tile"}},
     'bench_outputs_sha256': {n: sha(os.path.join(WK, 'counts', n)) for n in ('recount-fp32-S2-real_blind4.json', 'e37-bound-G4.json', 'e37-bound-G7.json')},
     'commands': {
         'recount-fp32-S2-real_blind4.json': ('count_e210.py --kinds fp32.e207.real_blind4 --js 15,47,79,111 --tsel 2,3 --jobs 1 '
                                              '(spec: the two blind4 fp32 files, file 0 pythia_embed_qkv, file 1 qwen_q_down)'),
         'e37-bound-G4.json': 'count_e210.py --kinds fp32.e207.e37 --js 47 --tsel 2 --jobs 1 (spec: the 61 desk e37 tiles)',
         'e37-bound-G7.json': 'count_e210.py --kinds fp32.e207.e37.randnpair0 --js 47 --tsel 2 --jobs 1 (spec: the same list, file 3 = the hybrid tile)'},
     'python': sys.version.split()[0] + ' (/usr/bin/python3 -I -B)'}
try:
    import numpy
    f['numpy'] = numpy.__version__
except Exception:
    f['numpy'] = None
starts, total, jobs = {}, 0.0, []
pat = re.compile(r'^(\S+ \S+) slot (\d) pid (\d+) (start: (.*)|end rc (\d+))$')
for line in open(os.path.join(W, 'locks', 'cpu-slots.log')):
    m = pat.match(line.rstrip('\n'))
    if not m:
        continue
    t = datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')
    key = (m.group(2), m.group(3))
    if m.group(5) is not None:
        if '/out/fix-v31counts/' in m.group(5):
            starts[key] = (t, m.group(5))
    elif key in starts:
        t0, cmd = starts.pop(key)
        d = (t - t0).total_seconds() / 60.0
        total += d
        sc = [x for x in cmd.split() if '/fix-v31counts/scripts/' in x]
        jobs.append({'start': t0.strftime('%Y-%m-%d %H:%M:%S'), 'minutes': round(d, 2), 'rc': int(m.group(6)),
                     'what': os.path.basename(sc[0]) if sc else '?'})
f['slot_jobs'] = jobs
f['slot_minutes_total'] = round(total, 2)
f['slot_jobs_open'] = [{'start': v[0].strftime('%Y-%m-%d %H:%M:%S'), 'what': ([os.path.basename(x) for x in v[1].split() if '/fix-v31counts/scripts/' in x]
                                                                         or ['?'])[0]} for v in starts.values()]
for b, h in f['binaries_sha256'].items():
    assert h == src['binaries_sha256'][b], b
for m, h in f['maps_sha256'].items():
    assert h == src['maps_sha256'][m], m
src['fix_v31counts'] = f
json.dump(src, open(os.path.join(L, 'counts', 'SOURCES.json'), 'w'), indent=1, sort_keys=True)
print(f"SOURCES.json: v31-counts' record + fix_v31counts: slot jobs {len(jobs)}, slot-minutes {total:.2f}, open {len(f['slot_jobs_open'])}")
for jb in jobs:
    print(f"  {jb['start']} {jb['minutes']:6.2f} min rc {jb['rc']} {jb['what']}")
