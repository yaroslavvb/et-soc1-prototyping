#!/usr/bin/env python3
"""Q130(c) — the explanation model: each kind's switching power and clock, predicted BEFORE E78 and E80 run.

    /usr/bin/python3 model.py --out predictions.json > predictions.txt

Numpy only.  No card is touched and nothing here is a measurement: every number is a prediction computed from
already-committed measurements, frozen for E78 (aifoundry3, 600 MHz pinned) and E80 (aifoundry2, its own
governor, no governor move).  Model id Q130C-M1.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════
THE MODEL

  dW(kind)  =  U_T * (1 - g)                              the lane the gate did not switch off
             + Phi(S_A; WA_T) + Phi(S_B; WB_T)            the operand bits, saturating per side
             + sigma_T * q                                 the product's SIGN, which no operand price sees

THREE fp32 numbers are fitted and nothing else: WA and WB on E70's two measured one-sided random-operand
steps, and sigma on E64's fp32 `signs`.  U is read off E67's and E70's own anchors.  fp32 randn -- the
headline kind -- is therefore an OUT-OF-SAMPLE CHECK, not a fit.  There is no cross-side overlap term: one
was fitted in a first pass and came out at -0.03, zero to within 3%, so it is declared zero.

all at 600 MHz and 521.8 mV on aifoundry3, over that type's OWN zero-data level (the basis every number in
this file uses: `over a running kernel on zero data`, E67's `anchor_zeros`).  Phi(S; W) = W(1 - e^(-S/W)) is
E70's selected coverage law.

  1. THE STREAM.  Each type's own issue order (kinds.json facts 2 and 3: txfma's 512 micro-ops x 8 column
     slots for fp32/fp16, TIMA's 256 x 16 for int8).  Per-position flip counts, cyclic over the micro-ops of
     one op, the broadcast A word counted once per column slot -- tools/claims-v3/hl/make_hl.py fma_flips's
     and rtl-sim/fma_toggle/tb.sv's convention:

         fA[j] = #{(m,l) : bit j of A_m != bit j of A_{m+1}},  fB[j] = #{(m,l) : bit j of B_(m,l) flips}

     A position that toggles on every presentation gives fB = 4,096 in every type and fA = 2,048 in fp32/fp16
     (the A word is held two micro-ops) or 4,096 in int8 (it changes every micro-op).  Those are exactly E65's
     and E67's own "designed bits per op" denominators, which is what lets their lists be used per position
     with no conversion at all.

  2. THE PRICES (fp32).  E65's B-side and E67's A-side 32-position lists, measured on aifoundry3 at 600 MHz
     and 521.8 mV -- E78's own card, clock and voltage.  Per flip: wB[j] = E65_B[j]/4096, wA[j] =
     E67_A[j]/2048.  S_A, S_B are E70's own additive sum generalised from one mask to a whole histogram, and
     `check_e70_rungs()` asserts that against all sixteen of E70's lq and alq rungs.

  3. THE LAW'S CURVATURE IS ANCHORED ON THE MEASURED ONE-SIDED RANDOM STEPS, not on E70's fit.  E70 warns
     that its own fitted W-infinity is not a ceiling and that its top rungs sit above it (nrd_a 7.209 W
     against a fitted 6.37 W; nrd_b 10.785 against 10.52), and it REJECTS the saturating form outright on the
     A side.  So WA_T and WB_T here are solved so the law reproduces E70's two measured one-sided
     random-operand steps exactly, and E70's fitted 6.37 / 10.52 W are carried as the sensitivity arm.

  4. THE PRODUCT'S SIGN.  A sign bit is the cheapest bit on the operand bus (E65 bit 31: 0.56 W a position,
     against 4.63 W for mantissa bit 22) and one of the dearest in the array, because it flips the sign of
     the PRODUCT and so the whole width of the adder's input.  No operand-position price can see that: E65's
     and E67's masks were measured against a CONSTANT other operand.  The term is

         q = (product-sign changes over all elements and column-slot-cycles) / 4096

     priced by one scalar sigma, fitted on E64's fp32 `signs` (+-1.0f, where it is the ONLY thing that
     happens).  The same operand pair priced with and without it is the difference between missing E64's
     `signs` by 4 W and hitting it.  E65's own `A=pi` rows say the same thing from the other side: the same B
     mantissa bit costs 3.2x more when the held A operand is pi than when it is 1.0.

  5. THE GATE.  `ex_tensor_zero_mask = A_zero | (tenB_zero[raddr] & tenB_zero[raddr|1])` (vpu_ctrl.v:802-818):
     one 32-bit test in fp32/fp16, TWO ANDed in int8, so the gate rate is ~p, ~p^2, ~p^8.  g is the gated
     fraction of the 4,096 column-slot-cycles of one op (kinds.json stats.gated_lane_frac, asserted here).
     U_fp32 = 8.555 +- 0.060 W, the lane un-gating step of E67's and E70's own anchors (a running kernel on
     zero data against one on a constant NON-zero operand).  In the `gate` arm a gated slot-cycle pays none
     of its flips; in the `bus` arm it pays all of them.  E64's fp32 sparse75 selects between the two.

  6. FORMAT (fp16, int8) -- the only arm with no price list of its own, because E79 is measuring those now.
     Each element bit is priced off fp32's list BY FIELD ROLE, the mantissa aligned at the MSB (a significand
     bit's price is set by how many partial-product columns it drives, so the narrow format's array is the
     top of the wide one) and the exponent at the LSB (the exponent is a counter into one shifter):

         sign     -> fp32 bit 31
         exponent -> fp32 bit 23 + b        (fp16: 5 bits -> 23..27)
         mantissa -> fp32 bit 22 - (m-1-b)  (fp16: 10 bits -> 13..22; int8 magnitude: 7 bits -> 16..22)

     and then the prices, the law's curvature AND sigma are all scaled by one number per format,

         beta_T = r_T * alpha_T,   r_fp16 = 11/24,  r_int8 = 8/24    (significand width over fp32's)

     with alpha_T the ONLY quantity fitted per format.  CALIBRATION FOR fp16 AND int8 IS E64's THREE KINDS
     AND NOTHING ELSE: zeros (both terms vanish -- a consistency check), ones (g = 0, no flips, no sign
     change, so it measures U_T alone) and randn (one scalar, alpha_T).  Every other kind of those two
     formats is out of sample.  alpha_T = 1 would mean the significand-width scaling is exactly right, so
     alpha_fp16 and alpha_int8 are themselves predictions E79's own price lists can falsify.

  7. E78's CARD AND CLOCK.  The fp32 prices, the law's anchors, the carry-over and U are all aifoundry3,
     600 MHz, 521.8 mV -- E78's operating point, so that arm needs no conversion.  E64's three kinds per
     format are aifoundry2 at 600 MHz / 517 mV (its fitted c) and carry over by ONE registered rule, E60's
     and E68's:

         W(a3, 600 MHz, 521.8 mV) = c(a2, 600 MHz, 517 mV) * (0.5218/0.517)^2 = c * 1.01865

     the dynamic term at V^2 with f fixed, which is E64's own s_f at f/600 = 1 (E72: the price follows the
     voltage; E60's cross-card check 1.300 W predicted against 1.291 measured, 0.7%).  Its checks here:
     E64's fp32 (randn - zeros) carries to 24.661 W against E67's own 24.659 +- 0.37 W, and E70's nrd_a and
     nrd_b carry to E64's a_randn_b_ones and a_ones_b_randn to 0.1 W.  LEAKAGE IS IN NONE OF IT: every figure
     is a difference of two runs at a common die reading, so the slope cancels.  Which slope de-leaked the
     inputs: each campaign's own registered reduction (E65 0.182, E67 0.175, E70 0.1975 W/C solved from their
     own runs; E64 E60's 0.442 W/C constant referred to 58 C).  Sensitivity arm: E71's measured
     0.3803 W/C on aifoundry3 over 58-62 C -- every price falls 2-5% and the un-gating term moves 0.105 W.

  8. E80's SPEED.  Back to aifoundry2 by the inverse of rule 7, into E64's own c, then

         burst     = E64's REGISTERED governor (surface_hpl.py simulate, tau 1.3 s, pass 0.24 s) on
                     p_f = B_f + c*s_f at the card's 65 W and a cool die: the call that builds E64's own cap
                     table 65 W column;
         sustained = E64-T1 (surface_hpl_t.py): the same governor with E66's leakage law in the power curve,
                     the die a state relaxing towards E64's thermal line die = 41.88 + 0.4696*W with
                     tau_th = 14 s, and a thermal limb that steps the clock down on a pass reading >= 66 C.
                     gamma = 3.0 (declared here: the voltage exponent with E64-T1's best out-of-sample
                     sustained rms, 6.2 MHz over nine SUS cells, and the one E64's own within-run busy slope
                     implies, 3.12).  gamma 0 and 2 are the sensitivity arms.
═══════════════════════════════════════════════════════════════════════════════════════════════════════════
"""
import argparse
import hashlib
import json
import math
import os
import statistics as st
import sys

