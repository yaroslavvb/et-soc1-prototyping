#!/usr/bin/env python3
"""E143 (Q138): the checks behind the README's "Corrections after verification" (Mon 2 Nov 2026). POST HOC, never a verdict.

Written after an independent verification of E143. It reads only committed files: this directory's results.json and the
session's launch records, the frozen predictions (tools/claims-v3/e143/predictions-e143.json), pool 5's and the kinds
matrix's tiles, E80's and E83's committed records, and E142's committed runs. It changes no frozen file, number, rule or
verdict. Every interval is a percentile bootstrap over tiles (20,000 draws, seed 143). Sections:

  (1) the blind rms values with their intervals, against the in-sample reference the rules drew from;
  (2) the 30 new kinds alone (the 6 anchors left out);
  (3) the board error: an offset or a scale? the slope on the predicted W, the levels, the burst D, and in-sample fits;
  (4) the clock's bias where the governor acts, against the drift check R0 on E80's identical tiles;
  (5) the check of C: what "counted" means for file tiles;
  (6) the 6 anchors and the bytes they share with E80's, E83's and M7's reference tiles;
  (7) the registration's commit time against E142's first runs of the pool;
  (8) the kinds table's cells: every tile's burst clock, burst board W, burst D and die rise, with the passes' spread.

    python3 docs/reports/data/2026-11-02-e143-blind5-aifoundry2/posthoc_corrections_e143.py > docs/reports/data/2026-11-02-e143-blind5-aifoundry2/posthoc-corrections.txt
"""
import datetime
import glob
import gzip
import hashlib
import json
import math
import os
import random
import statistics as st
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
REL = os.path.relpath(HERE, REPO)
R = json.load(open(os.path.join(HERE, "results.json")))
P = json.load(open(os.path.join(REPO, "tools", "claims-v3", "e143", "predictions-e143.json")))
T = R["score"]["reported"]["tiles"]
RU = R["score"]["rules"]
REF = P["reference"]
PST = datetime.timezone(datetime.timedelta(hours=-8))
DRAWS = 20000
rng = random.Random(143)
OUT = {"note": "post hoc, written after verification on Mon 2 Nov 2026; never a verdict; every interval a percentile bootstrap over tiles "
               f"({DRAWS} draws, seed 143)"}


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs))


def r3(x):
    return None if x is None else round(x, 3)


def boot(xs, f):
    v = sorted(f([rng.choice(xs) for _ in xs]) for _ in range(DRAWS))
    return [r3(v[int(0.025 * DRAWS)]), r3(v[int(0.975 * DRAWS) - 1])]


def ols(x, y):
    mx, my = st.mean(x), st.mean(y)
    sxx = sum((a - mx) ** 2 for a in x)
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sxx
    return b, my - b * mx


def slope_ci(x, y):
    pairs = list(zip(x, y))
    bs = []
    while len(bs) < DRAWS:
        s = [rng.choice(pairs) for _ in pairs]
        sx = [p[0] for p in s]
        if max(sx) - min(sx) < 1e-9:
            continue
        bs.append(ols(sx, [p[1] for p in s])[0])
    bs.sort()
    return [round(bs[int(0.025 * DRAWS)], 4), round(bs[int(0.975 * DRAWS) - 1], 4)]


def fmt(n):
    return n.split(".")[0]


def err(n, q):
    meas = {"mhz": "burst_mhz", "w": "burst_w", "rise": "rise_c", "D": "D_w"}[q]
    pred = {"mhz": "M7_mhz", "w": "M7_w", "rise": "M7_rise", "D": "M7_D"}[q]
    return T[n][meas] - T[n][pred]


gov = sorted(n for n, t in T.items() if t["group"] == "governed")
pin = sorted(n for n, t in T.items() if t["group"] == "pinned")
anchors = sorted(n for n in T if ".anchor_" in n)
zeros = sorted(n for n in T if n.endswith(".anchor_zeros"))
alln = sorted(T)
pin_nz = [n for n in pin if n not in zeros]
lines = []


def say(s=""):
    lines.append(s)


say("E143 post hoc checks for the corrections after verification (Mon 2 Nov 2026). Never a verdict. Intervals: percentile bootstrap over")
say(f"tiles, {DRAWS} draws, seed 143.")

