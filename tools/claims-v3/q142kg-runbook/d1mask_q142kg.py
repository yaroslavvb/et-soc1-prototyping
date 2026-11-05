#!/usr/bin/env python3
"""E173's departure D1 made a rule (README.md.dated-note-3.md): the parts of d1mask_q142kg.sh that read or write a file.

Written Thu 5 Nov 2026 (week 45), PST, in the E173 card lane's fix pass, after E173's data commit (ed8b5761) and before any E175 session.
A collection through a v3 step driver that hands its collector a raw copy under $RB_OUT (E173's step_e173_v3.sh line 24; E175's kit,
step_e175_v3.sh line 187) tees the C-log list's REQUIRED lines with that raw copy's paths into $RAW/logs/cclist.txt (the collectors' line 86),
copies logs/ into the data dir (their line 96), and v3.1's desk-path gate (nopath_q142s.py) then stops the step with 16. The rule replaces the
RB_OUT prefix of those paths, in that one file only, by `<RB_OUT>` (rb_disp's own display form), keeps the bytes as collected outside the repo,
and re-runs the step's two gates. This file does the reads and the one write; d1mask_q142kg.sh runs the gates through rb_common_v3.sh.

    d1mask_q142kg.py since <runbook.log> <step>          the collect step's start (the probe line of the call that stopped), only if that
                                                           step's last line is the desk-path gate's stop; prints SINCE <epoch s> ...
    d1mask_q142kg.py plan <data dir> <RB_OUT> <gate out>  every hit the gate printed is in logs/cclist.txt, and every RB_OUT there is the prefix
                                                           of a REQUIRED line's path; prints D1MASK-PLAN
    d1mask_q142kg.py manifest <data dir> <out file>       writes the sha256 and path of every file under it, sorted (symbolic links skipped)
    d1mask_q142kg.py compare <before> <after> <relpath>   the two manifests differ in <relpath> only, which changed; prints D1MASK-COMPARE
    d1mask_q142kg.py mask <cclist.txt> <RB_OUT> <copy>    keeps the bytes as collected in <copy> (outside the repo), writes the masked
                                                           bytes, checks the round trip; prints D1MASK-DONE
    d1mask_q142kg.py restore <copy> <cclist.txt>          writes the bytes as collected back; prints D1MASK-RESTORED
    d1mask_q142kg.py sha <file>                           prints the file's sha256

Exit codes: 0 done; 10 the rule does not apply (nothing to mask, the step's last line is not the desk-path stop, a copy that differs); 16 the
gate's hits are outside the rule (fix the route, remove the outputs, collect again); 2 a usage error. Standard library only; it prints paths as
given (repo-relative) and never prints RB_OUT.
SPDX-License-Identifier: Apache-2.0
"""
import datetime as dt
import hashlib
import os
import sys

MASK = "<RB_OUT>"
STOP_16 = "exit=16 a desk path reached what this step wrote"
ZONES = {"PST": -8, "PDT": -7}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def refuse(code, msg):
    print(("D1MASK-REFUSED: " if code == 10 else "D1MASK-OUTSIDE-RULE: ") + msg)
    return code


