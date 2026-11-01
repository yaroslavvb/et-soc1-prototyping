#!/usr/bin/env python3
"""E111 (Q133), desk, before any E111 data: the heat-path shapes fitted to E73's 14 included transfer points (the corrected
error, se_corr / sqrt 2 per component, E73 README result 4), and what each predicts at 0.005 Hz and at its odd harmonics.
P1D and P2 are E73's; P1D+slow (a parallel slow branch) and P1D+diff (a half-order, diffusive factor) are two forms that can
give the extra low-frequency lag of E73's result 8. The covariance draws give each prediction's spread.

    /usr/bin/python3 tools/claims-v3/e111/desk/fit_e73_models.py \
        docs/reports/data/2026-10-27-e73-camera-frequencies/analysis/fit.json tools/claims-v3/e111/desk/e73_models.json
"""
import json, math, sys
import numpy as np
from scipy.optimize import least_squares
P = json.load(open(sys.argv[1]))
pts = [p for p in P['points'] if p.get('included')]
f = np.array([p['f_hz'] for p in pts]); re = np.array([p['H_re_corr'] for p in pts]); im = np.array([p['H_im_corr'] for p in pts])
sig = np.array([p['se_corr'] for p in pts]) / math.sqrt(2)
print(len(pts), 'points; f =', sorted(set(np.round(f, 4))))
def model(name, th, ff):
    s = 2j * math.pi * ff
    if name == 'P1D':
        G, tau, Td = th; H = G / (1 + s * tau) * np.exp(-s * Td)
    elif name == 'P2':
        G, t1, t2 = th; H = G / ((1 + s * t1) * (1 + s * t2))
    elif name == 'P1D+slow':
        G, tau, Td, w, t3 = th; H = G * ((1 - w) / (1 + s * tau) + w / (1 + s * t3)) * np.exp(-s * Td)
    elif name == 'P1D*pole':
        G, tau, Td, t3 = th; H = G / ((1 + s * tau) * (1 + s * t3)) * np.exp(-s * Td)
    elif name == 'P1D+diff':
        G, tau, Td, td = th; H = G / (1 + s * tau) / np.sqrt(1 + s * td) * np.exp(-s * Td)
    # convention: lag positive -> conj
    return np.conj(H)
def resid(th, name):
    H = model(name, th, f)
    return np.concatenate([(H.real - re) / sig, (H.imag - im) / sig])
fits = {}
starts = {'P1D': [250, 16, 1], 'P2': [250, 15, 1], 'P1D+slow': [250, 14, 1, 0.3, 150], 'P1D*pole': [250, 14, 0.8, 30], 'P1D+diff': [250, 14, 0.8, 30]}
bounds = {'P1D': ([0, 0.1, 0], [5000, 200, 10]), 'P2': ([0, 0.1, 0.01], [5000, 200, 100]),
          'P1D+slow': ([0, 0.1, 0, 0, 20], [20000, 200, 10, 1, 5000]),
          'P1D*pole': ([0, 0.1, 0, 0.01], [20000, 200, 10, 5000]), 'P1D+diff': ([0, 0.1, 0, 0.01], [20000, 200, 10, 50000])}
for name in starts:
    best = None
    for k in range(40):
        x0 = np.array(starts[name], float) * np.exp(np.random.default_rng(k).normal(0, 0.5, len(starts[name]))) if k else np.array(starts[name], float)
        x0 = np.clip(x0, np.array(bounds[name][0]) + 1e-6, np.array(bounds[name][1]) - 1e-6)
        r = least_squares(resid, x0, args=(name,), bounds=bounds[name])
        if best is None or r.cost < best.cost: best = r
    chi2 = 2 * best.cost; npar = len(best.x); dof = 2 * len(f) - npar
    # covariance
    J = best.jac; cov = np.linalg.pinv(J.T @ J)
    out = {}
    for fq in (0.005, 0.00625, 0.01, 0.015, 0.025, 0.035, 0.045, 0.05):
        H = model(name, best.x, np.array([fq]))[0]
        out[fq] = (abs(H), math.degrees(math.atan2(H.imag, H.real)))
    # lag uncertainty at 0.005 by sampling the covariance
    rng = np.random.default_rng(1); lags = []; ratios = []
    for _ in range(4000):
        th = rng.multivariate_normal(best.x, cov)
        th = np.clip(th, np.array(bounds[name][0]), np.array(bounds[name][1]))
        H5 = model(name, th, np.array([0.005, 0.015, 0.025]))
        lags.append(math.degrees(math.atan2(H5[0].imag, H5[0].real))); ratios.append(abs(H5[1]) / abs(H5[0]))
    lags = np.array(lags); ratios = np.array(ratios)
    fits[name] = dict(x=best.x.tolist(), chi2=chi2, dof=dof, aic=chi2 + 2 * npar, at=out, lag5_sd=float(np.std(lags)), lag5_q=[float(np.percentile(lags, 2.5)), float(np.percentile(lags, 97.5))], r15_5=[float(np.percentile(ratios, 2.5)), float(np.percentile(ratios, 50)), float(np.percentile(ratios, 97.5))])
    print(f"{name:9s} x={np.round(best.x,3)} chi2={chi2:.2f}/{dof} AIC={chi2+2*npar:.2f}")
    for fq, (m, ph) in out.items(): print(f"     f={fq:.5f} |H|={m:7.1f} lag={ph:6.1f}")
    print(f"     lag(0.005) sd {np.std(lags):.2f} 95% {np.percentile(lags,2.5):.1f}..{np.percentile(lags,97.5):.1f}; |H(0.015)|/|H(0.005)| {np.percentile(ratios,50):.3f} [{np.percentile(ratios,2.5):.3f},{np.percentile(ratios,97.5):.3f}]")
json.dump(fits, open(sys.argv[2], 'w'), indent=1, default=str)
