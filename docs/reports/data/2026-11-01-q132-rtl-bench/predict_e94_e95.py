#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""The bench's frozen predictions for E94's 51 draws and E95's 33 tiles, per tile, with 95% intervals.

    predict_e94_e95.py --counts <this dir> --data <docs/reports/data> --kinds <tools/claims-v3/kinds> --out e94-e95-bench-prediction.json --table e94-e95-bench-prediction.md

The model is the one in README.md, frozen on data read before E94 and E95:

    D(tile) = rate * ( k * (nets(tile) - nets(zeros)) + a * (clocked(tile) - clocked(zeros)) )

Floats: k and a fitted on E78's 33 fp32 and fp16 kinds and on nothing else. int8: its own k and a, fitted on E78's 15 int8 kinds alone, because
its multiply and its adds are behavioural RTL with no nets inside them; those two numbers are empirical and not comparable with the float ones.
E95 runs on aifoundry3 card 0, E78's card: no scale. E94 runs on aifoundry1 card 1: each prediction times one card scale per family, fitted on E82
(that card's run of E78's kinds) and on nothing else.

The interval: t(0.975, n - 2) * sqrt(s^2 + x' C x + m^2). s is the rms of out-of-sample errors already read: leave-one-out on E78 plus every tile set
scored with frozen coefficients on that card (INTERVAL_SETS). C is the coefficients' jackknife covariance over E78's kinds. m is the standard error of
the tile's count over its three launch points. Nothing is added for a known bias: gated kinds have run 0.17-0.65 W low, and the interval is what covers it.

This script opens no E94 or E95 data directory. Tile names come from the counts, groups from the tile manifests (real2/real2.json, e94/e94.json).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import re
import statistics
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import design, load, lstsq, rows_from, stats  # noqa: E402

MODELS = {"vpu_map": ("dnetsm_vpu", "dclk"), "vpu_hier2": ("dnets2_vpu", "dclk")}
RANDOM = {"fp32": "randn", "fp16": "randn", "int8": "full"}
# the offsets E95 registered, as (tile, partner)
E95_OFFSETS = [("fp16.r2_gpt2_l6_mlp_down_fp16fwd", "fp16.real_l6_mlp_down"), ("fp16.r2_gpt2_l6_attn_qk_fp16fwd", "fp16.real_l6_attn_qk"),
               ("int8.r2_gpt2_l6_down_per_token", "int8.real_l6_mlp_down"), ("int8.r2_gpt2_l6_down_p9999", "int8.real_l6_mlp_down"),
               ("int8.r2_gpt2_l6_down_p999", "int8.real_l6_mlp_down"), ("int8.r2_gpt2_l11_down_p999", "int8.r2_gpt2_l11_down_maxabs"),
               ("int8.r2_gpt2_l11_down_asym", "int8.r2_gpt2_l11_down_maxabs"), ("int8.r2_vgg16_fc2_asym", "int8.r2_vgg16_fc2")]
COMMITTED = {"fp32.nn_like": 1, "fp32.sparse50": 1, "fp16.nn_like": 1, "fp16.uniform01": 1, "int8.sparse50": 1, "fp32.randn": 1, "fp16.randn": 1, "int8.full": 1}


def t975(nu):
    z = statistics.NormalDist().inv_cdf(0.975)
    return z + (z ** 3 + z) / (4 * nu) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * nu ** 2)


def loo_errors(rows, cols):
    y, p = [], []
    for i in range(len(rows)):
        b = lstsq(rows[:i] + rows[i + 1:], cols)
        y.append(rows[i]["D"])
        p.append(float((design([rows[i]], cols) @ b)[0]))
    return list(np.array(y) - np.array(p))


def jack_cov(rows, cols):
    jk = np.array([lstsq(rows[:i] + rows[i + 1:], cols) for i in range(len(rows))])
    d = jk - jk.mean(axis=0)
    return d.T @ d * (len(rows) - 1) / len(rows)


