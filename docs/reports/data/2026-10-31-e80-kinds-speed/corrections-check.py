#!/usr/bin/env python3
"""E80: the desk check behind the corrections after verification (Sat 31 Oct 2026). Desk only: it reads the committed
session and the committed reduction, and every number the README's "Corrections after verification" section quotes is
printed here. Nothing registered is recomputed differently: the per-sample conventions are reduce_hpl.py's (E64's).

    cd docs/reports/data/2026-10-31-e80-kinds-speed
    python3 corrections-check.py > corrections-check.txt

Inputs: results.json, posthoc-idle.json, s1/launches.jsonl.gz, s1/tel/*.jsonl.gz, s1/run.log, smoke/run.log,
E64's s1/run.log, smoke2/run.log and figures.json, and the frozen predictions.json. Python 3, no third-party modules.
"""
import gzip
import json
import math
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
E64 = os.path.join(HERE, "..", "2026-10-23-e64-horace-power-limit")
sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "kspeed"))
import reduce_kspeed as RK  # noqa: E402  (frozen; only its t1_sim is called, post hoc)

OPS = {"fp32": 8192, "fp16": 16384, "int8": 32768}
R = json.load(open(os.path.join(HERE, "results.json")))
PH = json.load(open(os.path.join(HERE, "posthoc-idle.json")))
PRED = json.load(open(os.path.join(REPO, "tools", "claims-v3", "kspeed", "predictions.json")))
C = R["cells"]
RUNS = {m["run"]: m for m in R["runs"]}


def jl_gz(path):
    out = []
    with gzip.open(path, "rt") as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith("{"):
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


def tel(run):
    """reduce_hpl.tel's tuple: (t_ms, die = minion-shire mean, hottest minion-shire sensor, board W, minion MHz)."""
    s = []
    for d in jl_gz(os.path.join(HERE, "s1", "tel", run + ".jsonl.gz")):
        try:
            ms = d.get("temp_c", {}).get("minshire") or [None, None, None]
            s.append((int(d["t_ms"]), ms[0], ms[2], d.get("board_w"), d.get("mhz", {}).get("minion")))
        except (KeyError, TypeError, ValueError, AttributeError):
            pass
    return sorted(s)


LAUNCH = {}
for L in jl_gz(os.path.join(HERE, "s1", "launches.jsonl.gz")):
    if L.get("role") == "work":
        LAUNCH.setdefault(L["run"], []).append(L)


def windows(run):
    procs = sorted(LAUNCH[run], key=lambda p: p["t_start_ms"])
    lw = [k for p in procs for k in p.get("sparsity", []) if k.get("t_start_ms") and k.get("t_end_ms")]
    t0 = procs[0]["t_start_ms"]
    t1 = max(p["t_end_ms"] for p in procs)
    return procs, lw, t0, t1


def rms(xs):
    xs = [x for x in xs if x is not None]
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else None


def hdr(s):
    print()
    print("=" * 8, s)


# ---------------------------------------------------------------------------------------------------------------
hdr("C1. The sustained runs: what holds each one below 800 MHz (E64's per-sample labels, last 40 s)")
print("The registered reduction (reduce_hpl.run_metrics) keeps the sampler readings that fall inside a kernel launch;")
print("sus_mhz, sus_w and sus_die are means over those readings. Here: their count, the die over them, the governor's")
print("throttle-down lines over the whole run (the trace ring covers the run from `ring from`), and the labels.")
print(f"{'run':30s} {'MHz':>6s} {'lim':8s} {'800':>5s} {'therm':>5s} {'ramp':>5s} {'other':>5s} | {'n_in':>4s} "
      f"{'die>=65':>7s} {'die>=66':>7s} {'maxdie':>6s} | {'thermal_down':>12s} {'power_down':>10s} {'first66_s':>9s} "
      f"{'ring from':>9s}")
