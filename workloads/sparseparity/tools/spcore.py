"""spcore.py: the Python side of sp.h (workloads/sparseparity/cpu/sp.h). Host code only; opens no card.

  gen()                the instance generator, bit-identical to sp.h, proto/spbits.c and proto/sp.py
  pm1_features(), pm1_labels(), btiles()
                       the +-1 int8 layouts and TensorIMA8A32's B tiles (hashes match `spref gen`)
  Geom                 colex ranks of (k-1)-subsets and the T2 tile geometry (row tiles, column tiles, staircase)
  closed_forms()       the coverage checksums' closed forms (Krawtchouk polynomials)
  brute()              every correlation by direct enumeration (small sizes; tests only)
  work lists, records  read/write the binary formats of sp.h section 6

Everything is exact integer arithmetic; numpy is used for the data only.
"""
from __future__ import annotations

import itertools
import math
import os
import struct
from dataclasses import dataclass, field

# one BLAS thread unless the caller says otherwise: these tools run beside frozen card validations
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np  # noqa: E402

M64 = (1 << 64) - 1
GOLD = 0x9E3779B97F4A7C15
KMAX = 6
INT32_MIN = -(1 << 31)


# ---------------------------------------------------------------- generator (mirrors sp.h / spbits.c / sp.py)
def mix64_int(z: int) -> int:
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
    key = mix64_int(seed * GOLD + stream * 0xD1B54A32D192ED03 + 0x632BE59BD9B4E019)
    idx = np.asarray(idx, dtype=np.uint64)
    return _mix64(np.uint64(key) + idx * np.uint64(GOLD))


@dataclass
class Instance:
    n: int
    k: int
    eta: float
    m: int
    seed: int
    X: np.ndarray        # (n, Wm) uint64, feature-major: bit s%64 of X[j, s//64] = feature j of sample s
    y: np.ndarray        # (Wm,) uint64
    noise: np.ndarray    # (Wm,) uint64
    secret: tuple

    @property
    def Wm(self) -> int:
        return self.X.shape[1]

    def bits(self):
        """(m, n) and (m,) uint8 arrays of 0/1."""
        xb = np.unpackbits(self.X.view(np.uint8), bitorder="little").reshape(self.n, -1)[:, : self.m]
        yb = np.unpackbits(self.y.view(np.uint8), bitorder="little")[: self.m]
        return np.ascontiguousarray(xb.T), yb


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
        h = mix64_int(h ^ v)
    for v in I.y.tolist():
        h = mix64_int(h ^ v)
    return f"{h:016x}"


def bytes_hash(buf: bytes) -> str:
    """sp_bytes_hash: mix64 chain over little-endian 8-byte words (the last one zero-padded)."""
    b = bytes(buf)
    h = GOLD ^ len(b)
    pad = b + b"\0" * (-len(b) % 8)
    for (v,) in struct.iter_unpack("<Q", pad):
        h = mix64_int(h ^ v)
    return f"{h:016x}"


# ---------------------------------------------------------------- layouts
def slices(m: int) -> int:
    return (m + 63) // 64


def pm1_features(I: Instance, mp: int) -> np.ndarray:
    """(n, mp) int8: +1 for bit 0, -1 for bit 1, 0 for padding samples."""
    xb, _ = I.bits()
    out = np.zeros((I.n, mp), dtype=np.int8)
    out[:, : I.m] = (1 - 2 * xb.T.astype(np.int16)).astype(np.int8)
    return out


def pm1_labels(I: Instance, mp: int) -> np.ndarray:
    _, yb = I.bits()
    out = np.zeros(mp, dtype=np.int8)
    out[: I.m] = (1 - 2 * yb.astype(np.int16)).astype(np.int8)
    return out


def btiles(I: Instance, S: int) -> np.ndarray:
    """(NJ, S, 16 lines, 16 columns, 4 samples) int8 = TensorIMA8A32 B tiles: byte (r, c, e) of tile (J, s) is
    x~[16J + c][64 s + 4 r + e]; columns >= n and samples >= m are 0. Row-major flattening = sp_btiles()."""
    NJ = (I.n + 15) // 16
    f = np.zeros((NJ * 16, 64 * S), dtype=np.int8)
    f[: I.n, :] = pm1_features(I, 64 * S)
    t = f.reshape(NJ, 16, S, 16, 4)            # (J, c, s, r, e)
    return np.ascontiguousarray(t.transpose(0, 2, 3, 1, 4))