# ---------------------------------------------------------------------------------------------------- (1)
say("\n(1) The blind rms values with 95% intervals over tiles, against the in-sample reference the rules drew from")
ref_cells_p = REF["pinned"]["cells"]
big = [i for i, m in enumerate(REF["pinned"]["mhz_err"]) if abs(m) > 5]
keep = [i for i in range(len(ref_cells_p)) if i not in big]
ref_p35_mhz = rms([REF["pinned"]["mhz_err"][i] for i in keep])
ref_p35_w = rms([REF["pinned"]["w_err"][i] for i in keep])
sec1 = {}
specs = [("E143-F1", gov, "mhz", REF["governed"]["rms_mhz"], "MHz"), ("E143-F2", pin, "mhz", REF["pinned"]["rms_mhz"], "MHz"),
         ("E143-W1", gov, "w", REF["governed"]["rms_w"], "W"), ("E143-W2", pin, "w", REF["pinned"]["rms_w"], "W"),
         ("E143-H1", alln, "rise", REF["heat"]["rms_c"], "C"), ("all 36 clock", alln, "mhz", None, "MHz"), ("all 36 board", alln, "w", None, "W")]
for name, names, q, ref, u in specs:
    e = [err(n, q) for n in names]
    ci = boot(e, rms)
    row = {"n": len(e), "rms": r3(rms(e)), "rms_95": ci, "ref_rms": ref,
           "ref_inside_interval": (None if ref is None else bool(ci[0] <= ref <= ci[1]))}
    if name in RU:
        row["registered_rms"] = RU[name]["rms"]
        row["registered_verdict"] = RU[name]["verdict"]
    sec1[name] = row
    say(f"  {name:13s} n {len(e):2d}: rms {rms(e):6.3f} {u} [{ci[0]:.3f}, {ci[1]:.3f}]" +
        ("" if ref is None else f"; reference {ref} {'inside' if row['ref_inside_interval'] else 'OUTSIDE'} the interval"))
sec1["reference_pinned_without_its_large_clock_errors"] = {
    "cells_left_out": [ref_cells_p[i] for i in big], "their_mhz_err": [REF["pinned"]["mhz_err"][i] for i in big],
    "their_w_err": [REF["pinned"]["w_err"][i] for i in big], "n_kept": len(keep), "rms_mhz": r3(ref_p35_mhz), "rms_w": r3(ref_p35_w),
    "source": "tools/claims-v3/e143/predictions-e143.json reference.pinned (cells, mhz_err, w_err): the cells with |clock error| > 5 MHz"}
say(f"  The reference's pinned rows: {len(big)} of {len(ref_cells_p)} cells M7 put at 800 MHz read {min(REF['pinned']['mhz_err']):.1f} to "
    f"{max(REF['pinned']['mhz_err'][i] for i in big):.1f} MHz ({', '.join(ref_cells_p[i] for i in big)}).")
say(f"  Without them the reference's pinned rms is {ref_p35_mhz:.3f} MHz and {ref_p35_w:.3f} W over {len(keep)} cells; pool 5's pinned tiles")
say(f"  held none like them (largest pinned clock error {min(err(n, 'mhz') for n in pin):.2f} MHz, int8.a_word_flipflop's one pass at 788 MHz).")
OUT["1_blind_rms_intervals"] = sec1

# ---------------------------------------------------------------------------------------------------- (2)
say("\n(2) The 30 new kinds alone (the 6 anchors left out), M7, rms with 95% intervals")
new = [n for n in alln if n not in anchors]
sec2 = {"anchors_left_out": anchors}
for name, names, q, u in (("governed clock", [n for n in gov if n in new], "mhz", "MHz"), ("pinned clock", [n for n in pin if n in new], "mhz", "MHz"),
                          ("governed board", [n for n in gov if n in new], "w", "W"), ("pinned board", [n for n in pin if n in new], "w", "W"),
                          ("all clock", new, "mhz", "MHz"), ("all board", new, "w", "W"), ("all rise", new, "rise", "C")):
    e = [err(n, q) for n in names]
    sec2[name] = {"n": len(e), "rms": r3(rms(e)), "rms_95": boot(e, rms), "mean": r3(st.mean(e))}
    say(f"  {name:15s} n {len(e):2d}: rms {rms(e):6.3f} {u} {sec2[name]['rms_95']}, mean {st.mean(e):+.3f}")
OUT["2_new_kinds_only"] = sec2

