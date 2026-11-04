#!/usr/bin/env python3
"""E160 (Q139): corrections after verification. POST HOC, never a verdict. Written at the desk on Tue 3 Nov 2026, about 17:20 PST, by the fix pass,
after an independent verifier re-derived every registered number and verdict (all stand) and reported seven minor faults in what the README and the
lane's result draw from them. Nothing here was registered; nothing frozen, measured or registered changes.

Inputs, all committed: this directory's results.json (the registered reduction, its committed cells and run rows) and posthoc-more.json; the frozen
tools/claims-v3/e160/predictions-e160.json; E143's results.json and posthoc-corrections.json. The registered reducer's own functions
(tools/claims-v3/e160/reduce_e160.py: score and scale, with their seeds) are called on results.json's committed cells, so a corrected figure differs
from a registered one only by the change named. Standard library otherwise.

    python3 docs/reports/data/2026-11-03-e160-blind6-aifoundry2/corrections_e160.py > docs/reports/data/2026-11-03-e160-blind6-aifoundry2/corrections.txt

  C1  fp16's burst D and the fp16 zeros anchor's idle pass. The burst D is "the mean over passes of burst_w less the burst_w of the same type's zeros
      anchor IN THE SAME PASS" (reduce_e160.py). fp16.anchor6_zeros's pass 1 carried a mid-burst POWER_IDLE status (posthoc-more.txt (M1)) and ran at
      752 MHz. Here pass 1's reference is the anchor's two 800 MHz passes' mean instead (passes 2 and 3 keep their own), and the reducer's score() is
      re-run on the cells with only the fp16 tiles' D changed: every fp16 tile's D, the burst-D sets, the fp16 zeros offset (M3) and M3's own-zeros
      figure; the rank-5 scale, which uses the clock-normalized c, beside it. The anchor's own pass-1 samples at 800 MHz (p800_w) give a cross-check.
  C2  the previous out-of-sample score on this card, E143's (M7 blind on pool 5, Mon 2 Nov), beside E160's (M8 blind on pool 6), with M7 on pool 6 and
      the in-sample reference; the pinned clock and board with the two idle passes set aside (the board's is new here, as (M4) did for the clock)
  C5  the kinds-table cells: every interval is the range of the tile's 3 passes (min, max), not a confidence interval; fp16's switching_W cells as
      C1; the cells of the three tiles whose pass 1 carried the idle status are flagged
  C7  what the M8 - M7 intervals are over (tiles, inside one session) and how far the session's capped level sits from the caps fitted on other
      sessions; E143's capped tiles beside

SPDX-License-Identifier: Apache-2.0
"""
import copy
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "e160"))
import reduce_e160 as RE  # noqa: E402  (the registered reducer: score, scale, paired_boot, rms_ci; nothing is collected or re-read)

REL = "docs/reports/data/2026-11-03-e160-blind6-aifoundry2"
E143 = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e143-blind5-aifoundry2")
R = json.load(open(os.path.join(HERE, "results.json")))
PM = json.load(open(os.path.join(HERE, "posthoc-more.json")))
P = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "e160", "predictions-e160.json")))
R143 = json.load(open(os.path.join(E143, "results.json")))
PC143 = json.load(open(os.path.join(E143, "posthoc-corrections.json")))
T = R["score"]["reported"]["tiles"]
GOV = RE.C.GOVERNED_BELOW_MHZ
out = {"note": "post hoc, written after verification on Tue 3 Nov 2026; never a verdict; no frozen, measured or registered number changes"}


def r(x, n=3):
    return None if x is None else round(x, n)


def rms(xs):
    xs = [x for x in xs if x is not None]
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else None


def canon(x):
    return json.dumps(x, sort_keys=True)


# ---------------------------------------------------------------- C1
print("E160 CORRECTIONS AFTER VERIFICATION (post hoc, labelled). Errors are measured - predicted. No registered number or verdict changes.")
print("\nC1. FP16'S BURST D AND THE FP16 ZEROS ANCHOR'S IDLE PASS")
mp = P["rules"]["min_passes"]
cells0 = R["cells"]
S0 = RE.score(copy.deepcopy(cells0), P, mp)
same_score = canon(S0) == canon(R["score"])
same_scale = canon(RE.scale(copy.deepcopy(cells0), P)) == canon(R["scale"])
print(f"  check: the registered reducer's score() and scale() on results.json's committed cells reproduce results.json's score: {same_score}, scale: {same_scale}")

