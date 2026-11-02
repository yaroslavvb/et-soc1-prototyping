#!/usr/bin/env python3
"""E119 (Q134), POST HOC: written after the session had started and after a look at its first launches; no rule reads it, and every number it prints is
labelled post hoc wherever it is quoted. Standard library only.

    python3 tools/claims-v3/e119/posthoc_e119.py <RUNDIR> [<RUNDIR> ...] --results results.json --out posthoc.json > posthoc.txt

  1. X both ways: the registered launch means and E105's fit T = C/f + M (reduce_e105.fit), side by side, with the clocks the [590, 610] MHz launches
     actually ran at (the window holds launches up to 1.7% above 600 MHz, which reads a clock-following arm's T600 up to that much short).
  2. The walk's extra time over the repeated block at each clock, E(f) = T(f) - T_c1(f), from the launch means: does it stay, shrink or grow with the clock?
  3. The minion spread, cycles_max / cycles_mean per launch, at 600 and at 800 MHz (E107 found x1.142 in c8s at 600 MHz on aifoundry3).
  4. T at 600 MHz across cards: this session's launch means against E107's pinned aifoundry3 T (scored.json `T`).
  5. The kinds table's governed cells: burst and sustained clock, rate, board power and die per arm, format and kind (results.json `cells`).
"""
import argparse
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "kspeed", "e105"))
import reduce_e105 as R105  # noqa: E402

TYPES = ("fp32", "fp16", "int8")
ARMS = ("c1", "c16r32", "c16r8", "c16r4", "c16r2", "c16", "c8s")


