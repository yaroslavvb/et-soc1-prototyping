#!/usr/bin/env python3
"""E135: the numbers behind the README's corrections after verification (Mon 2 Nov 2026).

    cd docs/reports/data/2026-11-02-e135-a100-kinds && python3 corrections-check.py > corrections-check.txt

Reads only committed files: this directory's logs/, results.json and posthoc.json; tools/gpu/e135/ (the registered
reducer's loaders, the frozen predictions, the app's plan functions, extracted with ast so that modal is never
imported); and the ET-SoC-1 records the README sets beside the A100 (E105, E119, E126). Standard library only.
It changes no file and scores nothing: every rule verdict stays the registered reducer's."""
import ast
import glob
import gzip
import json
import math
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
TOOLS = os.path.join(LAB, "tools", "gpu", "e135")
DATA = os.path.join(LAB, "docs", "reports", "data")
RUN = os.path.join(HERE, "logs", "e135-20261102-r1")
sys.path.insert(0, TOOLS)
import reduce_e135 as R  # noqa: E402  (the registered reducer: its loaders and windows, unchanged)

res = json.load(open(os.path.join(HERE, "results.json")))
ph = json.load(open(os.path.join(HERE, "posthoc.json")))
units = {u: R.load_unit(os.path.join(RUN, u)) for u in "AB"}
QUIET = {"twos", "zeros", "onebit", "pi"}


def P(*a):
    print(*a)


def gaps(dt, w, size=8192):
    return [g for g in res["gaps"] if g["dtype"] == dt and g["window"] == w and g["cap"] == "default" and g["size"] == size]


# C3: the interval of the bf16 sustained gap, by pass and by board
P("## C3. bf16 8192^3 zeros/randn, sustained: passes, board means, the two intervals")
rep = res["replicates"]["default|8192|bf16|sus"]
by = {}
for g in gaps("bf16", "sus"):
    by.setdefault(g["unit"], []).append(g["gap_rate"])
bm = {u: statistics.mean(v) for u, v in sorted(by.items())}
sd = statistics.stdev(list(bm.values()))
P(f"passes {rep['values']}, mean {rep['mean']:.4f}, pass-level t95 +/-{rep['t95_half']:.4f} (n {rep['n']}, df {rep['n'] - 1})")
P(f"board means {', '.join(f'{u} {v:.4f}' for u, v in bm.items())}; board-level t95 +/-{12.706 * sd / math.sqrt(2):.4f} (n 2, df 1)")

# C9: the digits; the burst's sampled clock ratio against the sustained one
P("\n## C9. gaps by format and window: the rate and the sampled clock ratio (means over passes)")
for dt in ("bf16", "fp16", "tf32", "int8"):
    for w in ("burst", "burst_b", "sus"):
        gg = gaps(dt, w)
        rr, cc = [g["gap_rate"] for g in gg], [g["gap_clock"] for g in gg]
        P(f"{dt} {w}: rate {statistics.mean(rr):.5f}, clock {statistics.mean(cc):.5f}, largest |rate - clock| in one pass "
          f"{max(abs(a - b) for a, b in zip(rr, cc)):.4f} (n {len(gg)})")
P("ladder, unit B, bf16, sustained: " + ", ".join(f"{g['size']}^3 x{g['gap_rate']:.4f}" for g in sorted(
    (g for g in res["gaps"] if g["unit"] == "B" and g["dtype"] == "bf16" and g["window"] == "sus" and g["cap"] == "default"
     and g["pass"] == 1), key=lambda g: g["size"])))

# C5, C7, C12: Horace's loop trial by trial; die means
P("\n## C5, C12. his loop trial by trial (gist6, article9): randn clocks, zeros after randn, die means")
for u in "AB":
    S = units[u]["samples"]
    for lab in ("gist6", "article9"):
        st = next(s for s in units[u]["steps"] if s.get("label") == lab)
        rows = st["rows"]
        sm_all, sm_last, z_rand, z_quiet, die = [], [], [], [], []
        for i, r in enumerate(rows):
            win = [s for s in S if r["t_a"] <= R.tmid(s) < r["t_b"]]
            die += [s["temp"] for s in win if s.get("temp") is not None]
            prev = rows[i - 1]["kind"] if i else None
            if r["kind"] == "zeros" and prev == "randn":
                z_rand.append(round(r["tflops"], 1))
            elif r["kind"] == "zeros" and prev in QUIET:
                z_quiet.append(round(r["tflops"], 1))
            if r["kind"] == "randn" and win:
                sm_all += [s["sm"] for s in win]
                sm_last.append(win[-1]["sm"])
        wall = statistics.median(r["t_b"] - r["t_a"] for r in rows)
        P(f"{u} {lab}: randn trials sample {min(sm_all)}-{max(sm_all)} MHz, last sample of each {min(sm_last)}-{max(sm_last)} MHz; "
          f"zeros after randn {z_rand}, after a quiet kind {min(z_quiet)}-{max(z_quiet)}; die mean {statistics.mean(die):.1f} C; "
          f"trial wall median {wall:.3f} s")
    dm = [res["cells"][f"{u}|default|8192|{dt}|{R.RANDOM_OF[dt]}|1"]["windows"]["sus"]["temp_mean"] for dt in ("bf16", "fp16", "tf32", "int8")]
    P(f"{u} random cells, pass 1, sustained die mean (bf16, fp16, tf32, int8): {[round(x, 1) for x in dm]}")

