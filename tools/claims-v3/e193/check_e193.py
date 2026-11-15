#!/usr/bin/env python3
"""E193's checker (Q177, lane kit-e193, Sat 14 Nov 2026, before any E193 datum): the kit's readers of what run_x04.py (registered,
unchanged) writes. One file, five modes; standard library only, but `checks`, which imports numpy through the registered reducer.

    python3 -I -B check_e193.py smoke DIR --rc N           the kit's smoke gate (on the box, by session_e193.sh): SMOKE GO / SMOKE NO-GO
    python3 -I -B check_e193.py stopreason DIR             why a runner call ended: "stop: <reason>", "no stop: done" or "no stop recorded"
    python3 -I -B check_e193.py drycmp LISTING REGISTERED --host PATH
                                                           a dry listing against the registration's (desk/dry-e193-*.txt), the host's path
                                                           written as the registration's: LISTING SAME / LISTING DIFFERS
    python3 -I -B check_e193.py summary DIR                a runner call's facts for the data README (calls, launches, passes, stops,
                                                           telemetry: samples, 600 MHz, board and die peaks); never a verdict
    python3 -I -B check_e193.py checks X04JSON DIR [--out FILE]
                                                           E193.md section 8's nine checks after the reduction: 1-7 read from the reducer's
                                                           x04.json, 8's count of readings the dip rule dropped (the reducer gives none)
                                                           and 9 by section 8's reading (less than half of the session's spin2 rate)

THE SMOKE GATE (E193.md 5: "every launch ok, every device process exit 0 ... its telemetry (600 MHz, below every stop)"): the runner
exited 0 and wrote no STOPPED, its log ends "done"; its log lists exactly the registered smoke's ten device processes in order (desk/
dry-e193-smoke-all.txt, read beside this file: block and arm), each "exit 0" with at least one launch, the train's with 12; runs.jsonl
holds every one of those launches, each "ok": true and "rc": 0, the train's three a segment and not short; the smoke's telemetry has at
least 150 samples, every one with mhz.minion 600 and board_w at most 65 W and temp_c.minshire[0] under 70 C (the runner's stop lines).
The smoke is never reduced as data.

CHECK 8 counts, in every window the registered reducer evaluates with its dip rule (each run's busy window and its two idle windows,
each train segment's window), the board readings more than 4 W below that window's median: the reducer's own Series, windows and
grouping, imported from proposal/src/reduce_x04.py by path (never copied, never changed). A reading inside two windows counts in each.
Exit 0 (GO, SAME, read), 3 (NO-GO, DIFFERS, a gate), 2 (usage). SPDX-License-Identifier: Apache-2.0
"""
import collections
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SMOKE_LISTING = os.path.join(HERE, "desk", "dry-e193-smoke-all.txt")
REDUCER = os.path.join(HERE, "proposal", "src", "reduce_x04.py")
REG_HOST = "build/x04clock/host/x04clock_host"
CALL_RE = re.compile(r"^pass (\d+) block (\S+) (\S+): (\d+) launches, exit (-?\d+)")
BOARD_STOP_W, DIE_STOP_C, CLOCK_MHZ = 65.0, 70.0, 600.0


def jl(path):
    out = []
    try:
        with open(path, errors="replace") as f:
            for ln in f:
                ln = ln.strip()
                if ln.startswith("{"):
                    try:
                        out.append(json.loads(ln))
                    except ValueError:
                        pass
    except OSError:
        pass
    return out


def lines(path):
    try:
        with open(path, errors="replace") as f:
            return f.read().splitlines()
    except OSError:
        return []


def registered_calls(listing):
    """[(block, arm)] of the device processes in a registered dry listing, in order."""
    calls = []
    for ln in lines(listing):
        m = CALL_RE.match(ln)
        if m:
            calls.append((m.group(2), m.group(3)))
    return calls


def log_calls(d):
    return [(int(m.group(1)), m.group(2), m.group(3), int(m.group(4)), int(m.group(5)))
            for m in (CALL_RE.match(x) for x in lines(os.path.join(d, "run.log"))) if m]


def die(s):
    try:
        return float(s["temp_c"]["minshire"][0])
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def mhz(s):
    try:
        return float((s.get("mhz") or {}).get("minion"))
    except (TypeError, ValueError):
        return None


