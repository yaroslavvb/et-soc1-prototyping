#!/usr/bin/env python3
"""E156 (Q139): E139's encoded memory term on a second card with new images. The operand images, the commands, every count.

    python3 tools/claims-v3/e156/make_e156.py <out-dir> --e132-gen docs/reports/data/2026-11-02-e132-memory-split/gen
    python3 tools/claims-v3/e156/make_e156.py <out-dir> --e132-gen <...> --check     # + re-derive every count from the bytes on disk

E139's design is E132's (tools/claims-v3/e132/make_e132.py): E110's DRAM command (flw_pat, --harts 1, --stride 64, 128 KB per hart, one
64 B line fetched per load from 128 MB in all) on E99's host, every image a whole number of 64 B lines repeated through the buffer.
E156 keeps E132's family E (the encoded part) and its anchors and ties byte for byte, checked against E132's committed gen.sha256, and
leaves out family A (the address-bit rungs, which serve E132's R2 and R5, not asked here). It adds two new encoded tests, each an image
and its encoded-quiet twin built the way E132 built eh_64 / el_64 (equal ones, equal raw toggles at every width, the encoded toggles
apart), so that E139's frozen price per encoded 64-bit toggle predicts each pair's encoded residual before any pass:

  e7_64 / e2_64  NEW BYTES, E132's 64-bit layout. 64-bit blocks of 0x07 / 0x1F (0x1F has five ones and is sent inverted, 0xE0 with
                 DMI high, so the 9 encoded pins differ in 7 places at each block edge) against 64-bit blocks of 0x0F / 0x1E (four ones
                 each, never inverted: 2 encoded pins differ). Both carry 256 ones and 2 raw bits changing a byte at each block edge
                 (raw 64-bit toggles 112 a line, a raw level E132 never ran); encoded 64-bit toggles 392 against 112: +280 a line (E139's
                 pairs: +392), 32 fewer pins high in the image (E139's pairs: 32 more). Every count E139's reading uses moves by 5/7 of
                 E139's pairs, so every reading below predicts the same residual: the clean test of the price on a second card at a
                 new count, new bytes and a new raw level.
  eh_32 / el_32  E132's eh_64 / el_64 BYTES in 32-bit blocks. The same four byte values, the same ones (288), the same pins high (256 /
                 224) and the same per-edge raw (1) and encoded (8 / 1) changes as E139's E56 pair, but the block edges fall every 32
                 bits: the 64-bit pieces of a line are all alike (raw and encoded 64-bit toggles 0), the 32-bit pieces change 15 times
                 a line, and the pins change at 15 beat edges a lane. E139's term, priced per encoded 64-bit toggle, predicts NO
                 encoded residual here; a term at 32 bits, or a mispriced pin toggle, predicts about 2.1 times E56's. The width test.

Counts per 64 B line (dm_enc / make_e110.features, E132's definitions): w ones, hi pins driven high after read DBI, t_enc / t_raw pin
toggles between beats after / before inversion, rW / eW raw / encoded toggles between consecutive W-bit pieces inside a line, tx_enc the
encoded pin toggles from a line's last beat to the next line's first on a channel (dm_enc.channel_across).
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "dm"))
sys.path.insert(0, os.path.join(HERE, "..", "mf"))
sys.path.insert(0, os.path.join(HERE, "..", "e110"))
from dm_enc import POP, channel_across, lines_of, path_distance  # noqa: E402  (E99's encoder, unchanged)
from make_mf import args_for  # noqa: E402  (E75's per-level commands, unchanged)
from make_e110 import blocks, features  # noqa: E402  (E110's block builder and per-line counts, unchanged)

# E132's items E156 keeps, byte for byte and with E132's manifest entries unchanged (family E, the ties' bases, the anchors)
KEPT = ["anchor_pi", "dp_zeros", "dm_u4", "dm_l08", "dm_a44", "wl_64", "vl_64", "wl_128", "vl_128", "c3_64", "c3_128", "eh_64", "el_64"]
NEW = ["e7_64", "e2_64", "eh_32", "el_32"]
KEYS = ("w", "hi", "t_enc", "t_raw", "r32", "r64", "r128", "half", "e32", "e64", "e128", "e256")


def lane_blocks(even_x, even_y, odd_x, odd_y, w):
    """One 64 B line of w-bit blocks: blocks alternate x and y, starting with x; even bytes (lane 0) carry even_*, odd bytes (lane 1) odd_*."""
    nb = w // 8
    L = np.zeros((1, 64), dtype=np.uint8)
    for i in range(64):
        first = (i // nb) % 2 == 0
        if i % 2 == 0:
            L[0, i] = even_x if first else even_y
        else:
            L[0, i] = odd_x if first else odd_y
    return L


def new_images():
    """name -> (one line, what it is)."""
    return {
        "e7_64": (blocks(0x07, 0x1F, 64), "64-bit blocks alternate all-0x07 / all-0x1F (0x1F sent inverted, 0xE0 with DMI high)"),
        "e2_64": (blocks(0x0F, 0x1E, 64), "64-bit blocks alternate all-0x0F / all-0x1E (never inverted): e7_64's encoded-quiet twin"),
        "eh_32": (blocks(0x0F, 0x1F, 32), "32-bit blocks alternate all-0x0F / all-0x1F: eh_64's bytes at 32-bit blocks"),
        "el_32": (lane_blocks(0x0F, 0x0E, 0x1F, 0x3F, 32), "32-bit blocks alternate, lane 0 0x0F / 0x0E, lane 1 0x1F / 0x3F: el_64's bytes "
                  "at 32-bit blocks, eh_32's encoded-quiet twin"),
    }


def designed(name):
    """The designed within-line counts (KEYS order) of the four new images, derived by hand in the README's table."""
    return {
        "e7_64": (256, 224, 98, 28, 56, 112, 0, 0, 196, 392, 0, 0),
        "e2_64": (256, 256, 28, 28, 56, 112, 0, 0, 56, 112, 0, 0),
        "eh_32": (288, 256, 240, 30, 60, 0, 0, 0, 480, 0, 0, 0),
        "el_32": (288, 224, 30, 30, 60, 0, 0, 0, 60, 0, 0, 0),
    }.get(name)


