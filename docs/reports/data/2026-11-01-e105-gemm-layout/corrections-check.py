#!/usr/bin/env python3
"""E105's corrections after verification (Sun 1 Nov 2026): every number in the README's section "Corrections after verification" that this directory's files can give, recomputed from them. Standard library only. Writes nothing.

    python3 corrections-check.py > corrections-check.txt
"""
import gzip
import json
import math
import os
import re
import statistics as st
from collections import defaultdict

D = os.path.dirname(os.path.abspath(__file__))
RD = f"{D}/aifoundry2/s1"
R = json.load(open(f"{D}/results-speed.json"))
P = json.load(open(f"{D}/scored-p.json"))
E101 = json.load(open(f"{D}/../2026-11-01-e101-real-matmul/e101.json"))["items"]
REG = json.load(open(f"{D}/../../../../tools/claims-v3/kinds/predictions-e101.json"))["clock"]["relation"]
ADM = json.load(open(f"{D}/aifoundry2/admission.json"))
CELLS, G = R["cells"], R["gaps"]
runs = [json.loads(x) for x in open(f"{RD}/runs.jsonl")]
procs = defaultdict(list)
for ln in gzip.open(f"{RD}/launches.jsonl.gz", "rt"):
    d = json.loads(ln)
    if d.get("role") == "work":
        procs[d["run"]].append(d)


def tel(run):
    out = []
    for ln in gzip.open(f"{RD}/tel/{run}.jsonl.gz", "rt"):
        if ln.startswith("{"):
            try:
                d = json.loads(ln)
            except ValueError:
                continue
            sp = d.get("sp") or {}
            f = lambda k: (sp.get(k) or [None])[0]
            ms = (d.get("temp_c") or {}).get("minshire") or [None]
            out.append({"t": d["t_ms"], "w": d.get("board_w"), "mhz": (d.get("mhz") or {}).get("minion"), "minion": f("minion_w"), "sram": f("sram_w"), "noc": f("noc_w"), "die": ms[0]})
    return sorted(out, key=lambda x: x["t"])


def base(lab):
    return re.sub(r"-rep\d+$", "", lab)


def key_of(lab):
    p = base(lab).split("-")
    return f"{p[0]}.{p[1]}" + (".half" if lab.endswith("-half") else ""), "-".join(p[2:])


def line(rows):
    n = len(rows)
    xs = [1.0 / f for f, _ in rows]
    ys = [t for _, t in rows]
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    C = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return C, my - C * mx


allrows = defaultdict(list)
pure = defaultdict(lambda: defaultdict(list))
perrun = defaultdict(dict)
passes = defaultdict(list)
for r in runs:
    run, lab = r["run"], r["label"]
    if lab == "rest" or run not in procs:
        continue
    key, kind = key_of(lab)
    s = tel(run)
    rows = []
    for p in procs[run]:
        for k in p.get("sparsity", []):
            if k.get("test") == "fma" and k.get("launch", 0) >= 0 and k.get("ok") and k.get("wall_s", 0) >= 0.1 and k.get("iters") and k.get("cycles_max"):
                f, T = k["cycles_max"] / k["wall_s"] / 1e6, k["wall_s"] / k["iters"] * 1e6
                if 590 < f < 810:
                    rows.append((f, T))
                    allrows[key].append((f, T))
                    passes[key].append(k.get("passes", 0))
                    smp = [x["mhz"] for x in s if k["t_start_ms"] <= x["t"] <= k["t_end_ms"]]
                    if smp and len(set(smp)) == 1 and abs(f - smp[0]) < 1.5 and smp[0] in (600, 700, 800):
                        pure[key][smp[0]].append(T)
    if rows and max(f for f, _ in rows) - min(f for f, _ in rows) > 100:
        perrun[key][run.split("-")[0] + "-" + run.split("-")[1]] = line(rows)

print("C1. Passes over one block per launch, in the arms that repeat one block, from the launch records (`passes`): the same loop, the same ops; only the addresses differ")
for key in ("gemm1.fp32", "gemmv1.fp32", "gemmc1.fp32", "gemmc1.int8"):
    x = sorted(passes[key])
    print(f"  {key}: median {st.median(x):.0f}, range {x[0]}-{x[-1]}")
print("  the 16-block arms:", {k: (min(passes[k]), max(passes[k])) for k in ("gemmc16.fp32", "gemmv16.fp32")})

