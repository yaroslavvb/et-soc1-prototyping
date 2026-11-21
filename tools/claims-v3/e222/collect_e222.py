#!/usr/bin/env python3
"""E222's collection at the desk (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum; E218's landed kit 5582edfc ported, the kit that ran E218 FULL on aifoundry3 card 0 at 03:11-03:56 PST that day): the desk half of steps 11 and 12, after the
copy-back, E215 arm A's collector (tools/claims-v3/e215/collect_e215.py, landed in 8bde0182, which made E215 arm A's committed data directory
on Thu 19 Nov 2026, 8355db15) for E222's one arm's data directory, line for line: E202's gate-stop record, a scrub that masks EVERY form of the box's home it
is given, and a scrub check the runbook runs on the dry pass's copy BEFORE the session (E209's lesson: its collection's scrub refused a real
record after the session, a home path written by a tool its desk tests had run only in desk mode, and the day was spent). Python's own modules
only.

    /usr/bin/python3 -B tools/claims-v3/e222/collect_e222.py copy-check COPY
        COPY-BACK EXACT: every file of the box's MANIFEST.sha256 is in COPY at its sha256, and COPY holds nothing else but MANIFEST.sha256
        itself, runner.out and runner.rc (the wrapper's two files); else exit 3
    /usr/bin/python3 -B tools/claims-v3/e222/collect_e222.py scrub-check COPY HOMESFILE LOGINFILE
        THE SCRUB on a private copy of COPY (made under the system's temporary folder, removed after; COPY is never written): "SCRUB-CHECK CLEAN:
        <n> files, <m> held a home path or the login and were masked" (exit 0), or "SCRUB-CHECK LEFT: <files>" (exit 3): the files the scrub
        could not clean. Step 8 runs it on the dry pass's copy-back (the box's own paths in its argv, logs and records) before the session.
    /usr/bin/python3 -B tools/claims-v3/e222/collect_e222.py data DAY ARM COPY HOMESFILE LOGINFILE [--neverrun DIR]
        DAY the window's day (YYYY-MM-DD); ARM A (aifoundry3 card 0, E222's one arm). THE DIRECTORY: docs/reports/data/<DAY>-e222-blind-
        matmul-aifoundry3/ when at least one run started (queue.json); else the session stopped before any run (a gate, a HUNG smoke process, a
        crash) and its record goes to docs/reports/gate-stops/<DAY>-e222-blind-matmul-T<T0>-aifoundry3/ (E202's form), never under
        docs/reports/data/ (step 2 reads every docs/reports/data/*e222*-aifoundry3 path as an E222 datum). Refused if it exists.
  HOMESFILE holds the box's home path in every form step 11 read on the box, one a line ($HOME, the user database's home, the home's physical
  path; the same path once). LOGINFILE holds our own box login (the look writes it).
  1. the copy checked again (COPY-BACK EXACT), then copied whole into <dir>/session/;
  2. THE SCRUB: every home path of HOMESFILE (the longest first) becomes "~", and OUR OWN BOX LOGIN becomes "<login>", in every text and .gz
     file; then ANOTHER LOGIN'S et-who HOLDER LINE (a line whose first field is a /dev/et* node or a lock:<name>, et-who's form, the form the
     runner's holder rule reads: its second field the login) keeps its node, pid and time, its login becomes "<another-login>" and its command
     column is dropped (fix-e213, verify-e213's finding 2: the runner writes et-who's raw lines under reads/, and a holder line of another login
     there is masked, never committed); then no file may hold a /home/ path, any of those homes, the login, or a holder line naming any login but
     "<login>" or "<another-login>" (exit 3);
  3. a data directory only: the reducer (reduce_e222.py, as committed) over the session: <dir>/data-e222.json (the frozen scorer's input) and
     <dir>/reduce-e222.txt;
  3n. with --neverrun DIR (step 6n's folder, RB_OUT/e222-neverrun-dir-<arm>.txt names it): its report and judgement, DIR/neverrun-e222.txt,
     DIR/neverrun-e222.json (the registration's scanner's report), DIR/judge-e222-<arm>.txt, DIR/judge-e222-<arm>.json and DIR/labels-e222-<arm>.json
     (desk/neverrun_card_e222.py's), copied in as neverrun-e222-card.txt, neverrun-e222-card.json, judge-e222-card.txt, judge-e222-card.json and
     labels-e222.json, scrubbed like the rest; refused (exit 3) if one is missing;
  4. <dir>/SHA256SUMS (paths beside it, as the lab's data lists).
The scorer is NOT run here: rb/s24_score_e222.sh runs score_e222.py on the committed data, after the data commit. It prints the directory on its
last line ("COLLECTED <dir>" or "COLLECTED-GATE-STOP <dir>"). Exit 0 collected, 3 a gate, 2 usage. RB_DESKTEST=1 with --outside <dir> lets the
desk tests write the directory in their scratch (never on the card day). SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e222_common as C  # noqa: E402

TEXT = (".json", ".txt", ".log", ".err", ".out", ".rc", ".sha256", ".jsonl")
EXTRA_OK = {"MANIFEST.sha256", "runner.rc", "runner.out"}
NR_FILES = (("neverrun-e222.txt", "neverrun-e222-card.txt"), ("neverrun-e222.json", "neverrun-e222-card.json"),
            ("judge-e222-{arm}.txt", "judge-e222-card.txt"), ("judge-e222-{arm}.json", "judge-e222-card.json"),
            ("labels-e222-{arm}.json", "labels-e222.json"))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_back_exact(copy):
    man = os.path.join(copy, "MANIFEST.sha256")
    if not os.path.exists(man):
        return ["no MANIFEST.sha256"]
    want = {}
    for ln in open(man):
        if ln.strip():
            h, p = ln.rstrip("\n").split("  ", 1)
            want[p] = h
    have = set()
    for dp, dn, fn in os.walk(copy):
        for n in fn:
            have.add(os.path.relpath(os.path.join(dp, n), copy))
    bad = [f"missing {p}" for p in want if p not in have]
    bad += [f"differs {p}" for p in want if p in have and sha(os.path.join(copy, p)) != want[p]]
    bad += [f"not in the manifest: {p}" for p in sorted(have - set(want) - EXTRA_OK)]
    return bad


def login_rx(login):
    return re.compile(rb"(?<![A-Za-z0-9_.-])" + re.escape(login.encode()) + rb"(?![A-Za-z0-9_-])")


# fix-e213 (verify-e213's finding 2): et-who's holder lines, "<node or lock:name>  <login>  <pid>  <time>  <command ...>" (the runner's holder rule
# reads the same lines: a first field starting /dev/et or lock:, more than one field, the second the login)
HOLDER_RX = re.compile(rb"^([ \t]*)((?:/dev/et|lock:)[^ \t]*)([ \t]+)([^ \t]+)(.*)$")
OURS, OTHER = b"<login>", b"<another-login>"


def mask_holders(data):
    """Another login's holder line: its node kept, its login "<another-login>", its pid and time kept when they read as such, its command
    dropped; our own lines ("<login>" by then) and lines already masked are left as they are."""
    out, changed = [], False
    for ln in data.split(b"\n"):
        m = HOLDER_RX.match(ln)
        if m and m.group(4) not in (OURS, OTHER):
            rest = m.group(5).split()
            keep = (b"  " + rest[0] + b"  " + rest[1]) if len(rest) >= 2 and rest[0].isdigit() else b""
            ln = m.group(1) + m.group(2) + m.group(3) + OTHER + keep
            changed = True
        out.append(ln)
    return b"\n".join(out) if changed else data


def holder_left(body):
    """a holder line still naming a login that is neither ours nor masked (the scrub refuses it, never silently)"""
    for ln in body.split(b"\n"):
        m = HOLDER_RX.match(ln)
        if m and m.group(4) not in (OURS, OTHER):
            return True
    return False


def scrub_bytes(data, homes, login):
    new = data
    for h in sorted(homes, key=len, reverse=True):       # the longest first: a physical path that holds another home is masked whole
        new = new.replace(h.encode(), b"~")
    if login:
        new = login_rx(login).sub(b"<login>", new)
    return mask_holders(new)


def scrub_file(p, homes, login):
    """The scrub of one file in place (a text or .gz file; any other file is read as it is): its bytes after the scrub."""
    raw = open(p, "rb").read()
    gz = p.endswith(".gz")
    data = gzip.decompress(raw) if gz else raw
    if not gz and not (p.endswith(TEXT) or os.path.basename(p) == "STOP" or os.path.basename(p).startswith("STOPTEST")):
        return data
    new = scrub_bytes(data, homes, login)
    if new != data:
        if gz:
            with gzip.open(p, "wb") as f:
                f.write(new)
        else:
            open(p, "wb").write(new)
    return new


def left_over(body, homes, login):
    return b"/home/" in body or any(h.encode() in body for h in homes) or login_rx(login).search(body) is not None or holder_left(body)


def read_homes(hf):
    """The box's home in every form step 11 read (one a line, absolute, distinct); [] when the file gives none."""
    try:
        lines = [ln.strip().rstrip("/") for ln in open(hf) if ln.strip()]
    except OSError:
        return []
    out = []
    for h in lines:
        if not h.startswith("/") or len(h) < 6:
            return []
        if h not in out:
            out.append(h)
    return out


