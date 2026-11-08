#!/usr/bin/env python3
# E185 and E183, day 2 (Sun 8 Nov 2026, before any E183 or E185 datum): the day-2 check, v1. E185's kit dated note 3
# (KIT.md.dated-note-3.md) and E183's kit dated note 2 (../../e183/KIT.md.dated-note-2.md) run it; the day-2 brief's dated note 1
# (CARD-LANE-BRIEF.md.dated-note-1.md, the same in both kits) says when. It answers the adversarial verifier of E185's kit note 2 and of
# E183's day-2 brief (verify-d2b, Q158b): its faults 1-3 (a committed change to a file the day reads, made together with its list line,
# or under a copied line, passed both day-2 step 2s; and the M1 readers' gate was weaker than step 2 v3's byte pin).
#
#   /usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v1.py tree [--pull] [--log FILE --step NAME] [--dry]
#   /usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v1.py m1 e185|e183 --data DIR [--rb-out DIR] [--log FILE --step NAME] [--dry]
#   /usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v1.py paths
#
# tree: (with --pull, first the lab clone's `git pull --ff-only`, bounded at 600 s, a failure classified as the network's or not), then,
#   on the tree as it is, every one of these, with the problems named:
#   1. HEAD descends from ANCHOR (6860643c, the commit of the day-2 brief, the last one verify-d2b read);
#   2. every list the day's two step 2s read, and E183's brief list, at its pinned count, at its own pinned sha256 and with every entry OK
#      (E183's brief list: its entries for october-forecast-model's note M1 are reported, never a gate); the two M1 lists are read and
#      REPORTED (never a gate: the M1 arms are reported arms, so their files cannot stop E185 or E183);
#   3. no commit since ANCHOR changed anything but an addition on the day's paths (git log -m --full-history --diff-filter=a, and the
#      tree diff ANCHOR..HEAD with the same filter): the day's paths are E183's, E185's, M11's, the footing law's, the k6/v3.1 runbook's
#      and the enercat workload's directories, plus every file any of those lists, E183's harness or E185's runbook pins name. A change to
#      an M1 note's own files (13, named below) is reported, never a gate;
#   4. no file added since ANCHOR in the day's directories is a Python module or package that shadows one the system python finds outside
#      the lab clone (its own modules and site packages, the user site among them), or that shares its module name with another of
#      the day's modules (M11's scorer puts both M11's and E185's directories on sys.path), a byte-code file or a .pth file (a planted
#      json.py beside a reader would be imported before the standard one);
#   5. no uncommitted change on the day's paths (git status, untracked files too).
# m1: the gate for an M1 reader, run after that run's data commit. The tree check (no pull), the run's M1 files unchanged since ANCHOR,
#   its M1 list at its count and own bytes with every entry OK, for E185 the last M1 line of step 2 v3 in E185's RB_OUT log reading "21
#   of 21 at its pinned bytes", and the data directory committed and clean. On all of them it runs the reader by the M1 note's own run
#   line (/usr/bin/python3 -B, from the lab's top, --out in the data directory), prints its exit status, and checks that the reader wrote
#   only its two outputs. A reader's own refusal never blocks anything: the data commit is already made.
# paths: prints the day's paths, one a line (for the desk test's coverage case).
#
# Exit codes (the runbooks'): 0 passed; 10 usage; 16 a gate says stop (the STOP line names why). It imports Python's own modules only; it reads git and
# files and writes nothing but its log line (and, in m1, the reader's two outputs).
# SPDX-License-Identifier: Apache-2.0
import argparse
import hashlib
import importlib.machinery
import os
import re
import subprocess
import sys
import time

ANCHOR = "6860643c8dacc57b6bf459dc9726721d68ec1f3a"   # E183: note M1's dated note 1 and the day-2 brief (06:49:00 PST Sun 8 Nov 2026)
CORE_DIRS = ["tools/claims-v3/e183", "tools/claims-v3/e185", "tools/claims-v3/m11", "tools/claims-v3/footing-law",
             "tools/claims-v3/q141k-runbook", "workloads/enercat"]
