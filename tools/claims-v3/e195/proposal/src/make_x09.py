#!/usr/bin/env python3
"""x09: the arm table, the designed counts per 64 B line, and the runner's manifest.

    python3 make_x09.py GEN_DIR [--host BUILD/host/x09mem_host] [--check] [--seed 1] [--no-ms]

Writes GEN_DIR/manifest.json (items for the public lab repo's tools/claims-v3/runitems.py: the drift anchor
`anchor_pi` and one `x9_*` item per arm, each with the host's arguments and its designed counts) and
GEN_DIR/counts.json. With --host, every arm's bytes are also taken from the host itself (`--dump-image`, which opens
no device) and every count is computed again from those bytes; --check fails (exit 1) on any difference between the
two computations, or on a host arm table that differs from this one.

Every x9_ item runs the host as `--item NAME --seconds %ITEM_S% --stop-file build/x09-STOP`: the session's stop file,
relative to the tree's root, where the runner runs (once it exists the host starts no further launch). With --no-ms
every x9_ item also gets the host's `--no-ms`: the memory shires' counters are not read, the manifest says "ms": false,
the smoke gate does not ask for them and the reducer's C6 reads NO DATA. The counts are written to 12 significant
digits, so the two files' bytes do not depend on numpy's version.

The counts follow the rules the public lab repo's E99 harness uses (tools/claims-v3/dm/dm_enc.py), from public
facts: 16 channels of 16 data pins and 2 inversion pins, a 64 B line as two 16-beat bursts on one channel, bytes in
order on two lanes (lane 0 even bytes, lane 1 odd bytes), every 16th line of the physical address on one channel,
and the data-bus inversion rule of the LPDDR4 standard (DC: a byte with more than four ones is sent inverted, its
inversion pin high), assumed live in both directions. Per line:

    w        ones in the raw data
    hi       pins driven high, inversion pins included (min(p, 9 - p) per byte of p ones)
    dmi      inversion pins high
    t_enc    pin toggles between consecutive beats inside the line (31 a lane, the two bursts taken as seamless)
    t_raw    the same on the raw bytes
    p64      bits changed between consecutive 8-byte pieces of the line (7 inner edges)
    half     bits that differ between the line's two 32 B halves
    k_chan   bits changed between two lines that follow each other on one channel (two independent draws from the
             lines that channel carries, the same line counting as no change: the harts run at different phases)
    tx_enc   pin toggles from the last beat of one line to the first beat of the next on the channel (same model)
    tx_raw   the same on the raw bytes (t_raw + tx_raw: the pin toggles if inversion were off; hi would then be w)
    x64      bits changed from the last 8-byte piece of one line to the first piece of the next (same model)
    x256     bits changed from the second 32 B half of one line to the first half of the next (same model)
    lines_ch distinct lines one channel carries (mean over the channels)
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

import numpy as np

LINE = 64
POP = np.array([bin(i).count("1") for i in range(256)], dtype=np.int64)
HIGH = np.where(POP > 4, 9 - POP, POP)
ENC = np.where(POP > 4, (~np.arange(256) & 0xFF) | 0x100, np.arange(256)).astype(np.int64)
POP9 = np.array([bin(i).count("1") for i in range(512)], dtype=np.int64)
IDN = np.arange(256, dtype=np.int64)

RD_PERIOD, WR_PERIOD = 1024, 8192
# name, mode, image, period, family, role. The same table as the host's (--list --json); --check compares them.
ARMS = [
    ("rd.z", "rd", "z", 0, "rd", "control"),
    ("rd.w1", "rd", "first:01", 0, "rd", "floor"),
    ("rd.u2", "rd", "b:03", 0, "rd", "tent"),
    ("rd.u4", "rd", "b:0f", 0, "rd", "tent"),
    ("rd.u7", "rd", "b:7f", 0, "rd", "tent"),
    ("rd.u8", "rd", "b:ff", 0, "rd", "tent"),
    ("rd.l08", "rd", "alt:00:ff:1", 0, "rd", "inversion"),
    ("rd.a44", "rd", "alt:0f:f0:2", 0, "rd", "toggle"),
    ("rd.rnd", "rd", "rnd", 0, "rd", "random"),
    ("wr.z", "wr", "z", 0, "wr", "control"),
    ("wr.w1", "wr", "first:01", 0, "wr", "floor"),
    ("wr.u2", "wr", "b:03", 0, "wr", "tent"),
    ("wr.u4", "wr", "b:0f", 0, "wr", "tent"),
    ("wr.u7", "wr", "b:7f", 0, "wr", "tent"),
    ("wr.u8", "wr", "b:ff", 0, "wr", "tent"),
    ("wr.l08", "wr", "alt:00:ff:1", 0, "wr", "inversion"),
    ("wr.a08", "wr", "alt:00:ff:2", 0, "wr", "inversion"),
    ("wr.a44", "wr", "alt:0f:f0:2", 0, "wr", "toggle"),
    ("wr.p64", "wr", "alt:0f:f0:8", 0, "wr", "path64"),
    ("wr.h256", "wr", "alt:0f:f0:32", 0, "wr", "half"),
    ("wr.c44", "wr", "par:0f:f0", 0, "wr", "channel"),
    ("wr.rnd", "wr", "rnd", 0, "wr", "random"),
    ("rdh.z", "rd", "z", RD_PERIOD, "rdh", "control"),
    ("rdh.u4", "rd", "b:0f", RD_PERIOD, "rdh", "tent"),
    ("rdh.rnd", "rd", "rnd", RD_PERIOD, "rdh", "random"),
    ("rdh.l1", "rdl1", "z", RD_PERIOD, "rdh", "no-traffic control"),
    ("wrh.z", "wr", "z", WR_PERIOD, "wrh", "control"),
    ("wrh.u4", "wr", "b:0f", WR_PERIOD, "wrh", "tent"),
    ("wrh.rnd", "wr", "rnd", WR_PERIOD, "wrh", "random"),
    ("wrh.scp", "wrscp", "z", WR_PERIOD, "wrh", "no-traffic control"),
    ("wrh.nst", "wrnst", "z", WR_PERIOD, "wrh", "no-traffic control"),
]
READ_REGION, WRITE_REGION = 128 * 1024, 256 * 1024


# ---- the images, the host's rules re-stated (host/main.cpp, fillLine) ------------------------------------------
def stream(seed, who):
    """The host's random stream of one hart (reads) or minion (writes): std::mt19937_64 seeded once with
    seed*0x9E3779B97F4A7C15 ^ (who << 32), eight draws a line, little-endian, line after line. Re-implemented here
    so the check is independent of the host's code."""
    return MT64(((seed * 0x9E3779B97F4A7C15) ^ (who << 32)) & 0xFFFFFFFFFFFFFFFF)


