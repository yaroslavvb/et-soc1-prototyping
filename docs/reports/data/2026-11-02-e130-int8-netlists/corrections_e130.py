#!/usr/bin/env python3
"""E130, corrections after verification (Mon 2 Nov 2026): post hoc checks behind the data README's corrections C1-C5.
Nothing here is a registered rule and no verdict moves. Committed files only, standard library only; it imports the
registered scorer and self-test (tools/claims-v3/e130/score_e130.py, selftest_e130.py) unchanged. Run from the repository
root:

    python3 docs/reports/data/2026-11-02-e130-int8-netlists/corrections_e130.py \
        > docs/reports/data/2026-11-02-e130-int8-netlists/corrections_e130.txt

[A] (C1) the rail arm in board units. The rail arm's fJ are rail watts over the same flips and rate, scored by the registered
    code against T_B, T_A, T_S and the netlists' bands, which are board fJ (each netlist's k is fitted on board watts). This
    rescales the rail's intervals by a rail-per-board factor s (board-equivalent fJ = rail fJ / s) and finds where each
    verdict holds as s moves.
[B] (C3) the session's noise like for like: the zeros' scatter about their neighbours' line, the statistic the README quotes
    (0.040 W), in the self-test's own model at several per-run sigma, so the session's scatter is set against the scatter the
    plan's sigma gives, not against sigma itself.
[C] (C5) the die by block: block.json's die_c (lib.sh's 1 s reads) and the telemetry's temp_c.minshire[0].
[D] (C2, C4) the sign bits at each base word and held operand, and E79's at its own word.
[E] (C4) E130-N by arm.
"""
import gzip
import json
import math
import os
import random
import re
import statistics
import sys

ROOT = os.getcwd()
DATA = os.path.join(ROOT, "docs/reports/data/2026-11-02-e130-int8-netlists")
REGDIR = os.path.join(ROOT, "tools/claims-v3/e130")
if not os.path.isfile(os.path.join(REGDIR, "score_e130.py")):
    raise SystemExit("run from the repository root")
sys.path.insert(0, REGDIR)
import score_e130 as sc  # noqa: E402
import selftest_e130 as st  # noqa: E402

S = json.load(open(os.path.join(DATA, "scored.json")))
REG = json.load(open(os.path.join(REGDIR, "predictions-e130.json")))
P = S["primary"]["statistics"]
R = S["arms"]["rail"]["statistics"]
TH = {k: REG["thresholds"][k]["value"] for k in ("T_B", "T_A", "T_S")}
SEP = {"B_odd_minus_even_fJ": "T_B", "A_odd_minus_even_fJ": "T_A", "A_sign_dense_minus_one_fJ": "T_S"}
NETS = ["booth_tree", "booth", "booth_swap", "plain"]
GROUPS = {"BOOTH ON B": ("RECODED", "FLAT", "RISES"), "BOOTH ON A": ("FLAT", "RECODED", "FLAT"),
          "NO BOOTH": ("FLAT", "FLAT", "RISES")}


def f(x, nd=1, sign=True):
    return ("{:+.%df}" % nd).format(x) if sign else ("{:.%df}" % nd).format(x)


def iv(lo, hi, nd=1, sign=True):
    return f"[{f(lo, nd, sign)}, {f(hi, nd, sign)}]"


def rule(lo, hi, t, up, down):
    return up if lo >= t else down if hi <= t else "INCONCLUSIVE"


def r4(v1, v2, v3):
    """E130-R4's group logic as registered (score_e130.py, the registration's decision rules)."""
    got = (v1, v2, v3)
    left = [g for g, want in GROUPS.items() if all(x == "INCONCLUSIVE" or x == w for x, w in zip(got, want))]
    nd = sum(x != "INCONCLUSIVE" for x in got)
    if len(left) == 1:
        return left[0] + ("" if nd == 3 else f" ({nd} of 3 rules decided)")
    if not left:
        return "NONE OF THE FOUR"
    return "INCONCLUSIVE between " + " / ".join(left)


