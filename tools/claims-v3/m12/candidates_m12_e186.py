#!/usr/bin/env python3
"""M12 for E186 (Q158): the merged candidate list for a tensor round 3, and the forecasts frozen for it before E186's registration.

The list merges M12's 20 candidate kinds and 14 trains (candidates-m12.json, frozen Sun 8 Nov 2026 05:07:07 PST, unchanged) with a second
candidate list of 23 kinds and 9 trains (E186-CANDIDATES: kind and train ids, formats and operand words only). Duplicates are merged by their
words; each kind gets one E186 id (K01-K39). For every kind and train candidates-m12.json does not cover, M12's forecast is computed here with
M12 exactly as committed (m12.json, no refit; m12_common and candidates_m12 imported unchanged; E178's flip model compiled unchanged; M10's
chain and predictor unchanged), and M10's frozen forecast is computed for every item. M12's 20 kinds and 14 trains are recomputed by the same
code and must equal candidates-m12.json's values exactly; their frozen values are carried as written.

    /usr/bin/python3 -B tools/claims-v3/m12/candidates_m12_e186.py --root . stage      # kinds-m12-e186.json and tiles-e186/ (new tiles)
    (bench/bench_m12_e186.sh runs the toggle bench on the mini -> bench/counts-m12-e186.json)
    /usr/bin/python3 -B tools/claims-v3/m12/candidates_m12_e186.py --root . forecast   # candidates-m12-e186.json and .md
    /usr/bin/python3 -B tools/claims-v3/m12/candidates_m12_e186.py --root . check      # recomputes both stages in memory, compares bytes

A forecast for a registration to take, not a registration; M12 stays post hoc (fitted on E182). Needs a C compiler and numpy (M10's chain).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import statistics
import struct
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m12_common as C  # noqa: E402
import candidates_m12 as CM  # noqa: E402

F1 = 0x3F800000
TILES_NEW = "tools/claims-v3/m12/tiles-e186"
COMMITTED_TILE_DIRS = ["tools/claims-v3/kinds/tiles", "tools/claims-v3/e178/tiles", "tools/claims-v3/e182/tiles", "tools/claims-v3/m12/tiles"]

# E186-CANDIDATES: kind ids, formats and operand words only (A word, B word), in that list's order
CAND_KINDS = [
    ("e186.fp32.one_w", "fp32", 0x3F800000, 0x3FFFFFFF), ("e186.fp32.w_one", "fp32", 0x3FFFFFFF, 0x3F800000),
    ("e186.fp32.one_one", "fp32", 0x3F800000, 0x3F800000), ("e186.fp32.a13_w", "fp32", 0x3FD55555, 0x3FFFFFFF),
    ("e186.fp32.a2_w", "fp32", 0x3FFFF800, 0x3FFFFFFF), ("e186.fp32.a13_one", "fp32", 0x3FD55555, 0x3F800000),
    ("e186.fp32.a2_one", "fp32", 0x3FFFF800, 0x3F800000), ("e186.fp32.ab0_w", "fp32", 0x3F800001, 0x3FFFFFFF),
    ("e186.fp32.ab22_w", "fp32", 0x3FC00000, 0x3FFFFFFF), ("e186.fp32.ab2_w", "fp32", 0x3F800004, 0x3FFFFFFF),
    ("e186.fp32.one_bb0", "fp32", 0x3F800000, 0x3F800001), ("e186.fp32.one_bb22", "fp32", 0x3F800000, 0x3FC00000),
    ("e186.fp16.one_w", "fp16", 0x3C003C00, 0x3FFF3FFF), ("e186.fp16.w_one", "fp16", 0x3FFF3FFF, 0x3C003C00),
    ("e186.int8.01_40", "int8", 0x01010101, 0x40404040), ("e186.int8.40_01", "int8", 0x40404040, 0x01010101),
    ("e186.int8.02_20", "int8", 0x02020202, 0x20202020), ("e186.int8.20_02", "int8", 0x20202020, 0x02020202),
    ("e186.int8.04_10", "int8", 0x04040404, 0x10101010), ("e186.int8.10_04", "int8", 0x10101010, 0x04040404),
    ("e186.int8.08_08", "int8", 0x08080808, 0x08080808), ("e186.int8.ff_c0", "int8", 0xFFFFFFFF, 0xC0C0C0C0),
    ("e186.int8.c0_ff", "int8", 0xC0C0C0C0, 0xFFFFFFFF)]
# its trains: id, first kind id, second kind id (a train reads D(first) - D(second)); ordered by id
CAND_TRAINS = [("R1", "e186.fp32.a13_w", "e186.fp32.a2_w"), ("R2", "e186.fp32.a13_one", "e186.fp32.a2_one"),
               ("R3", "e186.fp32.one_w", "e186.fp32.one_one"), ("R4", "e186.fp32.w_one", "e186.fp32.one_one"),
               ("R5", "e186.fp16.one_w", "e186.fp16.w_one"), ("R6", "e186.int8.01_40", "e186.int8.02_20"),
               ("R7", "e186.int8.04_10", "e186.int8.02_20"), ("R8", "e186.fp32.ab0_w", "e186.fp32.ab22_w"),
               ("R9", "e186.fp32.ab0_w", "e186.fp32.ab2_w")]
# each candidate train in this lane's own words: operand properties only
CAND_TRAIN_WHAT = {
    "R1": "fp32, B 0x3fffffff in both: A's mantissa popcount 12 in both, with 13 against 2 nonzero radix-4 digits in A's significand",
    "R2": "the same two A words as R1, B 1.0 in both",
    "R3": "fp32, A 1.0 in both: B 0x3fffffff against 1.0 (B gains its 23 mantissa bits)",
    "R4": "fp32, B 1.0 in both: A 0x3fffffff against 1.0 (A gains its 23 mantissa bits)",
    "R5": "the fp16 swap: (1.0, 0x3fff) against (0x3fff, 1.0) in both halves (20 held bits a 32-bit word moved from A to B)",
    "R6": "int8, product +64 in both, one 1-bit a byte on each side in both: (A +1, B +64) against (A +2, B +32), bits 0 and 6 against 1 and 5",
    "R7": "int8, product +64 in both, one 1-bit a byte on each side in both: (A +4, B +16) against (A +2, B +32), bits 2 and 4 against 1 and 5",
    "R8": "fp32, B 0x3fffffff in both: A one mantissa bit at bit 0 (3 nonzero radix-4 digits) against at bit 22 (2 digits)",
    "R9": "fp32, B 0x3fffffff in both: A one mantissa bit at bit 0 against at bit 2 (3 nonzero radix-4 digits each)"}


# ------------------------------------------------------------------ operand properties (for the descriptions only)
def signif(t, w):
    """the significand of each half (fp16) or of the word (fp32), hidden bit included; None for int8"""
    if t == "fp32":
        e, m = (w >> 23) & 0xFF, w & 0x7FFFFF
        return [(m | (1 << 23)) if e else m], 24
    if t == "fp16":
        out = []
        for h in ((w >> 16) & 0xFFFF, w & 0xFFFF):
            e, m = (h >> 10) & 0x1F, h & 0x3FF
            out.append((m | (1 << 10)) if e else m)
        return out, 11
    return None, None


def radix4_nonzero(x, nbits):
    """nonzero digits of x's radix-4 signed-digit form, digit i = -2 b(2i+1) + b(2i) + b(2i-1), b(-1) = 0, x read as unsigned"""
    n = 0
    for i in range((nbits + 2) // 2):
        b1 = (x >> (2 * i + 1)) & 1
        b0 = (x >> (2 * i)) & 1
        bm = (x >> (2 * i - 1)) & 1 if i > 0 else 0
        if -2 * b1 + b0 + bm != 0:
            n += 1
    return n


def props(t, aw, bw):
    p = {"popcount_a_word": C.popcount(aw), "popcount_b_word": C.popcount(bw), "hamming_a_b_word": C.popcount(aw ^ bw)}
    if t == "int8":
        sa, sb = aw & 0xFF, bw & 0xFF
        va, vb = sa - 256 if sa > 127 else sa, sb - 256 if sb > 127 else sb
        p.update({"a_byte": f"0x{sa:02x}", "b_byte": f"0x{sb:02x}", "a_value": va, "b_value": vb, "product": va * vb,
                  "popcount_a_byte": C.popcount(sa), "popcount_b_byte": C.popcount(sb),
                  "a_bits": [i for i in range(8) if (sa >> i) & 1], "b_bits": [i for i in range(8) if (sb >> i) & 1]})
    else:
        sa, nb = signif(t, aw)
        sbv, _ = signif(t, bw)
        mm = 0x7FFFFF if t == "fp32" else 0x03FF03FF
        p.update({"mantissa_popcount_a": C.popcount(aw & mm), "mantissa_popcount_b": C.popcount(bw & mm),
                  "radix4_nonzero_digits_a": sum(radix4_nonzero(x, nb) for x in sa),
                  "radix4_nonzero_digits_b": sum(radix4_nonzero(x, nb) for x in sbv)})
        if t == "fp32":
            p["mantissa_bits_a"] = [i for i in range(23) if (aw >> i) & 1]
            p["mantissa_bits_b"] = [i for i in range(23) if (bw >> i) & 1]
    return p


def i8name(w):
    v = w & 0xFF
    v = v - 256 if v > 127 else v
    return ("m" if v < 0 else "") + str(abs(v))


def new_name(t, aw, bw):
    if t == "int8":
        return f"e186_a{i8name(aw)}_b{i8name(bw)}"
    f = lambda w: "1" if w == F1 else f"{w:08x}"  # noqa: E731
    return f"e186_a{f(aw)}_b{f(bw)}"


def committed_tiles(root):
    seen = {}
    for d in COMMITTED_TILE_DIRS:
        for t in ("int8", "fp32", "fp16"):
            dd = os.path.join(root, d, t)
            if os.path.isdir(dd):
                for f in sorted(os.listdir(dd)):
                    if f.endswith(".bin"):
                        p = os.path.join(dd, f)
                        seen.setdefault(hashlib.sha256(open(p, "rb").read()).hexdigest(), (t, f[:-4], os.path.relpath(p, root)))
    return seen


def tile_bytes(aw, bw):
    return struct.pack("<I", aw) * 256 + struct.pack("<I", bw) * 256


# ------------------------------------------------------------------ the merged list (step 1)
def merged(root):
    seen = committed_tiles(root)
    rows, blobs, by_words = [], {}, {}
    for t, name, aw, bw, st, src in CM.kinds_rule():
        raw = tile_bytes(aw, bw)
        tile = src if src else f"tools/claims-v3/m12/tiles/{t}/{name}.bin"
        assert open(os.path.join(root, tile), "rb").read() == raw, tile
        r = {"key": f"{t}.{name}", "type": t, "a_word": f"0x{aw:08x}", "b_word": f"0x{bw:08x}", "tile": tile, "sha256": hashlib.sha256(raw).hexdigest(),
             "m12_key": f"{t}.{name}", "m12_set": st, "candidate_id": None, "source": "M12 (candidates-m12.json)",
             "tile_from": "committed before M12" if src else "M12's tile (8b85b498)", "new_tile": False, "bench": False, **props(t, aw, bw)}
        rows.append(r)
        by_words[(t, aw, bw)] = r
    for cid, t, aw, bw in CAND_KINDS:
        if (t, aw, bw) in by_words:
            r = by_words[(t, aw, bw)]
            r["candidate_id"] = cid
            r["source"] = "both lists (merged by words)"
            continue
        raw = tile_bytes(aw, bw)
        h = hashlib.sha256(raw).hexdigest()
        if h in seen:
            ct, cn, cp = seen[h]
            assert ct == t, (cid, seen[h])
            key, tile, tf, new = f"{t}.{cn}", cp, "committed tile, its own label", False
        else:
            nm = new_name(t, aw, bw)
            key, tile, tf, new = f"{t}.{nm}", f"{TILES_NEW}/{t}/{nm}.bin", "new tile (this lane)", True
            blobs[tile] = raw
        r = {"key": key, "type": t, "a_word": f"0x{aw:08x}", "b_word": f"0x{bw:08x}", "tile": tile, "sha256": h, "m12_key": None, "m12_set": None,
             "candidate_id": cid, "source": "E186-CANDIDATES only", "tile_from": tf, "new_tile": new, "bench": True, **props(t, aw, bw)}
        rows.append(r)
        by_words[(t, aw, bw)] = r
    for i, r in enumerate(rows):
        r["e186_id"] = f"K{i + 1:02d}"
    keys = [r["key"] for r in rows]
    assert len(set(keys)) == len(keys) == 39, len(keys)
    cid2key = {r["candidate_id"]: r["key"] for r in rows if r["candidate_id"]}
    trains = []
    for tid, a, b, st, what in CM.TRAINS:
        trains.append({"train": tid, "first": a, "second": b, "set": st, "what": what, "source": "M12 (candidates-m12.json)", "alias": None})
    for tid, fa, fb in CAND_TRAINS:
        a, b = cid2key[fa], cid2key[fb]
        dup = [x for x in trains if x["first"] == a and x["second"] == b]
        if dup:
            dup[0]["alias"] = tid
            dup[0]["source"] = "both lists (merged by words)"
            continue
        trains.append({"train": tid, "first": a, "second": b, "set": "E186-CANDIDATES", "what": CAND_TRAIN_WHAT[tid],
                       "source": "E186-CANDIDATES only", "alias": None, "candidate_first": fa, "candidate_second": fb})
    assert len(trains) == 22, len(trains)
    return rows, trains, blobs


def stage(root, write):
    rows, trains, blobs = merged(root)
    refs = {"int8.zeros": "tools/claims-v3/kinds/tiles/int8/zeros.bin", "fp32.zeros": "tools/claims-v3/kinds/tiles/fp32/zeros.bin",
            "fp16.zeros": "tools/claims-v3/kinds/tiles/fp16/zeros.bin"}
    for r in rows:
        if r["key"] in ("fp32.ones", "fp32.e182_a1_b3fffffff", "int8.m12_a1_b3", "fp32.m12_a1_b3f8000ff", "fp16.m12_a3c00_b3fff"):
            refs[r["key"]] = r["tile"]
    bench_rows = [{"key": k, "tile": p, "role": "reference (checked against its committed counts)"} for k, p in refs.items()]
    bench_rows += [{"key": r["key"], "tile": r["tile"], "role": "kind" + (" (a committed tile: checked against its committed counts)"
                                                                          if not r["new_tile"] else "")} for r in rows if r["bench"]]
    out = {"_what": "the merged candidate list for E186 (candidates_m12_e186.py stage): M12's 20 kinds and 14 trains with E186-CANDIDATES' 23 "
                    "kinds and 9 trains, duplicates merged by their words, each kind one E186 id; operand words only",
           "n_kinds": len(rows), "n_trains": len(trains), "kinds": rows, "trains": trains, "bench_rows": bench_rows}
    if write:
        for rel, raw in blobs.items():
            p = os.path.join(root, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "wb").write(raw)
        open(os.path.join(HERE, "kinds-m12-e186.json"), "w").write(json.dumps(out, indent=1) + "\n")
    return out, blobs


# ------------------------------------------------------------------ the forecasts (step 2)
def forecast(root):
    kl = json.load(open(os.path.join(HERE, "kinds-m12-e186.json")))
    cj = json.load(open(os.path.join(HERE, "candidates-m12.json")))
    m = json.load(open(os.path.join(HERE, "m12.json")))
    cm12 = json.load(open(os.path.join(HERE, "bench", "counts-m12.json")))["rows"]
    cnew = json.load(open(os.path.join(HERE, "bench", "counts-m12-e186.json")))["rows"]
    e178c = C.load(root, "tools/claims-v3/e178/bench/counts-e178.json")["rows"]
    e182c = C.load(root, "tools/claims-v3/e182/bench/counts-e182.json")["rows"]
    f182 = C.load(root, C.E182F)
    tr182 = C.load(root, f"{C.E182D}/trains-e182.json")["trains"]
    sc = C.load(root, f"{C.E182D}/scored.json")
    red = C.load(root, f"{C.E182D}/e182.json")
    K = sc["reported"]["kinds"]
    rate = {"int8": m["int8"]["mean_rate_per_s"],
            "fp32": statistics.median(K[k]["rate_per_s"] for k in K if k.startswith("fp32.")),
            "fp16": statistics.median(red["per_pass"][p]["fp16.randn"]["rate"] for p in red["per_pass"])}
    assert rate == cj["rates_per_s"], (rate, cj["rates_per_s"])
    N = f182["N_launch"]
    assert N == cj["N_launch"]
    sys.path.insert(0, os.path.join(root, "tools/claims-v3/e182"))
    sys.path.insert(0, os.path.join(root, C.M10D))
    import forecast_e182 as FE  # noqa: E402  (run_flips only)
    import fit_m10 as FM        # noqa: E402  (the feature chain only)
    import predict_m10 as PM    # noqa: E402
    m10 = PM.load_m10()
    zeros, zr = FM.M7.zeros_counts(), FM.M9.zeros_rows()
    se_reg = CM.HW_TRAIN / C.t975(31)
    assert abs(se_reg - cj["train_noise"]["se_w"]) < 1e-15
    se_meas = {"int8": statistics.median(tr182[t]["estimate"]["se"] for t in C.TRAINS8),
               "fp32": statistics.mean(tr182[t]["estimate"]["se"] for t in C.TRAINS32)}
    df_meas = {"int8": 31, "fp32": 37}
    out = {"_what": "M12's and M10's forecasts for E186's merged candidate list (candidates_m12_e186.py): a forecast for a registration to take, "
                    "NOT a registration", "label": "forecast, frozen; M12 a post hoc model (fitted on E182), M10 frozen; blind for a run only if "
                    "its registration commits this file before its first datum", "card": "aifoundry3, s = 1, W over each format's zeros",
           "rates_per_s": rate, "rates_rule": cj["rates_rule"] + " (candidates-m12.json's, unchanged)", "N_launch": N,
           "train_noise": {"registered": {"halfwidth_w": CM.HW_TRAIN, "units": 32, "se_w": se_reg},
                           "measured": {"se_w": {"int8": se_meas["int8"], "fp32": se_meas["fp32"], "fp16": se_meas["fp32"]},
                                        "df": {"int8": 31, "fp32": 37, "fp16": 37},
                                        "rule": "E182's trains: int8 the median se of T1-T4, fp32 the mean of T5 and T6; fp16 none measured, fp32's "
                                                "stands in (M12's REFIT.md.dated-note-2.md section 3)"}},
           "frozen_m12": {"file": "tools/claims-v3/m12/candidates-m12.json", "sha256": C.sha(os.path.join(HERE, "candidates-m12.json")),
                          "frozen": "Sun 8 Nov 2026 05:07:07 PST (FREEZE-m12.md)",
                          "use": "its 20 kinds' and 14 trains' M12 and M10 values are carried as frozen; recomputed here by the same code, "
                                 "they are equal (checks > frozen_m12_reproduced)"},
           "inputs_sha256": {p: C.sha(os.path.join(root, p)) for p in (
               "tools/claims-v3/m12/m12.json", "tools/claims-v3/m12/candidates-m12.json", "tools/claims-v3/m12/kinds-m12-e186.json",
               "tools/claims-v3/m12/bench/counts-m12.json", "tools/claims-v3/m12/bench/counts-m12-e186.json",
               "tools/claims-v3/m12/m12_common.py", "tools/claims-v3/m12/candidates_m12.py",
               "tools/claims-v3/e178/bench/counts-e178.json", "tools/claims-v3/e182/bench/counts-e182.json", C.E182F,
               f"{C.E182D}/scored.json", f"{C.E182D}/e182.json", f"{C.E182D}/trains-e182.json", f"{C.M10D}/m10.json",
               "tools/claims-v3/e178/flipmodel_e178.c", "rtl-sim/fma_toggle_v2/accum.c")},
           "checks": {}, "kinds": {}, "trains": {}}
    # the bench's checks: each zeros row and the committed reference tiles' rows, run again, equal their committed counts
    bc = {}
    for key, ref, src in (("int8.zeros", e178c, "E178"), ("fp32.zeros", e178c, "E178"), ("fp16.zeros", e178c, "E178"),
                          ("fp32.ones", e178c, "E178"), ("fp32.e182_a1_b3fffffff", e182c, "E182"), ("fp32.e182_a3fffffff_b1", e182c, "E182"),
                          ("int8.e178_v8", e178c, "E178"), ("int8.m12_a1_b3", cm12, "M12"), ("fp32.m12_a1_b3f8000ff", cm12, "M12"),
                          ("fp16.m12_a3c00_b3fff", cm12, "M12")):
        bc[key] = {"against": src, "mean_equal": cnew[key]["mean"] == ref[key]["mean"], "points_equal": cnew[key]["points"] == ref[key]["points"]}
    bc["check_mismatch_all_zero"] = all(p["check_mismatch"] == 0 for k in cnew for p in cnew[k]["points"])
    out["checks"]["bench"] = bc
    assert bc["check_mismatch_all_zero"] and all(v["mean_equal"] and v["points_equal"] for k, v in bc.items() if k != "check_mismatch_all_zero"), bc

    def counts_of(r):
        if r["m12_key"]:
            return cm12[r["key"]] if r["key"] in cm12 else cnew[r["key"]]
        return cnew[r["key"]]
    b8, cov8 = m["int8"]["b"], m["int8"]["cov"]
    b1, cov1 = m["arm_1K"]["b"], m["arm_1K"]["cov"]
    bf, covf = m["float"]["b"], m["float"]["cov"]
    fk = f182["kinds"]
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "flipmodel_e178")
        subprocess.run(["cc", "-O2", "-std=gnu11", f'-DACCUM_C="{os.path.join(root, "rtl-sim/fma_toggle_v2/accum.c")}"', "-o", exe,
                        os.path.join(root, "tools/claims-v3/e178/flipmodel_e178.c"), "-lm"], check=True)
        chk = {}
        for key in sorted(fk):   # all 24 of E182's kinds (M12's verifier's nit 7a)
            t = key.split(".")[0]
            fl = FE.run_flips(exe, t, fk[key]["a_word"], fk[key]["b_word"], N[t])
            chk[key] = fl["launch_mean"] == fk[key]["flips_i"]["launch_mean"]
        out["checks"]["flip_model_reproduces_e182_all_24"] = {"equal": sum(chk.values()), "of": len(chk)}
        assert all(chk.values()), chk
        for r in kl["kinds"]:
            t, key = r["type"], r["key"]
            fl = FE.run_flips(exe, t, r["a_word"], r["b_word"], N[t])
            lm = fl["launch_mean"]
            f = FM.chain_feats(counts_of(r), os.path.join(root, r["tile"]), t, zeros, zr)
            P = PM.d600(f, t, rate[t], "a3", m10, 1.0)
            row = {"e186_id": r["e186_id"], "type": t, "a_word": r["a_word"], "b_word": r["b_word"], "pc_a": r["popcount_a_word"],
                   "pc_b": r["popcount_b_word"], "tile": r["tile"], "m12_key": r["m12_key"], "candidate_id": r["candidate_id"],
                   "flips_launch_mean": lm, "P10_w": P, "M10_w": P}
            if t == "int8":
                d = C.int8_row(rate[t], lm, r["popcount_a_word"], r["popcount_b_word"])
                d1 = C.int8_row_1k(rate[t], lm, r["popcount_a_word"], r["popcount_b_word"])
                row["design_row"], row["_r1"] = d, d1
                row["M12_w"], row["M12_se_w"], row["M12-1K_w"] = C.dot(d, b8), C.se_of(d, cov8), C.dot(d1, b1)
            else:
                d = C.float_row(r["popcount_a_word"], r["popcount_b_word"])
                row["design_row"] = d
                row["M12_w"], row["M12_se_w"] = P + C.dot(d, bf), C.se_of(d, covf)
            if r["m12_key"]:
                fz = cj["kinds"][key]
                same = all(fz[q] == row[q] for q in ("M12_w", "M12_se_w", "P10_w", "flips_launch_mean", "design_row")
                           + (("M12-1K_w",) if t == "int8" else ()))
                assert same, key
                row["M12_from"] = "frozen: candidates-m12.json (recomputed here: equal)"
            else:
                row["M12_from"] = "new: computed here with M12 as committed (m12.json, no refit)"
            out["kinds"][key] = row
    frz = {"kinds_equal": sum(1 for k in out["kinds"].values() if k["m12_key"]), "trains_equal": 0}
    for x in kl["trains"]:
        tid, a, b = x["train"], x["first"], x["second"]
        A, B = out["kinds"][a], out["kinds"][b]
        dr = [p - q for p, q in zip(A["design_row"], B["design_row"])]
        arms = {}
        if A["type"] == "int8":
            dM12, sM12 = C.dot(dr, b8), C.se_of(dr, cov8)
            arms["M12-1K_w"] = C.dot([p - q for p, q in zip(A["_r1"], B["_r1"])], b1)
        else:
            dM12, sM12 = (A["P10_w"] - B["P10_w"]) + C.dot(dr, bf), C.se_of(dr, covf)
            if A["type"] == "fp16":
                arms["F16-NOHB_w (M10's difference alone)"] = A["P10_w"] - B["P10_w"]
        dM10 = A["P10_w"] - B["P10_w"]
        fam = "int8" if A["type"] == "int8" else "fp32"
        sig_r = math.sqrt(se_reg ** 2 + sM12 ** 2)
        sm = se_meas[fam]
        hw_m = sm * C.t975(df_meas[fam])
        sig_m = math.sqrt(sm ** 2 + sM12 ** 2)
        row = {"first": a, "second": b, "first_id": A["e186_id"], "second_id": B["e186_id"], "type": A["type"], "set": x["set"],
               "what": x["what"], "alias": x["alias"], "source": x["source"], "M12_w": dM12, "M12_se_w": sM12, "M10_w": dM10, **arms,
               "d_pc_a": A["pc_a"] - B["pc_a"], "d_pc_b": A["pc_b"] - B["pc_b"],
               "d_flips": {c: A["flips_launch_mean"][c] - B["flips_launch_mean"][c] for c in A["flips_launch_mean"]},
               "registered_noise": {"se_w": se_reg, "halfwidth_w": CM.HW_TRAIN,
                                    "power_excludes_0_if_M12": CM.norm_cdf((dM12 - CM.HW_TRAIN) / sig_r) + CM.norm_cdf((-dM12 - CM.HW_TRAIN) / sig_r),
                                    "power_excludes_0_if_M10": CM.norm_cdf((dM10 - CM.HW_TRAIN) / se_reg) + CM.norm_cdf((-dM10 - CM.HW_TRAIN) / se_reg),
                                    "separation_M12_M10_in_se": abs(dM12 - dM10) / sig_r},
               "measured_noise": {"se_w": sm, "halfwidth_w": hw_m,
                                  "power_excludes_0_if_M12": CM.norm_cdf((dM12 - hw_m) / sig_m) + CM.norm_cdf((-dM12 - hw_m) / sig_m),
                                  "power_excludes_0_if_M10": CM.norm_cdf((dM10 - hw_m) / sm) + CM.norm_cdf((-dM10 - hw_m) / sm),
                                  "separation_M12_M10_in_se": abs(dM12 - dM10) / sig_m}}
        if tid in cj["trains"]:
            fz = cj["trains"][tid]
            same = (fz["M12_w"] == dM12 and fz["M12_se_w"] == sM12 and fz["M10_w"] == dM10 and fz["first"] == a and fz["second"] == b
                    and fz["power_excludes_0_if_M12"] == row["registered_noise"]["power_excludes_0_if_M12"]
                    and fz["separation_M12_M10_in_se"] == row["registered_noise"]["separation_M12_M10_in_se"])
            assert same, tid
            frz["trains_equal"] += 1
            row["M12_from"] = "frozen: candidates-m12.json (recomputed here: equal)"
        else:
            row["M12_from"] = "new: computed here with M12 as committed (m12.json, no refit)"
        out["trains"][tid] = row
    out["checks"]["frozen_m12_reproduced"] = {**frz, "of_kinds": len(cj["kinds"]), "of_trains": len(cj["trains"])}
    assert frz["kinds_equal"] == 20 and frz["trains_equal"] == 14, frz
    order = sorted(out["trains"], key=lambda t: (-round(out["trains"][t]["registered_noise"]["separation_M12_M10_in_se"], 9), t))
    out["rank_by_separation_registered_noise"] = order
    for k in out["kinds"].values():
        k.pop("_r1", None)
    return out


