#!/usr/bin/env python3
"""E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): THE REAL-BYTES TEST of the host-output parser (the round's lesson of
Sun 15 Nov 2026, round log section 116: a runtime line can arrive INSIDE a host's own output on a real box). E197's test
(tools/claims-v3/e197/desk/realbytes_e197.py, unchanged beside it) for E200 on aifoundry2. E200's only host-output parser is E200's
runner's, made by W1 from E197's lab runner (lab/run_trains.py, D1, at 91c46f4e...) and checked at E200's runner sha256 (8774027b...): W1
changes two "--window" words (lines 241 and 247) and nothing of the parse loop, lines 204-212, which keeps a launch's record only from a
stdout line that starts with "REGFILE " and whose rest parses whole as JSON, and drops every other line. This test MAKES E200'S RUNNER the
way the kit does (E197's committed runner with W1's two lines replaced as the committed diff writes them, read at 8774027b...) and
EXECUTES ITS PARSE LOOP ITSELF (the for-loop node taken from that source's syntax tree and compiled as it stands) on:

  1. E191's committed smoke stdout (1a4bc1e3, aifoundry1 card 1: the ledger host's JSON line split by the runtime's "Opening device 1"),
     as committed, and its runtime bytes transplanted into a REGFILE line in the E197 host's exact form AT EVERY BYTE OFFSET of the line;
  2. AIFOUNDRY2'S REAL HOST OUTPUT, this very card's (ET_DEVICES unset, the runtime of the box the sittings run on): E194's committed host
     stdouts (72514ce5, Mon 16 Nov 2026: 24 pass files and 8 smoke files, the ledger and sparse-parity hosts) and E190 arm A's committed
     device-process stdouts (84 proc-NN.out files, Fri 13 Nov 2026, rgm136's SPARSITY host), each read line by line for any byte that is
     not the host's own whole line, and fed to the parser (no REGFILE prefix: nothing kept, no exception); E194's committed host stderr
     read for the runtime's own device-table lines (where this runtime prints: stderr);
  3. aifoundry3's real host output, as E197's test reads it (E193's four device-stdout files; E192's and E193's launch records; E192's
     device stderr): the same host family's runtime on the card E197 runs on;
  4. stand-in streams with a runtime line between two REGFILE lines (kept), inside one (dropped), a newline-less runtime fragment glued
     before or after one (dropped), and a stream with no runtime text (every line kept);
  5. the E197 host's print discipline, read from its source (a desk check of code): one printf a line ending in its newline, then fflush,
     after the device is opened; the longest line the format can print against PIPE_BUF (4,096 B).
E197's own outputs on aifoundry3 are not committed at this HEAD (E197 has not run): printed as NOT RUN, never a row. Every expectation is
stated before its reading; a row passes when the reading is as stated. Standard library only; it opens no device and runs no host.
    /usr/bin/python3 -I -B tools/claims-v3/e200/desk/realbytes_e200.py <the lab clone's top>     prints REALBYTES-E200 <n> of <m> PASS last
SPDX-License-Identifier: Apache-2.0
"""
import ast
import hashlib
import json
import os
import re
import sys

E = "tools/claims-v3/e197"
E2 = "tools/claims-v3/e200"
RUNNER_SHA = "91c46f4e8a28a2505af1f9e0bb029d1935da59e26915a80bfadd19abd638c40d"
E200_RUNNER_SHA = "8774027b4bba78c6b532988c46446987f75eec6d32985bd7b400cbb963eb5a41"
E194D = "docs/reports/data/2026-11-16-e194-blind-day-aifoundry2"
E190D = "docs/reports/data/2026-11-13-e190-large-gemm"
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


def e200_runner(top):
    """E200's runner as the kit makes it: E197's committed lab runner with W1's lines replaced as the committed diff writes them"""
    src = open(os.path.join(top, E, "lab/run_trains.py")).read().split("\n")
    minus, plus = [], []
    for ln in open(os.path.join(top, E2, "lab/run_trains-e200-W1.diff")).read().split("\n"):
        if ln.startswith("-") and not ln.startswith("---"):
            minus.append(ln[1:])
        elif ln.startswith("+") and not ln.startswith("+++"):
            plus.append(ln[1:])
    for a, b in zip(minus, plus):
        k = src.index(a)
        src[k] = b
    return "\n".join(src), len(minus), len(plus)