SUS = {}
for run, m in RUNS.items():
    if m["block"] != "SUS":
        continue
    procs, lw, t0, t1 = windows(run)
    tl = t1 - 40000
    kw = [(k["t_start_ms"], k["t_end_ms"]) for k in lw]
    s = tel(run)
    inn = [x for x in s if tl <= x[0] <= t1 and any(a <= x[0] <= b for a, b in kw)]
    d65 = sum(1 for x in inn if x[1] is not None and x[1] >= 65)
    d66 = sum(1 for x in inn if x[1] is not None and x[1] >= 66)
    mx = max(x[1] for x in inn if x[1] is not None)
    td = m.get("work_thermal_down") or []
    pd = m.get("work_power_down") or []
    sl = m["sus_last"]
    SUS[run] = dict(kind=m["kind"], n_in=len(inn), d65=d65, d66=d66, maxdie=mx, td=len(td), pd=len(pd),
                    td_first=(td[0]["t_s"] if td else None), sl=sl, mhz=m["sus_mhz_mean"], lim=m["limit"])
    print(f"{run:30s} {m['sus_mhz_mean']:6.1f} {m['limit']:8s} {sl['800']:5.3f} {sl['thermal']:5.3f} {sl['ramp']:5.3f} "
          f"{sl['other']:5.3f} | {len(inn):4d} {d65:4d} {d65 / len(inn):5.0%} {d66:4d}     {mx:4d}   | "
          f"{len(td):5d} first {td[0]['t_s'] if td else '-':>5} {len(pd):6d}     {m.get('sus_first_66_s')!s:>7}  "
          f"{m.get('sus_ring_from_s')!s:>7}  (placement {m['placement']['source']}, matched "
          f"{m['placement']['matched']}/{m['placement']['ops']})")
f = [v for v in SUS.values() if v["kind"] == "int8/full"]
print(f"int8 full: thermal-down lines {[v['td'] for v in f]} = {sum(v['td'] for v in f)} over its two runs; die >= 65 C in "
      f"{[round(v['d65'] / v['n_in'], 3) for v in f]} of its in-kernel last-40-s readings, >= 66 C in "
      f"{[v['d66'] for v in f]} readings; thermal-labelled share of the last 40 s {[v['sl']['thermal'] for v in f]}; "
      f"clocks {[v['mhz'] for v in f]} MHz, rates {C['int8/full']['sus_rate_runs']} TOPS. Its registered label is "
      f"`none` because >= 90% of the last 40 s read 800 MHz (README Decision rules).")
others = [v for v in SUS.values() if v["kind"].startswith("int8/") and v["kind"] != "int8/full"]
print("the other five int8 kinds: thermal-down lines", sorted({v["td"] for v in others}), "power-down lines",
      sorted({v["pd"] for v in others}), "; hottest in-kernel die reading in the last 40 s",
      {v["kind"]: v["maxdie"] for v in others})
print("power label anywhere in a sustained last 40 s:", any(v["sl"]["power"] > 0 for v in SUS.values()))

hdr("C1b. Why the unthrottled kinds read below 800 MHz sustained (the samples below 800, last 40 s, in-kernel)")
for run, v in SUS.items():
    if v["td"] or v["mhz"] >= 800:
        continue
    print(f"  {run:30s} {v['kind']:15s} {v['mhz']:6.1f} MHz: labels {v['sl']}")
print("  `ramp` = a reading below 800 within 1.5 s of a process start (reduce_hpl RAMP_S): each of the nine 8 s")
print("  processes climbs 600 -> 700 -> 800 as it starts. int8 neg_ones' `other` is the idle-reset dip at 74.78 s (C6).")
for k in ("int8/neg_ones", "int8/smallint"):
    for m in [m for m in R["runs"] if m["kind"] == k and m["block"] == "BURST"]:
        sub = [x for x in m["trace"] if 1.5 <= x[0] <= m["work_s"] and x[3] in (600, 700, 800) and x[3] != 800]
        print(f"  burst {m['run']:28s} {m['burst_mhz']:6.1f} MHz; readings below 800 in the 1.5 s-to-end window: "
              f"{len(sub)} ({', '.join(f'{x[0]} s {x[3]}' for x in sub[:3])}{' ...' if len(sub) > 3 else ''}); "
              f"work ends {m['work_s']} s")

# ---------------------------------------------------------------------------------------------------------------
hdr("C2. E80-S1: which way each out-of-sample switching term missed")
for k, cw, cp, ci in R["rules"]["E80-S1"]["rows"]:
    runs = C[k]["c_w_runs"]
    side = "inside" if ci[0] <= cw <= ci[1] else ("ABOVE" if cw > ci[1] else "BELOW")
    print(f"  {k:15s} measured {cw:7.3f} W (passes {runs}) predicted {cp:7.3f} [{ci[0]:.3f}, {ci[1]:.3f}] -> {side}; "
          f"{'above' if cw > cp else 'below'} the point by {cw - cp:+.3f} W; passes inside: "
          f"{[ci[0] <= x <= ci[1] for x in runs]}")