# C10: the pre-boost readings and the power sensor's update rate
P("\n## C10. the pre-boost readings (pass 1, default cap, 8192^3): loaded samples at the application clock, the boost")
rows = []
for d in ph["overshoot"]:
    u = d["unit"]
    st = next(s for s in units[u]["steps"] if s.get("op") == "cell" and s["step"]["dtype"] == d["dtype"]
              and s["step"]["kind"] == d["kind"] and s["step"]["pass"] == 1 and s["step"]["size"] == 8192)
    t0 = st["run"]["t0"]
    app = units[u]["static"].get("app_clock_sm") or 1095
    S = [s for s in units[u]["samples"] if t0 - 0.05 <= R.tmid(s) < t0 + 1.0]
    loaded = [(round(R.tmid(s) - t0, 2), round(s["p_mw"] / 1000.0, 1)) for s in S if s.get("sm") is not None
              and s["sm"] <= app + 30 and s.get("p_mw") is not None and s["p_mw"] / 1000.0 > (ph["idle_w"][u] + 60)]
    boost = next((round(R.tmid(s) - t0, 2) for s in S if s.get("sm") is not None and s["sm"] > app + 30), None)
    settled = len(loaded) >= 2 and abs(loaded[-1][1] - loaded[-2][1]) <= 0.05 * loaded[-1][1]
    rows.append((d, loaded, boost, settled))
    nf = d.get("n_fit")
    P(f"{u} {d['dtype']} {d['kind']}: boost at {boost} s; loaded readings (s, W) {loaded}; two readings agreeing within 5%: {settled}; "
      f"n_fit {'-' if nf is None else round(nf, 2)}")
bt = [b for _, _, b, _ in rows if b is not None]
P(f"boost {min(bt)}-{max(bt)} s after the first call (median {statistics.median(bt)}); "
  f"loaded readings before it: {min(len(l) for _, l, _, _ in rows)}-{max(len(l) for _, l, _, _ in rows)}")
fit = [(d, s) for d, _, _, s in rows if d.get("n_fit") is not None]
st_n = sorted(round(d["n_fit"], 2) for d, s in fit if s)
P(f"cells that fit n: {len(fit)}; with two readings within 5%: {len(st_n)}, n {st_n}; "
  f"median of all {statistics.median(d['n_fit'] for d, _ in fit):.3f}, range {min(d['n_fit'] for d, _ in fit):.2f}-{max(d['n_fit'] for d, _ in fit):.2f}")
same = tot = 0
ch = []
for u in "AB":
    for st in units[u]["steps"]:
        if st.get("op") != "cell" or st["step"]["size"] != 8192 or st["step"]["pass"] != 1:
            continue
        t0 = st["run"]["t0"]
        S = [s for s in units[u]["samples"] if t0 + 3.0 <= R.tmid(s) < t0 + 63.0 and s.get("p_mw") is not None]
        last = None
        for i in range(1, len(S)):
            tot += 1
            if S[i]["p_mw"] == S[i - 1]["p_mw"]:
                same += 1
            else:
                if last is not None:
                    ch.append(S[i]["t"] - last)
                last = S[i]["t"]
ch.sort()
P(f"power-usage readings in the sustained windows (pass 1): {same} of {tot} consecutive 100 ms samples repeat the value before "
  f"({same / tot:.1%}); time between changes median {statistics.median(ch):.2f} s, 90th percentile {ch[9 * len(ch) // 10]:.2f} s")

# C2: the 330 W view with its calibration
P("\n## C2. post hoc at 330 W (posthoc.json at_330)")
for r in ph["at_330"]:
    P(f"{r['unit']} {r['dtype']}: at 400 W model {r['gap_400']:.4f} against measured {r['measured_400']:.4f} "
      f"(error {r['model_error_400']:+.4f}); at 330 W {r['gap_330']:.4f}, less that error {r['gap_330_less_error']:.4f}")
z = next(d for d in ph["overshoot"] if d["unit"] == "B" and d["dtype"] == "bf16" and d["kind"] == "zeros")
rn = next(d for d in ph["overshoot"] if d["unit"] == "B" and d["dtype"] == "bf16" and d["kind"] == "randn")
P0 = ph["idle_w"]["B"]
P(f"unit B bf16: zeros' switching over idle at 1410 MHz as a share of randn's post-hoc demand there: "
  f"({z['p_sus']:.1f} - {P0:.1f}) / ({rn['demand_1410_w']:.1f} - {P0:.1f}) = {(z['p_sus'] - P0) / (rn['demand_1410_w'] - P0):.3f}")

