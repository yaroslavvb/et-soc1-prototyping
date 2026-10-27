#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E73: E63's registered lock-in, generalised to a half period of more than one launch, plus the odd
harmonics kept instead of thrown away.

    python3 lockin_hlf.py RED --protocol protocol-e73.json --template prereg/e62_bloom_dt.npy \
        --scene-ref prereg/e62_scene.npy [--fpa RED/fpa.npz] --out ANA

**This imports `lockin_hlc` and runs E63's own `analyse_block` verbatim.**  Exactly three of its module
functions are replaced, each because a half period of N launches breaks an assumption that only held for
N = 1, and each replacement reduces to the original when N = 1:

1. `block_laps` - the original marks a lap analysable only when it has exactly 2 phases
   (`len(ps) == 2`).  A lap of 2N phases is now accepted; the lap still runs from its first phase's
   planned start to its last phase's planned end, so `select_bins`' phase `phi` and `analyse_block`'s
   `f_hz` need no change at all.
2. `design` - the drift spline's knot spacing was the constant `KNOT_S = 40 s`, which is 2 laps at
   E63's 20 s lap and would be 0.4 of a lap at E73's 100 s one, where a cubic spline could absorb the
   signal itself.  The knot spacing is now **2 lap periods for every block**, which is E63's own ratio.
   The shared third-harmonic pair also becomes a pair per harmonic in `HARMONICS`.
3. `steady_steps` - the original reads arm A as phase index 0 and arm B as phase index 1.  Arm A is now
   phase indices 0..N-1 and arm B is N..2N-1, and the step is the median over all of arm A's steady
   windows minus the median over all of arm B's.

Everything else - the bin selection, the shutter guard, the free offset per inter-shutter stretch, the
per-lap complex amplitude, the sign-flip permutation p, the lap jackknife of H, the registration against
E62's scene, the ROI from E62's bloom map - is the code E63 froze on 23 October, called, not copied.

**What is new and is the point of E73.**  `harmonics_block` reads the shared odd-harmonic coefficients -
which the registered fit carries as nuisance columns and discards - for the camera ROI and for the board
power out of the same fit, and forms H(k f0) = Z_k(camera) / Z_k(board) in mK per watt.  Because
numerator and denominator come from the same frames and the same fit, the drive's own shape divides out
and the camera's gain cancels in any ratio of two H's.  Errors are jackknifed over laps, as Q126's
`posthoc/h3_rails_hlc.py` established for the 0.15 Hz point: the camera's noise is not white and a
design SE would be optimistic.

A block of lap period T therefore yields transfer points at f0 = 1/T (per-lap route, the registered one)
and at 3, 5, 7, 9 / T (shared route).  E73's three lap periods 20, 40 and 100 s put those on one
0.005 Hz grid, and 0.05 Hz is measured twice over - as the 0.05 Hz blocks' fundamental and as the 0.01 Hz
block's fifth harmonic.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
# in the repo hlc is the sibling directory; in the frozen copy staged on the card host it is a
# subdirectory of the code directory (run_e73.sh stage)
for _cand in (os.path.join(os.path.dirname(HERE), "hlc"), os.path.join(HERE, "hlc")):
    if os.path.exists(os.path.join(_cand, "lockin_hlc.py")):
        sys.path.insert(0, _cand)
        break
import lockin_hlc as L  # noqa: E402

# per-block state the replaced functions read (set by analyse_one before every call)
N_PHASES = 2            # 2 * n_per_arm: the phases one lap of this block has
N_PER_ARM = 1
KNOT_S = 40.0           # the drift spline's knot spacing for this block: 2 lap periods
HARMONICS = (3, 5, 7, 9)
KNOT_LAPS = 2.0         # the registered ratio: E63's 40 s knots over its 20 s lap


# ----------------------------------------------------------------- the three generalised functions

def block_laps(R, block, warmup=True):
    """E63's `block_laps` with `len(ps) == 2` generalised to `len(ps) == N_PHASES`."""
    by = {}
    for p in R["phases"]:
        if p.get("block") == block:
            by.setdefault(int(p["cycle"]), []).append(p)
    laps = []
    for c in sorted(by):
        ps = sorted(by[c], key=lambda p: p.get("slot", p["phase"]))
        t0 = (min(p["planned_start_ms"] for p in ps) - R["t0_ms"]) / 1000.0
        t1 = (max(p["planned_end_ms"] for p in ps) - R["t0_ms"]) / 1000.0
        bad = any(p.get("n_launch_fail") or p.get("n_launch_short") or p.get("stopped")
                  or p.get("truncated") or not p.get("n_launches") for p in ps)
        ok = (not bad) and len(ps) == N_PHASES and (not ps[0].get("warmup") or not warmup)
        laps.append((c, t0, t1, ok, [p["set"] for p in ps]))
    return laps


