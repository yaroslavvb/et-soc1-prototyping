#!/usr/bin/env python3
"""E107's rails (registered with E107.md): per run, the SP's SRAM and NoC rails, the board, and the DDR rail's die voltage over the idle just before the run, in
the window E105's verifier used for the NoC rail: [t0+2 s, t0+4 s) against [t0-1.5 s, t0-0.1 s), t0 the run's first launch record. Raw readings, no lag model
(reduce_e78.py deconvolves the minion rail; these two rails and the DDR voltage are read as they come). Per (pass, item) the mean over its runs, then over
passes the mean, SE and a 95% t interval, the pass the unit. Standard library only.

    python3 tools/claims-v3/e107/rails_e107.py <pass dir> [...] --out rails-e107.json

Per item: d_board_w, d_sram_w, d_noc_w, ddr_droop_mv (idle minus window: positive is a droop), and per op (the run's own rate) sram_nj_op, noc_nj_op.
"""
import argparse
import gzip
import json
import math
import os
import statistics as st
from collections import defaultdict

T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}


def mci(v):
    v = [x for x in v if x is not None]
    if not v:
        return {"mean": None, "se": None, "n": 0, "ci95": None}
    m = st.mean(v)
    if len(v) < 2:
        return {"mean": m, "se": None, "n": 1, "ci95": None}
    se = st.stdev(v) / math.sqrt(len(v))
    return {"mean": m, "se": se, "n": len(v), "ci95": se * T95.get(len(v) - 1, 2.0)}


def load(d):
    p = os.path.join(d, "telemetry.jsonl.gz")
    op = gzip.open if os.path.exists(p) else open
    p = p if os.path.exists(p) else os.path.join(d, "telemetry.jsonl")
    tel = []
    for ln in op(p, "rt"):
        if not ln.startswith("{"):
            continue
        try:
            x = json.loads(ln)
        except ValueError:
            continue
        sp = x.get("sp") or {}
        g = lambda k: (sp.get(k) or [None])[0]
        tel.append((x["t_ms"], x.get("board_w"), g("sram_w"), g("noc_w"), (x.get("die_mv") or {}).get("ddr")))
    tel.sort()
    return tel


def wm(tel, lo, hi, k):
    v = [s[k] for s in tel if lo <= s[0] < hi and s[k] is not None]
    return (st.mean(v), len(v)) if v else (None, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    per = defaultdict(lambda: defaultdict(list))      # item -> pass -> [run dicts]
    for d in a.dirs:
        tel = load(d)
        runs = defaultdict(list)
        for ln in open(os.path.join(d, "runs.jsonl")):
            r = json.loads(ln)
            if r.get("test") == "fma":
                runs[(r["block"], r["pos"], r["item"], r.get("attempt", 1))].append(r)
        for (blk, pos, item, att), rr in runs.items():
            rr.sort(key=lambda r: r["t_start_ms"])
            t0 = rr[0]["t_start_ms"]
            wl = [r for r in rr if r.get("launch", -9) >= 0 and r["t_start_ms"] < t0 + 4000 and r["t_end_ms"] > t0 + 2000]
            if not wl:
                continue
            rate = sum(r["iters"] for r in wl) * wl[0].get("minions", 1024) / sum(r["wall_s"] for r in wl)
            row = {}
            for k, name in ((1, "board"), (2, "sram"), (3, "noc"), (4, "ddr")):
                w, nw = wm(tel, t0 + 2000, t0 + 4000, k)
                i, ni = wm(tel, t0 - 1500, t0 - 100, k)
                row[name] = None if w is None or i is None or nw < 5 or ni < 5 else w - i
            per[item][blk].append({"rate": rate, **row})
    out = {}
    for item, bypass in sorted(per.items()):
        pv = defaultdict(list)
        for blk, rows in bypass.items():
            m = lambda k: st.mean([r[k] for r in rows if r[k] is not None]) if any(r[k] is not None for r in rows) else None
            rate = st.mean(r["rate"] for r in rows)
            b, s, n, dd = m("board"), m("sram"), m("noc"), m("ddr")
            pv["d_board_w"].append(b)
            pv["d_sram_w"].append(s)
            pv["d_noc_w"].append(n)
            pv["ddr_droop_mv"].append(None if dd is None else -dd)
            pv["sram_nj_op"].append(None if s is None else s / rate * 1e9)
            pv["noc_nj_op"].append(None if n is None else n / rate * 1e9)
            pv["T_us_launch"].append(1024 / rate * 1e6)
        out[item] = {k: mci(v) for k, v in pv.items()}
    json.dump({"experiment": "E107", "window": "[t0+2 s, t0+4 s) against [t0-1.5 s, t0-0.1 s)", "items": out}, open(a.out, "w"), indent=1)
    print(f"rails: {len(out)} items from {len(a.dirs)} passes -> {a.out}")


if __name__ == "__main__":
    main()
