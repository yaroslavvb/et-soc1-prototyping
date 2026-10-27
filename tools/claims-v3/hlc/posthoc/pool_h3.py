#!/usr/bin/env python3
"""E63, post hoc (Q126): pool the two sessions' third-harmonic transfers and rail shares.

    python3 pool_h3.py <s1 h3-rails.json> <s2 h3-rails.json> --out h3-rails-pooled.json

h3_rails_hlc.py reads one session. The camera's gain drifted through the hour (59.0, 52.9, 47.8, 42.4 mK/W
for the four top-rung blocks in time order), so the thing worth pooling is each block's RATIO
H(3f) / H(f), in which the drift divides out, not the transfer itself. Both are pooled here, by inverse
variance over the four top-rung blocks, with the middle rungs and the nulls kept out: the null switches no
watts, and a middle rung's third harmonic is a quarter of a top rung's on the same noise floor.

**Pool the complex transfer, not the magnitude** (the second pass, Mon 26 Oct 2026, after review). Each
block's H(3f) is a complex number whose jackknife cloud is 0.7-1.2 times its own length, and the magnitude
of such a quantity is biased upward: E|Z| > |E Z|, so an inverse-variance mean of four magnitudes sits above
the coherent transfer they share. The headline is now the vector mean, |<H3>|, with the mean of magnitudes
kept beside it and named for what it is -- an upper estimate, and the only one a reader of the first pass
saw. The same two means are given for H(f), where the cloud is small (SNR 14-21) and the two agree to under
a percent, which is the check that the machinery is not inventing the gap at 3f.

The ratio is pooled from each block's OWN jackknife (`transfer.ratio_jackknifed`, one leave-one-lap-out over
both harmonics at once), not from the two magnitudes' SEs combined in quadrature: H(3f) and H(f) are two
coefficients of the same fit on the same frames and share the camera's gain, which is the whole reason the
ratio is the quantity to pool. The quadrature SE is reported too, for comparison with the first pass.

From the pooled ratio it also reports the time constant a single pole would need to make it, whether the
measured lag at f agrees with that pole (a single pole cannot lag more than 90 degrees), and how far the
ratio sits from flat -- a ratio of 1, which is what "the board does not roll off between 0.05 and 0.15 Hz"
would mean.

Standard library only.
"""
import argparse
import cmath
import json
import math

TOPS = ("E63-TOP", "E63-TOP2")


def wmean(vals, ses):
    """Inverse-variance mean of real values and its SE."""
    pairs = [(v, s) for v, s in zip(vals, ses) if v is not None and s not in (None, 0)]
    if not pairs:
        return None, None, 0
    w = [1.0 / s ** 2 for _v, s in pairs]
    W = sum(w)
    return sum(wi * v for wi, (v, _s) in zip(w, pairs)) / W, math.sqrt(1.0 / W), len(pairs)