def stopreason(d):
    p = os.path.join(d, "STOPPED")
    if os.path.exists(p):
        return "stop: " + (lines(p) or ["(empty STOPPED)"])[0]
    ev = [e for e in jl(os.path.join(d, "events.jsonl")) if e.get("kind") == "stop"]
    if ev:
        return "stop: " + str(ev[-1].get("reason"))
    lg = lines(os.path.join(d, "run.log"))
    if lg and lg[-1].strip() == "done":
        return "no stop: done"
    return "no stop recorded (the runner's log does not end 'done')"


def smoke(d, rc):
    bad = []
    want = registered_calls(SMOKE_LISTING)
    if len(want) != 10:
        bad.append(f"the registered smoke listing gives {len(want)} calls, not 10")
    if rc != 0:
        bad.append(f"the runner exited {rc}")
    if os.path.exists(os.path.join(d, "STOPPED")):
        bad.append("STOPPED: " + (lines(os.path.join(d, "STOPPED")) or [""])[0])
    lg = lines(os.path.join(d, "run.log"))
    if not lg or lg[-1].strip() != "done":
        bad.append("the runner's log does not end 'done'")
    calls = log_calls(d)
    got = [(b, a) for _, b, a, _, _ in calls]
    if got != want:
        bad.append(f"the calls are not the registered smoke's: {got} against {want}")
    runs = jl(os.path.join(d, "runs.jsonl"))
    by = collections.defaultdict(list)
    for r in runs:
        by[(r.get("pass"), r.get("block"), r.get("pos"))].append(r)
    nl = 0
    seen = collections.Counter()
    for p, b, a, n, e in calls:
        pos = seen[(p, b)]                    # the runner's "pos": the call's place in its block, in the log's order
        seen[(p, b)] += 1
        if e != 0:
            bad.append(f"{a} (block {b}) exited {e}")
        train = a.startswith("tr_")
        if n < 1 or (train and n != 12):
            bad.append(f"{a} (block {b}) had {n} launches")
        rows = by.get((p, b, pos), [])
        if any((r.get("label") or r.get("arm")) != a for r in rows):
            bad.append(f"{a} (block {b}, position {pos}): a record of another arm")
        if len(rows) != n:
            bad.append(f"{a} (block {b}): {len(rows)} launch records for {n} launches")
        nl += len(rows)
        if any(r.get("ok") is not True or r.get("rc") != 0 for r in rows):
            bad.append(f"{a} (block {b}): a launch not ok, or a record with an exit other than 0")
        if train:
            segs = collections.Counter(r.get("seg") for r in rows)
            if any(segs.get(s, 0) != 3 for s in range(4)) or any(r.get("short_train") for r in rows):
                bad.append(f"{a}: segments {dict(segs)}, not 3 launches in each of 0-3")
    if len(runs) != nl:
        bad.append(f"runs.jsonl holds {len(runs)} records, {nl} belong to the registered calls")
    tel = jl(os.path.join(d, "telemetry.jsonl"))
    if len(tel) < 150:
        bad.append(f"the smoke's telemetry has {len(tel)} samples (fewer than 150)")
    off = sum(1 for s in tel if mhz(s) != CLOCK_MHZ)
    hiw = sum(1 for s in tel if s.get("board_w") is None or s["board_w"] > BOARD_STOP_W)
    hot = sum(1 for s in tel if die(s) is None or die(s) >= DIE_STOP_C)
    if off:
        bad.append(f"{off} samples not at 600 MHz (or without the field)")
    if hiw:
        bad.append(f"{hiw} samples above 65 W (or without board_w)")
    if hot:
        bad.append(f"{hot} samples at or above 70 C (or without the die reading)")
    bw = max((s["board_w"] for s in tel if s.get("board_w") is not None), default=float("nan"))
    dc = max((die(s) for s in tel if die(s) is not None), default=float("nan"))
    if bad:
        print("SMOKE NO-GO: " + "; ".join(bad))
        return 3
    print(f"SMOKE GO: 10 of 10 device processes exit 0 as registered, {nl} launches all ok, the train 12 of 12 (3 a segment); "
          f"telemetry {len(tel)} samples, every one at 600 MHz, board max {bw:.2f} W, die max {dc:.0f} C (below every stop)")
    return 0