# (list, base, pinned count, its own sha256, role); base "top": entries from the lab's top; "beside": from the list's own directory.
# role "gate": every entry OK; "brief": the M1 entries reported, the others a gate; "m1-e185"/"m1-e183": reported in tree, a gate in m1;
# "box": the build/ entries are the box's (skipped), the repo entries a gate.
LISTS = [
    ("tools/claims-v3/e185/SHA256SUMS-e185-registration", "top", 8, "dd772a171155a07cf5d00f8dc781951255c086f52d30de56c3f5456aa70adcc2", "gate"),
    ("tools/claims-v3/e185/SHA256SUMS-e185-kit", "top", 13, "79fdc9288e194719dc86e5e38c592f916773cd623e0b0ce17eaeebe52bc8b622", "gate"),
    ("tools/claims-v3/e185/rb/SHA256SUMS-rb-e185", "top", 21, "2f5371e8a290f7349292cc37e33e93f08c3d6856adcd118f46eed58d3266fe8a", "gate"),
    ("tools/claims-v3/e185/SHA256SUMS-e185-a1", "top", 5, "8757f508e88d633804d8448ab9706e0c6fd9da006dcdffe6bb45fc872a9f9670", "gate"),
    ("tools/claims-v3/e185/SHA256SUMS-e185-kit-note1", "top", 28, "0eeedd7c2f0724c30c705006f0439bfda91544992a02e8c720bed56eab38a780", "gate"),
    ("tools/claims-v3/e185/SHA256SUMS-e185-kit-note2", "top", 16, "f421125642edfd4cc00ede66a1695196db4d75d06ab27c7d5cadefa6ced6702a", "gate"),
    ("tools/claims-v3/e185/frozen-e185.sha256", "top", 30, "d3bbcf11a1eaea5133c0ee2776899fa0287ce221146a3fdd8325698b0987fe03", "box"),
    ("tools/claims-v3/m11/SHA256SUMS", "top", 58, "81fb1bd34949fe5109015a0e2896a459b733525148d957e02742ac31117a6d73", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-m11", "top", 6, "9ad75bc68b537ab881a6ca7fe9dc310704854f2b026f2624f61b5242832b77af", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-a1", "top", 9, "24e911ba79a2616f7b03b592503ee249d1d0aa53908a6d9ab7bcd749273ca25d", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-a2", "top", 7, "977336a77fe8e4a49a5ab653fb674eedce0fff210e71462dffb54d3f102a6f14", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-a3", "top", 7, "4e6a5e7a2fe0305833ef5227465c5193829278d1e980d6586456b7c661151054", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-a4", "top", 6, "891925d7b7342cc0feec78f33d3a5550f1391cf1701558bd2d6579595394e39b", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-a5", "top", 6, "c8736344caa85126464d61eda636aa69d5ca7abf99e1881f731ad8ed091478e6", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-a6", "beside", 9, "366a65fd7297de9a42e9e40ea8f948c2d2560d18081905879ed65aa6687fd5f1", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-a7", "beside", 7, "aeeed4de0c400d51d0b18e21e312911d534dc0a3b1d3485c04c92b783d639f66", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-a8", "top", 4, "5870af611428458e56dce426b0f2df925182dbd05e3a33216e631e90f846688c", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-a9", "top", 4, "5baeb74c040c93e245b08d69792ea42ac436f6a8af8c595bf0faa91ea26d92e4", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-a10", "top", 4, "50f246105b2026d9922a1ccedbc2045871565fdcddc6d5a97331c6cca7321c91", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-score-m11", "top", 4, "49a9b597791fb867379bae52382aecbb14e187afd844f7c915b88a3f6ca25f84", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-score-m11-v2", "top", 6, "3250422c3db9f3d1198ace20d32f8159f016c6a65ed04dbd93a2bcb2521dd224", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-score-m11-v3", "top", 6, "56504dc928667c30cb1d8fc189397292760bdb757bb5dd978c57e56e7b863dc1", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-score-m11-v4", "top", 5, "efcc3cfbe99a1cf276ba2f137e4cefd358f365c114935a86aa482d86925d9c62", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-score-m11-v5", "top", 4, "f6dd93bdf8e211db345987ea79af29103059f6546af28d3d5f3cc642d58da77c", "gate"),
    ("tools/claims-v3/footing-law/SHA256SUMS", "beside", 7, "59288c156963cd2eeda467dd29ed9ec3279825f998e9591aea91db6f69824b73", "gate"),
    ("tools/claims-v3/footing-law/SHA256SUMS-note1", "beside", 4, "9e6e3cf5438fccdcfeb4566c783204ff597f8e900449762446533195f4e45c44", "gate"),
    ("tools/claims-v3/e183/SHA256SUMS-e183-registration", "top", 20, "6defebd4c3ec66a6e4b1b3e921751d0513a0c78d3869cffe489f2f43508a1a8a", "gate"),
    ("tools/claims-v3/e183/SHA256SUMS-e183-kit", "top", 46, "2e06e0cc48bcf2fab2dc432e905a45456b35f058fab4603dcd732e9869bd8723", "gate"),
    ("tools/claims-v3/e183/SHA256SUMS-e183-note1", "top", 46, "24d0c583cdf8678dd254ad3b87c613fb6735d26a21eafb034843600fdb5383e7", "gate"),
    ("tools/claims-v3/e183/SHA256SUMS-e183-brief", "top", 15, "02c8b2b62d2b9469cb4e67736393a3c3d2d1516c3b44b504742eb47e2c89cf10", "brief"),
    ("tools/claims-v3/e185/SHA256SUMS-e185-m1", "top", 21, "52a6c1622fcf5f31b7e14e5b332f3a29ae8e5456998b74e30404d1094df7222c", "m1-e185"),
    ("tools/claims-v3/e183/SHA256SUMS-e183-m1", "top", 25, "c8bad97187caf6f31c9e21ddae39fa7f4888f6a43f02962045b2cb24b3d34865", "m1-e183"),
]
# october-forecast-model's notes M1: their own files (06286213 and 2f6a4440, and 6860643c's restatement of E183's M1-4). Reported arms.
M1_OWN = {
    "e185": ["tools/claims-v3/e185/E185.md.dated-note-M1.md", "tools/claims-v3/e185/m1-october-forecast-model-e185.json",
             "tools/claims-v3/e185/arm_m1_read_e185.py", "tools/claims-v3/e185/selftest_arm_m1_e185.py",
             "tools/claims-v3/e185/logs/selftest-arm-m1-e185.txt", "tools/claims-v3/e185/SHA256SUMS-e185-m1"],
    "e183": ["tools/claims-v3/e183/E183.md.dated-note-M1.md", "tools/claims-v3/e183/m1-october-forecast-model-e183.json",
             "tools/claims-v3/e183/arm_m1_read_e183.py", "tools/claims-v3/e183/selftest_arm_m1_e183.py",
             "tools/claims-v3/e183/logs/selftest-arm-m1-e183.txt", "tools/claims-v3/e183/SHA256SUMS-e183-m1",
             "tools/claims-v3/e183/E183.md.dated-note-M1.md.dated-note-1.md"],
}
M1_ALL = set(M1_OWN["e185"]) | set(M1_OWN["e183"])
# E185's runbook pins (rb_common_e185.sh's rb_pins), and E183's harness (its files and the train host's build inputs)
RB_PINS_FILES = ["tools/claims-v3/q141k-runbook/v3.1/rb_run.py", "tools/claims-v3/q141k-runbook/v3.1/nopath_q142s.py",
                 "tools/claims-v3/q141k-runbook/v3.1/ccdone_q142s.py", "tools/claims-v3/e164/scrub_etwho_e164.py"]