def verdicts_at(s):
    b, a, g = (R[k] for k in ("B_odd_minus_even_fJ", "A_odd_minus_even_fJ", "A_sign_dense_minus_one_fJ"))
    v1 = rule(b["lo"] / s, b["hi"] / s, TH["T_B"], "RECODED", "FLAT")
    v2 = rule(a["lo"] / s, a["hi"] / s, TH["T_A"], "RECODED", "FLAT")
    v3 = rule(g["lo"] / s, g["hi"] / s, TH["T_S"], "RISES", "FLAT")
    return v1, v2, v3, r4(v1, v2, v3)


def overlaps(lo, hi, band):
    return hi >= band["lo"] and lo <= band["hi"]


def ranges(pred, grid):
    """Contiguous runs of the grid where pred(s) is true, as (first, last) s."""
    out, start, prev = [], None, None
    for s in grid:
        ok = pred(s)
        if ok and start is None:
            start = s
        if not ok and start is not None:
            out.append((start, prev))
            start = None
        prev = s
    if start is not None:
        out.append((start, prev))
    return out


def fmt_ranges(rr):
    return ", ".join(f"{a:.3f}-{b:.3f}" for a, b in rr) if rr else "none in 0.10-30"


out = []
w = out.append
w("E130, corrections after verification: post hoc checks (Mon 2 Nov 2026). Nothing here is a registered rule; no verdict moves.")
w("Inputs: scored.json, predictions-e130.json, e130-items.json, aifoundry3/kinds/p130*/block.json and telemetry.jsonl.gz;")
w("the registered score_e130.py and selftest_e130.py imported unchanged.")
w("")

# ---------------------------------------------------------------- [A]
w("## [A] (C1) The rail arm in board units")
crb = None
src = open(os.path.join(ROOT, "tools/claims-v3/kinds/reduce_e78.py")).read()
m = re.search(r'"--c-rb", type=float, default=([0-9.]+), help="([^"]+)"', src)
crb = float(m.group(1))
w(f"E78's frozen rail-per-board constant: reduce_e78.py --c-rb default {crb} (\"{m.group(2)}\").")
lv = {}
for side in ("A", "B"):
    k = f"{side}_mean_bits0to6_fJ"
    rb = sc.fieller(R[k]["per_block"], P[k]["per_block"])
    lv[side] = rb
    w(f"This session's own rail / board on {side}'s bits 0-6 (a level; paired Fieller over {rb['n']} blocks): "
      f"{rb['ratio']:.3f} [{rb['lo']:.3f}, {rb['hi']:.3f}]  (rail {R[k]['mean']:.2f}, board {P[k]['mean']:.2f})")
w("")
w("The rail's separators, in rail fJ as the registered code scored them, and in board-equivalent fJ at s:")
for k, t in SEP.items():
    r = R[k]
    row = [f"  {k}: rail {f(r['mean'])} {iv(r['lo'], r['hi'])} rail-fJ (scored against {t} = {TH[t]:.2f} board-fJ)"]
    for s, why in ((crb, "E78's 0.81"), (lv["A"]["ratio"], "A's own"), (lv["B"]["ratio"], "B's own")):
        row.append(f"    at s = {s:.3f} ({why}): {f(r['mean'] / s)} {iv(r['lo'] / s, r['hi'] / s)}")
    w("\n".join(row))
w("")
b = R["B_odd_minus_even_fJ"]
w(f"R1 at the rail as s moves (closed form): RECODED for s <= {b['lo'] / TH['T_B']:.3f}, INCONCLUSIVE for "
  f"{b['lo'] / TH['T_B']:.3f} < s < {b['hi'] / TH['T_B']:.3f}, FLAT for s >= {b['hi'] / TH['T_B']:.3f}.")
