#!/usr/bin/env python3
"""E73 post hoc (Wed 28 Oct 2026, week 44): the registered fits re-run with the PER-COMPONENT error.

Why this file exists.  `lockin_hlf.py` reports `se_H` as the TOTAL complex jackknife SE of a transfer
point: se_H^2 = var(Re) + var(Im).  The frozen `fit_hlf.py` then weights a 2-component residual
|H - G s|^2 by 1/se_H^2 while counting dof = 2n - npar - 1.  Those two conventions do not match: with
an isotropic error the per-component sigma is se_H/sqrt(2), so the frozen chi2 is HALF the proper
chi2.  Every chi2/dof, reduced chi2, delta chi2 = 1 interval and dAIC the frozen script prints is
therefore off by a factor ~2 (intervals ~sqrt(2) too wide, dAIC half).  Found by the Q129 verifier,
Wed 28 Oct 2026.

This script changes nothing frozen.  It reads the committed `analysis/fit.json`, feeds the SAME
points, the same drift correction, the same conjugation and the same shapes to the same fitting
machinery with sigma = se_corr/sqrt(2), and writes the corrected table.  The registered verdicts
(R1-R6) do not depend on it: none of the six rules uses a model chi2.  The DIRECTION of every
conclusion survives and the one-pole exclusion gets stronger.

  python3 fit_sigma.py <ANA/fit.json> --out posthoc/sigma-corrected.json
  python3 fit_sigma.py <ANA/fit.json> --out posthoc/sigma-corrected.json \
      --predictions tools/claims-v3/hlf/predictions.json \
      --pooled docs/reports/data/2026-10-23-e63-camera-hamming-ladder/posthoc/h3-rails-pooled.json
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import fit_hlf as FH        # noqa: E402
import fit_priors as FP     # noqa: E402

MODELS = ("P1", "P1D", "P2", "P2D")
SQRT2 = math.sqrt(2.0)


def model_point(name, p, g, f):
    """The fitted family at one frequency, back in the lock-in's LAG convention."""
    s = FH.shape(name, np.array([f]), p)[0]
    return g * abs(s), -math.degrees(np.angle(s)), abs(s)


