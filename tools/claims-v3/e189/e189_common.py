#!/usr/bin/env python3
"""E189's kit (Q167, Thu 12 Nov 2026, before any E189 datum): what the box runner, the doubles, the collector and the desk tests share.

Python's own modules only (it runs on aifoundry3 under the system python3, and on the Intel under /usr/bin/python3 -I -B).
It reads the registration's plan-e189.json (K, the order, the stops, the die gate, the cap) and never changes it; it adds:
  - the two hosts' command lines for each configuration (E189.md section 4, the kit's build paths);
  - the smoke's ramped runs (E189.md section 10: --selftest, one launch of each program at a small size, the copy at 64 MiB before 1 GiB);
  - THE ADAPTER of E189.md section 8.1: the ledger host's own JSON line into the reducer's fields (host.json), so that
    workloads/sparseparity/tools/energy_reduce.py, unchanged, reads a ledger pass as it reads a sparse-parity one;
  - THE STOP LINES (E189.md section 11), one function a live sample goes through: board >= 65 W, minshire[0] >= 70 C, a sample off
    600 MHz taken in a pass (the first sets its pass aside, the second stops the session; outside a pass it is recorded only);
  - the cap (no pass after 108 card-minutes from the first card command) and the die gate (60 C, at most 10 minutes).
SPDX-License-Identifier: Apache-2.0
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PLAN = os.path.join(HERE, "plan-e189.json")
ORDER = ["copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled", "sparse-parity"]
LEDGER = ORDER[:5]
PROGRAM = {k: ("ledger" if k in LEDGER else "spp") for k in ORDER}
# the box's build directories (build_e189.sh writes them; the tree is aifoundry3's ~/aifoundry)
LEDGER_HOST = "build/e189ledger/host/ledger_host"
LEDGER_ELF = "build/e189ledger/kernel/ledger.elf"
SPP_HOST = "build/e189spp/host/sparseparity_host"
SPP_ELF = "build/e189spp/kernel/sparseparity.elf"
GUARD = "tools/claims-v3/e128/ettelem_guard.sh"      # E128's allow-list in front of build/ettelem/ettelem (READ commands only)
LOCK = "/run/lock/etsoc-shire0.lock"
EXPECT_SMOKE = "docs/reports/data/2026-11-12-q166-progs/digests/expect-b2048-r1-2048.txt"
IDLE_BEFORE_S, IDLE_AFTER_S, EVERY_MS = 8.0, 10.0, 100      # energy.sh's form (E189.md section 9)
HOST_TIMEOUT_S = 10                                         # every device-opening process under `timeout 10`
ANCHOR_S = 120                                              # three 2-minute idle anchors (E189.md section 10)
CAP_PASS_START_S = 108 * 60                                 # no pass starts after 108 card-minutes (E189.md section 10)
CAP_S = 110 * 60
DIE_GATE_C, DIE_GATE_WAIT_S, DIE_LOW_C = 60, 600, 52        # E189.md section 11; below 52 C does not block, it is labelled
STOP_BOARD_W, STOP_DIE_C, CLOCK_MHZ = 65.0, 70.0, 600
CLOSE_CONFIG_S = 15                                         # the end bound: the closing config read's share of the last
                                                            # seconds before 110 card-minutes (run_e189.py stop_sampler)


def plan():
    with open(PLAN) as f:
        return json.load(f)


def sequence(p=None):
    """The session's sequence as plan-e189.json writes it: ('anchor', n) and ('pass', config, k, order_index) items, in order."""
    p = p or plan()
    seq, seen, idx = [("anchor", 1)], {}, 0
    rounds = p["order"]["rounds"]
    for r, rnd in enumerate(rounds):
        for cfg in rnd:
            seen[cfg] = seen.get(cfg, 0) + 1
            idx += 1
            seq.append(("pass", cfg, seen[cfg], idx))
        if r == 1:
            seq.append(("anchor", 2))
    seq.append(("anchor", 3))
    return seq


