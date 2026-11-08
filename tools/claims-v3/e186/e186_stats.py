#!/usr/bin/env python3
"""E186 (Q158): the registered statistics of E186.md section 5, in one file that the power simulation (power_e186.py) and the kit's scorer
both import, so the rules simulated are the rules scored. E182's statistics (tools/claims-v3/e182/e182_stats.py, frozen in 58b88850) are
imported unchanged: a launch's reading, a process's quads, the units, a train's interval, the Welch-Satterthwaite combination and the words
SIGN, SIZE, NULL, SPLIT and AGREES. Standard library only; deterministic.

  size_band(iv, line, se_line)   SIZE against a forecast that carries its own se: the interval of (estimate - line) is
                                 (mean - line) +- sqrt(hw^2 + (1.96 se_line)^2), hw the train's own t half-width (REFIT.md section 4's
                                 held-out form). PASS when it holds 0; FAIL HIGH when the line lies above the estimate (the model prices
                                 more than the card reads); FAIL LOW when below. With se_line = 0 it is e182_stats.size_of.
  which(w12, w10)                M12 / M10 / BOTH / NEITHER: whose SIZE word reads PASS
  zscore(iv, line, se_line)      (mean - line) / sqrt(se^2 + se_line^2)
  chi2_95(n)                     the 95% point of chi-square at n degrees of freedom
  joint(zs)                      Q = sum z^2 over the scored trains: CONSISTENT when Q <= chi2_95(n), else INCONSISTENT
  models_word(j12, j10)          E186-M: M12 (M12 CONSISTENT, M10 not) / M10 / BOTH / NEITHER
  h16_word(words)                E186-H16: the arms whose SIZE reads PASS, in the order F16-SAME, SCALED, M10; NONE if none
  split_from(sw, sg, dsw, dsg)   beta_A and beta_B a held 1-bit a byte from two trains at one product, each train's (dh_A, dh_B) a byte
  slope_from(x, y, offs, bits)   a held-bit price a bit from the two ladder trains on one side (or the one scored, over its own bits)
  scaled(iv, f)                  an interval times f
  boot_rms_diff                  m12_common.boot_rms_diff (E186-LV), imported unchanged
SPDX-License-Identifier: Apache-2.0
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e182"))
sys.path.insert(0, os.path.join(HERE, "..", "m12"))
import e182_stats as S  # noqa: E402  (unchanged)
from m12_common import boot_rms_diff  # noqa: E402,F401  (unchanged)

Z95 = 1.959963984540054
DELTA_AB = 0.002     # W a held 1-bit a byte: E182-A's and E182-B's NULL band, kept for the splits at products 3 and 63


def size_band(iv, line, se_line):
    if iv.get("lo") is None:
        return "NOT SCORED"
    e = iv["mean"] - line
    hw = math.sqrt(iv["hw"] ** 2 + (Z95 * se_line) ** 2)
    if e - hw <= 0.0 <= e + hw:
        return "PASS"
    return "FAIL HIGH" if e + hw < 0 else "FAIL LOW"


def which(w12, w10):
    if "NOT SCORED" in (w12, w10):
        return "NOT SCORED"
    p12, p10 = w12 == "PASS", w10 == "PASS"
    return "BOTH" if p12 and p10 else ("M12" if p12 else ("M10" if p10 else "NEITHER"))


def zscore(iv, line, se_line):
    return (iv["mean"] - line) / math.sqrt(iv["se"] ** 2 + se_line ** 2)


def _gammainc_lower_reg(a, x):
    """P(a, x) by its series (x < a + 1) or continued fraction"""
    if x <= 0:
        return 0.0
    gl = math.lgamma(a)
    if x < a + 1:
        ap, s, d = a, 1.0 / a, 1.0 / a
        for _ in range(1000):
            ap += 1
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 1e-15:
                break
        return s * math.exp(-x + a * math.log(x) - gl)
    b, c, d = x + 1 - a, 1e300, 1.0 / (x + 1 - a)
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1) < 1e-15:
            break
    return 1.0 - math.exp(-x + a * math.log(x) - gl) * h


_C2 = {}


def chi2_95(n):
    if n not in _C2:
        lo, hi = 0.0, 10.0 * n + 50.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if _gammainc_lower_reg(n / 2.0, mid / 2.0) < 0.95:
                lo = mid
            else:
                hi = mid
        _C2[n] = (lo + hi) / 2
    return _C2[n]


def joint(zs):
    n = len(zs)
    if n == 0:
        return {"word": "NOT SCORED", "n": 0}
    q = sum(z * z for z in zs)
    c = chi2_95(n)
    return {"word": "CONSISTENT" if q <= c else "INCONSISTENT", "Q": q, "n": n, "chi2_95": c}


def models_word(j12, j10):
    if "NOT SCORED" in (j12, j10):
        return "NOT SCORED"
    a, b = j12 == "CONSISTENT", j10 == "CONSISTENT"
    return "BOTH" if a and b else ("M12" if a else ("M10" if b else "NEITHER"))


def h16_word(words):
    """words: {'F16-SAME': w, 'SCALED': w, 'M10': w}"""
    if any(v == "NOT SCORED" for v in words.values()):
        return "NOT SCORED"
    p = [k for k in ("F16-SAME", "SCALED", "M10") if words[k] == "PASS"]
    return "+".join(p) if p else "NONE"


def split_from(sw, sg, dsw, dsg):
    """sw, sg: the swap and sign trains' intervals; dsw, dsg: each train's (dh_A, dh_B), the popcount a byte first minus second.
    Solves dh_A beta_A + dh_B beta_B = train for both trains; each beta a Welch-Satterthwaite combination of the two."""
    if sw.get("se") is None or sg.get("se") is None:
        return {"mean": None, "se": None, "df": None, "lo": None, "hi": None}, {"mean": None, "se": None, "df": None, "lo": None, "hi": None}
    (a1, b1), (a2, b2) = dsw, dsg
    det = a1 * b2 - b1 * a2
    bA = S.combine(sw, sg, b2, -b1, det)
    bB = S.combine(sw, sg, -a2, a1, det)
    return bA, bB


def slope_from(x, y, offs, bits):
    """a held-bit price a bit from two ladder trains on one side, each D(first) - D(second) = its P10 offset + its bits x the price:
    ((x - offs[0]) + (y - offs[1])) / (bits[0] + bits[1]) when both are scored (Welch-Satterthwaite), else the one scored over its own bits"""
    xs, ys = x.get("se") is not None, y.get("se") is not None
    if xs and ys:
        n = bits[0] + bits[1]
        c = S.combine(x, y, 1, 1, n)
        sh = (offs[0] + offs[1]) / n
        return {"mean": c["mean"] - sh, "se": c["se"], "df": c["df"], "lo": c["lo"] - sh, "hi": c["hi"] - sh, "hw": c["hw"], "from": "both"}
    for iv, off, b, nm in ((x, offs[0], bits[0], "first"), (y, offs[1], bits[1], "second")):
        if iv.get("se") is not None:
            return {"mean": (iv["mean"] - off) / b, "se": iv["se"] / b, "df": iv["df"], "lo": (iv["lo"] - off) / b, "hi": (iv["hi"] - off) / b,
                    "hw": iv["hw"] / b, "from": nm + " only"}
    return {"mean": None, "se": None, "df": None, "lo": None, "hi": None}


def scaled(iv, f):
    if iv.get("lo") is None:
        return dict(iv)
    out = {"mean": iv["mean"] * f, "se": iv["se"] * abs(f), "df": iv["df"], "lo": iv["lo"] * f, "hi": iv["hi"] * f, "hw": iv["hw"] * abs(f)}
    if f < 0:
        out["lo"], out["hi"] = out["hi"], out["lo"]
    return out


if __name__ == "__main__":
    for n, want in ((1, 3.841459), (2, 5.991465), (3, 7.814728), (5, 11.070498), (8, 15.507313), (10, 18.307038), (12, 21.026070)):
        assert abs(chi2_95(n) - want) < 1e-5, (n, chi2_95(n), want)
    iv = {"mean": 0.10, "se": 0.0025, "df": 31, "lo": 0.10 - 0.0051, "hi": 0.10 + 0.0051, "hw": 0.0051}
    for ln in (0.09, 0.0949, 0.0951, 0.1049, 0.1051, 0.11):
        assert size_band(iv, ln, 0.0) == S.size_of(iv, ln), ln
    assert size_band(iv, 0.11, 0.005) == "PASS" and size_band(iv, 0.11, 0.004) == "FAIL HIGH"   # hw 0.0110 against 0.0094
    assert size_band(iv, 0.12, 0.005) == "FAIL HIGH" and size_band(iv, 0.08, 0.005) == "FAIL LOW"
    sw = {"mean": 0.0015, "se": 0.0025, "df": 31, "lo": 0, "hi": 0, "hw": 0}
    sg = {"mean": 0.1080, "se": 0.0025, "df": 31, "lo": 0, "hi": 0, "hw": 0}
    bA, bB = split_from(sw, sg, (-1, 1), (7, 5))
    assert abs(bA["mean"] - (0.1080 - 5 * 0.0015) / 12) < 1e-15 and abs(bB["mean"] - (0.1080 + 7 * 0.0015) / 12) < 1e-15
    print("e186_stats self-check PASS")
