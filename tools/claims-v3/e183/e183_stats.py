#!/usr/bin/env python3
"""E183 (Q155): the registered statistics (E183.md section 5), in one file that the power simulation (power_e183.py) and the kit's
scorer both import, so the rules simulated are the rules scored. Standard library only; deterministic.

E182's train statistics are used unchanged: tools/claims-v3/e182/e182_stats.py, loaded by path and refused unless its sha256 is the
one E182's registration list pins (SHA256SUMS-e182-registration). From it: the launch's reading (the mean of the block's 10 Hz board
samples in [t_start + 170 ms, t_end], after E82 A2's dip rule; fewer than 2 samples: no reading), the quads of a process (launches 1-4,
5-8, 9-12, signed by the orientation so each reads D(F) - D(S)), the units (consecutive SFFS / FSSF process pairs), the interval
(t(0.975, n - 1)), the Welch combination and the verdict words (SIGN, SIZE, NULL, REPEAT's AGREES / DIFFERS).

Added here, for E183's six trains T1-T6 (kinds-e183.json; dR and dO the result's and the operands' popcount differences, first minus
second):
  lincomb(terms)       sum of a_i x T_i over independent train intervals, Welch-Satterthwaite df
  price_b(T)           b, W per result 1-bit: (T1 + T3) / 14 (each dR = +7, dO = 0); one of them alone: T / 7
  price_c(T)           c, W per operand 1-bit: (T2 + T4) / 14 (each dO = +7, dR = 0); one alone: T / 7
  x_resid(T)           E183-X: T6 - (6 b - c), with b and c as price_b and price_c take them (T6: dR = +6, dO = -1)
  j_diff(T, a, b)      E183-J: T_b - T_a (T3 - T1, T4 - T2): does a bit's price move with 16 more mantissa bits held?
  mech_of(vb, vc)      E183-MECH from E183-B's and E183-C's NULL words (band +-0.004 W a bit)
  consistent_of(iv)    CONSISTENT when the interval holds 0, else INCONSISTENT
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import importlib.util
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E182_STATS = os.path.join(TOP, "tools", "claims-v3", "e182", "e182_stats.py")
E182_STATS_SHA = "b7fe938fd3f941e64aeec13bf8fc9456926b70b09bcdd0a88096fbc4fc8d44b3"   # SHA256SUMS-e182-registration, line 4


def _load_e182_stats():
    got = hashlib.sha256(open(E182_STATS, "rb").read()).hexdigest()
    if got != E182_STATS_SHA:
        raise SystemExit(f"e182_stats.py sha256 {got[:16]} is not E182's registered {E182_STATS_SHA[:16]}: refusing")
    spec = importlib.util.spec_from_file_location("e182_stats", E182_STATS)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


S = _load_e182_stats()
LAG_MS, DIP_W, MIN_UNITS = S.LAG_MS, S.DIP_W, S.MIN_UNITS
t975, dips_kept, launch_reading = S.t975, S.dips_kept, S.launch_reading
quads_of_process, train_units, interval, combine = S.quads_of_process, S.train_units, S.interval, S.combine
sign_of, size_of, null_of, agrees = S.sign_of, S.size_of, S.null_of, S.agrees

NULL_BAND_W = 0.004         # W a bit: E183-B's and E183-C's NULL band, twice the DOUBLED half-width of b and c (about 0.002 W a
                            # bit), as E182's band was twice its DOUBLED half-width; about two fifths of E180's measured price
DR = {"T1": 7, "T2": 0, "T3": 7, "T4": 0, "T5": 1, "T6": 6}
DO = {"T1": 0, "T2": 7, "T3": 0, "T4": 7, "T5": 1, "T6": -1}
LAUNCHES = 13               # a train process: the settle (launch 0), then launches 1-12, three quads


def scored(iv):
    return iv is not None and iv.get("se") is not None


def lincomb(terms):
    """terms: [(a, interval)] of independent intervals; the sum of a x mean with its Welch-Satterthwaite interval"""
    if not terms or any(not scored(iv) for _, iv in terms):
        return {"mean": None, "se": None, "df": None, "lo": None, "hi": None}
    m = sum(a * iv["mean"] for a, iv in terms)
    vs = [(a * iv["se"]) ** 2 for a, iv in terms]
    v = sum(vs)
    se = math.sqrt(v)
    den = sum(vi ** 2 / iv["df"] for vi, (_, iv) in zip(vs, terms) if vi > 0)
    df = v ** 2 / den if den > 0 else float(min(iv["df"] for _, iv in terms))
    hw = t975(df) * se
    return {"mean": m, "se": se, "df": df, "lo": m - hw, "hi": m + hw, "hw": hw}


def _pair_price(T, a, b, d):
    have = [k for k in (a, b) if scored(T.get(k))]
    if len(have) == 2:
        return lincomb([(1.0 / (2 * d), T[a]), (1.0 / (2 * d), T[b])]), have
    if len(have) == 1:
        return lincomb([(1.0 / d, T[have[0]])]), have
    return {"mean": None, "se": None, "df": None, "lo": None, "hi": None}, have


def price_b(T):
    """b from T1 and T3 (dR = 7 each, dO = 0)"""
    return _pair_price(T, "T1", "T3", 7)


def price_c(T):
    """c from T2 and T4 (dO = 7 each, dR = 0)"""
    return _pair_price(T, "T2", "T4", 7)


def x_resid(T):
    """T6 - (6 b - c) as one linear combination of the independent trains, with b and c as price_b and price_c take them"""
    if not scored(T.get("T6")):
        return {"mean": None, "se": None, "df": None, "lo": None, "hi": None}, []
    _, hb = price_b(T)
    _, hc = price_c(T)
    if not hb or not hc:
        return {"mean": None, "se": None, "df": None, "lo": None, "hi": None}, []
    terms = [(1.0, T["T6"])]
    terms += [(-6.0 / (7 * len(hb)), T[k]) for k in hb]
    terms += [(+1.0 / (7 * len(hc)), T[k]) for k in hc]
    return lincomb(terms), ["T6"] + hb + hc


def j_diff(T, a, b):
    if not (scored(T.get(a)) and scored(T.get(b))):
        return {"mean": None, "se": None, "df": None, "lo": None, "hi": None}
    return lincomb([(1.0, T[b]), (-1.0, T[a])])


def consistent_of(iv):
    if not scored(iv):
        return "NOT SCORED"
    return "CONSISTENT" if iv["lo"] <= 0 <= iv["hi"] else "INCONSISTENT"


def mech_of(vb, vc):
    """E183-MECH: RESULT (B POSITIVE, C NULL); OPERAND (B NULL, C POSITIVE); BOTH (both POSITIVE); NEITHER (both NULL); else UNSETTLED"""
    if "NOT SCORED" in (vb, vc):
        return "NOT SCORED"
    if vb == "POSITIVE" and vc == "NULL":
        return "RESULT"
    if vb == "NULL" and vc == "POSITIVE":
        return "OPERAND"
    if vb == "POSITIVE" and vc == "POSITIVE":
        return "BOTH"
    if vb == "NULL" and vc == "NULL":
        return "NEITHER"
    return "UNSETTLED"


def train_estimate(processes):
    """processes: [(orientation, [quads])] in the planned order -> the train's interval over units (NOT SCORED under MIN_UNITS)"""
    units = train_units(processes)
    iv = interval(units)
    iv["units"] = len(units)
    if len(units) < MIN_UNITS:
        return {"mean": iv.get("mean"), "se": None, "df": None, "lo": None, "hi": None, "units": len(units),
                "why": f"{len(units)} units, {MIN_UNITS} needed"}
    return iv