def registered_parser(src, path):
    """the for-loop of device() that reads the host's stdout, compiled from the runner's own syntax tree"""
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
    row("E197's lab runner at its registered sha256 (91c46f4e...)", sha(rp) == RUNNER_SHA, sha(rp)[:16])
    src, nm, npl = e200_runner(top)
    h2 = hashlib.sha256(src.encode()).hexdigest()
    row("E200's runner made by W1 (2 lines out, 2 in) reads E200's runner sha256 (8774027b...)", h2 == E200_RUNNER_SHA and nm == 2 and npl == 2, h2[:16])
    parse, span, seg = registered_parser(src, "run_trains.py (E200's runner)")
    row("the parse loop taken from the registered file's own syntax tree: lines %d-%d" % span, span == (204, 212))
    print("    | " + "\n    | ".join(seg.splitlines()))
    calls = []

    def run(text):
        calls.clear()
        return parse(text, "aifoundry2", "A", 0, {"train": "T1", "proc": 0}, lambda name, rec: calls.append((name, rec)))

    # the registration's table: the longest kind head (kindJson, byte for byte)
    heads = []
    for ln in open(os.path.join(top, E, "desk/host-list-e197.jsonl")):   # E197's registered table (E200's by reference)
        ln = ln.rstrip("\n")
        if ln:
            heads.append(ln[1:ln.index(',"regs":')])
    head = heads[0]
    clean = regfile_line(head)
    r = run(clean)
    row("a clean REGFILE line in the host's form: kept, its fields whole, written to runs.jsonl", len(r) == 1 and r[0]["kind"] == "rot.x64"
        and r[0]["host"] == "aifoundry2" and calls and calls[0][0] == "runs.jsonl")

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

    # 2. aifoundry2's real host output: this card's runtime
    e194 = []
    for dp, _dn, fn in os.walk(os.path.join(top, E194D)):
        for n in fn:
            if n in ("host-stdout.txt", "stdout.txt"):
                e194.append(os.path.relpath(os.path.join(dp, n), os.path.join(top, E194D)))
    e194.sort()
    p194 = all(pinned(top, E194D, rel) for rel in e194)
    host2 = other2 = kept2 = selftest = 0
    for rel in e194:
        b = open(os.path.join(top, E194D, rel), "rb").read()
        for ln in b.split(b"\n"):
            if not ln:
                continue
            if rel == "session/smoke/ledger-selftest/stdout.txt" and ln.startswith(b"SELFTEST ") and (ln.endswith(b" OK") or ln == b"SELFTEST PASS"):
                selftest += 1           # the ledger host's own self-test (no device opened): its own lines
                continue
            if ln.startswith(b"{") and ln.endswith(b"}"):
                try:
                    json.loads(ln)
                    host2 += 1
                    continue
                except ValueError:
                    pass
            other2 += 1
        kept2 += len(run(b.decode(errors="replace")))
    row("E194's committed host stdouts on THIS CARD (72514ce5: %d files, the ledger and sparse-parity hosts) at their data directory's "
        "SHA256SUMS" % len(e194), p194 and len(e194) == 32, len(e194))
    row("aifoundry2's runtime wrote NO byte on those hosts' stdout: every line the host's own (a whole JSON object; the ledger self-test's "
        "SELFTEST lines, a run that opens no device) (expected: 0 other lines); the parser keeps nothing from them and raises nothing",
        other2 == 0 and host2 >= 31 and selftest >= 1 and kept2 == 0, "%d host lines, %d self-test lines, %d other, %d kept" % (host2, selftest, other2, kept2))
    e190 = []
    for dp, _dn, fn in os.walk(os.path.join(top, E190D, "aifoundry2", "runs")):
        for n in fn:
            if n.startswith("proc-") and n.endswith(".out"):
                e190.append(os.path.relpath(os.path.join(dp, n), os.path.join(top, E190D)))
    e190.sort()
    p190 = all(pinned(top, E190D, rel) for rel in e190)
    host3 = other3 = kept3 = 0
    for rel in e190:
        b = open(os.path.join(top, E190D, rel), "rb").read()
        for ln in b.split(b"\n"):
            if not ln:
                continue
            if ln.startswith(b"SPARSITY {"):
                try:
                    json.loads(ln[len(b"SPARSITY "):])
                    host3 += 1
                    continue
                except ValueError:
                    pass
            other3 += 1
        kept3 += len(run(b.decode(errors="replace")))
    row("E190 arm A's committed device-process stdouts on THIS CARD (84 proc-NN.out, rgm136's host, ET_DEVICES unset) at their data "
        "directory's SHA256SUMS", p190 and len(e190) == 84, len(e190))
    row("aifoundry2's runtime wrote NO byte on those 84 processes' stdout: every line a whole SPARSITY line (expected: 0 other lines); the "
        "parser keeps nothing and raises nothing", other3 == 0 and host3 > 84 and kept3 == 0, "%d host lines, %d other, %d kept" % (host3, other3, kept3))
    herr = sorted(os.path.join(dp, n) for dp, _dn, fn in os.walk(os.path.join(top, E194D)) for n in fn if n == "host.err"
                  and not dp.endswith("ledger-selftest"))
    tabs = sum(1 for p in herr if any(ln.startswith("PCIe target:") for ln in open(p, errors="replace")))
    row("aifoundry2's runtime prints its device table on STDERR (E194's committed host stderr of the %d runs that opened the device: a table "
        "in each)" % len(herr), len(herr) == 31 and tabs == len(herr), tabs)

    # 3. aifoundry3's real host output (E197's rows)
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

    # 4. stand-in streams
    two = regfile_line(head, 1) + regfile_line(head, 2, "S")
    row("a runtime line BETWEEN two REGFILE lines: both kept (expected 2)", len(run(regfile_line(head, 1) + runtime + regfile_line(head, 2, "S"))) == 2)
    row("a runtime line INSIDE one of two: that one dropped, the other kept (expected 1)",
        len(run(regfile_line(head, 1)[:300] + runtime + regfile_line(head, 1)[300:] + regfile_line(head, 2, "S"))) == 1)
    row("a newline-less runtime fragment glued BEFORE a line: that line dropped (expected 1 of 2)",
        len(run("Opening device 0" + two)) == 1)
    row("a newline-less runtime fragment glued AFTER a line's closing brace: that line dropped (expected 1 of 2)",
        len(run(regfile_line(head, 1).rstrip("\n") + "Opening device 0\n" + regfile_line(head, 2, "S"))) == 1)
    row("thirteen clean lines (a train process's): 13 kept", len(run("".join(regfile_line(head, k) for k in range(13)))) == 13)

    # 5. the E197 host's print discipline, from its source
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
    ex = sorted(x for x in os.listdir(os.path.join(top, "docs/reports/data")) if "e197" in x)
    print("\nE197's own outputs on aifoundry3: %s" % ("NOT RUN (none committed at this HEAD: E197 has not run)" if not ex else
                                                     "committed (%s): read them in a later pass" % ", ".join(ex)))
    print("\nTHE KIT'S READING: E200's runner keeps E197's parse loop line for line (W1 touches two window words only); it drops a REGFILE "
          "line that a runtime print splits (E191's bytes, every interior offset) and one with a newline-less fragment glued to it; THIS "
          "CARD's runtime wrote no byte on a host's stdout in any committed output (E194's 32 host stdouts, E190 arm A's 84 process "
          "stdouts; its device table goes to stderr), nor did aifoundry3's; E197's host writes each line in one write of at most PIPE_BUF "
          "bytes after the device is open, so no print can land inside it. A split cannot occur on aifoundry2 by these readings: no "
          "amendment is proposed. The residual (a newline-less runtime fragment glued to a line, which no committed output shows) fails "
          "safe: in the smoke the runner's gate stops the sitting before any train (no data; the real-path test's SP1 runs it end to end), "
          "in a train that one process gives no value (a unit lost; two in a row stop the sitting); never a wrong datum.")
    n_ok = sum(1 for r in rows if r[1])
    print("\nREALBYTES-E200 %d of %d %s" % (n_ok, len(rows), "PASS" if n_ok == len(rows) else "FAIL"))
    return 0 if n_ok == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
