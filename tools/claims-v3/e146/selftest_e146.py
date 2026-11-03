#!/usr/bin/env python3
"""E146 (Q138): the self-test. score() on rows made up from the frozen numbers (each rule passing there and failing far off), R1's verdicts at MS's and
at MAB's numbers, the runner's preflight (it refuses E136's stop keys and a wrong binary), and the queue's stop-path check on made-up records: a trip on
live samples passes; a trip read at a pass's end (E139's 65 W stop), a stop that never fired and a die stop after a launch fail. No card.

    python3 tools/claims-v3/e146/selftest_e146.py > tools/claims-v3/e146/selftest.txt
"""
import copy
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_e146 as RD  # noqa: E402
import run_e146 as RUN  # noqa: E402
import queue_e146 as Q  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e146.json")))
TYPES = ("fp32", "fp16", "int8")
SH = list(P["shapes"])
FAILS = []


def say(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def rows(model, scale=1.0, dp=0.0):
    per, cells, t800 = {}, {}, {}
    for s in SH:
        for t in TYPES:
            L = P["laws"][f"{s}.{t}"][model]
            per[f"{s}.{t}"] = {"T800": L["T800_us"] * scale, "X": L["X"], "fit": None, "how": "launch means", "n800": 40, "n600": 4}
            for k in ("zeros", P["top"][t]):
                lab = f"{s}-{t}-{k}"
                c = P["cells"][lab]
                p8 = c["PS_w"]["800"] + dp
                cells[lab] = {"burst_p800_w_runs": [p8, p8], "burst_die_start": [50.0, 50.0],
                              "burst_die_max": [50.0 + P["heat"]["k_burst_c_per_w"] * (c["burst_w_S"] - P["heat"]["P_idle_w"])] * 2, "n_burst": 2, "n_sus": 0}
                if "sus_mhz_G2" in c and ((t == "fp32" and k == "randn") or (t == "int8" and k == "full")):
                    st = 55.0
                    die = min(P["heat"]["trip_c"], (1 - P["heat"]["w_sus"]) * st + P["heat"]["w_sus"] * (P["heat"]["die_idle_c"] + P["heat"]["c_steady_c_per_w"] * (c["sus_w_G2"] - P["heat"]["P_idle_w"])))
                    cells[lab].update({"sus_mhz": c["sus_mhz_G2"], "sus_w": c["sus_w_G2"], "sus_die": die, "sus_die_start": [st], "n_sus": 1})
                t800[lab] = L["T800_us"] * scale
    return per, cells, t800


# 1. at MS's own numbers every scored rule passes and R1 reads THE STORE TERM
per, cells, t800 = rows("MS")
V, E = RD.score(per, cells, t800, P, True, {}, [])
say(V["R1"]["verdict"] == "THE STORE TERM", f"R1 at MS's numbers: {V['R1']['verdict']} (h {V['R1']['per_format']['fp32'].get('h')})")
say(V["R2"]["pass"] == V["R2"]["n"] == 24 and V["R2"]["best"] == "MS", f"R2 at MS's numbers: {V['R2']['pass']}/{V['R2']['n']} PASS, best {V['R2']['best']}, rms {V['R2']['rms_rel']}")
say(V["R3"]["pass"] == V["R3"]["n"] == 48, f"R3 at PS's numbers: {V['R3']['pass']}/{V['R3']['n']}")
say(all(v["point"] == "PASS" for v in V["R5"]["T"].values()) and all(v["verdict"] == "PASS" for v in V["R5"]["power"].values()), "R5 at the frozen numbers: T and power PASS")
say(all(v["clock"] == "PASS" and v["power"] == "PASS" and v["die"] == "PASS" for v in V["R5"]["sus"].values()) and len(V["R5"]["sus"]) == 2, "R5 sustained at the frozen numbers: clock, power, die PASS")
say(V["R6"]["pass"] == V["R6"]["n"], f"R6 at the frozen numbers: {V['R6']['pass']}/{V['R6']['n']}")
say(V["R7"]["verdict"] == "PASS", "R7 when the kind does not change T")
r4 = [v for k, v in V["R4"]["cells"].items() if k.startswith("L4/L8")]
say(all(v["verdict"] in ("PASS", "NOT SCORED (PS floored at B(800))") for v in r4) and any(v["verdict"] == "PASS" for v in r4), f"R4 at PS's numbers: {[v['verdict'] for v in r4]}")
# 2. at MAB's numbers R1 reads NO STORE TERM and MAB is best
per, cells, t800 = rows("MAB")
V, E = RD.score(per, cells, t800, P, True, {}, [])
say(V["R1"]["verdict"] == "NO STORE TERM", f"R1 at MAB's numbers: {V['R1']['verdict']}")
say(V["R2"]["best"] == "MAB", f"R2 at MAB's numbers: best {V['R2']['best']}")
# 3. far off: 20% slow everywhere, power 8 W high
per, cells, t800 = rows("MS", 1.2, 8.0)
V, E = RD.score(per, cells, t800, P, True, {}, [])
say(V["R2"]["pass"] == 0, f"R2 20% slow: {V['R2']['pass']} PASS")
say(V["R3"]["pass"] == 0, f"R3 8 W high: {V['R3']['pass']} PASS")
say(all(v["point"] == "FAIL" for v in V["R5"]["T"].values()), "R5 T 20% slow: FAIL")
# 4. L8 not held by the L3: R1 falls back to L2/L4
per, cells, t800 = rows("MS")
for t in TYPES:
    per[f"L8.{t}"]["T800"] = P["laws"][f"L8.{t}"]["MS_24MB"]["T800_us"]
V, E = RD.score(per, cells, t800, P, True, {}, [])
say(str(V["R1"]["verdict"]).startswith("UNRESOLVED on L4/L8; L2/L4: THE STORE TERM"), f"R1 with L8's A fresh: {V['R1']['verdict']}")
# 5. a kind that changes T fails R7; failed checks fail R0
per, cells, t800 = rows("MS")
t800["L4-fp32-randn"] *= 1.03
V, E = RD.score(per, cells, t800, P, False, {}, [])
say(V["R7"]["verdict"] == "FAIL" and V["R0"]["verdict"] == "FAIL", "R7 with a kind 3% slow, R0 with a wrong check: FAIL")
# 6. the preflight
proto = json.load(open(os.path.join(HERE, "protocol.json")))
bad = copy.deepcopy(proto)
bad["safety"] = {"die_c": 80, "board_w": 93, "board_samples": 3}
why = RUN.preflight(bad, "/nonexistent")
say(why is not None and "abs_stop_c" in why, f"preflight refuses E136's stop keys: {why[:90] if why else why}")
why = RUN.preflight(proto, "/nonexistent")
say(why is not None and "sha256 None" in why, f"preflight refuses missing binaries: {why[:90] if why else why}")


# 7. the queue's stop-path check on made-up records
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
    live = lambda ms: 22.0 if ms < 1000 else 41.0  # noqa: E731
    make(root, "b-live", 4, "safety:board 41.0 W > 30 W on 3 samples", 1250, (900, 2100), live, lambda ms: 47)
    say(Q.Queue.check_stoptest(q, "b-live", "board") is None, "stop check: a board trip on live samples passes")
    make(root, "b-end", 4, "safety:board 41.0 W > 30 W on 3 samples", 7000, (900, 6900), live, lambda ms: 47)
    say(Q.Queue.check_stoptest(q, "b-end", "board") is not None, f"stop check: a trip read at the pass's end fails ({Q.Queue.check_stoptest(q, 'b-end', 'board')})")
    make(root, "b-never", 0, "done", None, (900, 6900), live, lambda ms: 47)
    say(Q.Queue.check_stoptest(q, "b-never", "board") is not None, "stop check: a stop that never fired fails")
    make(root, "d-live", 4, "safety:die 47 C >= 30 C", 80, None, lambda ms: 22.0, lambda ms: 47)
    say(Q.Queue.check_stoptest(q, "d-live", "die") is None, "stop check: a die trip on the first live sample passes")
    make(root, "d-late", 4, "safety:die 47 C >= 30 C", 6000, (900, 6900), lambda ms: 22.0, lambda ms: 47)
    say(Q.Queue.check_stoptest(q, "d-late", "die") is not None, "stop check: a die trip after a launch, seconds after its sample, fails")
print(f"\n{'ALL PASS' if not FAILS else str(len(FAILS)) + ' FAILED'}")
sys.exit(1 if FAILS else 0)
