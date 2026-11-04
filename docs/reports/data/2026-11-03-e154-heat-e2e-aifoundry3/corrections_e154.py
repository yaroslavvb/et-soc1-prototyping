#!/usr/bin/env python3
"""E154 (Q139): the numbers of the corrections after verification. POST HOC, never a verdict. Desk only (the Intel).

Written Tue 3 Nov 2026, about 19:50-20:30 PST, by the fix pass, after the data, the post hoc readings and the verifier's report. It
reads committed files only and imports the registered scorer tools/claims-v3/e154/score_e154.py, which checks the sha256 of its 13
frozen inputs on import and imports score_e144.py unchanged. Every reading below uses the registered machinery's own functions (the
frozen chain, score_e144's arm (a), arm (b) and traj); nothing is fitted or tuned, and no registered number, rule or verdict changes.

  C0   the registered scorer, re-run in memory on pass 15420, gives scored.json's plateau errors and session figure, so every
       number below stands on the same footing as the registered ones
  C1   the critic's rank-4 rule with both of its conditions: the plateau error AND the checkpoints' rms within the hold's
       critic_scale_C (Q139(e)'s frozen table), per pool-6 hold; then the same at the critic's flat "about 0.35 C"
  C2   arm A (the frozen chain on the measured board trace, score_e144's arm (a)) read at arm E's own checkpoints and windows, per
       hold, H_M included; arm A's plateau error as a share of the measured rise; E - A at each checkpoint; E144's two holds of
       2 Nov on this card beside (its committed scored.json)
  C3   the absolute die over each hold's last 300 s, predicted from R0's room (the closed loop arm E runs) against the measured
       one, for M8, M7, M6 and E153's measured S, with each hold's anchor error (measured minus predicted rest die)
  C4   each pool-6 hold's carried-in tail, its measured rest die above R0, and arm E restarted at its own rest (posthoc.json)
  C7   where the samples' since_reset_ms comes from (the sampler's own line)
  C9   the rule of the tile K_O holds (blind6.json)
  C11  (c)'s rise per board W for every hold and H_M's t63, as score_e144 computed them (E144's rules, not E154's)
  C12  process launches against dispatches, smoke and pass

    /usr/bin/python3 docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/corrections_e154.py
writes corrections.json and corrections.txt beside this file. numpy 1.26.4, Python 3.9.6 (the Intel's /usr/bin/python3).
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "e154"))
import score_e154 as sc  # noqa: E402  checks the 13 frozen inputs' sha256 on import; imports score_e144 unchanged

se = sc.se
hm = se.hm
ft = se.ft

PASS = os.path.join(HERE, "aifoundry3", "e154", "p15420")
SMOKE = os.path.join(HERE, "aifoundry3", "e154-smoke", "p15401")
SCORED = json.load(open(os.path.join(HERE, "scored.json")))
POSTHOC = json.load(open(os.path.join(HERE, "posthoc.json")))
E144 = json.load(open(os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e144-heat-minutes", "scored.json")))
BLIND6 = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "kinds", "blind6", "blind6.json")))
SAMPLER = os.path.join(ROOT, "tools", "claims-v3", "e89", "pvt_sample.py")
POOL6 = list(sc.POOL6)
HOLDS = ["H_M"] + POOL6
FLAT = 0.35            # the critic's "about 0.35 C on aifoundry3" (critic-q138, open rank 4, next_test)


def r3(x, n=3):
    return None if x is None else round(float(x), n)


def rms(xs):
    xs = [float(x) for x in xs]
    return math.sqrt(sum(x * x for x in xs) / len(xs))


def jl(p):
    return [json.loads(x) for x in open(p) if x.strip()]


problems = []
out = {"note": "POST HOC: the numbers the data README's 'Corrections after verification' quotes; never a verdict. Written by the fix "
               "pass, Tue 3 Nov 2026, after the data and the verifier's report.",
       "frozen_inputs_checked": len(sc.FROZEN)}

# ---------------------------------------------------------------------------------------------------------------- C0
sess = se.a3_load([PASS])
res = {m: {r["hold"]: r for r in sc.score_with(sess, m)["holds"]} for m in sc.MODELS}
c0 = {}
for nm in HOLDS:
    rE = res["M8"][nm]
    want_e = (SCORED["holds"][nm]["E_end_to_end"] if nm in POOL6 else SCORED["holds"][nm]["H_M_b_E78_S"])["plateau_err_C"]
    want_a = SCORED["holds"][nm]["A_given_watts"]["plateau_err_C"]
    got_e, got_a = r3(rE["b"]["plateau_err_C"]), r3(rE["a"]["plateau_err_C"])
    c0[nm] = {"E_or_b_plateau_err_C": got_e, "A_plateau_err_C": got_a, "as_scored": [want_e, want_a]}
    if got_e != want_e or got_a != want_a:
        problems.append(f"C0 {nm}: re-run {got_e}/{got_a} != scored.json {want_e}/{want_a}")
fig = {m: r3(rms([res[m][nm]["b"]["plateau_err_C"] for nm in POOL6])) for m in sc.MODELS}
fig["A_given_watts"] = r3(rms([res["M8"][nm]["a"]["plateau_err_C"] for nm in POOL6]))
want_fig = SCORED["session_figure"]["rms_plateau_err_C"]
for m, k in (("M8", "E_M8"), ("M7", "M7"), ("M6", "M6"), ("E153", "E153_measured_S"), ("A_given_watts", "A_given_watts")):
    if fig[m] != want_fig[k]:
        problems.append(f"C0 session figure {m}: {fig[m]} != {want_fig[k]}")
out["C0_reproduces_scored_json"] = {"holds": c0, "session_rms_plateau_err_C": fig}

# ---------------------------------------------------------------------------------------------------------------- C1
c1 = {}
for nm in POOL6:
    e = SCORED["holds"][nm]["E_end_to_end"]
    pe, tr, cs = e["plateau_err_C"], e["checkpoint_rms_C"], e["critic_scale_C"]
    c1[nm] = {"plateau_err_C": pe, "checkpoint_rms_C": tr, "critic_scale_C": cs,
              "plateau_within": abs(pe) <= cs, "rms_within": tr <= cs, "both_within (the critic's rule)": abs(pe) <= cs and tr <= cs,
              "flat_0.35_plateau_within": abs(pe) <= FLAT, "flat_0.35_both_within": abs(pe) <= FLAT and tr <= FLAT}
keys = ["plateau_within", "rms_within", "both_within (the critic's rule)", "flat_0.35_plateau_within", "flat_0.35_both_within"]
out["C1_the_critics_rule"] = {"holds": c1, "count_of_4": {k: sum(1 for nm in POOL6 if c1[nm][k]) for k in keys},
                              "which": {k: [nm for nm in POOL6 if c1[nm][k]] for k in keys},
                              "rule": "rms and plateau within sqrt(chain^2 + (R x power rms)^2), about 0.35 C on aifoundry3 (critic-q138, "
                                      "open rank 4); critic_scale_C is Q139(e)'s frozen per-hold value of it"}

# ---------------------------------------------------------------------------------------------------------------- C2
g, T = sess["g"], sess["T"]
pred_a = ft.predict_session(sess, se.TAU, se.R3)          # score_e144's arm (a): the frozen chain on the measured board trace
c2 = {}
for h in sess["holds"]:
    nm = h["name"]
    rE = res["M8"][nm]
    w = rE["b"]["window_s"]                                 # arm E's own checkpoint window (5 s; K_S one launch period)
    anc = hm.anchor_value(g, T, pred_a, h["anchor_end"])    # as score_hold anchors arm (a)
    tm = se.traj(g, T, h, w)
    ta = se.traj(g, pred_a + anc, h, w)
    cpa = {k: tm["rise_C_by_s"][k] - ta["rise_C_by_s"][k] for k in tm["rise_C_by_s"] if k == "end" or int(k) >= 60}
    pa = tm["plateau_rise_C"] - ta["plateau_rise_C"]
    if abs(pa - rE["a"]["plateau_err_C"]) > 1e-6:
        problems.append(f"C2 {nm}: arm A plateau at E's windows {pa} != the registered arm (a) {rE['a']['plateau_err_C']}")
    cpe = rE["b"]["checkpoint_err_C"]
    c2[nm] = {"item": h["item"], "window_s": r3(w), "measured_plateau_rise_C": r3(tm["plateau_rise_C"]),
              "A_plateau_err_C": r3(pa), "A_plateau_err_share_of_rise": r3(pa / tm["plateau_rise_C"], 4),
              "A_checkpoint_err_C": {k: r3(v) for k, v in cpa.items()}, "A_checkpoint_rms_C": r3(rms(cpa.values())),
              ("E_checkpoint_err_C" if nm in POOL6 else "b_from_E78_S_checkpoint_err_C"): cpe,
              ("E_minus_A_checkpoint_C" if nm in POOL6 else "b_minus_A_checkpoint_C"): {k: r3(cpe[k] - cpa[k]) for k in cpe if k in cpa},
              "A_registered": {"rms_C_over_every_sample": r3(rE["a"]["rms_C"]),
                               "err_at_s_10s_means": {k: r3(v) for k, v in rE["a"]["err_at_s"].items()}}}
big = [nm for nm in HOLDS if c2[nm]["measured_plateau_rise_C"] > 10]
small = [nm for nm in HOLDS if c2[nm]["measured_plateau_rise_C"] <= 10]
e144 = {}
for hh in E144["holds"]:
    e144[hh["hold"]] = {"item": hh["item"], "share": r3(hh["share_recorded"], 4), "rest_die_C": r3(hh["rest_die_C"]),
                        "measured_plateau_rise_C": r3(hh["b"]["measured"]["plateau_rise_C"]),
                        "A_plateau_err_C": r3(hh["a"]["plateau_err_C"]),
                        "A_plateau_err_share_of_rise": r3(hh["a"]["plateau_err_C"] / hh["b"]["measured"]["plateau_rise_C"], 4)}
out["C2_arm_A_at_arm_E_checkpoints"] = {
    "holds": c2,
    "large_rises_over_10C": {"holds": big, "A_plateau_err_C": [c2[n]["A_plateau_err_C"] for n in big],
                             "share_of_rise": [c2[n]["A_plateau_err_share_of_rise"] for n in big]},
    "small_rises": {"holds": small, "A_plateau_err_C": [c2[n]["A_plateau_err_C"] for n in small],
                    "share_of_rise": [c2[n]["A_plateau_err_share_of_rise"] for n in small]},
    "E144_same_card_2_Nov": e144,
    "definition": "arm A's error = the measured die minus the frozen chain on the measured board, anchored on the 120 s before the "
                  "hold (score_e144 arm (a)), read with arm E's traj windows: means over w s at 60, 120, 180, 300, 450 (600) s and "
                  "the end; the plateau (last 300 s) equals the registered arm (a) plateau exactly. The registered arm (a) rms is over "
                  "every sample of the hold, so it differs from the checkpoints' rms here."}

# ---------------------------------------------------------------------------------------------------------------- C3
c3 = {}
for m in sc.MODELS:
    rows = {}
    for nm in HOLDS:
        b = res[m][nm]["b"]
        ma = b["measured"]["base_C"] + b["measured"]["plateau_rise_C"]
        pa_ = b["predicted"]["base_C"] + b["predicted"]["plateau_rise_C"]
        rows[nm] = {"measured_die_last300s_C": r3(ma), "predicted_die_last300s_C": r3(pa_), "abs_err_C": r3(ma - pa_),
                    "anchor_err_C": r3(b["measured"]["base_C"] - b["predicted"]["base_C"]), "rise_err_C": r3(b["plateau_err_C"])}
        if m == "M8" and abs(ma - POSTHOC["holds"][nm]["measured_die_last300s_C"]) > 0.0015:
            problems.append(f"C3 {nm}: measured die {ma} != posthoc.json {POSTHOC['holds'][nm]['measured_die_last300s_C']}")
    c3[m] = {"holds": rows,
             "pool6_rms_abs_err_C": r3(rms([rows[nm]["abs_err_C"] for nm in POOL6])),
             "pool6_mean_abs_err_C": r3(float(np.mean([rows[nm]["abs_err_C"] for nm in POOL6]))),
             "pool6_rms_rise_err_C": r3(rms([rows[nm]["rise_err_C"] for nm in POOL6]))}
rank_abs = sorted(sc.MODELS, key=lambda m: c3[m]["pool6_rms_abs_err_C"])
rank_rise = sorted(sc.MODELS, key=lambda m: c3[m]["pool6_rms_rise_err_C"])
out["C3_absolute_die_plateau"] = {"models": c3, "ranking_best_first": {"absolute_die": rank_abs, "rise_over_anchor": rank_rise},
                                  "anchor_err_range_C_M8_pool6": [min(c3["M8"]["holds"][nm]["anchor_err_C"] for nm in POOL6),
                                                                  max(c3["M8"]["holds"][nm]["anchor_err_C"] for nm in POOL6)],
                                  "definition": "the die's mean over the hold's last 300 s, measured, against the closed loop from R0's "
                                                "rest die on the realized records (arm E's machinery) for each model's S; abs_err = "
                                                "rise_err + anchor_err, where anchor_err is the measured minus the predicted mean over "
                                                "the 120 s before the hold (the chain's tail error there)"}

# ---------------------------------------------------------------------------------------------------------------- C4
r0 = SCORED["session"]["rest_die_R0_C"]
out["C4_tails"] = {nm: {"carried_in_C": SCORED["holds"][nm]["E_predicted_M8"]["carried_in_C"],
                        "rest_die_above_R0_C": r3(SCORED["holds"][nm]["rest_die_C"] - r0),
                        "E_from_own_rest_plateau_err_C": POSTHOC["holds"][nm]["E_from_own_rest_plateau_err_C"]} for nm in HOLDS}
out["C4_tails"]["pool6_holds_on_a_tail"] = sum(1 for nm in POOL6 if SCORED["holds"][nm]["E_predicted_M8"]["carried_in_C"] > 0.5)

# ---------------------------------------------------------------------------------------------------------------- C7
lines = open(SAMPLER).read().splitlines()
hits = [(i + 1, s.strip()) for i, s in enumerate(lines) if "since_reset_ms" in s]
out["C7_since_reset_ms"] = {"file": "tools/claims-v3/e89/pvt_sample.py", "lines": hits,
                            "reading": "the sampler writes the field as a constant on every tick, so it says nothing about what was sent"}

# ---------------------------------------------------------------------------------------------------------------- C9
tiles = BLIND6["tiles"]
t_ko = tiles["fp32.a_onebit_b5_third"] if isinstance(tiles, dict) else [t for t in tiles if t.get("name") == "fp32.a_onebit_b5_third"][0]
out["C9_K_O_tile_rule"] = {"name": "fp32.a_onebit_b5_third", "rule": t_ko["rule"], "case": t_ko.get("case")}

# ---------------------------------------------------------------------------------------------------------------- C11
c11 = {}
for nm in HOLDS:
    c = SCORED["holds"][nm]["c_per_board_W_last300s"]
    c11[nm] = {"per_board_W_C_per_W": r3(c["per_board_W"]), "interval": [r3(x) for x in c["interval"]], "rise_C": r3(c["rise_C"]),
               "board_rise_W": r3(c["board_rise_W"]), "score_e144_verdict_E144_rule": c["verdict"]}
t63 = SCORED["holds"]["H_M"]["H_M_c_t63"]
out["C11_c_readings"] = {"per_board_W_last300s": c11,
                         "H_M_t63": {"t63_s": r3(t63["t63_s"], 1), "closed_loop_t63_s": t63["closed_loop_t63_s"],
                                     "ratio": r3(t63["ratio"]), "score_e144_verdict_E144_rule": t63["verdict"]},
                         "E144_rule": {"per_board_W": "PASS in [0.80, 0.94]; FAIL if the interval lies outside [0.74, 1.00] "
                                                      "(score_e144.C3_PBW)", "t63": "PASS in [0.75, 1.33] (score_e144.C3_T63)"}}

# ---------------------------------------------------------------------------------------------------------------- C12
pm, sm = jl(os.path.join(PASS, "marks.jsonl")), jl(os.path.join(SMOKE, "marks.jsonl"))
pr, sr = jl(os.path.join(PASS, "runs.jsonl")), jl(os.path.join(SMOKE, "runs.jsonl"))
cc = json.load(open(os.path.join(HERE, "ccheck", "ccheck-all.json")))["summary"]
sg = json.load(open(os.path.join(HERE, "logs", "smoke-gate.json")))
lp = sum(1 for m in pm if m.get("kind") == "launch")
ls = sum(1 for m in sm if m.get("kind") == "launch")
per_hold = {m["name"]: m.get("launches") for m in pm if m.get("kind") == "hold"}
out["C12_counts"] = {"pass_15420": {"process_launches": lp, "dispatches": len(pr), "launches_per_hold": per_hold},
                     "smoke_15401": {"process_launches": ls, "dispatches": len(sr), "smoke_gate_c_log": sg["c_log"]},
                     "total": {"process_launches": lp + ls, "dispatches": len(pr) + len(sr)},
                     "ccheck_all_summary": {"launches_field_counts_dispatches": cc["launches"], "PASS": cc["PASS"],
                                            "by_type": {k: v["PASS"] for k, v in cc["by_type"].items()}}}
if len(pr) + len(sr) != cc["launches"]:
    problems.append(f"C12: dispatches {len(pr) + len(sr)} != ccheck's {cc['launches']}")

out["problems"] = problems
out["ok"] = not problems


# ---------------------------------------------------------------------------------------------------------------- the printout
def fmt(x):
    return "—" if x is None else (f"{x:+.3f}" if isinstance(x, float) else str(x))


P = []
P.append("E154 corrections after verification: POST HOC, never a verdict (corrections_e154.py; committed inputs only)")
P.append(f"frozen inputs checked by score_e154 on import: {len(sc.FROZEN)}; problems: {problems or 'none'}")
P.append("")
P.append("C0  the registered scorer re-run in memory on p15420 (plateau errors, C): E (b for H_M) / A")
for nm in HOLDS:
    P.append(f"    {nm}: {fmt(c0[nm]['E_or_b_plateau_err_C'])} / {fmt(c0[nm]['A_plateau_err_C'])}   scored.json {c0[nm]['as_scored']}")
P.append(f"    session rms over the 4 pool-6 holds: {fig}")
P.append("")
P.append("C1  the critic's rule (plateau AND checkpoints' rms within critic_scale_C), arm E (M8)")
for nm in POOL6:
    x = c1[nm]
    P.append(f"    {nm}: plateau {fmt(x['plateau_err_C'])}, rms {x['checkpoint_rms_C']:.3f}, scale {x['critic_scale_C']:.3f}: plateau "
             f"{'in' if x['plateau_within'] else 'OUT'}, rms {'in' if x['rms_within'] else 'OUT'}, both "
             f"{'PASS' if x['both_within (the critic' + chr(39) + 's rule)'] else 'no'}; at a flat 0.35: plateau "
             f"{'in' if x['flat_0.35_plateau_within'] else 'OUT'}, both {'PASS' if x['flat_0.35_both_within'] else 'no'}")
P.append(f"    counts of 4: {out['C1_the_critics_rule']['count_of_4']}")
P.append(f"    which: {out['C1_the_critics_rule']['which']}")
P.append("")
P.append("C2  arm A (the chain given the measured board) at arm E's checkpoints (C, measured minus predicted rise)")
for nm in HOLDS:
    x = c2[nm]
    cpa = " ".join(f"{k}:{v:+.3f}" for k, v in x["A_checkpoint_err_C"].items())
    ek = "E_minus_A_checkpoint_C" if nm in POOL6 else "b_minus_A_checkpoint_C"
    ema = " ".join(f"{k}:{v:+.3f}" for k, v in x[ek].items())
    P.append(f"    {nm} ({x['item']}, rise {x['measured_plateau_rise_C']:.3f}, w {x['window_s']} s): A plateau {fmt(x['A_plateau_err_C'])} "
             f"= {100 * x['A_plateau_err_share_of_rise']:.1f}% of the rise; A checkpoints' rms {x['A_checkpoint_rms_C']:.3f}")
    P.append(f"        A   {cpa}")
    P.append(f"        {'E-A' if nm in POOL6 else 'b-A'} {ema}")
P.append(f"    large rises (> 10 C) {big}: A {out['C2_arm_A_at_arm_E_checkpoints']['large_rises_over_10C']['A_plateau_err_C']}, "
         f"share {out['C2_arm_A_at_arm_E_checkpoints']['large_rises_over_10C']['share_of_rise']}")
P.append(f"    small rises {small}: A {out['C2_arm_A_at_arm_E_checkpoints']['small_rises']['A_plateau_err_C']}, "
         f"share {out['C2_arm_A_at_arm_E_checkpoints']['small_rises']['share_of_rise']}")
for k, v in e144.items():
    P.append(f"    E144 (2 Nov, this card) {k} {v['item']} share {v['share']} from a {v['rest_die_C']} C rest: rise "
             f"{v['measured_plateau_rise_C']:.3f}, A plateau {fmt(v['A_plateau_err_C'])} ({100 * v['A_plateau_err_share_of_rise']:.2f}%)")
P.append("")
P.append("C3  the absolute die over the last 300 s, from R0's room (C): measured, predicted, abs error = rise error + anchor error")
for m in sc.MODELS:
    rr = c3[m]["holds"]
    P.append(f"    {m}: " + "; ".join(f"{nm} {rr[nm]['measured_die_last300s_C']:.3f} vs {rr[nm]['predicted_die_last300s_C']:.3f} "
                                       f"= {rr[nm]['abs_err_C']:+.3f} ({rr[nm]['rise_err_C']:+.3f} {rr[nm]['anchor_err_C']:+.3f})"
                                       for nm in POOL6))
    P.append(f"        pool-6 rms: absolute {c3[m]['pool6_rms_abs_err_C']:.3f} (mean {c3[m]['pool6_mean_abs_err_C']:+.3f}), "
             f"rise {c3[m]['pool6_rms_rise_err_C']:.3f}")
P.append(f"    H_M (from rest, E78's S in every arm): {c3['M8']['holds']['H_M']}")
P.append(f"    ranking, best first: absolute {rank_abs}; rise {rank_rise}")
P.append("")
P.append("C4  tails (C): carried-in (the chain), measured rest die above R0, arm E restarted at the hold's own rest")
for nm in HOLDS:
    x = out["C4_tails"][nm]
    P.append(f"    {nm}: {x['carried_in_C']}, {x['rest_die_above_R0_C']}, {x['E_from_own_rest_plateau_err_C']}")
P.append(f"    pool-6 holds that started on a tail: {out['C4_tails']['pool6_holds_on_a_tail']} of 4")
P.append("")
P.append(f"C7  {SAMPLER[len(ROOT) + 1:]}: {hits}")
P.append("")
P.append(f"C9  fp32.a_onebit_b5_third: {t_ko['rule']}")
P.append("")
P.append("C11 (c) per board W over the last 300 s (C/W) [interval], score_e144's verdict by E144's rule (not an E154 rule)")
for nm in HOLDS:
    x = c11[nm]
    P.append(f"    {nm}: {x['per_board_W_C_per_W']:.3f} [{x['interval'][0]:.3f}, {x['interval'][1]:.3f}] "
             f"(rise {x['rise_C']:.3f} C / board {x['board_rise_W']:.3f} W): {x['score_e144_verdict_E144_rule']}")
P.append(f"    H_M t63: {out['C11_c_readings']['H_M_t63']}")
P.append("")
P.append(f"C12 counts: {json.dumps(out['C12_counts'])}")

txt = "\n".join(P) + "\n"
open(os.path.join(HERE, "corrections.txt"), "w").write(txt)
open(os.path.join(HERE, "corrections.json"), "w").write(
    json.dumps(out, indent=1, default=lambda o: float(o) if isinstance(o, np.floating) else (bool(o) if isinstance(o, np.bool_) else str(o)))
    + "\n")
print(txt)
if problems:
    sys.exit(1)
