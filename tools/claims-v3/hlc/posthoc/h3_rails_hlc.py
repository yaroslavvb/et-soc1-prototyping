#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E63, post hoc (Q126, Mon 26 Oct 2026): the drive's third harmonic as a second transfer point, and the
card's own rails demodulated beside the board.

    python3 h3_rails_hlc.py RED --template <e62_bloom_dt.npy> [--scene-ref <e62_scene.npy>]
                            --protocol <protocol.json> --out h3-rails.json

NOT pre-registered and carrying no verdict: E63's five decision rules were frozen on 23 October and are
untouched by anything here (tools/claims-v3/hlc/README.md). This re-reads two things the registered run
computed and threw away, and one it never looked at.

1. **The third harmonic.** `lockin_hlc.design` carries `sin 3phi` and `-cos 3phi` as shared nuisance columns,
   so the square drive's third harmonic cannot leak into the fundamental; `analyse_block` then discards their
   coefficients. The drive switches on a 20 s grid, so the third harmonic is **0.15 Hz**. Reading the camera's
   and the board's third harmonics out of the same fit gives a second transfer point, H3 = Z3_roi / Z3_power in
   mK per watt, on exactly the data the 0.05 Hz point comes from. A square wave's own third harmonic is a third
   of its fundamental and in phase with it, so the drive's shape cancels in the ratio.
   Phase convention: the columns are sin(3 phi) and -cos(3 phi) with phi the FUNDAMENTAL's phase, so a
   component A sin(3 phi - psi) reads as A (cos psi, sin psi) and psi is the lag in degrees of the
   third-harmonic cycle (6.667 s), one third of the fundamental's 20 s. The lag is also given in seconds,
   which is what compares with the 0.05 Hz lag.
   Errors are jackknifed over laps (leave one lap out, refit everything), as the registered fundamental's are,
   not taken from the design: the camera's noise is not white and a design SE would be optimistic.
   H(3f) is written out as a complex number as well as a magnitude, and the ratio |H(3f)|/|H(f)| gets its
   own single jackknife, each left-out lap dropped from both harmonics at once. Both were added on the
   second pass (Mon 26 Oct 2026, after review): a magnitude whose cloud is a sizeable fraction of itself
   cannot be averaged across blocks (E|Z| > |E Z|), and combining the two harmonics' separate SEs in
   quadrature treats as independent two coefficients of the same fit that share the camera's gain.