def jl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        return [json.loads(x) for x in gzip.open(path + ".gz", "rt")]
    return [json.loads(x) for x in open(path)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--results", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    res = json.load(open(a.results))
    e107 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-01-e107-gemm-placement/scored.json")))["T"]
    rows = {}
    for rd in a.rundirs:
        runs = {r["run"]: r for r in jl(os.path.join(rd, "runs.jsonl"))}
        for L in jl(os.path.join(rd, "launches.jsonl")):
            r = runs.get(L["run"])
            if not r or L.get("role") != "work" or r["block"] == "SMOKE":
                continue
            lab = r["label"].replace("-rep2", "")
            arm, t, k = lab.split("-", 2)
            for s in L.get("sparsity", []):
                if s.get("test") == "fma" and s.get("launch", 0) >= 0 and s.get("ok") and s.get("wall_s", 0) >= 0.1 and s.get("iters"):
                    f = s["cycles_max"] / s["wall_s"] / 1e6
                    T = s["wall_s"] / s["iters"] * 1e6
                    spread = s["cycles_max"] / s["cycles_mean"] if s.get("cycles_mean") else None
                    rows.setdefault(f"{arm}.{t}", []).append((f, T, spread, k))
    out = {"what": "E119 post hoc (labelled): X both ways, the walk's extra time at each clock, the minion spread, T600 across cards, the governed cells", "arms": {}}
    print("POST HOC, labelled. Per arm and format: X by the registered launch means and by E105's fit; the [590, 610] launches' clocks; E(f) = T(f) - T_c1(f); spread")
    print(f"{'arm.format':13s} {'X means':>8s} {'X fit':>7s} {'f600 mean':>9s} {'n600':>4s} {'T600':>7s} {'E107 T600':>9s} {'a2/a3':>6s} {'T800':>7s} {'E600':>7s} {'E800':>7s} {'E800/E600':>9s} {'spr600':>7s} {'spr800':>7s}")
    per = {}
    for key in sorted(rows):
        rr = rows[key]
        lo = [(f, T, sp) for f, T, sp, _ in rr if 590 <= f <= 610]
        hi = [(f, T, sp) for f, T, sp, _ in rr if f >= 790]
        fit = R105.fit([(f, T) for f, T, _, _ in rr if 590 < f < 810])
        t6 = sum(T for _, T, _ in lo) / len(lo) if lo else None
        t8 = sum(T for _, T, _ in hi) / len(hi) if hi else None
        f6 = sum(f for f, _, _ in lo) / len(lo) if lo else None
        xf = (fit["C"] / 600 + fit["M"]) / (fit["C"] / 800 + fit["M"]) if fit and fit.get("C") is not None else None
        sp6 = [sp for _, _, sp in lo if sp]
        sp8 = [sp for _, _, sp in hi if sp]
        per[key] = {"T600_means": t6, "n600": len(lo), "f600_mean": f6, "T800_means": t8, "n800": len(hi), "X_means": (t6 / t8) if t6 and t8 else None,
                    "fit": fit, "X_fit": xf, "T600_fit": (fit["C"] / 600 + fit["M"]) if xf else None, "T800_fit": (fit["C"] / 800 + fit["M"]) if xf else None,
                    "spread600": (sum(sp6) / len(sp6)) if sp6 else None, "spread800": (sum(sp8) / len(sp8)) if sp8 else None, "T600_e107_a3": e107.get(key)}
    for key, v in per.items():
        arm, t = key.split(".")
        c1 = per.get(f"c1.{t}") or {}

        def best(d, which):
            return d.get(f"T{which}_means") if d.get(f"T{which}_means") is not None else d.get(f"T{which}_fit")
        e6 = (best(v, 600) - best(c1, 600)) if best(v, 600) is not None and best(c1, 600) is not None else None
        e8 = (best(v, 800) - best(c1, 800)) if best(v, 800) is not None and best(c1, 800) is not None else None
        v.update({"E600": e6, "E800": e8, "E800_over_E600": (e8 / e6) if e6 and e8 and arm != "c1" else None,
                  "a2_over_a3_T600": (best(v, 600) / v["T600_e107_a3"]) if best(v, 600) and v["T600_e107_a3"] else None})

    def f_(x, n=4, w=7):
        return f"{x:{w}.{n}f}" if isinstance(x, (int, float)) else f"{'-':>{w}s}"
    for key, v in per.items():
        print(f"{key:13s} {f_(v['X_means'], 3, 8)} {f_(v['X_fit'], 3)} {f_(v['f600_mean'], 1, 9)} {v['n600']:4d} {f_(v['T600_means'])} {f_(v['T600_e107_a3'], 4, 9)} "
              f"{f_(v['a2_over_a3_T600'], 4, 6)} {f_(v['T800_means'])} {f_(v['E600'])} {f_(v['E800'])} {f_(v['E800_over_E600'], 3, 9)} {f_(v['spread600'], 3)} {f_(v['spread800'], 3)}")
    out["arms"] = per
    cells = {}
    for lab, c in res["cells"].items():
        cells[lab] = {k: c.get(k) for k in ("burst_mhz", "burst_rate", "burst_w", "sus_mhz", "sus_rate", "sus_w", "sus_die", "n_burst", "n_sus", "sus_limit_runs", "idle_resets_burst", "idle_resets_sus")}
        cells[lab]["burst_die_max"] = max([x for x in (c.get("burst_die_max") or []) if x is not None], default=None)
        cells[lab]["burst_p800_w"] = max([x for x in (c.get("burst_p800_w_runs") or []) if x is not None], default=None)
    out["cells"] = cells
    print("\nPOST HOC, labelled. The governed cells (results.json cells): burst clock, rate, board W, die max; sustained clock, rate, board W, die; limit")
    for lab, c in cells.items():
        print(f"  {lab:24s} burst {f_(c['burst_mhz'], 1, 6)} MHz {f_(c['burst_rate'], 3, 8)} {f_(c['burst_w'], 1, 5)} W {f_(c['burst_die_max'], 0, 3)} C | "
              f"sus {f_(c['sus_mhz'], 1, 6)} MHz {f_(c['sus_rate'], 3, 8)} {f_(c['sus_w'], 1, 5)} W {f_(c['sus_die'], 1, 5)} C {c.get('sus_limit_runs')}")
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
