#!/usr/bin/env python3
"""Operation counts and time estimates behind the table in literature.md (brief SP1).

Every rate here is an estimate (E) except the ET int8 tensor peak, which is the measured
71.8 TOP/s from docs/et-soc1-notes.md. Run: python3 estimate_ops.py
"""
from math import comb, log, sqrt

CPU = 5e11          # pair-tests or bit-ops per second, one AVX-512 core (xor + popcount), optimistic (E)
ET_TENSOR = 3.59e13  # int8 MAC/s: 71.8 TOP/s measured / 2 (M), assumed reached by the split GEMM (E)
ET_VEC_L1 = 450e9 * 256  # xor bit-ops/s, matrix resident in L1/registers (E)
ET_VEC_L2 = 7e12         # xor bit-ops/s, streaming from L2 (E)


def m_needed(N, eta, sigmas=3.0):
    """Samples so the true coefficient 1-2*eta clears the max of N null correlations by `sigmas`."""
    return (sqrt(2 * log(N)) + sigmas) ** 2 / (1 - 2 * eta) ** 2


def fmt(t):
    for lim, div, unit in ((1e-3, 1e-6, "us"), (1, 1e-3, "ms"), (120, 1, "s"), (7200, 60, "min"), (3 * 86400, 3600, "h")):
        if t < lim:
            return f"{t / div:.3g} {unit}"
    return f"{t / 86400:.3g} d"


def main():
    print("correlation test: C(n,k)*m pair-tests")
    for n, k, eta in [(64, 4, 0.1), (128, 6, 0.2), (1024, 4, 0.3), (256, 6, 0.25), (128, 8, 0.2), (256, 8, 0.1)]:
        N = comb(n, k)
        m = m_needed(N, eta)
        P = N * m
        print(f"  n={n} k={k} eta={eta} m={m:.0f} ops={P:.2g} cpu={fmt(P / CPU)} et={fmt(P / ET_TENSOR)}")
    print("sample-then-GE: (1-eta)^-n tries of a 1/2 n^3 bit-op elimination")
    for n, eta in [(128, 0.1), (128, 0.15), (128, 0.2)]:
        ops = (1 - eta) ** -n * 0.5 * n ** 3
        print(f"  n={n} eta={eta} ops={ops:.2g} cpu={fmt(ops / CPU)} et={fmt(ops / ET_VEC_L1)}..{fmt(ops / ET_VEC_L2)}")
    print("Prange ISD (noiseless, m samples): C(n,k)/C(m,k) restarts of 1/2 m^2 n bit-ops")
    for n, k, m in [(32, 5, 18), (256, 12, 90), (512, 16, 150)]:
        it = comb(n, k) / comb(m, k)
        ops = it * 0.5 * m * m * n
        print(f"  n={n} k={k} m={m} restarts={it:.2g} ops={ops:.2g} cpu={fmt(ops / CPU)} "
              f"et={fmt(ops / ET_VEC_L1)}..{fmt(ops / ET_VEC_L2)}")


if __name__ == "__main__":
    main()
