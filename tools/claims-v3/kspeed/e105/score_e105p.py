#!/usr/bin/env python3
"""E105 amendment A1: scores the power arm's rules P1-P5 (predictions-e105-a1.json) on the two reductions of E101 session 1's own reducer, and prints the frozen clocks against the measured ones (predictions-e105.json, labelled, no rule). Standard library only.

    python3 score_e105p.py <data dir> > scored-p.txt     # the data dir holds e105c.json, e105v.json, results-speed.json; writes scored-p.json there

The gemm1 and gemm16 items in e105c.json ran gemmc1 and gemmc16; in e105v.json, gemmv1 and gemmv16. E101's benchmark and as-run numbers come from E101's own e101.json.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = sys.argv[1]
REG = json.load(open(os.path.join(HERE, "predictions-e105-a1.json")))
PRED = json.load(open(os.path.join(HERE, "predictions-e105.json")))
C = json.load(open(f"{D}/e105c.json"))
V = json.load(open(f"{D}/e105v.json"))
E101 = json.load(open(f"{D}/../2026-11-01-e101-real-matmul/e101.json"))["items"]
SPEED = json.load(open(f"{D}/results-speed.json"))
RULES = REG["rules"]
TOP = {"fp32": "randn", "fp16": "randn", "int8": "full"}
B800, S800 = PRED["relation"]["B"]["800"], PRED["relation"]["s800"]
CZ, XFER = {"fp32": 1.44, "fp16": 1.394, "int8": 2.123}, 1.01865


def rate(x):
    return x["rate"]["mean"] * x["macs_per_op"] * 2 / 1e12


def S(d, name):
    return d["items"][name]["S"]


out = {"experiment": "E105", "amendment": "A1", "passes": {"e105c": {"kept": C["passes"], "set_aside": C.get("passes_set_aside")}, "e105v": {"kept": V["passes"], "set_aside": V.get("passes_set_aside")}}, "rules": {}}
print(f"e105c (gemmc): passes {C['passes']}, set aside {C.get('passes_set_aside')}, runs {C['runs']}, kept {C['kept']}, clock {C.get('clock_mhz')}, leak {C['leak']['k_w_per_c']:.3f} W/C")
print(f"e105v (gemmv): passes {V['passes']}, set aside {V.get('passes_set_aside')}, runs {V['runs']}, kept {V['kept']}, clock {V.get('clock_mhz')}, leak {V['leak']['k_w_per_c']:.3f} W/C")

print("\nS over idle, W, at 600 MHz on aifoundry3; rate; cycles per op on a minion's mean")
table = {}
for tag, d, arm1, arm16 in (("by column", C, "gemmc1", "gemmc16"), ("vendor's strides", V, "gemmv1", "gemmv16")):
    for src, arm in (("gemm1", arm1), ("gemm16", arm16)):
        for t in ("fp32", "fp16", "int8"):
            for k in ("zeros", "ones", "sparse50", "real", TOP[t]):
                n = f"{src}.{t}.{k}"
                if n in d["items"] and d["items"][n]["S"]["mean"] is not None:
                    x = d["items"][n]
                    row = {"S_w": round(x["S"]["mean"], 2), "ci95": None if x["S"]["ci95"] is None else round(x["S"]["ci95"], 2), "n": x["S"]["n"], "rate": round(rate(x), 3), "cycles_per_op": round(x["cycles_per_op"], 1), "pj_mac": round(x["pj_mac_S"]["mean"], 3), "nj_op": round(x["pj_op_S"]["mean"] / 1000, 2)}
                    table[f"{arm}.{t}.{k}"] = row
                    print(f"  {arm:8s} {t} {k:9s} S {row['S_w']:6.2f} +- {row['ci95'] or 0:4.2f} n{row['n']}  rate {row['rate']:7.3f}  cycles {row['cycles_per_op']:7.1f}  {row['pj_mac']:6.3f} pJ/MAC  {row['nj_op']:6.2f} nJ/op")
out["cells"] = table

r = RULES["P1_rate"]
p1 = {}
for arm in ("gemmc1", "gemmv1", "gemmc16", "gemmv16"):
    for t in ("fp32", "fp16", "int8"):
        fz = REG["cells"][f"{arm}.{t}.rate"]["rate_600"]
        got = table[f"{arm}.{t}.{TOP[t]}"]["rate"]
        p1[f"{arm}.{t}"] = {"frozen": fz, "measured": got, "off": round(got / fz - 1, 3), "verdict": "PASS" if abs(got / fz - 1) <= r["bands"][arm] else "FAIL"}
out["rules"]["P1"] = p1

r = RULES["P2_premium"]
p2 = {}
for t in ("fp32", "fp16", "int8"):
    fz = REG["cells"][f"gemmc1.{t}.{TOP[t]}"]["S_w"]
    got = table[f"gemmc1.{t}.{TOP[t]}"]["S_w"]
    p2[t] = {"frozen": fz, "measured": got, "off": round(got / fz - 1, 3), "benchmark_e101": round(E101[f"mm16.{t}.{TOP[t]}"]["S"]["mean"], 2), "verdict": "PASS" if abs(got / fz - 1) <= r["band"] else "FAIL"}
out["rules"]["P2"] = p2

r = RULES["P3_int8_premium"]
res_full = S(C, "int8.full")["mean"]
x = table["gemmc1.int8.full"]["S_w"] - res_full
out["rules"]["P3"] = {"S_bycol": table["gemmc1.int8.full"]["S_w"], "ci95": table["gemmc1.int8.full"]["ci95"], "S_res": round(res_full, 2), "premium_w": round(x, 2), "benchmark_e101": 17.45, "as_run_e101": round(E101["gemm1.int8.full"]["S"]["mean"] - E101["int8.full"]["S"]["mean"], 2), "verdict": "COMES BACK" if x >= r["comes_back"] else ("STAYS GONE" if x < r["stays_gone"] else "PARTIAL")}

r = RULES["P4_refusal"]
sz = S(C, "fp32.zeros")["mean"]
c = CZ["fp32"] + (table["gemmc1.fp32.randn"]["S_w"] - sz) / XFER
p800 = B800 + S800 * c
a2 = SPEED["cells"]["gemmc1-fp32-randn"]
out["rules"]["P4"] = {"c_w": round(c, 2), "p800_w": round(p800, 1), "a2_c_w": a2.get("c_w"), "a2_p800_w_runs": a2.get("burst_p800_w_runs"), "verdict": "AT OR ABOVE 88 W: the cell should have been refused" if p800 >= r["limit_w"] else "BELOW 88 W: refused a cell it need not have"}

r = RULES["P5_zeros"]
p5 = {}
for t in ("fp32", "fp16", "int8"):
    sh = table[f"gemmc1.{t}.zeros"]["S_w"] / table[f"gemmc1.{t}.{TOP[t]}"]["S_w"]
    b = E101[f"mm16.{t}.zeros"]["S"]["mean"] / E101[f"mm16.{t}.{TOP[t]}"]["S"]["mean"]
    p5[t] = {"share": round(sh, 3), "benchmark": round(b, 3), "verdict": "PASS" if abs(sh - b) <= r["band"] else "FAIL"}
out["rules"]["P5"] = p5

print("\nrules:")
print(json.dumps(out["rules"], indent=1))

# Frozen clocks against the measured ones, labelled, no rule.
print("\nfrozen against measured clocks on aifoundry2, MHz, and c, W (labelled, no rule):")
eb, es = [], []
for lab, c_ in SPEED["cells"].items():
    fz = c_.get("frozen")
    if not fz:
        continue
    b, s = c_.get("burst_mhz"), c_.get("sus_mhz")
    if b is not None:
        eb.append(b - fz["burst_mhz"])
    if s is not None:
        es.append(s - fz["sus_mhz"])
    print(f"  {lab:26s} c frozen {fz['c_w']:6.2f} measured {c_.get('c_w') or 0:6.2f}  burst {fz['burst_mhz']:6.1f} / {b or 0:6.1f}  sustained {fz['sus_mhz']:6.1f} / {s or 0:6.1f}")


def rms(x):
    return round((sum(v * v for v in x) / len(x)) ** 0.5, 1) if x else None


out["frozen_clock_rms_mhz"] = {"burst": rms(eb), "n_burst": len(eb), "sustained": rms(es), "n_sus": len(es)}
print(out["frozen_clock_rms_mhz"])

# Two cards, one law: a3's T at 600 MHz against a2's fit.
print("\naifoundry3's T at 600 MHz, from the rate, against aifoundry2's fit at 600 MHz:")
K = {"fp32": 8.372, "fp16": 16.744, "int8": 33.48}
two = {}
for arm in ("gemmc1", "gemmv1", "gemmc16", "gemmv16"):
    for t in ("fp32", "fp16", "int8"):
        f = SPEED["fits"].get(f"{arm}.{t}")
        if f and f.get("C") is not None:
            got = K[t] / table[f"{arm}.{t}.{TOP[t]}"]["rate"]
            law = f["C"] / 600 + f["M"]
            two[f"{arm}.{t}"] = {"a3_T_600": round(got, 4), "a2_law_600": round(law, 4), "off": round(got / law - 1, 3)}
            print(f"  {arm}.{t}: {got:.4f} against {law:.4f} us ({(got / law - 1) * 100:+.1f}%)")
out["two_cards"] = two
json.dump(out, open(f"{D}/scored-p.json", "w"), indent=1)
