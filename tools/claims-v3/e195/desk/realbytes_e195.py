#!/usr/bin/env python3
"""E195's REAL-BYTES DESK TEST (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): CONTEXT section 116's lesson, that a
kit's every host-output parser is fed the REAL stdout bytes committed from a card, not only stand-in JSON. E195's one host-output parser
is the kit's runner (runitems_e195.py: runitems.py with the record read whole). This test runs THE RUNNER ITSELF, unchanged, on replays
of committed bytes (a replay tool prints a committed stdout file byte for byte as the "host"; a stand-in tree with a one-item manifest,
fresh telemetry, no heating, a stand-in et-holders), and beside it the registered runner runitems.py as the negative control:

  RB1  aifoundry1's split line (1a4bc1e3, E191's first session, Sun 15 Nov 2026: the ledger host's JSON line with the runtime's
       "Opening device 1" and its newline inside it), its head given the x09mem host's tag ("X09MEM "): runitems_e195.py reads ONE
       record, equal to the line with the runtime line removed (PASS, 2,048 records, 0 mismatches), and logs the dropped line;
       runitems.py fails the parse (JSONDecodeError, exit 1): the day's defect reproduced on the registered runner;
  RB2  every committed stdout of E191's second session (7156ac15: 31 of its 32 stdout.txt files carry the runtime line, inside the host's
       line or before it), tagged the same way: runitems_e195.py reads each whole (its JSON equal to the file with the runtime lines
       removed); runitems.py fails every one whose runtime line is inside the JSON;
  RB3  aifoundry3's real bytes (E193's four committed device-stdout.txt files, sittings A and B, the X04 host's lines, tag "X04 {"): both
       runners read the same records, field for field, and runitems_e195.py drops nothing (aifoundry3's runtime printed no stdout line);
  RB4  the runtime line inserted at EVERY byte offset inside one of those real aifoundry3 lines: the kit's reader (runitems_e195.py's own
       drop_runtime, imported from the file by path, and its own parse expression) reads the same record at every offset, and the
       runner itself at ten offsets; two runtime lines at once; a runtime line at the line's start (aifoundry1's form for every host
       that prints after the device opens, the x09mem host among them);
  RB5  an unknown text inside a real line (not the runtime line): the kit's runner still fails the parse (exit 1, no record written):
       never a wrong datum;
  RB6  where aifoundry3's runtime writes: E192's committed run/stderr.txt (330 device processes on aifoundry3, Sat 14 Nov 2026) and
       E193's four device-stderr.txt files carry the runtime's device-layer block on stderr, and no "Opening device" line anywhere;
       the runner reads stdout and stderr through separate pipes (capture_output);
  RB7  the census: every occurrence of "Opening device" in the lab's committed raw records at this clone's HEAD (git's blobs under
       docs/reports/data) is the runtime line "Opening device <n>" with its newline, at a line's start or inside a host's line (E191's
       records), or quoted inside a JSON string; none of another form, so the one form the kit drops is the only one the lab has seen
       (the mentions in code and prose under tools/ and workloads/ are counted beside: readers that skip it, a dry stub's own text).
No host binary runs; no device; nothing is opened (run inside the no-device sandbox all the same).
    bash slot.sh bash nodev.sh /usr/bin/python3 -I -B tools/claims-v3/e195/desk/realbytes_e195.py <empty scratch dir> > log
Prints REALBYTES-E195 <n> of <m> PASS (or FAIL). SPDX-License-Identifier: Apache-2.0
"""
import glob
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
PY = "/usr/bin/python3"
RES = []
D191 = "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1"
D191B = "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2"
D193 = ["docs/reports/data/2026-11-15-e193-x04-clock-sitting-a-aifoundry3", "docs/reports/data/2026-11-15-e193-x04-clock-sitting-b-aifoundry3"]
D192 = "docs/reports/data/2026-11-14-e192-intbits-aifoundry3"
RT = re.compile(r"Opening device [0-9]+\n")


def ok(name, cond, detail):
    RES.append((name, bool(cond)))
    print(f"-> {'PASS' if cond else 'FAIL'} ({name}: {detail})", flush=True)


