#!/usr/bin/env python3
"""E191's runner desk test, v2 (KIT.md.dated-note-2.md, Q184, Sun 15 Nov 2026, PST: after E189's data commit fa9098c4 of Sat 14 Nov 2026,
20:34:12 PST, and after E191's first session stopped at its smoke gate (1a4bc1e3), before any E191 pass datum): EVERY case of
selftest_run_e191.py (eb1ac923, unchanged beside it: R1-R19, E2E, R2E/R3E and the cut-tail control, I1-I10, B1-B2, D1, F1-F7, W1-W4, Q1-Q5;
its docstring names each) run on RUNNER v2 (run_e191_v2.py) in --dry sessions with DOUBLES v2 (fake_card_e191_v2.py: the ledger host's
line printed in main.cpp's two parts with the runtime's "Opening device 1" line INSIDE it, as aifoundry1 printed it on Sun 15 Nov 2026;
sparse parity's line after the runtime's line), so every case meets the split line, then kit note 2's cases on the dry path (the box's
step 8 v2 runs this path):
  S1  a plain session in the split form: every pass PASS, and every pass directory holds its raw stdout.txt (the ledger's with the runtime
      line inside its line), host-raw.json / host.json from the verified line, run.json's host_line naming the dropped line; every
      device-opening smoke.json the same; the session's start line names "kit note 2";
  S2  an unknown text inside the ledger host's line (E191_FAKE_RUNTIME=garble): the smoke gate fails safe, rc 16, "status None (the host's
      line was not read: ...)", no pass;
  S3  no runtime line (aifoundry3's form, =none): every pass PASS, nothing dropped;
  S4  a host that dies after it opened the card in pass 1 (E191_FAKE_HOST=crash from the 8th host, once): pass 1 a FAILED RUN flagged
      "the host's line was not read", the session goes on, rc 0.
    /usr/bin/python3 -B tools/claims-v3/e191/selftest_run_e191_v2.py <scratch dir outside the repo> [--no-e2e]
Prints the v1 test's own summary line, then SELFTEST-RUN-E191-V2 <n> of <m> PASS or FAIL (both parts); exit 0 or 1. A desk check of code:
nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_e191_v2  # noqa: E402
import selftest_run_e191 as ST  # noqa: E402

ST.RUN = os.path.join(HERE, "run_e191_v2.py")            # every v1 case on runner v2 (which runs doubles v2)
sys.modules["run_e191"] = run_e191_v2                    # D1's `import run_e191 as RR` reads runner v2's dry check


def note2_cases(S):
    mine = []

    def ok(cond, what):
        mine.append(bool(cond))
        print(f"-> {'PASS' if cond else 'FAIL'} ({what})", flush=True)
    C = run_e191_v2.C
    print("== S1 a plain session in aifoundry1's split form: the files of kit note 2")
    r, out, log, q = ST.session(S, "s1")
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    rows = []
    good = r.returncode == 0 and len(ran) == 6 and all(x.get("reading") == "PASS" for x in ran) and "plan FULL; kit note 2;" in log
    for x in ran:
        d = os.path.join(out, "passes", x["pass"])
        so = open(os.path.join(d, "stdout.txt")).read() if os.path.exists(os.path.join(d, "stdout.txt")) else ""
        rj = json.load(open(os.path.join(d, "run.json")))
        cfg = x["pass"].split("/")[0]
        want, _ = C.host_result(so, C.PROGRAM[cfg], C.host_argv(cfg, None, d))
        f = "host.json" if cfg == "sparse-parity" else "host-raw.json"
        got = json.loads(open(os.path.join(d, f)).read() or "{}")
        inside = so.startswith("Opening device 1\n{") if cfg == "sparse-parity" else ("Opening device 1\n," in so)
        g = bool(want) and got == want and inside and (rj.get("host_line") or {}).get("runtime_lines") == ["Opening device 1"]
        rows.append(f"{x['pass']} {'ok' if g else 'NOT ok'}")
        good = good and g
    smk = [json.load(open(os.path.join(out, "smoke", n, "smoke.json"))) for n in sorted(os.listdir(os.path.join(out, "smoke")))
           if n != "ledger-selftest"] if os.path.isdir(os.path.join(out, "smoke")) else []
    good = good and len(smk) == 7 and all(m.get("good") and (m.get("host_line") or {}).get("runtime_lines") == ["Opening device 1"] for m in smk)
    print(f"   {rows}; {len(smk)} device-opening smoke records")
    ok(good, "every pass PASS from its reassembled line; stdout.txt raw (the runtime line inside), the verified line in host-raw.json / "
             "host.json, host_line recorded; each device-opening smoke.json the same; 'kit note 2' on the start line")
    print("== S2 an unknown text inside the ledger host's line (E191_FAKE_RUNTIME=garble)")
    r, out, log, q = ST.session(S, "s2", env={"E191_FAKE_RUNTIME": "garble"})
    ok(r.returncode == 16 and "smoke gate failed: copy-64m-random: rc 0, status None (the host's line was not read:" in log and not q.get("queue"),
       "the line not read: the smoke gate fails safe, rc 16, no pass")
    print("== S3 no runtime line (aifoundry3's form)")
    r, out, log, q = ST.session(S, "s3", env={"E191_FAKE_RUNTIME": "none"})
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    rts = [(json.load(open(os.path.join(out, "passes", x["pass"], "run.json"))).get("host_line") or {}).get("runtime_lines") for x in ran]
    ok(r.returncode == 0 and len(ran) == 6 and all(x.get("reading") == "PASS" for x in ran) and all(t == [] for t in rts),
       "every pass PASS, nothing dropped")
    print("== S4 a host that dies after it opened the card, in pass 1")
    r, out, log, q = ST.session(S, "s4", env={"E191_FAKE_HOST": "crash", "E191_FAKE_HOST_FROM": "8", "E191_FAKE_HOST_COUNT": "1"})
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    p1 = json.load(open(os.path.join(out, "passes", "copy-zeros", "p1", "pass.json"))) if ran else {}
    ok(r.returncode == 0 and len(ran) == 6 and ran[0].get("reading", "").startswith("FAILED RUN")
       and any(f.startswith("the host's line was not read") for f in p1.get("flags") or []) and all(x.get("reading") == "PASS" for x in ran[1:]),
       "pass 1 a FAILED RUN flagged 'the host's line was not read'; the other five PASS; rc 0")
    return mine


if __name__ == "__main__":
    S = sys.argv[1]
    if os.path.abspath(S).startswith(ST.REPO + os.sep):
        sys.exit("the scratch directory must be outside the repository")
    os.makedirs(S, exist_ok=True)
    print(f"selftest_run_e191_v2 ({sys.executable} {sys.version.split()[0]}): selftest_run_e191.py's cases on run_e191_v2.py "
          f"({ST.RUN == os.path.join(HERE, 'run_e191_v2.py')}) with fake_card_e191_v2.py's doubles, then kit note 2's S1-S4", flush=True)
    ST.main(os.path.abspath(S), e2e="--no-e2e" not in sys.argv)
    m = note2_cases(os.path.abspath(S))
    n, tot = sum(ST.results) + sum(m), len(ST.results) + len(m)
    print(f"SELFTEST-RUN-E191-V2 {n} of {tot} {'PASS' if n == tot else 'FAIL'} (v1's cases {sum(ST.results)} of {len(ST.results)}, "
          f"kit note 2's {sum(m)} of {len(m)})")
    sys.exit(0 if n == tot else 1)
