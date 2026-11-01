#!/usr/bin/env python3
"""E87: the data README's tables and the blog's kinds-table cells, formatted from results.json (reduce_e87.py's
output) and this folder's frozen predictions.json. Formatting only: every number is read from those two files. The
one derived column, board pJ per operation, is the sustained board W over the sustained kernel rate, labelled as
derived. Written after the data, beside the registered reduction; it decides nothing.

    python3 tables_e87.py <data>/results.json [--pred predictions.json] [--cells <data>/cells.json] > <data>/tables.md

In cells.json `interval` holds only an uncertainty, as E83 settled after its verification (E83 C3, C7): the runs
themselves (two burst passes; two sustained runs where there are two), or, for a sustained cell of one run, E83's
one-run 1 sigma (15.6 MHz on the slope, i.e. thermal-held above 615 MHz; 5.6 MHz at or near a clamp; board W 0.82 W,
die 0.81 C). The limits get no interval.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
UNIT = {"fp32": "TFLOPS", "fp16": "TFLOPS", "int8": "TOPS"}
SRC = "docs/reports/data/2026-10-31-e87-real-tensors-speed/results.json"
PRED = "tools/claims-v3/kspeed/e87/predictions.json"
COND = ("aifoundry2 card 0, its own governor (65 W / 65 C read at every run, never set; no --reset-ms), 1,024 minions, "
        "one 16x16 TensorFMA repeated on the tile pair; ")
BURST_COND = "burst = one 6 s run from a die <= 55 C, mean clock 1.5 s to the end of the work, two passes in two rounds"
SUS_COND = "sustained = nine 8 s processes from a die <= 57 C, the in-kernel readings of the last 40 s"


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
    order = list(P["tiles"]) + list(P["anchors"])

    def label(k):
        t, n = k.split("/")
        return f"{t} {'real ' if k in P['tiles'] else ''}{n}"

    print("### Speed, power and heat per tile (measured)\n")
    print("| tile | burst MHz (passes) | burst rate | p800 W | burst limit | sustained MHz (runs) | sustained rate "
          "| board W | die °C | limit | c W | board pJ/op (derived) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k in order:
        c = C[k]
        u = UNIT[c["type"]]
        print(f"| {label(k)} | {f(c.get('burst_mhz'))} ({' / '.join(f(x) for x in c.get('burst_mhz_runs', []))}) "
              f"| {f(c.get('burst_rate'), 2)} {u} | {f(c.get('burst_p800_w'), 1)} | {c.get('burst_limit', '–')} "
              f"| {f(c.get('sus_mhz'))} ({' / '.join(f(x) for x in c.get('sus_mhz_runs', []))}) "
              f"| {f(c.get('sus_rate'), 2)} {u} | {f(c.get('sus_w'), 1)} | {f(c.get('sus_die'), 1)} "
              f"| {c.get('sus_limit', '–')} | {f(c.get('c_w'), 2)} | {f(pj(c), 2)} |")
    print("\n### Against Q130(n)'s frozen predictions (Amendment 1's scoring intervals; frozen D-propagated ranges)\n")
    print("| tile | burst | frozen point | scoring | inside | frozen range | sustained | frozen point | scoring | inside "
          "| frozen range | limit (predicted) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k in P["tiles"]:
        c, p = C[k], P["tiles"][k]
        fz, am = p["frozen"], p["amended"]
        bi, si = am["burst_scoring_interval_mhz"], am["sus_scoring_interval_mhz"]
        b, s = c.get("burst_mhz"), c.get("sus_mhz")
        print(f"| {label(k)} | {f(b)} | {fz['burst_mhz']} | {bi[0]}–{bi[1]} "
              f"| {'yes' if b is not None and bi[0] <= b <= bi[1] else 'no'} | {fz['burst_mhz_pi95'][0]}–{fz['burst_mhz_pi95'][1]} "
              f"| {f(s)} | {fz['sus_mhz']} | {si[0]}–{si[1]} | {'yes' if s is not None and si[0] <= s <= si[1] else 'no'} "
              f"| {fz['sus_mhz_pi95'][0]}–{fz['sus_mhz_pi95'][1]} | {c.get('sus_limit', '–')} ({fz['sus_limit']}) |")
    print("\n### Like with like: switching above zeros as a share of the same-session reference (measured c, bursts)\n")
    print("| tile | reference | measured ratio | Q130(n) predicted | S3 interval | frozen interval | c W measured | c W predicted (amended interval) |")
    print("|---|---|---|---|---|---|---|---|")
    LW = R["posthoc"].get("like_with_like_ratios", {})
    for k in P["tiles"]:
        L = P["tiles"][k]["like_with_like"]
        print(f"| {label(k)} | {L['ref_kind']} | {f(LW.get(k), 4)} | {L['ratio_to_ref_measured']:.4f} "
              f"| {L['S3_ratio_interval'][0]}–{L['S3_ratio_interval'][1]} | {L['frozen_ratio_interval'][0]}–{L['frozen_ratio_interval'][1]} "
              f"| {f(C[k].get('c_w'), 3)} | {P['tiles'][k]['frozen']['c_w']} ({P['tiles'][k]['c_amended_interval_w'][0]}–{P['tiles'][k]['c_amended_interval_w'][1]}) |")
    print("\n### Real against random, same session\n")
    print("| format | real tiles' mean burst | randn burst | difference | real mean sustained | randn sustained | difference |")
    print("|---|---|---|---|---|---|---|")
    for row in R["rules"]["E87-S2"]["rows"]:
        if len(row) < 5:
            continue
        x = row[4]
        print(f"| {row[0]} | {f(row[1])} | {f(row[2])} | {f(row[3])} | {f(x.get('beside_sus_real_mean'))} "
              f"| {f(x.get('beside_sus_randn'))} | {f(x.get('beside_sus_diff'))} |")
    i8 = [C[k] for k in P["tiles"] if k.startswith("int8/")]
    full = C.get("int8/full", {})
    if i8 and full.get("sus_mhz") is not None:
        sm = [c["sus_mhz"] for c in i8 if c.get("sus_mhz") is not None]
        bm = [c["burst_mhz"] for c in i8 if c.get("burst_mhz") is not None]
        if sm and bm:
            print(f"| int8 (vs full) | {f(sum(bm) / len(bm))} | {f(full.get('burst_mhz'))} "
                  f"| {f(sum(bm) / len(bm) - full['burst_mhz'])} | {f(sum(sm) / len(sm))} | {f(full['sus_mhz'])} "
                  f"| {f(sum(sm) / len(sm) - full['sus_mhz'])} |")

    if not a.cells:
        return 0
    cells = []

    def add(k, q, v, iv, unit, cond, key):
        t, n = k.split("/")
        cells.append({"format": t, "kind": (f"real GPT-2 {n}" if k in P["tiles"] else n), "quantity": q,
                      "value": v, "interval": iv, "unit": unit, "conditions": COND + cond,
                      "source": f"{SRC} cells['{k}'].{key}"})

    for k in order:
        c = C[k]
        t = c["type"]
        u = UNIT[t]
        if c.get("burst_mhz") is not None:
            runs = c["burst_mhz_runs"]
            add(k, "burst_MHz", c["burst_mhz"], f"passes {' / '.join(f(x) for x in runs)}", "MHz", BURST_COND, "burst_mhz")
            add(k, f"burst_{u}", c["burst_rate"], f"passes {' / '.join(f(x, 3) for x in c['burst_rate_runs'])}", u,
                BURST_COND, "burst_rate")
            add(k, "p800_W", c["burst_p800_w"], f"passes {' / '.join(f(x, 2) for x in c['burst_p800_w_runs'])}",
                "board W at 800 MHz in the first second", BURST_COND, "burst_p800_w")
            add(k, "burst_limit", c["burst_limit"], None, "first throttle-down test",
                BURST_COND + f"; first down per pass {c['burst_first_down']}", "burst_limit")
            add(k, "switching_c_W", c["c_w"], f"passes {' / '.join(f(x, 3) for x in c['c_w_runs'])}",
                "W: whole-board switching term at 600 MHz / 0.517 V referred to 58 C over E64's fitted B_f (not over "
                "idle; not the watts drawn at speed)", BURST_COND, "c_w")
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
            add(k, "limit", c["sus_limit"], None, "sustained limiting test",
                SUS_COND + f"; per run {c['sus_limit_runs']}", "sus_limit")
            p = pj(c)
            if p:
                cells.append({"format": t, "kind": (f"real GPT-2 {k.split('/')[1]}" if k in P["tiles"] else k.split('/')[1]),
                              "quantity": "board_pJ_per_op (derived)", "value": round(p, 3), "interval": None,
                              "unit": "pJ per FLOP" if t != "int8" else "pJ per op",
                              "conditions": COND + SUS_COND + "; derived: board W over the kernel's sustained rate",
                              "source": f"{SRC} cells['{k}'].sus_w / .sus_rate"})
    for k, v in LW.items():
        L = P["tiles"][k]["like_with_like"]
        cells.append({"format": k.split("/")[0], "kind": f"real GPT-2 {k.split('/')[1]}",
                      "quantity": f"switching_share_of_{L['ref_kind'].split('/')[1]}", "value": v,
                      "interval": None, "unit": "(c - c_zeros) / (c_ref - c_zeros), same session",
                      "conditions": COND + BURST_COND + f"; Q130(n) predicted {L['ratio_to_ref_measured']}",
                      "source": f"{SRC} posthoc.like_with_like_ratios['{k}']"})
    json.dump(cells, open(a.cells, "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
