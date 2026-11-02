#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q137(m): M6 = M5's power model refitted on every counted, measured kinds tile (22 experiments), extended with per-flip
terms, plus a heat term (die rise per board W per card, with its time constants). Forms compared by NESTED
leave-one-kind-out; the chosen forms frozen as M6.

    python3 fit_m6.py      # writes loko-m6.json, m6.json, rows-m6.json, heat-rows.json beside it

Power. Rows: M5's (fit_m5.assemble: E78 E82 E86 E88 E90 E91 E92 E93 E94 E95 E103 E104 E106) plus E102 E108 E115 E121 E122 E123
E127 E128 E131 (m6_rows.assemble), D in W over the type's zeros at 600 MHz. Counts: rtl-sim/fma_toggle_v2 as in M5; E123's 36
re-draws counted for this lane (counts-e123.json). Card 1 on card 0's footing by E82's model-free scale (as M5).
New features, from the tile bytes through make_kinds' issue stream (no bench needed):
  a_sign a_exp a_mant b_sign b_exp b_mant : operand-bit flips between consecutive micro-ops, by field and side (A broadcast
                                            to every column slot, as abits); int8: sign and magnitude fields
  psgn   : product-sign flips: a lane's sign(a) xor sign(b) changing between consecutive micro-ops (the sign term; E88 E92
           E104 E106 E108 E122 E128)
  a_small: the A side's flips when every A flip of the tile lies in the 4 low mantissa bits (E113/E125: A pays about two
           thirds of B's price per flip, except a mask of 2-4 low bits, which pays nearly the full price)
  gtr    : gate-state changes between consecutive micro-ops (M5's; the B-lane gate result of E127 and the gated lanes of E93/E121)
Heat. Rows: every item of the same experiments with a die rise over its window (dT_win, die C at the window less the
launch reading) and S (board W over idle); run length and launch offset from each experiment's runs.csv.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import hashlib
import json
import math
import os
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m6_rows as R  # noqa: E402
F = R.F
mk = F.mk
DD = R.DD

# ------------------------------------------------------------------ flip features (tile bytes only)
SMALL = {"fp32": 0x0000000F, "fp16": 0x000F000F, "int8": 0x03030303}


def pc(x):
    return mk.popcount32(np.asarray(x, dtype=np.uint64).astype(np.uint32))


def flip_feats(path, t):
    raw = open(path, "rb").read()
    aw, bw = mk.words_of(raw)
    a, b = mk.issue_streams_fast(aw, bw, t)
    a = a.astype(np.uint64)
    b = b.astype(np.uint64)
    da = a ^ np.roll(a, -1)
    db = b ^ np.roll(b, -1, axis=0)
    slots = mk.COLUMN_SLOTS[t]
    out = {}
    fl = mk.FIELDS[t]
    names = ("sign", "exp", "mant") if t != "int8" else ("sign", "mag")
    for nm in names:
        m = np.uint64(fl[nm])
        out[f"a_{nm}"] = float(pc(da & m).sum() * slots)
        out[f"b_{nm}"] = float(pc(db & m).sum())
    if t == "int8":
        out["a_exp"], out["b_exp"] = 0.0, 0.0
        out["a_mant"], out["b_mant"] = out.pop("a_mag"), out.pop("b_mag")
    sm = np.uint64(fl["sign"])
    ps = (a[:, None] ^ b) & sm
    out["psgn"] = float(pc(ps ^ np.roll(ps, -1, axis=0)).sum())
    allA = int(pc(da).sum())
    loA = int(pc(da & np.uint64(SMALL[t])).sum())
    out["a_small"] = float(allA * slots) if allA > 0 and loA == allA else 0.0
    return out


# ------------------------------------------------------------------ the forms (written before any fit ran)
BASE_F = ["mult", "add32", "add16", "bus", "rest", "clk"]          # M5's F10
BASE_I = ["nets_nobus", "bus", "clk"]                                # M5's I0 (I3)
FLD = ["a_sign", "a_exp", "a_mant", "b_sign", "b_exp", "b_mant"]
FORMS = {
    "float": {
        "G0_M5": BASE_F,
        "G1_gtr": BASE_F + ["gtr"],
        "G2_psgn": BASE_F + ["psgn"],
        "G3_fields": BASE_F + FLD,
        "G4_gtr_psgn": BASE_F + ["gtr", "psgn"],
        "G5_gtr_psgn_asmall": BASE_F + ["gtr", "psgn", "a_small"],
        "G6_gtr_psgn_fields": BASE_F + ["gtr", "psgn"] + FLD,
        "G7_all": BASE_F + ["gtr", "psgn", "a_small"] + FLD,
    },
    "int8": {
        "J0_M5": BASE_I,
        "J1_gtr": BASE_I + ["gtr"],
        "J2_psgn": BASE_I + ["psgn"],
        "J3_fields": BASE_I + ["a_sign", "a_mant", "b_sign", "b_mant"],
        "J4_gtr_psgn": BASE_I + ["gtr", "psgn"],
        "J5_all": BASE_I + ["gtr", "psgn", "a_small", "a_sign", "a_mant", "b_sign", "b_mant"],
    },
}


def tile_path_of(r):
    if r.get("tile_path"):
        return os.path.join(R.ROOT, r["tile_path"])
    return None


def all_rows():
    rows, missing, unc = R.assemble()
    # M5's rows carry no tile path: find it by sha256 among the tree's tiles
    by_sha = {}
    need = {r["tile_sha256"] for r in rows if not r.get("tile_path")}
    for lst in R.bins().values():
        for p in lst:
            h = R.sha(open(p, "rb").read())
            if h in need and h not in by_sha:
                by_sha[h] = p
    for r in rows:
        p = tile_path_of(r) or by_sha.get(r["tile_sha256"])
        if p is None:
            raise SystemExit(f"no tile for {r['exp']} {r['key']}")
        r["tile_path"] = os.path.relpath(p, R.ROOT)
        r["f"].update(flip_feats(p, r["type"]))
    return rows, missing, unc


# ------------------------------------------------------------------ nested leave-one-kind-out (M5's Family machinery)
def run_family(rows, famname, m5):
    fam = F.Family(rows, FORMS[famname])
    # M5 as frozen, no refit
    mf = m5["families"][famname]
    Xm = F.X_of(rows, mf["terms"])
    m5err = fam.y - Xm @ np.array(mf["coef_J"]) * np.where(fam.c1, mf["card1_scale"], 1.0)
    plain = {fn: fam.loko(fn) for fn in fam.forms}
    outer = np.full(len(fam.y), np.nan)
    picks = {}
    for k in range(len(fam.kinds)):
        score = {fn: F.rms(fam.loko(fn, (k,))) for fn in fam.forms}
        best = min(score, key=score.get)
        b, s = fam.fit(best, {k})
        m = fam.kid == k
        outer[m] = fam.y[m] - fam.pred(best, b, s, m)
        picks[best] = picks.get(best, 0) + 1
    sel = {fn: F.rms(e) for fn, e in plain.items()}
    best = min(sel, key=sel.get)
    b, s = fam.fit(best, set())
    C = fam.jackknife_cov(best)
    new = np.array([r["exp"] in R.NEW for r in rows])
    base = next(iter(fam.forms))
    tys = np.array([r["type"] for r in rows])

    def by(err):
        o = {"all": F.rms(err), **F.split_stats(fam, err)}
        o["new_experiments_only"] = {"n": int(new.sum()), "rms_w": F.rms(err[new])}
        for t in set(tys):
            o[f"{t}|new"] = {"n": int((new & (tys == t)).sum()), "rms_w": F.rms(err[new & (tys == t)])}
        return o

    pools = {}
    for t in sorted(set(tys)):
        for cd, cm in (("a3", ~fam.c1), ("c1", fam.c1)):
            e = outer[(tys == t) & cm]
            pools[f"{t}|{cd}"] = {"rms_w": F.rms(e), "n": int(np.sum(~np.isnan(e)))}
    res = {
        "n_rows": len(rows), "n_kinds": len(fam.kinds),
        "M5_frozen_no_refit": by(m5err),
        "M5_form_refit_plain_loko": by(plain[base]),
        "plain_loko_by_form": {fn: by(e) for fn, e in plain.items()},
        "nested_loko": {**by(outer), "inner_picks": picks},
        "chosen_form": best, "chosen_terms": FORMS[famname][best],
        "fit_on_all": {"coef_fJ": dict(zip(FORMS[famname][best], [float(x) * 1e15 for x in b])),
                       "coef_jackknife_se_fJ": dict(zip(FORMS[famname][best], [float(x) * 1e15 for x in np.sqrt(np.diag(C))])),
                       "card1_scale": s},
        "by_experiment": {e: {"n": int(sum(1 for r in rows if r["exp"] == e)),
                              "nested_rms_w": F.rms(np.array([outer[i] for i, r in enumerate(rows) if r["exp"] == e])),
                              "m5_frozen_rms_w": F.rms(np.array([m5err[i] for i, r in enumerate(rows) if r["exp"] == e]))}
                          for e in sorted({r["exp"] for r in rows})},
        "largest_nested_misses": sorted([{"exp": r["exp"], "key": r["key"], "D": r["D"], "err_w": float(outer[i]), "m5_err_w": float(m5err[i])}
                                         for i, r in enumerate(rows)], key=lambda x: -abs(x["err_w"]))[:15],
    }
    frozen = {"form": best, "terms": FORMS[famname][best], "coef_J": [float(x) for x in b], "coef_fJ": [float(x) * 1e15 for x in b],
              "cov_J2": C.tolist(), "card1_scale": s, "card1_scale_se": fam.scale_se(), "interval_pool_by_format_card": pools,
              "n_rows": len(rows), "n_kinds": len(fam.kinds)}
    return res, frozen, outer, m5err


# ------------------------------------------------------------------ heat
EXPDIR = {"E78": "2026-10-31-e78-kinds-energy-matrix", "E82": "2026-10-31-e82-kinds-aifoundry1", "E86": "2026-10-31-e86-real-tensors-energy",
          "E88": "2026-10-31-e88-result-path", "E90": "2026-10-31-e90-signs-spread", "E91": "2026-10-31-e91-real-tensors-aifoundry1",
          "E92": "2026-11-01-e92-sign-split", "E93": "2026-11-01-e93-zero-gate-silicon", "E94": "2026-11-01-e94-tile-spread",
          "E95": "2026-11-01-e95-real-tensors-energy", "E102": "2026-11-01-e102-balanced-bit-prices", "E103": "2026-11-01-e103-model-blind-test",
          "E104": "2026-11-01-e104-c-readback", "E106": "2026-11-01-e106-held-signs", "E108": "2026-11-01-e108-sign-located",
          "E115": "2026-11-01-e115-blind-pool", "E121": "2026-11-01-e121-zero-gate-replicate", "E122": "2026-11-01-e122-signs-replicate",
          "E123": "2026-11-01-e123-tile-spread-rest", "E127": "2026-11-02-e127-b-gate", "E128": "2026-11-02-e128-fp16-signs",
          "E131": "2026-11-02-e131-real-tiles-card1"}
# The heat path's time constants, quoted from committed results (not refitted here):
#  E73 (camera, ten frequencies): one pole of 15.98 s [13.34, 19.12] plus a 1.009 s delay, or poles of 15.57 s and 1.005 s.
#  E97 (aifoundry3, hold H1): 21% of the plateau by 10 s, 32% by 30 s, 45% by 60 s, 64% by 2 min, 90% by 5 min, ~98% by 10 min;
#      plateau about 0.9 C per board W. E111/E133 (aifoundry2): 0.65-0.70 C per board W over four holds, two sessions.
E97_STEP = [(10, 0.21), (30, 0.32), (60, 0.45), (120, 0.64), (300, 0.90), (600, 0.98)]
STEADY_C_PER_W = {"aifoundry3": {"value": 0.9, "source": "E97 holds (settled plateau, not a steady state by E97's test)"},
                  "aifoundry2": {"value": 0.675, "range": [0.65, 0.70], "source": "E111 + E133, four holds, two sessions"},
                  "aifoundry1-c1": {"value": None, "source": "no hold on this card"}}


def fit_step():
    """F(t) = 1 - sum w_i exp(-t/tau_i), tau = (1.005, 15.98, tau2, tau3): E73's two fast poles fixed, two slow fitted to E97's
    fractions (grid over tau2, tau3; nonnegative weights by lstsq then clipped). Returns taus, weights."""
    best = None
    ts = np.array([t for t, _ in E97_STEP], float)
    fr = np.array([f for _, f in E97_STEP], float)
    for t2 in np.geomspace(30, 400, 40):
        for t3 in np.geomspace(60, 1500, 40):
            if t3 <= t2 * 1.3:
                continue
            taus = np.array([1.005, 15.98, t2, t3])
            A = 1 - np.exp(-ts[:, None] / taus[None, :])
            A = np.vstack([A, np.ones(4) * 10])             # weights sum to 1 (soft, heavily weighted)
            y = np.concatenate([fr, [10.0]])
            w = np.linalg.lstsq(A, y, rcond=None)[0]
            if np.any(w < -1e-3):
                continue
            e = float(np.sqrt(np.mean((A[:-1] @ w - fr) ** 2)))
            if best is None or e < best[0]:
                best = (e, taus.tolist(), w.tolist())
    return {"rms_fraction": best[0], "tau_s": best[1], "weights": best[2]}


def heat_rows(power_rows):
    kind_of = {(r["exp"], r["key"]): r["kind"] for r in power_rows}
    out = []
    for e, d in EXPDIR.items():
        p = os.path.join(DD, d, f"{e.lower()}.json")
        its = json.load(open(p))["items"]
        card = json.load(open(p)).get("card", "")
        runs = list(csv.DictReader(open(os.path.join(DD, d, "runs.csv"))))
        runs.sort(key=lambda r: (r["pass"], float(r["t0_ms"] or 0)))
        dur, off = {}, {}
        starts = {}
        for r in runs:
            try:
                starts.setdefault(r["pass"], []).append(float(r["start_c"]))
            except (TypeError, ValueError):
                pass
        med = {p_: statistics.median(v) for p_, v in starts.items()}
        for a, b in zip(runs, runs[1:]):
            if a["pass"] == b["pass"]:
                try:
                    dur.setdefault(a["item"], []).append((float(b["prev_end_ms"]) - float(a["t0_ms"])) / 1000)
                except (TypeError, ValueError):
                    pass
        for r in runs:
            try:
                off.setdefault(r["item"], []).append(float(r["start_c"]) - med[r["pass"]])
            except (TypeError, ValueError, KeyError):
                pass
        for key, it in its.items():
            if not isinstance(it.get("dT_win"), dict) or it["dT_win"].get("mean") is None:
                continue
            if not isinstance(it.get("S"), dict) or it["S"].get("mean") is None:
                continue
            t = it.get("type") or key.split(".")[0]
            kind = kind_of.get((e, key)) or (key if key != "anchor_pi" else "fp32.anchor_pi")
            if dur.get(key) is None:
                continue
            if statistics.median(dur[key]) > HEAT_TRUN_MAX:
                continue
            out.append({"exp": e, "card": card, "key": key, "type": t, "kind": kind, "dT": float(it["dT_win"]["mean"]),
                        "S": float(it["S"]["mean"]), "D": (it.get("D") or {}).get("mean"), "T_run": float(statistics.median(dur[key])),
                        "off": float(statistics.mean(off.get(key, [0.0])))})
    return out


# Added after fit run 1's results were read (post hoc, README § Order): rows whose run is longer than the kinds harness's
# standard ~4.5 s are left out of the heat fit (E106 7.2 s, E128 11-14 s, E131 7.2 s: their launch reading is not comparable;
# E128 reads 0.0 C of rise at 11.8 W), and "before" is the lab's prior fixed rule, S x 0.118 C per board W (E97 § What this is).
HEAT_TRUN_MAX = 5.0
PRIOR_C_PER_W = 0.118
HFORMS = {
    "H0_one_constant": ["S"],
    "H1_per_card": ["S|card"],
    "H2_per_card_runlength": ["S|card", "ST|card"],
    "H3_per_card_runlength_launch": ["S|card", "ST|card", "off|card"],
    "H4_H3_int8": ["S|card", "ST|card", "off|card", "S_int8"],
}


def hX(rows, terms, cards):
    cols = []
    for q in terms:
        if q.endswith("|card"):
            base = q[:-5]
            for c in cards:
                cols.append([(hval(r, base) if r["card"] == c else 0.0) for r in rows])
        elif q == "S_int8":
            cols.append([r["S"] if r["type"] == "int8" else 0.0 for r in rows])
        else:
            cols.append([hval(r, q) for r in rows])
    return np.array(cols, float).T


def hval(r, q):
    return {"S": r["S"], "ST": r["S"] * (r["T_run"] - 4.5), "off": r["off"]}[q]


def heat_family(rows):
    cards = sorted({r["card"] for r in rows})
    y = np.array([r["dT"] for r in rows])
    kinds = sorted({r["kind"] for r in rows})
    kid = np.array([kinds.index(r["kind"]) for r in rows])
    X = {fn: hX(rows, t, cards) for fn, t in HFORMS.items()}

    def fit(fn, excl):
        m = ~np.isin(kid, list(excl))
        return np.linalg.lstsq(X[fn][m], y[m], rcond=None)[0]

    def loko(fn, outer=()):
        e = np.full(len(y), np.nan)
        for k in range(len(kinds)):
            if k in outer:
                continue
            b = fit(fn, set(outer) | {k})
            m = kid == k
            e[m] = y[m] - X[fn][m] @ b
        return e

    plain = {fn: loko(fn) for fn in HFORMS}
    outer = np.full(len(y), np.nan)
    picks = {}
    for k in range(len(kinds)):
        sc = {fn: F.rms(loko(fn, (k,))) for fn in HFORMS}
        best = min(sc, key=sc.get)
        b = fit(best, {k})
        m = kid == k
        outer[m] = y[m] - X[best][m] @ b
        picks[best] = picks.get(best, 0) + 1
    sel = {fn: F.rms(e) for fn, e in plain.items()}
    best = min(sel, key=sel.get)
    b = fit(best, set())
    tys = np.array([r["type"] for r in rows])
    cds = np.array([r["card"] for r in rows])

    def by(e):
        o = {"all": F.rms(e), "n": int(np.sum(~np.isnan(e)))}
        for t in ("fp32", "fp16", "int8"):
            o[t] = {"n": int(np.sum(tys == t)), "rms_c": F.rms(e[tys == t]), "bias_pred_minus_meas_c": -float(np.nanmean(e[tys == t]))}
        for c in cards:
            o[c] = {"n": int(np.sum(cds == c)), "rms_c": F.rms(e[cds == c])}
        return o

    names = []
    for q in HFORMS[best]:
        names += [f"{q[:-5]}|{c}" for c in cards] if q.endswith("|card") else [q]
    prior = y - PRIOR_C_PER_W * np.array([r["S"] for r in rows])
    return {"cards": cards, "n_rows": len(rows), "n_kinds": len(kinds),
            "before_prior_rule_0118": by(prior),
            "before_H0_one_constant_plain_loko": by(plain["H0_one_constant"]),
            "plain_loko_by_form": {fn: by(e) for fn, e in plain.items()},
            "nested_loko": {**by(outer), "inner_picks": picks},
            "chosen_form": best, "coef": dict(zip(names, [float(x) for x in b]))}, outer, prior


def main():
    rows, missing, unc = all_rows()
    if unc:
        print("uncounted tiles:", len(unc))
    m5 = json.load(open(os.path.join(DD, "2026-11-01-q133b-power-model", "m5.json")))
    res = {"_note": "Q137(m), fit_m6.py. Power: D in W over the type's zeros; heat: die rise over the window, C. Errors are measured - predicted.",
           "n_rows": len(rows), "experiments": sorted({r["exp"] for r in rows}), "missing": missing, "families": {}}
    frozen = {"_model": "M6 (Q137(m)): power = M5's bench terms plus per-flip terms, the form chosen by leave-one-kind-out, constants on all rows; heat = die rise per board W per card over the kinds window, with the time constants of E73/E97 and the steady coefficients of E97/E111/E133",
              "units": "power: W over the type's own zeros at 600 MHz on aifoundry3 card 0's footing (card 1 x card1_scale); heat: C over the run's launch reading, S = board W over idle",
              "families": {}}
    errs = {}
    for famname, want in (("float", lambda r: r["type"] != "int8"), ("int8", lambda r: r["type"] == "int8")):
        fr = [r for r in rows if want(r)]
        a, b, outer, m5e = run_family(fr, famname, m5)
        res["families"][famname] = a
        frozen["families"][famname] = b
        for i, r in enumerate(fr):
            errs[(r["exp"], r["key"])] = (float(outer[i]), float(m5e[i]))
    hr = heat_rows(rows)
    hres, hout, h0 = heat_family(hr)
    # end-to-end: the nested power error carried into heat at the chosen heat form's per-card S coefficient
    g = {k.split("|")[1]: v for k, v in hres["coef"].items() if k.startswith("S|")}
    e2e, e2e_before = [], []
    for i, r in enumerate(hr):
        pe = errs.get((r["exp"], r["key"]))
        if pe is None or math.isnan(hout[i]):
            continue
        gc = g.get(r["card"], 0.12)
        e2e.append((r["type"], hout[i] + gc * pe[0]))
        e2e_before.append((r["type"], h0[i] + gc * pe[1]))
    hres["end_to_end_note"] = "heat error when S is predicted: the nested heat error plus the card's S coefficient times the nested power error (rows with both)"
    hres["end_to_end"] = {t: {"n": sum(1 for q, _ in e2e if q == t), "rms_c": F.rms([e for q, e in e2e if q == t]),
                              "before_rms_c": F.rms([e for q, e in e2e_before if q == t])} for t in ("fp32", "fp16", "int8")}
    step = fit_step()
    res["heat"] = hres
    frozen["heat"] = {"form": hres["chosen_form"], "coef": hres["coef"], "terms": HFORMS[hres["chosen_form"]],
                      "window": "the kinds harness: a run of T_run s (4.5 s typical) from launch; ST = S x (T_run - 4.5); off = launch reading less the pass's median launch reading",
                      "step_response": step, "steady_c_per_board_w": STEADY_C_PER_W,
                      "interval_pool_c": {t: hres["nested_loko"][t]["rms_c"] for t in ("fp32", "fp16", "int8")}}
    json.dump(res, open(os.path.join(HERE, "loko-m6.json"), "w"), indent=1)
    json.dump(frozen, open(os.path.join(HERE, "m6.json"), "w"), indent=1, sort_keys=True)
    json.dump([{k: v for k, v in r.items() if k != "points"} for r in rows], open(os.path.join(HERE, "rows-m6.json"), "w"), indent=0)
    json.dump(hr, open(os.path.join(HERE, "heat-rows.json"), "w"), indent=0)
    for fam, v in res["families"].items():
        print(f"== {fam}: {v['n_rows']} rows {v['n_kinds']} kinds")
        for lab in ("M5_frozen_no_refit", "M5_form_refit_plain_loko", "nested_loko"):
            x = v[lab]
            print(f"  {lab:28s} all {x['all']:.3f} " + " ".join(f"{t} {x[t]['rms_w']:.3f}" for t in ("fp32", "fp16", "int8") if t in x)
                  + f" | new-exp {x['new_experiments_only']['rms_w']:.3f} (n {x['new_experiments_only']['n']})")
        for fn, x in v["plain_loko_by_form"].items():
            print(f"    plain {fn:22s} {x['all']:.3f}")
        print("  picks", v["nested_loko"]["inner_picks"], "chosen", v["chosen_form"], {k: round(c, 3) for k, c in v["fit_on_all"]["coef_fJ"].items()})
    h = res["heat"]
    print("== heat", h["n_rows"], "rows", h["n_kinds"], "kinds; before (S x 0.118)", {t: round(h["before_prior_rule_0118"][t]["rms_c"], 3) for t in ("fp32", "fp16", "int8")}, "H0", {t: round(h["before_H0_one_constant_plain_loko"][t]["rms_c"], 3) for t in ("fp32", "fp16", "int8")},
          "nested", {t: round(h["nested_loko"][t]["rms_c"], 3) for t in ("fp32", "fp16", "int8")}, h["nested_loko"]["inner_picks"], h["chosen_form"], h["coef"])
    print("   end to end", h["end_to_end"])
    print("   step", step)
    print("missing", len(missing))


if __name__ == "__main__":
    main()
