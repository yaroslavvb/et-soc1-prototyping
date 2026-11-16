#!/usr/bin/env python3
"""E194's check of the RUNBOOK's command lines (Q183, the kit, Sun 15 Nov 2026, after E194's registration and before any E194 datum):
E191's check (tools/claims-v3/e191/desk/drylisting_check_e191.py, unchanged beside it) for this box, on the runbook's side (the runner's
side is run_e194.py's own dry check, commands.jsonl, every dry session). It reads the runbook's dry listing (rb/list_steps_e194.sh's
output, which prints every remote script in full) and:
  1. finds every line that may open a device or a card lock on the box: E194's guard or the reader (ettelem_guard_e194.sh,
     build/ettelem-hpl/ettelem), a host (ledger_host, sparseparity_host), the session (session_e194.sh run by bash), a flock on /run/lock/;
  2. requires ET_DEVICES and V3_DEVICE UNSET for each: an `unset ET_DEVICES V3_DEVICE` earlier in the same remote script (or on the line),
     and no line of that script setting either;
  3. requires that no line of any remote script (the regular expressions that NAME device processes for counting, DEV_COMM and OTHER_COMM,
     k6's prelude's line that COUNTS card 1's holder lines, and the dry job's grep for the runner's dry-check words aside) names etsoc-shire1, /dev/et1_, an ET_DEVICES= or V3_DEVICE= setting,
     or runs dev_mngt_service or et-powertop;
  4. requires that every call the listing prints reaches aifoundry2 (this box) and no other box, and that the listing's last line reads
     "0 box calls beyond aifoundry2".
    /usr/bin/python3 -I -B tools/claims-v3/e194/desk/drylisting_check_e194.py <the dry listing>    (prints DRYLISTING-CHECK-E194 PASS or FAIL)
A desk check of code: nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import re
import sys

OPEN = re.compile(r"ettelem_guard_e194\.sh|build/ettelem-hpl/ettelem|ledger_host|sparseparity_host|bash tools/claims-v3/e194/session_e194\.sh|flock [^|]*/run/lock/")
FORBIDDEN = re.compile(r"etsoc-shire1|/dev/et1_|\bET_DEVICES=|\bV3_DEVICE=|\bdev_mngt_service\b|\bet-powertop\b")
COUNTING = re.compile(r"^(DEV_COMM|OTHER_COMM)=|\$1 ~ /\^\\/dev\\/et1_/ \|\| \$1 == \"lock:etsoc-shire1\.lock\"|^# |"
                      r"grep -c 'the device-command check: ")      # the dry job's grep for the runner's own dry-check line (a pattern)
UNSET = re.compile(r"\bunset\b[^#\n]*\bET_DEVICES\b[^#\n]*\bV3_DEVICE\b|\bunset\b[^#\n]*\bV3_DEVICE\b[^#\n]*\bET_DEVICES\b")


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
        unset = False
        for ln in lines:
            s = ln.strip()
            if UNSET.search(s):
                unset = True
            if FORBIDDEN.search(s) and not COUNTING.search(s):
                bad.append(f"forbidden: '{s[:110]}'")
            if s.startswith("#") or not OPEN.search(s) or "pgrep" in s or "ours_live" in s or s.startswith("echo ") or "grep " in s.split("|")[0]:
                continue
            opening.append((head[:60], s[:150], unset))
            if not unset:
                bad.append(f"ET_DEVICES and V3_DEVICE not unset before: '{s[:110]}'")
    targets = re.findall(r"^--- [a-z]+ on ([a-z0-9.-]+) \(|^--- probe ([a-z0-9.-]+),", text, re.M)
    boxes = sorted({a or b for a, b in targets})
    if boxes != ["aifoundry2"]:
        bad.append(f"the listing's calls reach {boxes}, not aifoundry2 alone")
    if re.search(r"\b(aifoundry1|aifoundry3):(nekko|aifoundry|claude)/", text):
        bad.append("a copy names another box's tree")
    last = [ln for ln in text.splitlines() if ln.startswith("dry listing: ") and "steps listed" in ln]
    if not last or not last[-1].endswith(", 0 box calls beyond aifoundry2"):
        bad.append(f"the listing's last line: {last[-1] if last else 'missing'}")
    print(f"drylisting_check_e194 ({sys.executable} {sys.version.split()[0]}): {len(bl)} remote scripts read in the dry listing; the calls "
          f"it prints reach {boxes}")
    for head, s, ok in opening:
        print(f"  device-opening line: {s}  -> ET_DEVICES and V3_DEVICE unset before it {'yes' if ok else 'NO'}")
    for b in bad:
        print(f"  {b}")
    good = not bad and len(opening) >= 2
    print(f"DRYLISTING-CHECK-E194 PASS: {len(opening)} device-opening line(s), each after an unset of ET_DEVICES and V3_DEVICE; no line names "
          f"another card or an ET_DEVICES setting, or runs dev_mngt_service or et-powertop; every call to aifoundry2 alone" if good else
          f"DRYLISTING-CHECK-E194 FAIL: {len(bad)} finding(s), {len(opening)} device-opening line(s)")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
