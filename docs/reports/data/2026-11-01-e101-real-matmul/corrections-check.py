#!/usr/bin/env python3
"""E101's corrections after verification (Sun 1 Nov 2026): every number in the README's section "Corrections after verification", recomputed from this directory's committed files. Standard library only. Writes nothing.

    python3 corrections-check.py > corrections-check.txt
"""
import glob
import gzip
import json
import math
import os

D = os.path.dirname(os.path.abspath(__file__))
E = json.load(open(f"{D}/e101.json"))["items"]
R = json.load(open(f"{D}/results-speed.json"))
CELLS = R["cells"]


def fit(rows):
    n = len(rows)
    xs = [1.0 / f for f, _ in rows]
    ys = [t for _, t in rows]
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    C = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    M = my - C * mx
    res = [y - (C * x + M) for x, y in zip(xs, ys)]
    s2 = sum(r * r for r in res) / (n - 2)
    return C, 1.96 * math.sqrt(s2 / sxx), M, 1.96 * math.sqrt(s2 * (1.0 / n + mx * mx / sxx)), 1000 * math.sqrt(sum(r * r for r in res) / n)


print("C1. T = C/f + M, on session 2's launches on aifoundry2 (aifoundry2/s1/launches.jsonl.gz): T = wall / ops per minion, f = cycles_max / wall, launches of at least 0.1 s between 590 and 810 MHz")
rows = {}
for ln in gzip.open(f"{D}/aifoundry2/s1/launches.jsonl.gz", "rt"):
    d = json.loads(ln)
    if d.get("role") != "work":
        continue
    parts = d["run"].split("-")
    lab = parts[2] if len(parts) > 3 else None
    if lab not in ("gemm1", "mm16", "res"):
        continue
    for k in d.get("sparsity", []):
        if k.get("test") == "fma" and k.get("launch", 0) >= 0 and k.get("wall_s", 0) >= 0.1 and k.get("iters") and k.get("cycles_max"):
            f = k["cycles_max"] / k["wall_s"] / 1e6
            if 590 < f < 810:
                rows.setdefault((lab, parts[3]), []).append((f, k["wall_s"] / k["iters"] * 1e6))
FITS = {}
for key in sorted(rows):
    if len(rows[key]) >= 3 and max(f for f, _ in rows[key]) - min(f for f, _ in rows[key]) > 1:
        C, cc, M, cm, rms = fit(rows[key])
        FITS[key] = (C, M)
        print(f"  {key[0]:6s} {key[1]:5s} n {len(rows[key]):4d}  C {C:7.1f} +- {cc:4.1f} cycles  M {M:6.3f} +- {cm:.3f} us  rms {rms:.1f} ns")
for key, zc, rc, gm in ((("gemm1", "fp32"), "gemm1-fp32-zeros", "gemm1-fp32-randn", "sus"), (("gemm1", "fp16"), "gemm1-fp16-zeros", "gemm1-fp16-randn", "sus"), (("gemm1", "fp32"), "gemm1-fp32-zeros", "gemm1-fp32-randn", "burst")):
    C, M = FITS[key]
    fz, fr = CELLS[zc][f"{gm}_mhz"], CELLS[rc][f"{gm}_mhz"]
    pred = (C / fr + M) / (C / fz + M)
    meas = CELLS[zc][f"{gm}_rate"] / CELLS[rc][f"{gm}_rate"]
    print(f"  {key[1]} {gm}: clocks {fz} and {fr} MHz; the law gives x{pred:.3f}, measured x{meas:.3f}")
C, M = FITS[("gemm1", "fp32")]
print(f"  M's share of the wall per op: {M / (C / 600 + M) * 100:.0f}% at 600 MHz, {M / (C / 800 + M) * 100:.0f}% at 800 MHz")
print("  the desk L2 model's miss shares: tools/claims-v3/kspeed/e105/desk/l2sim2.txt")

def rate(c):
    return E[c]["rate"]["mean"] * E[c]["macs_per_op"] * 2 / 1e12


print("C2. Energy per op, random, int8, nJ (e101.json items.<cell>.pj_op_S): gemm1", round(E["gemm1.int8.full"]["pj_op_S"]["mean"] / 1000, 2), "mm16", round(E["mm16.int8.full"]["pj_op_S"]["mean"] / 1000, 2),
      "; rate, T(FL)OP/s: gemm1", round(rate("gemm1.int8.full"), 2), "mm16", round(rate("mm16.int8.full"), 2), "ratio", round(rate("mm16.int8.full") / rate("gemm1.int8.full"), 2))

print("C3. Runs per pass, and the skipped one:")
total = 0
for d in sorted(glob.glob(f"{D}/aifoundry3/kinds/p1011[0-3]")):
    n = len({(r["pos"], r["item"]) for r in map(json.loads, open(f"{d}/runs.jsonl"))})
    total += n
    skipped = [json.loads(x) for x in open(f"{d}/marks.jsonl") if '"skipped"' in x]
    print(f"  {os.path.basename(d)}: {n} runs; skipped marks: {[(s.get('item') or s.get('detail'), str(s.get('why') or s.get('detail'))[:70]) for s in skipped]}")
