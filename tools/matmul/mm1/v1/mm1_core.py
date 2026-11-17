#!/usr/bin/env python3
"""MM1-v1 core: the matmul model's map, cycles, joules and transistor switches, shared by the predictor (mm1_v1.py) and the fit (fit_v1.py).

Scope (every output carries it): the lab's GEMM kernel rgm136 (gemmL<MB>x<NB>x<KB>, M = 1,024 MB, N = 512 NB, K = 512 KB w, w = 1/2/4 for
fp32/fp16/int8) on its grid, and the run_gemm calibrating arms (gemmc1, c4s, c8s, c8, c16, c16s, c16r<R>); an off-grid size is padded to the
next grid point. A shire mask runs the masked shires only, each minion doing the full-chip GEMM's own op list.

THE MAP (closed form; no constant is fitted to a shape):
  - op classes: where an op's A tile and B tile come from (L2, L3 or fresh F); half the ops (row half r = 0) pair A with B's far group B_r0,
    half (r = 1) with B's second use B_r1 (the walk's phases, mm-synth); the c-arms by the lab's own operand split (reuse_e146.arm_split).
  - design B's LRU stack distances (inputs/linemap.py groups()), WITH THE MASK: each distance is a sum of A terms (row panels, 2 MB a K block at
    the full chip), B terms (column panels, 1 MB a K block) and C terms (blocks, 2 MB); under a mask only the participating row groups' A
    tiles (R of 8), column groups' B tiles (C of 4) and shires' C tiles (n of 32) are touched, so each term scales by R/8, C/4 and n/32
    (groups_masked; at the full mask it equals groups() exactly). Tied to E206's registered LRU lines (reuse-e206.json) at strict caps.
  - L2 hits: the lab's desk L2 model per shape for KB <= 2 (inputs/l2_lab.json, run on reuse_e136 when a shape is missing), else none.
  - L3 retention r(d) = 1 / (1 + exp((d - x50)/s)) on each group's distances.
  - set conflicts (v1, replaces v0's collapse rule): when NB is a power of two >= 4 and the (masked) footprint exceeds 32 MB, both B groups'
    retention is multiplied by zeta (B's column-panel blocks sit NB MB apart, a power-of-two stride; E169, E206's 1x15x4 / 1x16x4).
CYCLES (wall basis, the slowest minion):
  T_op = sum_q P_q max(Tc_fmt(f), kA tau(A_q), tau(B_q)),  tau(L2) = F2/f in the gemmL loop (0 in run_gemm's), tau(L3) = c3/f + m3 X,
  tau(F) = cF/f + mF X; Tc = E119's c1 law, never below the card-measured floor (529 / 270 cycles: E101's tenb loop, a post hoc closed form);
  X = 1 at the full chip; a shire subset: X = 1 - chi (1 - n/32) (the spec's contention form, one chi), and the wall is the mean times
  rho_sub = 1 + eta (R_full - R)/(R_full - 1) for a subset that holds every column group but not every row group (R < 8, C = 4) (row-group
  imbalance, E206); the counter's mean = the wall / rho (the scorecard's regime medians) / rho_sub.
JOULES over idle (W x seconds):
  W = P_min(card) n/1,024 + P_mem(card) u + g [B(f) - B(600)] + rate s_V [e_res(card, fmt, kind) + sum_l n_l/32 (b_l + d_l phi(kind))]
  with u = the share of an op's 192 lines that leave the L2 (the memory path awake for any active shire; it does not scale with the minions),
  rate = n / T_op, s_V = (V/0.517 V)^2, e_res = ledger v2's frozen resident anchor (never refitted), phi = 0 zeros, 1 random, a kind's own
  value from its tiles' set-bit share otherwise; J at rest = J over idle + P_rest t (the run's measured rest, or the rest law, REPORTED).
SWITCHES (fin edges; die only, voltage removed; never scorable): counted (the tensor unit's open-flow netlist: fp32 at gate level, fp16 by the
  RTL ratio, int8 the vector unit only) + estimated (every class with no public netlist, the int8 arithmetic included), from the die's energy:
  board J over idle less the regulators' delivery loss (lab finding 19, E46: the minion regulator's 0.181 / 0.188 / 0.102 of its rail on
  aifoundry3 / aifoundry2 / card 1), less the fresh lines' energy (DRAM devices, PHY and path: reported apart, not converted), less the in-run
  leakage (k_leak dT t) and the governed base's leakage share, less the counted netlist's own energy (glitch README, measured end to end:
  1.925 pJ zero delay / 2.706 pJ timed a random fp32 multiply-add); the rest x kappa_die (fin edges a die joule).
SPDX-License-Identifier: Apache-2.0
"""
import importlib.util
import json
import math
import os
import re

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.join(HERE, 'inputs')


