#!/usr/bin/env python3
"""E197 (Q185, lane kit-e197, Sun 15 Nov 2026, before any E197 datum): THE REAL-BYTES TEST of the host-output parser (the round's
lesson of Sun 15 Nov 2026, round log section 116: a runtime line can arrive INSIDE a host's own output on a real box; E191's first
session stopped at its smoke gate on it). E197's only host-output parser is the registered runner's, lab/run_trains.py lines 204-212
(the lab's runner, departure D1, at sha256 91c46f4e...): it keeps a launch's record only from a stdout line that starts with "REGFILE "
and whose rest parses whole as JSON, and drops every other line. This test EXECUTES THOSE LINES THEMSELVES (the for-loop node taken from
the registered file's syntax tree and compiled as it stands, never re-written) on:

  1. E191's committed smoke stdout (1a4bc1e3, aifoundry1 card 1: the ledger host's JSON line split by the runtime's "Opening device 1"),
     as committed (at its data directory's SHA256SUMS), and its runtime bytes transplanted into a REGFILE line in the E197 host's exact
     form (main.cpp lines 289-300; the kind's fields byte for byte from the registration's table) AT EVERY BYTE OFFSET of the line;
  2. aifoundry3's real host output: E193's four committed device-stdout.txt files (sittings A and B, the smoke and the main run, each the
     whole standard output of one device process, open to close) fed to the parser as they are, and read line by line for any byte that
     is not the host's own; E192's and E193's committed launch records (runs.jsonl) counted against their plans (both runners kept a
     launch only from a whole host line, and E192's and E193's parsers raise on a split one: 3,255 and 2,808 + 1,350 launches read whole
     on aifoundry3's runtime); E192's committed device stderr counted for the runtime's own device-table lines (where that runtime
     prints: stderr);
  3. stand-in streams with a runtime line between two REGFILE lines (kept), inside one (dropped), a newline-less runtime fragment glued
     before or after one (dropped), and a stream with no runtime text (every line kept);
  4. the E197 host's print discipline, read from its source (a desk check of code): each REGFILE line is ONE printf call ending in its
     newline and followed by fflush(stdout), made after the launch, while the device was opened before the first launch (the Session
     constructor); the longest line the format can print with the registration's kinds, every numeric field at its widest, against
     PIPE_BUF (4,096 B): one write(2) of at most PIPE_BUF bytes to a pipe is atomic, so no other writer's bytes can land INSIDE a line.
Every expectation is stated before its reading, including the parser's DROP of a split line; a row passes when the reading is as
stated. Standard library only; it opens no device and runs no host.
    /usr/bin/python3 -I -B tools/claims-v3/e197/desk/realbytes_e197.py <the lab clone's top>     prints REALBYTES-E197 <n> of <m> PASS last
SPDX-License-Identifier: Apache-2.0
"""
import ast
import hashlib
import json
import os
import re
import sys

E = "tools/claims-v3/e197"
RUNNER_SHA = "91c46f4e8a28a2505af1f9e0bb029d1935da59e26915a80bfadd19abd638c40d"
E191 = "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1"
E193A = "docs/reports/data/2026-11-15-e193-x04-clock-sitting-a-aifoundry3"
E193B = "docs/reports/data/2026-11-15-e193-x04-clock-sitting-b-aifoundry3"
E192D = "docs/reports/data/2026-11-14-e192-intbits-aifoundry3"
PIPE_BUF = 4096


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def pinned(top, data, rel):
    """the file's sha256 equals its data directory's SHA256SUMS entry"""
    for ln in open(os.path.join(top, data, "SHA256SUMS")):
        h, p = ln.rstrip("\n").split("  ", 1)
        if p == rel:
            return h == sha(os.path.join(top, data, rel))
    return False


