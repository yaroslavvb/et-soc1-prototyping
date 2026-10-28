#!/usr/bin/env python3
"""E73 post hoc (Wed 28 Oct 2026, week 44): the registered heat-path shapes fitted across E73's own
frequencies TOGETHER WITH the two prior anchors the pre-registration names -- E63 A1's 0.05 Hz point
and Q126's 0.15 Hz third harmonic (`predictions.json` -> `anchors`, whose source is E63's committed
`posthoc/h3-rails-pooled.json`).

This is NOT the registered fit.  `fit_hlf.py` (the frozen script) fits E73's own points only, with one
real positive gain, and that is the number E73's rules are scored on.  Two things have to be added by
hand to put the anchors in the same fit, and both are choices made after the data were seen, so they
carry no verdict:

  1. **a second gain.**  The camera's absolute gain is not the same on two different afternoons -- E63
     measured 59 -> 42 mK/W of drift inside one hour, and E73's own reference line falls 44%/h -- so
     the anchors are given their own real positive gain and only the SHAPE is shared.  The one-gain
     variant is reported beside it to show what forcing a common gain does.
  2. **a circular error for the anchors.**  The pooled anchors' registered SEs are measured along the
     pooled vector's own direction; a complex least squares wants an error in both directions, so the
     isotropic SEs from the same committed file are used (3.409 mK/W at 0.05 Hz, 9.265 at 0.15 Hz).

It also profiles the low-frequency group delay (the quantity the pre-registration names as the
discriminator) for the REGISTERED E73-only fits, which `fit_hlf.py` reports only as a point value.

  python3 fit_priors.py <ANA/fit.json> --predictions <predictions.json> \
      --pooled <E63 posthoc/h3-rails-pooled.json> --out posthoc/prior-anchors.json
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import fit_hlf as FH  # noqa: E402

MODELS = ("P1", "P1D", "P2", "P2D")


def group_delay(name, p):
    """The registered definition, fit_hlf.py's own: tau for P1, tau + delay for P1D, and the sum of
    the two poles for P2 and P2D (so P2D's transport delay is NOT in it -- that is how the frozen
    script writes it, and `group_delay_true_s` below carries the sum including the delay)."""
    if name == "P1":
        return p[0]
    if name == "P1D":
        return p[0] + p[1]
    return p[0] + p[1]


def chi2_groups(name, groups, p, shared_gain=False):
    """chi2 with one real positive gain per group (or one gain for all groups)."""
    if shared_gain:
        f = np.concatenate([g["f"] for g in groups])
        H = np.concatenate([g["H"] for g in groups])
        s = np.concatenate([g["sig"] for g in groups])
        g0, c = FH.gain_and_chi2(name, f, H, s, p)
        return c, [g0] * len(groups)
    chi2 = 0.0
    gains = []
    for g in groups:
        gi, ci = FH.gain_and_chi2(name, g["f"], g["H"], g["sig"], p)
        chi2 += ci
        gains.append(gi)
    return chi2, gains


def grid_fit(name, groups, shared_gain=False, lo=0.05, hi=400.0, n=40, rounds=6):
    """fit_hlf.grid_fit's coarse-to-fine log grid, with the per-group gains."""
    k = FH.NPAR[name]
    bounds = [(lo, hi)] * k
    if name in ("P1D", "P2D"):
        bounds[-1] = (1e-3, 60.0)
    best = None
    for _r in range(rounds):
        axes = [np.exp(np.linspace(math.log(a), math.log(b), n)) for a, b in bounds]
        mesh = np.meshgrid(*axes, indexing="ij")
        flat = [m.ravel() for m in mesh]
        for i in range(len(flat[0])):
            p = [float(x[i]) for x in flat]
            if name in ("P2", "P2D") and p[1] > p[0]:
                continue
            c, gains = chi2_groups(name, groups, p, shared_gain)
            if best is None or c < best[1]:
                best = (p, c, gains)
        nb = []
        for j, (a, b) in enumerate(bounds):
            span = (math.log(b) - math.log(a)) / (n - 1) * 2.5
            c0 = math.log(best[0][j])
            nb.append((math.exp(max(math.log(a), c0 - span)), math.exp(min(math.log(b), c0 + span))))
        bounds = nb
    p, c, gains = best
    npts = sum(len(g["f"]) for g in groups)
    npar = FH.NPAR[name] + (1 if shared_gain else len(groups))
    dof = 2 * npts - npar
    return dict(name=name, label=FH.LABEL[name], params=p, gains=gains, chi2=c,
                n_points=npts, n_par=npar, dof=dof, chi2_red=c / max(1, dof),
                aic=c + 2 * npar, group_delay_s=group_delay(name, p))