# ---------------------------------------------------------------------------------------------------------------
hdr("C3. E80-R1 (PASS as registered): what the 21.7 MHz rests on")
rows = R["rules"]["E80-R1"]["rows"]
cap = [r for r in rows if r[1] == 800 and r[2] == 800]
inf = [r for r in rows if not (r[1] == 800 and r[2] == 800)]
print(f"  all 18: rms {rms([r[3] for r in rows]):.2f} MHz. Predicted 800 and measured 800 (residual 0 by the cap): "
      f"{len(cap)} -> {[r[0] for r in cap]}")
print(f"  the other {len(inf)}: rms {rms([r[3] for r in inf]):.2f} MHz; residuals (measured - predicted) "
      + ", ".join(f"{r[0]} {r[3]:+.1f}" for r in sorted(inf, key=lambda r: -abs(r[3]))))
wo = {k: v["burst_mhz_without"] for k, v in PH["kinds"].items()}
inf_wo = [(r[0], wo[r[0]] - r[2]) for r in inf]
print("  the same 10 with posthoc-idle.json's idle-reset and late-ramp samples set aside (post hoc): rms "
      f"{rms([d for _, d in inf_wo]):.2f} MHz; residuals " + ", ".join(f"{k} {d:+.1f}" for k, d in inf_wo)
      + f"; the most negative is {min(d for _, d in inf_wo):+.1f} MHz")
print(f"  all 18 that way: {rms([wo[r[0]] - r[2] for r in rows]):.2f} MHz (posthoc-idle.json views.R1_rms_without_mhz "
      f"{PH['views']['R1_rms_without_mhz']})")

# ---------------------------------------------------------------------------------------------------------------
hdr("C4. Board energy per operation at the sustained point: which samples the numerator and denominator cover")
print("  published (tables.md): sus_w / sus_rate. sus_w is the mean board W over the in-kernel readings (C1's n_in of")
print("  the ~400 readings in the last 40 s) and sus_rate is the kernel's operations over its own wall time: both cover")
print("  the kernel only. Whole window: the mean over ALL readings in the last 40 s over the wall-clock rate (gaps")
print("  between the nine processes included). Mixed: in-kernel W over the wall-clock rate (it counts the gaps' time but")
print("  charges them the in-kernel power).")
print(f"  {'kind':15s} {'in-kernel':>9s} {'whole':>7s} {'mixed':>7s} {'whole/in':>8s} | {'gap share (time)':>16s} "
      f"{'readings in/all':>15s} {'W in':>6s} {'W all':>6s} {'W gaps':>6s}")
PJ = {}
for k in C:
    su = [r for r, v in SUS.items() if v["kind"] == k]
    pin, pwh, pmx, gaps, nin, nall, win, wall, wgap, rks, rws = [], [], [], [], [], [], [], [], [], [], []
    for run in su:
        procs, lw, t0, t1 = windows(run)
        tl = t1 - 40000
        kw = [(x["t_start_ms"], x["t_end_ms"]) for x in lw]
        s = tel(run)
        a = [x for x in s if tl <= x[0] <= t1 and x[3] is not None]
        i = [x for x in a if any(p <= x[0] <= q for p, q in kw)]
        g = [x for x in a if not any(p <= x[0] <= q for p, q in kw)]
        lwl = [x for x in lw if x["t_start_ms"] >= tl]
        ops = sum(x["minions"] * x["iters"] * OPS[C[k]["type"]] for x in lwl)
        wl = sum(x["wall_s"] for x in lwl)
        rk, rw = ops / wl, ops / ((t1 - tl) / 1000.0)
        rks.append(rk)
        rws.append(rw)
        wi, wa = st.mean([x[3] for x in i]), st.mean([x[3] for x in a])
        pin.append(wi / rk * 1e12)
        pwh.append(wa / rw * 1e12)
        pmx.append(wi / rw * 1e12)
        gaps.append(1 - rw / rk)
        nin.append(len(i))
        nall.append(len(a))
        win.append(wi)
        wall.append(wa)
        wgap.append(st.mean([x[3] for x in g]) if g else float("nan"))
    # the cell's figures, formed as tables.py forms them (the mean over a kind's runs, then the ratio); the
    # recomputation must reproduce the registered in-kernel W and both rates
    assert abs(C[k]["sus_w"] - st.mean(win)) < 0.02, k
    assert abs(C[k]["sus_rate_wall"] - st.mean(rws) / 1e12) < 0.002 and abs(C[k]["sus_rate"] - st.mean(rks) / 1e12) < 0.002, k
    pub = C[k]["sus_w"] / C[k]["sus_rate"]
    whole = st.mean(wall) / C[k]["sus_rate_wall"]
    mixed = C[k]["sus_w"] / C[k]["sus_rate_wall"]
    PJ[k] = (pub, whole, mixed)
    print(f"  {k:15s} {pub:9.3f} {whole:7.3f} {mixed:7.3f} {whole / pub - 1:+8.1%} | "
          f"{st.mean(gaps):16.1%} {'/'.join(map(str, nin)):>7s} of {'/'.join(map(str, nall)):<7s} "
          f"{st.mean(win):6.2f} {st.mean(wall):6.2f} {st.mean(wgap):6.2f}")
