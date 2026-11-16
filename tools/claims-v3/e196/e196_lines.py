#!/usr/bin/env python3
"""E196's kit (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum): THE HOST-LINE READER, the one place where the kit's
runner (run_block_e196.py) reads what a device process printed. It is written for the lesson of CONTEXT section 116 (E191's first
session, 1a4bc1e3: aifoundry1's runtime printed "Opening device 1" inside the ledger host's JSON line and the kit's reader took the
broken head): a host's line is read from a source no runtime print can split.

Both hosts of E196 print one line a launch with ONE printf and ONE fflush (the lab's workloads/sparsity/host/main.cpp line 617,
"SPARSITY {...}"; the request's proposal/src/host/main.cpp lines 454 and 473, "X14 {...}" and "X14CHECK {...}"), so a split inside a line
needs another writer on the same stdout; aifoundry3's runtime prints its device lines on stderr (E193's committed device-stderr.txt), and
no aifoundry3 record holds a runtime line on a host's stdout. The reader does not rely on any of that:
  1. drop_runtime: every runtime line, the exact text "Opening device <n>" and its newline (RUNTIME_LINE, e191_common_v2.py's), is removed
     wherever it fell, at a line's start or inside a host's line; a JSON string cannot hold a raw newline, so the removal never cuts into
     the host's own text; the dropped lines are kept, in order, for the record;
  2. every line left that begins with one of the host's prefixes ("SPARSITY " for the lab's host; "X14 " and "X14CHECK " for the
     request's) must parse as a JSON object and carry every key the host's printf writes, each of its type, and agree with the command
     line it was run with (read_host's argv): test, type, pattern, values, row mask and minions for the lab host; values, label, row mask
     and minions for the request's (its label and values one of the process's two kinds in a train);
  3. ANY host line that fails 2 makes the process UNREADABLE: the runner then writes none of its records (a whole run or none: a
     missing calibration launch would move the reduction's window), marks it, fails the smoke gate for it, and counts a heater launch
     as failed. Never a wrong datum; an unknown text inside a line fails safe because the line no longer parses.
Lines of other text (neither a host line nor a runtime line) are counted and their heads kept in the record; they are never read.

    python3 -I -B tools/claims-v3/e196/e196_lines.py       (its self-check: E196-LINES SELF-CHECK PASS)
Python's standard library only (the box's python3 and the desk's /usr/bin/python3 3.12.3). SPDX-License-Identifier: Apache-2.0
"""
import json
import re

RUNTIME_LINE = re.compile(r"Opening device [0-9]+\n")       # aifoundry1's runtime on a host's stdout (1a4bc1e3); e191_common_v2.py's
NUM = (int, float)
# the lab's sparsity host, --test fma (workloads/sparsity/host/main.cpp lines 617-627, source 0f53a7d5...): every key, its type
SPARSITY_FMA = (("test", str), ("type", str), ("pattern", str), ("values", str), ("sparsity", NUM), ("b_sparsity", NUM),
                ("b_stream", int), ("row_mask", str), ("nnz_a", int), ("a_elems", int), ("fp16_one_sided_pairs", int),
                ("minions", int), ("shire_mask", str), ("iters", int), ("launch", int), ("cycles_max", int), ("cycles_mean", NUM),
                ("cycles_per_op", NUM), ("wall_s", NUM), ("t_start_ms", int), ("t_end_ms", int), ("ghz", NUM),
                ("tensor_errors", int), ("result", str), ("ok", bool))
# the request's x14_host (proposal/src/host/main.cpp lines 454-462 and 473-476, source b91a2c76...)
X14 = (("label", str), ("values", str), ("row_mask", str), ("kind", str), ("abba", str), ("minions", int), ("shire_mask", str),
       ("iters", int), ("launch", int), ("ops", int), ("cycles_max", int), ("cycles_mean", NUM), ("cycles_per_op", NUM),
       ("wall_s", NUM), ("t_start_ms", int), ("t_end_ms", int), ("ghz", NUM), ("tensor_errors", int), ("ok", bool))
X14CHECK = (("label", str), ("kind", str), ("after_launch", int), ("zero_rows", str), ("live_rows", str), ("zero_rows_bad", int),
            ("live_rows_zero", int), ("ok", bool))
FORMS = {"lab": {"SPARSITY ": SPARSITY_FMA}, "x14": {"X14 ": X14, "X14CHECK ": X14CHECK}}


