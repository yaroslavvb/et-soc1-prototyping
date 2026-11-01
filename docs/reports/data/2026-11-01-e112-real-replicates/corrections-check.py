#!/usr/bin/env python3
"""E112: the numbers behind the corrections after verification (Sun 1 Nov 2026), from committed files only (standard library).

    python3 docs/reports/data/2026-11-01-e112-real-replicates/corrections-check.py > .../corrections-check.txt

Post hoc and deciding nothing: no frozen file, reduction, number or printed verdict changes. Sections follow the verifier's
seven faults: C1 the card scale (what the 5% is, at each pairing, per tile, and the idle levels); C2 the six synthetic kinds'
scale beside the real tiles' (not X3's 15-kind median, which contains them); C3 (b)'s two-pass agreement and the two-pass
intervals around it; C4 the item-7 line's differences and E91's tally; C5 the leakage slope (every session's, and R5 and (b)'s
gate at E82's frozen 0.2414 W/C, read off the linear dependence of D on the slope); C6 the intervals of pJ/MAC and the die
rise; C7 the labels (carry-over SEs, X1's fp32 rank on the threshold, fp32 l0_mlp_up unresolved, the same-session tie).
"""
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
REF = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
MAT = ("l0_mlp_up", "l6_mlp_down", "l6_attn_qk")
REAL = [f"{ty}.real_{m}" for ty in ("fp32", "fp16", "int8") for m in MAT]
SYN = ["fp32.randn", "fp16.randn", "int8.full", "fp32.nn_like", "fp16.nn_like", "int8.gauss_q"]
E82_SLOPE = 0.2414  # E82's automatic slope on this card (e82.json > leak.k_w_per_c 0.24143), frozen by E93, E94, E103, E104


def load(*p):
    return json.load(open(os.path.join(*p)))


def lower_pct(ratio):
    """D(aifoundry3)/D(card 1) = ratio  ->  card 1 reads (1 - 1/ratio) lower, in percent."""
    return 100.0 * (1.0 - 1.0 / ratio)


