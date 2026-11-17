#!/usr/bin/python3
# mm-design-b (Q198): MM1-b's analytic line map of the lab's GEMM kernel (rgm136 SP_GEMM_LARGE, gemmL<MB>x<NB>x<KB>) and of the
# run_gemm c-arms. Desk; standard library only. /usr/bin/python3 3.12.3.
#
# Per shire-op (32 minion-ops at one step) a shire requests 192 lines: A 4 tiles x 16 lines = 64, B 8 tiles x 16 = 128 (cooperative
# loads: an A tile serves 8 minions, a B tile 4). Footprints in MB (1 tile = 1 KB in every format): A row panel 2*KB, B column panel KB,
# C block 2 (TensorStores allocate in the L3 with weight w). The walk: mb outer, nb inner, two row halves r, KB*32 k-steps each.
# Groups of requested lines and their LRU stack distance d (distinct tiles touched since the line's tile was last touched; derived in
# design.md section 3):
#   A_near  64*phi lines, phi = 1 if MB == 1 else (NB-1)/NB;  d ~ U[3KB, 4KB] + 2w (NB >= 2), 3KB + 2w (NB == 1);  L2 hits: half of
#           them at KB == 1 (the lab's L2 model), none at KB >= 2
#   A_far   64*(1-phi) lines (the first block of a row panel);  d = 2KB*MB + NB*KB + (2(MB-1)NB + 1.5)w (about the whole working
#           set; a compulsory miss in a GEMM run once)
#   B_r1    64 lines (the second row half reuses the B panel);  d = 2KB + w;  L2 hits 64 at KB == 1, 16 at KB == 2, else 0
#   B_r0    64 lines (the next row of blocks reuses the B panel); d = NB*KB + A_part + (2NB-1)w, A_part = KB (NB == 1),
#           2KB (MB == 1); MB > 1: 4KB inside a row, (3-u)KB at its last block, (2+u)KB at its first
# A line misses the L2 and is served by the L3 with probability r(d) (strict LRU: d < L, L = 32 MB; MM1-b: a fitted retention curve),
# else fresh (DRAM).
import math

L3_MB = 32.0
NU = 64  # points for the uniform distance average


def groups(MB, NB, KB, w=1.0):
    """list of (name, lines a shire-op, L2-hit lines, distances list (uniform weights))"""
    phi = 1.0 if MB == 1 else (NB - 1) / NB
    out = []
    a_near = 64.0 * phi
    a_l2 = 0.5 * a_near if KB == 1 else 0.0
    if NB >= 2:
        dA = [(3.0 + (i + 0.5) / NU) * KB + 2.0 * w for i in range(NU)]
    else:
        dA = [3.0 * KB + 2.0 * w]
    out.append(("A_near", a_near, a_l2, dA))
    if phi < 1.0:
        # previous touch: the row panel's last block in the previous pass; between: every other row's A panel, the own panel's
        # other tiles, every B panel, every other row's C blocks and about 1.5 of the own row's C halves
        out.append(("A_far", 64.0 * (1.0 - phi), 0.0, [2.0 * KB * MB + NB * KB + (2.0 * (MB - 1) * NB + 1.5) * w]))
    b1_l2 = 64.0 if KB == 1 else (16.0 if KB == 2 else 0.0)
    out.append(("B_r1", 64.0, b1_l2, [2.0 * KB + w]))
    # A part of the distance by the block's place in its row (nb) and the step's place in the sweep (u): MB == 1 one panel (2KB);
    # NB == 1 half of each of two panels (KB); else 4KB inside the row, (3 - u)KB at nb = NB - 1, (2 + u)KB at nb = 0
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
            dB0.append(NB * KB + ap + (2.0 * NB - 1.0) * w)
    out.append(("B_r0", 64.0, 0.0, dB0))
    return out


def strict(d, L=L3_MB):
    return 1.0 if d < L else 0.0


def logistic(x50, s):
    def r(d):
        z = (d - x50) / s
        if z > 50:
            return 0.0
        if z < -50:
            return 1.0
        return 1.0 / (1.0 + math.exp(z))
    return r


def gemmL_lines(MB, NB, KB, ret=strict, w=1.0, once=False):
    """per shire-op: n_L2, n_L3, n_F (and per group). once=True: the GEMM runs once (cold): the A_far group and the first row's B_r0
    lines are compulsory misses (fresh)."""
    n2 = n3 = nF = 0.0
    per = {}
    for name, cnt, l2, ds in groups(MB, NB, KB, w):
        rest = cnt - l2
        rr = sum(ret(d) for d in ds) / len(ds)
        if once and name == "A_far":
            rr = 0.0
        c3 = rest * rr
        cF = rest - c3
        if once and name == "B_r0":
            # the first row of blocks meets B for the first time
            cF += c3 / MB
            c3 -= c3 / MB
        n2 += l2
        n3 += c3
        nF += cF
        per[name] = (round(l2, 3), round(c3, 3), round(cF, 3))
    return {"n_L2": n2, "n_L3": n3, "n_F": nF, "groups": per}


C_ARMS = {  # (n_L2, n_L3, n_F) a shire-op: the lab's convention (E107 / E119 / E126; reuse_e146.arm_split; the scorecard's)
    "gemmc1": (192.0, 0.0, 0.0), "gemmc8s": (64.0, 128.0, 0.0), "gemmc4s": (64.0, 128.0, 0.0),
    "gemmc16": (64.0, 0.0, 128.0), "gemmc16s": (64.0, 0.0, 128.0), "gemmc8": (64.0, 0.0, 128.0),
}


def arm_lines(arm, ret=strict, w=1.0):
    import re
    m = re.fullmatch(r"gemmL(\d+)x(\d+)x(\d+)", arm)
    if m:
        MB, NB, KB = (int(x) for x in m.groups())
        return gemmL_lines(MB, NB, KB, ret, w)
    if arm in C_ARMS:
        a, b, c = C_ARMS[arm]
        return {"n_L2": a, "n_L3": b, "n_F": c, "groups": None}
    m = re.fullmatch(r"gemmc16r(\d+)", arm)
    if m:
        R = int(m.group(1))
        return {"n_L2": 192.0 - 128.0 / R, "n_L3": 0.0, "n_F": 128.0 / R, "groups": None}
    return None


# Vendored into tools/matmul/mm1/v0/inputs/ (Mon 16 Nov 2026, Q199): the design lane's own self-check stood here under
# `if __name__ == "__main__":` (it compared this map with another lane's desk LRU file and wrote its result into that lane's
# folder). MM1-v0 imports groups() only and never ran that block, so this copy cuts it; every line above is the design lane's
# file byte for byte (its sha256 is in ../README.md).
