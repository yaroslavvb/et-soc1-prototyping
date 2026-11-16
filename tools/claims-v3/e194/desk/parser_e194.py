#!/usr/bin/env python3
"""E194's parser test (Q183, the kit, Sun 15 Nov 2026, after E194's registration and before any E194 datum): THE HOST'S LINE
(e194_common.host_json), the fix for E191's stop record 1a4bc1e3 (CONTEXT section 116's lesson: a host's stdout on a real box can carry
runtime lines INSIDE the host's own output; every kit reads a host's result from a source no runtime print can split, and its desk test feeds
the parser the REAL stdout bytes committed from a card). Desk only: no device, no box; the one built host it runs (P7) runs inside the
round's sandbox (no /dev/et*, an empty /run/lock) with /sys hidden as well.

    /usr/bin/python3 -B tools/claims-v3/e194/desk/parser_e194.py [<a built ledger host> <its kernel ELF>]   (prints PARSER-E194 n of m PASS)

  P1  E191's committed aifoundry1 smoke stdout (copy-64m-random/stdout.txt, 1a4bc1e3: the ledger host's line split by "Opening device 1"):
      E191's last_json reads {} (the defect, reproduced); host_json reads the host's object (status PASS, 2,048 of 2,048 records, 0 bad,
      67,108,864 units, one launch), 'reassembled', the one dropped span "Opening device 1" a runtime line seen before; the object equals
      the bytes with that span removed, parsed;
  P2  E191's committed self-test stdout: no object ('none'), as the runner expects for the self-test (it reads "SELFTEST PASS");
  P3  E189's committed aifoundry3 smoke stdouts (eight files, 14 Nov 2026): each object read 'whole line', equal to its last line parsed;
  P4  E189's committed pass files (host-raw.json for the ledger passes, host.json for sparse parity's): each read 'whole line', equal;
  P5  THIS BOX's committed host stdouts (E190 arm A on aifoundry2 card 0, 13 Nov 2026, ET_DEVICES unset, the box's runtime): no line in any
      of them but the host's own (no runtime line), and host_json reads each line's object 'whole line';
  P6  this box's runtime libraries (/opt/et/lib/libetrt.so, libdeviceLayer.a) carry no "Opening device" string (aifoundry1's runtime
      printed it; a desk read of this box's files: the print E191 met cannot come from this box's runtime);
  P7  with a built ledger host: run it as E194's smoke runs its first device-opening process (--card, a 64 MiB copy, one launch), with
      ET_DEVICES unset, in the sandbox with /sys hidden (so it cannot reach the card): what this box's runtime prints on stdout before the
      open fails, and host_json on it; the same with ET_DEVICES=0 as a contrast (reported; the session never sets it);
  P8  E189's committed sha256 pass line with a runtime line inserted after EVERY token (one at a time), then two and three at once, a
      runtime line before and after the object, and a decoy line that begins with '{': the host's object every time, the dropped spans
      exactly the inserted ones;
  P9  refusals: a line cut short ('{"ledger":1,"prog":"cut'), a span inside a string value, an object that never closes: 'none' (never a
      guess), so the reading is a FAILED RUN or a failed gate, as registered.
fix-e194 (verify-e194's finding 2): e194_common.host_result, the reading the runner uses, on the same committed bytes and on the verifier's
attacks:
  P10 the committed real bytes, each against its own command line (E194's smoke and plan argv, which equal E189's): E191's split smoke
      (reassembled, the one runtime span), E189's seven smoke stdouts and 24 pass files (whole line), each equal to the object; and each
      of E189's ledger pass lines against ANOTHER configuration's command line: 'none' every time;
  P11 THE SWEEP: a foreign line at EVERY character position strictly inside two committed host lines (E189's sha256 pass line and E191's
      smoke object), for each of eleven lines (the digit, dot, e and E lines that a number-continuing reader merges, "42", "9", "E+7",
      "0 foo", ".5 x", "e5 bar", "1e3"; a lone "}"; an unknown word line; "Opening device 0 extra"; and the known "Opening device 0"):
      never a different object; the known runtime line read exactly at every token boundary and 'none' elsewhere; every other line 'none';
  P12 a stale object (a complete line, then a later line with the host's key cut short): 'none', never the earlier one; a runtime line
      before a nested object (so a '{' begins a line inside the host's line): the object; two complete lines: the last;
  P13 the config read: the reader's line split by a runtime line read; a digit line merged into minion_mv: 'none'; `e194_common.py
      --config-line` (step 7's reader on the box) prints the object, or nothing with exit 1.
A desk check of code on committed records; nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
sys.path.insert(0, E)
import e194_common as C  # noqa: E402

D191 = os.path.join(REPO, "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1/session/smoke")
D189 = os.path.join(REPO, "docs/reports/data/2026-11-14-e189-blind-day-aifoundry3")
D190 = os.path.join(REPO, "docs/reports/data/2026-11-13-e190-large-gemm/aifoundry2")
RES = []


def ok(cond, what):
    RES.append(bool(cond))
    print(f"-> {'PASS' if cond else 'FAIL'} ({what})", flush=True)


def last_json_e191(text):
    """E191's last_json, as committed (e191_common.py lines 134-141): the defect."""
    for ln in reversed(text.splitlines()):
        if ln.startswith("{"):
            try:
                return json.loads(ln)
            except ValueError:
                return {}
    return {}


