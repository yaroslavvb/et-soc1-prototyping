#!/usr/bin/env python3
"""E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): THE HOST-OUTPUT PARSERS ON REAL COMMITTED BYTES. Every parser that reads a
device tool's output on E209's path is fed the lab's committed bytes of that tool on this card and on aifoundry3, and a runtime line spliced in
(E191's lesson: a runtime print splits a host's record line): E208's runner's and reducer's parse_sparsity, last_json and parse_ident
(src/mms_common.py, src/mms_ident.py, unchanged), and the collection's checker (E208's data lane's check_session_e208.py, unchanged: its own
sparsity and device-block readers, run on the real-path session in the runbook's desk test). Standard library only; reads only.

    /usr/bin/python3 -I -B tools/claims-v3/e209/desk/realbytes_e209.py          prints one line a check and REALBYTES-E209 <n> of <m> PASS last

THE BYTES (each at its data directory's SHA256SUMS): E208's three sessions on this card (a2c0-S1, a2c0-S2, a2c0-S1r: every host process's stdout
and stderr, the smoke's, the config reads), E206 arm A's session on aifoundry3 (the same rgm136 host: 244 processes, its raw config stdout), and
E191's committed smoke stdout (aifoundry1 card 1), whose runtime line "Opening device 1" split the host's line there.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(REPO, "tools", "claims-v3", "e208", "proposal", "src")
sys.path.insert(0, SRC)
import mms_common as C  # noqa: E402
import mms_ident as N  # noqa: E402

DATA = os.path.join(REPO, "docs", "reports", "data")
E208 = ["2026-11-16-e208-mmsweep-a2c0-S1", "2026-11-16-e208-mmsweep-a2c0-S2", "2026-11-17-e208-mmsweep-a2c0-S1r"]
E206 = "2026-11-16-e206-matmul-sweep-aifoundry3"
E191 = "2026-11-15-e191-blind-day-aifoundry1-c1"
ROWS = []


def row(words, ok, detail=""):
    ROWS.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} {words}" + (f": {detail}" if detail != "" else ""))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pinned(d):
    sums = {}
    for ln in open(os.path.join(DATA, d, "SHA256SUMS")):
        h, r = ln.rstrip("\n").split("  ", 1)
        sums[r] = h
    bad = [r for r, h in sums.items() if r.startswith("session/") and (r.endswith((".out", ".err", ".json")) or "/runs/" in r)
           and os.path.exists(os.path.join(DATA, d, r)) and sha(os.path.join(DATA, d, r)) != h]
    return sums, bad


def procs(d):
    out = []
    for sub in ("runs", "smoke"):
        top = os.path.join(DATA, d, "session", sub)
        for k in sorted(os.listdir(top)) if os.path.isdir(top) else []:
            if not os.path.isdir(os.path.join(top, k)):
                continue
            for n in sorted(os.listdir(os.path.join(top, k))):
                if n.endswith(".out") and (n.startswith("proc")):
                    out.append((os.path.join(top, k, n), os.path.join(top, k, n[:-4] + ".err"), os.path.join(top, k)))
    return out


def main():
    # E208 on this card
    for d in E208:
        sums, bad = pinned(d)
        row(f"{d}: the session's host and config files at the data directory's SHA256SUMS", not bad, f"{len(bad)} differ")
        P = procs(d)
        n_rec = n_lines = n_other = n_bad_ident = 0
        mism = []
        for out, err, rdir in P:
            text = open(out, errors="replace").read()
            sp = C.parse_sparsity(text)
            lines = [ln for ln in text.splitlines() if ln.startswith("SPARSITY ")]
            n_lines += len(lines)
            n_rec += len(sp)
            n_other += sum(1 for ln in text.splitlines() if ln.strip() and not ln.startswith("SPARSITY "))
            tg, ids = N.parse_ident(open(err, errors="replace").read())
            if sorted(set(tg)) != [("0", "ops")] or sorted(set(ids)) != [0]:
                n_bad_ident += 1
            rj = os.path.join(rdir, "run.json")
            if os.path.exists(rj):
                rec = json.load(open(rj))
                name = os.path.basename(out)[:-4]
                for p in rec.get("procs") or []:
                    if p.get("name") == name and p.get("n_launch") != sum(1 for x in sp if x.get("test") == "fma"):
                        mism.append(f"{os.path.basename(rdir)}/{name}")
        row(f"{d}: parse_sparsity reads every SPARSITY line of its {len(P)} host stdouts ({n_rec} of {n_lines})", n_rec == n_lines and n_lines > 0)
        row(f"{d}: no byte on the hosts' stdout but SPARSITY lines (the device layer's table goes to stderr)", n_other == 0, f"{n_other} other lines")
        row(f"{d}: each run record's launch count = the parser's on its committed bytes", not mism, f"{len(mism)} differ {mism[:3]}")
        row(f"{d}: parse_ident on every host stderr: exactly /dev/et0_ops and physical device ID 0", n_bad_ident == 0, f"{n_bad_ident} other")
        for cf in ("config-start", "config-end"):
            j = json.load(open(os.path.join(DATA, d, "session", f"{cf}.json")))
            tg, ids = N.parse_ident(open(os.path.join(DATA, d, "session", f"{cf}.err")).read())
            why = N.config_identity("a2c0", j, open(os.path.join(DATA, d, "session", f"{cf}.err")).read())
            row(f"{d}: {cf}: the identity gate reads its committed stderr (/dev/et0_mgmt, ID 0) and the config gate its JSON",
                why == "" and C.config_ok("a2c0", j) == "", f"{why or 'ok'}; {C.config_ok('a2c0', j) or 'config ok'}")
    # E206 on aifoundry3 (the same host)
    sums, bad = pinned(E206)
    row(f"{E206}: its host and config files at its SHA256SUMS", not bad, f"{len(bad)} differ")
    P = procs(E206)
    n_rec = n_lines = n_other = 0
    for out, err, rdir in P:
        text = open(out, errors="replace").read()
        n_rec += len(C.parse_sparsity(text))
        n_lines += sum(1 for ln in text.splitlines() if ln.startswith("SPARSITY "))
        n_other += sum(1 for ln in text.splitlines() if ln.strip() and not ln.startswith("SPARSITY "))
    row(f"{E206}: parse_sparsity reads every SPARSITY line of its {len(P)} host stdouts ({n_rec} of {n_lines}); other stdout lines {n_other} (REPORTED)",
        n_rec == n_lines and n_lines > 0)
    raw = open(os.path.join(DATA, E206, "session", "config-start.out")).read()
    j = C.last_json(raw)
    row(f"{E206}: last_json on the raw config stdout reads its JSON line (aifoundry3's config: TDP {j.get('tdp_w')} W, {j.get('minion_mhz')} MHz)",
        isinstance(j, dict) and "tdp_w" in j)
    # the runtime line, E191's bytes, at every offset of a real SPARSITY line of this card
    e191 = open(os.path.join(DATA, E191, "session", "smoke", "copy-64m-random", "stdout.txt"), "rb").read()
    i = e191.index(b"Opening device")
    rt = e191[i:e191.index(b"\n", i) + 1].decode()
    row("E191's committed runtime bytes read (aifoundry1 card 1's smoke stdout): " + repr(rt), rt == "Opening device 1\n")
    out, err, rdir = procs(E208[0])[0]
    lines = open(out).read().splitlines()
    line = [ln for ln in lines if ln.startswith("SPARSITY ") and json.loads(ln[9:]).get("test") == "fma"][1]
    good = C.parse_sparsity(line + "\n")
    n = len(line)
    wrong = dropped = kept = 0
    for off in range(0, n + 1):
        s = line[:off] + rt + line[off:] + "\n"
        got = C.parse_sparsity(s)
        if got == good:
            kept += 1
        elif got == []:
            dropped += 1
        else:
            wrong += 1
    row(f"E191's runtime line spliced at every offset 0..{n} of a committed launch line of this card: the record read whole or dropped, never a "
        f"wrong value", wrong == 0 and kept + dropped == n + 1, f"kept {kept} (offset 0: the runtime line before the record), dropped {dropped}, wrong {wrong}")
    chk = [ln for ln in lines if ln.startswith("SPARSITY ") and json.loads(ln[9:]).get("test") == "check"][0]
    s = chk[:len(chk) // 2] + rt + chk[len(chk) // 2:] + "\n"
    rec = [x for x in C.parse_sparsity("\n".join(lines[:-1]) + "\n" + s) if x.get("test") == "check"]
    row("the check record split by the runtime line: no check read (the runner then records check None: a failed process, R0 FAIL)", rec == [])
    between = "\n".join(x + "\n" + rt.strip() for x in lines) + "\n"
    row("the runtime line between every two records: every record read", C.parse_sparsity(between) == C.parse_sparsity("\n".join(lines) + "\n"))
    print(f"REALBYTES-E209 {sum(ROWS)} of {len(ROWS)} {'PASS' if all(ROWS) else 'FAIL'}")
    return 0 if all(ROWS) else 1


if __name__ == "__main__":
    sys.exit(main())
