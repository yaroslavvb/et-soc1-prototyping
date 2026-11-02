#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q136(a): each of Q133(a)'s four int8 netlists' frozen prediction for every tile of E130's single-bit set.

    python3 predict.py            (from this directory; reads runs/, Q133(a)'s analysis.json, E78's e78.json, E79's scored.json and
                                   tools/claims-v3/kinds/e130/e130.json; writes predictions.json and tables.md)

The counts are the bench's own (Q133(a)'s rtl-sim/tima_gate, rebuilt unchanged; zero delay; every run behind the functional check) at
run_kinds.py's three launch points, 157,232, 471,698 and 786,163 ops into a 0.5 s launch; the PRIMARY value of a tile is the mean over
the three (run_kinds.py: "a time average over the launch is the average over the three"), the middle point and each point are kept
beside it. A single flip moves no clocked bit, so a flip's price is k x merged nets toggled in the whole VPU per flipped bit,
item minus its own zero, k being each netlist's own int8-alone fit (Q133(a) `model.arms.<arm>.int8_alone.coef_fJ.dnets_vpu`, M2 on
E78's board watts, aifoundry3, 600 MHz). PRIMARY merge: nets_map (Q133(a)'s convention for single bits; the merge Q132(b) sets beside
watts); nets_hier beside it, registered too. A watt step is fJ x flips per op x E78's int8 op rate.
"""
import hashlib
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DD = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ARMS = ["booth_tree", "booth", "booth_swap", "plain"]
GROUP = {"booth_tree": "Booth on B", "booth": "Booth on B", "booth_swap": "Booth on A", "plain": "no Booth"}
MID = 471698
POINTS = [157232, 471698, 786163]   # run_kinds.py launch_points("int8"): the midpoints of a 0.5 s launch's thirds at 600 MHz
MERGES = {"map": "nets_map", "hier": "nets_hier"}


def load(p):
    with open(p) as f:
        return json.load(f)


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    man = load(os.path.join(REPO, "tools", "claims-v3", "kinds", "e130", "e130.json"))
    items = {it["kind"]: it for it in man["items"]}
    q133 = load(os.path.join(DD, "2026-11-01-q133a-int8-gate-level", "analysis.json"))
    e78 = load(os.path.join(DD, "2026-10-31-e78-kinds-energy-matrix", "e78.json"))["items"]
    rates = [v["rate"]["mean"] for k, v in e78.items() if k.startswith("int8.") and "rate" in v]
    rate = float(np.mean(rates))
    e79 = load(os.path.join(DD, "2026-10-31-e79-fp16-int8-bit-prices", "scored.json"))["prices"]
    card_hw = {"a_list_board_fJ_ci95_median_4pass": float(np.median([e79["int8_a"][str(b)]["fJ_ci95"] for b in range(8)])),
               "b_list_board_fJ_ci95_median_4pass": float(np.median([e79["int8_b_kg"][str(b)]["fJ_ci95"] for b in range(8)])),
               "a_list_board_fJ": [round(e79["int8_a"][str(b)]["fJ"], 1) for b in range(8)],
               "b_list_board_fJ": [round(e79["int8_b_kg"][str(b)]["fJ"], 1) for b in range(8)],
               "source": "E79 scored.json prices.int8_a / int8_b_kg (aifoundry3, 600 MHz, 4 passes; base A 0xa5, B 93 c3 c6 ac 55 66 1e 8d)"}

    out = {"_what": "Q136(a), Mon 2 Nov 2026: Q133(a)'s four int8 netlists' frozen predictions for E130's 26 tiles (README.md)",
           "_units": "fJ per flipped bit (board), W of step over the item's own zero at E78's int8 rate; nets per flipped bit in the whole VPU",
           "inputs": {"k_fJ_per_net_toggle": {a: q133["model"]["arms"][a]["int8_alone"]["coef_fJ"]["dnets_vpu"] for a in ARMS},
                      "k_jackknife_se_fJ": {a: q133["model"]["arms"][a]["int8_alone"]["coef_jackknife_se_fJ"]["dnets_vpu"] for a in ARMS},
                      "k_source": "Q133(a) analysis.json model.arms.<arm>.int8_alone (M2, nets_hier, 15 int8 kinds of E78)",
                      "rate_ops_per_s": rate, "rate_source": f"mean of E78's {len(rates)} int8 items' rate.mean (e78.json)",
                      "launch_points_ops": POINTS, "primary": "nets_map, mean of the three launch points, at each netlist's own k",
                      "tiles": {k: v["sha256"] for k, v in items.items()},
                      "e130_json_sha256": sha_file(os.path.join(REPO, "tools", "claims-v3", "kinds", "e130", "e130.json"))},
           "card_precision_e79": card_hw, "arms": {}}

    for a in ARMS:
        rows = load(os.path.join(HERE, "runs", a, "counts.json"))["rows"]
        k = out["inputs"]["k_fJ_per_net_toggle"][a]
        kse = out["inputs"]["k_jackknife_se_fJ"][a]

        def pts(name):
            """name -> {n0: point} at the three launch points (all three required)."""
            r = rows.get("int8.e130_" + name)
            if not r:
                return None
            got = {x["n0"]: x for x in r["points"] if x}
            return got if all(n in got for n in POINTS) else None

        res = {"k_fJ": k, "group": GROUP[a], "items": {}, "zeros": {}}
        for name, it in items.items():
            P = pts(name)
            if it["bit"] is None:
                res["zeros"][name] = None if P is None else {
                    "check_mismatch": max(P[n]["check_mismatch"] for n in POINTS),
                    "vpu_map_by_point": [P[n]["vpu"]["nets_map"] for n in POINTS], "vpu_hier_by_point": [P[n]["vpu"]["nets_hier"] for n in POINTS],
                    "unit_map_by_point": [P[n]["unit"]["nets_map"] for n in POINTS], "unit_hier_by_point": [P[n]["unit"]["nets_hier"] for n in POINTS],
                    "ff_clocked_by_point": [P[n]["ff"]["all"]["clocked"] for n in POINTS]}
                continue
            Z = pts(it["zero"])
            if P is None or Z is None:
                res["items"][name] = None
                continue
            nf = it["designed_flips_per_op"]
            row = {"side": it["side"], "bit": it["bit"], "base_word": it["base_word"], "held": it["held"], "zero": it["zero"], "flips_per_op": nf,
                   "check_mismatch": max(max(P[n]["check_mismatch"], Z[n]["check_mismatch"]) for n in POINTS),
                   "d_ff_clocked_per_op": max(abs(P[n]["ff"]["all"]["clocked"] - Z[n]["ff"]["all"]["clocked"]) for n in POINTS)}
            for mk, key in MERGES.items():
                du = [(P[n]["unit"][key] - Z[n]["unit"][key]) / nf for n in POINTS]
                dv = [(P[n]["vpu"][key] - Z[n]["vpu"][key]) / nf for n in POINTS]
                m = float(np.mean(dv))
                row[f"unit_{mk}_per_flip"] = float(np.mean(du))
                row[f"vpu_{mk}_per_flip"] = m
                row[f"rest_{mk}_per_flip"] = m - float(np.mean(du))
                row[f"fJ_{mk}"] = k * m                                  # the primary: the launch's time average, three points
                row[f"fJ_{mk}_k_se"] = kse * m
                row[f"fJ_{mk}_by_point"] = [k * x for x in dv]
                row[f"fJ_{mk}_middle_point"] = k * dv[1]
                row[f"dW_{mk}"] = k * m * 1e-15 * nf * rate
            Pm, Zm = P[MID], Z[MID]
            row["by_stage_map_per_flip_middle"] = {s: (Pm["unit"]["by_stage"].get(s, 0) - Zm["unit"]["by_stage"].get(s, 0)) / nf
                                                   for s in sorted(set(Pm["unit"]["by_stage"]) | set(Zm["unit"]["by_stage"]))}
            res["items"][name] = row
        # the separating statistics, in both merges
        st = {}
        for mk in MERGES:
            def f(n):
                r = res["items"].get(n)
                return None if r is None else r[f"fJ_{mk}"]
            B = [f(f"b1_{j}") for j in range(8)]
            A = [f(f"a1_{j}") for j in range(8)]
            s = {}
            if all(x is not None for x in B):
                s["B_odd_over_even"] = float(np.mean([B[1], B[3], B[5]]) / np.mean([B[0], B[2], B[4]]))
                s["B_odd_minus_even_fJ"] = float(np.mean([B[1], B[3], B[5]]) - np.mean([B[0], B[2], B[4]]))
                s["B_mean_bits0to6_fJ"] = float(np.mean(B[:7]))
                s["B_sign_over_rest"] = float(B[7] / np.mean(B[:7]))
                s["B_list_fJ"] = B
            if all(x is not None for x in A):
                s["A_odd_over_even"] = float(np.mean([A[1], A[3], A[5]]) / np.mean([A[0], A[2], A[4]]))
                s["A_odd_minus_even_fJ"] = float(np.mean([A[1], A[3], A[5]]) - np.mean([A[0], A[2], A[4]]))
                s["A_mean_bits0to6_fJ"] = float(np.mean(A[:7]))
                s["A_sign_over_rest"] = float(A[7] / np.mean(A[:7]))
                s["A_list_fJ"] = A
            for side in ("b", "a"):
                S = side.upper()
                s1, s2, sd = f(f"{side}1_7"), f(f"{side}2_7"), f(f"{side}1d_7")
                if None not in (s1, s2, sd):
                    s[f"{S}_sign_fJ_word1_word2_word1dense"] = [s1, s2, sd]
                    s[f"{S}_sign_w2_over_w1"] = s2 / s1 if s1 else None
                    s[f"{S}_sign_w2_minus_w1_fJ"] = s2 - s1
                    s[f"{S}_sign_dense_over_one"] = sd / s1 if s1 else None
                    s[f"{S}_sign_dense_minus_one_fJ"] = sd - s1
            st[mk] = s
        # the first version's retired word-class-3 pairs, labelled apart: they are not predictions of any tile E130 runs
        scr = load(os.path.join(HERE, "runs", "screening_v1_class3.json"))["arms"].get(a, {})

        def scr_fJ(item, zero, nf, mk):
            p, z = scr.get("int8.e130_" + item), scr.get("int8.e130_" + zero)
            if not p or not z:
                return None
            pp = {x["n0"]: x for x in p["points"]}
            zz = {x["n0"]: x for x in z["points"]}
            ns = [n for n in POINTS if n in pp and n in zz]
            return k * float(np.mean([(pp[n]["vpu"][MERGES[mk]] - zz[n]["vpu"][MERGES[mk]]) / nf for n in ns]))
        res["screening_v1_class3"] = {mk: {"B_sign_w3_fJ": scr_fJ("b3_7", "hb3", 1024, mk), "A_sign_w3_fJ": scr_fJ("a3_7", "ha3", 8192, mk)}
                                      for mk in MERGES}
        for mk in MERGES:
            sc = res["screening_v1_class3"][mk]
            b1, a1 = st[mk]["B_sign_fJ_word1_word2_word1dense"][0], st[mk]["A_sign_fJ_word1_word2_word1dense"][0]
            sc["B_sign_w3_over_w1"] = sc["B_sign_w3_fJ"] / b1 if sc["B_sign_w3_fJ"] is not None else None
            sc["A_sign_w3_over_w1"] = sc["A_sign_w3_fJ"] / a1 if sc["A_sign_w3_fJ"] is not None else None
        res["stats"] = st
        out["arms"][a] = res

    # how far apart the netlists are, statistic by statistic, against E79's own card precision on this card
    sep = {}
    for mk in MERGES:
        d = {}
        for key in ("B_odd_minus_even_fJ", "A_odd_minus_even_fJ", "B_sign_dense_minus_one_fJ", "A_sign_dense_minus_one_fJ",
                    "B_sign_w2_minus_w1_fJ", "A_sign_w2_minus_w1_fJ", "B_mean_bits0to6_fJ", "A_mean_bits0to6_fJ",
                    "B_odd_over_even", "A_odd_over_even", "B_sign_dense_over_one", "A_sign_dense_over_one",
                    "B_sign_w2_over_w1", "A_sign_w2_over_w1", "B_sign_over_rest", "A_sign_over_rest"):
            vals = {a: out["arms"][a]["stats"][mk].get(key) for a in ARMS}
            if any(v is None for v in vals.values()):
                continue
            d[key] = {"by_arm": vals}
            if key.endswith("_fJ"):
                hw = card_hw["b_list_board_fJ_ci95_median_4pass" if key.startswith("B") else "a_list_board_fJ_ci95_median_4pass"]
                # a difference of two means of three items each (odd/even) or of two items (sign words): its 95% half-width from E79's
                # median item half-width, items independent: hw x sqrt(1/3 + 1/3) or hw x sqrt(2)
                n_hw = hw * (np.sqrt(2 / 3) if "odd_minus_even" in key else
                             (np.sqrt(2) if ("minus_w1" in key or "minus_one" in key) else np.sqrt(1 / 7)))
                d[key]["card_ci95_halfwidth_fJ_expected"] = float(n_hw)
                pairs = {}
                for i, x in enumerate(ARMS):
                    for y in ARMS[i + 1:]:
                        pairs[f"{x}-{y}"] = float(abs(vals[x] - vals[y]) / n_hw)
                d[key]["gap_over_card_halfwidth"] = pairs
        sep[mk] = d
    out["separation"] = sep
    with open(os.path.join(HERE, "predictions.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=False)
        fh.write("\n")
    write_tables(out)


def fmt(x, nd=1):
    return "—" if x is None else f"{x:.{nd}f}"


def write_tables(o):
    L = ["# Q136(a): the four int8 netlists' frozen predictions for E130 (generated by predict.py)", ""]
    for mk, label in (("map", "nets_map (primary)"), ("hier", "nets_hier")):
        L += [f"## fJ per flipped bit, priced at each netlist's own k, {label}", "",
              "| tile | side | bit | word | flips/op | " + " | ".join(ARMS) + " |", "|---|---|---:|---:|---:|" + "---:|" * len(ARMS)]
        names = [n for n in o["arms"][ARMS[0]]["items"]]
        for n in names:
            r0 = o["arms"][ARMS[0]]["items"][n]
            if r0 is None:
                continue
            vals = [o["arms"][a]["items"].get(n) for a in ARMS]
            L.append(f"| `{n}` | {r0['side'].upper()} | {r0['bit']} | {r0['base_word']} | {r0['flips_per_op']} | " +
                     " | ".join(fmt(v[f'fJ_{mk}'] if v else None) for v in vals) + " |")
        L += ["", f"## W of step over the item's own zero, {label}", "",
              "| tile | " + " | ".join(ARMS) + " |", "|---|" + "---:|" * len(ARMS)]
        for n in names:
            vals = [o["arms"][a]["items"].get(n) for a in ARMS]
            if vals[0] is None:
                continue
            L.append(f"| `{n}` | " + " | ".join(fmt(v[f'dW_{mk}'] if v else None, 3) for v in vals) + " |")
        L += ["", f"## The separating statistics, {label}", "", "| statistic | " + " | ".join(ARMS) + " | card 95% half-width (E79, 4 passes) |",
              "|---|" + "---:|" * (len(ARMS) + 1)]
        for key, d in o["separation"][mk].items():
            nd = 2 if not key.endswith("_fJ") else 1
            hw = d.get("card_ci95_halfwidth_fJ_expected")
            L.append(f"| {key} | " + " | ".join(fmt(d["by_arm"][a], nd) for a in ARMS) + f" | {fmt(hw)} |")
        L.append("")
    L += ["## Launch points: each tile's three points (nets_map, fJ per flipped bit), the primary being their mean", "",
          "| tile | " + " | ".join(ARMS) + " |", "|---|" + "---:|" * len(ARMS)]
    for n in [n for n in o["arms"][ARMS[0]]["items"] if o["arms"][ARMS[0]]["items"][n]]:
        L.append(f"| `{n}` | " + " | ".join("/".join(f"{x:.1f}" for x in o["arms"][a]["items"][n]["fJ_map_by_point"]) for a in ARMS) + " |")
    L.append("")
    L += ["## Inputs", "", "| netlist | group | k (fJ per net toggle) | jackknife s.e. |", "|---|---|---:|---:|"]
    for a in ARMS:
        L.append(f"| {a} | {GROUP[a]} | {o['inputs']['k_fJ_per_net_toggle'][a]:.4f} | {o['inputs']['k_jackknife_se_fJ'][a]:.4f} |")
    L += ["", f"Rate {o['inputs']['rate_ops_per_s']:.6e} int8 ops/s ({o['inputs']['rate_source']}); launch points {POINTS} ops.", ""]
    with open(os.path.join(HERE, "tables.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