print(f"  total runs {total}, of 4 x 78 = {4 * 78} planned")

print("C4. n behind each speed gap (results-speed.json cells.<cell>.n_burst, n_sus; burst rates per run):")
for c in ("gemm1-fp32-zeros", "gemm1-fp32-randn", "gemm1-fp16-zeros", "gemm1-fp16-randn", "gemm1-int8-zeros", "gemm1-int8-full", "mm16-int8-zeros", "mm16-int8-full", "res-fp32-zeros", "res-fp32-randn"):
    x = CELLS[c]
    print(f"  {c:20s} burst n {x['n_burst']} runs {x.get('burst_rate_runs')}, sustained n {x['n_sus']}")
z, r = CELLS["gemm1-fp32-zeros"]["burst_rate_runs"], CELLS["gemm1-fp32-randn"]["burst_rate_runs"]
pairs = sorted(a / b for a in z for b in r)
print(f"  gemm1 fp32 burst pairs: x{pairs[0]:.3f} to x{pairs[-1]:.3f}")
print("  sustained cells with n = 1:", sum(1 for x in CELLS.values() if x["n_sus"] == 1), "of", sum(1 for x in CELLS.values() if x["n_sus"]))

print("C6. The rate past the L3, fp32, TFLOPS at 600 MHz:", round(rate("gemm1.fp32.randn"), 2), round(rate("gemm16.fp32.randn"), 2), "ratio", round(rate("gemm1.fp32.randn") / rate("gemm16.fp32.randn"), 2))


def share(a, t, top):
    z, x = E[f"{a}.{t}.zeros" if a else f"{t}.zeros"]["S"], E[f"{a}.{t}.{top}" if a else f"{t}.{top}"]["S"]
    v = z["mean"] / x["mean"]
    hz, hx = z.get("ci95") or 0, x.get("ci95") or 0
    return v, v * math.sqrt((hz / z["mean"]) ** 2 + (hx / x["mean"]) ** 2), hz, hx


print("C7. Zeros / random, watts, this session (half widths propagated from the items' 95% half widths, not paired):")
for a in (None, "mm16", "gemm1"):
    for t, top in (("fp32", "randn"), ("fp16", "randn"), ("int8", "full")):
        v, h, _, _ = share(a, t, top)
        print(f"  {a or 'res':6s} {t}: {v * 100:5.1f} +- {h * 100:.1f} %")
R7 = json.load(open(f"{D}/scored.json"))["rules"]["R7_gate"]
print("  scored.json R7_gate, paired:", R7["R7a"], R7["R7b"], {k: (round(v["share"]["mean"] * 100, 1), round(v["share"]["ci95"] * 100, 1), v.get("res_share_e78")) for k, v in R7["cells"].items()})
print("  worst upper bound on a share:", round(max(v["share"]["hi"] for v in R7["cells"].values()), 3))

print("C10. Lost runs and the highest readings:")
s = [json.loads(x) for x in open(f"{D}/aifoundry2/s1/runs.jsonl")]
sess = json.load(open(f"{D}/aifoundry2/s1/session.json"))
print(f"  planned {len(sess['runs_planned'])}, recorded {len(s)}; first unrecorded {[r for r in sess['runs_planned'] if r not in {x['run'] for x in s}][:1]}")
print("  past the L3, random fp32, pJ per multiply-add:", round(E["gemm16.fp32.randn"]["pj_mac_S"]["mean"], 3))
top = []
for p in sorted(glob.glob(f"{D}/aifoundry2/s1/tel/*.jsonl.gz")):
    vals = []
    for ln in gzip.open(p, "rt"):
        if ln.startswith("{"):
            try:
                j = json.loads(ln)
            except ValueError:
                continue
            if j.get("board_w") is not None:
                vals.append((j["board_w"], j.get("t_ms")))
    if vals:
        top.append((max(v[0] for v in vals), os.path.basename(p)[:-9]))
top.sort(reverse=True)
print("  highest board reading per run:", top[:3])
p = f"{D}/aifoundry2/s1/tel/{top[0][1]}.jsonl.gz"
trip = [json.loads(ln) for ln in gzip.open(p, "rt") if ln.startswith("{") and '"board_w"' in ln]
hi = [j for j in trip if j.get("board_w") == top[0][0]]
print(f"  the {top[0][0]} W reading appears on {len(hi)} consecutive samples, {[j['t_ms'] - hi[-1]['t_ms'] for j in hi]} ms from the last; clocks {[j.get('mhz', {}).get('minion') for j in hi]} MHz, die {hi[-1].get('temp_c', {}).get('minshire', [None])[0]} C")
