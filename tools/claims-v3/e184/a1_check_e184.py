#!/usr/bin/env python3
"""E184's dated amendment A1, its check (desk only): the registration's E184-T reader and A1's on E58's committed card-1 bursts.

    /usr/bin/python3 -B tools/claims-v3/e184/a1_check_e184.py <repository top> > tools/claims-v3/e184/logs/a1-check-e184.txt

The registered reader (E184.md section 5.3, as the kit first wrote it): each burst's rail average from c.refreshes, a first-order step
0.16 s after the launch edge, level and size by least squares, tau on a 0.01 s grid from 0.10 to 3.00 s; the rise over [t_on - 1, t_off],
the fall over [t_off - 0.8, t_off + 4] from a constant level. A1's reader: tau_a1_e184.fit_burst (E58's model). Both on E58's 100 ms
bursts of p1-p3 (docs/reports/data/2026-09-29-tau-aifoundry1-c1/): the SRAM rail on the SRAM-dominated D bursts, the minion rail on the H and
M bursts, against E58's committed fits (report.json).
SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e184_common as c  # noqa: E402
import tau_a1_e184 as tau  # noqa: E402

TOP = os.path.abspath(sys.argv[1])
E58 = os.path.join(TOP, "docs/reports/data/2026-09-29-tau-aifoundry1-c1")


def registered_edge(ts, ys, te):
    best = None
    for k in range(10, 301):
        t_ = k / 100.0
        xs = [(1.0 - math.exp(-(t - te - 0.16) / t_)) if t > te + 0.16 else 0.0 for t in ts]
        n = len(ts)
        sx, sy, sxx, sxy = math.fsum(xs), math.fsum(ys), math.fsum(x * x for x in xs), math.fsum(x * y for x, y in zip(xs, ys))
        det = n * sxx - sx * sx
        if det <= 0:
            continue
        d = (n * sxy - sx * sy) / det
        r0 = (sy - d * sx) / n
        sse = math.fsum((y - r0 - d * x) ** 2 for x, y in zip(xs, ys))
        if best is None or sse < best[0]:
            best = (sse, t_)
    return best[1]


rep = json.load(open(os.path.join(E58, "report.json")))
rows = {"sram_w": [], "minion_w": []}
for pdir in sorted(glob.glob(os.path.join(E58, "p[0-9]"))):
    for b in (json.loads(line) for line in open(os.path.join(pdir, "bursts.jsonl"))):
        if b.get("rate_ms") != 100 or b.get("status") != "ok":
            continue
        tel = [json.loads(line) for line in open(os.path.join(pdir, "tel-%02d.jsonl" % b["win"])) if line.startswith("{")]
        ref = c.refreshes(tel)
        tp, lines = tau.passes(tel)
        tr, tf = b["t_on_ms"] / 1000.0, b["t_off_ms"] / 1000.0
        for rail, kinds in (("sram_w", ("D",)), ("minion_w", ("H", "M"))):
            if b["kind"] not in kinds:
                continue
            pr = [(d["t_ms"] / 1000.0, d["sp"][rail][0]) for d in ref if tr - 1.0 <= d["t_ms"] / 1000.0 <= tf]
            pf = [(d["t_ms"] / 1000.0, d["sp"][rail][0]) for d in ref if tf - 0.8 <= d["t_ms"] / 1000.0 <= tf + 4.0]
            reg_r = registered_edge([p[0] for p in pr], [p[1] for p in pr], tr)
            reg_f = registered_edge([p[0] for p in pf], [p[1] for p in pf], tf)
            a1 = tau.fit_burst(tp, [d["sp"][rail][0] for d in lines], tr, tf, None, rep[rail]["100"]["one_pass"]["d_s"])
            rows[rail].append({"pass": os.path.basename(pdir), "win": b["win"], "kind": b["kind"], "secs": b["secs"], "registered_rise": reg_r,
                               "registered_fall": reg_f, "a1_shared": a1["tau_shared"], "a1_rise": a1["tau_rise"], "a1_fall": a1["tau_fall"]})
out = {"what": "E184-T's registered reader and A1's on E58's committed card-1 bursts (a1_check_e184.py)", "e58": {
    "sram_w": {"one_pass": rep["sram_w"]["100"]["one_pass"], "rise_fall": rep["sram_w"]["100"]["rise_fall_tau_s"], "by_kind": rep["sram_w"]["100"]["by_kind_tau"]},
    "minion_w": {"one_pass": rep["minion_w"]["100"]["one_pass"], "rise_fall": rep["minion_w"]["100"]["rise_fall_tau_s"], "by_kind": rep["minion_w"]["100"]["by_kind_tau"]}}}
for rail, rs in rows.items():
    out[rail] = {"bursts": len(rs), "rows": rs}
    for k in ("registered_rise", "registered_fall", "a1_shared", "a1_rise", "a1_fall"):
        out[rail]["median_" + k] = c.median([r[k] for r in rs])
print(json.dumps(out, indent=1, sort_keys=True))
