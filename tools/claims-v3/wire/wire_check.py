#!/usr/bin/env python3
"""V3-WIRE: quick checks run at the end of a block (standard library only, no device access).

    python3 tools/claims-v3/wire/wire_check.py dump <OUT>/dump [--dry]
        Parses every dump_*.txt written by the --dump-slice launches (WIRE-FILL), compares each DUMP word with its
        EXPECT word, writes <OUT>/dump/check.json and prints a one-line note. Exit 1 if a launch has no dump, a
        short dump, a failed launch (an ENERCAT line without ok:true) or a mismatch (never in a dry run).
    python3 tools/claims-v3/wire/wire_check.py pass <OUT> --card C --pass N --expect K [--smoke] [--dry]
        First rewrites runs.jsonl, marks.jsonl and telemetry.jsonl keeping only complete JSON lines (a sampler or
        host stopped mid-write can leave a truncated last line, on which analyze_wire.jl, and so the reduction of
        the whole pass, would fail); the count removed goes into the note.
        Counts launches per configuration, telemetry lines, samples off 600 MHz, and marks every burst that the
        reduction will drop (any sample off 600 MHz in its window or brackets, a starved sampler: median took_ms
        > 60, and on aifoundry2 an implied clock outside 0.595-0.605 GHz, PLAN3 R-clock). Writes <OUT>/pass_check.json
        and prints a one-line note (no quotes, it goes into block.json). Exit 1 if the telemetry is empty or no
        burst launched (for --smoke: if any configuration did not launch).
The reduction (reduce.py) re-derives every drop from the raw files with analyze_wire.bursts(); these checks only
tell the operator, at block end, whether a pass needs to be re-run.
"""
import argparse
import glob
import gzip
import json
import os
import re
import statistics
import sys

CLOCK_BAND = (0.595, 0.605)   # PLAN3 R-clock, GHz


def _loads(l):
    try:
        return json.loads(l)
    except ValueError:
        return None


def jl(path):
    """JSON lines of a file (or its .gz); a truncated line (a process stopped mid-write) is skipped, not fatal."""
    if os.path.exists(path + ".gz"):
        rows = [_loads(l) for l in gzip.open(path + ".gz", "rt") if l.startswith("{")]
    elif os.path.exists(path):
        rows = [_loads(l) for l in open(path, errors="replace") if l.startswith("{")]
    else:
        return []
    return [r for r in rows if r is not None]


def sanitize(path):
    """Rewrite a plain JSON-lines file keeping only complete JSON objects; returns how many lines were removed.
    analyze_wire.jl (registered, used by the reduction) raises on a truncated line and would lose the whole pass."""
    if not os.path.exists(path):
        return 0
    lines = open(path, errors="replace").read().splitlines()
    keep = [l for l in lines if l.startswith("{") and isinstance(_loads(l), dict)]
    if len(keep) != len(lines):
        with open(path, "w") as f:
            f.writelines(l + "\n" for l in keep)
    return len(lines) - len(keep)


def parse_dump(path):
    """One --dump-slice launch: the DUMP and EXPECT words (hex strings), the ENERCAT ok flags, the host's error line.
    A launch counts ("complete") only if it printed 256 DUMP and 256 EXPECT words AND every ENERCAT line it printed
    says ok:true (at least one): a launch whose kernel failed leaves the slice unwritten, so its dump would be a
    launch failure, not a test of the store image."""
    dump, expect, ok, notok = [], [], False, False
    for line in open(path, errors="replace"):
        if line.startswith("DUMP "):
            dump += line.split()[1:]
        elif line.startswith("EXPECT "):
            expect += line.split()[1:]
        elif line.startswith("ENERCAT {"):
            if '"ok":true' in line:
                ok = True
            else:
                notok = True
    err = ""
    ep = path[:-4] + ".err" if path.endswith(".txt") else path + ".err"
    if os.path.exists(ep):
        fails = [l.strip() for l in open(ep, errors="replace")
                 if l.startswith("FAIL") or "refusing" in l or l.startswith("unknown option")]   # the last one is kept
        err = fails[-1] if fails else ""
    m = re.match(r"dump_(.+)_(\d+)\.txt$", os.path.basename(path))
    operands = m.group(1).replace("_", ":", 1) if m else "?"
    mism = [i for i, (a, b) in enumerate(zip(dump, expect)) if a != b]
    launch_ok = ok and not notok
    if not launch_ok and not err:
        err = "no ENERCAT line with ok:true" if not ok else "an ENERCAT line with ok:false"
    return {"file": os.path.basename(path), "operands": operands, "rep": int(m.group(2)) if m else None,
            "words": len(dump), "expect_words": len(expect), "enercat_ok": launch_ok, "error": err,
            "refused": "refus" in err.lower(),
            "complete": len(dump) == 256 and len(expect) == 256 and launch_ok,
            "mismatches": len(mism) + abs(len(dump) - len(expect)),
            "first_mismatch": ([mism[0], dump[mism[0]], expect[mism[0]]] if mism else None)}


