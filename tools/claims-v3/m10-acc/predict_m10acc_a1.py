#!/usr/bin/env python3
"""Q153(m10acc), dated amendment A1: M10-ACC-L's frozen term for any tile, from m10acc-a1.json and acctrace_m10acc_a1.c alone.

    python3 -B predict_m10acc_a1.py term --type int8 --a-word 0x05050505 --b-word 0x04040404 [--n N] [--rate R] [--card a3|c1] [--s S]
    python3 -B predict_m10acc_a1.py term --type fp32 --tile <tile.bin> [...]
    python3 -B predict_m10acc_a1.py selftest    # the term on committed rows (b, d) equals rows-m10acc-a1.json's; one-number traces
                                                # equal features-m10acc-a1.json's

The term, in W, added to M10's D: s x c x rate x (tau_L x x_lane + tau_bth x x_bth), c = M10's card-1 scale on card 1. Defaults as
predict_m10acc.py's (E178's launch size and median measured rate for the type, card a3, s = 1). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import predict_m10acc as P  # noqa: E402  (one_number and term_w only, unchanged)

OUT = P.OUT


def build(d, cc="cc"):
    exe = os.path.join(d, "acctrace_m10acc_a1")
    subprocess.run([cc, "-O2", "-std=gnu11", "-ffp-contract=off", f'-DACCUM_C="{P.ACCUM}"', "-o", exe,
                    os.path.join(HERE, "acctrace_m10acc_a1.c"), "-lm"], check=True)
    return exe


def trace(exe, t, raw, ns, d):
    p = os.path.join(d, hashlib.sha256(raw).hexdigest() + ".bin")
    open(p, "wb").write(raw)
    return json.loads(subprocess.run([exe, t, p, ",".join(str(n) for n in sorted(ns))], check=True, capture_output=True, text=True).stdout)


def cmd_term(a):
    m = json.load(open(os.path.join(OUT, "m10acc-a1.json")))
    fe = json.load(open(os.path.join(OUT, "forecasts-e182-m10acc-a1.json")))
    n = a.n or m["N_e178"][a.type]
    rate = a.rate or fe["rate"][a.type]
    raw = open(a.tile, "rb").read() if a.tile else P.one_number(a.a_word, a.b_word)
    if len(raw) != 2048:
        raise SystemExit("a tile is 2,048 bytes")
    with tempfile.TemporaryDirectory() as d:
        o = trace(build(d), a.type, raw, [n], d)
    xl, xb = o["x"][str(n)]["x_lane"], o["x_bth_per_op"]
    w, ends, entered = P.term_w(m, a.type, xl, xb, rate, a.card, a.s)
    print(json.dumps({"type": a.type, "N": n, "rate": rate, "card": a.card, "s": a.s, "x_lane_per_op": xl, "x_lane_per_uop": xl / m["uops_per_op"][a.type],
                      "x_acc_register_per_op": o["x"][str(n)]["x_acc"], "x_bth_per_op": xb, "term_w": w, "term_w_95": ends,
                      "family_entered_M10": entered}, indent=1))


def cmd_selftest(a):
    m = json.load(open(os.path.join(OUT, "m10acc-a1.json")))
    F = json.load(open(os.path.join(OUT, "features-m10acc-a1.json")))
    rows = json.load(open(os.path.join(OUT, "rows-m10acc-a1.json")))["rows"]
    worst, n = 0.0, 0
    for r in rows:
        if r["src"] not in ("b", "d"):
            continue
        f = m["families"]["int8" if r["type"] == "int8" else "float"]
        want = sum(z * f["tau_J"][q] for z, q in zip(r["z"], ["acc", "bth"][:len(r["z"])]))
        got, _, _ = P.term_w(m, r["type"], r["x_acc"], r["x_bth"], r["rate"], r["card"], r["s"])
        worst = max(worst, abs(got - want))
        n += 1
    if worst > 1e-12:
        raise SystemExit(f"SELFTEST FAIL: term differs by {worst}")
    k = 0
    with tempfile.TemporaryDirectory() as d:
        exe = build(d)
        for g in F["grid_e182"][:: max(1, len(F["grid_e182"]) // 12)]:
            nn = m["N_e178"][g["type"]]
            o = trace(exe, g["type"], P.one_number(g["a_word"], g["b_word"]), [nn], d)
            if abs(o["x"][str(nn)]["x_lane"] - F["tiles"][g["sha"]]["x_acc"][str(nn)]["total"]) > 1e-9:
                raise SystemExit(f"SELFTEST FAIL: trace differs for {g}")
            k += 1
    print(f"SELFTEST PASS (A1): the term on {n} committed rows (b, d) within {worst:.1e} W; {k} one-number traces equal the committed features")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("term", "selftest"))
    ap.add_argument("--type", choices=("fp32", "fp16", "int8"))
    ap.add_argument("--a-word")
    ap.add_argument("--b-word")
    ap.add_argument("--tile")
    ap.add_argument("--n", type=int)
    ap.add_argument("--rate", type=float)
    ap.add_argument("--card", default="a3", choices=("a3", "c1"))
    ap.add_argument("--s", type=float, default=1.0)
    a = ap.parse_args()
    if a.cmd == "term" and not (a.type and (a.tile or (a.a_word and a.b_word))):
        raise SystemExit("term needs --type and --tile or --a-word and --b-word")
    {"term": cmd_term, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    main()