if __name__ == "__main__":
    # self-checks: E182's t quantiles, and the combinations' algebra on fixed intervals
    for df, want in ((1, 12.7062), (5, 2.5706), (25, 2.0595), (100, 1.9840)):
        assert abs(t975(df) - want) < 5e-4, (df, t975(df), want)
    T = {k: {"mean": 7 * 0.0097 if k in ("T1", "T3") else 0.0, "se": 0.005, "df": 25.0} for k in ("T1", "T2", "T3", "T4")}
    T["T6"] = {"mean": 6 * 0.0097, "se": 0.005, "df": 25.0}
    b, hb = price_b(T)
    c, hc = price_c(T)
    assert abs(b["mean"] - 0.0097) < 1e-12 and abs(c["mean"]) < 1e-12 and hb == ["T1", "T3"] and hc == ["T2", "T4"]
    assert abs(b["se"] - math.sqrt(2) * 0.005 / 14) < 1e-15 and abs(b["df"] - 50.0) < 1e-9
    x, _ = x_resid(T)
    assert abs(x["mean"]) < 1e-12
    assert mech_of(null_of(b, NULL_BAND_W), null_of(c, NULL_BAND_W)) == "RESULT"
    T.pop("T3")
    b1, hb1 = price_b(T)
    assert hb1 == ["T1"] and abs(b1["mean"] - 0.0097) < 1e-12 and abs(b1["se"] - 0.005 / 7) < 1e-15
    print("e183_stats self-check PASS")
