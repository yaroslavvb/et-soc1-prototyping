#!/usr/bin/env python3
"""E199 (reg-e199, Q190), a desk check of code: E199's reduction pipeline on E192's own committed session re-makes E192's committed
prices byte for byte, so the forecast (E192's prices) is what the same pipeline gives on aifoundry3's data.

The pipeline (E199.md section 6.5): the session's run directory (runs.jsonl, marks.jsonl, telemetry.jsonl), then prefilter_e199.py
(E151's rail filter, unchanged), then E192's registered reducer reduce_intbits.py (715fddaa..., unchanged). Here the inputs are E192's
committed `run/runs.jsonl`, `run/marks.jsonl` and `run/telemetry.jsonl.gz` (unpacked), each checked against the session's own
`session/MANIFEST.sha256`, as E192's kit step 13 builds them. Needs numpy (the reducer's); run it in a private /dev.

    /usr/bin/python3 -I -B tools/claims-v3/e199/desk/pipeline_e192.py <an empty work dir outside the repository>

Prints PIPELINE-E192 PASS when: the filter removes no sample; the filtered telemetry equals the unpacked telemetry byte for byte; the
reducer's output equals intbits-e192.json byte for byte; and its printed lines equal intbits-e192.txt byte for byte.
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
D = os.path.join(TOP, "docs/reports/data/2026-11-14-e192-intbits-aifoundry3")
RED = os.path.join(TOP, "tools/claims-v3/e192/proposal/src/reduce_intbits.py")
PRE = os.path.join(TOP, "tools/claims-v3/e199/prefilter_e199.py")
PINS = {"reduce_intbits.py": "715fddaa36c1ca81889b20f39a649254479cb1db68d797c8a9876e0c0677d0b7",
        "intbits-e192.json": "0a675627f60ebad0002052c7f70c5042744a415a423a889b90c3b71f80a386c5",
        "intbits-e192.txt": "d18f40e616cf7cae722bcce20040274d46da8b8dd54c94adfa0d5da9329aa3c3"}


def sha_b(b):
    return hashlib.sha256(b).hexdigest()


def sha(p):
    with open(p, "rb") as f:
        return sha_b(f.read())


def main():
    work = sys.argv[1]
    if os.path.exists(work) and os.listdir(work):
        raise SystemExit("REFUSED: %s is not empty" % work)
    lines, ok = [], True

    def say(s, good=True):
        nonlocal ok
        ok = ok and good
        lines.append(("ok   " if good else "BAD  ") + s)

    say("reduce_intbits.py at its registered sha256 %s" % PINS["reduce_intbits.py"][:8], sha(RED) == PINS["reduce_intbits.py"])
    man = {}
    for l in open(os.path.join(D, "session/MANIFEST.sha256")):
        p = l.split()
        if len(p) == 2:
            man[p[1]] = p[0]
    run = os.path.join(work, "run")
    os.makedirs(run)
    for name in ("runs.jsonl", "marks.jsonl"):
        shutil.copyfile(os.path.join(D, "run", name), os.path.join(run, name))
    with gzip.open(os.path.join(D, "run/telemetry.jsonl.gz"), "rb") as f:
        tel = f.read()
    with open(os.path.join(run, "telemetry.jsonl"), "wb") as f:
        f.write(tel)
    for name in ("runs.jsonl", "marks.jsonl", "telemetry.jsonl"):
        got, want = sha(os.path.join(run, name)), man.get("./run/" + name)
        say("run/%s against session/MANIFEST.sha256: %s" % (name, got[:8]), got == want)
    flt = os.path.join(work, "run-filtered")
    r = subprocess.run([sys.executable, "-I", "-B", PRE, run, flt], capture_output=True, text=True)
    say("prefilter_e199.py rc %d: %s" % (r.returncode, r.stdout.strip()), r.returncode == 0)
    cen = json.load(open(os.path.join(flt, "railfilter-e199.json")))
    say("the rail filter removed %d of %d samples (F1 %d, F2 %d); the running-maximum field read %s" % (
        cen["union"], cen["samples"], cen["F1"], cen["F2"], cen["running_max_field_w"]), cen["union"] == 0)
    say("the filtered telemetry equals the unpacked telemetry byte for byte",
        sha(os.path.join(flt, "telemetry.jsonl")) == sha(os.path.join(run, "telemetry.jsonl")))
    for name in ("runs.jsonl", "marks.jsonl"):
        say("run-filtered/%s equals run/%s byte for byte" % (name, name), sha(os.path.join(flt, name)) == sha(os.path.join(run, name)))
    out = os.path.join(work, "intbits.json")
    r = subprocess.run([sys.executable, "-I", "-B", RED, flt, "--out", out], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with open(os.path.join(work, "intbits.txt"), "wb") as f:
        f.write(r.stdout)
    say("reduce_intbits.py rc %d" % r.returncode, r.returncode == 0)
    say("its output equals intbits-e192.json byte for byte (sha256 %s)" % sha(out)[:8], sha(out) == PINS["intbits-e192.json"])
    say("its printed lines equal intbits-e192.txt byte for byte (sha256 %s, %d lines)" % (
        sha_b(r.stdout)[:8], r.stdout.count(b"\n")), sha_b(r.stdout) == PINS["intbits-e192.txt"])
    lines.append("interpreter %s; numpy from the system" % sys.version.split()[0])
    lines.append("PIPELINE-E192 " + ("PASS" if ok else "FAIL"))
    print("\n".join(lines))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
