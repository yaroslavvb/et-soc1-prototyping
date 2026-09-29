#!/usr/bin/env python3
"""Planning model behind DESIGN.md (brief SP4): tensor-op counts, card time and energy per solve, CPU baselines.

Everything here is a prediction built from measured per-op costs (M) in docs/findings/05-claims.md, the energy
manual and SP3's CPU runs, plus the assumptions marked A. Nothing was run on a card. Run:
    python3 docs/research/sparse-parity/design_model.py            # all tables (markdown)
It uses only the standard library and scipy.stats (for the binomial tails of the two-stage screen).

The kernel it prices ("T2 split"): candidate S = R + {j}, R a (k-1)-subset with max(R) = p < j.
Rows of the int8 GEMM are u_R[i] = (-1)^(y_i + sum_{r in R} x_ir), columns are the raw features
v_j[i] = (-1)^(x_ij); C = U^T V gives m - 2 * disagreements for every candidate. Rows are taken in colex order
(so rows sharing max p are contiguous) in tiles of 16; a row tile whose smallest max is p visits the column
tiles from floor((p+1)/16) to n/16 - 1, and each output tile costs ceil(m/64) TensorIMA8A32 ops (16x16x64).
"""
from math import comb, ceil, log, sqrt

# ---------------------------------------------------------------- measured chip constants (M) and assumptions (A)
F = 600e6                 # minion clock on a warm die (M; aifoundry1 card 1 and aifoundry3 never leave it)
MIN_PER_SHIRE = 32
MACS_PER_OP = 16 * 16 * 64
CYC_RESIDENT = 270.0      # int8 op, A held in L1Scp, B streamed through TenB, 1,024 minions (M, E39: 270.00)
CYC_STREAMED = 280.35     # int8 op, A and B both tensor-loaded per op from a shared hot pool (M, E37 mmbench)
BW_PRIVATE = 4.0          # B per minion-cycle when every minion streams private tiles from its shire (M, E37: 511.94 cyc)
E_MAC = 0.30e-12          # J per int8 MAC over idle, random operands (M, E38: 0.26-0.31 by card)
E_BYTE = 3.7e-12          # J per byte tensor-loaded from the shire (D: mmbench int8 27.9 W over idle on a2, 7.3 B/cyc)
E_INSTR = 15e-12          # J per vector/scalar instruction over idle (M range 8-20 pJ, energy manual 3a)
P_IDLE = {"a2 (80 C)": 35.9, "a3 (80 C)": 37.3, "a1c1 (80 C)": 48.9}   # board idle law at 80 C (M, EM 7.1)
LAUNCH_S = 0.56e-3        # launch + wait of an empty kernel on 32 shires (M)
DRAM_BPS = 76e9           # (M)
PCIE_BPS = 8e9            # host<->card, between the staged 5-8 and DMA 12.5 GB/s (M)

# CPU (SP3, i7-11700K, AVX-512 VPOPCNTQ; per-subset single-thread ns against padded 64-bit words W) (M)
CPU_NS = {128: {1: .69, 2: .86, 3: 1.04, 8: 1.90, 24: 2.96},
          256: {1: .54, 2: .77, 3: .90, 4: 1.11, 8: 1.71, 32: 3.28},
          512: {1: .50, 2: .72, 3: .83, 8: 1.68, 24: 2.88, 32: 3.33}}
CPU_MEASURED_1T = {(256, 5, 466): 15.4, (512, 4, 1850): 9.4, (512, 4, 448): 4.7, (512, 5, 218): 288.0,
                   (512, 5, 2151): 1128.0, (1024, 5, 2373): 37080.0}
CPU16_SPEEDUP = (7.0, 8.5, 10.0)  # A: 16 threads on 8 cores vs 1 thread (4 threads measured 3.89x)
CPU_W = {"1T": 40.0, "16T": 150.0}  # A: package watts (i7-11700K PL1 125 W, PL2 251 W); not measured


