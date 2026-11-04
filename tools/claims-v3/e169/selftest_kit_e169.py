#!/usr/bin/env python3
"""E169 (Q141(s)): the run kit's self-test, before the kit's commit and before any E169 claim. Desk only: no card, no device, no ssh.

    nice -n 10 python3 -B tools/claims-v3/e169/selftest_kit_e169.py [--tmp <dir>] > tools/claims-v3/e169/selftest-kit.txt

1. The runner's bounds (run_e169.stops_ok): the registered protocol and both stop-path tests pass; a 93 W board stop, an 80 C die stop
   (E158's own, above this round's 76 C), an 88 W admission limit and a protocol missing a watcher key are refused.
2. The protocol (REGISTRATION-A2.md D3, D7, D8): the stops 60 W / 3 samples, 76 C, 82 W, lock 60 W; every label of every protocol in the
   admission table, every estimate at most 82 W; 50 bursts, the blocks A-F as registered (A in its fixed order), every E169 fp32 shape
   once in each of passes 1-5 and every tie in passes 1-2, the formats only in F; the blocks' pass map equal to reduce_e169's; the
   registered subset A-C of 26 bursts.
3. The order on the card: run_hpl.load_protocol(), the harness's own planner (one seeded generator over the blocks, order_seed 169), on
   protocol.json; printed, and the same order twice.
4. The queue's stop-path check (E146's code, in E169's queue, as E158's self-test ran it) on made-up records: a board trip on live samples
   passes; a trip read at a pass's end, a stop that never fired and a die trip after a launch fail; a die trip on the first live sample passes.
SPDX-License-Identifier: Apache-2.0
"""
import copy
import json
import os
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LAB, "tools/claims-v3/hpl"))
import run_e169 as RUN  # noqa: E402
import queue_e169 as Q  # noqa: E402
import reduce_e169 as RE  # noqa: E402
import run_hpl as H  # noqa: E402  (the harness's planner, load_protocol, unchanged)

FAILS = []
E169 = ("N1", "P1", "N2", "P2", "N3", "P3")
TIES = ("K4n7", "K4n8", "K6n5", "K6n4")


