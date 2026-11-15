#!/usr/bin/env python3
"""E191's DRY-VS-REAL AUDIT (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum; CONTEXT section
104's lesson, made code: "every card lane from now on is preceded by a dry-vs-real audit of its kit: each branch skipped in the dry path
must be covered by a desk test that runs the real path against stand-ins"). It reads run_e191.py's source, finds EVERY line that reads
the dry flag (self.dry, a.dry), and for each names what the real path does there and the desk cases that ran that real branch: the
real-path test's (desk/realpath_e191.py, its log logs/realpath-e191.txt) or, for main()'s refusals, the runner test's (its log
logs/selftest-run-e191.txt) and the runbook test's real session (logs/selftest-rb-e191.txt, case LA). Each named case must read PASS in its
committed log. A line it does not know is NOT COVERED (a new dry branch fails the audit until it is mapped to a real-path case).

    /usr/bin/python3 -I -B tools/claims-v3/e191/desk/dryaudit_e191.py      (from the top of the tree; prints DRY-AUDIT-E191 <n> of <m>)
A desk check of code: nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
RUNNER = os.path.join(E, "run_e191.py")
LOGS = {"rp": os.path.join(E, "logs", "realpath-e191.txt"), "run": os.path.join(E, "logs", "selftest-run-e191.txt"),
        "rb": os.path.join(E, "logs", "selftest-rb-e191.txt")}
# (a substring of the source line, what the real path does there, the cases that ran it: "rp:RPn", "run:Rn", "rb:LA")
MAP = [
    ("self.dry = a.dry", "the flag itself (no branch)", ["rp:RP1"]),
    ("self.watch_dir = self.dev_dir if self.dry else None", "the watch reads the cards' nodes where they are (/dev on the box; "
     "e191_ident.DEV_DIR): the sampler's fds and every host's tree", ["rp:RP1", "rp:RP9", "rp:RP12"]),
    ('w = ("DRY " + words) if self.dry', "no DRY mark on any line (the rest rule counts the session)", ["rp:RP1"]),
    ('"used": used_argv, "dry": self.dry', "each command recorded with its real form (used equals real)", ["rp:RP1"]),
    ('c = self.fake() + ["config"] if self.dry else self.real_config()', "the config read through E191's guard under `timeout 10` "
     "(its hostname and ET_DEVICES rules), its stderr kept", ["rp:RP1", "rp:RP7", "rp:RP8", "rp:RW1"]),
    ('if self.dry else self.real_sampler(seconds)', "the sampler through the guard; its own fds read for the identity",
     ["rp:RP1", "rp:RP9"]),
    ('c = self.fake() + ["etwho"] if self.dry else ["timeout", "20", "et-who"]', "et-who under `timeout 20` (PATH's et-who)",
     ["rp:RP1", "rp:RP10", "rp:RP11"]),
    ('"dry": self.dry,', "bookkeeping in run.json / pass.json / queue.json", ["rp:RP1"]),
    ('"lock": C.LOCK if not self.dry else "DRY"', "run.json names the card's lock", ["rp:RP1"]),
    ('"stub_card": self.a.double if self.dry else None', "run.json names no stub card", ["rp:RP1"]),
    ('"t_end_ms": t_end, "host_rc": rc, "host_status": j.get("status"), "reading": rd, "dry": self.dry', "bookkeeping in pass.json",
     ["rp:RP1"]),
    ('tag = " DRY" if self.dry else ""', "the session start line has no DRY tag (the rest rule counts it)", ["rp:RP1"]),
    ('result = {"t0": a.t0, "dry": self.dry', "bookkeeping in queue.json", ["rp:RP1"]),
    ('lockp = os.path.join(self.out, "dry.lock") if self.dry else C.LOCK', "card 1's lock (e191_common.LOCK), flock -n, held to the end",
     ["rp:RP1", "rp:RP2"]),
    ("if self.dry and self.device_opened:", "no dry check (the real path's commands are recorded in commands.jsonl; RP1 reads each "
     "real, each ET_DEVICES=1)", ["rp:RP1"]),
    ("if not a.dry:", "main(): the desk's overrides and V3_DRY refused without --dry; the registered session through session_e191.sh",
     ["run:R15", "rb:LA"]),
]
# the lines "if self.dry:" and "if not self.dry:" occur in more than one function: resolved by the function they are in
CONTEXT_MAP = {
    ("__init__", "if self.dry:"): ("the doubles' environment (schedule, stand-in nodes and lock, the alt card) is NOT set: the real nodes, "
                                   "lock and card", ["rp:RP1"]),
    ("host_cmd", "if self.dry:"): ("ONE host process under the real `timeout 10`, watched (stderr block, held nodes), the runner's bound",
                                   ["rp:RP1", "rp:RP12", "rp:RP13", "rp:RP14"]),
    ("our_device_procs", "if self.dry:"): ("the real ps read of our own device processes, the sampler's tree left out", ["rp:RP3"]),
    ("foreign", "if not self.dry:"): ("the real ps read: other users' device processes (a positive count needs a second login: not made on "
                                      "the desk) and our own (RP3)", ["rp:RP1", "rp:RP3"]),
    ("run", "if not self.dry:"): ("THE BOX CHECK: aifoundry1, ET_DEVICES=1, the reader at its pin, today's build records, hosts and (fix-e191k2) "
                                  "kernels at their records' sha256 with the kernel gate's OK line",
                                  ["rp:RP1", "rp:RP4", "rp:RP5", "rp:RP6", "rp:RP8", "rp:RW1", "rp:RP22", "rp:RP23"]),
}


def passed(kind, case):
    try:
        text = open(LOGS[kind]).read()
    except OSError:
        return False
    if kind == "rp":
        return re.search(rf"^{re.escape(case)}: PASS\b", text, re.M) is not None
    if kind == "run":
        return re.search(rf"^== {re.escape(case)} .*\n(?:   .*\n)*-> PASS", text, re.M) is not None
    return re.search(rf"^-> PASS \({re.escape(case)}\b", text, re.M) is not None


def main():
    src = open(RUNNER).read().splitlines()
    func = ""
    rows, bad = [], []
    for i, ln in enumerate(src, 1):
        m = re.match(r"^\s*def (\w+)\(", ln)
        if m:
            func = m.group(1)
        code = ln.split("#", 1)[0]
        if not re.search(r"\b(self|a|self\.a)\.dry\b", code):
            continue
        s = code.strip()
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
            continue
        what, cases = hit
        good = bool(cases) and all(passed(*c.split(":", 1)) for c in cases)
        rows.append((i, func, s, what, cases, good))
        if not good:
            bad.append(i)
    print(f"dryaudit_e191 ({sys.executable} {sys.version.split()[0]}): every line of run_e191.py that reads the dry flag, the real path "
          f"there, and the desk cases that ran it (each must read PASS in its committed log)")
    for i, func, s, what, cases, good in rows:
        print(f"  line {i:4d} [{func}] {s[:96]}")
        print(f"      real path: {what}; cases {', '.join(cases) or 'none'}: {'COVERED' if good else 'NOT COVERED'}")
    n = sum(1 for r in rows if r[5])
    print(f"DRY-AUDIT-E191 {n} of {len(rows)} {'COVERED' if not bad else 'NOT COVERED: lines ' + ', '.join(map(str, bad))}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