def check_sequence(p=None):
    """The written-out sequence (plan > order > sequence) equals the one built from the rounds: never re-drawn."""
    p = p or plan()
    words = [s for s in p["order"]["sequence"] if s.startswith("pass ")]
    built = [f"pass {it[3]}: {it[1]} p{it[2]}" for it in sequence(p) if it[0] == "pass"]
    return words == built and len(built) == 24


def host_argv(cfg, p=None, pass_dir=None):
    """One pass's host command line (without `timeout 10`), from the box tree's root."""
    p = p or plan()
    c = p["configs"][cfg]
    if PROGRAM[cfg] == "ledger":
        return [LEDGER_HOST, "--card"] + c["args"].split() + ["--kernel", LEDGER_ELF]
    rec = os.path.join(pass_dir, "host.rec") if pass_dir else "host.rec"
    return [SPP_HOST] + c["args"].split() + c["reps_flag"].split() + ["--kernel", SPP_ELF, "--records-out", rec]


def smoke_runs(programs):
    """The ramped smoke (E189.md section 10), for the programs built today: (name, argv, what it must show)."""
    out = []
    if "ledger" in programs:
        out.append(("ledger-selftest", [LEDGER_HOST, "--selftest"], "selftest"))
        base = [LEDGER_HOST, "--card", "--kernel", LEDGER_ELF, "--launches", "1"]
        out += [("copy-64m-random", base + ["--prog", "copy", "--bytes", "64M", "--passes", "1", "--data", "random", "--width", "32"], "ledger"),
                ("copy-64m-zeros", base + ["--prog", "copy", "--bytes", "64M", "--passes", "1", "--data", "zeros", "--width", "32"], "ledger"),
                ("copy-1g-random", base + ["--prog", "copy", "--bytes", "1G", "--passes", "1", "--data", "random", "--width", "32"], "ledger"),
                ("sha256-b2048-r1", base + ["--prog", "sha256", "--block", "2048", "--repeat", "1", "--expect", EXPECT_SMOKE], "ledger"),
                ("sort-shuffled-r1", base + ["--prog", "sort", "--keys", "512", "--reps", "1", "--order", "shuffled"], "ledger"),
                ("sort-sorted-r1", base + ["--prog", "sort", "--keys", "512", "--reps", "1", "--order", "sorted"], "ledger")]
    if "spp" in programs:
        c = plan()["configs"]["sparse-parity"]
        out.append(("sparse-parity-r1", [SPP_HOST] + c["args"].split() + ["--reps", "1", "--kernel", SPP_ELF], "spp"))
    return out


def last_json(text):
    for ln in reversed(text.splitlines()):
        if ln.startswith("{"):
            try:
                return json.loads(ln)
            except ValueError:
                return {}
    return {}


def ledger_good(raw):
    """Every check of the ledger host's line but the launch count (main.cpp's pass condition without `launched == launches`)."""
    P = raw.get("participants")
    ok = (raw.get("records_bad") == 0 and P and raw.get("records_ok") == P and raw.get("units") == raw.get("units_expected")
          and (raw.get("checked") or 0) > 0 and raw.get("mismatches") == 0 and raw.get("expect_mismatches", 0) == 0)
    return bool(ok)     # SHA-256's --expect over every participant is the scorer's own check (score_e189.read_pass)


