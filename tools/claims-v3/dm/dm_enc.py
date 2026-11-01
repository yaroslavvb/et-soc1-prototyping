#!/usr/bin/env python3
"""E99 (V3-DM): the line-level encoder. Bytes of an image -> what the LPDDR4X pins and the wide paths would carry.

The public facts it encodes (each re-found in the public source, tools/claims-v3/dm/README.md section 1):

  * 16 channels, each 16 data pins (two byte lanes) plus one DMI pin per lane: PRM section 1.5; the memory shire
    removes address bits 9:6 (core-et/rtl/inc/esr_defines.vh ESR_MS_MEM_CTL_RESET_VAL), bit 9 picks the controller,
    so a 64 B line goes to one channel and each channel carries every 16th line of the physical address. That bits
    8:6 pick the memory shire is inferred from those removal bits.
  * burst_rdwr = 8, so BL16: a 64 B line moves as two 32 B bursts, 32 beats in all, two bytes per beat (MSTR in
    etsoc-hal/src/memshire_ddr_init_functions.c). In-order byte order is assumed; a swap of the two lanes, or of the
    pins inside a lane, changes no count below.
  * read DBI on (DBICTL 7, DRAM mode register 3 = 0xF1, the PHY's RdDbiEnabled = 1), the DC rule of the LPDDR4 standard
    (from memory of JESD209-4, not in the repo): a byte with more than four ones is sent inverted, with its DMI pin
    high. So pins driven high per byte = p if p <= 4, else 9 - p: 0 1 2 3 4 4 3 2 1 for p = 0..8.
  * the PHY terminates reads to ground only (TxOdtDrvStren ODTStrenN = 0x38, ODTStrenP = 0), so a pin driven high
    draws DC and a pin driven low does not.

Everything is per 64 B line, on the bytes as they sit in a hart's region.
"""
import numpy as np

LINE = 64
POP = np.array([bin(i).count("1") for i in range(256)], dtype=np.int64)
HIGH = np.where(POP > 4, 9 - POP, POP)                                  # pins driven high per byte, DMI included
# ENC[b] = the 9 pins of one lane for byte b: bits 0..7 are DQ, bit 8 is DMI
ENC = np.where(POP > 4, (~np.arange(256) & 0xFF) | 0x100, np.arange(256)).astype(np.int64)
POP9 = np.array([bin(i).count("1") for i in range(512)], dtype=np.int64)


def lines_of(blob):
    """bytes -> (n_lines, 64) uint8 array."""
    a = np.frombuffer(blob, dtype=np.uint8)
    if a.size % LINE:
        raise ValueError("an image is a whole number of 64 B lines")
    return a.reshape(-1, LINE)


def within_toggles(L, table):
    """Pin toggles between consecutive beats inside one line, per line. Lane 0 carries bytes 0, 2, 4, ...; lane 1
    bytes 1, 3, 5, ... (31 transitions per lane; the two BL16 bursts are taken as seamless, which they are when the
    second follows at tCCD; a gap would drop 2 of the 62 transitions)."""
    e = table[L]
    return POP9[e[:, 2:] ^ e[:, :-2]].sum(axis=1)


def across_toggles(L, nxt, table):
    """Pin toggles from the last beat of line L to the first beat of the line that follows it on the channel."""
    a, b = table[L], table[nxt]
    return POP9[a[:, 62] ^ b[:, 0]] + POP9[a[:, 63] ^ b[:, 1]]


def bit_distance(A, B):
    return POP[A ^ B].sum(axis=1)


