#!/usr/bin/env python3
"""E132 (Q136): the memory path's split. The operand images, the commands, every count.

    python3 tools/claims-v3/e132/make_e132.py <out-dir> --e110-gen docs/reports/data/2026-11-01-e110-memory-width/gen
    python3 tools/claims-v3/e132/make_e132.py <out-dir> --e110-gen <...> --check     # + re-derive every count from the bytes on disk

E110's DRAM command, unchanged (flw_pat, --harts 1, --stride 64, 128 KB per hart: one 64 B line fetched per load), on E99's host
(file: takes 256 B, lines: any whole number of 64 B lines up to 512 KB; the host repeats an image through the whole buffer, so line g
of the buffer holds image line g mod n). Seven images are E110's own bytes (E99's for three of them), copied from E110's committed gen/
and checked byte for byte against its gen.sha256; fifteen are new.

Family A, the address-bit images (each line is A = 0x0F x 64 or its complement B = 0xF0 x 64; both carry 256 ones and 256 pins
high, no byte is inverted (p = 4), and nothing toggles inside a line at any width, so only which lines differ moves):

  dm_u4     every line A (E99's bytes): no path sees a change
  ab_<b>    b = 0..7: line g is B when bit b of g is set. A path that carries every 2^n-th line (an interleave of 2^n ways) sees
            A and B half and half when n <= b, and one value when n > b; a hart reading its slice in order sees a change every
            2^b lines. So ab_<b> - ab_<b-1> changes what the 2^b-way path sees and holds every finer path's count exactly.
  ab_x70    line g is B when bit 7 XOR bit 0 of g is set: every path sees what it sees in ab_7, and a hart's own stream sees a
            change on 127 lines of 128 (ab_7: 1 of 128). ab_x70 - ab_7 is the hart stream's own price.
  ab_rnd    each line A or B by a fixed shuffle (4,096 of each, seed 13201): not periodic inside the 8,192-line image (the
            host repeats it every 512 KB); every path sees half and half, a hart's stream changes on about half its lines.

Family E, the encoded part (one line repeated, the 64- or 128-bit blocks of E110's rungs):

  wl_64 wl_128  E110's W rungs: blocks of 0x00 / 0xFF (raw toggles; the encoded data stand still but for the DMI pins)
  vl_64 vl_128  E110's V rungs: blocks of 0x0F / 0xF0 (encoded toggles = raw toggles)
  c3_64 c3_128  new: blocks of 0x07 / 0xF8. 0xF8 is sent inverted, as 0x07 with DMI high, so the encoded data stand still but for
                the DMI pins, as in W: every toggle count, raw and encoded, equals W's; only 192 more pins are driven high
  eh_64         new: 64-bit blocks of 0x0F / 0x1F. A raw toggle of one bit a byte at each edge, but 0x1F is sent inverted
                (0xE0, DMI high): 8 of the 9 encoded pins move. raw 64-bit toggles 56 a line, encoded 448: W's mirror
  el_64         new: its encoded-quiet twin. Lane 0 alternates 0x0F / 0x0E, lane 1 0x1F / 0x3F: the same ones (288), the same raw
                toggles at every width (56 at 64 bits), encoded 56, 32 fewer pins high
  dm_l08 dm_a44 E99's bytes: lanes constant 0x00 / 0xFF (W's base), beats alternating 0x0F0F / 0xF0F0 (496 pin toggles: V16)
  anchors       anchor_pi (E75's drift anchor, first and last), dp_zeros (E81's zeros command)
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
from dm_enc import ENC, POP, channel_across, lines_of, path_distance  # noqa: E402  (E99's encoder, unchanged)
from make_mf import args_for  # noqa: E402  (E75's per-level commands, unchanged)
from make_e110 import blocks, features  # noqa: E402  (E110's block builder and per-line counts, unchanged)

E110_ITEMS = ["dm_u4", "dm_l08", "dm_a44", "wl_64", "vl_64", "wl_128", "vl_128"]
A = 0x0F
B = 0xF0
WAYS = (2, 4, 8, 16, 32, 64, 128, 256, 512)
SEED = 13201


def two_value(bitfun, n_lines):
    """n_lines lines, each A (all 0x0F) or B (all 0xF0) as bitfun(g) is 0 or 1."""
    L = np.full((n_lines, 64), A, dtype=np.uint8)
    for g in range(n_lines):
        if bitfun(g):
            L[g, :] = B
    return L


def el_line():
    """el_64: 64-bit pieces alternate; lane 0 (even bytes) 0x0F / 0x0E, lane 1 (odd bytes) 0x1F / 0x3F."""
    L = np.zeros((1, 64), dtype=np.uint8)
    for i in range(64):
        even_piece = (i // 8) % 2 == 0
        if i % 2 == 0:
            L[0, i] = 0x0F if even_piece else 0x0E
        else:
            L[0, i] = 0x1F if even_piece else 0x3F
    return L


def lines_args(name):
    a = args_for("dram", name)
    i = a.index("--operands")
    a[i + 1] = "lines:%GEN%/srcs/" + name + ".bin"
    return a


def stream_k(L):
    """Bits that differ between consecutive lines of a hart's in-order stream (the image read in address order, cyclic)."""
    return float(POP[L ^ np.roll(L, -1, axis=0)].sum(axis=1).mean())


