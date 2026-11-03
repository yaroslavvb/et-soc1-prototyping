"""Desk test of e162_app.py's builders and features on CPU torch (bytes differ from CUDA's; this checks logic only).
Usage: PYTHONPATH=<a CPU torch 2.2.2 install> python cpu_test_e162.py e162_app.py   (E162.md, "Selftest and desk runs")"""
import sys
import types

import torch

src = open(sys.argv[1]).read().replace('"cuda"', '"cpu"')
mod = types.ModuleType("e162cpu")
exec(compile(src, "e162cpu", "exec"), mod.__dict__)
E = mod
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def feats(k, n):
    A, B = E.make_pair(torch, k, n)
    assert A.shape == (n, n) and B.shape == (n, n), (E.kid(k), A.shape, B.shape)
    fe = E.kind_feats(torch, k, A, B)
    return A, B, fe


seen = set()
allk = E.PLUMB + E.SETS["A1"] + E.SETS["L1"] + E.SETS["A2"] + E.SETS["L2"] + E.SETS["E149"]
for k in allk:
    if E.kid(k) in seen:
        continue
    seen.add(E.kid(k))
    n = 128
    A, B, fe = feats(k, n)
    st = fe["A"]["stats"]
    check(st["finite"] and fe["B"]["stats"]["finite"], f"{E.kid(k)} not finite")
    for side in ("A", "B"):
        for key in ["ones", "row"] + [f"lag{s}" for s in E.LAGS] + [f"rlag{r}" for r in E.RLAGS]:
            W = 8 if k[0] == "int8" else 16
            check(len(fe[side][key]) == W, f"{E.kid(k)} {side} {key} len")
        check(fe[side]["row"] == fe[side]["rlag1"], f"{E.kid(k)} row != rlag1")
    for r in E.RLAGS:
        check(f"gtrR{r}" in fe["cross"], f"{E.kid(k)} no gtrR{r}")
print(f"built and featured {len(seen)} kinds at 128 on CPU")


def F(name):
    k = next(x for x in allk if E.kid(x) == name)
    return feats(k, 128)[2]