HARNESS = "tools/claims-v3/e183/harness-e183.json"
READERS = {
    "e185": {"list": "tools/claims-v3/e185/SHA256SUMS-e185-m1", "pin": 21,
             "data_re": r"docs/reports/data/[0-9]{4}-[0-9]{2}-[0-9]{2}-e185-m11-session3-aifoundry3",
             "argv": lambda d: ["tools/claims-v3/e185/arm_m1_read_e185.py", "--data", d, "--out", d + "/arm-m1-e185"],
             "outs": ["arm-m1-e185.json", "arm-m1-e185.txt"],
             "log_line": "october-forecast-model note M1 present, its list 21 of 21 at its pinned bytes"},
    "e183": {"list": "tools/claims-v3/e183/SHA256SUMS-e183-m1", "pin": 25,
             "data_re": r"docs/reports/data/[0-9]{4}-[0-9]{2}-[0-9]{2}-e183-vector-add-r2-aifoundry3",
             "argv": lambda d: ["tools/claims-v3/e183/arm_m1_read_e183.py", "--reduced", d + "/reduced-e183.json",
                                "--scored", d + "/scored-e183.json", "--out", d + "/arm-m1-e183"],
             "outs": ["arm-m1-e183.json", "arm-m1-e183.txt"],
             "log_line": None},
}
NET_RE = re.compile(r"Could not resolve host|unable to access|Could not read from remote|does not appear to be a git repository|"
                    r"Connection (refused|reset|timed out)|Operation timed out|Failed to connect|network is unreachable|"
                    r"early EOF|The remote end hung up", re.I)