def design(t, lapj, phi, nlaps, harm3=True, spline=True):
    """E63's `design` with the knot spacing read from KNOT_S and one shared pair per HARMONICS entry.

    Column order is unchanged where it matters: a0, b0, a1, b1, ... per lap, then the harmonic pairs in
    HARMONICS order, then the spline.  So harmonic HARMONICS[i] sits at 2*nlaps + 2*i."""
    cols, names = [], []
    for j in range(nlaps):
        m = (lapj == j).astype(float)
        cols += [m * np.sin(phi), -m * np.cos(phi)]
        names += [f"a{j}", f"b{j}"]
    if harm3:
        for k in HARMONICS:
            cols += [np.sin(k * phi), -np.cos(k * phi)]
            names += [f"a{k}", f"b{k}"]
    X = np.column_stack(cols) if cols else np.zeros((len(t), 0))
    if spline and len(t):
        B = L.bspline_basis(t, float(t.min()), float(t.max()) + 1e-6, knot_s=KNOT_S)[:, 1:]
        X = np.column_stack([X, B])
        names += [f"s{k + 1}" for k in range(B.shape[1])]
    return X, names


def steady_steps(R, tel, block, laps_ok):
    """E63's `steady_steps` with arm A = phase indices 0..N-1 and arm B = N..2N-1."""
    ts = tel[:, 0]
    out, held = [], []
    by = {}
    for Lr in R["launches"]:
        if Lr.get("block") == block:
            by.setdefault(int(Lr["cycle"]), {})[int(Lr["phase"])] = Lr
    n = N_PER_ARM
    for (c, *_rest) in laps_ok:
        arms = by.get(c, {})
        side = []
        for lo, hi in ((0, n), (n, 2 * n)):
            vals, mhz = [], []
            for ph in range(lo, hi):
                Lr = arms.get(ph)
                if not Lr:
                    continue
                a = Lr["t_start_ms"] / 1000.0 + L.STEADY_FROM_S
                b = Lr["t_end_ms"] / 1000.0 - L.STEADY_TO_END_S
                m = (ts >= a) & (ts <= b) & np.isfinite(tel[:, 1])
                if m.any():
                    vals.append(tel[m, 1])
                    mm = tel[m, 3]
                    mhz.append(mm[np.isfinite(mm)])
            side.append((np.concatenate(vals) if vals else np.zeros(0),
                         np.concatenate(mhz) if mhz else np.zeros(0)))
        a_w, a_m = side[0]
        b_w, b_m = side[1]
        out.append(float(np.median(a_w) - np.median(b_w)) if len(a_w) and len(b_w) else np.nan)
        allm = np.concatenate([a_m, b_m])
        held.append(float((allm >= 790).mean()) if len(allm) else np.nan)
    return np.array(out), np.array(held)


# ------------------------------------------------------------------------- the harmonics, kept

def _shared_of(X, seg, y, nl, demean_only, i_harm):
    """The shared coefficient of harmonic HARMONICS[i_harm] for one series under the block's design."""
    if demean_only:
        Xd, yd = X - X.mean(axis=0), y - y.mean()
        nst = 1
    else:
        Xd, yd = L.within(X, seg), L.within(y, seg)
        nst = len(np.unique(seg))
    _z, _v, _sig, coef = L.fit(Xd, yd[:, None], nl, nst)
    i = 2 * nl + 2 * i_harm
    return complex(float(coef[i, 0]), float(coef[i + 1, 0]))


def _fund_of(X, seg, y, nl, demean_only):
    """The inverse-design-variance mean of the per-lap fundamental, the registered fundamental's own form."""
    if demean_only:
        Xd, yd = X - X.mean(axis=0), y - y.mean()
        nst = 0
    else:
        Xd, yd = L.within(X, seg), L.within(y, seg)
        nst = len(np.unique(seg))
    z, v, _sig, _coef = L.fit(Xd, yd[:, None], nl, nst)
    w = np.where(np.isfinite(v) & (v > 0), 1.0 / v, 0.0)
    zz = z[:, 0]
    ok = np.isfinite(zz) & (w > 0)
    return complex((w[ok] * zz[ok]).sum() / w[ok].sum()) if ok.any() else complex(np.nan)


