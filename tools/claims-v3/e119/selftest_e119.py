#!/usr/bin/env python3
"""E119 (Q134): the self-test. Runs reduce_e119.score() on made-up rows built from the frozen laws (every rule passes), then breaks one thing at a time
and shows the matching rule fail; checks run_e119.fits() and that the protocol plans no cell the admission rule would refuse. No card, no data.

    python3 tools/claims-v3/e119/selftest_e119.py > tools/claims-v3/e119/selftest.txt
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_e119 as RD  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e119.json")))
PROTO = json.load(open(os.path.join(HERE, "protocol.json")))
TYPES, TOP = RD.TYPES, RD.TOP
fails = 0


def made_up(x_scale=None, t800_scale=None, gap_scale=1.0, p800_add=0.0):
    """per, cells, t800 as the frozen laws give them: each arm's launches at 600 and 800 MHz, each cell's burst and sustained as frozen."""
    per, cells, t800 = {}, {}, {}
    for t in TYPES:
        for a in P["arms"]:
            L = P["laws"][f"{a}.{t}"]
            t6, t8 = L["T600_us"], L["T800_us"]
            if t800_scale and a in t800_scale:
                t8 *= t800_scale[a]
            if x_scale and a in x_scale:
                t6 = t8 * L["X"] * x_scale[a]
            rows = [(600.0, t6)] * 4 + [(800.0, t8)] * 40
            per[f"{a}.{t}"] = RD.clock_x(rows, P)
            for k in ("zeros", TOP[t]):
                lab = f"{a}-{t}-{k}"
                fz = P["cells"][lab]
                c = {"burst_mhz": fz["burst_mhz"], "sus_mhz": fz["sus_mhz"], "burst_rate": fz["burst_rate"], "sus_rate": fz["sus_rate"],
                     "burst_p800_w_runs": [fz["p800_walk_w"] + (p800_add if k != "zeros" else 0.0)]}
                if k != "zeros":
                    c["sus_rate"] = fz["sus_rate"] / gap_scale
                cells[lab] = c
                t800[lab] = t8
    return per, cells, t800


def show(name, V, key, want):
    global fails
    got = V[key]
    if key in ("R1", "R3"):
        got_v = got["verdict"]
    elif key == "R2":
        got_v = "PASS" if all(c["verdict"] == "PASS" for c in got["cells"].values()) and got["order_fp32"] else "FAIL"
    elif key == "R5":
        got_v = "PASS" if all(c["verdict"] == "PASS" for c in got["cells"].values()) and got["order_fp32"] else "FAIL"
    else:
        got_v = got["verdict"]
    ok = got_v == want
    fails += 0 if ok else 1
    print(f"{'ok  ' if ok else 'FAIL'} {name:58s} {key}: {got_v} (want {want})")


per, cells, t800 = made_up()
V = RD.score(per, cells, t800, P)
for k, w in (("R0", "PASS"), ("R1", "REUSE IS THE VARIABLE AT 800 MHz"), ("R2", "PASS"), ("R3", "OUTSIDE THE CLOCK"), ("R4", "PASS"), ("R5", "PASS"), ("R6", "PASS")):
    show("the frozen laws themselves", V, k, w)
# R0: c1 3% slow in fp32
p2, c2, t2 = made_up(t800_scale={"c1": 1.03})
show("c1's T800 3% long (not E105's binary)", RD.score(p2, c2, t2, P), "R0", "FAIL")
show("a wrong check of C", RD.score(per, cells, t800, P, checks_ok=False), "R0", "FAIL")
# R1: reuse not the variable (c16r32 keeps most of the cold excess)
t3 = dict(t800)
for t in TYPES:
    for k in ("zeros", TOP[t]):
        t3[f"c16r32-{t}-{k}"] = t800[f"c16-{t}-{k}"] * 0.9
show("32 passes keep 90% of the cold walk's T", RD.score(per, cells, t3, P), "R1", "NOT THE VARIABLE")
t4 = dict(t800)
for t in TYPES:
    for k in ("zeros", TOP[t]):
        t4[f"c16r4-{t}-{k}"] = t800[f"c16r4-{t}-{k}"] * 1.08
show("one rung 8% off the 1/R law", RD.score(per, cells, t4, P), "R1", "PARTIAL")
# R2: X off by more than 0.03 on a rung, and the order broken
p5, c5, t5 = made_up(x_scale={"c16r4": 1.05})
show("c16r4's X 5% above M1", RD.score(p5, c5, t5, P), "R2", "FAIL")
# R3: c8s follows the clock
p6, c6, t6 = made_up(x_scale={"c8s": P["laws"]["c8s.fp32"]["X_M2"] / P["laws"]["c8s.fp32"]["X"]})
show("c8s's X at M2's (the L3 follows the clock)", RD.score(p6, c6, t6, P), "R3", "FOLLOWS THE CLOCK")
p7, c7, t7 = made_up(x_scale={"c8s": 1 + 0.5 * (P["laws"]["c8s.fp32"]["X_M2"] / P["laws"]["c8s.fp32"]["X"] - 1)})
show("c8s's X halfway", RD.score(p7, c7, t7, P), "R3", "PARTIAL")
# R4: random 2% slower than zeros at 800 MHz
t8 = dict(t800)
t8["c16r4-fp32-randn"] = t800["c16r4-fp32-zeros"] * 1.02
show("random's T800 2% over zeros' on one arm", RD.score(per, cells, t8, P), "R4", "FAIL")
# R5: gaps 10% smaller than frozen
p9, c9, t9 = made_up(gap_scale=1.10)
show("every sustained gap 10% over the frozen", RD.score(p9, c9, t9, P), "R5", "FAIL")
# R6: a random cell reads 3 W over its estimate
p10, c10, t10 = made_up(p800_add=15.0)
show("random cells 15 W over the walk-scaled level", RD.score(p10, c10, t10, P), "R6", "FAIL")
# clock_x falls back to the fit, and refuses with no span
x_fit = RD.clock_x([(600.0, 1.4)] + [(700.0, 1.3)] * 3 + [(800.0, 1.2)] * 3, P)
print(f"{'ok  ' if x_fit['how'] == 'fit' else 'FAIL'} {'one launch at 600 MHz: X from the fit':58s} how {x_fit['how']} X {x_fit['X']:.4f}")
fails += 0 if x_fit["how"] == "fit" else 1
x_none = RD.clock_x([(800.0, 1.2)] * 10, P)
print(f"{'ok  ' if x_none['X'] is None else 'FAIL'} {'no launch under 790 MHz: no X':58s} X {x_none['X']}")
fails += 0 if x_none["X"] is None else 1
# run_e119.fits (imported without touching run_e105's card code paths)
sys.path.insert(0, os.path.join(HERE, "..", "kspeed", "e105"))
import run_e119 as RU  # noqa: E402
for e, p, c, want in ((100.0, 113.8, 300.0, True), (200.0, 113.8, 300.0, False), (2600.0, 36.2, 2640.0, True), (2610.0, 36.2, 2640.0, False)):
    got = RU.fits(e, p, c)
    fails += 0 if got == want else 1
    print(f"{'ok  ' if got == want else 'FAIL'} fits(elapsed {e:.0f} s, plan {p} s, cap {c:.0f} s) = {got}")
# the protocol plans no cell the rule refuses, and every planned label has an admission entry
bad = []
for bl in PROTO["blocks"]:
    for r in bl["runs"]:
        lab = r["label"].replace("-rep2", "")
        e = PROTO["admission"].get(lab)
        if e is None or e.get("fixed_p800_w") is None or e["fixed_p800_w"] > PROTO["limit_p800_w"]:
            bad.append(lab)
print(f"{'ok  ' if not bad else 'FAIL'} every planned run is admitted at its frozen estimate: {len(bad)} not ({bad})")
fails += 1 if bad else 0
hi = max((PROTO["admission"][r["label"].replace("-rep2", "")]["fixed_p800_w"], r["label"]) for bl in PROTO["blocks"] for r in bl["runs"])
print(f"     the highest planned estimate: {hi[0]} W ({hi[1]}); limit {PROTO['limit_p800_w']} W, lock {PROTO['peak_lock_w']} W, stop {PROTO['safety']['board_cap_w']} W on {PROTO['safety']['cap_consecutive']} samples")
print("selftest ok" if not fails else f"selftest FAILED ({fails})")
sys.exit(1 if fails else 0)