PULL_BOUND_S = 600
READER_BOUND_S = 600


class Ctx:
    def __init__(self, repo, step, log):
        self.repo, self.step, self.log = repo, step or "check_day2_v1", log

    def say(self, msg):
        print(f"[{self.step}] {msg}", flush=True)

    def logline(self, msg):
        if self.log:
            try:
                with open(self.log, "a") as f:
                    f.write(time.strftime("%Y-%m-%d %H:%M:%S %Z") + f" step={self.step} {msg}\n")
            except OSError:
                pass


def git(ctx, *args, timeout=120):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", LC_ALL="C", GIT_PAGER="cat")
    try:
        p = subprocess.run(["git", "-C", ctx.repo] + list(args), stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           timeout=timeout, env=env)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"(killed at its {timeout} s bound)"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_list(ctx, rel, base):
    """[(hash, entry path from the lab's top)] for every non-empty line; None if the list cannot be read."""
    try:
        text = open(os.path.join(ctx.repo, rel), "rb").read().decode("utf-8", "replace")
    except OSError:
        return None
    out = []
    d = os.path.dirname(rel)
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) < 2:
            out.append(("", "<unreadable line>"))
            continue
        h, p = parts[0], parts[1].strip()
        if p.startswith("*"):
            p = p[1:]
        p = os.path.normpath(os.path.join(d, p)) if base == "beside" else os.path.normpath(p)
        out.append((h, p))
    return out


def check_lists(ctx, roles_gate=("gate", "brief", "box"), m1_gate=None):
    """Return (problems, reports, named): every list at its count, own bytes and entries; named = every repo file the lists name."""
    problems, reports, named = [], [], set()
    for rel, base, pin, own, role in LISTS:
        entries = read_list(ctx, rel, base)
        if entries is None:
            (problems if role in roles_gate or role == m1_gate else reports).append(f"{rel}: missing")
            continue
        n = len(entries)
        try:
            h = sha256_file(os.path.join(ctx.repo, rel))
        except OSError:
            h = ""
        ok_gate = ok_m1 = bad_gate = bad_m1 = skipped = 0
        bad_names = []
        for eh, ep in entries:
            if role == "box" and ep.startswith("build/"):
                skipped += 1
                continue
            named.add(ep)
            try:
                good = sha256_file(os.path.join(ctx.repo, ep)) == eh
            except OSError:
                good = False
            is_m1 = role == "brief" and ep in M1_ALL
            if good:
                if is_m1:
                    ok_m1 += 1
                else:
                    ok_gate += 1
            else:
                if is_m1:
                    bad_m1 += 1
                else:
                    bad_gate += 1
                    bad_names.append(ep)
        why = []
        if n != pin:
            why.append(f"{n} lines; pinned {pin}")
        if h != own:
            why.append("its own bytes differ from the pin")
        if bad_gate:
            why.append(f"{bad_gate} entr{'y' if bad_gate == 1 else 'ies'} not OK: " + ", ".join(bad_names[:4]) +
                       (" ..." if len(bad_names) > 4 else ""))
        short = os.path.relpath(rel, "tools/claims-v3")
        if role in ("m1-e185", "m1-e183"):
            msg = f"{short}: {ok_gate} OK of {n}; pinned {pin}" + ("" if not why else "; " + "; ".join(why))
            if role == m1_gate:
                if why:
                    problems.append(msg)
            else:
                reports.append(("M1 list " + msg) if why else f"M1 list {short} {ok_gate} of {pin} at its pinned bytes")
            continue
        if why:
            problems.append(f"{short} ({'; '.join(why)})")
        if role == "brief":
            reports.append(f"E183's brief list: {ok_gate} of {ok_gate + bad_gate} non-M1 entries OK; its {ok_m1 + bad_m1} M1 "
                           f"entries {'all OK' if not bad_m1 else f'{bad_m1} not OK (reported, never a gate)'}")
        if role == "box":
            reports.append(f"E185's box list: {ok_gate} of {n - skipped} repo entries OK ({skipped} build entries are the box's)")
    return problems, reports, named