def _imp(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


LM = _imp('mm1v1_linemap', os.path.join(INP, 'linemap.py'))
L2LAB = json.load(open(os.path.join(INP, 'l2_lab.json')))['shapes']
FULL = 0xFFFFFFFF
NU = LM.NU
FMT_W = {'fp32': 1, 'fp16': 2, 'int8': 4}
MACS = {'fp32': 4096, 'fp16': 8192, 'int8': 16384}
FLOOR = {'fp32': 529.0, 'fp16': 529.0, 'int8': 270.0}      # measured (E101 tenb loop), post hoc closed form: RTL + 7.75, B through TenB
C1LAW = {'fp32': (527.48, 0.0176), 'fp16': (527.48, 0.0176), 'int8': (283.03, 0.0146)}   # E119's c1 law (cycles, us)
CARMS = ('gemmc1', 'gemmc4s', 'gemmc8s', 'gemmc8', 'gemmc16', 'gemmc16s')
RHO = {'one_block': 1.006, 'inside': 1.126, 'past': 1.011, 'c4s': 1.143, 'c8s': 1.143, 'stream': 1.001}   # the scorecard's wall / mean medians
B_BASE = {600.0: 25.456, 700.0: 28.243, 800.0: 33.610}    # the M7 relation (W), the governed base
SCOPE = ("rgm136 gemmL<MB>x<NB>x<KB> on its grid (M = 1,024 MB, N = 512 NB, K = 512 KB w; off-grid sizes padded) and the run_gemm "
         "c-arms; shire masks run the masked shires only; one card, one clock per launch")


# ------------------------------------------------------------------------------------------------ masks and shapes
def mask_info(mask):
    m = int(mask, 16) if isinstance(mask, str) else int(mask)
    sh = [s for s in range(32) if (m >> s) & 1]
    R = len({s >> 2 for s in sh})
    C = len({s & 3 for s in sh})
    n = len(sh)
    return {'mask': m, 'n': n, 'R': R, 'C': C, 'sa': R / 8.0, 'sb': C / 4.0, 'sc': n / 32.0, 'full': m == FULL}


def parse_arm(arm):
    m = re.fullmatch(r'gemmL(\d+)x(\d+)x(\d+)', arm)
    if m:
        return tuple(int(x) for x in m.groups())
    return None


def is_pow2(x):
    return x > 0 and (x & (x - 1)) == 0


def footprint(MB, NB, KB, mi=None):
    """MB of distinct tiles a pass touches: A 2 MB, B 1 MB, C 2 MB a block, each scaled by the mask's shares"""
    sa, sb, sc = (1.0, 1.0, 1.0) if mi is None else (mi['sa'], mi['sb'], mi['sc'])
    return 2.0 * MB * KB * sa + NB * KB * sb + 2.0 * MB * NB * sc


def groups_masked(MB, NB, KB, sa=1.0, sb=1.0, sc=1.0):
    """design B's groups (linemap.groups, w = 1) with each stack distance's A, B and C terms scaled by the mask's shares (R/8, C/4, n/32).
    The decomposition of each distance (design B, design.md section 3): A_near (3 + u) KB + 2 = 2KB [A panel] + (1 + u) KB [B] + 2 [C];
    A_far 2 KB MB [A] + NB KB [B] + (2 (MB - 1) NB + 1.5) [C]; B_r1 2KB + 1 = KB [A half panel] + KB [B] + 1 [C half]; B_r0 NB KB [B] + A_part
    [A] + (2 NB - 1) [C halves]. At sa = sb = sc = 1 this is groups() number for number."""
    phi = 1.0 if MB == 1 else (NB - 1) / NB
    out = []
    a_near = 64.0 * phi
    a_l2 = 0.5 * a_near if KB == 1 else 0.0
    if NB >= 2:
        dA = [2.0 * KB * sa + (1.0 + (i + 0.5) / NU) * KB * sb + 2.0 * sc for i in range(NU)]
    else:
        dA = [2.0 * KB * sa + 1.0 * KB * sb + 2.0 * sc]
    out.append(('A_near', a_near, a_l2, dA))
    if phi < 1.0:
        out.append(('A_far', 64.0 * (1.0 - phi), 0.0, [2.0 * KB * MB * sa + NB * KB * sb + (2.0 * (MB - 1) * NB + 1.5) * sc]))
    b1_l2 = 64.0 if KB == 1 else (16.0 if KB == 2 else 0.0)
    out.append(('B_r1', 64.0, b1_l2, [KB * sa + KB * sb + 1.0 * sc]))
    dB0 = []
    for nb in range(NB):
        for i in range(NU):
            u = (i + 0.5) / NU
            if NB == 1:
                ap = 1.0 * KB
            elif MB == 1:
                ap = 2.0 * KB
            elif nb == NB - 1:
                ap = (3.0 - u) * KB
            elif nb == 0:
                ap = (2.0 + u) * KB
            else:
                ap = 4.0 * KB
            dB0.append(NB * KB * sb + ap * sa + (2.0 * NB - 1.0) * sc)
    out.append(('B_r0', 64.0, 0.0, dB0))
    return out


_L2_CACHE = {}


def l2_hits(MB, NB, KB):
    """the lab's desk L2 model's hits a shire-op, A and B apart (KB <= 2; none at KB >= 3: a B line's per-shire reuse distance is 384 KB x KB)"""
    if KB >= 3:
        return None
    k = 'gemmL%dx%dx%d' % (MB, NB, KB)
    if k in L2LAB:
        return L2LAB[k]['A_L2'], L2LAB[k]['B_L2']
    if k not in _L2_CACHE:   # run the lab's model (reuse_e136, vendored) exactly as mm-synth's l2_lab.py did
        import collections
        R = _imp('mm1v1_reuse_e136', os.path.join(INP, 'reuse_e136.py'))
        A0, B0 = 1 << 32, (1 << 32) + (1 << 30)
        out = collections.Counter()
        nops = 0
        for s0, s1 in ((0, 0), (3, 5)):
            ops = R.shire_ops(('large', MB, NB, KB), s0, s1, A0, B0)
            sets = collections.defaultdict(list)
            R.l2_pass(ops, sets, True)
            _, _, missed = R.l2_pass(ops, sets, True)
            for mo in missed:
                nops += 1
                nA = sum(1 for t in mo if t < B0)
                out['A_L2'] += 64 - nA
                out['B_L2'] += 128 - (len(mo) - nA)
        _L2_CACHE[k] = (round(out['A_L2'] / nops, 3), round(out['B_L2'] / nops, 3))
    return _L2_CACHE[k]


class Shape:
    """a point's map skeleton: its groups (counts, L2 hits, distance arrays) for the gemmL kernel, or its fixed classes for a c-arm"""

    def __init__(self, arm, mask=FULL, masked_map=True):
        self.arm = arm
        self.mi = mask_info(mask)
        self.blocks = parse_arm(arm)
        self.kernel = 'gemmL' if self.blocks else 'run_gemm'
        self.masked_map = masked_map
        if self.blocks:
            MB, NB, KB = self.blocks
            mi = self.mi if masked_map else mask_info(FULL)
            self.F_full = footprint(MB, NB, KB)
            self.F = footprint(MB, NB, KB, mi)
            gs = groups_masked(MB, NB, KB, mi['sa'], mi['sb'], mi['sc'])
            ov = l2_hits(MB, NB, KB)
            a_left = ov[0] if ov else None
            self.groups = []
            for name, cnt, l2, ds in gs:
                if ov is not None:
                    if name.startswith('A'):
                        l2 = min(cnt, a_left)
                        a_left -= l2
                    elif name == 'B_r1':
                        l2 = min(cnt, ov[1])
                    else:
                        l2 = min(cnt, max(ov[1] - 64.0, 0.0))
                self.groups.append((name, cnt, l2, np.array(ds, float)))
            self.p2 = is_pow2(NB) and NB >= 4
            self.ops = 64 * MB * NB * KB
        else:
            self.F = self.F_full = None
            self.p2 = False
            self.ops = None
            self.cl = carm_classes(arm)

    def Q(self, x50, s, zeta=1.0, rule='v1'):
        """op-class weights Q[a, b] (a: A's place, b: B's place; 0 L2, 1 L3, 2 fresh). rule 'v1': both B groups' retention x zeta when NB is
        a power of two >= 4 and the (masked) footprint exceeds 32 MB; rule 'v0': MM1-v0's collapse (B_r0 x 0.15 when MB = 1, NB in {4, 8},
        KB >= 4 and the full-chip footprint exceeds 32 MB), kept to reproduce v0's form; rule 'none': neither."""
        if self.kernel != 'gemmL':
            return self.cl
        A = np.zeros(3)
        Br0 = np.zeros(3)
        Br1 = np.zeros(3)
        MB, NB, KB = self.blocks
        conflict = rule in ('v1', 'r1') and self.p2 and self.F > 32.0
        v0c = rule == 'v0' and MB == 1 and NB in (4, 8) and KB >= 4 and self.F_full > 32.0
        for name, cnt, l2, ds in self.groups:
            xb = x50 * zeta if (rule == 'g2' and self.p2 and name.startswith('B')) else x50
            rr = float(np.mean(1.0 / (1.0 + np.exp(np.clip((ds - xb) / s, -50, 50)))))
            if conflict and (name == 'B_r1' if rule == 'r1' else name.startswith('B')):
                rr *= zeta
            if v0c and name == 'B_r0':
                rr *= 0.15
            v = np.array([l2, (cnt - l2) * rr, (cnt - l2) * (1 - rr)])
            if name.startswith('A'):
                A += v
            elif name == 'B_r1':
                Br1 += v
            else:
                Br0 += v
        Q = 0.5 * np.outer(A / 64.0, Br0 / 64.0) + 0.5 * np.outer(A / 64.0, Br1 / 64.0)
        return Q / Q.sum()

    def Qhalves(self, x50, s, zeta=1.0, rule='v1'):
        """the two row halves apart: Q0 (r = 0: A with B's far group B_r0) and Q1 (r = 1: A with B's second use B_r1), each summing to 1;
        Q = (Q0 + Q1) / 2. The c-arms by the lab's split: their first class is the r = 0 half, their L2 class the r = 1 half."""
        if self.kernel != 'gemmL':
            return carm_halves(self.arm)
        A = np.zeros(3)
        Br0 = np.zeros(3)
        Br1 = np.zeros(3)
        MB, NB, KB = self.blocks
        conflict = rule in ('v1', 'r1') and self.p2 and self.F > 32.0
        v0c = rule == 'v0' and MB == 1 and NB in (4, 8) and KB >= 4 and self.F_full > 32.0
        for name, cnt, l2, ds in self.groups:
            xb = x50 * zeta if (rule == 'g2' and self.p2 and name.startswith('B')) else x50
            rr = float(np.mean(1.0 / (1.0 + np.exp(np.clip((ds - xb) / s, -50, 50)))))
            if conflict and (name == 'B_r1' if rule == 'r1' else name.startswith('B')):
                rr *= zeta
            if v0c and name == 'B_r0':
                rr *= 0.15
            v = np.array([l2, (cnt - l2) * rr, (cnt - l2) * (1 - rr)])
            if name.startswith('A'):
                A += v
            elif name == 'B_r1':
                Br1 += v
            else:
                Br0 += v
        Q0 = np.outer(A / A.sum(), Br0 / Br0.sum())
        Q1 = np.outer(A / A.sum(), Br1 / Br1.sum())
        return Q0, Q1


def carm_halves(arm):
    Q0 = np.zeros((3, 3))
    Q1 = np.zeros((3, 3))
    m = re.fullmatch(r'gemmc16r(\d+)', arm)
    if m:
        R = int(m.group(1))
        Q0[2, 2] += 1.0 / R
        Q0[0, 0] += 1 - 1.0 / R
        Q1[2, 0] += 1.0 / R
        Q1[0, 0] += 1 - 1.0 / R
        return Q0, Q1
    a = {'gemmc1': ((0, 0), (0, 0)), 'gemmc8s': ((1, 1), (1, 0)), 'gemmc4s': ((1, 1), (1, 0)), 'gemmc16': ((2, 2), (2, 0)),
         'gemmc16s': ((2, 2), (2, 0)), 'gemmc8': ((2, 2), (2, 0))}[arm]
    Q0[a[0]] = 1.0
    Q1[a[1]] = 1.0
    return Q0, Q1


def carm_classes(arm):
    Q = np.zeros((3, 3))
    m = re.fullmatch(r'gemmc16r(\d+)', arm)
    if m:
        R = int(m.group(1))
        Q[2, 2] += 0.5 / R
        Q[2, 0] += 0.5 / R
        Q[0, 0] += 1 - 1.0 / R
        return Q
    cl = {'gemmc1': [(1.0, 0, 0)], 'gemmc8s': [(0.5, 1, 1), (0.5, 1, 0)], 'gemmc4s': [(0.5, 1, 1), (0.5, 1, 0)],
          'gemmc16': [(0.5, 2, 2), (0.5, 2, 0)], 'gemmc16s': [(0.5, 2, 2), (0.5, 2, 0)], 'gemmc8': [(0.5, 2, 2), (0.5, 2, 0)]}[arm]
    for w, a, b in cl:
        Q[a, b] += w
    return Q


def lines(Q):
    """lines a shire-op by place (L2, L3, F): A 64 x A's marginal + B 128 x B's marginal"""
    return 64.0 * Q.sum(axis=1) + 128.0 * Q.sum(axis=0)


# ------------------------------------------------------------------------------------------------ cycles
def Tc(fmt, f):
    c, m = C1LAW[fmt]
    return max(c / f + m, FLOOR[fmt] / f)


def t_op(Q, fmt, f, kernel, mi, P):
    """us an op, the slowest minion (wall basis), at the launch clock f (MHz), with parameters P"""
    X = 1.0 if mi['full'] else max(1.0 - P['chi'] * (1.0 - mi['n'] / 32.0), 0.05)
    tau = [P['F2'] / f if kernel == 'gemmL' else 0.0, P['c3'] / f + P['m3'] * X, P['cF'] / f + P['mF'] * X]
    tc = Tc(fmt, f)
    kA = P['kA']
    T = 0.0
    for a in range(3):
        for b in range(3):
            if Q[a, b] > 0:
                T += Q[a, b] * max(tc, kA * tau[a], tau[b])
    return T * rho_sub(mi, P)


def rho_sub(mi, P):
    """row-group imbalance of a subset holding every column group but not every row group (E206: wall / mean 1.21 at 0xf, 1.07 at 0xff)"""
    if mi['full'] or mi['C'] < 4 or mi['R'] >= 8:
        return 1.0
    return 1.0 + P['eta'] * max(0.0, (4.0 - mi['R']) / 3.0)


def rho_imbalance(mi, imb):
    """the counter's mean under a subset that holds every column group but not every row group (R < 4 of 8 row groups... see below): E206's
    measured wall / mean was 1.213 / 1.214 at 0xf (R = 1) and 1.069 / 1.083 at 0xff (R = 2), 1.000 at R >= 4; fitted as
    1 + eta_m ((4 - R) / 3)^gamma on those four points (post hoc; it moves the counter's mean only, never the wall or the seconds)."""
    if imb is None or mi['full'] or mi['C'] < 4 or mi['R'] >= 4:
        return 1.0
    return 1.0 + imb['eta_m'] * ((4.0 - mi['R']) / 3.0) ** imb['gamma']


def rho_mean(shape, n2, P=None):
    """the wall / the counter's mean, by regime (the scorecard's measured medians), before the subset imbalance"""
    if shape.kernel == 'gemmL':
        if n2 >= 191.5:
            return RHO['one_block']
        return RHO['inside'] if shape.F_full <= 32 else RHO['past']
    return {'gemmc1': RHO['one_block'], 'gemmc8s': RHO['c8s'], 'gemmc4s': RHO['c4s']}.get(shape.arm, RHO['stream'])


def sim_steps(shape):
    """the timing simulation's instruction count a minion a GEMM (hart 0; mm-timing's step law: 46.625 an op + 24.25 a C-tile row + 92 a launch)"""
    if shape.kernel != 'gemmL':
        return None
    MB, NB, KB = shape.blocks
    return 46.625 * shape.ops + 24.25 * (2 * MB * NB) + 92


# ------------------------------------------------------------------------------------------------ joules
def e_parts(Q, kind_phi):
    n2, n3, nF = lines(Q)
    return n2, n3, nF, (n3 + nF) / 192.0


def w_over(P, card, n, t_us, s_V, e_res_nJ, Q, phi, G=0.0):
    """W over idle at op time t_us (the wall, us), n active minions, the resident anchor e_res (nJ an op at 600 MHz), phi the kind's share"""
    n2, n3, nF, u = e_parts(Q, phi)
    rate = n / (t_us * 1e-6)
    rs = rate * s_V
    PJ = 1e-12
    return (P['Pmin|' + card] * n / 1024.0 + P['Pmem|' + card] * u + P['g'] * G + rs * e_res_nJ * 1e-9
            + rs * PJ * (n2 / 32.0 * (P['b2'] + P['d2'] * phi) + n3 / 32.0 * (P['b3'] + P['d3'] * phi) + nF / 32.0 * (P['bF'] + P['dF'] * phi)))


def w_terms(P, card, n, t_us, s_V, e_res_nJ, Q, phi, G=0.0):
    """the same W split by class (W): minion awake, memory-path awake, governed base, resident op, L2, L3 and fresh lines"""
    n2, n3, nF, u = e_parts(Q, phi)
    rate = n / (t_us * 1e-6)
    rs = rate * s_V
    PJ = 1e-12
    return {'awake_minions': P['Pmin|' + card] * n / 1024.0, 'awake_memory_path': P['Pmem|' + card] * u, 'governed_base': P['g'] * G,
            'resident_op': rs * e_res_nJ * 1e-9, 'lines_L2': rs * PJ * n2 / 32.0 * (P['b2'] + P['d2'] * phi),
            'lines_L3': rs * PJ * n3 / 32.0 * (P['b3'] + P['d3'] * phi), 'lines_fresh': rs * PJ * nF / 32.0 * (P['bF'] + P['dF'] * phi)}


# ------------------------------------------------------------------------------------------------ switches (die only)
SW_CONST = {
    'reg_loss_coeff': {'aifoundry3 card 0': 0.181, 'aifoundry2 card 0': 0.188, 'aifoundry1 card 1': 0.102},   # finding 19, E46: x minion-rail W
    'reg_loss_band': (0.0, 0.294),            # none, to the NoC rail's coefficient (finding 19, the largest per-rail share)
    'counted_pJ_fp32_random': (1.925, 2.706), # glitch README (C): bottom-up a random fp32 multiply-add, zero delay / timed, k = 1, 0.517 V
    'fin_edges_fp32_random': (71092.0, 107508.0),   # design C switch_table: zero delay / timed
    'kappa_die': (2.20e16, 3.97e16, 4.86e16), # fin edges a die joule: low = counted fin edges over the resident op's die energy (5.783 pJ /
                                              # (1 + 0.157), the three-card regulator mean); central = the counted netlist's own (107,508 /
                                              # 2.706 pJ); high = every joule on signal nets (14.5 fins / 0.2985 fJ)
    'k_leak_w_per_c': 0.47, 'k_rise_c_per_w': (0.12, 0.145),
    'gov_leak_share': (0.55, 0.65, 0.80),     # finding 16: leakage 55-80% of an idle card at 80 C (best fit 65%), applied to the governed base
}


def switches(J_terms, t, W, card, s_V, N_op, fmt, kind_key, sw_table):
    """die-only fin edges a GEMM: counted (the tensor unit's public netlist) and estimated (every other on-die class, the int8 arithmetic
    included), with the fresh lines' energy apart. J_terms: the joules a GEMM by class (board)."""
    c = SW_CONST
    reg = c['reg_loss_coeff'].get(card, 0.157)
    fe = (sw_table.get(kind_key) or {}).get('fin_edges_per_mac')
    macs = N_op * MACS[fmt]
    counted = (macs * fe['lo'], macs * fe['hi']) if fe else (None, None)
    # the counted netlist's own energy, at the card's volts: fin edges x (energy a fin edge of the fp32 unit, its own ratio)
    e_fe = (c['counted_pJ_fp32_random'][0] * 1e-12 / c['fin_edges_fp32_random'][0], c['counted_pJ_fp32_random'][1] * 1e-12 / c['fin_edges_fp32_random'][1])
    J_counted = (counted[0] * e_fe[0] * s_V, counted[1] * e_fe[1] * s_V) if fe else (0.0, 0.0)
    J_fresh = J_terms['lines_fresh']
    onboard = sum(v for k, v in J_terms.items() if k != 'lines_fresh')
    leak = (c['k_leak_w_per_c'] * c['k_rise_c_per_w'][0] * W * t, c['k_leak_w_per_c'] * c['k_rise_c_per_w'][1] * W * t)
    gov_leak = tuple(J_terms['governed_base'] * x for x in c['gov_leak_share'])
    die = onboard / (1.0 + reg)
    die_band = (onboard / (1.0 + c['reg_loss_band'][1]), onboard / (1.0 + c['reg_loss_band'][0]))
    est_c = max(die - 0.5 * (leak[0] + leak[1]) - gov_leak[1] - 0.5 * (J_counted[0] + J_counted[1]), 0.0) / s_V
    est_lo = max(die_band[0] - leak[1] - gov_leak[2] - J_counted[1], 0.0) / s_V
    est_hi = max(die_band[1] - leak[0] - gov_leak[0] - J_counted[0], 0.0) / s_V
    k = c['kappa_die']
    int8_arith = None
    if fmt == 'int8':
        # the int8 arithmetic has no public netlist: its die energy = the resident op's die share less the counted vector-unit part
        int8_arith = max(J_terms['resident_op'] / (1.0 + reg) - 0.5 * (J_counted[0] + J_counted[1]), 0.0) / s_V * k[1]
    return {'counted_fin_edges': list(counted), 'estimated_fin_edges': [est_lo * k[0], est_c * k[1], est_hi * k[2]],
            'of_which_int8_arithmetic_central': int8_arith,
            'die_J_over_idle': die, 'die_J_band': list(die_band), 'fresh_lines_J_apart': J_fresh, 'in_run_leakage_J': list(leak),
            'governed_leakage_J': list(gov_leak), 'counted_netlist_J': list(J_counted),
            'scope': 'die only: regulators out (finding 19 coefficient), DRAM devices, PHY and path apart (the fresh lines), leakage out; '
                     'counted = the tensor unit (fp32 gate level; fp16 RTL x ratio; int8 the vector unit only); not scorable'}