def load_port():
    spec = importlib.util.spec_from_file_location("runitems_e195_port", os.path.join(E, "runitems_e195.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Tree:
    """A stand-in tree for one runner call: a one-item manifest whose tool is a replay of a committed stdout file."""
    def __init__(self, S, name, tag):
        self.d = os.path.join(S, name)
        os.makedirs(os.path.join(self.d, "gen"))
        os.makedirs(os.path.join(self.d, "bin"))
        with open(os.path.join(self.d, "gen", "manifest.json"), "w") as f:
            json.dump({"items": [{"name": "x9_replay", "kind": "cmd", "tool": "main", "args": ["--replay"], "tag": tag}]}, f)
        self.replay = os.path.join(self.d, "replay.py")
        with open(self.replay, "w") as f:
            f.write("import sys\nsys.stdout.buffer.write(open(sys.argv[2], 'rb').read())\n")
        self.tool = os.path.join(self.d, "replay_host")
        with open(self.tool, "w") as f:
            f.write('#!/bin/bash\nexec %s -I -B %s "$@" "$E195_REPLAY"\n' % (PY, self.replay))
        os.chmod(self.tool, 0o755)
        with open(os.path.join(self.d, "bin", "sudo"), "w") as f:
            f.write('#!/bin/sh\necho "No process holds an ET-SoC-1 device node or card lock."\n')
        os.chmod(os.path.join(self.d, "bin", "sudo"), 0o755)

    def run(self, runner, data_file, k):
        out = os.path.join(self.d, "out%d" % k)
        tel = os.path.join(self.d, "tel%d.jsonl" % k)
        with open(tel, "w") as f:
            f.write(json.dumps({"t_ms": int(time.time() * 1000) + 60000, "board_w": 22.0, "temp_c": {"minshire": [50, 45, 70], "pmic": 50}}) + "\n")
        env = {"PATH": os.path.join(self.d, "bin") + ":/usr/bin:/bin", "USER": "deskuser", "E195_REPLAY": data_file, "LC_ALL": "C.UTF-8"}
        r = subprocess.run([PY, "-I", "-B", runner, out, "--root", self.d, "--gen", os.path.join(self.d, "gen"), "--items", "x9_replay",
                            "--tool", self.tool, "--tel-live", tel, "--preheat", "0", "--target", "100", "--burnin", "0", "--blocks", "1",
                            "--first-block", "1", "--seed", "1", "--card", "aifoundry3", "--max-c", "90"], capture_output=True, text=True, env=env)
        runs = []
        p = os.path.join(out, "runs.jsonl")
        if os.path.exists(p):
            runs = [json.loads(x) for x in open(p) if x.strip()]
        log = open(os.path.join(out, "run.log")).read() if os.path.exists(os.path.join(out, "run.log")) else ""
        return r.returncode, runs, log, r.stderr


def strip_rt(b):
    return RT.sub("", b)


def own_fields(rec, keys):
    return {k: rec.get(k) for k in keys}


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    S = os.path.abspath(argv[0])
    if os.path.exists(S) and os.listdir(S):
        print(f"REFUSED: {S} is not empty")
        return 2
    os.makedirs(S, exist_ok=True)
    port = load_port()
    NEW, OLD = os.path.join(E, "runitems_e195.py"), os.path.join(REPO, "tools/claims-v3/runitems.py")
    print(f"E195 real-bytes desk test, {time.strftime('%F %T %Z')}; Python {sys.version.split()[0]} ({PY}); the kit's runner "
          f"runitems_e195.py and, as the negative control, the registered runitems.py, each run unchanged on replays of committed bytes")
    k = [0]

    def nk():
        k[0] += 1
        return k[0]

    # ---- RB1: aifoundry1's split line, tagged as the x09mem host's
    src = os.path.join(REPO, D191, "session/smoke/copy-64m-random/stdout.txt")
    raw = open(src, "rb").read().decode()
    tagged = os.path.join(S, "rb1-x09mem.txt")
    open(tagged, "w").write("X09MEM " + raw)
    want = json.loads(strip_rt(raw))
    t = Tree(S, "t-rb1", "X09MEM {")
    rc, runs, log, err = t.run(NEW, tagged, nk())
    rc0, runs0, log0, err0 = t.run(OLD, tagged, nk())
    ok("RB1 the split line", rc == 0 and len(runs) == 1 and own_fields(runs[0], want) == want and runs[0].get("status") == "PASS" and
       runs[0].get("records_ok") == 2048 and "runtime line(s) dropped from the host's stdout: Opening device 1" in log,
       f"the committed stdout ({len(raw)} B, the runtime line at byte {raw.index('Opening device')}): runitems_e195.py rc {rc}, {len(runs)} record, "
       f"status {runs[0].get('status') if runs else None}, records_ok {runs[0].get('records_ok') if runs else None}, its fields equal to the line without the runtime line; the drop logged")
    ok("RB1 the negative control", rc0 != 0 and not runs0 and "JSONDecodeError" in err0,
       f"the registered runitems.py on the same bytes: rc {rc0}, {len(runs0)} records, {'JSONDecodeError' if 'JSONDecodeError' in err0 else err0[-120:]!r}: the day's defect reproduced")

    # ---- RB2: every committed stdout of E191's second session
    files = sorted(glob.glob(os.path.join(REPO, D191B, "**", "stdout.txt"), recursive=True))
    good, inside, old_fail, n_rt, nojson = 0, 0, 0, 0, 0
    t2 = Tree(S, "t-rb2", "X09MEM {")
    withjson = []
    for f in files:
        b = open(f, "rb").read().decode()
        heads = [i for i, ln in enumerate(b.split("\n")) if ln.startswith("{")]
        if not heads:
            nojson += 1     # the ledger self-test's stdout: its "SELFTEST PASS" lines and the runtime line, no record
            continue
        withjson.append(f)
        rts = RT.findall(b)
        n_rt += 1 if rts else 0
        cleaned = strip_rt(b)
        line = [ln for ln in cleaned.split("\n") if ln.startswith("{")][-1]
        want = json.loads(line)
        tg = os.path.join(S, "rb2-%d.txt" % len(os.listdir(S)))
        open(tg, "w").write("X09MEM " + b if b.startswith("{") else b.replace("\n{", "\nX09MEM {", 1))
        rc, runs, log, err = t2.run(NEW, tg, nk())
        if rc == 0 and runs and own_fields(runs[-1], want) == want:
            good += 1
        in_line = any(not b[m.start() - 1:m.start()] in ("", "\n") for m in RT.finditer(b))
        if in_line:
            inside += 1
            rc0, runs0, _, err0 = t2.run(OLD, tg, nk())
            old_fail += rc0 != 0 and not runs0
    ok("RB2 the second session's bytes", withjson and good == len(withjson) and old_fail == inside and inside > 0,
       f"{len(files)} committed stdout.txt files, {len(withjson)} with a host's JSON line ({nojson} the self-test's, no record), {n_rt} of those with "
       f"the runtime line, {inside} inside the host's line: runitems_e195.py read {good} of {len(withjson)} whole; the registered runitems.py "
       f"failed {old_fail} of the {inside} with the line inside")

    # ---- RB3: aifoundry3's real bytes (E193)
    a3 = []
    for d in D193:
        a3 += sorted(glob.glob(os.path.join(REPO, d, "*", "device-stdout.txt")))
    same, nrec, drops = 0, 0, 0
    t3 = Tree(S, "t-rb3", "X04 {")
    for f in a3:
        rc, runs, log, _ = t3.run(NEW, f, nk())
        rc0, runs0, _, _ = t3.run(OLD, f, nk())
        keys = list(json.loads(open(f).readline()[len("X04 "):]).keys())
        if rc == 0 and rc0 == 0 and len(runs) == len(runs0) and [own_fields(r, keys) for r in runs] == [own_fields(r, keys) for r in runs0]:
            same += 1
        nrec += len(runs)
        drops += log.count("runtime line(s) dropped")
    ok("RB3 aifoundry3's bytes", a3 and same == len(a3) and drops == 0,
       f"{len(a3)} committed device-stdout.txt files of E193 (aifoundry3, Sun 15 Nov 2026), {nrec} X04 records: both runners read the same "
       f"records field for field in {same}; runitems_e195.py dropped {drops} runtime lines (aifoundry3's runtime printed none on stdout)")

    # ---- RB4: the runtime line at every byte offset of a real aifoundry3 line
    line = open(a3[0]).readline()
    tag = "X04 {"
    js0 = json.loads(line[len(tag) - 1:])
    lo, hi = line.index("{"), len(line.rstrip("\n"))

    def read(text):
        kept, dropped = port.drop_runtime(text)
        recs = [json.loads(ln[len(tag) - 1:]) for ln in kept.splitlines() if ln.startswith(tag)]
        return recs, dropped
    allsame, nofs = 0, 0
    for off in range(0, hi + 1):
        txt = line[:off] + "Opening device 0\n" + line[off:]
        recs, dr = read(txt)
        nofs += 1
        allsame += recs == [js0] and len(dr) == 1
    two, _ = read(line[:lo + 40] + "Opening device 1\nOpening device 0\n" + line[lo + 40:])
    start, _ = read("Opening device 0\n" + line)
    t4 = Tree(S, "t-rb4", tag)
    runner_ok = 0
    offs = [lo + 1 + i * (hi - lo - 2) // 9 for i in range(10)]
    for off in offs:
        tg = os.path.join(S, "rb4-%d.txt" % off)
        open(tg, "w").write(line[:off] + "Opening device 0\n" + line[off:])
        rc, runs, log, _ = t4.run(NEW, tg, nk())
        runner_ok += rc == 0 and len(runs) == 1 and own_fields(runs[0], js0) == js0
    ok("RB4 every byte offset", allsame == nofs and two == [js0] and start == [js0] and runner_ok == len(offs),
       f"the runtime line at each of {nofs} offsets of a real X04 line read back the same record {allsame} times (the kit's own drop_runtime "
       f"and parse); two runtime lines at once: {'same' if two == [js0] else 'DIFFERENT'}; at the line's start: {'same' if start == [js0] else 'DIFFERENT'}; "
       f"the runner itself at {len(offs)} offsets: {runner_ok} whole")

    # ---- RB5: an unknown text inside a real line still fails the parse
    tg = os.path.join(S, "rb5.txt")
    open(tg, "w").write(line[:lo + 60] + "SOMETHING ELSE ON STDOUT\n" + line[lo + 60:])
    rc, runs, log, err = Tree(S, "t-rb5", tag).run(NEW, tg, nk())
    ok("RB5 unknown text fails closed", rc != 0 and not runs and "JSONDecodeError" in err,
       f"runitems_e195.py rc {rc}, {len(runs)} records, a JSONDecodeError: the pass would end (never a wrong datum)")

    # ---- RB6: where aifoundry3's runtime writes
    st = open(os.path.join(REPO, D192, "run/stderr.txt"), errors="replace").read()
    blocks, ready = st.count("LOGGER NOT INITIALIZED"), st.count("device ready in")
    e193err = sum(open(f, errors="replace").read().count("LOGGER NOT INITIALIZED") for d in D193 for f in glob.glob(os.path.join(REPO, d, "*", "device-stderr.txt")))
    opening = st.count("Opening device") + sum(open(f, errors="replace").read().count("Opening device") for d in D193
                                               for f in glob.glob(os.path.join(REPO, d, "*", "device-*.txt")))
    src_ok = "capture_output=True" in open(NEW).read()
    ok("RB6 aifoundry3's runtime on stderr", blocks >= 300 and e193err >= 4 and opening == 0 and src_ok,
       f"E192's run/stderr.txt (aifoundry3): {blocks} runtime device-layer blocks and {ready} 'device ready' lines; E193's device-stderr.txt: "
       f"{e193err} blocks; 'Opening device' in any of them and E193's stdout: {opening}; the runner reads stdout and stderr through separate pipes")

    # ---- RB7: the census of the runtime line in the lab's committed text files
    r = subprocess.run(["git", "-C", REPO, "grep", "-I", "-n", "Opening device", "HEAD", "--", "docs/reports/data"],
                       capture_output=True, text=True)
    rc_code = subprocess.run(["git", "-C", REPO, "grep", "-I", "-c", "Opening device", "HEAD", "--", "tools", "workloads", ":!docs"],
                             capture_output=True, text=True)
    ncode = sum(int(x.rsplit(":", 1)[1]) for x in rc_code.stdout.splitlines() if ":" in x)
    forms = {"line start": 0, "inside a host's line": 0, "quoted in JSON or prose": 0, "other": 0}
    other = []
    for ln in r.stdout.splitlines():
        parts = ln.split(":", 3)
        if len(parts) < 4:
            continue
        text = parts[3]
        for m in re.finditer(r"Opening device", text):
            after = text[m.end():]
            if not re.match(r" [0-9]+", after):
                if parts[1].startswith(("tools/claims-v3/e195/", "tools/claims-v3/e191/")) or "Opening device <n>" in text:
                    forms["quoted in JSON or prose"] += 1
                else:
                    forms["other"] += 1
                    other.append(f"{parts[1]}:{parts[2]}")
                continue
            if m.start() == 0:
                forms["line start"] += 1
            elif text.lstrip().startswith("{") and '"' not in text[max(0, m.start() - 1):m.start()]:
                forms["inside a host's line"] += 1
            else:
                forms["quoted in JSON or prose"] += 1
    ok("RB7 the census", forms["line start"] > 700 and forms["other"] == 0,
       f"'Opening device' in the lab's committed raw records at HEAD (docs/reports/data): {forms}; of another form: {other[:5]}; "
       f"beside them {ncode} mentions in code and prose under tools/ and workloads/ (readers that skip the line, a dry stub's own text)")

    n = sum(1 for _, g in RES if g)
    print(f"REALBYTES-E195 {n} of {len(RES)} {'PASS' if n == len(RES) else 'FAIL'}")
    return 0 if n == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