# ---------------------------------------------------------------------------------------------------- (3)
say("\n(3) The board error (measured - M7): an offset or a scale?")
sec3 = {}
for name, names in (("all 36", alln), ("pinned 17", pin), ("pinned non-zeros 14", pin_nz),
                    ("int8 non-zeros 10", [n for n in pin_nz if fmt(n) == "int8"]), ("governed 19", gov)):
    x = [T[n]["M7_w"] for n in names]
    y = [err(n, "w") for n in names]
    b, a = ols(x, y)
    ci = slope_ci(x, y)
    sec3["slope " + name] = {"n": len(names), "slope_w_per_w": round(b, 4), "slope_95": ci, "intercept_w": r3(a), "M7_w_range": [min(x), max(x)]}
    say(f"  slope on M7's W, {name:20s}: {b:+.4f} W/W [{ci[0]:+.4f}, {ci[1]:+.4f}] over M7 {min(x):.2f}-{max(x):.2f} W")
z_e = {n: err(n, "w") for n in zeros}
lev = {"zeros anchors, each": {n: r3(v) for n, v in z_e.items()}, "zeros anchors, mean (the zeros level)": r3(st.mean(z_e.values())),
       "float zeros anchors, mean": r3(st.mean(v for n, v in z_e.items() if fmt(n) != "int8")),
       "pinned floats, non-zeros (gated and block-sparse), mean": r3(st.mean(err(n, "w") for n in pin_nz if fmt(n) != "int8")),
       "pinned int8, non-zeros, mean": r3(st.mean(err(n, "w") for n in pin_nz if fmt(n) == "int8")),
       "governed, mean (the cap level)": r3(st.mean(err(n, "w") for n in gov)), "pinned, mean": r3(st.mean(err(n, "w") for n in pin))}
sec3["levels_w"] = lev
say("  levels (mean board error, W): " + "; ".join(f"{k} {v}" for k, v in lev.items() if not isinstance(v, dict)))
say("  the zeros anchors one by one: " + ", ".join(f"{n} {v:+.3f}" for n, v in z_e.items()))
dD = {"governed": [err(n, "D") for n in gov], "pinned floats non-zeros": [err(n, "D") for n in pin_nz if fmt(n) != "int8"],
      "pinned int8 non-zeros": [err(n, "D") for n in pin_nz if fmt(n) == "int8"]}
sec3["burst_D_error_w"] = {k: {"n": len(v), "mean": r3(st.mean(v)), "rms": r3(rms(v))} for k, v in dD.items()}
say("  burst D error (measured D - M7 D, W): " + "; ".join(f"{k} mean {st.mean(v):+.3f}, rms {rms(v):.3f} (n {len(v)})" for k, v in dD.items()))


def gain(names):
    return sum(T[n]["D_w"] * T[n]["M7_D"] for n in names) / sum(T[n]["M7_D"] ** 2 for n in names)


gains = {"pinned floats": gain([n for n in pin_nz if fmt(n) != "int8"]), "pinned int8": gain([n for n in pin_nz if fmt(n) == "int8"]), "pinned all": gain(pin_nz)}
sec3["D_gain_measured_on_M7"] = {k: round(v, 4) for k, v in gains.items()}
say("  D's gain (measured D on M7's D through 0, pass-matched D, non-zeros pinned): " + "; ".join(f"{k} {v:.4f}" for k, v in gains.items()))
# in-sample fits: A frozen; B cap level + zeros level; C B + one D gain on the pinned; C2 B + a D gain per format kind (floats, int8)
Lc = st.mean(err(n, "w") for n in gov)
Lz = st.mean(z_e.values())
z7 = {fmt(n): T[n]["M7_w"] for n in zeros}


def fitted_gain(names):
    num = sum((T[n]["M7_w"] - z7[fmt(n)]) * (T[n]["burst_w"] - z7[fmt(n)] - Lz) for n in names)
    den = sum((T[n]["M7_w"] - z7[fmt(n)]) ** 2 for n in names)
    return num / den


g1 = fitted_gain(pin_nz)
gf = fitted_gain([n for n in pin_nz if fmt(n) != "int8"])
gi = fitted_gain([n for n in pin_nz if fmt(n) == "int8"])