def harmonics_block(t, lapj, phi, seg, ycam, nl, tp, lap_p, phi_p, ypow):
    """Every transfer point of one block: H(k f0) = Z_k(camera) / Z_k(board), k = 1 and HARMONICS.

    One leave-one-lap-out jackknife per k, the same lap dropped from the camera and from the board, so
    the error is the error of the ratio actually quoted (Q126's `ratio_jack`, generalised)."""
    Xc, _ = design(t, lapj, phi, nl, harm3=True)
    Xp, _ = design(tp, lap_p, phi_p, nl, harm3=True)
    ks = [1] + list(HARMONICS)

    def one(Xc_, seg_, yc_, Xp_, yp_, nl_):
        vals = {}
        for j, k in enumerate(ks):
            if k == 1:
                zc = _fund_of(Xc_, seg_, yc_, nl_, False)
                zp = _fund_of(Xp_, None, yp_, nl_, True)
            else:
                zc = _shared_of(Xc_, seg_, yc_, nl_, False, j - 1)
                zp = _shared_of(Xp_, None, yp_, nl_, True, j - 1)
            vals[k] = (zc, zp)
        return vals

    full = one(Xc, seg, ycam, Xp, ypow, nl)
    reps = {k: [] for k in ks}
    for d in range(nl):
        mc = lapj != d
        mp = lap_p != d
        if mc.sum() < 50 or mp.sum() < 20:
            continue
        lc = lapj[mc].copy()
        lc[lc > d] -= 1
        lp = lap_p[mp].copy()
        lp[lp > d] -= 1
        Xck, _ = design(t[mc], lc, phi[mc], nl - 1, harm3=True)
        Xpk, _ = design(tp[mp], lp, phi_p[mp], nl - 1, harm3=True)
        v = one(Xck, seg[mc], ycam[mc], Xpk, ypow[mp], nl - 1)
        for k in ks:
            reps[k].append(v[k])
    out = {}
    for k in ks:
        zc, zp = full[k]
        rr = reps[k]
        row = dict(k=k, cam_mk=abs(zc), cam_phase_deg=math.degrees(np.angle(zc)),
                   board_w=abs(zp), board_phase_deg=math.degrees(np.angle(zp)),
                   cam_re=zc.real, cam_im=zc.imag, board_re=zp.real, board_im=zp.imag,
                   n_jack=len(rr))
        if len(rr) >= 3 and abs(zp) > 0:
            H = zc / zp
            hs = np.array([a / b for a, b in rr if abs(b) > 0])
            cs = np.array([a for a, b in rr])
            ps = np.array([b for a, b in rr])
            n = len(hs)
            row.update(H_re=float(H.real), H_im=float(H.imag), H_mag=float(abs(H)),
                       H_phase_deg=math.degrees(np.angle(H)),
                       se_H=float(np.sqrt((n - 1) / n * (np.abs(hs - hs.mean()) ** 2).sum())),
                       se_H_mag=float(np.sqrt((n - 1) / n *
                                              ((np.abs(hs) - np.abs(hs).mean()) ** 2).sum())),
                       se_H_phase_deg=math.degrees(
                           float(np.sqrt((n - 1) / n * (np.angle(hs * np.conj(H)) ** 2).sum()))),
                       se_cam_mk=float(np.sqrt((len(cs) - 1) / len(cs) *
                                               (np.abs(cs - cs.mean()) ** 2).sum())),
                       se_board_w=float(np.sqrt((len(ps) - 1) / len(ps) *
                                                (np.abs(ps - ps.mean()) ** 2).sum())),
                       n_laps=n)
        out[str(k)] = row
    return out


# ------------------------------------------------------------------------------------------ one block

