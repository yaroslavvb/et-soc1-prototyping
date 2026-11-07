#!/usr/bin/env python3
"""Q153(m10acc): M10-ACC's frozen term for any tile, from m10acc.json and the trace program alone (REGISTRATION.md section 6).

    python3 -B predict_m10acc.py term --type int8 --a-word 0x05050505 --b-word 0x04040404 [--n N] [--rate R] [--card a3|c1] [--s S]
    python3 -B predict_m10acc.py term --type fp32 --tile <tile.bin> [...]
    python3 -B predict_m10acc.py selftest        # the term on committed rows equals rows-m10acc.json's, and one-number traces
                                                 # equal features-m10acc.json's

The term, in W, added to M10's D for the same tile, session and card: s x c x rate x (tau_acc x x_acc + tau_bth x x_bth), with
c = M10's card-1 scale on card 1. Defaults: N = E178's launch size for the type (m10acc.json N_e178), rate = E178's median
measured rate for the type (forecasts-e178 file), card a3, s = 1. It prints the term with the 95% interval from tau_acc's
jackknife interval (x_bth's price held at its value), and whether the family's term entered M10 by the rule (R1-R3).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "docs", "reports", "data", "2026-11-07-q153-m10acc")
ACCUM = os.path.join(ROOT, "rtl-sim", "fma_toggle_v2", "accum.c")
fam_of = lambda t: "int8" if t == "int8" else "float"  # noqa: E731


def build(d, cc="cc"):
    exe = os.path.join(d, "acctrace_m10acc")
    subprocess.run([cc, "-O2", "-std=gnu11", "-ffp-contract=off", f'-DACCUM_C="{ACCUM}"', "-o", exe,
                    os.path.join(HERE, "acctrace_m10acc.c"), "-lm"], check=True)
    return exe


def trace(exe, t, raw, ns, d):
    p = os.path.join(d, hashlib.sha256(raw).hexdigest() + ".bin")
    open(p, "wb").write(raw)
    o = subprocess.run([exe, t, p, ",".join(str(n) for n in sorted(ns))], check=True, capture_output=True, text=True).stdout
    return json.loads(o)


def one_number(aw, bw):
    return struct.pack("<512I", *([int(aw, 16)] * 256 + [int(bw, 16)] * 256))


def term_w(m, t, x_acc, x_bth, rate, card, s):
    fam = fam_of(t)
    f = m["families"][fam]
    c = m["card1_scale"][fam] if card == "c1" else 1.0
    ta, tb = f["tau_J"]["acc"], f["tau_J"].get("bth", 0.0)
    lo, hi = f["jackknife_95_J"]["acc"]
    k = s * c * rate
    w = k * (ta * x_acc + tb * x_bth)
    ends = sorted([k * (lo * x_acc + tb * x_bth), k * (hi * x_acc + tb * x_bth)])
    return w, ends, f["enters"]


def cmd_term(a):
    m = json.load(open(os.path.join(OUT, "m10acc.json")))
    fe = json.load(open(os.path.join(OUT, "forecasts-e182-m10acc.json")))
    n = a.n or m["N_e178"][a.type]
    rate = a.rate or fe["rate"][a.type]
    raw = open(a.tile, "rb").read() if a.tile else one_number(a.a_word, a.b_word)
    if len(raw) != 2048:
        raise SystemExit("a tile is 2,048 bytes")
    with tempfile.TemporaryDirectory() as d:
        o = trace(build(d), a.type, raw, [n], d)
    xa, xb = o["x_acc"][str(n)]["total"], o["x_bth_per_op"]
    w, ends, entered = term_w(m, a.type, xa, xb, rate, a.card, a.s)
    print(json.dumps({"type": a.type, "N": n, "rate": rate, "card": a.card, "s": a.s, "x_acc_per_op": xa, "x_acc_per_uop": xa / m["uops_per_op"][a.type],
                      "x_bth_per_op": xb, "term_w": w, "term_w_95": ends, "family_entered_M10": entered}, indent=1))


def cmd_selftest(a):
    m = json.load(open(os.path.join(OUT, "m10acc.json")))
    F = json.load(open(os.path.join(OUT, "features-m10acc.json")))
    rows = json.load(open(os.path.join(OUT, "rows-m10acc.json")))
    worst, n = 0.0, 0
    for r in rows:
        if r["src"] not in ("b", "d"):
            continue
        fam = fam_of(r["type"])
        f = m["families"][fam]
        want = sum(z * f["tau_J"][q] for z, q in zip(r["z"], ["acc", "bth"][:len(r["z"])]))
        c = m["card1_scale"][fam] if r["card"] == "c1" else 1.0
        got, _, _ = term_w(m, r["type"], r["x_acc"], r["x_bth"], r["rate"], r["card"], r["s"])
        if abs(c - r["c"]) > 1e-12:
            raise SystemExit(f"card term differs for {r['key']}")
        worst = max(worst, abs(got - want))
        n += 1
    if worst > 1e-12:
        raise SystemExit(f"SELFTEST FAIL: term differs by {worst}")
    k = 0
    with tempfile.TemporaryDirectory() as d:
        exe = build(d)
        for g in F["grid_e182"][:: max(1, len(F["grid_e182"]) // 12)]:
            nn = m["N_e178"][g["type"]]
            o = trace(exe, g["type"], one_number(g["a_word"], g["b_word"]), [nn], d)
            want = F["tiles"][g["sha"]]["x_acc"][str(nn)]["total"]
            if abs(o["x_acc"][str(nn)]["total"] - want) > 1e-9:
                raise SystemExit(f"SELFTEST FAIL: trace differs for {g}")
            k += 1
    print(f"SELFTEST PASS: the term on {n} committed rows (b, d) within {worst:.1e} W; {k} one-number traces equal the committed features")


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