lo = min(v[1] / v[0] - 1 for v in PJ.values())
hi = max(v[1] / v[0] - 1 for v in PJ.values())
print(f"  whole-window over in-kernel: {lo:+.1%} to {hi:+.1%}; the mixed figure over the whole-window one: "
      f"{min(v[2] / v[1] - 1 for v in PJ.values()):+.1%} to {max(v[2] / v[1] - 1 for v in PJ.values()):+.1%}")

# ---------------------------------------------------------------------------------------------------------------
hdr("C5. The idle die at each session's first gate, and the loaded die line (results.json posthoc.die_line_e80)")
gate = re.compile(r"^(\d\d:\d\d:\d\d)\s+gate: .*'reading': \(([\d.]+), ([\d.]+), ([\d.]+), ([\d.]+)\)")
for label, path in (("E80 smoke (31 Oct)", os.path.join(HERE, "smoke", "run.log")),
                    ("E80 s1 (31 Oct)", os.path.join(HERE, "s1", "run.log")),
                    ("E64 smoke2 (23 Oct)", os.path.join(E64, "smoke2", "run.log")),
                    ("E64 s1 (23 Oct)", os.path.join(E64, "s1", "run.log"))):
    for ln in open(path):
        g = gate.match(ln)
        if g:
            print(f"  {label:20s} first gate {g.group(1)}: die {g.group(2)} C (hottest sensor {g.group(3)}), board "
                  f"{g.group(4)} W, {g.group(5)} MHz  [{os.path.relpath(path, HERE)}]")
            break
dl = R["posthoc"]["die_line_e80"]
print(f"  loaded: E80 line {dl['a_c']} + {dl['k_c_per_w']} C/W over {dl['n']} runs (rms {dl['rms_c']} C), 65.5 C at "
      f"{dl['cap_w_at_65_5']} W against E64's {dl['e64_line']['cap_w_at_65_5']} W "
      f"(+{dl['cap_w_at_65_5'] - dl['e64_line']['cap_w_at_65_5']:.1f} W); at E64's slope {dl['shift_c_at_e64_slope']} C")
print("  no ambient, inlet or fan reading exists in E80's or E64's committed sessions: the cause of the shift is not "
      "measured")