def e_fit(n, how):
    e = err(n, "w")
    if how == "A":
        return e
    if n in gov:
        return e - Lc
    if how == "B" or n in zeros:
        return e - Lz
    g = g1 if how == "C" else (gi if fmt(n) == "int8" else gf)
    return T[n]["burst_w"] - (z7[fmt(n)] + Lz + g * (T[n]["M7_w"] - z7[fmt(n)]))


fits = {}
for how, label in (("A", "as frozen"), ("B", "+ a cap level and a zeros level"), ("C", f"+ one D gain on the pinned ({g1:.4f})"),
                   ("C2", f"+ a D gain per format kind (floats {gf:.4f}, int8 {gi:.4f})")):
    e = {n: e_fit(n, how) for n in alln}
    fits[how] = {"what": label, "all36": r3(rms(list(e.values()))), "governed": r3(rms([e[n] for n in gov])),
                 "pinned": r3(rms([e[n] for n in pin])), "pinned_nonzeros": r3(rms([e[n] for n in pin_nz]))}
    say(f"  in-sample {how:2s} {label:52s}: rms all {fits[how]['all36']:.3f}, governed {fits[how]['governed']:.3f}, pinned {fits[how]['pinned']:.3f}, "
        f"pinned non-zeros {fits[how]['pinned_nonzeros']:.3f} W")
sec3["in_sample_fits"] = fits
sec3["in_sample_parameters"] = {"cap_level_w": r3(Lc), "zeros_level_w": r3(Lz), "one_D_gain_pinned": round(g1, 4),
                                "D_gain_floats": round(gf, 4), "D_gain_int8": round(gi, 4),
                                "note": "fitted on E143's own 36 tiles: in-sample; a term found here must be scored blind on a new pool or session"}
# inside the governed set: does the error rise with how far the tile's unthrottled power overshoots the cap?
adm = P["admission"]
x = [adm["b5-" + n]["fixed_p800_w"] for n in gov]
y = [err(n, "w") for n in gov]
b, a = ols(x, y)
ci = slope_ci(x, y)
gsplit = {}
for name, names in (("M7 below 760 MHz (random-like)", [n for n in gov if T[n]["M7_mhz"] < 760]), ("M7 760-795 MHz", [n for n in gov if T[n]["M7_mhz"] >= 760])):
    e = [err(n, "w") for n in names]
    gsplit[name] = {"n": len(e), "mean_w": r3(st.mean(e)), "mean_95": boot(e, st.mean)}
sec3["governed_vs_overshoot"] = {"x": "tools/claims-v3/e143/predictions-e143.json admission.<label>.fixed_p800_w (the frozen estimate of the tile's board W at 800 MHz)",
                                 "W_star_w": r3(P["relation"]["W_star_w"]), "slope_w_per_w": round(b, 4), "slope_95": ci, "x_range_w": [min(x), max(x)],
                                 "split": gsplit}
say(f"  inside the governed 19: board error on the frozen unthrottled estimate fixed_p800_w ({min(x):.1f}-{max(x):.1f} W, cap {P['relation']['W_star_w']:.2f}): "
    f"{b:+.4f} W/W [{ci[0]:+.4f}, {ci[1]:+.4f}]")
say("  governed board error by depth: " + "; ".join(f"{k} n {v['n']}, mean {v['mean_w']:+.3f} W {v['mean_95']}" for k, v in gsplit.items()))
OUT["3_board_error_offset_or_scale"] = sec3

# ---------------------------------------------------------------------------------------------------- (4)
say("\n(4) The clock's bias where the governor acts, against the drift check R0")
eg = [err(n, "mhz") for n in gov]
deep = [n for n in gov if T[n]["M7_mhz"] < 760]
light = [n for n in gov if T[n]["M7_mhz"] >= 760]
sec4 = {"governed": {"n": len(eg), "mean_mhz": r3(st.mean(eg)), "mean_95": boot(eg, st.mean), "n_below_prediction": sum(e < 0 for e in eg)}}
for name, names in (("governed, M7 below 760 MHz (random-like)", deep), ("governed, M7 760-795 MHz", light)):
    e = [err(n, "mhz") for n in names]
    sec4[name] = {"n": len(e), "mean_mhz": r3(st.mean(e)), "mean_95": boot(e, st.mean), "tiles": names}
say(f"  governed mean clock error {st.mean(eg):+.3f} MHz {sec4['governed']['mean_95']}; {sec4['governed']['n_below_prediction']} of {len(eg)} below their prediction")
for name in ("governed, M7 below 760 MHz (random-like)", "governed, M7 760-795 MHz"):
    s = sec4[name]
    say(f"  {name}: n {s['n']}, mean {s['mean_mhz']:+.3f} MHz {s['mean_95']}")
