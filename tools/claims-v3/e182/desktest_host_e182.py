#!/usr/bin/env python3
"""E182 (Q153, the kit): read desktest_host_e182.sh's runs of the train host on the mock runtime. Standard library only; no device.

  D1  every train run printed 14 SPARSITY records (the calibration launch -1 and launches 0-12), each with "train_kind" by the registered
      schedule (launches -1 and 0 the orientation's first letter, launch n >= 1 letter (n - 1) mod 4), "train_values" that kind's file and
      "abba" the orientation; every record ok
  D2  the C log holds the two tile sets once each (distinct fnv) and one C record per launch whose fnv is the scheduled kind's tiles'
  D3  ccheck.py judged every launch of every run PASS against its own tiles (none ROUNDING, UNMODELLED or FAIL)
  D4  the dumped tiles (<run>.tiles and <run>.tiles.S) equal the F and S files byte for byte
  D5  the three refusals exited non-zero with E182's words (no --launches, a bad orientation, a built-in --values)
  D6  without --values-b the host runs a plain run (no train fields), and its C log PASSes
  D7  a tampered copy of t1_sffs's C log (one F launch's fnv set to the S tiles') FAILs that launch in ccheck.py: the pairing is checked
    /usr/bin/python3 -B desktest_host_e182.py <out-dir of desktest_host_e182.sh>
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.abspath(sys.argv[1])
T = os.path.join(TOP, "tools/claims-v3/e182/tiles")
T78 = os.path.join(TOP, "tools/claims-v3/e178/tiles")
RUNS = {"t1_sffs": ("int8", f"{T78}/int8/e178_v5.bin", f"{T78}/int8/e178_v4.bin", "SFFS"),
        "t1_fssf": ("int8", f"{T78}/int8/e178_v5.bin", f"{T78}/int8/e178_v4.bin", "FSSF"),
        "t2_sffs": ("int8", f"{T}/int8/e182_a1_bm1.bin", f"{T}/int8/e182_am1_b1.bin", "SFFS"),
        "t5_fssf": ("fp32", f"{T}/fp32/e182_a1_b3fffffff.bin", f"{T}/fp32/e182_a3fffffff_b1.bin", "FSSF"),
        "t6_sffs": ("fp32", f"{T78}/fp32/e178_v5.bin", f"{T78}/fp32/e178_v4.bin", "SFFS")}
FAILS, N = [], [0]


def say(ok, what):
    N[0] += 1
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def fnv64(b):
    h = 1469598103934665603
    for x in b:
        h ^= x
        h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return f"{h:016x}"


def sparsity(name):
    return [json.loads(x[len("SPARSITY "):]) for x in open(os.path.join(OUT, name + ".out")) if x.startswith("SPARSITY {")]


def clog(name):
    return [json.loads(x) for x in open(os.path.join(OUT, name + ".jsonl")) if x.strip().startswith("{")]


def summary(name):
    last = open(os.path.join(OUT, name + ".check")).read().strip().splitlines()[-1]
    return json.loads(last[last.index("{"):])


def main():
    for name, (ty, f, s, ori) in RUNS.items():
        recs = sparsity(name)
        sched = [ori[0] if n < 1 else ori[(n - 1) % 4] for n in range(-1, 13)]
        kinds = [r.get("train_kind") for r in recs]
        vals = [r.get("train_values") for r in recs]
        ok = (len(recs) == 14 and [r["launch"] for r in recs] == list(range(-1, 13)) and kinds == sched and
              all(v == "file:" + (f if k == "F" else s) for k, v in zip(kinds, vals)) and all(r.get("abba") == ori for r in recs) and
              all(r["ok"] for r in recs) and all(r["type"] == ty for r in recs))
        say(ok, f"D1 {name}: 14 records, kinds {''.join(k or '?' for k in kinds)} against {''.join(sched)}")
        cl = clog(name)
        tiles = [r for r in cl if r.get("kind") == "tiles"]
        cs = [r for r in cl if r.get("kind") == "c"]
        fF, fS = fnv64(open(f, "rb").read()), fnv64(open(s, "rb").read())
        ok = (len(tiles) == 2 and {t["fnv"] for t in tiles} == {fF, fS} and len(cs) == 14 and
              [c["fnv"] for c in cs] == [fF if k == "F" else fS for k in sched] and [c["launch"] for c in cs] == list(range(-1, 13)))
        say(ok, f"D2 {name}: tiles records {len(tiles)}, C records {len(cs)}, each C record's fnv the scheduled kind's")
        sm = summary(name)
        say(sm.get("PASS") == 14 and sm.get("FAIL") == 0 and sm.get("ROUNDING", 0) == 0 and sm.get("UNMODELLED", 0) == 0,
            f"D3 {name}: ccheck {sm}")
        dF = open(os.path.join(OUT, name + ".tiles"), "rb").read()
        dS = open(os.path.join(OUT, name + ".tiles.S"), "rb").read()
        say(dF == open(f, "rb").read() and dS == open(s, "rb").read(), f"D4 {name}: dumped F and S tiles equal their files")
    for name, word in (("refuse_nolaunches", "E182: a train needs --launches"), ("refuse_ori", "E182: --abba is SFFS or FSSF"),
                       ("refuse_builtin", "E182: a train takes --values file: and --values-b file:")):
        txt = open(os.path.join(OUT, name + ".out")).read()
        say(word in txt and "SPARSITY {" not in txt, f"D5 {name}: refused with '{word}', no launch")
    recs = sparsity("plain")
    sm = summary("plain")
    say(len(recs) >= 2 and all("train_kind" not in r for r in recs) and sm.get("FAIL") == 0 and sm.get("PASS") == len(recs),
        f"D6 plain run: {len(recs)} records with no train field, ccheck {sm}")
    # D7: tamper one F launch's fnv in t1_sffs's C log; ccheck must fail exactly that launch
    lines = open(os.path.join(OUT, "t1_sffs.jsonl")).read().splitlines()
    fF = fnv64(open(RUNS["t1_sffs"][1], "rb").read())
    fS = fnv64(open(RUNS["t1_sffs"][2], "rb").read())
    out, done = [], False
    for x in lines:
        r = json.loads(x) if x.strip().startswith("{") else None
        if not done and r and r.get("kind") == "c" and r.get("fnv") == fF:
            x = x.replace(f'"fnv":"{fF}"', f'"fnv":"{fS}"')
            done = True
        out.append(x)
    tp = os.path.join(OUT, "t1_tampered.jsonl")
    open(tp, "w").write("\n".join(out) + "\n")
    r = subprocess.run(["python3", os.path.join(TOP, "tools/claims-v3/ccheck/ccheck.py"), "check", tp, "--jobs", "2", "--cache",
                        os.path.join(OUT, "cache")], capture_output=True, text=True)
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "{}"
    sm = json.loads(last[last.index("{"):]) if "{" in last else {}
    say(done and r.returncode != 0 and sm.get("FAIL") == 1 and sm.get("PASS") == 13, f"D7 tampered pairing: ccheck rc {r.returncode}, {sm}")
    print(f"DESKTEST-HOST-E182 {N[0] - len(FAILS)} of {N[0]} PASS" + ("" if not FAILS else ": " + "; ".join(FAILS)))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