# ---------------------------------------------------------------------------------------------------------------
hdr("C6. The idle reset inside a launch (posthoc-idle.json), checked against the trace ring and the kernel's counters")
dips = [(r, e) for r, v in PH["runs"].items() for e in v["episodes"] if e["kind"] == "dip"]
for run, e in dips:
    m = RUNS[run]
    el = m.get("event_list") or []
    idle = [x for x in el if x["kind"] == "pstat" and x.get("state") == 0 and x.get("t_s") is not None]
    near = [x["t_s"] for x in idle if -0.5 <= x["t_s"] - e["t_s"] <= 0.3]
    lims = [x["t_s"] for x in el if x["kind"] in ("power_down", "thermal_down") and x.get("t_s") is not None
            and e["t_s"] - 2 <= x["t_s"] <= e["t_s"] + 1.5]
    procs, lw, t0, t1 = windows(run)
    ghz = [round(x["ghz"], 3) for x in lw if x.get("ghz") and (x["t_start_ms"] - t0) / 1000 <= e["t_s"] + 0.6
           and (x["t_end_ms"] - t0) / 1000 >= e["t_s"]]
    cover = min((x["t_s"] for x in el if x.get("t_s") is not None), default=None)
    back = next((x[0] for x in m["trace"] if x[0] > e["t_s"] and x[3] == 800), None)
    print(f"  {run:28s} dip at {e['t_s']:6.2f} s, {e['samples']:2d} readings, die {e['die']} C, board {e['w_before']} W "
          f"before; back at 800 {back if back is not None and back <= m['work_s'] else 'not before the work ended'} "
          f"(work ends {m['work_s']} s); kernel GHz in the launch at the dip {ghz[:2]}; state-0 (POWER_IDLE) record "
          f"within -0.5..+0.3 s: {near or 'none'}; throttle lines near it: {lims or 'none'}; ring covers from "
          f"{cover} s (placement {m['placement']['source']}, matched {m['placement']['matched']}/{m['placement']['ops']})")
m = RUNS["SUS-08-int8-neg_ones-r1"]
ring = [(x["t_s"], x.get("mhz"), x.get("state")) for x in m["event_list"] if x["kind"] == "pstat"]
first7 = next(x[0] for x in m["trace"] if x[0] > 0 and x[3] == 700)
first8 = next(x[0] for x in m["trace"] if x[0] > 0 and x[3] == 800)
off = st.mean([first7 - ring[0][0], first8 - ring[1][0]])
print(f"  SUS-08's ring (placed by the session's clock fit, matched 0): {ring}. Its start ramp reads 700 / 800 MHz in the "
      f"sampler at {first7} / {first8} s, so that placement runs {off:.2f} s early; shifted by it the state-0 record "
      f"sits at {ring[2][0] + off:.2f} s, against the dip's first 600 MHz reading at 74.78 s")
for run in ("BURST-08-int8-neg_ones-r1", "BURST-17-fp32-nn_like-r1"):
    m = RUNS[run]
    tr = [x for x in m["trace"] if 1.5 <= x[0] <= m["work_s"] and x[3] in (600, 700, 800)]
    lab = {}
    for e in PH["runs"][run]["episodes"]:
        if e["kind"] == "dip":
            i0 = next(i for i, x in enumerate(tr) if abs(x[0] - e["t_s"]) < 0.01)
            for x in tr[i0:i0 + e["samples"]]:
                lab[x[0]] = "dip"
        else:
            for x in tr:
                if e["t_s"] + 1.2 < x[0] < e["first800_s"]:
                    lab[x[0]] = "late"
    for part in ("dip", "late"):
        cost = sum(800 - x[3] for x in tr if lab.get(x[0]) == part) / len(tr)
        print(f"  {run}: the {part} samples cost the 1.5 s-to-end mean {cost:.1f} MHz", end="")
    print(f"; registered {m['burst_mhz']}, both set aside {PH['runs'][run]['burst_mhz_without']}")
late = [(r, e) for r, v in PH["runs"].items() for e in v["episodes"] if e["kind"] == "late_ramp"]
print(f"  late ramps: {len(late)} (first 800 MHz reading more than 1.2 s after a process start, on a die under 65 C "
      f"and a board under 65 W):")
for r, e in sorted(late, key=lambda x: -x[1]["first800_s"] + x[1]["t_s"]):
    print(f"    {r:30s} process at {e['t_s']:6.2f} s: first 800 at {e['first800_s']:6.2f} s "
          f"(+{e['first800_s'] - e['t_s']:.2f} s), {e['samples']} reading(s) flagged")
# exposure: where the detector can see a dip at all (a reading at 800 MHz on a die under 65 C, more than 1.5 s after
# its process started and more than 0.3 s before it ended), against all work readings
expo = allw = 0
for run, m in RUNS.items():
    if m.get("kind") is None:
        continue
    procs, lw, t0, t1 = windows(run)
    spans = [((p["t_start_ms"] - t0) / 1000.0, (p["t_end_ms"] - t0) / 1000.0) for p in procs]
    for a, b in spans:
        xs = [x for x in m["trace"] if a <= x[0] <= b and x[3] in (600, 700, 800)]
        allw += len(xs)
        expo += sum(1 for x in xs if x[3] == 800 and (x[1] is None or x[1] < 65) and x[0] - a > 1.5
                    and b - x[0] > 0.3)
