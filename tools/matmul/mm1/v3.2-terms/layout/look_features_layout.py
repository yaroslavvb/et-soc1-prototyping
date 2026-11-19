#!/usr/bin/env python3
"""lay-contention s05: print the walk features of the equal-count layout groups beside the in-sample residuals (desk look, post hoc)."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, 'out')
F = json.load(open(os.path.join(WORK, 'features_layout.json')))
P = json.load(open(os.path.join(WORK, 'subset_points.json')))
SHAPE = re.compile(r'^gemmL(?:nc|n)?(\d+)x(\d+)x(\d+)$')


def wk(arm, kernel):
    if arm.startswith('gemmLnc'):
        return 'rgm136.gemmLnc'
    if arm.startswith('gemmLn'):
        return 'rgm211.gemmLn'
    return 'rgm211.gemmL' if kernel == 'rgm211' else 'rgm136.gemmL'


grp = {}
for i, p in enumerate(P):
    grp.setdefault((p['arm'], p['fmt'], p['n'], p['card'], p['kernel'], p['f'][:3]), []).append(i)
seen = set()
for g, idx in sorted(grp.items()):
    masks = sorted({P[i]['mask'] for i in idx})
    if len(masks) < 2:
        continue
    key0 = (g[0], g[2], tuple(masks))
    if key0 in seen:
        continue
    seen.add(key0)
    MB, NB, KB = (int(x) for x in SHAPE.match(g[0]).groups())
    k = wk(g[0], g[4])
    full = F['%s|%dx%dx%d|0xffffffff' % (k, MB, NB, KB)]
    print(f"{g[0]} n={g[2]} {g[3]} {g[1]}  full: fp {full['footprint_MB']:.1f} MB fresh/req {full['fresh_lines_step'] / full['lines_req_step']:.3f} "
          f"fresh/step {full['fresh_lines_step']:.0f} fanw {full['fanw']:.2f} link {full['mesh_link_max_lines']:.0f}")
    for i in sorted(idx, key=lambda i: P[i]['meas']):
        p = P[i]
        f = F['%s|%dx%dx%d|0x%x' % (k, MB, NB, KB, int(p['mask'], 16))]
        print(f"    {p['mask']:>11s} R{f['R']} C{f['C']} meas {p['meas']:8.1f} ein {100 * p['e_in']:+6.2f}%  fp {f['footprint_MB']:6.1f} MB "
              f"fresh/req {f['fresh_lines_step'] / f['lines_req_step']:.3f} fresh/step {f['fresh_lines_step']:6.1f} A_inL3 {f['A_in_L3']:.2f} "
              f"B_inL3 {f['B_in_L3']:.2f} fanw {f['fanw']:.2f} link {f['mesh_link_max_lines']:.0f} hopmax {f['mesh_hop_max']:.2f}")
