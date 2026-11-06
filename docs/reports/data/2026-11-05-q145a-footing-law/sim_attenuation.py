#!/usr/bin/env python3
"""heat-q145a: a Monte Carlo of the two estimators that read low (post hoc, a model of the estimators, not of the card).

(a) The per-run in-run fit (E60's and E78's 'leak auto'): a run's die temperature rises like E171's mean profile (about 1.55 C over the
    window, most of it in the first 2 s); the reading is that temperature rounded to a whole degree with a small sensor noise; board
    power = k_true x temperature + noise; the trace from 0.8 s to 4.4 s at 10 Hz; one straight line per run if the reading spans >= 1 C;
    the median over runs. The launch phase relative to the degree boundary is uniform, as the launch gate (a reading of 58) allows.
(b) The in-pass rests (Q139(u) F1): rests whose true temperature spreads with a given sd; a 1 s mean of 10 whole-degree readings with
    sensor noise; within-pass OLS, and its reverse regression.

    python3 -B sim_attenuation.py <out.json>
"""
import json
import sys

import numpy as np

rng = np.random.default_rng(145)


def sim_inrun(k_true, n_runs=4000, sigma_s=0.15, sigma_p=0.12, rise=1.9, tau=1.3):
    t = np.arange(0.8, 4.41, 0.1)
    ks = []
    for _ in range(n_runs):
        T0 = 57.5 + rng.random()                        # the launch reading is 58: the true start lies in [57.5, 58.5)
        Ttrue = T0 + rise * (1 - np.exp(-t / tau))
        X = np.round(Ttrue + rng.normal(0, sigma_s, len(t)))
        P = k_true * Ttrue + rng.normal(0, sigma_p, len(t))
        if X.max() - X.min() >= 1:
            ks.append(np.polyfit(X, P, 1)[0])
    return float(np.median(ks)), len(ks)


def sim_rests(k_true, sd_true, n_pass=50, n_rest=48, sigma_s=0.3, sigma_p=0.07):
    sxy = sxx = syy = 0.0
    for _ in range(n_pass):
        Tt = 58.4 + rng.normal(0, sd_true, n_rest)
        X = np.array([np.mean(np.round(T + rng.normal(0, sigma_s, 10))) for T in Tt])
        P = k_true * Tt + rng.normal(0, sigma_p, n_rest)
        dx, dy = X - X.mean(), P - P.mean()
        sxy += dx @ dy
        sxx += dx @ dx
        syy += dy @ dy
    return float(sxy / sxx), float(syy / sxy), float(np.sqrt(sxx / (n_pass * (n_rest - 1))))


def main():
    out = {"inrun": {}, "rests": {}}
    for k in (0.36, 0.49):
        for rise, tau in ((1.9, 1.3), (1.6, 1.0), (2.4, 1.6)):
            m, n = sim_inrun(k, rise=rise, tau=tau)
            out["inrun"][f"k{k}_rise{rise}_tau{tau}"] = {"median": m, "runs_kept": n, "ratio": m / k}
            print("inrun", k, rise, tau, round(m, 4), n, round(m / k, 3))
    for k in (0.36, 0.49):
        for sdt in (0.10, 0.15, 0.20):
            for ss in (0.2, 0.3, 0.45):
                ols, rev, sdx = sim_rests(k, sdt, sigma_s=ss)
                out["rests"][f"k{k}_sdT{sdt}_sens{ss}"] = {"ols": ols, "reverse": rev, "sd_reading": sdx, "ratio": ols / k}
                print("rests", k, sdt, ss, round(ols, 4), round(rev, 4), round(sdx, 3), round(ols / k, 3))
    json.dump(out, open(sys.argv[1], "w"), indent=1)


if __name__ == "__main__":
    main()
