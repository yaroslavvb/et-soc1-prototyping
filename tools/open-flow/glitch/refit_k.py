#!/usr/bin/env python3
"""Q138(g): Q133(a)'s int8 model M2 refitted with glitch-aware counts, and the single bits priced at the refitted k.

    refit_k.py --sims <dir> --glitch <analyze_glitch.py output json> --out <json>

M2 (Q133(a) result 4): D = rate x (k x VPU nets toggled + a x register bits clocked), each over int8's zeros, on E78's 15 int8
kinds (aifoundry3, 600 MHz, board watts). Zero-delay: Q133(a)'s VPU nets_hier at the middle launch point (its committed
runs/<arm>/counts_kinds.json). Glitch-aware: the same plus the unit's excess (timed - zero-delay toggles of the 16 tima_top
instances, kind minus zeros) from this lane's event simulation of the same stimulus. Clocked bits are the RTL run's (Q132(b)),
as in Q133(a). Leave-one-kind-out rms is the out-of-sample error.
"""
import argparse, json, os
import numpy as np
LAB = os.environ.get("LAB") or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
DD = f"{LAB}/docs/reports/data"
Q133 = f"{DD}/2026-11-01-q133a-int8-gate-level"
Q132 = f"{DD}/2026-11-01-q132-rtl-bench"
MID = 471698
KINDS = ["full", "gauss_q", "sorted", "pos", "smallint", "sparse50", "ternary", "highbit", "wsparse50", "neg_ones", "ones",
         "sparse90", "wsparse90", "a_full_b_zeros", "a_zeros_b_full"]
ARMS = ["booth_tree", "booth", "booth_swap", "plain"]


def at(row, n0):
    for p in row["points"]:
        if p["n0"] == n0:
            return p


def stats(y, p):
    y, p = np.array(y), np.array(p)
    return {"rms_w": float(np.sqrt(((y - p) ** 2).mean())), "bias_w": float((p - y).mean()), "worst_w": float(np.abs(y - p).max()),
            "pearson_r": float(np.corrcoef(y, p)[0, 1])}


def fit(rows, cols):
    X = np.array([[r[c] * r["rate"] for c in cols] for r in rows], float)
    y = np.array([r["D"] for r in rows], float)
    sc = np.where(X.max(axis=0) > 0, X.max(axis=0), 1.0)
    b, *_ = np.linalg.lstsq(X / sc, y, rcond=None)
    return b / sc