def main():
    A = load(HERE, "a-e91-rerun", "e91.json")
    SA = load(HERE, "a-e91-rerun", "scored.json")
    SB = load(HERE, "b-e95-card1", "scored.json")
    SBP = load(HERE, "b-e95-card1", "posthoc-gate026", "scored-posthoc-gate026.json")
    E86 = load(REPO, "docs/reports/data/2026-10-31-e86-real-tensors-energy/e86.json")
    E82 = load(REPO, "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/e82.json")
    E82S = load(REPO, "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/scored.json")
    E91 = load(REPO, "docs/reports/data/2026-10-31-e91-real-tensors-aifoundry1/e91.json")
    REG = load(REPO, "tools/claims-v3/e112/predictions-e112.json")

    pairings = [("primary: card 1 auto (dips removed) against E86 registered (auto)", SA["cross_card"]["primary"])]
    pairings += [(k, v) for k, v in SA["cross_card"]["pairs"].items()]

    print("== C1: the card scale D(aifoundry3, E86) / D(card 1, E112a) - what the 5% is")
    print(f"  leakage slopes (W/C): card 1 E112a auto {A['leak']['k_w_per_c']:.4f} ({A['leak']['n_runs']} runs); "
          f"aifoundry3 E86 auto {E86['leak']['k_w_per_c']:.4f} ({E86['leak']['n_runs']} runs); "
          f"E82 auto {E82['leak']['k_w_per_c']:.4f} ({E82['leak']['n_runs']} runs)")
    print(f"  idle levels (W, whole board): card 1 E112a {A['idle_level']['mean']:.3f}; aifoundry3 E86 {E86['idle_level']['mean']:.3f}"
          " - card 1's board draws MORE in total; D is power over each format's zeros, not absolute watts")
    print("  X4 = median over the nine real tiles, at each pairing (ratio; card 1 lower by):")
    for name, p in pairings:
        x4 = p["x4"]
        if x4["median_ratio"] is None:
            print(f"    {name}: NOT SCORED (too few passes in one of the two reductions)")
            continue
        pt = x4["per_type_median"]
        print(f"    {name}: {x4['median_ratio']:.4f} ({lower_pct(x4['median_ratio']):.1f}% lower); per type fp32 "
              f"{pt['fp32']:.4f}, fp16 {pt['fp16']:.4f}, int8 {pt['int8']:.4f}")
    print(f"  E82 on synthetic kinds (its own slope 0.2414 against E78's 0.1994, dips kept): median "
          f"{E82S['cross_card']['primary']['x3']['median_ratio']:.4f} over {E82S['cross_card']['primary']['x3']['n']} kinds "
          f"({lower_pct(E82S['cross_card']['primary']['x3']['median_ratio']):.1f}% lower) (E82 scored.json > cross_card.primary.x3)")
    kinds = SA["cross_card"]["primary"]["detail"]["kinds"]
    print("  per tile at the primary pairing (ratio +- its 95% half-width; card 1 lower by):")
    rs = []
    for n in REAL:
        k = kinds[n]
        rs.append(k["ratio"])
        print(f"    {n:24s} {k['ratio']:.4f} +- {k['ratio_ci95_halfwidth']:.4f} ({lower_pct(k['ratio']):.1f}% lower)")
    print(f"  range {min(rs):.4f}-{max(rs):.4f}: card 1 reads {lower_pct(min(rs)):.1f}-{lower_pct(max(rs)):.1f}% lower per tile")

    print("\n== C2: the real tiles' scale beside the six synthetic kinds run with them (X3's 15 kinds contain the nine real tiles)")
    print("  six synthetic kinds: " + ", ".join(SYN))
    for name, p in pairings:
        kd = p["detail"]["kinds"]
        syn = [kd[n]["D_e78_w"] / kd[n]["D_e82_w"] for n in SYN
               if n in kd and kd[n].get("D_e82_w") and kd[n].get("D_e78_w") and kd[n].get("status") == "ok"]
        x4 = p["x4"]["median_ratio"]
        x3 = p["detail"]["x3"]["median_ratio"]
        if x4 is None or len(syn) < 6:
            print(f"    {name}: NOT RESOLVED ({len(syn)} of 6 synthetic kinds resolved)")
            continue
        print(f"    {name}: real-tile median (X4) {x4:.4f}; six synthetic kinds' median {statistics.median(syn):.4f}; "
              f"gap {x4 - statistics.median(syn):+.4f}; X3 over all 15 (for reference) {x3:.4f}")
    print("  the six at the primary pairing, each:")
    for n in SYN:
        print(f"    {n:14s} {kinds[n]['ratio']:.4f}")

    print("\n== C3: (b)'s per-tile ratio to random, registered reduction, two kept passes - the agreement and the two-pass intervals")
    rows = SB["cross_card"]["primary"]["rows"]
    x5 = REG["b"]["cross_card"]["X5"]
    print(f"  X5's registered bands: {json.dumps(x5.get('band', x5.get('bands')))}")
    for ty in ("fp32", "fp16", "int8"):
        d = [(abs(v["r_card1"]["mean"] - v["r_aifoundry3"]["mean"]), v["r_card1"]["ci95"], n)
             for n, v in rows.items() if n.startswith(ty + ".") and "r_card1" in v and v["r_card1"]["mean"] is not None]
        hw = sorted(x[1] for x in d)
        print(f"  {ty}: {len(d)} tiles; max |diff| {max(x[0] for x in d):.4f}; median |diff| "
              f"{statistics.median([x[0] for x in d]):.4f}; card 1's own 95% half-width per tile (n 2, t 12.706): median "
              f"{statistics.median(hw):.4f}, range {hw[0]:.4f}-{hw[-1]:.4f}")
    print("  so the observed agreement (a point difference) lies far inside two passes' own intervals: it does not bound the")
    print("  difference, and E112(b) is NOT SCORED (b-e95-card1/scored.json > tally)")

    print("\n== C4: the item-7 line - differences with intervals, and E91's tally")
    rep = SA["replication_of_e86"]["rho_by_type"]
    for ty in ("fp32", "fp16", "int8"):
        r = rep[ty]
        print(f"  {ty}: {json.dumps(r)}")
    print(f"  tally: {json.dumps(SA['tally'])}")
    r5 = SA["rules"]["E91-R5"]["rows"]
    out = [f"{n} {v['diff_w']:+.3f} W (band +-{v['band_w']})" for n, v in r5.items() if v["verdict"] != "PASS"]
    print(f"  R5 at auto, cells outside their bands: {'; '.join(out)}; at the arms {json.dumps(SA['rules']['E91-R5']['at_arms'])}")

    print("\n== C5: the leakage slope - every session's automatic slope, and the verdicts at E82's frozen 0.2414 W/C")
    print(f"  automatic slopes (W/C): E112a {A['leak']['k_w_per_c']:.4f}, E112b "
          f"{load(HERE, 'b-e95-card1', 'e112b.json')['leak']['k_w_per_c']:.4f}, E91 {E91['leak']['k_w_per_c']:.4f} (card 1, dips "
          f"removed); E82 {E82['leak']['k_w_per_c']:.4f} (card 1, dips kept); E86 {E86['leak']['k_w_per_c']:.4f} (aifoundry3)")
    arms = {}
    for lab, f in (("0.1994", "e91-leak0.1994.json"), ("0.3803", "e91-leak0.3803.json"), ("auto", "e91.json"),
                   ("0.545", "e91-leak0.545.json")):
        R = load(HERE, "a-e91-rerun", f)
        arms[lab] = R
        print(f"  (a) {f}: slope {R['leak']['k_w_per_c']:.4f}, kept {R['passes']}")
    k1, k2 = arms["0.1994"]["leak"]["k_w_per_c"], arms["0.3803"]["leak"]["k_w_per_c"]
    print("  R5's cells, D(card 1) - E82's cell (W): at 0.1994 and 0.3803 (all five passes kept at both), the line through them")
    print("  checked at auto and 0.545 (also five passes), and read at 0.2414:")
    worst = 0.0
    allin = True
    for n, v in r5.items():
        e82 = v["D_e82_w"]
        d1 = arms["0.1994"]["items"][n]["D"]["mean"] - e82
        d2 = arms["0.3803"]["items"][n]["D"]["mean"] - e82
        slope = (d2 - d1) / (k2 - k1)
        chk = []
        for lab in ("auto", "0.545"):
            k = arms[lab]["leak"]["k_w_per_c"]
            pred = d1 + slope * (k - k1)
            act = arms[lab]["items"][n]["D"]["mean"] - e82
            worst = max(worst, abs(pred - act))
            chk.append(f"{lab} line {pred:+.3f} / reduced {act:+.3f}")
        at = d1 + slope * (E82_SLOPE - k1)
        inside = abs(at) <= v["band_w"]
        allin = allin and inside
        print(f"    {n:14s} 0.1994 {d1:+.3f}; 0.3803 {d2:+.3f}; {'; '.join(chk)}; at 0.2414 {at:+.3f} "
              f"(band +-{v['band_w']}: {'inside' if inside else 'OUTSIDE'})")
    print(f"  largest gap between the line and a reduction: {worst:.4f} W (D is linear in the slope: p80 = P - k * dT)")
    print(f"  so at 0.2414 every R5 cell is {'inside' if allin else 'NOT all inside'} its band (R5 would read PASS there); the")
    print("  registered R5 (at auto) stays FAIL")
    print("  (b)'s pass gate, the departure that set 11252 aside, at each reduction:")
    for f in ("e112b-leak0.1994.json", "e112b-leak0.3803.json", "e112b.json"):
        R = load(HERE, "b-e95-card1", f)
        print(f"    {f}: slope {R['leak']['k_w_per_c']:.4f}, kept {R['passes']}, set aside {json.dumps(R['passes_set_aside'])}")
    print("  the departure is the same -0.253 W at 0.1994, 0.3803 and auto, and both kept passes are kept at both ends, so at 0.2414")
    print("  (b) keeps the same two passes and stays NOT SCORED")

    print("\n== C6: intervals for pJ per MAC over idle and the 2 s die rise (95% over five passes)")
    tiles = A["items"]
    for n in REAL:
        it = tiles[n]
        dts = [A["per_pass"][str(p)][n]["dT_win"] for p in A["passes"]]
        print(f"  {n:24s} pJ/MAC (S) {it['pj_mac_S']['mean']:.3f} +- {it['pj_mac_S']['ci95']:.3f}; die rise "
              f"{it['dT_win']['mean']:.2f} +- {it['dT_win']['ci95']:.2f} C (per pass {', '.join(f'{x:.2f}' for x in dts)})")
    print("  the firmware reads the die in whole degrees (1 C resolution), and a window's rise is a difference of such readings")
    print("  averaged over its samples; int8 l6_mlp_down's zero-width interval is five passes that each read 1.00 C")

    print("\n== C7: labels")
    for lab, S in (("(a)", SA), ("(b)", SB)):
        c = S["checks"]["carryover"]
        print(f"  {lab} carry-over {c['slope_w_per_w']:.4f} W/W +- {c['se']:.4f} (one SE, n {c['n']}); "
              f"95% about +- {1.97 * c['se']:.4f}; limit 0.01")
    kd = SA["cross_card"]["primary"]["detail"]["kinds"]
    fp32 = ["fp32.nn_like", "fp32.randn"] + [f"fp32.real_{m}" for m in MAT]
    c1 = sorted(fp32, key=lambda n: kd[n]["D_e82_w"])
    a3 = sorted(fp32, key=lambda n: kd[n]["D_e78_w"])
    d2 = sum((c1.index(n) - a3.index(n)) ** 2 for n in fp32)
    nk = len(fp32)
    rho = 1 - 6 * d2 / (nk * (nk * nk - 1))
    print(f"  X1 fp32: {nk} kinds; rank by D on card 1 {c1}; on aifoundry3 {a3}; sum d^2 {d2}; Spearman {rho:.3f} against "
          f"the threshold 0.90 (scored {SA['cross_card']['primary']['detail']['x1']['fp32']['rho']}): one adjacent swap gives "
          "exactly 0.90, on the edge")
    for n in fp32:
        print(f"    {n:22s} card 1 {kd[n]['D_e82_w']:.3f} W, aifoundry3 {kd[n]['D_e78_w']:.3f} W")
    r3 = SA["rules"]["E91-R3"]["by_type"]["fp32"]["per_tile"]
    print(f"  R3 per tile, fp32: {json.dumps(r3)}")
    for m in MAT:
        n = f"fp32.real_{m}"
        per = [A["per_pass"][str(p)][n]["D"] / A["per_pass"][str(p)][REF["fp32"]]["D"] for p in A["passes"]]
        mu = statistics.fmean(per)
        hw = 2.776 * statistics.stdev(per) / math.sqrt(len(per))
        print(f"    {n:22s} D / random {mu:.4f} +- {hw:.4f}: upper bound {mu + hw:.4f} ({'not ' if mu + hw >= 1 else ''}resolved "
              f"below 1); saving {100 * (1 - mu):.2f}%")
    print("  same-session tie (E86's three tiles in (b) against (a)'s same-session D, band +-0.50 W, reported):")
    for lab, S in (("registered reduction, two kept passes", SB), ("post hoc, three passes (gate limit 0.26 W)", SBP)):
        t = S["same_session_tie_reported"]
        parts = [f"{n} {t[n]['D_b']['mean'] - t[n]['D_a']['mean']:+.3f} W (verdict {t[n]['verdict']})" for n in t]
        print(f"    {lab}: " + "; ".join(parts))


if __name__ == "__main__":
    main()
