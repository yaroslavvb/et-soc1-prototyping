"""sp.py: sparse-parity toy prototypes in Python + numpy.

  gen()          the data generator (bit-packed; the same counter-based RNG as spbits.c, so both
                 produce the identical instance for the same (n, k, eta, m, seed))
  gemm_solve()   the k-subset correlation search as a +-1 matrix product: split k = a + b, form the
                 products of a-subsets (times y) and of b-subsets, one GEMM gives every (a, b) pair's
                 correlation; pairs that share an index are masked out (float32 BLAS; exact below 2^24)
  ge_solve()     GF(2) Gaussian elimination on bit-packed rows (noiseless labels)
  p_success(), m99_model()
                 the success model of the exhaustive (= GEMM) estimator: the secret's disagreement
                 count T ~ Bin(m, eta) must beat all N-1 wrong subsets, each Bin(m, 1/2)
"""
from __future__ import annotations

import itertools
import math
import time
from dataclasses import dataclass

import numpy as np

M64 = (1 << 64) - 1
GOLD = 0x9E3779B97F4A7C15


def _mix64_int(z: int) -> int:
    z &= M64
    z ^= z >> 30
    z = (z * 0xBF58476D1CE4E5B9) & M64
    z ^= z >> 27
    z = (z * 0x94D049BB133111EB) & M64
    return z ^ (z >> 31)


@np.errstate(over="ignore")
def _mix64(z: np.ndarray) -> np.ndarray:
    z = z ^ (z >> np.uint64(30))
    z = z * np.uint64(0xBF58476D1CE4E5B9)
    z = z ^ (z >> np.uint64(27))
    z = z * np.uint64(0x94D049BB133111EB)
    return z ^ (z >> np.uint64(31))


@np.errstate(over="ignore")
def rnd(seed: int, stream: int, idx) -> np.ndarray:
    key = _mix64_int(seed * GOLD + stream * 0xD1B54A32D192ED03 + 0x632BE59BD9B4E019)
    idx = np.asarray(idx, dtype=np.uint64)
    return _mix64(np.uint64(key) + idx * np.uint64(GOLD))


@dataclass
class Instance:
    n: int
    k: int
    eta: float
    m: int
    seed: int
    X: np.ndarray       # (n, W) uint64: bit s of X[j] = feature j of sample s
    y: np.ndarray       # (W,) uint64
    noise: np.ndarray   # (W,) uint64, the flipped labels (evaluation only)
    secret: tuple

    @property
    def W(self) -> int:
        return self.X.shape[1]

    def bits(self) -> tuple[np.ndarray, np.ndarray]:
        """(m, n) and (m,) arrays of 0/1 (uint8)."""
        xb = np.unpackbits(self.X.view(np.uint8), bitorder="little").reshape(self.n, -1)[:, : self.m]
        yb = np.unpackbits(self.y.view(np.uint8), bitorder="little")[: self.m]
        return np.ascontiguousarray(xb.T), yb

    def pm(self, dtype=np.float32) -> tuple[np.ndarray, np.ndarray]:
        """+-1 encodings: 0 -> +1, 1 -> -1, so XOR becomes a product."""
        xb, yb = self.bits()
        return (1 - 2 * xb.astype(dtype)), (1 - 2 * yb.astype(dtype))


def gen(n: int, k: int, eta: float, m: int, seed: int) -> Instance:
    W = (m + 63) // 64
    last = ((1 << (m % 64)) - 1) if m % 64 else M64
    idx = (np.arange(n, dtype=np.uint64)[:, None] << np.uint64(32)) | np.arange(W, dtype=np.uint64)[None, :]
    X = rnd(seed, 1, idx)
    X[:, -1] &= np.uint64(last)
    perm = list(range(n))
    for i in range(k):
        r = int(rnd(seed, 3, i)) % (n - i)
        perm[i], perm[i + r] = perm[i + r], perm[i]
    secret = tuple(sorted(perm[:k]))
    thr = np.uint64(int(eta * 2.0**53))
    flip = (rnd(seed, 2, np.arange(m, dtype=np.uint64)) >> np.uint64(11)) < thr
    nb = np.zeros(W * 64, dtype=np.uint8)
    nb[:m] = flip
    noise = np.packbits(nb, bitorder="little").view("<u8").astype(np.uint64)
    y = noise.copy()
    for j in secret:
        y ^= X[j]
    return Instance(n, k, eta, m, seed, X, y, noise, secret)


def inst_hash(I: Instance) -> str:
    h = 0x12345678
    for v in I.X.ravel().tolist():
        h = _mix64_int(h ^ v)
    for v in I.y.tolist():
        h = _mix64_int(h ^ v)
    return f"{h:016x}"