def say(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def load(name):
    return json.load(open(os.path.join(HERE, name)))


def part1():
    proto = load("protocol.json")
    say(RUN.stops_ok(proto) is None, "the registered protocol's stops and limit pass the runner's check")
    for kind in ("board", "die"):
        for dry in ("", "-dry"):
            say(RUN.stops_ok(load(f"protocol-stoptest-{kind}{dry}.json")) is None, f"the {kind} stop test's protocol{' (dry)' if dry else ''} passes the runner's check")
    say(RUN.stops_ok(load("protocol-dry.json")) is None, "the dry protocol passes the runner's check")
    for where, k, v, why in (("safety", "board_cap_w", 93, "a 93 W board stop"), ("safety", "abs_stop_c", 80, "an 80 C die stop (E158's own)"),
                             ("top", "limit_p800_w", 88.0, "an 88 W admission limit")):
        p2 = copy.deepcopy(proto)
        if where == "safety":
            p2["safety"][k] = v
        else:
            p2[k] = v
        say(RUN.stops_ok(p2) is not None, f"the runner refuses {why}: {RUN.stops_ok(p2)}")
    p2 = copy.deepcopy(proto)
    del p2["safety"]["cap_consecutive"]
    say(RUN.stops_ok(p2) is not None, "the runner refuses a protocol whose stops lack a key the watcher reads")


def part2():
    proto = load("protocol.json")
    kit = load("kit-e169.json")
    say(proto["safety"] == {"abs_stop_c": 76, "board_cap_w": 60, "cap_consecutive": 3} and proto["limit_p800_w"] == 82.0 and proto["peak_lock_w"] == 60.0,
        f"the session's stops {proto['safety']}, limit {proto['limit_p800_w']} W, lock {proto['peak_lock_w']} W, as REGISTRATION-A2.md D7")
    b = load("protocol-stoptest-board.json")["safety"]
    d = load("protocol-stoptest-die.json")["safety"]
    say(b == {"abs_stop_c": 76, "board_cap_w": 30, "cap_consecutive": 3} and d == {"abs_stop_c": 30, "board_cap_w": 60, "cap_consecutive": 3},
        f"the stop-path tests lower one stop each: board {b}, die {d}")
    labels, tops = set(), []
    for name in ("protocol.json", "protocol-dry.json", "protocol-stoptest-board.json", "protocol-stoptest-die.json",
                 "protocol-stoptest-board-dry.json", "protocol-stoptest-die-dry.json"):
        p = load(name)
        for bl in p["blocks"]:
            for r in bl["runs"]:
                labels.add(r["label"])
                tops.append(p["admission"][r["label"]]["fixed_p800_w"])
    missing = sorted(lab for lab in labels if lab not in proto["admission"])
    say(not missing, f"every label of every protocol is in the admission table ({len(labels)} labels; missing {missing})")
    say(max(tops) <= 82.0, f"every estimate is at most 82 W (highest {max(tops)} W)")
    blocks = {bl["name"]: bl for bl in proto["blocks"]}
    say(list(blocks) == ["SMOKE", "A", "B", "C", "D", "E", "F"], f"the blocks in order: {list(blocks)}")
    A = [r["label"] for r in blocks["A"]["runs"]]
    want_A = [f"{s}-fp32-zeros" for s in E169] + [f"{s}-fp32-zeros" for s in TIES]
    say(A == want_A and not blocks["A"]["shuffle"], f"block A in its registered order, not shuffled: {A}")
    say(all(blocks[k]["shuffle"] for k in ("B", "C", "D", "E")) and not blocks["F"]["shuffle"], "blocks B-E shuffled, F in order")
    n = sum(len(bl["runs"]) for k, bl in blocks.items() if k != "SMOKE")
    sub = sum(len(blocks[k]["runs"]) for k in ("A", "B", "C"))
    say(n == 50 and sub == 26, f"{n} bursts; the registered subset A-C {sub}")
    pob = RE.PASS_OF_BLOCK_E169
    cover = {}
    for k, bl in blocks.items():
        if k == "SMOKE":
            continue
        for r in bl["runs"]:
            cover.setdefault(r["label"], []).append(pob[k])
    ok = all(sorted(cover[f"{s}-fp32-zeros"]) == [1, 2, 3, 4, 5] for s in E169) and all(sorted(cover[f"{s}-fp32-zeros"]) == [1, 2] for s in TIES)
    ok = ok and all(cover[f"{s}-{t}-zeros"] == [1] for s in E169 for t in ("fp16", "int8"))
    say(ok and set(pob) == set(blocks) - {"SMOKE"}, f"passes as reduce_e169 maps the blocks {pob}: every E169 fp32 shape in passes 1-5, every tie in 1-2, fp16 and int8 once (block F)")
    sm = [r["label"] for r in blocks["SMOKE"]["runs"]]
    say(sm == ["rest"] + kit["smoke_cells"] and set(proto["smoke_cycles"]) == set(kit["smoke_cells"]), f"the smoke: {sm}; cycles for {sorted(proto['smoke_cycles'])}")
    for bl in proto["blocks"]:
        if bl["name"] == "SMOKE":
            continue
        for r in bl["runs"]:
            if not (r["launch"] == {"seconds": 6, "budget": 7.5, "processes": 1} and r["tail_s"] == 4 and r["start"] == {"mode": "cool", "max_c": 55, "max_wait_s": 300}):
                say(False, f"{bl['name']} {r['label']}: not E158's burst")
                return
    say(True, "every session burst is E158's: one 6 s process (budget 7.5 s), tail 4 s, a cool start at or below 55 C waiting at most 300 s")


def part3():
    path = os.path.join(HERE, "protocol.json")
    raw, runs, bad = H.load_protocol(path)
    raw2, runs2, _ = H.load_protocol(path)
    order = [(r.block, r.label) for r in runs]
    say(not bad and order == [(r.block, r.label) for r in runs2], f"run_hpl.load_protocol plans {len(runs)} runs (the smoke apart), the same order twice, no complaint {bad}")
    for blk in ("A", "B", "C", "D", "E", "F"):
        print(f"     {blk}: " + " ".join(lab.split("-zeros")[0] for b, lab in order if b == blk))


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


def part4(tmp):
    with tempfile.TemporaryDirectory(dir=tmp) as root:
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


def main():
    tmp = sys.argv[sys.argv.index("--tmp") + 1] if "--tmp" in sys.argv else None
    print("1. The runner's bounds")
    part1()
    print("\n2. The protocol")
    part2()
    print("\n3. The order on the card (the harness's planner, order_seed 169)")
    part3()
    print("\n4. The queue's stop-path check on made-up records")
    part4(tmp)
    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