def registered_parser(path):
    """the for-loop of device() that reads the host's stdout, compiled from the registered file's own syntax tree"""
    src = open(path).read()
    tree = ast.parse(src)
    loop = None
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Attribute) and \
                node.iter.func.attr == "splitlines" and "REGFILE" in ast.get_source_segment(src, node):
            loop = node
    if loop is None:
        raise SystemExit("the REGFILE loop was not found in " + path)
    fn = ast.parse("def parse(text, host, blk, rc, info, jwrite):\n    recs = []\n    return recs\n").body[0]
    fn.body.insert(1, loop)
    mod = ast.Module(body=[fn], type_ignores=[])
    ast.fix_missing_locations(mod)
    g = {"json": json}
    exec(compile(mod, path, "exec"), g)
    return g["parse"], (loop.lineno, loop.end_lineno), ast.get_source_segment(src, loop)


def regfile_line(head, idx=1, letter="F", orient="SFFS", widest=False):
    """one REGFILE line in main.cpp's printf form (lines 289-300); widest: every numeric field at the widest the format can print"""
    big = 18446744073709551615
    v = dict(launch=idx, harts=1, parts=1024, iters=1562500000, imin=1525878, imax=1525879, body=200000000000.0, ret=204687500000,
             icr=4000, icm=40, l1m=8300, cmax=240000000, cmean=240000000.0, ipc=0.8331, rate=5.0e11, wall=0.4, t0=1794800000000,
             t1=1794800000400, bad=0)
    if widest:
        v.update(launch=2147483647, harts=big, parts=big, iters=big, imin=big, imax=big, body=1.8e19 * 128, ret=big, icr=big, icm=big,
                 l1m=big, cmax=big, cmean=1.8e19, ipc=-1.0e300, rate=-1.0e300, wall=-1.0e300, t0=-9223372036854775807,
                 t1=-9223372036854775807, bad=big)
    return ("REGFILE {%s,\"launch\":%d,\"letter\":\"%s\",\"orient\":\"%s\",\"harts\":%d,\"participants\":%d,"
            "\"iters\":%d,\"iters_min\":%d,\"iters_max\":%d,\"instr_body\":%.0f,\"retired_counter\":%d,\"icache_req\":%d,\"icache_miss\":%d,"
            "\"l1d_miss\":%d,\"cycles_max\":%d,\"cycles_mean\":%.0f,\"instr_per_cycle_per_hart\":%.4f,"
            "\"instr_per_s_600\":%.4e,\"ra\":\"%s\",\"gp\":\"%s\",\"deadline\":\"%s\",\"ra_gp_differ\":%d,"
            "\"window\":%d,\"wall_s\":%.4f,\"t_start_ms\":%d,\"t_end_ms\":%d,\"check_bad\":%d,\"ok\":%s}\n"
            % (head, v["launch"], letter, orient, v["harts"], v["parts"], v["iters"], v["imin"], v["imax"], v["body"], v["ret"],
               v["icr"], v["icm"], v["l1m"], v["cmax"], v["cmean"], v["ipc"], v["rate"], "0x" + "f" * 16, "0x" + "f" * 16,
               "0x" + "f" * 16, big if widest else 0, big if widest else 240000000, v["wall"], v["t0"], v["t1"], v["bad"],
               "false" if widest else "true"))


