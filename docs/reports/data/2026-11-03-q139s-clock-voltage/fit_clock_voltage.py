#!/usr/bin/env python3
"""Q139(s): the clock/voltage term refitted on every committed voltage read, and two out-of-sample tests. Post hoc, desk only.

    python3 fit_clock_voltage.py <lab repo root> <voltage-reads.json> --out clock-voltage.json > clock-voltage.txt

Needs numpy (the voltage table only); everything else is the lab's own frozen code, imported unchanged:
tools/claims-v3/hpl/surface_hpl.py (fit_linear, the E64 relation), tools/claims-v3/e119/make_predictions_e119.py (dither).

1. THE VOLTAGE TABLE. From survey_voltage_reads.py's bins: per card and operating point, the on-die PVT reading
   (die_mv.minion, DM_CMD_GET_ASIC_VOLTAGE), the PMIC's set point (reg_mv.minion, DM_CMD_GET_MODULE_VOLTAGE) and the SP
   statistic (sp.minion_mv[0], DM_CMD_GET_SP_STATS), over steady samples (the clock equal to the previous sample's within
   1 s). "busy" = minion rail >= 8 W (sp.minion_w[0]). Per data dir medians give the session-to-session spread. The droop:
   least squares of die_mv on the rail's current (sp.minion_w / V) at the set point's mode, per card and point.
2. s(f) = (V_f / V_600)^n x f / 600 for aifoundry2 (n = 2 unless said), V from: M7 (frozen: 0.517 / 0.568 / 0.618, E64's,
   from September's analyze_dvfs.py); PVT busy medians over every aifoundry2 read; the same without E143's data dir (the
   fit that never saw E143); the set points. The cross-card transfer xfer = (V_600,aifoundry3 / V_600,aifoundry2)^2 the same way.
3. E118's two-clock price ratio on aifoundry1 card 0, (V_600 / V_800)^n, V from card 0's reads WITHOUT E118's and E60's
   data dirs (the sessions whose prices make the ratio), against E118's committed ratios (posthoc_exponents.json rows).
4. E143's governed bursts (blind pool 5, aifoundry2, its own governor): each tile's burst clock and board W from M7's frozen
   D (predictions-e143.json D600_a3_footing_w) through M7's relation with the clock/voltage term swapped, scored against the
   measured per-tile means (results.json score.reported.tiles) on E143's registered groups (governed 19, pinned 17):
     A0  M7 as frozen (reproduces E143-F1/F2/W1/W2);
     A1  s(f) from the reads (never E143's), everything else frozen;
     A2  A1 refitted through M7's own chain: B(f) by E64's fit_linear on E64's committed rows, each E80/E83 run's c from its
         committed 58 C powers (reduce_kspeed's formula), the burst cap refitted on E80's and E83's kinds bursts (M7's
         golden-section fit), xfer from the reads; c_zeros kept frozen unless E64's zeros runs reproduce it;
     A3  A2 with n = 2.43 (E72's registered board exponent on aifoundry2; never E118's or E143's rows);
     A4  A2 with s(700), s(800) measured from board power instead of voltage (section 2b), never E143.
2b. THE FORM, FROM POWER (not a voltage read; labelled): P_f = B_f + c s_f gives P_800 = (B_800 - B_600 s_800) + s_800 P_600
   across runs, so the slope of each run's 58 C-referred P_800 on its P_600 (E64 figures.json runs p_ref; E80's and E83's
   runs p_ref58_w: the start ramp passes through every point) measures s(800) without B; likewise s(700). The exponent n
   that makes (V_f/V_600)^n f/600 equal it uses the reads' V. Caveat: P_600 comes from the ramp's first pass or two.
   The die rise is M7's frozen burst heat law, k (P - P_idle), on each arm's board W.
"""
import argparse
import collections
import json
import math
import os
import statistics as st
import sys

import numpy as np

PTS = (600, 700, 800)


def rms(e):
    e = [x for x in e if x is not None]
    return math.sqrt(sum(x * x for x in e) / len(e)) if e else None


def wmed(v, w):
    o = np.argsort(v)
    v = np.asarray(v, float)[o]
    c = np.cumsum(np.asarray(w, float)[o])
    return float(v[np.searchsorted(c, 0.5 * c[-1])])


