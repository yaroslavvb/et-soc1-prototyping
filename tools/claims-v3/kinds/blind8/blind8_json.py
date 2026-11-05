#!/usr/bin/env python3
"""Q142(x): blind8.json, pool 8's manifest in pool 7's JSON form, written mechanically from the pool's MANIFEST, so that Q142(p)'s
frozen predictor can read the pool (dated note A1 beside DESIGN.md, committed with this file before blind8.json existed).

    python3 -B blind8_json.py convert <pool dir> [--out <file>]   MANIFEST -> <pool dir>/blind8.json (or --out); refuses, writing
                                                                  nothing, if a line or a tile breaks the rule below
    python3 -B blind8_json.py roundtrip [--out <file.json>]       the rule on pool 7: blind7/MANIFEST converted against blind7.json
    python3 -B blind8_json.py sets <pool dir> [--out <file.json>] what the frozen predictor reads from <pool dir>: the manifest it
                                                                  picks, the anchors' roles and the scored sets; exit 0 only if
                                                                  they are A1-3's (pool 8's design)

THE RULE (the Q142(r)/(p)/(d) critic's fault 1, field by field). Each MANIFEST line holds eight fields,
`<sha256> <file> <label> <format> case=<c> p<k> <role> <flag>`, and gives one tile, in MANIFEST's order:
    name = label; file = file; type = format; case = c; priority = the integer k; anchor = (role in {anchor, check});
    role = role; real = (c == "R"); sha256 = {whole: the file's sha256 (it must equal the line's), a: of bytes 0-1023,
    b: of bytes 1024-2047}.
Nothing else is written per tile (the flag stays in MANIFEST; the predictor finds re-runs from the bytes). The top level holds a
note, the MANIFEST's and this file's sha256 and the tiles; no time stamp, so a re-run writes the same bytes. A line without eight
fields, a format other than fp32/fp16/int8, a case without "case=", a priority other than p<integer>, a role other than anchor,
check, kind or rerun, a repeated label, a tile that is not 2,048 bytes or whose bytes differ from its line: refused (exit 1),
nothing written.

`roundtrip` and `sets` import the frozen predictor through predict_pool8_a2.py (which checks its own and predict_pool8.py's hash
lists first) and call its manifest(), roles(), earlier_tiles(), tile_bytes() and make_sets() unchanged; the tile records they
pass to make_sets() hold exactly the four fields predict() builds for it (type, priority, anchor_role, rerun_of).
Standard library (numpy only through the predictor's imports). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
B7 = os.path.join(TOP, "tools", "claims-v3", "kinds", "blind7")
PRED_DIR = os.path.join(TOP, "docs", "reports", "data", "2026-11-05-q142p-pool8-predictor")
ROLES = ("anchor", "check", "kind", "rerun")
FORMATS = ("fp32", "fp16", "int8")
FLOATS = ("fp32", "fp16")
# dated note A1-3: what the frozen predictor must read from pool 8 before any count is used
EXPECT = {"roles": {"zeros": 3, "scale": 6, "check": 3}, "N1": 31, "by_format": {"fp32": 11, "fp16": 8, "int8": 12},
          "F1": 19, "I1": 12, "RR": 12, "KA": 2}
sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
fsha = lambda p: sha(open(p, "rb").read())  # noqa: E731


class Refused(Exception):
    pass


def rel(p):
    a = os.path.abspath(p)
    return os.path.relpath(a, TOP) if a.startswith(TOP + os.sep) else os.path.basename(a)


def convert(pool):
    """the rule, in memory: {"tiles": [...]} from <pool>/MANIFEST"""
    mpath = os.path.join(pool, "MANIFEST")
    tiles, seen, bad = [], set(), []
    lines = open(mpath).read().split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    for i, line in enumerate(lines, 1):
        f = line.split()
        if len(f) != 8:
            bad.append(f"line {i}: {len(f)} fields, not 8")
            continue
        h, file, label, fmt, case, prio, role, _flag = f
        if fmt not in FORMATS:
            bad.append(f"line {i}: format {fmt!r}")
        if not case.startswith("case=") or len(case) == 5:
            bad.append(f"line {i}: case {case!r}")
        if not re.fullmatch(r"p[0-9]+", prio):
            bad.append(f"line {i}: priority {prio!r}")
        if role not in ROLES:
            bad.append(f"line {i}: role {role!r}")
        if label in seen:
            bad.append(f"line {i}: label {label} repeats")
        seen.add(label)
        p = os.path.join(pool, file)
        raw = open(p, "rb").read() if os.path.isfile(p) else b""
        if len(raw) != 2048:
            bad.append(f"line {i}: {file} holds {len(raw)} bytes, not 2,048")
        elif sha(raw) != h:
            bad.append(f"line {i}: {file}'s bytes differ from its line's sha256")
        if bad:
            continue
        c = case[len("case="):]
        tiles.append({"name": label, "file": file, "type": fmt, "case": c, "priority": int(prio[1:]),
                      "anchor": role in ("anchor", "check"), "role": role, "real": c == "R",
                      "sha256": {"whole": h, "a": sha(raw[:1024]), "b": sha(raw[1024:])}})
    if bad:
        raise Refused("; ".join(bad))
    return {"_note": "Q142(x): pool 8's manifest in pool 7's JSON form, written mechanically from MANIFEST by blind8_json.py "
                     "(the rule in its docstring and in DESIGN.md.dated-note-1.md, A1-1); one tile a MANIFEST line, in its order",
            "source": "MANIFEST", "manifest_sha256": fsha(mpath), "converter": "tools/claims-v3/kinds/blind8/blind8_json.py",
            "converter_sha256": fsha(os.path.abspath(__file__)), "n_tiles": len(tiles), "tiles": tiles}


def predictor():
    """predict_pool8.py, frozen, through predict_pool8_a2.P() (it checks SHA256SUMS and SHA256SUMS-a2 before the import)"""
    if PRED_DIR not in sys.path:
        sys.path.insert(0, PRED_DIR)
    import predict_pool8_a2 as A  # noqa: E402
    return A, A.P()


def read_sets(P, man, pool):
    """what predict() derives before any count: the anchors' roles, and make_sets() on the four fields it reads"""
    rl = P.roles(man, pool)
    earlier = P.earlier_tiles()
    tiles = {}
    for m in man["tiles"]:
        _, _, h = P.tile_bytes(pool, m)
        tiles[m["name"]] = {"type": m["type"], "priority": m.get("priority"), "anchor_role": rl.get(m["name"], {}).get("role"),
                            "rerun_of": [f"{p}:{n}" for p, n, _ in earlier.get((h, m["type"]), [])] or None}
    return rl, tiles, P.make_sets(tiles, rl)