def drop_runtime(text):
    """(the host's own text, [the runtime lines dropped, in order]): every RUNTIME_LINE removed wherever it fell."""
    text = text or ""
    found = [m.group(0)[:-1] for m in RUNTIME_LINE.finditer(text)]
    return RUNTIME_LINE.sub("", text), found


def _typed(j, spec):
    bad = []
    for k, t in spec:
        if k not in j:
            bad.append("no %s" % k)
            continue
        v = j[k]
        if t is bool:
            if not isinstance(v, bool):
                bad.append("%s not a boolean" % k)
        elif t is int:
            if not isinstance(v, int) or isinstance(v, bool):
                bad.append("%s not an integer" % k)
        elif t is NUM:
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                bad.append("%s not a number" % k)
        elif not isinstance(v, t):
            bad.append("%s not a %s" % (k, t.__name__))
    return bad


def _arg(argv, name, default=None):
    argv = list(argv or [])
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return default


def _mask16(s):
    """a --row-mask word as both hosts print it: 0x%04llx of its low 16 bits, or None when it cannot be read"""
    try:
        return "0x%04x" % (int(s, 0) & 0xFFFF)
    except (TypeError, ValueError):
        return None


def _minions(argv, shires_default, per_default):
    try:
        sh = int(_arg(argv, "--shires", shires_default), 0)
        per = int(_arg(argv, "--per-shire", per_default), 0)
    except (TypeError, ValueError):
        return None
    return bin(sh & 0xFFFFFFFF).count("1") * per


def lab_checks(j, argv):
    """a SPARSITY line of the lab's host against its own form and the command it was run with: [] or the reasons"""
    bad = _typed(j, SPARSITY_FMA)
    if bad or argv is None:
        return bad
    want = {"test": _arg(argv, "--test", "fma"), "type": _arg(argv, "--type", "fp32"), "pattern": _arg(argv, "--pattern", "elem"),
            "values": _arg(argv, "--values", "small")}
    for k, w in want.items():
        if j[k] != w:
            bad.append("%s %r, not the command's %r" % (k, j[k], w))
    rm = _arg(argv, "--row-mask")
    wm = _mask16(rm) if rm is not None else "0xffff"
    if j["row_mask"] != wm:
        bad.append("row_mask %r, not the command's %r" % (j["row_mask"], wm))
    m = _minions(argv, "0x1", "1")       # the lab host's defaults: one minion of shire 0 (main.cpp's Options)
    if m is not None and j["minions"] != m:
        bad.append("minions %d, not the command's %d" % (j["minions"], m))
    if j["t_end_ms"] < j["t_start_ms"]:
        bad.append("t_end_ms before t_start_ms")
    return bad


def x14_checks(j, argv, prefix):
    """an X14 or X14CHECK line of the request's host against its own form and the command it was run with: [] or the reasons"""
    spec = X14 if prefix == "X14 " else X14CHECK
    bad = _typed(j, spec)
    if bad or argv is None:
        return bad
    kinds = {"F": (_arg(argv, "--label", ""), _arg(argv, "--values", "")),
             "S": (_arg(argv, "--label-b", _arg(argv, "--label", "")), _arg(argv, "--values-b", _arg(argv, "--values", "")))}
    train = _arg(argv, "--abba") is not None
    if train:
        if j["kind"] not in ("S", "F"):
            bad.append("kind %r in a train" % j["kind"])
            return bad
        lab, val = kinds[j["kind"]]
    else:
        if j["kind"] != "-":
            bad.append("kind %r outside a train" % j["kind"])
        lab, val = kinds["F"]
    if j["label"] != lab:
        bad.append("label %r, not the command's %r" % (j["label"], lab))
    if prefix == "X14 ":
        if j["values"] != val:
            bad.append("values %r, not the command's %r" % (j["values"], val))
        if j["abba"] != (_arg(argv, "--abba") or ""):
            bad.append("abba %r, not the command's %r" % (j["abba"], _arg(argv, "--abba") or ""))
        rm = _arg(argv, "--row-mask-b" if (train and j["kind"] == "S") else "--row-mask")
        if train and j["kind"] == "S" and rm is None:
            rm = _arg(argv, "--row-mask")
        wm = "none" if rm in (None, "none") else _mask16(rm)
        if j["row_mask"] != wm:
            bad.append("row_mask %r, not the command's %r" % (j["row_mask"], wm))
        m = _minions(argv, "0xffffffff", "32")   # the request's host's defaults: all 1,024 minions
        if m is not None and j["minions"] != m:
            bad.append("minions %d, not the command's %d" % (j["minions"], m))
        if j["t_end_ms"] < j["t_start_ms"]:
            bad.append("t_end_ms before t_start_ms")
    return bad


