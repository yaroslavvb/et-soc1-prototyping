#!/usr/bin/env python3
"""E191's DRY-VS-REAL AUDIT, v2 (KIT.md.dated-note-2.md, Q184, Sun 15 Nov 2026, PST: after E189's data commit fa9098c4 of Sat 14 Nov 2026,
20:34:12 PST, and after E191's first session stopped at its smoke gate (1a4bc1e3), before any E191 pass datum). desk/dryaudit_e191.py
(eb1ac923, unchanged beside it) read on RUNNER v2 (run_e191_v2.py) against kit note 2's logs, with CONTEXT section 116's lesson made a
second part of it:
  PART 1 (v1's): every line of run_e191_v2.py that reads the dry flag (self.dry, a.dry), what the real path does there, and the desk cases
     that ran that real branch, each PASS in its committed log: the real-path test v2's (logs/realpath-e191-v2.txt, whose stand-in hosts
     print aifoundry1's split line), the runner test v2's (logs/selftest-run-e191-v2.txt) and the runbook test v2's (logs/selftest-rb-e191-v2.txt);
  PART 2 (kit note 2, section 116's lesson: "a host's stdout on a real box can carry runtime lines INSIDE the host's own output"): every line
     of run_e191_v2.py that reads a device process's STANDARD OUTPUT (r.stdout, proc.stdout, a host's text through C.host_result,
     C.config_json or C.drop_runtime), what it reads, and the cases that fed it the REAL committed bytes (logs/realbytes-e191.txt) and the
     real path's split stand-ins; and NO line may read a stdout through e191_common.last_json (v1's reader, which took the broken head).
A line it does not know is NOT COVERED (a new dry branch, or a new stdout read, fails the audit until it is mapped to its cases).
    /usr/bin/python3 -I -B tools/claims-v3/e191/desk/dryaudit_e191_v2.py      (from the top of the tree; DRY-AUDIT-E191-V2 <n> of <m>)
A desk check of code: nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dryaudit_e191 as V1  # noqa: E402

E = os.path.normpath(os.path.join(HERE, ".."))
RUNNER = os.path.join(E, "run_e191_v2.py")
LOGS = {"rp": os.path.join(E, "logs", "realpath-e191-v2.txt"), "run": os.path.join(E, "logs", "selftest-run-e191-v2.txt"),
        "rb": os.path.join(E, "logs", "selftest-rb-e191-v2.txt"), "rbytes": os.path.join(E, "logs", "realbytes-e191.txt")}
V1.LOGS = LOGS                                   # v1's passed() reads these
# PART 1: v1's map, with main()'s launch read by the runbook test v2's launch of session v2 (LA2)
MAP = [(k, w, [("rb:LA2" if c == "rb:LA" else c) for c in cs]) for (k, w, cs) in V1.MAP]
CONTEXT_MAP = V1.CONTEXT_MAP
# PART 2: every stdout read (a substring of the source line, what it reads, the cases that fed it real or split bytes)
STDOUT_MAP = [
    ('["date", "+%F"]', "the date command's output (the Pacific day for the box check; no device)", ["rp:RP1", "rp:RP5"]),
    ('["ps", "-eo", "uid=,pid=,comm="]', "ps's lines (the device processes of ours and of other users; no device)", ["rp:RP3", "rp:RP20"]),
    ("lines = w.stdout.splitlines()", "et-who's lines before the first card command and before each pass (it opens no device; an answer it "
     "cannot read refuses, finding 3)", ["rp:RP10", "rp:RP11", "rp:RP17", "rp:RP18", "rp:RP19"]),
    ("lines = r.stdout.splitlines()", "et-who's lines in the identity read (b)", ["rp:RP1", "rp:RP9"]),
    ("for raw in proc.stdout:", "the sampler's lines: only a line that begins with '{' and parses is a sample (v1's code, unchanged); the "
     "reader's own 'Opening device 1' line, printed whole before its samples (e142's committed telemetry.jsonl.raw holds it first), is skipped",
     ["rp:RP1", "rp:RP24", "rbytes:RB10"]),
    ("j = C.config_json(r.stdout)", "the config read: the runtime lines dropped, then v1's last line beginning with '{' (E170's committed "
     "aifoundry1 config read, 'Opening device 0' then its line, read the same as v1 read it)", ["rbytes:RB5", "rp:RP1", "rp:RP7"]),
    ('"runtime_lines": C.drop_runtime(text)[1]', "the self-test's record (no device: no runtime line)", ["rbytes:RB9", "rp:RP1"]),
    ("j, hl = C.host_result(text, kind, argv)", "THE SMOKE: each device-opening host's line reassembled and verified (the day's committed bytes "
     "read PASS; every split offset; truly failed hosts read FAILED; v1's runner on the split stand-ins reproduces the day's stop)",
     ["rbytes:RB1", "rbytes:RB3", "rbytes:RB6", "rbytes:RB7", "rbytes:RB8", "rp:RP1", "rp:RPS1", "rp:RPS5", "rp:RP12", "run:S2"]),
    ('good = rc == 0 and "SELFTEST PASS" in C.drop_runtime(text)[0]', "the self-test's lines read once the runtime lines drop",
     ["rbytes:RB9", "rp:RP1"]),
    ("j, hl = C.host_result(text, C.PROGRAM[cfg], argv)", "EVERY PASS: the host's line reassembled and verified; host-raw.json / host.json "
     "written from it (the frozen scorer's and the reducer's readers read the verified dict); a line not read is a FAILED RUN, flagged",
     ["rbytes:RB2", "rbytes:RB4", "rbytes:RB7", "rp:RP1", "rp:RPS2", "rp:RPS3", "rp:RPS4", "rp:RPS6", "rp:RPS7", "rp:RPS8", "run:S1", "run:S4"]),
]


def passed(kind, case):
    if kind == "rbytes":
        try:
            text = open(LOGS["rbytes"]).read()
        except OSError:
            return False
        return re.search(rf"^{re.escape(case)}: PASS\b", text, re.M) is not None
    if kind == "run" and re.match(r"^S\d+$", case):
        try:
            text = open(LOGS["run"]).read()
        except OSError:
            return False
        return re.search(rf"^== {re.escape(case)} .*\n(?:   .*\n)*-> PASS", text, re.M) is not None
    return V1.passed(kind, case)


def main():
    src = open(RUNNER).read().splitlines()
    func = ""
    rows, bad = [], []
    srows, sbad = [], []
    for i, ln in enumerate(src, 1):
        m = re.match(r"^\s*def (\w+)\(", ln)
        if m:
            func = m.group(1)
        code = ln.split("#", 1)[0]
        s = code.strip()
        if re.search(r"\b(self|a|self\.a)\.dry\b", code):
            hit = None
            if s in ("if self.dry:", "if not self.dry:"):
                hit = CONTEXT_MAP.get((func, s))
            else:
                for key, what, cases in MAP:
                    if what and key in code:
                        hit = (what, cases)
                        break
            if not hit:
                rows.append((i, func, s, "NOT MAPPED", [], False))
                bad.append(i)
            else:
                what, cases = hit
                good = bool(cases) and all(passed(*c.split(":", 1)) for c in cases)
                rows.append((i, func, s, what, cases, good))
                if not good:
                    bad.append(i)
        if re.search(r"\.stdout\b|\blast_json\(|\bhost_result\(|\bconfig_json\(|\bdrop_runtime\(", code) and not s.startswith(("def ", "\"\"\"")):
            if "last_json(" in code:
                srows.append((i, func, s, "READS A STDOUT THROUGH v1's last_json (the reader that took the broken head)", [], False))
                sbad.append(i)
                continue
            hit = next(((w, cs) for k, w, cs in STDOUT_MAP if k in code), None)
            if not hit:
                srows.append((i, func, s, "NOT MAPPED", [], False))
                sbad.append(i)
                continue
            what, cases = hit
            good = all(passed(*c.split(":", 1)) for c in cases)
            srows.append((i, func, s, what, cases, good))
            if not good:
                sbad.append(i)
    print(f"dryaudit_e191_v2 ({sys.executable} {sys.version.split()[0]}): run_e191_v2.py; part 1, every line that reads the dry flag; "
          f"part 2, every line that reads a device process's standard output (each case must read PASS in its committed log)")
    print("PART 1: the dry flag")
    for i, func, s, what, cases, good in rows:
        print(f"  line {i:4d} [{func}] {s[:96]}")
        print(f"      real path: {what}; cases {', '.join(cases) or 'none'}: {'COVERED' if good else 'NOT COVERED'}")
    print("PART 2: the standard output (kit note 2; section 116's lesson)")
    for i, func, s, what, cases, good in srows:
        print(f"  line {i:4d} [{func}] {s[:96]}")
        print(f"      reads: {what}; cases {', '.join(cases) or 'none'}: {'COVERED' if good else 'NOT COVERED'}")
    n = sum(1 for r in rows + srows if r[5])
    m = len(rows) + len(srows)
    allbad = bad + sbad
    print(f"DRY-AUDIT-E191-V2 {n} of {m} {'COVERED' if not allbad else 'NOT COVERED: lines ' + ', '.join(map(str, allbad))} "
          f"(part 1: {sum(1 for r in rows if r[5])} of {len(rows)}; part 2: {sum(1 for r in srows if r[5])} of {len(srows)})")
    return 0 if not allbad else 1


if __name__ == "__main__":
    sys.exit(main())
