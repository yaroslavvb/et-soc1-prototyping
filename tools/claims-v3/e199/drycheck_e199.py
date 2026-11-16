#!/usr/bin/env python3
"""E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum; E192's file, a6fe5c20, unchanged beside it, ported to aifoundry1 card 1): the dry pass's reading. It reads the output of E192's
reference session in its DRY mode (`DRY=1 bash run_session.sh OUT 9` with the heater named, as session_e199.sh --dry runs it, ET_DEVICES=1 exported: nothing
is opened, every device call is printed) and checks it against the registration, line by line:
  - 328 device calls: 327 host runs and 1 heater launch (the smoke's heater check) (E192.md section 16 item 7, proposal section 10; E199.md section 2);
  - every device call under `timeout 10` with `--stop-file`; every host run with `--window 240000000`; the smoke's runs `--seconds 2`,
    every pass's runs `--seconds 4`; the heater with the lab's E78 arguments exactly (E192.md section 4);
  - the smoke block runs nop, add.a.f2, add.cr.l31; each of passes 0-8 runs 36 host runs in exactly the order the registration writes
    out for a host named aifoundry1 (order-e199-aifoundry1.txt, E199's registered file: two burn-ins and the first anchor, the 32 arms, the last anchor);
  - 20 marked idles (10 s before and after each of the 10 blocks) and 8 lock releases with their 30 s gap and holder check.
    /usr/bin/python3 -I -B drycheck_e199.py <run_session.out> <order-e199-aifoundry1.txt>
Prints the findings and a last line "E199-DRY OK: ..." (exit 0) or "E199-DRY FAIL: ..." (exit 16). Opens no device.
SPDX-License-Identifier: Apache-2.0
"""
import re
import sys

HEATER_ARGS = ("--test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1")
SMOKE = ["nop", "add.a.f2", "add.cr.l31"]


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 10
    lines = open(argv[0], errors="replace").read().splitlines()
    order = {}
    for ln in open(argv[1]):
        m = re.match(r"pass (\d+)(?: \(the registered warm-up\))?: (.*)$", ln.strip())
        if m:
            order[int(m.group(1))] = [w.split(":")[-1] for w in m.group(2).split()]
    bad, blocks, cur = [], [], []
    host_n = heat_n = idle_n = gap_n = 0
    for ln in lines:
        if ln.startswith("DRY: timeout"):
            w = ln[len("DRY: "):].split()
            if w[:2] != ["timeout", "10"] or "--stop-file" not in w:
                bad.append("a device call without timeout 10 and --stop-file: " + ln[:160])
            if "--arm" in w:
                host_n += 1
                arm = w[w.index("--arm") + 1]
                secs = w[w.index("--seconds") + 1] if "--seconds" in w else "?"
                win = w[w.index("--window") + 1] if "--window" in w else "?"
                if win != "240000000":
                    bad.append("a host run with --window %s: %s" % (win, ln[:160]))
                cur.append((arm, secs))
            elif "--test" in w:
                heat_n += 1
                got = " ".join(w[3:w.index("--stop-file")])
                if got != HEATER_ARGS:
                    bad.append("the heater's arguments read '%s', not the registered '%s'" % (got, HEATER_ARGS))
            else:
                bad.append("an unknown device call: " + ln[:160])
        elif ln.startswith("DRY: idle "):
            idle_n += 1
        elif re.search(r"DRY: card lock released; gap 30 s; holder check; card lock taken", ln):
            gap_n += 1
        m = re.match(r"pass (-?\d+): (\d+) runs$", ln.strip())
        if m:
            blocks.append((int(m.group(1)), int(m.group(2)), cur))
            cur = []
    if host_n + heat_n != 328 or host_n != 327 or heat_n != 1:
        bad.append("%d device calls (%d host, %d heater), not 328 (327, 1)" % (host_n + heat_n, host_n, heat_n))
    if [b[0] for b in blocks] != list(range(-1, 9)):
        bad.append("blocks %s, not the smoke and passes 0-8" % [b[0] for b in blocks])
    for p, n, runs in blocks:
        arms = [a for a, _ in runs]
        secs = {s for _, s in runs}
        if p == -1:
            if arms != SMOKE or secs != {"2"}:
                bad.append("the smoke ran %s at --seconds %s, not %s at 2" % (arms, sorted(secs), SMOKE))
        else:
            if n != 36 or len(runs) != 36:
                bad.append("pass %d: %d runs (%d host calls), not 36" % (p, n, len(runs)))
            if secs != {"4"}:
                bad.append("pass %d: --seconds %s, not 4" % (p, sorted(secs)))
            if arms != order.get(p):
                first = next((i for i, (x, y) in enumerate(zip(arms, order.get(p, []))) if x != y), None)
                bad.append("pass %d: the order differs from the registered order for aifoundry1 (first at run %s)" % (p, first))
    if idle_n != 20:
        bad.append("%d marked idles, not 20" % idle_n)
    if gap_n != 8:
        bad.append("%d lock releases with their gap, not 8" % gap_n)
    for b in bad:
        print("FINDING: " + b)
    if bad:
        print("E199-DRY FAIL: %d finding(s); %d device calls (%d host, %d heater)" % (len(bad), host_n + heat_n, host_n, heat_n))
        return 16
    print("E199-DRY OK: 328 device calls (327 host, 1 heater), every one under timeout 10 with --stop-file; the smoke 3 runs at 2 s; "
          "passes 0-8 36 runs each at 4 s in the registered order for aifoundry1; 20 marked idles; 8 lock releases with the 30 s gap")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