def stream_k(L):
    return float(POP[L ^ np.roll(L, -1, axis=0)].sum(axis=1).mean())


def across(L):
    out = {"d1": path_distance(L, 1)[0], "d16": path_distance(L, 16)[0]}
    out["tx_enc"], out["tx_raw"] = channel_across(L)
    out["k_stream"] = stream_k(L)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--e132-gen", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "srcs"), exist_ok=True)
    e132man = {it["name"]: it for it in json.load(open(os.path.join(a.e132_gen, "manifest.json")))["items"]}
    e132sha = {}
    for line in open(os.path.join(a.e132_gen, "gen.sha256")):
        h, f = line.split()
        e132sha[f] = h
    if hashlib.sha256(open(os.path.join(a.e132_gen, "manifest.json"), "rb").read()).hexdigest() != e132sha["manifest.json"]:
        raise SystemExit("E132's manifest.json differs from its gen.sha256")

    items = []
    for nm in KEPT:
        it = dict(e132man[nm])
        if it.get("src"):
            blob = open(os.path.join(a.e132_gen, "srcs", nm + ".bin"), "rb").read()
            if hashlib.sha256(blob).hexdigest() != e132sha["srcs/%s.bin" % nm]:
                raise SystemExit("%s is not E132's bytes" % nm)
            open(os.path.join(a.out, "srcs", nm + ".bin"), "wb").write(blob)
        items.append(it)
    for nm, (L1, what) in new_images().items():
        blob = np.tile(L1, (4, 1)).tobytes()
        open(os.path.join(a.out, "srcs", nm + ".bin"), "wb").write(blob)
        L = lines_of(blob)
        c = features(L)
        items.append({"name": nm, "kind": "cmd", "tool": "main", "family": "N", "level": "dram",
                      "src": "%GEN%/srcs/" + nm + ".bin", "src_bytes": len(blob), "k": stream_k(L), "w": c["w"],
                      "elem_bits": 512, "n_elem": len(L), "unit": "DRAM, 128 MB in all", "tag": "ENERCAT {", "args": args_for("dram", nm),
                      "designed": "%s; hi %.0f, t_enc %.0f, t_raw %.0f, r32 %.0f, r64 %.0f, e32 %.0f, e64 %.0f" % (
                          what, c["hi"], c["t_enc"], c["t_raw"], c["r32"], c["r64"], c["e32"], c["e64"])})
    man = {"exp": "E156", "items": items, "e132_gen_manifest_sha256": e132sha["manifest.json"]}
    json.dump(man, open(os.path.join(a.out, "manifest.json"), "w"), indent=1)
    with open(os.path.join(a.out, "gen.sha256"), "w") as fh:
        for f in ["manifest.json"] + sorted("srcs/" + x for x in os.listdir(os.path.join(a.out, "srcs"))):
            fh.write("%s  %s\n" % (hashlib.sha256(open(os.path.join(a.out, f), "rb").read()).hexdigest(), f))
    print("%d items -> %s" % (len(items), a.out))
    if not a.check:
        return
    bad = 0
    C = {}
    for it in items:
        if not it.get("src"):
            continue
        blob = open(it["src"].replace("%GEN%", a.out), "rb").read()
        L = lines_of(blob)
        c = features(L)
        c.update(across(L))
        c["sha256"] = hashlib.sha256(blob).hexdigest()
        c["distinct_lines"] = int(len(np.unique(L, axis=0)))
        c["lines"] = int(len(L))
        C[it["name"]] = c
        ok = len(blob) == it["src_bytes"] and c["distinct_lines"] == 1 and c["d1"] == 0.0 and c["d16"] == 0.0
        if it["name"] in NEW:
            got = tuple(c[k] for k in KEYS)
            ok &= got == designed(it["name"])
        else:
            ok &= it["args"] == e132man[it["name"]]["args"]
        print("%s %-7s fam=%s w=%-3.0f hi=%-3.0f t_enc=%-3.0f t_raw=%-3.0f r32=%-3.0f r64=%-3.0f r128=%-3.0f e32=%-3.0f e64=%-3.0f "
              "e128=%-3.0f tx_enc=%.1f tx_raw=%.1f"
              % ("ok " if ok else "BAD", it["name"], it.get("family"), c["w"], c["hi"], c["t_enc"], c["t_raw"], c["r32"], c["r64"],
                 c["r128"], c["e32"], c["e64"], c["e128"], c["tx_enc"], c["tx_raw"]))
        bad += 0 if ok else 1
    # the pairs: raw counts equal at every width, the ones equal; what moves
    pairs = {"E56": ("eh_64", "el_64"), "E448": ("vl_64", "c3_64"), "E192": ("vl_128", "c3_128"),
             "E7": ("e7_64", "e2_64"), "E32": ("eh_32", "el_32")}
    dl = {}
    for pn, (x, y) in pairs.items():
        d = {k: C[x][k] - C[y][k] for k in KEYS + ("tx_enc", "tx_raw", "dmi_hi")}
        same = all(d[k] == 0 for k in ("w", "t_raw", "r32", "r64", "r128", "half", "tx_raw"))
        dl[pn] = d
        print("%s pair %-5s %s - %s: raw equal at every width and the ones equal: %s; d_hi %+.0f d_t_enc %+.0f d_e32 %+.0f d_e64 %+.0f "
              "d_e128 %+.0f d_tx_enc %+.1f" % ("ok " if same else "BAD", pn, x, y, same, d["hi"], d["t_enc"], d["e32"], d["e64"],
                                                d["e128"], d["tx_enc"]))
        bad += 0 if same else 1
    json.dump({"items": C, "pairs": dl}, open(os.path.join(a.out, "counts.json"), "w"), indent=1, sort_keys=True)
    print("check: %d bad" % bad)
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
