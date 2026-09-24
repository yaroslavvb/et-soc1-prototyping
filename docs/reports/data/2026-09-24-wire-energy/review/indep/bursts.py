#!/usr/bin/env python3
"""Independent per-burst energy extraction (Method A), written without reference to analyze_wire.py.

Per (cfg, pass) burst:
  board: mean(board_w over [t0+0.5s, t1]) - mean(idle board_w in [t0-3.2s, t0) U (t1, t1+3.2s]),
         idle samples excluding any marks window padded [-0.2s, +0.6s].
  noc:   (mean(noc_w[0] over [t1-0.6s, t1]) - mean(noc_w[0] over [t0-2.5s, t0])) / 0.94
  E/B  = dW * wall / bytes, wall = t1 - t0 (t0 = first launch start, t1 = last launch end).
Output: bursts.json in this directory.
"""
import json, os, sys
import numpy as np

DATA = '/home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/data'
SETS = {
    ('v1', 'aifoundry2'): '2026-09-24-wire-aifoundry2',
    ('v1', 'aifoundry3'): '2026-09-24-wire-aifoundry3',
    ('v2', 'aifoundry2'): '2026-09-24-wire2-aifoundry2',
    ('v2', 'aifoundry3'): '2026-09-24-wire2-aifoundry3',
}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bursts.json')


def load(d):
    tel = [json.loads(l) for l in open(os.path.join(DATA, d, 'telemetry.jsonl'))]
    t = np.array([x['t_ms'] for x in tel], float)
    took = np.array([x['took_ms'] for x in tel], float)
    bw = np.array([x['board_w'] for x in tel], float)
    noc = np.array([x['sp']['noc_w'][0] for x in tel], float)
    temp = np.array([x['temp_c']['minshire'][0] for x in tel], float)
    mhz = np.array([x['mhz']['minion'] for x in tel], float)
    runs = [json.loads(l) for l in open(os.path.join(DATA, d, 'runs.jsonl'))]
    marks = [json.loads(l) for l in open(os.path.join(DATA, d, 'marks.jsonl'))]
    return dict(t=t, took=took, bw=bw, noc=noc, temp=temp, mhz=mhz), runs, marks


def main():
    out = []
    for (vs, card), d in SETS.items():
        tel, runs, marks = load(d)
        t = tel['t']
        inmark = np.zeros(len(t), bool)
        for m in marks:
            inmark |= (t >= m['t_start_ms'] - 200) & (t <= m['t_end_ms'] + 600)
        bursts = {}
        for r in runs:
            bursts.setdefault((r['cfg'], r['pass']), []).append(r)
        for (cfg, p), rs in bursts.items():
            rs.sort(key=lambda r: r['t_start_ms'])
            t0 = rs[0]['t_start_ms']; t1 = rs[-1]['t_end_ms']
            wall = (t1 - t0) / 1e3
            nbytes = sum(r['bytes'] for r in rs)
            burst = (t >= t0 + 500) & (t <= t1)
            idle = (((t >= t0 - 3200) & (t < t0)) | ((t > t1) & (t <= t1 + 3200))) & ~inmark
            idle_b = (t >= t0 - 3200) & (t < t0) & ~inmark
            idle_a = (t > t1) & (t <= t1 + 3200) & ~inmark
            nlast = (t >= t1 - 600) & (t <= t1)
            npre = (t >= t0 - 2500) & (t < t0)
            # instrument health: any slow read or sample gap around the burst
            around = (t >= t0 - 3200) & (t <= t1 + 3200)
            ta = t[around]
            maxgap = float(np.max(np.diff(ta))) if len(ta) > 1 else 1e9
            maxtook = float(np.max(tel['took'][around])) if around.any() else 1e9
            bad = maxtook > 300 or maxgap > 400 or burst.sum() < 10 or idle.sum() < 20 or nlast.sum() < 3
            bw_on = tel['bw'][burst].mean() if burst.any() else np.nan
            bw_idle = tel['bw'][idle].mean() if idle.any() else np.nan
            dW = bw_on - bw_idle
            dN = (tel['noc'][nlast].mean() - tel['noc'][npre].mean()) / 0.94 if nlast.any() and npre.any() else np.nan
            r0 = rs[0]
            # for comparison only: the pipeline's leakage model (analyze_wire.py A_LEAK_80=23.257 W, T_L=36 C)
            import math
            Tb = tel['temp'][burst].mean(); Ti = tel['temp'][idle].mean()
            leak = 23.257 / 36.0 * math.exp((0.5 * (Tb + Ti) - 80.0) / 36.0) * (Tb - Ti)
            out.append(dict(leak_w=float(leak), pJB_boardleak=(dW - leak) * wall / nbytes * 1e12,
                set=vs, card=card, cfg=cfg, pass_=p, n_launch=len(rs), wall=wall, bytes=nbytes,
                hop=r0['hop_distance'], mean_hops=r0['mean_hops'], axis=r0.get('hop_axis'),
                operands=r0['operands'], cycles_max=max(r['cycles_max'] for r in rs),
                dW=dW, dN=dN, pJB_board=dW * wall / nbytes * 1e12, pJB_noc=dN * wall / nbytes * 1e12,
                idle_before=float(tel['bw'][idle_b].mean()) if idle_b.any() else None,
                idle_after=float(tel['bw'][idle_a].mean()) if idle_a.any() else None,
                temp_on=float(tel['temp'][burst].mean()) if burst.any() else None,
                temp_idle=float(tel['temp'][idle].mean()) if idle.any() else None,
                mhz_on=float(np.median(tel['mhz'][burst])) if burst.any() else None,
                bad=bool(bad), maxtook=maxtook, maxgap=maxgap,
                n_burst=int(burst.sum()), n_idle=int(idle.sum()),
            ))
    json.dump(out, open(OUT, 'w'), indent=1)
    import collections
    c = collections.Counter((o['set'], o['card'], o['bad']) for o in out)
    print(c)
    for o in out:
        if o['bad']:
            print('BAD', o['set'], o['card'], o['cfg'], o['pass_'], o['maxtook'], o['maxgap'], o['n_burst'], o['n_idle'])


if __name__ == '__main__':
    main()