MANT = list(range(7))
fe = F("bf16.kS1")
check(all(abs(fe["A"][f"rlag{r}"][p]) == 0 for r in E.RLAGS for p in range(16)), "kS1 has row flips")
check(all(abs(fe["A"]["lag1"][p] - 1.0) < 1e-9 for p in MANT), "kS1 lag1 mantissa not 1")
check(all(fe["A"]["lag2"][p] == 0 for p in range(16)), "kS1 lag2 not 0")
fe = F("bf16.kS4")
check(abs(fe["A"]["lag4"][0] - 1.0) < 1e-9 and fe["A"]["lag8"][0] == 0, "kS4 lag4/lag8")
check(abs(fe["A"]["lag1"][0] - 0.25) < 0.01, f"kS4 lag1 {fe['A']['lag1'][0]}")
fe = F("bf16.rS1")
check(all(fe["A"][f"lag{s}"][p] == 0 for s in E.LAGS for p in range(16)), "rS1 has K flips")
check(abs(fe["A"]["rlag1"][0] - 1.0) < 1e-9 and fe["A"]["rlag2"][0] == 0, "rS1 rlag1/rlag2")
fe = F("bf16.rS16")
check(abs(fe["A"]["rlag16"][0] - 1.0) < 1e-9 and fe["A"]["rlag32"][0] == 0, "rS16 rlag16/32")
fe = F("bf16.rC16")
check(abs(fe["A"]["lag1"][0] - 0.5) < 0.1, f"rC16 lag1 {fe['A']['lag1'][0]}")
fe = F("bf16.rowc")
check(all(fe["A"][f"lag{s}"][p] == 0 for s in E.LAGS for p in range(16)), "rowc K flips")
check(fe["A"]["rlag1"][15] > 0.3, "rowc no row sign flips")
fe = F("bf16.colc")
check(all(fe["A"][f"rlag{r}"][p] == 0 for r in E.RLAGS for p in range(16)), "colc row flips")
check(fe["A"]["lag1"][15] > 0.3, "colc no K sign flips")
fe = F("bf16.sq1")
check(abs(fe["A"]["lag1"][0] - 1.0) < 1e-9 and 0.3 < fe["A"]["rlag1"][0] < 0.7, "sq1 (E149)")
fe = F("bf16.stripeR0")
check(fe["cross"]["gtr1"] < 0.02 and fe["cross"]["gtrR1"] > 0.3, f"stripeR0 gtr {fe['cross']['gtr1']} {fe['cross']['gtrR1']}")
fe = F("bf16.stripeK0")
check(fe["cross"]["gtr1"] > 0.3 and fe["cross"]["gtrR1"] < 0.02, "stripeK0 gtr")
fe = F("bf16.zs50")
check(fe["cross"]["gtrR1"] > 0.3 and fe["cross"]["gtr1"] > 0.3, "zs50 gtr both")
fe = F("bf16.zb50")
check(fe["cross"]["gtr1"] < 0.05 and fe["cross"]["gtrR1"] > 0.3, f"zb50 gtr {fe['cross']['gtr1']}")
fe = F("bf16.t16x16")
check(fe["A"]["lag1"][15] < 0.1 and fe["A"]["lag16"][15] > 0.3 and fe["A"]["rlag16"][15] > 0.3, "t16x16")
fe = F("bf16.kB8_4")
check(fe["A"]["rlag1"][0] < 0.1 and fe["A"]["rlag8"][0] > 0.3, f"kB8_4 rlag1 {fe['A']['rlag1'][0]}")
fe = F("bf16.checkv")
check(abs(fe["A"]["lag1"][0] - 1) < 1e-9 and abs(fe["A"]["rlag1"][0] - 1) < 1e-9 and fe["A"]["lag2"][0] == 0, "checkv")
fe = F("bf16.rdup8")
check(fe["A"]["rlag1"][15] < 0.1 and fe["A"]["rlag8"][15] > 0.3 and fe["A"]["lag1"][15] > 0.3, "rdup8")
fe = F("bf16.cdup8")
check(fe["A"]["lag1"][15] < 0.1 and fe["A"]["lag8"][15] > 0.3 and fe["A"]["rlag1"][15] > 0.3, "cdup8")
fe = F("bf16.walkK")
check(fe["A"]["lag1"][14] < fe["A"]["rlag1"][14], "walkK smoother along K")
fe = F("bf16.walkR")
check(fe["A"]["rlag1"][14] < fe["A"]["lag1"][14], "walkR smoother along rows")
fe = F("bf16.rollM")
check(fe["A"]["rlag1"][10] < fe["A"]["lag1"][10], "rollM smoother along rows")
fe = F("bf16.drollK")
check(fe["A"]["lag1"][10] < fe["A"]["rlag1"][10], "drollK smoother along K")
fe = F("int8.kS1")
check(all(abs(fe["A"]["lag1"][p] - 1) < 1e-9 for p in range(1, 7)) and fe["A"]["lag1"][0] == 0 and
      fe["A"]["lag1"][7] == 0, f"int8 kS1 {fe['A']['lag1']}")
fe = F("fp16.rS1")
check(all(abs(fe["A"]["rlag1"][p] - 1) < 1e-9 for p in range(10)) and fe["A"]["rlag1"][10] == 0, "fp16 rS1")
fe = F("int8.walkK")
check(fe["A"]["stats"]["max"] <= 100 and fe["A"]["stats"]["min"] >= -100, "int8 walkK range")
# the smoke kinds and sizes
for k in E.SMOKE_KINDS:
    check(E.size_of(k, {"bf16": 1}) in E.SMOKE_SIZES, f"smoke size {E.kid(k)}")
pl = E.plan("A1", "A", first=True)
check(pl["sizes"] == {"bf16": 2048, "fp16": 1024, "int8": 1024}, "A1 sizes")
p1 = [s for s in pl["steps"] if s["op"] == "pass"]
check(len(p1) == 2 and p1[0]["seq"] == list(reversed(E.plan("A1", "B", first=False)["steps"][3]["seq"])), "orders")
check(sum(1 for x in p1[0]["seq"] if x == "bf16.zeros") == 4, "anchors")
pl2 = E.plan("A2", "B", first=False, refuse=["x"])
check(pl2["refuse_uuid"] == ["x"] and pl2["steps"][3]["seq"] == list(reversed(E.plan("A2", "A")["steps"][3]["seq"])),
      "A2 plan")
plL = E.plan("L1", "LA", l40s_size=3072)
check(plL["sizes"]["bf16"] == 3072 and plL["expect_name"] == "L40S", "L1 plan")
print("FAILS:" if fails else "ALL CHECKS PASS", fails)