def profile(name, groups, p, chi2_min, j, shared_gain=False):
    """delta chi2 = 1 interval of time parameter j, the other time parameters refitted."""
    out = [None, None]
    for s_dir, side in ((-1, 0), (+1, 1)):
        x = p[j]
        for _ in range(400):
            x *= (1.0 + s_dir * 0.01)
            if x <= 1e-4 or x > 4000:
                break
            q = list(p)
            q[j] = x
            if FH.NPAR[name] > 1:
                others = [i for i in range(FH.NPAR[name]) if i != j]
                axes = [np.exp(np.linspace(math.log(max(1e-3, p[i] / 4)), math.log(p[i] * 4), 20))
                        for i in others]
                mesh = np.meshgrid(*axes, indexing="ij")
                fl = [m.ravel() for m in mesh]
                c = float("inf")
                for t in range(len(fl[0])):
                    r = list(q)
                    for a, i in enumerate(others):
                        r[i] = float(fl[a][t])
                    c = min(c, chi2_groups(name, groups, r, shared_gain)[0])
            else:
                c = chi2_groups(name, groups, q, shared_gain)[0]
            if c - chi2_min >= 1.0:
                out[side] = x
                break
    return out


def profile_group_delay(name, groups, p, chi2_min, shared_gain=False):
    """delta chi2 = 1 interval of the DERIVED group delay: scan it, refit the shape at fixed sum."""
    k = FH.NPAR[name]
    if k == 1:
        return profile(name, groups, p, chi2_min, 0, shared_gain)
    g0 = group_delay(name, p)
    out = [None, None]
    for s_dir, side in ((-1, 0), (+1, 1)):
        g = g0
        for _ in range(400):
            g *= (1.0 + s_dir * 0.01)
            if g <= 1e-3 or g > 4000:
                break
            # the best chi2 on the surface sum(params) == g, over a grid of the split
            frac = np.linspace(0.001, 0.999, 220)
            c = float("inf")
            if k == 2:
                for u in frac:
                    r = [g * (1 - u), g * u]
                    if name == "P2" and r[1] > r[0]:
                        continue
                    c = min(c, chi2_groups(name, groups, r, shared_gain)[0])
            else:
                for u in np.linspace(0.02, 0.98, 40):
                    for v in np.linspace(0.02, 0.98, 40):
                        r = [g * u, g * (1 - u) * v, g * (1 - u) * (1 - v)]
                        if r[1] > r[0]:
                            continue
                        c = min(c, chi2_groups(name, groups, r, shared_gain)[0])
            if c - chi2_min >= 1.0:
                out[side] = g
                break
    return out


def chi2_at_fixed_gain(name, group, p, g):
    s = FH.shape(name, group["f"], p)
    wt = 1.0 / np.asarray(group["sig"], dtype=np.float64) ** 2
    return float(np.sum(wt * np.abs(group["H"] - g * s) ** 2))


