#!/usr/bin/env python3
"""E152: the numbers behind the corrections after verification (Tue 3 Nov 2026, desk only; post hoc, labelled).

Nothing here is a registered verdict, and nothing frozen changes: the registration (tools/claims-v3/e152/, 2a744f4d),
scored.json, results.md, the reductions, posthoc/ and the raw passes stay as committed in 99dc31f3. No card, no device
command, nothing re-run. Standard library only; it reads committed files only:

  scored.json, posthoc/scored-footing-q139u.json      the registered reading and the post hoc reading on Q139(u)'s footing
  runs.csv, posthoc/runs-footing-q139u.csv             per-run D, to re-derive each pass's C(n) without the scorer
  aifoundry3/kinds/p1521[0-5]/plan.json, run.log       what each pass planned and what it ran
  tools/claims-v3/e152/predictions-e152.json           C8*, p*, the models' per-flip prices (the freeze)
  tools/claims-v3/e152/m8-bridge/predictions-aifoundry3.json   the footing M8's frozen bridge predictions are on
  docs/reports/data/2026-11-02-e127-b-gate/scored.json  E127's Q2 per pass (sha256 checked against the freeze)
  tools/claims-v3/e152/README.md                       the registration's text before its Amendments section

    python3 docs/reports/data/2026-11-03-e152-gate-dose/corrections_e152.py \
        > docs/reports/data/2026-11-03-e152-gate-dose/corrections.txt

It also writes corrections.json beside itself. C1-C5 are the README's corrections after verification.
"""
import csv
import hashlib
import json
import math
import os
import re
import statistics
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
REG = os.path.join(REPO, "tools", "claims-v3", "e152")
E127 = os.path.join(REPO, "docs", "reports", "data", "2026-11-02-e127-b-gate", "scored.json")
T975 = {1: 12.706205, 2: 4.302653, 3: 3.182446, 4: 2.776445, 5: 2.570582, 6: 2.446912}
PASSES = ["15210", "15211", "15212", "15213", "15214", "15215"]
DOSE_TILES = {1: ("fp32.gd1a", "fp32.gd1b"), 2: ("fp32.gd2a", "fp32.gd2b"), 4: ("fp32.gd4a", "fp32.gd4b"), 8: ("fp32.gd8",)}
OUT = {}


def load(p):
    with open(p) as f:
        return json.load(f)


