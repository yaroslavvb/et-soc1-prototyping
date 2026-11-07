#!/usr/bin/env python3
"""E182 (Q153): the registered statistics (E182.md section 5), in one file that the power simulation (power_e182.py) and the kit's
scorer both import, so the rules simulated are the rules scored. Standard library only; deterministic.

  t_quantile(p, df)                 Student's t quantile, by bisection on the regularized incomplete beta (exact to 1e-10)
  launch_reading(ts, ws, t0, t1)    a launch's board reading: the mean of the kept samples in [t0 + 170 ms, t1]; < 2 samples: None
  dips_kept(samples)                E82 amendment A2's dip rule over a block's sample sequence
  quads_of_process(readings, ori)   a process's quads (launches 1-4, 5-8, 9-12), signed by its orientation so each reads D(F) - D(S)
  train_units(processes)            consecutive (SFFS, FSSF) process pairs -> one unit each, the mean of the two process values
  interval(values)                  mean, se, n, df and the 95% t interval
  combine(x, y, a, b, k)            (a x + b y) / k with Welch-Satterthwaite df, for beta_A = (x_sign - x_swap) / 14 and beta_B
  sign_of / size_of / null_of       the verdict words
SPDX-License-Identifier: Apache-2.0
"""
import bisect
import math
import statistics

LAG_MS = 170
DIP_W = 4.0
MIN_UNITS = 8


# ------------------------------------------------------------------ t quantiles
def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(c) > 1e-300 else 1e300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(c) > 1e-300 else 1e300
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-15:
            break
    return h


def _ibeta(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lb) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lb) * _betacf(b, a, 1 - x) / b


def t_cdf(t, df):
    x = df / (df + t * t)
    p = 0.5 * _ibeta(df / 2.0, 0.5, x)
    return 1.0 - p if t > 0 else p


def t_quantile(p, df):
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


_TQ = {}


def _t975_int(n):
    if n not in _TQ:
        _TQ[n] = t_quantile(0.975, float(n))
    return _TQ[n]


def t975(df):
    """the 97.5% point of t at df degrees of freedom: exact at whole df; between whole df, linear in 1/df between its neighbours
    (Welch's df is fractional; the error is below 1e-4 from 30 df up; under 30 df it is computed exactly); above 4,000 df the normal point"""
    df = float(df)
    if df >= 4000:
        return 1.959963984540054
    lo = int(math.floor(df))
    if lo == df:
        return _t975_int(lo)
    if df < 30:
        k = round(df, 9)
        if k not in _TQ:
            _TQ[k] = t_quantile(0.975, df)
        return _TQ[k]
    hi = lo + 1
    w = (1 / lo - 1 / df) / (1 / lo - 1 / hi)
    return _t975_int(lo) + w * (_t975_int(hi) - _t975_int(lo))


# ------------------------------------------------------------------ the train's reading
def dips_kept(samples):
    """samples: [(t_ms, board_w)] sorted by time. E82 A2: drop i when board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W."""
    v = [w for _, w in samples]
    keep = [True] * len(samples)
    for i in range(2, len(samples) - 2):
        if v[i] < min(v[i - 2], v[i + 2]) - DIP_W:
            keep[i] = False
    return [s for s, k in zip(samples, keep) if k]


def launch_reading(ts, ws, t0_ms, t1_ms):
    i0 = bisect.bisect_left(ts, t0_ms + LAG_MS)
    i1 = bisect.bisect_right(ts, t1_ms)
    w = ws[i0:i1]
    return sum(w) / len(w) if len(w) >= 2 else None


def quads_of_process(readings, ori):
    """readings: {launch index: W} for launches 1..12 (0 is the settle); ori 'SFFS' or 'FSSF'. Each complete quad (L1..L4) gives
    sigma (L2 + L3 - L1 - L4) / 2 with sigma = +1 for SFFS (S F F S) and -1 for FSSF, so every quad reads D(F) - D(S)."""
    sg = 1.0 if ori == "SFFS" else -1.0
    out = []
    for q in range(3):
        ix = [4 * q + 1, 4 * q + 2, 4 * q + 3, 4 * q + 4]
        if all(readings.get(i) is not None for i in ix):
            L1, L2, L3, L4 = (readings[i] for i in ix)
            out.append(sg * (L2 + L3 - L1 - L4) / 2)
    return out


