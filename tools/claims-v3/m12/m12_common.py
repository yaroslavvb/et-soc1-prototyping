#!/usr/bin/env python3
"""M12 (Q157): the shared pieces of the refit (REFIT.md): the committed inputs' paths, the readers, the model's equations, a small
weighted least-squares solver with its covariance, the delta-method se, popcounts of a tile's lane words, and the bootstrap.

M12 changes M10 only for held-word tiles (REFIT.md section 2):
  int8 one-number tiles   D8 = c8 + R (k_w F_walk + k_s F_scp) 1e-15 + beta_A h_A + beta_B h_B      (k in fJ a flip)
  float held-word tiles   Df = P10 + c_f + gamma_A pc_A + gamma_B pc_B                               (P10 = M10 frozen)
Pure Python (no numpy). SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import random
import statistics
import struct

E182D = "docs/reports/data/2026-11-08-e182-one-number-r2-aifoundry3"
E182F = "tools/claims-v3/e182/forecast-e182.json"
E178D = "docs/reports/data/2026-11-06-e178-one-number-aifoundry3"
E178F = "tools/claims-v3/e178/forecast-e178.json"
E171D = "docs/reports/data/2026-11-05-e171-blind8-aifoundry3"
E172D = "docs/reports/data/2026-11-05-e172-blind8-card1"
B8 = "tools/claims-v3/kinds/blind8"
M10D = "docs/reports/data/2026-11-04-q142m-m10"
E184S = "docs/reports/data/2026-11-08-e184-sensor-validation/scored-e184-v3.json"
TRAINS8 = {"T1": ("int8.e178_v5", "int8.e178_v4"), "T2": ("int8.e182_a1_bm1", "int8.e182_am1_b1"),
           "T3": ("int8.neg_ones", "int8.ones"), "T4": ("int8.e178_a4_b5", "int8.e178_a5_b4")}
TRAINS32 = {"T5": ("fp32.e182_a1_b3fffffff", "fp32.e182_a3fffffff_b1"), "T6": ("fp32.e178_v5", "fp32.e178_v4")}
TRAIN_LINE_RULE = {"T5": "E182-F", "T6": "E182-H32T"}
CARD1_FLOAT = 0.9615998850616306      # m10.json > families > float > card1_scale (asserted by the fitter)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load(root, rel):
    return json.load(open(os.path.join(root, rel)))


# ------------------------------------------------------------------ the flips and popcounts of a kind
def f_walk(lm):
    """the accumulator's walk: its storage and its read and write data (flips an op, launch mean)"""
    return lm["c_store"] + lm["c_in"] + lm["c_out"]


def f_scp(lm):
    """the scratchpad's read data alternating A and B chunks (flips an op)"""
    return lm["scp"]


def popcount(w):
    return bin(w).count("1")


def tile_popcounts(raw):
    """the mean popcount of the tile's 256 A and 256 B 32-bit lane words (2,048 bytes: A then B)"""
    assert len(raw) == 2048, len(raw)
    aw = struct.unpack("<256I", raw[:1024])
    bw = struct.unpack("<256I", raw[1024:])
    return sum(map(popcount, aw)) / 256.0, sum(map(popcount, bw)) / 256.0, len(set(aw)), len(set(bw))


# ------------------------------------------------------------------ the model's design rows
def int8_row(R, lm, pc_a_word, pc_b_word):
    """[1, R F_walk 1e-15, R F_scp 1e-15, h_A, h_B]: the int8 part's design row (h the popcount a byte)"""
    return [1.0, R * f_walk(lm) * 1e-15, R * f_scp(lm) * 1e-15, pc_a_word / 4.0, pc_b_word / 4.0]


def int8_row_1k(R, lm, pc_a_word, pc_b_word):
    """arm M12-1K: one price for F_walk + F_scp"""
    return [1.0, R * (f_walk(lm) + f_scp(lm)) * 1e-15, pc_a_word / 4.0, pc_b_word / 4.0]


def float_row(pc_a, pc_b):
    """[1, pc_A, pc_B]: the float increment's design row (Df - P10)"""
    return [1.0, pc_a, pc_b]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


