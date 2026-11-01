#!/usr/bin/env python3
"""E96: the scorer's self-test, on hand-made cells and rounds, before any card has run. Every expected verdict below is written by hand
from README.md's rules; the test needs no session. It also tests the queue's slot parser and the fine reading on a planted trace.

    python3 selftest_e96.py > selftest.txt
"""
import copy
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_e96 as X  # noqa: E402
import queue_e96 as Q  # noqa: E402
import predict_e96 as PD  # noqa: E402

pred = json.load(open(os.path.join(HERE, "predictions.json")))
T = pred["tiles"]
bad = 0


def check(name, got, want):
    global bad
    ok = got == want
    bad += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {got}" + ("" if ok else f" (expected {want})"))


def good_cells():
    """Every tile at its frozen point, the anchors at their tie cells: every rule should pass."""
    c = {}
    for k, e in T.items():
        f = e["frozen"]
        c[k] = {"type": e["type"], "burst_mhz": f["burst_mhz"], "burst_mhz_without": f["burst_mhz"], "rel_on_measured_c_burst_mhz": f["burst_mhz"], "c_w": f["c_w"]}
        if k in pred["sus_core"]:
            c[k].update({"sus_mhz": f["sus_mhz"], "sus_limit_runs": [f["sus_limit"]], "sus_last": [{"800": f["sus_share800"]}], "rel_on_measured_c_sus_mhz": f["sus_mhz"]})
    for k, a in pred["anchors"].items():
        c[k] = {"type": a["type"], "burst_mhz": a["tie_burst_mhz"], "burst_mhz_without": a["tie_burst_mhz"], "sus_mhz": a["tie_sus_mhz"]}
    return c


# the frozen shares and bars, at their edges
check("share 20 of 25 is 80%: PASS", X.share_verdict(20, 25, 20, 0.8, 0.6), "PASS")
check("share 19 of 25: INCONCLUSIVE", X.share_verdict(19, 25, 20, 0.8, 0.6), "INCONCLUSIVE")
check("share 15 of 25 is 60%: INCONCLUSIVE (FAIL is < 60%)", X.share_verdict(15, 25, 20, 0.8, 0.6), "INCONCLUSIVE")
check("share 14 of 25: FAIL", X.share_verdict(14, 25, 20, 0.8, 0.6), "FAIL")
check("share with 19 run of a minimum 20: UNDER-RESOLVED", X.share_verdict(19, 19, 20, 0.8, 0.6), "UNDER-RESOLVED")
check("both PASS PASS", X.both_verdict("PASS", "PASS"), "PASS")
check("both PASS INCONCLUSIVE", X.both_verdict("PASS", "INCONCLUSIVE"), "INCONCLUSIVE")
check("both UNDER-RESOLVED FAIL", X.both_verdict("UNDER-RESOLVED", "FAIL"), "FAIL")
check("both UNDER-RESOLVED PASS", X.both_verdict("UNDER-RESOLVED", "PASS"), "UNDER-RESOLVED")

