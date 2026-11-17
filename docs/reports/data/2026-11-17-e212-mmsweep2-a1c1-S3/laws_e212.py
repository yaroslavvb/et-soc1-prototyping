#!/usr/bin/env python3
"""data-e212 (Q208, Tue 17 Nov 2026): the lab's law test of one E212 (1117-mmsweep2) session's tiles against E210's nine fp32
operand patterns, as E210.md section 3 states them bit for bit (written while E210's patterns were private; published only with
sessions committed after E210's registration reached GitHub main). Reads only; Python's own modules.

    /usr/bin/python3 -I -B laws_e212.py <session dir> <src dir> <E210 tiles dir> --out l.json --txt l.txt

For every fp32 plan tile the session's runs and smoke name (a tile file of the 2,048-byte layout the host reads: A[i][k] = word
16 i + k, B[k][j] = word 256 + 16 k + j), and for every E210 tile file as a self-test (each must obey its own folder's law):
  LAW, with the variety its random part implies:  negzero every word 0x80000000; signs every word 0x3F800000 or 0xBF800000, both
  present; lowmant8 0x3F800000 OR random bits 0-7 (more than two values of the field); highmant8 the same in bits 15-22; bhalfeq
  B[k][l+8] = B[k][l] with A and B drawn (over 16 distinct words each); badjeq B[k][2m+1] = B[k][2m] the same; hd4 each next A row 4
  mantissa bits from the row above and B[k][l+8] 4 mantissa bits from B[k][l]; maxalte A rows alternating by xor 0x83FFFFFF and
  B[k][l+8] = B[k][l] xor 0x83FFFFFF; arow50 A's odd rows +0.0 and every other word nonzero.
  SUPPORT (reported, a looser look): every word inside a law's value set, the variety not required (so a constant field counts).
The copied kinds tiles are E210's controls, never its patterns, and are not tested; fp16 and int8 tiles are outside E210's nine.
"""
import argparse
import collections
import json
import os
import struct
import sys

KINDS = {"src/tiles/fp32/randn.bin", "src/tiles/fp32/zeros.bin", "src/tiles/fp32/ones.bin",
         "src/tiles/fp16/randn.bin", "src/tiles/fp16/zeros.bin", "src/tiles/fp16/ones.bin",
         "src/tiles/int8/full.bin", "src/tiles/int8/zeros.bin", "src/tiles/int8/ones.bin"}
MANT = 0x007FFFFF
F = 0x83FFFFFF


def tiles_of(values):
    if not values:
        return []
    p = values.split(":")
    return p[2].split(",") if len(p) >= 3 else []


def test(b):
    w = list(struct.unpack("<512I", b[:2048]))
    A = [w[16 * i:16 * i + 16] for i in range(16)]
    B = [w[256 + 16 * k:256 + 16 * k + 16] for k in range(16)]
    s = set(w)
    law, sup = [], []
    if s == {0x80000000}:
        law.append("negzero")
    if s <= {0x3F800000, 0xBF800000}:
        sup.append("signs")
        if s == {0x3F800000, 0xBF800000}:
            law.append("signs")
    if all((x & ~0xFF) == 0x3F800000 for x in w):
        sup.append("lowmant8")
        if len({x & 0xFF for x in w}) > 2:
            law.append("lowmant8")
    if all((x & ~(0xFF << 15)) == 0x3F800000 for x in w):
        sup.append("highmant8")
        if len({(x >> 15) & 0xFF for x in w}) > 2:
            law.append("highmant8")
    a_var = len({x for r in A for x in r}) > 16
    b_var = len({x for r in B for x in r}) > 16
    if all(B[k][l + 8] == B[k][l] for k in range(16) for l in range(8)):
        sup.append("bhalfeq")
        if a_var and b_var:
            law.append("bhalfeq")
    if all(B[k][2 * m + 1] == B[k][2 * m] for k in range(16) for m in range(8)):
        sup.append("badjeq")
        if a_var and b_var:
            law.append("badjeq")
    if all(bin(A[i + 1][k] ^ A[i][k]).count("1") == 4 and not ((A[i + 1][k] ^ A[i][k]) & ~MANT) for i in range(15) for k in range(16)) \
            and all(bin(B[k][l + 8] ^ B[k][l]).count("1") == 4 and not ((B[k][l + 8] ^ B[k][l]) & ~MANT) for k in range(16) for l in range(8)):
        law.append("hd4")
    if all(A[i + 1][k] == A[i][k] ^ F for i in range(15) for k in range(16)) and all(B[k][l + 8] == B[k][l] ^ F for k in range(16) for l in range(8)):
        law.append("maxalte")
    if all(x == 0 for i in range(1, 16, 2) for x in A[i]) and all(x != 0 for i in range(0, 16, 2) for x in A[i]) and all(x != 0 for r in B for x in r):
        law.append("arow50")
    return law, sup


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("src")
    ap.add_argument("e210")
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt", required=True)
    a = ap.parse_args(argv)
    top = os.path.dirname(os.path.normpath(a.src))
    selftest = {}
    for d in sorted(os.listdir(os.path.join(a.e210, "fp32"))):
        c = collections.Counter()
        for f in sorted(os.listdir(os.path.join(a.e210, "fp32", d))):
            c[",".join(test(open(os.path.join(a.e210, "fp32", d, f), "rb").read())[0]) or "none"] += 1
        selftest[d] = dict(c)
    self_ok = all(list(v) == [k] for k, v in selftest.items())
    q = json.load(open(os.path.join(a.session, "queue.json")))
    sched = json.load(open(os.path.join(a.src, "sched", q["sched"])))
    used = collections.defaultdict(list)
    for k in sorted(os.listdir(os.path.join(a.session, "runs"))):
        r = json.load(open(os.path.join(a.session, "runs", k, "run.json")))
        for t in tiles_of((r.get("sched") or {}).get("values")):
            used[t].append(k)
    for s_ in sched.get("smoke") or []:
        for t in tiles_of(s_.get("values")):
            used[t].append("smoke " + s_.get("arm", "?"))
    tested = {}
    for t in sorted(used):
        if t in KINDS or "/fp32/" not in t:
            continue
        law, sup = test(open(os.path.join(top, t), "rb").read())
        tested[t] = {"runs": used[t], "laws": law, "support": sup}
    hits = {t: v for t, v in tested.items() if v["laws"]}
    sups = {t: v for t, v in tested.items() if v["support"] and not v["laws"]}
    L = [f"E210 self-test (each folder's files against the nine laws): {selftest} -> {'PASS' if self_ok else 'FAIL'}",
         f"fp32 plan tiles the session ran: {len(tested)}; obeying one of E210's laws: "
         + ("; ".join(f"{t} = {','.join(v['laws'])} (runs {', '.join(v['runs'])})" for t, v in hits.items()) or "none"),
         "inside a law's value support only (not the law): "
         + ("; ".join(f"{t} in {','.join(v['support'])} (runs {', '.join(v['runs'])})" for t, v in sups.items()) or "none")]
    out = {"what": "data-e212's law test of one E212 session's tiles against E210's nine fp32 patterns (reads only)",
           "session": os.path.basename(os.path.normpath(a.session)), "schedule": q["sched"], "selftest": selftest,
           "selftest_pass": self_ok, "tested": tested, "law_hits": sorted(hits), "support_only": sorted(sups),
           "python": sys.version.split()[0], "interpreter": sys.executable}
    json.dump(out, open(a.out, "w"), indent=1)
    open(a.txt, "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0 if self_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
