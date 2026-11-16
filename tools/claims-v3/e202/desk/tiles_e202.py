#!/usr/bin/env python3
"""E202's registration, desk: the operand statistics of the tile pairs E202's kernel issues, and of the lab's committed
int8 kinds, for the tensor-data price (E202.md section 4.2) and the bytes' data shares (section 4.3).

    /usr/bin/python3 -I -B tools/claims-v3/e202/desk/tiles_e202.py --files FILES --data DATA --out tiles-e202.json

FILES holds mnist-int8-trained.mlpw and mnist-int8-random.mlpw, DATA the decompressed train-images-idx3-ubyte; each is
accepted only by its sha256 in workloads/mnistmlp/model/PINS-SHA256SUMS (the program's pins). Nothing here runs on a
card or opens a device.

WHAT IT COMPUTES
1. The tile pairs, exactly as the kernel issues them (workloads/mnistmlp/model/mnist_model.py, imported unchanged: its
   read_mlpw, load_images, matmul_exact, requant and pack_b_tile; the same loop order as its dump-tiles command): for a
   group of 16 images, layer l, column block c, k tile t, the A tile (16 images x 64 uint8 activations) and the B tile
   (16 lines x 64 int8 as TenB holds them). Groups sampled by a rule fixed before any count: g_i = floor(i x 3750 / 8),
   i = 0..7 (0, 468, 937, 1406, 1875, 2343, 2812, 3281): 8 groups, 87,136 pairs a configuration, every layer's every
   weight tile 8 times.
2. Per pair, the lab's two tile numbers (tools/claims-v3/kinds/make_kinds.py two_numbers, the kinds table's own pair):
   g, the share of the op's 2,048 gate decisions the int8 zero gate turns off (an all-zero A word, or all eight bytes of
   a B column pair zero: make_kinds gate_mask, read off the RTL), and b, the operand bits the unit's input bus flips in
   one op (bus_bits_per_op). Computed here with numpy over many pairs at once, by make_kinds' own formulas, and checked
   EQUAL to make_kinds.two_numbers (unchanged) on every 97th pair (section "check").
3. Per layer and over all ops (each op weighted once, as the ledger prices ops): the means of g and b, their 5th, 50th
   and 95th percentiles, the zero-word and zero-element shares of A and B (make_kinds side_stats' definitions).
4. The bytes' data shares (tools/ledger/ledger_v2.py phi's inputs): rho, the share of set bits, and tau, the share of bits
   that change between successive elements (bytes, the ledger's own int8 convention: loads_ledger_v2.py DATA pm1_int8),
   in memory order, line by line, tile by tile in issue order: for the A tiles, the B tiles, the input tiles (layer 1's A
   tiles: the pixels), the activation stores (the bytes layers 1-4 write: layers 2-5's A data), and the weights once in
   issue order (what the chunk copies and the resident copy move).
5. The committed int8 kinds on aifoundry3 that M10 has rows for (docs/reports/data/2026-11-04-q142m-m10/rows-m10.json,
   card a3): each kind's committed tile(s) (rows-m9.json tile_path for the a3 rows; tools/claims-v3/kinds/blind7/
   blind7.json for E163's), each checked against its committed sha256, and its (g, b) by make_kinds.two_numbers itself
   (the mean over the kind's a3 tiles where it has several).
Interpreter: /usr/bin/python3 3.12.3 with numpy 1.26.4 wrote tiles-e202.json (named in the file).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import importlib.util
import json
import os
import platform
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
MODEL = "workloads/mnistmlp/model/mnist_model.py"
KINDS = "tools/claims-v3/kinds/make_kinds.py"
PINS = "workloads/mnistmlp/model/PINS-SHA256SUMS"
M10_ROWS = "docs/reports/data/2026-11-04-q142m-m10/rows-m10.json"
M9_ROWS = "docs/reports/data/2026-11-04-q140m-m9/rows-m9.json"
BLIND7 = "tools/claims-v3/kinds/blind7/blind7.json"
NSAMPLE = 8
GROUPS = [i * 3750 // NSAMPLE for i in range(NSAMPLE)]
CHECK_EVERY = 97
CONFIGS = {"trained": "mnist-int8-trained.mlpw", "random": "mnist-int8-random.mlpw"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def pins():
    out = {}
    for ln in open(os.path.join(REPO, PINS)):
        if ln.strip():
            h, n = ln.split(None, 1)
            out[n.strip()] = h
    return out


def words(tiles_u8):
    """(n, 16, 64) bytes -> (n, 16, 16) little-endian 32-bit words: make_kinds.words_of's grid, row = line."""
    return np.ascontiguousarray(tiles_u8).view("<u4").reshape(tiles_u8.shape[0], 16, 16).astype(np.uint32)