def report(rows, cols):
    b = fit(rows, cols)
    X = np.array([[r[c] * r["rate"] for c in cols] for r in rows], float)
    res = stats([r["D"] for r in rows], X @ b)
    res["coef_fJ"] = {c: float(x) * 1e15 for c, x in zip(cols, b)}
    loo, bs = [], []
    for i in range(len(rows)):
        bi = fit(rows[:i] + rows[i + 1:], cols)
        bs.append(bi)
        loo.append(float(np.array([rows[i][c] * rows[i]["rate"] for c in cols]) @ bi))
    res["loo"] = stats([r["D"] for r in rows], loo)
    bs, n = np.array(bs), len(rows)
    res["coef_jackknife_se_fJ"] = {c: float(np.sqrt((n - 1) / n * ((bs[:, j] - bs[:, j].mean()) ** 2).sum())) * 1e15 for j, c in enumerate(cols)}
    res["resid_w"] = {r["kind"]: float(r["D"] - q) for r, q in zip(rows, X @ b)}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sims", required=True)
    ap.add_argument("--glitch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    e78 = json.load(open(f"{DD}/2026-10-31-e78-kinds-energy-matrix/e78.json"))["items"]
    v2 = json.load(open(f"{Q132}/counts-v2.json"))["rows"]
    gl = json.load(open(a.glitch))
    out = {"_what": "M2 on E78's 15 int8 kinds, zero-delay against glitch-aware counts, middle launch point", "arms": {}}
    for arm in ARMS:
        ck = json.load(open(f"{Q133}/runs/{arm}/counts_kinds.json"))["rows"]
        packed = json.load(open(a.sims)) if a.sims.endswith(".json") else None     # a committed sims/<run>.json
        def sim(kind):
            key = f"{arm}__kind_{kind}__{MID}"
            if packed is not None:
                return packed.get(key)
            f = os.path.join(a.sims, key + ".json")
            return json.load(open(f)) if os.path.exists(f) else None
        sz = sim("zeros")
        if sz is None:
            continue
        rows_z, rows_g, missing = [], [], []
        for k in KINDS:
            s = sim(k)
            if s is None:
                missing.append(k)
                continue
            g, gz = at(ck["int8." + k], MID), at(ck["int8.zeros"], MID)
            ref, zr = v2["int8." + k], v2["int8.zeros"]
            dn = g["vpu"]["nets_hier"] - gz["vpu"]["nets_hier"]
            ex = (s["total"]["timed"] - s["total"]["zero"]) - (sz["total"]["timed"] - sz["total"]["zero"])
            dz_unit_mine = s["total"]["zero"] - sz["total"]["zero"]
            dclk = ref["mean"]["ff"]["all"]["clocked"] - zr["mean"]["ff"]["all"]["clocked"]
            base = {"kind": k, "D": e78["int8." + k]["D"]["mean"], "rate": e78["int8." + k]["rate"]["mean"], "dclk": dclk}
            rows_z.append({**base, "dnets": dn})
            rows_g.append({**base, "dnets": dn + ex, "dnets_zero": dn, "excess_unit": ex, "unit_zero_mine": dz_unit_mine,
                           "unit_timed_over_zero": (s["total"]["timed"] - sz["total"]["timed"]) / dz_unit_mine if dz_unit_mine else None})
        if missing or len(rows_z) < 5:
            out["arms"][arm] = {"missing": missing}
            continue
        rz = report(rows_z, ["dnets", "dclk"])
        rg = report(rows_g, ["dnets", "dclk"])
        # the glitches as their own term: D = rate x (k x zero-delay nets + k_g x the unit's excess + a x clocked bits);
        # k_g / k is the glitch weight the card's watts ask for
        r3 = report(rows_g, ["dnets_zero", "excess_unit", "dclk"])
        r3["glitch_weight_k_g_over_k"] = r3["coef_fJ"]["excess_unit"] / r3["coef_fJ"]["dnets_zero"]
        kz, kg = rz["coef_fJ"]["dnets"], rg["coef_fJ"]["dnets"]
        res = {"zero_delay": rz, "glitch_aware": rg, "glitch_term": r3, "kinds": {r["kind"]: {"excess_unit_per_op": r["excess_unit"],
               "unit_timed_over_zero": r["unit_timed_over_zero"], "dnets_zero": rz_r["dnets"], "dnets_glitch": r["dnets"]}
               for r, rz_r in zip(rows_g, rows_z)}}
        # the single bits at each fit's k (shapes do not move; levels do)
        ga = gl["arms"].get(arm)
        if ga and "glitch_fJ" in ga:
            k0 = ga["k_fJ"]
            sc = kg / k0
            res["single_bits_at_refit_k"] = {"k_refit_fJ": kg, "k_frozen_fJ": k0, "scale": sc,
                                             "B_list_fJ": [x * sc for x in ga["glitch_fJ"]["B_list"]],
                                             "A_list_fJ": [x * sc for x in ga["glitch_fJ"]["A_list"]],
                                             "B_odd_minus_even_fJ": ga["glitch_fJ"]["B_odd_minus_even"] * sc,
                                             "A_odd_minus_even_fJ": ga["glitch_fJ"]["A_odd_minus_even"] * sc,
                                             "A_sign_dense_minus_one_fJ": ga["glitch_fJ"]["A_sign_dense_minus_one"] * sc,
                                             "B_mean_bits0to6_fJ": ga["glitch_fJ"]["B_mean_bits0to6"] * sc,
                                             "A_mean_bits0to6_fJ": ga["glitch_fJ"]["A_mean_bits0to6"] * sc}
        out["arms"][arm] = res
        print(f"{arm}: k zero {kz:.3f} (a {rz['coef_fJ']['dclk']:.2f}) rms {rz['rms_w']:.3f} loo {rz['loo']['rms_w']:.3f} | "
              f"glitch k {kg:.3f} (a {rg['coef_fJ']['dclk']:.2f}) rms {rg['rms_w']:.3f} loo {rg['loo']['rms_w']:.3f} | "
              f"3-term k {r3['coef_fJ']['dnets_zero']:.3f} k_g {r3['coef_fJ']['excess_unit']:.3f} +- {r3['coef_jackknife_se_fJ']['excess_unit']:.3f} "
              f"(w {r3['glitch_weight_k_g_over_k']:.2f}) rms {r3['rms_w']:.3f} loo {r3['loo']['rms_w']:.3f}")
    json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
