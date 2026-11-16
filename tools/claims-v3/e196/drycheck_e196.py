#!/usr/bin/env python3
"""E196's kit (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum): THE DRY LISTING'S READER. session_e196.sh --dry runs
the port's DRY mode twice (six passes, as the registration's dry check ran the reference: E196.md section 16 item 8): the full plan and
the cut order (DROP_ARMS=F.Ae,Z.b50,I.H.mFFFF). This program rebuilds, from the REGISTERED files alone, every device call each listing
must hold, in order, and compares them line for line:
  - the commands: desk/commands-e196.txt (registered), its GEN and OUT placeholders and its two binaries' names replaced by the
    listing's own (the first heater line names the lab's host, the first train line the request's host, the first --stop-file the OUT);
    a smoke run of the lab's host is its pass command at --seconds 2 (E196.md section 6: "2 s each, no preheat");
  - the order: desk/order-e196-aifoundry3.txt and desk/order-e196-aifoundry3-cut.txt (registered), passes 0-5;
  - the shape (E196.md sections 3 and 6): the smoke (the heater check; I.H.m00FF, I.R.m00FF, Z.a0, I.R.full on the lab's host; the same
    four on the request's host; T1's first two processes, SFFS then FSSF); T1 then T2, each K.pi (the lab's host), 24 processes
    alternating SFFS and FSSF (the request's host), K.pi; passes 0-5, each two burn-ins, K.pi, the 28 (25 cut) arms, K.pi, all on the
    lab's host; 255 device calls (237 cut): the registration's 251 (233) and the smoke's second set of four;
  - every call under `timeout 10`, its last two words `--stop-file <OUT>/STOP`; the approach printed before every measured run (196
    with the heater, 178 cut) and with no preheat before the smoke's eight runs.
    python3 -I -B drycheck_e196.py <full listing> <cut listing> <tools/claims-v3/e196/desk>
Prints E196-DRY OK: ... or E196-DRY FAIL: ... last; exit 0 or 16. SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import sys

SMOKE = ["I.H.m00FF", "I.R.m00FF", "Z.a0", "I.R.full"]


def commands(desk):
    pas, heater, trains, premise = {}, None, {}, {}
    sec = None
    for ln in open(os.path.join(desk, "commands-e196.txt")):
        ln = ln.rstrip("\n")
        if ln.startswith("#"):
            sec = ln
            continue
        if not ln.strip():
            continue
        if "the request's host (x14_host), the train processes" in (sec or ""):
            t, o, rest = ln.split(None, 2)
            trains[(t, o)] = rest
        elif "the smoke's premise runs" in (sec or ""):
            a, rest = ln.split(None, 1)
            premise[a] = rest
        else:
            a, rest = ln.split(None, 1)
            if a == "heater":
                heater = rest
            else:
                pas[a] = rest
    return pas, heater, trains, premise


def order(path):
    o = {}
    for ln in open(path):
        if ln.startswith("pass "):
            head, rest = ln.split(":", 1)
            o[int(head.split()[1])] = [w.split("(")[0] for w in rest.split()]
    return o


def expected(desk, ordfile, lab, x14, gen, out, npass=6):
    pas, heater, trains, premise = commands(desk)
    o = order(ordfile)

    def sub(s):
        s = s.replace("sparsity_host ", lab + " ", 1) if s.startswith("sparsity_host ") else s.replace("x14_host ", x14 + " ", 1)
        return "timeout 10 " + s.replace("GEN/", gen + "/").replace("OUT/STOP", out + "/STOP")
    E = [sub(heater)]
    E += [sub(pas[a].replace("--seconds 4 ", "--seconds 2 ")) for a in SMOKE]
    E += [sub(premise[a]) for a in SMOKE]
    E += [sub(trains[("T1", "SFFS")]), sub(trains[("T1", "FSSF")])]
    for t in ("T1", "T2"):
        E.append(sub(pas["K.pi"]))
        E += [sub(trains[(t, "SFFS" if k % 2 == 0 else "FSSF")]) for k in range(24)]
        E.append(sub(pas["K.pi"]))
    for p in range(npass):
        E += [sub(pas[a]) for a in o[p]]
    return E


def calls(path):
    txt = open(path, errors="replace").read()
    c = [ln[len("DRY: "):] for ln in txt.splitlines() if ln.startswith("DRY: timeout ")]
    heat = sum(1 for ln in txt.splitlines() if ln.startswith("DRY: approach: heat to 59 C"))
    nopre = sum(1 for ln in txt.splitlines() if ln.startswith("DRY: approach: no preheat"))
    plans = re.findall(r"PLAN runs=(\d+) arms=(\d+) dropped=(\S+)", txt)
    return c, heat, nopre, plans


def check(path, desk, ordfile, want_n, want_heat, label):
    c, heat, nopre, plans = calls(path)
    bad = []
    if not c:
        return ["%s: no device call listed" % label], c
    lab = next((x.split()[2] for x in c if " --values randn " in x), "")
    x14 = next((x.split()[2] for x in c if " --abba " in x), "")
    m = re.search(r"--stop-file (\S+)/STOP$", c[0])
    out = m.group(1) if m else ""
    gen = out + "/gen"
    if not lab.endswith("build/sparsity-lab/host/sparsity_host"):
        bad.append("%s: the heater is %r, not the lab's host built into E196's root" % (label, lab))
    if not x14.endswith("build/x14/host/x14_host"):
        bad.append("%s: the trains run %r, not the request's host built into E196's root" % (label, x14))
    E = expected(desk, ordfile, lab, x14, gen, out)
    if len(c) != want_n or len(E) != want_n:
        bad.append("%s: %d device calls listed, %d expected (want %d)" % (label, len(c), len(E), want_n))
    for i, (g, w) in enumerate(zip(c, E)):
        if g != w:
            bad.append("%s: call %d differs: got %r, want %r" % (label, i + 1, g[:160], w[:160]))
            break
    if not all(x.startswith("timeout 10 ") and x.split()[-2] == "--stop-file" for x in c):
        bad.append("%s: a call not under timeout 10 or without --stop-file last" % label)
    if heat != want_heat or nopre != 8:
        bad.append("%s: %d approach lines with the heater (want %d), %d with no preheat (want 8)" % (label, heat, want_heat, nopre))
    return bad, c


def main():
    full, cut, desk = sys.argv[1:4]
    b1, c1 = check(full, desk, os.path.join(desk, "order-e196-aifoundry3.txt"), 255, 196, "full")
    b2, c2 = check(cut, desk, os.path.join(desk, "order-e196-aifoundry3-cut.txt"), 237, 178, "cut")
    pl = re.findall(r"PLAN runs=(\d+) arms=(\d+) dropped=(\S+)", open(full).read() + open(cut).read())
    for b in b1 + b2:
        print("  " + b)
    nlab = sum(1 for x in c1 if x.split()[2].endswith("sparsity_host"))
    nx14 = sum(1 for x in c1 if x.split()[2].endswith("x14_host"))
    if b1 or b2:
        print("E196-DRY FAIL: %d problems (above)" % len(b1 + b2))
        return 16
    print("E196-DRY OK: %d device calls (%d with the cut order), line for line the registered commands (desk/commands-e196.txt) in the "
          "written orders for aifoundry3 (passes 0-5): %d on the lab's unchanged host (the heater check, the smoke's first set, the train "
          "anchors, every pass run), %d on the request's host (the smoke's premise runs and two T1 processes, the 48 train processes); "
          "every one under timeout 10 with --stop-file; the approach before every measured run (196; 178 cut) and none before the smoke's "
          "eight; plans %s" % (len(c1), len(c2), nlab, nx14, sorted(set(pl))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
