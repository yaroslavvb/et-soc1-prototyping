#!/usr/bin/env python3
"""E159 (Q139): the self-test, run before the registration's commit. No card. It checks that the protocol carries Q139(q)'s frozen design unchanged, that
the runner's stop limits refuse what the brief forbids, that the queue's stop-path check (E146's code, in E159's queue) passes a live trip and fails the
known bad ones, and that the reduction scores complete holds through the frozen scorer, leaves a cut hold out, and applies the attribution rule.

    /usr/bin/python3 tools/claims-v3/e159/selftest_e159.py > tools/claims-v3/e159/selftest.txt
"""
import copy
import gzip
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_e159 as RUN  # noqa: E402
import queue_e159 as Q  # noqa: E402
import reduce_e159 as RD  # noqa: E402

ROOT = RD.ROOT
P = RD.PRED
D = P["design"]
PROTO = json.load(open(os.path.join(HERE, "protocol.json")))
FAILS = []


def say(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


# 1. the protocol is Q139(q)'s frozen design
say(RUN.R146.sha256(os.path.join(RD.G3DIR, "predictions-e159.json")) == RUN.PREDICTIONS_SHA256, "the frozen predictions file has its registered sha256 (91def7c4)")
runs = [(b["name"], r) for b in PROTO["blocks"] for r in b["runs"]]
holds = [r for n, r in runs if n in ("H", "Z")]
say([r["label"] for r in holds] == D["order"], f"the holds run in the frozen order: {[r['label'] for r in holds]}")
say([r["label"] for n, r in runs if n == "H"] == D["registered_subset"], "block H is the registered subset, the first six")
ok = all(r["values"] == P["cells"][r["label"]]["values"] and r["type"] == P["cells"][r["label"]]["type"] for r in holds)
say(ok, "every hold's values string and format are the frozen cell's")
h = D["hold"]
ok = all(r["launch"] == {"seconds": h["seconds"], "budget": h["budget"], "processes": h["processes"]} and r["tail_s"] == h["tail_s"] and r["start"] == h["start"] for r in holds)
say(ok, f"every hold is {h['processes']} processes of --seconds {h['seconds']} (budget {h['budget']}, tail {h['tail_s']} s) from a cool start <= {h['start']['max_c']} C")
say(PROTO["safety"] == D["stops"], f"the session's stops are the frozen ones: {PROTO['safety']}")
say([n for n, r in runs][:1] == ["SMOKE"] and [r["label"] for n, r in runs if n == "R"] == ["rest"], "the smoke, then the session's 30 s rest reading before the first hold")
say(all(PROTO["admission"][r["label"]]["fixed_p800_w"] == P["cells"][r["label"]]["predicted_peak_w"] for r in holds), "every hold's admission estimate is its frozen predicted peak")
top = max(P["cells"][r["label"]]["predicted_peak_w"] for r in holds)
say(top <= 82.0 and all(P["cells"][r["label"]]["runs_as_designed"] for r in holds), f"every hold's predicted peak is at most 82 W (highest {top} W): every hold runs as designed")
say(PROTO["limit_p800_w"] == 82.0 and PROTO["peak_lock_w"] == 82.0, "admission limit 82 W, peak lock 82 W")
dry = json.load(open(os.path.join(HERE, "protocol-dry.json")))
say([r["label"] for b in dry["blocks"] for r in b["runs"] if b["name"] in ("H", "Z")] == D["order"], "the dry protocol has the same holds in the same order")

# 2. the runner's stop limits (the brief: board stops at most 85 W; nothing above 82 W predicted runs as designed)
say(RUN.stops_ok(PROTO) is None, "the registered protocol's stops and limit pass the runner's check")
for k, v, why in (("board_cap_w", 93, "a 93 W board stop"), ("limit_p800_w", 88.0, "an 88 W admission limit")):
    p2 = copy.deepcopy(PROTO)
    if k == "board_cap_w":
        p2["safety"][k] = v
    else:
        p2[k] = v
    say(RUN.stops_ok(p2) is not None, f"the runner refuses {why}: {RUN.stops_ok(p2)}")
p2 = copy.deepcopy(PROTO)
del p2["safety"]["cap_consecutive"]
say(RUN.stops_ok(p2) is not None, "the runner refuses a protocol whose stops lack a key the watcher reads")
for kind in ("board", "die"):
    say(RUN.stops_ok(json.load(open(os.path.join(HERE, f"protocol-stoptest-{kind}.json")))) is None, f"the {kind} stop test's protocol passes the runner's check")


# 3. the queue's stop-path check (E146's code, in E159's queue) on made-up records
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
    live = lambda ms: 22.0 if ms < 1500 else 38.0  # noqa: E731  (an H1 zeros burst: 22 W at rest, 38 W at 800 MHz)
    make(root, "b-live", 4, "safety:board 38.0 W > 30 W on 3 samples", 1750, (900, 2100), live, lambda ms: 46)
    say(Q.Queue.check_stoptest(q, "b-live", "board") is None, "stop check: a board trip on live samples (a zeros burst over 30 W) passes")
    make(root, "b-end", 4, "safety:board 38.0 W > 30 W on 3 samples", 7000, (900, 6900), live, lambda ms: 46)
    say(Q.Queue.check_stoptest(q, "b-end", "board") is not None, f"stop check: a trip read at the pass's end fails ({Q.Queue.check_stoptest(q, 'b-end', 'board')})")
    make(root, "b-never", 0, "done", None, (900, 6900), live, lambda ms: 46)
    say(Q.Queue.check_stoptest(q, "b-never", "board") is not None, "stop check: a stop that never fired fails")
    make(root, "d-live", 4, "safety:die 46 C >= 30 C", 80, None, lambda ms: 22.0, lambda ms: 46)
    say(Q.Queue.check_stoptest(q, "d-live", "die") is None, "stop check: a die trip on the first live sample passes")
    make(root, "d-late", 4, "safety:die 46 C >= 30 C", 6000, (900, 6900), lambda ms: 22.0, lambda ms: 46)
    say(Q.Queue.check_stoptest(q, "d-late", "die") is not None, "stop check: a die trip after a launch, seconds after its sample, fails")

# 4. the reduction on E146's committed session, F6's two holds relabelled as H1's cells (a check of the code path: the frozen H1 levels are used)
SRC = os.path.join(ROOT, "docs/reports/data/2026-11-02-e146-gemm-stores/aifoundry2")
rel = {"F6-fp32-randn": "H1-fp32-randn", "F6-int8-full": "H1-int8-full"}
tmp = tempfile.mkdtemp(prefix="e159-selftest-", dir=os.environ.get("TMPDIR"))
try:
    for case in ("whole", "cut"):
        rd = os.path.join(tmp, case)
        s1 = os.path.join(rd, "s1")
        os.makedirs(s1)
        os.symlink(os.path.join(SRC, "s1", "tel"), os.path.join(s1, "tel"))
        with open(os.path.join(s1, "runs.jsonl"), "w") as f:
            for x in open(os.path.join(SRC, "s1", "runs.jsonl")):
                r = json.loads(x)
                if r.get("processes", 1) > 1:
                    r["label"] = rel.get(r["label"], r["label"])
                f.write(json.dumps(r) + "\n")
        L = [json.loads(x) for x in gzip.open(os.path.join(SRC, "s1", "launches.jsonl.gz"), "rt")]
        if case == "cut":      # drop one process of the fp32 hold: it must be cut and not scored
            drop = next(i for i, p in enumerate(L) if p.get("run") == "D-06-F6-fp32-randn-r1" and p.get("role") == "work")
            L.pop(drop)
        with gzip.open(os.path.join(s1, "launches.jsonl.gz"), "wt") as f:
            for p in L:
                f.write(json.dumps(p) + "\n")
        for n in ("marks.jsonl", "end.json"):
            shutil.copy(os.path.join(SRC, "s1", n), os.path.join(s1, n))
        res = RD.reduce(rd, None, check=(case == "whole"))
        cells = [x["cell"] for x in res["rows"]]
        if case == "whole":
            say(cells == ["H1-fp32-randn", "H1-int8-full"], f"the reduction scores both complete holds through the frozen scorer: {cells}")
            g = res["rows"][0]
            say(abs(g["meas"]["mhz"] - 745.1) < 0.2 and abs(g["meas"]["w"] - 56.15) < 0.02, f"its measured window is E146's F6 fp32 random ({g['meas']['mhz']:.1f} MHz, {g['meas']['w']:.2f} W)")
            say(res["R0_checks_of_C"]["verdict"] == "PASS", f"R0 PASS on E146's session ({res['R0_checks_of_C']['kernel_records']} kernel records)")
            say(set(res["all_scored"]["verdict_G3"]) == {"mhz", "w", "die"} and not res["registered_subset"]["complete"], "the verdicts are per quantity; the subset is reported incomplete when holds are missing")
        else:
            say(cells == ["H1-int8-full"] and len(res["cut"]) == 1 and "processes recorded" in res["cut"][0]["why_cut"], f"a hold missing a process is cut and not scored ({res['cut']})")
finally:
    shutil.rmtree(tmp)

# 5. the attribution rule on made-up rows
row = {"p800": 63.0, "P0_800": 57.09, "inside_G3": {"mhz": False, "w": False, "die": False}, "err": {"chain_on_measured": {"die": 0.4}}}
a = RD.attribute(row)
say(a["mhz"].startswith("P0's level") and a["w"].startswith("P0's level") and a["die"].startswith("the power path"), f"a miss with p800 5.9 W over P0(800) is P0's level; a die miss with the chain inside 1 C is the power path ({a})")
row = {"p800": 58.0, "P0_800": 57.09, "inside_G3": {"mhz": False, "w": True, "die": False}, "err": {"chain_on_measured": {"die": 1.6}}}
a = RD.attribute(row)
say(a["mhz"].startswith("not P0's level") and a["w"] == "inside" and a["die"].startswith("the heat path"), f"a clock miss with p800 within 4 W is not P0's level; a die miss with the chain outside 1 C is the heat path ({a})")

print(f"\n{'ALL PASS' if not FAILS else str(len(FAILS)) + ' FAILED'}")
sys.exit(1 if FAILS else 0)