import numpy as np

MODEL_ID = "Q130C-M1"
N, WORDS = 16, 256
TYPES = {"fp32": (1, 4), "fp16": (2, 2), "int8": (4, 1)}
MICROOPS = {"fp32": 512, "fp16": 512, "int8": 256}
SLOTS = {"fp32": 8, "fp16": 8, "int8": 16}
SLOT_CYCLES = 4096                      # micro-ops x slots, the same in every type
CYCLES_PER_OP = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
MACS_PER_OP = {"fp32": 4096, "fp16": 8192, "int8": 16384}

# ── the price lists, aifoundry3, 600 MHz, 521.8 mV (W per fully-toggled position)
E65_B = [0.63, 0.51, 0.41, 0.48, 0.48, 0.46, 0.38, 0.53, 0.52, 0.61, 0.96, 1.10, 1.57, 1.78, 2.16, 2.54,
         2.79, 2.84, 3.15, 3.72, 3.97, 4.16, 4.63, 0.80, 0.79, 0.68, 0.87, 0.51, 0.95, 1.06, 0.74, 0.56]
E67_A = [0.46, 1.14, 0.47, 1.08, 0.35, 0.71, 0.99, 0.58, 0.38, 0.75, 0.85, 1.26, 0.97, 2.00, 1.47, 2.44,
         1.88, 1.50, 2.48, 2.67, 2.52, 2.63, 3.26, 0.64, 0.61, 0.36, 0.66, 0.53, 0.73, 0.87, 0.40, 0.56]
B_DENOM, A_DENOM = 4096.0, 2048.0
WINF_B_E70, WINF_A_E70 = 10.52, 6.37    # E70's own fits, the sensitivity arm
RHO = 1.246                             # the A/B per-designed-bit carry-over at a random word's weight
U_FP32, U_FP32_SE = 8.555, 0.060
NRD_A, NRD_A_SE = 7.209, 0.015          # E70: random A against a constant B, over aq_h0
NRD_B, NRD_B_SE = 10.785, 0.024         # E70: random B against a constant A, over lq_h0
ZR = {"anchor_zeros_w": 27.828, "anchor_randn_w": 52.487, "const_operand_w": 36.383,
      "step_w": 24.659, "step_se_w": 0.37, "ungating_w": 8.555, "flip_w": 16.104}
E70_LAW_RMS_W = 0.232

E64_B = {600: 25.455614671708208, 700: 28.243261128820862, 800: 33.60956684526229}
E64_S = {600: 1.0, 700: 1.408193628120374, 800: 1.90517380064275}
E64_FIT_RMS_W = 0.8242388715772772
E64_C = {("fp32", "zeros"): [1.406, 1.473, 1.442], ("fp32", "ones"): [11.164, 9.648, 9.704],
         ("fp32", "randn"): [25.459, 25.593, 25.862], ("fp32", "sparse75"): [3.849, 3.997],
         ("fp32", "signs"): [14.383, 14.222], ("fp32", "pow2"): [15.117, 15.149],
         ("fp32", "mant"): [22.906, 22.796], ("fp32", "uniform"): [23.637, 23.646],
         ("fp32", "a_randn_b_ones"): [16.832, 16.933], ("fp32", "a_ones_b_randn"): [20.389, 20.413],
         ("fp16", "zeros"): [1.394], ("fp16", "ones"): [9.702], ("fp16", "randn"): [23.284],
         ("int8", "zeros"): [2.123], ("int8", "ones"): [2.684], ("int8", "randn"): [9.101]}
V_A2, V_A3 = 0.517, 0.5218
XFER = (V_A3 / V_A2) ** 2
OP_RATE_600 = 1.1208e9                  # whole-card TensorFMA ops/s at 600 MHz, E70's measured rate
R_T = {"fp32": 1.0, "fp16": 11.0 / 24.0, "int8": 8.0 / 24.0}
E64_GOV = {"tau_s": 1.3, "pass_s": 0.24}
T_REF, T_TRIP, GAMMA = 58.0, 66.0, 3.0
FLOOR_SE_W = 0.15                       # an absolute 1-sigma floor: E60's own run-to-run repeatability
LAM = 0.0                               # declared: a fitted overlap came out at -0.03, zero to within 3%
CAL_KINDS = {("fp32", "signs"), ("fp16", "randn"), ("int8", "full"),
             ("fp16", "ones"), ("int8", "ones"), ("fp16", "zeros"), ("int8", "zeros")}
# the 1-sigma relative band on the (operand bits + product sign) terms of an OUT-OF-SAMPLE kind
REL_BAND = {"fp32": 0.12, "fp16": 0.30, "int8": 0.30}
# the error on the calibration TARGET itself, which every kind of that format inherits
TARGET_SE = {"fp32": ZR["step_se_w"], "fp16": E64_FIT_RMS_W * XFER * 2 ** 0.5,
             "int8": E64_FIT_RMS_W * XFER * 2 ** 0.5}


def popcount32(x):
    x = np.asarray(x, dtype=np.uint32)
    x = x - ((x >> np.uint32(1)) & np.uint32(0x55555555))
    x = (x & np.uint32(0x33333333)) + ((x >> np.uint32(2)) & np.uint32(0x33333333))
    x = (x + (x >> np.uint32(4))) & np.uint32(0x0F0F0F0F)
    return ((x * np.uint32(0x01010101)) >> np.uint32(24)).astype(np.int64)