print(f"  exposure: {expo} of {allw} work readings ({expo / allw:.0%}) are at 800 MHz on a die under 65 C inside the "
      f"detector's span, about {expo / 10:.0f} s of {allw / 10:.0f} s at 10 Hz; {len(dips)} dips in "
      f"{PH['views']['processes']} processes. E63 (14-card-behaviour.md): 8 in 360 launches of 8.5 s at 800 MHz, die "
      f"54-57 C, dips 1.4-8.4 s into a launch.")

# ---------------------------------------------------------------------------------------------------------------
hdr("C7. Q130(c)'s R7 and R8 against what Q130(c) registered (post hoc views, labelled; the verdicts stand)")
w7_reg = sum(1 for c in C.values() if abs(c["burst_mhz"] - c["pred_burst_q130c"]) <= 25)
w7_win = sum(1 for c in C.values() if abs(c["burst_mhz"] - c["pred_burst_reg"]) <= 25)
print(f"  R7's 25 MHz clause on Q130(c)'s 4-12 s numbers (as scored): {w7_reg} of 18; on the same model's 1.5-6.5 s "
      f"numbers (E80's registered burst prediction, the window E80 measures): {w7_win} of 18")
print("  Q130(c)'s burst 4-12 s minus its 1.5-6.5 s prediction: " + ", ".join(
    f"{k} {c['pred_burst_q130c'] - c['pred_burst_reg']:+.1f}" for k, c in C.items()
    if abs(c["pred_burst_q130c"] - c["pred_burst_reg"]) > 0.05))
xs = [m["sus_w_mean"] for m in R["runs"] if m["block"] == "SUS"]
ys = [m["sus_die_mean"] for m in R["runs"] if m["block"] == "SUS"]
mx_, my_ = st.mean(xs), st.mean(ys)
k_ = sum((x - mx_) * (y - my_) for x, y in zip(xs, ys)) / sum((x - mx_) ** 2 for x in xs)
line = {"k_c_per_w": k_, "a_c": my_ - k_ * mx_}
# the criterion first: on the frozen line (die_line None) it must give back Q130(c)'s own frozen R8 labels
same = 0
for k, c in C.items():
    su = [m for m in R["runs"] if m["kind"] == k and m["block"] == "SUS"]
    sims = [RK.t1_sim(PRED, PRED["kinds"][k]["c_pred_w"], m["die_start"] or 57) for m in su]
    lim = "thermal" if st.mean([s["die_c"] for s in sims]) >= 65.5 else "power"
    same += lim == c["pred_limit_q130c"]
print(f"  criterion check (thermal when the simulated die mean is >= 65.5 C, else power), frozen line: {same} of 18 "
      f"cells match Q130(c)'s frozen sustained_limit")
lim_ok = clk_ok = 0
rows8 = []
for k, c in C.items():
    su = [m for m in R["runs"] if m["kind"] == k and m["block"] == "SUS"]
    sims = [RK.t1_sim(PRED, PRED["kinds"][k]["c_pred_w"], m["die_start"] or 57, line) for m in su]
    mhz = st.mean([s["mhz"] for s in sims])
    lim = "thermal" if st.mean([s["die_c"] for s in sims]) >= 65.5 else "power"
    meas = ["thermal" if x == "thermal" else "power" for x in c["sus_limit_runs"]]
    ok_l = all(x == lim for x in meas)
    ok_c = abs(c["sus_mhz"] - mhz) <= 40
    lim_ok += ok_l
    clk_ok += ok_c
    rows8.append(f"{k} {mhz:.1f}/{lim}{'' if ok_l else ' (limit wrong)'}")
print(f"  R8 with the die line re-read IN SAMPLE (E80's own line, fitted on these 21 runs; Q130(c)'s frozen c): limit "
      f"right {lim_ok} of 18, clock within 40 MHz {clk_ok} of 18 -> would read "
      f"{'PASS' if lim_ok == 18 and clk_ok >= 0.7 * 18 else 'FAIL'}; as scored (frozen line): limit 13, clock 13, FAIL")
print("    " + "; ".join(rows8))