rep = R["replicate"]["tiles"]
r0 = {}
for k, v in rep.items():
    pr = P["replicate"][k]
    r0[k] = {"tonight_mhz": v["burst_mhz"], "vs_E80_plus_E83_mean": v["d_mhz"], "vs_E80": r3(v["burst_mhz"] - pr["e80_burst_mhz"]),
             "vs_E83": r3(v["burst_mhz"] - pr["e83_burst_mhz"]), "same_bytes_sha256": pr["sha256"]}
    say(f"  R0 {k}: {v['burst_mhz']} MHz tonight; {v['d_mhz']:+.2f} against E80 and E83's mean, {r0[k]['vs_E80']:+.2f} against E80, {r0[k]['vs_E83']:+.2f} against E83")
sec4["R0_replicates"] = r0
for n in ("fp32.anchor_randn", "fp16.anchor_randn"):
    pe = [r3(x - T[n]["M7_mhz"]) for x in T[n]["burst_mhz_runs"]]
    sec4[n + " per pass error"] = pe
    say(f"  {n}: per-pass clock error {pe} MHz (mean {err(n, 'mhz'):+.2f})")
OUT["4_clock_bias_and_drift"] = sec4

# ---------------------------------------------------------------------------------------------------- (5)
say("\n(5) The check of C: what 'counted' means for file tiles")
sec5 = {}


def launches(path):
    c = {}
    n = te = 0
    vals = set()
    for line in gzip.open(path, "rt"):
        r = json.loads(line)
        for x in (r.get("sparsity") or []):
            n += 1
            key = f"result={x.get('result')} ok={x.get('ok')}"
            c[key] = c.get(key, 0) + 1
            te += int(x.get("tensor_errors") or 0)
            vals.add((x.get("values") or "")[:5])
    return {"kernel_launches": n, "result_ok": c, "tensor_errors": te, "values_prefix": sorted(vals)}


for lab, p in (("E143 s1", os.path.join(HERE, "aifoundry2", "s1", "launches.jsonl.gz")), ("E143 smoke", os.path.join(HERE, "aifoundry2", "smoke", "launches.jsonl.gz")),
               ("E80 s1", os.path.join(REPO, "docs", "reports", "data", "2026-10-31-e80-kinds-speed", "s1", "launches.jsonl.gz")),
               ("E80 smoke", os.path.join(REPO, "docs", "reports", "data", "2026-10-31-e80-kinds-speed", "smoke", "launches.jsonl.gz"))):
    sec5[lab] = launches(p)
    say(f"  {lab}: {sec5[lab]['kernel_launches']} kernel launches, {sec5[lab]['result_ok']}, tensor errors {sec5[lab]['tensor_errors']}, values {sec5[lab]['values_prefix']}")
sec5["host_rule"] = ("workloads/sparsity/host/main.cpp:589 rawValues = values != 'small'; :614 a raw-values launch's check is 'unchecked'; "
                     ":615 ok = the launch completed, every hart reported (summarize's bad == 0) and no tensor error")
say("  " + sec5["host_rule"])
OUT["5_check_of_C"] = sec5

# ---------------------------------------------------------------------------------------------------- (6)
say("\n(6) The 6 anchors")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


sec6 = {}
for n in anchors:
    f = fmt(n)
    a = sha(os.path.join(REPO, "tools", "claims-v3", "kinds", "blind5", "tiles", f, n + ".bin"))
    kind = n.split(".anchor_")[1]
    kt = os.path.join(REPO, "tools", "claims-v3", "kinds", "tiles", f, kind + ".bin")
    k = sha(kt) if os.path.exists(kt) else None
    sec6[n] = {"sha256": a, "kinds_tile": os.path.relpath(kt, REPO), "kinds_tile_sha256": k, "same_bytes": a == k}
zsha = sec6[zeros[0]]["sha256"]
found = []
for p in sorted(glob.glob(os.path.join(REPO, "docs", "reports", "data", "2026-10-31-e8[03]-kinds-speed*", "s1", "kspeed.json"))):
    if zsha in open(p).read():
        found.append(os.path.relpath(p, REPO))