ALAB = "b6-fp16.anchor6_zeros"
a = cells0[ALAB]
apass = dict(zip(a["passes"], a["burst_w_runs"]))
amhz = dict(zip(a["passes"], a["burst_mhz_runs"]))
ac = dict(zip(a["passes"], a["c_w_runs"]))
a800p = dict(zip(a["passes"], a["p800_w_runs"]))
good = [p for p in a["passes"] if amhz[p] >= GOV]
bad = [p for p in a["passes"] if amhz[p] < GOV]
ref800 = st.mean(apass[p] for p in good)
refc = st.mean(ac[p] for p in good)
short = {p: ref800 - apass[p] for p in bad}
mean_shift = sum(short.values()) / len(a["passes"])
alt = {p: a800p[p] - apass[p] for p in bad}
alt_shift = sum(alt.values()) / len(a["passes"])
anchor = {"tile": "fp16.anchor6_zeros", "passes": a["passes"], "burst_mhz_runs": a["burst_mhz_runs"], "burst_w_runs": a["burst_w_runs"],
          "p800_w_runs": a["p800_w_runs"], "c_w_runs": a["c_w_runs"], "passes_at_800": good, "passes_below_795": bad,
          "w_at_800_passes": r(ref800, 3), "pass_short_w": {str(p): r(v, 3) for p, v in short.items()}, "mean_D_shift_w": r(mean_shift, 3),
          "crosscheck_own_800_samples": {"pass_p800_w": {str(p): a800p[p] for p in bad}, "pass_short_w": {str(p): r(v, 3) for p, v in alt.items()},
                                         "mean_D_shift_w": r(alt_shift, 3)},
          "c_at_800_passes": r(refc, 3)}
print(f"  the anchor fp16.anchor6_zeros: clock {a['burst_mhz_runs']} MHz, board {a['burst_w_runs']} W, its samples at 800 MHz (p800_w) {a['p800_w_runs']} W, "
      f"c {a['c_w_runs']} W")
print(f"  pass 1's reference, the anchor's two 800 MHz passes' mean: {ref800:.3f} W; pass 1 read {', '.join(f'{v:.3f}' for v in short.values())} W short, "
      f"so every fp16 tile's 3-pass mean D is {mean_shift:.3f} W high")
print(f"  cross-check, pass 1's own samples at 800 MHz: {', '.join(str(a800p[p]) for p in bad)} W, {', '.join(f'{v:.3f}' for v in alt.values())} W short, "
      f"mean D {alt_shift:.3f} W high")
out["C1_anchor"] = anchor

cells1 = copy.deepcopy(cells0)
rows = {}
print("  every fp16 tile's burst D (W): registered (passes) -> corrected (passes); M8 / M7 / M6 predicted; M8's error registered -> corrected")
for lab, c in sorted(cells0.items()):
    if c.get("type") != "fp16" or lab == ALAB or not c.get("name"):
        continue
    W = dict(zip(c["passes"], c["burst_w_runs"]))
    reg = [W[p] - apass[p] for p in c["passes"]]
    cor = [W[p] - (ref800 if p in bad else apass[p]) for p in c["passes"]]
    assert [round(x, 3) for x in reg] == c["D_runs"], lab
    n = c["name"]
    pm = {m: P["tiles"][n]["models"][m]["burst_D_w"] for m in RE.MODELS}
    dw = st.mean(cor)
    rows[n] = {"D_w_registered": c["D_w"], "D_runs_registered": c["D_runs"], "D_w_corrected": r(dw, 3), "D_runs_corrected": [r(x, 3) for x in cor],
               "D_runs_corrected_range": [r(min(cor), 3), r(max(cor), 3)], "shift_w": r(dw - c["D_w"], 3),
               **{f"{m}_D_w": pm[m] for m in RE.MODELS}, "M8_err_registered": r(c["D_w"] - pm["M8"], 3), "M8_err_corrected": r(dw - pm["M8"], 3),
               "M7_err_corrected": r(dw - pm["M7"], 3), "M6_err_corrected": r(dw - pm["M6"], 3), "group": c["group"]}
    cells1[lab]["D_runs"] = [round(x, 3) for x in cor]
    cells1[lab]["D_w"] = round(dw, 3)
    print(f"    {n:34s} {c['group']:8s} {c['D_w']:7.3f} {c['D_runs']} -> {dw:7.3f} {[round(x, 2) for x in cor]};  {pm['M8']:.2f} / {pm['M7']:.2f} / {pm['M6']:.2f};"
          f"  {c['D_w'] - pm['M8']:+.3f} -> {dw - pm['M8']:+.3f}")
