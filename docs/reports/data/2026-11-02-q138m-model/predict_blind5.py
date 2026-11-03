#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q138(m): frozen predictions with bands for a pool of kinds tiles, by M7 and, through the same interface, M5 and M6 as frozen.

    python3 predict_blind5.py <pool_dir> <card> [--counts <counts.json>] [--out <dir>]
        card: aifoundry3 | aifoundry1c1 | aifoundry2

<pool_dir> holds the tiles and a manifest in blind pool 4's layout (tools/claims-v3/kinds/blind4/): a JSON file with a "tiles"
list of {name, type, file (relative to pool_dir), sha256: {whole}, priority, case}; blind5.json is preferred, else the one
JSON there with a "tiles" list. Bench counts (rtl-sim/fma_toggle_v2's run_kinds.py output for the pool's tiles, rows keyed by
tile name) come from --counts, else from the one counts-*.json in pool_dir; without them the script prints the bench command
and exits 2. Nothing is refitted: every constant comes from m7.json, M6's m6.json and M5's m5.json, read and hashed here.

Per tile and model, on the card named:
  aifoundry3, aifoundry1c1 (600 MHz pinned): D, W over the type's own zeros, with a 95% band; the die rise over the kinds
    harness's 4.5 s run, C, with a 95% band (M5 has no heat term: null).
  aifoundry2 (its own governor, bursts of the kinds harness, E80's 6 s burst): the burst clock (MHz), the board power in the
    burst (W), D in the burst (board W less zeros' board W in their own burst), and the die's rise in the burst (C), each with
    a 95% band. M7's clock-and-voltage term and burst heat law are applied to each model's D at 600 MHz (M5 and M6 have no
    clock term of their own).
Band rules (m7.json band_rule): M7 power k x sqrt(pool^2 + s^2 x C x), M5/M6 1.96 x sqrt(pool^2 + s^2 x C x) (their frozen rule,
predict_blind4.py's), pool = the model's nested rms for the tile's format and card; heat M7 k_h x pool_h, M6 1.96 x its pool.
Writes <out>/predictions-<card>.json and .md (out defaults to pool_dir).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import glob
import hashlib
import json
import math
import os
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_m7 as M7  # noqa: E402
F = M7.F
ROOT = M7.ROOT
sha = lambda b: hashlib.sha256(b).hexdigest()
fsha = lambda p: sha(open(p, "rb").read())
CARDS = {"aifoundry3": "a3", "aifoundry1c1": "c1", "aifoundry2": "a2"}
HEAT_CARD = {"a3": "aifoundry3", "c1": "aifoundry1-c1"}


def manifest(pool):
    p = os.path.join(pool, "blind5.json")
    if not os.path.exists(p):
        c = [q for q in sorted(glob.glob(os.path.join(pool, "*.json"))) if isinstance(json.load(open(q)).get("tiles"), list)]
        if len(c) != 1:
            raise SystemExit(f"no single manifest with a 'tiles' list in {pool}: {c}")
        p = c[0]
    return p, json.load(open(p))


def zeros_S(card_json_prefix):
    """mean S (board W over idle) of the zeros items of each format, over the training experiments run on that card"""
    out = {}
    for t in ("fp32", "fp16", "int8"):
        v = []
        for e, d in M7.M6.EXPDIR.items():
            j = json.load(open(os.path.join(M7.DD, d, f"{e.lower()}.json")))
            z = j["items"].get(f"{t}.zeros")
            if j.get("card", "").startswith(card_json_prefix) and z and isinstance(z.get("S"), dict) and z["S"].get("mean") is not None:
                v.append(float(z["S"]["mean"]))
        out[t] = {"mean": statistics.mean(v), "n": len(v)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pool")
    ap.add_argument("card", choices=sorted(CARDS))
    ap.add_argument("--counts", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    pool = os.path.abspath(a.pool)
    cd = CARDS[a.card]
    mpath, man = manifest(pool)
    cpath = a.counts
    if cpath is None:
        c = sorted(glob.glob(os.path.join(pool, "counts-*.json")))
        cpath = c[0] if len(c) == 1 else None
    if cpath is None:
        spec = ",".join(f"{m['type']}:{m['name'].split('.', 1)[-1]}:{os.path.join(pool, m['file'])}" for m in man["tiles"])
        print("no bench counts for this pool. Run the bench (rtl-sim/fma_toggle_v2, Q133(b)'s README section Rerun), e.g.:\n"
              f"  python3 run_kinds.py --bin obj_vpu/Vtb --accum ./accum --settle ./settle_count --maps maps --kinds ../../tools/claims-v3/kinds "
              f"--only __none__ --jobs 6 --out counts-pool.json --extra-tiles {spec}\n"
              "then rerun with --counts counts-pool.json (rows are matched by tile name, or by type.name)")
        sys.exit(2)
    counts = json.load(open(cpath))["rows"]
    m7p = os.path.join(HERE, "m7.json")
    m6p = os.path.join(M7.M6D, "m6.json")
    m5p = os.path.join(M7.M5D, "m5.json")
    m7, m6, m5 = (json.load(open(p)) for p in (m7p, m6p, m5p))
    zeros = M7.zeros_counts()
    a2 = m7["aifoundry2"]
    rel = a2["relation"]
    B = {int(k): v for k, v in rel["B_w"].items()}
    SF = {int(k): v for k, v in rel["s_f"].items()}
    CZ, XFER = rel["c_zeros_w"], rel["xfer"]
    W, SIG = a2["burst_cap"]["W_star_used_w"], a2["burst_cap"]["sigma_w"]
    sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "e119"))
    import make_predictions_e119 as M119  # noqa: E402

    def levels(c):
        return {f: B[f] + c * SF[f] for f in (600, 700, 800)}

    def p_at(P, f):
        if f >= 800:
            return P[800]
        if f >= 700:
            return P[700] + (P[800] - P[700]) * (f - 700) / 100.0
        return P[600] + (P[700] - P[600]) * (f - 600) / 100.0 if f >= 600 else P[600]

    def burst(D, t):
        c = CZ[t] + D / XFER
        f = M119.dither(levels(c), W, SIG)[0]
        cz = CZ[t]
        fz = M119.dither(levels(cz), W, SIG)[0]
        P, Pz = p_at(levels(c), f), p_at(levels(cz), fz)
        return f, P, P - Pz
    e2e = a2["end_to_end_band"]
    bh = a2["burst_heat"]
    H7 = m7["heat"]
    H6 = m6["heat"]
    sz = {cc: zeros_S(HEAT_CARD[cc].split("-")[0] if cc == "a3" else "aifoundry1") for cc in ("a3", "c1")}
    out = {"_note": f"Q138(m) predict_blind5.py: frozen predictions for {os.path.relpath(pool, ROOT) if pool.startswith(ROOT) else os.path.basename(pool)} on {a.card}; nothing refitted",
           "card": a.card, "m7_sha256": fsha(m7p), "m6_sha256": fsha(m6p), "m5_sha256": fsha(m5p),
           "manifest": os.path.basename(mpath), "manifest_sha256": fsha(mpath), "counts_sha256": fsha(cpath),
           "predict_blind5_sha256": fsha(os.path.abspath(__file__)), "fit_m7_sha256": fsha(os.path.join(HERE, "fit_m7.py")),
           "zeros_S_w": sz.get(cd), "band_rule": m7["band_rule"], "tiles": {}}
    for meta in sorted(man["tiles"], key=lambda m: m["name"]):
        name, t = meta["name"], meta["type"]
        p = os.path.join(pool, meta["file"])
        h = fsha(p)
        crow = counts.get(name) or counts.get(f"{t}.{name}") or counts.get(name.split(".", 1)[-1])
        rec = {"type": t, "priority": meta.get("priority"), "case": meta.get("case"), "sha256": h,
               "sha256_matches_manifest": (h == meta["sha256"]["whole"]) if isinstance(meta.get("sha256"), dict) else None}
        if crow is None:
            rec["error"] = "no bench count"
            out["tiles"][name] = rec
            continue
        rec["check_mismatch"] = crow["mean"].get("check_mismatch")
        f = M7.feats_from_counts(crow, p, t, zeros)
        rec["features"] = f
        fam = "int8" if t == "int8" else "float"
        rate = F.RATE[t]
        for lab, mod in (("M7", m7["families"][fam]), ("M6", m6["families"][fam]), ("M5", m5["families"][fam])):
            x = np.array([rate * f[q] for q in mod["terms"]])
            b = np.array(mod["coef_J"])
            C = np.array(mod["cov_J2"])
            d = float(x @ b)
            pc = "c1" if cd == "c1" else "a3"
            s = 1.0
            if cd == "c1":
                s = mod["card1_scale_by_format"][t] if lab == "M7" else mod["card1_scale"]
            k = mod["band_k"] if lab == "M7" else 1.96
            pool_rms = mod["interval_pool_by_format_card"][f"{t}|{pc}"]["rms_w"]
            hw = k * math.sqrt(pool_rms ** 2 + s * s * float(x @ C @ x))
            r = {"D600_a3_footing_w": round(d, 4)}
            if cd in ("a3", "c1"):
                D = s * d
                r["D_w"] = round(D, 4)
                r["D_95"] = [round(D - hw, 4), round(D + hw, 4)]
                S = D + sz[cd][t]["mean"]
                r["S_w"] = round(S, 4)
                if lab == "M7":
                    g = H7["coef"].get(f"S|{HEAT_CARD[cd]}")
                    ph = H7["interval_pool_by_format_card_c"][f"{t}|{HEAT_CARD[cd]}"]["rms_c"]
                    dT, hh = g * S, H7["band_k"] * ph
                elif lab == "M6":
                    g = H6["coef"].get(f"S|{HEAT_CARD[cd]}")
                    dT, hh = g * S, 1.96 * H6["interval_pool_c"][t]
                else:
                    dT = hh = None
                r["dT_win_c"] = None if dT is None else round(dT, 3)
                r["dT_win_95"] = None if dT is None else [round(dT - hh, 3), round(dT + hh, 3)]
            else:
                fb, P, Db = burst(d, t)
                r.update({"burst_mhz": round(fb, 1), "burst_mhz_95": [round(fb - e2e["q95_abs_mhz"], 1), round(min(800.0, fb + e2e["q95_abs_mhz"]), 1)],
                          "burst_board_w": round(P, 2), "burst_board_95": [round(P - e2e["q95_abs_board_w"], 2), round(P + e2e["q95_abs_board_w"], 2)],
                          "burst_D_w": round(Db, 2), "burst_D_95": [round(Db - e2e["q95_abs_board_w"], 2), round(Db + e2e["q95_abs_board_w"], 2)],
                          "burst_die_rise_c": round(bh["k_used_c_per_w"] * (P - bh["P_idle_w"]), 2),
                          "burst_die_rise_95": [round(bh["k_used_c_per_w"] * (P - bh["P_idle_w"]) - bh["q95_abs_c"], 2), round(bh["k_used_c_per_w"] * (P - bh["P_idle_w"]) + bh["q95_abs_c"], 2)],
                          "clock_term": "M7's (frozen in m7.json aifoundry2)"})
            rec[lab] = r
        out["tiles"][name] = rec
    od = a.out or pool
    os.makedirs(od, exist_ok=True)
    js = os.path.join(od, f"predictions-{a.card}.json")
    json.dump(out, open(js, "w"), indent=1, sort_keys=True)
    L = [f"# Frozen predictions on {a.card} (Q138(m) predict_blind5.py: M7, M6, M5; nothing refitted)", "",
         f"m7.json `{out['m7_sha256']}`; m6.json `{out['m6_sha256']}`; m5.json `{out['m5_sha256']}`; manifest `{out['manifest']}` `{out['manifest_sha256']}`; counts `{out['counts_sha256']}`.", ""]
    if cd in ("a3", "c1"):
        L += ["D: W over the type's own zeros at 600 MHz on this card. dT: die rise over the kinds harness's 4.5 s run. Bands 95% (m7.json band_rule).", "",
              "| tile | prio | M7 D (W) | 95% | M6 D | 95% | M5 D | 95% | M7 dT (C) | 95% | M6 dT |", "|---|---|---:|---|---:|---|---:|---|---:|---|---:|"]
        for n, r in out["tiles"].items():
            if "error" in r:
                L.append(f"| `{n}` | | {r['error']} | | | | | | | | |")
                continue
            q = lambda m, k: r[m][k]
            L.append(f"| `{n}` | {r['priority']} | {q('M7','D_w'):.3f} | [{q('M7','D_95')[0]:.2f}, {q('M7','D_95')[1]:.2f}] | {q('M6','D_w'):.3f} | [{q('M6','D_95')[0]:.2f}, {q('M6','D_95')[1]:.2f}] | "
                     f"{q('M5','D_w'):.3f} | [{q('M5','D_95')[0]:.2f}, {q('M5','D_95')[1]:.2f}] | {q('M7','dT_win_c'):.2f} | [{q('M7','dT_win_95')[0]:.2f}, {q('M7','dT_win_95')[1]:.2f}] | {q('M6','dT_win_c'):.2f} |")
    else:
        L += ["Bursts under aifoundry2's own governor: clock (MHz), board W, D (board W less zeros' in their own burst), die rise (C); 95% bands.", "",
              "| tile | prio | M7 MHz | 95% | M7 board W | 95% | M7 D (W) | M7 die rise (C) | 95% | M6 MHz / W | M5 MHz / W |", "|---|---|---:|---|---:|---|---:|---:|---|---|---|"]
        for n, r in out["tiles"].items():
            if "error" in r:
                L.append(f"| `{n}` | | {r['error']} | | | | | | | | |")
                continue
            m = r["M7"]
            L.append(f"| `{n}` | {r['priority']} | {m['burst_mhz']:.1f} | [{m['burst_mhz_95'][0]:.0f}, {m['burst_mhz_95'][1]:.0f}] | {m['burst_board_w']:.2f} | [{m['burst_board_95'][0]:.1f}, {m['burst_board_95'][1]:.1f}] | "
                     f"{m['burst_D_w']:.2f} | {m['burst_die_rise_c']:.2f} | [{m['burst_die_rise_95'][0]:.2f}, {m['burst_die_rise_95'][1]:.2f}] | {r['M6']['burst_mhz']:.1f} / {r['M6']['burst_board_w']:.2f} | {r['M5']['burst_mhz']:.1f} / {r['M5']['burst_board_w']:.2f} |")
    open(os.path.join(od, f"predictions-{a.card}.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
