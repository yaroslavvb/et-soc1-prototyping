#!/usr/bin/env python3
"""E168 (Q141(o)): the self-test, run before the kit's commit. No card. It is E159's selftest_e159.py ported to E168, with checks for
what E168 adds. Run on the Intel (the frozen scorer needs numpy):

    /usr/bin/python3 -B tools/claims-v3/e168/selftest_e168.py > tools/claims-v3/e168/selftest.txt

  1. The protocol carries Q140(q)'s frozen design (e39d06da) and amendment A2 (226249e1) unchanged: order, blocks, values, hold shape,
     the gates' bounds (A2 section 2), stops, admission estimates; the dry twin has the same holds.
  2. The runner's stop limits refuse what the brief forbids.
  3. The runner's addition: E101's imported tile check refuses the frozen W8A8 hold's pool-6 file; run_e168.verify_tiles accepts the
     whole session; a changed byte, a wrong type and a moved manifest are refused.
  4. The queue's stop-path check (E146's code) on made-up records, and E168's smoke check of C.
  5. The reduction on E159's committed session (aifoundry2, Tue 3 Nov), five holds relabelled as E168 cells and A2's: the A7 rows equal
     the frozen scorer's own on the same holds; A2's call gives the same warm row; a hold missing a process, or a process with no check
     of C, is cut; R0; the start-dependence reading on made-up rows.
  6. The frozen scorer's own self-test, re-run unchanged: its output equals the committed selftest-score-e168.txt; check (9 files) OK;
     the 18-file sidecar OK.
  7. The parent's registered verdicts: E159's registered reduction (reduce_e159.py, unchanged) on E159's committed data gives E159's
     committed results.json verdicts (all nine holds and the subset), the parent run E168's kit is ported from.
SPDX-License-Identifier: Apache-2.0
"""
import copy
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_e168 as RUN  # noqa: E402
import queue_e168 as Q  # noqa: E402
import reduce_e168 as RD  # noqa: E402

ROOT = RD.ROOT
P = RD.PRED
A2 = RD.A2
D = P["design"]
PROTO = json.load(open(os.path.join(HERE, "protocol.json")))
DRY = json.load(open(os.path.join(HERE, "protocol-dry.json")))
FAILS = []
E159 = os.path.join(ROOT, "docs/reports/data/2026-11-03-e159-gemm-sustained")