out["C1_fp16_tiles"] = rows

S1 = RE.score(copy.deepcopy(cells1), P, mp)
rules_same = canon(S1["rules"]) == canon(R["score"]["rules"])
nonD_same = all(S1["reported"]["by_set"][s][k] == v for s, row in R["score"]["reported"]["by_set"].items() for k, v in row.items() if "_D_" not in k)
print(f"  unchanged by it (checked): every rule (F1-F3, W1-W3, H1, H3, PK): {rules_same}; every clock, board and rise figure of every set: {nonD_same}")
sets = {}
print("  the burst-D sets, re-scored by the registered score() (same seeds): rms M8 / M7 / M6 registered -> corrected; M8 - M7 and M8 - M6, 95% over tiles")
for s, row in R["score"]["reported"]["by_set"].items():
    new = S1["reported"]["by_set"][s]
    if all(new[k] == row[k] for k in row if "_D_" in k):
        continue
    ks = ["M8_D_rms", "M7_D_rms", "M6_D_rms", "M8_D_mean", "M7_D_mean", "M6_D_mean", "M8_minus_M7_D_rms_95", "M8_minus_M6_D_rms_95", "M8_D_inside"]
    sets[s] = {"registered": {k: row[k] for k in ks}, "corrected": {k: new[k] for k in ks}}
    print(f"    {s:18s} {row['M8_D_rms']:.2f} / {row['M7_D_rms']:.2f} / {row['M6_D_rms']:.2f} -> {new['M8_D_rms']:.2f} / {new['M7_D_rms']:.2f} / {new['M6_D_rms']:.2f};"
          f"  M8-M7 {row['M8_minus_M7_D_rms_95']} -> {new['M8_minus_M7_D_rms_95']};  M8-M6 {row['M8_minus_M6_D_rms_95']} -> {new['M8_minus_M6_D_rms_95']};"
          f"  M8 mean {row['M8_D_mean']:+.3f} -> {new['M8_D_mean']:+.3f}")
out["C1_burst_D_sets"] = sets
out["C1_unchanged"] = {"rules": rules_same, "clock_board_rise_sets": nonD_same, "score_reproduces": same_score, "scale_reproduces": same_scale}

# the rank-5 scale (reported, NOT SCORED): it uses c, the clock-normalized power, not the board W
cells2 = copy.deepcopy(cells0)
for lab, c in cells2.items():
    if c.get("type") != "fp16" or lab == ALAB or not c.get("name"):
        continue
    cw = dict(zip(c["passes"], c["c_w_runs"]))
    cz = [cw[p] - (refc if p in bad else ac[p]) for p in c["passes"] if cw.get(p) is not None]
    c["c_minus_zeros_w"] = round(st.mean(cz), 4)
sc2 = RE.scale(cells2, P)
scale_c = {"registered": {k: R["scale"][k] for k in ("floats|M8_predicted_D600", "int8|M8_predicted_D600")},
           "pass1_c_at_800_passes": {k: sc2[k] for k in ("floats|M8_predicted_D600", "int8|M8_predicted_D600")},
           "anchor_c_w_runs": a["c_w_runs"], "anchor_c_at_800_passes": r(refc, 3)}
print(f"  the rank-5 scale (reported) uses c, the clock-normalized power: the anchor's pass-1 c is {ac[1]} W against {', '.join(str(ac[p]) for p in good)} W at 800 MHz,"
      f" so it is not biased low; with pass 1's c replaced by the 800 MHz passes' mean ({refc:.3f} W) the floats median reads "
      f"{sc2['floats|M8_predicted_D600']['median']} (n {sc2['floats|M8_predicted_D600']['n']}) against the registered {R['scale']['floats|M8_predicted_D600']['median']}; int8 "
      f"{sc2['int8|M8_predicted_D600']['median']} (unchanged)")