sec6["zeros_sha256_named_in"] = found
for n in anchors:
    s = sec6[n]
    say(f"  {n}: {s['sha256'][:12]}... {'the same bytes as' if s['same_bytes'] else 'not the bytes of'} {s['kinds_tile']}")
say(f"  the zeros tiles' sha256 {zsha[:12]}... is named in: {', '.join(found)}")
OUT["6_anchors"] = sec6

# ---------------------------------------------------------------------------------------------------- (7)
say("\n(7) E143's registration commit against E142's first runs of the pool")
try:
    ct = int(subprocess.run(["git", "-C", REPO, "show", "-s", "--format=%ct", "38cd9099"], capture_output=True, text=True, timeout=20).stdout.strip())
    src = "git show -s --format=%ct 38cd9099"
except Exception:
    ct, src = 1793681649, "constant (git unavailable): 38cd9099's commit time"
pool = set(T)
e142 = os.path.join(REPO, "docs", "reports", "data", "2026-11-02-e142-blind5-card1", "aifoundry1-c1", "e142", "p14210", "runs.jsonl")
rows = [json.loads(line) for line in open(e142)]
pr = [r for r in rows if r.get("item") in pool]
first = min(pr, key=lambda r: r["t_start_ms"])
before = [r for r in pr if r["t_start_ms"] < ct * 1000]
sec7 = {"commit_38cd9099_pst": datetime.datetime.fromtimestamp(ct, PST).strftime("%H:%M:%S"), "commit_time_source": src,
        "e142_first_pool_record": {"item": first["item"], "start_pst": datetime.datetime.fromtimestamp(first["t_start_ms"] / 1000, PST).strftime("%H:%M:%S.%f")[:-3],
                                   "seconds_before_commit": round(ct - first["t_start_ms"] / 1000, 1)},
        "e142_pool_records_before_commit": len(before), "e142_pool_tiles_before_commit": sorted({r["item"] for r in before}),
        "source": os.path.relpath(e142, REPO)}
say(f"  38cd9099 committed {sec7['commit_38cd9099_pst']} PST ({src}); E142's first record of a pool tile, {first['item']}, started "
    f"{sec7['e142_first_pool_record']['start_pst']} PST, {sec7['e142_first_pool_record']['seconds_before_commit']} s before;")
say(f"  {len(before)} of E142's records of {len(sec7['e142_pool_tiles_before_commit'])} pool tiles started before the commit: {', '.join(sec7['e142_pool_tiles_before_commit'])}")
OUT["7_registration_vs_e142"] = sec7

# ---------------------------------------------------------------------------------------------------- (8)
say("\n(8) The kinds table's cells (aifoundry2 card 0, its own governor, E80's 6 s burst, 3 passes; interval = the passes' spread)")
cells = []
qdef = {"burst_MHz": ("burst_mhz", "burst_mhz_runs", "MHz", "the sampled clock (100 ms telemetry) from 1.5 s after the first launch to the work's end"),
        "burst_W": ("burst_w", "burst_w_runs", "W", "the board W over the same samples"),
        "D_W": ("D_w", "D_runs", "W", "the burst W less the same type's zeros tile's burst W in the same pass (0 by definition for the zeros tiles, so left out)"),
        "die_C": ("rise_c", "rise_runs", "C", "the die's rise over the burst: die_max - die_start (E64's reduction)")}
for n in alln:
    for q, (k, kr, u, what) in qdef.items():
        if q == "D_W" and n in zeros:
            continue
        runs = T[n][kr]
        cells.append({"format": fmt(n), "kind": n.split(".", 1)[1], "quantity": q, "value": T[n][k], "interval": [min(runs), max(runs)],
                      "unit": u, "conditions": f"aifoundry2 card 0, own governor (65 W / 65 C, nothing set), E80's 6 s burst, 3 passes, mean of passes; M7 {T[n]['group']}",
                      "source": f"{REL}/results.json score.reported.tiles.{n}.{k}"})
OUT["8_table_cells"] = {"interval": "the spread of the 3 passes (min, max)", "quantities": {q: v[3] for q, v in qdef.items()}, "cells": cells}
say(f"  {len(cells)} cells: 36 tiles x burst_MHz, burst_W and die_C, and D_W for the 33 that are not zeros (D is 0 by definition there)")

json.dump(OUT, open(os.path.join(HERE, "posthoc-corrections.json"), "w"), indent=1)
print("\n".join(lines))
