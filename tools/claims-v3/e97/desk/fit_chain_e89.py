#!/usr/bin/env python3
"""E97 desk check (no card): the heat path of aifoundry3 card 0, fitted to E89's committed raw passes.

The lab's thermal model (docs/findings/11-thermal-model.md) is aifoundry2's, from September, and says of itself that its
network does not transfer to another card. E89's two passes are 38 minutes of 10 Hz fine readings on the card E97 uses. This
fits the Foster chain of that document (the same fixed time constants, every resistance non-negative) from the measured
board power to the 34-sensor mean, with the pass's opening idle as the origin. Lawson-Hanson non-negative least squares in
numpy, so nothing else is needed. The input power is the whole board's, leakage included, so the chain is open loop.

    python3 tools/claims-v3/e97/desk/fit_chain_e89.py > tools/claims-v3/e97/desk/chain_e89.txt
writes chain_e89.json beside itself.
"""
import gzip
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
D = os.path.join(ROOT, "docs/reports/data/2026-10-31-e89-heat-low-power/aifoundry3/e89")
G, H, C5 = 57400, 249400, 4096


def c2t(n):
    return (G + H * n / C5 - H / 2) / 1000.0


def load(p):
    t, P, T = [], [], []
    for line in gzip.open(os.path.join(D, p, "telemetry.jsonl.gz"), "rt"):
        if not line.startswith("{"):
            continue
        r = json.loads(line)
        c = (r.get("pvt") or {}).get("c") or []
        if "board_w" not in r or len(c) != 34:
            continue
        t.append(r["t_ms"] / 1000.0)
        P.append(r["board_w"])
        T.append(sum(c2t(x) for x in c) / 34.0)
    return np.array(t), np.array(P), np.array(T)


def nnls(A, b, tol=1e-10, maxit=200):
    """Lawson-Hanson."""
    n = A.shape[1]
    x = np.zeros(n)
    P = np.zeros(n, bool)
    w = A.T @ (b - A @ x)
    it = 0
    while (~P).any() and w[~P].max() > tol and it < maxit:
        it += 1
        j = np.argmax(np.where(~P, w, -np.inf))
        P[j] = True
        while True:
            s = np.zeros(n)
            s[P] = np.linalg.lstsq(A[:, P], b, rcond=None)[0]
            if s[P].min() > 0:
                break
            q = P & (s <= 0)
            alpha = np.min(x[q] / (x[q] - s[q]))
            x = x + alpha * (s - x)
            P = x > tol
        x = s
        w = A.T @ (b - A @ x)
    return x


def fit(g, Pd, y, tau):
    tau = np.array(tau, float)
    X = np.zeros((len(g), len(tau)))
    x = np.zeros(len(tau))
    a = np.exp(-(g[1] - g[0]) / tau)
    for i, p in enumerate(Pd):
        x = a * x + (1 - a) * p
        X[i] = x
    R = nnls(X[::5], y[::5])
    rms = float(np.sqrt(np.mean((y - X @ R) ** 2)))
    return R, rms


def main():
    t1, P1, T1 = load("p8910")
    t2, P2, T2 = load("p8911")
    t, P, T = np.r_[t1, t2], np.r_[P1, P2], np.r_[T1, T2]
    g = np.arange(t[0], t[-1], 0.2)
    Pg, Tg = np.interp(g, t, P), np.interp(g, t, T)
    P0, T0 = float(np.median(P[:150])), float(np.median(T[:150]))
    print(f"E89's two passes: {t[-1] - t[0]:.0f} s, {len(t)} samples; opening idle {T0:.3f} degC, {P0:.3f} W; "
          f"mean over the passes {T.mean():.2f} degC, {P.mean():.2f} W, so {(T.mean() - T0) / (P.mean() - P0):.3f} degC per board W on the means")
    out = {"source": "docs/reports/data/2026-10-31-e89-heat-low-power/aifoundry3/e89/p8910, p8911", "idle_C": T0, "idle_W": P0, "fits": {}}
    for name, tau in (("lab_grid", [1.5, 4, 60, 150, 400, 2500]), ("decades", [1, 3, 10, 30, 100, 300, 1000])):
        R, rms = fit(g, Pg - P0, Tg - T0, tau)
        tau = np.array(tau, float)
        print(f"{name}: tau {tau.tolist()}  R {np.round(R, 4).tolist()}  total {R.sum():.4f} degC per board W  rms {rms:.3f} degC")
        for s in (2, 30, 60, 120, 300, 600, 1800):
            v = float((R * (1 - np.exp(-s / tau))).sum())
            print(f"   open loop, {s:5d} s after a step: {v:.3f} degC per board W, {v / R.sum():.3f} of the total")
        out["fits"][name] = {"tau": tau.tolist(), "R": R.tolist(), "total": float(R.sum()), "rms": rms}
    json.dump(out, open(os.path.join(HERE, "chain_e89.json"), "w"), indent=1)
    print("What E89 cannot say: its passes last 38 minutes and swing the mean power by little, so a stage slower than about 400 s is barely constrained.")


if __name__ == "__main__":
    main()