def wmean_complex(zs, ses, clouds):
    """Inverse-variance mean of complex values, and the SE of ITS MAGNITUDE.

    `se` from ratio_jack / jackknife_ratio is the rms length of the jackknife cloud, the SE of the complex
    quantity in two dimensions, so 1/se^2 is the weight for both components at once. The error on the
    pooled MAGNITUDE is not that: it is the error along the pooled vector's own direction. Each block's
    jackknife cloud is carried here, so that direction's variance is taken from the cloud itself --
    Var(sum w_i Z_i . u) = sum w_i^2 Var_i(Z_i . u) / (sum w_i)^2 -- with no assumption that the cloud is
    a circle. (It is not quite: the camera's phase is worse determined than its amplitude.)"""
    items = [(complex(z[0], z[1]), s, c) for z, s, c in zip(zs, ses, clouds)
             if z is not None and s not in (None, 0)]
    if not items:
        return None, None, None, 0
    w = [1.0 / s ** 2 for _z, s, _c in items]
    W = sum(w)
    m = sum(wi * z for wi, (z, _s, _c) in zip(w, items)) / W
    iso = math.sqrt(1.0 / W)
    if abs(m) == 0 or any(c is None for _z, _s, c in items):
        return m, iso, iso, len(items)
    u = m / abs(m)
    var = 0.0
    for wi, (_z, _s, c) in zip(w, items):
        proj = [(complex(p[0], p[1]) * u.conjugate()).real for p in c]
        n = len(proj)
        mu = sum(proj) / n
        vi = (n - 1) / n * sum((p - mu) ** 2 for p in proj)   # the jackknife variance along u
        var += wi ** 2 * vi
    return m, math.sqrt(var) / W, iso, len(items)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    S = [json.load(open(p)) for p in a.files]
    rows = []
    for si, s in enumerate(S, 1):
        for b in TOPS:
            r = s["blocks"].get(b) or {}
            H1, H3 = r.get("transfer", {}).get("f"), r.get("transfer", {}).get("3f")
            if not H1 or not H3:
                continue
            ratio = H3["mag"] / H1["mag"]
            # the first pass's error on the ratio: the two magnitudes' relative SEs in quadrature. Kept for
            # comparison only; `ratio_jack_se` below is the one this file pools.
            se_quad = ratio * math.hypot(H3["se_mag"] / H3["mag"], H1["se_mag"] / H1["mag"])
            rj = r["transfer"].get("ratio_jackknifed") or {}
            jc = r["transfer"].get("jack_clouds") or {}
            rows.append(dict(session=si, block=b, H_f=H1["mag"], se_H_f=H1["se_mag"],
                             H_f_re=H1["H_re"], H_f_im=H1["H_im"], se_H_f_cplx=H1["se"],
                             lag_f_deg=H1["phase_deg"], lag_f_s=H1["lag_s"],
                             H_3f=H3["mag"], se_H_3f=H3["se_mag"],
                             H_3f_re=H3["H_re"], H_3f_im=H3["H_im"], se_H_3f_cplx=H3["se"],
                             lag_3f_deg=H3["phase_deg"], lag_3f_s=H3["lag_s"],
                             ratio=ratio, se_ratio_quadrature=se_quad,
                             ratio_jack=rj.get("ratio"), se_ratio_jack=rj.get("se"),
                             n_laps_ratio_jack=rj.get("n_laps"),
                             camera_3f_mk=r["camera"]["third"]["amp"], camera_3f_se=r["camera"]["third"]["se"],
                             board_3f_w=r["electrical"]["board"]["third"]["amp"],
                             board_3f_se=r["electrical"]["board"]["third"]["se"],
                             _cloud_3f=jc.get("H_3f"), _cloud_f=jc.get("H_f")))
    # magnitudes (the first pass's route, kept as an upper estimate)
    H3m, H3se, n = wmean([r["H_3f"] for r in rows], [r["se_H_3f"] for r in rows])
    H1m, H1se, _ = wmean([r["H_f"] for r in rows], [r["se_H_f"] for r in rows])
    # the coherent (vector) means -- the headline
    Z3, Z3se, Z3iso, _n = wmean_complex([(r["H_3f_re"], r["H_3f_im"]) for r in rows],
                                        [r["se_H_3f_cplx"] for r in rows],
                                        [r["_cloud_3f"] for r in rows])
    Z1, Z1se, Z1iso, _n1 = wmean_complex([(r["H_f_re"], r["H_f_im"]) for r in rows],
                                         [r["se_H_f_cplx"] for r in rows],
                                         [r["_cloud_f"] for r in rows])
    # the ratio, from each block's own single jackknife
    rm, rse, nr = wmean([r["ratio_jack"] for r in rows], [r["se_ratio_jack"] for r in rows])
    rq, rqse, _ = wmean([r["ratio"] for r in rows], [r["se_ratio_quadrature"] for r in rows])
    f_hz = 0.05

    def one_pole_tau(ratio):
        """The tau of the single pole whose |H(3f)|/|H(f)| = sqrt((1+x^2)/(1+9x^2)) is `ratio`,
        x = 2 pi f tau. None when no pole can make it: the function falls from 1 at tau = 0 to 1/3
        as tau grows, so a ratio at or under 1/3 is off the end of the family."""
        if ratio is None or not 0 < ratio < 1:
            return None
        k = ratio ** 2
        den = 9 * k - 1
        if den <= 0:
            return None
        x2 = (1 - k) / den
        if x2 <= 0:
            return None
        return math.sqrt(x2) / (2 * math.pi * f_hz)

    pole = None
    if rm is not None:
        tau = one_pole_tau(rm)
        tau_hi = one_pole_tau(rm - rse) if rse else None   # a SMALLER ratio means a LONGER tau
        tau_lo = one_pole_tau(rm + rse) if rse else None
        x = 2 * math.pi * f_hz * tau if tau else None
        pole = dict(
            tau_s=tau,
            tau_s_minus_1se=tau_lo, tau_s_plus_1se=tau_hi,
            lag_f_deg=(math.degrees(math.atan(x)) if x else None),
            lag_3f_deg=(math.degrees(math.atan(3 * x)) if x else None),
            asymptote=1.0 / 3.0,
            weakly_determined=bool(tau is None or rm - rse <= 1.0 / 3.0),
            note=("a single pole's ratio bottoms out at 1/3 = 0.3333 as tau grows, and the measured "
                  "ratio sits on that floor, so tau is bounded below and not above: any pole longer "
                  "than the 1-sigma figure fits as well. The tau is a scale, not a fitted time "
                  "constant."))
    lag_mean = sum(r["lag_f_deg"] for r in rows) / len(rows)
    flat = dict(ratio_if_flat=1.0, se_from_flat=((1.0 - rm) / rse if rse else None),
                se_from_zero=(rm / rse if rse else None),
                note=("'flat' is a ratio of 1: the board answering 0.15 Hz as strongly as 0.05 Hz. The "
                      "distance from flat is the statement the roll-off rests on; the distance from zero "
                      "only says the third harmonic was seen at all."))
    out = dict(experiment="E63", post_hoc=True, request="Q126", f_hz=f_hz, f3_hz=3 * f_hz,
               blocks_pooled=[f"s{r['session']} {r['block']}" for r in rows], n=n,
               rows=[{k: v for k, v in r.items() if not k.startswith("_")} for r in rows],
               pooled=dict(
                   # the headline: coherent means
                   H_3f_mk_per_w=(abs(Z3) if Z3 else None), se_H_3f=Z3se,
                   H_3f_phase_deg=(math.degrees(cmath.phase(Z3)) if Z3 else None),
                   H_f_mk_per_w=(abs(Z1) if Z1 else None), se_H_f=Z1se,
                   H_f_phase_deg=(math.degrees(cmath.phase(Z1)) if Z1 else None),
                   pooling=("vector (complex) inverse-variance mean over the four top-rung blocks; the SE "
                            "is along the pooled vector's own direction, taken from each block's "
                            "jackknife cloud projected onto it"),
                   se_H_3f_isotropic=Z3iso, se_H_f_isotropic=Z1iso,
                   isotropic_note=("what the SE would be if each cloud were a circle of the same total "
                                   "width: sqrt(1 / sum 1/se^2). Quoted only to show how much the "
                                   "projection changes it."),
                   # the first pass's route, kept and named
                   H_3f_mean_of_mags=H3m, se_H_3f_mean_of_mags=H3se,
                   H_f_mean_of_mags=H1m, se_H_f_mean_of_mags=H1se,
                   mean_of_mags_note=("an inverse-variance mean of the four magnitudes. Biased upward, "
                                      "because |Z| of a noisy complex quantity averages above the "
                                      "magnitude of its mean; an upper estimate of the coherent transfer, "
                                      "and the number the first pass published."),
                   ratio_3f_over_f=rm, se_ratio=rse, n_ratio=nr,
                   ratio_se_source=("each block's own leave-one-lap-out jackknife of |H(3f)|/|H(f)|, "
                                    "the same lap dropped from both harmonics"),
                   ratio_quadrature=rq, se_ratio_quadrature=rqse,
                   mean_lag_f_deg=lag_mean),
               distance_from_flat=flat,
               one_pole=pole,
               one_pole_note=("the measured lag at f is larger than a single pole can give (90 degrees is its "
                              "limit), so this tau only sets the scale of the roll-off"
                              if lag_mean > 90 else "the measured lag at f is within a single pole's range"))
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    for r in rows:
        rjs = (f"{r['ratio_jack']:.2f} ± {r['se_ratio_jack']:.2f}"
               if r["ratio_jack"] is not None else "–")
        print(f"s{r['session']} {r['block']:9s}: H(f) {r['H_f']:5.1f} ± {r['se_H_f']:4.1f} at "
              f"{r['lag_f_deg']:4.0f}°, H(3f) {r['H_3f']:5.1f} ± {r['se_H_3f']:4.1f} at {r['lag_3f_deg']:4.0f}°; "
              f"ratio {rjs}  (camera at 3f {r['camera_3f_mk']:5.1f} ± "
              f"{r['camera_3f_se']:4.1f} mK on {r['board_3f_w']:.3f} W)")
    print(f"pooled over {n} top-rung blocks, vector mean: H(f) {abs(Z1):.1f} ± {Z1se:.1f} at "
          f"{math.degrees(cmath.phase(Z1)):.0f}°, H(3f) {abs(Z3):.1f} ± {Z3se:.1f} mK/W at "
          f"{math.degrees(cmath.phase(Z3)):.0f}°")
    print(f"   mean of magnitudes, for comparison (upper estimate): H(f) {H1m:.1f} ± {H1se:.1f}, "
          f"H(3f) {H3m:.1f} ± {H3se:.1f} mK/W")
    print(f"   ratio {rm:.3f} ± {rse:.3f} (jackknifed; quadrature {rq:.3f} ± {rqse:.3f}); "
          f"{flat['se_from_flat']:.1f} SE from flat, {flat['se_from_zero']:.1f} SE from zero")
    if pole and pole["tau_s"]:
        hi = ("inf" if pole["tau_s_plus_1se"] is None else f"{pole['tau_s_plus_1se']:.1f}")
        lo = ("–" if pole["tau_s_minus_1se"] is None else f"{pole['tau_s_minus_1se']:.1f}")
        print(f"one pole that would give that ratio: tau {pole['tau_s']:.1f} s "
              f"(1 sigma {lo} to {hi} s; the family bottoms out at 1/3, so the upper end is open) "
              f"— its lag at f would be {pole['lag_f_deg']:.0f}°, measured {lag_mean:.0f}°")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
