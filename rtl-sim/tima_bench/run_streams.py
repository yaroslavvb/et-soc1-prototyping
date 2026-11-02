#!/usr/bin/env python3
"""Q136(c): every stream of E109's and E124's design through the TIMA bench (build.sh), per TensorFMA op on one minion.

    python3 rtl-sim/tima_bench/run_streams.py --bin <scratch>/obj_q136c/Vtb --out counts.json [--jobs 6]       # from the repo root

A stream is one item of the design: a tile, a shape (A rows, K), a row mask, and how the run before it left the TIMA controls. Three sets:
  design     E109's twelve items and the six anchors and pi it ran beside them (E124 ran the same design unchanged on another card), each at
             the card's own cycles per op as the bench's period (E109 R6: the bench's cycles + 7.75, which the cards matched to 0.001), so
             a window holds the core's loop too and a count an op times the card's measured op rate is a count a second
  check      E109's committed desk arms (tools/claims-v3/e109/desk/bench-arms.json): the same streams at the FSM's own pace (+period=1) and
             the two zeros at the card's period, to be compared field by field with what E109's lean build counted
  context    the fp32 arms run after two int8 ops (+pre=2), as on the card, where an fp32 run follows int8 runs and the TIMA controls,
             clocked only while int8 works (vpu_tensorfma.v:841), keep the values the last int8 op left them
  arms       desk-only shapes that move one int8 candidate (not run on any card): K = 1 with first_pass on every op against K = 1 without
             (TenC's read enable low or high, nothing else changed), one A row (TenC read at one address), eight A rows, all with no issue
Each run: one warm op (first_pass), then 4 measured ops (E109's bench_arms_e109.py: +warm=1 +ops=4 +first=1). C starts at 0.
Standard library only. SPDX-License-Identifier: Apache-2.0"""
import argparse
import hashlib
import json
import os
import struct
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
KINDS = os.path.join(ROOT, "tools", "claims-v3", "kinds")
E109_ARMS = os.path.join(ROOT, "tools", "claims-v3", "e109", "desk", "bench-arms.json")

TILE = {("fp32", "zeros"): "tiles/fp32/zeros.bin", ("int8", "zeros"): "tiles/int8/zeros.bin", ("fp16", "zeros"): "tiles/fp16/zeros.bin",
        ("fp32", "a_zeros_b_randn"): "tiles/fp32/a_zeros_b_randn.bin", ("fp32", "a_nz_b_randn"): "e93/tiles/fp32/a_nz_b_randn.bin",
        ("fp32", "pi"): "tiles/fp32/pi.bin", ("fp32", "randn"): "tiles/fp32/randn.bin", ("fp16", "randn"): "tiles/fp16/randn.bin",
        ("int8", "full"): "tiles/int8/full.bin"}
# arm -> (A rows, K, row mask or None); E109's ARMS (e109_common.py) plus the desk-only shapes
SHAPE = {"base": (16, 16, None), "m0": (16, 16, 0x0000), "k8": (16, 8, None), "r8": (8, 16, None), "m0k8": (16, 8, 0x0000),
         "m0r8": (8, 16, 0x0000), "m0r1": (1, 16, 0x0000), "m0k1": (16, 1, 0x0000)}
# the cards' cycles per op (E109 and E124, every arm within 0.001 of these; R6), used as the bench's period
CARD_CPO = {("fp32", "base"): 546, ("fp32", "m0"): 544, ("fp32", "k8"): 282, ("fp32", "r8"): 290, ("fp32", "m0k8"): 280,
            ("int8", "base"): 318, ("int8", "m0"): 318, ("int8", "k8"): 166, ("int8", "r8"): 190, ("int8", "m0k8"): 166,
            ("fp16", "base"): 546}
DELTA = 7.75   # E109's fitted core-loop cycles: the card's cycles per op = the bench's + 7.75 (R6); used only for desk-only arms