def wq(v, w, q):
    o = np.argsort(v)
    v = np.asarray(v, float)[o]
    c = np.cumsum(np.asarray(w, float)[o])
    return float(v[min(len(v) - 1, np.searchsorted(c, q * c[-1]))])


# ------------------------------------------------------------------ 1. the voltage table
def voltage_table(reads, exclude_dirs=()):
    T = collections.defaultdict(lambda: {"die": [], "reg": collections.Counter(), "sp": [], "dirs": collections.defaultdict(list), "droop": []})
    for r in reads["files"]:
        if r["top"] in exclude_dirs:
            continue
        for b in r["bins"]:
            f, steady, reg, die, spv, wb, n, sbw, sT, smw, nT = b
            if not steady:
                continue
            k = (r["card"], f)
            if reg is not None:
                T[k]["reg"][reg] += n
            if spv is not None:
                T[k]["sp"].append((spv, n))
            if die is None:
                continue
            busy = wb is not None and wb >= 8.0
            T[k]["die"].append((die, n, busy))
            T[k]["dirs"][r["top"]].append((die, n))
            if wb is not None and reg is not None:
                T[k]["droop"].append((reg, die, smw / n, n))
            if nT and reg is not None:
                T[k].setdefault("temp", []).append((reg, die, sT / nT, nT))
    out = {}
    for (card, f), v in sorted(T.items()):
        if not v["die"] and not v["sp"]:
            continue
        rec = {"card": card, "mhz": f}
        if v["die"]:
            dv = [x[0] for x in v["die"]]
            w = [x[1] for x in v["die"]]
            bz = [(x[0], x[1]) for x in v["die"] if x[2]]
            rec.update({"n_pvt": int(sum(w)), "pvt_median_mv": wmed(dv, w), "pvt_p05_p95_mv": [wq(dv, w, 0.05), wq(dv, w, 0.95)],
                        "pvt_mean_mv": float(np.average(dv, weights=w)),
                        "pvt_busy_median_mv": wmed([a for a, _ in bz], [b for _, b in bz]) if bz else None,
                        "pvt_busy_mean_mv": float(np.average([a for a, _ in bz], weights=[b for _, b in bz])) if bz else None,
                        "n_busy": int(sum(b for _, b in bz))})
            dm = {d: wmed([a for a, _ in xs], [b for _, b in xs]) for d, xs in v["dirs"].items() if sum(b for _, b in xs) >= 100}
            rec["n_dirs"] = len(dm)
            rec["dir_medians_range_mv"] = [min(dm.values()), max(dm.values())] if dm else None
            rec["dir_medians_mv"] = dict(sorted(dm.items()))
        if v["reg"]:
            mode, cnt = v["reg"].most_common(1)[0]
            rec["set_point_mode_mv"] = mode
            rec["set_point_mode_share"] = cnt / sum(v["reg"].values())
            rec["n_set_point"] = int(sum(v["reg"].values()))
            dr = [x for x in v["droop"] if x[0] == mode]
            if len(dr) >= 3 and sum(x[3] for x in dr) > 200:
                I = np.array([x[2] / (x[1] / 1000.0) for x in dr])     # rail current, A
                y = np.array([x[1] for x in dr], float)
                ww = np.array([x[3] for x in dr], float)
                X = np.vstack([np.ones_like(I), I]).T
                Wm = np.diag(ww)
                beta = np.linalg.solve(X.T @ Wm @ X, X.T @ Wm @ y)
                rec["droop_fit"] = {"pvt_at_0A_mv": float(beta[0]), "mv_per_A": float(beta[1]), "mohm": float(-beta[1]),
                                    "current_A_p05_p95": [wq(I, ww, 0.05), wq(I, ww, 0.95)], "n": int(ww.sum())}
        tp = [x for x in v.get("temp", []) if x[0] == rec.get("set_point_mode_mv")]
        if len(tp) >= 3 and sum(x[3] for x in tp) > 200:
            Tc = np.array([x[2] for x in tp])
            y = np.array([x[1] for x in tp], float)
            ww = np.array([x[3] for x in tp], float)
            if np.ptp(Tc) >= 3:
                X = np.vstack([np.ones_like(Tc), Tc]).T
                Wm = np.diag(ww)
                beta = np.linalg.solve(X.T @ Wm @ X, X.T @ Wm @ y)
                rec["pvt_temp_fit"] = {"mv_per_C": float(beta[1]), "die_C_p05_p95": [wq(Tc, ww, 0.05), wq(Tc, ww, 0.95)], "n": int(ww.sum())}
        if v["sp"]:
            rec["sp_stat_median_mv"] = wmed([a for a, _ in v["sp"]], [b for _, b in v["sp"]])
            rec["n_sp"] = int(sum(b for _, b in v["sp"]))
        out[f"{card}@{f}"] = rec
    return out


