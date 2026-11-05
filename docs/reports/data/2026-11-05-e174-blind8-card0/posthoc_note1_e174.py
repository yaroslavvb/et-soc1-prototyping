#!/usr/bin/env python3
"""E174's data README, dated note 1 (Thu 5 Nov 2026, after E174's and E172's data): the post hoc desk checks that note cites, for the four
faults the data verifier of the pool-8 card day's aifoundry1 lane found. Post hoc and read only: nothing in the repo is written, no device,
no box and no network is reached. Every repo file it reads is a committed blob at HEAD (git show, git archive), never the work tree, but for
the kit modules it imports (each checked equal to its HEAD blob first). Two optional arguments name the card day's own records on the desk,
which are not in the repo: the runbook's directory (its log and call outputs, printed with every desk path masked) and the pulled copy of
E174 (gitignored, for the collector's own check-of-C outputs).

    /usr/bin/python3 -B docs/reports/data/2026-11-05-e174-blind8-card0/posthoc_note1_e174.py --work <a new directory outside the repo> \\
        [--rb-out <the card day's runbook directory>] [--raw build/e174-raw] [--no-replay] > posthoc-note1-e174.txt

 1. the three commits of the lane and their times (committer dates; the push times where this clone's reflog holds them), and the lab's main
    at D1's copy and at E174's launch;
 2. with --rb-out: the box's own records of D1, from the first box check to the second (desk paths masked);
 3. D1's inputs: frozen-sha256-e174.json's 32 files, each blob's sha256 at the list's commit (c8064454), at D1's (0a14c7bb) and at HEAD
    against its frozen value, and any commit touching one since c8064454; each file's class: run_e174.py's BOX_FROZEN, in note 1's sync list
    (parsed from box/step_e174_v2.sh, the list step_e174_v3.sh hands on), or outside it, and with --rb-out whether the box had it;
 4. the checks of C as committed against the hashes results.json records, and with --raw the collector's own outputs and their fate;
 5. unless --no-replay: the registered score replayed from this directory as committed, by dated note 1's reproduce command;
 6. the login check: scrub_etwho_e164.py --check, unchanged, in EVERY directory of E174's, E172's and E170's committed data directories
    (each .gz decompressed and the binary tiles left out, in a copy under --work), and every box home path counted by login (another login
    is counted, never named).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import glob
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
D174 = "docs/reports/data/2026-11-05-e174-blind8-card0"
D172 = "docs/reports/data/2026-11-05-e172-blind8-card1"
D170 = "docs/reports/data/2026-11-04-e170-blind7-card0"
KIT = "tools/claims-v3/e174"
SCRUB = "tools/claims-v3/e164/scrub_etwho_e164.py"
LIST_COMMIT, D1_COMMIT = "c8064454", "0a14c7bb"
DATA_COMMITS = (("0a14c7bb", "D1's dated note 3"), ("e5206b5b", "E174's data"), ("b3255af1", "E172's data and P8-KA pooled"))
BOX_HOME = re.compile(rb"/" + rb"home/([A-Za-z_][\w.-]*)")      # built in two parts, so this file carries no box path


def git(*a, binary=False):
    r = subprocess.run(["git", "-C", REPO, *a], capture_output=True)
    if r.returncode:
        return None
    return r.stdout if binary else r.stdout.decode()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def blob_sha(rev, path):
    b = git("show", f"{rev}:{path}", binary=True)
    return None if b is None else sha(b)


def extract(rev, path, dest):
    """git archive <rev> <path> unpacked under dest; returns dest/<path>"""
    b = git("archive", "--format=tar", rev, path, binary=True)
    with tarfile.open(fileobj=io.BytesIO(b)) as t:
        t.extractall(dest)
    return os.path.join(dest, path)


def head(title):
    print(f"\n== {title}")


# ------------------------------------------------------------------ 1. the commits
def sec_commits():
    head("1. the lane's commits, and the lab's main at D1's copy and at E174's launch")
    rl = git("reflog", "show", "--date=format:%Y-%m-%d %H:%M:%S %z", "refs/remotes/origin/main") or ""
    for c, what in DATA_COMMITS:
        when = git("log", "-1", "--format=%cd", "--date=format:%Y-%m-%d %H:%M:%S %z", c).strip()
        parent = git("log", "-1", "--format=%p", c).strip()
        st = [ln.split("\t")[0] for ln in git("show", "--name-status", "--format=", c).splitlines() if ln.strip()]
        push = [m.group(1) for ln in rl.splitlines() if ln.startswith(c) for m in [re.search(r"@\{([^}]+)\}: update by push", ln)] if m]
        print(f"  {c} ({what}): committed {when}, parent {parent}; {st.count('A')} file(s) added, {len(st) - st.count('A')} other; "
              f"pushed {push[0] if push else '(not in this clone reflog)'}")
    for label, t in (("D1's copy, 12:43:02", "2026-11-05 12:43:02 -0800"), ("E174's launch, 12:44:48", "2026-11-05 12:44:48 -0800")):
        m = git("log", "-1", "--first-parent", f"--before={t}", "--format=%h %cd", "--date=format:%H:%M:%S %z", "HEAD").strip()
        print(f"  the lab's main at {label}: {m}")
    between = git("log", "--first-parent", "--format=%h", "--since=2026-11-05 12:42:30 -0800", "--until=2026-11-05 12:44:48 -0800",
                  "HEAD").split()
    print(f"  commits on main between D1's commit and E174's launch: {len(between)} {' '.join(between)}")


# ------------------------------------------------------------------ 3. D1's inputs
def sync_list():
    src = git("show", f"HEAD:{KIT}/box/step_e174_v2.sh")
    m = re.search(r'rsync -a -c -R --exclude __pycache__ --exclude logs/ -e "\$RB_RSH" \\\n(.*?)\n\s*aifoundry1:nekko/', src, re.S)
    return [t for t in m.group(1).split() if t != "\\"]


def in_sync(p, sl):
    return any(p.startswith(s) if s.endswith("/") else p == s for s in sl)


def sec_d1(box_absent):
    head("3. D1's inputs: frozen-sha256-e174.json's files, from git")
    fz = json.loads(git("show", f"HEAD:{KIT}/frozen-sha256-e174.json"))["files"]
    for rel in ("e174_common.py", "run_e174.py"):
        same = blob_sha("HEAD", f"{KIT}/{rel}") == sha(open(os.path.join(REPO, KIT, rel), "rb").read())
        print(f"  {KIT}/{rel}: the work tree {'equals' if same else 'DIFFERS FROM'} HEAD's blob")
    sys.path.insert(0, os.path.join(REPO, KIT))
    import e174_common as C  # noqa: E402  (names only)
    box = (C.MAN_REL, C.C173.MANIFEST_REL, C.C173.POOL_SUMS_REL, "tools/claims-v3/e165/e165_common.py", "tools/claims-v3/e170/e170_common.py",
           C.GUARD_REL, C.C173.RUN_HPL_REL, C.C173.WATCHER_REL)
    src = git("show", f"HEAD:{KIT}/run_e174.py")
    line_ok = ('BOX_FROZEN = (C.MAN_REL, C.C173.MANIFEST_REL, C.C173.POOL_SUMS_REL, "tools/claims-v3/e165/e165_common.py", '
               '"tools/claims-v3/e170/e170_common.py",') in src and "C.GUARD_REL, C.C173.RUN_HPL_REL, C.C173.WATCHER_REL)" in src
    print(f"  run_e174.py's BOX_FROZEN line read as the 8 names below: {'yes' if line_ok else 'NO'}")
    sl = sync_list()
    print(f"  note 1's sync list (box/step_e174_v2.sh, sync): {len(sl)} entries")
    added = git("log", "--diff-filter=A", "--format=%h %cd", "--date=format:%Y-%m-%d %H:%M:%S %z", "--", f"{KIT}/frozen-sha256-e174.json").strip()
    print(f"  frozen-sha256-e174.json added in {added}; later commits to it: "
          f"{git('log', '--format=%h', f'{LIST_COMMIT}..HEAD', '--', f'{KIT}/frozen-sha256-e174.json').split() or 'none'}")
    bad, rows = 0, []
    for p, want in sorted(fz.items()):
        hs = [blob_sha(r, p) for r in (LIST_COMMIT, D1_COMMIT, "HEAD")]
        later = git("log", "--format=%h", f"{LIST_COMMIT}..HEAD", "--", p).split()
        ok = all(h == want for h in hs) and not later
        bad += not ok
        cls = "BOX_FROZEN, synced" if p in box and in_sync(p, sl) else ("BOX_FROZEN, NOT SYNCED" if p in box else
                                                                        ("synced" if in_sync(p, sl) else "outside the sync"))
        if box_absent is not None and not in_sync(p, sl):
            cls += ", absent on the box at 12:40:13" if p in box_absent else ", present on the box at 12:40:13"
        rows.append((p, cls, want[:12], "OK" if ok else "BAD", " ".join(later) or "-"))
    print("  path | class | frozen sha256 | at c8064454, 0a14c7bb and HEAD | commits since c8064454")
    for r in rows:
        print("  " + " | ".join(r))
    n_out = [r for r in rows if "outside" in r[1]]
    print(f"  RESULT: {len(rows) - bad} of {len(rows)} at their frozen sha256 at c8064454, 0a14c7bb and HEAD, none touched since; "
          f"{sum('BOX_FROZEN' in r[1] for r in rows)} BOX_FROZEN (all synced: {all('NOT SYNCED' not in r[1] for r in rows)}); "
          f"{len(rows) - len(n_out)} in the sync list; {len(n_out)} outside it")
    if box_absent is not None:
        print(f"  of those {len(n_out)}: {sum('absent' in r[1] for r in n_out)} absent on the box at 12:40:13 (D1 copied exactly these), "
              f"{sum('present' in r[1] for r in n_out)} present there; files the box named absent that are not outside the sync: "
              f"{sorted(set(box_absent) - {r[0] for r in n_out}) or 'none'}")
    ccf = C.CCHECK_FROZEN
    print(f"  Q139(k)'s run-time files (CCHECK_FROZEN): {len(ccf)}, all in the sync list: {all(in_sync(p, sl) for p in ccf)}, "
          f"all at their sha256 at HEAD: {all(blob_sha('HEAD', p) == h for p, h in ccf.items())}")
    return fz


# ------------------------------------------------------------------ 2. the box's own records of D1
def masker(rb_out):
    subs = [(os.path.realpath(rb_out), "<RB_OUT>"), (os.path.abspath(rb_out), "<RB_OUT>"), (REPO, "<lab clone>")]

    def m(s):
        for a, b in subs:
            s = s.replace(a, b)
        s = re.sub("/" + r"Users/[^\s'\"]+", "<desk path>", s)      # built in two parts, as BOX_HOME
        s = re.sub("/" + r"home/([A-Za-z_][\w.-]*)", lambda x: "~" if x.group(1) == OWNER else "/" + "home/<another-user>", s)
        return s
    return m


def sec_box(rb_out):
    head("2. the box's own records of D1 (the card day's runbook log and call outputs; desk paths masked)")
    m = masker(rb_out)
    log = open(os.path.join(rb_out, "runbook.log"), encoding="utf-8", errors="replace").read().splitlines()
    keep = [ln for ln in log if re.search(r"step=(e174_check_q142kg2|e174_frozen_read_k6|e174_d1_copy_q142kg2) ", ln)
            and "2026-11-05 12:38:41" <= ln[:19] <= "2026-11-05 12:44:22"]
    print(f"  runbook.log, {len(keep)} line(s), 12:38:41-12:44:22 PST:")
    for ln in keep:
        print("    " + m(ln))
    calls = os.path.join(rb_out, "calls")
    pats = [("the first box check (its job's output)", "123851-*-e174_check_q142kg2-1-*-wait-a1c0-check-e174.out"),
            ("the box's read-only frozen-input check, 12:40:13", "124012-*-e174_frozen_read_k6-1-e174_frozen_box.out"),
            ("D1: the 18 files' git status --short in the lab clone, 12:43:00", "124300-*-e174_d1_copy_q142kg2-1-local.out"),
            ("D1: the quiet read on the box, 12:43:01", "12430*-e174_d1_copy_q142kg2-2-*-quiet.out"),
            ("D1: the rsync's own output, 12:43:02", "12430*-e174_d1_copy_q142kg2-3-local.out"),
            ("the second box check (its job's output)", "124312-*-e174_check_q142kg2-1-*-wait-a1c0-check-e174.out")]
    absent = []
    for what, pat in pats:
        fs = sorted(glob.glob(os.path.join(calls, pat)))
        if len(fs) != 1:
            print(f"  {what}: {len(fs)} file(s) match, NOT READ")
            continue
        b = open(fs[0], "rb").read()
        print(f"  {what}: {os.path.basename(fs[0])}, {len(b)} bytes, sha256 {sha(b)[:16]}")
        for ln in b.decode("utf-8", "replace").splitlines():
            print("    | " + m(ln))
        if not b:
            print("    (empty)")
        if "frozen_box" in pat:
            absent = [x.group(1) for x in re.finditer(r"^\s+(\S+): sha256 None, frozen [0-9a-f]{64}$", b.decode(), re.M)]
    cl = os.path.join(rb_out, "a1c0-check-clean-e174.txt")
    if os.path.isfile(cl):
        print(f"  the step's clean mark (a1c0-check-clean-e174.txt): {m(open(cl).read().strip())}")
    print(f"  files the 12:40:13 read named absent (sha256 None): {len(absent)}")
    return absent


# ------------------------------------------------------------------ 4. the checks of C
def sec_ccheck(raw):
    head("4. the checks of C: as committed, against results.json's record")
    rj = json.loads(git("show", f"HEAD:{D174}/results.json"))
    rec = rj["ccheck_files"]
    top = [ln.split("\t")[1] for ln in git("ls-tree", "HEAD", f"{D174}/").splitlines()]
    cc = sorted(os.path.basename(p) for p in top if os.path.basename(p).startswith("ccheck-"))
    print(f"  committed beside results.json: {', '.join(cc)}")
    for name, want in rec.items():
        forms = []
        for suf in ("", ".gz"):
            b = git("show", f"HEAD:{D174}/{name}{suf}", binary=True)
            if b is not None:
                got = sha(gzip.decompress(b) if suf else b)
                forms.append(f"{name}{suf} ({len(b):,} bytes{', gunzipped' if suf else ''}: sha256 {got[:16]} "
                             f"{'= the record' if got == want else '!= the record ' + want[:16]})")
        print(f"  results.json records {name} {want[:16]}: committed as {'; '.join(forms) or 'NOTHING'}")
    if raw:
        rc = os.path.join(raw, "cc")
        print(f"  the collector's own outputs in the pulled copy's cc/ (gitignored, desk only): {len(os.listdir(rc))} files")
        for f in sorted(os.listdir(rc)):
            b = open(os.path.join(rc, f), "rb").read()
            fate = []
            for suf in ("", ".gz"):
                cb = git("show", f"HEAD:{D174}/{f}{suf}", binary=True)
                if cb is not None:
                    fate.append(f"committed as {f}{suf}" + (" (equal)" if (gzip.decompress(cb) if suf else cb) == b else " (DIFFERS)"))
            if f == "cclist.txt" and git("show", f"HEAD:{D174}/logs/cclist.txt", binary=True) == b:
                fate.append("committed as logs/cclist.txt (equal)")
            print(f"    {f}: {len(b):,} bytes, sha256 {sha(b)[:16]}; {'; '.join(fate) or 'not committed'}")
        p = os.path.join(rc, "ccheck-s1.json")
        if os.path.isfile(p):
            z = subprocess.run(["gzip", "-n", "-c", p], capture_output=True).stdout
            cz = git("show", f"HEAD:{D174}/ccheck-s1.json.gz", binary=True)
            print(f"  gzip -n -c of the pulled copy's ccheck-s1.json (the collector's gzip -n -k, default level): sha256 {sha(z)[:16]}; "
                  f"the committed ccheck-s1.json.gz {sha(cz)[:16]}: {'byte for byte the same' if z == cz else 'DIFFERENT'}")


# ------------------------------------------------------------------ 5. the registered score, replayed
def sec_replay(work):
    head("5. the registered score replayed from this directory as committed (dated note 1's reproduce command)")
    tree = extract("HEAD", D174, os.path.join(work, "replay-tree"))
    out = os.path.join(work, "replay-out")
    os.makedirs(out)
    with open(os.path.join(out, "ccheck-s1.json"), "wb") as f:
        f.write(gzip.decompress(open(os.path.join(tree, "ccheck-s1.json.gz"), "rb").read()))
    cmd = [sys.executable, "-B", os.path.join(REPO, KIT, "score_e174.py"), os.path.join(tree, "aifoundry1-c0", "s1"),
           "--ccheck", os.path.join(out, "ccheck-s1.json"), os.path.join(tree, "ccheck-smoke.json"), os.path.join(tree, "ccheck-stoptest-board.json"),
           "--out", os.path.join(out, "results.json")]
    gz_left = len(glob.glob(os.path.join(tree, "aifoundry1-c0", "s1", "**", "*.gz"), recursive=True))
    print(f"  the session's files read as committed: {gz_left} .gz file(s) under aifoundry1-c0/s1/, none unpacked")
    t0 = time.time()
    with open(os.path.join(out, "score.txt"), "wb") as f:
        rc = subprocess.run(cmd, cwd=REPO, stdout=f, stderr=subprocess.STDOUT).returncode
    print(f"  score_e174.py rc {rc}, {time.time() - t0:.0f} s")
    for name in ("results.json", "score.txt"):
        a = open(os.path.join(out, name), "rb").read()
        b = git("show", f"HEAD:{D174}/{name}", binary=True)
        if a == b:
            print(f"  {name}: byte for byte the committed file (sha256 {sha(a)[:16]})")
        else:
            al, bl = a.decode(errors="replace").splitlines(), b.decode(errors="replace").splitlines()
            diff = [i for i in range(max(len(al), len(bl))) if (al[i] if i < len(al) else None) != (bl[i] if i < len(bl) else None)]
            print(f"  {name}: DIFFERS from the committed file ({len(diff)} line(s) of {len(bl)}; first {diff[:5]})")
            if name == "results.json":
                same = json.loads(a) == json.loads(b)
                print(f"  {name}: parsed, {'equal' if same else 'NOT equal'} to the committed file")


# ------------------------------------------------------------------ 6. the login check
def sec_logins(work):
    head("6. the login check in every directory (scrub_etwho_e164.py --check, unchanged, with the owner's box login)")
    src = git("show", f"HEAD:{SCRUB}")
    print(f"  {SCRUB}: HEAD blob sha256 {sha(src.encode())[:16]}; work tree "
          f"{'equal' if sha(open(os.path.join(REPO, SCRUB), 'rb').read()) == sha(src.encode()) else 'DIFFERENT'}; it reads only the files "
          f"directly in the directory it is given: {'yes' if 'for name in sorted(os.listdir(d)):' in src and 'os.walk' not in src else 'NO'}")
    total_left = 0
    for D in (D174, D172, D170):
        ddir = extract("HEAD", D, os.path.join(work, "logins"))
        n_files = sum(len(fs) for _, _, fs in os.walk(ddir))
        top = sum(1 for f in os.listdir(ddir) if os.path.isfile(os.path.join(ddir, f)))
        unz = bins = 0
        for dp, _, fs in os.walk(ddir):
            for f in fs:
                p = os.path.join(dp, f)
                if f.endswith(".gz"):
                    with open(p[:-3], "wb") as g:
                        g.write(gzip.decompress(open(p, "rb").read()))
                    os.remove(p)
                    unz += 1
                elif f.endswith(".bin"):
                    os.remove(p)
                    bins += 1
        dirs, left, lines = 0, 0, []
        for dp, _, _ in os.walk(ddir):
            dirs += 1
            r = subprocess.run([sys.executable, "-B", os.path.join(REPO, SCRUB), "--check", dp, "--owner", OWNER], capture_output=True, text=True)
            last = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
            mm = re.search(r"\((\d+) left\)", last)
            left += int(mm.group(1)) if mm else 1
            if r.returncode or not last.startswith("scrub check: OK"):
                lines.append(f"    {os.path.relpath(dp, ddir) or '.'}: rc {r.returncode}: {r.stdout.strip()[:300]}")
        homes = collections.Counter()
        for dp, _, fs in os.walk(ddir):
            for f in fs:
                for x in BOX_HOME.finditer(open(os.path.join(dp, f), "rb").read()):
                    homes["owner" if x.group(1).decode() == OWNER else "another"] += 1
        total_left += left
        print(f"  {D} (HEAD): {n_files} committed files, {top} directly in the top directory; in the copy {unz} .gz unpacked, {bins} "
              f".bin tile(s) left out; --check run in {dirs} directories: {left} left")
        for ln in lines:
            print(ln)
        print(f"    box home paths: the owner's {homes['owner']:,}, another login's {homes['another']}")
    print(f"  RESULT: {total_left} other login(s) left in any directory of the three data directories")


def main():
    global OWNER
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, help="a new directory outside the repo")
    ap.add_argument("--rb-out")
    ap.add_argument("--raw")
    ap.add_argument("--owner", default="yaroslavvb", help="the box login of record (collect_e174.sh's E174_OWNER default)")
    ap.add_argument("--no-replay", action="store_true")
    a = ap.parse_args()
    OWNER = a.owner
    work = os.path.abspath(a.work)
    if work == REPO or work.startswith(REPO + os.sep) or (os.path.exists(work) and os.listdir(work)):
        sys.exit("refused: --work must be a new or empty directory outside the repo")
    os.makedirs(work, exist_ok=True)
    print("E174 data README, dated note 1: post hoc desk checks (posthoc_note1_e174.py)")
    print(f"HEAD {git('rev-parse', '--short=8', 'HEAD').strip()} ({git('log', '-1', '--format=%cd', '--date=format:%Y-%m-%d %H:%M:%S %z').strip()}); "
          f"run {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; python {sys.version.split()[0]}")
    sec_commits()
    absent = sec_box(a.rb_out) if a.rb_out else None
    sec_d1(absent)
    sec_ccheck(a.raw)
    if not a.no_replay:
        sec_replay(work)
    sec_logins(work)


OWNER = "yaroslavvb"
if __name__ == "__main__":
    main()