def cpu_1t(n, k, m):
    if (n, k, m) in CPU_MEASURED_1T:
        return CPU_MEASURED_1T[(n, k, m)]
    W = (m + 63) // 64
    W = W if W <= 4 else (W + 7) // 8 * 8
    tab = CPU_NS[min(CPU_NS, key=lambda x: abs(log(x / n)))]
    ws = sorted(tab)
    if W <= ws[0]:
        ns = tab[ws[0]]
    elif W >= ws[-1]:
        ns = tab[ws[-1]] + (tab[ws[-1]] - tab[ws[-2]]) / (ws[-1] - ws[-2]) * (W - ws[-1])
    else:
        lo = max(w for w in ws if w <= W)
        hi = min(w for w in ws if w >= W)
        ns = tab[lo] if hi == lo else tab[lo] + (tab[hi] - tab[lo]) * (W - lo) / (hi - lo)
    return comb(n, k) * ns * 1e-9


def t2_tiles(n, k):
    """(output tiles, row tiles) of the T2 split with 16-row tiles in colex order (tiles may straddle p)."""
    a = k - 1
    out = rows = 0
    for p in range(a - 1, n - 1):
        t0 = -(-comb(p, a) // 16)
        t1 = -(-comb(p + 1, a) // 16)
        ntiles = t1 - t0
        out += ntiles * (n // 16 - (p + 1) // 16)
        rows += ntiles
    return out, rows


def plan(n, k, m, variant, shires=32):
    """Card time and energy of one full scan. variant: 'private' (M3 baseline) or 'coop' (M4, B loads shared)."""
    S = -(-m // 64)
    mp = 64 * S
    out_tiles, row_tiles = t2_tiles(n, k)
    ops = out_tiles * S
    ops_per_row = ops / row_tiles
    resident = S <= 3                      # A (16 x mp bytes) fits the 48-line L1 scratchpad
    gen_w = 16 * mp / ops_per_row          # generated rows written to the scratchpad, per op
    a_rd = (16 * mp / ops_per_row) if resident else 1024.0
    b_rd = 1024.0 if variant == "private" else 1024.0 / MIN_PER_SHIRE
    bytes_op = a_rd + b_rd + gen_w
    # With S = 3 the resident A fills all 48 L1Scp lines, so the next row tile's A cannot be double-buffered:
    # the tensor unit waits for 16 x mp bytes at the private streaming rate once per row tile.
    stall = 16 * mp / BW_PRIVATE / ops_per_row if S == 3 else 0.0
    cyc = max((CYC_RESIDENT if resident else CYC_STREAMED) + stall, bytes_op / BW_PRIVATE)
    minions = MIN_PER_SHIRE * shires
    t_k = ops * cyc / (minions * F)
    x_bytes = n * mp
    t_fix = LAUNCH_S + x_bytes / PCIE_BPS + shires * x_bytes / DRAM_BPS
    instr = row_tiles * 16 * mp / 32 * 3 + out_tiles * 100 + ops * 6
    e_dyn = ops * MACS_PER_OP * E_MAC + ops * bytes_op * E_BYTE + instr * E_INSTR
    return dict(S=S, mp=mp, ops=ops, macs=ops * MACS_PER_OP, ovh=ops * MACS_PER_OP / (comb(n, k) * m),
                ops_per_row=ops_per_row, resident=resident, bytes_op=bytes_op, cyc=cyc, t=t_k + t_fix,
                t_kernel=t_k, p_dyn=e_dyn / t_k, e_dyn=e_dyn, scp_bytes=x_bytes + MIN_PER_SHIRE * 16 * mp)


def screen(n, k, eta, m1, survivors_target):
    """Two-stage: keep candidates with correlation >= tau on m1 samples. Returns tau, P(secret kept), E[survivors]."""
    from scipy.stats import binom
    N = comb(n, k)
    best = None
    for d in range(m1 + 1):                # keep if disagreements <= d
        surv = N * binom.cdf(d, m1, 0.5)
        if surv > survivors_target:
            break
        best = (m1 - 2 * d, float(binom.cdf(d, m1, eta)), surv)
    return best


def binom_cdf(d, m, p):
    """P(Bin(m, p) <= d), exact enough in floating point (log-space terms; no scipy)."""
    from math import exp, lgamma, log
    if d < 0:
        return 0.0
    if d >= m:
        return 1.0
    lp, lq = log(p), log(1 - p)
    return min(1.0, sum(exp(lgamma(m + 1) - lgamma(i + 1) - lgamma(m - i + 1) + i * lp + (m - i) * lq)
                        for i in range(0, d + 1)))


def screen_at(n, k, eta, m1, tau):
    """Two-stage at a given tau1: keep c1 >= tau1 on m1 samples. -> (P(secret kept), E[survivors])."""
    d = (m1 - tau) // 2                    # c1 >= tau  <=>  disagreements <= (m1 - tau) / 2
    return binom_cdf(d, m1, eta), comb(n, k) * binom_cdf(d, m1, 0.5)


# The two-stage screens the CPU baseline is paired with (review R2, findings 2 and 5): each showcase size at the
# card's m1 and at the CPU's own optimum. (id, n, k, eta, m1, tau1, m)
SCREENS = [("L2", 512, 4, 0.4, 832, 80, 1850), ("L2", 512, 4, 0.4, 1024, 104, 1850),
           ("F5", 256, 5, 0.4, 1024, 104, 1925), ("F5", 256, 5, 0.4, 1280, 144, 1925),
           ("L5", 512, 5, 0.4, 1024, 104, 2151), ("L5", 512, 5, 0.4, 1280, 144, 2151)]


def fmt(t):
    for lim, div, unit in ((1e-3, 1e-6, "us"), (1, 1e-3, "ms"), (120, 1, "s"), (7200, 60, "min")):
        if t < lim:
            return f"{t / div:.3g} {unit}"
    return f"{t / 3600:.3g} h"


LADDER = [  # id, n, k, eta, m (scanned), role
    ("C0", 32, 3, 0.1, 128, "exact check: every correlation dumped; sys_emu, then 1 minion"),
    ("C1", 128, 4, 0.2, 192, "correctness on the card, 20 seeds; A resident"),
    ("L1", 512, 4, 0.3, 448, "strong scaling 1 -> 32 shires (CPU measured)"),
    ("L2", 512, 4, 0.4, 1850, "SP3's S1: strong scaling 2 -> 32 shires; energy burst"),
    ("L3", 512, 5, 0.2, 192, "SP3's S2 as a two-stage screen (m1 = 192, A resident) + verify; weak scaling"),
    ("L3s", 512, 5, 0.2, 218, "S2 single-stage, for comparison"),
    ("L4", 1024, 4, 0.3, 492, "n = 1024"),
    ("L5", 512, 5, 0.4, 2151, "SP3's S3: time-sliced over 3-5 processes"),
    ("L6", 1024, 5, 0.4, 2373, "SP3's S4: timed 1/256 slices only"),
]


def vec_rate(m, ipc):
    """subset-samples/s of the bit-sliced vector path: ~9 instructions per 256 subset-samples for long m
    (load, XOR, carry-save popcount), ~16 when m <= 64 (four 64-bit candidates per register)."""
    per256 = 16 if m <= 64 else 9
    return MIN_PER_SHIRE * 32 * F * ipc * 256 / per256


def p_success(N, m, eta):
    """SP3's model (workloads/sparseparity/proto/sp.py): the secret is the unique best of N subsets."""
    import numpy as np
    from scipy.stats import binom
    t = np.arange(m + 1)
    pT = binom.pmf(t, m, eta)
    return float(np.sum(pT * np.exp((N - 1) * binom.logsf(t, m, 0.5))))


def m99(n, k, eta):
    N = comb(n, k)
    lo, hi = 1, 8
    while p_success(N, hi, eta) < 0.99:
        lo, hi = hi, hi * 2
    while lo < hi:
        mid = (lo + hi) // 2
        if p_success(N, mid, eta) >= 0.99:
            hi = mid
        else:
            lo = mid + 1
    return hi


def main():
    print("## Tensor work (T2 split)\n")
    print("| id | n | k | eta | m | S=ceil(m/64) | ops | MACs / (C(n,k) m) | ops per row tile | A resident | scratchpad per shire |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for i, n, k, e, m, _ in LADDER:
        p = plan(n, k, m, "private")
        print(f"| {i} | {n} | {k} | {e} | {m} | {p['S']} | {p['ops']:.3g} | {p['ovh']:.3f} | {p['ops_per_row']:.1f} | "
              f"{'yes' if p['resident'] else 'no'} | {p['scp_bytes'] / 2**20:.2f} MB |")

    print("\n## Time and energy per solve, 32 shires, 600 MHz\n")
    print("| id | CPU 1T | CPU 16T (A) | card M3 private: cyc/op, time | card M4 coop: cyc/op, time | "
          "vector path (IPC 0.37-0.74) | vs 1T | vs 16T | board W (a2) | J per solve (a2) | J over idle | CPU 16T J (A) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for i, n, k, e, m, _ in LADDER:
        c1 = cpu_1t(n, k, m)
        c16 = c1 / CPU16_SPEEDUP[1]
        pv, co = plan(n, k, m, "private"), plan(n, k, m, "coop")
        pw = P_IDLE["a2 (80 C)"] + pv["p_dyn"]
        pw_c = P_IDLE["a2 (80 C)"] + co["p_dyn"]
        vw = comb(n, k) * max(m, 64)
        vt = f"{fmt(vw / vec_rate(m, 0.74) + LAUNCH_S)}-{fmt(vw / vec_rate(m, 0.37) + LAUNCH_S)}"
        print(f"| {i} | {fmt(c1)} | {fmt(c16)} | {pv['cyc']:.0f}, {fmt(pv['t'])} | {co['cyc']:.0f}, {fmt(co['t'])} | {vt} | "
              f"{c1 / pv['t']:.0f}-{c1 / co['t']:.0f}x | {c16 / pv['t']:.1f}-{c16 / co['t']:.1f}x | "
              f"{pw:.0f} / {pw_c:.0f} | {pw * pv['t']:.3g} / {pw_c * co['t']:.3g} | "
              f"{pv['e_dyn']:.3g} / {co['e_dyn']:.3g} | {CPU_W['16T'] * c16:.3g} |")

    print("\n## Strong scaling, M3 private variant (kernel + fixed costs)\n")
    print("| id | 1 | 2 | 4 | 8 | 16 | 32 shires | efficiency at 32 |")
    print("|---|---|---|---|---|---|---|---|")
    for i, n, k, e, m, _ in LADDER:
        ts = [plan(n, k, m, "private", s)["t"] for s in (1, 2, 4, 8, 16, 32)]
        print(f"| {i} | " + " | ".join(fmt(t) for t in ts) + f" | {ts[0] / (32 * ts[-1]):.2f} |")

    print("\n## Two-stage screen (stage 1 on the card, stage 2 on the host)\n")
    for (n, k, e, m1, target, m_full) in [(512, 5, 0.2, 192, 1e5, 218), (512, 4, 0.3, 192, 3e7, 448),
                                          (512, 5, 0.4, 1280, 1e7, 2151), (512, 4, 0.4, 832, 1e7, 1850),
                                          (1024, 4, 0.3, 256, 1e7, 492)]:
        tau, pk, surv = screen(n, k, e, m1, target)
        s1p, s1c = plan(n, k, m1, "private"), plan(n, k, m1, "coop")
        full_p, full_c = plan(n, k, m_full, "private"), plan(n, k, m_full, "coop")
        verify = surv * m_full / 5e11 / 8.5 + surv * 8 / PCIE_BPS
        print(f"- ({n},{k},{e}) m1={m1}: keep c >= {tau}; P(secret kept) = {pk:.4f}; E[survivors] = {surv:.3g}; "
              f"stage 1 {fmt(s1p['t'])} private / {fmt(s1c['t'])} coop against one stage at m={m_full}: "
              f"{fmt(full_p['t'])} / {fmt(full_c['t'])}; stage 2 on 16 host threads + transfer ~{fmt(verify)}")

    print("\n## Two-stage screens at the eta = 0.4 showcase sizes, at two m1 each (review R2: pair the card with the "
          "CPU's best method)\n")
    print("| id | (n, k, m) | m1 | tau1 | P(secret kept) | E[survivors] | card stage 1, M3 private / M4 coop (P) | "
          "card one stage at m (P) |")
    print("|---|---|---|---|---|---|---|---|")
    for i, n, k, e, m1, tau, m_full in SCREENS:
        pk, surv = screen_at(n, k, e, m1, tau)
        s1p, s1c = plan(n, k, m1, "private"), plan(n, k, m1, "coop")
        fp, fc = plan(n, k, m_full, "private"), plan(n, k, m_full, "coop")
        print(f"| {i} | ({n}, {k}, {m_full}) | {m1} | {tau} | {pk:.4f} | {surv:.3g} | {fmt(s1p['t'])} / {fmt(s1c['t'])} | "
              f"{fmt(fp['t'])} / {fmt(fc['t'])} |")

    print("\n## Where the cores become visible: m99 (SP3's model) and card time, M3 private variant, 32 shires\n")
    print("Cell: m99 / C(n,k) m / card time / CPU 1T. Bold: card kernel 50 ms - 8 s (launch < 1%, one process).\n")
    print("| n | k | eta=0.1 | eta=0.2 | eta=0.3 | eta=0.4 |")
    print("|---|---|---|---|---|---|")
    for n in (128, 256, 512, 1024):
        for k in (3, 4, 5):
            cells = []
            for e in (0.1, 0.2, 0.3, 0.4):
                m = m99(n, k, e)
                pv = plan(n, k, m, "private")
                c = f"{m} / {comb(n, k) * m:.1g} / {fmt(pv['t'])} / {fmt(cpu_1t(n, k, m))}"
                cells.append(f"**{c}**" if 0.05 <= pv["t_kernel"] <= 8 else c)
            print(f"| {n} | {k} | " + " | ".join(cells) + " |")

    print("\n## Early exit: accept the first candidate with c >= tau_acc (false accept <= 1e-3 by union bound)\n")
    from scipy.stats import binom
    for i, n, k, e, m, _ in LADDER:
        if i not in ("L1", "L2", "L4", "L5"):
            continue
        N = comb(n, k)
        d = 0
        while N * binom.cdf(d + 1, m, 0.5) <= 1e-3:
            d += 1
        pacc = float(binom.cdf(d, m, e))
        print(f"- {i}: tau_acc = {m - 2 * d} (disagreements <= {d}); P(secret clears it) = {pacc:.3f}; "
              f"expected scan fraction {pacc * 0.5 + (1 - pacc):.2f}")

    print("\n## Batch mode: 1,024 instances of (64, 4, 0.1, m = 64), one per minion, vector path\n")
    inst = comb(64, 4) * 64
    for ipc in (0.37, 0.74):
        cyc = inst / 256 * 16 / ipc
        t = cyc / F + LAUNCH_S
        e_dyn = 1024 * inst / 256 * 16 * E_INSTR * 1.3
        print(f"- IPC {ipc}: {fmt(t)} for 1,024 instances ({fmt(t / 1024)} each); CPU 1T 0.50 ms each = "
              f"{fmt(0.501e-3 * 1024)}, 16T ~{fmt(0.501e-3 * 1024 / 8.5)}; board ~{(35.9 + e_dyn / (t - LAUNCH_S)):.0f} W, "
              f"{(35.9 * t + e_dyn) / 1024 * 1e3:.2g} mJ per instance")


if __name__ == "__main__":
    main()
