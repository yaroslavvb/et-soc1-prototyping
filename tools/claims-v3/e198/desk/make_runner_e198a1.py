#!/usr/bin/env python3
"""E198 dated amendment A1 (Q196, lane a1-e198, Mon 16 Nov 2026, before any E198 datum): THE LAB'S RUNNER COPY, made from E193's runner as
committed (tools/claims-v3/e193/proposal/src/run_x04.py, sha256 26d08862..., which stays byte for byte as it is) by the exact hunks below
and nothing else, then checked: each hunk's old text stands exactly once in E193's runner, every changed line belongs to a hunk, and every
other line is the same bytes. The hunks are the kill path only (E198.md.dated-amendment-A1.md section 2):
  K1-K3  the doc lines that describe the kill (the run's `timeout -k 1 10`, the stop list, the clean-up's "kills the program 1 s later");
  K4     a constant: END_WAIT_S = 25 (10 s to its timeout's TERM, then the 15 s end_device() first waits);
  K5     each device process under a plain `timeout 10` (TERM at 10 s, never a KILL);
  K6     the device process waited for at most END_WAIT_S: one still running is reported at once ("device process not ended: tell the lab
         admin"), recorded as "device_not_ended", and LEFT RUNNING (kids["device"] keeps it, so the clean-up waits for it again);
  K7     end_device()'s doc: SIGTERM to its timeout and a wait, never a KILL; a process that does not end is reported and left;
  K8     the caller: a device process not ended is the registered stop "tell the lab admin" (stop(): STOPPED, the stop file); the session
         stops launching;
  K9     the clean-up after a device process not ended (E193's code returned before the lock and the sampler): the lock stays until the
         runner exits, as before, and the sampler is now stopped all the same, by E193's own SIGTERM and 10 s wait, so it does not hold
         the card's management node until its own --seconds end. Under E193's `-k 1` the KILL at 11 s ended such a process, end_device()
         returned True and the clean-up stopped the sampler; K9 keeps that sampler stop on the path the KILL used to take.
Dated fix (Q196, lane fix-a1e198, Mon 16 Nov 2026, before the land and before any E198 datum), answering verify-a1e198: K9 is new (its
finding 1); K3 now also covers its next line (the sampler stop) and K3 and K7 say what GNU timeout does with a TERM sent to it after it
has passed one on or sent its own (it ignores it: coreutils 9.4 read on aifoundry2; its finding 2).
    /usr/bin/python3 -I -B tools/claims-v3/e198/desk/make_runner_e198a1.py --check     (from the top: re-make in memory, compare)
    /usr/bin/python3 -I -B tools/claims-v3/e198/desk/make_runner_e198a1.py --write     (write run_x04_e198a1.py and its diff)
Prints RUNNER-A1 CHECK PASS (or FAIL) with the counts. Exit 0 / 3, 2 usage. SPDX-License-Identifier: Apache-2.0
"""
import difflib
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
SRC_REL = "tools/claims-v3/e193/proposal/src/run_x04.py"
OUT_REL = "tools/claims-v3/e198/run_x04_e198a1.py"
DIFF_REL = "tools/claims-v3/e198/run_x04_e198a1.diff"
SRC_SHA = "26d0886225618288745d541960fcaacc847341ab8e27ee2d277820ae4115bc51"