def words_of(raw):
    w = np.frombuffer(raw, dtype="<u4")
    return w[:WORDS].reshape(N, N).astype(np.uint64), w[WORDS:].reshape(N, N).astype(np.uint64)


def issue_streams(aw, bw, t):
    a, b = np.asarray(aw, dtype=np.uint64), np.asarray(bw, dtype=np.uint64)
    if t == "int8":
        return a.T.reshape(-1).copy(), np.repeat(b, N, axis=0)
    b3 = b.reshape(N, 2, 8)
    return (np.repeat(a.T.reshape(-1), 2),
            np.broadcast_to(b3[:, None, :, :], (N, N, 2, 8)).reshape(-1, 8).copy())


def gate_mask(a_seq, b_seq, t):
    if t == "int8":
        return (a_seq[:, None] == 0) | ((b_seq[:, 0:8] == 0) & (b_seq[:, 8:16] == 0))
    return (a_seq[:, None] == 0) | (b_seq == 0)


def live_slots(gated, t):
    """Liveness per (micro-op, column slot).  int8's eight gate bits each cover the pair (l, l+8)."""
    return np.concatenate([~gated, ~gated], axis=1) if t == "int8" else ~gated


def sign_bits(w, t):
    """The sign bit of every element of a 32-bit word, as (…, E)."""
    E, size = TYPES[t]
    ew = 32 // E
    return np.stack([((np.asarray(w, dtype=np.uint64) >> np.uint64(e * ew + ew - 1)) & np.uint64(1))
                     for e in range(E)], axis=-1).astype(np.int64)


def features(aw, bw, t, arm):
    """fA[32], fB[32], q (product-sign changes / 4,096), g, bus bits."""
    a_seq, b_seq = issue_streams(aw, bw, t)
    gated = gate_mask(a_seq, b_seq, t)
    live = live_slots(gated, t).astype(np.int64)
    da = (a_seq ^ np.roll(a_seq, -1)).astype(np.uint32)
    db = (b_seq ^ np.roll(b_seq, -1, axis=0)).astype(np.uint32)
    bits = np.arange(32, dtype=np.uint32)
    da_b = ((da[:, None] >> bits[None, :]) & np.uint32(1)).astype(np.int64)
    db_b = ((db[:, :, None] >> bits[None, None, :]) & np.uint32(1)).astype(np.int64)
    if arm == "bus":
        fa = da_b.sum(axis=0) * SLOTS[t]
        fb = db_b.sum(axis=(0, 1))
        wgt = np.ones_like(live)
    else:
        fa = (da_b * live.sum(axis=1)[:, None]).sum(axis=0)
        fb = (db_b * live[:, :, None]).sum(axis=(0, 1))
        wgt = live
    # the product's sign, per element and column-slot-cycle
    sa = sign_bits(a_seq, t)[:, None, :]                      # (microops, 1, E)
    sb = sign_bits(b_seq, t)                                   # (microops, slots, E)
    p = (sa ^ sb)
    dp = (p != np.roll(p, -1, axis=0)).astype(np.int64)
    q = float((dp * wgt[:, :, None]).sum()) / SLOT_CYCLES
    bus = int(popcount32(da).sum() * SLOTS[t] + popcount32(db).sum())
    return fa, fb, q, float(gated.mean()), bus


def price_lists(t):
    """Per-flip prices for the 32 positions of a lane operand word, W per flip per op, carrying r_T."""
    wb32 = np.array(E65_B) / B_DENOM
    wa32 = np.array(E67_A) / (A_DENOM * (2.0 if t == "int8" else 1.0))
    if t == "fp32":
        return wa32, wb32
    E, _ = TYPES[t]
    ew = 32 // E
    if t == "fp16":
        m, e = 10, 5
        src = [22 - (m - 1 - b) for b in range(m)] + [23 + b for b in range(e)] + [31]
    else:
        m, e = 7, 0
        src = [22 - (m - 1 - b) for b in range(m)] + [31]
    assert len(src) == ew
    wa, wb = np.zeros(32), np.zeros(32)
    for el in range(E):
        for b, j in enumerate(src):
            wa[el * ew + b] = wa32[j] * R_T[t]
            wb[el * ew + b] = wb32[j] * R_T[t]
    return wa, wb


def phi(s, w):
    return w * (1.0 - math.exp(-s / w)) if w > 0 and s > 0 else 0.0