def profile_gain(name, group, p, chi2_min, g_best):
    """delta chi2 = 1 interval of the zero-frequency gain of one group's fit, the shape refitted."""
    k = FH.NPAR[name]
    out = [None, None]
    for s_dir, side in ((-1, 0), (+1, 1)):
        g = g_best
        for _ in range(400):
            g *= (1.0 + s_dir * 0.005)
            axes = [np.exp(np.linspace(math.log(max(1e-3, p[i] / 4)), math.log(p[i] * 4), 22))
                    for i in range(k)]
            mesh = np.meshgrid(*axes, indexing="ij")
            fl = [m.ravel() for m in mesh]
            c = float("inf")
            for t in range(len(fl[0])):
                r = [float(x[t]) for x in fl]
                if name in ("P2", "P2D") and r[1] > r[0]:
                    continue
                c = min(c, chi2_at_fixed_gain(name, group, r, g))
            if c - chi2_min >= 1.0:
                out[side] = g
                break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fit_json", help="the registered fit.json (E73's points live in it)")
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--pooled", required=True, help="E63 posthoc/h3-rails-pooled.json (Q126)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    F = json.load(open(a.fit_json))
    P = json.load(open(a.predictions))
    POOL = json.load(open(a.pooled))

    # ---------------------------------------------------------------- E73's own included points
    # exactly what the registered fit feeds its models: the drift-corrected complex transfer,
    # conjugated out of the lock-in's lag convention into the models' exp(-i w Td) one, with se_corr
    f73, H73, s73, lab = [], [], [], []
    for r in F["points"]:
        if not r["included"]:
            continue
        f73.append(r["f_hz"])
        H73.append(complex(r["H_re_corr"], r["H_im_corr"]).conjugate())
        s73.append(max(r.get("se_corr") or r["se_cplx"], 1e-9))
        lab.append("%s k%d" % (r["block"], r["k"]))
    e73 = dict(name="E73", f=np.array(f73), H=np.array(H73), sig=np.array(s73), labels=lab)

    # ---------------------------------------------------------------- the two registered anchors
    an = P["anchors"]
    pl = POOL["pooled"]
    a_f = [an["f_ref_hz"], 3 * an["f_ref_hz"]]
    a_mag = [an["H_f_mk_per_w"], pl["H_3f_mk_per_w"]]
    a_lag = [an["lag_f_deg"], an["lag_3f_deg"]]
    a_sig = [pl["se_H_f_isotropic"], pl["se_H_3f_isotropic"]]
    prior = dict(name="E63+Q126",
                 f=np.array(a_f),
                 H=np.array([m * complex(math.cos(math.radians(-l)), math.sin(math.radians(-l)))
                             for m, l in zip(a_mag, a_lag)]),
                 sig=np.array(a_sig),
                 labels=["E63 A1 0.05 Hz (4 blocks pooled)", "Q126 0.15 Hz (3rd harmonic)"])

    out = dict(
        experiment="E73", request="Q129", post_hoc=True,
        written="Wed 28 Oct 2026 (week 44)",
        verdict=None,
        note="not the registered fit; see this file's docstring for the two added choices",
        registered_fit=os.path.basename(a.fit_json),
        anchors=dict(f_hz=a_f, mag_mk_per_w=a_mag, lag_deg=a_lag, se_isotropic=a_sig,
                     source=an["source"],
                     se_along_vector=[an["se_H_f"], pl["se_H_3f"]],
                     pooled_vector_phase_deg=pl["H_f_phase_deg"],
                     registered_lag_note="the registration's anchor lag at 0.05 Hz is the mean of the "
                                         "four blocks' lags (99.11 deg); the pooled vector's own "
                                         "phase is 95.39 deg, carried here as a sensitivity"),
        n_e73_points=len(f73), e73_points=lab,
        fits={}, fits_shared_gain={}, registered_group_delay={}, sensitivity={})

    # ------------------------------------------------- the across-frequency fit, anchors included
    for nm in MODELS:
        fit = grid_fit(nm, [e73, prior])
        ci = [profile(nm, [e73, prior], fit["params"], fit["chi2"], j) for j in range(FH.NPAR[nm])]
        fit["param_names"] = {"P1": ["tau_s"], "P1D": ["tau_s", "delay_s"],
                              "P2": ["tau1_s", "tau2_s"],
                              "P2D": ["tau1_s", "tau2_s", "delay_s"]}[nm]
        fit["param_ci68"] = ci
        fit["group_delay_ci68"] = profile_group_delay(nm, [e73, prior], fit["params"], fit["chi2"])
        fit["gain_names"] = ["E73", "E63+Q126"]
        fit["gain_ratio_prior_over_e73"] = fit["gains"][1] / fit["gains"][0] if fit["gains"][0] else None
        fit["residual_sigma"] = {}
        for grp in (e73, prior):
            s = FH.shape(nm, grp["f"], fit["params"])
            g = fit["gains"][fit["gain_names"].index(grp["name"])]
            res = np.abs(grp["H"] - g * s) / grp["sig"]
            for l, r in zip(grp["labels"], res):
                fit["residual_sigma"][l] = float(r)
        out["fits"][nm] = fit

        sg = grid_fit(nm, [e73, prior], shared_gain=True)
        sg["param_names"] = fit["param_names"]
        sg["group_delay_ci68"] = profile_group_delay(nm, [e73, prior], sg["params"], sg["chi2"],
                                                     shared_gain=True)
        out["fits_shared_gain"][nm] = sg

    best = min(out["fits"], key=lambda k: out["fits"][k]["aic"])
    out["preferred"] = best
    out["aic_table"] = {k: out["fits"][k]["aic"] for k in MODELS}

    # ------------------------------------- the registered E73-only fits: group delay with intervals
    for nm in MODELS:
        rf = F["fits"][nm]
        gd = profile_group_delay(nm, [e73], rf["params"], rf["chi2"])
        out["registered_group_delay"][nm] = dict(
            group_delay_s=group_delay(nm, rf["params"]), ci68=gd,
            params=rf["params"], chi2=rf["chi2"], dof=rf["dof"], aic=rf["aic"],
            dc_gain_mk_per_w=rf["gain"],
            dc_gain_ci68=profile_gain(nm, e73, rf["params"], rf["chi2"], rf["gain"]),
            dc_gain_note="the fitted shape's zero-frequency gain: what a watt held on the board "
                         "forever would read on the camera IF this shape ran to DC. Nothing below "
                         "0.01 Hz is measured, so it is an extrapolation of the fitted family.")

    # ------------------------------------------------------------------------------ sensitivities
    # (a) the anchors with the pooled vector's own phase at 0.05 Hz instead of the mean of lags
    alt = dict(prior)
    alt["H"] = np.array([a_mag[0] * complex(math.cos(math.radians(-pl["H_f_phase_deg"])),
                                            math.sin(math.radians(-pl["H_f_phase_deg"]))),
                         prior["H"][1]])
    for nm in ("P1D", "P2"):
        fit = grid_fit(nm, [e73, alt])
        out["sensitivity"]["%s_anchor_phase_95p39" % nm] = dict(
            params=fit["params"], chi2=fit["chi2"], dof=fit["dof"], aic=fit["aic"],
            group_delay_s=fit["group_delay_s"])
    # (b) the anchors' SEs along the pooled vector (the registered ones) instead of isotropic
    alt2 = dict(prior)
    alt2["sig"] = np.array([an["se_H_f"], pl["se_H_3f"]])
    for nm in ("P1D", "P2"):
        fit = grid_fit(nm, [e73, alt2])
        out["sensitivity"]["%s_anchor_se_along_vector" % nm] = dict(
            params=fit["params"], chi2=fit["chi2"], dof=fit["dof"], aic=fit["aic"],
            group_delay_s=fit["group_delay_s"])
    # (c) the anchors alone, for the record: what two points say on their own
    for nm in ("P1D", "P2"):
        fit = grid_fit(nm, [prior])
        out["sensitivity"]["%s_anchors_only" % nm] = dict(
            params=fit["params"], chi2=fit["chi2"], dof=fit["dof"],
            group_delay_s=fit["group_delay_s"],
            note="2 complex points, 4 numbers, 3 parameters: not a test, only a restatement")

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1, default=float)
        fh.write("\n")

    # ------------------------------------------------------------------------------------ readable
    print("E73 + the two registered anchors (%d + 2 complex points), shape shared, a gain each"
          % len(f73))
    for nm in MODELS:
        f = out["fits"][nm]
        print("  %-4s %-26s %s  G %7.1f / %7.1f  chi2 %6.2f/%d  AIC %6.2f  group %5.2f s %s"
              % (nm, f["label"],
                 " ".join("%s=%.3f[%s]" % (n, v, ",".join("%.2f" % x if x else "-" for x in c))
                          for n, v, c in zip(f["param_names"], f["params"], f["param_ci68"])),
                 f["gains"][0], f["gains"][1], f["chi2"], f["dof"], f["aic"], f["group_delay_s"],
                 "[%s]" % ",".join("%.2f" % x if x else "-" for x in f["group_delay_ci68"])))
    print("  preferred by AIC: %s ; gain ratio prior/E73 %.3f"
          % (best, out["fits"][best]["gain_ratio_prior_over_e73"]))
    print("one gain for everything (the anchors forced onto E73's gain):")
    for nm in MODELS:
        f = out["fits_shared_gain"][nm]
        print("  %-4s %s  chi2 %6.2f/%d  AIC %6.2f  group %5.2f s"
              % (nm, " ".join("%.3f" % v for v in f["params"]), f["chi2"], f["dof"], f["aic"],
                 f["group_delay_s"]))
    print("the REGISTERED E73-only fits, group delay and DC gain with delta chi2 = 1 intervals:")
    for nm in MODELS:
        g = out["registered_group_delay"][nm]
        print("  %-4s group %5.2f s [%s]  G0 %6.1f [%s] mK/W  chi2 %6.2f/%d AIC %6.2f"
              % (nm, g["group_delay_s"],
                 ", ".join("%.2f" % x if x else "-" for x in g["ci68"]),
                 g["dc_gain_mk_per_w"],
                 ", ".join("%.1f" % x if x else "-" for x in g["dc_gain_ci68"]),
                 g["chi2"], g["dof"], g["aic"]))
    print("wrote %s" % os.path.relpath(a.out))   # relative: an absolute home path has no business in a public repo


if __name__ == "__main__":
    main()