c = good_cells()
s2t, s2bt = pred["claims_e96"]["S2_gate_buys_speed"]["tiles"], pred["claims_e96"]["S2b_gate_buys_sustained_clock"]["tiles"]
B = pred["bars"]
check("S1 every tile at its point", X.score_s1(c, pred)["verdict"], "PASS")
check("S1 population", (X.score_s1(c, pred)["population_burst"], X.score_s1(c, pred)["population_sus"]), (25, 11))
check("S4 every limit as predicted", X.score_s4(c, pred)["verdict"], "PASS")
check("S5 clocks on the relation", X.score_s5(c, pred)["verdict"], "PASS")
check("T anchors at their tie cells", X.score_tie(c, pred)["verdict"], "PASS")
check("T int8 full's tie is the mean of 793.4, 786.5, 774.7", pred["anchors"]["int8/full"]["tie_sus_mhz"], 784.9)
check("T int8 full at 800 ties (+15.1)", abs(800 - pred["anchors"]["int8/full"]["tie_sus_mhz"]) <= 25, True)
check("T rows", len(X.score_tie(c, pred)["rows"]), 12)
# S2 at its edges, against the randn cells in hand
R32, R16 = c["fp32/randn"]["burst_mhz"], c["fp16/randn"]["burst_mhz"]
S32, S16 = c["fp32/randn"]["sus_mhz"], c["fp16/randn"]["sus_mhz"]
check("S2 800 against the randn cells", X.score_gate(c, s2t, "burst_mhz", B["S2_pass_mhz"], B["S2_fail_mhz"])["verdict"], "PASS")
x = copy.deepcopy(c); x["fp32/vgg16_fc2"]["burst_mhz"] = R32 + 39.9
check("S2 one tile +39.9: INCONCLUSIVE", X.score_gate(x, s2t, "burst_mhz", B["S2_pass_mhz"], B["S2_fail_mhz"])["verdict"], "INCONCLUSIVE")
x = copy.deepcopy(c); x["fp32/vgg16_fc2"]["burst_mhz"] = R32 + 40.0
check("S2 one tile +40.0: PASS", X.score_gate(x, s2t, "burst_mhz", B["S2_pass_mhz"], B["S2_fail_mhz"])["verdict"], "PASS")
x = copy.deepcopy(c); x["fp16/t5small_l0_down"]["burst_mhz"] = R16 + 14.9
check("S2 one tile +14.9: FAIL", X.score_gate(x, s2t, "burst_mhz", B["S2_pass_mhz"], B["S2_fail_mhz"])["verdict"], "FAIL")
x = copy.deepcopy(c); del x["fp16/t5small_l0_down"]
check("S2 a tile missing: UNDER-RESOLVED", X.score_gate(x, s2t, "burst_mhz", B["S2_pass_mhz"], B["S2_fail_mhz"])["verdict"], "UNDER-RESOLVED")
x = copy.deepcopy(c); del x["fp16/t5small_l0_down"]; x["fp32/vgg16_fc2"]["burst_mhz"] = R32 + 4.0
check("S2 a tile missing, another +4: FAIL stands", X.score_gate(x, s2t, "burst_mhz", B["S2_pass_mhz"], B["S2_fail_mhz"])["verdict"], "FAIL")
check("S2b at the frozen points", X.score_gate(c, s2bt, "sus_mhz", B["S2b_pass_mhz"], B["S2b_fail_mhz"])["verdict"], "PASS")
x = copy.deepcopy(c); x["fp32/resnet18_l3c1"]["sus_mhz"] = S32 + 49.0
check("S2b one tile +49: INCONCLUSIVE", X.score_gate(x, s2bt, "sus_mhz", B["S2b_pass_mhz"], B["S2b_fail_mhz"])["verdict"], "INCONCLUSIVE")
# S3: fp16's tiles sit at 737.5, 737.5, 736.3, mean 737.1
x = copy.deepcopy(c); x["fp16/randn"]["burst_mhz"] = 720.0
check("S3 with fp16 randn 720, +17.1: FAIL", X.score_s3(x, pred)["verdict"], "FAIL")
x = copy.deepcopy(c); x["fp16/randn"]["burst_mhz"] = 730.0
check("S3 with fp16 randn 730, +7.1: PASS", X.score_s3(x, pred)["verdict"], "PASS")
x = copy.deepcopy(x); del x["fp32/bert_l6_up"]
check("S3 a tile missing: UNDER-RESOLVED", X.score_s3(x, pred)["verdict"], "UNDER-RESOLVED")
x = copy.deepcopy(c); x["fp32/vgg16_fc2"]["sus_limit_runs"] = ["thermal"]; x["fp16/vgg16_fc2"]["sus_limit_runs"] = ["none"]; x["fp32/t5small_l0_up"]["sus_limit_runs"] = ["power"]
check("S4 8 of 11 right is 73%: INCONCLUSIVE", X.score_s4(x, pred)["verdict"], "INCONCLUSIVE")
x = copy.deepcopy(c)
for k in ("fp32/vgg16_fc2", "fp16/vgg16_fc2", "fp32/t5small_l0_up", "fp32/bert_l6_up", "fp16/vit_l5_down"):
    x[k]["sus_limit_runs"] = ["unresolved"]
check("S4 6 of 11 right is 55%: FAIL", X.score_s4(x, pred)["verdict"], "FAIL")
x = copy.deepcopy(c)
for k in pred["sus_core"]:
    x[k]["sus_mhz"] = x[k]["rel_on_measured_c_sus_mhz"] + 20
check("S5 sustained rms 20: INCONCLUSIVE", X.score_s5(x, pred)["verdict"], "INCONCLUSIVE")
for k in pred["sus_core"]:
    x[k]["sus_mhz"] = x[k]["rel_on_measured_c_sus_mhz"] + 26
check("S5 sustained rms 26: FAIL", X.score_s5(x, pred)["verdict"], "FAIL")
x = copy.deepcopy(c)
for k in list(T)[4:]:
    del x[k]["rel_on_measured_c_burst_mhz"]