def across_line_counts(L):
    """What every path of an interleave sees: the mean bits differing between two reads of it (dm_enc.path_distance, which counts the
    same-value pairs, on purpose), for 2..512 ways, and the 1-way reading (all lines, two independent draws)."""
    out = {}
    for w in (1,) + WAYS:
        out["d%d" % w] = path_distance(L, w)[0]
    te, tr = channel_across(L)
    out["tx_enc"], out["tx_raw"] = te, tr
    out["k_stream"] = stream_k(L)
    return out


def designed(name):
    """The designed within-line counts (w, hi, t_enc, t_raw, r32, r64, r128, half, e32, e64, e128, e256) of every image."""
    if name == "dm_u4" or name.startswith("ab_"):
        return (256, 256, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    if name == "dm_l08":
        return (256, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    if name == "dm_a44":
        return (256, 256, 496, 496, 0, 0, 0, 0, 0, 0, 0, 0)
    if name == "wl_64":
        return (256, 32, 14, 112, 224, 448, 0, 0, 28, 56, 0, 0)
    if name == "c3_64":
        return (256, 224, 14, 112, 224, 448, 0, 0, 28, 56, 0, 0)
    if name == "vl_64":
        return (256, 256, 112, 112, 224, 448, 0, 0, 224, 448, 0, 0)
    if name == "wl_128":
        return (256, 32, 6, 48, 96, 192, 384, 0, 12, 24, 48, 0)
    if name == "c3_128":
        return (256, 224, 6, 48, 96, 192, 384, 0, 12, 24, 48, 0)
    if name == "vl_128":
        return (256, 256, 48, 48, 96, 192, 384, 0, 96, 192, 384, 0)
    if name == "eh_64":
        return (288, 256, 112, 14, 28, 56, 0, 0, 224, 448, 0, 0)
    if name == "el_64":
        return (288, 224, 14, 14, 28, 56, 0, 0, 28, 56, 0, 0)
    return None


def designed_across(name):
    """The designed across-line view: for ab_<b>, every path of 2^n ways with n <= b sees A/B half and half (256 bits a read), the rest
    0; ab_x70 as ab_7; ab_rnd every way about 256; one-line images 0."""
    if name.startswith("ab_") and name[3:].isdigit():
        b = int(name[3:])
        return {w: (256.0 if w <= 2 ** b else 0.0) for w in WAYS}
    if name == "ab_x70":
        return {w: (256.0 if w <= 128 else 0.0) for w in WAYS}
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--e110-gen", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "srcs"), exist_ok=True)
    e110man = {it["name"]: it for it in json.load(open(os.path.join(a.e110_gen, "manifest.json")))["items"]}
    e110sha = {}
    for line in open(os.path.join(a.e110_gen, "gen.sha256")):
        h, f = line.split()
        e110sha[f] = h

    items = [dict(e110man["anchor_pi"])]
    it = dict(e110man["dp_zeros"])
    it["designed"] = "E81's, E99's and E110's dp_zeros, unchanged"
    items.append(it)
    imgs = {}
    for nm in E110_ITEMS:
        blob = open(os.path.join(a.e110_gen, "srcs", nm + ".bin"), "rb").read()
        if hashlib.sha256(blob).hexdigest() != e110sha["srcs/%s.bin" % nm]:
            raise SystemExit("%s is not E110's bytes" % nm)
        fam = "A" if nm == "dm_u4" else "E"
        imgs[nm] = (blob, e110man[nm]["args"], fam, "E110's bytes and command, unchanged")
    for b in range(8):
        L = two_value(lambda g, b=b: (g >> b) & 1, 256)
        imgs["ab_%d" % b] = (L.tobytes(), lines_args("ab_%d" % b), "A", "line g is 0xF0 x 64 when bit %d of g is set, else 0x0F x 64" % b)
    L = two_value(lambda g: ((g >> 7) ^ g) & 1, 256)
    imgs["ab_x70"] = (L.tobytes(), lines_args("ab_x70"), "A", "line g is 0xF0 x 64 when bit 7 XOR bit 0 of g is set")
    perm = np.random.default_rng(SEED).permutation(np.r_[np.zeros(4096, int), np.ones(4096, int)])
    L = two_value(lambda g: perm[g], 8192)
    imgs["ab_rnd"] = (L.tobytes(), lines_args("ab_rnd"), "A", "each line 0x0F x 64 or 0xF0 x 64 by a fixed shuffle, 4,096 each (seed %d)" % SEED)
    for w in (64, 128):
        L = blocks(0x07, 0xF8, w)
        imgs["c3_%d" % w] = (np.tile(L, (4, 1)).tobytes(), args_for("dram", "c3_%d" % w), "E",
                             "%d-bit blocks alternate all-0x07 / all-0xF8" % w)
    L = blocks(0x0F, 0x1F, 64)
    imgs["eh_64"] = (np.tile(L, (4, 1)).tobytes(), args_for("dram", "eh_64"), "E", "64-bit blocks alternate all-0x0F / all-0x1F")
    L = el_line()
    imgs["el_64"] = (np.tile(L, (4, 1)).tobytes(), args_for("dram", "el_64"), "E",
                     "64-bit blocks alternate, lane 0 0x0F / 0x0E, lane 1 0x1F / 0x3F")

    for nm, (blob, args, fam, what) in imgs.items():
        open(os.path.join(a.out, "srcs", nm + ".bin"), "wb").write(blob)
        L = lines_of(blob)
        c = features(L)
        items.append({"name": nm, "kind": "cmd", "tool": "main", "family": fam, "level": "dram",
                      "src": "%GEN%/srcs/" + nm + ".bin", "src_bytes": len(blob), "k": stream_k(L), "w": c["w"],
                      "elem_bits": 512, "n_elem": len(L), "unit": "DRAM, 128 MB in all", "tag": "ENERCAT {", "args": args,
                      "designed": "%s; hi %.0f, t_enc %.0f, t_raw %.0f, r64 %.0f, half %.0f, e64 %.0f" % (
                          what, c["hi"], c["t_enc"], c["t_raw"], c["r64"], c["half"], c["e64"])})
    man = {"exp": "E132", "items": items, "e110_gen_manifest_sha256": hashlib.sha256(
        open(os.path.join(a.e110_gen, "manifest.json"), "rb").read()).hexdigest()}
    json.dump(man, open(os.path.join(a.out, "manifest.json"), "w"), indent=1)
    with open(os.path.join(a.out, "gen.sha256"), "w") as fh:
        for f in ["manifest.json"] + sorted("srcs/" + x for x in os.listdir(os.path.join(a.out, "srcs"))):
            fh.write("%s  %s\n" % (hashlib.sha256(open(os.path.join(a.out, f), "rb").read()).hexdigest(), f))
    print("%d items -> %s" % (len(items), a.out))
    if not a.check:
        return
    bad = 0
    C = {}
    keys = ("w", "hi", "t_enc", "t_raw", "r32", "r64", "r128", "half", "e32", "e64", "e128", "e256")
    for it in items:
        if not it.get("src"):
            continue
        blob = open(it["src"].replace("%GEN%", a.out), "rb").read()
        L = lines_of(blob)
        c = features(L)
        c.update(across_line_counts(L))
        c["sha256"] = hashlib.sha256(blob).hexdigest()
        c["distinct_lines"] = int(len(np.unique(L, axis=0)))
        c["lines"] = int(len(L))
        C[it["name"]] = c
        ok = len(blob) == it["src_bytes"]
        want = designed(it["name"])
        got = tuple(c[k] for k in keys)
        ok &= want is not None and got == want
        da = designed_across(it["name"])
        if da is not None:
            for w, v in da.items():
                ok &= abs(c["d%d" % w] - v) < 1e-9
        elif it["name"] == "ab_rnd":
            ok &= all(240.0 < c["d%d" % w] < 270.0 for w in WAYS if w <= 128) and c["distinct_lines"] == 2
        else:
            ok &= c["distinct_lines"] == 1 and all(c["d%d" % w] == 0.0 for w in WAYS)
        print("%s %-7s fam=%s lines=%-5d w=%-3.0f hi=%-3.0f t_enc=%-3.0f t_raw=%-3.0f r64=%-3.0f r128=%-3.0f e64=%-3.0f e128=%-3.0f | k=%-5.1f "
              "d1=%-5.1f %s tx=%.1f"
              % ("ok " if ok else "BAD", it["name"], it["family"], len(L), c["w"], c["hi"], c["t_enc"], c["t_raw"], c["r64"], c["r128"],
                 c["e64"], c["e128"], c["k_stream"], c["d1"], " ".join("d%d=%.0f" % (w, c["d%d" % w]) for w in WAYS), c["tx_enc"]))
        bad += 0 if ok else 1
    for nm in E110_ITEMS:
        it = next(x for x in items if x["name"] == nm)
        same = it["args"] == e110man[nm]["args"]
        print("%s %s: command identical to E110's" % ("ok " if same else "BAD", nm))
        bad += 0 if same else 1
    # the stream and the across-line views the design relies on
    for nm, kw in (("ab_7", 4.0), ("ab_x70", 508.0), ("ab_0", 512.0), ("ab_4", 32.0)):
        ok = abs(C[nm]["k_stream"] - kw) < 1e-9
        print("%s %s: a hart's stream changes %.1f bits a line (designed %.1f)" % ("ok " if ok else "BAD", nm, C[nm]["k_stream"], kw))
        bad += 0 if ok else 1
    json.dump(C, open(os.path.join(a.out, "counts.json"), "w"), indent=1, sort_keys=True)
    print("check: %d bad" % bad)
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
