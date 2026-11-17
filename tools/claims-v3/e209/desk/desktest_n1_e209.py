#!/usr/bin/env python3
"""E209's kit note 1 (Q212, lane note-e209, Tue 17 Nov 2026 PST): THE DESK TEST of the fixed collection (collect_e209_n1.py) and of the two
runbook steps that call it (rb/s22_collect_e209_n1.sh, step 11; rb/s24_score_e209_n1.sh, step 13's manifest read), on E209's REAL session
(read only) and on stand-ins that must pass and must fail. Python's own modules only. Run it from a scratch clone of the lab (never from the
lab clone the card lanes use), inside the round's slot and no-device sandbox, while THE QUIET DESK FLAG is absent:

    bash W/slot.sh bash W/nodev.sh /usr/bin/python3 -I -B tools/claims-v3/e209/desk/desktest_n1_e209.py \
        --root E209_ROOT --rb RB_OUT_OF_THE_CARD_LANE --work A_NEW_EMPTY_FOLDER

--root is the card lane's box root (its sessions/<SID> is read, never written); --rb is the card lane's RB_OUT (its e209-session.txt,
e209-first.txt, window.env, ranbefore-e209.json, neverrun-*/ and copy/ are copied, never written); --work is a new folder outside the repo
where every case writes (its own RB_OUT, its own stand-in lab, its own stand-in box root). Nothing is written in the repo it runs from, in
the box root or in the card lane's RB_OUT; no card, no device, no network. Every printed line has the user database's home written as
<home>, the login as <login> and the work folder as <work>.

THE CASES (each prints its verdict; the last line is "DESKTEST-N1-E209 <k> of <n> PASS"):
  R1  the real session, collect_e209_n1.py, an RB_OUT holding the card lane's first copy-back copy/<SID>: exit 0; the data directory's
      session/ equals the copy-back but for the record, which differs in its line 34 alone, that line reading E200's form; the record's raw
      sha256 = its manifest line; nothing private left anywhere in the data directory; SHA256SUMS reads OK; copy/<SID> untouched
  R2  the real session, collect_e209.py (the kit's, unchanged): exit 16, the words card-e209 read; nothing written in its lab
  EQ  collect_e209.py on a stand-in whose record is masked beforehand (its manifest line made to match): exit 0, and its data directory
      equals R1's in every file but session/MANIFEST.sha256 (that one line) and SHA256SUMS (that one line): THE MASK and nothing else
  C1  R1's RB_OUT again (its copy-n1 there): exit 10, nothing new written
  C2  --copy-name 'bad/name': exit 10 before any copy
  P2  a stand-in whose record's ledger path holds no home (a desk ledger folder): exit 0, nothing masked, the record at its manifest line
  F1  the home in another line of the record as well: exit 16           F2  the login alone in fwgate's stderr: exit 16
  F3  another user's home folder in runner.out: exit 16                F4  the box root's path in runner.out: exit 16
  F5  the ledger line with another home: exit 16 (never masked)         F6  the ledger line of another card's ledger: exit 16 (never masked)
  F7  the ledger line's exact text in runner.out, not in a record: 16   F8  two ledger lines in the record: exit 16 (THE MASK refuses)
  F9  the home inside a .gz file of the session: exit 16                F10 the record under another file name: exit 16 (never masked)
      (F1-F10: nothing written in the case's lab)
  M0  `sha256sum -c --quiet MANIFEST.sha256` (the kit's step 13 read) on R1's committed-to-be session/: FAILS on the record alone
  M1  --manifest-check on it: exit 0, 1 line by THE MASK       M6  --manifest-check on the raw copy-back: exit 0, 0 by THE MASK
  M2  another file changed: exit 10        M3  the record changed in a second line: exit 10        M4  "~" read as another home: exit 10
  M5  a listed file missing: exit 10       M7  the masked form under another file name: exit 10
  S1  rb/s22_collect_e209_n1.sh in its desk mode on the real session (a stand-in quiet-desk flag, a stand-in lab): exit 0, the data directory
      written, the stand-in flag lowered, RB_OUT/collect-n1.txt and e209-datadir.txt written; its data directory equals R1's but for the
      checker's outputs where the checker writes its own run time
  S2  outside its desk mode, a stand-in round folder showing no collect span: exit 10 (THE ONE-LAB RULE)
  S3  RB_ONELAB_LANE=collect-e209 with the span shown only under the card lane's name: exit 10 (the span is read under RB_ONELAB_LANE)
  S4  RB_ONELAB_LANE=collect-e209 with its span shown: the span held, then the collector refuses a bad copy name (10) before any write
  W1  rb/s24_score_e209_n1.sh in a stand-in repository (rb_e209.sh, both step-13 scripts, collect_e209_n1.py, E208's reducer and module at
      their pins, a committed stand-in data directory holding only the masked record and its manifest line): the manifest read passes (1 by
      THE MASK) and the reducer runs (and fails on the stand-in: exit 14)
  W2  the kit's rb/s24_score_e209.sh on the same: exit 10 at its manifest read (why step 13 needs the note's script)
  W3  rb/s24_score_e209_n1.sh with the record changed in a second line: exit 10 at the manifest read, the reducer never runs
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import hashlib
import json
import os
import pwd
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.dirname(HERE)                                   # tools/claims-v3/e209 in the repo it runs from
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
CK_DIR = "docs/reports/data/2026-11-16-e208-mmsweep-a2c0-S1"
REC = "first/fwgate-aifoundry2-c0-20261117-103044.json"
PY = "/usr/bin/python3"
ME = pwd.getpwuid(os.getuid())
HOME, LOGIN = ME.pw_dir, ME.pw_name
HROOT = (os.path.dirname(HOME) + "/").encode()    # the folder that holds the homes (the scrub's own home-root pattern names it on this box)
RESULTS = []
WORK = ""


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def shab(b):
    return hashlib.sha256(b).hexdigest()


def m(s):
    s = str(s)
    if WORK:
        s = s.replace(WORK, "<work>")
    return s.replace(HOME, "<home>").replace(LOGIN, "<login>")


def say(s=""):
    print(m(s), flush=True)


def verdict(case, ok, words):
    RESULTS.append((case, bool(ok)))
    say(f"CASE {case}: {'PASS' if ok else 'FAIL'}: {words}")


def run(cmd, env=None, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=cwd)
    return r.returncode, (r.stdout + r.stderr)


def tail(out, n=1):
    return " | ".join(x for x in out.strip().splitlines()[-n:])


def tree(d):
    out = {}
    for dp, dn, fn in os.walk(d):
        dn.sort()
        for n in sorted(fn):
            p = os.path.join(dp, n)
            out[os.path.relpath(p, d)] = sha(p)
    return out


def private_in(d):
    pats = [LOGIN.encode(), HOME.encode(), HROOT]
    hits = []
    for dp, dn, fn in os.walk(d):
        for n in fn:
            b = open(os.path.join(dp, n), "rb").read()
            if n.endswith(".gz"):
                try:
                    b = gzip.decompress(b)
                except OSError:
                    pass
            if any(p in b for p in pats):
                hits.append(os.path.relpath(os.path.join(dp, n), d))
    return hits


def make_lab(name):
    lab = os.path.join(WORK, "labs", name)
    os.makedirs(os.path.join(lab, CK_DIR))
    for f in ("check_session_e208.py", "SHA256SUMS"):
        shutil.copy2(os.path.join(REPO, CK_DIR, f), os.path.join(lab, CK_DIR, f))
    return lab


def make_rb(name, rbsrc, with_copy=False):
    rb = os.path.join(WORK, "rb", name)
    os.makedirs(rb)
    for f in ("e209-session.txt", "e209-first.txt", "window.env", "ranbefore-e209.json"):
        if os.path.exists(os.path.join(rbsrc, f)):
            shutil.copy2(os.path.join(rbsrc, f), os.path.join(rb, f))
    for x in sorted(os.listdir(rbsrc)):
        if x.startswith("neverrun-") and os.path.isdir(os.path.join(rbsrc, x)):
            shutil.copytree(os.path.join(rbsrc, x), os.path.join(rb, x))
    if with_copy:
        shutil.copytree(os.path.join(rbsrc, "copy"), os.path.join(rb, "copy"), symlinks=True)
    return rb


def make_box(name, root, sid, edits=(), renames=(), adds=()):
    """A stand-in box root: src/, build/BUILD-mms.json, sessions/<SID>.start.out and a copy of the real session, edited; every changed,
    renamed or added file's manifest line re-made (runner.out stays outside the manifest)."""
    box = os.path.join(WORK, "boxes", name)
    os.makedirs(os.path.join(box, "sessions"))
    shutil.copytree(os.path.join(root, "src"), os.path.join(box, "src"))
    os.makedirs(os.path.join(box, "build"))
    shutil.copy2(os.path.join(root, "build", "BUILD-mms.json"), os.path.join(box, "build", "BUILD-mms.json"))
    so = os.path.join(root, "sessions", sid + ".start.out")
    if os.path.exists(so):
        shutil.copy2(so, os.path.join(box, "sessions", sid + ".start.out"))
    sd = os.path.join(box, "sessions", sid)
    shutil.copytree(os.path.join(root, "sessions", sid), sd)
    man = [ln.rstrip("\n").split("  ", 1) for ln in open(os.path.join(sd, "MANIFEST.sha256")) if ln.strip()]
    for rel, fn in edits:
        p = os.path.join(sd, rel)
        data = open(p, "rb").read()          # read first: open(p, "wb") would empty the file before its argument is read
        open(p, "wb").write(fn(data))
    for old, new in renames:
        os.rename(os.path.join(sd, old), os.path.join(sd, new))
        man = [[h, new if r == old else r] for h, r in man]
    for rel, b in adds:
        open(os.path.join(sd, rel), "wb").write(b)
        man.append(["", rel])
    man = [[sha(os.path.join(sd, r)) if (r in [e[0] for e in edits] or r in [n for _, n in renames] or r in [a[0] for a in adds]) else h, r]
           for h, r in man]
    open(os.path.join(sd, "MANIFEST.sha256"), "w").write("".join(f"{h}  {r}\n" for h, r in man))
    return box