def say(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


CELLS = dict(P["cells"])
CELLS[RD.A2_LABEL] = A2["cells"][RD.A2_LABEL]
GATES = {"cold": {"mode": "cool", "max_c": 46, "max_wait_s": 360}, "warm55": {"mode": "cool", "max_c": 55, "max_wait_s": 300}}

# 1. the protocol is the frozen design plus A2
say(RUN.R146.sha256(RD.PRED_PATH) == RUN.PREDICTIONS_SHA256, f"the frozen predictions file has its registered sha256 (e39d06da): {RUN.PREDICTIONS_SHA256[:12]}...")
say(RUN.R146.sha256(RD.A2_PATH) == RUN.AMENDMENT_SHA256 == RD.A2_SHA256, f"A2's predictions-e168-a2.json has its registered sha256 (226249e1): {RD.A2_SHA256[:12]}...")
w, c = P["cells"][RD.WARM_ZEROS], A2["cells"][RD.A2_LABEL]
say(A2["cells"][RD.WARM_ZEROS] == w and c["G4"] == w["both_nominal_starts"]["cold"]["G4"] and c["G3_as_frozen"] == w["both_nominal_starts"]["cold"]["G3_as_frozen"]
    and all(c[k] == w[k] for k in ("values", "P0_w", "predicted_peak_w", "type", "kind", "shape")) and A2["g4"] == P["g4"],
    "A2's file holds the frozen warm cell unchanged, and its cold cell is that cell with both_nominal_starts.cold's G4 and G3 (nothing computed)")
runs = [(b["name"], r) for b in PROTO["blocks"] for r in b["runs"]]
holds = [r for n, r in runs if n in ("H", "I", "A")]
say([r["label"] for r in holds] == D["order"] + [RD.A2_LABEL], f"the holds run in the frozen order, then A2's: {[r['label'] for r in holds]}")
say([r["label"] for n, r in runs if n == "H"] == RD.SUBSET and len(RD.SUBSET) == 6, "block H is the registered subset, the six fp32 random holds")
say([r["label"] for n, r in runs if n == "A"] == [RD.A2_LABEL], "block A is A2's one hold, last")
say(all(r["values"] == CELLS[r["label"]]["values"] and r["type"] == CELLS[r["label"]]["type"] for r in holds), "every hold's values string and format are the frozen cell's")
h = D["hold"]
say(all(r["launch"] == {"seconds": h["seconds"], "budget": h["budget"], "processes": h["processes"]} and r["tail_s"] == h["tail_s"] for r in holds),
    f"every hold is {h['processes']} processes of --seconds {h['seconds']} (budget {h['budget']}, tail {h['tail_s']} s)")
say(all(r["start"] == GATES[CELLS[r["label"]]["start"]] for r in holds), "every hold's gate is A2 section 2's for its start: cold 46 C / 360 s, warm55 55 C / 300 s")
say(PROTO["safety"] == D["stops"], f"the session's stops are the frozen ones: {PROTO['safety']}")
say([n for n, r in runs][:1] == ["SMOKE"] and [r["label"] for n, r in runs if n == "R"] == ["rest"] and [n for n, _ in runs].index("R") < [n for n, _ in runs].index("H"),
    "the smoke, then the session's 30 s rest reading before the first hold")
say(all(PROTO["admission"][r["label"]]["fixed_p800_w"] == CELLS[r["label"]]["predicted_peak_w"] for r in holds), "every hold's admission estimate is its frozen predicted peak")
top = max(CELLS[r["label"]]["predicted_peak_w"] for r in holds)
say(top <= 82.0 and all(CELLS[r["label"]]["runs_as_designed"] for r in holds), f"every hold's predicted peak is at most 82 W (highest {top} W): every hold runs as designed")
say(PROTO["limit_p800_w"] == 82.0 and PROTO["peak_lock_w"] == 82.0, "admission limit 82 W, peak lock 82 W")
labels = {r["label"] for _, r in runs}
for kind in ("board", "die"):
    labels |= {r["label"] for b in json.load(open(os.path.join(HERE, f"protocol-stoptest-{kind}.json")))["blocks"] for r in b["runs"]}
say(all(lab in PROTO["admission"] for lab in labels), f"every label the queue runs is in the admission table ({len(labels)} labels)")
say(set(PROTO["smoke_cycles"]) == {r["label"] for n, r in runs if n == "SMOKE" and r["label"] != "rest"}, f"the smoke's cycles per op cover its four launches: {PROTO['smoke_cycles']}")
dh = [r for b in DRY["blocks"] for r in b["runs"] if b["name"] in ("H", "I", "A")]
say([r["label"] for r in dh] == [r["label"] for r in holds] and all(r["start"]["max_wait_s"] == 6 and r["start"]["max_c"] == GATES[CELLS[r["label"]]["start"]]["max_c"] for r in dh),
    "the dry protocol has the same holds in the same order, the same gate temperatures, waits cut to 6 s")
say(PROTO["caps"]["max_card_min"] == 58.0, "the session's own cap is 58 card-minutes (A2: 63 in all with the smoke and the stop tests)")

# 2. the runner's stop limits
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

# 3. the runner's addition: pool 6's W8A8 tile
H = RUN.R146.R119.H
proto_all, all_runs, badp = H.load_protocol(os.path.join(HERE, "protocol.json"), [b["name"] for b in PROTO["blocks"]])
say(not badp, f"run_hpl.py's protocol check (run_e101s.py's values check for GEMM values) passes every run: {badp}")
w8 = [r for r in all_runs if RUN.is_pool6_value(r.values)]
say(len(w8) == 1 and w8[0].label == "S2-int8-real_smol_w8a8_down-warm55", f"exactly one run names a pool-6 tile: {[r.label for r in w8]}")
try:
    RUN._prev_verify(ROOT, w8)
    say(False, "E101's imported verify_tiles refuses the frozen W8A8 hold's pool-6 file (it did not: the addition would not be needed)")
except SystemExit as e:
    say("is not a registered tile" in str(e), f"E101's imported verify_tiles refuses the frozen W8A8 hold's pool-6 file, the whole session at load: {str(e)[:150]}")
try:
    tiles, ksha, krev = RUN.verify_tiles(ROOT, all_runs)
    rec = tiles.get(w8[0].values, {})
    say(rec.get("pool") == "blind6" and list(rec.get("files", {}).values())[0]["sha256"] == "24fe46efcb1b3a93deea9e781e8caf17495ded5703366bec820bda9603111b2f",
        f"run_e168.verify_tiles accepts every run of the session; the W8A8 tile checked against blind6.json (2,048 B, whole/A/B sha256): {len(tiles)} values")
except SystemExit as e:
    say(False, f"run_e168.verify_tiles refused the registered session: {e}")
dry_all = H.load_protocol(os.path.join(HERE, "protocol-dry.json"), [b["name"] for b in DRY["blocks"]])[1]
try:
    RUN.verify_tiles(ROOT, dry_all)
    say(True, "run_e168.verify_tiles accepts every run of the dry protocol (run_kspeed.py calls it under --dry too)")
except SystemExit as e:
    say(False, f"run_e168.verify_tiles refused the dry protocol: {e}")
tmp = tempfile.mkdtemp(prefix="e168-selftest-root-", dir=os.environ.get("TMPDIR"))
try:
    pool = os.path.join(tmp, RUN.C6.POOL_REL)
    os.makedirs(os.path.join(pool, "tiles", "int8"))
    for f in ("blind6.json", "MANIFEST"):
        shutil.copy(os.path.join(ROOT, RUN.C6.POOL_REL, f), os.path.join(pool, f))
    src = os.path.join(ROOT, RUN.C6.POOL_REL, "tiles/int8/int8.real_smol_w8a8_down.bin")
    dst = os.path.join(pool, "tiles/int8/int8.real_smol_w8a8_down.bin")
    shutil.copy(src, dst)
    say(RUN.pool6_why(tmp, w8) == [], "pool6_why passes the tile in a copied tree")
    b = bytearray(open(dst, "rb").read())
    b[1500] ^= 0x01
    open(dst, "wb").write(bytes(b))
    why = RUN.pool6_why(tmp, w8)
    say(bool(why) and "sha256" in why[0], f"one flipped bit in B is refused: {why[0][:110] if why else why}")
    shutil.copy(src, dst)
    r_fp = copy.copy(w8[0])
    r_fp.type = "fp32"
    why = RUN.pool6_why(tmp, [r_fp])
    say(bool(why) and "a int8 tile" in why[0], f"an int8 pool-6 tile on an fp32 run is refused: {why[:1]}")
    open(os.path.join(pool, "MANIFEST"), "a").write("x\n")
    why = RUN.pool6_why(tmp, w8)
    say(bool(why) and "MANIFEST" in why[0], f"a changed MANIFEST is refused: {why[0][:100] if why else why}")
finally:
    shutil.rmtree(tmp)


# 4. the queue's stop-path check (E146's code, in E168's queue) and the smoke's check of C, on made-up records
class FakeA:
    pass


class FakeQ:
    def __init__(self, runs, dry=False):
        self.runs = runs
        self.a = FakeA()
        self.a.dry = dry
        self.a.protocol = os.path.join(HERE, "protocol.json")
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


def make_smoke(root, with_check):
    d = os.path.join(root, "smoke")
    os.makedirs(d)
    json.dump({"exit": 0, "reason": "done"}, open(os.path.join(d, "end.json"), "w"))
    sm = [r for b in PROTO["blocks"] if b["name"] == "SMOKE" for r in b["runs"]]
    with open(os.path.join(d, "runs.jsonl"), "w") as f, open(os.path.join(d, "launches.jsonl"), "w") as g:
        for i, r in enumerate(sm):
            name = f"SMOKE-{i:02d}-{r['label']}-r1"
            f.write(json.dumps({"run": name, "label": r["label"], "queries": {"config": {"tdp_w": 65, "temp_threshold_c": 65}}}) + "\n")
            if r["label"] == "rest":
                continue
            sp = [{"test": "fma", "cycles_per_op": PROTO["smoke_cycles"][r["label"]] * 1.1, "ok": True, "result": "unchecked"}]
            if with_check:
                sp.append({"test": "check", "cycles_per_op": PROTO["smoke_cycles"][r["label"]] * 1.1, "ok": True, "result": "exact"})
            g.write(json.dumps({"run": name, "role": "work", "rc": 0, "sparsity": sp}) + "\n")
    return d


with tempfile.TemporaryDirectory() as tdir:
    q = FakeQ(tdir)
    live = lambda ms: 22.0 if ms < 1500 else 38.0  # noqa: E731  (an S2 zeros burst: 22 W at rest, 38 W at 800 MHz)
    make(tdir, "b-live", 4, "safety:board 38.0 W > 30 W on 3 samples", 1750, (900, 2100), live, lambda ms: 46)
    say(Q.Queue.check_stoptest(q, "b-live", "board") is None, "stop check: a board trip on live samples (a zeros burst over 30 W) passes")
    make(tdir, "b-end", 4, "safety:board 38.0 W > 30 W on 3 samples", 7000, (900, 6900), live, lambda ms: 46)
    say(Q.Queue.check_stoptest(q, "b-end", "board") is not None, f"stop check: a trip read at the pass's end fails ({Q.Queue.check_stoptest(q, 'b-end', 'board')})")
    make(tdir, "b-never", 0, "done", None, (900, 6900), live, lambda ms: 46)
    say(Q.Queue.check_stoptest(q, "b-never", "board") is not None, "stop check: a stop that never fired fails")
    make(tdir, "d-live", 4, "safety:die 46 C >= 30 C", 80, None, lambda ms: 22.0, lambda ms: 46)
    say(Q.Queue.check_stoptest(q, "d-live", "die") is None, "stop check: a die trip on the first live sample passes")
    make(tdir, "d-late", 4, "safety:die 46 C >= 30 C", 6000, (900, 6900), lambda ms: 22.0, lambda ms: 46)
    say(Q.Queue.check_stoptest(q, "d-late", "die") is not None, "stop check: a die trip after a launch, seconds after its sample, fails")
for with_check in (True, False):
    with tempfile.TemporaryDirectory() as tdir:
        make_smoke(tdir, with_check)
        why = Q.Queue.check_smoke(FakeQ(tdir))
        if with_check:
            say(why is None, f"smoke check: four launches, each with an ok check of C and cycles at 110% of the frozen law's, pass ({why})")
        else:
            say(why is not None and "check of C" in why, f"smoke check (E168's): a launch with no check-of-C record fails ({why})")

# 5. the reduction on E159's committed session: five holds relabelled
SRC = os.path.join(E159, "aifoundry2", "s1")
REL = {"H1-fp32-randn": "S1-fp32-randn-cold", "H2-fp32-randn": "S2-fp32-randn-cold", "H3-fp32-randn": "S3-fp32-randn-cold",
       "H1-int8-full": RD.WARM_ZEROS, "H2-int8-full": RD.A2_LABEL}


def build_case(rd, drop=None, strip_check=None):
    s1 = os.path.join(rd, "s1")
    os.makedirs(s1)
    os.symlink(os.path.join(SRC, "tel"), os.path.join(s1, "tel"))
    with open(os.path.join(s1, "runs.jsonl"), "w") as f:
        for x in open(os.path.join(SRC, "runs.jsonl")):
            r = json.loads(x)
            if r.get("processes", 1) > 1:
                r["label"] = REL.get(r["label"], r["label"])
            f.write(json.dumps(r) + "\n")
    L = [json.loads(x) for x in gzip.open(os.path.join(SRC, "launches.jsonl.gz"), "rt")]
    if drop:
        L.pop(next(i for i, p in enumerate(L) if p.get("run") == drop and p.get("role") == "work"))
    if strip_check:
        p = next(p for p in L if p.get("run") == strip_check and p.get("role") == "work")
        p["sparsity"] = [k for k in p["sparsity"] if k.get("test") != "check"]
    with gzip.open(os.path.join(s1, "launches.jsonl.gz"), "wt") as f:
        for p in L:
            f.write(json.dumps(p) + "\n")
    for n in ("marks.jsonl", "end.json"):
        shutil.copy(os.path.join(SRC, n), os.path.join(s1, n))
    return s1


tmp = tempfile.mkdtemp(prefix="e168-selftest-", dir=os.environ.get("TMPDIR"))
try:
    rd = os.path.join(tmp, "whole")
    s1 = build_case(rd)
    res = RD.reduce(rd, None, check=True)
    cells = [x["cell"] for x in res["rows"]]
    say(cells == ["S1-fp32-randn-cold", "S2-fp32-randn-cold", "S3-fp32-randn-cold", RD.WARM_ZEROS], f"A7's rows are the four relabelled nine-cell holds, A2's left out: {cells}")
    # the frozen scorer called directly on the same holds must give the same rows
    direct = RD.temp_session(s1, {h["run"] for h in res["complete"] if h["label"] in RD.NINE}, {RD.A2_LABEL})
    try:
        dres, _ = RD.quiet_score(direct)
    finally:
        shutil.rmtree(direct)
    same = len(dres["rows"]) == len(res["rows"]) and all(
        a["cell"] == b["cell"] and all(abs(a["pred"]["G4"][q] - b["pred"]["G4"][q]) < 1e-12 and abs(a["meas"][q] - b["meas"][q]) < 1e-12 for q in RD.RULE)
        for a, b in zip(sorted(dres["rows"], key=lambda x: x["cell"]), sorted(res["rows"], key=lambda x: x["cell"])))
    say(same, "the reduction's A7 rows equal score_e168.score's own rows on the same holds (the frozen scorer, unchanged, is the score)")
    say(all(c["ok"] for c in res["consistency"]) and len(res["consistency"]) == 2,
        f"consistency: the recomputed verdicts equal the scorer's, and A2's call gives the same warm row: {res['consistency']}")
    sd = res["A2_reported"]["start_dependence"]
    cold = res["A2_reported"]["cold_row"]
    warm = next(x for x in res["rows"] if x["cell"] == RD.WARM_ZEROS)
    say(abs(sd["dW_meas_w"] - (cold["meas"]["w"] - warm["meas"]["w"])) < 0.0006 and abs(sd["dW_G4_w"] - (cold["pred"]["G4"]["w"] - warm["pred"]["G4"]["w"])) < 0.0006
        and sd["dW_G4_nominal_frozen_w"] == 1.334 and "reading" in sd,
        f"A2's start dependence is computed from the two rows (code path only; E159's int8 full holds stand in): {json.dumps({k: sd[k] for k in ('dW_meas_w', 'dW_G4_w', 'reading')})}")
    say(res["R0_checks_of_C"]["verdict"] == "PASS" and not res["R0_checks_of_C"]["launches_without_check_of_C"],
        f"R0 PASS on E159's session ({res['R0_checks_of_C']['kernel_records']} kernel records, {res['R0_checks_of_C']['work_launches']} work launches, every one with a check of C)")
    say(set(res["all_scored"]["verdict_G4"]) == {"mhz", "w", "die"} and not res["registered_subset"]["complete"], "the verdicts are per quantity; the subset is reported incomplete when holds are missing")
    rd2 = os.path.join(tmp, "cut")
    build_case(rd2, drop="H-02-H2-fp32-randn-r1")
    res2 = RD.reduce(rd2, None, check=False)
    say([x["cell"] for x in res2["rows"]] == ["S1-fp32-randn-cold", "S3-fp32-randn-cold", RD.WARM_ZEROS] and any("processes recorded" in c["why_cut"] for c in res2["cut"]),
        f"a hold missing a process is cut and not scored ({[(c['label'], c['why_cut']) for c in res2['cut']]})")
    rd3 = os.path.join(tmp, "nocheck")
    build_case(rd3, strip_check="H-03-H2-int8-full-r1")
    res3 = RD.reduce(rd3, None, check=False)
    say(any(c["label"] == RD.A2_LABEL and "check of C" in c["why_cut"] for c in res3["cut"]) and res3["A2_reported"]["start_dependence"]["reading"].startswith("NOT RUN or CUT"),
        f"a process with no check-of-C record cuts its hold (here A2's), and A2's reading says so: {res3['A2_reported']['start_dependence']['reading'][:90]}")
    rd4 = os.path.join(tmp, "nocheck-dry")
    s4 = build_case(rd4, strip_check="H-03-H2-int8-full-r1")
    json.dump({"experiment": "E168", "dry": True}, open(os.path.join(s4, "e168.json"), "w"))
    res4 = RD.reduce(rd4, None, check=False)
    say(not res4["cut"] and all("dry" in h for h in res4["complete"]),
        "the same session marked --dry in its e168.json (the toy card writes no check of C) keeps the hold, and every hold record says it is a dry session")
finally:
    shutil.rmtree(tmp)
for dW, dG4, want in ((1.0, 1.334, "SUPPORTED"), (0.05, 1.334, "NO START DEPENDENCE"), (-1.0, 1.334, "OPPOSITE SIGN"), (-0.70, 1.334, "OPPOSITE SIGN"), (0.5, 0.15, "NO READING")):
    cw = {"meas": {"w": 36.0, "die": 56.0, "mhz": 800.0}, "pred": {a: {"w": 36.3, "die": 56.0, "mhz": 800.0} for a in ("G4", "G3_as_frozen", "E136_law")}, "die_start": 55.0}
    cc = copy.deepcopy(cw)
    cc["meas"]["w"] += dW
    cc["pred"]["G4"]["w"] += dG4
    cc["die_start"] = 46.0
    r = RD.a2_reading(cc, cw)
    say(r["reading"].startswith(want) or want in r["reading"], f"A2's reading: dW {dW:+.2f} W against dW_G4 {dG4:+.3f} W reads '{r['reading'][:60]}'")

# 6. the frozen scorer's own self-test, re-run unchanged
G4D = RD.G4DIR
p = subprocess.run([sys.executable, "-B", "score_e168.py", "selftest"], cwd=G4D, capture_output=True, text=True, timeout=600)
committed = open(os.path.join(G4D, "selftest-score-e168.txt")).read()
say(p.returncode == 0 and p.stdout == committed, f"score_e168.py selftest, re-run unchanged, prints exactly the committed selftest-score-e168.txt ({len(p.stdout)} bytes): "
    f"{[ln for ln in p.stdout.splitlines() if ln.startswith('SELFTEST')]}")
p = subprocess.run([sys.executable, "-B", "score_e168.py", "check"], cwd=G4D, capture_output=True, text=True, timeout=120)
say(p.returncode == 0 and p.stdout.strip() == "CHECK OK (9 files)", f"score_e168.py check: {p.stdout.strip()}")
bad, n = RD.freeze_check()
say(not bad and n == 18, f"the 18-file sidecar frozen-sha256-e168-scorer.txt: {n} lines, {18 - len([b for b in bad if b.startswith('sidecar')])} OK")

# 7. the parent's registered verdicts: E159's reduction, unchanged, on E159's committed data
tmpo = tempfile.mkdtemp(prefix="e168-selftest-e159-", dir=os.environ.get("TMPDIR"))
try:
    outj = os.path.join(tmpo, "results.json")
    p = subprocess.run([sys.executable, "-B", "tools/claims-v3/e159/reduce_e159.py", os.path.join(E159, "aifoundry2"), "--out", outj], cwd=ROOT,
                       capture_output=True, text=True, timeout=900)
    got = json.load(open(outj)) if p.returncode == 0 else {}
    ref = json.load(open(os.path.join(E159, "results.json")))
    ok = p.returncode == 0 and got["all_scored"]["verdict_G3"] == ref["all_scored"]["verdict_G3"] and got["registered_subset"]["verdict_G3"] == ref["registered_subset"]["verdict_G3"]
    say(ok, f"E159's registered reduction (reduce_e159.py, unchanged) on E159's committed data reproduces its committed verdicts: all nine "
        f"{got.get('all_scored', {}).get('verdict_G3')}, the subset {got.get('registered_subset', {}).get('verdict_G3')}")
    say(p.returncode == 0 and got["rows"] == ref["rows"], "and its nine scored rows equal the committed results.json's, number for number")
finally:
    shutil.rmtree(tmpo)

print(f"\n{'ALL PASS' if not FAILS else str(len(FAILS)) + ' FAILED'}")
sys.exit(1 if FAILS else 0)