def adapt_ledger(raw, K):
    """THE ADAPTER (E189.md section 8.1): the ledger host's line -> the reducer's fields. reps_done = launches; reps_requested = K;
    launch_s = wall_s; launch_epoch_ms = [the first launch's t0, the last launch's t1]; status as the host said it; problems
    ["reps: k of K done"] when the budget cut the burst short with every other check good (the reducer then flags it, never fails
    it); otherwise, when the host said FAIL, the checks that failed (the reducer then fails the pass: a FAILED RUN, not a datum)."""
    n = int(raw.get("launches") or 0)
    ep = raw.get("launch_epoch_ms") or []
    good = ledger_good(raw)
    short = good and 0 < n < K and raw.get("status") != "PASS"
    out = {"adapter": "e189_common.adapt_ledger (E189.md section 8.1)", "ledger_prog": raw.get("prog"),
           "status": raw.get("status"), "reps_requested": K, "reps_done": n,
           "launch_s": [float(x) for x in (raw.get("wall_s") or [])],
           "launch_epoch_ms": [ep[0], ep[-1]] if len(ep) >= 2 else [0, 0],
           "kernel": {"cycles_max": (raw.get("hart0_cycles") or {}).get("max")},
           "problems": [], "stop_reason": ""}
    if raw.get("status") == "PASS":
        out["reps_consistent"] = "ok"
    elif short:
        out["reps_consistent"] = "ok"
        out["problems"] = [f"reps: {n} of {K} done"]
        out["stop_reason"] = "budget"
    else:
        why = (f"records_ok {raw.get('records_ok')} of {raw.get('participants')}, records_bad {raw.get('records_bad')}, "
               f"units {raw.get('units')} of {raw.get('units_expected')}, checked {raw.get('checked')}, mismatches "
               f"{raw.get('mismatches')}, expect_mismatches {raw.get('expect_mismatches')}, first_mismatch "
               f"'{raw.get('first_mismatch')}', launches {n} of {K}")
        out["reps_consistent"] = "bad"
        out["problems"] = ["checks: " + why] if raw else ["no JSON line from the ledger host"]
    return out


class Stops:
    """THE STOP LINES on live samples (E189.md section 11). feed(sample, in_pass) returns the actions it implies, in order:
    'set-aside' (the first sample off 600 MHz taken in a pass), 'stop' (board >= 65 W or minshire[0] >= 70 C on any live sample, or a
    second sample off 600 MHz taken in a pass). THE CLOCK LINE counts only the samples taken in a pass, as E189.md 11 words it ("the first
    sample off it sets its pass aside; a second one, in any pass, stops the session"): a sample off the clock outside a pass (an anchor,
    the smoke, between passes) is recorded in events with counted False and reported, and sets nothing aside and stops nothing (fixed Fri
    13 Nov 2026 before any datum, verify-e189's nit: the first kit counted every session sample). A pass is the runner's whole pass, from
    its first idle second to its last (in_pass). A test threshold (the stop-path test) is passed in; the real ones are the registration's."""

    def __init__(self, board_w=STOP_BOARD_W, die_c=STOP_DIE_C, clock_mhz=CLOCK_MHZ):
        self.board_w, self.die_c, self.clock_mhz = board_w, die_c, clock_mhz
        self.off_clock = 0          # the samples off the clock taken in a pass (the line's count)
        self.stop = None
        self.events = []            # every sample off the clock, in a pass or not

    def feed(self, s, in_pass):
        acts = []
        bw = s.get("board_w")
        die = ((s.get("temp_c") or {}).get("minshire") or [None])[0]
        mhz = (s.get("mhz") or {}).get("minion")
        t = s.get("t_ms")
        if bw is not None and bw >= self.board_w and not self.stop:
            self.stop = f"board {bw} W at or above {self.board_w:g} W"
            acts.append("stop")
        if die is not None and die >= self.die_c and not self.stop:
            self.stop = f"minshire[0] {die} C at or above {self.die_c:g} C"
            acts.append("stop")
        if mhz is not None and mhz != self.clock_mhz:
            if in_pass:
                self.off_clock += 1
            self.events.append({"t_ms": t, "minion_mhz": mhz, "n": self.off_clock if in_pass else None,
                                "in_pass": bool(in_pass), "counted": bool(in_pass)})
            if in_pass and self.off_clock == 1:
                acts.append("set-aside")
            if in_pass and self.off_clock >= 2 and not self.stop:
                self.stop = f"a second sample off {self.clock_mhz} MHz in a pass ({mhz} MHz)"
                acts.append("stop")
        return acts


def die_of(s):
    return ((s.get("temp_c") or {}).get("minshire") or [None])[0]