# ---------------------------------------------------------------- GEMM (meet in the middle)
def _combos(n: int, a: int) -> np.ndarray:
    return np.array(list(itertools.combinations(range(n), a)), dtype=np.int32).reshape(-1, a)


def _products(Xpm: np.ndarray, S: np.ndarray) -> np.ndarray:
    P = Xpm[:, S[:, 0]].copy()
    for t in range(1, S.shape[1]):
        P *= Xpm[:, S[:, t]]
    return P


def gemm_solve(I: Instance, block: int = 0, cblock: int = 2048, split: str = "canonical") -> dict:
    """Largest +-1 correlation over all k-subsets via GEMMs of a-subset by b-subset products (k = a + b).

    split="canonical": a k-set is split only one way, A = its a smallest indices, B = its b largest, so
      max(A) < min(B). Rows (a-subsets) are sorted by max(A) and columns (b-subsets) by min(B); the valid
      pairs then form a staircase, and a row block only multiplies the columns with min(B) > its smallest
      max(A). Every k-set is computed once; entries off the staircase are masked.
    split="all": every (A, B) pair (every k-set C(k, a) times, halved when a == b by computing only blocks
      on or above the diagonal); pairs sharing an index are masked.
    """
    n, k, m = I.n, I.k, I.m
    a = k // 2
    b = k - a
    Xpm, ypm = I.pm(np.float32)
    t0 = time.perf_counter()
    if a == 0:
        corr = ypm @ Xpm
        j = int(np.argmax(corr))
        return dict(found=(j,), ok=(j,) == I.secret, macs=m * n, wall_s=time.perf_counter() - t0, unique=True)
    block = block or (64 if a == 1 else 512)            # row block: small enough for the staircase to pay
    SA, SB = _combos(n, a), _combos(n, b)
    if split == "canonical":
        SA = SA[np.argsort(SA[:, -1], kind="stable")]   # by max; SB is lexicographic, so already by min
    best, best_set, unique, macs = -np.inf, None, True, 0.0
    for ia in range(0, len(SA), block):
        sa = SA[ia : ia + block]
        if split == "canonical":
            jb0 = int(np.searchsorted(SB[:, 0], sa[0, -1], side="right"))
        else:
            jb0 = ia if a == b else 0
        if jb0 >= len(SB):
            continue
        FA = _products(Xpm, sa) * ypm[:, None]          # (m, ba): y * x_A
        for ib in range(jb0, len(SB), cblock):
            sb = SB[ib : ib + cblock]
            FB = _products(Xpm, sb)                      # (m, bb): x_B
            G = FA.T @ FB                                # (ba, bb) correlations over m samples
            macs += G.size * m
            if split == "canonical":
                bad = sa[:, -1, None] >= sb[None, :, 0]  # not max(A) < min(B)
            else:
                bad = np.zeros(G.shape, dtype=bool)
                for s in range(a):
                    for t in range(b):
                        bad |= sa[:, s, None] == sb[None, :, t]
            G[bad] = -np.inf
            v = G.max()
            if v < best:
                continue
            if v > best:                                 # new leader
                i, j = np.unravel_index(int(np.argmax(G)), G.shape)
                best, best_set, unique = v, tuple(sorted(set(sa[i]) | set(sb[j]))), True
            # every entry at the leading value must decode to the same k-set (with split="all" the same
            # set recurs once per split); a different set at the same value is a tie = failure
            ii, jj = np.nonzero(G == best)
            for i, j in zip(ii.tolist(), jj.tolist()):
                if tuple(sorted(set(sa[i]) | set(sb[j]))) != best_set:
                    unique = False
                    break
    best_set = tuple(int(x) for x in best_set)
    return dict(found=best_set, ok=(best_set == I.secret and unique), unique=unique, split=split,
                best_corr=float(best), macs=macs, wall_s=time.perf_counter() - t0)


def gemm_macs(n: int, k: int, m: int, tile: int = 0, split: str = "canonical", round_cols: bool = False) -> float:
    """MACs of the blocked GEMM search. canonical: sum over row blocks of `tile` a-subsets (sorted by max)
    of rows x (b-subsets with min(B) > the block's smallest max; rounded up to `tile` with round_cols, as
    hardware tiles are) x m. all: C(n,a) C(n,b) m, about half when a == b."""
    a = k // 2
    b = k - a
    if a == 0:
        return float(n * m)
    tile = tile or (64 if a == 1 else 512)
    if split == "all":
        if a == b:
            A = math.comb(n, a)
            return (A * (A + 1) / 2) * m
        return float(math.comb(n, a) * math.comb(n, b) * m)
    counts = np.array([math.comb(t, a - 1) for t in range(n)], dtype=np.int64)   # a-subsets with max = t
    maxA = np.repeat(np.arange(n), counts)
    starts = np.arange(0, len(maxA), tile)
    rows = np.minimum(tile, len(maxA) - starts).astype(float)
    cols = np.array([math.comb(n - 1 - int(t), b) for t in maxA[starts]], dtype=float)
    if round_cols:
        cols = np.ceil(cols / tile) * tile
    return float(np.sum(rows * cols) * m)