x[list(T)[0]]["burst_mhz"] += 100
check("S5 a big rms on 4 of 25 bursts: UNDER-RESOLVED, not FAIL", X.score_s5(x, pred)["verdict"], "UNDER-RESOLVED")
x = copy.deepcopy(c); x["int8/full"]["sus_mhz"] = pred["anchors"]["int8/full"]["tie_sus_mhz"] - 25.3
check("T one row 25.3 off: FAIL", X.score_tie(x, pred)["verdict"], "FAIL")
x = copy.deepcopy(c)
for k in pred["sus_core"][7:]:
    del x[k]["sus_mhz"]
check("S1 with only the plan's 7 sustained tiles still scores", (X.score_s1(x, pred)["population_sus"], X.score_s1(x, pred)["verdict_sus"]), (7, "PASS"))
for k in pred["sus_core"][6:7]:
    del x[k]["sus_mhz"]
check("S1 with 6 sustained tiles: UNDER-RESOLVED", X.score_s1(x, pred)["verdict_sus"], "UNDER-RESOLVED")

# the partition, by hand; the same function in the predictions' power table
for lo, hi, want in ((16, 30, "DIFFERENT_BEYOND_BAR"), (-30, -16, "DIFFERENT_BEYOND_BAR"), (3, 25, "DIFFERENT"), (-25, -3, "DIFFERENT"), (2, 11, "DIFFERENT_SMALL"),
                     (-8, 11, "SAME_WITHIN_BAR"), (-15, 15, "SAME_WITHIN_BAR"), (-16, 11, "INCONCLUSIVE"), (-8, 15.5, "INCONCLUSIVE"), (0, 0, "SAME_WITHIN_BAR")):
    check(f"partition [{lo}, {hi}]", X.partition(lo, hi, 15.0), want)
    check(f"partition [{lo}, {hi}], predict_e96's copy", PD.partition(lo, hi, 15.0), want)
check("side below", X.side(-3, -1), "BELOW")
check("side above", X.side(1, 3), "ABOVE")
check("side holds 0", X.side(-1, 1), "INCONCLUSIVE")


def arm_rounds(rows, limit="thermal", w=None, die=None):
    """rows: per round [full, l0, l6d, l6a] clocks."""
    out = {}
    ks = ["int8/full", "int8/l0_mlp_up", "int8/l6_mlp_down", "int8/l6_attn_qk"]
    for i, row in enumerate(rows, 1):
        out[i] = {k: {"mhz": v, "w": 50.0 + (w[j] if w else 0), "die": 64.0 + (die[j] if die else 0), "limit": limit, "mhz_without": v, "fine_w": 47.0 + (w[j] if w else 0), "share800": 0.9}
                  for j, (k, v) in enumerate(zip(ks, row))}
    return out


# by hand: d = +12, +15, +9, +12 (mean(real) - full); mean 12, sd sqrt((0 + 9 + 9 + 0) / 3) = sqrt 6 = 2.449; SE 1.2247; t(3) 3.182; half-width 3.897
R4 = [[780, 790, 792, 794], [778, 790, 794, 795], [786, 793, 796, 796], [782, 792, 794, 796]]
a = X.score_arm(arm_rounds(R4), pred)
check("I1 rounds", a["E96-I1"]["rounds"], [12.0, 15.0, 9.0, 12.0])
check("I1 mean", a["E96-I1"]["mean"], 12.0)
check("I1 half-width", a["E96-I1"]["halfwidth"], 3.897)
check("I1 verdict: [8.1, 15.9] excludes 0, reaches past 15", a["E96-I1"]["verdict"], "DIFFERENT")
check("I1 not at the cap", a["E96-I1"]["at_the_cap"], False)
# t(2) with the first three rounds only: mean 12, sd 3, SE 1.732, half-width 7.453
a3 = X.score_arm(arm_rounds(R4[:3]), pred)
check("I1 three rounds half-width", a3["E96-I1"]["halfwidth"], 7.453)
check("I1 three rounds verdict: [4.5, 19.5]", a3["E96-I1"]["verdict"], "DIFFERENT")
a2 = X.score_arm(arm_rounds(R4[:2]), pred)
check("I1 two rounds: NOT SCORED", a2["E96-I1"]["verdict"], "NOT SCORED")
r = arm_rounds(R4); del r[4]["int8/l6_attn_qk"]
check("a broken round does not count", X.score_arm(r, pred)["n"], 3)
cap = arm_rounds([[800, 800, 800, 800]] * 4, limit="none")
a = X.score_arm(cap, pred)
check("every run at 800: SAME_WITHIN_BAR", a["E96-I1"]["verdict"], "SAME_WITHIN_BAR")
check("every run at 800: at the cap", a["E96-I1"]["at_the_cap"], True)
wide = [[780, 800, 800, 800], [800, 790, 780, 800], [760, 790, 800, 780], [800, 800, 790, 770]]
check("a wide night: INCONCLUSIVE", X.score_arm(arm_rounds(wide), pred)["E96-I1"]["verdict"], "INCONCLUSIVE")
a = X.score_arm(arm_rounds(R4, w=[0.0, -1.0, -2.0, -2.5], die=[0.0, -0.4, -1.0, -1.1]), pred)
check("I2 board W: mean(real) - full is -1.833", a["E96-I2"]["mean"], -1.833)
check("I2 with no spread: BELOW", a["E96-I2"]["verdict"], "BELOW")
check("I3 die BELOW", a["E96-I3"]["verdict"], "BELOW")
check("labelled fine W reads BELOW", a["labelled"]["fine_w_at_800"]["reads"], "BELOW")
# the pooled arm by hand on a 2 x 2-free table: rows R4, kinds 4, df 9
p = X.two_way([row for row in R4], pred["t975"])
check("two-way df", p["df"], 9)
check("two-way contrast equals the paired mean", p["mean"], 12.0)