def two_numbers_many(MK, aw, bw):
    """make_kinds.two_numbers(aw, bw, 'int8') for n pairs at once: issue_streams_fast's int8 stream (A word-column p
    walked down every micro-op, the B line held for 16), gate_mask's int8 gate, and the bus count with 16 slots."""
    n = aw.shape[0]
    a_seq = np.transpose(aw, (0, 2, 1)).reshape(n, 256)                 # for p: for i: Aword[i][p]
    b_seq = np.repeat(bw, 16, axis=1)                                   # (n, 256, 16): line p held 16 micro-ops
    gated = (a_seq[:, :, None] == 0) | ((b_seq[:, :, 0:8] == 0) & (b_seq[:, :, 8:16] == 0))
    g = gated.reshape(n, -1).mean(axis=1)
    da = a_seq ^ np.roll(a_seq, -1, axis=1)
    db = b_seq ^ np.roll(b_seq, -1, axis=1)
    bus = MK.popcount32(da).sum(axis=1) * MK.COLUMN_SLOTS["int8"] + MK.popcount32(db).reshape(n, -1).sum(axis=1)
    return g, bus


def bit_shares(stream_u8):
    """rho (set bits) and tau (bits that change between successive bytes) of one byte stream, in order."""
    s = np.ascontiguousarray(stream_u8).reshape(-1)
    pc = np.unpackbits(s).reshape(-1, 8).sum(axis=1)
    ch = np.unpackbits(s[1:] ^ s[:-1]).reshape(-1, 8).sum(axis=1)
    return {"rho": float(pc.mean() / 8.0), "tau": float(ch.mean() / 8.0), "bytes": int(s.size)}


def pct(x, q):
    return float(np.percentile(np.asarray(x, dtype=np.float64), q))


