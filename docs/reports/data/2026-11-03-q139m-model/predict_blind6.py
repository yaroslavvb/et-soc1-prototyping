#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q139(m): frozen predictions with bands for a pool of kinds tiles, by M8 and, through the same interface, M7 and M6 as frozen.

    python3 predict_blind6.py <pool_dir> <card> [--counts <counts.json>] [--out <dir>]
        card: aifoundry3 | aifoundry1c1 | aifoundry2

<pool_dir> holds the tiles and a manifest in blind pool 5's layout (tools/claims-v3/kinds/blind5/): a JSON file with a "tiles"
list of {name, type, file (relative to pool_dir), sha256: {whole}, priority, case}; blind6.json is preferred, then blind5.json,
else the one JSON there with a "tiles" list. Bench counts (rtl-sim/fma_toggle_v2's run_kinds.py output for the pool's tiles, rows
keyed by tile name) come from --counts, else from the one counts-*.json in pool_dir; without them the script prints the bench
command and exits 2. Nothing is refitted: every constant comes from m8.json, Q138(m)'s m7.json and Q137(m)'s m6.json, read and
hashed here. M8's extra features (the C-register descriptors, the int8 B position and byte features) come from the tile bytes.

Per tile and model, on the card named:
  aifoundry3, aifoundry1c1 (600 MHz pinned): D, W over the type's own zeros on Q139(u)'s footing (reduce with
    reduce_footing.K_FROZEN and A2 once), with a 95% band; the die rise over the kinds harness's 4.5 s run (C) with a 95% band
    (M8 carries M7's heat law, applied to M8's S).
  aifoundry2 (its own governor, E80's 6 s bursts; the footing: dips kept, as E80/E83/E143's kspeed reductions): the burst clock
    (MHz), the board power in the burst (W), D in the burst, the die's rise (C), each with a 95% band, and M8's predicted PEAK
    board power (expected, and its 95% upper value) for the 82 W stop. M7 and M6 go through M7's frozen clock term, as
    predict_blind5.py did; only M8 predicts the peak.
Band rules: m8.json band_rule (M8), m7.json's band_k for M7 (k x sqrt(pool^2 + s^2 x C x)), 1.96 x sqrt(pool^2 + s^2 x C x) for M6.
Writes <out>/predictions-<card>.json and .md (out defaults to pool_dir).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import glob
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_m8 as M8  # noqa: E402  (imports fit_m7, fit_m6, fit_m5, reduce_footing, make_blind5 unchanged)
import numpy as np  # noqa: E402

M7 = M8.M7
F = M7.F
ROOT = M8.ROOT
sys.path.insert(0, M8.M7D)
import predict_blind5 as P5  # noqa: E402  (zeros_S, unchanged)
sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
fsha = lambda p: sha(open(p, "rb").read())  # noqa: E731
CARDS = {"aifoundry3": "a3", "aifoundry1c1": "c1", "aifoundry2": "a2"}
HEAT_CARD = {"a3": "aifoundry3", "c1": "aifoundry1-c1"}


