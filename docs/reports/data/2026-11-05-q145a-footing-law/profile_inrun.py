#!/usr/bin/env python3
"""heat-q145a: the mean board-power and die-reading profile after a launch (post hoc, descriptive), to read what an in-run slope
mixes. Per run: P(t) - P over [t0+3.0, t0+3.5) s and T(t) - T over the same, in 0.25 s bins from t0+0.25 s to t0+4.0 s; the
mean over runs whose run lasts >= 4.0 s. Also the same profile's slope dP/dT between successive half-second points.

    python3 -B profile_inrun.py <lab repo top> <out.json>
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import footing_inrun as F  # noqa: E402  (this lane's own loader)


def prof(dirs, gov=False):
    edges = np.arange(0.25, 4.01, 0.25)
    accP = [[] for _ in edges[:-1]]
    accT = [[] for _ in edges[:-1]]
    accM = [[] for _ in edges[:-1]]
    for d in dirs:
        X = F.load_tel(d, nodips=True)
        if X is None:
            continue
        runs = F.runs_of(d, X, gov_free=gov)
        t, P, T, M = X["t"], X["P"], X["T"], X["m34"]
        for r in runs:
            t0 = r["t0"]
            if r["tend"] - t0 < 4000:
                continue
            ref = (t >= t0 + 3000) & (t < t0 + 3500)
            if ref.sum() < 3:
                continue
            Pr, Tr = P[ref].mean(), T[ref].mean()
            Mr = np.nanmean(M[ref]) if np.isfinite(M[ref]).any() else np.nan
            for i in range(len(edges) - 1):
                q = (t >= t0 + 1000 * edges[i]) & (t < t0 + 1000 * edges[i + 1])
                if q.sum():
                    accP[i].append(P[q].mean() - Pr)
                    accT[i].append(T[q].mean() - Tr)
                    if np.isfinite(Mr):
                        accM[i].append(np.nanmean(M[q]) - Mr)
    out = []
    for i in range(len(edges) - 1):
        out.append({"t_s": float((edges[i] + edges[i + 1]) / 2), "n": len(accP[i]),
                    "dP_w": float(np.mean(accP[i])) if accP[i] else None, "dT_fw": float(np.mean(accT[i])) if accT[i] else None,
                    "dT_m34": float(np.mean(accM[i])) if accM[i] else None})
    return out


def main():
    top, outp = sys.argv[1], sys.argv[2]
    D = os.path.join(top, "docs/reports/data")
    res = {}
    b = os.path.join(D, "2026-11-05-e171-blind8-aifoundry3/aifoundry3/e171")
    res["E171_a3"] = prof([os.path.join(b, x) for x in sorted(os.listdir(b)) if x.startswith("p")])
    b = os.path.join(D, "2026-11-05-e172-blind8-card1/aifoundry1-c1/e172")
    res["E172_c1"] = prof([os.path.join(b, x) for x in sorted(os.listdir(b)) if x.startswith("p")])
    b = os.path.join(D, "2026-10-20-bitflip-ladder/aifoundry3/hl")
    res["E60_a3"] = prof([os.path.join(b, f"p{i}") for i in range(1, 9)])
    for k, v in res.items():
        print(k)
        for row in v:
            print("  t %.3f n %4d dP %+.3f dTfw %+.3f" % (row["t_s"], row["n"], row["dP_w"] or 0, row["dT_fw"] or 0),
                  "" if row["dT_m34"] is None else "dTm34 %+.3f" % row["dT_m34"])
    json.dump(res, open(outp, "w"), indent=1)


if __name__ == "__main__":
    main()