def drycmp(listing, registered, host):
    a = [x.replace(host, REG_HOST) for x in lines(listing)]
    b = lines(registered)
    n = sum(1 for x in a if x.startswith("DRY ET_DEVICES="))
    if a == b:
        print(f"LISTING SAME: {os.path.basename(registered)}, {n} device calls, {len(a)} lines (the host's path written as the registration's)")
        return 0
    k = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    print(f"LISTING DIFFERS from {os.path.basename(registered)} at line {k + 1} ({len(a)} lines against {len(b)}; {n} device calls): "
          f"{(a[k] if k < len(a) else '<end>')[:160]!r} against {(b[k] if k < len(b) else '<end>')[:160]!r}")
    return 3


def summary(d):
    calls = log_calls(d)
    runs = jl(os.path.join(d, "runs.jsonl"))
    tel = jl(os.path.join(d, "telemetry.jsonl"))
    per_arm = collections.Counter(a for _, _, a, _, _ in calls)
    passes = sorted({p for p, _, _, _, _ in calls})
    out = {"device_processes": len(calls), "exit_codes": dict(collections.Counter(e for *_, e in calls)),
           "launches": len(runs), "launches_ok": sum(1 for r in runs if r.get("ok") is True),
           "passes_seen": passes, "processes_per_arm": dict(sorted(per_arm.items())), "stop": stopreason(d),
           "telemetry_samples": len(tel),
           "telemetry_off_600": sum(1 for s in tel if mhz(s) != CLOCK_MHZ),
           "board_max_w": max((s["board_w"] for s in tel if s.get("board_w") is not None), default=None),
           "die_max_c": max((die(s) for s in tel if die(s) is not None), default=None),
           "idle_down_waits": sum(1 for e in jl(os.path.join(d, "events.jsonl")) if e.get("kind") == "idle_down"),
           "card_waits": sum(1 for e in jl(os.path.join(d, "events.jsonl")) if e.get("kind") in ("card_busy", "card_wait")),
           "short_trains": sum(1 for e in jl(os.path.join(d, "events.jsonl")) if e.get("kind") == "short_train"),
           "incomplete": sum(1 for e in jl(os.path.join(d, "events.jsonl")) if e.get("kind") == "incomplete")}
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