# ---------------------------------------------------------------- GF(2) elimination (numpy)
def ge_solve(I: Instance) -> dict:
    """Gauss-Jordan over GF(2) on bit-packed sample rows [x | y]; noiseless labels."""
    xb, yb = I.bits()
    n, m = I.n, I.m
    R = np.zeros((m, n + 1), dtype=np.uint8)
    R[:, :n] = xb
    R[:, n] = yb
    Wr = (n + 1 + 63) // 64
    pad = np.zeros((m, Wr * 64), dtype=np.uint8)
    pad[:, : n + 1] = R
    P = np.packbits(pad, axis=1, bitorder="little").view("<u8").copy()  # (m, Wr)
    t0 = time.perf_counter()
    rank = 0
    pivrow = {}
    word_xors = 0
    for c in range(n):
        w, sh = divmod(c, 64)
        col = (P[rank:, w] >> np.uint64(sh)) & np.uint64(1)
        nz = np.flatnonzero(col)
        if nz.size == 0:
            continue
        p = rank + int(nz[0])
        if p != rank:
            P[[rank, p]] = P[[p, rank]]
        hit = ((P[:, w] >> np.uint64(sh)) & np.uint64(1)).astype(bool)
        hit[rank] = False
        P[hit] ^= P[rank]
        word_xors += int(hit.sum()) * Wr
        pivrow[c] = rank
        rank += 1
    wall = time.perf_counter() - t0
    if rank < n:
        return dict(ok=False, rank=rank, wall_s=wall, word_xors=word_xors)
    lw, lsh = divmod(n, 64)
    sol = [c for c in range(n) if (int(P[pivrow[c], lw]) >> lsh) & 1]
    return dict(ok=tuple(sol) == I.secret, rank=rank, found=tuple(sol), wall_s=wall, word_xors=word_xors)


# ---------------------------------------------------------------- success model of the exhaustive search
def p_success(N: float, m: int, eta: float) -> float:
    """P(secret is the unique best of N subsets on m samples), treating the N-1 wrong subsets'
    disagreement counts as independent Bin(m, 1/2) (they are exactly Bin(m, 1/2) and pairwise independent)."""
    from scipy.stats import binom

    t = np.arange(m + 1)
    if eta == 0:
        pT = np.zeros(m + 1)
        pT[0] = 1.0
    else:
        pT = binom.pmf(t, m, eta)
    logsf = binom.logsf(t, m, 0.5)                  # log P(wrong > t)
    return float(np.sum(pT * np.exp((N - 1) * logsf)))


def m99_model(n: int, k: int, eta: float, target: float = 0.99) -> int:
    N = math.comb(n, k)
    lo, hi = 1, 8
    while p_success(N, hi, eta) < target:
        lo, hi = hi, hi * 2
    while lo < hi:
        mid = (lo + hi) // 2
        if p_success(N, mid, eta) >= target:
            hi = mid
        else:
            lo = mid + 1
    return hi


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser(description="generate one instance and run the numpy solvers")
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--eta", type=float, default=0.1)
    ap.add_argument("--m", type=int, default=0, help="0 = the model's 99%% sample count")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--save", default="", help="write the packed instance to this .npz")
    ap.add_argument("--hash", action="store_true", help="print the instance hash (cross-check with spbits gen)")
    ap.add_argument("--solvers", default="gemm,ge")
    args = ap.parse_args()
    m = args.m or m99_model(args.n, args.k, args.eta)
    I = gen(args.n, args.k, args.eta, m, args.seed)
    out = dict(n=I.n, k=I.k, eta=I.eta, m=I.m, seed=I.seed, secret=list(I.secret),
               noisy=int(sum(bin(int(v)).count("1") for v in I.noise)))
    if args.hash:
        out["hash"] = inst_hash(I)
    if args.save:
        np.savez(args.save, X=I.X, y=I.y, secret=np.array(I.secret), n=I.n, k=I.k, eta=I.eta, m=I.m, seed=I.seed)
    for s in args.solvers.split(","):
        if s == "gemm":
            r = gemm_solve(I)
            out["gemm"] = {k2: (list(v) if isinstance(v, tuple) else v) for k2, v in r.items()}
        elif s == "ge" and args.eta == 0:
            r = ge_solve(gen(args.n, args.k, 0.0, max(m, args.n + 16), args.seed))
            out["ge"] = {k2: (list(v) if isinstance(v, tuple) else v) for k2, v in r.items()}
    print(json.dumps(out))