def errs(rows, cols, b, scale=1.0):
    rows = [r for r in rows if r["D"] is not None and r["kind"] != "zeros"]
    return [float(r["D"] - q) for r, q in zip(rows, (design(rows, cols) @ b) * scale)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counts", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--kinds", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--table", required=True)
    a = ap.parse_args()
    cd, dd = a.counts, a.data
    e78 = load(f"{dd}/2026-10-31-e78-kinds-energy-matrix/e78.json")
    e82 = load(f"{dd}/2026-10-31-e82-kinds-aifoundry1/e82.json")
    e86 = load(f"{dd}/2026-10-31-e86-real-tensors-energy/e86.json") if os.path.exists(f"{dd}/2026-10-31-e86-real-tensors-energy/e86.json") else None
    if e86 is None:
        for n in os.listdir(dd):
            if "e86" in n and os.path.exists(f"{dd}/{n}/e86.json"):
                e86 = load(f"{dd}/{n}/e86.json")
    e90 = None
    for n in os.listdir(dd):
        if "e90" in n and os.path.exists(f"{dd}/{n}/e90.json"):
            e90 = load(f"{dd}/{n}/e90.json")
    e88 = load(f"{dd}/2026-10-31-e88-result-path/e88.json")
    e92 = load(f"{dd}/2026-11-01-e92-sign-split/e92.json")
    zc = load(f"{cd}/counts-v2.json")["rows"]
    tiles = load(f"{cd}/counts-e94e95.json")["rows"]
    real2 = load(f"{a.kinds}/real2/real2.json")["tiles"]
    e94m = load(f"{a.kinds}/e94/e94.json")["tiles"]

    k78 = rows_from(f"{cd}/counts-v2.json", e78["items"], zc)
    floats = [r for r in k78 if r["type"] in ("fp32", "fp16") and r["kind"] != "zeros"]
    int8 = [r for r in k78 if r["type"] == "int8" and r["kind"] != "zeros"]
    rate = {t: e78["items"][f"{t}.{RANDOM[t]}"]["rate"]["mean"] for t in RANDOM}
    new = rows_from(f"{cd}/counts-e94e95.json", None, zc)
    for r in new:
        r["rate"] = rate[r["type"]]
    bykey = {r["key"]: r for r in new}
    committed = {r["key"]: r for r in k78}
    for k, r in committed.items():
        r["rate_e78"] = r["rate"]

    out = {"_note": "Frozen predictions from RTL counts, E78's kinds and, for the card scale and the interval only, experiments already read (E82, E86, E88, E90, E92). "
                    "No E94 or E95 measurement is in this file's inputs.",
           "tile_sets": {"e94": "tools/claims-v3/kinds/e94/tiles, 51 draws: 42 fresh, 9 E90's byte for byte", "e95": "tools/claims-v3/kinds/real2/tiles (30) and real/tiles (3)"},
           "models": {}}
    for mname, cols in MODELS.items():
        bf, b8 = lstsq(floats, cols), lstsq(int8, cols)
        cf, c8 = jack_cov(floats, cols), jack_cov(int8, cols)
        # card 1's scales, from E82 only
        r82 = rows_from(f"{cd}/counts-v2.json", e82["items"], zc)
        f82 = [r for r in r82 if r["D"] is not None and r["type"] != "int8" and r["kind"] != "zeros"]
        i82 = [r for r in r82 if r["D"] is not None and r["type"] == "int8" and r["kind"] != "zeros"]
        pf82, pi82 = design(f82, cols) @ bf, design(i82, cols) @ b8
        sf = float(np.linalg.lstsq(pf82[:, None], np.array([r["D"] for r in f82]), rcond=None)[0][0])
        si = float(np.linalg.lstsq(pi82[:, None], np.array([r["D"] for r in i82]), rcond=None)[0][0])
        # jackknife of each scale
        def jk_scale(p, y):
            v = [float((np.delete(p, i) @ np.delete(y, i)) / (np.delete(p, i) @ np.delete(p, i))) for i in range(len(p))]
            m = sum(v) / len(v)
            return math.sqrt(sum((x - m) ** 2 for x in v) * (len(v) - 1) / len(v))
        se_sf, se_si = jk_scale(pf82, np.array([r["D"] for r in f82])), jk_scale(pi82, np.array([r["D"] for r in i82]))
        # out-of-sample errors already read
        sets = {}
        sets["float, E78 LOO"] = loo_errors(floats, cols)
        sets["int8, E78 LOO"] = loo_errors(int8, cols)
        r86 = rows_from(f"{cd}/counts-e86.json", e86["items"], zc)
        r90 = rows_from(f"{cd}/counts-e90.json", e90["items"], zc)
        r92 = rows_from(f"{cd}/counts-e92.json", e92["items"], zc)
        sets["float, E86"] = errs([r for r in r86 if r["type"] != "int8"], cols, bf)
        sets["int8, E86"] = errs([r for r in r86 if r["type"] == "int8"], cols, b8)
        sets["float, E90"] = errs([r for r in r90 if r["type"] != "int8"], cols, bf)
        sets["int8, E90"] = errs([r for r in r90 if r["type"] == "int8"], cols, b8)
        sets["float, E92"] = errs(r92, cols, bf)
        r88 = rows_from(f"{cd}/counts-e88.json", e88["items"], zc)
        sets["float card 1, E82 after scale"] = errs(f82, cols, bf, sf)
        sets["int8 card 1, E82 after scale"] = errs(i82, cols, b8, si)
        sets["float card 1, E88 with E82's scale"] = errs([r for r in r88 if r["type"] != "int8"], cols, bf, sf)
        sets["int8 card 1, E88 with E82's scale"] = errs([r for r in r88 if r["type"] == "int8"], cols, b8, si)
        def pool(*names):
            v = [x for n in names for x in sets[n] if x == x]
            return {"n": len(v), "rms_w": math.sqrt(sum(x * x for x in v) / len(v)), "sets": list(names)}
        INTERVAL_SETS = {"float.aifoundry3": pool("float, E78 LOO", "float, E86", "float, E90", "float, E92"),
                         "int8.aifoundry3": pool("int8, E78 LOO", "int8, E86", "int8, E90"),
                         "float.card1": pool("float card 1, E82 after scale", "float card 1, E88 with E82's scale"),
                         "int8.card1": pool("int8 card 1, E82 after scale", "int8 card 1, E88 with E82's scale")}

        def predict(r, card):
            fam = "int8" if r["type"] == "int8" else "float"
            b, C = (b8, c8) if fam == "int8" else (bf, cf)
            x = np.array([r[c] * r["rate"] for c in cols], float)
            p0 = float(x @ b)
            s, se_s = (1.0, 0.0) if card == "aifoundry3" else ((si, se_si) if fam == "int8" else (sf, se_sf))
            pts = [float((np.array([(q["vpu"]["nets_map" if cols[0] == "dnetsm_vpu" else "nets_hier2"] - zc[r["type"] + ".zeros"]["mean"]["vpu"]["nets_map" if cols[0] == "dnetsm_vpu" else "nets_hier2"]) * r["rate"],
                                     (q["ff"]["all"]["clocked"] - zc[r["type"] + ".zeros"]["mean"]["ff"]["all"]["clocked"]) * r["rate"]]) @ b) * s) for q in tiles[r["key"]]["points"]] if r["key"] in tiles else [p0 * s]
            m = float(np.std(pts, ddof=1) / math.sqrt(len(pts))) if len(pts) > 1 else 0.0
            iv = INTERVAL_SETS[f"{fam}.{'card1' if card != 'aifoundry3' else 'aifoundry3'}"]
            var = iv["rms_w"] ** 2 + s * s * float(x @ C @ x) + (p0 * se_s) ** 2 + m * m
            half = t975(iv["n"] - 2) * math.sqrt(var)
            return {"D_w": p0 * s, "lo95": max(p0 * s - half, 0.0), "hi95": p0 * s + half, "half95": half, "launch_points_w": pts}

        o = {"k_fJ_per_net_toggle": {"float": float(bf[0]) * 1e15, "int8": float(b8[0]) * 1e15},
             "a_fJ_per_clocked_bit": {"float": float(bf[1]) * 1e15, "int8": float(b8[1]) * 1e15},
             "fit_rms_w_on_e78": {"float": float(np.sqrt(np.mean((np.array([r["D"] for r in floats]) - design(floats, cols) @ bf) ** 2))),
                                  "int8": float(np.sqrt(np.mean((np.array([r["D"] for r in int8]) - design(int8, cols) @ b8) ** 2)))},
             "n_fit": {"float": len(floats), "int8": len(int8)},
             "card1_scale_from_e82": {"float": sf, "float_se": se_sf, "int8": si, "int8_se": se_si, "n": {"float": len(f82), "int8": len(i82)}},
             "interval_pools": INTERVAL_SETS,
             "e95_aifoundry3": {}, "e94_card1": {}, "e94_committed_card1": {}}
        for k, r in bykey.items():
            t, name = r["type"], r["kind"]
            cm = tiles[k]["mean"]
            row = {"type": t, "gate_closes": 1 - cm["valid_slots"] / 4096, "nets_per_op": cm["vpu"]["nets_map" if cols[0] == "dnetsm_vpu" else "nets_hier2"], "clocked_per_op": cm["ff"]["all"]["clocked"],
                   "check_mismatch_words": cm["check_mismatch"], "by_stage_per_op": cm["vpu"]["by_stage"] if mname == "vpu_map" else None}
            if name.startswith("r2_"):
                g = real2[t][name[3:]]
                row.update({"group": g.get("group"), "tier": g.get("tier"), "blind": True})
                row.update(predict(r, "aifoundry3"))
                o["e95_aifoundry3"][k] = row
            elif name.startswith("real_"):
                row.update({"group": "E86 partner", "blind": False, "why_not_blind": "this tile's power on this card was read in E86; k and a did not use it"})
                row.update(predict(r, "aifoundry3"))
                o["e95_aifoundry3"][k] = row
            else:
                row.update({"group": e94m[k].get("group"), "rule": re.sub(r"_e9[04]d\d+$", "", name), "fresh": "_e94d" in name, "blind": True})
                row.update(predict(r, "card1"))
                o["e94_card1"][k] = row
        for k in COMMITTED:
            r = dict(committed[k])
            r["rate"] = rate[r["type"]]
            row = {"type": r["type"], "blind": False, "why_not_blind": "committed tile, read in E82 on this card; the scale used it", "nets_per_op": r["netsm_vpu"] if cols[0] == "dnetsm_vpu" else r["nets2_vpu"], "clocked_per_op": r["clk"]}
            row.update(predict(r, "card1"))
            o["e94_committed_card1"][k] = row
        # per rule: the draws' predicted mean and spread, and where the committed tile sits
        rules = {}
        for k, row in o["e94_card1"].items():
            rules.setdefault(f"{row['type']}.{row['rule']}", []).append((k, row))
        o["e94_rules"] = {}
        for rk, v in sorted(rules.items()):
            for label, sel in (("all", v), ("fresh", [x for x in v if x[1]["fresh"]])):
                d = [x[1]["D_w"] for x in sel]
                sd = statistics.stdev(d) if len(d) > 1 else None
                o["e94_rules"].setdefault(rk, {})[label] = {"n": len(d), "mean_w": sum(d) / len(d), "sd_w": sd}
            c = o["e94_committed_card1"].get(rk)
            if c:
                o["e94_rules"][rk]["committed_D_w"] = c["D_w"]
                o["e94_rules"][rk]["committed_minus_mean_of_fresh_w"] = c["D_w"] - o["e94_rules"][rk]["fresh"]["mean_w"]
        # E95's registered offsets
        o["e95_offsets"] = []
        for x, y in E95_OFFSETS:
            X, Y = o["e95_aifoundry3"][x], o["e95_aifoundry3"][y]
            fam = "int8" if x.startswith("int8") else "float"
            hw = t975(INTERVAL_SETS[f"{fam}.aifoundry3"]["n"] - 2) * math.sqrt(2) * INTERVAL_SETS[f"{fam}.aifoundry3"]["rms_w"]
            o["e95_offsets"].append({"tile": x, "partner": y, "offset_w": X["D_w"] - Y["D_w"], "half95_conservative": hw})
        out["models"][mname] = o
    out["primary"] = "vpu_map"
    json.dump(out, open(a.out, "w"), indent=1)

    P, H = out["models"]["vpu_map"], out["models"]["vpu_hier2"]
    with open(a.table, "w") as f:
        w = f.write
        w("# Frozen bench predictions for E94 and E95\n\n")
        w("Written by `predict_e94_e95.py`; D in W over the type's own zeros, at 600 MHz; the commit holding this file is the freeze. `g` is the share of slots the zero gate closes in the RTL; `miss` counts words of C the bench got wrong against software (fp16's named window residue included).\n\n")
        w(f"Floats: k = {P['k_fJ_per_net_toggle']['float']:.3f} fJ, a = {P['a_fJ_per_clocked_bit']['float']:.3f} fJ, fitted on E78's {P['n_fit']['float']} fp32 and fp16 kinds. int8: k = {P['k_fJ_per_net_toggle']['int8']:.3f} fJ, a = {P['a_fJ_per_clocked_bit']['int8']:.3f} fJ, its own, fitted on E78's {P['n_fit']['int8']} int8 kinds, not comparable with the float ones. Card 1's scale from E82: float {P['card1_scale_from_e82']['float']:.4f} ± {P['card1_scale_from_e82']['float_se']:.4f}, int8 {P['card1_scale_from_e82']['int8']:.4f} ± {P['card1_scale_from_e82']['int8_se']:.4f}.\n\n")
        w("## E95, aifoundry3 card 0: no scale\n\n| tile | group | g | nets/op | clocked/op | **D, W [95%]** | hier2 D, W | miss |\n|---|---|---:|---:|---:|---:|---:|---:|\n")
        for k, r in sorted(P["e95_aifoundry3"].items(), key=lambda kv: (kv[0][:4], -kv[1]["D_w"])):
            w(f"| `{k}`{'' if r['blind'] else ' (E86 read)'} | {r['group']} | {r['gate_closes']:.3f} | {r['nets_per_op']:,.0f} | {r['clocked_per_op']:,.0f} | **{r['D_w']:.2f}** [{r['lo95']:.2f}, {r['hi95']:.2f}] | {H['e95_aifoundry3'][k]['D_w']:.2f} | {r['check_mismatch_words']:.1f} |\n")
        w("\n### E95's registered offsets\n\n| tile | partner | offset, W [conservative 95%] | hier2 |\n|---|---|---:|---:|\n")
        for x, y in zip(P["e95_offsets"], H["e95_offsets"]):
            w(f"| `{x['tile']}` | `{x['partner']}` | {x['offset_w']:+.2f} [{x['offset_w'] - x['half95_conservative']:+.2f}, {x['offset_w'] + x['half95_conservative']:+.2f}] | {y['offset_w']:+.2f} |\n")
        w("\n## E94, aifoundry1 card 1: E82's scale\n\n| tile | fresh | g | nets/op | clocked/op | **D, W [95%]** | hier2 D, W | miss |\n|---|---|---:|---:|---:|---:|---:|---:|\n")
        for k, r in sorted(P["e94_card1"].items()):
            w(f"| `{k}` | {'yes' if r['fresh'] else 'E90 draw'} | {r['gate_closes']:.3f} | {r['nets_per_op']:,.0f} | {r['clocked_per_op']:,.0f} | **{r['D_w']:.2f}** [{r['lo95']:.2f}, {r['hi95']:.2f}] | {H['e94_card1'][k]['D_w']:.2f} | {r['check_mismatch_words']:.1f} |\n")
        w("\n### E94 by rule: the bench's own between-draw spread\n\n| rule | fresh draws | mean of fresh, W | SD of fresh, W | committed tile, W (read in E82) | committed − mean of fresh, W |\n|---|---:|---:|---:|---:|---:|\n")
        for rk, r in P["e94_rules"].items():
            cd_ = r.get("committed_D_w")
            w(f"| `{rk}` | {r['fresh']['n']} | {r['fresh']['mean_w']:.2f} | {r['fresh']['sd_w']:.3f} | {'' if cd_ is None else f'{cd_:.2f}'} | {'' if cd_ is None else format(r['committed_minus_mean_of_fresh_w'], '+.2f')} |\n")
        w("\n## How the intervals are built\n\n")
        for n, iv in P["interval_pools"].items():
            w(f"- `{n}`: pooled out-of-sample rms {iv['rms_w']:.3f} W over {iv['n']} errors already read ({', '.join(iv['sets'])}).\n")
    for n, iv in P["interval_pools"].items():
        print(n, round(iv["rms_w"], 3), iv["n"])
    print("scale", P["card1_scale_from_e82"])
    print("worst mismatch", max(r["check_mismatch_words"] for s in ("e95_aifoundry3", "e94_card1") for r in P[s].values()))


if __name__ == "__main__":
    main()