def tokens_end(line):
    """Every position just after a complete token of a one-line JSON object (outside strings): where a runtime print can land."""
    pos, ins, esc = [], False, False
    for i, ch in enumerate(line):
        if ins:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                ins = False
                pos.append(i + 1)
            continue
        if ch == '"':
            ins = True
        elif ch in ",:{}[]":
            pos.append(i + 1)
        elif ch.isdigit() and (i + 1 == len(line) or not (line[i + 1].isdigit() or line[i + 1] in ".eE+-")):
            pos.append(i + 1)
        elif line[i - 2:i + 1] in ("rue", "lse", "ull") and i >= 2:
            pos.append(i + 1)
    return sorted(set(p for p in pos if 0 < p < len(line)))


def main(argv):
    print(f"parser_e194 ({sys.executable} {sys.version.split()[0]}); the repository at {os.path.basename(REPO)}")
    # ---- P1
    t = open(os.path.join(D191, "copy-64m-random", "stdout.txt")).read()
    o, r = C.host_json(t, "ledger")
    cut = t.replace("Opening device 1\n", "")
    want = json.loads(cut.strip())
    print(f"   P1: E191's last_json -> {last_json_e191(t)}; host_json -> method {r['method']}, dropped {r['dropped']}, runtime {r['runtime']}; "
          f"status {o.get('status')}, records {o.get('records_ok')}/{o.get('participants')}, bad {o.get('records_bad')}, units "
          f"{o.get('units')}/{o.get('units_expected')}, launches {o.get('launches')}")
    ok(last_json_e191(t) == {} and r["method"] == "reassembled" and r["dropped"] == ["Opening device 1"] and r["runtime"] == [True]
       and o == want and o.get("status") == "PASS" and o.get("records_ok") == 2048 and o.get("records_bad") == 0
       and o.get("units") == 67108864 and o.get("launches") == 1,
       "P1: the committed aifoundry1 bytes: E191's parser read {} (the defect); host_json reads the host's own object, one runtime span dropped")
    # ---- P2
    t = open(os.path.join(D191, "ledger-selftest", "stdout.txt")).read()
    o, r = C.host_json(t, "ledger")
    ok(r["method"] == "none" and o == {} and "SELFTEST PASS" in t, "P2: the self-test's stdout holds no object ('none'); its PASS line is read")
    # ---- P3
    files = sorted(glob.glob(os.path.join(D189, "session", "smoke", "*", "stdout.txt")))
    rows = []
    for f in files:
        txt = open(f).read()
        kind = os.path.basename(os.path.dirname(f))
        if kind == "ledger-selftest":
            continue
        w = "workload" if kind.startswith("sparse") else "ledger"
        o, r = C.host_json(txt, w)
        rows.append((kind, r["method"], o == last_json_e191(txt) and bool(o)))
    print(f"   P3: {rows}")
    ok(len(rows) == 7 and all(m == "whole line" and eq for _, m, eq in rows),
       "P3: E189's seven committed aifoundry3 smoke host stdouts read 'whole line', each equal to its last line parsed")
    # ---- P4
    rows = []
    for f in sorted(glob.glob(os.path.join(D189, "passes", "*", "p*", "host-raw.json")) +
                    glob.glob(os.path.join(D189, "passes", "sparse-parity", "p*", "host.json"))):
        txt = open(f).read()
        w = "workload" if "/sparse-parity/" in f else "ledger"
        o, r = C.host_json(txt, w)
        rows.append(r["method"] == "whole line" and o == last_json_e191(txt) and bool(o))
    ok(len(rows) == 24 and all(rows), f"P4: E189's {len(rows)} committed pass host files (20 ledger, 4 sparse parity) read 'whole line', each equal")
    # ---- P5
    outs = sorted(glob.glob(os.path.join(D190, "smoke", "*", "proc.out")) + glob.glob(os.path.join(D190, "runs", "*", "proc-*.out")))
    foreign, nlines, whole = 0, 0, 0
    for f in outs:
        for ln in open(f).read().splitlines():
            nlines += 1
            if not ln.startswith("SPARSITY {"):
                foreign += 1
                continue
            o, r = C.host_json(ln + "\n", "test")
            whole += int(r["method"] == "whole line" and o.get("test") in ("fma", "check"))
    print(f"   P5: {len(outs)} committed host stdouts of E190 arm A on this card, {nlines} lines, {foreign} not the host's own, {whole} read whole")
    ok(len(outs) == 87 and nlines > 0 and foreign == 0 and whole == nlines,
       "P5: this box's runtime (ET_DEVICES unset) printed no line of its own into any of 87 committed host stdouts; each line read whole")
    # ---- P6
    libs = [p for p in ("/opt/et/lib/libetrt.so", "/opt/et/lib/libdeviceLayer.a") if os.path.exists(p)]
    hits = {p: open(p, "rb").read().count(b"Opening device") for p in libs}
    print(f"   P6: 'Opening device' in this box's runtime libraries: {hits}")
    ok(len(libs) == 2 and all(v == 0 for v in hits.values()), "P6: this box's runtime carries no 'Opening device' string (a desk read of its files)")
    # ---- P7
    if len(argv) >= 2 and os.path.exists(argv[0]) and os.path.exists(argv[1]):
        host, elf = argv[0], argv[1]
        res = {}
        for name, extra in (("ET_DEVICES unset", {}), ("ET_DEVICES=0 (contrast; never set by the session)", {"ET_DEVICES": "0"})):
            env = {k: v for k, v in os.environ.items() if k not in ("ET_DEVICES", "V3_DEVICE")}
            env.update(extra, LD_LIBRARY_PATH="/opt/et/lib")
            argv_h = ["/usr/bin/bwrap", "--dev-bind", "/", "/", "--dev", "/dev", "--tmpfs", "/sys", "--tmpfs", "/run/lock", "--die-with-parent",
                      "--", "timeout", "10", host, "--card", "--kernel", elf, "--launches", "1", "--prog", "copy", "--bytes", "64M",
                      "--passes", "1", "--data", "random", "--width", "32"]
            p = subprocess.run(argv_h, capture_output=True, text=True, env=env, timeout=60, stdin=subprocess.DEVNULL)
            o, r = C.host_json(p.stdout, "ledger")
            other = [ln for ln in p.stdout.splitlines() if ln and not ln.startswith("{")]
            res[name] = (p.returncode, r["method"], other, p.stdout[:160])
            print(f"   P7 [{name}]: rc {p.returncode}; stdout {len(p.stdout)} B, its first 160: {p.stdout[:160]!r}; host_json {r['method']}"
                  f" (dropped {r['dropped']}); lines not the host's: {other}; stderr's last line: "
                  f"{(p.stderr.strip().splitlines() or [''])[-1][:160]!r}")
        a = res["ET_DEVICES unset"]
        ok(a[0] != 0 and not any("Opening device" in x for x in a[2]) and a[1] in ("none", "whole line"),
           "P7: the real ledger host built on this box, run to its device open in the sandbox (/sys hidden, no /dev/et*): the open fails; "
           "this box's runtime printed no 'Opening device' line on its stdout")
    else:
        print("   P7: NOT RUN (no built host given)")
    # ---- P8
    line = open(os.path.join(D189, "passes", "sha256", "p1", "host-raw.json")).read().strip()
    obj = json.loads(line)
    ends = tokens_end(line)
    good1 = 0
    for k in ends:
        o, r = C.host_json(line[:k] + "Opening device 0\n" + line[k:] + "\n", "ledger")
        good1 += int(o == obj and r["dropped"] == ["Opening device 0"])
    multi = 0
    picks = [ends[len(ends) // 5], ends[len(ends) // 2], ends[4 * len(ends) // 5]]
    for nins in (2, 3):
        s = line
        for k in sorted(picks[:nins], reverse=True):
            s = s[:k] + f"runtime line {k}\n" + s[k:]
        o, r = C.host_json(s + "\n", "ledger")
        multi += int(o == obj and len(r["dropped"]) == nins and r["runtime"] == [False] * nins)
    o3, r3 = C.host_json("Opening device 0\n" + line + "\nOpening device 0\n", "ledger")
    o4, r4 = C.host_json(line + '\n{"a decoy line a runtime printed"\n', "ledger")
    print(f"   P8: {good1} of {len(ends)} single insertions read the object exactly; {multi} of 2 multiple insertions; around: "
          f"{r3['method']}; decoy: {r4['method']} after {r4.get('candidates_tried')} candidates")
    ok(good1 == len(ends) and len(ends) > 50 and multi == 2 and o3 == obj and r3["method"] == "whole line" and o4 == obj,
       "P8: a runtime line at every token boundary, two and three at once, around the object, and a decoy '{' line: the object every time")
    # ---- P9
    n1 = C.host_json('{"ledger":1,"prog":"cut\n', "ledger")[1]["method"]
    n2 = C.host_json('{"ledger":1,"prog":"co' + "Opening device 0\n" + 'py","status":"PASS"}\n', "ledger")[1]["method"]
    n3 = C.host_json('{"ledger":1,"prog":"copy","width":32Opening device 0\n', "ledger")[1]["method"]
    ok(n1 == n2 == n3 == "none", "P9: a cut line, a span inside a string value, an object that never closes: 'none' each (never a guess)")
    # ---- fix-e194: host_result (the runner's reading), P10-P13
    smoke_argv = {n: a for n, a, k in C.smoke_runs(["ledger", "spp"])}
    t = open(os.path.join(D191, "copy-64m-random", "stdout.txt")).read()
    o, r = C.host_result(t, "ledger", smoke_argv["copy-64m-random"])
    rows = [("E191 smoke copy-64m-random", r["method"], o == json.loads(t.replace("Opening device 1\n", "").strip()) and r["dropped"] == ["Opening device 1"])]
    for f in sorted(glob.glob(os.path.join(D189, "session", "smoke", "*", "stdout.txt"))):
        name = os.path.basename(os.path.dirname(f))
        if name == "ledger-selftest":
            continue
        txt = open(f).read()
        kind = "spp" if name.startswith("sparse") else "ledger"
        o, r = C.host_result(txt, kind, smoke_argv[name])
        rows.append((f"E189 smoke {name}", r["method"], o == last_json_e191(txt) and bool(o)))
    other = 0
    for f in sorted(glob.glob(os.path.join(D189, "passes", "*", "p*", "host-raw.json")) +
                    glob.glob(os.path.join(D189, "passes", "sparse-parity", "p*", "host.json"))):
        cfg = f.split(os.sep)[-3]
        txt = open(f).read()
        o, r = C.host_result(txt, C.PROGRAM[cfg], C.host_argv(cfg, None, "X"))
        rows.append((f"E189 {cfg}/{f.split(os.sep)[-2]}", r["method"], o == last_json_e191(txt) and bool(o)))
        if C.PROGRAM[cfg] == "ledger":
            for cfg2 in C.LEDGER:
                if cfg2 != cfg and C.host_argv(cfg2) != C.host_argv(cfg):
                    other += int(C.host_result(txt, "ledger", C.host_argv(cfg2))[1]["method"] == "none")
    good = [x for x in rows if x[1] in ("whole line", "reassembled") and x[2]]
    print(f"   P10: {len(good)} of {len(rows)} committed host stdouts and lines read by host_result against their own command lines "
          f"(the split one {rows[0][1]}); E189's 20 ledger pass lines against the 4 other configurations' command lines: {other} of 80 'none'")
    ok(len(rows) == 32 and len(good) == 32 and rows[0][1] == "reassembled" and other == 80,
       "P10: every committed real host line reads by host_result against its own command line (E191's split smoke reassembled); "
       "against another configuration's command line, 'none' every time")
    lines = [("E189 sha256 p1", open(os.path.join(D189, "passes", "sha256", "p1", "host-raw.json")).read().strip(), C.host_argv("sha256")),
             ("E191 smoke copy-64m-random", t.replace("Opening device 1\n", "").strip(), smoke_argv["copy-64m-random"])]
    inserts = ["42", "9", "E+7", "0 foo", ".5 x", "e5 bar", "1e3", "}", "Warning: something", "Opening device 0 extra", "Opening device 0"]
    wrong, positions, rows11 = 0, 0, []
    for name, line, argv in lines:
        obj = json.loads(line)
        keyend = len('{"ledger"')
        between = set()
        for k in range(1, len(line)):           # where JSON allows whitespace: a space there leaves the object as it was
            try:
                if json.loads(line[:k] + " " + line[k:]) == obj:
                    between.add(k)
            except ValueError:
                pass
        want_known = {k for k in between if k >= keyend}       # the key's own '{"ledger"' must stay whole (fail-safe 'none' inside it)
        known_exact, other_exact = set(), 0
        for k in range(1, len(line)):
            positions += 1
            for ins in inserts:
                o, r = C.host_result(line[:k] + ins + "\n" + line[k:] + "\n", "ledger", argv)
                if o and o != obj:
                    wrong += 1
                elif o == obj and ins == "Opening device 0":
                    known_exact.add(k)
                elif o == obj:
                    other_exact += 1            # the object read exactly as the host printed it (a '}' that took the last brace's place)
        rows11.append((name, len(line), len(between), len(want_known), known_exact == want_known, other_exact))
    print(f"   P11: {positions} positions x {len(inserts)} lines = {positions * len(inserts)} insertions; a different object: {wrong}; per line "
          f"(name, length, positions between tokens, of them past the key, the known runtime line read exactly at exactly those, any other "
          f"line read as the exact object): {rows11}")
    ok(wrong == 0 and positions > 1000 and all(x[4] for x in rows11) and all(x[3] > 50 for x in rows11) and all(x[5] <= 1 for x in rows11),
       "P11: a foreign line at every position inside two committed host lines: never a different object (the digit, dot, e and E lines "
       "a number-continuing reader merged read 'none'); the known runtime line read exactly at every position between tokens past the "
       "host's key and nowhere else")
    line, argv = lines[0][1], lines[0][2]
    obj = json.loads(line)
    k = line.index("{", line.index('"hart0_cycles"'))
    s1 = C.host_result(line + "\n" + line[:200] + "\n", "ledger", argv)
    s2 = C.host_result(line[:k] + "Opening device 0\n" + line[k:] + "\n", "ledger", argv)
    s3 = C.host_result(json.dumps(dict(obj, launches=obj["launches"] - 1)) + "\n" + line + "\n", "ledger", argv)
    print(f"   P12: a stale object: {s1[1]['method']} ({str(s1[1].get('why'))[:90]}); a runtime line before a nested object: {s2[1]['method']}; "
          f"two complete lines: the last read {s3[0] == obj}")
    ok(s1[0] == {} and s1[1]["method"] == "none" and "an earlier one is never read" in s1[1]["why"] and s2[0] == obj and s3[0] == obj,
       "P12: a later line with the host's key that cannot be read reads 'none' (never the earlier complete one); a '{' that begins a line "
       "inside the host's line does not hide it; of two complete lines, the last")
    cfgl = '{"tdp_w":65,"temp_threshold_c":65,"power_state":3,"power_state_name":"low_power","minion_mhz":600,"minion_mv":519}'
    c1 = C.host_result(cfgl.replace(',"minion_mhz"', 'Opening device 0\n,"minion_mhz"') + "\n", "config")
    c2b = C.host_result(cfgl.replace(':519}', ':5') + "19\n}\n", "config")
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        pf = os.path.join(td, "config.out")
        open(pf, "w").write("Opening device 0\n" + cfgl + "\n")
        g = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "e194_common.py"), "--config-line", pf], capture_output=True, text=True)
        open(pf, "w").write(cfgl.replace(':519}', ':5') + "19\n}\n")
        b = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "e194_common.py"), "--config-line", pf], capture_output=True, text=True)
    print(f"   P13: the config line split by a runtime line: {c1[1]['method']}; a digit line merged into minion_mv: {c2b[1]['method']} "
          f"({str(c2b[1].get('why'))[:80]}); --config-line: rc {g.returncode} {g.stdout.strip()[:60]!r}; on the merged line rc {b.returncode}, "
          f"stdout {b.stdout.strip()!r}")
    ok(c1[0] == json.loads(cfgl) and c2b[0] == {} and c2b[1]["method"] == "none" and g.returncode == 0
       and json.loads(g.stdout) == json.loads(cfgl) and b.returncode == 1 and b.stdout.strip() == "",
       "P13: the config read split by a runtime line read; a digit line merged into minion_mv 'none'; step 7's --config-line prints the "
       "object, or nothing (exit 1)")
    print(f"PARSER-E194 {sum(RES)} of {len(RES)} {'PASS' if all(RES) else 'FAIL'}")
    return 0 if all(RES) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
