#!/usr/bin/env python3
"""E220's addition to step 12 for arm A in E213's Amendment A2 form (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum; E213's A2 by Q219's lane a2-e213, landed 8b675547): fwgate's read
folder, copied back at A2's step 4, goes into arm A's data directory as fwgate/, AFTER THE KIT'S SCRUB (the kit's own collect_e220a.py functions,
imported unchanged: every form of the box's home -> "~", our box login -> "<login>", another login's et-who holder line masked; then no home
path and no login left), and the directory's SHA256SUMS is made again over every file in collect_e220a.py's form (sha256, two spaces,
the path beside it; sorted by path). The kit's own step 12 (tools/claims-v3/e220/rb/s23_data_e220a.sh, unchanged) runs first and makes the
directory; this adds to it and changes no byte the kit wrote but SHA256SUMS. Python's own modules only.

    /usr/bin/python3 -I -B tools/claims-v3/e220/a2/data_e220a_a2.py add DATA COPY LIST HOMESFILE LOGINFILE LOOKFILE [EVIDENCE]
        DATA      the directory step 12 made (docs/reports/data/<day>-e220-blind-matmul-aifoundry1-c1, or a gate stop's record under
                  docs/reports/gate-stops/), relative to the lab clone; an absolute path outside it only with RB_DESKTEST=1 (the desk test)
        COPY      RB_OUT/e220a-a2-fwgate-A (A2's step 4's copy of the read's folder; absent or empty when step 4 read CONTINUITY)
        LIST      RB_OUT/e220a-a2-fwgate-A.sha256 (the box's own sha256 list of that folder, step 4's)
        HOMESFILE RB_OUT/box-home-A.txt (step 11's: the box's home in every form);  LOGINFILE RB_OUT/box-login-aifoundry1.txt (the look's)
        LOOKFILE  RB_OUT/e220a-a2-look-A.txt (A2's step 4's verdict line)
        EVIDENCE  RB_OUT/e220a-a2-evidence-A (fix-a2e213, verify-a2e213's finding 2: step 4's read-only capture of this boot's fwgate ledger lines
                  and the kit's attempt-log lines, with its list EVIDENCE.sha256). When the read's folder is added, its two files go beside the
                  record in fwgate/ AFTER THE KIT'S SCRUB (the ledger lines' record paths name the box's home: masked as "~"). NEVER A
                  REFUSAL: a capture that is missing, changed since step 4, not whole, or not clean after the scrub is left out and said.
  CONTINUITY (step 4 read no firmware: the box booted before the newest committed record of card 1) with no copy: "A2-DATA CONTINUITY: nothing
  added; SHA256SUMS as the kit made it" (exit 0). EQUAL: the copy checked again against LIST (every file at its sha256, nothing else), then
  copied into DATA/fwgate/ (refused if it exists), scrubbed, checked (exactly one fwgate read record, verdict EQUAL, box aifoundry1, card 1,
  its raw answer's two files beside it at the sha256 the record names), then EVIDENCE's two files beside them (scrubbed; or left out, said),
  SHA256SUMS made again and read back: "A2-DATA ADDED fwgate/: ..." (exit 0). Anything else: "A2-DATA REFUSED: ..." (exit 3), DATA/fwgate/
  removed again if this call made it, SHA256SUMS untouched: commit nothing.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "e220"))
import collect_e220a as K  # noqa: E402  (the kit's collection: its scrub, unchanged)


def refuse(msg, made=None):
    if made and os.path.isdir(made):
        shutil.rmtree(made)
    print("A2-DATA REFUSED: " + msg)
    return 3


def read_list(p):
    out = {}
    for ln in open(p):
        if not ln.strip():
            continue
        h, rel = ln.rstrip("\n").split("  ", 1)
        if not re.fullmatch(r"[0-9a-f]{64}", h) or rel.startswith("/") or ".." in rel.split("/"):
            raise ValueError(f"an unreadable line in {p}")
        out[rel] = h
    return out


def files_under(top):
    have = []
    for dp, dn, fn in os.walk(top):
        dn.sort()
        for n in sorted(fn):
            have.append(os.path.relpath(os.path.join(dp, n), top))
    return have


def remake_sums(dabs):
    rows = [f"{K.sha(os.path.join(dabs, r))}  {r}" for r in files_under(dabs) if r != "SHA256SUMS"]
    with open(os.path.join(dabs, "SHA256SUMS"), "w") as f:
        f.write("\n".join(sorted(rows, key=lambda x: x[66:])) + "\n")
    return len(rows)


def sums_ok(dabs):
    want = read_list(os.path.join(dabs, "SHA256SUMS"))
    have = set(files_under(dabs)) - {"SHA256SUMS"}
    bad = [r for r in want if r not in have or K.sha(os.path.join(dabs, r)) != want[r]] + sorted(have - set(want))
    return len(want), bad


EV_FILES = ("fwgate-ledger-aifoundry1-c1-this-boot.jsonl", "a2-fwgate-attempts-aifoundry1-c1-this-boot.jsonl")


def add_evidence(dst, ev, homes, login):
    """fix-a2e213 (verify-a2e213's finding 2): step 4's capture of this boot's fwgate ledger lines and the kit's attempt-log lines into fwgate/
    beside the record, through the kit's scrub. Never a refusal: what cannot be added is left out and said. (files added, a note)"""
    what = "the evidence of the one call"
    if not ev:
        return 0, f"{what}: no capture given (left out)"
    if not os.path.isdir(ev):
        return 0, f"{what}: step 4 captured none in this RB_OUT (left out)"
    have = files_under(ev)
    try:
        want = read_list(ev.rstrip("/") + ".sha256")
    except (OSError, ValueError) as e:
        return 0, f"{what}: its list cannot be read ({e}) (left out)"
    bad = ([f"missing {r}" for r in EV_FILES if r not in have] + [f"not one of its two files: {r}" for r in sorted(set(have) | set(want))
                                                                    if r not in EV_FILES]
           + [f"not on its list: {r}" for r in EV_FILES if r in have and r not in want]
           + [f"differs {r}" for r in EV_FILES if r in have and r in want and K.sha(os.path.join(ev, r)) != want[r]])
    if bad:
        return 0, f"{what}: changed since step 4 or not whole ({'; '.join(bad[:4])}) (left out)"
    made = []
    try:
        for r in EV_FILES:
            p = os.path.join(dst, r)
            if os.path.exists(p):
                raise ValueError(f"fwgate/{r} exists already")
            shutil.copyfile(os.path.join(ev, r), p)
            made.append(p)
            body = K.scrub_file(p, homes, login)
            if K.left_over(body, homes, login):
                raise ValueError(f"THE SCRUB left a home path, the login or another login's holder line in fwgate/{r}")
    except (OSError, ValueError) as e:
        for p in made:
            if os.path.isfile(p):
                os.remove(p)
        return 0, f"{what}: left out ({e})"
    nl = [sum(1 for ln in open(p, "rb") if ln.strip()) for p in made]
    return len(made), (f"{what}: fwgate/{EV_FILES[0]} ({nl[0]} line(s)) and fwgate/{EV_FILES[1]} ({nl[1]} line(s)), this boot's, through "
                       "the kit's scrub")


def main(argv):
    if len(argv) not in (7, 8) or argv[0] != "add":
        print(__doc__)
        return 2
    data, copy, lst, hf, lf, look = argv[1:7]
    ev = argv[7] if len(argv) == 8 else ""
    if os.path.isabs(data):
        if os.environ.get("RB_DESKTEST") != "1" or os.path.realpath(data).startswith(os.path.realpath(REPO) + os.sep):
            return refuse(f"an absolute DATA path ({data}) is the desk test's alone (RB_DESKTEST=1, outside the lab clone)")
        dabs = data
    else:
        if not re.fullmatch(r"docs/reports/(data/\d{4}-\d{2}-\d{2}-e220-blind-matmul-aifoundry1-c1|gate-stops/\d{4}-\d{2}-\d{2}-e220-blind-matmul-T\d+-"
                            r"aifoundry1-c1)", data):
            return refuse(f"{data} is not E220 arm A's data directory or gate stop's record")
        dabs = os.path.join(REPO, data)
    if not os.path.isdir(dabs) or not os.path.isfile(os.path.join(dabs, "SHA256SUMS")):
        return refuse(f"{data} is not a collected directory with its SHA256SUMS (the kit's step 12 runs first)")
    kb, bad0 = sums_ok(dabs)
    if bad0:
        return refuse(f"{data}'s SHA256SUMS does not read every file OK before A2's addition ({', '.join(bad0[:4])})")
    try:
        verdict = open(look).read()
    except OSError:
        return refuse(f"no A2 step-4 verdict ({look})")
    m = re.search(r"A2-LOOK-A: (CONTINUITY|EQUAL)\b", verdict)
    if not m:
        return refuse(f"A2's step 4 did not pass in this RB_OUT ({look})")
    have = files_under(copy) if os.path.isdir(copy) else []
    if m.group(1) == "CONTINUITY" and not have:
        print(f"A2-DATA CONTINUITY: step 4 read no firmware (the box booted before the newest committed record of card 1): nothing added; "
              f"SHA256SUMS as the kit made it ({kb} entries)")
        return 0
    if not have:
        return refuse(f"step 4 read {m.group(1)} but its copy of the read's folder ({copy}) is empty or missing")
    try:
        want = read_list(lst)
    except (OSError, ValueError) as e:
        return refuse(f"the box's list of the read's folder cannot be read ({e})")
    badc = ([f"missing {r}" for r in want if r not in have] + [f"differs {r}" for r in want if r in have and K.sha(os.path.join(copy, r)) != want[r]]
            + [f"not on the box's list: {r}" for r in sorted(set(have) - set(want))])
    if badc:
        return refuse("step 4's copy is not the box's folder any more: " + "; ".join(badc[:5]))
    homes, login = K.read_homes(hf), K.read_login(lf)
    if not homes or not login:
        return refuse("no box home (step 11's RB_OUT/box-home-A.txt) or no login (the look's RB_OUT/box-login-aifoundry1.txt)")
    dst = os.path.join(dabs, "fwgate")
    if os.path.exists(dst):
        return refuse(f"{data}/fwgate exists already (never merge into an earlier copy)")
    shutil.copytree(copy, dst)
    n, masked, left = K.scrub_tree(dst, homes, login)
    if left:
        return refuse("THE SCRUB left a home path, the login or another login's holder line in fwgate/" + ", fwgate/".join([""] + left[:6]),
                      made=dst)
    recs = []
    for r in files_under(dst):
        if re.fullmatch(r"fwgate-aifoundry1-c1-\d{8}-\d{6}\.json", r):
            try:
                recs.append((r, json.load(open(os.path.join(dst, r)))))
            except (OSError, ValueError):
                return refuse(f"fwgate/{r} cannot be read after the scrub", made=dst)
    if len(recs) != 1:
        return refuse(f"fwgate/ holds {len(recs)} read records of aifoundry1 card 1, not one", made=dst)
    name, rec = recs[0]
    raw = rec.get("raw") if isinstance(rec.get("raw"), dict) else {}
    rawbad = []
    for k in ("stdout", "stderr"):
        x = raw.get(k) if isinstance(raw.get(k), dict) else {}
        p = os.path.join(dst, str(x.get("file", "")))
        if not x.get("file") or not os.path.isfile(p) or K.sha(p) != x.get("sha256"):
            rawbad.append(k)
    if (rec.get("schema") != "fwgate-read/1" or rec.get("verdict") != "EQUAL" or rec.get("box") != "aifoundry1" or rec.get("card") != 1
            or rawbad):
        return refuse(f"fwgate/{name} is not an EQUAL read of aifoundry1 card 1 with its raw answer at its sha256 (verdict {rec.get('verdict')}, "
                      f"raw {', '.join(rawbad) or 'ok'})", made=dst)
    nev, evnote = add_evidence(dst, ev, homes, login)                   # fix-a2e213: never a refusal
    nsum = remake_sums(dabs)
    ka, bad1 = sums_ok(dabs)
    if bad1 or ka != kb + n + nev:
        return refuse(f"SHA256SUMS made again does not read back ({ka} entries, want {kb + n + nev}; {', '.join(bad1[:4])})", made=dst)
    print(f"A2-DATA ADDED fwgate/: {n} files from step 4's copy ({masked} masked by the kit's scrub: the record's ledger path's home -> '~'), the "
          f"record {name} (EQUAL, aifoundry1 card 1, read {rec.get('read_at')}, both locks {rec.get('locks')}, et-who --check rc "
          f"{rec.get('et_who_check_rc')}, ET_DEVICES {rec.get('ET_DEVICES')}), its raw answer at its sha256; {evnote}; SHA256SUMS made again: "
          f"{nsum} entries ({kb} the kit's and {n + nev} A2's), every one OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
