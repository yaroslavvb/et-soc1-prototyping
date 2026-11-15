#!/usr/bin/env python3
"""E193's data READMEs, dated note 1 (Sun 15 Nov 2026, after the data verifier): the figures the note quotes, read again from committed
files. Post hoc: it decides nothing, scores nothing and changes no committed file. The same script (identical bytes) sits in both
sittings' data directories; it reads the directory it sits in and names its outputs by that sitting.

    python3 -I -B docs/reports/data/2026-11-15-e193-x04-clock-sitting-<a|b>-aifoundry3/posthoc_note1_e193.py --out DIR [--data DIR]

It reads only the files of its directory's data commit: the 28 files SHA256SUMS lists, README.md and SHA256SUMS (never a file added
after them, so the note's own files do not change its outputs); and, in sitting B's directory, sitting A's session/session.log, checked
against A's SHA256SUMS. A data directory is never edited after its data commit, so a re-run from any later tree reads the same bytes.

Section 0: the anchors: SHA256SUMS read entry by entry; the sha256 of README.md and SHA256SUMS; (B) A's session log at its entry.
Section 1: the moments the READMEs call a first card command, and the look: the session's holder check (first-card-command.txt and
  session/session.log), k6's step 7 config read and k6's look (both as README.md gives them); the card-minutes counted from each to the
  session's end; the runner's deadline as set and as it would have been from step 7's read; (A) the owner's waiver of the post at
  10:22:36 PST, as the note gives it (the round's log, section 115; sitting B's README quotes it), set against those moments; (B) the
  40-minute rest from sitting A's end to the look, step 7's read and the holder check.
Section 2: the peaks in each runner call's telemetry (smoke/ and x04/): samples, the clock, the board and the die (temp_c.minshire[0]),
  each extreme with its count of samples and the first and last time it was read.
Section 3: the device output files: each runner call's device-stdout.txt and device-stderr.txt against its runs.jsonl and run.log
  (which device process's output they hold).

It writes posthoc-note1-e193-<a|b>.json and .txt in --out, with paths relative to the data directory, times in PST (UTC-8, fixed: the
day is after the 1 Nov change), floats rounded to 9 significant digits and no run time, so a re-run from the same tree under the same
interpreter writes both byte for byte. --data names the data directory when the script runs from a copy. Standard library only.
/usr/bin/python3 3.12.3 wrote the committed outputs.
SPDX-License-Identifier: Apache-2.0
"""
import datetime
import gzip
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PST = datetime.timezone(datetime.timedelta(hours=-8), "PST")
DAY = "2026-11-15"
CAP_S = {"a": 3600, "b": 3000}          # E193.md 6: caps 60 and 50 card-minutes
REST_S = 40 * 60                         # E193.md 6: the 40-minute rest
WAIVER = "10:22:36"                      # the owner's waiver of the post (the round's log, section 115), as the note gives it
SIBLING_A = "../2026-11-15-e193-x04-clock-sitting-a-aifoundry3"


def arg(name, default):
    a = sys.argv[1:]
    return a[a.index(name) + 1] if name in a else default


DATA = os.path.abspath(arg("--data", HERE))
OUT = arg("--out", None)
if not OUT:
    sys.exit("usage: posthoc_note1_e193.py --out DIR [--data DIR]")
OUT = os.path.abspath(OUT)
NAME = os.path.basename(DATA.rstrip("/"))
m = re.search(r"-sitting-([ab])-", NAME)
if not m:
    sys.exit("not an E193 sitting's data directory: " + NAME)
S = m.group(1)


def g(x):
    return float("%.9g" % x) if isinstance(x, float) else x


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha(path):
    with open(path, "rb") as f:
        return sha_bytes(f.read())


