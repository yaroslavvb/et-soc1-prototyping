#!/usr/bin/env python3
"""E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE REAL-BYTES DESK TEST (the round's lesson of Sun 15 Nov 2026,
E191's first session: "a host's stdout on a real box can carry runtime lines INSIDE the host's own output ... its real-path desk test feeds
the parser the REAL stdout bytes committed from a card"). EVERY reader of a device program's output in E199's chain is fed the bytes the
lab committed from aifoundry1 card 1 (E191's two sessions: 1a4bc1e3, whose smoke stdout holds aifoundry1's runtime line "Opening device 1"
INSIDE the ledger host's JSON line, and 7156ac15) and from E192's real session on aifoundry3 card 0 (a6e17e83), each file read at its
data directory's SHA256SUMS line:
  RB1  run_block.py's INTBITS reader (E192's, registered, unchanged; its three statements read from the file at its registered sha256
       38106da5...) on E192's 3,000+ real INTBITS records (each line re-made from runs.jsonl without run_block.py's own added fields):
       every record read back exactly;
  RB2  the same lines with aifoundry1's runtime line (its bytes cut from 1a4bc1e3's stdout) on a line of its own before the first INTBITS
       line, the intbits host's form (it prints nothing before it opens the card; one printf and fflush a line, main.cpp lines 408-417):
       every record read, the runtime line skipped;
  RB3  the runtime line at EVERY byte offset of a real INTBITS line: the reader reads it exactly (offset 0, or after the line's own
       newline), loses that one line (offsets 1-7, inside "INTBITS "), or raises (offsets 8 on: json.loads, the block ends): NEVER a
       record that differs from the host's; counted by outcome;
  RB4  END TO END: the REAL run_block.py, unchanged, run as a process with a stand-in host that prints the real bytes (its idles and quiet
       shortened by its own options: the reader is under test, not the protocol): the runtime line first (3 runs x 5 records read
       exactly); inside line 1 at offset 20 (exit 1, JSONDecodeError, no record of that run, none wrong); at offset 4 (that line lost,
       the rest read); 1a4bc1e3's committed stdout and 7156ac15's sparse-parity stdout as a host's whole output (no record, no crash);
  RB5  the gate's WATCH (gate_e199.stderr_wrong, the code the gate runs) on E191's real card-1 host stderr (no other card) and on E192's
       real aifoundry3 stderr (706 blocks naming /dev/et0_ops and ID 0: card 0's form refused);
  RB6  THE IDENTITY GATE (a) (ident_e199.config_gate) on E191's real card-1 config read (its stderr; its JSON line with the real runtime
       line first, and inside the line): OK; on E170's real aifoundry1 card-0 read ("Opening device 0" then minion_mv 519): refused;
       card 1's real read with E170's real runtime line ("Opening device 0") in place of card 1's: refused by that line alone (fix-e199,
       verify-e199 F5);
  RB7  the telemetry readers (run_block.last_sample, the reducer's jl, the gate's Tail) on E191's real aifoundry1 telemetry lines with
       the runtime line on its own line and inside a sample: the broken sample skipped, never a wrong one.
    /usr/bin/python3 -I -B tools/claims-v3/e199/desk/realbytes_e199.py <a scratch dir outside the repo>     (from the repository's top)
Prints REALBYTES-E199 <n> of <m> PASS (exit 0) or FAIL. Opens no device; the end-to-end runs use stand-in hosts only (run it inside
W/nodev.sh all the same). SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import threading
import time

TOP = os.getcwd()
S = sys.argv[1]
D191A = "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1"
D191B = "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2"
D192 = "docs/reports/data/2026-11-14-e192-intbits-aifoundry3"
D170 = "docs/reports/data/2026-11-04-e170-blind7-card0"
RUNBLOCK = "tools/claims-v3/e192/proposal/src/run_block.py"
RUNBLOCK_SHA = "38106da5"
ADDED = ("host", "pass", "seq", "role", "approach", "rc")
npass = ncase = 0
fails = []


def ok(cond, label, detail=""):
    global npass, ncase
    ncase += 1
    if cond:
        npass += 1
        print("-> PASS (%s)" % label, flush=True)
    else:
        fails.append(label.split(" ")[0])
        print("-> FAIL (%s%s)" % (label, (": " + str(detail)[:400]) if detail else ""), flush=True)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def committed(d, rel):
    """The file's bytes, checked against its data directory's SHA256SUMS line (any SHA256SUMS* list there that names it)."""
    b = open(os.path.join(TOP, d, rel), "rb").read()
    lines = []
    for fn in sorted(os.listdir(os.path.join(TOP, d))):
        if fn.startswith("SHA256SUMS"):
            lines += open(os.path.join(TOP, d, fn)).read().splitlines()
    want = [ln.split()[0] for ln in lines if ln.split()[-1:] and ln.split()[-1].lstrip("./*") in (rel, "./" + rel)]
    if want and want[0] != sha(b):
        raise SystemExit("%s/%s is not at its SHA256SUMS line" % (d, rel))
    return b, bool(want)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def reader(text):
    """run_block.py's three statements (lines 216-218), as RB1 checks they stand in the registered file: the records an INTBITS stdout
    yields; raises where run_block.py raises."""
    out = []
    for line in text.splitlines():
        if line.startswith("INTBITS "):
            rec = json.loads(line[len("INTBITS "):])
            out.append(rec)
    return out


def main():
    print("E199 real-bytes desk test (kit-e199), %s; Python %s" % (time.strftime("%F %T %Z"), sys.version.split()[0]), flush=True)
    os.makedirs(S, exist_ok=True)
    split, l1 = committed(D191A, "session/smoke/copy-64m-random/stdout.txt")
    spp, l2 = committed(D191B, "passes/sparse-parity/p1/stdout.txt")
    herr, l3 = committed(D191B, "passes/copy-random/p1/host.err")
    cerr, l4 = committed(D191B, "session/config-start.err")
    cjson, l5 = committed(D191B, "session/config-start.json")
    telgz, l6 = committed(D191B, "session/telemetry.jsonl.gz")
    runs, l7 = committed(D192, "run/runs.jsonl")
    a3err, l8 = committed(D192, "run/stderr.txt")
    c170 = open(os.path.join(TOP, D170, "aifoundry1-c0/config-start.txt"), "rb").read()
    m = re.search(rb"Opening device [0-9]+\n", split)
    RT = m.group(0).decode()
    print("inputs: 1a4bc1e3's split smoke stdout (%d B, listed %s; the runtime line at byte %d inside the host's line: %r); 7156ac15's "
          "sparse-parity stdout, a host.err, the config read, the telemetry (listed %s); E192's runs.jsonl and stderr.txt (listed %s); "
          "E170's card-0 config read" % (len(split), l1, m.start(), RT, all((l2, l3, l4, l5, l6)), l7 and l8), flush=True)
    src = open(os.path.join(TOP, RUNBLOCK), "rb").read()
    stmts = ('        for line in r.stdout.splitlines():\n            if line.startswith("INTBITS "):\n'
             '                rec = json.loads(line[len("INTBITS "):])\n')
    ok(sha(src).startswith(RUNBLOCK_SHA) and stmts.encode() in src, "RB0 run_block.py at its registered sha256 holds the reader's three statements verbatim (lines 216-218)")
    recs = [json.loads(x) for x in runs.decode().splitlines() if x.startswith("{")]
    base = [{k: v for k, v in r.items() if k not in ADDED} for r in recs]
    lines = ["INTBITS " + json.dumps(b, separators=(",", ":")) for b in base]
    got = reader("\n".join(lines) + "\n")
    ok(got == base and len(got) > 3000, "RB1 E192's %d real aifoundry3 INTBITS records, re-made as lines: every one read back exactly" % len(base))
    got2 = reader(RT + "\n".join(lines) + "\n")
    ok(got2 == base, "RB2 aifoundry1's real runtime line on its own line before the first INTBITS line: every record read, the runtime line skipped")
    ln = lines[0]
    outcome = {"exact": 0, "lost": 0, "raise": 0, "wrong": 0}
    for off in range(0, len(ln) + 1):
        t = ln[:off] + RT + ln[off:] + "\n" if off < len(ln) else ln + "\n" + RT
        try:
            g = reader(t)
        except ValueError:
            outcome["raise"] += 1
            continue
        if g == [base[0]]:
            outcome["exact"] += 1
        elif g == []:
            outcome["lost"] += 1
        else:
            outcome["wrong"] += 1
    ok(outcome["wrong"] == 0 and outcome["exact"] == 2 and outcome["lost"] == 7 and outcome["raise"] == len(ln) - 8,
       "RB3 the runtime line at every one of %d byte offsets of a real INTBITS line: %s (never a wrong record)" % (len(ln) + 1, outcome), outcome)
    # ---- RB4: the real run_block.py end to end with stand-in hosts printing the real bytes ----
    rb = os.path.join(TOP, RUNBLOCK)
    tel = os.path.join(S, "tel.jsonl")
    stop_tel = threading.Event()

    def tel_writer():
        while not stop_tel.is_set():
            with open(tel, "a") as f:
                f.write(json.dumps({"t_ms": int(time.time() * 1000), "board_w": 30.0, "temp_c": {"minshire": [50, 52, 49]},
                                    "mhz": {"minion": 600}}) + "\n")
            stop_tel.wait(0.1)
    th = threading.Thread(target=tel_writer, daemon=True)
    th.start()
    time.sleep(0.5)

    def e2e(name, payload):
        d = os.path.join(S, name)
        os.makedirs(d, exist_ok=True)
        pf = os.path.join(d, "payload.bin")
        open(pf, "wb").write(payload)
        host = os.path.join(d, "host.sh")
        open(host, "w").write("#!/bin/bash\ncat %s\nexit 0\n" % pf)
        os.chmod(host, 0o755)
        p = subprocess.run(["/usr/bin/python3", "-B", rb, os.path.join(d, "out"), "-1", "--smoke", "--host-bin", host, "--tel", tel,
                            "--idle", "0.2", "--quiet-s", "0.05", "--heater", ""], capture_output=True, text=True, timeout=120)
        rj = os.path.join(d, "out", "runs.jsonl")
        rr = [json.loads(x) for x in open(rj)] if os.path.exists(rj) else []
        return p.returncode, rr, p.stderr
    five = "\n".join(lines[:5]) + "\n"
    rc, rr, er = e2e("a-runtime-first", (RT + five).encode())
    ok(rc == 0 and len(rr) == 15 and [{k: v for k, v in r.items() if k not in ADDED} for r in rr] == base[:5] * 3,
       "RB4a the REAL run_block.py, a stand-in host printing the runtime line then 5 real lines (3 smoke runs): 15 records, each exactly the host's", (rc, len(rr), er[-200:]))
    bad1 = lines[0][:20] + RT + lines[0][20:] + "\n" + "\n".join(lines[1:5]) + "\n"
    rc, rr, er = e2e("b-inside-20", bad1.encode())
    ok(rc != 0 and "JSONDecodeError" in er and rr == [], "RB4b the runtime line inside line 1 at offset 20: run_block.py raises (exit %d, JSONDecodeError), no record of the run, none wrong" % rc, (rc, len(rr), er[-160:]))
    bad2 = lines[0][:4] + RT + lines[0][4:] + "\n" + "\n".join(lines[1:5]) + "\n"
    rc, rr, er = e2e("c-inside-4", bad2.encode())
    ok(rc == 0 and len(rr) == 12 and [{k: v for k, v in r.items() if k not in ADDED} for r in rr] == base[1:5] * 3,
       "RB4c the runtime line inside 'INTBITS ' (offset 4): that line lost, the other 4 read exactly in each run (12 records)", (rc, len(rr)))
    rc, rr, er = e2e("d-1a4bc1e3-stdout", split)
    rc2, rr2, er2 = e2e("e-7156ac15-spp-stdout", spp)
    ok(rc == 0 and rr == [] and rc2 == 0 and rr2 == [] and "0 launches" in er and "0 launches" in er2,
       "RB4d 1a4bc1e3's and 7156ac15's committed stdout as a host's whole output: no record, no crash (run_block.py reports 0 launches)", (rc, rc2, er[-120:]))
    stop_tel.set()
    th.join(timeout=2)
    # ---- RB5: the gate's watch on real stderr ----
    G = load(os.path.join(TOP, "tools/claims-v3/e199/gate_e199.py"), "gate_e199")
    b1, w1 = G.stderr_wrong(herr.decode(errors="replace"))
    b3, w3 = G.stderr_wrong(a3err.decode(errors="replace"))
    ok(b1 == ["1"] and w1 == [] and len(b3) == 706 and set(b3) == {"0"} and w3 == ["/dev/et0_ops", "Physical device ID 0"],
       "RB5 the gate's watch: E191's real card-1 host stderr names card 1 alone (no stop); E192's real aifoundry3 stderr (706 blocks) names card 0: refused", (b1, w1, len(b3), w3))
    # ---- RB6: the identity gate (a) on real config reads ----
    IE = load(os.path.join(TOP, "tools/claims-v3/e199/ident_e199.py"), "ident_e199")
    jl1 = cjson.decode().strip()
    w_a, f_a = IE.config_gate(RT + jl1 + "\n", cerr.decode(errors="replace"))
    i = jl1.index('"minion_mhz"')
    w_b, f_b = IE.config_gate(jl1[:i] + RT + jl1[i:] + "\n", cerr.decode(errors="replace"))
    w_c, f_c = IE.config_gate(c170.decode(), cerr.decode(errors="replace"))
    w_d, f_d = IE.config_gate(RT + jl1 + "\n", a3err.decode(errors="replace")[:4000])
    rt170 = re.search(r"Opening device [0-9]+\n", c170.decode()).group(0)
    w_e, f_e = IE.config_gate(rt170 + jl1 + "\n", cerr.decode(errors="replace"))
    ok(w_a == "" and f_a["runtime_lines"] == ["Opening device 1"] and w_b == "" and "minion_mv 519" in w_c and "/dev/et0_ops" in w_d
       and rt170 == "Opening device 0\n" and w_e.startswith("a runtime line names another device: Opening device 0"),
       "RB6 the identity gate (a): E191's real card-1 read with the runtime line first, and inside the JSON line: OK; E170's real card-0 read (minion_mv 519): refused; E192's aifoundry3 block: refused; card 1's real read with E170's real runtime line (Opening device 0): refused by that line alone", (w_a, w_b, w_c[:80], w_d[:80], w_e[:80]))
    # ---- RB7: the telemetry readers ----
    tl = [x for x in gzip.decompress(telgz).decode().splitlines() if x.startswith("{")][:400]
    RBM = load(rb, "run_block_for_test")
    RED = load(os.path.join(TOP, "tools/claims-v3/e192/proposal/src/reduce_intbits.py"), "reduce_for_test")
    good = [json.loads(x) for x in tl]
    k = 200
    own = tl[:k] + [RT.rstrip("\n")] + tl[k:]
    ins = tl[:k] + [tl[k][:30] + RT + tl[k][30:]] + tl[k + 1:]
    res = []
    for name, ls in (("own", own), ("inside", ins)):
        p = os.path.join(S, "tel-%s.jsonl" % name)
        open(p, "w").write("\n".join(ls) + "\n")
        j = RED.jl(p)
        t = G.Tail(p).read()
        last = RBM.last_sample(p)
        res.append((name, len(j), len(t), last == good[-1], all(x in good for x in j), all(x in good for x in t)))
    ok(res[0][1:] == (400, 400, True, True, True) and res[1][1:] == (399, 399, True, True, True),
       "RB7 the telemetry readers on E191's real aifoundry1 samples: the runtime line on its own line skipped (400 read), inside a sample: that sample skipped (399), never a wrong one", res)
    print("\nREALBYTES-E199 %d of %d %s" % (npass, ncase, "PASS" if not fails else "FAIL: " + ", ".join(fails)), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
