#!/usr/bin/env python3
"""E109: corrections after verification (Sun 1 Nov 2026). POST HOC and deciding nothing.

Every number the README's corrections C1-C9 cite that no earlier file prints, computed from committed files only:
posthoc.json, scored.json, scored-3pass.json, e109-3pass.json, logs/e109-queue.out, logs/e109-session.log, and the frozen
tools/claims-v3/e109/predictions-e109.json and desk/bench-arms.json. Nothing touches a card; no reduction is re-run.

    python3 docs/reports/data/2026-11-01-e109-int8-zeros/corrections-check.py     # writes corrections-check.txt and .json beside it

Intervals are 95% t over passes (n = 3: t 4.303; n = 2: t 12.706); the pass is the unit of replication.
Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(HERE, "..", "..", "..", "..", "tools", "claims-v3", "e109")
T95 = {1: 12.706, 2: 4.303, 3: 3.182}


def load(*p):
    return json.load(open(os.path.join(*p)))


def ci(v):
    n = len(v)
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    h = T95[n - 1] * sd / math.sqrt(n)
    return {"mean": m, "half": h, "lo": m - h, "hi": m + h, "n": n, "per_pass": v}


def f(c, k=3, unit="", sign=True):
    return f"{c['mean']:{'+' if sign else ''}.{k}f} ± {c['half']:.{k}f}{(' ' + unit) if unit else ''}"


POST = load(HERE, "posthoc.json")
SC = {"2 kept passes (scored.json)": load(HERE, "scored.json"), "3 passes, gate lifted (scored-3pass.json, post hoc)": load(HERE, "scored-3pass.json")}
PH = {"2 kept passes (scored.json)": POST["registered_reduction"], "3 passes, gate lifted (scored-3pass.json, post hoc)": POST["three_passes_gate_lifted"]}
PRED = load(TOOLS, "predictions-e109.json")
BENCH = load(TOOLS, "desk", "bench-arms.json")["per_op"]
R3P = load(HERE, "e109-3pass.json")

out = {"what": "E109 corrections after verification: post hoc, deciding nothing"}
L = ["E109 CORRECTIONS CHECK (corrections-check.py): post hoc, deciding nothing; mean ± 95% over passes", ""]

# C1: the lanes' price per register-bit clock edge is not one price for both formats
L.append("## C1: the lanes' price on zeros, per register-bit clock edge and per enabled bit, paired by pass")
c1 = {}
for lab, r in PH.items():
    ef, ei = r["U_per_edge_fp32_fj"]["per_pass"], r["U_per_edge_int8_fj"]["per_pass"]
    cf, cl = r["U_per_clocked_fp32_fj"]["per_pass"], r["U_per_clocked_int8_fj"]["per_pass"]
    d = ci([b - a for a, b in zip(ef, ei)])
    q = ci([b / a for a, b in zip(ef, ei)])
    qc = ci([b / a for a, b in zip(cf, cl)])
    c1[lab] = {"edge_fp32_fj": ef, "edge_int8_fj": ei, "edge_int8_minus_fp32_fj": d, "edge_ratio_int8_over_fp32": q,
               "enabled_ratio_int8_over_fp32": qc}
    L.append(f"{lab}:")
    L.append(f"  per edge, fJ, per pass: fp32 {', '.join(f'{x:.3f}' for x in ef)}; int8 {', '.join(f'{x:.3f}' for x in ei)}")
    L.append(f"  int8 - fp32 {f(d, 3, 'fJ')}; int8 / fp32 {f(q, 2, sign=False)} (one price would read 1.00)")
    L.append(f"  per enabled bit, int8 / fp32 per pass {', '.join(f'{x:.2f}' for x in qc['per_pass'])}: {f(qc, 2, sign=False)}")
out["C1"] = c1
L.append("")

# C2: item 15's raw step, and what T takes out of it
L.append("## C2: item 15, a live -0 lane with random B over a constant live lane (pi x pi): the raw step and T")
c2 = {}
for lab, s in SC.items():
    pp = s["per_pass"]
    raw = ci([pp[p]["item15"]["D_a_nz_b_randn"] - pp[p]["item15"]["D_pi"] for p in pp])
    tm = ci([pp[p]["item15"]["T_minus"] for p in pp])
    rest = ci([pp[p]["item15"]["D_a_nz_b_randn"] - pp[p]["item15"]["D_pi"] - pp[p]["item15"]["T_minus"] for p in pp])
    c2[lab] = {"raw_step_w": raw, "T_minus_w": tm, "rest_w": rest, "R8_w": s["rules"]["R8_gated_transport"]["stat"],
               "R8_verdict": s["rules"]["R8_gated_transport"]["verdict"], "posthoc_live_over_constant_w": PH[lab]["live_over_constant_w"]}
    L.append(f"{lab}:")
    L.append(f"  D(a_nz_b_randn) - D(anchor_pi) {f(raw, 3, 'W')}; T_minus (B's bytes to the register files, no micro-op) {f(tm, 3, 'W')}; "
             f"the rest {f(rest, 3, 'W')} (posthoc.txt's live_over_constant {f(PH[lab]['live_over_constant_w'], 3, 'W')})")
    L.append(f"  R8 (random B in the gated lanes beyond T_plus) {f(s['rules']['R8_gated_transport']['stat'], 3, 'W')}: {s['rules']['R8_gated_transport']['verdict']}")
out["C2"] = c2
L.append("")

# C3: the cycle rule carries one fitted constant
L.append("## C3: R6's predictions are the bench's cycles plus one constant fitted on the ordinary op")
c3 = {"delta_cycles_frozen": PRED["delta_cycles"], "fit": {}, "arms": {}}
for fm in ("fp32", "int8"):
    bench = BENCH[f"base.{fm}.zeros"]["cycles"]
    card = R3P["items"][f"{fm}.zeros"]["cycles_per_op"]
    c3["fit"][fm] = {"bench_base_cycles": bench, "card_plain_cycles": card, "card_minus_bench": card - bench}
    L.append(f"{fm}: the ordinary op, card {card} against the bench's {bench}: {card - bench:.3f} cycles (frozen delta {PRED['delta_cycles'][fm]})")
for arm, pr in PRED["rules"]["R6_cycles"]["predicted"].items():
    m = SC["3 passes, gate lifted (scored-3pass.json, post hoc)"]["rules"]["R6_cycles"][arm]["measured"]
    c3["arms"][arm] = {"bench_cycles": BENCH[arm]["cycles"], "predicted": pr, "measured": m, "diff": round(m - pr, 6)}
L.append("the ten arms, none used in the fit: " + "; ".join(f"{a} {v['bench_cycles']} + 7.75 = {v['predicted']} vs {v['measured']}" for a, v in c3["arms"].items()))
L.append(f"largest |measured - predicted|: {max(abs(v['diff']) for v in c3['arms'].values()):.3f} cycles")
out["C3"] = c3
L.append("")

# C4: the per-op price's upper bounds in both readings
L.append("## C4: e_op, the per-op price with no micro-op issued: 95% upper bounds against the ops reading's price")
c4 = {}
for lab, s in SC.items():
    need = s["rules"]["R1_ops"]["reading_e_op_pj"]
    q = s["quantities"]
    c4[lab] = {"reading_e_op_pj": need, **{fm: {"mean": q[fm]["e_op_pj"]["mean"], "half": q[fm]["e_op_pj"]["half"], "upper": q[fm]["e_op_pj"]["hi"]} for fm in ("fp32", "int8")}}
    L.append(f"{lab}: fp32 {f(q['fp32']['e_op_pj'], 1, 'pJ')} (upper {q['fp32']['e_op_pj']['hi']:.0f}); int8 {f(q['int8']['e_op_pj'], 1, 'pJ')} "
             f"(upper {q['int8']['e_op_pj']['hi']:.0f}); the ops reading needs {need:.0f} pJ")
out["C4"] = c4
L.append("")

# C5: the two readings: the means agree, the width moves three verdicts
L.append("## C5: the two readings compared")
two, three = SC["2 kept passes (scored.json)"], SC["3 passes, gate lifted (scored-3pass.json, post hoc)"]
rows, inside = [], 0
for grp, names in (("fp32", list(two["quantities"]["fp32"])), ("int8", list(two["quantities"]["int8"])), ("gap", list(two["gap"])), ("item15", list(two["item15"]))):
    for nm in names:
        a = two["quantities"][grp][nm] if grp in ("fp32", "int8") else two[grp][nm]
        b = three["quantities"][grp][nm] if grp in ("fp32", "int8") else three[grp][nm]
        ok = (b["lo"] <= a["mean"] <= b["hi"]) and (a["lo"] <= b["mean"] <= a["hi"])
        inside += ok
        rows.append({"quantity": f"{grp}.{nm}", "two": [a["mean"], a["half"]], "three": [b["mean"], b["half"]], "each_mean_inside_the_other": ok})
L.append(f"{inside} of {len(rows)} quantities: each reading's mean inside the other's 95% interval")


def verdicts(s):
    r = s["rules"]
    v = {k: r[k]["verdict"] for k in ("R0_answer", "R1_ops", "R2_lanes", "R3_per_time", "R7_sign_unseen", "R8_gated_transport")}
    v["R4_b_reads"] = f"{r['R4_b_reads']['verdict']}; H_reads {r['R4_b_reads']['h_reads']}"
    v.update({f"R5 {fm}": r["R5_additive"][fm]["verdict"] for fm in ("fp32", "int8")})
    v.update({f"R6 {a}": r["R6_cycles"][a]["verdict"] for a in r["R6_cycles"]})
    v.update({f"R10 {c}": r["R10_tie"][c]["verdict"] for c in r["R10_tie"]})
    return v


v2, v3 = verdicts(two), verdicts(three)
moved = {k: [v2[k], v3[k]] for k in v2 if v2[k] != v3[k]}
held = sorted(k for k in v2 if v2[k] == v3[k])
L.append("verdicts that differ (2 kept -> 3 passes): " + "; ".join(f"{k} {a} -> {b}" for k, (a, b) in moved.items()))
L.append(f"verdicts that read the same in both ({len(held)}): " + ", ".join(f"{k} {v2[k]}" for k in held if not k.startswith(("R6 ", "R10 "))) +
         f", R6 x{sum(k.startswith('R6 ') for k in held)}, R10 x{sum(k.startswith('R10 ') for k in held)}")
for k in ("R1_ops",):
    L.append(f"R1's G_op: 2 kept {f(two['rules'][k]['G_op'], 3, 'W')}, 3 passes {f(three['rules'][k]['G_op'], 3, 'W')}, line {two['rules'][k]['line_w']:.3f} / {three['rules'][k]['line_w']:.3f} W")
L.append(f"R8: 2 kept {f(two['rules']['R8_gated_transport']['stat'], 3, 'W')}, 3 passes {f(three['rules']['R8_gated_transport']['stat'], 3, 'W')} (inside ±0.25 W is PASS)")
L.append(f"R5 int8: 2 kept {f(two['rules']['R5_additive']['int8']['stat'], 3, 'W')}, 3 passes {f(three['rules']['R5_additive']['int8']['stat'], 3, 'W')} (inside ±0.15 W is PASS)")
out["C5"] = {"quantities": rows, "inside_count": inside, "n_quantities": len(rows), "verdicts_two": v2, "verdicts_three": v3, "moved": moved}
L.append("")

# C9: what a replicate with a spare pass costs, from this session's own timings
L.append("## C9: the owed replicate's card time, at this session's pace")
q = open(os.path.join(HERE, "logs", "e109-queue.out")).read()
s = open(os.path.join(HERE, "logs", "e109-session.log")).read()


def sec(t):
    h, m, x = (int(y) for y in t.split(":"))
    return h * 3600 + m * 60 + x


t_sess0 = sec(re.search(r"(\d\d:\d\d:\d\d) PST session start", s).group(1))
t_sess1 = sec(re.search(r"(\d\d:\d\d:\d\d) PST session end", s).group(1))
t_q0 = sec(re.search(r"^(\d\d:\d\d:\d\d) e109: start, deadline in (\d+) min", q, re.M).group(1))
dl_min = int(re.search(r"deadline in (\d+) min", q).group(1))
starts = {p: sec(t) for t, p in re.findall(r"^(\d\d:\d\d:\d\d) p(\d+) starts", q, re.M)}
ends = {p: (sec(t), int(d)) for t, p, d in re.findall(r"^(\d\d:\d\d:\d\d) p(\d+) rc=0 \((\d+) s\)", q, re.M)}
t_stop = sec(re.search(r"^(\d\d:\d\d:\d\d) deadline: stopping before p(\d+)", q, re.M).group(1))
passes = sorted(ends)
durs = [ends[p][1] for p in passes]
nxt = [starts[p] for p in passes[1:]] + [t_stop]
gaps = [b - ends[p][0] for p, b in zip(passes, nxt)]
overhead = (t_q0 - t_sess0) + (t_sess1 - t_stop)
used = t_sess1 - t_sess0
warm = sum(durs[1:]) / len(durs[1:])
gap = sum(gaps) / len(gaps)
add_pace, add_long = warm + gap, max(durs) + gap
budget = {n: {"at_warm_pace_min": (used + (n - len(passes)) * add_pace) / 60, "at_longest_pass_min": (used + (n - len(passes)) * add_long) / 60} for n in (3, 4, 5)}
# does E109's own deadline (queue start + 23 min; a pass starts only if now + the longest pass so far fits) admit a fourth pass at this pace?
fits4_real = (t_stop - t_q0) + max(durs) <= dl_min * 60
fits4_even = 3 * add_pace + warm <= dl_min * 60
L.append(f"session {used} s ({used / 60:.1f} card-minutes): smoke and config reads {overhead} s; passes {', '.join(f'{p} {d} s' for p, d in zip(passes, durs))} "
         f"(the first heated from a cold die); {gap:.0f} s after each pass")
for n, b in budget.items():
    L.append(f"{n} passes: about {b['at_warm_pace_min']:.1f} card-minutes at the warm passes' pace ({warm:.0f} s + {gap:.0f} s), "
             f"{b['at_longest_pass_min']:.1f} if every added pass took the longest ({max(durs)} s)")
L.append(f"E109's own {dl_min}-minute queue deadline admits a fourth pass: as it ran {fits4_real}; even with every pass at the warm pace {fits4_even}. "
         f"So E109's frame unchanged runs at most 3 passes, and min_kept_passes is {PRED['min_kept_passes']}: no spare")
out["C9"] = {"session_s": used, "overhead_s": overhead, "passes": dict(zip(passes, durs)), "gaps_s": gaps, "budget_card_minutes": budget,
             "deadline_min": dl_min, "fourth_pass_fits_as_run": fits4_real, "fourth_pass_fits_at_warm_pace": fits4_even,
             "min_kept_passes": PRED["min_kept_passes"], "cap_card_minutes": PRED["cap_card_minutes"]}

json.dump(out, open(os.path.join(HERE, "corrections-check.json"), "w"), indent=1)
open(os.path.join(HERE, "corrections-check.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