def stream_list():
    S = []
    def add(set_, name, fmt, kind, arm, period, pre=0, firstall=0):
        rows, cols, mask = SHAPE[arm]
        S.append({"set": set_, "name": name, "fmt": fmt, "kind": kind, "arm": arm, "rows": rows, "cols": cols, "mask": mask,
                  "period": period, "pre": pre, "firstall": firstall, "tile": TILE[(fmt, kind)]})
    # design: E109's and E124's items, at the card's cycles per op
    for fmt in ("fp32", "int8"):
        for arm in ("base", "m0", "k8", "r8", "m0k8"):
            add("design", f"{fmt}.zeros" if arm == "base" else f"{arm}.{fmt}.zeros", fmt, "zeros", arm, CARD_CPO[(fmt, arm)])
    for kind in ("a_zeros_b_randn", "a_nz_b_randn"):
        add("design", f"fp32.{kind}", "fp32", kind, "base", 546)
        add("design", f"m0.fp32.{kind}", "fp32", kind, "m0", 544)
    add("design", "anchor_pi", "fp32", "pi", "base", 546)
    add("design", "fp32.randn", "fp32", "randn", "base", 546)
    add("design", "fp16.zeros", "fp16", "zeros", "base", 546)
    add("design", "fp16.randn", "fp16", "randn", "base", 546)
    add("design", "int8.full", "int8", "full", "base", 318)
    # check: E109's committed desk arms, at the FSM's pace, and the two zeros at the card's period
    for fmt, kind, arms in (("fp32", "zeros", ("base", "m0", "k8", "r8", "m0k8")), ("int8", "zeros", ("base", "m0", "k8", "r8", "m0k8")),
                            ("fp32", "a_zeros_b_randn", ("base", "m0")), ("fp32", "a_nz_b_randn", ("base", "m0")),
                            ("fp32", "pi", ("base", "m0")), ("fp32", "randn", ("base", "m0"))):
        for arm in arms:
            add("check", f"{arm}.{fmt}.{kind}", fmt, kind, arm, 1)
    add("check", "card_period:fp32.zeros", "fp32", "zeros", "base", 546)
    add("check", "card_period:int8.zeros", "int8", "zeros", "base", 318)
    # context: fp32 after an int8 run (two int8 ops, the first with first_pass, then the stream)
    for arm in ("base", "m0", "k8", "r8", "m0k8"):
        add("context", "pre.fp32.zeros" if arm == "base" else f"pre.{arm}.fp32.zeros", "fp32", "zeros", arm, CARD_CPO[("fp32", arm)], pre=2)
    add("context", "pre.m0.fp32.a_zeros_b_randn", "fp32", "a_zeros_b_randn", "m0", 544, pre=2)
    add("context", "pre.anchor_pi", "fp32", "pi", "base", 546, pre=2)
    # and the desk-only fp32 arms' partners in the card's order (period filled in by main(), as for set "arms")
    for name, arm in (("pre.m0r1.fp32.zeros", "m0r1"), ("pre.m0k1.fp32.zeros", "m0k1"), ("pre.m0r8.fp32.zeros", "m0r8")):
        add("context_arms", name, "fp32", "zeros", arm, None, pre=2)
    # arms: desk-only shapes (no card has run them). Each runs first at the FSM's own pace (+period=1, set "arms_pace"), then at the
    # card's predicted cycles per op, round(bench + 7.75) (set "arms", period filled in by main()), so a count an op times the predicted
    # op rate is a count a second, as for the design's streams
    # first_pass is cleared when the FSM moves to the next A column (vpu_tensorfma.v:726), so first_pass on every op keeps TenC's read
    # enable low for a whole op only when the op has one A column (K = 1): m0k1 against f1.m0k1 differ in that enable and nothing else
    for name, arm, fa in (("m0k1.int8.zeros", "m0k1", 0), ("f1.m0k1.int8.zeros", "m0k1", 1), ("m0k1.fp32.zeros", "m0k1", 0),
                          ("m0r1.int8.zeros", "m0r1", 0), ("m0r1.fp32.zeros", "m0r1", 0), ("m0r8.int8.zeros", "m0r8", 0),
                          ("m0r8.fp32.zeros", "m0r8", 0), ("f1.m0.int8.zeros", "m0", 1)):
        fmt = "fp32" if "fp32" in name else "int8"
        add("arms_pace", name, fmt, "zeros", arm, 1, firstall=fa)
        add("arms", name, fmt, "zeros", arm, None, firstall=fa)
    return S


