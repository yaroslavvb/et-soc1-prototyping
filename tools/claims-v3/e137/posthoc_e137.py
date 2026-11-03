#!/usr/bin/env python3
"""E137: what the README quotes beyond scored.json. Standard library only. POST HOC: no rule of E137's depends on it, and nothing here decides a
verdict. Written before any E137 data was read (it runs on E128's committed reduction as a check of itself first).

    python3 tools/claims-v3/e137/posthoc_e137.py <data dir> > <data dir>/posthoc_e137.txt

A: every registered quantity on the board and on the minion rail (Drail, which the board meter's dips do not touch), per pass, in the reading the
   set-aside rule chose; and the same from E128's two passes beside it.
B: the lane bits behind each fp16 contrast (E128's desk counts, per op per minion) and board watts per differing lane C-read + result bit, post hoc
   (E128's posthoc_e128.py section C, same formula: W / ((C-read + result bits) x ops/s), ops/s the session's fp32.randn launch rate).
C: the sign term out of sample: M4's seven frozen fp16 sign contrasts against E128's two passes (before) and E137's passes (after): the error of
   each, the rms, and the interval half-width the data puts on it.
D: E137's watts against E128's on the same card and tiles: per tile D(E137) / D(E128).
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306}
REG = json.load(open(os.path.join(HERE, "predictions-e137.json")))
SPEC = json.load(open(os.path.join(ROOT, "tools/claims-v3/e128/e128/e128.json")))
E128 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-02-e128-fp16-signs/e128.json")))
Q = REG["quantities"]
SIGN = REG["rules"]["E137-R7"]["legs"]


def mci(v):
    v = [x for x in v if x is not None]
    if len(v) < 2:
        return (v[0] if v else None), None, len(v)
    return sum(v) / len(v), T975.get(len(v) - 1, 2.0) * statistics.stdev(v) / math.sqrt(len(v)), len(v)


def f(m, c, n, d=3):
    if m is None:
        return "—"
    return f"{m:.{d}f}" + ("" if c is None else f" ± {c:.{d}f}") + f" (n {n})"


def qval(name, row):
    q = Q[name]
    if q["form"] == "contrast":
        if any(t not in row for t in q["plus"] + q["minus"]):
            return None
        return sum(row[t] for t in q["plus"]) - sum(row[t] for t in q["minus"])
    a, b = qval(q["a"], row), qval(q["b"], row)
    if a is None or b is None:
        return None
    return (a / b if b else None) if q["form"] == "ratio" else a - b


def rows(red, passes, key="D"):
    return {p: {t: v[key] for t, v in red["per_pass"][p].items() if isinstance(v, dict) and v.get(key) is not None} for p in passes}


def main():
    ddir = sys.argv[1]
    P = json.load(open(os.path.join(ddir, "e137.json")))
    SC = json.load(open(os.path.join(ddir, "scored.json")))["primary"]
    passes = [str(p) for p in SC["passes"]]
    relaxed = json.load(open(os.path.join(ddir, "e137-relaxed.json"))) if os.path.exists(os.path.join(ddir, "e137-relaxed.json")) else P
    src = {p: (P if p in P["per_pass"] else relaxed) for p in passes}
    B = {p: rows(src[p], [p])[p] for p in passes}
    Rl = {p: rows(src[p], [p], "Drail")[p] for p in passes}
    B128 = rows(E128, sorted(E128["per_pass"]))
    R128 = rows(E128, sorted(E128["per_pass"]), "Drail")
    print(f"E137 post hoc. Reading {SC['reading']}, passes {passes}; E128's passes {sorted(B128)}")
    print("\nA. every registered quantity, board and rail, per pass (E137), and E128's two passes beside")
    for name in Q:
        b = [qval(name, B[p]) for p in passes]
        r = [qval(name, Rl[p]) for p in passes]
        b8 = [qval(name, B128[p]) for p in B128]
        pb = ", ".join("—" if x is None else f"{x:.3f}" for x in b)
        print(f"  {name:20s} board {f(*mci(b))}  rail {f(*mci(r))}  | E128 board {f(*mci(b8))}  M4 {Q[name].get('M', float('nan')):.3f}  per pass [{pb}]")
    rate = P["items"]["fp32.randn"]["rate"]["mean"]
    print(f"\nB. lane bits behind each fp16 contrast (E128's desk counts, per op per minion) and board watts per differing lane C-read + result bit; "
          f"ops/s {rate:.4g} (fp32.randn's launch rate)")
    for name in ("fp16.Bm_het", "fp16.Bm_walk", "fp16.Bm_rest", "fp16.Bz_het", "fp16.Bz_walk", "fp16.Bz_rest", "fp16.held_alt", "fp16.walk_alt"):
        q = Q[name]
        cnt = lambda n: SPEC["tiles"][n]["counts_real"]
        d = {k: sum(cnt(n)[k] for n in q["plus"]) - sum(cnt(n)[k] for n in q["minus"]) for k in ("alt1", "alt2", "cbus", "rbus", "store")}
        m, c, n = mci([qval(name, B[p]) for p in passes])
        bits = d["cbus"] + d["rbus"]
        fj = (m / (bits * rate) * 1e15) if bits and m is not None else float("nan")
        fjc = abs(c / (bits * rate) * 1e15) if bits and c is not None else float("nan")
        print(f"  {name:16s} {f(m, c, n)} W | alternations {d['alt1']:+.0f} {d['alt2']:+.0f} | lane C-read {d['cbus']:+.0f} result {d['rbus']:+.0f} "
              f"store {d['store']:+.0f} bits | {fj:.1f} ± {fjc:.1f} fJ per differing lane bit")
    print("\nC. the sign term out of sample: M4's seven frozen fp16 sign contrasts, error = measured - M4 (W)")
    for lab, src_rows in (("before (E128, 2 passes)", B128), ("after (E137)", B)):
        errs = []
        for name in SIGN:
            m, c, n = mci([qval(name, src_rows[p]) for p in src_rows])
            if m is None:
                continue
            errs.append(m - Q[name]["M"])
            print(f"  {lab:24s} {name:12s} measured {f(m, c, n)}  M4 {Q[name]['M']:.3f} ± {Q[name]['half95']:.2f}  error {m - Q[name]['M']:+.3f}")
        rms = math.sqrt(sum(e * e for e in errs) / len(errs)) if errs else float("nan")
        bias = sum(errs) / len(errs) if errs else float("nan")
        print(f"  {lab:24s} rms {rms:.3f} W, mean error {bias:+.3f} W over {len(errs)} contrasts")
    print("\nD. E137's watts against E128's on the same card and tiles: D(E137) / D(E128), item means")
    rat = []
    for t in sorted(REG["tiles"]):
        a = mci([B[p].get(t) for p in passes])[0]
        b = mci([B128[p].get(t) for p in B128])[0]
        if a and b:
            rat.append(a / b)
            print(f"  {t:14s} E137 {a:.3f}  E128 {b:.3f}  ratio {a / b:.4f}")
    if rat:
        print(f"  median ratio {statistics.median(rat):.4f}, range {min(rat):.4f}-{max(rat):.4f}, {len(rat)} items")


if __name__ == "__main__":
    main()