out["C1_scale_rank5"] = scale_c

# M3: the fp16 zeros offset and the own-zeros-level figure
m3 = PM["M3_what_M8_leaves"]["pinned"]
own_reg = m3["own_zeros_offset_w"]
own800 = {}
for ty in ("fp32", "fp16", "int8"):
    t = T[f"{ty}.anchor6_zeros"]
    w800 = [w for w, f in zip(t["burst_w_runs"], t["burst_mhz_runs"]) if f >= GOV]
    own800[ty] = st.mean(w800) - P["tiles"][f"{ty}.anchor6_zeros"]["models"]["M8"]["burst_board_w"]
pin = sorted(n for n, t in T.items() if t["group"] == "pinned")
nz = [n for n in pin if not n.endswith("anchor6_zeros")]
e = {n: T[n]["burst_w"] - P["tiles"][n]["models"]["M8"]["burst_board_w"] for n in pin}
reg_own = [e[n] - own_reg[P["tiles"][n]["type"]] for n in nz]
cor_own = [e[n] - own800[P["tiles"][n]["type"]] for n in nz]
assert abs(rms(reg_own) - m3["nonzeros_rms_w_with_own_zeros_anchor"]) < 1e-3
m3c = {"own_zeros_offset_w_registered": own_reg, "own_zeros_offset_w_at_800_passes": {k: r(v, 3) for k, v in own800.items()},
       "anchors_under_M8_at_800_w": [r(min(-v for v in own800.values()), 2), r(max(-v for v in own800.values()), 2)],
       "nonzeros_n": len(nz), "nonzeros_rms_w_with_own_zeros_anchor": {"registered": m3["nonzeros_rms_w_with_own_zeros_anchor"], "at_800_passes": r(rms(cor_own), 3)},
       "nonzeros_mean_w_with_own_zeros_anchor": {"registered": m3["nonzeros_mean_w_with_own_zeros_anchor"], "at_800_passes": r(st.mean(cor_own), 3)},
       "fp16_nonzeros_pinned": [n for n in nz if P["tiles"][n]["type"] == "fp16"]}
print(f"  the zeros anchors' offset from M8's level (M3): registered {json.dumps(own_reg)}; over their 800 MHz passes "
      f"{json.dumps({k: r(v, 3) for k, v in own800.items()})}: the three anchors {m3c['anchors_under_M8_at_800_w'][0]}-{m3c['anchors_under_M8_at_800_w'][1]} W under M8 at 800 MHz")
print(f"  M3's own zeros level on the {len(nz)} pinned tiles that are not zeros: rms {m3['nonzeros_rms_w_with_own_zeros_anchor']} -> {rms(cor_own):.3f} W, "
      f"mean {m3['nonzeros_mean_w_with_own_zeros_anchor']:+.3f} -> {st.mean(cor_own):+.3f} W (fp16's three: {', '.join(m3c['fp16_nonzeros_pinned'])})")
out["C1_M3_zeros_level"] = m3c

# the other tiles whose own pass 1 carried the idle status (M1): flagged, not corrected (no registered rule sets a pass aside)
idle = [x["run"] for x in PM["M1_mid_burst_idle"]["E160"]["which"]]
own_idle = {}
for x in R["run_rows"]:
    if x["run"] in idle:
        n = x["label"][3:]
        t = T[n]
        others = [(f, w) for f, w, p in zip(t["burst_mhz_runs"], t["burst_w_runs"], t["passes"]) if p != x["pass"]]
        own_idle[n] = {"run": x["run"], "pass": x["pass"], "burst_mhz": x["burst_mhz"], "burst_w": x["burst_w"],
                       "other_passes_mhz": [f for f, _ in others], "other_passes_w": [w for _, w in others]}
        print(f"  idle pass (M1) {x['run']}: {x['burst_mhz']} MHz, {x['burst_w']} W; the tile's other passes {[f for f, _ in others]} MHz, {[w for _, w in others]} W")
out["C1_idle_passes"] = own_idle

