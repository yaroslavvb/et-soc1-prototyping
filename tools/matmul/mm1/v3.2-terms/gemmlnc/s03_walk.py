#!/usr/bin/env python3
"""lnc-energy step 2b (desk, no fitted constant): the traffic quantities rgm136's gemmLnc branch changes against its gemmL twin, from MM1-v3.1's
masked walk as landed (tools/matmul/mm1/v3.1/walk/walk/walk_v31.py, 5a75e212), at the full mask, for every committed gemmLnc shape, the smoke
shape 2x2x2 and E215's gemmLnc shapes (their shapes only: E215's registration, never a datum):
  - the shire's tile reads a shire-op after cooperation (summary.per_shire_step) and the duplicates (reads beyond the distinct ones);
  - the lab's desk L2 model on shire 0's own line stream, second pass (walk.l2_shire): A and B lines a shire-op that hit;
  - the chip's strict LRU of the active shires' tiles at 32 MB (walk.summary l3_strict): identical for both kernels by construction
    (chip_steps does not read the coop flag: checked by hashing chip_steps of both kernels at the small shapes);
  - the footprint (walk.footprint_tiles).
Standard library only; /usr/bin/python3 3.12.3."""
import hashlib
import json
import os
import sys
import time

LAB = os.environ.get('ET_LAB') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..'))
WALK = os.path.join(LAB, 'tools/matmul/mm1/v3.1/walk/walk')
OUT = os.environ.get('LNC_WORK') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work')
sys.path.insert(0, WALK)
import walk_v31 as Wk  # noqa: E402

SHAPES = [('2x3x2', 'E211 c01c'), ('3x5x7', 'E211 c02c'), ('1x1x1', 'E213 a087/k40'), ('1x1x44', 'E213 a086'), ('1x6x5', 'E213 a079'),
          ('3x1x3', 'E213 a075/k37'), ('4x1x6', 'E213 a082'), ('2x2x2', 'E213/E215 smoke s03/s14'),
          ('1x15x3', 'E215 a024 (shape only)'), ('1x12x4', 'E215 a026 (shape only)'), ('8x1x5', 'E215 a031 (shape only)'),
          ('5x1x10', 'E215 a032 (shape only)'), ('2x1x37', 'E215 b013 (shape only)')]
MASK = '0xffffffff'


def chip_hash(kernel, MB, NB, KB):
    h = hashlib.sha256()
    for st in Wk.chip_steps(kernel, MB, NB, KB, MASK):
        h.update(repr(st).encode())
    return h.hexdigest()


rows = []
for shp, what in SHAPES:
    MB, NB, KB = Wk.parse_shape(shp)
    t0 = time.time()
    s_l = Wk.summary('rgm136.gemmL', MB, NB, KB, MASK)
    r = {'shape': shp, 'what': what, 'MB': MB, 'NB': NB, 'KB': KB, 'footprint': s_l['footprint'], 'l3_strict_32MB': s_l['l3_strict'],
         'per_shire_step_gemmL': s_l['per_shire_step'], 'chip_step': s_l['chip_step']}
    s_n = None
    if MB * NB * KB <= 12:
        same = chip_hash('rgm136.gemmL', MB, NB, KB) == chip_hash('rgm136.gemmLnc', MB, NB, KB)
        s_n = Wk.summary('rgm136.gemmLnc', MB, NB, KB, MASK)
        r['chip_stream_equal_gemmL_gemmLnc'] = bool(same and s_n['l3_strict'] == s_l['l3_strict'])
    else:
        r['chip_stream_equal_gemmL_gemmLnc'] = 'by construction (chip_steps reads no coop flag); hashed at the small shapes'
    psn = {'A_reads': 32, 'B_reads': 32, 'A_distinct': 4, 'B_distinct': 8, 'lines_read': 1024, 'lines_distinct': 192}
    if s_n is not None:
        assert s_n['per_shire_step'] == psn, s_n['per_shire_step']
    r['per_shire_step_gemmLnc'] = psn
    for ker in ('rgm136.gemmL', 'rgm136.gemmLnc'):
        hits = Wk.l2_shire(ker, MB, NB, KB, 0)
        n = len(hits)
        r['l2_desk_shire0_' + ker.split('.')[1]] = {'A_L2_lines_per_op': sum(h[0] for h in hits) / n, 'B_L2_lines_per_op': sum(h[1] for h in hits) / n}
    a_l, b_l = r['l2_desk_shire0_gemmL']['A_L2_lines_per_op'], r['l2_desk_shire0_gemmL']['B_L2_lines_per_op']
    a_n, b_n = r['l2_desk_shire0_gemmLnc']['A_L2_lines_per_op'], r['l2_desk_shire0_gemmLnc']['B_L2_lines_per_op']
    r['derived_per_shire_op'] = {
        'duplicate_line_reads': 1024 - 192, 'duplicate_A_lines': 448, 'duplicate_B_lines': 384,
        'gemmL_lines_beyond_L2_desk': 192 - a_l - b_l, 'gemmLnc_lines_beyond_L2_desk': 1024 - a_n - b_n,
        'extra_L2_hits_desk': (a_n + b_n) - (a_l + b_l),
        'duplicates_that_hit_L2_desk_share': ((a_n + b_n) - (a_l + b_l)) / 832.0}
    r['seconds'] = round(time.time() - t0, 2)
    rows.append(r)
    d = r['derived_per_shire_op']
    print('%-7s %-28s fp %7.2f MB | L2-desk hits a shire-op gemmL A %6.2f B %6.2f, gemmLnc A %7.2f B %7.2f | beyond L2: L %6.2f Lnc %6.2f | '
          'dup hit L2 %.4f | L3 strict A %.3f B %.3f fresh lines/step %.1f | chip equal %s | %.1f s' % (
              shp, what, r['footprint']['MB'], a_l, b_l, a_n, b_n, d['gemmL_lines_beyond_L2_desk'], d['gemmLnc_lines_beyond_L2_desk'],
              d['duplicates_that_hit_L2_desk_share'], r['l3_strict_32MB']['A_in_L3_share_distinct'], r['l3_strict_32MB']['B_in_L3_share_distinct'],
              r['l3_strict_32MB']['chip_fresh_lines_per_step'], r['chip_stream_equal_gemmL_gemmLnc'], r['seconds']), flush=True)

json.dump({'walk': os.path.join('tools/matmul/mm1/v3.1/walk/walk', 'walk_v31.py'),
           'walk_sha256': hashlib.sha256(open(os.path.join(WALK, 'walk_v31.py'), 'rb').read()).hexdigest(), 'mask': MASK, 'rows': rows},
          open(os.path.join(OUT, 's03_walk.json'), 'w'), indent=1)
print('wrote work/s03_walk.json')
