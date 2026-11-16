#!/usr/bin/env python3
"""E197's checker (Q185, lane kit-e197, Sun 15 Nov 2026, before any E197 datum). Standard library only; it opens no device.

    python3 -I -B check_e197.py drycmp LISTING REGISTERED --host H --out OUT
        The reference session's dry listing (DRY=1 run_session.sh OUT <plan>, with the host H) against the registration's
        (desk/dry-e197-<plan>.txt, made with H=build/host/regfile_host and OUT out-<plan>): the clock stamps "[HH:MM:SS] " are
        dropped, H is written as build/host/regfile_host and OUT as out-<plan>, then every line must be equal. Prints
        "LISTING SAME <plan>: <n> lines, <k> device calls" (exit 0) or "LISTING DIFFERS ..." with the first differing lines (exit 3).
    python3 -I -B check_e197.py summary RUN --plan full|short|ext [--watch WATCH.jsonl]
        The end of a sitting, read from the reference session's own files in RUN (marks.jsonl, runs.jsonl, STOP) and the kit's
        watch log: the runner's smoke gate, the kit's smoke check, the train blocks started and complete, the train processes
        recorded, the stop and whether it names the card (E197.md 6's list: board, die, clock, sampler, a device process ended by its
        timeout or not ending, two failed device processes in a row), and one machine line for step 9 of sitting 2:
        "SITTING-RESULT: smoke <passed|failed|not reached>; train blocks complete <k> (<blocks>); card stop <none|yes: why>". When no
        block of trains.tsv began, it prints "GATE-STOP: <why>" (the session ended before its trains: E197.md 11's "no sitting" rows).
    python3 -I -B check_e197.py checks REGFILE_JSON --out CHECKS_JSON
        After the registered reducer (reduce_regfile.py, unchanged, no --prediction): E197.md 8's rows that the reducer reports, each
        printed in E197.md 8's words with its numbers (gates as the reducer applied them; reports as REPORTED, with the lab's two
        readings of section 8: the I-cache row as the two medians and their ratio, no verdict word; the L1 data miss row as the
        per-launch medians by kind, F beside S, REPORTED). Nothing is scored against any forecast. Prints "CHECKS READ: ..." last.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import re
import sys

STAMP = re.compile(r"^\[\d\d:\d\d:\d\d\] ")
REG_HOST = "build/host/regfile_host"
TRAIN_BLOCKS = ("A", "B", "C", "D", "E")
CARD_WORDS = (  # a stop that names the card (E197.md 6), by its writer's words
    ("stopwatch", "board"), ("stopwatch", "die reading"), ("stopwatch", "newest telemetry sample"), ("stopwatch", "no telemetry sample"),
    ("run_trains", "die reading"), ("run_trains", "telemetry"), ("run_trains", "killed by its timeout"),
    ("run_trains", "two failed device processes"), ("watch_e197", "board"), ("watch_e197", "die reading"),
    ("watch_e197", "minion clock"), ("watch_e197", "still runs"), ("watch_e197", "smoke check"), ("run_trains", "smoke gate"))


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
    m = re.search(r"dry-e197-(full|short|ext)\.txt$", reg)
    plan = m.group(1) if m else "?"

    def norm(ln):
        ln = STAMP.sub("", ln.rstrip("\n"))
        ln = ln.replace(host, REG_HOST).replace(out + "/", "out-%s/" % plan)
        return ln

    have = [norm(ln) for ln in open(lst)]
    want = [STAMP.sub("", ln) for ln in want]
    calls = sum(1 for ln in have if ln.startswith("DRY: timeout 10 "))
    if have == want:
        print("LISTING SAME %s: %d lines, %d device calls (the host written %s, the session's OUT out-%s/, clock stamps dropped)"
              % (plan, len(have), calls, REG_HOST, plan))
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
    wk = [e for e in jl(wl) if e.get("kind") == "smoke_check"] if wl else []
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

    tr = res.get("trains", {})
    for t, x in sorted(tr.items(), key=lambda kv: int(kv[0][1:])):
        dr = x.get("dropped") or {}
        row("%s gates: check_bad 0 and ok; 1,024 participants; clock within 1 MHz; rate within 0.5 %%" % t, "gate",
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
    out = {"checks": rows, "note": "E197.md 8's rows as the registered reducer reports them; nothing is scored against any forecast"}
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