# ---------------------------------------------------------------- C2
print("\nC2. THE PREVIOUS OUT-OF-SAMPLE SCORE ON THIS CARD: E143 (M7 blind on pool 5, Mon 2 Nov evening) BESIDE E160 (M8 blind on pool 6, Tue 3 Nov morning)")
iv143 = PC143["1_blind_rms_intervals"]
rr = R["score"]["rules"]
bs = R["score"]["reported"]["by_set"]
# the pinned clock and board with the two pinned idle passes set aside (the clock is (M4)'s; the board is new here, the same rule)
w2 = []
for n in pin:
    t = T[n]
    kept = [w for w, p in zip(t["burst_w_runs"], t["passes"]) if not any(x.endswith(f"-b6-{n}-r{p}") for x in idle)]
    w2.append(st.mean(kept) - P["tiles"][n]["models"]["M8"]["burst_board_w"])
m4 = PM["M4_F2_without_idle_passes"]
cmp_rows = []
for q, s, k143, k160, setname, mk in (("clock MHz", "governed", "E143-F1", "E160-F1", "governed", "mhz"), ("clock MHz", "pinned", "E143-F2", "E160-F2", "pinned", "mhz"),
                                      ("board W", "governed", "E143-W1", "E160-W1", "governed", "w"), ("board W", "pinned", "E143-W2", "E160-W2", "pinned", "w"),
                                      ("die rise C", "all", "E143-H1", "E160-H1", "all", "rise")):
    a143, a160 = iv143[k143], rr[k160]
    row = {"quantity": q, "set": s, "E143_M7_blind": {"n": a143["n"], "rms": a143["rms"], "rms_95": a143["rms_95"], "verdict": a143["registered_verdict"]},
           "E160_M8_blind": {"n": a160["n"], "rms": a160["rms"], "rms_95": a160["rms_95_over_tiles"], "verdict": a160["verdict"]},
           "E160_M7_same_tiles": bs[setname][f"M7_{mk}_rms"], "in_sample_reference_M8": rr[k160]["ref_rms"],
           "E160_minus_E143": r(a160["rms"] - a143["rms"], 3)}
    cmp_rows.append(row)
    print(f"  {q:10s} {s:8s}  E143 M7 n {a143['n']:2d} {a143['rms']:6.3f} {a143['rms_95']}  |  E160 M8 n {a160['n']:2d} {a160['rms']:6.3f} {a160['rms_95_over_tiles']}"
          f"  (M7 on the same tiles {bs[setname][f'M7_{mk}_rms']})  |  in-sample reference {rr[k160]['ref_rms']}  |  E160 - E143 {a160['rms'] - a143['rms']:+.3f}")
for k in ("all 36 clock", "all 36 board"):
    a143 = iv143[k]
    mk = "mhz" if "clock" in k else "w"
    print(f"  {k:19s}  E143 M7 {a143['rms']} {a143['rms_95']}  |  E160 M8 all 48 {bs['all'][f'M8_{mk}_rms']} {bs['all'][f'M8_{mk}_rms_95']}  (M7 {bs['all'][f'M7_{mk}_rms']})")
idle_aside = {"pinned_clock_mhz_rms": m4["rms_mhz_with_them_set_aside"], "pinned_board_w_rms": r(rms(w2), 3), "pinned_board_w_mean": r(st.mean(w2), 3),
              "set_aside_runs": m4["set_aside_runs"]}
print(f"  pinned, the two idle passes set aside (post hoc): clock {m4['rms_mhz_with_them_set_aside']} MHz ((M4)), board {rms(w2):.3f} W (mean {st.mean(w2):+.3f}) against E143's 1.007 MHz and 1.184 W")
out["C2_previous_blind_score"] = {"rows": cmp_rows, "all": {k: iv143[k] for k in ("all 36 clock", "all 36 board")},
                                  "E160_all_48": {"mhz": [bs["all"]["M8_mhz_rms"], bs["all"]["M8_mhz_rms_95"]], "w": [bs["all"]["M8_w_rms"], bs["all"]["M8_w_rms_95"]],
                                                  "rise": [bs["all"]["M8_rise_rms"], bs["all"]["M8_rise_rms_95"]]},
                                  "E160_pinned_idle_passes_set_aside": idle_aside,
                                  "E143_source": "docs/reports/data/2026-11-02-e143-blind5-aifoundry2/results.json score.rules; posthoc-corrections.json 1_blind_rms_intervals"}

