"""Student t distribution without scipy: regularized incomplete beta (Numerical Recipes continued fraction)."""
import math
def _betacf(a, b, x, itmax=300, eps=3e-14):
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > 1e-300 else 1e-300); h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(c) > 1e-300 else 1e300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(c) > 1e-300 else 1e300
        de = d * c; h *= de
        if abs(de - 1) < eps: break
    return h
def betainc(a, b, x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    bt = math.exp(lbt)
    if x < (a + 1) / (a + b + 2): return bt * _betacf(a, b, x) / a
    return 1 - bt * _betacf(b, a, 1 - x) / b
def sf(t, df):
    """P(T > t)"""
    x = df / (df + t * t)
    p = 0.5 * betainc(df / 2, 0.5, x)
    return p if t >= 0 else 1 - p
def ppf(q, df):
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2
        if 1 - sf(mid, df) < q: lo = mid
        else: hi = mid
    return (lo + hi) / 2
if __name__ == "__main__":
    for df in (1, 2, 3, 4, 5, 10):
        print(df, round(ppf(0.995, df), 4), round(ppf(0.975, df), 4))
