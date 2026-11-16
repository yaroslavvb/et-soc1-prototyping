#!/usr/bin/env python3
"""E200's checker (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): E197's checker (tools/claims-v3/e197/check_e197.py,
unchanged beside it) with E200's three readings (E200.md 4, 7 and 19.3). Standard library only; it opens no device.

    python3 -I -B check_e200.py drycmp LISTING REGISTERED --host H --out OUT
        The reference session's dry listing with E200's runner (DRY=1 run_session.sh OUT <plan>, with the host H) against E197's
        registered listing (tools/claims-v3/e197/desk/dry-e197-<plan>.txt, made with H=build/host/regfile_host and OUT out-<plan>):
        the clock stamps "[HH:MM:SS] " are dropped, H is written as build/host/regfile_host and OUT as out-<plan>; every device call
        must carry W1's "--window 320000000" and none E197's "--window 240000000" (E200.md 4: W1 is the listings' one difference); with
        W1's window written back as E197's, every line must then be equal. Prints "LISTING SAME <plan>: <n> lines, <k> device calls,
        each with W1's window" (exit 0) or "LISTING DIFFERS ..." with the first differing lines (exit 3).
    python3 -I -B check_e200.py summary RUN --plan full|short|ext [--watch WATCH.jsonl]
        The end of a sitting, read from the reference session's own files in RUN (marks.jsonl, runs.jsonl, STOP) and the kit's
        watch log: the runner's smoke gate, the kit's smoke check (with the smoke's clock, C3), the train blocks started and complete,
        the train processes recorded, the watch's clock verdicts (C3: judged, at 800 MHz, OFF, not judged), the stop and whether it names
        the card (E197.md 6's list, with E200's: board, die, aifoundry2's own lines, C3's clock, sampler, a device process ended by its
        timeout or not ending, two failed device processes in a row), and one machine line for step 9 of sitting 2:
        "SITTING-RESULT: smoke <passed|failed|not reached>; train blocks complete <k> (<blocks>); card stop <none|yes: why>". When no
        block of trains.tsv began, it prints "GATE-STOP: <why>" (the session ended before its trains: E200.md 13's "no train block" rows).
    python3 -I -B check_e200.py checks REGFILE_JSON --out CHECKS_JSON
        After E200's registered reduction (reduce_e200.py: E197's reducer by path and sha256 with C1 and C2, no --prediction): E197.md
        8's rows that the reducer reports, each printed in E197.md 8's words with its numbers, but the clock row, which E200.md 4's C1
        reads (THE CLOCK RULE in place of "within 1 MHz of the session's clock (600 MHz)"), with THE CLOCK RULE'S TALLIES beside it per
        session (E200.md 7: processes judged, kept, set aside by each clause; launches not read before 2.0 s; the anchors' windows) from
        the reduction's "e200" key. Nothing is scored against any forecast (E200.md 0). Prints "CHECKS READ: ..." last.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import re
import sys

STAMP = re.compile(r"^\[\d\d:\d\d:\d\d\] ")
REG_HOST = "build/host/regfile_host"
TRAIN_BLOCKS = ("A", "B", "C", "D", "E")
CARD_WORDS = (  # a stop that names the card (E197.md 6, with E200's watch), by its writer's words
    ("stopwatch", "board"), ("stopwatch", "die reading"), ("stopwatch", "newest telemetry sample"), ("stopwatch", "no telemetry sample"),
    ("run_trains", "die reading"), ("run_trains", "telemetry"), ("run_trains", "killed by its timeout"),
    ("run_trains", "two failed device processes"), ("watch_e200", "board"), ("watch_e200", "die reading"),
    ("watch_e200", "the clock (C3)"), ("watch_e200", "still runs"), ("watch_e200", "smoke check"), ("run_trains", "smoke gate"))
W1_WINDOW, E197_WINDOW = "--window 320000000", "--window 240000000"


def jl(path):
    out = []
    try:
        with open(path) as f:
            for ln in f:
                ln = ln.strip()
                if ln.startswith("{") and ln.endswith("}"):
                    try:
                        v = json.loads(ln)
                    except ValueError:
                        continue
                    if isinstance(v, dict):
                        out.append(v)
    except OSError:
        pass
    return out


def drycmp(argv):
    lst, reg = argv[0], argv[1]
    host = argv[argv.index("--host") + 1]
    out = argv[argv.index("--out") + 1].rstrip("/")
    want = [ln.rstrip("\n") for ln in open(reg)]
    m = re.search(r"dry-e197-(full|short|ext)\.txt$", reg)   # E197's registered listings: E200's are E197's but W1
    plan = m.group(1) if m else "?"

    def norm(ln):
        ln = STAMP.sub("", ln.rstrip("\n"))
        ln = ln.replace(host, REG_HOST).replace(out + "/", "out-%s/" % plan)
        return ln

    raw = [norm(ln) for ln in open(lst)]
    want = [STAMP.sub("", ln) for ln in want]
    devs = [ln for ln in raw if ln.startswith("DRY: timeout 10 ")]
    calls = len(devs)
    w1 = sum(1 for ln in devs if (" " + W1_WINDOW + " ") in (ln + " "))
    old = sum(1 for ln in raw if E197_WINDOW in ln)
    if calls == 0 or w1 != calls or old:
        print("LISTING DIFFERS %s: %d device calls, %d with W1's '%s', %d lines with E197's '%s' (E200.md 4: every device call carries "
              "W1's window and none E197's)" % (plan, calls, w1, W1_WINDOW, old, E197_WINDOW))
        return 3
    have = [ln.replace(W1_WINDOW, E197_WINDOW) if ln.startswith("DRY: timeout 10 ") else ln for ln in raw]
    if have == want:
        print("LISTING SAME %s: %d lines, %d device calls, each with W1's window (the host written %s, the session's OUT out-%s/, "
              "clock stamps dropped; W1's window written back as E197's)" % (plan, len(have), calls, REG_HOST, plan))
        return 0
    for i, (x, y) in enumerate(zip(have, want)):
        if x != y:
            print("LISTING DIFFERS %s at line %d:\n  box:  %s\n  reg:  %s" % (plan, i + 1, x[:200], y[:200]))
            break
    else:
        print("LISTING DIFFERS %s: %d lines against the registration's %d" % (plan, len(have), len(want)))
    return 3


def stop_info(run):
    p = os.path.join(run, "STOP")
    if not os.path.exists(p):
        return None
    try:
        txt = open(p).read()
    except OSError:
        txt = ""
    first = txt.splitlines()[0] if txt.strip() else ""
    try:
        j = json.loads(first)
        if not isinstance(j, dict):
            raise ValueError
    except ValueError:
        return {"by": "by hand", "why": (first or "an empty STOP file")[:200], "card": False}
    by, why = str(j.get("by", "?")), str(j.get("why", "?"))
    card = j.get("card") if isinstance(j.get("card"), bool) else any(by == b and w in why for b, w in CARD_WORDS)
    return {"by": by, "why": why, "card": bool(card), "t_ms": j.get("t_ms")}


def summary(argv):
    run = argv[0]
    plan = argv[argv.index("--plan") + 1]
    wl = argv[argv.index("--watch") + 1] if "--watch" in argv else None
    marks, runs = jl(os.path.join(run, "marks.jsonl")), jl(os.path.join(run, "runs.jsonl"))
    g = [m for m in marks if m.get("kind") == "smoke_gate"]
    if not g:
        smoke = "not reached"
    else:
        smoke = "passed" if g[0].get("ok") is True else "failed"
    wl_ev = jl(wl) if wl else []
    wk = [e for e in wl_ev if e.get("kind") == "smoke_check"]
    ck = [e for e in wl_ev if e.get("kind") == "clock"]
    kit = "not reached" if not wk else ("passed" if wk[0].get("ok") else "FAILED: " + "; ".join(wk[0].get("reasons", []))[:300])
    plan_blocks = ["E"] if plan == "ext" else ["A", "B", "C", "D"]
    # a block began when it wrote an idle, anchor or train mark (a stop_seen mark at its first check, or a skipped mark, is no start)
    started = [b for b in plan_blocks if any(m.get("block") == b and m.get("kind") in ("idle", "anchor", "train") for m in marks)]
    complete = [b for b in plan_blocks if any(m.get("block") == b and m.get("kind") == "idle" and m.get("label") == "after"
                                             for m in marks)]
    tprocs = sum(1 for m in marks if m.get("kind") == "train" and m.get("block") in TRAIN_BLOCKS)
    cuts = [m for m in marks if m.get("kind") in ("cut", "skipped")]
    st = stop_info(run)
    print("the runner's smoke gate: %s%s" % (smoke, (" (%d launches, rates %s-%s)" % (g[0].get("launches", 0), g[0].get("rate_min"),
                                                                                      g[0].get("rate_max"))) if g else ""))
    print("the kit's smoke check: %s" % kit)
    print("train blocks started: %d of %d (%s); complete: %d (%s); train processes recorded: %d" % (
        len(started), len(plan_blocks), " ".join(started) or "none", len(complete), " ".join(complete) or "none", tprocs))
    print("the clock (C3, the kit's watch): train processes judged %d; at 800 MHz %d; OFF %d; not judged %d; the longest OFF run %d" % (
        sum(1 for e in ck if e.get("verdict") in ("800", "OFF")), sum(1 for e in ck if e.get("verdict") == "800"),
        sum(1 for e in ck if e.get("verdict") == "OFF"), sum(1 for e in ck if e.get("verdict") == "not judged"),
        max([e.get("run", 0) for e in ck] or [0])))
    for c in cuts:
        print("the deadline: %s %s in block %s%s" % (c.get("kind"), c.get("train"), c.get("block"),
                                                     (" before process %s of %s" % (c.get("proc"), c.get("processes"))) if c.get("kind") == "cut" else ""))
    if st:
        print("stop: %s: %s (%s)" % (st["by"], st["why"][:300], "names the card" if st["card"] else "does not name the card"))
    else:
        print("stop: none")
    cs = "none" if not st or not st["card"] else "yes: %s: %s" % (st["by"], st["why"][:160])
    print("SITTING-RESULT: smoke %s; train blocks complete %d (%s); card stop %s" % (
        "passed" if smoke == "passed" and kit == "passed" else ("failed" if "fail" in (smoke + kit).lower() else "not reached"),
        len(complete), " ".join(complete) or "none", cs))
    if not started:
        why = st["why"][:240] if st else ("the runner's smoke gate failed" if smoke == "failed" else "no block began")
        print("GATE-STOP: no block of trains.tsv began (%s)" % why)
    return 0


def checks(argv):
    res = json.load(open(argv[0]))
    outp = argv[argv.index("--out") + 1] if "--out" in argv else None
    rows, words = [], []

    def row(name, kind, verdict, detail):
        rows.append({"check": name, "kind": kind, "verdict": verdict, "detail": detail})
        print("%-70s %-8s %s" % (name[:70], verdict, json.dumps(detail)[:400]))
        words.append(verdict)

    e2 = res.get("e200")
    if not isinstance(e2, dict) or not isinstance(e2.get("sessions"), list):
        print("CHECKS REFUSED: the result has no 'e200' key: it is not reduce_e200.py's output (E200.md 6)")
        return 3
    for S in e2["sessions"]:
        row("THE CLOCK RULE (C1) for %s: the session's median clock 800 MHz within 1 MHz; each train process kept only if every sample "
            "from its first launch + 1.5 s to its last launch's end reads 800 MHz within 1 MHz and its last launch ran at 780-810 MHz "
            "by its own count; nothing read before 2.0 s (C2)" % S.get("session"), "gate", "APPLIED" if S.get("median_clock_ok") else "NOT 800",
            {k: S.get(k) for k in ("median_clock_mhz", "median_clock_ok", "processes_judged", "processes_kept_by_clock",
                                    "set_aside_median_clock", "set_aside_samples_after_allowance", "set_aside_no_last_launch",
                                    "set_aside_own_count", "launches_asked", "launches_before_2s_not_read", "launches_read_as_e197",
                                    "launches_unmatched", "anchor_groups", "anchor_board_windows_moved",
                                    "anchor_bursts_off_800_after_allowance", "samples_with_t", "samples_without_clock",
                                    "samples_off_800")})
    tr = res.get("trains", {})
    for t, x in sorted(tr.items(), key=lambda kv: int(kv[0][1:])):
        dr = x.get("dropped") or {}
        row("%s gates: check_bad 0 and ok; 1,024 participants; the clock by THE CLOCK RULE (C1: E197.md 8's clock row read by E200.md "
            "4); rate within 0.5 %%" % t, "gate",
            "APPLIED", {"processes": x.get("processes"), "planned": x.get("planned"), "units": x.get("units"), "dropped": dr})
        rr = x.get("rate_ratio_F_over_S")
        ns = x.get("sign") == "NOT SCORED"
        row("%s gate: F and S median rates within 0.05 %%; at least 8 units" % t, "gate",
            "NOT SCORED" if ns else "PASS", {"rate_ratio_F_over_S": rr, "units": x.get("units")})
        bk = x.get("by_kind") or {}
        ret = {L: (v.get("retired_per_body"), v.get("retired_flag")) for L, v in bk.items()}
        row("%s report: retired / body within 0.5 %% of 131/128 plus the entry and exit, per kind" % t, "report",
            "FLAGGED" if any(f for _, f in ret.values()) else "REPORTED", {"retired_per_body": ret})
        icm = {L: v.get("icache_miss_per_iter") for L, v in bk.items()}
        ratio = None
        if icm.get("F") and icm.get("S"):
            ratio = icm["F"] / icm["S"]
        row("%s report: instruction-cache misses per iteration for F and S (the two medians and their ratio)" % t, "report",
            "REPORTED", {"icache_miss_per_iter": icm, "F_over_S": ratio})
        row("%s report: L1 data misses, per-launch median by kind, F beside S (the kernel's entry and exit included)" % t,
            "report", "REPORTED", {L: v.get("l1d_miss_median") for L, v in bk.items()})
        row("%s report: launches with a hart's iterations more than 1 %% below the mean hart's" % t, "report", "REPORTED",
            {L: v.get("launches_with_a_slow_hart") for L, v in bk.items()})
        row("%s report: rail voltage samples beyond +-3 mV of the session median in the train's spans" % t, "report",
            "REPORTED", {"off_and_samples": x.get("rail_mv_samples_off_3mV")})
    dr = res.get("anchor_drift") or []
    row("the anchors' first and last bursts of a block within 0.3 W", "report",
        "FLAGGED" if any(d.get("flag") for d in dr) else "REPORTED",
        {"flagged": [(d.get("session"), d.get("block"), d.get("kind"), d.get("last_minus_first_w")) for d in dr if d.get("flag")],
         "pairs": len(dr)})
    g = res.get("train_gain")
    row("the train gain (T3 over the anchors' burst difference) within 0.95-1.05 (outside: the gain-corrected prices first)",
        "report", "FLAGGED" if res.get("train_gain_flag") else ("REPORTED" if g is not None else "NOT COMPUTED"), {"train_gain": g})
    row("the cell reading (order, T2, BOUNDED: cell; else cell_ctrl first)", "reading rule", "REPORTED", res.get("cell_reading"))
    row("the stops seen by the reducer (a process ending after a STOP gives no value)", "gate", "APPLIED", {"stops": res.get("stops")})
    out = {"checks": rows, "note": "E197.md 8's rows as E200's registered reduction reports them, the clock row read by C1 with its "
           "tallies (E200.md 4 and 7); nothing is scored against any forecast"}
    if outp:
        with open(outp, "w") as f:
            json.dump(out, f, indent=1)
            f.write("\n")
    n = {w: words.count(w) for w in sorted(set(words))}
    print("CHECKS READ: %d rows (%s)" % (len(rows), ", ".join("%s %d" % kv for kv in n.items())))
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "drycmp" and len(rest) >= 2:
        return drycmp(rest)
    if cmd == "summary" and rest:
        return summary(rest)
    if cmd == "checks" and rest:
        return checks(rest)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