def analyse_one(R, tel, bspec, roi, tmpl, rng, fpa):
    """One block: E63's analyse_block through the patched functions, then the harmonics."""
    global N_PHASES, N_PER_ARM, KNOT_S
    bid = bspec.get("id") or bspec.get("name")
    N_PER_ARM = int(bspec.get("n_per_arm") or 1)
    N_PHASES = 2 * N_PER_ARM
    lap_s = float(bspec.get("lap_s") or (N_PHASES * 10.0))
    KNOT_S = KNOT_LAPS * lap_s
    r, maps = L.analyse_block(R, tel, bid, roi, tmpl, rng, fpa=fpa)
    r["n_per_arm"] = N_PER_ARM
    r["lap_s_planned"] = lap_s
    r["knot_s"] = KNOT_S
    r["harmonics"] = list(HARMONICS)
    if "error" in r:
        return r, maps
    # the same bins and laps the registered fit used, for the harmonics
    laps = block_laps(R, bid)
    okl = [x for x in laps if x[3]]
    nl = len(okl)
    idx, lapj, phi, seg = L.select_bins(R, laps)
    ycam = R["mk"][idx].astype(np.float64)[:, roi].mean(axis=1)
    P, _cnt = L.power_series(R, tel, R["t"])
    sel = np.zeros(len(R["t"]), bool)
    for (_c, t0, t1, _ok, _s) in okl:
        sel |= (R["t"] >= t0) & (R["t"] < t1)
    sel &= np.isfinite(P)
    ip = np.nonzero(sel)[0]
    lap_p = np.full(len(ip), -1, int)
    phi_p = np.zeros(len(ip))
    for j, (_c, t0, t1, _ok, _s) in enumerate(okl):
        m = (R["t"][ip] >= t0) & (R["t"][ip] < t1)
        lap_p[m] = j
        phi_p[m] = 2 * math.pi * (R["t"][ip][m] - t0) / (t1 - t0)
    r["transfer"] = harmonics_block(R["t"][idx], lapj, phi, seg, ycam, nl,
                                    R["t"][ip], lap_p, phi_p, P[ip])
    r["span_s"] = [float(okl[0][1]), float(okl[-1][2])]
    r["t_mid_s"] = 0.5 * (r["span_s"][0] + r["span_s"][1])
    f0 = 1.0 / float(np.mean([x[2] - x[1] for x in okl]))
    for k, row in r["transfer"].items():
        row["f_hz"] = f0 * int(k)
    return r, maps


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("red")
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--template", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fpa", default=None)
    ap.add_argument("--scene-ref", default=None)
    ap.add_argument("--blocks", nargs="+", default=None)
    ap.add_argument("--harmonics", default="3,5,7,9")
    ap.add_argument("--knot-laps", type=float, default=2.0)
    ap.add_argument("--seed", type=int, default=73)
    a = ap.parse_args(argv)
    global HARMONICS, KNOT_LAPS
    HARMONICS = tuple(int(x) for x in a.harmonics.split(",") if x.strip())
    KNOT_LAPS = a.knot_laps

    # the three replacements, installed into the registered module
    L.block_laps = block_laps
    L.design = design
    L.steady_steps = steady_steps

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
        reg = dict(shift_full_px=[dy, dx], shift_binned_px=[by, bx], peak_corr=pk,
                   template_moved=moved)
        print(f"camera view vs E62: moved ({dy}, {dx}) full-res px, peak corr {pk:.2f}; "
              f"template {'shifted' if moved else 'kept'}")
    roi = L.roi_from_template(tmpl)
    fpa = dict(np.load(a.fpa)) if a.fpa else None
    with open(a.protocol) as f:
        proto = json.load(f)
    want = a.blocks or [b.get("id") or b.get("name") for b in proto["blocks"]]
    specs = {(b.get("id") or b.get("name")): b for b in proto["blocks"]}
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    res = {}
    for bid in want:
        r, maps = analyse_one(R, tel, specs[bid], roi, tmpl, rng, fpa)
        res[bid] = r
        if maps is not None:
            np.savez_compressed(os.path.join(a.out, f"{bid}-maps.npz"), roi=roi, **maps)
        rr = r.get("roi", {})
        tr = (r.get("transfer") or {}).get("1", {})
        print(f"{bid}: N={r['n_per_arm']} f={1.0/r['lap_s_planned']:.4f} Hz "
              f"laps {r['laps_analysed']}/{r['laps_total']} bins {r['bins_kept']}/{r['bins_in_laps']} "
              f"stretches {r['stretches']}; ROI {rr.get('amp', float('nan')):.1f} "
              f"+- {rr.get('se_along', float('nan')):.1f} mK p={rr.get('p_signflip', float('nan')):.3g} "
              f"ph {rr.get('phase_deg', float('nan')):.0f} deg; board "
              f"{r.get('power', {}).get('amp', float('nan')):.3f} W; step "
              f"{r.get('board_step_w', {}).get('mean', float('nan')):.3f} W; "
              f"H(f0) {tr.get('H_mag', float('nan')):.1f} +- {tr.get('se_H_mag', float('nan')):.1f} "
              f"mK/W at {tr.get('H_phase_deg', float('nan')):.0f} deg")
    out = dict(experiment=proto.get("experiment"), request=proto.get("request"),
               red=os.path.abspath(a.red), template=os.path.abspath(a.template),
               roi_pixels=int(roi.sum()), registration=reg,
               knobs=dict(guard_pre_s=L.GUARD_PRE_S, guard_post_s=L.GUARD_POST_S,
                          min_stretch_bins=L.MIN_STRETCH_BINS, min_n_frac=L.MIN_N_FRAC,
                          knot_laps=KNOT_LAPS, harmonics=list(HARMONICS), n_perm=L.N_PERM,
                          roi_quantile=L.ROI_QUANTILE, seed=a.seed,
                          patched=["block_laps", "design", "steady_steps"]),
               blocks=res)
    with open(os.path.join(a.out, "lockin.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
        f.write("\n")
    print("wrote", os.path.join(a.out, "lockin.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