def read_login(lf):
    try:
        login = open(lf).read().strip()
    except OSError:
        login = ""
    return login if re.fullmatch(r"[a-z_][a-z0-9_-]{1,31}", login) else ""


def scrub_tree(root, homes, login):
    """(files, masked, left): THE SCRUB over every file under root, in place."""
    n = masked = 0
    left = []
    for dp, dn, fn in os.walk(root):
        dn.sort()
        for name in sorted(fn):
            p = os.path.join(dp, name)
            before = sha(p)
            body = scrub_file(p, homes, login)
            n += 1
            masked += 1 if sha(p) != before else 0
            if left_over(body, homes, login):
                left.append(os.path.relpath(p, root))
    return n, masked, left


def main(argv):
    if len(argv) >= 2 and argv[0] == "copy-check":
        bad = copy_back_exact(os.path.abspath(argv[1]))
        if bad:
            print("COPY-BACK NOT EXACT: " + "; ".join(bad[:10]))
            return 3
        print("COPY-BACK EXACT: every file of the box's MANIFEST.sha256 at its sha256, nothing else but runner.out and runner.rc")
        return 0
    if len(argv) == 4 and argv[0] == "scrub-check":
        src, homes, login = os.path.abspath(argv[1]), read_homes(argv[2]), read_login(argv[3])
        if not os.path.isdir(src) or not homes or not login:
            print("SCRUB-CHECK REFUSED: no folder, no home or no login (the homes file and the look's login file)")
            return 2
        with tempfile.TemporaryDirectory(prefix="e222-scrubcheck-") as td:
            dst = os.path.join(td, "copy")
            shutil.copytree(src, dst, symlinks=True)
            n, masked, left = scrub_tree(dst, homes, login)
        if left:
            print(f"SCRUB-CHECK LEFT: {len(left)} of {n} files still hold a /home/ path, a home, the login or another login's holder line after the "
                  f"scrub: " + ", ".join(left[:10]))
            return 3
        print(f"SCRUB-CHECK CLEAN: {n} files, {masked} held a home path or the login and were masked; none left (another login's holder lines "
              f"masked as <another-login>, their commands dropped)")
        return 0
    if len(argv) < 6 or argv[0] != "data":
        print(__doc__)
        return 2
    day, arm, copy, hf, lf = argv[1], argv[2], os.path.abspath(argv[3]), argv[4], argv[5]
    rest = argv[6:]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day) or arm not in C.ARMS:
        print(f"COLLECT-REFUSED: unreadable day {day!r} or arm {arm!r}")
        return 2
    outside = nrdir = None
    while rest:
        if rest[0] == "--outside" and len(rest) >= 2:
            if os.environ.get("RB_DESKTEST") != "1":
                print("COLLECT-REFUSED: --outside is the desk tests' own (RB_DESKTEST=1)")
                return 2
            outside = os.path.abspath(rest[1])
            rest = rest[2:]
        elif rest[0] == "--neverrun" and len(rest) >= 2:
            nrdir = os.path.abspath(rest[1])
            rest = rest[2:]
        else:
            print(f"COLLECT-REFUSED: unreadable arguments {rest!r}")
            return 2
    nrfiles = []
    if nrdir:
        nrfiles = [(os.path.join(nrdir, s.format(arm=arm)), d) for s, d in NR_FILES]
        miss = [s for s, _ in nrfiles if not os.path.isfile(s)]
        if miss:
            print(f"COLLECT-REFUSED: step 6n's report is not whole in {nrdir} (missing {len(miss)} of {len(nrfiles)} files)")
            return 3
    homes = read_homes(hf)
    if not homes:
        print(f"COLLECT-REFUSED: the homes file {hf!r} gives no absolute home path (step 11 writes RB_OUT/box-home-<arm>.txt)")
        return 2
    login = read_login(lf)
    if not login:
        print("COLLECT-REFUSED: the login file gives no login (the look writes it: RB_OUT/box-login-<box>.txt)")
        return 2
    bad = copy_back_exact(copy)
    if bad:
        print("COPY-BACK NOT EXACT: " + "; ".join(bad[:10]))
        return 3
    print("COPY-BACK EXACT: every file of the box's MANIFEST.sha256 at its sha256")
    try:
        q = json.load(open(os.path.join(copy, "queue.json")))
    except (OSError, ValueError):
        q = {}
    ran = any(x.get("ran") for x in q.get("queue", []))
    m = re.search(r"T(\d+)-" + arm + "$", os.path.basename(copy.rstrip("/")))
    t0 = m.group(1) if m else str(q.get("t0", "0"))
    box = C.ARMS[arm]["data_dir"]
    rel = (f"docs/reports/data/{day}-e222-blind-matmul-{box}" if ran else f"docs/reports/gate-stops/{day}-e222-blind-matmul-T{t0}-{box}")
    dabs = os.path.join(outside, os.path.basename(rel)) if outside else os.path.join(REPO, rel)
    if os.path.exists(dabs):
        print(f"COLLECT-REFUSED: {rel} exists already (never merge into an earlier copy)")
        return 3
    os.makedirs(dabs)
    dst = os.path.join(dabs, "session")
    shutil.copytree(copy, dst)
    n, masked, left = scrub_tree(dst, homes, login)
    left = [os.path.join("session", x) for x in left]
    if left:
        print(f"SCRUB FAILED: a /home/ path, a home, the box login or another login's holder line is left in " + ", ".join(left[:10]))
        return 3
    print(f"scrubbed: {len(homes)} form(s) of the box home -> '~', the box login -> '<login>', another login's holder lines -> '<another-login>' "
          f"without their commands ({masked} of {n} files masked), no /home/ path left")
    for src, name in nrfiles:              # step 6n's report and judgement (3n), scrubbed like the rest
        dst2 = os.path.join(dabs, name)
        shutil.copyfile(src, dst2)
        body = scrub_file(dst2, homes, login)
        if left_over(body, homes, login):
            print(f"SCRUB FAILED: a /home/ path, a home or the box login is left in {name}")
            return 3
    if nrfiles:
        print("step 6n's report copied in: " + ", ".join(d for _, d in nrfiles))
    if ran:
        cmd = [sys.executable, "-I", "-B", os.path.join(HERE, "reduce_e222.py"), "--arm", f"{arm}={dst}",
               "--out", os.path.join(dabs, "data-e222.json"), "--txt", os.path.join(dabs, "reduce-e222.txt")]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(os.path.join(dabs, "data-e222.json")):
            print(f"REDUCER FAILED: rc {r.returncode}: {r.stdout[-300:]} {r.stderr[-300:]}")
            return 3
        for p in ("data-e222.json", "reduce-e222.txt"):
            body = scrub_file(os.path.join(dabs, p), homes, login)
            if left_over(body, homes, login):
                print(f"SCRUB FAILED: a /home/ path, a home or the box login is left in {p}")
                return 3
    rows = []
    for dp, dn, fn in os.walk(dabs):
        dn.sort()
        for name in sorted(fn):
            p = os.path.join(dp, name)
            r2 = os.path.relpath(p, dabs)
            if r2 != "SHA256SUMS":
                rows.append(f"{sha(p)}  {r2}")
    with open(os.path.join(dabs, "SHA256SUMS"), "w") as f:
        f.write("\n".join(sorted(rows, key=lambda x: x[66:])) + "\n")
    print(f"{len(rows)} files in SHA256SUMS; the scrub clean" + ("; data-e222.json written" if ran else "; no run started: a gate stop's record"))
    print(("COLLECTED " if ran else "COLLECTED-GATE-STOP ") + (dabs if outside else rel))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