def day_paths(ctx, named):
    """The day's paths: the core directories, plus every named file outside them (the M1 notes' own files kept apart)."""
    extra = set(named) | set(RB_PINS_FILES)
    try:
        import json
        hj = json.load(open(os.path.join(ctx.repo, HARNESS)))
        extra |= set(hj.get("files", {})) | set(hj.get("build_inputs", {}))
    except (OSError, ValueError):
        pass
    outside = sorted(p for p in extra if not any(p == d or p.startswith(d + "/") for d in CORE_DIRS))
    dirs = sorted(set(CORE_DIRS) | {os.path.dirname(p) for p in outside})
    return list(CORE_DIRS) + outside, dirs


def parse_name_status(text):
    """[(commit or '', status, [paths])] from git's --name-status output, with '@@<sha>' commit lines."""
    out, cur = [], ""
    for line in text.splitlines():
        if line.startswith("@@"):
            cur = line[2:].strip()
            continue
        if not line.strip():
            continue
        parts = line.split("\t")
        out.append((cur, parts[0], parts[1:]))
    return out


def history(ctx, paths):
    """Non-additions since ANCHOR on the paths: (gating changes, M1 changes), each as 'X path (commit)'."""
    gate, m1 = [], []
    rc, so, se = git(ctx, "log", "-m", "--full-history", "--diff-filter=a", "--name-status", "--format=@@%H",
                     f"{ANCHOR}..HEAD", "--", *paths)
    if rc != 0:
        return [f"git log failed (rc {rc}): {se.strip()[:200]}"], m1
    rc2, so2, se2 = git(ctx, "diff", "--diff-filter=a", "--name-status", ANCHOR, "HEAD", "--", *paths)
    if rc2 != 0:
        return [f"git diff failed (rc {rc2}): {se2.strip()[:200]}"], m1
    seen = set()
    for commit, st, ps in parse_name_status(so) + [("tree diff", s, p) for _, s, p in parse_name_status(so2)]:
        key = (st[:1], tuple(ps))
        item = f"{st[:1]} {' -> '.join(ps)} ({commit[:8] if commit != 'tree diff' else 'the tree diff from ' + ANCHOR[:8]})"
        if all(p in M1_ALL for p in ps):
            if key not in seen:
                m1.append(item)
        else:
            if key not in seen:
                gate.append(item)
        seen.add(key)
    return gate, m1


