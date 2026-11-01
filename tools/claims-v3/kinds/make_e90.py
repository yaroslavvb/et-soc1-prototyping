#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E90 (Q130): the tiles of E90 - sign patterns in fp32, fp16 and int8, and three fresh draws of the three random-rule
kinds the Q130 critic names (items 6 and 13). Written with make_kinds.py's own machinery (draw_elements, encode,
words_of, issue_streams, tile_stats; imported, not copied), so every tile is in the host's `file:` layout and its
stats are counted exactly as kinds.json counts E78's.

    python3 tools/claims-v3/kinds/make_e90.py            # writes e90/tiles/<type>/<name>.bin and e90/e90.json
    python3 tools/claims-v3/kinds/make_e90.py --check    # rebuild in memory and compare with what is on disk

The sign group (critic item 6; Horace hub "sign patterns"):
  <t>.signs          every element +1 or -1 with equal probability, both sides (E64's fp32 `signs`), fp32 fp16 int8
  <t>.abs_randn      E78's committed <t>.randn tile with every element's sign bit CLEARED: the same magnitudes as
                     E78's anchor, all positive (fp32, fp16)
  <t>.negabs_randn   the same tile with every sign bit SET: all negative (fp32, fp16)
  fp32.pm_pi         every element +pi or -pi (0x40490FDB / 0xC0490FDB), both sides: a sign-only flip at a fixed
                     magnitude whose mantissa is full, beside the tie anchor_pi (every element +pi)
  So <t>.randn (E78's anchor, random signs), <t>.abs_randn and <t>.negabs_randn carry IDENTICAL magnitude bits;
  they differ only in their sign bits. int8 has no sign-magnitude form (two's complement), so int8 gets `signs`
  only: +1 is 0x01 and -1 is 0xFF, so one sign change flips seven bits.
The redraw group (critic item 13; E78 C5): <kind>_d1, _d2, _d3 for fp32.sparse50, fp16.nn_like, fp16.uniform01,
  each drawn by make_kinds.draw_elements with a NEW seed, recorded in e90.json (seed = the first 8 bytes,
  little-endian, of sha256("E90/<type>/<kind>/draw<r>")); E78's committed tile of each kind runs beside them.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_kinds as mk  # noqa: E402

OUT = os.path.join(HERE, "e90")
KINDS_JSON = os.path.join(HERE, "kinds.json")
REDRAW = (("fp32", "sparse50"), ("fp16", "nn_like"), ("fp16", "uniform01"))
DRAWS = (1, 2, 3)
SIGN_MASK = {"fp32": 0x80000000, "fp16": 0x80008000, "int8": 0x80808080}


def seed_of(tag):
    return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8], "little")


def e78_tile(type_name, kind):
    """E78's committed tile bytes, checked against kinds.json's sha256."""
    k = json.load(open(KINDS_JSON))
    v = k["kinds"][type_name][kind]
    raw = open(os.path.join(HERE, v["file"]), "rb").read()
    if hashlib.sha256(raw).hexdigest() != v["sha256"]:
        raise SystemExit(f"{type_name}/{kind}: committed tile differs from kinds.json")
    return raw, v


def sign_flips_per_op(raw, type_name):
    """Designed sign-bit flips per op, E65/E67/E79's rule: an element read whose sign bit differs from the previous
    read in the same lane's stream, summed over the lanes (the broadcast A word counted once per column slot) and
    wrapped op to op. Returns (A, B)."""
    aw, bw = mk.words_of(raw)
    a_seq, b_seq = mk.issue_streams(aw, bw, type_name)
    m = np.uint64(SIGN_MASK[type_name])
    da = (a_seq ^ np.roll(a_seq, -1)) & m
    db = (b_seq ^ np.roll(b_seq, -1, axis=0)) & m
    return (int(mk.popcount32(da.astype(np.uint32)).sum() * mk.COLUMN_SLOTS[type_name]),
            int(mk.popcount32(db.astype(np.uint32)).sum()))


def entries():
    """name -> (type, kind, group, rule, raw bytes, extra fields)."""
    out = {}
    E = {t: mk.TYPES[t] for t in mk.TYPES}
    # --- the sign group
    for t in ("fp32", "fp16", "int8"):
        tag = f"E90/{t}/signs"
        rng = np.random.default_rng(seed_of(tag))
        _, _, _, K = E[t]
        sa = np.where(rng.integers(0, 2, (mk.N, K)) == 1, 1.0, -1.0)
        sb = np.where(rng.integers(0, 2, (K, mk.N)) == 1, 1.0, -1.0)
        out[f"{t}.signs"] = (t, "signs", "signs",
                             "every element +1 or -1 with equal probability, both sides (E64's fp32 `signs`)"
                             + ("; int8: 0x01 / 0xFF, so a sign change flips seven bits" if t == "int8" else ""),
                             mk.encode(sa, sb, t), {"seed_tag": tag, "seed": seed_of(tag)})
    for t in ("fp32", "fp16"):
        raw0, v0 = e78_tile(t, "randn")
        aw, bw = mk.words_of(raw0)
        m = np.uint64(SIGN_MASK[t])
        if t == "fp32":
            assert np.all((aw & np.uint64(0x7FFFFFFF)) != 0) and np.all((bw & np.uint64(0x7FFFFFFF)) != 0)
        else:
            for w in (aw, bw):
                assert np.all((w & np.uint64(0x7FFF)) != 0) and np.all((w & np.uint64(0x7FFF0000)) != 0)
        out[f"{t}.abs_randn"] = (t, "abs_randn", "signs",
                                 f"E78's committed {t}.randn tile (sha256 {v0['sha256'][:12]}...) with every "
                                 "element's sign bit cleared: the anchor's magnitudes, all positive",
                                 mk.from_words(aw & ~m & np.uint64(0xFFFFFFFF), bw & ~m & np.uint64(0xFFFFFFFF)),
                                 {"from": f"tools/claims-v3/kinds/{v0['file']}", "from_sha256": v0["sha256"]})
        out[f"{t}.negabs_randn"] = (t, "negabs_randn", "signs",
                                    f"E78's committed {t}.randn tile with every element's sign bit set: the "
                                    "anchor's magnitudes, all negative",
                                    mk.from_words(aw | m, bw | m),
                                    {"from": f"tools/claims-v3/kinds/{v0['file']}", "from_sha256": v0["sha256"]})
    tag = "E90/fp32/pm_pi"
    rng = np.random.default_rng(seed_of(tag))
    sa = np.where(rng.integers(0, 2, (mk.N, 16)) == 1, mk.PI_F32, -mk.PI_F32)
    sb = np.where(rng.integers(0, 2, (16, mk.N)) == 1, mk.PI_F32, -mk.PI_F32)
    out["fp32.pm_pi"] = ("fp32", "pm_pi", "signs",
                         "every element +pi or -pi (0x40490FDB / 0xC0490FDB) with equal probability, both sides: "
                         "a sign-only flip at a fixed magnitude with a full mantissa",
                         mk.encode(sa, sb, "fp32"), {"seed_tag": tag, "seed": seed_of(tag)})
    # --- the redraw group
    for t, kind in REDRAW:
        for r in DRAWS:
            tag = f"E90/{t}/{kind}/draw{r}"
            rng = np.random.default_rng(seed_of(tag))
            a_el, b_el = mk.draw_elements(t, kind, rng)
            out[f"{t}.{kind}_d{r}"] = (t, f"{kind}_d{r}", "redraw",
                                       f"a fresh draw of E78's rule `{kind}` ({t}) with a new seed",
                                       mk.encode(a_el, b_el, t),
                                       {"seed_tag": tag, "seed": seed_of(tag), "rule_of": f"{t}.{kind}"})
    return out


def build(check=False):
    k = json.load(open(KINDS_JSON))
    spec = {"experiment": "E90", "date": "2026-10-31",
            "generator": "tools/claims-v3/kinds/make_e90.py (make_kinds.py's draw_elements, encode, issue_streams "
                         "and tile_stats, imported)",
            "kinds_json_sha256": hashlib.sha256(open(KINDS_JSON, "rb").read()).hexdigest(),
            "make_kinds_sha256": hashlib.sha256(open(os.path.join(HERE, "make_kinds.py"), "rb").read()).hexdigest(),
            "seed_rule": "seed = int.from_bytes(sha256(seed_tag)[:8], 'little'); rng = numpy default_rng(seed)",
            "tiles": {}}
    problems = []
    for name, (t, kind, group, rule, raw, extra) in entries().items():
        assert len(raw) == 2048, name
        rel = f"tiles/{t}/{kind}.bin"
        p = os.path.join(OUT, rel)
        if check:
            have = open(p, "rb").read() if os.path.exists(p) else b""
            if have != raw:
                problems.append(f"{name}: on-disk tile differs from the rebuild")
        else:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "wb").write(raw)
        st = mk.tile_stats(raw, t)
        fa, fb = sign_flips_per_op(raw, t)
        ent = {"type": t, "kind": kind, "group": group, "rule": rule, "file": rel, "bytes": 2048,
               "sha256": hashlib.sha256(raw).hexdigest(), "sha256_a": hashlib.sha256(raw[:1024]).hexdigest(),
               "sha256_b": hashlib.sha256(raw[1024:]).hexdigest(),
               "stats": {"gated_lane_frac": st["gated_lane_frac"], "bus_bits_per_op": st["bus_bits_per_op"],
                         "sign_flips_per_op_a": fa, "sign_flips_per_op_b": fb,
                         "hamming_a": st["a"]["hamming"], "hamming_b": st["b"]["hamming"]},
               "provisional": t == "int8"}
        ent.update(extra)
        if group == "redraw":
            base = k["kinds"][t][extra["rule_of"].split(".", 1)[1]]
            rep = base.get("replicates", {})
            ent["committed_tile"] = {"name": extra["rule_of"], "sha256": base["sha256"],
                                     "gated_lane_frac": base["stats"]["gated_lane_frac"],
                                     "bus_bits_per_op": base["stats"]["bus_bits_per_op"]}
            ent["rule_band"] = {q: {kk: rep[q][kk] for kk in ("mean", "p2.5", "p97.5")} for q in rep
                                if isinstance(rep.get(q), dict)}
        spec["tiles"][name] = ent
    # the E78 references' sign flips, for the predictions (counted the same way from the committed tiles)
    refs = {}
    for t, kind in (("fp32", "randn"), ("fp16", "randn"), ("fp32", "ones"), ("fp16", "ones"), ("int8", "ones"),
                    ("int8", "neg_ones"), ("fp32", "pi"), ("int8", "highbit")):
        raw0, v0 = e78_tile(t, kind)
        fa, fb = sign_flips_per_op(raw0, t)
        refs[f"{t}.{kind}"] = {"sha256": v0["sha256"], "sign_flips_per_op_a": fa, "sign_flips_per_op_b": fb,
                               "bus_bits_per_op": v0["stats"]["bus_bits_per_op"]}
    spec["e78_references"] = refs
    return spec, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    spec, problems = build(check=a.check)
    if a.check:
        old = json.load(open(os.path.join(OUT, "e90.json")))
        if old.get("tiles") != json.loads(json.dumps(spec["tiles"])):
            problems.append("e90.json tiles differ from the rebuild")
        print(json.dumps({"tiles": len(spec["tiles"]), "problems": problems}))
        sys.exit(1 if problems else 0)
    json.dump(spec, open(os.path.join(OUT, "e90.json"), "w"), indent=1)
    for n, e in spec["tiles"].items():
        s = e["stats"]
        print(f"{n:24s} gated {s['gated_lane_frac']:.4f} bus {s['bus_bits_per_op']:6d} "
              f"signflips A {s['sign_flips_per_op_a']:5d} B {s['sign_flips_per_op_b']:5d}")
    for n, e in spec["e78_references"].items():
        print(f"ref {n:20s} bus {e['bus_bits_per_op']:6d} signflips A {e['sign_flips_per_op_a']:5d} "
              f"B {e['sign_flips_per_op_b']:5d}")


if __name__ == "__main__":
    main()
