#!/usr/bin/env python3
"""E101, session 2: the self-test of what is new in this folder, before any card has run. NOTHING HERE IS A MEASUREMENT.

    python3 selftest_e101s.py > selftest.txt

1. The slot parser on the night's format. 2. A login ending a session: the queue waits while `who` shows it, resumes as s2 with the first session's runs skipped, and stops resuming at the slot's give-up time. 3. The runner's skip of recorded runs. 4. The smoke's cycle band.
"""
import json
import os
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import queue_e101s as Q  # noqa: E402

bad = 0


def check(name, got, want):
    global bad
    ok = got == want
    bad += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {got}" + ("" if ok else f" (expected {want})"))


with tempfile.TemporaryDirectory() as td:
    slots = os.path.join(td, "slots.txt")
    open(slots, "w").write("SLOT E96: start 1793527500 (x), end 1793532000 (y): z\nSLOT E101: start 1793535600 (12:20 UTC = 04:20 PST), end 1793540100 (13:35 UTC = 05:35 PST): a real matmul\n"
                           "E98 P3: rest reading starts 1793533200 (x)\nE98 P6: rest reading starts 1793541300 (13:55 UTC = 05:55 PST); the card\n")
    a, b, nxt = Q.parse_slots(slots)
    check("slot start", a, 1793535600000)
    check("slot end", b, 1793540100000)
    check("next rest", nxt, 1793541300000)

    # the queue's loop with its parts stubbed: the session is ended by a login, the login goes, the second session runs out the plan
    args = types.SimpleNamespace(slots=slots, runs=os.path.join(td, "runs"), protocol="x", cap=72.0, give_up_min=25.0, cap_margin_s=180.0, root=td, dry=True)
    q = Q.Queue(args)
    Q.POLL_S = 0
    log = []
    calls = {"who": 0}
    q.wait_for_slot = lambda: True
    q.snapshot = lambda tag: {"tag": tag}
    q.copy_history = lambda *x: 0
    q.check_smoke = lambda: None
    q.stop_ms = Q.now_ms() + 3600000
    q.end_ms = Q.now_ms() + 3780000
    q.give_up_ms = Q.now_ms() + 2000000

    def retry(name, only=None, cap_fn=None):
        log.append((name, list(q.skip_done)))
        return 0 if name == "smoke" else (3 if name == "s1" else 0)

    def who():
        calls["who"] += 1
        return "1 other user(s) logged in" if calls["who"] <= 2 else None
    q.session_retry = retry
    q.why_not_free = who
    q.run()
    check("sessions and what each skips", log, [("smoke", []), ("s1", []), ("s2", ["s1"])])
    check("the wait looked at who until it was clear", calls["who"], 3)

    # the same with the login still there at the give-up time: no resume
    args2 = types.SimpleNamespace(**{**vars(args), "runs": os.path.join(td, "runs2")})
    q2 = Q.Queue(args2)
    q2.wait_for_slot = lambda: True
    q2.snapshot = lambda tag: {"tag": tag}
    q2.copy_history = lambda *x: 0
    q2.check_smoke = lambda: None
    q2.stop_ms = Q.now_ms() + 3600000
    q2.end_ms = Q.now_ms() + 3780000
    q2.give_up_ms = Q.now_ms() - 1
    log2 = []

    def retry2(name, only=None, cap_fn=None):
        log2.append(name)
        return 0 if name == "smoke" else 3
    q2.session_retry = retry2
    q2.why_not_free = lambda: "1 other user(s) logged in"
    q2.run()
    check("a login that stays past the give-up time ends the queue", log2, ["smoke", "s1"])
    recs = [json.loads(x) for x in open(os.path.join(args2.runs, "queue.jsonl"))]
    check("no login name in the queue's record", [r for r in recs if r.get("kind") == "no_resume"][0]["why"], "1 other user(s) logged in")

    # the runner's skip
    done = os.path.join(td, "s1")
    os.makedirs(done)
    P = os.path.join(HERE, "protocol-dry.json")
    env = dict(os.environ)
    r0 = subprocess.run([sys.executable, os.path.join(HERE, "run_e101s.py"), "--protocol", P, "--out", os.path.join(td, "x"), "--list"], capture_output=True, text=True, env=env)
    names = [ln.split()[0] for ln in r0.stdout.splitlines() if ln.startswith(("BURST-", "SUS-", "WARM-", "SUSX-"))]
    with open(os.path.join(done, "runs.jsonl"), "w") as f:
        for n in names[:5]:
            f.write(json.dumps({"run": n}) + "\n")
    env["E101_SKIP_DONE"] = done
    r1 = subprocess.run([sys.executable, os.path.join(HERE, "run_e101s.py"), "--protocol", P, "--out", os.path.join(td, "x"), "--list"], capture_output=True, text=True, env=env)
    names1 = [ln.split()[0] for ln in r1.stdout.splitlines() if ln.startswith(("BURST-", "SUS-", "WARM-", "SUSX-"))]
    check("the runs recorded are skipped, the rest kept in order", names1, names[5:])
    check("the plan's blocks", sorted({n.split("-")[0] for n in names}), ["BURST", "SUS", "SUSX", "WARM"])

check("the smoke's cycle band: 529 against 529", Q.CYC_LO <= 529.0 / 529.0 <= Q.CYC_HI, True)
check("the smoke's cycle band: 546 against 740, the wrong kernel", Q.CYC_LO <= 546.0 / 740.16 <= Q.CYC_HI, False)
check("the smoke's cycle band: 1000 against 740", Q.CYC_LO <= 1000.0 / 740.16 <= Q.CYC_HI, True)
print("SELFTEST", "PASS" if not bad else "FAIL")
sys.exit(1 if bad else 0)