# ---------------------------------------------------------------------------------------------------------------
hdr("C8. The burst passes: pass order against the die each pass started from")
lim_kinds = [k for k, c in C.items() if c["burst_limit"] == "power"]
p1 = [c["burst_die_start"][0] for c in C.values()]
p2 = [c["burst_die_start"][1] for c in C.values()]
print(f"  start die, pass 1: {min(p1)}-{max(p1)} C; pass 2: {min(p2)}-{max(p2)} C")
for k in lim_kinds:
    c = C[k]
    a, b = c["burst_mhz_runs"]
    print(f"  {k:15s} pass 1 {a:6.1f} MHz from {c['burst_die_start'][0]} C, pass 2 {b:6.1f} MHz from "
          f"{c['burst_die_start'][1]} C: {b - a:+.1f} MHz; p800 {c['burst_p800_w_runs']} W")
print(f"  power-limited kinds lower in pass 2: {sum(1 for k in lim_kinds if C[k]['burst_mhz_runs'][1] < C[k]['burst_mhz_runs'][0])}"
      f" of {len(lim_kinds)}")

# ---------------------------------------------------------------------------------------------------------------
hdr("C9. The sampler: how each one was stopped (marks.jsonl)")
for sess in ("smoke", "s1"):
    stops, rcs, kills = 0, {}, 0
    for ln in open(os.path.join(HERE, sess, "marks.jsonl")):
        if not ln.strip():
            continue
        s = ln
        if "sampler_stop" in s:
            stops += 1
            g = re.search(r"rc (-?\d+)", s)
            rcs[g.group(1) if g else "?"] = rcs.get(g.group(1) if g else "?", 0) + 1
        if "ignored SIGTERM" in s or "SIGKILL" in s:
            kills += 1
    print(f"  {sess:6s} sampler_stop marks {stops}, by rc {rcs}; marks naming SIGKILL / ignored SIGTERM: {kills}")

# ---------------------------------------------------------------------------------------------------------------
hdr("C10. E80-S2's population (34 of 36 bursts) and its post-hoc view")
for m in R["runs"]:
    if m["block"] == "BURST" and m.get("gov_own_mhz") is None:
        n7 = sum(1 for x in m["trace"] if 0 <= x[0] <= m["work_s"] and x[3] == 700)
        print(f"  left out: {m['run']} (p_raw_w {m['p_raw_w']}; {n7} reading at 700 MHz, so no pair of consecutive "
              f"700 MHz readings for surface_hpl.powers and no 700 MHz power for the simulation, which needs all three)")
b = [(r, v) for r, v in PH["runs"].items() if v["block"] == "BURST" and v.get("gov_own_mhz") is not None]
both800 = [r for r, v in b if v["gov_own_mhz"] == 800 and v["burst_mhz_without"] == 800]
res = [v["gov_own_mhz"] - v["burst_mhz_without"] for r, v in b if r not in both800]
print(f"  post hoc S2 (dip and late-ramp samples set aside, posthoc-idle.json): rms {PH['views']['S2_rms_without_mhz']} "
      f"over {len(b)}; {len(both800)} of them read 800 in both the simulation and the measurement; over the other "
      f"{len(res)}: rms {rms(res):.2f} MHz")

# ---------------------------------------------------------------------------------------------------------------
hdr("C11. bf16-truncated fp32 against random fp32: the two bases of the saving")
F64 = json.load(open(os.path.join(E64, "figures.json")))
z = F64["fit"]["c"]["SUS-00-fp32-zeros-1024-r1"]
cb, cr = C["fp32/bf16trunc"]["c_w"], C["fp32/randn"]["c_w"]
pb, pr = PRED["kinds"]["fp32/bf16trunc"]["c_pred_w"], PRED["kinds"]["fp32/randn"]["c_pred_w"]
print(f"  measured c: bf16trunc {cb}, randn {cr}; E64 fp32 zeros c {z} (figures.json fit.c SUS-00-fp32-zeros-1024-r1)")
print(f"  saving over the zeros level: {1 - (cb - z) / (cr - z):.1%}; of the whole switching term: {1 - cb / cr:.1%}")
print(f"  frozen: bf16trunc {pb}, randn {pr}: over zeros {1 - (pb - z) / (pr - z):.1%}, whole term {1 - pb / pr:.1%}")
print()
print("done")