# ---------------------------------------------------------------- colex ranks and the T2 geometry
class Geom:
    """Rows: the a = k-1 subsets of 0..n-2 in colex order; row tiles of 16; column tiles of 16 features."""

    def __init__(self, n: int, k: int, m: int):
        if not (2 <= k <= KMAX and k <= n <= 4096):
            raise ValueError(f"need 2 <= k <= {KMAX}, k <= n <= 4096")
        self.n, self.k, self.a, self.m = n, k, k - 1, m
        self.S = slices(m)
        self.mp = 64 * self.S
        self.NJ = (n + 15) // 16
        self.NR = math.comb(n - 1, self.a)
        self.NT = (self.NR + 15) // 16
        self.Ncand = math.comb(n, k)
        # first row tile whose first column tile is >= q, q = 0..NJ
        self.Tq = [self.tile_of_j0(q) for q in range(self.NJ + 1)]

    def rank(self, R) -> int:
        return sum(math.comb(r, t + 1) for t, r in enumerate(R))

    def _pmax(self, t: int, v: int, lo: int, hi: int) -> int:
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if math.comb(mid, t) <= v:
                lo = mid
            else:
                hi = mid - 1
        return lo

    def unrank(self, rank: int, a: int | None = None) -> list:
        a = self.a if a is None else a
        R = [0] * a
        hi = self.n
        for t in range(a - 1, -1, -1):
            p = self._pmax(t + 1, rank, t, hi - 1)
            R[t] = p
            rank -= math.comb(p, t + 1)
            hi = p
        return R

    def row_max(self, rank: int) -> int:
        return self._pmax(self.a, rank, self.a - 1, self.n - 1)

    def tile_j0(self, t: int) -> int:
        return (self.row_max(16 * t) + 1) // 16

    def tile_of_j0(self, q: int) -> int:
        if q <= 0:
            return 0
        p = 16 * q - 1
        if p > self.n - 2:
            return self.NT
        return min((math.comb(p, self.a) + 15) // 16, self.NT)

    def runs(self):
        """[(t_begin, t_end, nJ)]: row tiles grouped by their number of column tiles (non-increasing in t)."""
        return [(self.Tq[q], self.Tq[q + 1], self.NJ - q) for q in range(self.NJ) if self.Tq[q + 1] > self.Tq[q]]

    def range_outtiles(self, t0: int, t1: int) -> int:
        return sum(max(0, min(b, t1) - max(a, t0)) * nJ for a, b, nJ in self.runs())

    def range_cands(self, t0: int, t1: int) -> int:
        r0, r1 = 16 * t0, min(16 * t1, self.NR)
        tot = 0
        for p in range(self.a - 1, self.n - 1):
            a0, a1 = math.comb(p, self.a), math.comb(p + 1, self.a)
            lo, hi = max(a0, r0), min(a1, r1)
            if hi > lo:
                tot += (hi - lo) * (self.n - 1 - p)
        return tot

    def colex_key(self, j: int, row: int) -> int:
        return math.comb(j, self.k) + row

    def found_set(self, row: int, j: int) -> tuple:
        return tuple(self.unrank(row)) + (j,)


def score(I: Instance, G: "Geom", row: int, j: int) -> int:
    """c(T) for the candidate (row, j) on instance I: m - 2 popcount(y ^ x_R ^ x_j)."""
    v = I.y.copy()
    for r in G.unrank(row) + [j]:
        v ^= I.X[r]
    return I.m - 2 * int(np.unpackbits(v.view(np.uint8)).sum())


# ---------------------------------------------------------------- checksums
def krawtchouk(n: int, k: int) -> list:
    return [sum((-1) ** t * math.comb(w, t) * math.comb(n - w, k - t) for t in range(k + 1)) for w in range(n + 1)]


def closed_forms(I: Instance):
    """(sum_c, sum_c2 exact, sum_c2 mod 2^64) over all C(n,k) candidates, from the data alone."""
    xb, yb = I.bits()
    yt = 1 - 2 * yb.astype(np.int64)
    w = xb.sum(axis=1).astype(np.int64)
    K = krawtchouk(I.n, I.k)
    s1 = sum(int(yt[i]) * K[int(w[i])] for i in range(I.m))
    xf = xb.astype(np.float64)
    G = xf @ xf.T                                        # exact: entries <= n < 2^53
    D = (w[:, None] + w[None, :] - 2 * np.rint(G).astype(np.int64))
    kmax = max(abs(v) for v in K)
    if kmax * I.m < (1 << 62):
        Karr = np.array(K, dtype=np.int64)
        rows = (Karr[D] * yt[None, :]).sum(axis=1)       # per-row sums fit int64
        s2 = sum(int(yt[i]) * int(rows[i]) for i in range(I.m))
    else:                                                # huge n, k: exact Python integers
        s2 = 0
        for i in range(I.m):
            s2 += int(yt[i]) * sum(int(yt[j]) * K[int(D[i, j])] for j in range(I.m))
    return s1, s2, s2 & M64


def brute(I: Instance):
    """{colex rank of T: c(T)} for every k-subset, by direct +-1 products (tests only; C(n,k) <= ~3e5)."""
    xb, yb = I.bits()
    xp = 1 - 2 * xb.astype(np.int32)
    yp = 1 - 2 * yb.astype(np.int32)
    T = np.array(list(itertools.combinations(range(I.n), I.k)), dtype=np.int64)
    prod = yp[:, None] * np.ones((1, len(T)), dtype=np.int32)
    for q in range(I.k):
        prod = prod * xp[:, T[:, q]]
    c = prod.sum(axis=0)
    keys = sum(np.array([math.comb(int(v), q + 1) for v in T[:, q]], dtype=np.int64) for q in range(I.k))
    return dict(zip(keys.tolist(), c.tolist())), T


# ---------------------------------------------------------------- binary formats (sp.h section 6)
WL_MAGIC, WL_VERSION = 0x4C575053, 1
WL_TWOSTAGE, WL_COOP = 1, 2
WL_HDR = struct.Struct("<12I i 3I Q 5Q 2Q")          # 128 B
WL_MINION = struct.Struct("<4I")                      # 16 B
WL_RANGE = struct.Struct("<5Q 6H 3I")                 # 64 B
OUT_MAGIC, REC_MAGIC = 0x314F5053, 0x31525053
OUT_HDR = struct.Struct("<8I 4Q")                     # 64 B
REC = struct.Struct("<I H H I i Q I I q Q Q Q")      # 64 B
TOP = struct.Struct("<i I Q")                         # 16 B
REC_VALID, REC_HAS_BEST, REC_LOG_OVERFLOW, REC_ERROR, REC_TIE = 1, 2, 4, 8, 16
assert WL_HDR.size == 128 and WL_MINION.size == 16 and WL_RANGE.size == 64
assert OUT_HDR.size == 64 and REC.size == 64 and TOP.size == 16

HDR_FIELDS = ("magic version n k m S nshires mps nminions nranges topm flags tau1 slice nslices blocks_per_minion "
              "shire_mask NR NT total_ops total_cands total_cyc".split())


@dataclass
class WorkList:
    hdr: dict
    minions: list = field(default_factory=list)     # [(first_range, nranges, shire, minion_in_shire)]
    ranges: list = field(default_factory=list)      # [dict(tile_begin, tile_end, ops, cands, cyc, first_R, minion, block)]

    def to_bytes(self) -> bytes:
        h = self.hdr
        out = [WL_HDR.pack(WL_MAGIC, WL_VERSION, h["n"], h["k"], h["m"], h["S"], h["nshires"], h["mps"],
                           h["nminions"], len(self.ranges), h["topm"], h["flags"], h["tau1"], h["slice"],
                           h["nslices"], h["blocks_per_minion"], h["shire_mask"], h["NR"], h["NT"],
                           h["total_ops"], h["total_cands"], h["total_cyc"], 0, 0)]
        out += [WL_MINION.pack(*mi) for mi in self.minions]
        for r in self.ranges:
            fr = list(r["first_R"]) + [0xFFFF] * (KMAX - len(r["first_R"]))
            out.append(WL_RANGE.pack(r["tile_begin"], r["tile_end"], r["ops"], r["cands"], int(round(r["cyc"])),
                                     *fr, r["minion"], r["block"], 0))
        return b"".join(out)

    @staticmethod
    def from_bytes(b: bytes) -> "WorkList":
        v = WL_HDR.unpack_from(b, 0)
        if v[0] != WL_MAGIC or v[1] != WL_VERSION:
            raise ValueError("not a version-1 work list")
        hdr = dict(zip(HDR_FIELDS, v[:22]))
        o = WL_HDR.size
        minions = [WL_MINION.unpack_from(b, o + i * 16) for i in range(hdr["nminions"])]
        o += 16 * hdr["nminions"]
        ranges = []
        for i in range(hdr["nranges"]):
            f = WL_RANGE.unpack_from(b, o + i * 64)
            ranges.append(dict(tile_begin=f[0], tile_end=f[1], ops=f[2], cands=f[3], cyc=f[4],
                               first_R=[x for x in f[5:11] if x != 0xFFFF], minion=f[11], block=f[12]))
        return WorkList(hdr, minions, ranges)


REC_FIELDS = "magic hart flags minion best_c best_row best_j ops sum_c sum_c2 cands cycles".split()


def read_out(b: bytes):
    """-> (header dict, records [dict] indexed minion*harts + hart, tops [[(c, j, row)]] per minion)."""
    v = OUT_HDR.unpack_from(b, 0)
    hdr = dict(zip("magic version nminions harts topm n k m nranges total_ops total_cands reserved".split(), v))
    if hdr["magic"] != OUT_MAGIC:
        raise ValueError("not an sp output file")
    o = OUT_HDR.size
    nrec = hdr["nminions"] * hdr["harts"]
    recs = [dict(zip(REC_FIELDS, REC.unpack_from(b, o + 64 * i))) for i in range(nrec)]
    o += 64 * nrec
    tops = []
    for q in range(hdr["nminions"]):
        lst = []
        for i in range(hdr["topm"]):
            c, j, row = TOP.unpack_from(b, o + 16 * (q * hdr["topm"] + i))
            if c != INT32_MIN:
                lst.append((c, j, row))
        tops.append(lst)
    return hdr, recs, tops


def surv_unpack(e: int):
    return e & 0xFFFFFFFFFF, (e >> 40) & 0xFFF, e >> 52       # row, j, c1


def better(a, b) -> bool:
    """(c, j, row) a is better than b: larger c, then smaller colex rank (smaller j, then smaller row)."""
    return a[0] > b[0] or (a[0] == b[0] and (a[1], a[2]) < (b[1], b[2]))


def sort_key(e):
    return (-e[0], e[1], e[2])
