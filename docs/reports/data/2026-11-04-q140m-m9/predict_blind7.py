#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q140(m): frozen predictions with bands for a pool of kinds tiles, by M9 and, through the same interface, M8, M7 and M6 as frozen.

    python3 predict_blind7.py <pool_dir> <card> [--counts <counts.json>] [--out <dir>]
                              [--a2-terms <m9_a2.json>] [--a2-session <reads.json>] [--a2-die-start <C>]
        card: aifoundry3 | aifoundry1c1 | aifoundry2

<pool_dir> holds the tiles and a manifest in blind pool 5's layout (a JSON file with a "tiles" list of {name, type, file relative to
pool_dir, sha256: {whole}, priority, case}); blind7.json is preferred, then blind6.json, then blind5.json, else the one JSON there with a
"tiles" list. Bench counts (rtl-sim/fma_toggle_v2's run_kinds.py output for the pool's tiles, at its three launch points) come from
--counts, else from the one counts-*.json in pool_dir; without them the script prints the bench command and exits 2. Nothing is
refitted: every constant comes from m9.json, Q139(m)'s m8.json, Q138(m)'s m7.json and Q137(m)'s m6.json.

Per tile and model, on the card named:
  aifoundry3, aifoundry1c1 (600 MHz pinned): D, W over the type's own zeros on Q139(u)'s footing, with a 95% band; the die rise over
    the kinds harness's 4.5 s run with a 95% band (M9 and M8 carry M7's heat law, applied to their own S).
  aifoundry2 (its own governor, E80's 6 s bursts): M8, M7 and M6 exactly as Q139(m)'s predict_blind6.py. M9: its D at 600 MHz on
    aifoundry3's footing (with its band) goes through
      - without --a2-terms: M8's frozen aifoundry2 relation, bands and peak rule (m8.json aifoundry2, carried in m9.json);
      - with --a2-terms <m9_a2.json>: Q140(l)'s part: predict_m9_a2.py beside that JSON (or the JSON's "predictor" entry, {"file",
        "function"}), called per tile as burst(D600, type, anchors=<--a2-session>, die_starts=[<--a2-die-start>] or None,
        D_band_hw=M9's 95% half-width on D); a module with no burst() but a predict_tiles(terms, tiles, session) is called once
        instead. The result is the tile's M9.a2_q140l block, and a2_part.primary says which aifoundry2 prediction is M9's. If no
        predictor is found, the block says so and the handoff file below is the input to apply Q140(l)'s frozen code by hand.
        --a2-session is a JSON of the session's own zeros-anchor reads, {format: [{burst_w, burst_mhz, die_start}, ...]} (or that
        dict under "anchors"), as predict_m9_a2.burst takes them.
    Always written for aifoundry2: <out>/a2-inputs-aifoundry2.json, every tile's M9 and M8 D at 600 MHz with bands (the input any
    aifoundry2 relation takes), so Q140(x) can apply Q140(l)'s frozen code to it mechanically.
Band rules: m9.json band_rule (M9), m8.json's (M8), m7.json's band_k (M7), 1.96 (M6).
Writes <out>/predictions-<card>.json and .md (out defaults to pool_dir).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import glob
import hashlib
import importlib.util
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_m9 as M9  # noqa: E402  (imports fit_m8, fit_m7, fit_m6, fit_m5, reduce_footing, make_blind5 unchanged)
import numpy as np  # noqa: E402

M8 = M9.M8
M7 = M8.M7
F = M7.F
ROOT = M9.ROOT
sys.path.insert(0, M8.M7D)
import predict_blind5 as P5  # noqa: E402  (zeros_S, unchanged)
sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
fsha = lambda p: sha(open(p, "rb").read())  # noqa: E731
CARDS = {"aifoundry3": "a3", "aifoundry1c1": "c1", "aifoundry2": "a2"}
HEAT_CARD = {"a3": "aifoundry3", "c1": "aifoundry1-c1"}


def manifest(pool):
    for nm in ("blind7.json", "blind6.json", "blind5.json"):
        p = os.path.join(pool, nm)
        if os.path.exists(p):
            return p, json.load(open(p))
    c = [q for q in sorted(glob.glob(os.path.join(pool, "*.json"))) if isinstance(json.load(open(q)).get("tiles"), list)]
    if len(c) != 1:
        raise SystemExit(f"no single manifest with a 'tiles' list in {pool}: {c}")
    return c[0], json.load(open(c[0]))


