#!/usr/bin/env python3
"""E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE AUDIT OF EVERY BRANCH THE DRY PASS SKIPS, and the case of a
desk test that ran it for real. The dry pass (session_e199.sh --dry: E192's run_session.sh in its DRY mode) prints every device call and
opens nothing, so it runs none of the branches below; each is named with the file it lives in and the cases that ran it, and the audit
reads the committed logs (logs/desktest-realpath-e199.txt, logs/realbytes-e199.txt, logs/selftest-rb-e199.txt) for each case's PASS
line. A branch is COVERED only when every case named for it reads PASS there. The branches no desk case can reach are listed apart, each
with why (never counted as covered).
    /usr/bin/python3 -I -B tools/claims-v3/e199/desk/dryaudit_e199.py        (from the repository's top)
Prints one line a branch and DRY-AUDIT-E199 <n> of <m> COVERED (exit 0 when every branch is), else NOT COVERED (exit 1).
SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import sys

L = "tools/claims-v3/e199/logs/"
LOGS = {"rp": L + "desktest-realpath-e199.txt", "rb": L + "realbytes-e199.txt", "rbk": L + "selftest-rb-e199.txt"}
BRANCHES = [
    # (file, branch, [(log, case label prefix), ...])
    ("session_e199.sh", "a desk-test variable without E199_DESKTEST=1 refused", [("rp", "R2 ")]),
    ("session_e199.sh", "the host's name (aifoundry1 by hostname and Python) refused otherwise", [("rp", "R1 ")]),
    ("session_e199.sh", "a registered session file of E192's off its sha256 refused", [("rp", "R4 ")]),
    ("session_e199.sh", "the kit's list off the sha256 the runbook passed refused", [("rp", "R3 ")]),
    ("session_e199.sh", "the reader off E191's pin refused", [("rp", "R5 ")]),
    ("session_e199.sh", "THE SELECTION: a binary without ET_DEVICES refused before anything", [("rp", "R6 ")]),
    ("session_e199.sh", "aifoundry1's two cards' nodes counted by name (only card 1's; three nodes)", [("rp", "N1 "), ("rp", "N2 ")]),
    ("session_e199.sh", "no card 1 lock file refused", [("rp", "R7 ")]),
    ("session_e199.sh", "no deadline refused (the real path only)", [("rp", "R8 ")]),
    ("session_e199.sh", "the free check: a holder on card 1, on card 0, another user's process, card 1's lock held", [("rp", "H1 "), ("rp", "H1b "), ("rp", "H2 "), ("rp", "H3 ")]),
    ("session_e199.sh", "THE FIRST CARD COMMAND and THE IDENTITY GATE (a): OK, card 0's block, card 0's voltage", [("rp", "P2 "), ("rp", "IA1 "), ("rp", "IA2 ")]),
    ("session_e199.sh", "the config read: the runtime line inside its JSON; no config once (one more read); twice (exit 16)", [("rp", "IA3 "), ("rp", "IA4 "), ("rp", "IA5 ")]),
    ("session_e199.sh", "the guard: ET_DEVICES missing or 0, a word but config refused; ET_DEVICES=1 runs the read", [("rp", "0f "), ("rp", "0g ")]),
    ("session_e199.sh", "the per-sensor probe and the sampler's choice (pvt; the go's plain sampler)", [("rp", "P3 "), ("rp", "FE ")]),
    ("session_e199.sh", "the gate watcher's death (STOP), a signal to the wrapper (STOP)", [("rp", "G4 "), ("rp", "T ")]),
    ("session_e199.sh", "SESSION_DONE written by the wrapper when run_session.sh exits before its EXIT trap", [("rp", "B7 ")]),
    ("session_e199.sh", "the end config read, kept with its stderr", [("rp", "P16 ")]),
    ("gate_e199.py", "THE SMOKE GATE: GO with card 1's identity block from each smoke device process; a failed smoke run", [("rp", "P7 "), ("rp", "G1 ")]),
    ("gate_e199.py", "THE CAP: read before each pass; D0 before pass 0", [("rp", "P15 "), ("rp", "G2a ")]),
    ("gate_e199.py", "CARD 1'S LIVE STOP LINES: board >= 65 W; minshire[0] >= 70 C; 65 W before the heater check's 70 W", [("rp", "LS1 "), ("rp", "LS2 "), ("rp", "HC ")]),
    ("gate_e199.py", "THE IDENTITY GATE (b): OK; ours on card 0; another login on card 0; the sampler holding nothing", [("rp", "P6 "), ("rp", "IB1 "), ("rp", "IB2 "), ("rp", "IB3 ")]),
    ("gate_e199.py", "THE WATCH: a host naming card 0 on its stderr; a host holding card 0's node; the smoke's heater naming card 0", [("rp", "W1 "), ("rp", "W2 "), ("rp", "W3 ")]),
    ("gate_e199.py", "THE WATCH's stderr reader on real bytes (card 1's committed stderr passes; aifoundry3's 706 card-0 blocks refused)", [("rb", "RB5 ")]),
    ("run_session.sh (E192's)", "its node count and selection: two cards unset; a binary ignoring ET_DEVICES (line 65); et1_ops not a node", [("rp", "N3 "), ("rp", "N4 "), ("rp", "N5 ")]),
    ("run_session.sh (E192's)", "free_before_sampler refusing after the first card command; free_with_sampler refusing (a holder of ours on card 0)", [("rp", "B7 "), ("rp", "IB1 ")]),
    ("run_session.sh (E192's)", "the sampler for the session, stopped by SIGTERM; locked_block (card 1's lock held for every host and heater)", [("rp", "P5 "), ("rp", "P11 "), ("rp", "P13 ")]),
    ("run_session.sh (E192's)", "the passes, STOP after the gap (THE STOP PATH, two passes)", [("rp", "P14 ")]),
    ("run_block.py (E192's)", "run(): INTBITS parsing on the real path, with aifoundry1's runtime line first on every host", [("rp", "P12 "), ("rp", "P10.0 "), ("rp", "P10.1 ")]),
    ("run_block.py (E192's)", "run(): the runtime line inside an INTBITS line (the block raises; no wrong record)", [("rp", "RT1 "), ("rb", "RB3 "), ("rb", "RB4b "), ("rb", "RB4c ")]),
    ("run_block.py (E192's)", "run(): E192's real aifoundry3 records and aifoundry1's committed stdout bytes", [("rb", "RB1 "), ("rb", "RB2 "), ("rb", "RB4a "), ("rb", "RB4d ")]),
    ("run_block.py (E192's)", "reading(): hot; stale; heater_check() on the real path", [("rp", "LS2 "), ("rp", "S3 "), ("rp", "P8 ")]),
    ("run_block.py, the reducer, the gate (telemetry readers)", "the runtime line on its own line and inside a sample", [("rb", "RB7 ")]),
    ("stopwatch.py (E192's)", "its die and staleness stops (its board stop: card 1's 65 W line acts first, LS1)", [("rp", "LS2 "), ("rp", "S3 ")]),
    ("ident_e199.py", "THE IDENTITY GATE (a) on real config reads (card 1's passes; card 0's refused; a runtime line naming device 0 refused)", [("rb", "RB6 ")]),
    ("rb/s09_a1_reads_e199.sh", "step 7's config read only after the rest opens (refused before it, no config read sent)", [("rbk", "R7a")]),
    ("rb/rest_rule_e199.sh", "the rest rule through step 9 (refused at 10 minutes; launched at 45)", [("rbk", "RS a session 10 min ago")]),
    ("rb/s20_wait_e199.sh", "the wait's session-name patterns on the real script (RUN-RUNNING) and against a decoy name alive past the bound (RUN-GONE in one loop)", [("rbk", "W1r "), ("rbk", "WN ")]),
]
NOT_REACHED = [
    ("stopwatch.py", "its board stop (above 80 W on three distinct readings): on card 1 the gate's 65 W line writes STOP at the first sample at or "
     "above 65 W (LS1), so stopwatch's 80 W rule cannot act first; its 'no telemetry sample in the first 60 s': the block's own reading stops "
     "the smoke first (S3, as in E192's kit)"),
    ("run_session.sh", "a killed run_session.sh (SIGKILL): nothing of ours sends one"),
    ("the box", "the reader, the heater and the host on aifoundry1's running build; our own live collector's real duty cycle on card 1's "
     "management node: read on the card day only"),
]


def main():
    top = os.getcwd()
    text = {}
    for k, p in LOGS.items():
        try:
            text[k] = open(os.path.join(top, p), errors="replace").read()
        except OSError:
            text[k] = ""
    n = cov = 0
    for f, b, cases in BRANCHES:
        n += 1
        res = []
        for lg, lab in cases:
            hit = re.search(r"^-> PASS \(" + re.escape(lab), text[lg], re.M)
            res.append("%s:%s %s" % (lg, lab.strip(), "PASS" if hit else "MISSING"))
        good = all(x.endswith("PASS") for x in res)
        cov += good
        print("%s | %s | %s | %s" % ("COVERED" if good else "NOT COVERED", f, b, "; ".join(res)))
    for f, why in NOT_REACHED:
        print("NOT REACHED AT THE DESK (named, not counted) | %s | %s" % (f, why))
    print("DRY-AUDIT-E199 %d of %d %s" % (cov, n, "COVERED" if cov == n else "NOT COVERED"))
    return 0 if cov == n else 1


if __name__ == "__main__":
    sys.exit(main())
