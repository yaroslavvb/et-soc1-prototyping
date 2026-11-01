#!/usr/bin/env python3
"""E110 (Q133): the memory path's width ladder. The operand images, the commands, every count.

    python3 tools/claims-v3/e110/make_e110.py <out-dir> --e99-gen docs/reports/data/2026-11-01-e99-dram-mechanism/gen
    python3 tools/claims-v3/e110/make_e110.py <out-dir> --e99-gen <...> --check     # + re-derive every count from the bytes on disk

E99's DRAM command, unchanged (flw_pat, --harts 1, --stride 64, 128 KB per hart: one 64 B line fetched per load), and E75's L2 command
(8 KB per hart) for the on-chip arm. Nine images are E99's own bytes, copied from its committed gen/ and checked byte for byte
against its gen.sha256; ten are new. Every line of a family carries the same ones and the same pins driven high after read DBI, so
inside a family only where a line's bits change moves:

  family  item            what moves (per 64 B line; E99's read-DBI encoder, tools/claims-v3/dm/dm_enc.py)
  W       dm_l08          baseline: byte lanes constant, 0x00 and 0xFF; no toggle between 16-bit or wider pieces (E99's bytes)
  (raw)   dm_a08          16-bit beats alternate 0x0000/0xFFFF (E99's bytes)
          wl_32 64 128    32-, 64-, 128-bit blocks alternate all-0x00 / all-0xFF
          wl_256          the 32 B halves: 0x00 then 0xFF
          dp_c1           the 32 B halves: 0xFF then 0x00 (E81's and E99's bytes: E99's `half` image)
          Every W line: 256 ones, 32 pins high. After inversion every data pin is low, so only the DMI pins move: the raw bits toggle
          and the encoded data stand still except one DMI bit per byte at each block edge.
  V       dm_u4           baseline: every byte 0x0F (E99's bytes); no toggle anywhere
  (raw =  dm_a44          16-bit beats alternate 0x0F0F/0xF0F0 (E99's bytes)
  enc.)   vl_32 64 128    32-, 64-, 128-bit blocks alternate all-0x0F / all-0xF0
          vl_256          the 32 B halves: 0x0F then 0xF0
          Every V line: 256 ones, 256 pins high, no byte inverted (p = 4), so the encoded data toggle exactly as the raw data do.
  T       dm_u1, dm_u8    every byte 0x01, 0xFF at DRAM: 64 and 512 ones, 64 pins high each (E99's bytes; E99's tie18)
          l2_u1, l2_u8    the same bytes at E75's L2 level (8 KB per hart, 256 KB per shire): no DRAM, no pins
          l2_zeros        E75's L2 zeros command
  P       dm_L2, dm_L8192   the two ends of E99's period ladder (its `D`), E99's bytes, unchanged
  anchors anchor_pi (E75's drift anchor), dp_zeros, dp_bern (E81's commands)

For a rung of width w, a W-bit piece with W <= w toggles at each of the line's 512/w - 1 block edges (all W bits), and a W-bit piece
with W > w never toggles (every such piece holds the same blocks in the same order). So a path of width W sees toggles only on rungs
w >= W, and the first rung that costs is the narrowest path that pays. The file: operand takes exactly 256 B (four lines), so a one-line
image is repeated four times, as E99 did; dm_L8192 goes through E99's lines: operand.
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
from dm_enc import ENC, POP, counts, lines_of  # noqa: E402  (E99's encoder, unchanged)
from make_mf import args_for  # noqa: E402  (E75's per-level commands, unchanged)

E99_ITEMS = ["dp_c1", "dm_l08", "dm_a08", "dm_u4", "dm_a44", "dm_u1", "dm_u8", "dm_L2", "dm_L8192"]
WIDTHS = (16, 32, 64, 128, 256)
FAMILY = {"dp_c1": "W", "dm_l08": "W", "dm_a08": "W", "dm_u4": "V", "dm_a44": "V", "dm_u1": "T", "dm_u8": "T"}


def blocks(x, y, w):
    """One 64 B line: blocks of w bits alternate x-bytes and y-bytes, starting with x."""
    nb = w // 8
    L = np.zeros((1, 64), dtype=np.uint8)
    for i in range(64):
        L[0, i] = x if (i // nb) % 2 == 0 else y
    return L


def features(L):
    """Per-line counts. dm_enc.counts (w, hi, t_enc, t_raw, k, half, k_chan, k_shire, ...), plus the raw (rW) and encoded (eW) toggles
    between consecutive W-bit pieces inside a line, W = 32, 64, 128, 256, in the bytes' own order: E99's post-hoc definitions
    (tools/claims-v3/dm/posthoc_fit.py `features`), written out here so the registration does not depend on a post-hoc file. eW counts the
    pins of the 9-pin encoded byte (8 DQ + DMI) that differ; e256 is the encoded `half`."""
    f = counts(L)
    out = {k: f[k] for k in ("w", "hi", "dmi_hi", "t_enc", "t_raw", "half", "k", "k_chan", "k_shire", "k_bank", "period_lines")}
    e9 = ((ENC[L][..., None] >> np.arange(9)) & 1).astype(np.uint8)
    for W in (32, 64, 128, 256):
        nb = W // 8
        P = L.reshape(L.shape[0], 64 // nb, nb)
        out["r%d" % W] = float(POP[P[:, 1:] ^ P[:, :-1]].sum(axis=(1, 2)).mean())
        Q = e9.reshape(L.shape[0], 64 // nb, nb, 9)
        out["e%d" % W] = float((Q[:, 1:] != Q[:, :-1]).sum(axis=(1, 2, 3)).mean())
    out["r16"] = out["t_raw"]
    out["e16"] = out["t_enc"]
    return out


def expected(name):
    """The designed counts of every new image and of E99's reused ones: (w, hi, t_enc, t_raw, r32, r64, r128, half, e32, e64, e128, e256)."""
    n = {16: 31, 32: 15, 64: 7, 128: 3, 256: 1}
    def ladder(w, enc_full):
        r = {W: (n[w] * W if W <= w else 0) for W in WIDTHS}
        if enc_full:      # V: raw = encoded, DMI never moves
            e = dict(r)
        else:             # W: only the DMI bit of each byte moves, one per byte at each edge
            e = {W: (n[w] * W // 8 if W <= w else 0) for W in WIDTHS}
        return r, e
    if name in ("dm_l08",):
        return (256, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    if name == "dm_u4":
        return (256, 256, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    fam = None
    if name in ("dm_a08",) or name.startswith("wl_") or name == "dp_c1":
        fam = "W"
    if name in ("dm_a44",) or name.startswith("vl_"):
        fam = "V"
    if fam:
        w = 16 if name in ("dm_a08", "dm_a44") else 256 if name == "dp_c1" else int(name[3:])
        r, e = ladder(w, fam == "V")
        hi = 32 if fam == "W" else 256
        return (256, hi, e[16], r[16], r[32], r[64], r[128], r[256], e[32], e[64], e[128], e[256])
    if name in ("dm_u1", "l2_u1"):
        return (64, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    if name in ("dm_u8", "l2_u8"):
        return (512, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--e99-gen", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "srcs"), exist_ok=True)
    e99man = {it["name"]: it for it in json.load(open(os.path.join(a.e99_gen, "manifest.json")))["items"]}
    e99sha = {}
    for line in open(os.path.join(a.e99_gen, "gen.sha256")):
        h, f = line.split()
        e99sha[f] = h

    items = [dict(e99man["anchor_pi"])]
    for nm in ("dp_zeros", "dp_bern"):
        it = dict(e99man[nm])
        it["designed"] = "E81's and E99's " + nm + ", unchanged"
        items.append(it)
    imgs = {}
    for nm in E99_ITEMS:
        blob = open(os.path.join(a.e99_gen, "srcs", nm + ".bin"), "rb").read()
        if hashlib.sha256(blob).hexdigest() != e99sha["srcs/%s.bin" % nm]:
            raise SystemExit("%s is not E99's bytes" % nm)
        imgs[nm] = (blob, e99man[nm]["args"], FAMILY.get(nm, "P" if nm.startswith("dm_L") else "?"), "E99's bytes, unchanged")
    for w in (32, 64, 128, 256):
        L = blocks(0x00, 0xFF, w)
        imgs["wl_%d" % w] = (np.tile(L, (4, 1)).tobytes(), args_for("dram", "wl_%d" % w), "W",
                             "%d-bit blocks alternate all-0x00 / all-0xFF" % w)
        L = blocks(0x0F, 0xF0, w)
        imgs["vl_%d" % w] = (np.tile(L, (4, 1)).tobytes(), args_for("dram", "vl_%d" % w), "V",
                             "%d-bit blocks alternate all-0x0F / all-0xF0" % w)
    for nm, v in (("l2_u1", 0x01), ("l2_u8", 0xFF)):
        L = np.full((4, 64), v, dtype=np.uint8)
        imgs[nm] = (L.tobytes(), args_for("l2", nm), "T", "every byte 0x%02X at E75's L2 level" % v)

    for nm, (blob, args, fam, what) in imgs.items():
        open(os.path.join(a.out, "srcs", nm + ".bin"), "wb").write(blob)
        L = lines_of(blob)
        c = features(L)
        level = "l2" if nm.startswith("l2_") else "dram"
        items.append({"name": nm, "kind": "cmd", "tool": "main", "family": fam, "level": level,
                      "src": "%GEN%/srcs/" + nm + ".bin", "src_bytes": len(blob), "k": c["k"], "w": c["w"],
                      "elem_bits": 512, "n_elem": len(L), "unit": "L2, 256 KB per shire" if level == "l2" else "DRAM, 128 MB in all",
                      "tag": "ENERCAT {", "args": args,
                      "designed": "%s; hi %.0f, t_enc %.0f, t_raw %.0f, r64 %.0f, half %.0f, e64 %.0f" % (
                          what, c["hi"], c["t_enc"], c["t_raw"], c["r64"], c["half"], c["e64"])})
    l2z = {"name": "l2_zeros", "kind": "cmd", "tool": "main", "family": "T", "level": "l2", "k": 0, "w": 0, "elem_bits": 512,
           "n_elem": 4, "unit": "L2, 256 KB per shire", "tag": "ENERCAT {", "args": args_for("l2", None),
           "designed": "E75's L2 zeros command, unchanged"}
    items.append(l2z)
    man = {"exp": "E110", "items": items, "e99_gen_manifest_sha256": hashlib.sha256(
        open(os.path.join(a.e99_gen, "manifest.json"), "rb").read()).hexdigest()}
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
        c["sha256"] = hashlib.sha256(blob).hexdigest()
        c["distinct_lines"] = int(len(np.unique(L, axis=0)))
        C[it["name"]] = c
        want = expected(it["name"])
        ok = len(blob) == it["src_bytes"]
        if want is not None:
            got = tuple(c[k] for k in keys)
            ok &= got == want
            ok &= c["distinct_lines"] == 1 and c["k"] == 0 and c["k_chan"] == 0 and c["k_shire"] == 0
        elif it["name"].startswith("dm_L"):
            p = int(it["name"][4:])
            ok &= c["distinct_lines"] == p and c["w"] == 256 and c["hi"] == 211
        else:
            ok = False
        print("%s %-9s fam=%s lines=%-5d w=%-5.0f hi=%-5.1f t_enc=%-5.1f t_raw=%-5.1f r32=%-5.1f r64=%-5.1f r128=%-5.1f half=%-5.1f"
              " e32=%-5.1f e64=%-5.1f e128=%-5.1f e256=%-5.1f k_chan=%-5.1f k_shire=%-5.1f"
              % ("ok " if ok else "BAD", it["name"], it["family"], len(L), c["w"], c["hi"], c["t_enc"], c["t_raw"], c["r32"], c["r64"],
                 c["r128"], c["half"], c["e32"], c["e64"], c["e128"], c["e256"], c["k_chan"], c["k_shire"]))
        bad += 0 if ok else 1
    # the reused images are E99's bytes and E99's commands, byte for byte
    for nm in E99_ITEMS:
        it = next(x for x in items if x["name"] == nm)
        same = it["args"] == e99man[nm]["args"]
        print("%s %s: command identical to E99's" % ("ok " if same else "BAD", nm))
        bad += 0 if same else 1
    json.dump(C, open(os.path.join(a.out, "counts.json"), "w"), indent=1, sort_keys=True)
    print("check: %d bad" % bad)
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
