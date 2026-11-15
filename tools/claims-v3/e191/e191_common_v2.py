#!/usr/bin/env python3
"""E191's kit, dated note 2 (Q184, Sun 15 Nov 2026, PST; written after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12 PST, and
after E191's first session stopped at its smoke gate (its record 1a4bc1e3), before any E191 pass datum): e191_common.py (eb1ac923,
unchanged beside it; every name of it is this module's by import) with ONE change of kit mechanics, THE HOST'S RESULT READ FROM A SOURCE
NO RUNTIME PRINT CAN SPLIT (KIT.md.dated-note-2.md section 1):

  What happened. On aifoundry1 the device runtime prints "Opening device 1" on the host's STANDARD OUTPUT when the host opens card 1
  (earlier lab readers skip that line: workloads/memhier/analyze.py line 125). The ledger host prints its one JSON line in two parts
  (workloads/ledger/host/main.cpp lines 478-492 before it opens the card, line 621 on after its launches), so on Sun 15 Nov 2026 the
  smoke's copy-64m-random printed  {"ledger":1,...,"width":32Opening device 1<newline>,"launches":1,...,"status":"PASS"}<newline>  and
  e191_common.last_json, which takes the last line that begins with "{", took the broken head: status None, the smoke gate failed, no
  pass ran (the committed bytes: docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1/session/smoke/copy-64m-random/stdout.txt).

  The reading here. Neither host writes its result line to a file of its own (the ledger host's line goes to stdout only; sparse parity's
  --records-out file holds its records, not its line), and a new host flag would change the registered command lines, so the host's line
  is REASSEMBLED from its standard output:
    1. drop_runtime: every runtime line, the exact text "Opening device <n>" with its newline (RUNTIME_LINE), is removed wherever it fell
       (at a line's start, or inside the host's own line after the head the host printed before it opened the card). A JSON string cannot
       hold a raw newline, so the removal can never cut into the host's own text; the dropped lines are kept, in order, for the record;
    2. the host's line is the LAST line of what is left that begins with "{" (e191_common.last_json's own rule, so a stream without a
       runtime line reads exactly as v1 read it), and it must parse as a JSON object;
    3. its own fields are verified (host_result): the ledger host's line names "ledger": 1, the command's --prog and "device": "card", and
       the head fields its command line sets (copy: bytes, passes, data, width; sha256: block, repeat; sort: keys, reps, order); a line
       whose status is PASS or FAIL carries every field of the tail the adapter, the reducer and the scorer read (launches, wall_s,
       launch_epoch_ms, records_ok, records_bad, units, units_expected, hart0_cycles, checked, mismatches, expect_checked,
       expect_mismatches, first_mismatch, status), each of its type, with len(wall_s) == launches and len(launch_epoch_ms) == 2 x launches
       (main.cpp pushes one wall time and two span ends per launch, a failed launch included); sparse parity's line names "workload":
       "sparseparity" and, at PASS or FAIL, carries reps_requested (the command's --reps), reps_done, launch_s, launch_epoch_ms and kernel.
       A line that fails a check is NOT read (an empty result, with the reason): the smoke gate fails, a pass is a FAILED RUN; never a
       wrong datum. Any other text left (a line that is neither the host's nor a known runtime line) is counted and kept in the record;
       inside the host's line it makes the line unparseable, so it fails safe.
  config_json: the config read through the guard is read the same way (drop_runtime, then e191_common.last_json); the reader prints its
  line after it opens the card, so it read whole on Sun 15 Nov 2026 too: no reading changes, the class of defect is closed.
  Nothing else changes: the adapter (adapt_ledger, E191.md 8.1, E189's word for word), the reading in words, THE STOP LINES, the
  sequence, every number and every gate are e191_common.py's, by import.
Python's own modules only (it runs on aifoundry1 under the system python3, and on the desk under /usr/bin/python3 -I -B).
    python3 -I -B tools/claims-v3/e191/e191_common_v2.py        the self-check (E191-COMMON-V2 SELF-CHECK PASS)
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e191_common as V1  # noqa: E402
from e191_common import *  # noqa: E402,F401,F403   every name of e191_common.py, unchanged

NOTE = "E191 kit note 2 (e191_common_v2.py: the host's line reassembled, runtime lines dropped)"
RUNTIME_LINE = re.compile(r"Opening device [0-9]+\n")       # aifoundry1's runtime, on the host's stdout (1a4bc1e3's smoke stdout.txt)
LEDGER_TAIL = (("launches", int), ("wall_s", list), ("launch_epoch_ms", list), ("records_ok", int), ("records_bad", int), ("units", int),
               ("units_expected", int), ("hart0_cycles", dict), ("checked", int), ("mismatches", int), ("expect_checked", int),
               ("expect_mismatches", int), ("first_mismatch", str), ("status", str))
SPP_TAIL = (("reps_requested", int), ("reps_done", int), ("launch_s", list), ("launch_epoch_ms", list), ("kernel", dict), ("status", str))


def drop_runtime(text):
    """(the host's own text, [the runtime lines dropped, in order]): every RUNTIME_LINE removed wherever it fell."""
    text = text or ""
    found = [m.group(0)[:-1] for m in RUNTIME_LINE.finditer(text)]
    return RUNTIME_LINE.sub("", text), found


def config_json(text):
    """The config read's JSON line (the reader's), read as e191_common.last_json reads it once the runtime lines are dropped."""
    return V1.last_json(drop_runtime(text)[0])


def _arg(argv, name):
    argv = list(argv or [])
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return None


def parse_size(s):
    """main.cpp's parseSize: strtod, then K, M or G (powers of 1024), truncated to an integer; None if it cannot be read."""
    m = re.match(r"^\s*([0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)([A-Za-z]?)", str(s))
    if not m:
        return None
    v = float(m.group(1)) * {"K": 1024, "M": 1024 ** 2, "G": 1024.0 ** 3}.get(m.group(2).upper(), 1)
    return int(v)


def _isint(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _typed(j, spec):
    bad = []
    for k, t in spec:
        v = j.get(k, None)
        if k not in j:
            bad.append(f"no {k}")
        elif t is int and not _isint(v):
            bad.append(f"{k} not an integer")
        elif t is not int and not isinstance(v, t):
            bad.append(f"{k} not a {t.__name__}")
    return bad


def ledger_checks(j, argv):
    """The ledger host's line against its own form and its command line: [] when it is the host's complete line, else the reasons."""
    bad = []
    if j.get("ledger") != 1:
        bad.append(f"ledger {j.get('ledger')!r}, not 1")
    prog = _arg(argv, "--prog")
    if prog is not None and j.get("prog") != prog:
        bad.append(f"prog {j.get('prog')!r}, not the command's {prog!r}")
    if "--card" in (argv or []) and j.get("device") != "card":
        bad.append(f"device {j.get('device')!r}, not 'card'")
    want = []
    if prog == "copy":
        want = [("bytes", "--bytes", parse_size), ("passes", "--passes", int), ("data", "--data", str), ("width", "--width", int)]
    elif prog == "sha256":
        want = [("block", "--block", parse_size), ("repeat", "--repeat", int)]
    elif prog == "sort":
        want = [("keys", "--keys", int), ("reps", "--reps", int), ("order", "--order", str)]
    for key, flag, conv in want:
        a = _arg(argv, flag)
        if a is None:
            continue
        try:
            w = conv(a)
        except (TypeError, ValueError):
            w = None
        if j.get(key) != w:
            bad.append(f"{key} {j.get(key)!r}, not the command's {w!r}")
    st = j.get("status")
    if not isinstance(st, str):
        bad.append("no status")
    elif st in ("PASS", "FAIL"):
        bad += _typed(j, LEDGER_TAIL)
        if not bad:
            n = j["launches"]
            if len(j["wall_s"]) != n:
                bad.append(f"{len(j['wall_s'])} wall times for {n} launches")
            if len(j["launch_epoch_ms"]) != 2 * n:
                bad.append(f"{len(j['launch_epoch_ms'])} span ends for {n} launches")
            if not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in j["wall_s"]):
                bad.append("a wall time not a number")
            if not all(_isint(x) for x in j["launch_epoch_ms"]):
                bad.append("a span end not an integer")
    return bad


def spp_checks(j, argv):
    """Sparse parity's line against its own form and its command line: [] when it is the host's complete line, else the reasons."""
    bad = []
    if j.get("workload") != "sparseparity":
        bad.append(f"workload {j.get('workload')!r}, not 'sparseparity'")
    st = j.get("status")
    if not isinstance(st, str):
        bad.append("no status")
    elif st in ("PASS", "FAIL"):
        bad += _typed(j, SPP_TAIL)
        r = _arg(argv, "--reps")
        if not bad and r is not None and str(j["reps_requested"]) != str(r):
            bad.append(f"reps_requested {j['reps_requested']}, not the command's {r}")
    return bad


def host_result(text, kind, argv):
    """THE HOST'S RESULT (kit note 2): (the host's line as a dict, or {} when it cannot be read; the record). kind is 'ledger' or 'spp'.
    The record: what was read and why not, the runtime lines dropped, the count of the host's own JSON-looking lines and of other lines
    left. Every case reads {} rather than a line it cannot verify."""
    host, rt = drop_runtime(text)
    lines = [ln for ln in host.split("\n") if ln.strip()]
    cands = [ln for ln in lines if ln.startswith("{")]
    other = [ln for ln in lines if not ln.startswith("{")]
    rec = {"reader": "e191_common_v2.host_result (kit note 2): the host's stdout, runtime lines dropped, its last '{' line verified",
           "runtime_lines": rt, "json_lines": len(cands), "other_lines": len(other),
           "other_heads": [ln[:60] for ln in other[:3]], "why": ""}
    if not cands:
        rec["why"] = "no line of the host's that begins with '{'" + (" (a runtime line was dropped)" if rt else "")
        return {}, rec
    try:
        j = json.loads(cands[-1])
    except ValueError as e:
        rec["why"] = f"the host's last line does not parse once the runtime lines are dropped ({str(e)[:80]}; it begins {cands[-1][:40]!r})"
        return {}, rec
    if not isinstance(j, dict):
        rec["why"] = "the host's last line is not a JSON object"
        return {}, rec
    bad = ledger_checks(j, argv) if kind == "ledger" else spp_checks(j, argv)
    if bad:
        rec["why"] = "the line is not the host's complete line for this command: " + "; ".join(bad[:4])
        return {}, rec
    return j, rec


def why_words(rec):
    """One line for the session log: the runtime lines dropped, or why the host's line was not read."""
    rt = rec.get("runtime_lines") or []
    s = (f"{len(rt)} runtime line(s) dropped ({', '.join(sorted(set(rt)))})" if rt else "no runtime line")
    return s + (f"; NOT READ: {rec['why']}" if rec.get("why") else "")


if __name__ == "__main__":
    bad = []
    v1 = __import__("subprocess").run([sys.executable, "-I", "-B", os.path.join(os.path.dirname(os.path.abspath(__file__)), "e191_common.py")],
                                      capture_output=True, text=True)
    if "E191-COMMON SELF-CHECK PASS" not in v1.stdout:
        bad.append("e191_common.py's own self-check: " + v1.stdout.strip()[-120:])
    argv = ["build/e191ledger/host/ledger_host", "--card", "--kernel", "build/e191ledger/kernel/ledger.elf", "--launches", "1", "--prog",
            "copy", "--bytes", "64M", "--passes", "1", "--data", "random", "--width", "32"]
    head = ('{"ledger":1,"prog":"copy","device":"card","participants":2048,"shire_mask":"0xffffffff","minion_mask":"0x0","harts":2,'
            '"seed":1,"model_s":0.0067,"bytes":67108864,"part_bytes":32768,"passes":1,"data":"random","width":32')
    tail = (',"launches":1,"wall_s":[0.0064],"launch_epoch_ms":[1,2],"records_ok":2048,"records_bad":0,"units":67108864,'
            '"units_expected":67108864,"hart0_cycles":{"max":3,"min":2,"mean":2.5,"n":1024},"checked":2048,"mismatches":0,'
            '"expect_checked":0,"expect_mismatches":0,"first_mismatch":"","status":"PASS"}')
    whole = json.loads(head + tail)
    split = head + "Opening device 1\n" + tail + "\n"
    if V1.last_json(split) != {}:
        bad.append("v1's reader read the split line (the defect is not reproduced)")
    j, r = host_result(split, "ledger", argv)
    if j != whole or r["runtime_lines"] != ["Opening device 1"] or r["why"]:
        bad.append(f"the split line: {r}")
    for k in range(0, len(head + tail) + 1, 7):
        s = (head + tail)[:k] + "Opening device 1\n" + (head + tail)[k:] + "\n"
        if host_result(s, "ledger", argv)[0] != whole:
            bad.append(f"the runtime line at offset {k} not reassembled")
            break
    if host_result("Opening device 1\n" + head + tail + "\n", "ledger", argv)[0] != whole or \
            host_result(head + tail + "\n", "ledger", argv)[0] != whole:
        bad.append("the runtime line on its own line, or no runtime line, not read")
    failed = head + "Opening device 1\n" + tail.replace('"mismatches":0,', '"mismatches":1,').replace('"PASS"', '"FAIL"') + "\n"
    jf, rf = host_result(failed, "ledger", argv)
    if jf.get("status") != "FAIL" or V1.adapt_ledger(jf, 1)["reps_consistent"] != "bad":
        bad.append(f"a failed host not read FAILED: {jf.get('status')} {rf}")
    for name, t in (("the head alone (the host died after it opened the card)", head + "Opening device 1\n"), ("nothing", ""),
                    ("an unknown text inside the line", head + "Warning: x\n" + tail + "\n"),
                    ("another command's line", split.replace('"width":32', '"width":64')),
                    ("a line with a field missing", head + "Opening device 1\n" + tail.replace('"units":67108864,', '') + "\n"),
                    ("a span end missing", head + "Opening device 1\n" + tail.replace("[1,2]", "[1]") + "\n")):
        jj, rr = host_result(t, "ledger", argv)
        if jj or not rr["why"]:
            bad.append(f"{name}: read {jj}")
    sargv = ["build/e191spp/host/sparseparity_host", "--n", "544", "--reps", "1", "--kernel", "build/e191spp/kernel/sparseparity.elf"]
    sj = {"workload": "sparseparity", "device": "silicon", "reps_requested": 1, "reps_done": 1, "launch_s": [0.5], "launch_epoch_ms": [1, 2],
          "kernel": {"cycles_max": 3}, "result": {"solved": True}, "problems": [], "status": "PASS"}
    js, rs = host_result("Opening device 1\n" + json.dumps(sj) + "\n", "spp", sargv)
    if js != sj or rs["runtime_lines"] != ["Opening device 1"]:
        bad.append(f"sparse parity's line after a runtime line: {rs}")
    if host_result(json.dumps(dict(sj, reps_requested=9)) + "\n", "spp", sargv)[0]:
        bad.append("sparse parity's line for another --reps read")
    if config_json("Opening device 1\n" + '{"tdp_w":65,"temp_threshold_c":65,"minion_mhz":600}\n') != {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}:
        bad.append("config_json")
    if parse_size("64M") != 67108864 or parse_size("1G") != 1073741824 or parse_size("2048") != 2048 or parse_size("1.5K") != 1536:
        bad.append("parse_size")
    print("E191-COMMON-V2 SELF-CHECK " + ("PASS" if not bad else "FAIL: " + "; ".join(bad)))
    sys.exit(0 if not bad else 1)
