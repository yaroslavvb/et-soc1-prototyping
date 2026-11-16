#!/usr/bin/env python3
"""E195's kit (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): THE AUDIT TABLE of every line of the session's chain that
reads a dry flag (desk/dry-branches-e195.tsv; Q191, lane fix-e195: the closing read's row, verify-e195's finding 1), made from the
files' own lines: each such line, its number, its text, what the dry path does
there, what the real path does, and the real-path desk test's cases that ran its real branch. A line that reads a dry flag and has no
reading below fails (exit 3): a new dry branch is NOT COVERED until it is read and mapped here.

    python3 -I -B drybranches_e195.py [--write]      (from anywhere; prints the rows; --write writes desk/dry-branches-e195.tsv)
SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
FILES = [("tools/claims-v3/e195/session_e195.sh", r"DRYF"), ("tools/claims-v3/e195/block_e195.sh", r"V3_DRY"),
         ("tools/claims-v3/e195/lib_e195.sh", r"V3_DRY"), ("tools/claims-v3/lib.sh", r"V3_DRY"),
         ("tools/claims-v3/e195/proposal/src/lib_x09.sh", r"V3_DRY"), ("tools/claims-v3/e195/runitems_e195.py", r"a\.dry|V3_DRY")]
# (file, the stripped line's start) -> (under the dry path, on the real path, the cases that ran the real branch)
READ = {
    ("session_e195.sh", "DRYF="): ("DRYF set by --dry", "DRYF empty: the real path", "P,F,Y1"),
    ("session_e195.sh", 'case "${1:-}" in "") ;; --dry) DRYF=1'): ("--dry: DRYF=1", "no argument: the real path", "P,Y1"),
    ("session_e195.sh", "SD=build/e195/T$T0; [ -n \"$DRYF\" ]"): ("the session's files in T<T0>-dry", "T<T0>", "P,Y1"),
    ("session_e195.sh", "say() {"): ("every log line 'DRY ...' (every rest rule skips it)", "plain lines", "P,Y1"),
    ("session_e195.sh", "DATA=$RR/build/claims-v3/$CARD/$EXPN;"): ("the data folder under build/claims-v3-dry", "build/claims-v3/aifoundry3/x09-T<T0>", "P,Y1"),
    ("session_e195.sh", 'if [ -n "$DRYF" ]; then say "timeout 20 et-who --check'): ("the closing holder check and config read printed only", "et-who --check first (the registered cfg()): no read while it does not read the card free; else the closing read through the guard under the lock; skipped beside a stuck sampler", "P,K1,L2,H2,H3,H4"),
    ("session_e195.sh", 'if [ -n "$DRYF" ]; then#block'): ("each block in the foreground with V3_DRY=1", "each block in the background, waited by bg_wait (a signal interrupts the wait; the block is waited again)", "P,SG,BS"),
    ("session_e195.sh", 'say "session start'): ("'; DRY' on the start line", "the start line", "P,Y1"),
    ("session_e195.sh", 'if [ -n "$DRYF" ]; then#first'): ("the holder check, the node count and the start config read printed only", "the holder check (the first card command), the one ops node, the lock file, the start config read and its gate", "P,H1,N2,N0,L1,C1"),
    ("session_e195.sh", 'if [ -z "$DRYF" ]; then'): ("no watcher", "the watcher started; no block unless it runs", "P,DW"),
    ("session_e195.sh", "watching() {"): ("watching() true", "kill -0 on the watcher", "P,DW"),
    ("session_e195.sh", 'if [ -n "$DRYF" ]; then#smoke'): ("the smoke gates not run", "the registered smoke gate and the kit's 65 W / 65 C gate", "P,G65,GP,G2"),
    ("session_e195.sh", '[ -n "$DRYF" ] && {'): ("the dry listing checked (check_e195.py dry)", "skipped", "P,Y1"),
    ("block_e195.sh", '[ -n "${V3_DRY:-}" ] || [ -e "$LK" ]'): ("no lock file needed", "the card lock file must exist (the session reads it first)", "P"),
    ("lib_e195.sh", 'if [ -n "${V3_DRY:-}" ]; then return 0; fi'): ("x9k_wait_ours returns at once", "waits, holding the lock, while a device process of ours runs (30 s bound, no signal)", "BS,P"),
    ("lib_e195.sh", 'if [ -z "${V3_DRY:-}" ]; then'): ("lib.sh's dry stubs stay", "stop_sampler (no SIGKILL), start_sampler (no forwarding, no second sampler), die_c (none beside a stuck sampler)", "P,K1"),
    ("lib.sh", 'if [ -e "$lk" ] && [ -z "${V3_DRY:-}" ]; then'): ("no card lock taken", "block_begin takes the card lock (flock -n fd 9) or exits 3", "P,L2"),
    ("lib.sh", 'if [ -n "${V3_DRY:-}" ]; then'): ("the dry stubs (hold10, die_c, heat_to, drain_mgmt, start/stop_sampler, others_present, ours_running)", "the real functions (die_c; others_present and the sampler as lib_x09.sh and lib_e195.sh replace them)", "P,K1,H3"),
    ("lib_x09.sh", 'if [ -z "${V3_DRY:-}" ]; then'): ("lib.sh's dry others_present (nobody)", "the kits' other-user test: another user's device process or holder of this card's nodes or lock", "P,H3"),
    ("runitems_e195.py", 'ap.add_argument("--dry"'): ("--dry from V3_DRY", "the real path", "P,Y1"),
    ("runitems_e195.py", "if a.dry:#dev"): ("dev() prints the command", "timeout 10 + the command, its stdout read whole", "P,SP,S2,SL,X1"),
    ("runitems_e195.py", "if a.dry:#reading"): ("reading() returns the target", "the live telemetry: stale, no line, hot", "P,D1,T1"),
    ("runitems_e195.py", "if a.dry:#approach"): ("approach() a fixed record", "heats to 59 C, waits for 58 C", "P"),
    ("runitems_e195.py", "if a.dry:#others"): ("check_others() nothing", "et-holders (another user) and the pass's STOP before every item", "P,H2,B1,SG"),
    ("runitems_e195.py", '+ ("" if n or a.dry else'): ("the dry line", "the run's line; rc and stderr when no record", "P,NR"),
    ("runitems_e195.py", "if n or a.dry:"): ("one call", "a retry when no launch record", "P,NR"),
    ("runitems_e195.py", "time.sleep(0 if a.dry else 3)"): ("no final sleep", "3 s", "P"),
}
# lines whose text repeats in one file: told apart by the function they sit in
CONTEXT = {("session_e195.sh", 'if [ -n "$DRYF" ]; then'): [("block() {", "#block"), ("if [ -n \"$DRYF\" ]; then\n  FIRST", "#first"),
                                                            ("CUR=$SMOKE", "#smoke")],
           ("runitems_e195.py", "if a.dry:"): [("def dev(", "#dev"), ("def reading(", "#reading"), ("def approach(", "#approach"),
                                                ("def check_others(", "#others")]}


def key_of(fn, lines, i, s):
    b = os.path.basename(fn)
    for (cf, start), tags in CONTEXT.items():
        if b == cf and s == start:
            best = None
            for marker, tag in tags:
                first = marker.split("\n")[0]
                for j in range(i - 1, -1, -1):
                    if lines[j].strip().startswith(first.strip()):
                        if best is None or j > best[0]:
                            best = (j, tag)
                        break
            if b == "session_e195.sh" and lines[i + 1].strip().startswith("FIRST"):
                return (b, start + "#first")
            if best:
                return (b, start + best[1])
    for (rb, start), v in READ.items():
        if rb == b and "#" not in start and s.startswith(start):
            return (rb, start)
    return None


def rows():
    out, missing = [], []
    for fn, pat in FILES:
        lines = open(os.path.join(REPO, fn)).read().split("\n")
        for i, ln in enumerate(lines):
            if not re.search(pat, ln) or ln.lstrip().startswith("#"):
                continue
            s = ln.strip()
            k = key_of(fn, lines, i, s)
            if not k or k not in READ:
                missing.append(f"{fn}:{i + 1}: {s[:80]}")
                continue
            d, r, c = READ[k]
            out.append((fn, str(i + 1), s[:70], d, r, c))
    return out, missing


def main(argv):
    out, missing = rows()
    for r in out:
        print("\t".join(r))
    if missing:
        print("DRYBRANCHES-E195 NOT COVERED: " + "; ".join(missing))
        return 3
    if "--write" in argv:
        with open(os.path.join(HERE, "dry-branches-e195.tsv"), "w") as f:
            f.write("# E195's kit: THE AUDIT of every line of the session's chain that reads a dry flag (made by desk/drybranches_e195.py from the\n"
                    "# files' own lines; desk/desktest_realpath_e195.py reads the files against it: a line without a row, a row whose text differs or a\n"
                    "# named case that failed fails the audit).\n"
                    "# file\tline\ttext (prefix)\tunder the dry path\ton the real path\tcases that ran the real branch\n")
            for r in out:
                f.write("\t".join(r) + "\n")
    print(f"DRYBRANCHES-E195 OK: {len(out)} lines that read a dry flag, each read and mapped")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