def check_dumps(d):
    files = sorted(glob.glob(os.path.join(d, "dump_*.txt")))
    res = [parse_dump(f) for f in files]
    return {"launches": len(res), "complete": sum(r["complete"] for r in res),
            "matched": sum(r["complete"] and r["mismatches"] == 0 for r in res),
            "with_mismatch": [r["file"] for r in res if r["complete"] and r["mismatches"]],
            "incomplete": [r["file"] for r in res if not r["complete"]], "per_launch": res}


def cmd_dump(a):
    s = check_dumps(a.dir)
    json.dump(s, open(os.path.join(a.dir, "check.json"), "w"), indent=1)
    note = f"dumps {s['matched']}/{s['launches']} match"
    if s["with_mismatch"]:
        note += f", mismatch in {len(s['with_mismatch'])}"
    if s["incomplete"]:
        note += f", {len(s['incomplete'])} without a full dump or with a failed launch"
    print(note)
    if a.dry:
        return 0
    return 0 if s["launches"] and s["matched"] == s["launches"] else 1


def cmd_pass(a):
    cut = {n: sanitize(os.path.join(a.out, n)) for n in ("runs.jsonl", "marks.jsonl", "telemetry.jsonl")}
    runs = jl(os.path.join(a.out, "runs.jsonl"))
    tel = jl(os.path.join(a.out, "telemetry.jsonl"))
    marks = jl(os.path.join(a.out, "marks.jsonl"))
    t = [s["t_ms"] / 1000.0 for s in tel]
    mhz = [s.get("mhz", {}).get("minion") for s in tel]
    took = [s.get("took_ms", 0) for s in tel]
    die = [s.get("temp_c", {}).get("minshire", [None])[0] for s in tel]
    by = {}
    for r in runs:
        by.setdefault(r["cfg"], []).append(r)
    bursts, marked = {}, []
    for cfg, rs in by.items():
        lo = min(r["t_start_ms"] for r in rs) / 1000.0
        hi = max(r["t_end_ms"] for r in rs) / 1000.0
        ghz = [r["cycles_max"] / r["wall_s"] / 1e9 for r in rs if r.get("wall_s")]
        win = [i for i, x in enumerate(t) if lo - 3.5 <= x <= hi + 3.8]
        busy = [i for i, x in enumerate(t) if lo <= x <= hi]
        why = []
        if any(mhz[i] != 600 for i in win):
            why.append("clock off 600 MHz")
        if busy and statistics.median(took[i] for i in busy) > 60:
            why.append("sampler starved")
        if len(busy) < 5:
            why.append("too few samples")
        if a.card == "aifoundry2" and ghz and not all(CLOCK_BAND[0] <= g <= CLOCK_BAND[1] for g in ghz):
            why.append("implied clock")
        bursts[cfg] = {"launches": len(rs), "ok": all(r.get("ok") for r in rs),
                       "implied_ghz": [round(min(ghz), 5), round(max(ghz), 5)] if ghz else None,
                       "samples": len(busy), "marked": why}
        if why:
            marked.append(cfg)
    order = []
    op = os.path.join(a.out, "order.json")
    if os.path.exists(op):
        order = json.load(open(op))["order"]
    missing = [c for c in order if c not in by]
    off600 = sum(1 for m in mhz if m != 600)
    heaters = sum(1 for m in marks if m["kind"] == "heater")
    restarts = 0
    lp = os.path.join(a.out, "run.log")
    if os.path.exists(lp):
        restarts = sum("restarting" in l for l in open(lp))
    dies = [x for x in die if x is not None]
    s = {"card": a.card, "pass": a.pass_, "configurations_expected": a.expect, "configurations_launched": len(by),
         "missing": missing, "launches": len(runs), "telemetry_lines": len(tel), "samples_off_600": off600,
         "die_c": [min(dies), max(dies)] if dies else None, "heaters": heaters, "sampler_restarts": restarts,
         "marked_for_dropping": marked, "truncated_lines_removed": cut, "bursts": bursts}
    json.dump(s, open(os.path.join(a.out, "pass_check.json"), "w"), indent=1)
    note = (f"{len(by)}/{a.expect} cfgs, {len(runs)} launches, {len(tel)} samples, {off600} off 600 MHz, "
            f"{len(marked)} bursts marked for dropping, {heaters} heater runs, {restarts} sampler restarts"
            + (f", die {min(dies)}-{max(dies)} C" if dies else ""))
    if any(cut.values()):
        note += ", truncated lines removed: " + " ".join(f"{k} {v}" for k, v in cut.items() if v)
    if missing:
        note += f", not launched: {' '.join(missing[:4])}{' ...' if len(missing) > 4 else ''}"
    print(note.replace('"', "").replace("\\", "/"))
    if a.dry:
        return 0
    if not tel or not runs:
        return 1
    if a.smoke and (missing or len(by) < a.expect):
        return 1
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dump")
    d.add_argument("dir")
    d.add_argument("--dry", action="store_true")
    p = sub.add_parser("pass")
    p.add_argument("out")
    p.add_argument("--card", required=True)
    p.add_argument("--pass", dest="pass_", type=int, required=True)
    p.add_argument("--expect", type=int, required=True)
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    return cmd_dump(a) if a.cmd == "dump" else cmd_pass(a)


if __name__ == "__main__":
    sys.exit(main())
