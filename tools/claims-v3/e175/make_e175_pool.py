#!/usr/bin/env python3
"""Q143(g): E175's tiles, drawn by a committed rule from a seed nobody chose, and the rule that keeps or replaces each one by its frozen
predictions (E175.md, "The design"). Written and committed with E175.md before any E175 tile, count or prediction exists.

    python3 -B make_e175_pool.py seed                                   # the seed, its rule and its value
    python3 -B make_e175_pool.py draw --out DIR                         # the candidate stream (CAP candidates) and the three zeros anchors
    python3 -B make_e175_pool.py draw --test --out DIR/TEST             # the same code on a test seed, into a directory named TEST only
    python3 -B make_e175_pool.py manifest --stream DIR/stream-e175.json --upto K --out DIR
                                                                        # DIR/e175.json: the zeros anchors and candidates 0..K-1 (not refused)
    python3 -B make_e175_pool.py select --stream DIR/stream-e175.json --predictions P.json --upto K --out design-e175.json
                                                                        # the registered selection over candidates 0..K-1, in stream order
    python3 -B make_e175_pool.py build --stream DIR/stream-e175.json --design design-e175.json --out POOL
                                                                        # the pool: the zeros anchors and the selected tiles, e175.json, SHA256SUMS
    python3 -B make_e175_pool.py check --out POOL                       # every tile re-read: bytes, label, class, refusals, twins

The candidates come from pool 8's committed generator, unchanged (tools/claims-v3/kinds/blind8/make_blind8.py, lab 153b720f; its sha256 is
checked before it is imported): each candidate draws a format (fp32 or fp16), one of that generator's twelve float families (U_FLOAT, its
section 5.3) and a truncation m, all on its own seeded stream; the family's own u_float() makes A and B; the low m mantissa bits of every element
are then cleared (fp32 m in 0-23, fp16 m in 0-10, uniform), and make_kinds.encode writes the 2,048 bytes. A candidate is refused (and the next one
drawn) if make_blind8's tile_refusal or class_check refuses it, or if its bytes equal any committed tile under tools/claims-v3/kinds/ or an earlier
candidate's. Nothing here reads a measurement or a model's error: the selection reads only the frozen predictor's predictions.

Run with the Intel's /usr/bin/python3 (3.9.6, numpy 1.26.4), as the predictor runs; numpy's distributions are not promised to give the same
stream on another numpy version, so the committed tiles (their sha256 in the pool's SHA256SUMS) are what runs, and a re-draw on this interpreter
gives them byte for byte. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
KINDS = os.path.join(TOP, "tools", "claims-v3", "kinds")
B8_PY = os.path.join(KINDS, "blind8", "make_blind8.py")
B8_SHA256 = "fee9a4f01d32795e526c0b8ec06657b04024e8413351302080422643a76d14ea"   # DESIGN.md section 0; lab 153b720f
MK_PY = os.path.join(KINDS, "make_kinds.py")
B8_JSON = os.path.join(KINDS, "blind8", "blind8.json")

SEED_COMMIT = "4576fb9078726ec4ae186f2e91170986f6e03c58"   # lab commit: pool 8's predictions frozen (Q142(x)), before this design
SEED_RULE = "int(sha256(ascii of the 40-hex commit string).hexdigest()[:16], 16)"
SEED = int(hashlib.sha256(SEED_COMMIT.encode("ascii")).hexdigest()[:16], 16)
TEST_SEED = int(hashlib.sha256(b"e175 dry run, never the pool").hexdigest()[:16], 16)   # draw --test only: a directory named TEST, never the pool
_USE = {"seed": SEED}
CAP = 64                                    # candidates in the stream at most
FORMATS_DRAWN = ("fp32", "fp16")
TRUNC = {"fp32": (0, 23), "fp16": (0, 10)}  # m, the low mantissa bits cleared in every element, uniform over the closed range
GOVERNED_BELOW_MHZ = 795.0                  # the frozen file's group rule (POOL8-REGISTRATION section 7; A2-3 (f))
ADMISSION_W = 82.0                          # a candidate whose larger 95% upper peak (M10 carried, M9's part) exceeds it is replaced
STRATA = ((0.0, 745.0), (745.0, 762.0), (762.0, 779.0), (779.0, 795.0))   # M10 carried's fallback burst clock, MHz, [lo, hi)
PER_STRATUM = 4
N_GOVERNED = PER_STRATUM * len(STRATA)      # 16
N_PINNED = 8
MIN_GOVERNED = 8                            # the registered minimum of a group (pool8-registration.json, A2_group)
ZEROS = ("fp32.anchor7_zeros", "fp16.anchor7_zeros", "int8.anchor7_zeros")
LABEL = "e5c{i:02d}_{fam}_t{m}_{sig}"       # <fmt>.<this>: the index, the family, m and 6 hex of the tile's sha256


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    with open(p, "rb") as f:
        return sha(f.read())


def rng(*tag):
    """one stream per tag from the one seed: make_kinds.rng_for's and make_blind8.rng's scheme, under the prefix e175/"""
    t = "e175/" + "/".join(str(x) for x in tag)
    return np.random.default_rng([_USE["seed"], int.from_bytes(hashlib.sha256(t.encode()).digest()[:8], "little")])


def load_mod(path, name, want=None):
    if want and sha_file(path) != want:
        raise SystemExit(f"STOP: {os.path.relpath(path, TOP)} differs from its committed sha256 {want}")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mods():
    return load_mod(MK_PY, "make_kinds"), load_mod(B8_PY, "make_blind8", B8_SHA256)


def truncate(x, fmt, m):
    """clear the low m mantissa bits of every element (sign and exponent untouched); the result is exactly representable"""
    if fmt == "fp32":
        v = np.ascontiguousarray(np.asarray(x, dtype=np.float64).astype(np.float32))
        return (v.view(np.uint32) & np.uint32((0xFFFFFFFF << m) & 0xFFFFFFFF)).view(np.float32)
    v = np.ascontiguousarray(np.asarray(x, dtype=np.float64).astype(np.float16))
    return (v.view(np.uint16) & np.uint16((0xFFFF << m) & 0xFFFF)).view(np.float16)


def earlier_hashes():
    """every committed tile file under tools/claims-v3/kinds/ (the pools blind3-blind8, the kinds' tiles, the real cuts): sha256 -> path"""
    out = {}
    for dirpath, _, files in os.walk(KINDS):
        for fn in sorted(files):
            if fn.endswith(".bin"):
                p = os.path.join(dirpath, fn)
                out.setdefault(sha_file(p), os.path.relpath(p, TOP))
    return out


def candidate(i, mk, B8):
    r = rng("cand", i)
    fmt = FORMATS_DRAWN[int(r.integers(0, len(FORMATS_DRAWN)))]
    fam = B8.U_FLOAT[int(r.integers(0, len(B8.U_FLOAT)))]
    lo, hi = TRUNC[fmt]
    m = int(r.integers(lo, hi + 1))
    K = mk.TYPES[fmt][3]
    A, B, params = B8.u_float(fam, rng("fam", i), K)
    if fmt == "fp16":
        A, B = np.clip(A, -B8.FP16_MAX, B8.FP16_MAX), np.clip(B, -B8.FP16_MAX, B8.FP16_MAX)
    raw = mk.encode(truncate(A, fmt, m), truncate(B, fmt, m), fmt)
    return fmt, fam, m, params, raw


def jsonable(p):
    return {k: (float(v) if isinstance(v, (float, np.floating)) else int(v) if isinstance(v, (int, np.integer)) else v) for k, v in p.items()}


def draw(out, test=False):
    if test:
        if os.path.basename(os.path.normpath(out)) != "TEST":
            raise SystemExit("STOP: a test draw goes only to a directory named TEST")
        _USE["seed"] = TEST_SEED
    mk, B8 = mods()
    early = earlier_hashes()
    seen = {}
    cands = []
    os.makedirs(out, exist_ok=True)
    for i in range(CAP):
        fmt, fam, m, params, raw = candidate(i, mk, B8)
        h = sha(raw)
        rec = {"index": i, "type": fmt, "family": fam, "trunc_bits": m, "params": jsonable(params), "sha256_whole": h,
               "streams": [["cand", i], ["fam", i]]}
        why = B8.tile_refusal(raw, fmt, mk)
        if why is None:
            ok, why2 = B8.class_check(raw, fmt, "U", "kind", mk)
            why = None if ok else why2
        if why is None and h in early:
            why = f"byte twin of the committed {early[h]}"
        if why is None and h in seen:
            why = f"byte twin of candidate {seen[h]}"
        if why is not None:
            rec["refused"] = why
        else:
            seen[h] = i
            name = f"{fmt}." + LABEL.format(i=i, fam=fam, m=m, sig=h[:6])
            rel = f"tiles/{fmt}/{name}.bin"
            os.makedirs(os.path.join(out, "tiles", fmt), exist_ok=True)
            with open(os.path.join(out, rel), "wb") as f:
                f.write(raw)
            rec.update(name=name, file=rel, sha256={"whole": h, "a": sha(raw[:1024]), "b": sha(raw[1024:])})
        cands.append(rec)
    z = zeros_records(out)
    stream = {"_note": "Q143(g) make_e175_pool.py draw: E175's candidate stream, in stream order (E175.md, The design)",
              "seed_commit": SEED_COMMIT, "seed_rule": SEED_RULE, "seed": _USE["seed"], "seed_hex": f"{_USE['seed']:#018x}",
              "test_seed": bool(test), "cap": CAP,
              "trunc_bits": {k: list(v) for k, v in TRUNC.items()}, "families": list(B8.U_FLOAT), "formats": list(FORMATS_DRAWN),
              "generator_sha256": sha_file(os.path.abspath(__file__)), "make_blind8_sha256": sha_file(B8_PY), "make_kinds_sha256": sha_file(MK_PY),
              "python": sys.version.split()[0], "numpy": np.__version__, "earlier_tiles_hashed": len(early),
              "zeros_anchors": z, "candidates": cands}
    with open(os.path.join(out, "stream-e175.json"), "w") as f:
        json.dump(stream, f, indent=1, sort_keys=True)
    n_ok = sum(1 for c in cands if "refused" not in c)
    print(json.dumps({"candidates": len(cands), "kept_by_the_generator": n_ok, "refused": len(cands) - n_ok,
                      "by_format": {t: sum(1 for c in cands if c["type"] == t and "refused" not in c) for t in FORMATS_DRAWN},
                      "earlier_tiles_hashed": len(early), "seed": f"{_USE['seed']:#018x}", "test_seed": bool(test)}, sort_keys=True))
    return stream


def zeros_records(out):
    """pool 8's three zeros anchors (pool 7's floors, one file's bytes under three types), copied with their blind8.json records"""
    man = {t["name"]: t for t in json.load(open(B8_JSON))["tiles"]}
    recs = []
    for n in ZEROS:
        t = dict(man[n])
        src = os.path.join(KINDS, "blind8", t["file"])
        raw = open(src, "rb").read()
        if sha(raw) != t["sha256"]["whole"]:
            raise SystemExit(f"STOP: {n} does not hash as blind8.json says")
        os.makedirs(os.path.join(out, os.path.dirname(t["file"])), exist_ok=True)
        with open(os.path.join(out, t["file"]), "wb") as f:
            f.write(raw)
        recs.append(t)
    return recs


def manifest_tiles(stream, names):
    out = [dict(z) for z in stream["zeros_anchors"]]
    for c in stream["candidates"]:
        if c.get("name") in names:
            out.append({"name": c["name"], "file": c["file"], "type": c["type"], "case": "U-trunc", "priority": 1, "anchor": False,
                        "role": "kind", "real": False, "sha256": c["sha256"],
                        "e175": {"index": c["index"], "family": c["family"], "trunc_bits": c["trunc_bits"], "params": c["params"]}})
    return out


def write_manifest(stream, upto, out):
    names = [c["name"] for c in stream["candidates"][:upto] if "refused" not in c]
    tiles = manifest_tiles(stream, set(names))
    doc = {"_note": f"Q143(g): E175's manifest in pool 7's JSON form (blind8.json's fields), the zeros anchors and candidates 0-{upto - 1}",
           "n_tiles": len(tiles), "upto": upto, "tiles": tiles}
    with open(os.path.join(out, "e175.json"), "w") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
    print(json.dumps({"manifest": os.path.join(out, "e175.json"), "tiles": len(tiles), "candidates": len(names)}))


def stratum_of(mhz):
    for k, (lo, hi) in enumerate(STRATA):
        if lo <= mhz < hi:
            return k
    return None


def select(stream, pred, upto):
    """E175.md, The design, steps 1-6: the candidates in stream order; the first PER_STRATUM governed per stratum and the first N_PINNED
    pinned, each admitted at 82 W; a candidate over 82 W is replaced by the next draw; the stream stops when every set is full or at CAP"""
    tiles = pred["tiles"]
    strata = [[] for _ in STRATA]
    pinned, spare, rec = [], [], []
    stop_at = None
    for c in stream["candidates"][:upto]:
        r = {"index": c["index"], "name": c.get("name"), "type": c["type"], "family": c["family"], "trunc_bits": c["trunc_bits"]}
        if "refused" in c:
            r["outcome"] = "refused by the generator: " + c["refused"]
            rec.append(r)
            continue
        t = tiles.get(c["name"])
        if t is None:
            raise SystemExit(f"STOP: candidate {c['index']} ({c['name']}) has no prediction: predict ran on fewer candidates than --upto")
        a, b = t["M10"]["a2_fallback"], t["M9"]["a2_fallback"]
        peak = max(float(a["peak_board_hi95_w"]), float(b["peak_board_hi95_w"]))
        r.update(M10_mhz=a["burst_mhz"], M10_board_w=a["burst_board_w"], M10_group=a["group"], M9_mhz=b["burst_mhz"],
                 peak_hi95_w=round(peak, 3), M10_D600_w=t["M10"]["D600_a3_footing_w"])
        if peak > ADMISSION_W:
            r["outcome"] = "out at 82 W: replaced by the next draw"
        elif a["group"] == "governed":
            k = stratum_of(float(a["burst_mhz"]))
            if k is None:
                raise SystemExit(f"STOP: {c['name']}: governed at {a['burst_mhz']} MHz, in no stratum")
            r["stratum"] = k + 1
            if len(strata[k]) < PER_STRATUM:
                strata[k].append(c["name"])
                r["outcome"] = f"governed: kept in stratum {k + 1}"
            else:
                spare.append(c["name"])
                r["outcome"] = f"governed: stratum {k + 1} full (a spare, for step 6 only)"
        else:
            if len(pinned) < N_PINNED:
                pinned.append(c["name"])
                r["outcome"] = "pinned: kept"
            else:
                r["outcome"] = "pinned: the pinned set full"
        rec.append(r)
        if all(len(s) == PER_STRATUM for s in strata) and len(pinned) == N_PINNED:
            stop_at = c["index"]
            break
    filled = stop_at is not None
    fallback = []
    if not filled and upto >= CAP:
        for nm in spare:
            if sum(len(s) for s in strata) + len(fallback) >= N_GOVERNED:
                break
            fallback.append(nm)
    governed = [n for s in strata for n in s] + fallback
    status = ("FILLED" if filled else "AT CAP" if upto >= CAP else "NEEDS MORE CANDIDATES")
    if status == "AT CAP" and len(governed) < MIN_GOVERNED:
        status = "NO-GO: fewer than 8 governed tiles within the cap"
    return {"_note": "Q143(g) make_e175_pool.py select: E175.md, The design; predictions only, never a measurement",
            "status": status, "upto": upto, "stopped_at_index": stop_at, "strata_mhz": [list(s) for s in STRATA],
            "governed_by_stratum": strata, "governed_fallback": fallback, "governed": governed, "pinned": pinned,
            "n_governed": len(governed), "n_pinned": len(pinned), "spares": spare, "records": rec,
            "predictions_sha256": pred.get("_sha256")}


def build(stream, design, out):
    if design["status"] not in ("FILLED", "AT CAP"):
        raise SystemExit(f"STOP: the design reads {design['status']}")
    names = set(design["governed"]) | set(design["pinned"])
    tiles = manifest_tiles(stream, names)
    src = os.path.dirname(os.path.abspath(design["_stream_path"]))
    os.makedirs(out, exist_ok=True)
    for t in tiles:
        raw = open(os.path.join(src, t["file"]), "rb").read()
        if sha(raw) != t["sha256"]["whole"]:
            raise SystemExit(f"STOP: {t['name']} does not hash as the stream says")
        os.makedirs(os.path.join(out, os.path.dirname(t["file"])), exist_ok=True)
        with open(os.path.join(out, t["file"]), "wb") as f:
            f.write(raw)
    for t in tiles:
        n = t["name"]
        t["e175_set"] = "zeros" if n in ZEROS else "governed" if n in design["governed"] else "pinned"
    doc = {"_note": "Q143(g): E175's pool, the zeros anchors and the selected tiles, in pool 7's JSON form (make_e175_pool.py build)",
           "n_tiles": len(tiles), "seed_commit": SEED_COMMIT, "seed": SEED, "generator_sha256": sha_file(os.path.abspath(__file__)),
           "governed": design["governed"], "pinned": design["pinned"], "zeros_anchors": list(ZEROS), "tiles": tiles}
    with open(os.path.join(out, "e175.json"), "w") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
    lines = []
    for dirpath, _, files in os.walk(out):
        for fn in sorted(files):
            if fn == "SHA256SUMS":
                continue
            p = os.path.join(dirpath, fn)
            lines.append(f"{sha_file(p)}  {os.path.relpath(p, out)}")
    with open(os.path.join(out, "SHA256SUMS"), "w") as f:
        f.write("\n".join(sorted(lines, key=lambda x: x.split()[1])) + "\n")
    print(json.dumps({"pool": out, "tiles": len(tiles), "governed": len(design["governed"]), "pinned": len(design["pinned"])}))


def check(out):
    mk, B8 = mods()
    doc = json.load(open(os.path.join(out, "e175.json")))
    early = earlier_hashes()
    bad, seen = [], {}
    for t in doc["tiles"]:
        raw = open(os.path.join(out, t["file"]), "rb").read()
        h = sha(raw)
        if h != t["sha256"]["whole"] or sha(raw[:1024]) != t["sha256"]["a"] or sha(raw[1024:]) != t["sha256"]["b"]:
            bad.append(f"{t['name']}: sha256 differs")
        if t["name"] in ZEROS:
            continue
        e = t["e175"]
        fmt, fam, m, _, raw2 = candidate(e["index"], mk, B8)
        if raw2 != raw or fmt != t["type"] or fam != e["family"] or m != e["trunc_bits"]:
            bad.append(f"{t['name']}: the stream's candidate {e['index']} does not give these bytes")
        want = f"{fmt}." + LABEL.format(i=e["index"], fam=fam, m=m, sig=h[:6])
        if want != t["name"]:
            bad.append(f"{t['name']}: the label from the bytes reads {want}")
        why = B8.tile_refusal(raw, fmt, mk)
        ok, why2 = B8.class_check(raw, fmt, "U", "kind", mk)
        if why or not ok:
            bad.append(f"{t['name']}: refused ({why or why2})")
        if h in early:
            bad.append(f"{t['name']}: a byte twin of {early[h]}")
        if h in seen:
            bad.append(f"{t['name']}: a byte twin of {seen[h]}")
        seen[h] = t["name"]
    print(f"checked {len(doc['tiles'])} tiles: {len(bad)} problems")
    for b in bad:
        print("  ", b)
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed")
    d = sub.add_parser("draw")
    d.add_argument("--out", required=True)
    d.add_argument("--test", action="store_true")
    m = sub.add_parser("manifest")
    m.add_argument("--stream", required=True)
    m.add_argument("--upto", type=int, required=True)
    m.add_argument("--out", required=True)
    s = sub.add_parser("select")
    s.add_argument("--stream", required=True)
    s.add_argument("--predictions", required=True)
    s.add_argument("--upto", type=int, required=True)
    s.add_argument("--out", required=True)
    b = sub.add_parser("build")
    b.add_argument("--stream", required=True)
    b.add_argument("--design", required=True)
    b.add_argument("--out", required=True)
    c = sub.add_parser("check")
    c.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "seed":
        print(json.dumps({"seed_commit": SEED_COMMIT, "rule": SEED_RULE, "seed": SEED, "seed_hex": f"{SEED:#018x}"}))
        return 0
    if a.cmd == "draw":
        draw(a.out, a.test)
        return 0
    if a.cmd == "check":
        return check(a.out)
    stream = json.load(open(a.stream))
    if stream.get("generator_sha256") != sha_file(os.path.abspath(__file__)):
        raise SystemExit("STOP: the stream was drawn by another version of this file")
    if stream.get("test_seed") and a.cmd == "build" and os.path.basename(os.path.normpath(a.out)) != "TEST":
        raise SystemExit("STOP: a test stream builds only into a directory named TEST")
    if a.cmd == "manifest":
        write_manifest(stream, min(a.upto, CAP), a.out)
        return 0
    if a.cmd == "select":
        pred = json.load(open(a.predictions))
        pred["_sha256"] = sha_file(a.predictions)
        res = select(stream, pred, min(a.upto, CAP))
        res["stream_sha256"] = sha_file(a.stream)
        res["_stream_path"] = os.path.relpath(os.path.abspath(a.stream), TOP)
        with open(a.out, "w") as f:
            json.dump(res, f, indent=1, sort_keys=True)
        print(json.dumps({k: res[k] for k in ("status", "upto", "stopped_at_index", "n_governed", "n_pinned")}, sort_keys=True))
        return 0
    design = json.load(open(a.design))
    design["_stream_path"] = os.path.join(TOP, design["_stream_path"]) if not os.path.isabs(design["_stream_path"]) else design["_stream_path"]
    build(stream, design, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
