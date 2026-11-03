#!/usr/bin/env python3
"""E158 (Q139): the self-test of the frozen scorer, run before the registration's commit. No card. It makes up per-shape T800 rows from known
retention curves through model_e158.py (MAB's frozen prices and the desk's lines), runs reduce_e158.score() on them, and checks that each rule reads
what was built in; then the runner's stop limits and the queue's stop-path check (E146's, run on E158's queue) on made-up records.

    python3 tools/claims-v3/e158/selftest_e158.py > tools/claims-v3/e158/selftest.txt
"""
import copy
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model_e158 as M  # noqa: E402
import reduce_e158 as RD  # noqa: E402
import run_e158 as RUN  # noqa: E402
import queue_e158 as Q  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e158.json")))
DESK = M.load_desk()
AB, C1 = M.load_prices()
E146 = json.load(open(RD.E146_RES))
FAILS = []


def say(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def rows(curve, w, f6_scale=1.0, family_shift=None):
    """per and passes from a known truth: every ladder rung, F6, D2, D4 and the K4 rungs in fp16 and int8; two passes"""
    per, passes = {}, {}
    shapes = list(P["ladder"]) + ["F6", "D2", "D4"]
    for s in shapes:
        for t in M.TYPES:
            if t != "fp32" and not (s.startswith("K4") or s == "F6"):
                continue
            cr = curve
            if family_shift and s.startswith(family_shift[0]):
                cr = (lambda c, d: (lambda x: c(x + d)))(curve, family_shift[1])
            T8 = M.T_model(DESK["shapes"][s], cr, w, AB, C1, t)["T800"] * (f6_scale if s == "F6" else 1.0)
            per[f"{s}.{t}"] = {"T800": T8, "T600": None, "n600": 0, "n800": 20, "X": None, "how": None, "fit": None}
            for ps in (1, 2):
                passes[f"{ps}|{s}.{t}"] = T8
    return per, passes


def run(curve, w, **kw):
    per, passes = rows(curve, w, **kw)
    return RD.score(per, passes, P, DESK, AB, C1, True, None, E146, None)


# 1. a soft curve with C occupying the L3: ISO finds w near 1, F6 within 3%
V, E = run(M.curve_logistic(41.0, 3.0), 1.0)
say(V["R1"]["consistent"] == "CONSISTENT", f"R1 consistent on a soft truth ({V['R1']['outside']})")
say(V["R1"]["against_strict_c"] == "SOFT", "R1 reads a soft curve as SOFT")
say(V["R2"]["verdict"] == "C OCCUPIES THE L3", f"R2 on a w = 1 truth: {V['R2']['verdict']} (w {V['R2']['iso']['w']}, rms {V['R2']['iso']['rms_share']:.4f}, at w=0 {V['R2']['rms_w0']})")
say(V["R3"]["verdict"] == "PASS", f"R3 PASS when F6 follows the same curve (ISO {V['R3']['per_format']['fp32']['ISO']})")
say(V["R5"]["pass"] == V["R5"]["n"] and V["R5"]["n"] == 14, f"R5: the formats follow the fp32 curve ({V['R5']['pass']} of {V['R5']['n']})")
say(abs(V["R2"]["logi"]["x50_mb"] - 41.0) < 1.0 and V["R2"]["logi"]["w"] > 0.85, f"LOGI recovers x50 41 and w 1 ({V['R2']['logi']})")
# 2. strict LRU with C taking none of it
V, E = run(M.curve_strict(32.0), 0.0)
say(V["R2"]["verdict"] == "C TAKES NONE OF IT", f"R2 on a w = 0 strict truth: {V['R2']['verdict']} (w {V['R2']['iso']['w']}, near-best {V['R2']['iso']['w_near']}, rms {V['R2']['iso']['rms_share']:.4f}, at w=1 {V['R2']['rms_w1']})")
say(V["R1"]["against_strict_noc"] == "STRICT" and V["R1"]["against_strict_c"] == "SOFT", "R1: the w = 0 strict truth is STRICT against STRICT-NOC, SOFT against STRICT-C")
# 3. strict LRU with C occupying the L3 (E146's model) is read as STRICT, and its w as C OCCUPIES
V, E = run(M.curve_strict(32.0), 1.0)
say(V["R1"]["against_strict_c"] == "STRICT", "R1: E146's strict model read as STRICT")
say(V["R2"]["verdict"] == "C OCCUPIES THE L3", f"R2 on E146's strict model: {V['R2']['verdict']} (near-best w {V['R2']['iso']['w_near']})")
# 3b. a soft curve with half of C's traffic occupying the L3: PARTIAL
V, E = run(M.curve_logistic(38.0, 3.0), 0.5)
say(V["R2"]["verdict"] == "PARTIAL", f"R2 on a w = 0.5 soft truth: {V['R2']['verdict']} (w {V['R2']['iso']['w']}, near-best {V['R2']['iso']['w_near']})")
say(V["R3"]["verdict"] == "PASS", "R3 PASS when F6 follows E146's strict model too")
# 4. a curve that differs by family against the C share (K6, the C-light family, retaining as if 15 MB nearer): no w can fold that, so no single curve
V, E = run(M.curve_logistic(41.0, 3.0), 1.0, family_shift=("K6", -15.0))
say(V["R2"]["verdict"] == "NO SINGLE CURVE", f"R2 on family-dependent retention: {V['R2']['verdict']} (rms {V['R2']['iso']['rms_share']:.4f})")
# 5. F6 10% off the curve: R3 FAILS
V, E = run(M.curve_logistic(41.0, 3.0), 1.0, f6_scale=0.90)
say(V["R3"]["verdict"] == "FAIL", f"R3 FAIL when F6 runs 10% faster than its curve ({V['R3']['per_format']['fp32']['ISO']})")
# 6. a rung MAB cannot carry: INCONSISTENT
per, passes = rows(M.curve_logistic(41.0, 3.0), 1.0)
per["K4n8.fp32"]["T800"] *= 1.25
V, E = RD.score(per, passes, P, DESK, AB, C1, True, None, E146, None)
say(V["R1"]["consistent"] == "INCONSISTENT" and "K4n8" in V["R1"]["outside"], f"R1 INCONSISTENT names the rung MAB cannot carry ({V['R1']['outside']})")
# 7. a failed check of C labels the verdicts
V, E = RD.score(*rows(M.curve_logistic(41.0, 3.0), 1.0), P, DESK, AB, C1, False, None, E146, None)
say(V["R0"]["verdict"] == "FAIL", "R0 FAIL when a check of C failed")

# 8. the runner's stop limits (the brief: board stops at most 85 W; nothing above 82 W predicted runs as designed)
proto = json.load(open(os.path.join(HERE, "protocol.json")))
say(RUN.stops_ok(proto) is None, "the registered protocol's stops and limit pass the runner's check")
for k, v, why in (("board_cap_w", 93, "a 93 W board stop"), ("limit_p800_w", 88.0, "an 88 W admission limit")):
    p2 = copy.deepcopy(proto)
    if k == "board_cap_w":
        p2["safety"][k] = v
    else:
        p2[k] = v
    say(RUN.stops_ok(p2) is not None, f"the runner refuses {why}: {RUN.stops_ok(p2)}")
p2 = copy.deepcopy(proto)
del p2["safety"]["cap_consecutive"]
say(RUN.stops_ok(p2) is not None, "the runner refuses a protocol whose stops lack a key the watcher reads")
for kind in ("board", "die"):
    say(RUN.stops_ok(json.load(open(os.path.join(HERE, f"protocol-stoptest-{kind}.json")))) is None, f"the {kind} stop test's protocol passes the runner's check")
top = max(v["predicted_peak_w"] for v in P["cells"].values())
say(top <= 82.0, f"every cell's predicted peak board power is at most 82 W (highest {top} W)")


# 9. the queue's stop-path check (E146's code, in E158's queue) on made-up records
class FakeA:
    pass


class FakeQ:
    def __init__(self, runs):
        self.runs = runs
        self.a = FakeA()
        self.a.stoptest = {"board": os.path.join(HERE, "protocol-stoptest-board.json"), "die": os.path.join(HERE, "protocol-stoptest-die.json")}
        self.recs = []

    def rec(self, kind, **kw):
        self.recs.append((kind, kw))


def make(root, name, exit_code, reason, trip_ms, launch, board_fn, die_fn, t0=1_000_000):
    d = os.path.join(root, name)
    os.makedirs(os.path.join(d, "tel"))
    json.dump({"exit": exit_code, "reason": reason}, open(os.path.join(d, "end.json"), "w"))
    with open(os.path.join(d, "marks.jsonl"), "w") as f:
        if trip_ms is not None:
            f.write(json.dumps({"t_ms": t0 + trip_ms, "kind": "safety_trip", "detail": reason}) + "\n")
    with open(os.path.join(d, "tel", "x.jsonl"), "w") as f:
        for i in range(90):
            t = t0 + 100 * i
            f.write(json.dumps({"t_ms": t, "board_w": board_fn(100 * i), "temp_c": {"minshire": [die_fn(100 * i), 0, die_fn(100 * i) + 2]}}) + "\n")
    with open(os.path.join(d, "launches.jsonl"), "w") as f:
        if launch:
            f.write(json.dumps({"run": "STOPTEST-00", "role": "work", "t_start_ms": t0 + launch[0], "t_end_ms": t0 + launch[1]}) + "\n")
    return d


with tempfile.TemporaryDirectory() as root:
    q = FakeQ(root)
    live = lambda ms: 22.0 if ms < 1500 else 37.0  # noqa: E731  (a zeros burst: 22 W at rest, 37 W at 800 MHz)
    make(root, "b-live", 4, "safety:board 37.0 W > 30 W on 3 samples", 1750, (900, 2100), live, lambda ms: 47)
    say(Q.Queue.check_stoptest(q, "b-live", "board") is None, "stop check: a board trip on live samples (a zeros burst over 30 W) passes")
    make(root, "b-end", 4, "safety:board 37.0 W > 30 W on 3 samples", 7000, (900, 6900), live, lambda ms: 47)
    say(Q.Queue.check_stoptest(q, "b-end", "board") is not None, f"stop check: a trip read at the pass's end fails ({Q.Queue.check_stoptest(q, 'b-end', 'board')})")
    make(root, "b-never", 0, "done", None, (900, 6900), live, lambda ms: 47)
    say(Q.Queue.check_stoptest(q, "b-never", "board") is not None, "stop check: a stop that never fired fails")
    make(root, "d-live", 4, "safety:die 47 C >= 30 C", 80, None, lambda ms: 22.0, lambda ms: 47)
    say(Q.Queue.check_stoptest(q, "d-live", "die") is None, "stop check: a die trip on the first live sample passes")
    make(root, "d-late", 4, "safety:die 47 C >= 30 C", 6000, (900, 6900), lambda ms: 22.0, lambda ms: 47)
    say(Q.Queue.check_stoptest(q, "d-late", "die") is not None, "stop check: a die trip after a launch, seconds after its sample, fails")
print(f"\n{'ALL PASS' if not FAILS else str(len(FAILS)) + ' FAILED'}")
sys.exit(1 if FAILS else 0)
