#!/usr/bin/env python3
"""E136: the headline re-derived from the raw records with code of its own (post hoc, labelled; it decides nothing). It does not import any of the lab's
reducers: it reads aifoundry2/s1/runs.jsonl, launches.jsonl.gz and tel/*.jsonl.gz directly. Standard library only.

    python3 docs/reports/data/2026-11-02-e136-large-gemm/rederive_e136.py > docs/reports/data/2026-11-02-e136-large-gemm/rederive.txt

Per GEMM and format: T at 800 MHz = wall / ops per minion over the work launches (launch >= 0, ok, wall >= 0.1 s) whose kernel clock (cycles_max /
wall) reads >= 790 MHz, every kind pooled; T at 600 MHz the same over 590-610 MHz. Per run, from the sampler: a burst's mean clock, mean board W and
the die mean's highest reading over its work window (first work launch start to last work launch end); a sustained run's the same over the last 40 s of
its work window, and its rate from the work launches that start inside that window (ops / wall, 2 x MACs x 1,024 minions a op).
"""
import glob
import gzip
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.join(HERE, "aifoundry2", "s1")
MACS = {"fp32": 4096, "fp16": 8192, "int8": 16384}
P = json.load(open(os.path.join(HERE, "..", "..", "..", "..", "tools", "claims-v3", "e136", "predictions-e136.json")))


def jl(p):
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt") as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith("{"):
                try:
                    yield json.loads(ln)
                except ValueError:
                    pass


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def main():
    runs = {r["run"]: r for r in jl(os.path.join(RD, "runs.jsonl"))}
    launches = {}
    for L in jl(os.path.join(RD, "launches.jsonl.gz")):
        if L.get("role") == "work":
            launches.setdefault(L["run"], []).append(L)
    Trows = {}
    out = {"per_gemm": {}, "runs": {}}
    for name, r in runs.items():
        lab = r["label"]
        g, t, k = lab.split("-", 2)
        ks = []
        for L in launches.get(name, []):
            for s in L.get("sparsity", []):
                if s.get("test") == "fma" and s.get("launch", -1) >= 0 and s.get("ok") and s.get("wall_s", 0) >= 0.1 and s.get("iters"):
                    f = s["cycles_max"] / s["wall_s"] / 1e6
                    T = s["wall_s"] / s["iters"] * 1e6
                    Trows.setdefault(f"{g}.{t}", []).append((f, T))
                    ks.append((s["t_start_ms"], s["t_end_ms"], s["iters"], s["wall_s"], f))
        if not ks:
            continue
        w0, w1 = min(x[0] for x in ks), max(x[1] for x in ks)
        sus = r.get("processes", 1) >= 2
        if sus:
            w0 = max(w0, w1 - 40000)
        tel = list(jl(os.path.join(RD, r["tel"] + ".gz"))) if os.path.exists(os.path.join(RD, r["tel"] + ".gz")) else list(jl(os.path.join(RD, r["tel"])))
        win = [d for d in tel if w0 <= d["t_ms"] <= w1]
        pre = [d for d in tel if d["t_ms"] < min(x[0] for x in ks)]
        mhz = mean([(d.get("mhz") or {}).get("minion") for d in win])
        bw = mean([d.get("board_w") for d in win])
        die = [((d.get("temp_c") or {}).get("minshire") or [None])[0] for d in win]
        die = [x for x in die if x is not None]
        start = ((pre[-1].get("temp_c") or {}).get("minshire") or [None])[0] if pre else None
        inw = [x for x in ks if x[0] >= w0]
        rate = 2.0 * MACS[t] * 1024 * sum(x[2] for x in inw) / sum(x[3] for x in inw) / 1e12 if inw else None
        out["runs"][name] = {"label": lab, "mode": "sus" if sus else "burst", "mhz": None if mhz is None else round(mhz, 1), "board_w": None if bw is None else round(bw, 2),
                             "die_mean_c": None if not die else round(sum(die) / len(die), 2), "die_max_c": None if not die else max(die), "die_start_c": start,
                             "rate": None if rate is None else round(rate, 3), "n_tel": len(win)}
    for key, rows in sorted(Trows.items()):
        hi = [T for f, T in rows if f >= 790]
        lo = [T for f, T in rows if 590 <= f <= 610]
        g, t = key.split(".")
        rec = {"T800": None if not hi else round(mean(hi), 4), "n800": len(hi), "T600": None if not lo else round(mean(lo), 4), "n600": len(lo)}
        if hi:
            sd = math.sqrt(sum((x - mean(hi)) ** 2 for x in hi) / max(1, len(hi) - 1))
            rec["T800_sd"] = round(sd, 4)
            lw = P["laws"][key]
            rec["T800_P1"] = lw["P1"]["T800_us"]
            rec["err_P1"] = round(rec["T800"] / lw["P1"]["T800_us"] - 1, 4)
            if "P2" in lw:
                rec["h"] = round((rec["T800"] - lw["P2"]["T800_us"]) / (lw["P1"]["T800_us"] - lw["P2"]["T800_us"]), 3)
        if hi and lo:
            rec["X"] = round(rec["T600"] / rec["T800"], 4)
        out["per_gemm"][key] = rec
    json.dump(out, open(os.path.join(HERE, "rederive.json"), "w"), indent=1)
    print("E136, re-derived from the raw records (post hoc, labelled; independent code)")
    for k, v in out["per_gemm"].items():
        print(f"  {k:10s} T800 {v['T800']} (n {v['n800']}, sd {v.get('T800_sd')}) T600 {v['T600']} (n {v['n600']}) X {v.get('X')}  P1 {v.get('T800_P1')} err {v.get('err_P1')} h {v.get('h')}")
    for n, v in out["runs"].items():
        print(f"  {n:34s} {v['mode']:5s} {v['mhz']} MHz {v['board_w']} W die mean {v['die_mean_c']} max {v['die_max_c']} start {v['die_start_c']} rate {v['rate']} (n {v['n_tel']})")


if __name__ == "__main__":
    main()
