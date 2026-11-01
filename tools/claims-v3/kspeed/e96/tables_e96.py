#!/usr/bin/env python3
"""E96: the data README's tables and the blog's kinds-table cells, formatted from results.json (reduce_e96.py's output) and this folder's
frozen predictions.json. Formatting only: every number is read from those two files. The one derived column, board pJ per operation, is the
sustained board W over the sustained kernel rate, labelled as derived. It decides nothing.

    python3 tables_e96.py <data>/results.json [--pred predictions.json] [--cells <data>/cells.json] > <data>/tables.md

In cells.json `interval` holds only an uncertainty, as E83 settled after its verification (E83 C3, C7): the runs themselves (two burst passes;
the sustained runs where there are two or more), or, for a sustained cell of one run, E83's one-run 1 sigma (15.6 MHz on the slope, i.e. thermal-held
above 615 MHz; 5.6 MHz at or near a clamp; board W 0.82 W, die 0.81 C). The limits get no interval.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
UNIT = {"fp32": "TFLOPS", "fp16": "TFLOPS", "int8": "TOPS"}
SRC = "docs/reports/data/2026-11-01-e96-real-tensors-speed/results.json"
COND = ("aifoundry2 card 0, its own governor (65 W / 65 C read at every run, never set; no --reset-ms), 1,024 minions, "
        "one 16x16 TensorFMA repeated on the tile pair; ")
BURST_COND = "burst = one 6 s run from a die <= 55 C, mean clock 1.5 s to the end of the work, two passes in two rounds"
SUS_COND = "sustained = nine 8 s processes from a die <= 57 C, the in-kernel readings of the last 40 s"
GROUP = {"Z": "exact zeros (ReLU)", "N": "no exact zeros", "T": "bf16-grid weights", "M": "-0.0", "F": "fp16 forward", "C": "int8 calibration", "B": "bf16 forward"}


def f(x, d=1):
    return "–" if x is None else (f"{x:.{d}f}" if isinstance(x, (int, float)) else str(x))


def pj(c):
    sw, sr = c.get("sus_w"), c.get("sus_rate")
    return sw / sr if (sw and sr) else None          # W / (Tops/s) = pJ per op


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions.json"))
    ap.add_argument("--cells")
    a = ap.parse_args()
    R = json.load(open(a.results))
    P = json.load(open(a.pred))
    U = P["uncertainty_e83"]
    C = R["cells"]
    T = P["tiles"]
    order = list(T) + list(P["arm"]["tiles"]) + list(P["anchors"])
    post = R["posthoc"]

    def label(k):
        t, n = k.split("/")
        return f"{t} {n}"

    print("### Speed, power and heat per tile (measured)\n")
    print("| tile | what | burst MHz (passes) | burst rate | p800 W | burst limit | sustained MHz (runs) | sustained rate | board W | die °C | limit | c W | board pJ/op (derived) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k in order:
        c = C[k]
        u = UNIT[c["type"]]
        what = GROUP.get(T[k]["group"], "") if k in T else ("E87's real int8" if k in P["arm"]["tiles"] else "anchor")
        print(f"| {label(k)} | {what} | {f(c.get('burst_mhz'))} ({' / '.join(f(x) for x in c.get('burst_mhz_runs', []))}) "
              f"| {f(c.get('burst_rate'), 2)} {u} | {f(c.get('burst_p800_w'), 1)} | {c.get('burst_limit', '–')} "
              f"| {f(c.get('sus_mhz'))} ({' / '.join(f(x) for x in c.get('sus_mhz_runs', []))}) "
              f"| {f(c.get('sus_rate'), 2)} {u} | {f(c.get('sus_w'), 1)} | {f(c.get('sus_die'), 1)} "
              f"| {c.get('sus_limit', '–')} | {f(c.get('c_w'), 2)} | {f(pj(c), 2)} |")

    print("\n### Against Q132(r)'s frozen predictions (scoring intervals; the frozen D-propagated ranges beside them)\n")
    print("| tile | burst | frozen | scoring | inside | D range | sustained | frozen | scoring | inside | D range | limit (predicted) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k in T:
        c, z = C[k], T[k]["frozen"]
        bi, si, bd, sd = z["burst_scoring_interval_mhz"], z["sus_scoring_interval_mhz"], z["burst_D_propagated_range_mhz"], z["sus_D_propagated_range_mhz"]
        b, s = c.get("burst_mhz"), c.get("sus_mhz")
        print(f"| {label(k)} | {f(b)} | {z['burst_mhz']} | {bi[0]}–{bi[1]} | {'yes' if b is not None and bi[0] <= b <= bi[1] else 'no'} | {bd[0]}–{bd[1]} "
              f"| {f(s)} | {z['sus_mhz']} | {si[0]}–{si[1]} | {('yes' if si[0] <= s <= si[1] else 'no') if s is not None else '–'} | {sd[0]}–{sd[1]} "
              f"| {c.get('sus_limit', '–')} ({z['sus_limit']}) |")

    print("\n### The gate and the clock: gated tiles against same-session random data of their format\n")
    print("| tile | gate closes | c W measured | c W (a) | c W gate law | burst | − randn | relation on measured c | gate law | sustained | − randn | relation on measured c | gate law |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    diff = {r[0]: r for r in post.get("diff_from_random_rows", [])}
    for k in T:
        if T[k]["gated_lane_frac"] <= 0 or T[k]["type"] == "int8":
            continue
        c, g = C[k], T[k]["gate_law"] or {}
        d = diff.get(k, [None] * 4)
        print(f"| {label(k)} | {T[k]['gated_lane_frac']:.3f} | {f(c.get('c_w'), 2)} | {T[k]['frozen']['c_w']} | {g.get('c_w', '–')} | {f(c.get('burst_mhz'))} | {f(d[2])} "
              f"| {f(c.get('rel_on_measured_c_burst_mhz'))} | {g.get('burst_mhz', '–')} | {f(c.get('sus_mhz'))} | {f(d[3])} | {f(c.get('rel_on_measured_c_sus_mhz'))} | {g.get('sus_mhz', '–')} |")

    print("\n### Real against random, no zero word, and the special cases\n")
    print("| tile | what | burst | − randn | sustained | − randn |")
    print("|---|---|---|---|---|---|")
    for k in T:
        if T[k]["gated_lane_frac"] > 0 or T[k]["type"] == "int8":
            continue
        c = C[k]
        d = diff.get(k, [None] * 4)
        print(f"| {label(k)} | {GROUP.get(T[k]['group'], '')} | {f(c.get('burst_mhz'))} | {f(d[2])} | {f(c.get('sus_mhz'))} | {f(d[3])} |")
    for row in R["rules"]["E96-S3"]["rows"]:
        print(f"| S3 mean, {row[0]} | | {f(row[1])} | {f(row[3])} | | |")

    print("\n### Like with like: switching above zeros as a share of the same-session reference (measured c, bursts)\n")
    print("| tile | reference | measured share | (a) over E78's measured reference | gate law over it | c W measured | c W (a) |")
    print("|---|---|---|---|---|---|---|")
    LW = post.get("like_with_like_ratios", {})
    rows = {r[0]: r for r in post.get("like_with_like_rows", [])}
    for k in T:
        r = rows.get(k, [None] * 4)
        print(f"| {label(k)} | {T[k]['ref_kind']} | {f(LW.get(k), 4)} | {f(r[2], 4)} | {f(r[3], 4)} | {f(C[k].get('c_w'), 3)} | {T[k]['frozen']['c_w']} |")
    for k in P["arm"]["tiles"]:
        if LW.get(k) is not None:
            print(f"| {label(k)} | int8/full | {f(LW.get(k), 4)} | – | – | {f(C[k].get('c_w'), 3)} | – |")

    print("\n### The int8 arm, by round: sustained MHz, board W, die °C, limit\n")
    D = post.get("arm_rounds_detail", {})
    kinds = [P["arm"]["ref"]] + list(P["arm"]["tiles"])
    print("| round | " + " | ".join(label(k) for k in kinds) + " | mean(real) − full, MHz |")
    print("|---|" + "---|" * (len(kinds) + 1))
    i1 = R["rules"]["E96-I1"]
    whole = post.get("arm_rows", {}).get("whole_rounds", [])
    for r in sorted(D, key=int):
        cols = []
        for k in kinds:
            x = D[r].get(k)
            cols.append(f"{f(x['mhz'])} / {f(x['w'], 2)} / {f(x['die'], 1)} / {x['limit']}" if x else "–")
        dv = i1["rounds"][whole.index(int(r))] if i1.get("rounds") and int(r) in whole else None
        print(f"| {r} | " + " | ".join(cols) + f" | {f(dv)} |")
    print()
    for name in ("E96-I1", "E96-I2", "E96-I3"):
        v = R["rules"][name]
        print(f"- **{name}**: {v.get('verdict')}; mean {v.get('mean')}, 95% [{v.get('lo')}, {v.get('hi')}], n {v.get('n')}" + (f", at the cap {v.get('at_the_cap')}" if name == "E96-I1" else ""))
    lab = post.get("arm_labelled") or {}
    for k, v in (lab.get("per_tile_clock") or {}).items():
        print(f"- labelled, {label(k)} − full: mean {v['mean']} MHz, 95% [{v['lo']}, {v['hi']}], reads {v['reads']}")
    for name, key, unit in (("clock with dips left out", "clock_dips_left_out", "MHz"), ("fine W at 800 MHz", "fine_w_at_800", "W"), ("clock, pooled two-way", "clock_pooled_two_way", "MHz")):
        v = lab.get(key)
        if v:
            print(f"- labelled, {name}: mean {v['mean']} {unit}, 95% [{v['lo']}, {v['hi']}], reads {v.get('reads')}" + (f" ({v['df']} df, residual sd {v['residual_sd']})" if "df" in v else ""))
    if lab.get("run_sd_pooled_mhz") is not None:
        print(f"- labelled, one run's sd in this arm, pooled over the kinds: {lab['run_sd_pooled_mhz']} MHz; per kind {lab['run_sd_mhz']}")

    print("\n### The heat path\n")
    L, Q = post.get("die_line_e96") or {}, post.get("line_at_e98_k") or {}
    print(f"- die line, all sustained runs: die = {L.get('a_c')} + {L.get('k_c_per_w')} W, rms {L.get('rms_c')} °C, n {L.get('n')}, shift at E80's slope {L.get('shift_c_at_e80_slope')} °C (E87's: {P['line']['e87_die_line']['shift_c_at_e80_slope']})")
    print(f"- E98's line, die − {Q.get('k_c_per_w')} W, over {Q.get('kinds_shared_with_e98')}: {Q.get('mean_over_shared_kinds_c')} °C (E87's {Q.get('e87_same_kinds_c')}, difference {Q.get('difference_from_e87_c')}); over all runs {Q.get('mean_over_all_runs_c')}; trend {Q.get('trend_c_per_min')} °C/min")
    print(f"- a-adj E96: W* {(post.get('a_adj_e96') or {}).get('W_star_adj_w')} W, sustained rms on the frozen c {(post.get('a_adj_e96') or {}).get('sus_rms_frozen_c_mhz')}, on the measured c {(post.get('a_adj_e96') or {}).get('sus_rms_measured_c_mhz')} MHz")
    for name, v in (post.get("rest") or {}).items():
        print(f"- rest, {name}: {json.dumps(v)}")

    if not a.cells:
        return 0
    cells = []

    def add(k, q, v, iv, unit, cond, key):
        t, n = k.split("/")
        kind = f"real {n}" if k in T or k in P["arm"]["tiles"] else n
        cells.append({"format": t, "kind": kind, "quantity": q, "value": v, "interval": iv, "unit": unit, "conditions": COND + cond,
                      "source": f"{SRC} cells['{k}'].{key}"})

    for k in order:
        c = C[k]
        t = c["type"]
        u = UNIT[t]
        if c.get("burst_mhz") is not None:
            runs = c["burst_mhz_runs"]
            add(k, "burst_MHz", c["burst_mhz"], f"passes {' / '.join(f(x) for x in runs)}", "MHz", BURST_COND, "burst_mhz")
            add(k, f"burst_{u}", c["burst_rate"], f"passes {' / '.join(f(x, 3) for x in c['burst_rate_runs'])}", u, BURST_COND, "burst_rate")
            add(k, "p800_W", c["burst_p800_w"], f"passes {' / '.join(f(x, 2) for x in c['burst_p800_w_runs'])}", "board W at 800 MHz in the first second", BURST_COND, "burst_p800_w")
            add(k, "burst_limit", c["burst_limit"], None, "first throttle-down test", BURST_COND + f"; first down per pass {c['burst_first_down']}", "burst_limit")
            add(k, "switching_c_W", c["c_w"], f"passes {' / '.join(f(x, 3) for x in c['c_w_runs'])}",
                "W: whole-board switching term at 600 MHz / 0.517 V referred to 58 C over E64's fitted B_f (not over idle; not the watts drawn at speed)", BURST_COND, "c_w")
        if c.get("sus_mhz") is not None:
            runs = c["sus_mhz_runs"]
            if len(runs) >= 2:
                iv_m = f"runs {' / '.join(f(x) for x in runs)}"
                iv_w = f"runs {' / '.join(f(x, 2) for x in c['sus_w_runs'])}"
                iv_d = f"runs {' / '.join(f(x, 2) for x in c['sus_die_runs'])}"
                iv_r = f"runs {' / '.join(f(x, 3) for x in c['sus_rate_runs'])}"
            else:
                slope = c.get("sus_limit") == "thermal" and c["sus_mhz"] > 615
                sg = U["sus_one_run_sigma_mhz_slope"] if slope else U["sus_one_run_sigma_mhz_clamp"]
                iv_m = f"one run; 1 sigma +-{sg} MHz ({'slope' if slope else 'clamp'}, E83 C3)"
                iv_w = f"one run; 1 sigma +-{U['sus_board_w_sigma']} W (E83 C3)"
                iv_d = f"one run; 1 sigma +-{U['sus_die_c_sigma']} C (E83 C3)"
                iv_r = f"one run; 1 sigma +-{round(c['sus_rate'] * sg / c['sus_mhz'], 3)} (the clock's sigma, scaled)"
            add(k, "sustained_MHz", c["sus_mhz"], iv_m, "MHz", SUS_COND, "sus_mhz")
            add(k, f"sustained_{u}", c["sus_rate"], iv_r, u, SUS_COND, "sus_rate")
            add(k, "board_W", c["sus_w"], iv_w, "board W (in-kernel mean, last 40 s)", SUS_COND, "sus_w")
            add(k, "die_C", c["sus_die"], iv_d, "C (die, in-kernel mean, last 40 s)", SUS_COND, "sus_die")
            add(k, "limit", c["sus_limit"], None, "sustained limiting test", SUS_COND + f"; per run {c['sus_limit_runs']}", "sus_limit")
            p = pj(c)
            if p:
                n = k.split("/")[1]
                cells.append({"format": t, "kind": (f"real {n}" if k in T or k in P["arm"]["tiles"] else n), "quantity": "board_pJ_per_op (derived)", "value": round(p, 3),
                              "interval": None, "unit": "pJ per FLOP" if t != "int8" else "pJ per op", "conditions": COND + SUS_COND + "; derived: board W over the kernel's sustained rate",
                              "source": f"{SRC} cells['{k}'].sus_w / .sus_rate"})
    for k, v in LW.items():
        n = k.split("/")[1]
        ref = T[k]["ref_kind"] if k in T else "int8/full"
        pr = T[k]["ratio_to_ref_measured_e78"] if k in T else None
        cells.append({"format": k.split("/")[0], "kind": f"real {n}", "quantity": f"switching_share_of_{ref.split('/')[1]}", "value": v, "interval": None,
                      "unit": "(c - c_zeros) / (c_ref - c_zeros), same session", "conditions": COND + BURST_COND + (f"; Q132(r) predicted {pr} (over E78's measured reference)" if pr is not None else ""),
                      "source": f"{SRC} posthoc.like_with_like_ratios['{k}']"})
    json.dump(cells, open(a.cells, "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