2. **The rails.** The 10 Hz sampler logs the card's own minion, SRAM and NoC rail watts (`sp.minion_w`,
   `sp.sram_w`, `sp.noc_w`, each [avg, min, max]) in every run, beside the board input watts the experiment
   used. Each rail goes through the power's own lap model (one stretch, the same spline and harmonics), and
   through the step the board step is measured with (the median in 2.0..end-0.3 s of arm A's launch minus arm
   B's), giving each rail's share of the board step.

numpy only, python 3.12: it runs on the lab host, where the RED cubes are.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import lockin_hlc as L  # noqa: E402

RAILS = ("minion", "sram", "noc")


# --------------------------------------------------------------------------------- the rails from tel.jsonl

def tel_rails(red):
    """(host epoch s, board W, minion W, SRAM W, NoC W) from the runner's tel.jsonl. The sampler writes each
    rail as [avg, min, max] over the sampling window; the average is the one used, as `board_avg_w` is for the
    board. A line missing a rail is dropped from that rail, not from the row (NaN)."""
    path = os.path.join(red, "tel.jsonl")
    if not os.path.exists(path):
        path += ".gz"
    rows = []
    for r in L.read_jsonl(path):
        line = r.get("line", r)
        if isinstance(line, str):
            try:
                line = json.loads(line)
            except ValueError:
                continue
        try:
            t = float(line.get("t_ms", r.get("host_ms"))) / 1000.0
            bw = float(line["board_w"])
        except (TypeError, ValueError, KeyError):
            continue
        sp = line.get("sp") or {}
        vals = []
        for rail in RAILS:
            v = sp.get(f"{rail}_w")
            try:
                vals.append(float(v[0] if isinstance(v, list) else v))
            except (TypeError, ValueError, IndexError):
                vals.append(np.nan)
        rows.append((t, bw, *vals))
    return np.array(sorted(rows), dtype=np.float64) if rows else np.zeros((0, 2 + len(RAILS)))


def binned(R, tel, col, t_bins):
    """One telemetry column averaged into the RED's 0.5 s bins (host clock), as power_series does."""
    half = 0.5 * float(R["meta"].get("bin_s", 0.5))
    ts = tel[:, 0] - R["t0_ms"] / 1000.0
    v = tel[:, col]
    ok0 = np.isfinite(v)
    edges = np.concatenate([t_bins - half, [t_bins[-1] + half]])
    k = np.searchsorted(edges, ts, side="right") - 1
    ok = ok0 & (k >= 0) & (k < len(t_bins))
    s = np.bincount(k[ok], weights=v[ok], minlength=len(t_bins))
    c = np.bincount(k[ok], minlength=len(t_bins))
    with np.errstate(invalid="ignore"):
        return s / np.where(c > 0, c, np.nan)


def rail_steps(R, tel, col, block, laps_ok):
    """One column's step per analysed lap, in the windows steady_steps uses for the board."""
    ts = tel[:, 0]
    by = {}
    for Lr in R["launches"]:
        if Lr.get("block") == block:
            by.setdefault(int(Lr["cycle"]), {})[int(Lr["phase"])] = Lr
    out = []
    for (c, *_rest) in laps_ok:
        arms = by.get(c, {})
        vals = []
        for ph in (0, 1):
            Lr = arms.get(ph)
            if not Lr:
                vals.append(np.nan)
                continue
            a = Lr["t_start_ms"] / 1000.0 + L.STEADY_FROM_S
            b = Lr["t_end_ms"] / 1000.0 - L.STEADY_TO_END_S
            m = (ts >= a) & (ts <= b) & np.isfinite(tel[:, col])
            vals.append(float(np.median(tel[m, col])) if m.any() else np.nan)
        out.append(vals[0] - vals[1])
    return np.array(out)


# --------------------------------------------------------------------------------- fundamental and harmonic

def _h3_of(X, seg, y, nl, demean_only):
    """The shared third-harmonic coefficient of one series under the block's design.
    demean_only: the power and the rails have no shutter, so their design is demeaned, not within-stretch."""
    if demean_only:
        Xd, yd = X - X.mean(axis=0), y - y.mean()
    else:
        Xd, yd = L.within(X, seg), L.within(y, seg)
    nst = 1 if demean_only else len(np.unique(seg))
    _z, _v, _sig, coef = L.fit(Xd, yd[:, None], nl, nst)
    i3 = 2 * nl
    return complex(float(coef[i3, 0]), float(coef[i3 + 1, 0]))


def harmonic_block(t, lapj, phi, seg, y, nl, demean_only):
    """Z3 of one series, with a leave-one-lap-out jackknife SE.

    Returns the summary, the replicate array, and the lap index each replicate leaves out, so a ratio
    taken against another series can be jackknifed lap by lap on the same left-out laps."""
    X, _ = L.design(t, lapj, phi, nl, harm3=True)
    Z3 = _h3_of(X, seg, y, nl, demean_only)
    js, ks = [], []
    for k in range(nl):
        m = lapj != k
        if m.sum() < 50:
            continue
        lj = lapj[m].copy()
        lj[lj > k] -= 1
        Xk, _ = L.design(t[m], lj, phi[m], nl - 1, harm3=True)
        js.append(_h3_of(Xk, seg[m], y[m], nl - 1, demean_only))
        ks.append(k)
    js = np.array(js)
    n = len(js)
    se = float(np.sqrt((n - 1) / n * (np.abs(js - js.mean()) ** 2).sum())) if n >= 3 else None
    return dict(Z3_re=Z3.real, Z3_im=Z3.imag, amp=abs(Z3), phase_deg=math.degrees(np.angle(Z3)),
                se=se, n_jack=n), js, np.array(ks, int)


def ratio_jack(num, num_js, den, den_js):
    """H = num/den with a leave-one-lap-out SE, as lockin_hlc.jackknife_ratio does for the fundamental.

    `se` is the SE of the complex H (the length of the jackknife cloud); `se_mag` is the SE of |H|, which
    is what a magnitude is quoted with. Both are kept because they answer different questions, and the
    complex one is what a pooled value must be built from: |mean of H| is not mean of |H| when the cloud
    is a sizeable fraction of H, which it is here."""
    if den == 0 or len(num_js) != len(den_js) or len(num_js) < 3:
        return None
    H = num / den
    hs = num_js / den_js
    n = len(hs)
    se = float(np.sqrt((n - 1) / n * (np.abs(hs - hs.mean()) ** 2).sum()))
    se_mag = float(np.sqrt((n - 1) / n * ((np.abs(hs) - np.abs(hs).mean()) ** 2).sum()))
    se_ph = float(np.sqrt((n - 1) / n * (np.angle(hs * np.conj(H)) ** 2).sum()))
    return dict(H_re=float(H.real), H_im=float(H.imag),
                mag=abs(H), phase_deg=math.degrees(np.angle(H)), se=se, se_mag=se_mag,
                se_phase_deg=math.degrees(se_ph), n_laps=n)


def _h1_replicates(z, wz, p, wp):
    """The per-lap leave-one-out replicates of lockin_hlc.jackknife_ratio's H = <z>/<p>, with the lap
    index each one leaves out. The registered script computes the same cloud and reports only its width;
    the replicates are needed here to jackknife |H(3f)|/|H(f)| on the same left-out laps."""
    ok = np.isfinite(z) & np.isfinite(p) & (wz > 0) & (wp > 0)
    idx = np.nonzero(ok)[0]
    z, wz, p, wp = z[ok], wz[ok], p[ok], wp[ok]
    n = len(z)
    if n < 3:
        return np.array([]), np.array([], int)
    hs = np.array([((np.delete(wz, k) * np.delete(z, k)).sum() / np.delete(wz, k).sum())
                   / ((np.delete(wp, k) * np.delete(p, k)).sum() / np.delete(wp, k).sum())
                   for k in range(n)])
    return hs, idx


def ratio_of_mags_jack(h3, h3_js, h3_ks, h1, h1_js, h1_ks):
    """|H(3f)| / |H(f)| with ONE leave-one-lap-out jackknife over the laps both clouds share.

    The quadrature of the two magnitudes' relative SEs is not the right error here: H(3f) and H(f) are two
    coefficients of the SAME fit on the SAME frames, and the camera's gain, which is the ratio's whole
    reason for existing, is common to both and cancels. Dropping a lap drops it from both, so this is the
    error of the quantity actually quoted."""
    common = sorted(set(h3_ks.tolist()) & set(h1_ks.tolist()))
    if len(common) < 3 or abs(h1) == 0:
        return None
    i3 = {k: i for i, k in enumerate(h3_ks.tolist())}
    i1 = {k: i for i, k in enumerate(h1_ks.tolist())}
    rs = np.array([abs(h3_js[i3[k]]) / abs(h1_js[i1[k]]) for k in common])
    n = len(rs)
    r = abs(h3) / abs(h1)
    se = float(np.sqrt((n - 1) / n * ((rs - rs.mean()) ** 2).sum()))
    # no jackknife bias correction is reported: n*r - (n-1)*mean(rs) is unstable for a ratio whose
    # numerator sits near 1 SE (it reads 0.04 against 0.30 on the first block), so it would be a
    # number nothing uses and a reader could quote.
    return dict(ratio=float(r), se=se, n_laps=n, jack_mean=float(rs.mean()))


# --------------------------------------------------------------------------------- one block

def do_block(R, tel, block, roi, rng):
    laps = L.block_laps(R, block)
    okl = [x for x in laps if x[3]]
    nl = len(okl)
    out = dict(block=block, laps=nl)
    if nl < 3:
        out["error"] = "too few laps"
        return out
    lap_s = float(np.mean([x[2] - x[1] for x in okl]))
    out["lap_s"] = lap_s
    out["f_hz"] = 1.0 / lap_s
    out["f3_hz"] = 3.0 / lap_s

    # the camera: the registered bin selection, the ROI mean, free offset per stretch
    idx, lapj, phi, seg = L.select_bins(R, laps)
    if len(idx) < 50:
        out["error"] = "too few bins"
        return out
    t = R["t"][idx]
    yroi = R["mk"][idx][:, roi].mean(axis=1).astype(np.float64)
    cam, cam_js, cam_ks = harmonic_block(t, lapj, phi, seg, yroi, nl, demean_only=False)

    # the electrical series, each on the RED's bins inside the analysed laps, one stretch
    sel = np.zeros(len(R["t"]), bool)
    for (_, t0, t1, _ok, _s) in okl:
        sel |= (R["t"] >= t0) & (R["t"] < t1)
    series = {"board": binned(R, tel, 1, R["t"])}
    for i, rail in enumerate(RAILS):
        series[rail] = binned(R, tel, 2 + i, R["t"])
    elec, elec_js, elec_ks = {}, {}, {}
    for name, P in series.items():
        s = sel & np.isfinite(P)
        ip = np.nonzero(s)[0]
        if len(ip) < 50:
            continue
        lp = np.full(len(ip), -1, int)
        pp = np.zeros(len(ip))
        for j, (_, t0, t1, _ok, _s) in enumerate(okl):
            m = (R["t"][ip] >= t0) & (R["t"][ip] < t1)
            lp[m] = j
            pp[m] = 2 * math.pi * (R["t"][ip][m] - t0) / (t1 - t0)
        elec[name], elec_js[name], elec_ks[name] = harmonic_block(R["t"][ip], lp, pp,
                                                                  np.zeros(len(ip), int),
                                                                  P[ip], nl, demean_only=True)
        # the fundamental, through the registered path, for the rails (the board's is in lockin.json)
        Xp, _ = L.design(R["t"][ip], lp, pp, nl, harm3=True)
        Xp = Xp - Xp.mean(axis=0)
        z, v, _sig, _c = L.fit(Xp, (P[ip] - P[ip].mean())[:, None], nl)
        w = np.where(np.isfinite(v) & (v > 0), 1.0 / v, 0.0)
        elec[name]["fundamental"] = L.lap_stats(z[:, 0], w, rng)
        elec[name]["_z1"] = z[:, 0]
        elec[name]["_w"] = w

    # the camera's fundamental, the registered way, for the transfer at f beside the one at 3f
    Xc, _ = L.design(t, lapj, phi, nl, harm3=True)
    Xcw = L.within(Xc, seg)
    zc, vc, _s, _c = L.fit(Xcw, L.within(yroi, seg)[:, None], nl, len(np.unique(seg)))
    wc = np.where(np.isfinite(vc) & (vc > 0), 1.0 / vc, 0.0)
    cam_f = L.lap_stats(zc[:, 0], wc, rng)

    out["camera"] = dict(fundamental=cam_f, third=_clean(cam))
    out["electrical"] = {k: dict(fundamental=v["fundamental"], third=_clean(v)) for k, v in elec.items()}

    # the two transfer points
    zb = complex(elec["board"]["fundamental"]["Z_re"], elec["board"]["fundamental"]["Z_im"])
    H1 = L.jackknife_ratio(zc[:, 0], wc, elec["board"]["_z1"], elec["board"]["_w"])
    H3 = ratio_jack(complex(cam["Z3_re"], cam["Z3_im"]), cam_js,
                    complex(elec["board"]["Z3_re"], elec["board"]["Z3_im"]), elec_js["board"])
    for H, per in ((H1, lap_s), (H3, lap_s / 3.0)):
        if H:
            H["lag_s"] = H["phase_deg"] / 360.0 * per
            H["se_lag_s"] = H["se_phase_deg"] / 360.0 * per
    out["transfer"] = {"f": H1, "3f": H3}
    out["transfer"]["ratio_3f_over_f"] = (H3["mag"] / H1["mag"]) if (H1 and H3) else None
    # the same ratio with its own leave-one-lap-out error, dropping each lap from BOTH harmonics
    out["transfer"]["ratio_jackknifed"] = None
    out["transfer"]["jack_clouds"] = None
    if H1 and H3:
        bk = elec_ks["board"]
        shared = sorted(set(cam_ks.tolist()) & set(bk.tolist()))
        ic = {k: i for i, k in enumerate(cam_ks.tolist())}
        ib = {k: i for i, k in enumerate(bk.tolist())}
        h3_js = np.array([cam_js[ic[k]] / elec_js["board"][ib[k]] for k in shared])
        h3_ks = np.array(shared, int)
        h3c = (complex(cam["Z3_re"], cam["Z3_im"])
               / complex(elec["board"]["Z3_re"], elec["board"]["Z3_im"]))
        h1_js, h1_ks = _h1_replicates(zc[:, 0], wc, elec["board"]["_z1"], elec["board"]["_w"])
        if len(h1_js):
            out["transfer"]["ratio_jackknifed"] = ratio_of_mags_jack(
                h3c, h3_js, h3_ks, complex(H1["H_re"], H1["H_im"]), h1_js, h1_ks)
            # the clouds themselves, so a pool across blocks can take each block's error along whatever
            # direction the pooled transfer points in, instead of assuming the cloud is a circle
            out["transfer"]["jack_clouds"] = dict(
                laps_3f=h3_ks.tolist(), H_3f=[[z.real, z.imag] for z in h3_js],
                laps_f=h1_ks.tolist(), H_f=[[z.real, z.imag] for z in h1_js])

    # the rails' share of the board step, and of its fundamental
    steps = {name: rail_steps(R, tel, col, block, okl)
             for name, col in (("board", 1), *((r, 2 + i) for i, r in enumerate(RAILS)))}
    sb = float(np.nanmean(steps["board"]))
    sh = {}
    for name, v in steps.items():
        n = int(np.isfinite(v).sum())
        sh[name] = dict(step_w=float(np.nanmean(v)),
                        se=float(np.nanstd(v) / math.sqrt(max(1, n))), n=n,
                        share_of_board=(float(np.nanmean(v) / sb) if abs(sb) > 1e-9 else None),
                        fundamental_w=(elec.get(name, {}).get("fundamental", {}) or {}).get("amp"),
                        fundamental_share=((elec[name]["fundamental"]["amp"]
                                            / elec["board"]["fundamental"]["amp"])
                                           if name in elec and elec["board"]["fundamental"].get("amp") else None))
    rail_sum = float(np.nansum([sh[r]["step_w"] for r in RAILS]))
    sh["rails_summed"] = dict(step_w=rail_sum,
                              share_of_board=(rail_sum / sb if abs(sb) > 1e-9 else None),
                              fundamental_w=float(np.nansum([sh[r]["fundamental_w"] or np.nan for r in RAILS])),
                              fundamental_share=(float(np.nansum([sh[r]["fundamental_w"] or np.nan
                                                                  for r in RAILS]))
                                                 / elec["board"]["fundamental"]["amp"]
                                                 if elec["board"]["fundamental"].get("amp") else None))
    out["steps"] = sh
    return out


def _clean(d):
    return {k: v for k, v in d.items() if not k.startswith("_") and k != "fundamental"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("red")
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--template", required=True)
    ap.add_argument("--scene-ref", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=126)
    a = ap.parse_args(argv)
    R = L.load_red(a.red)
    tel = tel_rails(a.red)
    tmpl = np.load(a.template).astype(np.float64)
    reg = None
    if a.scene_ref and os.path.exists(os.path.join(a.red, "scene.npy")):
        dy, dx, pk = L.scene_shift(np.load(a.scene_ref).astype(np.float64),
                                   np.load(os.path.join(a.red, "scene.npy")).astype(np.float64))
        by, bx = int(round(dy / 2.0)), int(round(dx / 2.0))
        moved = max(abs(by), abs(bx)) > 2
        if moved:
            tmpl = np.roll(tmpl, (by, bx), axis=(0, 1))
        reg = dict(shift_full_px=[dy, dx], shift_binned_px=[by, bx], peak_corr=pk, template_moved=moved)
    roi = L.roi_from_template(tmpl)
    with open(a.protocol) as f:
        proto = json.load(f)
    blocks = [b.get("id") or b.get("name") for b in proto["blocks"]]
    rng = np.random.default_rng(a.seed)
    out = dict(experiment=proto.get("experiment"), post_hoc=True, request="Q126",
               note=("not pre-registered, no verdict: the third harmonic of the registered fit, read out as a "
                     "second transfer point, and the card's own rails demodulated beside the board"),
               red=os.path.abspath(a.red), registration=reg, roi_pixels=int(roi.sum()),
               tel_rows=int(len(tel)), blocks={})
    for b in blocks:
        r = do_block(R, tel, b, roi, rng)
        out["blocks"][b] = r
        if "error" in r:
            print(f"{b}: {r['error']}")
            continue
        c3, p3 = r["camera"]["third"], r["electrical"]["board"]["third"]
        H1, H3 = r["transfer"]["f"], r["transfer"]["3f"]
        print(f"{b}: 3f = {r['f3_hz']:.3f} Hz; camera {c3['amp']:.1f} ± {c3['se']:.1f} mK, board "
              f"{p3['amp']:.3f} W; H(f) {H1['mag']:.1f} ± {H1['se_mag']:.1f} mK/W at {H1['phase_deg']:.0f}° "
              f"({H1['lag_s']:.2f} s), H(3f) "
              + (f"{H3['mag']:.1f} ± {H3['se_mag']:.1f} mK/W at {H3['phase_deg']:.0f}° ({H3['lag_s']:.2f} s)"
                 if H3 else "–"))
        rj = r["transfer"].get("ratio_jackknifed")
        if rj:
            print(f"     |H(3f)|/|H(f)| = {rj['ratio']:.3f} ± {rj['se']:.3f} "
                  f"(one jackknife over {rj['n_laps']} laps, both harmonics)")
        s = r["steps"]
        print(f"     step: board {s['board']['step_w']:+.3f} W; minion {s['minion']['step_w']:+.3f} "
              f"({100 * s['minion']['share_of_board']:.1f}%), SRAM {s['sram']['step_w']:+.3f} "
              f"({100 * s['sram']['share_of_board']:.1f}%), NoC {s['noc']['step_w']:+.3f} "
              f"({100 * s['noc']['share_of_board']:.1f}%), three rails "
              f"{100 * s['rails_summed']['share_of_board']:.1f}%")
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, default=lambda o: float(o) if isinstance(o, np.floating) else str(o))
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
