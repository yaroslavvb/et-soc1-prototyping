#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q133(b): M4 refitted and extended on every float and int8 tile the bench has counted and a card has measured, the
forms compared by NESTED leave-one-kind-out, the chosen form frozen as M5.

    python3 fit_m5.py            # from anywhere in the tree; writes loko.json, m5.json and rows.json beside it

Rows: every tile with bench counts (rtl-sim/fma_toggle_v2, Q132(b)) and a measured D (W over the type's zeros) - E78, E86,
E90, E92 and E95 on aifoundry3 card 0; E82, E88, E91, E93, E94, E103, E104 and E106 on aifoundry1 card 1 - plus the counts
this lane ran for E93's, E104's and E106's tiles that no counts file had (counts-q133b-train.json). Card 1's rows are put on
card 0's footing by one model-free scale: E82's kinds against E78's same tiles, sum(D82 D78) / sum(D78^2), per family.

Kinds: a held-out "kind" is every row of one tile rule, on both cards and in every experiment (byte-identical tiles share
a kind; E90's and E94's re-draws join their rule). Nested: for each held-out kind, every form is scored by leave-one-kind-out
on the remaining kinds, the best is refitted on them and predicts the held-out kind; the outer errors score the whole
procedure. The same inner step on all the rows chooses the frozen form.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import re
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(ROOT, "docs", "reports", "data")
B = os.path.join(DD, "2026-11-01-q132-rtl-bench")
K = os.path.join(ROOT, "tools", "claims-v3", "kinds")
sys.path.insert(0, K)
import make_kinds as mk  # noqa: E402

CPO = {"fp32": 546, "fp16": 546, "int8": 318}
RATE = {t: 600e6 / c * 1024 * 0.9963 for t, c in CPO.items()}
ANCHOR_NAMES = {"zeros", "anchor_pi"}
load = lambda p: json.load(open(p))
sha = lambda b: hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------ features
def gate_transitions(raw, t):
    """Gate decisions that change between consecutive micro-ops of one accumulate op (cyclic), summed over the eight gate
    bits: how often a lane's clock-gate state flips. make_kinds' stream and gate rule (kinds README section 1)."""
    aw, bw = mk.words_of(raw)
    a_seq, b_seq = mk.issue_streams_fast(aw, bw, t)
    g = mk.gate_mask(a_seq, b_seq, t)
    return int(np.sum(g != np.roll(g, -1, axis=0)))


def tile_feats(path, t):
    raw = open(path, "rb").read()
    aw, bw = mk.words_of(raw)
    a_seq, b_seq = mk.issue_streams_fast(aw, bw, t)
    da = mk.popcount32((a_seq ^ np.roll(a_seq, -1)).astype(np.uint32)).sum() * mk.COLUMN_SLOTS[t]
    db = mk.popcount32((b_seq ^ np.roll(b_seq, -1, axis=0)).astype(np.uint32)).sum()
    return {"abits": float(da), "bbits": float(db), "gtr": float(gate_transitions(raw, t)), "sha256": sha(raw)}


def bench_feats(m, z):
    """Per op on one minion, the tile's counts less the type's zeros (counts-v2), by stage of the whole VPU (nets_map)."""
    s, q = m["vpu"]["by_stage"], z["vpu"]["by_stage"]
    d = {k: s[k] - q[k] for k in s}
    f = {
        "mult": d["multiplier"], "add": d["adder_norm"], "core": d["multiplier"] + d["adder_norm"],
        "bus": d["lane_operand_bus"],
        "expop": d["exponent"] + d["operand"], "ctrl": d["control"] + d["vpu_sequencer"] + d["other"],
        "res": d["result"] + d["c_regfile"],
        "clk": m["ff"]["all"]["clocked"] - z["ff"]["all"]["clocked"],
        "fft": m["ff"]["all"]["toggles"] - z["ff"]["all"]["toggles"],
    }
    f["rest"] = (m["vpu"]["nets_map"] - z["vpu"]["nets_map"]) - f["core"] - f["bus"]
    f["nets_nobus"] = (m["vpu"]["nets_map"] - z["vpu"]["nets_map"]) - f["bus"]
    return f


def fmt_feats(f, t):
    """The adder and the core priced apart per float format: fp16's two-term path drives the same unit differently (E92,
    E104, E106: its alternation reads lower than fp32's, per toggle)."""
    f["add32"] = f["add"] if t == "fp32" else 0.0
    f["add16"] = f["add"] if t == "fp16" else 0.0
    f["core32"] = f["core"] if t == "fp32" else 0.0
    f["core16"] = f["core"] if t == "fp16" else 0.0
    return f


# The forms compared. M4 is F0 (floats) and I0 (int8, its I3). Every other form adds what the brief named: the adder
# priced apart from the multiplier (signs: E88, E92, E104, E106), register bits that change, the gate's switching (gated
# lanes: E93, E94), and the A side's bus bits (the A side with a busy partner: E103-R8).
FORMS = {
    "float": {
        "F0_M4": ["core", "bus", "rest", "clk"],
        "F1_split": ["mult", "add", "bus", "rest", "clk"],
        "F2_stages": ["mult", "add", "bus", "expop", "ctrl", "res", "clk"],
        "F3_split_fft": ["mult", "add", "bus", "rest", "clk", "fft"],
        "F4_M4_abits": ["core", "bus", "rest", "clk", "abits"],
        "F5_split_abits": ["mult", "add", "bus", "rest", "clk", "abits"],
        "F6_split_abits_gtr": ["mult", "add", "bus", "rest", "clk", "abits", "gtr"],
        "F7_M4_gtr": ["core", "bus", "rest", "clk", "gtr"],
        "F8_stages_abits_gtr": ["mult", "add", "bus", "expop", "ctrl", "res", "clk", "abits", "gtr"],
        "F9_stages_gtr": ["mult", "add", "bus", "expop", "ctrl", "res", "clk", "gtr"],
        "F10_add_by_format": ["mult", "add32", "add16", "bus", "rest", "clk"],
        "F11_core_by_format": ["core32", "core16", "bus", "rest", "clk"],
        "F12_core_by_format_gtr": ["core32", "core16", "bus", "rest", "clk", "gtr"],
    },
    "int8": {
        "I0_I3": ["nets_nobus", "bus", "clk"],
        "I1_fft": ["nets_nobus", "bus", "clk", "fft"],
        "I2_abits": ["nets_nobus", "bus", "clk", "abits"],
        "I3_gtr": ["nets_nobus", "bus", "clk", "gtr"],
        "I4_abits_bbits": ["nets_nobus", "bus", "clk", "abits", "bbits"],
    },
}


# ------------------------------------------------------------------ rows
def kinds_tile(t, n):
    return os.path.join(K, "tiles", t, f"{n}.bin")


def assemble():
    zc = load(f"{B}/counts-v2.json")["rows"]
    zeros = {t: zc[f"{t}.zeros"]["mean"] for t in CPO}
    tp = os.path.join(HERE, "counts-q133b-train.json")
    train = load(tp)["rows"] if os.path.exists(tp) else {}
    c86 = load(f"{B}/counts-e86.json")["rows"]
    c88 = load(f"{B}/counts-e88.json")["rows"]
    c90 = load(f"{B}/counts-e90.json")["rows"]
    c92 = load(f"{B}/counts-e92.json")["rows"]
    c9495 = load(f"{B}/counts-e94e95.json")["rows"]
    cpool = load(f"{B}/counts-e103-pool.json")["rows"]
    items = {e: load(os.path.join(DD, p))["items"] for e, p in {
        "E78": "2026-10-31-e78-kinds-energy-matrix/e78.json", "E82": "2026-10-31-e82-kinds-aifoundry1/e82.json",
        "E86": "2026-10-31-e86-real-tensors-energy/e86.json", "E91": "2026-10-31-e91-real-tensors-aifoundry1/e91.json",
        "E88": "2026-10-31-e88-result-path/e88.json", "E90": "2026-10-31-e90-signs-spread/e90.json",
        "E92": "2026-11-01-e92-sign-split/e92.json", "E94": "2026-11-01-e94-tile-spread/e94.json",
        "E95": "2026-11-01-e95-real-tensors-energy/e95.json", "E103": "2026-11-01-e103-model-blind-test/e103.json",
        "E93": "2026-11-01-e93-zero-gate-silicon/e93.json", "E104": "2026-11-01-e104-c-readback/e104.json",
        "E106": "2026-11-01-e106-held-signs/e106.json"}.items()}
    # every counted tile, by the sha256 of its bytes -> (counts row, tile path, label)
    by_sha = {}

    def reg(row, path, label):
        h = sha(open(path, "rb").read())
        by_sha.setdefault(h, (row, path, label))
        return h

    for k, v in zc.items():
        reg(v, kinds_tile(v["type"], v["kind"]), f"{v['type']}.{v['kind']}")
    for k, v in c92.items():
        reg(v, os.path.join(K, "e92", "tiles", v["type"], v["kind"] + ".bin"), f"{v['type']}.s:{v['kind']}")
    for k, v in c90.items():
        base = re.sub(r"_d\d+$", "", v["kind"])
        lab = f"{v['type']}.{base}" if os.path.exists(kinds_tile(v["type"], base)) else f"{v['type']}.s:{base}"
        reg(v, os.path.join(K, "e90", "tiles", v["type"], v["kind"] + ".bin"), lab)
    for k, v in c88.items():
        reg(v, os.path.join(ROOT, "tools", "claims-v3", "rpath", "tiles", v["type"], v["kind"] + ".bin"), f"{v['type']}.e88:{v['kind']}")
    for k, v in c86.items():
        reg(v, os.path.join(K, "real", "tiles", v["type"], v["kind"] + ".bin"), f"{v['type']}.real:{v['kind']}")
    for k, v in c9495.items():
        t, n = v["type"], v["kind"]
        if n.startswith("r2_"):
            reg(v, os.path.join(K, "real2", "tiles", t, n[3:] + ".bin"), f"{t}.real2:{n[3:]}")
        elif n.startswith("real_"):
            reg(v, os.path.join(K, "real", "tiles", t, n[5:] + ".bin"), f"{t}.real:{n[5:]}")
        else:
            base = re.sub(r"_e9[04]d\d+$", "", n)
            reg(v, os.path.join(K, "e94", "tiles", t, n + ".bin"), f"{t}.{base}")
    e103_names = set(load(os.path.join(K, "e103", "e103.json"))["tiles"].keys())
    for k, v in cpool.items():
        if k in e103_names:
            reg(v, os.path.join(K, "e103", "tiles", v["type"], v["kind"] + ".bin"), f"{v['type']}.e103:{v['kind']}")
    for k, v in train.items():
        t, n = v["type"], v["kind"]
        pre, base = n.split("_", 1)
        reg(v, os.path.join(K, pre, "tiles", t, base + ".bin"), f"{t}.{pre}:{base}")

    def tile_of(e, t, n):
        """The tile file an experiment's item ran, by the experiment's own layout."""
        cand = {
            "E78": [kinds_tile(t, n)], "E82": [kinds_tile(t, n)],
            "E86": [os.path.join(K, "real", "tiles", t, n.replace("real_", "", 1) + ".bin"), kinds_tile(t, n)],
            "E91": [os.path.join(K, "real", "tiles", t, n.replace("real_", "", 1) + ".bin"), kinds_tile(t, n)],
            "E88": [os.path.join(ROOT, "tools", "claims-v3", "rpath", "tiles", t, n + ".bin")],
            "E90": [os.path.join(K, "e90", "tiles", t, n + ".bin"), kinds_tile(t, n)],
            "E92": [os.path.join(K, "e92", "tiles", t, n + ".bin"), kinds_tile(t, n)],
            "E94": [os.path.join(K, "e94", "tiles", t, n + ".bin"), kinds_tile(t, n)],
            "E95": [os.path.join(K, "real2", "tiles", t, n.replace("r2_", "", 1) + ".bin"),
                    os.path.join(K, "real", "tiles", t, n.replace("real_", "", 1) + ".bin")],
            "E103": [os.path.join(K, "e103", "tiles", t, n + ".bin")],
            "E93": [os.path.join(K, "e93", "tiles", t, n + ".bin"), kinds_tile(t, n)],
            "E104": [os.path.join(K, "e104", "tiles", t, n + ".bin"), kinds_tile(t, n)],
            "E106": [os.path.join(K, "e106", "tiles", t, n + ".bin"), kinds_tile(t, n)],
        }[e]
        for p in cand:
            if os.path.exists(p):
                return p
        return None

    card = {"E78": "a3", "E86": "a3", "E90": "a3", "E92": "a3", "E95": "a3"}
    rows, missing = [], []
    for e, its in items.items():
        for key, it in its.items():
            if key == "anchor_pi" or not isinstance(it.get("D"), dict) or it["D"].get("mean") is None:
                continue
            t, n = key.split(".", 1)
            if n in ANCHOR_NAMES:
                continue
            # anchors of later sessions are E78's kinds again: keep them only in E78 and E82, where they are the matrix
            if e not in ("E78", "E82") and n in ("randn", "full"):
                continue
            p = tile_of(e, t, n)
            if p is None:
                missing.append(f"{e}:{key} (no tile)")
                continue
            h = sha(open(p, "rb").read())
            if h not in by_sha:
                missing.append(f"{e}:{key} (no counts)")
                continue
            crow, _, lab = by_sha[h]
            rate = it["rate"]["mean"] if isinstance(it.get("rate"), dict) and it["rate"].get("mean") else RATE[t]
            f = fmt_feats(bench_feats(crow["mean"], zeros[t]), t)
            f.update({k: v for k, v in tile_feats(p, t).items() if k != "sha256"})
            pts = [fmt_feats(bench_feats(q, zeros[t]), t) for q in crow["points"]]
            rows.append({"exp": e, "card": card.get(e, "c1"), "key": key, "type": t, "kind": lab, "tile_sha256": h,
                         "D": float(it["D"]["mean"]), "D_se": it["D"].get("se"), "rate": float(rate), "f": f, "points": pts,
                         "check_mismatch": crow["mean"].get("check_mismatch")})
    return rows, missing


# ------------------------------------------------------------------ fitting
def X_of(rows, terms):
    return np.array([[r["rate"] * r["f"][q] for q in terms] for r in rows], float)


class Family:
    """One family's rows as arrays: y, the card-1 flag, kind ids, and every form's X, built once."""

    def __init__(self, rows, forms):
        self.rows = rows
        self.forms = forms
        self.y = np.array([r["D"] for r in rows], float)
        self.c1 = np.array([r["card"] == "c1" for r in rows])
        self.kinds = sorted({r["kind"] for r in rows})
        ki = {k: i for i, k in enumerate(self.kinds)}
        self.kid = np.array([ki[r["kind"]] for r in rows])
        self.X = {fn: X_of(rows, terms) for fn, terms in forms.items()}
        self.sc = {fn: np.where(np.abs(X).max(axis=0) == 0, 1.0, np.abs(X).max(axis=0)) for fn, X in self.X.items()}
        # card 1's scale, model-free: E82's kinds against E78's same tiles (D78 > 0.5 W)
        a = {r["kind"]: r["D"] for r in rows if r["exp"] == "E78"}
        b = {r["kind"]: r["D"] for r in rows if r["exp"] == "E82"}
        self.pairs = {ki[k]: (a[k], b[k]) for k in a if k in b and a[k] > 0.5}
        self.num = sum(x * y for x, y in self.pairs.values())
        self.den = sum(x * x for x, y in self.pairs.values())

    def scale(self, excl):
        num, den, n = self.num, self.den, len(self.pairs)
        for k in excl:
            if k in self.pairs:
                x, y = self.pairs[k]
                num -= x * y
                den -= x * x
                n -= 1
        return num / den if n >= 3 else 1.0

    def fit(self, fn, excl):
        """Fit form fn on every row whose kind is not in excl (a set of kind ids)."""
        m = ~np.isin(self.kid, list(excl)) if excl else np.ones(len(self.y), bool)
        s = self.scale(excl)
        X = self.X[fn][m] / self.sc[fn]
        y = self.y[m] / np.where(self.c1[m], s, 1.0)
        b = np.linalg.lstsq(X, y, rcond=None)[0] / self.sc[fn]
        return b, s

    def pred(self, fn, b, s, mask):
        return self.X[fn][mask] @ b * np.where(self.c1[mask], s, 1.0)

    def loko(self, fn, outer_excl=()):
        """Leave-one-kind-out errors (D - prediction) for every row outside outer_excl, as an array with NaN elsewhere."""
        err = np.full(len(self.y), np.nan)
        for k in range(len(self.kinds)):
            if k in outer_excl:
                continue
            b, s = self.fit(fn, set(outer_excl) | {k})
            m = self.kid == k
            err[m] = self.y[m] - self.pred(fn, b, s, m)
        return err

    def scale_se(self):
        ks = list(self.pairs)
        js = [self.scale({k}) for k in ks]
        mj = sum(js) / len(js)
        return math.sqrt(sum((x - mj) ** 2 for x in js) * (len(js) - 1) / len(js))

    def jackknife_cov(self, fn):
        bs = np.array([self.fit(fn, {k})[0] for k in range(len(self.kinds))])
        d = bs - bs.mean(axis=0)
        return d.T @ d * (len(self.kinds) - 1) / len(self.kinds)


def rms(v):
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    return float(np.sqrt(np.mean(v ** 2))) if len(v) else None


def split_stats(fam, err):
    out = {}
    tys = np.array([r["type"] for r in fam.rows])
    for lab, m in (("fp32", tys == "fp32"), ("fp16", tys == "fp16"), ("int8", tys == "int8"), ("card a3", ~fam.c1), ("card c1", fam.c1)):
        e = err[m]
        e = e[~np.isnan(e)]
        if len(e):
            out[lab] = {"n": int(len(e)), "rms_w": rms(e), "bias_pred_minus_meas_w": -float(np.mean(e))}
    return out


def t975(nu):
    z = statistics.NormalDist().inv_cdf(0.975)
    return z + (z ** 3 + z) / (4 * nu) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * nu ** 2)