def sizes(sets):
    return {k: (len(v) if isinstance(v, list) else {kk: len(vv) for kk, vv in v.items()}) for k, v in sets.items()}


def roundtrip():
    conv = convert(B7)
    ref = json.load(open(os.path.join(B7, "blind7.json")))
    cv = {t["name"]: t for t in conv["tiles"]}
    rf = {t["name"]: t for t in ref["tiles"]}
    mism, bad_names = [], set()
    for n in sorted(set(cv) | set(rf)):
        a, b = cv.get(n), rf.get(n)
        if a is None or b is None:
            mism.append(f"{n}: only in {'blind7.json' if a is None else 'MANIFEST'}")
            bad_names.add(n)
            continue
        for k in ("file", "type", "priority", "anchor", "real"):
            if a[k] != b[k]:
                mism.append(f"{n}.{k}: {a[k]!r} against {b[k]!r}")
                bad_names.add(n)
        for k in ("whole", "a", "b"):
            if a["sha256"][k] != b["sha256"][k]:
                mism.append(f"{n}.sha256.{k}")
                bad_names.add(n)
    order_same = [t["name"] for t in conv["tiles"]] == [t["name"] for t in ref["tiles"]]
    # the predictor's own reading of each manifest (pool 7's tiles are all their own earlier twins, so RR holds every float kind)
    _, P = predictor()
    r_conv, _, s_conv = read_sets(P, conv, B7)
    r_ref, _, s_ref = read_sets(P, ref, B7)
    same_roles = {n: v["role"] for n, v in r_conv.items()} == {n: v["role"] for n, v in r_ref.items()}
    same_sets = s_conv == s_ref
    ok = not mism and len(cv) == len(rf) == 61 and same_roles and same_sets
    return {"_note": "Q142(x) blind8_json.py roundtrip: the converter's rule on pool 7 (blind7/MANIFEST) against the committed blind7.json",
            "manifest": rel(os.path.join(B7, "MANIFEST")), "manifest_sha256": fsha(os.path.join(B7, "MANIFEST")),
            "reference": rel(os.path.join(B7, "blind7.json")), "reference_sha256": fsha(os.path.join(B7, "blind7.json")),
            "converter_sha256": fsha(os.path.abspath(__file__)),
            "fields_compared": ["name (the key)", "file", "type", "priority", "anchor", "real", "sha256.whole", "sha256.a", "sha256.b"],
            "tiles_converted": len(cv), "tiles_in_reference": len(rf),
            "tiles_identical_in_every_field": len((set(cv) & set(rf)) - bad_names),
            "mismatches": mism, "same_order": order_same,
            "predictor_roles_identical": same_roles, "predictor_sets_identical": same_sets, "predictor_sets_sizes": sizes(s_ref),
            "not_compared": "case (blind7.json writes a description, MANIFEST a letter) and role (blind7.json has no role field); "
                            "the predictor reads neither for pool 7's anchors",
            "PASS": ok}


