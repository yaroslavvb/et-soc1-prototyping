#!/usr/bin/env python3
"""E191's check of the RUNBOOK's command lines (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191
datum): E191's dated note 1, item 4, on the runbook's side ("the desk dry pass asserts these, over every device-opening command in the
runner's and the runbook's command lines"). The runner's side is run_e191.py's own dry check (commands.jsonl, every dry session). This
reads the runbook's dry listing (rb/list_steps_e191.sh's output, which prints every remote script in full) and:
  1. finds every line that may open a device or a card lock on the box: E191's guard or the reader (ettelem_guard_e191.sh,
     build/ettelem/ettelem), a host (ledger_host, sparseparity_host), the session (session_e191.sh run by bash), a flock on /run/lock/;
  2. requires ET_DEVICES=1 for each: on the line itself or by an `export ET_DEVICES=1` earlier in the same remote script;
  3. requires that no line of any remote script (the regular expressions that NAME device processes for counting, DEV_COMM and OTHER_COMM,
     the look's awk patterns that COUNT card 0's holder lines, and the dry job's grep for the runner's dry-check line aside) names etsoc-shire0, /dev/et0_, ET_DEVICES=0, unsets ET_DEVICES, or
     runs dev_mngt_service or et-powertop.
    /usr/bin/python3 -I -B tools/claims-v3/e191/desk/drylisting_check_e191.py <the dry listing>    (prints DRYLISTING-CHECK-E191 PASS or FAIL)
A desk check of code: nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import re
import sys

OPEN = re.compile(r"ettelem_guard_e191\.sh|build/ettelem/ettelem|ledger_host|sparseparity_host|bash tools/claims-v3/e191/session_e191\.sh|flock [^|]*/run/lock/")
FORBIDDEN = re.compile(r"etsoc-shire0|/dev/et0_|ET_DEVICES=0|unset[^#\n]*ET_DEVICES|\bdev_mngt_service\b|\bet-powertop\b")
COUNTING = re.compile(r"^(DEV_COMM|OTHER_COMM)=|\$1 ~ /\^\\/dev\\/et0_/|\$1 == \"lock:etsoc-shire0\.lock\"|card 0 must show none|"
                      r"grep -c 'the device-command check: ")      # the dry job's grep for the runner's own dry-check line (a pattern)


def blocks(text):
    """The remote scripts the listing prints: lists of their lines (the '    | ' prefix taken off), each with the header it follows."""
    out, cur, head = [], None, ""
    for ln in text.splitlines():
        if ln.startswith("    | "):
            if cur is None:
                cur = []
                out.append((head, cur))
            cur.append(ln[6:])
        else:
            cur = None
            if ln.startswith("--- ") or ln.startswith("---- "):
                head = ln
    return out


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    text = open(argv[0]).read()
    bl = blocks(text)
    opening, bad = [], []
    for head, lines in bl:
        exported = False
        for ln in lines:
            s = ln.strip()
            if re.search(r"^export [^#]*\bET_DEVICES=1\b", s):
                exported = True
            if FORBIDDEN.search(s) and not COUNTING.search(s):
                bad.append(f"forbidden: '{s[:110]}'")
            if s.startswith("#") or not OPEN.search(s) or "pgrep" in s or "ours_live" in s or s.startswith("echo ") or "grep " in s.split("|")[0]:
                continue
            inline = re.search(r"\bET_DEVICES=1\b", s) is not None
            opening.append((head[:60], s[:150], inline or exported))
            if not (inline or exported):
                bad.append(f"no ET_DEVICES=1: '{s[:110]}'")
    print(f"drylisting_check_e191 ({sys.executable} {sys.version.split()[0]}): {len(bl)} remote scripts read in the dry listing")
    for head, s, ok in opening:
        print(f"  device-opening line: {s}  -> ET_DEVICES=1 {'yes' if ok else 'NO'}")
    for b in bad:
        print(f"  {b}")
    good = not bad and len(opening) >= 2
    print(f"DRYLISTING-CHECK-E191 {'PASS' if good else 'FAIL'}: {len(opening)} device-opening line(s), each with ET_DEVICES=1; no line names card 0, "
          f"unsets ET_DEVICES or runs dev_mngt_service or et-powertop" if good else
          f"DRYLISTING-CHECK-E191 FAIL: {len(bad)} finding(s), {len(opening)} device-opening line(s)")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
