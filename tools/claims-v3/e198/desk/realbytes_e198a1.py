#!/usr/bin/env python3
"""E198's REAL-BYTES DESK TEST AFTER DATED AMENDMENT A1 (Q196, lane a1-e198, Mon 16 Nov 2026, before any E198 datum). It is
realbytes_e198.py (kit-e198, Q191; unchanged beside it) with THE LAB'S RUNNER COPY (run_x04_e198a1.py) in place of E193's runner: RB0 finds
the copy's X04 filter (the three lines E193's runner has at 540-542, byte for byte, 20 lines lower in the copy because of A1's hunks above
them) and RB6 imports the copy's Telemetry reader (unchanged code). Every other check is v1's, on the same committed bytes.
Dated fix (Q196, lane fix-a1e198, Mon 16 Nov 2026, before the land): the offset was 14 before the fix; K3 and K7 (two doc lines more
each) and K9 (two lines more in the clean-up) moved the filter 6 lines lower, to 20; its three lines are unchanged.
    /usr/bin/python3 -I -B tools/claims-v3/e198/desk/realbytes_e198a1.py            (from the repository's top)
Prints REALBYTES-E198-A1 <n> of <m> PASS (or FAIL). Exit 0 / 1. v1's docstring, for its checks:
E198's REAL-BYTES DESK TEST (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): CONTEXT section 116's lesson. EVERY parser of
host or device-tool output on E198's path is fed the bytes the lab committed from the cards: aifoundry1's, with the runtime's line
`Opening device 1` INSIDE a host's JSON line (E191's first session 1a4bc1e3 and its second 7156ac15), and E193's real aifoundry3 X04 output
(fe08ed67, 96ef447c). Reads committed files only (git's blobs at the commits named, so no later record moves them); runs no host.

    /usr/bin/python3 -I -B tools/claims-v3/e198/desk/realbytes_e198.py            (from the repository's top)

Each verdict is stated before it is read:
  RB1  E193's four real device-stdout.txt files (each sitting's smoke and main run's last device process): drop_runtime leaves them byte for
       byte; the runner's X04 filter reads every X04 line of each.
  RB2  aifoundry1's REAL runtime line (its exact bytes, taken from 1a4bc1e3's smoke stdout.txt) inserted at EVERY byte offset of every X04
       line of RB1's files: through the guard (drop_runtime) the stream is the original byte for byte and the runner's filter reads the
       same records; WITHOUT the guard the runner's filter reads offset 0 (the line's start: the runtime's line skipped) and raises or
       loses the record at every other offset (the negative control: what E198.md 3 says the unchanged runner would do).
  RB3  two runtime lines at once (card 1's and card 0's) inside one X04 line, and the line before and after: the guard restores the bytes.
  RB4  every committed aifoundry1 stdout.txt that holds the runtime line (1a4bc1e3's and 7156ac15's): after the guard, one line, a JSON
       object of its host (the ledger host's "ledger": 1, or sparse parity's "workload"), nothing left of the runtime text; the files with
       the line INSIDE the host's line (the ledger host's) are exactly those whose last JSON line does not parse before the guard (run 1
       of this test stated "every one broken before" and read 28 of 33: the other five are sparse parity's, whose runtime line stands at a
       line's start; the statement corrected, the code unchanged).
  RB5  the config read's parse (session_e198.sh: grep '^{' | tail -n 1): the runtime line before ettelem's JSON (card 1's form), and the
       lab's committed aifoundry1 card-0 identity reads that hold `Opening device 0`: the JSON line is read, the runtime line never.
  RB6  the unchanged runner's Telemetry reader (run_x04.py's class, imported by its path, unchanged) on E191's second session's real
       aifoundry1 telemetry: every sample read; with the runtime line at a line's start, the same samples; inside a sample's line, that one
       sample dropped by the reader's own guard (reported); and every committed aifoundry1 telemetry file holds no runtime line (counted).
  RB7  the registered reducer's telemetry expression (reduce_x04.py line 55, its text checked) on E193's real telemetry with the runtime
       line at a line's start: the same samples.
  RB8  THE IDENTITY GATE (a) on the committed aifoundry1 card-1 config stderr (7156ac15 config-start.err): ident_e198.py selfcheck --real.
  RB9  every occurrence of `Opening device` in the lab's committed text under docs/reports/data at HEAD, by form: at a line's start, inside
       a line (the ledger host's), or quoted; drop_runtime removes exactly the first two forms and leaves the quoted ones.
Prints REALBYTES-E198 <n> of <m> PASS (or FAIL). Exit 0 / 1. SPDX-License-Identifier: Apache-2.0
"""
import gzip
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
RUNNER = os.path.join(REPO, "tools/claims-v3/e198/run_x04_e198a1.py")            # A1: the lab's runner copy
E193_RUNNER = os.path.join(REPO, "tools/claims-v3/e193/proposal/src/run_x04.py")  # E193's, where the filter stands at 540-542
REDUCER = os.path.join(REPO, "tools/claims-v3/e193/proposal/src/reduce_x04.py")
RES = []


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