def md(o, kl):
    ids = {r["key"]: r for r in kl["kinds"]}
    L = ["# M12's and M10's forecasts for E186's merged candidate list (candidates_m12_e186.py)", "",
         "A forecast for a registration to take, **not registered**. aifoundry3, s = 1, W over each format's zeros; rates "
         + ", ".join(f"{t} {v:.6e} /s" for t, v in o["rates_per_s"].items()) + " (candidates-m12.json's). M12 is post hoc (fitted on E182) "
         "and M10 frozen; these forecasts become blind for a run only if its registration commits them before its first datum. M12's 20 kinds "
         "and 14 trains are candidates-m12.json's frozen values (recomputed here: equal); the other 19 kinds and 8 trains are new here, from "
         "M12 as committed.", "",
         f"Registered train noise: half-width {o['train_noise']['registered']['halfwidth_w']} W at 32 units (se "
         f"{o['train_noise']['registered']['se_w']:.5f} W). Measured (E182): se int8 {o['train_noise']['measured']['se_w']['int8']:.5f}, "
         f"fp32 {o['train_noise']['measured']['se_w']['fp32']:.5f} W (fp16: fp32's). Separation = |M12 - M10| over the train's se combined "
         "with M12's; power = the chance the train's 95% interval excludes 0.", "",
         "| train | first - second | M12, W (se) | M10, W | sep. registered | sep. measured | power if M12 (reg.) | from |",
         "|---|---|---:|---:|---:|---:|---:|---|"]
    for tid in o["rank_by_separation_registered_noise"]:
        v = o["trains"][tid]
        nm = tid + (f" (= {v['alias']})" if v["alias"] else "")
        L.append(f"| {nm} | {v['first_id']} {v['first']} - {v['second_id']} {v['second']} | {v['M12_w']:+.4f} ({v['M12_se_w']:.4f}) | "
                 f"{v['M10_w']:+.4f} | {v['registered_noise']['separation_M12_M10_in_se']:.1f} | {v['measured_noise']['separation_M12_M10_in_se']:.1f} | "
                 f"{v['registered_noise']['power_excludes_0_if_M12']:.2f} | {'frozen' if v['M12_from'].startswith('frozen') else 'new'} |")
    L += ["", "| id | kind | A word | B word | pc A / B | M12, W (se) | M10, W | also | tile |", "|---|---|---|---|---|---:|---:|---|---|"]
    for key, v in o["kinds"].items():
        r = ids[key]
        L.append(f"| {v['e186_id']} | {key} | {v['a_word']} | {v['b_word']} | {v['pc_a']} / {v['pc_b']} | {v['M12_w']:.4f} ({v['M12_se_w']:.4f}) | "
                 f"{v['P10_w']:.4f} | {r['candidate_id'] or '-'} | {r['tile_from']} |")
    L += ["", "Checks: " + json.dumps(o["checks"], sort_keys=True)]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("what", choices=("stage", "forecast", "check"))
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    if a.what == "stage":
        out, blobs = stage(root, True)
        print(f"staged {out['n_kinds']} kinds ({len(blobs)} new tiles) and {out['n_trains']} trains")
        return 0
    kl = json.load(open(os.path.join(HERE, "kinds-m12-e186.json")))
    if a.what == "forecast":
        o = forecast(root)
        open(os.path.join(HERE, "candidates-m12-e186.json"), "w").write(json.dumps(o, indent=1, sort_keys=True) + "\n")
        open(os.path.join(HERE, "candidates-m12-e186.md"), "w").write(md(o, kl))
        print(md(o, kl))
        return 0
    out, blobs = stage(root, False)
    ok = open(os.path.join(HERE, "kinds-m12-e186.json")).read() == json.dumps(out, indent=1) + "\n" and all(
        open(os.path.join(root, p), "rb").read() == raw for p, raw in blobs.items())
    o = forecast(root)
    ok = ok and open(os.path.join(HERE, "candidates-m12-e186.json")).read() == json.dumps(o, indent=1, sort_keys=True) + "\n" and \
        open(os.path.join(HERE, "candidates-m12-e186.md")).read() == md(o, kl)
    print("CHECK PASS" if ok else "CHECK FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
