#!/usr/bin/env python3
"""E85: the registered lock-in and the decision rules (README, Analysis and Decision rules).

    python3 lockin_hlk.py RED --protocol protocol-e85.json --predictions predictions.json \
        --template prereg/e62_bloom_dt.npy --scene-ref prereg/e62_scene.npy --fpa RED/fpa.npz --out ANA

RED is reduce_hm.py's output for the session (E62's reducer, unchanged).

1. **E63's lock-in, verbatim.**  This imports `lockin_hlc` and runs its `analyse_block` on every block
   of the protocol, with E63's ROI (the warm quarter of E62's bloom map, moved with the camera if the
   view moved by more than 2 binned pixels), E63's knobs and E63's seed.  Nothing in it is changed:
   per block the ROI's 0.05 Hz amplitude with a free offset for every stretch between shutter events,
   the board power through the same lap model, the transfer H = Z / W (mK per watt of fundamental)
   with its lap jackknife, the board step, the shutter-phase test and the FPA control.
2. **Added here, per block:** the analysed laps' mid-time (for the drift line), E73's hold measure
   (the share of 10 Hz samples at >= 790 MHz from 1.5 s into each analysed launch to its end, the die
   mean and max), the per-launch idle-reset dips, and each arm's steady board level.
3. **The reference line** (E73's `ref_line`, copied): a weighted straight line in time through the
   reference blocks' |H| (the camera's gain drift), and a weighted constant phase.
4. **The rules** E85-R1 ... R9, as predictions.json froze them, scored into score.json / score.txt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.join(HERE, "hlc"), os.path.join(HERE, "..", "hlc")):
    if os.path.exists(os.path.join(p, "lockin_hlc.py")):
        sys.path.insert(0, os.path.abspath(p))
        break
import lockin_hlc as L  # noqa: E402

HOLD_FROM_S = 1.5
HOLD_MHZ = 790.0


def wrap180(d):
    return (d + 180.0) % 360.0 - 180.0


# ------------------------------------------------------------------------------------------ per block

def block_extras(R, tel, block):
    laps = [x for x in L.block_laps(R, block) if x[3]]
    ts = tel[:, 0]
    t_mid = float(np.mean([0.5 * (t0 + t1) for (_, t0, t1, _, _) in laps])) if laps else None
    span = [float(min(t0 for (_, t0, _, _, _) in laps)), float(max(t1 for (_, _, t1, _, _) in laps))] if laps else None
    cyc = {c for (c, _, _, _, _) in laps}
    shares, dies, dips, arm_w = [], [], 0, {0: [], 1: []}
    n_launch = 0
    for la in R["launches"]:
        if la.get("block") != block or int(la["cycle"]) not in cyc:
            continue
        n_launch += 1
        a, b = la["t_start_ms"] / 1000.0 + HOLD_FROM_S, la["t_end_ms"] / 1000.0
        m = (ts >= a) & (ts <= b)
        mz = tel[m, 3]
        mz = mz[np.isfinite(mz)]
        if len(mz):
            shares.append(mz >= HOLD_MHZ)
            if (mz < HOLD_MHZ).any():
                dips += 1
        dies += list(tel[m, 2][np.isfinite(tel[m, 2])])
        a2, b2 = la["t_start_ms"] / 1000.0 + L.STEADY_FROM_S, la["t_end_ms"] / 1000.0 - L.STEADY_TO_END_S
        m2 = (ts >= a2) & (ts <= b2)
        if m2.any():
            arm_w[int(la["phase"])].append(float(np.median(tel[m2, 1])))
    allsh = np.concatenate(shares) if shares else np.zeros(0, bool)
    die = np.array(dies)
    sh = float(allsh.mean()) if len(allsh) else None
    dm = float(die.mean()) if len(die) else None
    return dict(t_mid_s=t_mid, span_s=span, launches_analysed=n_launch,
                hold=dict(samples=int(len(allsh)), share_ge_790=sh,
                          die_mean_c=dm, die_max_c=float(die.max()) if len(die) else None,
                          launches_with_dip=int(dips),
                          holds=bool(sh is not None and sh >= 0.95 and dm is not None and dm < 65.0)),
                arm_board_w=dict(A_median=float(np.median(arm_w[0])) if arm_w[0] else None,
                                 B_median=float(np.median(arm_w[1])) if arm_w[1] else None))


# ------------------------------------------------------------------------------------------ the reference line

def ref_line(points, t_mid):
    """E73's fit_hlf.ref_line: a weighted straight line in time through |H|, a weighted constant phase.
    With one point the line is that point with no slope; the phase gets its weighted-mean SE."""
    t = np.array([p["t_s"] for p in points])
    y = np.array([p["mag"] for p in points])
    s = np.array([max(p["se_mag"], 1e-9) for p in points])
    ph = np.array([p["phase_deg"] for p in points])
    sp = np.array([max(p.get("se_phase_deg") or 5.0, 1e-3) for p in points])
    wt = 1.0 / s ** 2
    wp = 1.0 / sp ** 2
    ph0 = float((wp * ph).sum() / wp.sum())
    out = dict(phase_deg=ph0, se_phase_deg=float(1.0 / math.sqrt(wp.sum())),
               chi2_phase=float(np.sum(wp * (ph - ph0) ** 2)), dof_phase=max(0, len(t) - 1), t_mid_s=t_mid,
               points=[dict(block=p["block"], t_s=p["t_s"], mag=p["mag"], se_mag=p["se_mag"],
                            phase_deg=p["phase_deg"], se_phase_deg=p.get("se_phase_deg")) for p in points])
    if len(t) == 1:
        out.update(mag_at_mid=float(y[0]), se_mag_at_mid=float(s[0]), slope_mk_per_w_per_s=0.0, se_slope=0.0,
                   drift_per_hour_frac=None, chi2=0.0, dof=0, residual_sigma=[0.0])
        return out
    X = np.column_stack([np.ones(len(t)), t - t_mid])
    A = X.T @ (wt[:, None] * X)
    c = np.linalg.solve(A, X.T @ (wt * y))
    cov = np.linalg.inv(A)
    res = y - X @ c
    out.update(mag_at_mid=float(c[0]), se_mag_at_mid=float(math.sqrt(cov[0, 0])),
               slope_mk_per_w_per_s=float(c[1]), se_slope=float(math.sqrt(cov[1, 1])),
               cov01=float(cov[0, 1]),
               drift_per_hour_frac=float(c[1] * 3600.0 / c[0]) if c[0] else None,
               chi2=float(np.sum(wt * res ** 2)), dof=max(0, len(t) - 2),
               residual_sigma=[float(r / ss) for r, ss in zip(res, s)])
    return out


def line_at(rl, t):
    return rl["mag_at_mid"] + rl["slope_mk_per_w_per_s"] * (t - rl["t_mid_s"])


def line_se_at(rl, t):
    """The line's SE at t, with the covariance term (exact for a straight line)."""
    dt = t - rl["t_mid_s"]
    v = rl["se_mag_at_mid"] ** 2 + (rl["se_slope"] * dt) ** 2 + 2.0 * dt * rl.get("cov01", 0.0)
    return math.sqrt(max(v, 0.0))