# C11: what the nvidia-smi -q text keeps (field names only; the values are in the logs)
P("\n## C11. identifier lines in each static step's nvidia-smi -q text")
for u in "AB":
    st = units[u]["static"]
    txt = next((v for v in st.values() if isinstance(v, str) and "Product Name" in v), "")
    kept, scrubbed = [], []
    for line in txt.splitlines():
        m = re.match(r"\s*(Serial Number|GPU UUID|GPU PDI|Board ID|Chassis Serial Number|ClusterUUID)\s*:\s*(.*)", line)
        if m:
            (scrubbed if "[scrubbed]" in m.group(2) else kept).append(m.group(1))
    bus = bool(re.search(r"^GPU [0-9A-F]{8}:[0-9A-F]{2}:[0-9A-F]{2}\.[0-9]", txt, re.M))
    pip = st.get("pip") or []
    cub = [p for p in (pip if isinstance(pip, list) else [f"{k}=={v}" for k, v in pip.items()]) if "cublas" in str(p).lower()]
    P(f"{u} {st.get('name')}: scrubbed {scrubbed}; kept {kept}{' and the PCI bus id' if bus else ''}; torch {st.get('torch')}, {cub}")

# C13: the cost ceilings, from the app's own plan functions (ast-extracted, modal not imported)
P("\n## C13. projected cost and the two ceilings (e135_app.py plan functions)")
src = os.path.join(TOOLS, "e135_app.py")
tree = ast.parse(open(src).read())
fns = {"_cell", "_proto", "plan_A", "plan_B", "plan_S", "step_seconds", "dollars", "describe"}
consts = {"BF16_A", "FP16_A", "TF32_A", "INT8_A", "GIST6", "ARTICLE9", "CFG_MAIN", "CFG_SMOKE", "RATE", "CPU_CORES", "MEM_MIB",
          "TIMEOUT_MAIN_S", "TIMEOUT_SMOKE_S", "BUDGET_S"}
body = [n for n in tree.body if (isinstance(n, ast.FunctionDef) and n.name in fns)
        or (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in consts for t in n.targets))]
ns = {}
exec(compile(ast.Module(body=body, type_ignores=[]), "e135_app.py", "exec"), ns)
tp = tg = tt = 0.0
for u, fn in (("A", ns["plan_A"]), ("B", ns["plan_B"]), ("S", ns["plan_S"])):
    e, _, _ = ns["describe"](fn())
    to = ns["TIMEOUT_MAIN_S"] if u != "S" else ns["TIMEOUT_SMOKE_S"]
    tp += ns["dollars"](e)[0]
    tg += ns["dollars"](min(ns["BUDGET_S"][u] + 60.0, to))[0]
    tt += ns["dollars"](to)[0]
P(f"projected ${tp:.2f}; budget guard (each unit stops at its budget) ${tg:.2f}; function timeouts ${tt:.2f}")

# C1: the ET-SoC-1 kernels beside the A100
P("\n## C1. zeros/random on the ET-SoC-1, by kernel (aifoundry2 under its own governor)")
pr = json.load(open(os.path.join(TOOLS, "predictions-e135.json")))["etsoc1"]["gaps"]
for dt in ("fp32", "fp16", "int8"):
    g = pr.get(dt, {})
    P(f"resident loop (E80, E83), {dt}: burst {g.get('burst_gap_range')}, sustained {g.get('sus_gap_range')}")
e105 = json.load(open(os.path.join(DATA, "2026-11-01-e105-gemm-layout", "results-speed.json")))["gaps"]
for k in ("gemmc1-fp32-randn", "gemmc1-fp32-sparse25", "gemmc1-fp16-randn", "gemmc1-int8-full"):
    P(f"E105 repeated block, B by column, {k[7:]}: {e105[k]}")
p5 = json.load(open(os.path.join(DATA, "2026-11-01-e105-gemm-layout", "scored-p.json")))["rules"]["P5"]
P(f"E105 zeros' share of random's switching at 600 MHz (aifoundry3), by column and the benchmark: {p5}")
e119 = json.load(open(os.path.join(DATA, "2026-11-01-e119-gemm-speed", "results.json")))["gaps"]
for k in ("c16r8-fp32-randn", "c16r4-fp32-randn", "c16r2-fp32-randn", "c8s-fp32-randn", "c8s-int8-full"):
    P(f"E119 walk {k}: {e119[k]}")
e126 = json.load(open(os.path.join(DATA, "2026-11-02-e126-gemm-arms", "results.json")))["gaps"]
for k in ("c16r8-fp32-randn", "c16r4-fp32-randn", "c16r2-fp32-randn", "c8s-fp32-randn", "c4s-fp32-randn", "c4s-int8-full",
          "c8-fp32-randn", "c16s-fp32-randn"):
    P(f"E126 walk {k}: {e126[k]}")