if __name__ == "__main__":
    # a self-check of the pieces that need no card: the sequence as written, the commands, the adapter's three cases, the stop lines
    import sys
    p = plan()
    bad = []
    if not check_sequence(p):
        bad.append("the sequence differs from plan-e189.json's written order")
    ks = {k: p["configs"][k]["launches_K"] for k in ORDER}
    if ks != {"copy-zeros": 8, "copy-random": 8, "sha256": 9, "sort-sorted": 8, "sort-shuffled": 7, "sparse-parity": 9}:
        bad.append(f"K {ks}")
    for k in LEDGER:
        a = host_argv(k, p)
        if f"--launches {ks[k]}" not in " ".join(a) or "--card" not in a:
            bad.append(f"{k} argv {a}")
    if "--expect" not in host_argv("sha256", p):
        bad.append("sha256 without --expect")
    a = host_argv("sparse-parity", p, "X")
    if a[a.index("--reps") + 1] != "9" or "--budget" not in a:
        bad.append(f"sparse parity argv {a}")
    raw = {"prog": "copy", "participants": 2048, "records_ok": 2048, "records_bad": 0, "units": 5, "units_expected": 5,
           "checked": 2048, "mismatches": 0, "expect_mismatches": 0, "launches": 6, "wall_s": [0.6] * 6,
           "launch_epoch_ms": [1, 2, 3, 4], "hart0_cycles": {"max": 393600000}, "status": "FAIL"}
    h = adapt_ledger(raw, 8)
    if not (h["problems"] == ["reps: 6 of 8 done"] and h["reps_consistent"] == "ok" and h["launch_epoch_ms"] == [1, 4]):
        bad.append(f"adapter short {h}")
    raw2 = dict(raw, mismatches=1, first_mismatch="participant 7", launches=8)
    h2 = adapt_ledger(raw2, 8)
    if not (h2["reps_consistent"] == "bad" and h2["problems"][0].startswith("checks:")):
        bad.append(f"adapter fail {h2}")
    h3 = adapt_ledger(dict(raw, launches=8, status="PASS"), 8)
    if not (h3["problems"] == [] and h3["reps_done"] == 8 and h3["status"] == "PASS"):
        bad.append(f"adapter pass {h3}")
    # THE STOP LINES (fixed Fri 13 Nov 2026): the clock line counts in-pass samples only (E189.md 11); board and die trip anywhere
    def smp(mhz=600, bw=30.0, die=55):
        return {"t_ms": 1, "board_w": bw, "temp_c": {"minshire": [die, die - 1, die + 1]}, "mhz": {"minion": mhz}}
    st = Stops()
    acts = [st.feed(smp(800), None), st.feed(smp(800), None), st.feed(smp(800), "copy-zeros/p1"), st.feed(smp(600), "copy-zeros/p1"),
            st.feed(smp(800), None), st.feed(smp(800), "sha256/p1")]
    if not (acts == [[], [], ["set-aside"], [], [], ["stop"]] and st.off_clock == 2 and len(st.events) == 5
            and [e["counted"] for e in st.events] == [False, False, True, False, True] and "in a pass" in (st.stop or "")):
        bad.append(f"clock line {acts} {st.events} {st.stop}")
    st2 = Stops()
    if not (st2.feed(smp(800), "x/p1") == ["set-aside"] and st2.feed(smp(800), "x/p1") == ["stop"]):
        bad.append("clock line: two samples in one pass did not set aside and stop")
    st3 = Stops()
    if not (st3.feed(smp(bw=65.0), None) == ["stop"] and Stops().feed(smp(die=70), None) == ["stop"]
            and Stops().feed(smp(bw=64.99, die=69), "x/p1") == []):
        bad.append("board or die line outside a pass, or a sample under both, read wrong")
    print("E189-COMMON SELF-CHECK " + ("PASS" if not bad else "FAIL: " + "; ".join(bad)))
    sys.exit(0 if not bad else 1)