# ------------------------------------------------------------------------------------------ the rules

def score(res, PR, proto):
    spec = {(b.get("id") or b.get("name")): b for b in proto["blocks"]}
    pb = PR["blocks"]
    refs = [b for b in PR["reference_blocks"] if b in res and res[b].get("transfer_roi")]
    pts = [dict(block=b, t_s=res[b]["t_mid_s"], mag=res[b]["transfer_roi"]["mag"],
                se_mag=res[b]["transfer_roi"]["se_mag"], phase_deg=res[b]["transfer_roi"]["phase_deg"],
                se_phase_deg=res[b]["transfer_roi"]["se_phase_deg"]) for b in refs]
    t_all = [r["t_mid_s"] for r in res.values() if r.get("t_mid_s") is not None] or [0.0]
    t_mid = 0.5 * (min(t_all) + max(t_all))
    rl = ref_line(pts, t_mid) if pts else None
    rules, kinds = {}, {}
    if rl is not None:
        ucam = np.mean([complex(res[b]["roi"]["Z_re"], res[b]["roi"]["Z_im"]) / res[b]["roi"]["amp"] for b in refs])
        ucam = ucam / abs(ucam)
        upow = np.mean([complex(res[b]["power"]["Z_re"], res[b]["power"]["Z_im"]) / res[b]["power"]["amp"]
                        for b in refs])
        upow = upow / abs(upow)
    for bid, b in res.items():
        if spec.get(bid, {}).get("role") != "kind" or not b.get("transfer_roi") or rl is None:
            continue
        H = b["transfer_roi"]
        t = b["t_mid_s"]
        href, sel = line_at(rl, t), line_se_at(rl, t)
        Rk = H["mag"] / href
        se_own = H["se_mag"] / href
        se_line = H["mag"] * sel / href ** 2
        se_R = math.hypot(se_own, se_line)
        dlag = wrap180(H["phase_deg"] - rl["phase_deg"])
        se_lag = math.hypot(H["se_phase_deg"], rl["se_phase_deg"])
        Wf = b["power"]["amp"]
        step = b["board_step_w"]["mean"]
        p = pb[bid]
        # the camera as a wattmeter: the kind's camera fundamental through the drift-corrected reference
        # transfer, back to a board step via the session's own fundamental-per-step
        refs_fps = [res[r]["power"]["amp"] / res[r]["board_step_w"]["mean"] for r in refs]
        fps = float(np.mean(refs_fps))
        w_cam_step = b["roi"]["amp"] / href / fps
        se_w_cam = w_cam_step * math.hypot(b["roi"]["se_along"] / b["roi"]["amp"], sel / href)
        kinds[bid] = dict(
            format=p["format"], kind=p["kind"], t_mid_s=t,
            camera_roi_mk=b["roi"]["amp"], se_camera_roi_mk=b["roi"]["se_along"], camera_snr=b["roi"]["snr"],
            camera_phase_deg=b["roi"]["phase_deg"], p_signflip=b["roi"]["p_signflip"],
            board_step_w=step, se_board_step_w=b["board_step_w"]["se"], board_fundamental_w=Wf,
            board_step_full_card_equiv_w=step * PR["constants"]["full_card_minions"] / PR["constants"]["minions"],
            predicted_full_card_step_w=p["p800_full_card_w"]["kind"] - p["p800_full_card_w"]["zeros"],
            H_mk_per_w=H["mag"], se_H=H["se_mag"], H_phase_deg=H["phase_deg"], se_H_phase_deg=H["se_phase_deg"],
            mk_per_w_of_step=b["roi"]["amp"] / step if step else None,
            href_at_t=href, se_href_at_t=sel,
            H_drift_corrected_to_mid=H["mag"] * rl["mag_at_mid"] / href,
            ratio_R=Rk, se_R=se_R, se_R_own=se_own, se_R_line=se_line,
            lag_minus_ref_deg=dlag, se_lag_deg=se_lag,
            camera_read_step_w=w_cam_step, se_camera_read_step_w=se_w_cam,
            hold=b.get("hold"), arm_board_w=b.get("arm_board_w"))
    main = [k for k in PR["main_kinds"] if k in kinds]
    # R1
    for k in main:
        x = kinds[k]
        ok = x["p_signflip"] < 0.001 and 0.0 < x["H_phase_deg"] < 180.0
        rules.setdefault("E85-R1_seen", {})[k] = dict(p=x["p_signflip"], snr=x["camera_snr"],
                                                      lag_deg=x["H_phase_deg"], verdict="PASS" if ok else "FAIL")
    # R2
    for k in main:
        x = kinds[k]
        tol = max(3 * x["se_R"], 0.10)
        rules.setdefault("E85-R2_heat_follows_watts", {})[k] = dict(
            R=x["ratio_R"], se_R=x["se_R"], tolerance=tol,
            verdict="PASS" if abs(x["ratio_R"] - 1.0) <= tol else "FAIL")
    # R3
    if main:
        w = np.array([1.0 / kinds[k]["se_R_own"] ** 2 for k in main])
        Rv = np.array([kinds[k]["ratio_R"] for k in main])
        Rp = float((w * Rv).sum() / w.sum())
        se_own = float(1.0 / math.sqrt(w.sum()))
        se_line = float((w * np.array([kinds[k]["se_R_line"] for k in main])).sum() / w.sum())  # fully correlated
        se_p = math.hypot(se_own, se_line)
        tol = max(3 * se_p, 0.05)
        rules["E85-R3_pooled"] = dict(R_pooled=Rp, se=se_p, se_own=se_own, se_line=se_line, tolerance=tol,
                                      kinds=main, chi2_about_pooled=float((w * (Rv - Rp) ** 2).sum()),
                                      verdict="PASS" if abs(Rp - 1.0) <= tol else "FAIL")
    # R4
    for k in main:
        x = kinds[k]
        tol = max(3 * x["se_lag_deg"], 15.0)
        rules.setdefault("E85-R4_same_lag", {})[k] = dict(
            lag_minus_ref_deg=x["lag_minus_ref_deg"], se=x["se_lag_deg"], tolerance=tol,
            verdict="PASS" if abs(x["lag_minus_ref_deg"]) <= tol else "FAIL")
    # R5: the near-null kind
    if "E85-SP90" in res and res["E85-SP90"].get("roi", {}).get("n_laps", 0) >= 3 and rl is not None:
        b = res["E85-SP90"]
        t = b["t_mid_s"]
        Href_c = line_at(rl, t) * complex(math.cos(math.radians(rl["phase_deg"])),
                                          math.sin(math.radians(rl["phase_deg"])))
        W = complex(b["power"]["Z_re"], b["power"]["Z_im"])
        Z = complex(b["roi"]["Z_re"], b["roi"]["Z_im"])
        expect = (Href_c * W * np.conj(ucam)).real
        a = (Z * np.conj(ucam)).real
        se = math.sqrt(0.5 * (b["roi"]["se_re"] ** 2 + b["roi"]["se_im"] ** 2))
        rules["E85-R5_near_null"] = dict(along_ref_mk=float(a), se_mk=se, expected_mk=float(expect),
                                         board_step_w=b["board_step_w"]["mean"], board_fundamental_w=b["power"]["amp"],
                                         p_signflip=b["roi"]["p_signflip"],
                                         verdict="PASS" if abs(a - expect) <= 3 * se else "FAIL")
    # R6: electrical, every block
    for bid, b in res.items():
        if bid not in pb or "board_step_w" not in b:
            continue
        lo, hi = pb[bid]["board_step_band_w"]
        m = b["board_step_w"]["mean"]
        rules.setdefault("E85-R6_electrical", {})[bid] = dict(step_w=m, se=b["board_step_w"]["se"],
                                                             predicted=pb[bid]["board_step_w"], band=[lo, hi],
                                                             verdict="PASS" if lo <= m <= hi else "FAIL")
    # R7
    if rl is not None:
        if len(pts) >= 3:
            worst = max(abs(x) for x in rl["residual_sigma"])
            rules["E85-R7_reference_line"] = dict(worst_residual_sigma=worst, chi2=rl["chi2"], dof=rl["dof"],
                                                  mag_at_mid=rl["mag_at_mid"], se=rl["se_mag_at_mid"],
                                                  drift_per_hour_frac=rl["drift_per_hour_frac"],
                                                  phase_deg=rl["phase_deg"],
                                                  verdict="PASS" if worst <= 3 else "FAIL")
        else:
            rules["E85-R7_reference_line"] = dict(n_refs=len(pts), verdict="NOT SCORED")
    # R8
    for bid, b in res.items():
        h = b.get("hold")
        if not h:
            continue
        rules.setdefault("E85-R8_hold", {})[bid] = dict(share_ge_790=h["share_ge_790"], die_mean_c=h["die_mean_c"],
                                                       die_max_c=h["die_max_c"],
                                                       launches_with_dip=h["launches_with_dip"],
                                                       verdict="PASS" if h["holds"] else "FAIL")
    # R9
    for k in main:
        lo, hi = pb[k]["camera_roi_band_mk"]
        a = kinds[k]["camera_roi_mk"]
        rules.setdefault("E85-R9_absolute", {})[k] = dict(camera_roi_mk=a, predicted=pb[k]["camera_roi_mk"],
                                                         band=[lo, hi], verdict="PASS" if lo <= a <= hi else "FAIL")
    return dict(reference_line=rl, kinds=kinds, rules=rules)