def counts(L, stream_lines=2048, pairs_seed=7):
    """Per-line means for a periodic image L (its lines in address order, period = len(L)), as a stream of address
    order reads it. The image is assumed to start at a line aligned to the 16-way channel interleave (host slices and
    the kernel's bank offsets are multiples of 1 KB); the alignment only rotates the channels and changes no count."""
    n = len(L)
    idn = np.arange(256, dtype=np.int64)
    out = {}
    out["period_lines"] = int(n)
    out["distinct_lines"] = int(len(np.unique(L, axis=0)))
    out["w"] = float(POP[L].sum(axis=1).mean())
    out["hi"] = float(HIGH[L].sum(axis=1).mean())
    out["dmi_hi"] = float((POP[L] > 4).sum(axis=1).mean())
    out["t_enc"] = float(within_toggles(L, ENC).mean())
    out["t_raw"] = float(within_toggles(L, idn).mean())
    nxt = np.roll(L, -1, axis=0)
    out["k"] = float(bit_distance(L, nxt).mean())
    out["half"] = float(bit_distance(L[:, :32], L[:, 32:]).mean())
    # the byte multiset, for the design's own check
    hist = np.bincount(POP[L].ravel(), minlength=9) / max(1, L.size) * LINE
    out["byte_pop_per_line"] = [float(x) for x in hist]
    # what one path that carries every Nth line sees: distinct values, and the bits that change between two reads of
    # that path. Harts run at different phases of the image, so the two reads are two independent draws from the
    # values at that path's addresses (the same line counts as no change).
    for way, name in ((8, "shire"), (16, "chan"), (128, "bank")):
        d, nv = path_distance(L, way, pairs_seed)
        out["k_" + name] = d
        out["n_" + name] = nv
    # the same independent-draw reading for the pins' last-beat-to-first-beat toggles on a channel
    te, tr = channel_across(L, pairs_seed)
    out["tx_enc"] = te
    out["tx_raw"] = tr
    return out


def path_values(n, way):
    """Which image lines one path of a `way`-way line interleave sees, for each of its phases: a list of index arrays."""
    return [np.arange(c, c + n * way) % n for c in range(way)][: way]


def path_distance(L, way, seed=7):
    """Mean over the paths of the bits that differ between two independent reads of that path, and the mean number of
    distinct values a path sees."""
    n = len(L)
    rng = np.random.default_rng(seed)
    ds, nv = [], []
    step = way
    g = np.gcd(n, step)
    n_distinct_idx = n // g
    if n <= 4096:
        for c in range(way):
            idx = (c + step * np.arange(n_distinct_idx)) % n
            vals = np.unique(L[idx], axis=0)
            nv.append(len(vals))
            if len(vals) == 1:
                ds.append(0.0)
                continue
            d = POP[vals[:, None, :] ^ vals[None, :, :]].sum(axis=2) if len(vals) <= 512 else None
            if d is not None:
                ds.append(float(d.mean()))                     # includes the same-value pairs, on purpose
            else:
                i, j = rng.integers(0, len(vals), 20000), rng.integers(0, len(vals), 20000)
                ds.append(float(bit_distance(vals[i], vals[j]).mean()))
    else:
        for c in range(0, way):
            idx = (c + step * np.arange(n_distinct_idx)) % n
            vals = L[idx]
            nv.append(len(np.unique(vals, axis=0)))
            i, j = rng.integers(0, len(vals), 20000), rng.integers(0, len(vals), 20000)
            ds.append(float(bit_distance(vals[i], vals[j]).mean()))
    return float(np.mean(ds)), float(np.mean(nv))


def channel_across(L, seed=7):
    n = len(L)
    idn = np.arange(256, dtype=np.int64)
    g = np.gcd(n, 16)
    m = n // g
    rng = np.random.default_rng(seed)
    te, tr = [], []
    for c in range(16):
        idx = (c + 16 * np.arange(m)) % n
        vals = L[idx]
        if len(vals) <= 64:
            i, j = np.meshgrid(np.arange(len(vals)), np.arange(len(vals)))
            i, j = i.ravel(), j.ravel()
        else:
            i, j = rng.integers(0, len(vals), 20000), rng.integers(0, len(vals), 20000)
        te.append(float(across_toggles(vals[i], vals[j], ENC).mean()))
        tr.append(float(across_toggles(vals[i], vals[j], idn).mean()))
    return float(np.mean(te)), float(np.mean(tr))