def config_stats(MM, MK, wpath, x):
    Q, B, M, name = MM.read_mlpw(wpath)
    per_layer = {l: {"g": [], "b": [], "az_w": [], "bz_w": [], "az_e": [], "bz_e": []} for l in range(5)}
    streams = {"A": [], "B": [], "input": [], "act_store": []}
    checked, equal = 0, 0
    k = 0
    for g0 in GROUPS:
        h = np.zeros((MM.NGROUP, MM.KPAD[0]), dtype=np.uint8)
        h[:, :784] = x[MM.NGROUP * g0:MM.NGROUP * (g0 + 1)]
        for l in range(5):
            nb, nt = MM.NPAD[l] // 16, MM.KPAD[l] // 64
            At = np.stack([h[:, 64 * t:64 * (t + 1)] for t in range(nt)])                    # (nt, 16, 64) uint8
            Bt = np.stack([MM.pack_b_tile(Q, l, c, t) for c in range(nb) for t in range(nt)]).view(np.uint8)
            A_pairs = np.tile(At, (nb, 1, 1))                                                  # issue order: c, then t
            aw, bw = words(A_pairs), words(Bt)
            gg, bb = two_numbers_many(MK, aw, bw)
            d = per_layer[l]
            d["g"].append(gg)
            d["b"].append(bb)
            d["az_w"].append((aw == 0).reshape(len(aw), -1).mean(axis=1))
            d["bz_w"].append((bw == 0).reshape(len(bw), -1).mean(axis=1))
            d["az_e"].append((A_pairs == 0).reshape(len(A_pairs), -1).mean(axis=1))
            d["bz_e"].append((Bt == 0).reshape(len(Bt), -1).mean(axis=1))
            streams["A"].append(A_pairs.reshape(-1))
            streams["B"].append(Bt.reshape(-1))
            if l == 0:
                streams["input"].append(At.reshape(-1))
            else:
                streams["act_store"].append(h.reshape(-1))
            for i in range(len(aw)):
                if (k + i) % CHECK_EVERY == 0:
                    raw = A_pairs[i].tobytes() + Bt[i].tobytes()
                    ref = MK.two_numbers(*MK.words_of(raw), "int8")
                    checked += 1
                    equal += int(ref[0] == float(gg[i]) and ref[1] == int(bb[i]))
            k += len(aw)
            acc = MM.matmul_exact(h, Q[l], exact_int=True)
            if l < 4:
                h = MM.requant(acc, B[l], M[l])
    ops = {l: (MM.NPAD[l] // 16) * (MM.KPAD[l] // 64) for l in range(5)}
    out = {"weights": os.path.basename(wpath), "weights_name": name, "layers": {}, "ops_per_group": ops}
    allg, allb = [], []
    for l in range(5):
        d = {kk: np.concatenate(v) for kk, v in per_layer[l].items()}
        allg.append(d["g"])
        allb.append(d["b"])
        out["layers"][str(l + 1)] = {
            "ops_per_group": ops[l], "pairs_sampled": int(d["g"].size),
            "g_mean": float(d["g"].mean()), "g_p5_p50_p95": [pct(d["g"], q) for q in (5, 50, 95)],
            "b_mean": float(d["b"].mean()), "b_p5_p50_p95": [pct(d["b"], q) for q in (5, 50, 95)],
            "a_zero_word": float(d["az_w"].mean()), "b_zero_word": float(d["bz_w"].mean()),
            "a_zero_elem": float(d["az_e"].mean()), "b_zero_elem": float(d["bz_e"].mean())}
    g_all, b_all = np.concatenate(allg), np.concatenate(allb)
    out["all_ops"] = {"pairs_sampled": int(g_all.size), "g_mean": float(g_all.mean()), "b_mean": float(b_all.mean()),
                      "g_p5_p50_p95": [pct(g_all, q) for q in (5, 50, 95)],
                      "b_p5_p50_p95": [pct(b_all, q) for q in (5, 50, 95)]}
    out["streams"] = {kk: bit_shares(np.concatenate(v)) for kk, v in streams.items()}
    wt = np.concatenate([np.stack([MM.pack_b_tile(Q, l, c, t) for c in range(MM.NPAD[l] // 16)
                                   for t in range(MM.KPAD[l] // 64)]).view(np.uint8).reshape(-1) for l in range(5)])
    out["streams"]["weights_once"] = bit_shares(wt)
    out["check_two_numbers"] = {"pairs_checked": checked, "equal": equal,
                                "what": "make_kinds.two_numbers (unchanged) on every %dth pair against this script's "
                                        "vectorised form" % CHECK_EVERY}
    return out


def kinds_stats(MK):
    rows = json.load(open(os.path.join(REPO, M10_ROWS)))
    r9 = json.load(open(os.path.join(REPO, M9_ROWS)))
    b7 = json.load(open(os.path.join(REPO, BLIND7)))
    tiles = {}
    for r in r9:
        if r["type"] == "int8" and r["card"] == "a3" and r.get("tile_path"):
            tiles.setdefault(r["kind"], set()).add((r["tile_path"], r.get("tile_sha256")))
    for meta in b7["tiles"]:
        if meta.get("anchor") or meta["type"] != "int8":
            continue
        kname = "int8.blind7:" + meta["name"].split(".", 1)[1]
        tiles.setdefault(kname, set()).add((os.path.relpath(os.path.join(REPO, os.path.dirname(BLIND7), meta["file"]), REPO),
                                            meta["sha256"]["whole"]))
    kinds = sorted(set(r["kind"] for r in rows if r["type"] == "int8" and r["card"] == "a3"))
    out = {}
    for kd in kinds:
        gs, bs, used = [], [], []
        for p, h in sorted(tiles.get(kd, ())):
            raw = open(os.path.join(REPO, p), "rb").read()
            if h and hashlib.sha256(raw).hexdigest() != h:
                sys.exit(f"refused: {p} does not hash as committed")
            g, b = MK.two_numbers(*MK.words_of(raw), "int8")
            gs.append(g)
            bs.append(b)
            used.append(p)
        if not used:
            sys.exit(f"refused: no committed tile for {kd}")
        out[kd] = {"g": float(np.mean(gs)), "b": float(np.mean(bs)), "tiles": used}
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    pin = pins()
    paths = {k: os.path.join(a.files, v) for k, v in CONFIGS.items()}
    img = os.path.join(a.data, "train-images-idx3-ubyte")
    for p in list(paths.values()) + [img]:
        if sha(p) != pin[os.path.basename(p)]:
            sys.exit(f"refused: {os.path.basename(p)} differs from its pin")
    MM = load("mnist_model", MODEL)
    MK = load("make_kinds", KINDS)
    x = MM.load_images(img)
    res = {"_what": "E202's registration, desk: operand statistics of the kernel's tile pairs and of the committed int8 "
                    "kinds (tiles_e202.py); desk check of code, no card",
           "interpreter": f"{sys.executable} {platform.python_version()}, numpy {np.__version__}",
           "groups_sampled": GROUPS, "inputs_sha256": {
               **{os.path.basename(p): sha(p) for p in list(paths.values()) + [img]},
               MODEL: sha(os.path.join(REPO, MODEL)), KINDS: sha(os.path.join(REPO, KINDS)),
               PINS: sha(os.path.join(REPO, PINS)), M10_ROWS: sha(os.path.join(REPO, M10_ROWS)),
               M9_ROWS: sha(os.path.join(REPO, M9_ROWS)), BLIND7: sha(os.path.join(REPO, BLIND7))},
           "configs": {k: config_stats(MM, MK, p, x) for k, p in paths.items()},
           "kinds_a3": kinds_stats(MK)}
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
        f.write("\n")
    for k, v in res["configs"].items():
        print(k, "g %.4f b %.1f" % (v["all_ops"]["g_mean"], v["all_ops"]["b_mean"]),
              "check %d/%d" % (v["check_two_numbers"]["equal"], v["check_two_numbers"]["pairs_checked"]),
              {s: (round(z["rho"], 4), round(z["tau"], 4)) for s, z in v["streams"].items()})
    print("kinds", len(res["kinds_a3"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