def cmd_since(log, step):
    try:
        lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
    except OSError as e:
        return refuse(10, f"cannot read the runbook log ({type(e).__name__})")
    mine = [ln.split(" ", 4) for ln in lines]
    mine = [w for w in mine if len(w) == 5 and w[3] == f"step={step}"]
    if not mine:
        return refuse(10, f"the runbook log has no line of step {step}")
    stops = [k for k, w in enumerate(mine) if w[4].startswith("exit=")]
    if not stops:
        return refuse(10, f"step {step} has no stop in the runbook log")
    k = stops[-1]
    if not mine[k][4].startswith(STOP_16):
        return refuse(10, f"step {step}'s last stop is not the desk-path gate's ({mine[k][4][:48]})")
    if k != len(mine) - 1:
        return refuse(10, f"step {step} ran again after its desk-path stop: read the runbook log first")
    probes = [j for j in range(k) if mine[j][4].startswith("class=probe ")]
    if not probes:
        return refuse(10, f"step {step} has no probe line before its desk-path stop")
    j = probes[-1]
    if [x for x in range(j + 1, k) if mine[x][4].startswith("exit=")]:
        return refuse(10, f"step {step}'s last probe line is not the start of the call that stopped at the desk-path gate")
    d, t, z = mine[j][:3]
    if z not in ZONES:
        return refuse(10, f"the probe line's zone {z!r} is neither PST nor PDT")
    when = dt.datetime.strptime(f"{d} {t}", "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone(dt.timedelta(hours=ZONES[z])))
    print(f"SINCE {int(when.timestamp())} {d} {t} {z} (the collect step's probe line; its desk-path stop at {' '.join(mine[k][:3])})")
    return 0


def cmd_plan(ddir, rbout, gate):
    target = os.path.join(ddir, "logs", "cclist.txt")
    try:
        g = open(gate, encoding="utf-8", errors="replace").read().splitlines()
    except OSError as e:
        return refuse(10, f"cannot read the gate's output ({type(e).__name__})")
    hits, other = 0, []
    for ln in g:
        if ln.startswith(("MISSING ", "UNREAD ")):
            other.append(ln.split(" ", 1)[0])
        elif ln.startswith("HIT "):
            p = ln[4:].split(": ", 1)[0]
            if p == target:
                hits += 1
            else:
                other.append("HIT " + (os.path.relpath(p, ddir) if not os.path.isabs(p) else "(an absolute path)"))
    if other:
        return refuse(16, f"the gate read a desk path, or a missing or unread file, outside logs/cclist.txt: {len(other)} line(s), "
                          f"the first {other[0]}")
    if not hits:
        return refuse(10, "the gate read no desk path in logs/cclist.txt: nothing to mask")
    rb = rbout.rstrip("/")
    if not rb.startswith("/") or len(rb) < 2:
        return refuse(10, "RB_OUT is not an absolute path: the rule masks an absolute RB_OUT only")
    try:
        raw = open(target, "rb").read()
    except OSError as e:
        return refuse(10, f"cannot read logs/cclist.txt ({type(e).__name__})")
    if MASK.encode() in raw:
        return refuse(10, f"logs/cclist.txt already holds {MASK}: the rule runs once, on the bytes as collected")
    text = raw.decode("utf-8")
    n_req, n_occ = 0, text.count(rb)
    for ln in text.split("\n"):
        if ln == "":
            continue
        w = ln.split(" ", 2)
        if w[0] == "REQUIRED" and len(w) == 3:
            p = w[2]
            if p.startswith(rb + "/"):
                if p.count(rb) != 1:
                    return refuse(16, "a REQUIRED path names RB_OUT more than once")
                n_req += 1
            elif p.startswith("/") or ".." in p.split("/") or rb in p:
                return refuse(16, "a REQUIRED path is absolute or climbs out without being under RB_OUT: the mask does not cover it")
        elif w[0] == "cclist:":
            if rb in ln:
                return refuse(16, "the list's summary line names RB_OUT")
        else:
            return refuse(16, f"logs/cclist.txt holds a line the C-log list (cclist_q142kg.py) never prints: {w[0][:20]!r}")
    if n_occ != n_req or n_req == 0:
        return refuse(16, f"RB_OUT occurs {n_occ} time(s) in logs/cclist.txt, {n_req} of them as a REQUIRED path's prefix: "
                          f"the mask does not cover the rest")
    print(f"D1MASK-PLAN: {n_occ} occurrence(s) of RB_OUT, each the prefix of a REQUIRED line's path, and every hit the gate printed "
          f"is in logs/cclist.txt ({hits} HIT line(s)); sha256 as collected {sha(raw)}")
    return 0


def cmd_manifest(ddir, out):
    rows = []
    for d, dirs, fs in os.walk(ddir):
        dirs.sort()
        for fn in sorted(fs):
            p = os.path.join(d, fn)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            rows.append(f"{sha(open(p, 'rb').read())}  {os.path.relpath(p, ddir)}\n")
    with open(out, "w", encoding="utf-8") as f:
        f.writelines(rows)
    print(f"D1MASK-MANIFEST: {len(rows)} files, the list's sha256 {sha(''.join(rows).encode())}")
    return 0


def cmd_compare(before, after, rel):
    def read(p):
        m = {}
        for ln in open(p, encoding="utf-8"):
            h, q = ln.rstrip("\n").split("  ", 1)
            m[q] = h
        return m
    a, b = read(before), read(after)
    if set(a) != set(b):
        return refuse(16, f"the data dir's files changed in number or name ({len(a)} before, {len(b)} after)")
    changed = sorted(q for q in a if a[q] != b[q])
    if changed != [rel]:
        return refuse(16, f"the files changed are {changed[:3]} ({len(changed)}), not {rel} alone")
    print(f"D1MASK-COMPARE: of the data dir's {len(a)} files only {rel} changed")
    return 0


def cmd_mask(target, rbout, copy):
    raw = open(target, "rb").read()
    rb = rbout.rstrip("/").encode()
    if os.path.exists(copy):
        if open(copy, "rb").read() != raw:
            return refuse(10, "a copy as collected is already kept and differs from logs/cclist.txt: read it before anything else")
    else:
        os.makedirs(os.path.dirname(copy), exist_ok=True)
        with open(copy, "wb") as f:
            f.write(raw)
    if open(copy, "rb").read() != raw:
        return refuse(10, "the copy as collected does not read back")
    new = raw.replace(rb, MASK.encode())
    n = raw.count(rb)
    if new.replace(MASK.encode(), rb) != raw or new.replace(MASK.encode(), b"") != raw.replace(rb, b""):
        return refuse(10, "the mask does not round-trip")
    with open(target, "wb") as f:
        f.write(new)
    if open(target, "rb").read() != new:
        return refuse(10, "logs/cclist.txt does not read back")
    print(f"D1MASK-DONE: {n} occurrence(s) of RB_OUT replaced by {MASK} in logs/cclist.txt, nothing else; sha256 as collected "
          f"{sha(raw)}, after {sha(new)}; the bytes as collected kept outside the repo")
    return 0


def cmd_restore(copy, target):
    raw = open(copy, "rb").read()
    with open(target, "wb") as f:
        f.write(raw)
    print(f"D1MASK-RESTORED: logs/cclist.txt holds the bytes as collected again (sha256 {sha(open(target, 'rb').read())})")
    return 0


def cmd_sha(p):
    print(sha(open(p, "rb").read()))
    return 0


def main(argv):
    use = {"since": (2, cmd_since), "plan": (3, cmd_plan), "manifest": (2, cmd_manifest), "compare": (3, cmd_compare),
           "mask": (3, cmd_mask), "restore": (2, cmd_restore), "sha": (1, cmd_sha)}
    if not argv or argv[0] not in use or len(argv) != use[argv[0]][0] + 1:
        print("usage: d1mask_q142kg.py since <log> <step> | plan <data dir> <RB_OUT> <gate out> | manifest <data dir> <out> | "
              "compare <before> <after> <relpath> | mask <cclist.txt> <RB_OUT> <copy> | restore <copy> <cclist.txt> | sha <file>")
        return 2
    return use[argv[0]][1](*argv[1:])


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    sys.exit(main(sys.argv[1:]))