print("\nC2. Launches wholly at one clock level (every sample in the launch agrees, and the kernel's own clock within 1.5 MHz): T, us; what x1.333 of clock buys; per-run C (runs with more than 100 MHz of span)")
for key in sorted(pure):
    lv = pure[key]
    a, b = lv.get(600, []), lv.get(800, [])
    if a and b:
        ra = st.mean(a) / st.mean(b)
        cs = sorted(c for c, _ in perrun[key].values())
        print(f"  {key:18s} at 600: n {len(a):3d} T {st.mean(a):.4f}; at 800: n {len(b):3d} T {st.mean(b):.4f}; at 700: n {len(lv.get(700, []))}; x1.333 of clock buys x{ra:.3f}; per-run C {cs[0]:.0f}-{cs[-1]:.0f} over {len(cs)} runs")
print("  all launches:", {k: len(v) for k, v in allrows.items()})
lowc = {k: sum(1 for f, _ in allrows[k] if f < 780) for k in allrows}
print("  launches below 780 MHz:", lowc)
print("  cold strides, per-run C and M:", {k: (round(v[0], 1), round(v[1], 3)) for k, v in perrun["gemmv16.fp32"].items()})
print("  E101 to E105, the same arm's C: 344.3 (the verifier's fit of E101), ", R["fits"]["gemm1.fp32"]["C"], "with a printed +-", R["fits"]["gemm1.fp32"]["C_ci"])
Tm = {k: st.mean(pure[k][800]) for k in pure if pure[k].get(800)}
print(f"  the rate by column over strides at 800 MHz: x{CELLS['gemmc1-fp32-zeros']['burst_rate'] / CELLS['gemmv1-fp32-sparse50']['burst_rate']:.2f}")

print("\nC2. The NoC rail per op over the idle just before the run, 2-4 s after the first launch began (post hoc), nJ")
noc = defaultdict(list)
for r in runs:
    run, lab = r["run"], r["label"]
    if lab == "rest" or run not in procs:
        continue
    key, kind = key_of(lab)
    if key.endswith(".half") or kind not in ("zeros", "randn"):
        continue
    s = tel(run)
    ps = procs[run]
    t0 = min(p["t_start_ms"] for p in ps)
    idle = [x["noc"] for x in s if t0 - 1500 <= x["t"] <= t0 - 100 and x["noc"] is not None]
    win = [x["noc"] for x in s if t0 + 2000 <= x["t"] <= t0 + 4000 and x["noc"] is not None]
    kk = [k for p in ps for k in p.get("sparsity", []) if k.get("test") == "fma" and k.get("t_start_ms") and t0 + 2000 <= k["t_start_ms"] <= t0 + 4000 and k.get("iters")]
    if len(idle) >= 3 and len(win) >= 5 and kk:
        T = sum(k["wall_s"] for k in kk) / sum(k["iters"] for k in kk) * 1e6
        noc[(key, kind)].append((st.mean(win) - st.mean(idle)) * T / kk[0]["minions"] * 1000)
for k in sorted(noc):
    print(f"  {k[0]:14s} {k[1]:6s} {st.mean(noc[k]):5.2f} (n {len(noc[k])})")
bz, br = st.mean(noc[("gemmc1.fp32", "zeros")]), st.mean(noc[("gemmc1.fp32", "randn")])
az, ar = st.mean(noc[("gemm1.fp32", "zeros")]) - bz, st.mean(noc[("gemm1.fp32", "randn")]) - br
for arm in ("gemmv1.fp32", "gemmc16.fp32", "gemmv16.fp32"):
    print(f"  {arm}: over by column's base, as a share of as-run's: zeros {(st.mean(noc[(arm, 'zeros')]) - bz) / az:.2f}, random {(st.mean(noc[(arm, 'randn')]) - br) / ar:.2f}")
F = R["fits"]
print(f"  M per unit of that traffic on zeros, us/nJ: as run {F['gemm1.fp32']['M'] / az:.2f}, strides {F['gemmv1.fp32']['M'] / (st.mean(noc[('gemmv1.fp32', 'zeros')]) - bz):.2f}")
print(f"  cold by column's M over as-run's: x{F['gemmc16.fp32']['M'] / F['gemm1.fp32']['M']:.2f}, on NoC traffic per op of {st.mean(noc[('gemmc16.fp32', 'zeros')]):.2f} against {st.mean(noc[('gemm1.fp32', 'zeros')]):.2f} nJ")

