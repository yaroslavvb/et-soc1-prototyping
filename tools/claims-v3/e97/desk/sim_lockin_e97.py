#!/usr/bin/env python3
"""E97 desk check (no card): is E89's lock-in unbiased on E97's blocks and order, with 12 more blocks against idle and a pass 3.6 times as long?

The chain and the leakage law are the frozen ones (predictions-e97.json), driven by E78's and E86's powers on the runner's schedule, in the registered order of passes 9710 and 9711.
In this world every kind heats alike per W, so every r must read 1. Each block is fitted as the reducer fits it (a shared quadratic, one fundamental per lap); no noise, so what is left is
the design's own bias. A second run with the lab's slower chain (it has 400 s and 2,500 s stages) shows the same on a heat path with more memory.

    /usr/bin/python3 tools/claims-v3/e97/desk/sim_lockin_e97.py > tools/claims-v3/e97/desk/sim_lockin_e97.txt
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import e97_common as c  # noqa: E402

P = json.load(open(os.path.join(HERE, "..", "predictions-e97.json")))
A, L = P["leak_law"]["A_W"], P["leak_law"]["L_C"]
DT = 0.1
S = {v["kind"]: v["S"] for v in P["blocks"].values()}
S.update({"int8.zeros": 2.605, "idle": 0.0})
Ti = 51.4


def half(item, secs):
    n = int(round(secs / DT))
    if item == "idle":
        return np.zeros(n)
    tt = (np.arange(n) * DT) % 7.12
    return np.where(tt >= 0.3, S[item], 0.0)


def session(order):
    p, marks = [np.zeros(int(15 / DT))], []
    tn = 15.0
    for b in order:
        k, z = c.BLOCKS[b]
        p.append(half(z, 20.0))
        ta = tn + 20.0
        for _ in range(2):
            p.append(half(k, 30.0))
            p.append(half(z, 30.0))
        tn = ta + 120.0
        marks.append((b, ta))
    return np.concatenate(p), marks


def simulate(pw, tau, R):
    tau, R = np.array(tau), np.array(R)
    a = np.exp(-DT / tau)
    x = np.zeros(len(tau))
    T = np.empty(len(pw))
    P_ = np.empty(len(pw))
    l0 = A * math.exp((Ti - 80) / L)
    for i, q in enumerate(pw):
        t_ = Ti + x.sum()
        d = q + A * math.exp((t_ - 80) / L) - l0
        x = a * x + (1 - a) * R * d
        T[i] = t_
        P_[i] = d
    return T, P_


def laps(t, y, t0):
    per = 60.0
    span = 2 * per
    m = (t >= t0) & (t < t0 + span)
    tau = t[m] - t0
    u = tau / span - 0.5
    w = 2 * math.pi / per
    cols = [np.ones_like(u), u, u * u]
    for cy in range(2):
        ind = ((tau >= cy * per) & (tau < (cy + 1) * per)).astype(float)
        cols += [np.cos(w * tau) * ind, np.sin(w * tau) * ind]
    co, *_ = np.linalg.lstsq(np.column_stack(cols), y[m], rcond=None)
    return [complex(co[3 + 2 * j], -co[4 + 2 * j]) for j in range(2)]


for name in ("e89_fit", "lab_model"):
    hp = P["heat_paths"][name]
    pw = []
    marks = []
    t0 = 0.0
    for pno in (9710, 9711):
        p_, m_ = session(c.pass_order("aifoundry3", pno))
        pw.append(p_)
        marks += [(b, ta + t0, pno) for b, ta in m_]
        t0 += len(p_) * DT
    pw = np.concatenate(pw)
    T, dP = simulate(pw, hp["tau"], hp["R"])
    t = np.arange(len(pw)) * DT
    print(f"== {name}: tau {hp['tau']}, R {hp['R']}; {len(pw) * DT / 60:.1f} min of blocks, die {T.min():.1f}-{T.max():.1f} C, mean {T.mean():.2f} C")
    res = {}
    for b, ta, pno in marks:
        fT, fP = laps(t, T, ta), laps(t, dP, ta)
        res.setdefault(b, []).append(np.mean([a_ / b_ for a_, b_ in zip(fT, fP)]))
    h_ref = abs(np.mean(res[c.REF_BLOCK]))
    rr = {b: abs(np.mean(v)) / h_ref for b, v in res.items()}
    low = [rr[b] for b in c.LOW_BLOCKS]
    print(f"   H_ref {h_ref:.4f} C/W, phase {np.degrees(np.angle(np.mean(res[c.REF_BLOCK]))):.1f} deg; r over the 28 blocks {min(low):.3f}-{max(low):.3f}, mean {np.mean(low):.3f}, against idle {np.mean([rr[b] for b in c.AGAINST_IDLE]):.3f}, against zeros {np.mean([rr[b] for b in c.AGAINST_ZEROS]):.3f}")
    worst = sorted(rr.items(), key=lambda kv: abs(kv[1] - 1))[-4:]
    print("   the furthest from 1:", ", ".join(f"{b} {v:.3f}" for b, v in worst))