for s, why in ((1.0, "the registered code's implicit 1"), (crb, "E78's frozen"), (lv["A"]["ratio"], "A's own"),
               (lv["B"]["ratio"], "B's own")):
    v = verdicts_at(s)
    w(f"  s = {s:.3f} ({why}): R1 {v[0]}, R2 {v[1]}, R3 {v[2]} -> R4 {v[3]}")
grid = [0.1 * (300 ** (i / 20000)) for i in range(20001)]
w("R2 FLAT for s in " + fmt_ranges(ranges(lambda s: verdicts_at(s)[1] == "FLAT", grid))
  + "; R3 RISES for s in " + fmt_ranges(ranges(lambda s: verdicts_at(s)[2] == "RISES", grid)) + " (grid 0.10-30).")
for g in ("BOOTH ON B", "NO BOOTH"):
    w(f"R4 reads exactly '{g}' (2 of 3 decided or 3 of 3) for s in "
      + fmt_ranges(ranges(lambda s, g=g: verdicts_at(s)[3].split(" (")[0] == g, grid)))
w("R4 reads 'INCONCLUSIVE between BOOTH ON B / NO BOOTH' for s in "
  + fmt_ranges(ranges(lambda s: verdicts_at(s)[3] == "INCONCLUSIVE between BOOTH ON B / NO BOOTH", grid)))
w("")
w("E130-N at the rail as s moves: the s range where the rail's interval overlaps each netlist's band (board fJ):")
for n in NETS:
    bands = REG["netlists"][n]["bands"]
    parts = []
    for k in SEP:
        r = R[k]
        parts.append(f"{k.replace('_fJ', '')} {fmt_ranges(ranges(lambda s, r=r, bd=bands[k]: overlaps(r['lo'] / s, r['hi'] / s, bd), grid))}")
    surv = ranges(lambda s, bands=bands: all(overlaps(R[k]['lo'] / s, R[k]['hi'] / s, bands[k]) for k in SEP), grid)
    w(f"  {n}: " + "; ".join(parts) + f"  -> SURVIVES for s in {fmt_ranges(surv)}")
excl_all = ranges(lambda s: not any(overlaps(R['B_odd_minus_even_fJ']['lo'] / s, R['B_odd_minus_even_fJ']['hi'] / s,
                                             REG['netlists'][n]['bands']['B_odd_minus_even_fJ']) for n in NETS), grid)
w("B's odd - even alone excludes every netlist's band for s in " + fmt_ranges(excl_all) + ".")
w("")
w("The unit-free ratios (no s needed), rail and board, against each netlist's frozen prediction (nets_map; nets_hier):")
for k in ("B_odd_over_even", "A_odd_over_even", "A_sign_dense_over_one"):
    preds = "; ".join(f"{n} {REG['netlists'][n]['stats']['map'][k]:.2f}; {REG['netlists'][n]['stats']['hier'][k]:.2f}"
                      for n in NETS)
    w(f"  {k}: rail {R[k]['ratio']:.2f} [{R[k]['lo']:.2f}, {R[k]['hi']:.2f}], board {P[k]['ratio']:.2f} "
      f"[{P[k]['lo']:.2f}, {P[k]['hi']:.2f}]; {preds}")
w("")

# ---------------------------------------------------------------- [B]
w("## [B] (C3) The session's noise, like for like (the self-test's own model; nothing here is a measurement)")
obs = S["primary"]["zero_residual_sd_W"]
w(f"Session: zeros' scatter about their neighbours' line, board {obs:.4f} W over {S['primary']['zero_residual_n']} interior "
  f"reads (rail {S['arms']['rail']['zero_residual_sd_W']:.4f} W). The planning sigma is a per-run white noise (0.025 W a run).")