def run(binary, st, ops=4, warm=1):
    raw = open(os.path.join(KINDS, st["tile"]), "rb").read()
    assert len(raw) == 2048, (st["tile"], len(raw))
    words = list(struct.unpack("<512I", raw)) + [0] * 256
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "t.hex")
        open(h, "w").write("\n".join(f"{w:08x}" for w in words) + "\n")
        args = [binary, f"+tiles={h}", f"+fmt={st['fmt']}", f"+warm={warm}", f"+ops={ops}", "+first=1", f"+period={st['period']}",
                f"+rows={st['rows']}", f"+cols={st['cols']}", f"+pre={st['pre']}", f"+firstall={st['firstall']}"]
        if st["mask"] is not None:
            args.append(f"+mask={st['mask']:x}")
        out = subprocess.run(["nice", "-n", "10"] + args, capture_output=True, text=True, check=True).stdout
    acct = unit = x = arr = line = None
    for l in out.splitlines():
        if l.startswith("ACCT "): acct = json.loads(l[5:])
        elif l.startswith("ACCTU "): unit = [int(v) for v in l.split()[1:]]
        elif l.startswith("ACCTX "): x = json.loads(l[6:])
        elif l.startswith("ACCTARR "): arr = json.loads(l[8:])
        elif l.startswith("ACCTLINE "): line = json.loads(l[9:])
    assert acct and unit and x and arr is not None and line is not None, out[-2000:]
    n = acct["ops"]
    r = {k: acct[k] / n for k in ("cycles", "busy", "uops", "txfma_valid", "tima_valid", "scp_reads", "ff_clocked_bits", "ff_toggles", "ff_present_bits")}
    for i, u in enumerate(("txfma", "tima", "rest")):
        r[f"{u}_clocked"], r[f"{u}_toggles"], r[f"{u}_present"] = unit[3 * i] / n, unit[3 * i + 1] / n, unit[3 * i + 2] / n
    r["x"] = {k: v / n for k, v in x.items() if k not in ("pre", "firstall")}
    r["arrays"] = {c: {k: (v / n if k not in ("instances", "width", "entries") else v) for k, v in a.items()} for c, a in arr.items()}
    r["lines"] = {k: [v[0], v[1] / n, v[2] / n, v[3] / n] for k, v in line.items()}     # width, clocked, toggles, present (an op)
    r["ops_measured"] = n
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    S = stream_list()
    if a.only:
        keep = set(a.only.split(","))
        S = [s for s in S if s["name"] in keep or s["set"] in keep]
    first = [s for s in S if s["period"] is not None]
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        res1 = list(ex.map(lambda s: run(a.bin, s), first))
    pace = {s["name"]: r["cycles"] for s, r in zip(first, res1) if s["set"] == "arms_pace"}
    later = [s for s in S if s["period"] is None]
    for s in later:
        base = s["name"][4:] if s["name"].startswith("pre.") else s["name"]
        s["period"] = int(round(pace[base] + DELTA))
        s["period_rule"] = f"round({pace[base]:.2f} + {DELTA}): the bench's cycles at its own pace ({base}) plus E109's fitted core loop (R6)"
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        res2 = list(ex.map(lambda s: run(a.bin, s), later))
    S = first + later
    res = res1 + res2
    out = {"what": "Q136(c): per TensorFMA op on one minion, every stream of E109's/E124's design through the TIMA bench (rtl-sim/tima_bench)",
           "binary_sha256": hashlib.sha256(open(a.bin, "rb").read()).hexdigest(), "streams": []}
    for s, r in zip(S, res):
        out["streams"].append({**s, "per_op": r})
    # the check against E109's committed desk arms: every field of its lean build, exactly
    ref = json.load(open(E109_ARMS))
    fields = ("cycles", "busy", "uops", "txfma_valid", "tima_valid", "scp_reads", "ff_clocked_bits", "ff_toggles", "ff_present_bits",
              "txfma_clocked", "txfma_toggles", "txfma_present", "tima_clocked", "tima_toggles", "tima_present", "rest_clocked", "rest_toggles", "rest_present")
    chk = {"compared": 0, "fields": 0, "differ": []}
    for st in out["streams"]:
        if st["set"] != "check":
            continue
        if st["name"].startswith("card_period:"):
            rr = ref["card_period"].get(st["name"].split(":", 1)[1])
        else:
            rr = ref["per_op"].get(st["name"])
        if rr is None:
            continue
        chk["compared"] += 1
        for f in fields:
            chk["fields"] += 1
            if abs(rr[f] - st["per_op"][f]) > 1e-9:
                chk["differ"].append({"stream": st["name"], "field": f, "e109": rr[f], "here": st["per_op"][f]})
    out["check_against_e109_bench_arms"] = chk
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"{len(S)} streams; against E109's bench-arms.json: {chk['compared']} streams, {chk['fields']} fields, {len(chk['differ'])} differ")
    for dd in chk["differ"][:20]:
        print("  DIFFER", dd)


if __name__ == "__main__":
    main()