HUNKS = [
    ("K1", "`timeout -k 1 10` after `--gap` seconds of idle: `--burst` seconds of 0.4 s launches, or, for a train (block T),\n",
     "`timeout 10` after `--gap` seconds of idle (E198 A1: TERM at 10 s, never a KILL): `--burst` seconds of 0.4 s\n"
     "launches, or, for a train (block T),\n"),
    ("K2", "    a launch that did not finish is also a call for the lab admin (a hung hart needs a card reset);\n",
     "    a launch that did not finish is also a call for the lab admin (a hung hart needs a card reset); E198 A1: a device process\n"
     "    still running END_WAIT_S after it started (its timeout's TERM came at 10 s) is the same stop: reported at once, never killed,\n"
     "    left running for the lab admin;\n"),
    ("K3", "its `timeout`, which passes it on and kills the program 1 s later, and the runner waits for it (15 s, then once more\n"
           "60 s) before it releases the card lock; then the sampler is stopped with SIGTERM and waited for. Children are started\n",
     "its `timeout`, which passes it on unless it has already passed on or sent a TERM (GNU timeout; E198 A1: no KILL follows),\n"
     "and the runner waits for it (15 s, then once more 60 s) before it releases the card lock; then the sampler is stopped\n"
     "with SIGTERM and waited for (E198 A1: also when the device process did not end, whose card lock then goes when this\n"
     "runner exits). Children are started\n"),
    ("K4", "FREE_WAIT_S, FREE_POLL_S = 600, 30\n",
     "FREE_WAIT_S, FREE_POLL_S = 600, 30\n"
     "END_WAIT_S = 25       # E198 A1: a device process still running this long after it started (TERM at 10 s) is reported, never killed\n"),
    ("K5", '        cmd = ["timeout", "-k", "1", "10", a.host, "--window", "240000000", "--seconds", str(seconds),\n',
     '        cmd = ["timeout", "10", a.host, "--window", "240000000", "--seconds", str(seconds),\n'),
    ("K6", "        rc = p.wait()\n        kids[\"device\"] = None\n",
     "        try:                                    # E198 A1: no KILL follows its timeout's TERM at 10 s\n"
     "            rc = p.wait(timeout=END_WAIT_S)\n"
     "        except subprocess.TimeoutExpired:       # still running: reported at once and left running for the lab admin\n"
     "            say(\"device process still running %d s after it started (its timeout's TERM came at 10 s; nothing is killed): \"\n"
     "                \"device process not ended: tell the lab admin\" % END_WAIT_S)\n"
     "            event(\"device_not_ended\", arm=x[\"arm\"], seconds=END_WAIT_S)\n"
     "            return None, \"\"\n"
     "        kids[\"device\"] = None\n"),
    ("K7", '        """End a device process still running (the runner was stopped by a signal): SIGTERM to its `timeout`, which\n'
           '        passes it on and kills the program 1 s later; wait for it. True when no device process is left."""\n',
     '        """End a device process still running (the runner was stopped by a signal, or the process outlived its timeout\'s\n'
     '        TERM): SIGTERM to its `timeout` and wait for it (E198 A1: never a KILL). GNU timeout passes on only the first\n'
     '        TERM sent to it, and none once it has sent its own at 10 s, so a process that outlived that TERM gets nothing\n'
     '        more from here. True when no device process is left; False when one is still there: reported, and left for the\n'
     '        lab admin."""\n'),
    ("K8", "                        rc, out = device(x, a.burst)\n                        recs = []\n",
     "                        rc, out = device(x, a.burst)\n"
     "                        if rc is None:                  # E198 A1: the device process did not end after its timeout's TERM\n"
     "                            return stop(f\"{x['arm']}: device process not ended {END_WAIT_S} s after it started, its timeout's \"\n"
     "                                        \"TERM at 10 s (nothing killed: tell the lab admin)\")\n"
     "                        recs = []\n"),
    ("K9", "    def cleanup():\n"
           "        \"\"\"Idempotent. A running device process first (ended and waited for), then the lock, then the sampler.\"\"\"\n"
           "        if not end_device():\n"
           "            say(\"device process not ended: the card lock goes only when this runner exits\")\n"
           "            return\n"
           "        release_card()\n",
     "    def cleanup():\n"
     "        \"\"\"Idempotent. A running device process first (ended and waited for), then the lock, then the sampler (E198 A1:\n"
     "        a device process not ended keeps the lock until this runner exits, and the sampler is stopped all the same).\"\"\"\n"
     "        if not end_device():\n"
     "            say(\"device process not ended: the card lock goes only when this runner exits\")\n"
     "            say(\"E198 A1: the sampler is stopped all the same (SIGTERM), so it does not hold the management node\")\n"
     "        else:\n"
     "            release_card()\n"),
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def make():
    with open(os.path.join(REPO, SRC_REL), "rb") as f:
        raw = f.read()
    bad = []
    if sha(raw) != SRC_SHA:
        bad.append(f"E193's runner reads {sha(raw)[:16]}, not its registered {SRC_SHA[:16]}")
    text = raw.decode()
    for name, old, new in HUNKS:
        n = text.count(old)
        if n != 1:
            bad.append(f"{name}: its old text stands {n} times in E193's runner, not once")
            continue
        text = text.replace(old, new)
    return raw.decode(), text, bad


def check_lines(old, new):
    """Every changed line belongs to a hunk: the diff's removed lines are exactly the hunks' old lines, its added lines the hunks' new."""
    sm = difflib.SequenceMatcher(a=old.splitlines(True), b=new.splitlines(True), autojunk=False)
    rem, add = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            rem += old.splitlines(True)[i1:i2]
            add += new.splitlines(True)[j1:j2]
    want_rem = [ln for _, o, _ in HUNKS for ln in o.splitlines(True)]
    want_add = [ln for _, _, n in HUNKS for ln in n.splitlines(True)]
    # a hunk's unchanged context line (K4's, K6's and K8's first or last line) is equal on both sides and drops out of the diff
    ctx = [ln for _, o, n in HUNKS for ln in o.splitlines(True) if ln in n.splitlines(True)]
    for ln in ctx:
        if ln in want_rem:
            want_rem.remove(ln)
        if ln in want_add:
            want_add.remove(ln)
    return sorted(rem) == sorted(want_rem) and sorted(add) == sorted(want_add), len(rem), len(add)


def udiff(old, new):
    return "".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile="a/" + SRC_REL, tofile="b/" + OUT_REL))


