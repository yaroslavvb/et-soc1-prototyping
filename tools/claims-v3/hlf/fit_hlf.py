#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E73: the heat path fitted across the frequencies, and the registered rules scored.

    python3 fit_hlf.py ANA/lockin.json --protocol protocol-e73.json \
        --predictions predictions.json --out fit.json [--md fit.txt]

What it does, in the order the README registers it.

1. **The reference line.**  The three 0.05 Hz blocks bracket the two new frequencies.  Their |H| is fitted
   with a weighted straight line in time (the camera's gain drift: E63 saw 59 -> 42 mK/W in an hour) and
   their phase with a weighted constant, because a gain that drifts with the camera's own temperature
   changes how many millikelvin a watt buys and not when the heat arrives.  Every block is then corrected
   to the session's mid-time by the line, and the line's own uncertainty at that block's time goes into
   the point's error in quadrature.  This is why the protocol spends 12 of its 41 minutes on references.
2. **The transfer table.**  Every (block, odd harmonic) pair with a board amplitude of at least 5 SE
   becomes one complex point H(f) in mK per watt.  0.05 Hz appears twice over - as the reference blocks'
   fundamental and as the 0.01 Hz block's fifth harmonic - and the two are compared, not merged.
3. **The models.**  Four nested shapes, each fitted by weighted complex least squares with ONE real
   positive gain (a complex gain would absorb a phase offset and hollow out the comparison):
       P1    G / (1 + i w tau)
       P1D   G / (1 + i w tau) * exp(-i w Td)                      (M1's family)
       P2    G / ((1 + i w tau1)(1 + i w tau2))                     (M2's family)
       P2D   G / ((1 + i w tau1)(1 + i w tau2)) * exp(-i w Td)
   The time constants come from a coarse-to-fine log grid (no scipy on the lab host); the gain is solved
   in closed form at every grid point.  chi-square counts two degrees of freedom per complex point.
   Errors on the time constants are the 1-sigma contour of the profile chi-square (delta chi2 = 1).
4. **The rules**, R1 to R6 and the inclusion rule, exactly as `predictions.json` froze them.
"""
from __future__ import annotations

import argparse
import json
import math
import os

import numpy as np

W = 2.0 * math.pi


# ------------------------------------------------------------------------------------- the shapes

def shape(name, f, p):
    w = W * np.asarray(f, dtype=np.float64)
    if name == "P1":
        return 1.0 / (1 + 1j * w * p[0])
    if name == "P1D":
        return np.exp(-1j * w * p[1]) / (1 + 1j * w * p[0])
    if name == "P2":
        return 1.0 / ((1 + 1j * w * p[0]) * (1 + 1j * w * p[1]))
    if name == "P2D":
        return np.exp(-1j * w * p[2]) / ((1 + 1j * w * p[0]) * (1 + 1j * w * p[1]))
    raise ValueError(name)


NPAR = {"P1": 1, "P1D": 2, "P2": 2, "P2D": 3}
LABEL = {"P1": "one pole", "P1D": "one pole and a delay", "P2": "two poles",
         "P2D": "two poles and a delay"}


def gain_and_chi2(name, f, H, sig, p):
    s = shape(name, f, p)
    wt = 1.0 / np.asarray(sig, dtype=np.float64) ** 2
    num = float(np.sum(wt * np.real(np.conj(s) * H)))
    den = float(np.sum(wt * np.abs(s) ** 2))
    if den <= 0:
        return 0.0, float("inf")
    g = num / den
    chi2 = float(np.sum(wt * np.abs(H - g * s) ** 2))
    return g, chi2


def grid_fit(name, f, H, sig, lo=0.05, hi=400.0, n=40, rounds=6):
    """Coarse-to-fine log grid over the model's time parameters; the gain is closed form."""
    k = NPAR[name]
    bounds = [(lo, hi)] * k
    if name in ("P1D", "P2D"):
        bounds[-1] = (1e-3, 60.0)          # a transport delay, seconds
    best = None
    for _r in range(rounds):
        axes = [np.exp(np.linspace(math.log(a), math.log(b), n)) for a, b in bounds]
        grids = np.meshgrid(*axes, indexing="ij")
        flat = [g.ravel() for g in grids]
        for i in range(len(flat[0])):
            p = [float(x[i]) for x in flat]
            if name in ("P2", "P2D") and p[1] > p[0]:
                continue                    # tau1 >= tau2 by convention; halves the grid
            g, c = gain_and_chi2(name, f, H, sig, p)
            if best is None or c < best[1]:
                best = (p, c, g)
        # shrink each axis around the winner
        nb = []
        for j, (a, b) in enumerate(bounds):
            span = (math.log(b) - math.log(a)) / (n - 1) * 2.5
            c0 = math.log(best[0][j])
            nb.append((math.exp(max(math.log(a), c0 - span)), math.exp(min(math.log(b), c0 + span))))
        bounds = nb
    p, c, g = best
    return dict(name=name, label=LABEL[name], params=p, gain=g, chi2=c,
                n_points=len(f), dof=2 * len(f) - NPAR[name] - 1,
                chi2_red=c / max(1, 2 * len(f) - NPAR[name] - 1),
                aic=c + 2 * (NPAR[name] + 1))


def profile_se(name, f, H, sig, p, j, chi2_min):
    """The delta chi2 = 1 interval of parameter j, the others refitted on a local grid."""
    out = [None, None]
    for s_dir, side in ((-1, 0), (+1, 1)):
        x = p[j]
        for _ in range(240):
            x *= (1.0 + s_dir * 0.01)
            if x <= 1e-4 or x > 4000:
                break
            q = list(p)
            q[j] = x
            if NPAR[name] > 1:
                # refit the other time parameters coarsely around their best values
                best = float("inf")
                others = [i for i in range(NPAR[name]) if i != j]
                axes = [np.exp(np.linspace(math.log(max(1e-3, p[i] / 3)),
                                           math.log(p[i] * 3), 16)) for i in others]
                mesh = np.meshgrid(*axes, indexing="ij")
                fl = [m.ravel() for m in mesh]
                for t in range(len(fl[0])):
                    r = list(q)
                    for a, i in enumerate(others):
                        r[i] = float(fl[a][t])
                    best = min(best, gain_and_chi2(name, f, H, sig, r)[1])
                c = best
            else:
                c = gain_and_chi2(name, f, H, sig, q)[1]
            if c - chi2_min >= 1.0:
                out[side] = x
                break
    return out


# -------------------------------------------------------------------------------- the reference line

def ref_line(points, t_mid):
    """Weighted straight line in time through the reference blocks' |H|, and a weighted constant phase."""
    t = np.array([p["t_s"] for p in points])
    y = np.array([p["mag"] for p in points])
    s = np.array([p["se_mag"] for p in points])
    ph = np.array([p["phase_deg"] for p in points])
    sp = np.array([max(p.get("se_phase_deg") or 5.0, 1e-3) for p in points])
    wt = 1.0 / s ** 2
    X = np.column_stack([np.ones(len(t)), t - t_mid])
    A = X.T @ (wt[:, None] * X)
    b = X.T @ (wt * y)
    c = np.linalg.solve(A, b)
    cov = np.linalg.inv(A)
    res = y - X @ c
    chi2 = float(np.sum(wt * res ** 2))
    wp = 1.0 / sp ** 2
    ph0 = float((wp * ph).sum() / wp.sum())
    chi2_ph = float(np.sum(wp * (ph - ph0) ** 2))
    return dict(mag_at_mid=float(c[0]), se_mag_at_mid=float(math.sqrt(cov[0, 0])),
                slope_mk_per_w_per_s=float(c[1]), se_slope=float(math.sqrt(cov[1, 1])),
                drift_per_hour_frac=float(c[1] * 3600.0 / c[0]) if c[0] else None,
                phase_deg=ph0, chi2=chi2, dof=max(0, len(t) - 2), chi2_phase=chi2_ph,
                dof_phase=max(0, len(t) - 1), t_mid_s=t_mid,
                residual_sigma=[float(r / ss) for r, ss in zip(res, s)],
                points=[dict(block=p["block"], t_s=p["t_s"], mag=p["mag"], se_mag=p["se_mag"],
                             phase_deg=p["phase_deg"]) for p in points])


def line_at(rl, t):
    return rl["mag_at_mid"] + rl["slope_mk_per_w_per_s"] * (t - rl["t_mid_s"])


def line_se_at(rl, t):
    # the line's own SE at t, from the two diagonal terms (the cross term is small and dropped,
    # which makes this slightly conservative)
    return math.hypot(rl["se_mag_at_mid"], rl["se_slope"] * (t - rl["t_mid_s"]))


# ------------------------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lockin")
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", default=None)
    ap.add_argument("--min-board-se", type=float, default=5.0)
    a = ap.parse_args()
    with open(a.lockin) as f:
        LK = json.load(f)
    with open(a.protocol) as f:
        proto = json.load(f)
    with open(a.predictions) as f:
        PR = json.load(f)
    spec = {(b.get("id") or b.get("name")): b for b in proto["blocks"]}

    # ------------------------------------------------------------ the table of points
    rows = []
    for bid, b in LK["blocks"].items():
        if "transfer" not in b:
            continue
        t_mid = b.get("t_mid_s")
        if t_mid is None:
            # the block's own mid-time, from its analysed laps' span as the lock-in recorded it
            t_mid = b.get("span_s", [0, 0])
            t_mid = 0.5 * (t_mid[0] + t_mid[1]) if isinstance(t_mid, list) else 0.0
        for k, r in sorted(b["transfer"].items(), key=lambda kv: int(kv[0])):
            if "H_mag" not in r:
                continue
            board_se = r.get("se_board_w") or float("inf")
            rows.append(dict(block=bid, k=int(k), f_hz=r["f_hz"], t_s=float(t_mid),
                             n_per_arm=b.get("n_per_arm"),
                             mag=r["H_mag"], se_mag=r["se_H_mag"], se_cplx=r["se_H"],
                             phase_deg=r["H_phase_deg"], se_phase_deg=r.get("se_H_phase_deg"),
                             H_re=r["H_re"], H_im=r["H_im"],
                             cam_mk=r["cam_mk"], se_cam_mk=r.get("se_cam_mk"),
                             board_w=r["board_w"], se_board_w=r.get("se_board_w"),
                             board_sigma=(r["board_w"] / board_se) if board_se else None,
                             cam_sigma=(r["cam_mk"] / r["se_cam_mk"]) if r.get("se_cam_mk") else None,
                             included=bool(board_se and r["board_w"] / board_se >= a.min_board_se)))

    refs = [r for r in rows if r["k"] == 1 and spec.get(r["block"], {}).get("n_per_arm") == 1]
    t_all = [r["t_s"] for r in rows] or [0.0]
    t_mid = 0.5 * (min(t_all) + max(t_all))
    rl = ref_line(refs, t_mid) if len(refs) >= 2 else None

    # ------------------------------------------------------------ drift correction
    for r in rows:
        if rl is None:
            r["drift_factor"] = 1.0
            r["mag_corr"], r["se_corr"] = r["mag"], r["se_cplx"]
            continue
        here = line_at(rl, r["t_s"])
        fac = rl["mag_at_mid"] / here if here else 1.0
        r["drift_factor"] = float(fac)
        r["mag_corr"] = r["mag"] * fac
        rel = line_se_at(rl, r["t_s"]) / here if here else 0.0
        r["se_corr"] = float(math.hypot(r["se_cplx"] * fac, r["mag"] * fac * rel))
        r["H_re_corr"], r["H_im_corr"] = r["H_re"] * fac, r["H_im"] * fac
        r["ratio_to_ref"] = r["mag_corr"] / rl["mag_at_mid"] if rl["mag_at_mid"] else None
        r["se_ratio_to_ref"] = r["se_corr"] / rl["mag_at_mid"] if rl["mag_at_mid"] else None

    use = [r for r in rows if r["included"]]
    f = np.array([r["f_hz"] for r in use])
    H = np.array([complex(r.get("H_re_corr", r["H_re"]), r.get("H_im_corr", r["H_im"]))
                  for r in use])
    # the lock-in's phase convention is a LAG: H = A exp(+i psi) with psi the lag. The models are
    # written with exp(-i w Td), so the data is conjugated once, here, into the models' convention.
    H = np.conj(H)
    sig = np.array([max(r.get("se_corr") or r["se_cplx"], 1e-9) for r in use])

    fits = {}
    if len(use) >= 3:
        for name in ("P1", "P1D", "P2", "P2D"):
            if 2 * len(use) - NPAR[name] - 1 < 1:
                continue
            fr = grid_fit(name, f, H, sig, n=36, rounds=6)
            ses = []
            for j in range(NPAR[name]):
                ses.append(profile_se(name, f, H, sig, fr["params"], j, fr["chi2"]))
            fr["param_names"] = (["tau_s"] if name == "P1" else
                                 ["tau_s", "delay_s"] if name == "P1D" else
                                 ["tau1_s", "tau2_s"] if name == "P2" else
                                 ["tau1_s", "tau2_s", "delay_s"])
            fr["param_ci68"] = ses
            fr["group_delay_s"] = float(sum(fr["params"][:2]) if name in ("P2", "P2D")
                                        else fr["params"][0] + (fr["params"][1] if name == "P1D"
                                                                else 0.0))
            fr["dc_gain_mk_per_w"] = fr["gain"]
            fr["residuals"] = [dict(block=r["block"], f_hz=r["f_hz"],
                                    resid_sigma=float(abs(H[i] - fr["gain"]
                                                          * shape(name, f[i], fr["params"])) / sig[i]))
                               for i, r in enumerate(use)]
            fits[name] = fr

    # ------------------------------------------------------------ the rules
    def pt(bid, k):
        for r in rows:
            if r["block"] == bid and r["k"] == k:
                return r
        return None

    rules = {}
    f10 = next((b for bid, b in LK["blocks"].items() if b.get("n_per_arm") == 5), None)
    f25 = next((b for bid, b in LK["blocks"].items() if b.get("n_per_arm") == 2), None)
    f10_id = next((bid for bid, b in LK["blocks"].items() if b.get("n_per_arm") == 5), None)
    f25_id = next((bid for bid, b in LK["blocks"].items() if b.get("n_per_arm") == 2), None)

    if f10 and "roi" in f10:
        roi = f10["roi"]
        p1 = pt(f10_id, 1) or {}
        nsig = roi["amp"] / roi["se_along"] if roi.get("se_along") else None
        bsig = p1.get("board_sigma")
        ok = bool(nsig and nsig >= 3 and roi.get("p_signflip", 1) <= 0.01 and bsig and bsig >= 5)
        rules["R1_detected_at_0p01"] = dict(
            roi_mk=roi["amp"], se_mk=roi["se_along"], sigma=nsig, p_signflip=roi.get("p_signflip"),
            board_w=p1.get("board_w"), board_sigma=bsig,
            verdict="PASS" if ok else "FAIL")
    if rl is not None:
        worst = max(abs(x) for x in rl["residual_sigma"])
        rules["R2_reference_line"] = dict(
            mag_at_mid=rl["mag_at_mid"], se=rl["se_mag_at_mid"],
            drift_per_hour_frac=rl["drift_per_hour_frac"], chi2=rl["chi2"], dof=rl["dof"],
            worst_residual_sigma=worst, phase_deg=rl["phase_deg"],
            chi2_phase=rl["chi2_phase"], dof_phase=rl["dof_phase"],
            verdict="PASS" if worst <= 3 else "FAIL")
    r25, r10 = pt(f25_id, 1), pt(f10_id, 1)
    if r25 and r10 and r25.get("ratio_to_ref") and r10.get("ratio_to_ref"):
        a25, s25 = r25["ratio_to_ref"], r25["se_ratio_to_ref"]
        a10, s10 = r10["ratio_to_ref"], r10["se_ratio_to_ref"]
        ok = (a25 - 1.0 >= s25) and (a10 - a25 >= math.hypot(s10, s25))
        rules["R3_low_pass"] = dict(ratio_0p025=a25, se_0p025=s25, ratio_0p01=a10, se_0p01=s10,
                                    verdict="PASS" if ok else "FAIL")
    if r10:
        d = PR["models"]["discriminator"]
        lag, se = r10["phase_deg"], r10.get("se_phase_deg") or 0.0
        z1 = (lag - d["lag_at_0p01_M1_deg"]) / se if se else None
        z2 = (lag - d["lag_at_0p01_M2_deg"]) / se if se else None
        sur = []
        if z1 is not None and abs(z1) <= 2:
            sur.append("M1 (one pole and a delay)")
        if z2 is not None and abs(z2) <= 2:
            sur.append("M2 (two poles)")
        rules["R4_group_delay"] = dict(
            lag_0p01_deg=lag, se_deg=se, M1_predicted_deg=d["lag_at_0p01_M1_deg"],
            M2_predicted_deg=d["lag_at_0p01_M2_deg"], sigma_from_M1=z1, sigma_from_M2=z2,
            mag_ratio_measured=r10.get("ratio_to_ref"),
            M1_predicted_ratio=d["H_over_ref_at_0p01_M1"], M2_predicted_ratio=d["H_over_ref_at_0p01_M2"],
            surviving=sur or ["neither within 2 SE"], verdict="REPORTED (no PASS by design)")
    h5 = pt(f10_id, 5)
    if h5 and rl is not None:
        want = complex(rl["mag_at_mid"] * math.cos(math.radians(rl["phase_deg"])),
                       rl["mag_at_mid"] * math.sin(math.radians(rl["phase_deg"])))
        got = complex(h5.get("H_re_corr", h5["H_re"]), h5.get("H_im_corr", h5["H_im"]))
        se = math.hypot(h5.get("se_corr") or h5["se_cplx"], rl["se_mag_at_mid"])
        rules["R5_0p05_twice"] = dict(
            from_reference=[want.real, want.imag], from_fifth_harmonic=[got.real, got.imag],
            diff=abs(got - want), se=se, sigma=abs(got - want) / se if se else None,
            board_sigma=h5.get("board_sigma"),
            verdict=("PASS" if se and abs(got - want) <= 3 * se else "FAIL"))
    hold, hold_ok = {}, True
    for bid, b in LK["blocks"].items():
        h = b.get("hold") or {}
        s = h.get("samples_800_share")
        d = h.get("die_mean_c")
        hold[bid] = dict(samples_800_share=s, die_mean_c=d, launches=h.get("launches"),
                         share_of_launches_held=h.get("share_held"))
        if s is not None and s < 0.95:
            hold_ok = False
        if d is not None and d >= 65.0:
            hold_ok = False
    rules["R6_hold"] = dict(per_block=hold, verdict="PASS" if hold_ok else "FAIL",
                            note=("samples at 800 MHz from 1.5 s into each launch; the per-launch dip "
                                  "count is reported in lockin.json without a verdict (E63's lesson)"))

    out = dict(experiment="E73", request="Q129",
               lockin=os.path.abspath(a.lockin), min_board_se=a.min_board_se,
               reference_line=rl, points=rows, points_included=len(use), fits=fits,
               preferred=(min(fits.values(), key=lambda x: x["aic"])["name"] if fits else None),
               rules=rules, frozen_predictions=PR["models"])
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1, default=float)
        fh.write("\n")

    lines = []
    lines.append(f"E73 transfer table ({len(rows)} points, {len(use)} in the fit; "
                 f"board >= {a.min_board_se} SE)")
    lines.append(f"{'block':10s} {'k':>2s} {'f/Hz':>7s} {'cam/mK':>9s} {'board/W':>9s} "
                 f"{'|H|':>8s} {'se':>6s} {'lag':>7s} {'se':>5s} {'H/ref':>7s} {'in':>3s}")
    for r in sorted(rows, key=lambda x: x["f_hz"]):
        lines.append(f"{r['block']:10s} {r['k']:2d} {r['f_hz']:7.4f} "
                     f"{r['cam_mk']:7.1f}+-{(r['se_cam_mk'] or 0):<4.0f} "
                     f"{r['board_w']:6.3f}+-{(r['se_board_w'] or 0):<4.3f} "
                     f"{r['mag']:8.2f} {r['se_mag']:6.2f} {r['phase_deg']:7.1f} "
                     f"{(r['se_phase_deg'] or 0):5.1f} "
                     f"{(r.get('ratio_to_ref') or float('nan')):7.3f} {'Y' if r['included'] else '.':>3s}")
    if rl:
        lines.append("")
        lines.append(f"reference line at 0.05 Hz: {rl['mag_at_mid']:.2f} +- {rl['se_mag_at_mid']:.2f} "
                     f"mK/W at the session mid-time, drift "
                     f"{100*(rl['drift_per_hour_frac'] or 0):+.1f}%/h, "
                     f"chi2 {rl['chi2']:.2f}/{rl['dof']}; phase {rl['phase_deg']:.1f} deg "
                     f"(chi2 {rl['chi2_phase']:.2f}/{rl['dof_phase']})")
    if fits:
        lines.append("")
        lines.append(f"{'model':24s} {'params':>34s} {'G/mK/W':>9s} {'chi2':>8s} {'dof':>4s} "
                     f"{'red':>6s} {'AIC':>8s}")
        for nm in ("P1", "P1D", "P2", "P2D"):
            if nm not in fits:
                continue
            fr = fits[nm]
            ps = ", ".join(f"{n.replace('_s','')}={v:.3g}" for n, v in
                           zip(fr["param_names"], fr["params"]))
            lines.append(f"{nm+' '+fr['label']:24s} {ps:>34s} {fr['gain']:9.2f} {fr['chi2']:8.2f} "
                         f"{fr['dof']:4d} {fr['chi2_red']:6.2f} {fr['aic']:8.2f}")
        lines.append(f"preferred by AIC: {out['preferred']}")
    lines.append("")
    for k, v in rules.items():
        lines.append(f"{k}: {v.get('verdict', '')}")
    txt = "\n".join(lines) + "\n"
    if a.md:
        with open(a.md, "w") as fh:
            fh.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