# ------------------------------------------------------------------ weighted least squares
def inverse(M):
    n = len(M)
    A = [list(r) + [1.0 if i == j else 0.0 for j in range(n)] for i, r in enumerate(M)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(A[r][c]))
        if abs(A[p][c]) < 1e-300:
            raise ValueError("singular design")
        A[c], A[p] = A[p], A[c]
        pv = A[c][c]
        A[c] = [x / pv for x in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0.0:
                f = A[r][c]
                A[r] = [x - f * z for x, z in zip(A[r], A[c])]
    return [r[n:] for r in A]


def wls(X, y, var):
    """minimise sum (y - X b)^2 / var: returns b and cov(b) = (X' W X)^-1 (the variances taken as known)"""
    n = len(X[0])
    XtWX = [[sum(X[r][i] * X[r][j] / var[r] for r in range(len(X))) for j in range(n)] for i in range(n)]
    XtWy = [sum(X[r][i] * y[r] / var[r] for r in range(len(X))) for i in range(n)]
    cov = inverse(XtWX)
    b = [dot(cov[i], XtWy) for i in range(n)]
    return b, cov


def hat_diag(X, var, cov):
    """the leverages h_rr = x_r' cov x_r / var_r"""
    return [dot(x, [dot(cov[i], x) for i in range(len(x))]) / v for x, v in zip(X, var)]


def se_of(row, cov):
    return math.sqrt(max(0.0, dot(row, [dot(cov[i], row) for i in range(len(row))])))


def joint_fit(kind_rows, kind_y, train_rows, train_y, train_se, tol=1e-12, it_max=200):
    """REFIT.md section 3's int8 fit: the kinds rows at one common variance sigma_K^2 (their own residual variance over their
    effective degrees of freedom, n_K - sum of their leverages, iterated) and the trains at their own se^2"""
    nk = len(kind_rows)
    X = kind_rows + train_rows
    y = kind_y + train_y
    b0, _ = wls(kind_rows, kind_y, [1.0] * nk) if nk > len(kind_rows[0]) else (None, None)
    s2 = statistics.pvariance(kind_y) if b0 is None else sum((yy - dot(r, b0)) ** 2 for yy, r in zip(kind_y, kind_rows)) / max(1, nk - len(kind_rows[0]))
    for it in range(it_max):
        var = [s2] * nk + [s * s for s in train_se]
        b, cov = wls(X, y, var)
        h = hat_diag(X, var, cov)
        dof = nk - sum(h[:nk])
        new = sum((yy - dot(r, b)) ** 2 for yy, r in zip(kind_y, kind_rows)) / dof
        if abs(new - s2) <= tol * max(s2, 1e-30):
            s2 = new
            break
        s2 = new
    var = [s2] * nk + [s * s for s in train_se]
    b, cov = wls(X, y, var)
    res_k = [yy - dot(r, b) for yy, r in zip(kind_y, kind_rows)]
    z_t = [(yy - dot(r, b)) / s for yy, r, s in zip(train_y, train_rows, train_se)]
    return {"b": b, "cov": cov, "sigma_K": math.sqrt(s2), "dof_K": dof, "iterations": it + 1, "kinds_resid": res_k, "trains_z": z_t}


# ------------------------------------------------------------------ held-out statistics
def t975(df):
    """the two-sided 95% t quantile (df >= 1), by the usual table for small df and a series beyond"""
    tab = {1: 12.706204736, 2: 4.302652730, 3: 3.182446305, 4: 2.776445105, 5: 2.570581836, 6: 2.446911851, 7: 2.364624252,
           8: 2.306004135, 9: 2.262157163, 10: 2.228138852, 15: 2.131449546, 20: 2.085963447, 30: 2.042272456, 31: 2.039513446,
           37: 2.026192463, 40: 2.021075390, 60: 2.000297822}
    if df in tab:
        return tab[df]
    z = 1.959963985
    g1 = (z ** 3 + z) / 4
    g2 = (5 * z ** 5 + 16 * z ** 3 + 3 * z) / 96
    g3 = (3 * z ** 7 + 19 * z ** 5 + 17 * z ** 3 - 15 * z) / 384
    return z + g1 / df + g2 / df ** 2 + g3 / df ** 3


def group_stats(e):
    n = len(e)
    if n == 0:
        return {"n": 0}
    m = sum(e) / n
    return {"n": n, "rms": math.sqrt(sum(x * x for x in e) / n), "bias": m, "centred_rms": math.sqrt(sum((x - m) ** 2 for x in e) / n)}


def rms(e):
    return math.sqrt(sum(x * x for x in e) / len(e))


def boot_rms_diff(e1, e0, draws=2000, seed=1570):
    """rms(e1) - rms(e0) on the same rows, with a percentile 95% interval over rows resampled with replacement"""
    rng = random.Random(seed)
    n = len(e1)
    d = []
    for _ in range(draws):
        idx = [rng.randrange(n) for _ in range(n)]
        d.append(rms([e1[i] for i in idx]) - rms([e0[i] for i in idx]))
    d.sort()
    return {"diff": rms(e1) - rms(e0), "lo95": d[int(0.025 * draws)], "hi95": d[int(0.975 * draws) - 1], "draws": draws, "seed": seed}


def gain_offset_word(b):
    """REFIT.md section 4: b = boot_rms_diff(e_gain, e_offset)"""
    if b["lo95"] > 0:
        return "OFFSET"
    if b["hi95"] < 0:
        return "GAIN"
    return "NOT SEPARABLE"
