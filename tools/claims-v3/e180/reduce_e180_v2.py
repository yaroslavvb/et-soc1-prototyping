#!/usr/bin/env python3
"""E180's reduction, v2 (the registration's dated note A1 section 4; the kit's dated note 1 section 2): v1's reduction, unchanged, plus
the per-burst readings A1's reported arms need.

    python3 tools/claims-v3/e180/reduce_e180_v2.py --data <card data dir: .../e180> --out reduced-e180-v2.json [--card aifoundry3]

v1 (reduce_e180.py, which stays as committed) is imported and run first: its every field (each kind's D per pass, the kept runs, the set-aside
passes and their reasons) is returned unchanged, so the registered rules read exactly what v1 gives them. Then, for the same kept bursts,
from the same pass telemetry and the same analyze_catalogue.bursts_of (imported unchanged), each burst also gets (A1 section 4.1):
  rise     Tb - Ti, bursts_of's die rise of the board's correction;
  D_FL1    over_idle_raw_w - k_FL1(T_mid) x rise, the card's own footing law (tools/claims-v3/footing-law, c14e5f35: aifoundry3's, or card
           1's on the fallback), T_mid = (Tb + Ti) / 2;
  D_E60    over_idle_raw_w - 0.2026 x rise (aifoundry3 only: E60's in-run slope there, reduce.txt line 19 at dfee3d7a);
  R_raw    rails_over.minion_w, bursts_of's raw minion-rail rise (the last 0.6 s against the rail idle before it, / 0.94);
  R        the net minion rail on footing A: R_raw - 0.81 x k21(T_rails) x (fw - fi) / 0.94, with tw, ti the raw die's means over the rails'
           busy window [hi - 0.6, hi] and idle window [max(prev hi + 3.0, lo - 3.5), lo - 0.3] (bursts_of's), T_rails = (tw + ti) / 2,
           fw, fi the same means of the die passed through the card's rail filter (recut.py's first-order lowpass at catalogue.json
           rail_filter tau: aifoundry3 1.235 s, card 1 1.153 s), k21 the 21 Sep law; the anatomy's rule A
           (docs/reports/data/2026-11-05-q145a-anatomy-top-lines/posthoc_note1_q145a.py burst_rises, 877e7476), line for line;
and each kind's per-pass mean of each, in "<name>" dictionaries beside v1's "D" (D_FL1, D_E60, R, R_raw, rise), with the kept bursts'
values in "runs_v2". A burst v1 kept but v2 cannot read (no rail window samples) is listed in "v2_unread" and leaves its kind's v2 means
from the other runs (never from v1's D). Nothing here changes a registered reading.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import re
import statistics as st
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_e180 as r1  # noqa: E402  (v1, unchanged)

C_RB, REACH, E60_SLOPE = 0.81, 0.94, 0.2026
TAU = {"aifoundry3": 1.235, "aifoundry1-c1": 1.153}
LAWKEY = {"aifoundry3": "aifoundry3", "aifoundry1-c1": "aifoundry1c1"}
KEYS = ("D_FL1", "D_E60", "R", "R_raw", "rise")


def k21(T):
    return 23.257 / 36.0 * math.exp((T - 80.0) / 36.0)


def lowpass(t, x, tau):
    y = [x[0]]
    for i in range(1, len(x)):
        a = 1.0 - math.exp(-(t[i] - t[i - 1]) / tau)
        y.append(y[-1] + a * (x[i] - y[-1]))
    return y


def wmean(t, x, lo, hi):
    v = [b for a, b in zip(t, x) if lo <= a <= hi]
    return (sum(v) / len(v), len(v)) if v else (None, 0)


def extras(d, ac, card, q):
    tel, runs = r1.jl(os.path.join(d, "telemetry.jsonl")), r1.jl(os.path.join(d, "runs.jsonl"))
    if len(tel) < 50 or not runs:
        return {}
    res = ac.bursts_of(tel, runs)
    bursts, arrays, spans = res
    t = [float(x) for x in arrays[0]]
    T = [float(x) for x in arrays[2]]
    Tf = lowpass(t, T, TAU.get(card, 1.235))
    los = [s[0] for s in spans]
    out = {}
    for b in bursts:
        lo, hi = b["t_lo"], b["t_hi"]
        i = los.index(lo)
        prev_hi = spans[i - 1][1] if i else t[0]
        ri_lo, ri_hi = max(prev_hi + 3.0, lo - 3.5), lo - 0.3
        tw, nw = wmean(t, T, hi - 0.6, hi)
        ti, ni = wmean(t, T, ri_lo, ri_hi)
        fw, _ = wmean(t, Tf, hi - 0.6, hi)
        fi, _ = wmean(t, Tf, ri_lo, ri_hi)
        rise = b["die_c_busy"] - b["die_c_idle"]
        tmid = 0.5 * (b["die_c_busy"] + b["die_c_idle"])
        rec = {"rise": rise, "D_FL1": b["over_idle_raw_w"] - (2 * q[0] * tmid + q[1]) * rise,
               "D_E60": b["over_idle_raw_w"] - E60_SLOPE * rise if card == "aifoundry3" else None,
               "R_raw": b["rails_over"]["minion_w"]}
        if nw < 1 or ni < 1:
            rec["R"] = None
        else:
            rec["R"] = b["rails_over"]["minion_w"] - C_RB * k21(0.5 * (tw + ti)) * (fw - fi) / REACH
            rec.update({"t_rails_window_c": tw, "t_rails_idle_c": ti, "rise_rails_filtered_c": fw - fi})
        out[b["cfg"]] = rec
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="the card's e180 directory, holding p<P>/")
    ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    ap.add_argument("--card", default="aifoundry3")
    ap.add_argument("--plan", default=None)
    a = ap.parse_args()
    v1 = a.out + ".v1.json"
    sys.argv = ["reduce_e180.py", "--data", a.data, "--out", v1, "--root", a.root, "--card", a.card] + (["--plan", a.plan] if a.plan else [])
    r1.main()
    red = json.load(open(v1))
    os.remove(v1)
    q = json.load(open(os.path.join(a.root, "tools/claims-v3/footing-law/footing-law.json")))["laws"][LAWKEY.get(a.card, "aifoundry3")]["quad_w"]
    ac = r1.analyzer(a.root)
    red["v2"] = {"what": "reduce_e180_v2.py: v1's reduction unchanged, plus A1 section 4.1's per-burst readings", "card": a.card,
                 "footing_law_quad_w": q, "rail_tau_s": TAU.get(a.card, 1.235), "c_rb": C_RB, "reach": REACH, "e60_slope": E60_SLOPE}
    for group in ("passes", "set_aside"):
        for p, rec in red[group].items():
            ex = extras(os.path.join(a.data, f"p{p}"), ac, a.card, q)
            rec["runs_v2"], rec["v2_unread"] = {}, []
            for key in KEYS:
                rec[key] = {}
            for k, runs in rec.get("runs", {}).items():
                vals = []
                for r in runs:
                    e = ex.get(r["cfg"])
                    if e is None or e["R"] is None:
                        rec["v2_unread"].append(r["cfg"])
                    if e is not None:
                        vals.append(e)
                rec["runs_v2"][k] = vals
                for key in KEYS:
                    xs = [e[key] for e in vals if e.get(key) is not None]
                    if xs:
                        rec[key][k] = st.mean(xs)
    json.dump(red, open(a.out, "w"), indent=1, sort_keys=True)
    n_unread = sum(len(v["v2_unread"]) for g in ("passes", "set_aside") for v in red[g].values())
    print(f"v2: the per-burst readings added for {len(red['passes'])} kept passes; bursts v2 could not read: {n_unread}")


if __name__ == "__main__":
    main()