def load_reducer():
    spec = importlib.util.spec_from_file_location("reduce_x04_registered", REDUCER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def dip_count(d):
    """Check 8: readings the dip rule drops, per window the reducer evaluates (its own code: load, Series, windows)."""
    import numpy as np
    R = load_reducer()
    tel, runs, _ = R.load(d, "", "")
    S = R.Series(tel, None)
    bursts = collections.OrderedDict()
    for r in runs:
        bursts.setdefault((r["pass"], r["block"], r["pos"]), []).append(r)
    keys = sorted(bursts, key=lambda k: min(r["t_start_ms"] for r in bursts[k]))

    def drops(a, b):
        v = S.w[S.sel(a, b)]
        return (int((v < np.median(v) - 4.0).sum()), int(v.size)) if v.size else (0, 0)
    tot = collections.Counter()
    by_pass = collections.Counter()
    for i, k in enumerate(keys):
        rs = bursts[k]
        lo, hi, before, after = R.windows(keys, bursts, i, S.t[0], S.t[-1])
        if rs[0].get("train"):
            segs = collections.defaultdict(list)
            for r in rs:
                segs[r["seg"]].append(r)
            for s, srs in segs.items():
                n, m = drops(min(r["t_start_ms"] for r in srs) / 1000.0 + 0.5, max(r["t_end_ms"] for r in srs) / 1000.0)
                tot["train_segment"] += n; tot["train_segment_readings"] += m; by_pass[k[0]] += n
            continue
        for name, w in (("busy", (lo + 0.5, hi)), ("idle_before", before), ("idle_after", after)):
            n, m = drops(*w)
            tot[name] += n; tot[name + "_readings"] += m; by_pass[k[0]] += n
    dropped = tot["busy"] + tot["idle_before"] + tot["idle_after"] + tot["train_segment"]
    return {"dropped_readings": dropped, "by_window": dict(tot), "by_pass": {str(p): n for p, n in sorted(by_pass.items())},
            "measured_passes_dropped": sum(n for p, n in by_pass.items() if p > 0),
            "note": "readings more than 4 W below their window's median, counted in every window the registered reducer evaluates; "
                    "a reading inside two windows counts in each; pass 0 (the warm-up) is counted in by_pass and left out of "
                    "measured_passes_dropped"}


def checks(xpath, d, outp):
    x = json.load(open(xpath))
    c = x.get("checks", {})
    rep = {"schema": "e193-checks/1", "x04_json": os.path.basename(xpath), "checks": {}}
    C = rep["checks"]
    for n in ("spin2", "faddps_p1", "fsgnjs_p1"):
        k = "1_2_catalogue_" + n
        C[("1 " if n == "spin2" else "2 ") + n] = ({"verdict": "PASS" if c[k]["pass"] else "FAIL", **c[k]} if k in c
                                                    else {"verdict": "NOT COMPUTED", "why": f"{n} has no measured value"})
    dr = c.get("3_anchor_drift")
    C["3 anchor drift"] = ({"verdict": "PASS" if not dr["flagged"] else "FLAGGED", "flagged": dr["flagged"],
                            "boundaries": len(dr["by_block_w"])} if dr else {"verdict": "NOT COMPUTED"})
    dv = c.get("4_device_ok", {})
    trains_bad = sum(1 for t in x.get("trains_runs", []) if not t.get("ok"))
    C["4 device ok"] = {"verdict": "REPORTED", "runs": dv.get("runs"), "trains": dv.get("trains"),
                        "dropped_device": dv.get("dropped_device"), "trains_not_ok": trains_bad}
    C["5 clock"] = {"verdict": "REPORTED", "dropped_clock": dv.get("dropped_clock")}
    du = c.get("6_duty_linear")
    C["6 duty linear"] = ({"verdict": "PASS" if du["pass"] else "FAIL", "residuals_w": du["residuals_w"]} if du
                          else {"verdict": "NOT COMPUTED", "why": "the duty line needs three of its four arms"})
    C["7 nulls"] = {"verdict": "REPORTED", **c.get("7_nulls", {})}
    try:
        C["8 dip rule"] = {"verdict": "REPORTED", **dip_count(d)}
    except Exception as e:      # the count is a report; its failure is said, never hidden
        C["8 dip rule"] = {"verdict": "NOT COMPUTED", "why": f"{type(e).__name__}: {e}"}
    arms, trains = x.get("arms", {}), x.get("trains", {})
    if "spin2" in arms and "tr_tk_stall2" in trains:
        s2 = arms["spin2"]["slots_per_cycle_per_hart"]
        by = trains["tr_tk_stall2"]["slots_per_cycle_per_hart_by_seg"]
        dv_rate = (by["1"] + by["2"]) / 2.0
        name = "a stalled pipeline" if dv_rate < 0.5 * s2 else "a divide issue loop"
        C["9 stall2"] = {"verdict": "REPORTED", "divides_per_hart_cycle": dv_rate, "spin2_slots_per_hart_cycle": s2,
                         "threshold": "less than half of the session's spin2 rate (E193.md 8, the lab's reading)", "name": name}
    else:
        C["9 stall2"] = {"verdict": "NOT COMPUTED", "why": "needs spin2 and tr_tk_stall2 (sitting A)"}
    txt = json.dumps(rep, indent=1, sort_keys=True, default=float)
    if outp:
        open(outp, "w").write(txt + "\n")
    for k in sorted(C):
        print(f"check {k}: {C[k]['verdict']}")
    print("CHECKS READ: " + ", ".join(f"{k.split()[0]} {C[k]['verdict']}" for k in sorted(C)))
    return 0


def main(argv):
    if len(argv) >= 2 and argv[0] == "smoke":
        rc = int(argv[argv.index("--rc") + 1]) if "--rc" in argv else -1
        return smoke(argv[1], rc)
    if len(argv) == 2 and argv[0] == "stopreason":
        print(stopreason(argv[1]))
        return 0
    if len(argv) == 5 and argv[0] == "drycmp" and argv[3] == "--host":
        return drycmp(argv[1], argv[2], argv[4])
    if len(argv) == 2 and argv[0] == "summary":
        return summary(argv[1])
    if len(argv) >= 3 and argv[0] == "checks":
        return checks(argv[1], argv[2], argv[argv.index("--out") + 1] if "--out" in argv else "")
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