def sums(path):
    out = []
    for ln in open(path, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.strip():
            h, p = ln.split("  ", 1)
            out.append((h, p))
    return out


def clock(epoch_s):
    return datetime.datetime.fromtimestamp(int(epoch_s), PST).strftime("%H:%M:%S")


def stamp_ms(ms):
    return datetime.datetime.fromtimestamp(ms // 1000, PST).strftime("%H:%M:%S") + ".%03d" % (ms % 1000)


def epoch(day, hms):
    d = datetime.datetime.strptime(day + " " + hms, "%Y-%m-%d %H:%M:%S").replace(tzinfo=PST)
    return int(d.timestamp())


def span(sec):
    sec = int(sec)
    sign = "-" if sec < 0 else ""
    sec = abs(sec)
    h, r = divmod(sec, 3600)
    mi, s = divmod(r, 60)
    return sign + (f"{h} h {mi} min {s:02d} s" if h else f"{mi} min {s:02d} s")


txt = []
res = {"sitting": S.upper(), "data_dir": NAME, "interpreter": "python %d.%d.%d" % sys.version_info[:3]}


def say(s=""):
    txt.append(s)


say(f"E193 sitting {S.upper()}'s data README, dated note 1: post hoc readings of committed files (decides nothing; scores nothing)")
say(f"data directory: {NAME}")
say(f"interpreter: {res['interpreter']}")
say()

# ---------------------------------------------------------------- 0. anchors
say("0. anchors")
listed = sums(os.path.join(DATA, "SHA256SUMS"))
bad = [p for h, p in listed if sha(os.path.join(DATA, p)) != h]
say(f"  SHA256SUMS: {len(listed) - len(bad)} of {len(listed)} entries OK; with README.md and SHA256SUMS the data commit's "
    f"{len(listed) + 2} files")
for p in bad:
    say(f"    NOT OK: {p}")
readme_b = open(os.path.join(DATA, "README.md"), "rb").read()
say(f"  README.md sha256 {sha_bytes(readme_b)}")
say(f"  SHA256SUMS sha256 {sha(os.path.join(DATA, 'SHA256SUMS'))}")
res["anchors"] = {"sha256sums_entries": len(listed), "sha256sums_ok": len(listed) - len(bad),
                  "readme_sha256": sha_bytes(readme_b), "sha256sums_sha256": sha(os.path.join(DATA, "SHA256SUMS"))}
a_end = None
if S == "b":
    A = os.path.normpath(os.path.join(DATA, SIBLING_A))
    a_sums = dict((p, h) for h, p in sums(os.path.join(A, "SHA256SUMS")))
    ok = a_sums.get("session/session.log") == sha(os.path.join(A, "session/session.log"))
    say(f"  sitting A's session/session.log at its directory's SHA256SUMS ({SIBLING_A}/SHA256SUMS): {'yes' if ok else 'NO'}")
    res["anchors"]["sitting_a_session_log_ok"] = ok
    for i, ln in enumerate(open(os.path.join(A, "session/session.log"), encoding="utf-8"), 1):
        mm = re.match(r"(\d{4}-\d\d-\d\d) (\d\d:\d\d:\d\d) PST session end\b", ln)
        if mm:
            a_end = (epoch(mm.group(1), mm.group(2)), i)
say()

# ---------------------------------------------------------------- 1. the moments
say("1. the moments the README calls a first card command, the look, and the card-minutes")
log = [ln.rstrip("\n") for ln in open(os.path.join(DATA, "session/session.log"), encoding="utf-8")]
ev = {}
for i, ln in enumerate(log, 1):
    mm = re.match(r"(\d{4}-\d\d-\d\d) (\d\d:\d\d:\d\d) PST (.*)$", ln)
    if not mm:
        continue
    t, rest = epoch(mm.group(1), mm.group(2)), mm.group(3)
    for key, rx in (("start", r"session start \(T0 (\d+)"), ("holder", r"the first card command \(the holder check\)"),
                    ("deadline", r"the runner's deadline: \d\d:\d\d:\d\d PST \(epoch (\d+)"), ("main_end", r"main run end:"),
                    ("end", r"session end\b")):
        mk = re.match(rx, rest)
        if mk and key not in ev:
            ev[key] = (t, i, int(mk.group(1)) if mk.groups() else None)
t0 = int(open(os.path.join(DATA, "session/first-card-command.txt")).read().split()[0])
readme = readme_b.decode("utf-8")


def readme_time(rx):
    mm = re.search(rx, readme)
    if not mm:
        return None, None
    return epoch(DAY, mm.group(1)), readme.count("\n", 0, mm.start(1)) + 1


step7, step7_line = readme_time(r"k6's\s+step\s+7\s+read\s+at\s+(\d\d:\d\d:\d\d)\s+PST")
look, look_line = readme_time(r"the\s+holder\s+rule:\s+FREE\s+at\s+(\d\d:\d\d:\d\d)\s+PST")
end = ev["end"][0]
say(f"  the session's first card command, its holder check: T0 {t0} = {clock(t0)} PST (session/first-card-command.txt; "
    f"session/session.log line {ev['holder'][1]}, and line {ev['start'][1]}'s T0 {ev['start'][2]})")
say(f"  k6's step 7 config read, as README.md gives it: {clock(step7)} PST (line {step7_line}); {t0 - step7} s before the holder check")
say(f"  k6's look (step 4), as README.md gives it: {clock(look)} PST (line {look_line}); {t0 - look} s before the holder check")
say(f"  the main run's end: {clock(ev['main_end'][0])} PST (session/session.log line {ev['main_end'][1]}); the session's end: "
    f"{clock(end)} PST (line {ev['end'][1]})")
cm = {}
for key, t in (("holder_check", t0), ("step7_read", step7), ("look", look)):
    cm[key] = {"from": clock(t), "seconds": end - t, "card_minutes": round((end - t) / 60, 2)}
say(f"  card-minutes to the session's end: from the holder check {cm['holder_check']['card_minutes']:.2f} ({end - t0} s); from step 7's "
    f"read {cm['step7_read']['card_minutes']:.2f} ({end - step7} s); from the look {cm['look']['card_minutes']:.2f} ({end - look} s); "
    f"the cap {CAP_S[S] // 60}")
dl = ev["deadline"][2]
say(f"  the runner's deadline as set: {clock(dl)} PST (epoch {dl}; session/session.log line {ev['deadline'][1]}) = the holder check + "
    f"{dl - t0} s (the cap {CAP_S[S]} s - 120 s: {'yes' if dl - t0 == CAP_S[S] - 120 else 'NO'}); the main run ended "
    f"{span(dl - ev['main_end'][0])} before it")
dl7 = step7 + CAP_S[S] - 120
say(f"  had it counted from step 7's read: {clock(dl7)} PST ({dl - dl7} s earlier); the main run ended {span(dl7 - ev['main_end'][0])} "
    f"before that")
res["moments"] = {"holder_check_t0": t0, "holder_check": clock(t0), "step7_read": clock(step7), "step7_readme_line": step7_line,
                  "look": clock(look), "look_readme_line": look_line, "main_run_end": clock(ev["main_end"][0]),
                  "session_end": clock(end), "card_minutes": cm, "cap_minutes": CAP_S[S] // 60,
                  "deadline_epoch": dl, "deadline": clock(dl), "deadline_minus_t0_s": dl - t0,
                  "deadline_margin_s": dl - ev["main_end"][0], "deadline_from_step7": clock(dl7),
                  "deadline_from_step7_margin_s": dl7 - ev["main_end"][0]}
if S == "a":
    w = epoch(DAY, WAIVER)
    say(f"  the owner's waiver of the post, as the note gives it: {WAIVER} PST; {step7 - w} s ({span(step7 - w)}) before step 7's read, "
        f"{t0 - w} s ({span(t0 - w)}) before the holder check, {look - w} s before the look")
    res["moments"]["waiver"] = {"at": WAIVER, "before_step7_s": step7 - w, "before_holder_check_s": t0 - w, "before_look_s": look - w}
else:
    ae, ai = a_end
    say(f"  sitting A's session end: {clock(ae)} PST ({SIBLING_A}/session/session.log line {ai}); the rest opens {clock(ae + REST_S)} PST")
    rest = {}
    for key, label, t in (("look", "the look", look), ("step7_read", "step 7's read", step7),
                          ("holder_check", "the holder check", t0)):
        rest[key] = {"at": clock(t), "seconds": t - ae, "whole_minutes": (t - ae) // 60, "forty_or_more": t - ae >= REST_S}
        say(f"    to {label} ({clock(t)}): {t - ae} s ({span(t - ae)}), {(t - ae) // 60} whole minutes "
            f"({'40 or more' if t - ae >= REST_S else 'under 40'})")
    res["rest_from_sitting_a_end"] = {"sitting_a_end": clock(ae), "sitting_a_log_line": ai, "opens": clock(ae + REST_S), **rest}
say()

# ---------------------------------------------------------------- 2. the peaks
say("2. the peaks in each runner call's telemetry (board_w; the die = temp_c.minshire[0]; the clock = mhz.minion)")
res["telemetry"] = {}
for call in ("smoke", "x04"):
    rows = []
    with gzip.open(os.path.join(DATA, call, "telemetry.jsonl.gz"), "rt", encoding="utf-8") as f:
        for ln in f:
            if ln.strip():
                d = json.loads(ln)
                rows.append((d["t_ms"], d["board_w"], d["temp_c"]["minshire"][0], d.get("mhz", {}).get("minion")))
    rec = {"samples": len(rows), "at_600_mhz": sum(1 for r in rows if r[3] == 600),
           "first": stamp_ms(rows[0][0]), "last": stamp_ms(rows[-1][0])}
    say(f"  {call}/telemetry.jsonl.gz: {len(rows)} samples, {rec['at_600_mhz']} at 600 MHz, {rec['first']} to {rec['last']} PST")
    for q, k in (("board_w", 1), ("die_c", 2)):
        for ext, fn in (("max", max), ("min", min)):
            v = fn(r[k] for r in rows)
            at = [r[0] for r in rows if r[k] == v]
            rec[f"{q}_{ext}"] = {"value": g(float(v)) if q == "board_w" else v, "samples": len(at),
                                 "first": stamp_ms(at[0]), "last": stamp_ms(at[-1])}
            vs = f"{v:.2f} W" if q == "board_w" else f"{v} C"
            say(f"    {'board' if q == 'board_w' else 'die'} {ext} {vs}: {len(at)} sample{'s' if len(at) != 1 else ''}"
                + (f", first {stamp_ms(at[0])}, last {stamp_ms(at[-1])} PST" if len(at) > 1 else f", at {stamp_ms(at[0])} PST"))
    res["telemetry"][call] = rec
say()

# ---------------------------------------------------------------- 3. the device output files
say("3. the device output files against runs.jsonl and run.log")
res["device_files"] = {}
for call in ("smoke", "x04"):
    runs = [json.loads(ln) for ln in open(os.path.join(DATA, call, "runs.jsonl"), encoding="utf-8") if ln.strip()]
    out_lines = open(os.path.join(DATA, call, "device-stdout.txt"), encoding="utf-8").read().splitlines()
    x04 = [json.loads(ln[4:]) for ln in out_lines if ln.startswith("X04 ")]
    idx = []
    for x in x04:
        hit = [i for i, r in enumerate(runs) if all(r.get(k) == v for k, v in x.items())]
        idx.append(hit)
    flat = [h[0] for h in idx if len(h) == 1]
    tail = list(range(len(runs) - len(x04), len(runs)))
    procs = set((runs[i]["pass"], runs[i]["block"], runs[i]["pos"], runs[i]["label"]) for i in flat)
    err_b = open(os.path.join(DATA, call, "device-stderr.txt"), "rb").read()
    err = err_b.decode("utf-8", errors="replace")
    rl = [ln for ln in open(os.path.join(DATA, call, "run.log"), encoding="utf-8").read().splitlines()]
    plines = [ln for ln in rl if re.match(r"pass \d+ block \S+ \S+: \d+ launches, exit \d+$", ln)]
    rec = {"runs_jsonl_records": len(runs), "stdout_lines": len(out_lines), "stdout_x04_lines": len(x04),
           "each_matches_one_record": all(len(h) == 1 for h in idx), "are_the_last_records": flat == tail,
           "device_processes_named": sorted([list(p) for p in procs]), "stderr_lines": len(err.splitlines()),
           "stderr_bytes": len(err_b), "stderr_pcie_target_lines": len(re.findall(r"^PCIe target:", err, re.M)),
           "run_log_device_process_lines": len(plines), "run_log_last_device_process": plines[-1] if plines else None,
           "run_log_last_line": rl[-1] if rl else None}
    say(f"  {call}/device-stdout.txt: {len(out_lines)} lines, {len(x04)} X04 lines; each equals exactly one record of "
        f"{call}/runs.jsonl ({len(runs)} records): {'yes' if rec['each_matches_one_record'] else 'NO'}; they are its last "
        f"{len(x04)}: {'yes' if rec['are_the_last_records'] else 'NO'}; one device process: "
        f"{'yes' if len(procs) == 1 else 'NO'} (pass, block, position, label {rec['device_processes_named']})")
    say(f"  {call}/run.log: {len(plines)} device-process lines; the last: '{rec['run_log_last_device_process']}'; its last line: "
        f"'{rec['run_log_last_line']}'")
    say(f"  {call}/device-stderr.txt: {rec['stderr_lines']} lines, {rec['stderr_bytes']} bytes, {rec['stderr_pcie_target_lines']} "
        f"'PCIe target:' line (the device layer's report as one device process opens the ops node)")
    res["device_files"][call] = rec
say()
say("end")


def rnd(o):
    if isinstance(o, dict):
        return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, list):
        return [rnd(v) for v in o]
    return g(o)


os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, f"posthoc-note1-e193-{S}.json"), "w", encoding="utf-8") as f:
    json.dump(rnd(res), f, indent=1, sort_keys=True)
    f.write("\n")
with open(os.path.join(OUT, f"posthoc-note1-e193-{S}.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(txt) + "\n")
print("\n".join(txt))