SIG = [0.015, 0.020, 0.025, 0.030, 0.0325, 0.035, 0.040]
WORLDS = ["booth_tree", "booth_swap", "plain", "e79", "both"]
NSES = 100
med_sd, med_hw, p05, p95 = {}, {}, {}, {}
for sg in SIG:
    sds, hws = [], {wd: [] for wd in WORLDS}
    for wd in WORLDS:
        for i in range(NSES):
            res, book = st.score_rows(st.session(wd, random.Random(f"E130-C3|{wd}|{sg}|{i}"), sg))
            sds.append(res["zero_residual_sd_W"])
            hws[wd].append(res["statistics"]["B_odd_minus_even_fJ"]["ci95"])
    sds.sort()
    med_sd[sg] = statistics.median(sds)
    p05[sg], p95[sg] = sds[len(sds) // 20], sds[-len(sds) // 20 - 1]
    med_hw[sg] = {wd: statistics.median(v) for wd, v in hws.items()}
    w(f"  sigma {sg:.4f} W a run: zeros' scatter median {med_sd[sg]:.4f} W (5-95% {p05[sg]:.4f}-"
      f"{p95[sg]:.4f}; {len(sds)} sessions, {len(book.zero_resid)} interior reads each); B odd - even "
      f"median half-width " + ", ".join(f"{wd} {med_hw[sg][wd]:.1f}" for wd in WORLDS) + " fJ")
sig_hat = None
for lo_s, hi_s in zip(SIG, SIG[1:]):
    if med_sd[lo_s] <= obs <= med_sd[hi_s]:
        sig_hat = lo_s + (hi_s - lo_s) * (obs - med_sd[lo_s]) / (med_sd[hi_s] - med_sd[lo_s])
w(f"At the planning sigma 0.025 W the model's scatter is {med_sd[0.025]:.4f} W, so the session's {obs:.4f} W is "
  f"{obs / med_sd[0.025]:.2f}x it (against {obs / 0.025:.2f}x when set against sigma itself).")
if sig_hat:
    lo_s = max(s for s in SIG if s <= sig_hat)
    hi_s = min(s for s in SIG if s >= sig_hat)
    hw = {wd: med_hw[lo_s][wd] + (med_hw[hi_s][wd] - med_hw[lo_s][wd]) * (sig_hat - lo_s) / (hi_s - lo_s) for wd in WORLDS}
    w(f"The per-run sigma that gives the session's scatter (linear between grid points): {sig_hat:.4f} W, "
      f"{sig_hat / 0.025:.2f}x the plan's 0.025 W. At that sigma the model's median B odd - even half-width is "
      + ", ".join(f"{wd} {hw[wd]:.1f}" for wd in WORLDS) + " fJ.")
fit = [sg for sg in SIG if p05[sg] <= obs <= p95[sg]]


def cross(xs, ys, y):
    """sigma where the piecewise-linear curve (xs, ys) first crosses y."""
    for x0, x1 in zip(xs, xs[1:]):
        y0, y1 = ys[x0], ys[x1]
        if min(y0, y1) <= y <= max(y0, y1) and y1 != y0:
            return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
    return None


lo_fit, hi_fit = cross(SIG, p95, obs), cross(SIG, p05, obs)
w(f"Per-run sigma whose 5-95% scatter range holds the session's {obs:.4f} W: grid points "
  + ", ".join(f"{s:.4f}" for s in fit) + (f"; edges (linear) {lo_fit:.4f}-{hi_fit:.4f} W" if lo_fit and hi_fit else "")
  + ". One session's scatter pins sigma only that well.")
pb = P["B_odd_minus_even_fJ"]
w(f"The session: B odd - even half-width {pb['ci95']:.1f} fJ over {pb['n']} blocks (per-block sd "
  f"{pb['se'] * math.sqrt(pb['n']):.1f} fJ).")
blocks = pb["per_block"]
w("  per block: " + ", ".join(f"{k} {f(v)}" for k, v in sorted(blocks.items())))
rest = sc.mean_ci([v for k, v in blocks.items() if k != "13010"])
sd_rest = rest["se"] * math.sqrt(rest["n"])
w(f"  without 13010 (post hoc, no rule sets it aside): {f(rest['mean'])} {iv(rest['lo'], rest['hi'])}, half-width "
  f"{rest['ci95']:.1f} fJ over {rest['n']} blocks (per-block sd {sd_rest:.1f} fJ)")
w("")

# ---------------------------------------------------------------- [C]
w("## [C] (C5) The die by block, in session order (degrees C)")
order = [13010, 13020, 13011, 13021, 13012, 13022, 13013, 13023, 13014, 13015]
after = []
for p in order:
    d = os.path.join(DATA, "aifoundry3/kinds", f"p{p}")
    bj = json.load(open(os.path.join(d, "block.json")))
    temps = []
    with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            t = (rec.get("temp_c") or {}).get("minshire")
            if isinstance(t, list) and t and isinstance(t[0], (int, float)):
                temps.append(t[0])
    w(f"  {p}: block.json die_c start {bj.get('die_c_start')}, end {bj.get('die_c_end')}; telemetry minshire[0] "
      f"{min(temps)}-{max(temps)} over {len(temps)} samples")
    if p != order[0]:
        after += temps + [x for x in (bj.get("die_c_start"), bj.get("die_c_end")) if x is not None]
w(f"After the first block (13020 onward): {min(after)}-{max(after)} C.")
w("")

# ---------------------------------------------------------------- [D]
w("## [D] (C2, C4) The sign bits at each base word and held operand (board p_raw, primary; rail beside)")
items = {t["tile"]: t for t in json.load(open(os.path.join(REGDIR, "e130-items.json")))["tiles"]}
PR, RR = S["primary"]["prices"], S["arms"]["rail"]["prices"]
for t in ("a1_7", "a2_7", "a1d_7", "b1_7", "b2_7", "b1d_7"):
    it = items[t]
    held = ("B" if it["side"] == "a" else "A") + " = " + it["held"]
    x, y = PR[t]["fJ"], RR[t]["fJ"]
    w(f"  {t}: side {it['side'].upper()}, base word {it['side'].upper()}{it['base_word']}, held {held}: board "
      f"{f(x['mean'])} {iv(x['lo'], x['hi'])} fJ; rail {f(y['mean'])} {iv(y['lo'], y['hi'])} rail-fJ")
for k in ("A_sign_w2_over_w1", "B_sign_w2_over_w1"):
    w(f"  {k}: board {P[k]['ratio']:.2f} [{P[k]['lo']:.2f}, {P[k]['hi']:.2f}], rail {R[k]['ratio']:.2f} "
      f"[{R[k]['lo']:.2f}, {R[k]['hi']:.2f}] (unit-free)")
a = P["A_mean_bits0to6_fJ"]
w(f"  A's bits 0-6 (held B = 0x1): {f(a['mean'])} {iv(a['lo'], a['hi'])} fJ; A sign, B = 0x55 over B = 1: "
  f"{P['A_sign_dense_over_one']['ratio']:.3f} [{P['A_sign_dense_over_one']['lo']:.3f}, {P['A_sign_dense_over_one']['hi']:.3f}]")
e79 = REG["card_precision_e79"]
w(f"  E79 at its own words (predictions-e130.json card_precision_e79; {e79['source']}): A sign "
  f"{e79['a_list_board_fJ'][7]:+.1f}, B sign {e79['b_list_board_fJ'][7]:+.1f} board fJ")
w("")

# ---------------------------------------------------------------- [E]
w("## [E] (C4) E130-N, each netlist's verdict, primary and every arm (scored.json)")
arms = [("primary", S["primary"])] + list(S["arms"].items())
for n in NETS:
    w(f"  {n}: " + "; ".join(f"{a} {x['netlists'][n]['verdict']}" for a, x in arms))
w("  blocks set aside: " + "; ".join(f"{a} {[y['pass'] for y in x['set_aside']] or 'none'}" for a, x in arms))

print("\n".join(out))