def sets_check(pool):
    A, P = predictor()
    n_inputs = P.check_inputs()
    mpath, man = P.manifest(pool)
    rl, tiles, sets = read_sets(P, man, pool)
    by_role = {r: sorted(n for n, v in rl.items() if v["role"] == r) for r in ("zeros", "scale", "check")}
    src = {r: sorted({v["source"] for v in rl.values() if v["role"] == r}) for r in by_role}
    got = {"roles": {r: len(v) for r, v in by_role.items()}, "N1": len(sets["N1"]), "by_format": {t: len(v) for t, v in sets["by_format"].items()},
           "F1": len(sets["F1"]), "I1": len(sets["I1"]), "RR": len(sets["RR"]), "KA": len(sets["KA"])}
    diff = {k: {"expected": EXPECT[k], "read": got[k]} for k in EXPECT if EXPECT[k] != got[k]}
    picked = os.path.basename(mpath)
    ok = not diff and picked == "blind8.json"
    return {"_note": "Q142(x) blind8_json.py sets: what Q142(p)'s frozen predictor reads from pool 8 before any count (dated note A1-3)",
            "predictor": "predict_pool8_a2.P() -> predict_pool8.py (lab 9d81d254 / 97765c0a), its own manifest(), roles(), earlier_tiles(), "
                         "tile_bytes() and make_sets()", "inputs_checked": n_inputs,
            "manifest_picked": rel(mpath), "manifest_sha256": fsha(mpath), "n_tiles": len(man["tiles"]),
            "roles": by_role, "role_sources": src, "sets": sets, "sizes": sizes(sets),
            "rerun_of": {n: tiles[n]["rerun_of"] for n in sorted(tiles) if tiles[n]["rerun_of"]},
            "expected": EXPECT, "read": got, "differences": diff, "PASS": ok}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("convert")
    c.add_argument("pool")
    c.add_argument("--out")
    r = sub.add_parser("roundtrip")
    r.add_argument("--out")
    s = sub.add_parser("sets")
    s.add_argument("pool")
    s.add_argument("--out")
    a = ap.parse_args()
    if a.cmd == "convert":
        try:
            j = convert(os.path.abspath(a.pool))
        except Refused as e:
            print("REFUSED; nothing written: " + str(e))
            return 1
        out = a.out or os.path.join(a.pool, "blind8.json")
        if os.path.exists(out):
            print(f"REFUSED; {rel(out)} exists (new files only)")
            return 1
        with open(out, "w") as fh:
            json.dump(j, fh, indent=1)
            fh.write("\n")
        print(json.dumps({"wrote": rel(out), "sha256": fsha(out), "tiles": j["n_tiles"], "manifest_sha256": j["manifest_sha256"]}))
        return 0
    try:
        res = roundtrip() if a.cmd == "roundtrip" else sets_check(os.path.abspath(a.pool))
    except Exception as e:  # the predictor's Refused (anchor roles) or a stop: no reading, exit 2
        if type(e).__name__ != "Refused":
            raise
        print("REFUSED by the predictor: " + str(e))
        return 2
    txt = json.dumps(res, indent=1, sort_keys=True)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(txt + "\n")
    print(json.dumps({k: res[k] for k in res if k in ("PASS", "tiles_converted", "tiles_identical_in_every_field", "mismatches",
                                                      "predictor_roles_identical", "predictor_sets_identical", "manifest_picked",
                                                      "read", "differences")}, sort_keys=True))
    return 0 if res["PASS"] else 2


if __name__ == "__main__":
    sys.exit(main())