# the fine reading: 40 s at 800 MHz, one dip of 1 s at 600 with W 40, then 700 for 1 s; samples at 10 Hz
tr, spans = [], [(0.0, 8.0), (8.4, 16.4), (16.8, 24.8), (25.2, 33.2), (33.6, 41.6)]
t = 0.0
while t <= 41.6:
    inside_ = any(a <= t <= b for a, b in spans)
    mhz = 800
    w = 50.0
    if 20.0 <= t < 21.0:
        mhz, w = 600, 40.0
    elif 21.0 <= t < 22.0:
        mhz, w = 700, 44.0
    tr.append([round(t, 1), 60, w, mhz] if inside_ else [round(t, 1), 60, 25.0, 600])
    t += 0.1
m = {"trace": tr, "work_s": 41.6, "proc_spans": spans}
procs = [{"role": "work", "t_start_ms": int(a * 1000) + 1000000, "t_end_ms": int(b * 1000) + 1000000,
          "sparsity": [{"t_start_ms": int(a * 1000) + 1000000, "t_end_ms": int(b * 1000) + 1000000}]} for a, b in spans]
f = X.fine_view(m, procs)
check("fine W leaves out the dip, its climb and the rest of 3 s", f["fine_w"], 50.0)
check("fine view found one dip", f["dips"], 1)
check("the share at 800 counts the dip against it", f["share800"] < 1.0, True)

# E98's rest rule on history rows: 40 min of rows at 5 s, the last busy row 25 min 5 s before the end: 10 min skipped, 905 s left, so 181 rows
end = 10 ** 12
rows = []
for i in range(480):
    t = end - (480 - i) * 5000
    busy = t < end - 25 * 60000
    rows.append({"t": t, "temps": {"nic": 44.0, "nvme": 37.0}, "cards": [{"w": 40.0 if busy else 22.0, "die": 60 if busy else 47, "held": busy}]})
r = X.history_rest(rows, end)
check("rest: 905 s of rows left", r["rows"], 181)
check("rest W", r["w"], 22.0)
check("rest raw die", r["die_raw"], 47.0)

# the slots file as the E98 lane writes it
with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
    fh.write("SLOT E100: start 1793521800 (08:30 UTC = 01:30 PDT), end 1793524200 (09:10 UTC = 01:10 PST): the idle-reset test\n"
             "SLOT E96: start 1793527500 (10:05 UTC = 02:05 PST), end 1793532000 (11:20 UTC = 03:20 PST): real tensors' speed\n"
             "E98 P2: rest reading starts 1793525400 (09:30 UTC)\nE98 P3: rest reading starts 1793533200 (11:40 UTC)\nE98 P4: rest reading starts 1793535900 (12:25 UTC)\n")
check("the slot parser", Q.parse_slots(fh.name), (1793527500000, 1793532000000, 1793533200000))
os.unlink(fh.name)
check("the labels", (X.round_of("int8-real-l0_mlp_up-round3"), X.round_of("fp32-randn-rep2")), (3, None))

print()
print("ALL PASS" if not bad else f"{bad} FAILED")
sys.exit(1 if bad else 0)
