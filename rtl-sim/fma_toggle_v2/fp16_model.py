#!/usr/bin/env python3
"""The fp16 TFMA_PH_PS arithmetic as the RTL's fixed-point window computes it, not as exact arithmetic would.

    r = c + a_lo*b_lo + a_hi*b_hi, RTZ, on a window whose LSB sits 25 bits below the largest term's leading position.

Read off txfma_ediff_opdorder_logic.v (which term is largest), txfma_f3.v (the two aligners and the bits they keep),
txfma_c2.v and txfma_e2.v (negation and sticky), txfma_f4.v and txfma_f5.v (the sum, its clearing below B24, its negation).
"""
from fractions import Fraction

EB = 127


def f16(h):
    return (h >> 15) & 1, (h >> 10) & 0x1F, h & 0x3FF


def mant16(e, m):
    return (0x400 | m) if e else 0


def e32_of(e, zero_qualified):
    """txfma_e1.v: {e[4], {3{~e[4] (& ~zero)}}, e[3:0]}"""
    e4 = (e >> 4) & 1
    ext = (0 if e4 else 7)
    if zero_qualified and e == 0:
        ext = 0
    return (e4 << 7) | (ext << 4) | (e & 0xF)


def fp16_terms(a, b, c):
    ahi, alo, bhi, blo = a >> 16, a & 0xFFFF, b >> 16, b & 0xFFFF
    sa, ea, fa = f16(ahi)
    sb, eb, fb = f16(bhi)
    sal, eal, fal = f16(alo)
    sbl, ebl, fbl = f16(blo)
    sc = c >> 31
    ec = (c >> 23) & 0xFF
    fc = c & 0x7FFFFF
    ph_zero = ea == 0 or eb == 0
    pl_zero = eal == 0 or ebl == 0
    c_zero = ec == 0
    eph = e32_of(ea, True) + e32_of(eb, False) - EB
    epl = e32_of(eal, False) + e32_of(ebl, False) - EB
    # the products on [A1:B19]: 22 bits, A1 weight 2, A0 weight 1, B19 weight 2^-20
    mph = mant16(ea, fa) * mant16(eb, fb)
    mpl = mant16(eal, fal) * mant16(ebl, fbl)
    # C on [A0:B22]: 24 bits, B22 weight 2^-23
    mc = (0x800000 | fc) if ec else 0
    sph, spl = sa ^ sb, sal ^ sbl
    return dict(sc=sc, ec=ec, mc=mc, c_zero=c_zero, eph=eph, epl=epl, mph=mph, mpl=mpl, sph=sph, spl=spl,
                ph_zero=ph_zero, pl_zero=pl_zero)


def model(a, b, c, neg_sticky_mode=3, info=None):
    """-> fp32 word. Only for finite operands: NaN and infinity are handled by the caller.

    `info`, if a dict, receives "x": the sum's magnitude on the window, in window units, before its last correction.
    neg_sticky_mode 3 is the RTL's rule (txfma_f4.v:75, :82-86, txfma_f5.v:175): a negative sum with any lost bit is
    one's-complemented, so it reads one unit low. The other modes are there to show that this is the rule that fits.
    """
    t = fp16_terms(a, b, c)
    cph = ((t["ec"] - t["eph"]) < 0 and not t["ph_zero"]) or t["c_zero"]
    cpl = ((t["ec"] - t["epl"]) < 0 and not t["pl_zero"]) or t["c_zero"]
    phpl = ((t["eph"] - t["epl"]) < 0 and not t["pl_zero"]) or t["ph_zero"]
    key = (cph, cpl, phpl)
    if not cph and not cpl:                  # c > ph, pl
        op3, al1, al2 = "C", "PH", "PL"
    elif key == (False, True, True) or key == (True, True, True):
        op3, al1, al2 = "PL", "C", "PH"
    else:                                    # (T,F,F), (T,T,F)
        op3, al1, al2 = "PH", "C", "PL"
    E = {"C": t["ec"], "PH": t["eph"], "PL": t["epl"]}
    S = {"C": t["sc"], "PH": t["sph"], "PL": t["spl"]}
    Z = {"C": t["c_zero"], "PH": t["ph_zero"], "PL": t["pl_zero"]}
    # everything on a grid of B24 units: A0 = 2^25 units, B22 = 2^2 units, B19 = 2^5 units
    M = {"C": t["mc"] << 2, "PH": t["mph"] << 5, "PL": t["mpl"] << 5}
    eref = E[op3]
    if op3 == "C":
        pass
    total = M[op3]
    any_sticky = False
    cin_low = 0
    d1 = abs(eref - E[al1])
    d2 = abs(eref - E[al2])
    m1 = 0 if d1 > 26 else M[al1] >> d1
    lost1 = (M[al1] & ((1 << min(d1, 200)) - 1)) != 0 if d1 <= 200 else M[al1] != 0
    if Z[al1]:
        lost1 = False
    if d1 > 26:
        lost1 = M[al1] != 0
    m2 = 0 if d2 > 26 else M[al2] >> d2
    lost2 = (M[al2] & ((1 << min(d2, 200)) - 1)) != 0 if d2 <= 200 else M[al2] != 0
    if Z[al2]:
        lost2 = False
    if d2 > 26:
        lost2 = M[al2] != 0
    neg1 = S[al1] != S[op3]
    neg2 = S[al2] != S[op3]
    # The window keeps B24 and up. A negated aligned term loses its sticky +1, so it is floor(-x), on both aligners.
    x = total
    x += (-m1 - (1 if lost1 else 0)) if neg1 else m1
    x += (-m2 - (1 if lost2 else 0)) if neg2 else m2
    sticky_pos = (lost1 and not neg1) or (lost2 and not neg2)
    sign = S[op3]
    if info is not None:
        info["x"] = abs(x)
    if x < 0:
        sign ^= 1
        x = -x
        if sticky_pos and neg_sticky_mode == 1:
            x -= 1
        if (lost1 or lost2) and neg_sticky_mode == 3:
            x -= 1
    if x == 0:
        # all three terms zero: IEEE's rule for a sum of zeros (negative only if every term is); exact cancellation gives +0
        if t["c_zero"] and t["ph_zero"] and t["pl_zero"] and t["sc"] and t["sph"] and t["spl"]:
            return 0x80000000
        return 0
    # value = x * 2^(eref - 127 - 25)
    n = x.bit_length()
    be = eref + (n - 1 - 25)
    mant = x >> (n - 24) if n >= 24 else x << (24 - n)
    if be <= 0:
        return sign << 31
    if be >= 255:
        return (sign << 31) | 0x7F7FFFFF
    return (sign << 31) | (be << 23) | (mant & 0x7FFFFF)