def gain_profile_exact(name, f, H, sig, chi2_min, p_best, span=6.0):
    """The delta chi2 = 1 interval of the zero-frequency gain, the shape profiled out exactly.

    For fixed shape parameters p the chi2 is an exact parabola in the gain,
    chi2(p, g) = c(p) + den(p) * (g - ghat(p))^2 with den = sum(w |s|^2) and ghat the closed-form
    gain fit_hlf.py already uses.  So the gains allowed at delta chi2 = 1 are the union over p of
    ghat(p) +- sqrt((chi2_min + 1 - c(p)) / den(p)), which this evaluates on a fine log grid around
    the best fit instead of stepping the gain and re-gridding the shape (what fit_priors.profile_gain
    does, whose step and grid make the interval granular once the chi2 is the proper one).
    """
    k = FH.NPAR[name]
    n = 90 if k <= 2 else 45
    axes = [np.exp(np.linspace(math.log(p / span), math.log(p * span), n)) for p in p_best]
    mesh = np.meshgrid(*axes, indexing="ij")
    flat = [m.ravel() for m in mesh]
    wt = 1.0 / np.asarray(sig, dtype=np.float64) ** 2
    lo, hi = None, None
    for i in range(len(flat[0])):
        p = [float(x[i]) for x in flat]
        s = FH.shape(name, f, p)
        den = float(np.sum(wt * np.abs(s) ** 2))
        if den <= 0:
            continue
        gh = float(np.sum(wt * np.real(np.conj(s) * H))) / den
        c = float(np.sum(wt * np.abs(H - gh * s) ** 2))
        slack = chi2_min + 1.0 - c
        if slack < 0:
            continue
        half = math.sqrt(slack / den)
        a, b = gh - half, gh + half
        lo = a if lo is None else min(lo, a)
        hi = b if hi is None else max(hi, b)
    return [lo, hi]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fit_json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--predictions")
    ap.add_argument("--pooled")
    a = ap.parse_args()

    F = json.load(open(a.fit_json))

    f73, H73, s_tot, lab, pts = [], [], [], [], []
    for r in F["points"]:
        if not r["included"]:
            continue
        f73.append(r["f_hz"])
        H73.append(complex(r["H_re_corr"], r["H_im_corr"]).conjugate())
        s_tot.append(max(r.get("se_corr") or r["se_cplx"], 1e-9))
        lab.append("%s k%d" % (r["block"], r["k"]))
        pts.append(r)
    f = np.array(f73)
    H = np.array(H73)
    sig_total = np.array(s_tot)
    sig = sig_total / SQRT2            # the per-component error, the whole of the correction
    grp = dict(name="E73", f=f, H=H, sig=sig, labels=lab)

    rl = F["reference_line"]
    out = dict(
        experiment="E73", request="Q129", post_hoc=True, verdict=None,
        written="Wed 28 Oct 2026 (week 44)",
        what="the registered fits re-run with sigma = se_H/sqrt(2), the per-component error",
        why=("lockin_hlf.py's se_H is the TOTAL complex jackknife SE (var_re + var_im) while "
             "fit_hlf.py weights a two-component residual by 1/se_H^2 and counts dof = 2n - npar - 1; "
             "the frozen chi2 is therefore half the proper chi2 and every interval is ~sqrt(2) too "
             "wide and every dAIC half. Found by the Q129 verifier, Wed 28 Oct 2026."),
        registered_fit=os.path.basename(a.fit_json),
        rules_affected="none: R1-R6 are scored on the lock-in's own SEs, not on a model chi2",
        n_points=len(f73), points=lab,
        sigma_convention=dict(frozen="se_corr (total complex)", corrected="se_corr / sqrt(2)",
                              dof="2*n_points - npar - 1 (unchanged)"),
        fits={}, frozen_fits={}, delta_aic={}, frozen_delta_aic={})

    for nm in MODELS:
        fr = FH.grid_fit(nm, f, H, sig, n=36, rounds=6)
        fr["param_names"] = {"P1": ["tau_s"], "P1D": ["tau_s", "delay_s"],
                             "P2": ["tau1_s", "tau2_s"],
                             "P2D": ["tau1_s", "tau2_s", "delay_s"]}[nm]
        fr["param_ci68"] = [FH.profile_se(nm, f, H, sig, fr["params"], j, fr["chi2"])
                            for j in range(FH.NPAR[nm])]
        fr["group_delay_s"] = FP.group_delay(nm, fr["params"])
        fr["group_delay_ci68"] = FP.profile_group_delay(nm, [grp], fr["params"], fr["chi2"])
        fr["dc_gain_ci68"] = gain_profile_exact(nm, f, H, sig, fr["chi2"], fr["params"])
        fr["dc_gain_ci68_method"] = ("the gain's dchi2 = 1 interval with the shape profiled out "
                                     "exactly (gain_profile_exact), not fit_priors' stepped grid")
        fr["dc_gain_mk_per_w"] = fr["gain"]
        # residuals: the complex norm (null expectation sqrt(2)) AND the lag deviation alone
        res = []
        for i, r in enumerate(pts):
            mg, lag, att = model_point(nm, fr["params"], fr["gain"], r["f_hz"])
            res.append(dict(
                point=lab[i], f_hz=r["f_hz"],
                resid_sigma_cplx=float(abs(H[i] - fr["gain"]
                                           * FH.shape(nm, f[i], fr["params"])) / sig[i]),
                model_mag_mk_per_w=mg, model_lag_deg=lag,
                data_lag_deg=r["phase_deg"], se_lag_deg=r["se_phase_deg"],
                lag_dev_se=((r["phase_deg"] - lag) / r["se_phase_deg"]
                            if r.get("se_phase_deg") else None),
                data_mag_mk_per_w=r["mag_corr"], se_mag_mk_per_w=r.get("se_corr")))
        fr["residuals"] = res
        fr["resid_note"] = ("resid_sigma_cplx is the two-component norm, whose null expectation is "
                            "sqrt(2) = 1.41, not 1; lag_dev_se is the lag alone against that "
                            "point's own phase SE and is NOT wrapped to +-180 deg, so it is "
                            "meaningless where the measured phase has wrapped (the two 0.15 Hz "
                            "REF k3 points)")
        out["fits"][nm] = fr
        rf = F["fits"][nm]
        out["frozen_fits"][nm] = dict(params=rf["params"], gain=rf["gain"], chi2=rf["chi2"],
                                      dof=rf["dof"], chi2_red=rf["chi2_red"], aic=rf["aic"],
                                      param_ci68=rf["param_ci68"],
                                      group_delay_s=rf["group_delay_s"],
                                      # the same exact gain profile under the FROZEN (total) sigma,
                                      # so the published [205, 307] can be checked like for like
                                      dc_gain_ci68_exact=gain_profile_exact(
                                          nm, f, H, sig_total, rf["chi2"], rf["params"]))

    best = min(out["fits"], key=lambda k: out["fits"][k]["aic"])
    out["preferred"] = best
    for nm in MODELS:
        out["delta_aic"][nm] = out["fits"][nm]["aic"] - out["fits"][best]["aic"]
        out["frozen_delta_aic"][nm] = F["fits"][nm]["aic"] - F["fits"][F["preferred"]]["aic"]
    out["delta_chi2_P1_over_P1D"] = out["fits"]["P1"]["chi2"] - out["fits"]["P1D"]["chi2"]

    # ---------------------------------------------- where the preferred family sits at 0.05 Hz
    bp = out["fits"][best]
    mg, lag, att = model_point(best, bp["params"], bp["gain"], 0.05)
    out["at_0p05_hz"] = dict(
        model=best, attenuation=att, model_mag_mk_per_w=mg, model_lag_deg=lag,
        reference_line_mk_per_w=rl["mag_at_mid"], se_reference_line=rl["se_mag_at_mid"],
        undershoot_line_se=(rl["mag_at_mid"] - mg) / rl["se_mag_at_mid"],
        undershoot_frac=(rl["mag_at_mid"] - mg) / rl["mag_at_mid"],
        g0_implied_by_the_line=rl["mag_at_mid"] / att,
        note=("the fitted family's own 0.05 Hz value is BELOW the measured reference line: either "
              "quote G0 with that undershoot stated, or quote the steady gain the measured line "
              "implies under the fitted shape (line / attenuation). The two are not the same number "
              "and the coda must say which it means."))
    out["step_response"] = dict(
        t63_s=bp["group_delay_s"] if best == "P1" else None,
        t63_s_shape=bp["params"][0] + (bp["params"][1] if best in ("P1D",) else 0.0),
        t95_s_approx=3.0 * bp["params"][0] + (bp["params"][1] if best == "P1D" else 0.0))

    # ---------------------------------------------- the anchors fit, same correction (sensitivity)
    if a.predictions and a.pooled:
        P = json.load(open(a.predictions))
        POOL = json.load(open(a.pooled))
        an, pl = P["anchors"], POOL["pooled"]
        a_f = [an["f_ref_hz"], 3 * an["f_ref_hz"]]
        a_mag = [an["H_f_mk_per_w"], pl["H_3f_mk_per_w"]]
        a_lag = [an["lag_f_deg"], an["lag_3f_deg"]]
        prior = dict(name="E63+Q126", f=np.array(a_f),
                     H=np.array([m * complex(math.cos(math.radians(-l)), math.sin(math.radians(-l)))
                                 for m, l in zip(a_mag, a_lag)]),
                     sig=np.array([pl["se_H_f_isotropic"], pl["se_H_3f_isotropic"]]),
                     labels=["E63 A1 0.05 Hz", "Q126 0.15 Hz"])
        out["anchors_sensitivity"] = dict(
            note=("the post-hoc anchors fit (prior-anchors.json) with E73's per-component sigma; the "
                  "anchors' own isotropic SEs are already per-direction and are left alone. Params "
                  "and chi2/AIC only, no profiled intervals."),
            fits={})
        for nm in MODELS:
            fit = FP.grid_fit(nm, [grp, prior])
            out["anchors_sensitivity"]["fits"][nm] = dict(
                params=fit["params"], gains=fit["gains"], chi2=fit["chi2"], dof=fit["dof"],
                aic=fit["aic"], group_delay_s=FP.group_delay(nm, fit["params"]))
        fb = min(out["anchors_sensitivity"]["fits"],
                 key=lambda k: out["anchors_sensitivity"]["fits"][k]["aic"])
        out["anchors_sensitivity"]["preferred"] = fb
        out["anchors_sensitivity"]["delta_aic"] = {
            nm: out["anchors_sensitivity"]["fits"][nm]["aic"]
            - out["anchors_sensitivity"]["fits"][fb]["aic"] for nm in MODELS}

    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=False)
        fh.write("\n")

    # ------------------------------------------------------------------------------------ report
    def ci(c):
        return "[%.2f, %.2f]" % (c[0], c[1]) if c and c[0] and c[1] else "[-, -]"

    print("E73, the registered fits re-run with the per-component error (sigma = se_H/sqrt(2))")
    print("%d included points, dof = 2n - npar - 1 as before\n" % len(f73))
    print("%-5s %-34s %-22s %8s %5s %6s %8s %7s" %
          ("model", "parameters (dchi2=1)", "G0 / mK/W", "chi2", "dof", "red", "AIC", "dAIC"))
    for nm in MODELS:
        fr = out["fits"][nm]
        ps = " ".join("%s=%.3f %s" % (n, v, ci(c)) for n, v, c in
                      zip(fr["param_names"], fr["params"], fr["param_ci68"]))
        g = "%.1f %s" % (fr["gain"], ci(fr.get("dc_gain_ci68")))
        print("%-5s %-34s %-22s %8.2f %5d %6.3f %8.2f %7.2f" %
              (nm, ps, g, fr["chi2"], fr["dof"], fr["chi2_red"], fr["aic"], out["delta_aic"][nm]))
        print("      group delay %.2f s %s   (frozen: chi2 %.2f, dAIC %+.2f, group %.2f s)" %
              (fr["group_delay_s"], ci(fr.get("group_delay_ci68")),
               out["frozen_fits"][nm]["chi2"], out["frozen_delta_aic"][nm],
               out["frozen_fits"][nm]["group_delay_s"]))
    print("\npreferred by AIC: %s ; dchi2(P1 - %s) = %.2f for one extra parameter"
          % (best, best, out["delta_chi2_P1_over_P1D"]))
    r01 = next(r for r in out["fits"][best]["residuals"] if abs(r["f_hz"] - 0.01) < 1e-6)
    print("0.01 Hz: model lag %.2f deg, data %.2f +- %.2f -> %.2f SE in the lag alone; "
          "complex norm %.2f (null sqrt2 = 1.41)"
          % (r01["model_lag_deg"], r01["data_lag_deg"], r01["se_lag_deg"], r01["lag_dev_se"],
             r01["resid_sigma_cplx"]))
    z = out["at_0p05_hz"]
    print("0.05 Hz: attenuation %.5f, model %.2f mK/W vs the measured line %.2f +- %.2f "
          "-> %.2f line-SE (%.1f%%) low; the line under this shape implies G0 = %.1f mK/W"
          % (z["attenuation"], z["model_mag_mk_per_w"], z["reference_line_mk_per_w"],
             z["se_reference_line"], z["undershoot_line_se"], 100 * z["undershoot_frac"],
             z["g0_implied_by_the_line"]))
    if "anchors_sensitivity" in out:
        print("\nthe post-hoc anchors fit with the same correction:")
        for nm in MODELS:
            fx = out["anchors_sensitivity"]["fits"][nm]
            print("  %-4s %s chi2 %7.2f/%d AIC %7.2f dAIC %+6.2f group %.2f s"
                  % (nm, " ".join("%.3f" % v for v in fx["params"]), fx["chi2"], fx["dof"],
                     fx["aic"], out["anchors_sensitivity"]["delta_aic"][nm], fx["group_delay_s"]))
    print("\nwrote %s" % os.path.relpath(a.out))


if __name__ == "__main__":
    main()