print("\nC3. R8's gap: zeros and random in the cold burst, sampled clock and rate")
for arm in ("gemmc16", "gemmv16"):
    z, x = CELLS[f"{arm}-fp32-zeros"], CELLS[f"{arm}-fp32-randn"]
    print(f"  {arm}: clocks {z['burst_mhz']} and {x['burst_mhz']} MHz, rates {z['burst_rate']} and {x['burst_rate']}; x{z['burst_rate'] / x['burst_rate']:.3f} at clock x{z['burst_mhz'] / x['burst_mhz']:.3f}")

print("\nC4. The cold walk's traffic at 600 MHz, GB/s: per pass, T x 16 blocks x 64 ops per minion; 3 MB of A + B and 2 MB of C per block (strides' B reads the same 1 MB through its 1.08 MB pitch)")
K = 8.372
for name, rate in (("as run, E101", E101["gemm16.fp32.randn"]["rate"]["mean"] * E101["gemm16.fp32.randn"]["macs_per_op"] * 2 / 1e12), ("by column", P["cells"]["gemmc16.fp32.randn"]["rate"]), ("strides", P["cells"]["gemmv16.fp32.randn"]["rate"])):
    T = K / rate
    tp = T * 16 * 64 * 1e-6
    miss = {"as run, E101": 1.0, "by column": 0.667, "strides": 0.802}[name]
    print(f"  {name:13s} T {T:.2f} us; distinct A + B {48e6 * 1.048576 / tp / 1e9:5.1f}; C's stores {32e6 * 1.048576 / tp / 1e9:5.1f}; L2-miss traffic at the desk's {miss:.3f} of 192 lines per shire per op {192 * 64 * 32 * miss / (T * 1e-6) / 1e9:6.1f}")

print("\nC5. The power rule: estimate against the highest board reading of each run (aifoundry2/admission.json)")
seen = ADM["seen"]
over = sorted(((v["peak_w"] - v["est_w"], k) for k, v in seen.items() if v.get("est_w") is not None and v.get("peak_w") is not None), reverse=True)
big = [x for x in over if x[0] >= 3.0]
print(f"  runs {len(over)}; reading above the estimate by 3 W or more on {len(big)}: {big[-1][0]:.2f} to {big[0][0]:.2f} W; the largest: {big[0][1]}")
for run in ("A-11-gemmc1-fp32-randn-r1", "E-04-gemmc1-fp16-randn-r1", "E-05-gemmc1-fp16-randn-r1"):
    s = tel(run)
    t0 = min(p["t_start_ms"] for p in procs[run])
    pk = max(s, key=lambda x: x["w"] or 0)
    print(f"  {run}: estimate {seen[run]['est_w']}; peak {pk['w']} W at {(pk['t'] - t0) / 1000:.1f} s, clock {pk['mhz']} MHz, die {pk['die']} C")
print("  samples over 97 W in any run:", sum(1 for r in runs if r["label"] != "rest" for x in tel(r["run"]) if (x["w"] or 0) > 97))
print(f"  extrapolation: {seen['A-11-gemmc1-fp32-randn-r1']['peak_w']} + ({seen['E-05-gemmc1-fp16-randn-r1']['peak_w']} - {seen['E-04-gemmc1-fp16-randn-r1']['peak_w']}) = {seen['A-11-gemmc1-fp32-randn-r1']['peak_w'] + seen['E-05-gemmc1-fp16-randn-r1']['peak_w'] - seen['E-04-gemmc1-fp16-randn-r1']['peak_w']:.1f} W")
print(f"  P4: the relation on aifoundry3's S: {P['rules']['P4']['p800_w']} W; aifoundry2's measured P_800 {CELLS['gemmc1-fp32-randn']['burst_p800_w_runs']}")

print("\nC6. int8, one relation (E83's, E101's frozen constants) on each arm's own c, against the measured sustained gaps")
B = {int(k): v for k, v in REG["B_registered_w"].items()}
SF = {int(k): v for k, v in REG["s_f"].items()}
Ws, ss = REG["sustained"]["W_star_w"], REG["sustained"]["sigma_w"]


def d3(c, W):
    p6, p7, p8 = B[600] + c * SF[600], B[700] + c * SF[700], B[800] + c * SF[800]
    if W >= p8:
        return 800.0
    if W >= p7:
        return 700.0 + 100.0 * (W - p7) / (p8 - p7)
    if W >= p6:
        return 600.0 + 100.0 * (W - p6) / (p7 - p6)
    return 600.0


def rel(c):
    zs = [-3.0 + 6.0 * i / 40 for i in range(41)]
    w = [math.exp(-z * z / 2) for z in zs]
    return sum(a * d3(c, Ws + ss * z) for a, z in zip(w, zs)) / sum(w)


