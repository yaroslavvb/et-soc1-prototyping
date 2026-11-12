#!/usr/bin/env python3
"""E188 (Q165, registration): the registered statistics of E188.md section 5 that E186's do not already give, in one file the power
simulation (power_e188.py) and the kit's scorer both import, so the rules simulated are the rules scored. E186's statistics
(tools/claims-v3/e186/e186_stats.py, which imports E182's e182_stats unchanged) are imported unchanged: a train's interval, SIGN, SIZE
against a band (size_band), WHICH, the joint Q and its words, AGREES. Standard library only; deterministic.

  held_part(iv, m10_line)          a train's estimate less its M10 line (M10's P10 difference at the session's s and rate): the part M10
                                   does not price, which M12 says is gamma_A dpc_A + gamma_B dpc_B
  mean_of(ivs)                     the plain mean of n independent intervals, its se sqrt(sum se^2) / n, Welch-Satterthwaite df
  per_bit(iv, bits)                an interval over a bit count
  flat_q(ivs)                      Q = sum (y_i - y_w)^2 / se_i^2, y_w the inverse-variance mean; FLAT when Q <= the 95% point of
                                   chi-square at n - 1, else VARIES (E188-BPOS)
  repeat(iv, lo, hi)               e182_stats.agrees: AGREES when the two intervals overlap, DIFFERS HIGH / DIFFERS LOW otherwise
SPDX-License-Identifier: Apache-2.0
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e186"))
import e186_stats as R  # noqa: E402  (unchanged)
S = R.S                 # e182_stats, unchanged

NONE = {"mean": None, "se": None, "df": None, "lo": None, "hi": None, "hw": None}


def held_part(iv, m10_line):
    if iv.get("se") is None:
        return dict(NONE)
    m = iv["mean"] - m10_line
    return {"mean": m, "se": iv["se"], "df": iv["df"], "lo": iv["lo"] - m10_line, "hi": iv["hi"] - m10_line, "hw": iv["hw"]}


def mean_of(ivs):
    if not ivs or any(v.get("se") is None for v in ivs):
        return dict(NONE)
    n = len(ivs)
    m = sum(v["mean"] for v in ivs) / n
    var = [(v["se"] / n) ** 2 for v in ivs]
    se = math.sqrt(sum(var))
    df = sum(var) ** 2 / sum(x ** 2 / v["df"] for x, v in zip(var, ivs))
    hw = S.t975(df) * se
    return {"mean": m, "se": se, "df": df, "lo": m - hw, "hi": m + hw, "hw": hw, "n": n}


def per_bit(iv, bits):
    return R.scaled(iv, 1.0 / bits) if iv.get("se") is not None else dict(NONE)


def flat_q(ivs):
    if len(ivs) < 2 or any(v.get("se") is None for v in ivs):
        return {"word": "NOT SCORED", "n": len(ivs)}
    w = [1.0 / v["se"] ** 2 for v in ivs]
    yw = sum(wi * v["mean"] for wi, v in zip(w, ivs)) / sum(w)
    q = sum(wi * (v["mean"] - yw) ** 2 for wi, v in zip(w, ivs))
    c = R.chi2_95(len(ivs) - 1)
    return {"word": "FLAT" if q <= c else "VARIES", "Q": q, "df": len(ivs) - 1, "chi2_95": c, "weighted_mean": yw}


def repeat(iv, lo, hi):
    return S.agrees(iv, lo, hi) if iv.get("lo") is not None else "NOT SCORED"


if __name__ == "__main__":
    a = {"mean": 0.015, "se": 0.0025, "df": 37, "lo": 0.015 - 0.0051, "hi": 0.015 + 0.0051, "hw": 0.0051}
    b = {"mean": 0.011, "se": 0.0025, "df": 37, "lo": 0.011 - 0.0051, "hi": 0.011 + 0.0051, "hw": 0.0051}
    m = mean_of([a, b])
    assert abs(m["mean"] - 0.013) < 1e-15 and abs(m["se"] - 0.0025 / math.sqrt(2)) < 1e-15 and abs(m["df"] - 74) < 1e-9, m
    c = S.combine(a, b, 1, 1, 2)
    assert abs(c["mean"] - m["mean"]) < 1e-15 and abs(c["se"] - m["se"]) < 1e-15 and abs(c["df"] - m["df"]) < 1e-9
    f = flat_q([a, b])
    assert abs(f["Q"] - (0.004 ** 2) / (2 * 0.0025 ** 2)) < 1e-12 and f["word"] == "FLAT", f
    far = dict(a, mean=0.030, lo=0.030 - 0.0051, hi=0.030 + 0.0051)
    assert flat_q([far, b])["word"] == "VARIES"
    h = held_part(a, 0.002)
    assert abs(h["mean"] - 0.013) < 1e-15 and abs(h["lo"] - (0.015 - 0.0051 - 0.002)) < 1e-15
    p = per_bit(a, 23)
    assert abs(p["mean"] - 0.015 / 23) < 1e-15 and abs(p["hw"] - 0.0051 / 23) < 1e-15
    assert repeat(a, 0.0205, 0.03) == "DIFFERS LOW" and repeat(a, 0.0, 0.0095) == "DIFFERS HIGH" and repeat(a, 0.019, 0.03) == "AGREES"
    print("e188_stats self-check PASS")