D = load(os.path.join(E, "dropruntime_e198.py"), "dropruntime_e198")


def blob(commit, path):
    return subprocess.run(["git", "-C", REPO, "show", f"{commit}:{path}"], capture_output=True, check=True).stdout


def ok(name, cond, detail):
    RES.append((name, bool(cond)))
    print(f"-> {'PASS' if cond else 'FAIL'} ({name}: {detail})", flush=True)


FILTER_LINES = ['                        for line in out.splitlines():', '                            if line.startswith("X04 {"):',
                '                                recs.append(json.loads(line[4:]))']


def runner_filter(text):
    """run_x04.py lines 540-542, as they stand (checked against the file below): (records, error or '')."""
    recs = []
    try:
        for line in text.splitlines():
            if line.startswith("X04 {"):
                recs.append(json.loads(line[4:]))
    except ValueError as e:
        return recs, str(e)[:60]
    return recs, ""


def main():
    src = open(RUNNER).read().splitlines()
    i = next((k for k in range(len(src)) if src[k:k + 3] == FILTER_LINES), -1)
    s193 = open(E193_RUNNER).read().splitlines()
    j = next((k for k in range(len(s193)) if s193[k:k + 3] == FILTER_LINES), -1)
    ok("RB0 the filter as the runner has it", j == 539 and i == j + 20 and sum(1 for k in range(len(src)) if src[k:k + 3] == FILTER_LINES) == 1,
       f"E193's run_x04.py lines {j + 1}-{j + 3}; the lab's copy run_x04_e198a1.py lines {i + 1}-{i + 3}: the same three lines this test applies")
    rt_src = blob("1a4bc1e3", "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1/session/smoke/copy-64m-random/stdout.txt")
    m = re.search(rb"Opening device [0-9]+\n", rt_src)
    RT = m.group(0)
    ok("RB0 the real runtime line", RT == b"Opening device 1\n" and m.start() == 217, f"{RT!r} at byte {m.start()} of 1a4bc1e3's smoke stdout")
    # ---- RB1, RB2, RB3: E193's real X04 output
    files = [(c, f"docs/reports/data/2026-11-15-e193-x04-clock-sitting-{s}-aifoundry3/{d}/device-stdout.txt")
             for c, s in (("fe08ed67", "a"), ("96ef447c", "b")) for d in ("smoke", "x04")]
    forms = guarded_same = raw_ok0 = raw_bad = raw_lost = 0
    nrecs = 0
    for c, p in files:
        b = blob(c, p)
        clean, dropped = D.drop_runtime(b)
        recs, err = runner_filter(b.decode())
        nrecs += len(recs)
        ok("RB1 " + p.split("/")[-2] + "/" + p.split("-sitting-")[1][:1], clean == b and not dropped and recs and not err,
           f"{c} {p.split('/')[-2]}: {len(b)} bytes, {len(recs)} X04 records, drop_runtime unchanged")
        lines = b.split(b"\n")
        for li, ln in enumerate(lines):
            if not ln.startswith(b"X04 {"):
                continue
            for off in range(len(ln) + 1):
                mod = b"\n".join(lines[:li] + [ln[:off] + RT + ln[off:]] + lines[li + 1:])
                forms += 1
                c2, d2 = D.drop_runtime(mod)
                if c2 == b and d2 == [1] and runner_filter(c2.decode()) == (recs, ""):
                    guarded_same += 1
                r3, e3 = runner_filter(mod.decode())
                if off == 0 and not e3 and r3 == recs:
                    raw_ok0 += 1
                elif e3:
                    raw_bad += 1
                elif len(r3) < len(recs):
                    raw_lost += 1
    ok("RB2 guarded at every offset", guarded_same == forms and forms > 1000,
       f"{guarded_same} of {forms} forms restored byte for byte and read as the original {nrecs} records")
    nlines = sum(1 for c, p in files for ln in blob(c, p).split(b"\n") if ln.startswith(b"X04 {"))
    ok("RB2 unguarded (negative control)", raw_ok0 == nlines and raw_bad + raw_lost == forms - nlines,
       f"without the guard: offset 0 read in {raw_ok0} of {nlines} lines; every other offset raises ({raw_bad}) or loses the record ({raw_lost})")
    b = blob(*files[3])
    ln = b.split(b"\n")[0]
    two = b"Opening device 0\n" + ln[:40] + RT + ln[40:80] + b"Opening device 0\n" + ln[80:] + b"\n" + RT + b"\n".join(b.split(b"\n")[1:])
    c2, d2 = D.drop_runtime(two)
    ok("RB3 two runtime lines and the line around", c2 == b and d2 == [0, 1, 0, 1], f"dropped cards {d2}; restored {c2 == b}")
    # ---- RB4: every committed aifoundry1 stdout.txt with the runtime line inside a host's line
    hits = []
    for c in ("1a4bc1e3", "7156ac15"):
        out = subprocess.run(["git", "-C", REPO, "grep", "-l", "Opening device", c, "--",
                              "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1*"], capture_output=True, text=True).stdout
        hits += [(c, x.split(":", 1)[1]) for x in out.split() if x.endswith("stdout.txt")]
    good = 0
    inside_files, broken_files = set(), set()
    for c, p in hits:
        b = blob(c, p)
        clean, dropped = D.drop_runtime(b)
        ls = [x for x in clean.split(b"\n") if x.strip()]
        try:
            j = json.loads(ls[-1]) if len(ls) == 1 else None
        except ValueError:
            j = None
        if isinstance(j, dict) and (j.get("ledger") == 1 or j.get("workload") == "sparseparity") and dropped and b"Opening device" not in clean:
            good += 1
        if any(m.start() > 0 and b[m.start() - 1:m.start()] != b"\n" for m in re.finditer(rb"Opening device [0-9]+\n", b)):
            inside_files.add(p)
        raw_lines = [x for x in b.split(b"\n") if x.startswith(b"{")]
        try:
            json.loads(raw_lines[-1])
        except (ValueError, IndexError):
            broken_files.add(p)
    ok("RB4 aifoundry1's committed stdout.txt", hits and good == len(hits) and inside_files == broken_files and len(inside_files) >= 1,
       f"{len(hits)} committed stdout.txt (1a4bc1e3, 7156ac15): each one host JSON line after the guard, nothing of the runtime text left "
       f"({good}); the {len(inside_files)} with the runtime line inside the ledger host's line are exactly the {len(broken_files)} that do not "
       f"parse before it; the other {len(hits) - len(inside_files)} (sparse parity's form: the line at a line's start) parse either way")
    # ---- RB5: the config read's parse
    cfg = json.dumps({"tdp_w": 65, "temp_threshold_c": 65, "power_state": 3, "power_state_name": "low_power", "minion_mhz": 600,
                      "minion_mv": 499}).encode()
    def grep_last(b):  # the session's own two commands, run as it runs them: grep '^{', then tail -n 1
        g = subprocess.run(["grep", "^{"], input=b, capture_output=True).stdout
        return subprocess.run(["tail", "-n", "1"], input=g, capture_output=True).stdout
    got = grep_last(RT + cfg + b"\n")
    c0 = []
    for p in ("docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/ident/final-160652.out",
              "docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/ident/ident-154200.out"):
        b = open(os.path.join(REPO, p), "rb").read()
        g = grep_last(b).strip()
        c0.append(bool(g) and g.startswith(b"{") and b"Opening device" not in g and b"Opening device 0" in b)
    ok("RB5 the config read's parse", got.strip() == cfg and all(c0),
       f"card 1's form read as its JSON; the two committed aifoundry1 card-0 identity reads with 'Opening device 0' read as JSON lines {c0}")
    # ---- RB6: the runner's Telemetry reader on aifoundry1's real telemetry
    R = load(RUNNER, "run_x04_e198a1_for_e198_realbytes")
    tel = gzip.decompress(blob("7156ac15", "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2/session/telemetry.jsonl.gz"))
    tdir = os.environ.get("TMPDIR_E198") or os.path.join("/tmp", "realbytes-e198-%d" % os.getpid())
    os.makedirs(tdir, exist_ok=True)
    def poll(b):
        p = os.path.join(tdir, "t.jsonl")
        with open(p, "wb") as f:
            f.write(b)
        t = R.Telemetry(p)
        t.poll()
        os.remove(p)
        return t.samples
    s0 = poll(tel)
    njson = sum(1 for x in tel.split(b"\n") if x.startswith(b"{"))
    first = tel.index(b"\n") + 1
    s1 = poll(RT + tel)
    s2 = poll(tel[:first + 30] + RT + tel[first + 30:])
    ok("RB6 the runner's telemetry reader", len(s0) == njson > 1000 and s1 == s0 and len(s2) == len(s0) - 1,
       f"{len(s0)} of {njson} samples; the runtime line at the start: the same; inside the second sample: {len(s2)} (one dropped by the reader's guard)")
    cnt = 0
    nfiles = 0
    out = subprocess.run(["git", "-C", REPO, "ls-files", "docs/reports/data"], capture_output=True, text=True).stdout.split()
    for p in out:
        if "aifoundry1" in p and re.search(r"telemetry[^/]*\.jsonl(\.gz)?$", p):
            b = open(os.path.join(REPO, p), "rb").read()
            if p.endswith(".gz"):
                b = gzip.decompress(b)
            nfiles += 1
            cnt += b.count(b"Opening device")
    ok("RB6 aifoundry1's committed telemetry", nfiles > 5 and cnt == 0, f"{nfiles} committed aifoundry1 telemetry files: {cnt} runtime lines")
    os.rmdir(tdir)
    # ---- RB7: the reducer's expression
    red = open(REDUCER).read().splitlines()
    expr = '    tel = [json.loads(l) for l in open(tel_path or os.path.join(d, "telemetry.jsonl")) if l.startswith("{")]'
    t3 = gzip.decompress(blob("96ef447c", "docs/reports/data/2026-11-15-e193-x04-clock-sitting-b-aifoundry3/x04/telemetry.jsonl.gz"))
    def red_read(b):
        return [json.loads(l) for l in b.decode().splitlines(keepends=True) if l.startswith("{")]
    ok("RB7 the reducer's telemetry expression", red[54] == expr and red_read(RT + t3) == red_read(t3) and len(red_read(t3)) > 1000,
       f"reduce_x04.py line 55 as applied; {len(red_read(t3))} samples of E193's sitting B with and without the runtime line at the start")
    # ---- RB8: the identity gate on the committed card-1 stderr
    err = blob("7156ac15", "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2/session/config-start.err")
    p = os.path.join(E, "logs", ".rb8-err.txt")
    with open(p, "wb") as f:
        f.write(err)
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "ident_e198.py"), "selfcheck", "--real", p], capture_output=True, text=True)
    os.remove(p)
    print("\n".join("   " + x for x in r.stdout.splitlines()))
    ok("RB8 the identity gate on the real card-1 stderr", r.returncode == 0 and "SELF-CHECK PASS" in r.stdout,
       r.stdout.strip().splitlines()[-1][:160] if r.stdout.strip() else r.stderr[-160:])
    # ---- RB9: every occurrence in the lab's committed text, by form
    out = subprocess.run(["git", "-C", REPO, "grep", "-l", "-I", "Opening device", "HEAD", "--", "docs/reports/data"],
                         capture_output=True, text=True).stdout.split()
    start = inside = quoted = other = removed_ok = 0
    for x in out:
        b = blob("HEAD", x.split(":", 1)[1])
        for mm in re.finditer(rb"Opening device", b):
            k = mm.start()
            tail = re.match(rb"Opening device [0-9]+\n", b[k:])
            if tail and (k == 0 or b[k - 1:k] == b"\n"):
                start += 1
            elif tail:
                inside += 1
            elif re.match(rb"Opening device [0-9]+(\\n|\"|')", b[k:]):
                quoted += 1
            else:
                other += 1
        clean, dropped = D.drop_runtime(b)
        removed_ok += (b.count(b"Opening device") - clean.count(b"Opening device")) == len(dropped)
    ok("RB9 every committed occurrence", removed_ok == len(out) and start > 500 and inside >= 1,
       f"{len(out)} files at HEAD: {start} at a line's start, {inside} inside a line, {quoted} quoted, {other} other; "
       f"drop_runtime removed exactly the first two forms in {removed_ok} of {len(out)} files")
    n = sum(1 for _, c in RES if c)
    print(f"REALBYTES-E198-A1 {n} of {len(RES)} {'PASS' if n == len(RES) else 'FAIL'} (python {sys.version.split()[0]})")
    return 0 if n == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main())