cz = 2.123
c_res = cz + (E101["int8.full"]["S"]["mean"] - E101["int8.zeros"]["S"]["mean"]) / REG["xfer"]
c_col = CELLS["gemmc1-int8-full"]["c_w"]
for name, c in (("the loop", c_res), ("by column", c_col), ("the benchmark", 26.535)):
    print(f"  {name:14s} c {c:6.2f}: relation's sustained clock {rel(c):6.1f} MHz, zeros / this x{rel(cz + 2) / rel(c):.3f} (zeros at 800)")
print(f"  by column measured: x{G['gemmc1-int8-full']['sus_rate']:.3f} rate; with zeros at its burst rate, {CELLS['gemmc1-int8-zeros']['burst_rate']} TOPS, free of the dips: x{CELLS['gemmc1-int8-zeros']['burst_rate'] / CELLS['gemmc1-int8-full']['sus_rate']:.3f}")
dips = {}
for r in runs:
    if r["label"].startswith("gemmc1-int8-zeros") and r.get("processes", 1) >= 2:
        s = tel(r["run"])
        starts = [p["t_start_ms"] for p in procs[r["run"]]]
        t1 = max(p["t_end_ms"] for p in procs[r["run"]])
        lo = [x for x in s if starts[0] <= x["t"] <= t1 and x["mhz"] and x["mhz"] < 800]
        seg = []
        for x in lo:
            if seg and x["t"] - seg[-1][1] < 500:
                seg[-1][1] = x["t"]
            else:
                seg.append([x["t"], x["t"]])
        # the first process's start-up ramp is not a dip
        dips[r["run"]] = [(round((b - a) / 1000 + 0.1, 1), any(0 <= a - t <= 1500 for t in starts[1:])) for a, b in seg if a - starts[0] > 1500]
print("  zeros' sustained dips:", dips, "total", sum(len(v) for v in dips.values()), "at a process boundary", sum(1 for v in dips.values() for x in v if x[1]))
print("  idle_resets_sus as counted:", CELLS["gemmc1-int8-zeros"]["idle_resets_sus"])

print("\nC8. Gaps on the kernel's own clock (cycles_max / wall), in the reducer's windows (burst from 1.5 s, sustained the last 40 s), beside the sampled clock")


def kclock(lab, sus):
    out = []
    for r in runs:
        if r["label"] != lab and base(r["label"]) != lab:
            continue
        ps = procs[r["run"]]
        is_sus = r.get("processes", 1) >= 2
        if is_sus != sus:
            continue
        t0 = min(p["t_start_ms"] for p in ps)
        t1 = max(p["t_end_ms"] for p in ps)
        kk = [k for p in ps for k in p.get("sparsity", []) if k.get("test") == "fma" and k.get("launch", 0) >= 0 and k.get("t_start_ms") and k["t_start_ms"] >= (t1 - 40000 if sus else t0 + 1500)]
        w = sum(k["wall_s"] for k in kk)
        if w:
            out.append(sum(k["cycles_max"] for k in kk) / w / 1e6)
    return st.mean(out) if out else None


for lab, z, sus in (("gemmc1-fp32-randn", "gemmc1-fp32-zeros", False), ("gemmc1-fp32-sparse25", "gemmc1-fp32-zeros", True), ("gemmc1-fp16-randn", "gemmc1-fp16-zeros", True), ("gemmc1-int8-full", "gemmc1-int8-zeros", True)):
    a, b = kclock(z, sus), kclock(lab, sus)
    g = G[lab]
    tag = "sus" if sus else "burst"
    print(f"  {lab:22s} {tag:5s} rate x{g[tag + '_rate']:.3f}, sampled clock x{g[tag + '_clock']:.3f}, kernel clock x{a / b:.3f}")
print(f"  by column fp32 random, the law's rate at the kernel's clocks: x{(F['gemmc1.fp32']['C'] / kclock('gemmc1-fp32-randn', False) + F['gemmc1.fp32']['M']) / (F['gemmc1.fp32']['C'] / kclock('gemmc1-fp32-zeros', False) + F['gemmc1.fp32']['M']):.3f}")
c = F["gemmc1.fp32"]
print(f"  sustained fp32 random by column, expected, at 800 and 600 MHz by the law: x{(c['C'] / 600 + c['M']) / (c['C'] / 797.7 + c['M']):.3f} (labelled, not measured)")
print("\nThe frozen files are unchanged. score_e105p.py was first committed with the data; its git log says so.")