def shadows(ctx, dirs):
    """Files added since ANCHOR in the day's directories (the core ones in full; any other only its own files and packages, the
    places a script there imports from): (count, problems)."""
    specs = []
    for d in dirs:
        if d in CORE_DIRS:
            specs.append(d)
        else:
            specs += [f":(glob){d}/*", f":(glob){d}/*/__init__.py", f":(glob){d}/__pycache__/*"]
    rc, so, se = git(ctx, "diff", "--diff-filter=A", "--name-only", ANCHOR, "HEAD", "--", *specs)
    if rc != 0:
        return 0, [f"git diff (additions) failed (rc {rc}): {se.strip()[:200]}"]
    added = [l for l in so.splitlines() if l.strip()]
    real = os.path.realpath(ctx.repo)
    search = [p for p in sys.path if p and not (os.path.realpath(p) + os.sep).startswith(real + os.sep)]
    try:  # the user site too (M11's scorers import numpy from it, so a planted numpy.py would shadow it), never the lab clone
        import site
        us = site.getusersitepackages()
        if us and os.path.isdir(us) and us not in search and not (os.path.realpath(us) + os.sep).startswith(real + os.sep):
            search.append(us)
    except Exception:
        pass

    def modname(p):
        b = os.path.basename(p)
        if b == "__init__.py":
            return os.path.basename(os.path.dirname(p))
        if b.endswith(".py"):
            return b[:-3]
        if b.endswith((".so", ".dylib")):
            return b.split(".")[0]
        return None
    rc, so, _ = git(ctx, "ls-files", "--", *specs)   # the day's own modules: a scorer puts two kits' directories on sys.path
    names = {}
    for p in so.splitlines():
        n = modname(p)
        if n:
            names.setdefault(n, []).append(p)
    probs = []
    for p in added:
        b = os.path.basename(p)
        if "/__pycache__/" in "/" + p or b.endswith((".pyc", ".pyo")) or b.endswith(".pth"):
            probs.append(f"{p} (a byte-code or .pth file)")
            continue
        name = modname(p)
        if not name:
            continue
        if name in sys.builtin_module_names or importlib.machinery.PathFinder.find_spec(name, search) is not None:
            probs.append(f"{p} (shadows the module '{name}' the system python finds)")
        elif len([q for q in names.get(name, []) if q != p]) > 0:
            probs.append(f"{p} (its module name '{name}' is also {[q for q in names[name] if q != p][0]}'s)")
    return len(added), probs


def status(ctx, paths):
    rc, so, se = git(ctx, "status", "--porcelain=v1", "--untracked-files=all", "--", *paths)
    if rc != 0:
        return [f"git status failed (rc {rc}): {se.strip()[:200]}"]
    return [l for l in so.splitlines() if l.strip()]