def load_a2_predictor(terms_path):
    """Q140(l)'s predictor module: the JSON's "predictor" entry, else predict_m9_a2.py beside it. Returns (terms, module, path, note)."""
    terms = json.load(open(terms_path))
    d = os.path.dirname(os.path.abspath(terms_path))
    spec = terms.get("predictor") if isinstance(terms.get("predictor"), dict) else None
    cands = []
    if spec and spec.get("file"):
        cands += [os.path.join(d, spec["file"]), os.path.join(ROOT, spec["file"])]
    cands.append(os.path.join(d, "predict_m9_a2.py"))
    path = next((p for p in cands if os.path.exists(p)), None)
    if path is None:
        return terms, None, None, f"no predictor found beside {os.path.basename(terms_path)}"
    if d not in sys.path:
        sys.path.insert(0, d)
    s = importlib.util.spec_from_file_location("m9_a2_predictor", path)
    mod = importlib.util.module_from_spec(s)
    s.loader.exec_module(mod)
    return terms, mod, path, os.path.basename(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pool")
    ap.add_argument("card", choices=sorted(CARDS))
    ap.add_argument("--counts", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--a2-terms", default=None, help="Q140(l)'s m9_a2.json (aifoundry2 only)")
    ap.add_argument("--a2-session", default=None, help="the session's own zeros-anchor reads for Q140(l)'s predictor (aifoundry2 only)")
    ap.add_argument("--a2-die-start", type=float, default=None, help="a nominal die start (C) for Q140(l)'s predictor (aifoundry2 only)")
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
        print("no bench counts for this pool. Run the bench (rtl-sim/fma_toggle_v2, Q133(b)'s README section Rerun; the build whose seven "
              "files Q139(x) hashed in tools/claims-v3/kinds/blind6/README-predictions.md), at its default three launch points, e.g.:\n"
              f"  python3 run_kinds.py --bin obj_vpu/Vtb --accum ./accum --settle ./settle_count --maps maps --kinds ../../tools/claims-v3/kinds "
              f"--only __none__ --jobs 4 --out counts-pool.json --extra-tiles {spec}\n"
              "then rerun with --counts counts-pool.json (rows are matched by tile name, or by type.name)")
        sys.exit(2)
    counts = json.load(open(cpath))["rows"]
    m9p = os.path.join(HERE, "m9.json")
    m8p, m7p, m6p = os.path.join(M9.M8D, "m8.json"), os.path.join(M8.M7D, "m7.json"), os.path.join(M7.M6D, "m6.json")
    m9, m8, m7, m6 = (json.load(open(p)) for p in (m9p, m8p, m7p, m6p))
    zeros = M7.zeros_counts()
    zr = M9.zeros_rows()
    import make_predictions_e119 as M119  # noqa: E402  (fit_m8 put tools/claims-v3/e119 on the path)
    # M7's frozen aifoundry2 relation (for M7 and M6, exactly as predict_blind5.py / predict_blind6.py)
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
    out = {"_note": f"Q140(m) predict_blind7.py: frozen predictions for {os.path.relpath(pool, ROOT) if pool.startswith(ROOT) else os.path.basename(pool)} "
                    f"on {a.card}; nothing refitted",
           "card": a.card, "m9_sha256": fsha(m9p), "m8_sha256": fsha(m8p), "m7_sha256": fsha(m7p), "m6_sha256": fsha(m6p),
           "manifest": os.path.basename(mpath), "manifest_sha256": fsha(mpath), "counts_sha256": fsha(cpath),
           "predict_blind7_sha256": fsha(os.path.abspath(__file__)), "fit_m9_sha256": fsha(os.path.join(HERE, "fit_m9.py")),
           "footing": m9["footing"], "zeros_S_w": sz.get(cd), "band_rule_M9": m9["band_rule"], "band_rule_M8": m8["band_rule"], "tiles": {}}
    e2e8 = a8["bands"]
    handoff = {}
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
        f9 = dict(f8)
        f9.update(M9.m9_extra(f8, t, crow, p, zr))
        rec["features"] = f9
        fam = "int8" if t == "int8" else "float"
        rate = F.RATE[t]
        for lab, mod, fv in (("M9", m9["families"][fam], f9), ("M8", m8["families"][fam], f8),
                             ("M7", m7["families"][fam], f), ("M6", m6["families"][fam], f)):
            x = np.array([rate * fv[q] for q in mod["terms"]])
            b = np.array(mod["coef_J"])
            C = np.array(mod["cov_J2"])
            d = float(x @ b)
            pc = "c1" if cd == "c1" else "a3"
            s = 1.0
            if cd == "c1":
                s = mod["card1_scale_by_format"][t] if lab in ("M9", "M8", "M7") else mod["card1_scale"]
            k = mod["band_k"] if lab in ("M9", "M8", "M7") else 1.96
            pool_rms = mod["interval_pool_by_format_card"][f"{t}|{pc}"]["rms_w"]
            hw = k * math.sqrt(pool_rms ** 2 + s * s * float(x @ C @ x))
            r = {"D600_a3_footing_w": round(d, 4)}
            if lab == "M9":
                r["form"] = mod["form"]
                r["D600_a3_95"] = [round(d - hw, 4), round(d + hw, 4)] if cd == "a2" else None
            if cd in ("a3", "c1"):
                D = s * d
                r["D_w"] = round(D, 4)
                r["D_95"] = [round(D - hw, 4), round(D + hw, 4)]
                S = D + sz[cd][t]["mean"]
                r["S_w"] = round(S, 4)
                if lab in ("M9", "M8", "M7"):
                    g = H7["coef"].get(f"S|{HEAT_CARD[cd]}")
                    ph = H7["interval_pool_by_format_card_c"][f"{t}|{HEAT_CARD[cd]}"]["rms_c"]
                    dT, hh = g * S, H7["band_k"] * ph
                else:
                    g = H6["coef"].get(f"S|{HEAT_CARD[cd]}")
                    dT, hh = g * S, 1.96 * H6["interval_pool_c"][t]
                r["dT_win_c"] = round(dT, 3)
                r["dT_win_95"] = [round(dT - hh, 3), round(dT + hh, 3)]
            elif lab in ("M9", "M8"):
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
                          "clock_term": "M8's (m8.json aifoundry2: zeros level, D scale and cap as kept)" if lab == "M8"
                          else "M8's frozen aifoundry2 relation, bands and peak rule (m8.json aifoundry2), applied to M9's D600"})
                if lab == "M9":
                    handoff[name] = {"name": name, "type": t, "D600_a3_footing_w": round(d, 4), "D600_a3_95": [round(d - hw, 4), round(d + hw, 4)]}
                else:
                    handoff[name]["M8_D600_a3_footing_w"] = round(d, 4)
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
    if cd == "a2":
        hp = os.path.join(od, "a2-inputs-aifoundry2.json")
        json.dump({"_note": "M9's (and M8's) D at 600 MHz on aifoundry3's footing per tile, with M9's 95% band: the input of any aifoundry2 "
                            "relation (Q140(l)'s predict_m9_a2.py, or M8's frozen one)", "m9_sha256": out["m9_sha256"], "tiles": handoff},
                  open(hp, "w"), indent=1, sort_keys=True)
        out["a2_inputs"] = os.path.basename(hp)
        out["a2_part"] = {"applied": "M8's frozen aifoundry2 relation (no --a2-terms)"}
        out["a2_part"]["primary"] = "m8_relation"
        if a.a2_terms:
            terms, mod, ppath, note = load_a2_predictor(a.a2_terms)
            tp = os.path.abspath(a.a2_terms)
            out["a2_part"] = {"terms_file": os.path.relpath(tp, ROOT) if tp.startswith(ROOT) else os.path.basename(tp),
                              "terms_sha256": fsha(a.a2_terms), "predictor": note, "predictor_sha256": fsha(ppath) if ppath else None,
                              "session_file": os.path.basename(a.a2_session) if a.a2_session else None,
                              "session_sha256": fsha(a.a2_session) if a.a2_session else None, "die_start_c": a.a2_die_start,
                              "primary": "m8_relation"}
            sess = json.load(open(a.a2_session)) if a.a2_session else None
            anchors = sess.get("anchors", sess) if isinstance(sess, dict) else None
            if mod is not None and getattr(mod, "M9_SHA256", None) and getattr(mod, "M9_SHA256") != out["a2_part"]["terms_sha256"]:
                out["a2_part"]["warning"] = "the predictor reads its own m9_a2.json, whose sha256 differs from --a2-terms"
            if mod is not None and callable(getattr(mod, "burst", None)):
                ds = [a.a2_die_start] if a.a2_die_start is not None else None
                for n, hv in sorted(handoff.items()):
                    lo, hi = hv["D600_a3_95"]
                    res = mod.burst(hv["D600_a3_footing_w"], hv["type"], anchors=anchors, die_starts=ds, D_band_hw=0.5 * (hi - lo))
                    out["tiles"][n]["M9"]["a2_q140l"] = res
                out["a2_part"].update({"applied": f"Q140(l)'s part ({note} burst()), called on M9's D600 per tile", "primary": "a2_q140l"})
            elif mod is not None and callable(getattr(mod, "predict_tiles", None)):
                res = mod.predict_tiles(terms, [handoff[n] for n in sorted(handoff)], sess)
                for n, v in (res or {}).items():
                    if n in out["tiles"] and "M9" in out["tiles"][n]:
                        out["tiles"][n]["M9"]["a2_q140l"] = v
                out["a2_part"].update({"applied": f"Q140(l)'s part ({note} predict_tiles()), called on M9's D600 per tile", "primary": "a2_q140l"})
            else:
                why = note if mod is None else f"{note} has neither burst() nor predict_tiles()"
                out["a2_part"]["applied"] = f"NOT APPLIED: {why}; apply Q140(l)'s frozen code to {out['a2_inputs']} (M9's D600 per tile)"
    js = os.path.join(od, f"predictions-{a.card}.json")
    json.dump(out, open(js, "w"), indent=1, sort_keys=True)
    L = [f"# Frozen predictions on {a.card} (Q140(m) predict_blind7.py: M9, M8, M7, M6; nothing refitted)", "",
         f"m9.json `{out['m9_sha256']}`; m8.json `{out['m8_sha256']}`; m7.json `{out['m7_sha256']}`; m6.json `{out['m6_sha256']}`; "
         f"manifest `{out['manifest']}` `{out['manifest_sha256']}`; counts `{out['counts_sha256']}`.", ""]
    if cd in ("a3", "c1"):
        L += ["D: W over the type's own zeros at 600 MHz on this card, Q139(u)'s footing. dT: die rise over the kinds harness's 4.5 s run. Bands 95%.", "",
              "| tile | prio | M9 D (W) | 95% | M8 D | 95% | M7 D | M6 D | M9 dT (C) | 95% |", "|---|---|---:|---|---:|---|---:|---:|---:|---|"]
        for n, r in out["tiles"].items():
            if "error" in r:
                L.append(f"| `{n}` | | {r['error']} | | | | | | | |")
                continue
            q = lambda m, k: r[m][k]  # noqa: E731
            L.append(f"| `{n}` | {r['priority']} | {q('M9','D_w'):.3f} | [{q('M9','D_95')[0]:.2f}, {q('M9','D_95')[1]:.2f}] | {q('M8','D_w'):.3f} | "
                     f"[{q('M8','D_95')[0]:.2f}, {q('M8','D_95')[1]:.2f}] | {q('M7','D_w'):.3f} | {q('M6','D_w'):.3f} | {q('M9','dT_win_c'):.2f} | "
                     f"[{q('M9','dT_win_95')[0]:.2f}, {q('M9','dT_win_95')[1]:.2f}] |")
    else:
        L += [f"Bursts under aifoundry2's own governor (dips kept). M9 here: {out['a2_part']['applied']}. Clock (MHz), board W, die rise (C); 95% bands; "
              "the peak board power (expected / 95% upper; the stop is 82 W).", "",
              "| tile | prio | M9 D600 (W) | M9 MHz | M9 board W | M9 peak W / hi95 | > 82 W? | M8 MHz / W | M8 peak hi95 | M7 MHz / W | M6 MHz / W |",
              "|---|---|---:|---:|---:|---|---|---|---:|---|---|"]
        for n, r in out["tiles"].items():
            if "error" in r:
                L.append(f"| `{n}` | | {r['error']} | | | | | | | | |")
                continue
            m, e = r["M9"], r["M8"]
            L.append(f"| `{n}` | {r['priority']} | {m['D600_a3_footing_w']:.3f} | {m['burst_mhz']:.1f} | {m['burst_board_w']:.2f} | {m['peak_board_w']:.2f} / "
                     f"{m['peak_board_hi95_w']:.2f} | {'YES' if m['peak_over_82w'] else 'no'} | {e['burst_mhz']:.1f} / {e['burst_board_w']:.2f} | "
                     f"{e['peak_board_hi95_w']:.2f} | {r['M7']['burst_mhz']:.1f} / {r['M7']['burst_board_w']:.2f} | {r['M6']['burst_mhz']:.1f} / {r['M6']['burst_board_w']:.2f} |")
    open(os.path.join(od, f"predictions-{a.card}.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
