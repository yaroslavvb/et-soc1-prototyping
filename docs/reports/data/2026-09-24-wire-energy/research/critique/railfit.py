#!/usr/bin/env python3
"""Per-rail and per-component fits of the wire/hop* configurations in catalogue.json:
energy per payload byte vs d, per card, for zeros, random and random-zeros; with and without d=8;
and a check of whether bandwidth (1/BW) explains the per-byte trend of each rail."""
import json, numpy as np
C = json.load(open('/home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/data/2026-09-23-energy-manual/catalogue.json'))
def fit(x, y):
    A = np.vstack([np.ones_like(x), x]).T
    c, *_ = np.linalg.lstsq(A, y, rcond=None); r = y - A @ c
    return c[0], c[1], float(np.sqrt(np.mean(r**2)))
res = {}
for host, card in C['cards'].items():
    s = card['summary']
    rows = {}
    for o in ('zeros', 'random'):
        for d in (1, 2, 3, 4, 5, 6, 8):
            v = s[f'wire/hop{d}/{o}']
            bw = v['bytes_per_s']['mean']
            W = v['over_idle_w']['mean']
            r = {k: v['rails_over_w'][k]['mean'] for k in ('minion_w', 'sram_w', 'noc_w')}
            r['unmetered_w'] = W - sum(r.values())
            r['board_w'] = W
            rows[(o, d)] = {k: val / bw * 1e12 for k, val in r.items()}   # pJ per payload byte
            rows[(o, d)]['bw_GBs'] = bw / 1e9
            rows[(o, d)]['shires'] = v['shires']
    print(f"\n=== {host}: pJ per payload byte by rail")
    print(" d  | " + " | ".join(f"{o[:4]} board  min  sram   noc  unm" for o in ('zeros', 'random')) + " | GB/s  GB/s/shire")
    for d in (1, 2, 3, 4, 5, 6, 8):
        z, rr = rows[('zeros', d)], rows[('random', d)]
        print(f" {d}  | " + " | ".join(f"{q['board_w']:9.2f} {q['minion_w']:5.2f} {q['sram_w']:5.2f} {q['noc_w']:5.2f} {q['unmetered_w']:5.2f}" for q in (z, rr))
              + f" | {rr['bw_GBs']:6.1f} {rr['bw_GBs']/rr['shires']:5.1f}")
    for sel, ds in (("all d", (1, 2, 3, 4, 5, 6, 8)), ("d<=6", (1, 2, 3, 4, 5, 6)), ("d<=5", (1, 2, 3, 4, 5))):
        x = np.array(ds, float)
        for comp in ('board_w', 'noc_w', 'sram_w', 'minion_w', 'unmetered_w'):
            yz = np.array([rows[('zeros', d)][comp] for d in ds]); yr = np.array([rows[('random', d)][comp] for d in ds])
            fz, fr, fd = fit(x, yz), fit(x, yr), fit(x, yr - yz)
            res[f"{host}/{sel}/{comp}"] = {"zeros": fz, "random": fr, "diff": fd}
            print(f"  {sel:5s} {comp:12s} slope pJ/B/hop: zeros {fz[1]:6.3f}  random {fr[1]:6.3f}  diff {fd[1]:6.3f} (int {fd[0]:5.2f}, rms {fd[2]:.2f})")
    # 1/BW model: per-byte = a + b*d + c/BW ; can't separate with 7 points well, show correlation of d and 1/BW
    ds = (1, 2, 3, 4, 5, 6, 8)
    x = np.array(ds, float); ibw = np.array([1 / rows[('random', d)]['bw_GBs'] * rows[('random', d)]['shires'] for d in ds])
    print("  corr(d, 1/BW-per-shire) =", round(float(np.corrcoef(x, ibw)[0, 1]), 3))
json.dump({k: {kk: list(map(float, vv)) for kk, vv in v.items()} for k, v in res.items()}, open('railfit.json', 'w'), indent=1)