# ---------------------------------------------------------------- C5
print("\nC5. THE KINDS-TABLE CELLS")
cond = ("aifoundry2 card 0 under its own governor (65 W / 65 C read, never set), 6 s bursts of one 16x16 TensorFMA on 1,024 minions, die start <= 55 C, "
        "3 passes, every launch's C bit-exact")
IV = "range of the 3 passes (min, max), not a confidence interval"
src = f"{REL}/results.json score.reported.tiles"
csrc = f"{REL}/corrections.json C1_fp16_tiles"
flag = {n: f"pass {v['pass']} carried a mid-burst POWER_IDLE status ({v['burst_mhz']} MHz; posthoc-more.txt (M1)); the value includes it, as registered"
        for n, v in own_idle.items()}
cells = []


def spread(xs):
    xs = [x for x in xs if x is not None]
    return [min(xs), max(xs)]


def add(**k):
    k.setdefault("interval_kind", IV)
    k.setdefault("conditions", cond)
    cells.append(k)


for n, t in sorted(T.items()):
    fmt, kind = n.split(".", 1)
    note = {"note": flag[n]} if n in flag else {}
    add(format=fmt, kind=kind, quantity="burst_MHz", value=t["burst_mhz"], interval=spread(t["burst_mhz_runs"]), unit="MHz", source=f"{src}.{n}.burst_mhz", **note)
    add(format=fmt, kind=kind, quantity="board_W", value=t["burst_w"], interval=spread(t["burst_w_runs"]), unit="W", source=f"{src}.{n}.burst_w", **note)
    if t.get("D_w") is not None and not n.endswith("anchor6_zeros"):
        if n in rows:
            nn = {"note": "corrected after verification: pass 1 against the fp16 zeros anchor's two 800 MHz passes (its pass 1 carried a mid-burst idle status), "
                          f"{rows[n]['shift_w']:+.3f} W from the registered {rows[n]['D_w_registered']} W" + (f"; {flag[n]}" if n in flag else "")}
            add(format=fmt, kind=kind, quantity="switching_W", value=rows[n]["D_w_corrected"], interval=rows[n]["D_runs_corrected_range"],
                unit="W (burst board W over the fp16 zeros anchor: the same pass's, pass 1's from its two 800 MHz passes)", source=f"{csrc}.{n}.D_w_corrected", **nn)
        else:
            add(format=fmt, kind=kind, quantity="switching_W", value=t["D_w"], interval=spread(t["D_runs"]), unit="W (burst board W over the same pass's zeros anchor)",
                source=f"{src}.{n}.D_w", **note)
    add(format=fmt, kind=kind, quantity="die_rise_C", value=t["rise_c"], interval=spread(t["rise_runs"]), unit="C (die max - die start in a 6 s burst)",
        source=f"{src}.{n}.rise_c", **note)
    add(format=fmt, kind=kind, quantity="peak_board_W", value=max(x for x in t["peak_w_runs"] if x is not None), interval=spread(t["peak_w_runs"]),
        unit="W (the highest board sample)", source=f"{src}.{n}.peak_w_runs", **note)
byq = {}
for c in cells:
    byq[(c["format"], c["quantity"])] = byq.get((c["format"], c["quantity"]), 0) + 1
print(f"  {len(cells)} cells, every interval the {IV}; fp16 switching_W {byq[('fp16', 'switching_W')]} cells from C1; "
      f"{sum(1 for c in cells if 'note' in c and 'POWER_IDLE' in c['note'])} cells of {len(flag)} tiles flagged for their idle pass")
out["C5_table_cells"] = {"interval": IV, "n": len(cells), "cells": cells}