def sha256(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def ci(vals):
    n = len(vals)
    m = statistics.mean(vals)
    sd = statistics.stdev(vals)
    h = T975[n - 1] * sd / math.sqrt(n)
    return {"mean": m, "sd": sd, "h": h, "lo": m - h, "hi": m + h, "n": n}


def ls_intercept(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return my - b * mx, b


def say(s=""):
    print(s)


def per_pass_C_from_runs(path):
    """C(n) per pass from runs.csv alone: a tile's D in a pass is the mean over its kept runs, a dose's D the mean of
    its tiles', C(n) = D(dose n) - D(gd0). The registration's definition (Decision rules), not the scorer's code."""
    D = defaultdict(lambda: defaultdict(list))
    with open(path) as f:
        for r in csv.DictReader(f):
            if r["item"].startswith("fp32.gd") or r["item"] in ("fp32.q_chk", "fp32.q_steady"):
                D[r["pass"]][r["item"]].append(float(r["D"]))
    C = {n: [] for n in DOSE_TILES}
    Q2 = []
    for p in PASSES:
        d = {k: statistics.mean(v) for k, v in D[p].items()}
        for n, ts in DOSE_TILES.items():
            C[n].append(statistics.mean(d[t] for t in ts) - d["fp32.gd0"])
        Q2.append(d["fp32.q_chk"] - d["fp32.q_steady"])
    return C, Q2


reg = load(os.path.join(HERE, "scored.json"))["primary"]
foot = load(os.path.join(HERE, "posthoc", "scored-footing-q139u.json"))["primary"]
pred = load(os.path.join(REG, "predictions-e152.json"))
C8S = reg["rules"]["E152-R1"]["C8_star_w"]
TAU = reg["rules"]["E152-R1"]["tau_w"]
assert abs(TAU - 0.1 * C8S) < 1e-12

say("E152, corrections after verification: the numbers (post hoc, labelled; never a verdict)")
say(f"C8* (E127's price x 4,080 flips x the op rate, frozen) = {C8S:.4f} W; tau = 0.10 x C8* = {TAU:.4f} W")
say()

# ---------------------------------------------------------------- C1: how precisely the ladder is linear
say("C1. How precisely the ladder is linear: the 3% figures are point estimates; the 95% bounds reach about 10%")
c1 = {}
for lab, src in (("registered", reg), ("footing", foot)):
    r1 = src["rules"]["E152-R1"]
    C8 = r1["C8_w"]
    rows = {}
    say(f"  {lab}: C(8) {C8:+.4f} +- {r1['C8_ci95_w']:.4f} W")
    for n in ("1", "2", "4"):
        d = r1["delta_w"][n]
        rows[n] = {"delta_w": d["mean"], "lo_w": d["lo95"], "hi_w": d["hi95"],
                   "point_pct_C8star": 100 * d["mean"] / C8S, "point_pct_session_C8": 100 * d["mean"] / C8,
                   "lo_pct_C8star": 100 * d["lo95"] / C8S, "hi_pct_C8star": 100 * d["hi95"] / C8S,
                   "abs_plus_h_pct_C8star": 100 * (abs(d["mean"]) + d["ci95"]) / C8S}
        x = rows[n]
        say(f"    delta({n}) {x['delta_w']:+.4f} W [{x['lo_w']:+.4f}, {x['hi_w']:+.4f}]: point {x['point_pct_C8star']:+.2f}% of C8* "
            f"({x['point_pct_session_C8']:+.2f}% of the session's C(8)); 95% {x['lo_pct_C8star']:+.1f}% to {x['hi_pct_C8star']:+.1f}% of C8*; "
            f"|delta| + h = {x['abs_plus_h_pct_C8star']:.2f}% of C8*")
    worst = max(rows[n]["abs_plus_h_pct_C8star"] for n in rows)
    span = (min(rows[n]["lo_pct_C8star"] for n in rows), max(rows[n]["hi_pct_C8star"] for n in rows))
    say(f"    the three intervals span {span[0]:+.1f}% to {span[1]:+.1f}% of C8*; the worst |delta| + h is {worst:.2f}% of C8* "
        f"(the rule's line is 10%)")
    c1[lab] = {"C8_w": C8, "C8_h_w": r1["C8_ci95_w"], "delta": rows, "worst_abs_plus_h_pct_C8star": worst,
               "span_pct_C8star": span}

# the least-squares intercept of C(n) on n (a part spent whenever any lane flips), per pass, then t(5) over passes
ns = [1, 2, 4, 8]
for lab, src, csvp in (("registered", reg, os.path.join(HERE, "runs.csv")),
                       ("footing", foot, os.path.join(HERE, "posthoc", "runs-footing-q139u.csv"))):
    Cs = {n: src["doses"][str(n)]["C_w"]["values"] for n in ns}
    Cr, _ = per_pass_C_from_runs(csvp)
    worst_diff = max(abs(a - b) for n in ns for a, b in zip(Cs[n], Cr[n]))
    ints = [ls_intercept(ns, [Cs[n][i] for n in ns])[0] for i in range(len(PASSES))]
    s = ci(ints)
    line = src["reported"]["line_C_on_n"]["intercept_w"]
    assert abs(statistics.mean(ints) - line) < 1e-9, "mean of per-pass intercepts must equal the intercept of the means"
    c1[lab]["intercept"] = {"per_pass_w": ints, "mean_w": s["mean"], "h_w": s["h"], "lo_w": s["lo"], "hi_w": s["hi"],
                            "lo_pct_C8star": 100 * s["lo"] / C8S, "hi_pct_C8star": 100 * s["hi"] / C8S,
                            "point_pct_C8star": 100 * s["mean"] / C8S, "scored_line_intercept_w": line,
                            "runs_csv_vs_scored_max_abs_diff_w": worst_diff}
    say(f"  {lab}: the least-squares intercept of C(n) on n = 1, 2, 4, 8, fitted per pass, t(5) over the six passes: "
        f"{s['mean']:+.4f} +- {s['h']:.4f} W = {100 * s['lo'] / C8S:+.1f}% to {100 * s['hi'] / C8S:+.1f}% of C8* "
        f"(point {100 * s['mean'] / C8S:+.1f}%; equal to scored.json's line of the means, {line:+.4f}; C(n) per pass "
        f"from runs alone matches the scorer's to {worst_diff:.1e} W)")

rp = reg["reported"]
g = rp["gd1h_minus_gd1_w"]
C1w = reg["doses"]["1"]["C_w"]["mean"]
c1["per_boundary"] = {"mean_w": g["mean"], "lo_w": g["lo95"], "hi_w": g["hi95"], "C1_w": C1w}
say(f"  the per-boundary test, gd1h - mean(gd1a, gd1b): {g['mean']:+.3f} W [{g['lo95']:+.3f}, {g['hi95']:+.3f}] "
    f"(a per-boundary cost would make it negative): its interval is {g['hi95'] - g['lo95']:.3f} W wide, against the "
    f"single-lane contrast C(1) = {C1w:+.3f} W itself: unresolved")
c1["mirror"] = {}
for k in ("n=1", "n=2", "n=4"):
    m = rp["mirror_pairs_w"][k]
    c1["mirror"][k] = {"mean_w": m["mean"], "h_w": m["ci95"]}
    say(f"  mirror pair {k}: {m['mean']:+.3f} +- {m['ci95']:.3f} W: unresolved")
OUT["C1"] = c1
say()

# ---------------------------------------------------------------- C2: M8's 7%
say("C2. M8's per-flip price against the ladder: 7% is a point estimate, not a resolved difference as registered")
mp = pred["models_per_flip_fJ"]
models = {"M8 whole at E127's pair": mp["M8_whole_at_E127_pair"], "M7 whole at E127's pair": mp["M7_whole_at_E127_pair"],
          "M6 whole at E127's pair": mp["M6_whole_at_E127_pair"]}
c2 = {"models_fJ": models}
for lab, src in (("registered", reg), ("footing", foot)):
    r2 = src["rules"]["E152-R2"]
    lo, hi, p = r2["lo95_fJ"], r2["hi95_fJ"], r2["price_fJ"]
    inside = {}
    for name, v in models.items():
        if lo <= v <= hi:
            inside[name] = {"inside": True, "margin_fJ": min(v - lo, hi - v)}
        else:
            inside[name] = {"inside": False, "outside_by_fJ": (lo - v) if v < lo else (v - hi)}
    c2[lab] = {"price_fJ": p, "h_fJ": r2["ci95_fJ"], "lo_fJ": lo, "hi_fJ": hi, "ladder_over_M8": p / mp["M8_whole_at_E127_pair"],
               "models": inside}
    say(f"  {lab}: the ladder's price {p:.1f} +- {r2['ci95_fJ']:.1f} fJ [{lo:.1f}, {hi:.1f}]; ladder / M8 whole = "
        f"{p / mp['M8_whole_at_E127_pair']:.3f} (point)")
    for name, x in inside.items():
        v = models[name]
        if x["inside"]:
            say(f"    {name} {v:.1f} fJ: INSIDE the interval (by {x['margin_fJ']:.1f} fJ)")
        else:
            say(f"    {name} {v:.1f} fJ: outside the interval by {x['outside_by_fJ']:.1f} fJ")
pa = reg["reported"]["per_dose_against_predictions"]
c8 = reg["doses"]["8"]["C_w"]
m8_c8 = pa["8"]["M8_linear_bench_w"]
say(f"  registered C(8) = {c8['mean']:+.3f} +- {c8['ci95']:.3f} W = [{c8['lo95']:+.3f}, {c8['hi95']:+.3f}]: M8's linear-bench "
    f"{m8_c8:+.3f} inside: {c8['lo95'] <= m8_c8 <= c8['hi95']}; E127's frozen C8* {C8S:+.3f} inside: {c8['lo95'] <= C8S <= c8['hi95']}")
hw = {n: reg["doses"][n]["C_w"]["ci95"] for n in ("1", "2", "4", "8")}
fhw = {n: foot["doses"][n]["C_w"]["ci95"] for n in ("1", "2", "4", "8")}


def rms(key, src):
    e = [src["doses"][n]["C_w"]["mean"] - src["doses"][n]["C_pred_w"][key] for n in ("1", "2", "4", "8")]
    return math.sqrt(sum(x * x for x in e) / len(e)), e


rmsE, eE = rms("E127_price", reg)
rmsM, eM = rms("M8_linear_bench", reg)
frmsE, _ = rms("E127_price", foot)
frmsM, _ = rms("M8_linear_bench", foot)
for lab, h, a, b in (("registered", hw, rmsE, rmsM), ("footing", fhw, frmsE, frmsM)):
    say(f"  {lab}: the contrasts' 95% half-widths C(1) {h['1']:.3f}, C(2) {h['2']:.3f}, C(4) {h['4']:.3f}, C(8) {h['8']:.3f} W "
        f"(smallest {min(h.values()):.3f}); rms of measured - predicted over the four contrasts: E127's price {a:.4f} W, "
        f"M8 whole {b:.4f} W; both below the smallest half-width: {max(a, b) < min(h.values())}")
say(f"  M8's errors by dose (registered, measured - predicted): " + ", ".join(f"{x:+.4f}" for x in eM) + " W")
gd0 = reg["table"]["fp32.gd0"]
say(f"  every C(n) is D(dose n) - D(gd0): D(gd0) = {gd0['D']:.3f} +- {gd0['ci95']:.3f} W, so a shift of D(gd0) inside its own "
    f"95% half-width moves all four contrasts together by up to {gd0['ci95']:.3f} W, more than M8's gaps at one and two "
    f"lanes ({eM[0]:+.3f}, {eM[1]:+.3f} W): 'low at every dose' is not four independent readings")
c2.update({"C8_w": c8["mean"], "C8_lo_w": c8["lo95"], "C8_hi_w": c8["hi95"], "M8_linear_bench_C8_w": m8_c8, "C8_star_w": C8S,
           "half_widths_w": {"registered": hw, "footing": fhw},
           "rms_w": {"E127_price": {"registered": rmsE, "footing": frmsE}, "M8_whole": {"registered": rmsM, "footing": frmsM}},
           "M8_basis": "M8 is fitted on Q139(u)'s footing (q139m-model README), so its per-flip price is a footing-basis figure",
           "M8_errors_w": eM,
           "D_gd0_w": gd0["D"], "D_gd0_h_w": gd0["ci95"]})
OUT["C2"] = c2
say()

# ---------------------------------------------------------------- C3: the run count
say("C3. The run count: 186 runs planned, 185 ran; one anchor skipped by E78's registered launch gate")
c3 = {"passes": {}}
rows_by_pass = defaultdict(list)
with open(os.path.join(HERE, "runs.csv")) as f:
    for r in csv.DictReader(f):
        rows_by_pass[r["pass"]].append(r)
planned_total = ran_total = 0
for p in PASSES:
    d = os.path.join(HERE, "aifoundry3", "kinds", "p" + p)
    plan = load(os.path.join(d, "plan.json"))
    ran = rows_by_pass[p]
    with open(os.path.join(d, "run.log")) as f:
        skips = [(i + 1, line.strip()) for i, line in enumerate(f) if line.rstrip().endswith(": skipped")]
    tiles = sum(1 for r in ran if r["item"].startswith("fp32.gd") or r["item"] in ("fp32.q_chk", "fp32.q_steady"))
    fails = sum(1 for r in ran if r["fail"] not in ("", "0"))
    z8 = sum(1 for r in ran if r["item"] == "int8.zeros")
    planned_total += len(plan)
    ran_total += len(ran)
    c3["passes"][p] = {"planned": len(plan), "ran": len(ran), "e152_tile_runs": tiles, "failing_a_run_gate": fails,
                       "int8_zeros_runs": z8, "skipped_lines": skips}
    say(f"  p{p}: planned {len(plan)}, ran {len(ran)} (E152 tiles {tiles} of 11, failing a run gate {fails}, "
        f"int8.zeros {z8} of 3)" + "".join(f"; run.log line {i}: {s}" for i, s in skips))
c3.update({"planned": planned_total, "ran": ran_total})
say(f"  in all: {ran_total} of {planned_total} planned runs ran; every E152 tile ran in every pass; the skipped run is an "
    f"anchor, which leaves int8's zeros level in that pass on two runs (it is int8.full's reference, an S1 cell only)")
OUT["C3"] = c3
say()

# ---------------------------------------------------------------- C4: two doses cross tau
say("C4. Two doses cross tau, not one")
c4 = {}
for n in ("1", "2", "4"):
    d = reg["rules"]["E152-R1"]["delta_w"][n]
    top = abs(d["mean"]) + d["ci95"]
    c4[n] = {"abs_plus_h_w": top, "minus_tau_w": top - TAU, "pct_C8star": 100 * top / C8S}
    say(f"  n={n}: |delta| + h = {top:.4f} W ({100 * top / C8S:.2f}% of C8*), {top - TAU:+.4f} W against tau {TAU:.4f}"
        + ("  CROSSES" if top > TAU else ""))
OUT["C4"] = c4
say()

# ---------------------------------------------------------------- C5: the footing existed at registration; the noise
say("C5. Q139(u)'s footing existed when E152 registered; how much of the session's noise the 'auto' slope explains")
with open(os.path.join(REG, "README.md")) as f:
    text = f.read()
frozen = text.split("\n## Amendments", 1)[0]
hits = {k: len(re.findall(re.escape(k), frozen)) for k in ("Q139(u)", "0.2056", "footing")}
foot_lines = [ln.strip()[:160] for ln in frozen.splitlines() if "footing" in ln]
say(f"  the registration's text before its Amendments: 'Q139(u)' x{hits['Q139(u)']}, '0.2056' x{hits['0.2056']}, "
    f"'footing' x{hits['footing']}" + "".join(f"; the line: {x}" for x in foot_lines))
br = load(os.path.join(REG, "m8-bridge", "predictions-aifoundry3.json"))
say(f"  m8-bridge (the frozen M8/M7/M6 columns): footing {json.dumps(br['footing']['k_w_per_c'])} W/C, dips "
    f"'{br['footing']['dips']}' (Q139(u)'s footing)")
assert sha256(E127) == pred["price"]["source_sha256"], "E127's scored.json differs from the one the freeze read"
e127q2 = load(E127)["primary"]["contrasts"]["Q2: fp32.q_chk - fp32.q_steady"]["per_pass_w"]
q2 = {"registered": reg["rules"]["E152-S2"]["Q2_w"]["values"], "footing": foot["rules"]["E152-S2"]["Q2_w"]["values"],
      "E127": e127q2}
_, q2r = per_pass_C_from_runs(os.path.join(HERE, "runs.csv"))
assert max(abs(a - b) for a, b in zip(q2r, q2["registered"])) < 1e-9
sd = {k: statistics.stdev(v) for k, v in q2.items()}
excess_reg = sd["registered"] ** 2 - sd["E127"] ** 2
excess_foot = sd["footing"] ** 2 - sd["E127"] ** 2
share = (excess_reg - excess_foot) / excess_reg
say(f"  Q2 (q_chk - q_steady) per-pass sd: registered {sd['registered']:.3f} W, footing {sd['footing']:.3f} W, E127 "
    f"{sd['E127']:.3f} W ({len(e127q2)} passes; E127's sha256 checked): {sd['registered'] / sd['E127']:.1f}x and "
    f"{sd['footing'] / sd['E127']:.1f}x E127's")
say(f"  the variance above E127's: registered {excess_reg:.4f} W^2, footing {excess_foot:.4f} W^2: the footing's slope removes "
    f"{100 * share:.0f}% of it (a point reading from six and five passes' sd)")
OUT["C5"] = {"registration_text_hits": hits, "registration_footing_lines": foot_lines,
             "m8_bridge_footing": br["footing"], "Q2_sd_w": sd, "excess_var_w2": {"registered": excess_reg, "footing": excess_foot},
             "share_removed_by_footing": share}

with open(os.path.join(HERE, "corrections.json"), "w") as f:
    json.dump(OUT, f, indent=1, sort_keys=True)
    f.write("\n")
say()
say("wrote corrections.json")