def collect(script, root, sid, rb, lab, extra=()):
    return run([PY, "-I", "-B", os.path.join(E, script), "--root", root, "--sid", sid, "--rb-out", rb, "--lab", lab] + list(extra))


def line_of(b, i):
    return b.split(b"\n")[i - 1]


def main(argv):
    global WORK
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rb", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args(argv)
    root, rbsrc = os.path.realpath(a.root), os.path.realpath(a.rb)
    WORK = os.path.realpath(a.work)
    if os.path.exists(WORK) and os.listdir(WORK):
        print("DESKTEST-N1-E209: --work must be a new or empty folder")
        return 2
    if (WORK + "/").startswith(REPO + "/") or (WORK + "/").startswith(root + "/") or (WORK + "/").startswith(rbsrc + "/"):
        print("DESKTEST-N1-E209: --work must be outside the repo, the box root and the card lane's RB_OUT")
        return 2
    os.makedirs(WORK, exist_ok=True)
    sid = dict(x.split("=", 1) for x in open(os.path.join(rbsrc, "e209-session.txt")).read().split())["SID"]
    sd = os.path.join(root, "sessions", sid)
    raw = open(os.path.join(sd, REC), "rb").read()
    man0 = dict((r, h) for h, r in (ln.rstrip("\n").split("  ", 1) for ln in open(os.path.join(sd, "MANIFEST.sha256")) if ln.strip()))
    rb_before = tree(rbsrc)
    box_before = tree(sd)
    say(f"== DESKTEST-N1-E209 (interpreter {PY} {sys.version.split()[0]}); the repo it runs from at "
        f"{run(['git', '-C', REPO, 'rev-parse', '--short', 'HEAD'])[1].strip()}; session {sid}; collect_e209_n1.py "
        f"{sha(os.path.join(E, 'collect_e209_n1.py'))[:16]}...; collect_e209.py {sha(os.path.join(E, 'collect_e209.py'))[:16]}...")
    nl = raw.count(b"\n")
    say(f"   the real record {REC}: {len(raw)} bytes, {nl} lines, sha256 {shab(raw)} (its manifest line {man0.get(REC)})")
    hl = [i + 1 for i, ln in enumerate(raw.split(b"\n")) if HOME.encode() in ln or LOGIN.encode() in ln or HROOT in ln]
    say(f"   lines of it holding the login, the home or the home root: {hl}")
    want_line = b' "ledger": "~/.local/state/fwgate/aifoundry2-c0.jsonl",'

    # R1: the real session, the fixed collection, beside the card lane's first copy-back
    rb1, lab1 = make_rb("R1", rbsrc, with_copy=True), make_lab("R1")
    first_before = tree(os.path.join(rb1, "copy"))
    rc, out = collect("collect_e209_n1.py", root, sid, rb1, lab1)
    for ln in out.strip().splitlines():
        say(f"   R1 | {ln[:300]}")
    dd = os.path.join(lab1, "docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2")
    ok = rc == 0 and os.path.isdir(dd)
    words = [f"exit {rc}"]
    if ok:
        cp = os.path.join(rb1, "copy-n1", sid)
        t_dd, t_cp = tree(os.path.join(dd, "session")), tree(cp)
        diff = sorted(k for k in set(t_dd) | set(t_cp) if t_dd.get(k) != t_cp.get(k))
        com = open(os.path.join(dd, "session", REC), "rb").read()
        rl, cl = raw.split(b"\n"), com.split(b"\n")
        dl = [i + 1 for i in range(max(len(rl), len(cl))) if (rl[i] if i < len(rl) else None) != (cl[i] if i < len(cl) else None)]
        priv = private_in(dd)
        sums_ok = run(["sha256sum", "-c", "--quiet", "SHA256SUMS"], cwd=dd)[0] == 0
        mask = json.load(open(os.path.join(rb1, "copy-n1", "mask-n1.json")))
        first_same = tree(os.path.join(rb1, "copy")) == first_before
        ok = (diff == [REC] and dl == [34] and line_of(com, 34) == want_line and shab(raw) == man0.get(REC) == t_cp.get(REC)
              and not priv and sums_ok and first_same and len(mask["masked"]) == 1 and mask["masked"][0]["committed_sha256"] == shab(com)
              and os.path.exists(os.path.join(rb1, "copy", sid, "MANIFEST.sha256")))
        words += [f"session/ vs the copy-back: differing files {diff}", f"the record's differing lines {dl}",
                  f"line 34 now {line_of(com, 34).decode()}", f"raw sha256 {shab(raw)[:16]}... = the manifest line: {shab(raw) == man0.get(REC)}",
                  f"committed sha256 {shab(com)}", f"private strings in the data directory: {priv or 'none'}",
                  f"SHA256SUMS OK: {sums_ok}", f"copy/<SID> untouched: {first_same}", f"data directory files: {len(tree(dd))}"]
        R1_DD, R1_COM = dd, com
    else:
        R1_DD, R1_COM = None, None
    verdict("R1", ok, "; ".join(words))

    # R2: the kit's own collector on the real session (card-e209's stop, reproduced)
    rb2, lab2 = make_rb("R2", rbsrc), make_lab("R2")
    rc, out = collect("collect_e209.py", root, sid, rb2, lab2)
    ok = rc == 16 and "THE SCRUB found 1 file(s) with a private string" in out and f"{REC}: the login name" in out \
        and not os.path.exists(os.path.join(lab2, "docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2"))
    verdict("R2", ok, f"exit {rc}: {tail(out)[:260]}")

    # EQ: the kit's collector on the session with the record masked beforehand
    pre = raw.replace(HOME.encode() + b"/.local/state/fwgate/aifoundry2-c0.jsonl", b"~/.local/state/fwgate/aifoundry2-c0.jsonl", 1)
    boxq = make_box("EQ", root, sid, edits=[(REC, lambda b: pre)])
    rbq, labq = make_rb("EQ", rbsrc), make_lab("EQ")
    rc, out = collect("collect_e209.py", boxq, sid, rbq, labq)
    ddq = os.path.join(labq, "docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2")
    ok = rc == 0 and R1_DD is not None and os.path.isdir(ddq)
    words = [f"exit {rc}"]
    if ok:
        tq, t1 = tree(ddq), tree(R1_DD)
        diff = sorted(k for k in set(tq) | set(t1) if tq.get(k) != t1.get(k))
        mq = open(os.path.join(ddq, "session/MANIFEST.sha256")).read().splitlines()
        m1 = open(os.path.join(R1_DD, "session/MANIFEST.sha256")).read().splitlines()
        mdiff = [i + 1 for i in range(len(m1)) if i >= len(mq) or mq[i] != m1[i]]
        sq = open(os.path.join(ddq, "SHA256SUMS")).read().splitlines()
        s1 = open(os.path.join(R1_DD, "SHA256SUMS")).read().splitlines()
        sdiff = [s1[i].split("  ", 1)[1] for i in range(len(s1)) if i >= len(sq) or sq[i] != s1[i]]
        ckd = [k for k in diff if k.startswith("checks-e209")]
        ok = (set(diff) - set(ckd) == {"session/MANIFEST.sha256", "SHA256SUMS"} and len(mdiff) == 1
              and set(sdiff) - set(ckd) == {"session/MANIFEST.sha256"})
        words += [f"files differing from R1's data directory: {diff}", f"MANIFEST lines differing: {mdiff}",
                  f"SHA256SUMS lines differing: {sdiff}", f"the checker's outputs differing (its own run time, if any): {ckd or 'none'}"]
    verdict("EQ", ok, "; ".join(words))

    # C1: R1's RB_OUT again; C2: a bad copy name
    before = tree(lab1)
    rc, out = collect("collect_e209_n1.py", root, sid, rb1, lab1)
    verdict("C1", rc == 10 and "RB_OUT/copy-n1 exists already" in out and tree(lab1) == before, f"exit {rc}: {tail(out)[:200]}")
    rbc, labc = make_rb("C2", rbsrc), make_lab("C2")
    rc, out = collect("collect_e209_n1.py", root, sid, rbc, labc, ["--copy-name", "bad/name"])
    verdict("C2", rc == 10 and "--copy-name" in out and not os.path.exists(os.path.join(rbc, "bad")), f"exit {rc}: {tail(out)[:200]}")

    # P2: no home in the record's ledger path (a desk ledger folder)
    desk_line = raw.replace(HOME.encode() + b"/.local/state/fwgate/", b"desk-ledger/", 1)
    boxp = make_box("P2", root, sid, edits=[(REC, lambda b: desk_line)])
    rbp, labp = make_rb("P2", rbsrc), make_lab("P2")
    rc, out = collect("collect_e209_n1.py", boxp, sid, rbp, labp)
    ddp = os.path.join(labp, "docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2")
    ok = rc == 0 and "no line to mask" in out and os.path.exists(os.path.join(ddp, "session", REC)) \
        and sha(os.path.join(ddp, "session", REC)) == shab(desk_line)
    verdict("P2", ok, f"exit {rc}: {[x for x in out.splitlines() if x.startswith('THE MASK')]}; the record committed at its own bytes: "
                      f"{ok}")

    # F1-F10: each must stop with 16 and write nothing in its lab
    hb = HOME.encode()
    lines = raw.split(b"\n")
    l33 = lines[32]
    l34 = lines[33]
    other_home = HROOT + b"someone-else"
    fcases = [
        ("F1", "the home in another line of the record too", dict(edits=[(REC, lambda b: b.replace(l33, b' "fwgate_sha256": "' + hb + b'/x",', 1))]), "first/fwgate-aifoundry2-c0-20261117-103044.json: the login name"),
        ("F2", "the login alone in fwgate's stderr", dict(edits=[(REC.replace(".json", ".stderr"), lambda b: b + b"desk: " + LOGIN.encode() + b"\n")]), "first/fwgate-aifoundry2-c0-20261117-103044.stderr: the login name"),
        ("F3", "another user's home folder in runner.out", dict(edits=[("runner.out", lambda b: b + other_home + b"/x\n")]), "runner.out: a home path"),
        ("F4", "the box root's path in runner.out (under the home here, so the login is named first)", dict(edits=[("runner.out", lambda b: b + b"BOXROOT/x\n")]), "runner.out: the"),
        ("F5", "the ledger line with another home", dict(edits=[(REC, lambda b: b.replace(l34, l34.replace(hb, other_home), 1))]), "first/fwgate-aifoundry2-c0-20261117-103044.json: a home path"),
        ("F6", "the ledger line of another card's ledger", dict(edits=[(REC, lambda b: b.replace(l34, l34.replace(b"aifoundry2-c0.jsonl", b"aifoundry2-c1.jsonl"), 1))]), "first/fwgate-aifoundry2-c0-20261117-103044.json: the login name"),
        ("F7", "the ledger line's text in runner.out (not a record)", dict(edits=[("runner.out", lambda b: b + l34 + b"\n")]), "runner.out: the login name"),
        ("F8", "two ledger lines in the record", dict(edits=[(REC, lambda b: b.replace(l34, l34 + b"\n" + l34, 1))]), "THE MASK: 2 ledger lines"),
        ("F9", "the home inside a .gz file of the session", dict(adds=[("desk-extra.jsonl.gz", gzip.compress(b'{"desk": "' + hb + b'/x"}\n', mtime=0))]), "desk-extra.jsonl.gz: the login name"),
        ("F10", "the record under another file name", dict(renames=[(REC, "first/fwgate-copy.json")]), "first/fwgate-copy.json: the login name"),
    ]
    for case, what, kw, want in fcases:
        boxf = make_box(case, root, sid, **{k: v for k, v in kw.items()})
        if case == "F4":   # the stand-in box root's own real path, written into runner.out
            p = os.path.join(boxf, "sessions", sid, "runner.out")
            data = open(p, "rb").read()
            open(p, "wb").write(data.replace(b"BOXROOT", os.path.realpath(boxf).encode()))
        rbf, labf = make_rb(case, rbsrc), make_lab(case)
        rc, out = collect("collect_e209_n1.py", boxf, sid, rbf, labf)
        nothing = not os.path.exists(os.path.join(labf, "docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2"))
        edited = tree(os.path.join(boxf, "sessions", sid)) != box_before
        verdict(case, rc == 16 and want in out and nothing and edited, f"{what}: the stand-in differs from the real session: {edited}; "
                f"exit {rc}, nothing written in its lab: {nothing}: {tail(out)[:240]}")

    # M0-M7: step 13's manifest read
    if R1_DD:
        s1 = os.path.join(R1_DD, "session")
        rc, out = run(["sha256sum", "-c", "--quiet", "MANIFEST.sha256"], cwd=s1)
        verdict("M0", rc != 0 and REC in out and out.count("FAILED") >= 1 and len([x for x in out.splitlines() if ": FAILED" in x]) == 1,
                f"the kit's read: rc {rc}: {tail(out, 2)[:200]}")
        rc, out = run([PY, "-I", "-B", os.path.join(E, "collect_e209_n1.py"), "--manifest-check", s1])
        verdict("M1", rc == 0 and "(1 by THE MASK" in out, f"exit {rc}: {tail(out)[:300]}")
        rc, out = run([PY, "-I", "-B", os.path.join(E, "collect_e209_n1.py"), "--manifest-check", os.path.join(rb1, "copy-n1", sid)])
        verdict("M6", rc == 0 and "(0 by THE MASK" in out, f"the raw copy-back: exit {rc}: {tail(out)[:200]}")

        def mcase(case, what, fn):
            d = os.path.join(WORK, "mcheck", case)
            shutil.copytree(s1, d)
            fn(d)
            rc, out = run([PY, "-I", "-B", os.path.join(E, "collect_e209_n1.py"), "--manifest-check", d])
            verdict(case, rc == 10 and "MANIFEST CHECK FAILED" in out, f"{what}: exit {rc}: {tail(out)[:240]}")

        def app(p, b):
            open(p, "ab").write(b)

        mcase("M2", "another file changed", lambda d: app(os.path.join(d, "session.log"), b"\n"))
        mcase("M3", "the record changed in a second line", lambda d: open(os.path.join(d, REC), "wb").write(
            R1_COM.replace(b'"locks": [', b'"locks" : [', 1)))
        mcase("M4", "'~' read as another home", lambda d: open(os.path.join(d, REC), "wb").write(
            R1_COM.replace(b'"~/.local', b'"' + other_home + b'/.local', 1)))
        mcase("M5", "a listed file missing", lambda d: os.remove(os.path.join(d, "session.log")))

        def m7(d):
            n = os.path.join(d, "first", "fwgate-copy.json")
            os.rename(os.path.join(d, REC), n)
            txt = open(os.path.join(d, "MANIFEST.sha256")).read().replace(REC, "first/fwgate-copy.json")
            open(os.path.join(d, "MANIFEST.sha256"), "w").write(txt)
        mcase("M7", "the masked form under another file name", m7)
    else:
        for c in ("M0", "M1", "M6", "M2", "M3", "M4", "M5", "M7"):
            verdict(c, False, "NOT RUN (R1 failed)")

    # S1-S4: step 11's script
    s22 = os.path.join(E, "rb", "s22_collect_e209_n1.sh")
    flag = os.path.join(WORK, "standin-flag", "quiet-desk-aifoundry2")
    os.makedirs(os.path.dirname(flag))
    open(flag, "w").write("card-e209 2026-11-17 (desk test stand-in)\n")
    rbs, labs = make_rb("S1", rbsrc, with_copy=True), make_lab("S1")
    env = {k: v for k, v in os.environ.items() if not k.startswith("RB_")}
    env.update(RB_OUT=rbs, E209_ROOT=root, RB_QUIET=flag, RB_LANE="card-e209", RB_DESKTEST="1", RB_DATA_LAB=labs, RB_W=os.path.join(WORK, "no-w"))
    rc, out = run(["bash", s22], env=env)
    for ln in out.strip().splitlines():
        say(f"   S1 | {ln[:300]}")
    dds = os.path.join(labs, "docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2")
    ok = rc == 0 and os.path.isdir(dds) and not os.path.exists(flag) and os.path.exists(os.path.join(rbs, "collect-n1.txt")) \
        and open(os.path.join(rbs, "e209-datadir.txt")).read().strip() == "DD=docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2"
    words = [f"exit {rc}", f"the stand-in flag lowered: {not os.path.exists(flag)}"]
    if ok and R1_DD:
        ts_, t1 = tree(dds), tree(R1_DD)
        diff = sorted(k for k in set(ts_) | set(t1) if ts_.get(k) != t1.get(k))
        ok = set(diff) <= {"checks-e209.json", "checks-e209.txt", "SHA256SUMS"}
        words.append(f"files differing from R1's data directory: {diff or 'none'}")
    verdict("S1", ok, "; ".join(words))

    def standin_w(name, shown):
        w = os.path.join(WORK, "w", name)
        os.makedirs(w)
        open(os.path.join(w, "onelab.sh"), "w").write("#!/bin/bash\n# desk test stand-in for the round's onelab.sh, 'show' only\n"
                                                      f"case \"${{1:-show}}\" in show) {''.join(f'echo \"  {x}\"; ' for x in shown)}echo \"(end)\";; "
                                                      "*) exit 2;; esac\n")
        return w
    open(flag, "w").write("card-e209 2026-11-17 (desk test stand-in)\n")
    for case, shown, ol, want, extra in (("S2", [], None, "THE ONE-LAB RULE: card-e209 is not in its collect span", None),
                                         ("S3", ["collect-card-e209"], "collect-e209", "THE ONE-LAB RULE: collect-e209 is not in its collect span", None),
                                         ("S4", ["collect-collect-e209"], "collect-e209", "THE ONE-LAB RULE: collect-collect-e209 held", "bad/name")):
        rbx = make_rb(case, rbsrc)
        env = {k: v for k, v in os.environ.items() if not k.startswith("RB_")}
        env.update(RB_OUT=rbx, E209_ROOT=root, RB_QUIET=flag, RB_LANE="card-e209", RB_W=standin_w(case, shown))
        if ol:
            env["RB_ONELAB_LANE"] = ol
        if extra:
            env["RB_COPY_NAME"] = extra
        rc, out = run(["bash", s22], env=env)
        ok = rc == 10 and want in out and not any(x.startswith("copy") for x in os.listdir(rbx))
        if case == "S4":
            ok = ok and "--copy-name 'bad/name'" in out
        verdict(case, ok, f"exit {rc}: {' | '.join(x for x in out.strip().splitlines() if 'ONE-LAB' in x or 'COLLECT' in x)[:300]}")
    if os.path.exists(flag):
        os.remove(flag)

    # W1-W3: step 13's script in a stand-in repository
    if R1_COM is not None:
        mr = os.path.join(WORK, "minirepo")
        for rel in ("tools/claims-v3/e209/rb/rb_e209.sh", "tools/claims-v3/e209/rb/s24_score_e209.sh", "tools/claims-v3/e209/rb/s24_score_e209_n1.sh",
                    "tools/claims-v3/e209/collect_e209_n1.py", "tools/claims-v3/e208/proposal/src/reduce_mms.py",
                    "tools/claims-v3/e208/proposal/src/mms_common.py"):
            os.makedirs(os.path.dirname(os.path.join(mr, rel)), exist_ok=True)
            shutil.copy2(os.path.join(REPO, rel), os.path.join(mr, rel))
        for case, com in (("w1", R1_COM), ("w3", R1_COM.replace(b'"locks": [', b'"locks" : [', 1))):
            d = os.path.join(mr, f"docs/reports/data/2026-11-17-e209-desk-standin-{case}")
            os.makedirs(os.path.join(d, "session", "first"))
            open(os.path.join(d, "session", REC), "wb").write(com)
            open(os.path.join(d, "session", "MANIFEST.sha256"), "w").write(f"{man0[REC]}  {REC}\n")
            open(os.path.join(d, "SHA256SUMS"), "w").write("".join(f"{h}  {r}\n" for r, h in sorted(tree(d).items()) if r != "SHA256SUMS"))
        g = ["git", "-C", mr, "-c", "user.name=desk", "-c", "user.email=desk@localhost", "-c", "core.hooksPath=/dev/null"]
        r1 = run(["git", "init", "-q", mr])[0]
        r2 = run(g + ["add", "-A"])[0]
        r3 = run(g + ["commit", "-q", "-m", "desk stand-in (never pushed)"])[0]
        say(f"   the stand-in repository: git init rc {r1}, add rc {r2}, commit rc {r3}")
        for case, script, dd_, want_rc, want, never in (
                ("W1", "s24_score_e209_n1.sh", "w1", 14, "MANIFEST CHECK: 1 of 1 manifest lines OK (1 by THE MASK", None),
                ("W2", "s24_score_e209.sh", "w1", 10, "the committed session does not read its manifest OK", "reduce_mms.py rc"),
                ("W3", "s24_score_e209_n1.sh", "w3", 10, "the committed session does not read its manifest OK, but for THE MASK", "reduce_mms.py rc")):
            rbw = os.path.join(WORK, "rb", case)
            os.makedirs(rbw)
            open(os.path.join(rbw, "e209-datadir.txt"), "w").write(f"DD=docs/reports/data/2026-11-17-e209-desk-standin-{dd_}\n")
            env = {k: v for k, v in os.environ.items() if not k.startswith("RB_")}
            env.update(RB_OUT=rbw)
            rc, out = run(["bash", os.path.join(mr, "tools/claims-v3/e209/rb", script)], env=env)
            ok = rc == want_rc and want in out and (never is None or never not in out)
            if case == "W1":
                ok = ok and "reduce_mms.py rc" in out
            verdict(case, ok, f"exit {rc}: {' | '.join(x for x in out.strip().splitlines() if 'MANIFEST' in x or 'reduce_mms' in x or 'exit' in x)[:340]}")
    else:
        for c in ("W1", "W2", "W3"):
            verdict(c, False, "NOT RUN (R1 failed)")

    # nothing written where it must not be
    same_rb, same_box = tree(rbsrc) == rb_before, tree(sd) == box_before
    st = run(["git", "-C", REPO, "status", "--porcelain", "--untracked-files=all", "--", "docs/reports/data"])[1].strip()
    verdict("Z", same_rb and same_box and not st, f"the card lane's RB_OUT unchanged: {same_rb}; the box root's session unchanged: {same_box}; "
                                                  f"no data path written in the repo it runs from: {not st}")
    k = sum(1 for _, ok in RESULTS if ok)
    say(f"DESKTEST-N1-E209 {k} of {len(RESULTS)} PASS" if k == len(RESULTS) else f"DESKTEST-N1-E209 {k} of {len(RESULTS)} PASS (FAILED: "
        f"{[c for c, ok in RESULTS if not ok]})")
    return 0 if k == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