# ---------------------------------------------------------------- C7
print("\nC7. WHAT THE M8 - M7 INTERVALS ARE OVER")
m3a = PM["M3_what_M8_leaves"]
W0, WSTAR = P["relation"]["W0_w"], 65.58008573814928   # M8's refitted cap; M7's (m8.json aifoundry2.M7_frozen.W_star_w), as posthoc_more_e160.py
T143 = R143["score"]["reported"]["tiles"]
P143 = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "e143", "predictions-e143.json")))
cap143 = [T143[n]["burst_w"] for n in T143 if P143["tiles"][n]["models"]["M7"]["burst_board_w"] >= WSTAR - 0.1 and T143[n]["burst_w"] is not None]
die = PM["M2_session_vs_E143"]["die_at_burst_start"]
c7 = {"interval_over": "a paired percentile bootstrap over tiles inside one session (reduce_e160.py paired_boot, 5000 draws, seed 1601 + n): it carries the tiles' "
                       "spread, not the session-to-session movement of the effective cap",
      "governed_M8_minus_M7_mhz_rms_95": bs["governed"]["M8_minus_M7_mhz_rms_95"], "governed_M8_minus_M7_w_rms_95": bs["governed"]["M8_minus_M7_w_rms_95"],
      "all_M8_minus_M7_mhz_rms_95": bs["all"]["M8_minus_M7_mhz_rms_95"], "all_M8_minus_M7_w_rms_95": bs["all"]["M8_minus_M7_w_rms_95"],
      "E160_capped_tiles": {"n": m3a["capped_tiles"], "mean_w": m3a["capped_measured_board_mean_w"], "range_w": m3a["capped_measured_board_range_w"],
                            "over_M8_cap_w": m3a["against_M8_cap_w"], "over_M7_cap_w": m3a["against_M7_cap_w"]},
      "E143_capped_tiles_M7": {"n": len(cap143), "mean_w": r(st.mean(cap143), 3) if cap143 else None, "over_M7_cap_w": r(st.mean(cap143) - WSTAR, 3) if cap143 else None,
                               "rule": "M7's predicted board W at or within 0.1 W of its cap 65.58 W (predictions-e143.json)"},
      "caps_w": {"M8_refit_on_95_bursts_E80_E83_E143": r(W0, 2), "M7": r(WSTAR, 2)},
      "die_at_burst_start_mean_c": {"E160": die["E160"]["all_mean_c"], "E143": die["E143"]["all_mean_c"]},
      "governed_mean_clock_err_mhz": {"E143_M7_on_its_governed": R143["score"]["rules"]["E143-F1"]["mean_err"],
                                      "E160_M7_on_its_governed": bs["governed"]["M7_mhz_mean"], "E160_M8_on_its_governed": bs["governed"]["M8_mhz_mean"]},
      "same_tile_vs_E143": PM["M2_session_vs_E143"]["replicates_vs_E143"]}
print(f"  the intervals are {c7['interval_over']}")
print(f"  governed M8 - M7: clock {c7['governed_M8_minus_M7_mhz_rms_95']} MHz rms, board {c7['governed_M8_minus_M7_w_rms_95']} W; all 48: clock {c7['all_M8_minus_M7_mhz_rms_95']},"
      f" board {c7['all_M8_minus_M7_w_rms_95']}")
print(f"  this session's capped tiles (M8 at its cap): {m3a['capped_tiles']}, mean {m3a['capped_measured_board_mean_w']} W ({m3a['capped_measured_board_range_w']}), "
      f"{m3a['against_M8_cap_w']:+.3f} W over M8's cap {W0:.2f} W (refitted on E80's, E83's and E143's 95 bursts), {m3a['against_M7_cap_w']:+.3f} W over M7's {WSTAR:.2f} W")
if cap143:
    print(f"  E143's capped tiles (M7 at its cap): {len(cap143)}, mean {st.mean(cap143):.3f} W, {st.mean(cap143) - WSTAR:+.3f} W over M7's cap")
print(f"  the die at the bursts' start, mean over bursts: E160 {die['E160']['all_mean_c']} C, E143 {die['E143']['all_mean_c']} C")
g = c7["governed_mean_clock_err_mhz"]
print(f"  the same model in two sessions: M7 as frozen read E143's governed tiles {g['E143_M7_on_its_governed']:+.2f} MHz (measured - predicted, mean) and E160's "
      f"{g['E160_M7_on_its_governed']:+.2f} MHz; M8 E160's {g['E160_M8_on_its_governed']:+.2f} MHz")
rp = c7["same_tile_vs_E143"]["k-fp16-randn"]
print(f"  the same tile in both sessions (E80's fp16 random): {rp['E160_mhz']} against {rp['E143_mhz']} MHz ({rp['d_mhz']:+.2f}) at {rp['E160_w']} against {rp['E143_w']} W "
      f"({rp['d_w']:+.3f}); so the session moved the clock at the same watts, and the capped tiles' board held about the same level in both")
out["C7_one_session"] = c7

json.dump(out, open(os.path.join(HERE, "corrections.json"), "w"), indent=1)
