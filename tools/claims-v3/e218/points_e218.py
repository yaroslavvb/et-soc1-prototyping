#!/usr/bin/env python3
"""E218 (Q230): the registered points and order of MM1-v3.2's BLIND MATMUL DAY on aifoundry3 card 0 at its pinned 600 MHz, one arm. Written
before any E218 datum. Standard library only.

    /usr/bin/python3 -I -B tools/claims-v3/e218/points_e218.py            reads desk/neverrun-e218.json, writes points-e218.json and points-e218.csv
    /usr/bin/python3 -I -B tools/claims-v3/e218/points_e218.py --check    rebuilds both and compares them with the files (exit 0 = PASS)

THE POINTS: MM1-v3.2's landed list (tools/matmul/mm1/v3.2/out/e218/points-e218.csv, landed 4e386f75, sha256 pinned below and checked first;
exit 4 if it differs), never re-chosen here: its 54 rows - family G 12 (rgm136 gemmLnc) with its 12 cooperative twins Gt, Y 16 (8 pairs of
equal-count masks), F 14 (the full chip, new sizes and formats) - by DECLARED-v32.md section 9's point rule as the land drew it. A point this
registration's never-run scan reads as run (desk/neverrun-e218.json, the literal reading) is DROPPED and said (the lane's brief: 'drop any point
that ran anywhere since, and say so'; E218.md departure D1); no point is added, none re-drawn.
THE TIE (E213's and E215's): t01 = E206's p001 (gemmL2x4x4 fp32 random, the full chip; E206 arm A, E207, E213 arm A and E215 arm A ran it on
this card: the bridge to earlier days; run and read, never in a rule).
THE SMOKE (one checked 2 s process each, never a point): s01 (gemmL2x2x2 fp32, rgm136's host and ELF: the session gate) at the opening; s03
(gemmLnc2x2x2 fp32, rgm211's host with rgm136's ELF: family G's own smoke and stop path) right before the G block (E215 arm A's form).
A CASE (time is kind-blind in every model) is a distinct (kernel loop, arm token, format, shire mask): every E218 point is its own case.
THE ORDER (DECLARED-v32.md section 9.5, applied to the points as registered): s01; t01; pass 1 = every Gt, Y and F point once, in Python's
random.Random("E218|A|pass1") shuffle of their sorted ids; t01; pass 2 = pass 1 reversed; t01; then THE G BLOCK, LAST: s03, the G points by
their planning peak PP ascending (ties by id), then the same reversed.
THE POINT FORM: E215's (points_e215.describe, imported at its pin: the host, ELF, mask geometry, tiles by sha256, the host's arguments).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
LANDED = ("tools/matmul/mm1/v3.2/out/e218/points-e218.csv", "1771826ee5a05327a2516b51345f9f0ef198c029b072e3d587e3d490cac54936")
LANDED_FC = ("tools/matmul/mm1/v3.2/out/e218/forecasts-e218.json", "1236dd9953b853a59293fc00377ff451b85756319cc80934c60208a7334d6209")
P215 = ("tools/claims-v3/e215/points_e215.py", "a8733593aaf91a3a38284ae4ce177983a8a4f57cc2f0363ceeb38b34a3f88f29")
E206_POINTS = ("tools/claims-v3/e206/points-e206.json", "121cada61673aabd7f2deaadbb37cb1164c772737cbe1085c6c9f3ff3ac77a1e")
NEVER = os.path.join(HERE, "desk", "neverrun-e218.json")
OUTJ = os.path.join(HERE, "points-e218.json")
OUTC = os.path.join(HERE, "points-e218.csv")
A3 = "aifoundry3 card 0"
LOOP = {"G": "rgm136 gemmLnc", "Gt": "rgm136 gemmL", "Y": "rgm136 gemmL", "F": "rgm136 gemmL"}


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def pinned(rel, want):
    got = sha_rel(rel)
    if got != want:
        print(f"points_e218: REFUSED, {rel} is {got}, pinned {want}")
        sys.exit(4)
    return os.path.join(REPO, rel)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def fnum(x):
    return None if x in ("", None) else float(x)


def build():
    P = load("points_e215_pinned", pinned(*P215))
    rows = list(csv.DictReader(open(pinned(*LANDED), newline="")))
    pinned(*LANDED_FC)
    nv = json.load(open(NEVER))
    if nv.get("points_sha256") != LANDED[1]:
        raise SystemExit("points_e218: desk/neverrun-e218.json was not made on the landed points file")
    ran = {v["id"]: v for v in nv["literal"]["points"] if not v["never_run"]}
    e206 = json.load(open(pinned(*E206_POINTS)))
    pts, dropped = [], []
    for r in rows:
        fam = r["family"]
        why = (f"MM1-v3.2's landed E218 {fam} point ({r['how']}{', regime ' + r['regime'] if r['regime'] else ''}"
               f"{', pair ' + r['pair'] if r['pair'] else ''}{', twin of ' + r['twin_of'] if r['twin_of'] else ''}); score {r['score'] or '-'}")
        extra = {"regime": r["regime"] or None, "how": r["how"], "pair": r["pair"] or None, "twin": r["twin"] or None,
                 "twin_of": r["twin_of"] or None, "score": fnum(r["score"]), "PP_W": fnum(r["PP"]), "PP_by": r["PP_by"],
                 "landed_row": {k: r[k] for k in ("id", "arm", "fmt", "mask", "MB", "NB", "KB", "ops_per_minion_per_gemm", "shires", "minions")}}
        p = P.describe(r["id"], "A", fam, "registered", r["arm"], r["fmt"], r["kind"], r["mask"], LOOP[fam], "point", why, A3, extra)
        if p["ops_per_minion_per_gemm"] != int(r["ops_per_minion_per_gemm"]) or p["minions"] != int(r["minions"]):
            raise SystemExit(f"points_e218: {r['id']} does not close against its landed row")
        if r["id"] in ran:
            v = ran[r["id"]]
            dropped.append({"id": r["id"], "family": fam, "token": r["arm"], "mask": r["mask"], "evidence": v["evidence"], "rule": v["rule"],
                            "why": ("DROPPED (the lane's brief: a point the registration's never-run scan reads as run is dropped and said; E218.md "
                                    "D1): the literal scan counts a hit in a folder naming no card; the files are desk copies of E219's "
                                    "registration inside a data lane folder, no run on aifoundry3 card 0 (section 4)")})
            continue
        pts.append(p)
    ids = {p["id"] for p in pts}
    for p in pts:
        if p.get("pair"):
            mates = [q["id"] for q in pts if q.get("pair") == p["pair"] and q["id"] != p["id"]]
            p["pair_mate"] = mates[0] if mates else None
            p["pair_complete"] = bool(mates)
        if p["family"] == "G":
            p["twin_registered"] = p.get("twin") in ids
    by = {p["id"]: p for p in pts}
    q = by.get
    smoke = [P.describe("s01", "A", "smoke", "smoke", "gemmL2x2x2", "fp32", "random", "0xffffffff", "rgm136 gemmL", "smoke",
                        "E213's and E215's s01: rgm136's host and ELF (the session gate)", A3),
             P.describe("s03", "A", "smoke", "smoke", "gemmLnc2x2x2", "fp32", "random", "0xffffffff", "rgm136 gemmLnc", "smoke",
                        "E213's and E215's s03: rgm211's host with rgm136's ELF (family G's own smoke and stop path), right before the G block", A3)]
    p001 = {p["id"]: p for p in e206["points"]}["p001"]
    tie = P.describe("t01", "A", "tie", "tie", p001["arm"], p001["format"], p001["kind"], p001["shire_mask"], "rgm136 gemmL", "tie",
                     "E206's p001: E206 arm A, E207, E213 arm A and E215 arm A ran it on this card (the bridge)", A3)
    rnd = random.Random("E218|A|pass1")
    p1 = sorted(p["id"] for p in pts if p["family"] in ("Gt", "Y", "F"))
    rnd.shuffle(p1)
    g = sorted((p for p in pts if p["family"] == "G"), key=lambda p: (p["PP_W"], p["id"]))
    gb = [p["id"] for p in g]
    seq = [("smoke", "s01"), ("tie", "t01")] + [("pass1", i) for i in p1] + [("tie", "t01")] + [("pass2", i) for i in reversed(p1)] + \
          [("tie", "t01"), ("G-smoke", "s03")] + [("G-pass1", i) for i in gb] + [("G-pass2", i) for i in reversed(gb)]
    if set(p1) | set(gb) != ids:
        raise SystemExit("points_e218: the order does not hold every point")
    pairs = {}
    for p in pts:
        if p.get("pair"):
            pairs.setdefault(p["pair"], []).append(p["id"])
    fams = {}
    for p in pts:
        fams[p["family"]] = fams.get(p["family"], 0) + 1
    out = {"experiment": "E218", "request": "Q230", "card": A3, "clock": "600 MHz, pinned (read, never set)",
           "what": "the registered points and order of MM1-v3.2's blind matmul day (frozen before any E218 datum)",
           "source": {"path": LANDED[0], "sha256": LANDED[1], "what": "MM1-v3.2's landed E218 list (54 rows), by DECLARED-v32.md section 9's rule"},
           "forecasts": {"path": LANDED_FC[0], "sha256": LANDED_FC[1]},
           "neverrun": {"path": "tools/claims-v3/e218/desk/neverrun-e218.json", "scan_sha256": nv["scan_sha256"], "scan_window": nv["scan_window"],
                        "lab_head": nv["lab_head"], "files_read": nv["files_read"]},
           "n_points": len(pts), "n_cases": len(pts), "families": dict(sorted(fams.items())), "dropped_ran_since": dropped,
           "pairs": {k: sorted(v) for k, v in sorted(pairs.items())},
           "pairs_complete": sorted(k for k, v in pairs.items() if len(v) == 2),
           "twins": {p["id"]: p["twin"] for p in g}, "twins_registered": sorted(p["id"] for p in g if p.get("twin_registered")),
           "points": pts, "smoke": smoke, "tie": tie,
           "order": {"seed": "E218|A|pass1", "pass1": p1, "pass2": list(reversed(p1)), "G_block": gb + list(reversed(gb)),
                     "sequence_blocks": seq, "runs": 2 * len(p1) + 2 * len(gb) + 3, "smoke_processes": 2}}
    js = json.dumps(out, indent=1, sort_keys=True) + "\n"
    cols = ["id", "family", "regime", "how", "pair", "pair_mate", "twin", "twin_of", "loop", "host", "elf", "arm", "format", "kind", "shire_mask",
            "shires", "minions", "M", "N", "K", "M_computed", "N_computed", "ops_per_minion_per_gemm", "macs_per_gemm", "case", "PP_W", "values"]
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(cols)
    for p in pts + [tie] + smoke:
        w.writerow(["" if p.get(c) is None else (repr(p[c]) if isinstance(p.get(c), float) else p[c]) for c in cols])
    return js, buf.getvalue(), out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    js, cs, out = build()
    if a.check:
        ok = open(OUTJ).read() == js and open(OUTC).read() == cs
        print(f"points_e218 --check: {'PASS' if ok else 'FAIL'} ({out['n_points']} points)")
        sys.exit(0 if ok else 1)
    open(OUTJ, "w").write(js)
    open(OUTC, "w").write(cs)
    print(f"points_e218: {out['n_points']} points {out['families']}, dropped {[d['id'] for d in out['dropped_ran_since']]}, "
          f"pairs complete {len(out['pairs_complete'])} of {len(out['pairs'])}, twins registered {len(out['twins_registered'])} of 12, "
          f"runs {out['order']['runs']}; points-e218.json {hashlib.sha256(js.encode()).hexdigest()}")


if __name__ == "__main__":
    main()