def train_units(processes):
    """processes: [(orientation, [quads])] in the planned order. Process k's value is the mean of its quads (none: no value);
    unit j pairs processes 2j and 2j+1 (one of each orientation by the plan) when both have a value."""
    vals = [(o, (sum(q) / len(q)) if q else None) for o, q in processes]
    units = []
    for j in range(len(vals) // 2):
        (o1, v1), (o2, v2) = vals[2 * j], vals[2 * j + 1]
        if v1 is not None and v2 is not None and o1 != o2:
            units.append((v1 + v2) / 2)
    return units


def interval(values):
    v = [float(x) for x in values if x is not None]
    n = len(v)
    if n < 2:
        return {"n": n, "mean": v[0] if v else None, "se": None, "df": None, "lo": None, "hi": None}
    m = statistics.mean(v)
    se = statistics.stdev(v) / math.sqrt(n)
    hw = t975(n - 1) * se
    return {"n": n, "mean": m, "se": se, "df": n - 1, "lo": m - hw, "hi": m + hw, "hw": hw}


def combine(x, y, a, b, k):
    """(a x + b y) / k for two independent intervals x, y (dicts from interval()), Welch-Satterthwaite df"""
    if x.get("se") is None or y.get("se") is None:
        return {"mean": None, "se": None, "df": None, "lo": None, "hi": None}
    m = (a * x["mean"] + b * y["mean"]) / k
    vx, vy = (a * x["se"] / k) ** 2, (b * y["se"] / k) ** 2
    se = math.sqrt(vx + vy)
    df = (vx + vy) ** 2 / (vx ** 2 / x["df"] + vy ** 2 / y["df"])
    hw = t975(df) * se
    return {"mean": m, "se": se, "df": df, "lo": m - hw, "hi": m + hw, "hw": hw}


# ------------------------------------------------------------------ verdict words
def sign_of(iv):
    if iv.get("lo") is None:
        return "NOT SCORED"
    if iv["lo"] > 0:
        return "POSITIVE"
    if iv["hi"] < 0:
        return "NEGATIVE"
    return "NOT RESOLVED"


def size_of(iv, line):
    """PASS if the forecast line lies inside the interval; FAIL HIGH if it lies above (the model prices more than the card reads);
    FAIL LOW if below"""
    if iv.get("lo") is None:
        return "NOT SCORED"
    if iv["lo"] <= line <= iv["hi"]:
        return "PASS"
    return "FAIL HIGH" if line > iv["hi"] else "FAIL LOW"


def null_of(iv, delta):
    """the side's verdict: POSITIVE / NEGATIVE (the interval excludes 0), NULL (the interval inside +-delta), else NOT RESOLVED"""
    s = sign_of(iv)
    if s in ("POSITIVE", "NEGATIVE", "NOT SCORED"):
        return s
    return "NULL" if -delta < iv["lo"] and iv["hi"] < delta else "NOT RESOLVED"


def split_of(va, vb):
    """E182-SPLIT from E182-A's and E182-B's words"""
    if va == "NULL" and vb == "POSITIVE":
        return "B-ONLY"
    if va == "POSITIVE" and vb == "POSITIVE":
        return "A+B"
    if va == "POSITIVE" and vb == "NULL":
        return "A-ONLY"
    if va == "NULL" and vb == "NULL":
        return "NEITHER"
    if "NOT SCORED" in (va, vb):
        return "NOT SCORED"
    return "UNSETTLED"


def agrees(iv, lo, hi):
    """two intervals overlap"""
    if iv.get("lo") is None:
        return "NOT SCORED"
    if iv["hi"] < lo:
        return "DIFFERS LOW"
    if iv["lo"] > hi:
        return "DIFFERS HIGH"
    return "AGREES"


def spearman(x, y):
    def ranks(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else 0.0


def ols(xs, ys):
    """slope, its se and the intercept (score_e178.ols's slope and se)"""
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxx = sum((a - mx) ** 2 for a in xs)
    b = sum((a - mx) * (c - my) for a, c in zip(xs, ys)) / sxx
    resid = [c - (my + b * (a - mx)) for a, c in zip(xs, ys)]
    se = math.sqrt(sum(r * r for r in resid) / (len(xs) - 2) / sxx)
    return b, se, my - b * mx


if __name__ == "__main__":
    # self-check of the t quantiles against the textbook values
    for df, want in ((1, 12.7062), (2, 4.3027), (4, 2.7764), (11, 2.2010), (30, 2.0423), (62, 1.9990), (1000, 1.9623)):
        assert abs(t975(df) - want) < 5e-4, (df, t975(df), want)
    for df in (1.5, 2.7, 3.5, 9.3, 30.5, 40.5, 62.7, 123.4):
        assert abs(t975(df) - t_quantile(0.975, df)) < 1e-4, (df, t975(df), t_quantile(0.975, df))
    print("e182_stats self-check PASS")