def sf(V, n=2.0):
    return {f: (V[f] / V[600]) ** n * f / 600.0 for f in PTS}


# ------------------------------------------------------------------ 4. E143's governed bursts through M7's chain
class Chain:
    def __init__(self, root):
        self.root = root
        sys.path.insert(0, os.path.join(root, "tools", "claims-v3", "hpl"))
        sys.path.insert(0, os.path.join(root, "tools", "claims-v3", "e119"))
        import surface_hpl as SH  # noqa: E402
        import make_predictions_e119 as M119  # noqa: E402
        self.SH, self.M119 = SH, M119
        self.m7 = json.load(open(os.path.join(root, "docs/reports/data/2026-11-02-q138m-model/m7.json")))
        a2 = self.m7["aifoundry2"]
        rel = a2["relation"]
        self.B7 = {int(k): v for k, v in rel["B_w"].items()}
        self.S7 = {int(k): v for k, v in rel["s_f"].items()}
        self.CZ7, self.X7 = rel["c_zeros_w"], rel["xfer"]
        self.W7, self.SIG = a2["burst_cap"]["W_star_used_w"], a2["burst_cap"]["sigma_w"]
        self.kh, self.p_idle = a2["burst_heat"]["k_used_c_per_w"], a2["burst_heat"]["P_idle_w"]
        self.e64 = json.load(open(os.path.join(root, "docs/reports/data/2026-10-23-e64-horace-power-limit/figures.json")))
        self.kinds = {}
        for d in ("2026-10-31-e80-kinds-speed", "2026-10-31-e83-kinds-speed-rest"):
            self.kinds[d] = json.load(open(os.path.join(root, "docs/reports/data", d, "results.json")))

    # E64's fit, with the s(f) given (surface_hpl.fit_linear reads the module's S)
    def fit_B(self, S):
        old = dict(self.SH.S)
        self.SH.S.clear()
        self.SH.S.update(S)
        try:
            rows = []
            for m in self.e64["runs"]:
                pref = m.get("p_ref")
                if pref and m["block"] in ("LAD", "MIN", "SUS", "SMOKE"):
                    for f in PTS:
                        if pref.get(str(f)) is not None:
                            rows.append((m["run"], f, pref[str(f)]))
            B, c, r = self.SH.fit_linear(rows)
        finally:
            self.SH.S.clear()
            self.SH.S.update(old)
        return {int(k): v for k, v in B.items()}, c, r, len(rows)

    # each E80/E83 kinds cell: burst_mhz as committed; c_w recomputed from its BURST runs' committed 58 C powers
    def cells(self, S, B):
        out = []
        for d, R in self.kinds.items():
            runs = R["runs"]
            for lab, c in R["cells"].items():
                if c.get("burst_mhz") is None or c.get("c_w") is None:
                    continue
                t, k = lab.split("/")
                bu = [m for m in runs if m.get("kind") == lab and m.get("block") == "BURST"]   # reduce_kspeed's bu
                cs = []
                for m in bu:
                    p = m.get("p_ref58_w")
                    if not p:
                        continue
                    num = sum(S[f] * (p[str(f)] - B[f]) for f in PTS if p.get(str(f)) is not None)
                    den = sum(S[f] ** 2 for f in PTS if p.get(str(f)) is not None)
                    if den:
                        cs.append(num / den)
                out.append({"exp": d.split("-")[3].upper(), "type": t, "kind": k, "burst_mhz": float(c["burst_mhz"]),
                            "c_w_committed": float(c["c_w"]), "c_w": st.mean(cs) if cs else None})
        return out

    def clock(self, B, S, c, W):
        lv = {f: B[f] + c * S[f] for f in PTS}
        return self.M119.dither(lv, W, self.SIG)[0], lv

    @staticmethod
    def p_at(P, f):
        if f >= 800:
            return P[800]
        if f >= 700:
            return P[700] + (P[800] - P[700]) * (f - 700) / 100.0
        return P[600] + (P[700] - P[600]) * (f - 600) / 100.0 if f >= 600 else P[600]

    def fit_W(self, cells, B, S):
        lo, hi = 50.0, 90.0
        e = lambda W: sum((self.clock(B, S, x["c_w"], W)[0] - x["burst_mhz"]) ** 2 for x in cells)
        for _ in range(60):
            a, b = lo + (hi - lo) * 0.382, lo + (hi - lo) * 0.618
            if e(a) < e(b):
                hi = b
            else:
                lo = a
        return (lo + hi) / 2

    def predict(self, D, t, B, S, CZ, X, W):
        c = CZ[t] + D / X
        f, lv = self.clock(B, S, c, W)
        return f, self.p_at(lv, f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("reads")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    import gzip
    reads = json.load(gzip.open(a.reads, "rt") if a.reads.endswith(".gz") else open(a.reads))
    E143D = "2026-11-02-e143-blind5-aifoundry2"
    E118D, E60D = "2026-11-01-e118-two-clock-card0", "2026-10-20-bitflip-ladder"
    out = {"_note": "Q139(s) fit_clock_voltage.py: post hoc desk refit of the clock/voltage term on committed reads; nothing on a card"}
    L = []

    # 1. tables
    tab_all = voltage_table(reads)
    tab_no143 = voltage_table(reads, exclude_dirs=(E143D,))
    tab_no118 = voltage_table(reads, exclude_dirs=(E118D, E60D))
    out["voltage_table"] = tab_all
    L.append("1. VOLTAGE PER OPERATING POINT (steady samples; PVT = die_mv.minion, GET_ASIC_VOLTAGE; set = reg_mv.minion, GET_MODULE_VOLTAGE)")
    L.append(f"{'card@MHz':18s} {'n PVT':>9s} {'PVT med':>8s} {'busy med':>8s} {'p05-p95':>9s} {'dirs':>4s} {'dir range':>10s} {'set':>5s} {'share':>6s} {'SP stat':>7s} {'droop mohm':>10s} {'I p05-p95 A':>12s} {'mV/C':>8s} {'die C':>9s}")
    for k, r in tab_all.items():
        dr = r.get("droop_fit") or {}
        L.append(f"{k:18s} {r.get('n_pvt', 0):9d} {r.get('pvt_median_mv', float('nan')):8.0f} {r.get('pvt_busy_median_mv') or float('nan'):8.0f} "
                 f"{str([int(x) for x in r.get('pvt_p05_p95_mv', [0, 0])]):>9s} {r.get('n_dirs', 0):4d} {str(r.get('dir_medians_range_mv')):>10s} "
                 f"{r.get('set_point_mode_mv', 0):5d} {r.get('set_point_mode_share', 0):6.3f} {r.get('sp_stat_median_mv') or float('nan'):7.0f} "
                 f"{dr.get('mohm', float('nan')):10.3f} {str([round(x, 1) for x in dr.get('current_A_p05_p95', [])]):>12s} "
                 f"{(r.get('pvt_temp_fit') or {}).get('mv_per_C', float('nan')):8.3f} {str([round(x) for x in (r.get('pvt_temp_fit') or {}).get('die_C_p05_p95', [])]):>9s}")
    out["config_reads"] = collections.Counter(f"{c['card']}@{c['mhz']}:{c['mv']}" for c in reads["config_reads"]).most_common()
    L.append("config reads (ettelem config: minion_mhz with GET_ASIC_VOLTAGE minion mV): " + ", ".join(f"{k} x{v}" for k, v in out["config_reads"]))

    # 2. s(f) variants (aifoundry2) and xfer
    def pv(tab, card, f, key="pvt_busy_mean_mv"):
        return tab[f"{card}@{f}"][key] / 1000.0
    V = {"M7_frozen": {600: 0.517, 700: 0.568, 800: 0.618},
         "pvt_busy_median_all": {f: pv(tab_all, "aifoundry2", f, "pvt_busy_median_mv") for f in PTS},
         "pvt_busy_mean_all": {f: pv(tab_all, "aifoundry2", f) for f in PTS},
         "pvt_busy_mean_no_E143": {f: pv(tab_no143, "aifoundry2", f) for f in PTS},
         "set_points": {f: tab_all[f"aifoundry2@{f}"]["set_point_mode_mv"] / 1000.0 for f in PTS}}
    S = {k: sf(v) for k, v in V.items()}
    S["pvt_no_E143_n2.43"] = sf(V["pvt_busy_mean_no_E143"], 2.43)
    X = {"M7_frozen": (0.5218 / 0.517) ** 2,
         "pvt_busy_mean_all": (pv(tab_all, "aifoundry3", 600) / pv(tab_all, "aifoundry2", 600)) ** 2,
         "pvt_busy_mean_no_E143": (pv(tab_no143, "aifoundry3", 600) / pv(tab_no143, "aifoundry2", 600)) ** 2,
         "set_points": (tab_all["aifoundry3@600"]["set_point_mode_mv"] / tab_all["aifoundry2@600"]["set_point_mode_mv"]) ** 2}
    out["V_aifoundry2_v"] = V
    out["s_f"] = S
    out["xfer"] = X
    L.append("")
    L.append("2. s(f) = (V_f/V_600)^n f/600 ON aifoundry2, AND THE TRANSFER xfer = (V_600,a3 / V_600,a2)^2")
    for k in S:
        vv = V.get(k.replace("_n2.43", "")) or V["pvt_busy_mean_no_E143"]
        L.append(f"  {k:24s} V = {', '.join(f'{vv[f]:.4f}' for f in PTS)} V   s(700) = {S[k][700]:.4f}  s(800) = {S[k][800]:.4f}"
                 f"   ({100 * (S[k][700] / S['M7_frozen'][700] - 1):+.2f}% / {100 * (S[k][800] / S['M7_frozen'][800] - 1):+.2f}% vs M7)")
    for k, v in X.items():
        L.append(f"  xfer {k:22s} {v:.5f} ({100 * (v / X['M7_frozen'] - 1):+.2f}% vs M7)")
    # cross-card V^2 against the measured card scale (rank 5's cheap read)
    v_c1, v_a3, v_a2, v_c0 = (pv(tab_all, c, 600) for c in ("aifoundry1c1", "aifoundry3", "aifoundry2", "aifoundry1c0"))
    out["cross_card_v2_at_600"] = {"aifoundry1c1_over_aifoundry3": (v_c1 / v_a3) ** 2, "aifoundry2_over_aifoundry3": (v_a2 / v_a3) ** 2,
                                   "aifoundry1c0_over_aifoundry3": (v_c0 / v_a3) ** 2,
                                   "V600_v": {"aifoundry1c1": v_c1, "aifoundry3": v_a3, "aifoundry2": v_a2, "aifoundry1c0": v_c0}}
    L.append(f"  cross-card V^2 at 600 MHz (PVT busy means): card1/a3 {(v_c1 / v_a3) ** 2:.4f}, a2/a3 {(v_a2 / v_a3) ** 2:.4f}, card0/a3 {(v_c0 / v_a3) ** 2:.4f}")

    # 2b. the form from board power (labelled; not a voltage read)
    R = os.path.join(root, "docs/reports/data")
    src = {"E64": [m.get("p_ref") for m in json.load(open(os.path.join(R, "2026-10-23-e64-horace-power-limit/figures.json")))["runs"]
                   if m["block"] in ("LAD", "MIN", "SUS", "SMOKE")]}
    for d, k in (("2026-10-31-e80-kinds-speed", "E80"), ("2026-10-31-e83-kinds-speed-rest", "E83")):
        src[k] = [m.get("p_ref58_w") for m in json.load(open(os.path.join(R, d, "results.json")))["runs"]]

    def slope(pairs):
        x = np.array([q[0] for q in pairs])
        y = np.array([q[1] for q in pairs])
        Xm = np.vstack([np.ones_like(x), x]).T
        b = np.linalg.lstsq(Xm, y, rcond=None)[0]
        res = y - Xm @ b
        cov = (res @ res / (len(y) - 2)) * np.linalg.inv(Xm.T @ Xm)
        return {"s": float(b[1]), "se": float(math.sqrt(cov[1, 1])), "intercept_w": float(b[0]), "rms_w": float(math.sqrt(np.mean(res * res))),
                "n_runs": len(y), "P600_range_w": [float(x.min()), float(x.max())]}
    form = {}
    Vr = V["pvt_busy_mean_no_E143"]
    for f in (700, 800):
        for k in ("E64", "E80", "E83", "pooled"):
            ps = [p for kk in (src if k == "pooled" else {k: src[k]}) for p in src[kk]]
            pairs = [(p["600"], p[str(f)]) for p in ps if p and p.get("600") is not None and p.get(str(f)) is not None]
            r = slope(pairs)
            r["n_implied"] = math.log(r["s"] / (f / 600.0)) / math.log(Vr[f] / Vr[600])
            r["n_se"] = r["se"] / r["s"] / math.log(Vr[f] / Vr[600])
            form[f"{k}@{f}"] = r
    out["form_from_power"] = form
    S["power_ramp_slopes"] = {600: 1.0, 700: form["pooled@700"]["s"], 800: form["pooled@800"]["s"]}
    L.append("")
    L.append("2b. THE FORM FROM BOARD POWER (labelled; slope of each run's P_f on its P_600, 58 C-referred, E64/E80/E83 start ramps; never E143)")
    for k, r in form.items():
        L.append(f"  {k:12s} s = {r['s']:.4f} +- {r['se']:.4f}  (V^2 from the reads: {S['pvt_busy_mean_no_E143'][int(k.split('@')[1])]:.4f})  implied n = {r['n_implied']:.2f} +- {r['n_se']:.2f}"
                 f"  rms {r['rms_w']:.2f} W  runs {r['n_runs']}")

    # 3. E118's ratio
    e118 = json.load(open(os.path.join(root, "docs/reports/data", E118D, "posthoc_exponents.json")))
    v6, v8 = pv(tab_no118, "aifoundry1c0", 600), pv(tab_no118, "aifoundry1c0", 800)
    v6s, v8s = (tab_no118[f"aifoundry1c0@{f}"]["set_point_mode_mv"] / 1000.0 for f in (600, 800))
    preds = {"V2_pvt_card0_never_E118_E60": (v6 / v8) ** 2, "V2_set_points_card0": (v6s / v8s) ** 2,
             "V2_E118_registered_voltages": (e118["v600"] / e118["v800"]) ** 2,
             "M7_frozen_aifoundry2_voltages": (0.517 / 0.618) ** 2,
             "Vn_E72_board_n2.43_card0_pvt": (v6 / v8) ** 2.43, "Vn_E72_rail_n1.72_card0_pvt": (v6 / v8) ** 1.72,
             "Vn_ramp_n_aifoundry2_card0_pvt": (v6 / v8) ** form["pooled@800"]["n_implied"],
             "energy_also_scales_with_f": (v6 / v8) ** 2 * 600 / 800}
    rows = [{"row": r["row"], "ratio": r["ratio"], "ratio_se": r["ratio_se"]} for r in e118["rows"]]
    sc = {}
    for pk, p in preds.items():
        sc[pk] = {"pred": p, "by_row": [{"row": r["row"][:60], "meas_minus_pred": r["ratio"] - p, "in_se": (r["ratio"] - p) / r["ratio_se"]} for r in rows]}
    out["E118_ratio"] = {"card0_v_never_E118_E60": {"600": v6, "800": v8, "set_600": v6s, "set_800": v8s,
                                                     "n_600": tab_no118["aifoundry1c0@600"]["n_busy"], "n_800": tab_no118["aifoundry1c0@800"]["n_busy"],
                                                     "dirs_600": sorted(tab_no118["aifoundry1c0@600"]["dir_medians_mv"]), "dirs_800": sorted(tab_no118["aifoundry1c0@800"]["dir_medians_mv"])},
                         "measured_rows": rows, "predictions": sc}
    L.append("")
    L.append(f"3. E118's TWO-CLOCK PRICE RATIO (600/800) ON aifoundry1 card 0; card 0's V without E118's and E60's dirs: {v6:.4f} / {v8:.4f} V "
             f"(set points {v6s:.3f} / {v8s:.3f}); E118 registered {e118['v600']:.4f} / {e118['v800']:.4f}")
    for r in rows:
        L.append(f"  measured  {r['ratio']:.4f} +- {r['ratio_se']:.4f}   {r['row'][:80]}")
    for pk, v in sc.items():
        L.append(f"  {pk:36s} {v['pred']:.4f}   meas-pred: " + "  ".join(f"{x['meas_minus_pred']:+.4f} ({x['in_se']:+.1f} SE)" for x in v["by_row"]))

    # 4. E143
    ch = Chain(root)
    P143 = json.load(open(os.path.join(root, "tools/claims-v3/e143/predictions-e143.json")))
    R143 = json.load(open(os.path.join(root, "docs/reports/data", E143D, "results.json")))
    meas = R143["score"]["reported"]["tiles"]
    tiles = sorted(meas)
    # A2's refits
    B_rep, c64, rms64, n64 = ch.fit_B(ch.S7)
    rep_ok = all(abs(B_rep[f] - ch.B7[f]) < 1e-6 for f in PTS)
    zr = {}
    for t in ("fp32", "fp16", "int8"):
        zz = [v for k, v in c64.items() if f"-{t}-zeros" in k]
        zr[t] = st.mean(zz) if zz else None
    cz_reproduced = all(zr[t] is not None and abs(zr[t] - ch.CZ7[t]) < 0.02 for t in zr)
    cells7 = ch.cells(ch.S7, ch.B7)
    cw_dev = max(abs(x["c_w"] - x["c_w_committed"]) for x in cells7 if x["c_w"] is not None)
    W_rep = ch.fit_W([x for x in cells7 if x["c_w"] is not None], ch.B7, ch.S7)
    out["chain_reproduction"] = {"B_from_E64_rows_equals_M7": rep_ok, "B_rep": B_rep, "E64_rows": n64, "E64_fit_rms_w": rms64,
                                 "c_zeros_from_E64_zeros_runs": zr, "c_zeros_reproduced": cz_reproduced,
                                 "max_abs_c_w_recomputed_minus_committed": cw_dev, "W_star_refit_at_M7_terms": W_rep, "W_star_M7": ch.W7,
                                 "n_kinds_cells": len(cells7)}
    arms = {}

    def arm(name, B, S_, CZ, X_, W, note):
        rows_ = {}
        for n in tiles:
            t = P143["tiles"][n]["type"]
            D = P143["tiles"][n]["models"]["M7"]["D600_a3_footing_w"]
            f, P = ch.predict(D, t, B, S_, CZ, X_, W)
            rows_[n] = {"type": t, "group": P143["tiles"][n]["group"], "mhz_pred": f, "w_pred": P, "rise_pred": ch.kh * (P - ch.p_idle),
                        "mhz_meas": meas[n]["burst_mhz"], "w_meas": meas[n]["burst_w"], "rise_meas": meas[n]["rise_c"]}
        res = {"note": note, "B": B, "s_f": S_, "c_zeros": CZ, "xfer": X_, "W_star": W, "sets": {}}
        for sname, sel in (("governed", lambda r: r["group"] == "governed"), ("pinned", lambda r: r["group"] == "pinned"), ("all", lambda r: True)):
            rr = [r for r in rows_.values() if sel(r)]
            for q in ("mhz", "w", "rise"):
                e = [r[f"{q}_meas"] - r[f"{q}_pred"] for r in rr if r[f"{q}_meas"] is not None]
                res["sets"].setdefault(sname, {"n": len(rr)})[f"{q}_rms"] = rms(e)
                res["sets"][sname][f"{q}_mean_meas_minus_pred"] = st.mean(e) if e else None
        res["tiles"] = rows_
        arms[name] = res
        return res

    arm("A0_M7_frozen", ch.B7, ch.S7, ch.CZ7, ch.X7, ch.W7, "M7 as frozen in m7.json (reproduces E143's registered F1/F2/W1/W2)")
    S1 = S["pvt_busy_mean_no_E143"]
    arm("A1_s_from_reads_only", ch.B7, S1, ch.CZ7, ch.X7, ch.W7, "s(f) from aifoundry2's PVT busy means without E143's dir; B, c_zeros, xfer, W* frozen")
    for nm, Sx, note in (("A2_s_from_reads_chain_refit", S1, "s(f) from the reads (never E143), B refit on E64's rows, each E80/E83 cell's c recomputed, W* refit on the kinds bursts, xfer from the reads"),
                         ("A3_n2.43_chain_refit", S["pvt_no_E143_n2.43"], "as A2 with n = 2.43 (E72's registered board exponent, aifoundry2)"),
                         ("A4_power_slopes_chain_refit", S["power_ramp_slopes"], "as A2 with s(700), s(800) the board-power ramp slopes of E64/E80/E83 (section 2b)")):
        B2, c2, r2, _ = ch.fit_B(Sx)
        cz2 = ch.CZ7
        if cz_reproduced:
            cz2 = {t: st.mean([v for k, v in c2.items() if f"-{t}-zeros" in k]) for t in ("fp32", "fp16", "int8")}
        cl = [x for x in ch.cells(Sx, B2) if x["c_w"] is not None]
        W2 = ch.fit_W(cl, B2, Sx)
        loo = []
        for kk in sorted({(x["type"], x["kind"]) for x in cl}):
            tr = [x for x in cl if (x["type"], x["kind"]) != kk]
            Wk = ch.fit_W(tr, B2, Sx)
            loo += [x["burst_mhz"] - ch.clock(B2, Sx, x["c_w"], Wk)[0] for x in cl if (x["type"], x["kind"]) == kk]
        res = arm(nm, B2, Sx, cz2, X["pvt_busy_mean_no_E143"], W2, note)
        res["E64_fit_rms_w"] = r2
        res["kinds_bursts_loko_rms_mhz"] = rms(loo)
    # M7's own leave-one-kind-out on the kinds bursts at its frozen terms, for comparison
    loo7 = []
    cl7 = [x for x in cells7 if x["c_w"] is not None]
    for kk in sorted({(x["type"], x["kind"]) for x in cl7}):
        tr = [x for x in cl7 if (x["type"], x["kind"]) != kk]
        Wk = ch.fit_W(tr, ch.B7, ch.S7)
        loo7 += [x["burst_mhz"] - ch.clock(ch.B7, ch.S7, x["c_w"], Wk)[0] for x in cl7 if (x["type"], x["kind"]) == kk]
    arms["A0_M7_frozen"]["kinds_bursts_loko_rms_mhz"] = rms(loo7)
    out["E143"] = {k: {kk: vv for kk, vv in v.items() if kk != "tiles"} for k, v in arms.items()}
    out["E143_tiles"] = {k: v["tiles"] for k, v in arms.items()}
    reg = R143["score"]["rules"]
    out["E143_registered"] = {k: {"rms": reg[k]["rms"], "mean_err": reg[k]["mean_err"]} for k in ("E143-F1", "E143-F2", "E143-W1", "E143-W2", "E143-H1")}
    L.append("")
    L.append("4. E143'S BURSTS UNDER aifoundry2'S GOVERNOR (36 tiles; measured - predicted; registered groups)")
    L.append(f"  chain reproduction: B from E64's {n64} rows = M7's: {rep_ok}; c_zeros from E64's zeros runs {zr} reproduced: {cz_reproduced}; "
             f"E80/E83 c_w recomputed vs committed max |d| {cw_dev:.4f} W; W* refit at M7's terms {W_rep:.3f} (M7 {ch.W7:.3f})")
    L.append(f"  registered (E143 results.json): F1 governed clock {reg['E143-F1']['rms']} MHz (mean {reg['E143-F1']['mean_err']}); F2 pinned {reg['E143-F2']['rms']} ({reg['E143-F2']['mean_err']}); "
             f"W1 governed board {reg['E143-W1']['rms']} W ({reg['E143-W1']['mean_err']}); W2 pinned {reg['E143-W2']['rms']} ({reg['E143-W2']['mean_err']}); H1 rise {reg['E143-H1']['rms']} C")
    for k, v in arms.items():
        s = v["sets"]
        L.append(f"  {k:30s} s800 {v['s_f'][800]:.4f} B800 {v['B'][800]:.3f} W* {v['W_star']:.3f} xfer {v['xfer']:.5f} | "
                 f"gov clk {s['governed']['mhz_rms']:.2f} ({s['governed']['mhz_mean_meas_minus_pred']:+.2f}) W {s['governed']['w_rms']:.3f} ({s['governed']['w_mean_meas_minus_pred']:+.3f}) | "
                 f"pin clk {s['pinned']['mhz_rms']:.2f} ({s['pinned']['mhz_mean_meas_minus_pred']:+.2f}) W {s['pinned']['w_rms']:.3f} ({s['pinned']['w_mean_meas_minus_pred']:+.3f}) | "
                 f"all rise {s['all']['rise_rms']:.3f} C | kinds LOKO {v.get('kinds_bursts_loko_rms_mhz') or float('nan'):.2f} MHz")
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True, default=float)
    print("\n".join(L))


if __name__ == "__main__":
    main()