def main(argv):
    if argv not in (["--check"], ["--write"]):
        print(__doc__)
        return 2
    old, new, bad = make()
    same_rest, nrem, nadd = check_lines(old, new)
    if not same_rest:
        bad.append("a changed line outside the hunks")
    d = udiff(old, new)
    if argv == ["--write"] and not bad:
        with open(os.path.join(REPO, OUT_REL), "w") as f:
            f.write(new)
        with open(os.path.join(REPO, DIFF_REL), "w") as f:
            f.write(d)
    have = open(os.path.join(REPO, OUT_REL)).read() if os.path.exists(os.path.join(REPO, OUT_REL)) else ""
    hd = open(os.path.join(REPO, DIFF_REL)).read() if os.path.exists(os.path.join(REPO, DIFF_REL)) else ""
    if have != new:
        bad.append(f"{OUT_REL} is not the re-made copy")
    if hd != d:
        bad.append(f"{DIFF_REL} is not the re-made diff")
    banned = [ln for ln in new.splitlines() if "timeout\", \"-k" in ln or "-k 1" in ln or "SIGKILL" in ln or ".kill(" in ln]
    if banned:
        bad.append(f"a kill word left in the copy: {banned[:2]}")
    print(f"E193's runner {SRC_SHA[:16]}... ({len(old.splitlines())} lines); the lab's copy {sha(new.encode())} ({len(new.splitlines())} lines); "
          f"{len(HUNKS)} hunks ({', '.join(h[0] for h in HUNKS)}), each applied once; the diff: {nrem} line(s) removed, {nadd} added, "
          f"every one inside a hunk; diff sha256 {sha(d.encode())}")
    if bad:
        print("RUNNER-A1 CHECK FAIL: " + "; ".join(bad))
        return 3
    print("RUNNER-A1 CHECK PASS: the copy is E193's runner with the kill path changed and nothing else; no 'timeout -k', SIGKILL or .kill( in it")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