def m4_frozen():
    m4 = load(os.path.join(K, "predictions-e103.json"))["models"]
    bF = np.array([m4["float"]["coef_fJ"][q] for q in ("k_core", "k_bus", "k_rest", "a_clocked")]) * 1e-15
    bI = np.array([m4["int8"]["coef_fJ"][q] for q in ("k_nets", "k_bus", "a_clocked")]) * 1e-15
    return {"float": (bF, m4["float"]["card1_scale"], FORMS["float"]["F0_M4"]), "int8": (bI, m4["int8"]["card1_scale"], FORMS["int8"]["I0_I3"])}


def main():
    rows, missing = assemble()
    M4 = m4_frozen()
    res = {"_note": "Q133(b), fit_m5.py. D in W over the type's zeros; errors are D - prediction; bias is prediction - D.",
           "n_rows": len(rows), "missing": missing, "experiments": sorted({r["exp"] for r in rows}), "families": {}}
    frozen = {"_model": "M5 (Q133(b)): for each family, the form chosen by leave-one-kind-out over every counted, measured tile, its constants fitted on all of them",
              "units": "D, W over the type's own zeros at 600 MHz on aifoundry3 card 0's footing; on aifoundry1 card 1 multiply by card1_scale",
              "features": "rate (ops/s, chip-wide) x per-op counts of rtl-sim/fma_toggle_v2 (vpu_top, nets_map stages, clocked bits) less the type's zeros (counts-v2.json); abits/bbits/gtr from the tile bytes (make_kinds stream)",
              "families": {}}
    for famname, want in (("float", lambda r: r["type"] != "int8"), ("int8", lambda r: r["type"] == "int8")):
        fr = [r for r in rows if want(r)]
        fam = Family(fr, FORMS[famname])
        bb, ss, tt = M4[famname]
        m4p = X_of(fr, tt) @ bb * np.where(fam.c1, ss, 1.0)
        m4err = fam.y - m4p
        plain = {fn: fam.loko(fn) for fn in fam.forms}
        outer = np.full(len(fam.y), np.nan)
        picks = {}
        for k in range(len(fam.kinds)):
            score = {}
            for fn in fam.forms:
                e = fam.loko(fn, (k,))
                score[fn] = rms(e)
            best = min(score, key=score.get)
            b, s = fam.fit(best, {k})
            m = fam.kid == k
            outer[m] = fam.y[m] - fam.pred(best, b, s, m)
            picks[fam.kinds[k]] = best
        sel = {fn: rms(e) for fn, e in plain.items()}
        best = min(sel, key=sel.get)
        b, s = fam.fit(best, set())
        C = fam.jackknife_cov(best)
        fit_err = fam.y - fam.pred(best, b, s, np.ones(len(fam.y), bool))
        pick_counts = {}
        for v in picks.values():
            pick_counts[v] = pick_counts.get(v, 0) + 1
        res["families"][famname] = {
            "n_rows": len(fr), "n_kinds": len(fam.kinds),
            "M4_frozen_no_refit": {"all": rms(m4err), **split_stats(fam, m4err)},
            "plain_loko_by_form": {fn: {"all": rms(e), **split_stats(fam, e)} for fn, e in plain.items()},
            "coef_fJ_fit_on_all_by_form": {fn: dict(zip(FORMS[famname][fn], [float(x) * 1e15 for x in fam.fit(fn, set())[0]])) for fn in fam.forms},
            "nested_loko": {"all": rms(outer), **split_stats(fam, outer), "inner_picks": pick_counts},
            "chosen_form": best, "chosen_terms": FORMS[famname][best],
            "fit_on_all": {"coef_fJ": [float(x) * 1e15 for x in b], "coef_jackknife_se_fJ": [float(x) * 1e15 for x in np.sqrt(np.diag(C))],
                           "card1_scale": s, "rms_w": rms(fit_err), **split_stats(fam, fit_err)},
            "row_errors": [{"exp": r["exp"], "key": r["key"], "kind": r["kind"], "D": r["D"], "nested_err_w": float(outer[i]), "m4_frozen_err_w": float(m4err[i]),
                            "m4_form_loko_err_w": float(plain[next(iter(fam.forms))][i]), "chosen_form_loko_err_w": float(plain[best][i])} for i, r in enumerate(fr)],
            "by_experiment": {e: {"n": int(sum(1 for r in fr if r["exp"] == e)),
                                  "nested_rms_w": rms(np.array([outer[i] for i, r in enumerate(fr) if r["exp"] == e])),
                                  "m4_frozen_rms_w": rms(np.array([m4err[i] for i, r in enumerate(fr) if r["exp"] == e])),
                                  "m4_form_loko_rms_w": rms(np.array([plain[next(iter(fam.forms))][i] for i, r in enumerate(fr) if r["exp"] == e]))}
                              for e in sorted({r["exp"] for r in fr})},
            "largest_nested_misses": sorted([{"exp": r["exp"], "key": r["key"], "kind": r["kind"], "D": r["D"], "err_w": float(outer[i]), "m4_err_w": float(m4err[i])}
                                             for i, r in enumerate(fr)], key=lambda x: -abs(x["err_w"]))[:15],
        }
        pools = {}
        tys = np.array([r["type"] for r in fr])
        for t in (("fp32", "fp16") if famname == "float" else ("int8",)):
            e = outer[tys == t]
            pools[t] = {"rms_w": rms(e), "n": int(np.sum(~np.isnan(e)))}
        pools_fc = {}
        for t in (("fp32", "fp16") if famname == "float" else ("int8",)):
            for cd, cm in (("a3", ~fam.c1), ("c1", fam.c1)):
                e = outer[(tys == t) & cm]
                pools_fc[f"{t}|{cd}"] = {"rms_w": rms(e), "n": int(np.sum(~np.isnan(e)))}
        frozen["families"][famname] = {"interval_pool_by_format_card": pools_fc, "card1_scale_se": fam.scale_se(), "form": best, "terms": FORMS[famname][best], "coef_J": [float(x) for x in b], "coef_fJ": [float(x) * 1e15 for x in b],
                                       "cov_J2": C.tolist(), "card1_scale": s, "interval_pool_nested_loko": pools, "n_rows": len(fr), "n_kinds": len(fam.kinds)}
    json.dump(res, open(os.path.join(HERE, "loko.json"), "w"), indent=1)
    json.dump(frozen, open(os.path.join(HERE, "m5.json"), "w"), indent=1, sort_keys=True)
    with open(os.path.join(HERE, "rows.json"), "w") as f:
        json.dump([{k: v for k, v in r.items() if k != "points"} for r in rows], f, indent=0)
    for famname, v in res["families"].items():
        print(f"== {famname}: {v['n_rows']} rows, {v['n_kinds']} kinds; M4 frozen, no refit: {v['M4_frozen_no_refit']['all']:.3f} W  " + "  ".join(f"{k} {y['rms_w']:.3f}" for k, y in v["M4_frozen_no_refit"].items() if k != "all"))
        for fn, x in v["plain_loko_by_form"].items():
            print(f"   plain LOKO {fn:22s} {x['all']:.3f}  " + "  ".join(f"{k} {y['rms_w']:.3f}" for k, y in x.items() if k != "all"))
        print(f"   NESTED LOKO {v['nested_loko']['all']:.3f}  picks {v['nested_loko']['inner_picks']}  " + "  ".join(f"{k} {y['rms_w']:.3f}" for k, y in v["nested_loko"].items() if k not in ("all", "inner_picks")))
        print("   by experiment (nested / M4 form LOKO / M4 frozen): " + "; ".join(f"{e} n{x['n']} {x['nested_rms_w']:.3f}/{x['m4_form_loko_rms_w']:.3f}/{x['m4_frozen_rms_w']:.3f}" for e, x in v["by_experiment"].items()))
        print(f"   chosen {v['chosen_form']}: " + ", ".join(f"{q} {c:.3f}+-{e:.3f}" for q, c, e in zip(v['chosen_terms'], v['fit_on_all']['coef_fJ'], v['fit_on_all']['coef_jackknife_se_fJ'])) + f" fJ; scale {v['fit_on_all']['card1_scale']:.4f}; fit rms {v['fit_on_all']['rms_w']:.3f}")
    print("missing:", missing)


if __name__ == "__main__":
    main()