def main(argv):
    top = argv[0] if argv else "."
    rows = []

    def row(what, ok, detail=""):
        rows.append((what, bool(ok), detail))
        print("%s %s%s" % ("ok  " if ok else "FAIL", what, ("  [" + str(detail) + "]") if detail != "" else ""), flush=True)

    rp = os.path.join(top, E, "lab/run_trains.py")
    row("the lab's runner at its registered sha256 (91c46f4e...)", sha(rp) == RUNNER_SHA, sha(rp)[:16])
    parse, span, seg = registered_parser(rp)
    row("the parse loop taken from the registered file's own syntax tree: lines %d-%d" % span, span == (204, 212))
    print("    | " + "\n    | ".join(seg.splitlines()))
    calls = []

    def run(text):
        calls.clear()
        return parse(text, "aifoundry3", "A", 0, {"train": "T1", "proc": 0}, lambda name, rec: calls.append((name, rec)))

    # the registration's table: the longest kind head (kindJson, byte for byte)
    heads = []
    for ln in open(os.path.join(top, E, "desk/host-list-e197.jsonl")):
        ln = ln.rstrip("\n")
        if ln:
            heads.append(ln[1:ln.index(',"regs":')])
    head = heads[0]
    clean = regfile_line(head)
    r = run(clean)
    row("a clean REGFILE line in the host's form: kept, its fields whole, written to runs.jsonl", len(r) == 1 and r[0]["kind"] == "rot.x64"
        and r[0]["host"] == "aifoundry3" and calls and calls[0][0] == "runs.jsonl")

    # 1. E191's committed bytes
    rel = "session/smoke/copy-64m-random/stdout.txt"
    raw = open(os.path.join(top, E191, rel), "rb").read()
    row("E191's committed smoke stdout (aifoundry1, 1a4bc1e3) at its data directory's SHA256SUMS", pinned(top, E191, rel), sha(os.path.join(top, E191, rel))[:16])
    i = raw.index(b"Opening device")
    j = raw.index(b"\n", i) + 1
    runtime = raw[i:j].decode()
    row("its runtime bytes, inside the ledger host's line: %r at byte %d of the line" % (runtime, i), runtime == "Opening device 1\n" and i > 0)
    r = run(raw.decode())
    row("the committed bytes as they are: no REGFILE line, nothing kept, no exception (expected: 0)", len(r) == 0, len(r))
    kept = {}
    n = len(clean) - 1                       # the line without its newline
    for off in range(0, n + 2):              # every byte offset, the line's start and the place after its newline included
        s = clean[:off] + runtime + clean[off:]
        kept[off] = len(run(s))
    interior = [k for k in range(1, n + 1)]
    row("E191's runtime line transplanted INSIDE the REGFILE line, at every interior offset 1..%d: the registered parser DROPS the launch "
        "(expected: 0 of 1 kept at each)" % n, all(kept[k] == 0 for k in interior), "kept at %d of %d interior offsets" % (
            sum(kept[k] for k in interior), len(interior)))
    row("at offset 0 (the runtime line before the host's line, on its own line): kept (expected 1)", kept[0] == 1)
    row("after the host's newline (offset %d): kept (expected 1)" % (n + 1), kept[n + 1] == 1)

    # 2. aifoundry3's real host output
    nl_host = nl_other = 0
    files = [(E193A, "smoke/device-stdout.txt"), (E193A, "x04/device-stdout.txt"), (E193B, "smoke/device-stdout.txt"),
             (E193B, "x04/device-stdout.txt")]
    allpin = True
    for data, rel in files:
        allpin = allpin and pinned(top, data, rel)
        b = open(os.path.join(top, data, rel), "rb").read()
        for ln in b.split(b"\n"):
            if not ln:
                continue
            if ln.startswith(b"X04 {"):
                try:
                    json.loads(ln[4:])
                    nl_host += 1
                    continue
                except ValueError:
                    pass
            nl_other += 1
        r = run(b.decode(errors="replace"))
        if r:
            nl_other += 1000
    row("E193's four committed device-stdout files (aifoundry3, Sun 15 Nov 2026) at their data directories' SHA256SUMS", allpin)
    row("aifoundry3's runtime wrote NO byte on the host's stdout in those four whole device processes: every line the host's own and "
        "whole (expected: 0 other lines)", nl_other == 0 and nl_host > 0, "%d host lines, %d other" % (nl_host, nl_other))
    a = sum(1 for _ in open(os.path.join(top, E193A, "x04/runs.jsonl")))
    b = sum(1 for _ in open(os.path.join(top, E193B, "x04/runs.jsonl")))
    c = sum(1 for _ in open(os.path.join(top, E192D, "run/runs.jsonl")))
    row("E193's committed launch records: 2,808 and 1,350 (its plans', read whole by a parser that raises on a split host line)",
        a == 2808 and b == 1350, "%d, %d" % (a, b))
    row("E192's committed launch records: 3,255 (read whole by run_block.py, which raises on a split INTBITS line)", c == 3255, c)
    ptab = sum(1 for ln in open(os.path.join(top, E192D, "run/stderr.txt"), errors="replace") if ln.startswith("PCIe target:"))
    row("aifoundry3's runtime prints its device table on STDERR (E192's committed device stderr: one table an open)", ptab > 300, "%d tables" % ptab)

    # 3. stand-in streams
    two = regfile_line(head, 1) + regfile_line(head, 2, "S")
    row("a runtime line BETWEEN two REGFILE lines: both kept (expected 2)", len(run(regfile_line(head, 1) + runtime + regfile_line(head, 2, "S"))) == 2)
    row("a runtime line INSIDE one of two: that one dropped, the other kept (expected 1)",
        len(run(regfile_line(head, 1)[:300] + runtime + regfile_line(head, 1)[300:] + regfile_line(head, 2, "S"))) == 1)
    row("a newline-less runtime fragment glued BEFORE a line: that line dropped (expected 1 of 2)",
        len(run("Opening device 0" + two)) == 1)
    row("a newline-less runtime fragment glued AFTER a line's closing brace: that line dropped (expected 1 of 2)",
        len(run(regfile_line(head, 1).rstrip("\n") + "Opening device 0\n" + regfile_line(head, 2, "S"))) == 1)
    row("thirteen clean lines (a train process's): 13 kept", len(run("".join(regfile_line(head, k) for k in range(13)))) == 13)

    # 4. the E197 host's print discipline, from its source
    m = open(os.path.join(top, E, "proposal/src/host/main.cpp")).read()
    blk = m[m.index('std::printf("REGFILE {'):m.index("return ok && n && !bad;")]
    one = blk.count("std::printf(") == 1 and blk.count("\\n\"") == 1 and "std::fflush(stdout);" in blk
    row("main.cpp: each REGFILE line is ONE printf ending in its newline, then fflush(stdout)", one)
    sess = m.index("Session dev(o, elf, todo);")
    first = m.index("if (!runOnce(o, dev,", sess)
    row("main.cpp: the device is opened (the Session constructor) before the first launch's line", sess < first)
    lens = [len(regfile_line(h, widest=True)) for h in heads]
    row("the longest REGFILE line the format can print (the registration's 34 kinds, every numeric field at its widest): %d B, at most "
        "PIPE_BUF (%d B): one atomic write(2) to a pipe" % (max(lens), PIPE_BUF), max(lens) <= PIPE_BUF, max(lens))
    row("the typical line: %d B" % len(clean), len(clean) < 1200)

    # the kit's reading, stated
    print("\nTHE KIT'S READING (E197.md 18.2's condition): the registered parser drops a REGFILE line that a runtime print splits (E191's "
          "bytes, every interior offset) and one with a newline-less fragment glued to it; aifoundry3's runtime wrote no byte on a host's "
          "stdout in any committed output (its device table goes to stderr), and E192's and E193's whole-line parsers read every launch "
          "there; E197's host writes each line in one write of at most PIPE_BUF bytes after the device is open, so no print can land "
          "inside it. A split cannot occur on aifoundry3 by these readings: no amendment is proposed. The residual (a newline-less runtime "
          "fragment glued to a line, which no aifoundry3 output shows) fails safe: in the smoke the runner's gate stops the sitting before "
          "any train (no data; the real-path test's SP1 runs it end to end), in a train that one process gives no value (a unit lost; two "
          "in a row stop the sitting); never a wrong datum.")
    n_ok = sum(1 for r in rows if r[1])
    print("\nREALBYTES-E197 %d of %d %s" % (n_ok, len(rows), "PASS" if n_ok == len(rows) else "FAIL"))
    return 0 if n_ok == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