def solve_winf(s, target, lo=0.05, hi=400.0):
    """W such that Phi(s; W) = target.  Phi is increasing in W with limit s, so target < s is needed."""
    if target >= s:
        return None
    for _ in range(300):
        mid = (lo + hi) / 2
        if phi(s, mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


class Model:
    def __init__(self, wa_inf, wb_inf, lam, sigma, u, arm):
        self.wa_inf, self.wb_inf, self.lam, self.sigma, self.u, self.arm = wa_inf, wb_inf, lam, sigma, u, arm

    def dw(self, fa, fb, q, g, t, alpha):
        wa, wb = price_lists(t)
        beta = R_T[t] * alpha
        s_a = float(np.dot(fa, wa)) * alpha
        s_b = float(np.dot(fb, wb)) * alpha
        n_a = 2.0 if t == "int8" else 1.0                      # int8's A denominator is 4,096, not 2,048
        wia, wib = self.wa_inf * n_a * beta, self.wb_inf * beta
        pa, pb = phi(s_a, wia), phi(s_b, wib)
        flip = pa + pb - self.lam * min(pa, pb)        # self.lam is LAM = 0: the two sides simply add
        sign = self.sigma * beta * q
        return {"S_A_w": s_a, "S_B_w": s_b, "winf_a_w": wia, "winf_b_w": wib, "phi_a_w": pa, "phi_b_w": pb,
                "flip_w": flip, "sign_w": sign, "ungate_w": self.u[t] * (1.0 - g),
                "dw_w": self.u[t] * (1.0 - g) + flip + sign}


def host_tiles(kind, rng):
    """The fp32 value rules of workloads/sparsity/host/main.cpp:458-478, drawn with numpy instead of
    libstdc++ (E64's own tiles were never dumped).  Fill order: the A buffer then the B buffer, 4 bytes a
    value, 256 values each (main.cpp:480-485)."""
    n = 2 * WORDS
    if kind == "zeros":
        v = np.zeros(n)
    elif kind == "ones":
        v = np.ones(n)
    elif kind == "randn":
        v = rng.standard_normal(n)
    elif kind == "uniform":
        v = rng.random(n)
    elif kind == "sparse75":
        v = np.where(rng.integers(0, 4, n) != 0, 0.0, rng.standard_normal(n))
    elif kind == "signs":
        v = np.where(rng.integers(0, 2, n) != 0, 1.0, -1.0)
    elif kind == "pow2":
        v = np.ldexp(1.0, rng.integers(0, 17, n) - 8)
    elif kind == "mant":
        v = 1.0 + rng.random(n)
    elif kind in ("a_randn_b_ones", "a_ones_b_randn"):
        isb = np.zeros(n, dtype=bool)
        isb[WORDS:] = True
        r = rng.standard_normal(n)
        v = np.where(isb, 1.0, r) if kind == "a_randn_b_ones" else np.where(isb, r, 1.0)
    else:
        raise KeyError(kind)
    return words_of(v.astype(np.float32).tobytes())


def check_e70_rungs():
    lq = {1: 0.625, 2: 1.138, 3: 1.543, 4: 2.026, 6: 2.970, 8: 3.886, 12: 7.078, 16: 15.122, 23: 40.384}
    alq = {1: 0.459, 2: 1.599, 4: 3.150, 8: 5.784, 12: 9.025, 16: 15.913, 23: 32.852}
    rows = [{"item": "lq_h%d" % h, "e70_S_w": s, "from_this_file": round(sum(E65_B[:h]), 4),
             "d_w": round(sum(E65_B[:h]) - s, 4)} for h, s in sorted(lq.items())]
    rows += [{"item": "alq_h%d" % h, "e70_S_w": s, "from_this_file": round(sum(E67_A[:h]), 4),
              "d_w": round(sum(E67_A[:h]) - s, 4)} for h, s in sorted(alq.items())]
    return {"rungs": rows, "n": len(rows), "max_abs_d_w": max(abs(r["d_w"]) for r in rows),
            "what": ("E70's own additive sums S for its nine lq and seven alq rungs, re-derived from this "
                     "file's E65/E67 price lists position by position.  The residual is the 2 dp rounding of "
                     "the published lists.  E70's seven spread (ls) rungs use a mask its item table defines "
                     "and are not re-derived here.")}


def simulate_e64(p, tdp, tau, dt, t_end=12.0, t_from=4.0, start_avg=24.0, ramp_at=0.4):
    """surface_hpl.py simulate(), copied so this file stands alone; asserted against the import in main()."""
    pts = (600, 700, 800)
    k, avg, t, acc, n, climbing = 0, start_avg, 0.0, 0.0, 0.0, True
    while t < t_end:
        if t >= ramp_at:
            if climbing:
                if avg > tdp:
                    climbing = False
                elif k < 2:
                    k += 1
                else:
                    climbing = False
            else:
                if avg > tdp and k > 0:
                    k -= 1
                elif avg < tdp and k < 2:
                    k += 1
        avg += (p[pts[k]] - avg) * (1 - math.exp(-dt / tau))
        if t >= t_from:
            acc += pts[k]
            n += 1
        t += dt
    return acc / n if n else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kinds", default="../../../../tools/claims-v3/kinds")
    ap.add_argument("--e64", default="../2026-10-23-e64-horace-power-limit")
    ap.add_argument("--hpl", default="../../../../tools/claims-v3/hpl")
    ap.add_argument("--out", default="predictions.json")
    ap.add_argument("--draws", type=int, default=24)
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    kdir = os.path.join(here, a.kinds)
    K = json.load(open(os.path.join(kdir, "kinds.json")))
    sys.path.insert(0, os.path.join(here, a.hpl))
    import surface_hpl as SH
    import surface_hpl_t as ST

    out = {"model_id": MODEL_ID, "date": "2026-10-31", "lane": "Q130(c)",
           "what": ("switching power, energy and clock predicted per (format, kind) BEFORE E78 (aifoundry3, "
                    "600 MHz pinned) and E80 (aifoundry2, its own governor) run.  No card was touched; "
                    "nothing here is a measurement."),
           "basis": ("every switching W is over that TYPE's OWN zero-data level (E67's `anchor_zeros`: a "
                     "running kernel on zero operands), at 600 MHz and 521.8 mV on aifoundry3"),
           "kinds_spec": {"revision": K.get("revision"), "commit": "7d9c0d9e",
                          "path": "tools/claims-v3/kinds/kinds.json"},
           "inputs": {}, "calibration": {}, "checks": {}, "predictions": {}, "speed": {}}

    # ── 0. every tile verified, and this file's stream / gate / bus counter against kinds.json
    bad, tiles = [], {}
    for t in ("fp32", "fp16", "int8"):
        for kind, rec in K["kinds"][t].items():
            raw = open(os.path.join(kdir, rec["file"]), "rb").read()
            if hashlib.sha256(raw).hexdigest() != rec["sha256"]:
                bad.append([t, kind, "sha256"])
                continue
            aw, bw = words_of(raw)
            tiles[(t, kind)] = (aw, bw)
            fa, fb, q, g, bus = features(aw, bw, t, "bus")
            if bus != rec["stats"]["bus_bits_per_op"]:
                bad.append([t, kind, "bus %d != %d" % (bus, rec["stats"]["bus_bits_per_op"])])
            if abs(g - rec["stats"]["gated_lane_frac"]) > 2e-6:
                bad.append([t, kind, "gate %.6f != %.6f" % (g, rec["stats"]["gated_lane_frac"])])
            if int(fa.sum() + fb.sum()) != bus:
                bad.append([t, kind, "histogram %d != bus %d" % (int(fa.sum() + fb.sum()), bus)])
    out["checks"]["kinds_json_reproduced"] = {
        "kinds": len(tiles), "failures": bad,
        "what": ("sha256 of all 51 tiles, plus this file's own stream, gate and bus counts against "
                 "kinds.json's stats.bus_bits_per_op and stats.gated_lane_frac for every kind")}
    out["checks"]["e70_additive_sums"] = check_e70_rungs()

    # ── 1. the fp32 host kinds, as stand-in tiles, both gating arms
    rng = np.random.default_rng(20261031)
    HK = {}
    for kind in ("zeros", "ones", "randn", "sparse75", "signs", "pow2", "mant", "uniform",
                 "a_randn_b_ones", "a_ones_b_randn"):
        HK[kind] = {arm: [features(*host_tiles(kind, np.random.default_rng(20261031 + 7919 * i)),
                                   "fp32", arm) for i in range(a.draws)] for arm in ("bus", "gate")}
    wa32, wb32 = price_lists("fp32")

    def sums(f):
        fa, fb, q, g, _ = f
        return float(np.dot(fa, wa32)), float(np.dot(fb, wb32)), q, g

    # ── 2. calibration, fp32: WA, WB on E70's nrd_a / nrd_b; lam on randn; sigma on signs.  A fixed point.
    cal_arms = {}
    for arm in ("bus", "gate"):
        mean = {k: [st.mean(x) for x in zip(*[sums(f) for f in HK[k][arm]])] for k in HK}
        sA_r, _, q_a, _ = mean["a_randn_b_ones"]       # A random, B constant 1.0  -> E70's nrd_a
        _, sB_r, q_b, _ = mean["a_ones_b_randn"]       # A constant 1.0, B random  -> E70's nrd_b
        sA_n, sB_n, q_n, _ = mean["randn"]             # both random               -> the split's 16.104 W
        sA_s, sB_s, q_s, _ = mean["signs"]             # +-1.0f: only the sign moves
        sigma, lam, trace = 6.0, LAM, []
        tgt = (st.mean(E64_C[("fp32", "signs")]) - st.mean(E64_C[("fp32", "zeros")])) * XFER
        for _ in range(400):
            wa_inf = solve_winf(sA_r, NRD_A - sigma * q_a)
            wb_inf = solve_winf(sB_r, NRD_B - sigma * q_b)
            if wa_inf is None or wb_inf is None:
                trace.append("unsolvable at sigma %.3f" % sigma)
                break
            pas, pbs = phi(sA_s, wa_inf), phi(sB_s, wb_inf)
            new = (tgt - U_FP32 - (pas + pbs - lam * min(pas, pbs))) / q_s
            if abs(new - sigma) < 1e-10:
                sigma = new
                break
            sigma = 0.5 * sigma + 0.5 * new
        # fp32 randn is now a CHECK, not a fit: the split's own 16.104 +- 0.37 W flip term
        pa, pb = phi(sA_n, wa_inf), phi(sB_n, wb_inf)
        randn_pred = pa + pb - lam * min(pa, pb) + sigma * q_n
        cal_arms[arm] = {"wa_inf_w": wa_inf, "wb_inf_w": wb_inf, "lam": lam, "sigma_w": sigma,
                         "S_A_randn_w": sA_r, "S_B_randn_w": sB_r,
                         "q": {"nrd_a": q_a, "nrd_b": q_b, "randn": q_n, "signs": q_s},
                         "randn_flip_term_check": {"predicted_w": round(randn_pred, 3),
                                                   "measured_w": ZR["flip_w"], "se_w": ZR["step_se_w"],
                                                   "resid_w": round(randn_pred - ZR["flip_w"], 3)},
                         "trace": trace}
    # ── 3. the gating arm, selected on E64's fp32 sparse75 (an fp32 kind, which rule 5 of the header allows)
    scores = {}
    for arm in ("bus", "gate"):
        c = cal_arms[arm]
        M = Model(c["wa_inf_w"], c["wb_inf_w"], c["lam"], c["sigma_w"], {"fp32": U_FP32}, arm)
        rows = []
        for kind in HK:
            vals = [M.dw(*HK[kind][arm][i][:4], "fp32", 1.0)["dw_w"] for i in range(a.draws)]
            meas = (st.mean(E64_C[("fp32", kind)]) - st.mean(E64_C[("fp32", "zeros")])) * XFER
            rows.append({"kind": kind, "pred_w": round(st.mean(vals), 3),
                         "draw_sd_w": round(st.pstdev(vals), 3), "e64_w": round(meas, 3),
                         "resid_w": round(st.mean(vals) - meas, 3),
                         "in_sample": kind == "signs"})
        oos = [r for r in rows if not r["in_sample"] and r["kind"] != "zeros"]
        scores[arm] = {"calibration": {k: v for k, v in c.items() if k != "trace"}, "rows": rows,
                       "oos_rms_w": round((sum(r["resid_w"] ** 2 for r in oos) / len(oos)) ** 0.5, 3),
                       "sparse75_resid_w": [r["resid_w"] for r in rows if r["kind"] == "sparse75"][0]}
    ARM = min(scores, key=lambda x: abs(scores[x]["sparse75_resid_w"]))
    C = cal_arms[ARM]
    out["calibration"]["gating_arm"] = {
        "selected": ARM, "selected_on": "E64's fp32 sparse75, the only measured kind that is mostly gated",
        "scores": scores,
        "what_the_arms_are": ("`bus`: a gated column-slot-cycle still pays its operand-bus flips.  `gate`: it "
                              "pays none of them (vpu_lane.v clock-gates the lane, so its input registers do "
                              "not capture).  E78's sparse kinds settle it.")}
    out["calibration"]["fp32"] = {
        "wa_inf_w": round(C["wa_inf_w"], 4), "wb_inf_w": round(C["wb_inf_w"], 4),
        "lam": LAM, "sigma_w": round(C["sigma_w"], 4), "u_w": U_FP32,
        "fitted_parameters": 3,
        "anchored_on": {"wa_inf": "E70 nrd_a 7.209 +- 0.015 W (random A, constant B)",
                        "wb_inf": "E70 nrd_b 10.785 +- 0.024 W (constant A, random B)",
                        "sigma": "E64's fp32 `signs` (+-1.0f), 13.10 W over zeros, carried to a3's voltage",
                        "lam": "DECLARED ZERO: a fitted overlap came out at -0.029, zero to within 3%",
                        "u": "E67/E70 anchors: a running kernel on zero data against one on a constant nonzero"},
        "randn_is_a_check": C["randn_flip_term_check"],
        "e70_fit_for_comparison": {"winf_a_w": WINF_A_E70, "winf_b_w": WINF_B_E70,
                                   "note": ("E70's own fits, which its own top rungs EXCEED (nrd_a 7.209 > "
                                            "6.37, nrd_b 10.785 > 10.52) and whose A-side FORM E70 rejects; "
                                            "they are the sensitivity arm, not the primary")},
        "sign_term_reading": ("sigma = %.2f W is what a product-sign change costs when it happens on every "
                              "one of the 4,096 column-slot-cycles.  The operand-bus price of the sign bit "
                              "itself is 0.56 W a position (E65 bit 31) -- %.0fx less.  This is the term no "
                              "per-position price list can carry, because E65 and E67 measured every mask "
                              "against a CONSTANT other operand."
                              % (C["sigma_w"], C["sigma_w"] / 0.56))}
    M32 = Model(C["wa_inf_w"], C["wb_inf_w"], C["lam"], C["sigma_w"], {"fp32": U_FP32}, ARM)
    oos = [r for r in scores[ARM]["rows"] if not r["in_sample"] and r["kind"] != "zeros"]
    rel = [abs(r["resid_w"]) / r["e64_w"] for r in oos if r["e64_w"] > 2.0]
    out["calibration"]["fp32_out_of_sample"] = {
        "kinds": [r["kind"] for r in oos], "rms_w": scores[ARM]["oos_rms_w"],
        "median_rel": round(st.median(rel), 4), "max_rel": round(max(rel), 4),
        "what": ("the model, with its four fp32 numbers fixed, against E64's measured kinds it was NOT fitted "
                 "on.  a_randn_b_ones and a_ones_b_randn are the card-transfer check: E70's one-sided "
                 "random-operand steps measured on aifoundry3 against E64's measured on aifoundry2.")}

    # ── 4. calibration, fp16 and int8: U_T from (ones - zeros), alpha_T from randn.  Nothing else.
    U_T, ALPHA, perfmt = {"fp32": U_FP32}, {"fp32": 1.0}, {}
    for t in ("fp16", "int8"):
        u = (st.mean(E64_C[(t, "ones")]) - st.mean(E64_C[(t, "zeros")])) * XFER
        target = (st.mean(E64_C[(t, "randn")]) - st.mean(E64_C[(t, "zeros")])) * XFER
        base = {"fp16": "randn", "int8": "full"}[t]
        f = features(*tiles[(t, base)], t, ARM)
        U_T[t] = u
        M = Model(C["wa_inf_w"], C["wb_inf_w"], C["lam"], C["sigma_w"], U_T, ARM)
        lo, hi = 1e-4, 80.0
        for _ in range(300):
            mid = (lo + hi) / 2
            if M.dw(*f[:4], t, mid)["dw_w"] < target:
                lo = mid
            else:
                hi = mid
        ALPHA[t] = (lo + hi) / 2
        fz = features(*tiles[(t, "zeros")], t, ARM)
        fo = features(*tiles[(t, "ones")], t, ARM)
        perfmt[t] = {
            "u_w": round(u, 3), "u_se_w": round(E64_FIT_RMS_W * XFER * 2 ** 0.5, 3),
            "u_from": "E64 (c_ones - c_zeros) x %.5f, ONE run each" % XFER,
            "randn_target_w": round(target, 3), "calibrating_kind": base,
            "r_t": round(R_T[t], 4), "alpha": round(ALPHA[t], 4), "beta": round(R_T[t] * ALPHA[t], 4),
            "alpha_reading": ("alpha = 1 would mean the significand-width scaling r_T is exactly right; this "
                              "is a prediction E79's own fp16/int8 price lists can falsify"),
            "zeros_check_w": round(M.dw(*fz[:4], t, ALPHA[t])["dw_w"], 4),
            "ones_check_w": round(M.dw(*fo[:4], t, ALPHA[t])["dw_w"], 3)}
    out["calibration"]["per_format"] = perfmt

    # ── 4b. the SAME calibration under the other gating arm, so every kind carries both and E78 can settle it
    ALT = "bus" if ARM == "gate" else "gate"
    CA = cal_arms[ALT]
    U_ALT = dict(U_T)
    A_ALT = {"fp32": 1.0}
    M_ALT = Model(CA["wa_inf_w"], CA["wb_inf_w"], CA["lam"], CA["sigma_w"], U_ALT, ALT)
    for t in ("fp16", "int8"):
        target = (st.mean(E64_C[(t, "randn")]) - st.mean(E64_C[(t, "zeros")])) * XFER
        f = features(*tiles[(t, {"fp16": "randn", "int8": "full"}[t])], t, ALT)
        lo, hi = 1e-4, 80.0
        for _ in range(300):
            mid = (lo + hi) / 2
            if M_ALT.dw(*f[:4], t, mid)["dw_w"] < target:
                lo = mid
            else:
                hi = mid
        A_ALT[t] = (lo + hi) / 2
    out["calibration"]["alt_gating_arm"] = {
        "arm": ALT, "wa_inf_w": round(CA["wa_inf_w"], 4), "wb_inf_w": round(CA["wb_inf_w"], 4),
        "sigma_w": round(CA["sigma_w"], 4), "alpha": {k: round(v, 4) for k, v in A_ALT.items()},
        "what": ("the whole model re-calibrated under the other reading of the gate, carried per kind as "
                 "`switching_w_alt_gating_arm`.  The kinds where the two arms disagree most are exactly the "
                 "ones E78 should run first: they settle whether a clock-gated lane still pays its operand "
                 "bus.")}
    out["calibration"]["u_per_format"] = {
        "fp32_w": U_FP32, "fp32_se_w": U_FP32_SE, "fp16_w": round(U_T["fp16"], 3),
        "int8_w": round(U_T["int8"], 3),
        "fp32_from_e64_for_comparison_w": round((st.mean(E64_C[("fp32", "ones")]) -
                                                 st.mean(E64_C[("fp32", "zeros")])) * XFER, 3),
        "reading": ("int8's lane un-gating term is %.2f W against fp32's 8.555 -- %.0fx smaller.  int8 runs on "
                    "TIMA with the txfma clock OFF (vpu_tensorfma.v:157-166, 626-628), so most of what fp32 "
                    "pays merely to have a live lane is not switched on at all.  It rests on ONE E64 run per "
                    "point, so its interval is +-%.2f W."
                    % (U_T["int8"], U_FP32 / U_T["int8"], E64_FIT_RMS_W * XFER * 2 ** 0.5))}
    MODEL = Model(C["wa_inf_w"], C["wb_inf_w"], C["lam"], C["sigma_w"], U_T, ARM)

    # ── 5. the governor: E64's registered burst, E64-T1's sustained
    gt = ST.build(json.load(open(os.path.join(here, a.e64, "results.json")))["runs"], GAMMA)
    out["speed"]["model"] = {"burst": "surface_hpl.py simulate, tau 1.3 s, pass 0.24 s, 65 W, cool die, "
                                      "mean clock 4-12 s on p_f = E64's B_f + c*s_f",
                             "sustained": "surface_hpl_t.py at gamma 3.0, die a state on E64's thermal line, "
                                          "tau_th 14 s, thermal limb trip 66 C, mean clock 40-80 s",
                             "gamma": GAMMA, "B_t1": gt["B"], "governor_t1": gt["governor"],
                             "die_line": gt["die_line"], "tau_th": gt["tau_th"],
                             "e64_thermal_line": "die = 41.88 + 0.4696 C per W (surface.txt:27)",
                             "clamp_band_w": [49.23, 51.36],
                             "clamp_band_source": "2026-10-31-q130-governor-thermal-branch/clamp-band.json"}
    out["checks"]["simulate_port"] = {
        "this_file_mhz": round(simulate_e64({600: 50.3, 700: 64.2, 800: 83.0}, 65.0, 1.3, 0.24), 3),
        "surface_hpl_mhz": round(SH.simulate({600: 50.3, 700: 64.2, 800: 83.0}, 65.0, 1.3, 0.24,
                                             t_end=12.0, t_from=4.0), 3),
        "e64_cap_table_fp32_randn_65w_mhz": 700.0,
        "what": "this file's copy of E64's governor against the import, on E64's own fp32 randn powers"}

    def speed(c_a2):
        pw = {f: E64_B[f] + c_a2 * E64_S[f] for f in (600, 700, 800)}
        burst = simulate_e64(pw, 65.0, E64_GOV["tau_s"], E64_GOV["pass_s"])
        pm = ST.p_maker(gt["B"], c_a2, GAMMA)
        sus = ST.simulate(pm, 65.0, gt["governor"]["tau_s"], gt["governor"]["pass_s"], t_end=80.0,
                          t_from=40.0, T0=T_REF, therm=gt["die_line"], tau_th=gt["tau_th"]["tau_th_s"],
                          trip=T_TRIP)
        bt = ST.simulate(pm, 65.0, gt["governor"]["tau_s"], gt["governor"]["pass_s"], t_end=6.5, t_from=1.5,
                         T0=T_REF, therm=gt["die_line"], tau_th=gt["tau_th"]["tau_th_s"], trip=T_TRIP)
        return pw, burst, sus, bt

    # the E64 cells the speed path reproduces, as its own check
    chk = []
    for (t, k), cs in sorted(E64_C.items()):
        if t == "fp32" and k not in ("zeros", "ones", "randn"):
            continue
        pw, burst, sus, _ = speed(st.mean(cs))
        chk.append({"cell": "%s/%s" % (t, k), "c_w": round(st.mean(cs), 3),
                    "burst_mhz": round(burst, 1), "sustained_mhz": round(sus["mhz"], 1),
                    "sustained_die_c": round(sus["die_c"], 2)})
    out["checks"]["speed_on_e64_own_c"] = {
        "rows": chk,
        "measured_sustained_mhz": {"fp32/zeros": 800.0, "fp32/ones": 737.9, "fp32/randn": 600.0,
                                   "fp16/zeros": 794.4, "fp16/ones": 737.1, "fp16/randn": 600.5,
                                   "int8/zeros": 800.0, "int8/ones": 800.0, "int8/randn": 763.2},
        "what": "the same two simulations on E64's OWN fitted c, against its measured SUS clocks"}

    # ── 6. the predictions
    preds = {}
    for t in ("fp32", "fp16", "int8"):
        for kind in sorted(K["kinds"][t]):
            rec = K["kinds"][t][kind]
            f = features(*tiles[(t, kind)], t, ARM)
            fa, fb, q, g, bus = f
            p = MODEL.dw(fa, fb, q, g, t, ALPHA[t])
            dw = p["dw_w"]
            fz = features(*tiles[(t, kind)], t, ALT)
            dw_alt = M_ALT.dw(*fz[:4], t, A_ALT[t])["dw_w"]
            rep = rec.get("replicates") or {}
            gsd = 0.0
            if isinstance(rep, dict):
                gr = rep.get("gated_lane_frac")
                if isinstance(gr, dict) and isinstance(gr.get("sd"), (int, float)):
                    gsd = float(gr["sd"])
            insample = (t, kind) in CAL_KINDS
            band = (0.0 if insample else REL_BAND[t]) * (p["flip_w"] + p["sign_w"])
            e_law = E70_LAW_RMS_W * (1.0 if t == "fp32" else R_T[t] * ALPHA[t]) * (1 - g)
            e_u = (U_FP32_SE if t == "fp32" else TARGET_SE[t]) * (1 - g)
            e_tgt = TARGET_SE[t] * min(1.0, (p["flip_w"] + p["sign_w"]) /
                                       max(1e-9, MODEL.dw(*features(*tiles[(t, {"fp32": "randn", "fp16": "randn", "int8": "full"}[t])], t, ARM)[:4], t, ALPHA[t])["flip_w"]
                                           + MODEL.dw(*features(*tiles[(t, {"fp32": "randn", "fp16": "randn", "int8": "full"}[t])], t, ARM)[:4], t, ALPHA[t])["sign_w"]))
            err = (band ** 2 + e_law ** 2 + e_u ** 2 + e_tgt ** 2 + (U_T[t] * gsd) ** 2
                   + FLOOR_SE_W ** 2) ** 0.5
            rate = OP_RATE_600 * (546.0 / CYCLES_PER_OP[t])
            pj = dw / rate * 1e12
            c_a2 = st.mean(E64_C[(t, "zeros")]) + dw / XFER
            pw, burst, sus, bt = speed(c_a2)
            preds["%s/%s" % (t, kind)] = {
                "type": t, "kind": kind, "tier": rec["tier"], "rule": rec["rule"],
                "tile_sha256": rec["sha256"], "gated_lane_frac": round(g, 6), "bus_bits_per_op": bus,
                "product_sign_rate": round(q, 5),
                "S_A_w": round(p["S_A_w"], 4), "S_B_w": round(p["S_B_w"], 4),
                "term_ungating_w": round(p["ungate_w"], 4), "term_operand_bits_w": round(p["flip_w"], 4),
                "term_product_sign_w": round(p["sign_w"], 4),
                "switching_w_600mhz_a3": round(dw, 3),
                "switching_w_alt_gating_arm": round(dw_alt, 3),
                "gating_arm_spread_w": round(abs(dw_alt - dw), 3),
                "switching_w_ci68": [round(max(0.0, dw - err), 3), round(dw + err, 3)],
                "switching_w_ci95": [round(max(0.0, dw - 2 * err), 3), round(dw + 2 * err, 3)],
                "pj_per_op": round(pj, 1), "pj_per_mac": round(pj / MACS_PER_OP[t], 4),
                "pj_per_op_ci95": [round(max(0.0, dw - 2 * err) / rate * 1e12, 1),
                                   round((dw + 2 * err) / rate * 1e12, 1)],
                "c_w_a2_600mhz": round(c_a2, 3), "p_w_a2": {str(k2): round(v, 2) for k2, v in pw.items()},
                "burst_mhz_65w": round(burst, 0), "burst_mhz_t1": round(bt["mhz"], 0) if bt else None,
                "sustained_mhz": round(sus["mhz"], 0), "sustained_die_c": round(sus["die_c"], 2),
                "sustained_board_w": round(sus["w"], 2),
                "sustained_limit": "thermal" if sus["die_c"] >= T_TRIP - 0.5 else "power",
                "calibration_status": "in sample" if (t, kind) in CAL_KINDS else "out of sample",
                "provisional": t == "int8"}
    out["predictions"] = preds
    out["interval_rule"] = {
        "rel_band": REL_BAND, "target_se_w": {k: round(v, 3) for k, v in TARGET_SE.items()},
        "fp32_oos_median_rel": round(st.median(rel), 4), "fp32_oos_max_rel": round(max(rel), 4),
        "what": ("1 sigma is the quadrature of: (i) a relative band on the (operand bits + product sign) "
                 "terms, zero for a calibration kind, 12% for an out-of-sample fp32 kind (its own measured "
                 "out-of-sample median miss is 6%, max 34% on the smallest value) and 30% for fp16/int8, "
                 "whose whole price list is one fitted scalar; (ii) E70's law fit rms 0.232 W times the live "
                 "fraction; (iii) U's error times the live fraction; (iv) the calibration TARGET's own error "
                 "(fp32 the split's 0.37 W; fp16/int8 E64's single-run 1.19 W), pro-rated by size; (v) the "
                 "gate rate's single-tile sd from kinds.json times U.  ci95 is 2 sigma.  It does NOT cover "
                 "the two structural unknowns: the A-side broadcast weight, and int8's provisional stream.")}
    out["decision_rules"] = {
        "R1": ("E78: the measured switching power over the type's own zeros level is inside `switching_w_ci95` "
               "for at least 70% of the fp32 kinds run, and at least 50% of the fp16 and int8 kinds."),
        "R2": ("E78: the ORDER is right -- Spearman correlation of predicted against measured switching power "
               ">= 0.90 within each format, over every kind run."),
        "R3": ("E78: the gate's signature.  (sparse50 - wsparse50) switching power is >= 2 W in BOTH fp16 and "
               "int8 (wsparse50 gates more, so it must cost less), and |fp32 sparse50 - fp32 wsparse50| "
               "<= 1.0 W, because in fp32 element sparsity IS word sparsity and the two are one kind."),
        "R4": ("E78: int8 (ones - zeros) switching power <= 2.0 W, against fp32's 8.555 W.  This is the "
               "sharpest structural prediction in this file and the one most likely to fail, because it "
               "rests on a single E64 run per point (+- 1.19 W)."),
        "R5": ("E79: alpha_fp16 and alpha_int8 land in [0.5, 2.0] when re-solved against E79's own measured "
               "fp16/int8 per-bit prices -- i.e. the significand-width scaling is right to a factor of two."),
        "R6": ("E78: the product-sign term is real.  fp32 `neg_ones` costs within 1 W of `ones` (no sign "
               "CHANGE: every element is -1.0, so the product's sign never moves), while int8 `ternary` and "
               "`highbit`, whose signs do change, cost at least 1 W more than int8 `ones`."),
        "R9": ("E78: the gate's reach.  fp32 `a_randn_b_zeros` is 100% gated by the B side while its A "
               "operand bus keeps moving (27,920 bits an op).  The `gate` arm says it costs ~0 W over zeros; "
               "the `bus` arm says it costs several watts.  Whichever E78 measures SELECTS the arm, and every "
               "kind's `switching_w_alt_gating_arm` is this file's prediction under the other one.  This is "
               "the single most informative cell in the matrix and E78 should run it first."),
        "R7": ("E80: predicted burst MHz within 25 MHz of measured for at least 70% of the cells run, and "
               "every cell predicted at 800 MHz measures >= 790 MHz."),
        "R8": ("E80: the sustained LIMIT is called right (thermal vs power) for every cell, and the predicted "
               "sustained MHz is within 40 MHz of measured for at least 70% of them."),
        "failure_is_reported_as_failure": True}
    out["departures"] = [
        ("E64's own tiles were never dumped, so the fp32 scoring tiles for its ten host kinds are STAND-INS "
         "drawn from the host's own rules (main.cpp:458-478) with numpy, not libstdc++'s distributions.  "
         "Each row carries its draw sd over %d draws." % a.draws),
        ("The law's curvature is anchored on E70's measured nrd_a / nrd_b rather than on E70's own fitted "
         "W-infinity, because E70's own top rungs and those two measurements both sit ABOVE its fit and it "
         "warns that the fit is not a ceiling.  E70's 6.37 / 10.52 W are the sensitivity arm."),
        ("E70 REJECTS the saturating FORM on the A side (its increments accelerate).  The A arm is declared, "
         "not selected.  rho = 1.246 is the alternative pricing and the x8 / x16 broadcast multiplier is a "
         "counting convention, not a measurement: E78 must validate the A-side weight."),
        ("The product-sign term is NEW here.  It makes E64's fp32 `signs` a calibration kind, so fp32 now "
         "has four fitted numbers (WA, WB, lam, sigma) against six out-of-sample measured kinds."),
        ("int8's bus and Hamming figures are PROVISIONAL in kinds.json (they rest on the reconstructed "
         "256-micro-op / 16-slot TIMA stream), so every int8 switching prediction here is provisional with "
         "them.  Its gated_* figures are not."),
        ("gamma = 3.0 is this lane's declared choice among E64-T1's arms, on its out-of-sample sustained rms "
         "and E64's own within-run busy slope (3.12).  It is not a figure E64-T1 itself registers."),
        ("The sustained predictions inherit E69's FAILED drift check: the same cell read 49.38 W at 65.4 C on "
         "23 Oct and 51.89 W at 65.2 C on 27 Oct, +2.51 W at one die temperature, more than the clamp band's "
         "whole 2.13 W width.  A sustained miss of that size is a thermal-path drift, not a model failure; "
         "E80 should re-read the die line before scoring R8.")]
    json.dump(out, open(os.path.join(here, a.out), "w"), indent=1, sort_keys=False)

    # ── the human report
    print("model %s   gating arm %s   U fp32 %.3f  fp16 %.3f  int8 %.3f W" %
          (MODEL_ID, ARM, U_T["fp32"], U_T["fp16"], U_T["int8"]))
    print("fp32 (3 fitted): WA_inf %.3f  WB_inf %.3f  sigma %.3f W, lam declared 0   (E70's own fits: %.2f / %.2f)"
          % (C["wa_inf_w"], C["wb_inf_w"], C["sigma_w"], WINF_A_E70, WINF_B_E70))
    rc = C["randn_flip_term_check"]
    print("fp32 randn is a CHECK: flip term predicted %.3f W against the split's measured %.3f +- %.2f (resid %+.3f)"
          % (rc["predicted_w"], rc["measured_w"], rc["se_w"], rc["resid_w"]))
    print("alpha fp16 %.3f (beta %.3f)   alpha int8 %.3f (beta %.3f)" %
          (ALPHA["fp16"], R_T["fp16"] * ALPHA["fp16"], ALPHA["int8"], R_T["int8"] * ALPHA["int8"]))
    print("bands: out-of-sample +-%.0f%% (fp32) / +-%.0f%% (fp16, int8) of the flip+sign term, plus the target SE"
          % (100 * REL_BAND["fp32"], 100 * REL_BAND["fp16"]))
    print("checks: kinds.json %d kinds / %d failures;  E70 sums max |d| %.4f W;  governor port %s" %
          (len(tiles), len(bad), out["checks"]["e70_additive_sums"]["max_abs_d_w"],
           out["checks"]["simulate_port"]["this_file_mhz"] == out["checks"]["simulate_port"]["surface_hpl_mhz"]))
    print("\nfp32 scoring against E64's own measured kinds (arm %s):" % ARM)
    print("  %-16s %8s %8s %8s %8s  %s" % ("kind", "pred W", "sd", "E64 W", "resid", ""))
    for r in scores[ARM]["rows"]:
        print("  %-16s %8.2f %8.2f %8.2f %8.2f  %s" %
              (r["kind"], r["pred_w"], r["draw_sd_w"], r["e64_w"], r["resid_w"],
               "fitted" if r["in_sample"] else ""))
    print("  out of sample: rms %.2f W over %d kinds, median |rel| %.1f%%, max %.1f%%" %
          (scores[ARM]["oos_rms_w"], len(oos), 100 * st.median(rel), 100 * max(rel)))
    print("\nspeed path on E64's OWN c, against its measured sustained clocks:")
    for r in chk:
        print("  %-12s c %6.2f  burst %5.0f  sustained %5.0f (meas %5.1f)  die %5.2f" %
              (r["cell"], r["c_w"], r["burst_mhz"], r["sustained_mhz"],
               out["checks"]["speed_on_e64_own_c"]["measured_sustained_mhz"]["%s" % r["cell"]],
               r["sustained_die_c"]))
    for t in ("fp32", "fp16", "int8"):
        print("\n%s — predicted switching W over its own zeros at 600 MHz on aifoundry3; clocks on aifoundry2"
              % t)
        print("  %-16s %2s %5s %6s %7s %16s %8s %6s %6s %7s" %
              ("kind", "ti", "gate", "q", "W", "95% interval", "pJ/MAC", "burst", "sust", "limit"))
        for key, p in preds.items():
            if p["type"] != t:
                continue
            print("  %-16s %2d %5.3f %6.3f %7.2f  [%6.2f, %6.2f] %8.3f %6.0f %6.0f %7s%s" %
                  (p["kind"], p["tier"], p["gated_lane_frac"], p["product_sign_rate"],
                   p["switching_w_600mhz_a3"], p["switching_w_ci95"][0], p["switching_w_ci95"][1],
                   p["pj_per_mac"], p["burst_mhz_65w"], p["sustained_mhz"], p["sustained_limit"],
                   "  *fitted" if p["calibration_status"] == "in sample" else ""))
    h = hashlib.sha256(open(os.path.join(here, a.out), "rb").read()).hexdigest()
    print("\n%s sha256 %s" % (a.out, h))
    return 0


if __name__ == "__main__":
    sys.exit(main())
