#!/usr/bin/env python3
"""E224 ARM B (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum): THE DRY AUDIT (E216's desk/dryaudit_e216.py form, E209's). The lesson (round log
sections 104 and 116): a dry pass never runs the branches its flag skips, so every line of the session's code that reads the dry flag - E208's
runner run_mms.py (unchanged, imported) AND E224's src/run_e224b.py - is listed here with the REAL path there and the real-path desk cases that ran
that real path; each case must read PASS in the kit's committed real-path log. Standard library only; reads only.

    /usr/bin/python3 -I -B tools/claims-v3/e224/desk/dryaudit_e224b.py [<the real-path log>]     (default: logs/realpath-e224b.txt)

It finds every line of tools/claims-v3/e208/proposal/src/run_mms.py (at its registered sha256 in E208's src/ list) and of E224's box/run_e224b.py
that reads `self.dry`, `a.dry` or defines `--dry`, refuses if any such line is not in its table below (or a table line no longer reads the flag
there), and prints, per line: the function, the line, the real path, the cases and COVERED (every case named PASS in the log) or NOT COVERED.
E224's own runbook has no RB_DRY mode (each step is a local script: the dry listing prints it, it runs nothing); E224's box scripts
(start_e224b.sh, session_e224b.sh) take no dry flag (dry_e224b.sh is the dry pass itself) and their one desk switch, E224B_DESKTEST, is audited at
the end the same way. Prints DRY-AUDIT-E224B <n> of <m> COVERED last (exit 0 only when every line is).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
RUNNER = os.path.join(REPO, "tools", "claims-v3", "e208", "proposal", "src", "run_mms.py")
START = os.path.join(E, "box", "start_e224b.sh")
RUNNER216 = os.path.join(E, "box", "run_e224b.py")
FLAG = re.compile(r"\bself\.dry\b|\ba\.dry\b|\"--dry\"")
# line -> (a snippet the line holds, the real path there, the real-path cases that ran it)
TABLE = {
    153: ("self.dry = a.dry", "the flag itself (no branch): false on the real path", ["MAIN"]),
    154: ("self.scale = a.scale if a.dry else 1.0", "the real pace, scale 1: every wait, rest and bound at its registered length "
          "(the 60 s opening rest, 10 s at rest, the 6 s burst, the die gate's waits)", ["MAIN", "STEP"]),
    167: ("self.kit_stop =", "the box root's run/KITSTOP (the kit's own stop word, read before the card's lock: a present one opens no device; "
          "start_e224b.sh never makes it)", ["MAIN"]),
    195: ("self.dev_dir =", "the card's real node folder (mms_ident.DEV_DIR): the identity read of the sampler's and every host's open nodes "
          "reads /dev/et0_ops and /dev/et0_mgmt there", ["MAIN", "HOLDER", "WRONGCFG"]),
    196: ("if self.dry:", "no doubles' environment and no device-call log: E208's guard (guard_ettelem.sh) over the reader, the built host, "
          "the real nodes; ET_DEVICES and V3_DEVICE unset on aifoundry2", ["MAIN", "BOARD", "DIE", "RUNTIME", "HANG", "QUIET", "TWOFAIL"]),
    230: ("'DRY ' if self.dry", "no DRY mark on any log line (the rest rule, the checker and the collection read the session as a card session)",
          ["MAIN"]),
    237: ("if not self.dry:", "device_call returns the REAL command: the config read and the sampler through the guard, each host under the "
          "plain `timeout 10` (never -k)", ["MAIN", "RUNTIME", "HANG", "WRONGCFG", "TWOFAIL"]),
    261: ("if self.dry:", "et-who under `timeout 20` (PATH's et-who), read before the session, at the identity read and before every run",
          ["MAIN", "HOLDER", "BUSYLOCK"]),
    319: ("if self.dry:", "the real ps read: a CI job, another device process of ours, another user's device process on aifoundry2", ["MAIN", "HANG"]),
    350: ("me = pwd.getpwuid", "the holder rule's own login from the password database (not $USER)", ["MAIN", "HOLDER"]),
    444: ("w = w * self.scale if self.dry else w", "the sampler's SIGTERM waits at their real lengths (a deaf sampler is never joined by a "
          "second one)", ["MAIN", "QUIET"]),
    446: ("w = min(w, max(2.0 * (self.scale if self.dry else 1.0)", "the same waits against the session's deadline at the real pace", ["MAIN", "QUIET"]),
    466: ("limit = C.SAMPLE_FRESH_S if not self.dry", "the sampler is live only with a sample under 2 s old (else stopped by SIGTERM and "
          "started again)", ["QUIET"]),
    503: ("if not self.dry:", "ours_alive: the real ps read of our device processes (the LEFTOVER's wait holds the card's lock until none is left)",
          ["HANG"]),
    634: ("me = pwd.getpwuid", "the identity read's own login from the password database", ["MAIN", "HOLDER"]),
    901: ('return os.path.join(self.dev_dir, "card.lock") if self.dry', "the card's real lock /run/lock/etsoc-shire0.lock",
          ["MAIN", "BUSYLOCK", "NOLOCK"]),
    905: ("if not self.dry:", "the lock must exist, be no link and be root's: else no device opened", ["MAIN", "NOLOCK", "R-REAL"]),
    933: ("' DRY scale '", "the session start line carries no DRY tag", ["MAIN"]),
    935: ('"dry": self.dry', "queue.json says dry false (the rest rule counts the session when it reached the card; the checker reads it)",
          ["MAIN", "R-REAL"]),
    940: ("if not self.dry:", "the box root's run/ folder", ["MAIN"]),
    942: ("boxp = os.path.join(self.out, \"box.lock\") if self.dry", "the box root's run/box.lock", ["MAIN"]),
    943: ("take_box_lock(boxp, None if self.dry", "the lock start_e224b.sh took (fd 9, MMS_BOX_LOCK_FD): held from the start's checks to the "
          "session's end", ["MAIN"]),
    948: ("if not self.dry:", "THE BOX CHECK: aifoundry2, today's build record, the kernel ELF at E136's pin, the host and the reader at the "
          "record's sha256, the harness, the device-command audit GO (its refusal side is not run by a case: the build desk test and step 2 "
          "check the same pins)", ["MAIN", "STEP"]),
    1030: ("if self.dry and a.stop_after", "--dry only: on the real path the operator's stop comes from stop_mms.sh touching run/STOP",
           ["MAIN", "STEP", "RUNTIME", "QUIET"]),
    1075: ("bound = C.LEFTOVER_WAIT_S", "the LEFTOVER's wait at its registered bound (10 minutes), never a kill", ["HANG"]),
    1104: ("if self.dry:", "no device-call log to close", ["MAIN"]),
    1139: ('parser.add_argument("--dry"', "the flag's definition (no branch)", ["MAIN"]),
    1155: ("if not a.dry and (", "the desk's overrides (--scale, --trip-arm, --stop-after and the rest) refused without --dry: the real session "
           "takes none (session_e224b.sh passes none; run_e224b.py passes its own arguments on)", ["MAIN"]),
}
# E224's own lines reading the dry flag (box/run_e224b.py)
TABLE224 = {
    146: ("if self.dry:", "no G knobs in the environment: rgm211's host's real stand-in at build/e224brgm211/host/sparsity_host, gated per "
          "process; a G failure is the host's own record (the walk check, the check of C, rc), never a knob", ["MAIN", "GWALK", "GHANG", "GTRIP"]),
    170: ("if self.dry and real and real[0] == \"timeout\"", "device_call returns rgm211's REAL host command under its sized plain timeout "
          "(`timeout 10`; never -k), its argv E208's but argv[0]", ["MAIN", "GWALK", "GHANG", "GTRIP"]),
    280: ('parser.add_argument("--dry"', "the flag's definition (no branch)", ["MAIN"]),
    304: ("if not a.dry and desk:", "the desk's overrides (E208's and E224's --g-* flags) refused without --dry: the real session takes none",
          ["MAIN"]),
}
# E224's own desk switch on the real path: start_e224b.sh's E224B_DESKTEST (a desk test's reboot-gate record is taken only with it)
DESK = [("E224B_DESKTEST", "a reboot-gate record that is a desk test's refused without E224B_DESKTEST=1; a real record (desk_test false) taken "
         "without it, the session unmarked", ["R-NODESK", "R-REAL"])]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main(argv):
    log = argv[0] if argv else os.path.join(E, "logs", "realpath-e224b.txt")
    sums = os.path.join(REPO, "tools", "claims-v3", "e208", "proposal", "src", "SRC-SHA256SUMS")
    want = {ln.split("  ", 1)[1].strip(): ln.split("  ", 1)[0] for ln in open(sums) if "  " in ln}
    print(f"dryaudit_e224b (/usr/bin/python3 {sys.version.split()[0]}): every line of E208's run_mms.py that reads the dry flag, the real path "
          f"there, and the real-path cases that ran it (each must read PASS in {os.path.relpath(log, REPO)})")
    if sha(RUNNER) != want.get("src/run_mms.py"):
        print(f"REFUSED: run_mms.py is not at E208's registered sha256 ({sha(RUNNER)[:16]})")
        return 2
    passed = set()
    for ln in open(log):
        m = re.match(r"^(PASS|FAIL) (\S+) \(", ln)
        if m and m.group(1) == "PASS":
            passed.add(m.group(2))
    lines = open(RUNNER).read().splitlines()
    found = [i for i, t in enumerate(lines, 1) if FLAG.search(t) and not t.strip().startswith("#")]
    extra = [i for i in found if i not in TABLE]
    gone = [i for i, (snip, _, _) in TABLE.items() if i > len(lines) or snip not in lines[i - 1] or i not in found]
    if extra or gone:
        print(f"REFUSED: lines reading the dry flag not in the table {extra}; table lines that no longer hold it {gone}")
        return 2
    fn, n_ok, n = "?", 0, 0
    fns = {}
    for i, t in enumerate(lines, 1):
        m = re.match(r"\s*def (\w+)", t)
        if m:
            fn = m.group(1)
        fns[i] = fn
    for i in sorted(TABLE):
        snip, real, cases = TABLE[i]
        ok = all(c in passed for c in cases)
        n += 1
        n_ok += ok
        print(f"  line {i:4d} [{fns[i]}] {lines[i - 1].strip()[:110]}")
        print(f"      real path: {real}; cases {', '.join('rp:' + c for c in cases)}: {'COVERED' if ok else 'NOT COVERED'}"
              + ("" if ok else f" (not PASS: {[c for c in cases if c not in passed]})"))
    l216 = open(RUNNER216).read().splitlines()
    f216 = [i for i, t in enumerate(l216, 1) if FLAG.search(t) and not t.strip().startswith("#")]
    extra2 = [i for i in f216 if i not in TABLE224]
    gone2 = [i for i, (snip, _, _) in TABLE224.items() if i > len(l216) or snip not in l216[i - 1] or i not in f216]
    if extra2 or gone2:
        print(f"REFUSED: run_e224b.py lines reading the dry flag not in its table {extra2}; table lines that no longer hold it {gone2}")
        return 2
    fn = "?"
    fns2 = {}
    for i, t in enumerate(l216, 1):
        m = re.match(r"\s*def (\w+)", t)
        if m:
            fn = m.group(1)
        fns2[i] = fn
    for i in sorted(TABLE224):
        snip, real, cases = TABLE224[i]
        ok = all(c in passed for c in cases)
        n += 1
        n_ok += ok
        print(f"  box/run_e224b.py line {i:4d} [{fns2[i]}] {l216[i - 1].strip()[:100]}")
        print(f"      real path: {real}; cases {', '.join('rp:' + c for c in cases)}: {'COVERED' if ok else 'NOT COVERED'}"
              + ("" if ok else f" (not PASS: {[c for c in cases if c not in passed]})"))
    st = open(START).read()
    for word, real, cases in DESK:
        ok = word in st and all(c in passed for c in cases)
        n += 1
        n_ok += ok
        print(f"  box/start_e224b.sh: {word}")
        print(f"      real path: {real}; cases {', '.join('rp:' + c for c in cases)}: {'COVERED' if ok else 'NOT COVERED'}")
    print(f"DRY-AUDIT-E224B {n_ok} of {n} {'COVERED' if n_ok == n else 'NOT ALL COVERED'}")
    return 0 if n_ok == n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