class MT64:
    """The 64-bit Mersenne Twister (std::mt19937_64), for the random images."""
    def __init__(self, seed):
        self.mt = [0] * 312
        self.mt[0] = seed & 0xFFFFFFFFFFFFFFFF
        for i in range(1, 312):
            self.mt[i] = (6364136223846793005 * (self.mt[i - 1] ^ (self.mt[i - 1] >> 62)) + i) & 0xFFFFFFFFFFFFFFFF
        self.i = 312

    def next(self):
        if self.i >= 312:
            for k in range(312):
                y = (self.mt[k] & 0xFFFFFFFF80000000) | (self.mt[(k + 1) % 312] & 0x7FFFFFFF)
                v = self.mt[(k + 156) % 312] ^ (y >> 1)
                if y & 1:
                    v ^= 0xB5026F5AA96619E9
                self.mt[k] = v
            self.i = 0
        y = self.mt[self.i]
        self.i += 1
        y ^= (y >> 29) & 0x5555555555555555
        y ^= (y << 17) & 0x71D67FFFEDA60000
        y ^= (y << 37) & 0xFFF7EEE000000000
        y ^= y >> 43
        return y & 0xFFFFFFFFFFFFFFFF


def line_bytes(spec, who, line, rng, writes):
    """One 64 B line; `rng` is who's stream (stream()), drawn only by the random rule."""
    f = spec.split(":")
    if f[0] == "z":
        return bytes(64)
    if f[0] == "b":
        return bytes([int(f[1], 16)]) * 64
    if f[0] == "first":
        return bytes([int(f[1], 16)]) + bytes(63)
    if f[0] == "alt":
        x, y, n = int(f[1], 16), int(f[2], 16), int(f[3])
        return bytes([y if (j // n) & 1 else x for j in range(64)])
    if f[0] == "par":
        x, y = int(f[1], 16), int(f[2], 16)
        second = (who & 1) if writes else ((line >> 4) & 1)
        return bytes([y if second else x]) * 64
    if f[0] == "rnd":
        return b"".join(int(rng.next()).to_bytes(8, "little") for _ in range(8))
    raise ValueError("unknown image " + spec)


def who_lines(spec, who, nlines, seed, writes):
    """The first nlines lines of one hart's region (reads) or minion's image (writes)."""
    g = stream(seed, who)
    return b"".join(line_bytes(spec, who, l, g, writes) for l in range(nlines))


# ---- the counts ----------------------------------------------------------------------------------------------
def per_line(L):
    """L: (n, 64) uint8 lines -> dict of per-line arrays."""
    L = L.astype(np.int64)
    e = ENC[L]
    out = {
        "w": POP[L].sum(axis=1),
        "hi": HIGH[L].sum(axis=1),
        "dmi": (POP[L] > 4).sum(axis=1),
        "t_enc": POP9[e[:, 2:] ^ e[:, :-2]].sum(axis=1),
        "t_raw": POP[L[:, 2:] ^ L[:, :-2]].sum(axis=1),
        "half": POP[L[:, :32] ^ L[:, 32:]].sum(axis=1),
    }
    pieces = L.reshape(-1, 8, 8)
    out["p64"] = POP[pieces[:, 1:, :] ^ pieces[:, :-1, :]].sum(axis=(1, 2))
    return out


def channel_stats(pop_lines, rng, ndraw=20000):
    """Two independent draws (A then B) from the lines one channel carries, the same line allowed: bits changed
    (k_chan), pin toggles from A's last beat to B's first (tx_enc; tx_raw on the raw bytes), bits changed from A's
    last 8-byte piece to B's first (x64) and from A's second half to B's first half (x256), and the distinct lines
    the channel carries."""
    V, cnt = np.unique(pop_lines, axis=0, return_counts=True)
    V = V.astype(np.int64)
    if len(V) <= 64:   # exact: every ordered pair, weighted by how often each value occurs
        i, j = np.meshgrid(np.arange(len(V)), np.arange(len(V)))
        i, j = i.ravel(), j.ravel()
        wv = cnt / cnt.sum()
        wt = wv[i] * wv[j]
        A, B = V[i], V[j]
    else:
        P = pop_lines.astype(np.int64)
        A, B = P[rng.integers(0, len(P), ndraw)], P[rng.integers(0, len(P), ndraw)]
        wt = np.full(len(A), 1.0 / len(A))
    ea, eb = ENC[A], ENC[B]
    k = (POP[A ^ B].sum(axis=1) * wt).sum()
    tx = ((POP9[ea[:, 62] ^ eb[:, 0]] + POP9[ea[:, 63] ^ eb[:, 1]]) * wt).sum()
    txr = ((POP[A[:, 62] ^ B[:, 0]] + POP[A[:, 63] ^ B[:, 1]]) * wt).sum()
    x64 = (POP[A[:, 56:] ^ B[:, :8]].sum(axis=1) * wt).sum()
    x256 = (POP[A[:, 32:] ^ B[:, :32]].sum(axis=1) * wt).sum()
    return float(k), float(tx), float(txr), float(x64), float(x256), int(len(V))


_BLOBS = {}


def rule_blob(mode, spec, seed):
    """The bytes an arm moves, by this file's rules (cached: rd.rnd and rdh.rnd move the same bytes)."""
    writes = mode in ("wr", "wrscp", "wrnst")
    key = (writes, spec, seed)
    if key not in _BLOBS:
        if writes:
            _BLOBS[key] = b"".join(who_lines(spec, m, 8, seed, True) for m in range(1024))
        else:
            nl = READ_REGION // 64
            if spec == "rnd":
                _BLOBS[key] = b"".join(who_lines(spec, h, nl, seed, False) for h in (0, 2, 4))
            else:
                _BLOBS[key] = who_lines(spec, 0, nl, seed, False) * 3
    return _BLOBS[key]


def arm_lines(name, mode, spec, seed, source=None):
    """The lines an arm moves and, per channel, the population of lines that channel carries.

    Reads: harts 0, 2, 4 (three regions; designed images are the same in every region, random ones differ), every
    line of each 128 KB region; line l of a region goes to channel l mod 16 (regions start on 1 KB boundaries).
    Writes: all 1,024 minions' 512 B images; line j of an image goes to channel j or j + 8, so channel c carries line
    c mod 8 of every minion's image."""
    writes = mode in ("wr", "wrscp", "wrnst")
    blob = source if source is not None else rule_blob(mode, spec, seed)
    L = np.frombuffer(blob, dtype=np.uint8).reshape(-1, 64)
    chans = []
    if writes:
        Lm = L.reshape(1024, 8, 64)
        for c in range(16):
            chans.append(Lm[:, c % 8, :])
    else:
        nl = len(L) // 3
        idx = np.arange(len(L)) % nl
        for c in range(16):
            chans.append(L[(idx % 16) == c])
    return L, chans


def counts_for(name, mode, spec, seed, source=None):
    L, chans = arm_lines(name, mode, spec, seed, source)
    pl = per_line(L)
    out = {k: float(v.mean()) for k, v in pl.items()}
    rng = np.random.default_rng(7)
    ks, txs, txrs, x64s, x256s, ns = zip(*(channel_stats(c, rng) for c in chans))
    out["k_chan"] = float(np.mean(ks))
    out["tx_enc"] = float(np.mean(txs))
    out["tx_raw"] = float(np.mean(txrs))
    out["x64"] = float(np.mean(x64s))
    out["x256"] = float(np.mean(x256s))
    out["lines_ch"] = float(np.mean(ns))
    if mode in ("rdl1", "wrscp", "wrnst"):   # no DRAM traffic: no line on a channel
        out = {k: 0.0 for k in out}
        out["no_dram"] = 1
    out = {k: float(f"{v:.12g}") if isinstance(v, float) else v for k, v in out.items()}   # 12 significant digits
    out["sha256_bytes"] = hashlib.sha256(L.tobytes()).hexdigest()
    return out


def host_arms(host):
    r = subprocess.run([host, "--list", "--json"], capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise SystemExit("host --list failed: " + r.stderr[-300:])
    return json.loads(r.stdout)


def host_bytes(host, arm, seed, tmp):
    r = subprocess.run([host, "--item", arm, "--seed", str(seed), "--dump-image", tmp], capture_output=True,
                       text=True, timeout=300, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise SystemExit(f"host --dump-image {arm} failed: " + r.stderr[-300:])
    with open(tmp, "rb") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gen")
    parser.add_argument("--host", default="")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--no-ms", action="store_true", help="every x9_ item without the memory shires' counters")
    a = parser.parse_args()
    os.makedirs(a.gen, exist_ok=True)
    if a.check and not a.host:
        raise SystemExit("--check needs --host")
    bad = []
    if a.host:
        ha = host_arms(a.host)
        mine = [{"name": n, "mode": m, "image": i, "period": p} for n, m, i, p, _, _ in ARMS]
        theirs = [{k: x[k] for k in ("name", "mode", "image", "period")} for x in ha]
        if mine != theirs:
            bad.append("the host's arm table differs from this one")
    table = {}
    for name, mode, spec, period, fam, role in ARMS:
        c = counts_for(name, mode, spec, a.seed)
        if a.host:
            tmp = os.path.join(a.gen, "dump.bin")
            src = host_bytes(a.host, name, a.seed, tmp)
            os.remove(tmp)
            if mode in ("rdl1", "wrscp", "wrnst"):
                ch = dict(c)
            else:
                ch = counts_for(name, mode, spec, a.seed, source=src)
            for k in c:
                if k == "sha256_bytes":
                    if c[k] != ch[k]:
                        bad.append(f"{name}: the host's bytes differ from the rule ({ch[k][:12]} against {c[k][:12]})")
                elif abs(c[k] - ch[k]) > 1e-9:
                    bad.append(f"{name}: {k} {ch[k]} from the host's bytes against {c[k]}")
        table[name] = {"mode": mode, "image": spec, "period": period, "family": fam, "role": role, "counts": c}
    items = [{"name": "anchor_pi", "kind": "fma", "family": "anchor", "values": "pi"}]
    for name, mode, spec, period, fam, role in ARMS:
        cc = {k: v for k, v in table[name]["counts"].items() if k != "sha256_bytes"}
        args = ["--item", name, "--seconds", "%ITEM_S%", "--stop-file", "build/x09-STOP"] + (["--no-ms"] if a.no_ms else [])
        items.append({"name": "x9_" + name.replace(".", "_"), "kind": "cmd", "tool": "main",
                      "args": args, "tag": "X09MEM {",
                      "family": fam, "role": role, "designed": cc})
    man = {"exp": "x09", "what": "memory traffic with designed data: ones against toggles, read and written",
           "seed": a.seed, "ms": not a.no_ms, "items": items}
    with open(os.path.join(a.gen, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1)
    with open(os.path.join(a.gen, "counts.json"), "w") as f:
        json.dump(table, f, indent=1)
    keys = ["w", "hi", "dmi", "t_enc", "t_raw", "p64", "half", "k_chan", "tx_enc", "tx_raw", "x64", "x256", "lines_ch"]
    print("arm      period " + " ".join(f"{k:>8s}" for k in keys))
    for name, mode, spec, period, fam, role in ARMS:
        c = table[name]["counts"]
        print(f"{name:8s} {period:6d} " + " ".join(f"{c[k]:8.2f}" for k in keys))
    if bad:
        print("CHECK FAIL:")
        for b in bad:
            print("  " + b)
        sys.exit(1)
    if a.check:
        print(f"CHECK OK: {len(ARMS)} arms, the host's bytes and arm table agree with this file's rules")


if __name__ == "__main__":
    main()