def do_pull(ctx):
    rc, so, se = git(ctx, "pull", "--ff-only", timeout=PULL_BOUND_S)
    if rc == 0:
        return None, (so.strip().splitlines() or [""])[-1]
    text = (so + "\n" + se).strip()
    if git(ctx, "symbolic-ref", "-q", "HEAD")[0] != 0:
        return "pull: HEAD is detached (not the network's: a dated note first)", text
    if git(ctx, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")[0] != 0:
        return "pull: the branch has no upstream (not the network's: a dated note first)", text
    if rc == 124 or NET_RE.search(text):
        return ("pull: the upstream did not answer (the network's: run this step again once it answers)" +
                (f"; killed at its {PULL_BOUND_S} s bound" if rc == 124 else "")), text
    a = git(ctx, "merge-base", "--is-ancestor", "HEAD", "@{u}")[0]
    b = git(ctx, "merge-base", "--is-ancestor", "@{u}", "HEAD")[0]
    if a != 0 and b != 0:
        return "pull: the clone has diverged from its upstream (not the network's: a dated note first)", text
    return f"pull: failed (rc {rc}; not the network's by its words: a dated note first)", text


def tree_check(ctx, pull, m1_gate=None):
    """Returns (problems, reports, head)."""
    problems, reports = [], []
    if pull:
        p, words = do_pull(ctx)
        if p:
            problems.append(p)
            ctx.say(f"the pull: {words.splitlines()[-1][:200] if words else ''}")
            return problems, reports, ""
        reports.append(f"pulled ({words[:80]})")
    rc, so, _ = git(ctx, "rev-parse", "HEAD")
    head = so.strip() if rc == 0 else ""
    if git(ctx, "merge-base", "--is-ancestor", ANCHOR, "HEAD")[0] != 0:
        problems.append(f"ancestry (HEAD does not descend from {ANCHOR[:8]})")
    lp, lr, named = check_lists(ctx, m1_gate=m1_gate)
    problems += lp
    reports += lr
    paths, dirs = day_paths(ctx, named)
    hg, hm = history(ctx, paths)
    if hg:
        problems.append(f"history: {len(hg)} change(s) other than an addition since {ANCHOR[:8]} on the day's paths: " +
                        "; ".join(hg[:6]) + (" ..." if len(hg) > 6 else ""))
    if hm:
        reports.append(f"M1 files changed since {ANCHOR[:8]} (reported; that M1 arm is not read on this day): " + "; ".join(hm[:6]))
    else:
        reports.append(f"M1 files: none changed since {ANCHOR[:8]}")
    nadd, sp = shadows(ctx, dirs)
    if sp:
        problems.append("additions: " + "; ".join(sp[:6]))
    reports.append(f"{nadd} file(s) added since {ANCHOR[:8]} in the day's {len(dirs)} directories, none a shadowing module"
                   if not sp else f"{nadd} file(s) added since {ANCHOR[:8]}")
    st = status(ctx, paths)
    if st:
        problems.append(f"status: {len(st)} uncommitted change(s) on the day's paths: " + "; ".join(s.strip() for s in st[:6]))
    reports.append(f"the day's paths: {len(CORE_DIRS)} directories and {len(paths) - len(CORE_DIRS)} named files outside them")
    return problems, reports, head


def main():
    ap = argparse.ArgumentParser(prog="check_day2_v1.py")
    ap.add_argument("mode", choices=["tree", "m1", "paths"])
    ap.add_argument("run", nargs="?", choices=["e185", "e183"])
    ap.add_argument("--pull", action="store_true")
    ap.add_argument("--data")
    ap.add_argument("--rb-out")
    ap.add_argument("--log")
    ap.add_argument("--step")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--repo")
    try:
        a = ap.parse_args()
    except SystemExit:
        return 10
    here = os.path.dirname(os.path.abspath(__file__))
    repo = a.repo or os.environ.get("RB_REPO") or os.path.normpath(os.path.join(here, "..", "..", "..", ".."))
    ctx = Ctx(repo, a.step, a.log)
    if not os.path.isdir(os.path.join(repo, ".git")) and not os.path.isfile(os.path.join(repo, ".git")):
        ctx.say(f"STOP: not a lab clone: {os.path.basename(repo)}")
        return 10
    if a.mode == "paths":
        _, _, named = check_lists(ctx)
        paths, dirs = day_paths(ctx, named)
        for p in paths:
            print(p)
        return 0
    if a.mode == "tree":
        if a.dry:
            ctx.say("--- the day-2 check v1 (dry listing; nothing is run): " + ("git pull --ff-only, bounded at 600 s; " if a.pull else "") +
                    f"HEAD descends from {ANCHOR[:8]}; {len(LISTS)} lists at their counts and own bytes; no change but an addition "
                    f"since {ANCHOR[:8]} on the day's paths; no shadowing addition; no uncommitted change")
            return 0
        problems, reports, head = tree_check(ctx, a.pull)
        for r in reports:
            ctx.say("  " + r)
        if problems:
            msg = "the day-2 check failed: " + " | ".join(problems)
            ctx.say("DAY2-CHECK STOP: " + msg)
            ctx.logline(f"exit=16 {msg}")
            return 16
        ctx.say(f"DAY2-CHECK OK at {head[:12]}: HEAD descends from {ANCHOR[:8]}; {len(LISTS) - 2} lists at their counts, own bytes and "
                f"entries (E183's brief list's M1 entries and the two M1 lists reported); no change but an addition since "
                f"{ANCHOR[:8]} on the day's paths; no shadowing addition; no uncommitted change")
        ctx.logline(f"day-2 check v1 passed at {head}")
        return 0
    # m1
    if not a.run or not a.data:
        ctx.say("usage: check_day2_v1.py m1 e185|e183 --data <data dir> [--rb-out <E185's RB_OUT>]")
        return 10
    R = READERS[a.run]
    data = os.path.normpath(a.data).rstrip("/")
    if os.path.isabs(data):
        try:
            data = os.path.relpath(os.path.realpath(data), os.path.realpath(repo))
        except ValueError:
            pass
    if not re.fullmatch(R["data_re"], data):
        ctx.say(f"STOP: {data} is not {a.run.upper()}'s data directory (docs/reports/data/<day>-...)")
        return 10
    if a.run == "e185" and not a.rb_out:
        ctx.say("usage: E185's reader gate needs --rb-out <E185's RB_OUT> (step 2 v3's M1 line)")
        return 10
    if a.dry:
        ctx.say(f"--- the M1 reader gate for {a.run.upper()} (dry listing; nothing is run): the day-2 check (no pull); its M1 files "
                f"unchanged since {ANCHOR[:8]}; its M1 list at {R['pin']} and its own bytes" +
                ("; step 2 v3's last M1 line '21 of 21 at its pinned bytes'" if a.run == "e185" else "") +
                f"; {data} committed and clean; then /usr/bin/python3 -B " + " ".join(R["argv"](data)))
        return 0
    problems, reports, head = tree_check(ctx, False, m1_gate="m1-" + a.run)
    for r in reports:
        ctx.say("  " + r)
    rc, so, _ = git(ctx, "log", "-m", "--full-history", "--diff-filter=a", "--name-status", "--format=@@%H", f"{ANCHOR}..HEAD", "--",
                    *M1_OWN[a.run])
    changed = [x for x in parse_name_status(so) if x[1]]
    if rc != 0 or changed:
        problems.append(f"{a.run.upper()}'s M1 files changed since {ANCHOR[:8]}: " +
                        "; ".join(f"{st} {' '.join(ps)}" for _, st, ps in changed[:6]))
    st = status(ctx, M1_OWN[a.run])
    if st:
        problems.append(f"{a.run.upper()}'s M1 files: uncommitted change(s): " + "; ".join(s.strip() for s in st[:6]))
    if R["log_line"]:
        last = ""
        try:
            for line in open(os.path.join(a.rb_out, "runbook.log"), errors="replace"):
                if "october-forecast-model note M1" in line:
                    last = line.strip()
        except OSError:
            last = ""
        if R["log_line"] not in last:
            problems.append("step 2 v3's last M1 line in E185's RB_OUT log does not read '21 of 21 at its pinned bytes'" +
                            (f" (it reads: {last.split('note M1', 1)[-1].strip()[:120]})" if last else " (no such line)"))
    if not os.path.isdir(os.path.join(repo, data)):
        problems.append(f"{data}: no such directory")
    else:
        rc, so, _ = git(ctx, "ls-files", "--", data)
        if rc != 0 or not so.strip():
            problems.append(f"{data}: not committed (the reader runs after the data commit)")
        sd = status(ctx, [data])
        if sd:
            problems.append(f"{data}: {len(sd)} uncommitted change(s): " + "; ".join(s.strip() for s in sd[:4]))
        for o in R["outs"]:
            if os.path.exists(os.path.join(repo, data, o)):
                problems.append(f"{data}/{o} exists already")
    if problems:
        msg = f"the M1 reader gate for {a.run.upper()} refused, the reader not run: " + " | ".join(problems)
        ctx.say("M1-READER-GATE STOP: " + msg)
        ctx.logline(f"exit=16 {msg}")
        return 16
    ctx.say(f"M1-READER-GATE {a.run} OK at {head[:12]}: running /usr/bin/python3 -B " + " ".join(R["argv"](data)))
    ctx.logline(f"M1 reader gate {a.run} passed at {head}")
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    try:
        p = subprocess.run(["/usr/bin/python3", "-B"] + R["argv"](data), cwd=repo, stdin=subprocess.DEVNULL, capture_output=True,
                           text=True, timeout=READER_BOUND_S, env=env)
        rrc, rout = p.returncode, (p.stdout + p.stderr)
    except subprocess.TimeoutExpired:
        rrc, rout = 124, f"(killed at its {READER_BOUND_S} s bound)"
    for line in rout.splitlines():
        print("    | " + line)
    ctx.say(f"READER-RC {rrc} (a refusal or a non-zero exit is recorded, never a block)")
    ctx.logline(f"M1 reader {a.run} rc {rrc}")
    expect = {f"?? {data}/{o}" for o in R["outs"]}
    after = status(ctx, [data])
    extra = [s for s in after if s.strip() not in expect]
    rest = status(ctx, day_paths(ctx, check_lists(ctx)[2])[0])
    if extra or rest:
        msg = "the reader changed files beyond its two outputs: " + "; ".join(s.strip() for s in (extra + rest)[:6])
        ctx.say("M1-READER STOP: " + msg)
        ctx.logline(f"exit=16 {msg}")
        return 16
    ctx.say(f"M1 reader outputs: {len(after)} new file(s) in {data}, nothing else changed; commit them with a dated note beside the "
            f"data README")
    return 0


if __name__ == "__main__":
    sys.exit(main())