def manifest(pool):
    for nm in ("blind6.json", "blind5.json"):
        p = os.path.join(pool, nm)
        if os.path.exists(p):
            return p, json.load(open(p))
    c = [q for q in sorted(glob.glob(os.path.join(pool, "*.json"))) if isinstance(json.load(open(q)).get("tiles"), list)]
    if len(c) != 1:
        raise SystemExit(f"no single manifest with a 'tiles' list in {pool}: {c}")
    return c[0], json.load(open(c[0]))


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
    m8p, m7p, m6p = os.path.join(HERE, "m8.json"), os.path.join(M8.M7D, "m7.json"), os.path.join(M7.M6D, "m6.json")
    m8, m7, m6 = (json.load(open(p)) for p in (m8p, m7p, m6p))
    zeros = M7.zeros_counts()
    import make_predictions_e119 as M119  # noqa: E402  (fit_m8 put tools/claims-v3/e119 on the path)
    # M7's frozen aifoundry2 relation (for M7 and M6, exactly as predict_blind5.py)
    a7 = m7["aifoundry2"]
    rel = a7["relation"]
    B = {int(k): v for k, v in rel["B_w"].items()}
    SF = {int(k): v for k, v in rel["s_f"].items()}
    CZ7, XFER7 = rel["c_zeros_w"], rel["xfer"]
    W7, SIG = a7["burst_cap"]["W_star_used_w"], a7["burst_cap"]["sigma_w"]
    a8 = m8["aifoundry2"]
    par8 = a8["params"]

    def levels(c):
        return {f: B[f] + c * SF[f] for f in (600, 700, 800)}

    def p_at(P, f):
        if f >= 800:
            return P[800]
        if f >= 700:
            return P[700] + (P[800] - P[700]) * (f - 700) / 100.0
        return P[600] + (P[700] - P[600]) * (f - 600) / 100.0 if f >= 600 else P[600]

    def burst7(D, t):
        c = CZ7[t] + D / XFER7
        f = M119.dither(levels(c), W7, SIG)[0]
        cz = CZ7[t]
        fz = M119.dither(levels(cz), W7, SIG)[0]
        P, Pz = p_at(levels(c), f), p_at(levels(cz), fz)
        return f, P, P - Pz

    def cap8(c):
        P8 = B[800] + c * SF[800]
        return par8["W0"] + par8["gamma"] * max(0.0, P8 - par8["W0"]), P8

    def burst8(D, t):
        c = par8["c_zeros_w"][t] + par8["g"][t] * D
        W, P8 = cap8(c)
        f = M119.dither(levels(c), W, SIG)[0]
        cz = par8["c_zeros_w"][t]
        Wz, _ = cap8(cz)
        fz = M119.dither(levels(cz), Wz, SIG)[0]
        P, Pz = p_at(levels(c), f), p_at(levels(cz), fz)
        return f, P, P - Pz, P8
    bh = a7["burst_heat"]
    H7, H6 = m7["heat"], m6["heat"]
    sz = {cc: P5.zeros_S("aifoundry3" if cc == "a3" else "aifoundry1") for cc in ("a3", "c1")}
    out = {"_note": f"Q139(m) predict_blind6.py: frozen predictions for {os.path.relpath(pool, ROOT) if pool.startswith(ROOT) else os.path.basename(pool)} on {a.card}; nothing refitted",
           "card": a.card, "m8_sha256": fsha(m8p), "m7_sha256": fsha(m7p), "m6_sha256": fsha(m6p),
           "manifest": os.path.basename(mpath), "manifest_sha256": fsha(mpath), "counts_sha256": fsha(cpath),
           "predict_blind6_sha256": fsha(os.path.abspath(__file__)), "fit_m8_sha256": fsha(os.path.join(HERE, "fit_m8.py")),
           "footing": m8["footing"], "zeros_S_w": sz.get(cd), "band_rule_M8": m8["band_rule"], "tiles": {}}
    e2e8 = a8["bands"]
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
        f8 = dict(f)
        f8.update(M8.m8_extra(p, t))
        M8.finish(f8)
        rec["features"] = f8
        fam = "int8" if t == "int8" else "float"
        rate = F.RATE[t]
        for lab, mod, fv in (("M8", m8["families"][fam], f8), ("M7", m7["families"][fam], f), ("M6", m6["families"][fam], f)):
            x = np.array([rate * fv[q] for q in mod["terms"]])
            b = np.array(mod["coef_J"])
            C = np.array(mod["cov_J2"])
            d = float(x @ b)
            pc = "c1" if cd == "c1" else "a3"
            s = 1.0
            if cd == "c1":
                s = mod["card1_scale_by_format"][t] if lab in ("M8", "M7") else mod["card1_scale"]
            k = mod["band_k"] if lab in ("M8", "M7") else 1.96
            pool_rms = mod["interval_pool_by_format_card"][f"{t}|{pc}"]["rms_w"]
            hw = k * math.sqrt(pool_rms ** 2 + s * s * float(x @ C @ x))
            r = {"D600_a3_footing_w": round(d, 4)}
            if cd in ("a3", "c1"):
                D = s * d
                r["D_w"] = round(D, 4)
                r["D_95"] = [round(D - hw, 4), round(D + hw, 4)]
                S = D + sz[cd][t]["mean"]
                r["S_w"] = round(S, 4)
                if lab in ("M8", "M7"):
                    g = H7["coef"].get(f"S|{HEAT_CARD[cd]}")
                    ph = H7["interval_pool_by_format_card_c"][f"{t}|{HEAT_CARD[cd]}"]["rms_c"]
                    dT, hh = g * S, H7["band_k"] * ph
                else:
                    g = H6["coef"].get(f"S|{HEAT_CARD[cd]}")
                    dT, hh = g * S, 1.96 * H6["interval_pool_c"][t]
                r["dT_win_c"] = round(dT, 3)
                r["dT_win_95"] = [round(dT - hh, 3), round(dT + hh, 3)]
            elif lab == "M8":
                fb, P, Db, P8 = burst8(d, t)
                c_hi = par8["c_zeros_w"][t] + par8["g"][t] * (d + hw)
                P8_hi = B[800] + c_hi * SF[800]
                pk = a8["peak"]
                r.update({"burst_mhz": round(fb, 1), "burst_mhz_95": [round(fb - e2e8["q95_abs_mhz_e2e"], 1), round(min(800.0, fb + e2e8["q95_abs_mhz_e2e"]), 1)],
                          "burst_board_w": round(P, 2), "burst_board_95": [round(P - e2e8["q95_abs_board_w_e2e"], 2), round(P + e2e8["q95_abs_board_w_e2e"], 2)],
                          "burst_D_w": round(Db, 2), "burst_D_95": [round(Db - e2e8["q95_abs_board_w_e2e"], 2), round(Db + e2e8["q95_abs_board_w_e2e"], 2)],
                          "burst_die_rise_c": round(bh["k_used_c_per_w"] * (P - bh["P_idle_w"]), 2),
                          "burst_die_rise_95": [round(bh["k_used_c_per_w"] * (P - bh["P_idle_w"]) - bh["q95_abs_c"], 2), round(bh["k_used_c_per_w"] * (P - bh["P_idle_w"]) + bh["q95_abs_c"], 2)],
                          "P800_w": round(P8, 2), "peak_board_w": round(P8 + pk["excess_median_w"], 2),
                          "peak_board_hi95_w": round(P8_hi + pk["excess_q95_w"], 2),
                          "peak_over_82w": bool(P8_hi + pk["excess_q95_w"] > 82.0),
                          "clock_term": "M8's (m8.json aifoundry2: zeros level, D scale and cap as kept)"})
            else:
                fb, P, Db = burst7(d, t)
                e2e = a7["end_to_end_band"]
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
    L = [f"# Frozen predictions on {a.card} (Q139(m) predict_blind6.py: M8, M7, M6; nothing refitted)", "",
         f"m8.json `{out['m8_sha256']}`; m7.json `{out['m7_sha256']}`; m6.json `{out['m6_sha256']}`; manifest `{out['manifest']}` `{out['manifest_sha256']}`; counts `{out['counts_sha256']}`.", ""]
    if cd in ("a3", "c1"):
        L += ["D: W over the type's own zeros at 600 MHz on this card, Q139(u)'s footing. dT: die rise over the kinds harness's 4.5 s run. Bands 95%.", "",
              "| tile | prio | M8 D (W) | 95% | M7 D | 95% | M6 D | 95% | M8 dT (C) | 95% |", "|---|---|---:|---|---:|---|---:|---|---:|---|"]
        for n, r in out["tiles"].items():
            if "error" in r:
                L.append(f"| `{n}` | | {r['error']} | | | | | | | |")
                continue
            q = lambda m, k: r[m][k]  # noqa: E731
            L.append(f"| `{n}` | {r['priority']} | {q('M8','D_w'):.3f} | [{q('M8','D_95')[0]:.2f}, {q('M8','D_95')[1]:.2f}] | {q('M7','D_w'):.3f} | [{q('M7','D_95')[0]:.2f}, {q('M7','D_95')[1]:.2f}] | "
                     f"{q('M6','D_w'):.3f} | [{q('M6','D_95')[0]:.2f}, {q('M6','D_95')[1]:.2f}] | {q('M8','dT_win_c'):.2f} | [{q('M8','dT_win_95')[0]:.2f}, {q('M8','dT_win_95')[1]:.2f}] |")
    else:
        L += ["Bursts under aifoundry2's own governor (dips kept): clock (MHz), board W, D, die rise (C); 95% bands; M8's peak board power (expected / 95% upper; the stop is 82 W).", "",
              "| tile | prio | M8 MHz | 95% | M8 board W | 95% | M8 peak W | peak hi95 | > 82 W? | M8 die rise (C) | M7 MHz / W | M6 MHz / W |", "|---|---|---:|---|---:|---|---:|---:|---|---:|---|---|"]
        for n, r in out["tiles"].items():
            if "error" in r:
                L.append(f"| `{n}` | | {r['error']} | | | | | | | | | |")
                continue
            m = r["M8"]
            L.append(f"| `{n}` | {r['priority']} | {m['burst_mhz']:.1f} | [{m['burst_mhz_95'][0]:.0f}, {m['burst_mhz_95'][1]:.0f}] | {m['burst_board_w']:.2f} | [{m['burst_board_95'][0]:.1f}, {m['burst_board_95'][1]:.1f}] | "
                     f"{m['peak_board_w']:.2f} | {m['peak_board_hi95_w']:.2f} | {'YES' if m['peak_over_82w'] else 'no'} | {m['burst_die_rise_c']:.2f} | {r['M7']['burst_mhz']:.1f} / {r['M7']['burst_board_w']:.2f} | {r['M6']['burst_mhz']:.1f} / {r['M6']['burst_board_w']:.2f} |")
    open(os.path.join(od, f"predictions-{a.card}.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
