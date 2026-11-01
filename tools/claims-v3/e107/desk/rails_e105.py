#!/usr/bin/env python3
"""Desk check before E107's registration (Sun 1 Nov 2026, Q133): on E105's and E101's committed aifoundry3 passes, the rails over the idle just before each
run (window [t0+2 s, t0+4 s) against [t0-1.5 s, t0-0.1 s)), per op, nJ; t0 = the run's first launch record. Raw readings, no lag model, so the minion
column is not reduce_e78.py's and runs negative on zeros. What it showed, and why R4c reads the DDR voltage: the cold 16-block walk droops the DDR rail
1.9-3.5 mV, the L3-fed packed gemm1 0.5-1.0 mV, the resident loop about 0. Run: python3 rails_e105.py > rails_e105.txt"""
import gzip, json, os, statistics as st, sys
from collections import defaultdict
L = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "docs", "reports", "data")
dirs = {"e105c": [f"{L}/2026-11-01-e105-gemm-layout/aifoundry3/kinds-e105c/p10520", f"{L}/2026-11-01-e105-gemm-layout/aifoundry3/kinds-e105c/p10522"],
        "e101": [f"{L}/2026-11-01-e101-real-matmul/aifoundry3/kinds/p1011{i}" for i in range(4)]}
out = defaultdict(list)
for tag, ds in dirs.items():
    for d in ds:
        tel = []
        for ln in gzip.open(f"{d}/telemetry.jsonl.gz", "rt"):
            if not ln.startswith("{"):
                continue
            try:
                x = json.loads(ln)
            except ValueError:
                continue
            sp = x.get("sp") or {}
            g = lambda k: (sp.get(k) or [None])[0]
            tel.append((x["t_ms"], x.get("board_w"), g("minion_w"), g("sram_w"), g("noc_w"), (x.get("die_mv") or {}).get("ddr")))
        tel.sort()
        runs = defaultdict(list)
        for ln in open(f"{d}/runs.jsonl"):
            r = json.loads(ln)
            if r.get("test") == "fma" and r.get("launch", -9) >= -1:
                runs[(r["pos"], r["item"])].append(r)
        for (pos, item), rr in runs.items():
            if not any(item.startswith(p) for p in ("gemm1.", "gemm16.", "fp32.", "int8.", "fp16.")):
                continue
            rr.sort(key=lambda r: r["t_start_ms"])
            t0 = rr[0]["t_start_ms"]
            w = [s for s in tel if t0 + 2000 <= s[0] < t0 + 4000]
            i = [s for s in tel if t0 - 1500 <= s[0] < t0 - 100]
            if len(w) < 5 or len(i) < 5:
                continue
            wl = [r for r in rr if r["launch"] >= 0]
            rate = sum(r["iters"] for r in wl) * wl[0]["minions"] / sum(r["wall_s"] for r in wl)
            dv = [st.mean(s[k] for s in w if s[k] is not None) - st.mean(s[k] for s in i if s[k] is not None) for k in (1, 2, 3, 4, 5)]
            rem = dv[0] - dv[1] - dv[2] - dv[3]
            out[(tag, item)].append((rate, *dv, rem))
print("arm/item              n  T600us  boardS  minion   sram    noc  remain | nJ/op: board minion sram noc remain | ddr mV")
for k in sorted(out):
    v = out[k]
    m = [st.mean(x[j] for x in v) for j in range(7)]
    rate = m[0]
    T = 1024 / rate * 1e6
    nj = [x / rate * 1e9 for x in (m[1], m[2], m[3], m[4], m[6])]
    print(f"{k[0]:5s} {k[1]:20s} {len(v):2d} {T:6.3f} {m[1]:7.2f} {m[2]:7.2f} {m[3]:6.2f} {m[4]:6.2f} {m[6]:7.2f} | {nj[0]:6.2f} {nj[1]:6.2f} {nj[2]:5.2f} {nj[3]:5.2f} {nj[4]:6.2f} | {m[5]:+.2f}")