def read_host(text, form, argv=None):
    """THE HOST'S LINES (see the module's head). form: 'lab' (the lab's sparsity host) or 'x14' (the request's host).
    Returns (records, info): records [(prefix, dict)] in the order printed; info {"runtime_lines", "other_lines", "other_heads",
    "unreadable": [reasons], "readable": bool}. When info["readable"] is False the caller writes NONE of the records."""
    prefixes = FORMS[form]
    host, rt = drop_runtime(text)
    recs, other, unreadable = [], [], []
    for ln in host.split("\n"):
        if not ln.strip():
            continue
        pre = next((p for p in sorted(prefixes, key=len, reverse=True) if ln.startswith(p)), None)
        if pre is None:
            # a line that names a host prefix anywhere but at its start is a split the runtime-line rule did not catch
            if any(p.strip() + " {" in ln for p in prefixes):
                unreadable.append("a host line not at a line's start (%r)" % ln[:60])
            other.append(ln)
            continue
        try:
            j = json.loads(ln[len(pre):])
        except ValueError as e:
            unreadable.append("a %sline does not parse once the runtime lines are dropped (%s; it begins %r)" % (pre, str(e)[:60], ln[:50]))
            continue
        if not isinstance(j, dict):
            unreadable.append("a %sline is not a JSON object" % pre)
            continue
        why = lab_checks(j, argv) if form == "lab" else x14_checks(j, argv, pre)
        if why:
            unreadable.append("a %sline is not the host's line for this command: %s" % (pre, "; ".join(why[:3])))
            continue
        recs.append((pre, j))
    info = {"reader": "e196_lines.read_host (kit-e196): the host's stdout, runtime lines dropped, every host line verified",
            "runtime_lines": rt, "other_lines": len(other), "other_heads": [x[:60] for x in other[:3]],
            "unreadable": unreadable, "readable": not unreadable}
    return recs, info


def launches_in_order(recs, prefix):
    """the launch records of one process must run -1, 0, 1, ... in print order (one calibration launch, then each launch once)"""
    ns = [j["launch"] for p, j in recs if p == prefix]
    return ns == list(range(-1, len(ns) - 1))


def _selfcheck():
    argv = ["--test", "fma", "--type", "fp32", "--pattern", "none", "--values", "file:g/tiles/h.bin", "--row-mask", "0x00FF",
            "--shires", "0xffffffff", "--per-shire", "32", "--seconds", "4", "--stop-file", "o/STOP"]
    line = ('SPARSITY {"test":"fma","type":"fp32","pattern":"none","values":"file:g/tiles/h.bin","sparsity":0.0000,"b_sparsity":0.0000,'
            '"b_stream":0,"row_mask":"0x00ff","nnz_a":256,"a_elems":256,"fp16_one_sided_pairs":0,"minions":1024,'
            '"shire_mask":"0xffffffff","iters":20000,"launch":-1,"cycles_max":10880700,"cycles_mean":10880700.0,'
            '"cycles_per_op":544.035,"wall_s":0.018626,"t_start_ms":1790397435674,"t_end_ms":1790397435693,"ghz":0.5844,'
            '"tensor_errors":0,"result":"unchecked","ok":true}\n')
    ok = []
    r, i = read_host(line, "lab", argv)
    ok.append(i["readable"] and len(r) == 1)
    for k in range(len(line)):
        r2, i2 = read_host(line[:k] + "Opening device 0\n" + line[k:], "lab", argv)
        ok.append(i2["readable"] and r2 == r and i2["runtime_lines"] == ["Opening device 0"])
    r3, i3 = read_host(line[:40] + "garbage\n" + line[40:], "lab", argv)
    ok.append(not i3["readable"])
    r4, i4 = read_host(line.replace('"minions":1024', '"minions":32'), "lab", argv)
    ok.append(not i4["readable"])
    print("E196-LINES SELF-CHECK %s (%d of %d)" % ("PASS" if all(ok) else "FAIL", sum(ok), len(ok)))
    return all(ok)


if __name__ == "__main__":
    raise SystemExit(0 if _selfcheck() else 1)
