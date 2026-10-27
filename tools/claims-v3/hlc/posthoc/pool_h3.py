#!/usr/bin/env python3
"""E63, post hoc (Q126): pool the two sessions' third-harmonic transfers and rail shares.

    python3 pool_h3.py <s1 h3-rails.json> <s2 h3-rails.json> --out h3-rails-pooled.json

h3_rails_hlc.py reads one session. The camera's gain drifted through the hour (59.0, 52.9, 47.8, 42.4 mK/W
for the four top-rung blocks in time order), so the thing worth pooling is each block's RATIO
H(3f) / H(f), in which the drift divides out, not the transfer itself. Both are pooled here, by inverse
variance over the four top-rung blocks, with the middle rungs and the nulls kept out: the null switches no
watts, and a middle rung's third harmonic is a quarter of a top rung's on the same noise floor.

From the pooled ratio it also reports the time constant a single pole would need to make it, and says
whether the measured lag at f agrees with that pole (a single pole cannot lag more than 90 degrees).

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
            # the error is dominated by the third harmonic's; the fundamental's adds in quadrature
            se = ratio * math.hypot(H3["se_mag"] / H3["mag"], H1["se_mag"] / H1["mag"])
            rows.append(dict(session=si, block=b, H_f=H1["mag"], se_H_f=H1["se_mag"],
                             lag_f_deg=H1["phase_deg"], lag_f_s=H1["lag_s"],
                             H_3f=H3["mag"], se_H_3f=H3["se_mag"], lag_3f_deg=H3["phase_deg"],
                             lag_3f_s=H3["lag_s"], ratio=ratio, se_ratio=se,
                             camera_3f_mk=r["camera"]["third"]["amp"], camera_3f_se=r["camera"]["third"]["se"],
                             board_3f_w=r["electrical"]["board"]["third"]["amp"]))
    H3m, H3se, n = wmean([r["H_3f"] for r in rows], [r["se_H_3f"] for r in rows])
    H1m, H1se, _ = wmean([r["H_f"] for r in rows], [r["se_H_f"] for r in rows])
    rm, rse, _ = wmean([r["ratio"] for r in rows], [r["se_ratio"] for r in rows])
    f = rows[0]["H_f"] and None
    f_hz = 0.05
    pole = None
    if rm and 0 < rm < 1:
        # |H(3f)|/|H(f)| for one pole: sqrt((1 + x^2) / (1 + 9 x^2)), x = 2 pi f tau
        k = rm ** 2
        den = 9 * k - 1
        if den > 0:
            x2 = (1 - k) / den
            if x2 > 0:
                x = math.sqrt(x2)
                pole = dict(tau_s=x / (2 * math.pi * f_hz), lag_f_deg=math.degrees(math.atan(x)),
                            lag_3f_deg=math.degrees(math.atan(3 * x)))
    lag_mean = sum(r["lag_f_deg"] for r in rows) / len(rows)
    out = dict(experiment="E63", post_hoc=True, request="Q126", f_hz=f_hz, f3_hz=3 * f_hz,
               blocks_pooled=[f"s{r['session']} {r['block']}" for r in rows], n=n, rows=rows,
               pooled=dict(H_f_mk_per_w=H1m, se_H_f=H1se, H_3f_mk_per_w=H3m, se_H_3f=H3se,
                           ratio_3f_over_f=rm, se_ratio=rse, mean_lag_f_deg=lag_mean),
               one_pole=pole,
               one_pole_note=("the measured lag at f is larger than a single pole can give (90 degrees is its "
                              "limit), so this tau only sets the scale of the roll-off"
                              if lag_mean > 90 else "the measured lag at f is within a single pole's range"))
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    for r in rows:
        print(f"s{r['session']} {r['block']:9s}: H(f) {r['H_f']:5.1f} ± {r['se_H_f']:4.1f} at "
              f"{r['lag_f_deg']:4.0f}°, H(3f) {r['H_3f']:5.1f} ± {r['se_H_3f']:4.1f} at {r['lag_3f_deg']:4.0f}°; "
              f"ratio {r['ratio']:.2f} ± {r['se_ratio']:.2f}  (camera at 3f {r['camera_3f_mk']:5.1f} ± "
              f"{r['camera_3f_se']:4.1f} mK on {r['board_3f_w']:.3f} W)")
    print(f"pooled over {n} top-rung blocks: H(f) {H1m:.1f} ± {H1se:.1f}, H(3f) {H3m:.1f} ± {H3se:.1f} mK/W, "
          f"ratio {rm:.2f} ± {rse:.2f}")
    if pole:
        print(f"one pole that would give that ratio: tau {pole['tau_s']:.1f} s "
              f"(its lag at f would be {pole['lag_f_deg']:.0f}°, measured {lag_mean:.0f}°)")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