def summary_lines(res, sc, order):
    out = ["E85 lock-in (E63's analyse_block, verbatim) and rules", ""]
    out.append("block      laps  ROI mK (SE)        phase   p        step W (SE)       fund W   H mK/W (SE)    lag    "
               "hold>=790  die mean/max  dips")
    for bid in order:
        r = res.get(bid)
        if not r or "roi" not in r:
            out.append(f"{bid:9s}  {r.get('error') if r else 'missing'}")
            continue
        H = r.get("transfer_roi") or {}
        h = r.get("hold") or {}
        out.append(f"{bid:9s}  {r['laps_analysed']:3d}  {r['roi']['amp']:7.1f} ({r['roi']['se_along']:5.1f})  "
                   f"{r['roi']['phase_deg']:6.1f}  {r['roi']['p_signflip']:.1e}  "
                   f"{r['board_step_w']['mean']:7.3f} ({r['board_step_w']['se']:.3f})  {r['power']['amp']:6.3f}  "
                   f"{H.get('mag', float('nan')):6.2f} ({H.get('se_mag', float('nan')):5.2f})  "
                   f"{H.get('phase_deg', float('nan')):6.1f}  {h.get('share_ge_790', float('nan')):.4f}     "
                   f"{h.get('die_mean_c', float('nan')):.1f}/{h.get('die_max_c', float('nan')):.1f}   "
                   f"{h.get('launches_with_dip')}")
    rl = sc.get("reference_line")
    if rl:
        out += ["", f"reference line: |H| {rl['mag_at_mid']:.2f} +- {rl['se_mag_at_mid']:.2f} mK/W at the session "
                    f"mid-time, slope {rl['slope_mk_per_w_per_s'] * 3600:.2f} mK/W per hour "
                    f"({(rl['drift_per_hour_frac'] or 0) * 100:.1f}%/h), phase {rl['phase_deg']:.1f} +- "
                    f"{rl['se_phase_deg']:.1f} deg, chi2 {rl['chi2']:.2f}/{rl['dof']}"]
    out += ["", "kind       R = H/Href(t) (SE)   lag - ref (SE)   camera-read step W (SE)  meter step W   mK/W of step"]
    for k, x in sc["kinds"].items():
        out.append(f"{k:9s}  {x['ratio_R']:.3f} ({x['se_R']:.3f})       {x['lag_minus_ref_deg']:6.1f} "
                   f"({x['se_lag_deg']:4.1f})     {x['camera_read_step_w']:6.3f} ({x['se_camera_read_step_w']:.3f})"
                   f"          {x['board_step_w']:6.3f}        {x['mk_per_w_of_step']:.2f}")
    out += ["", "rules:"]
    for name, v in sc["rules"].items():
        if "verdict" in v:
            out.append(f"  {name}: {v['verdict']}  " + json.dumps({a: b for a, b in v.items() if a != 'verdict'},
                                                                default=float)[:220])
        else:
            for bid, w in v.items():
                out.append(f"  {name} [{bid}]: {w['verdict']}  " +
                           json.dumps({a: b for a, b in w.items() if a != 'verdict'}, default=float)[:200])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("red")
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--template", required=True)
    ap.add_argument("--scene-ref", default=None)
    ap.add_argument("--fpa", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=63)
    a = ap.parse_args(argv)
    R = L.load_red(a.red)
    tel = L.tel_samples(a.red)
    tmpl = np.load(a.template).astype(np.float64)
    if tmpl.shape != R["mk"].shape[1:]:
        raise SystemExit(f"template {tmpl.shape} is not the RED's frame {R['mk'].shape[1:]}")
    reg = None
    if a.scene_ref and os.path.exists(os.path.join(a.red, "scene.npy")):
        dy, dx, pk = L.scene_shift(np.load(a.scene_ref).astype(np.float64),
                                   np.load(os.path.join(a.red, "scene.npy")).astype(np.float64))
        by, bx = int(round(dy / 2.0)), int(round(dx / 2.0))
        moved = max(abs(by), abs(bx)) > 2
        if moved:
            tmpl = np.roll(tmpl, (by, bx), axis=(0, 1))
        reg = dict(shift_full_px=[dy, dx], shift_binned_px=[by, bx], peak_corr=pk, template_moved=moved)
        print(f"camera view vs E62: moved ({dy}, {dx}) full-res px, peak corr {pk:.2f}; "
              f"template {'shifted' if moved else 'kept'}")
    roi = L.roi_from_template(tmpl)
    fpa = dict(np.load(a.fpa)) if a.fpa else None
    with open(a.protocol) as f:
        proto = json.load(f)
    with open(a.predictions) as f:
        PR = json.load(f)
    order = [b.get("id") or b.get("name") for b in proto["blocks"]]
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    res = {}
    for b in order:
        r, maps = L.analyse_block(R, tel, b, roi, tmpl, rng, fpa=fpa)
        r.update(block_extras(R, tel, b))
        res[b] = r
        if maps is not None:
            np.savez_compressed(os.path.join(a.out, f"{b}-maps.npz"), roi=roi, **maps)
    sc = score(res, PR, proto)
    knobs = dict(guard_pre_s=L.GUARD_PRE_S, guard_post_s=L.GUARD_POST_S, min_stretch_bins=L.MIN_STRETCH_BINS,
                 min_n_frac=L.MIN_N_FRAC, knot_s=L.KNOT_S, n_perm=L.N_PERM, roi_quantile=L.ROI_QUANTILE,
                 harm3=True, seed=a.seed, hold_from_s=HOLD_FROM_S, hold_mhz=HOLD_MHZ)
    out = dict(experiment=proto.get("experiment"), red=os.path.basename(os.path.normpath(a.red)),
               roi_pixels=int(roi.sum()), registration=reg, knobs=knobs,
               shutter_events=int(len(R["ffc_t"])), bins=int(len(R["t"])), blocks=res)
    dflt = (lambda o: float(o) if isinstance(o, np.floating) else
            (int(o) if isinstance(o, np.integer) else str(o)))
    with open(os.path.join(a.out, "lockin.json"), "w") as f:
        json.dump(out, f, indent=1, default=dflt)
    with open(os.path.join(a.out, "score.json"), "w") as f:
        json.dump(dict(experiment="E85", predictions_sha256=hashlib.sha256(open(a.predictions, "rb").read()).hexdigest(), **sc), f, indent=1, default=dflt)
    lines = summary_lines(res, sc, order)
    with open(os.path.join(a.out, "score.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
