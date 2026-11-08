#!/usr/bin/env python3
# E185 and E183, day 2 (Sun 8 Nov 2026, before any E183 or E185 datum): the day-2 check, v2. E185's kit dated note 4
# (KIT.md.dated-note-4.md) and E183's kit dated note 3 (../../e183/KIT.md.dated-note-3.md) run it; the day-2 brief's dated note 2
# (CARD-LANE-BRIEF.md.dated-note-2.md, the same in both kits) says when. It answers the adversarial verifier of the day-2 check
# (verify-fx, Q158): its fault 1 (E185's registered scorer, M11's scorer v5 with arms_e185.py, and E185's collector load lab files that
# v1's perimeter does not name, so a committed change to one of them passed v1 and both step 2s) and its fault 2 (outside the six core
# directories v1's status read saw only the named files, so an untracked module planted beside one was never seen).
#
#   /usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py tree [--pull] [--log FILE --step NAME] [--dry]
#   /usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py m1 e185|e183 --data DIR [--rb-out DIR] [--log FILE --step NAME] [--dry]
#   /usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py paths
#
# It is v1 (rb/check_day2_v1.py, 1e74546a), checked first against its committed sha256 and then loaded by its path (never from sys.path,
# so -I keeps its meaning), with v1's anchor (6860643c), rules, functions and exit codes unchanged, and three additions:
#   1. v1's 32 lists, plus 15: the 12 lists the day's scorer opens that v1 did not read (pool 8's predictor's and its freeze's lists, M10's
#      list, the three lists of the pool-8 scorers, M11's three card-1 reader and refit lists, aifoundry3's idle-floor lists and k6's driver
#      list), this note's closure list (rb/SHA256SUMS-day2-closure-v2: the 168 lab files the day's desk-side steps load that v1's
#      perimeter did not name, by a run-time trace of the steps), and the two day-2 kit-note lists of 1e74546a (E185's kit note 3's and
#      E183's kit note 2's). Each is read at its pinned count, its own pinned sha256 and with every entry OK, and each list and every file
#      it names joins the day's paths: no change but an addition since 6860643c, nothing uncommitted, no added shadowing module;
#   2. the directories the day's scripts put on sys.path (18, by the same trace) join the directories the additions check reads;
#   3. no untracked module in any of the day's directories, the core ones and every other one alike (git status --untracked-files=all
#      over them): a .py, .pyc, .pyo, .pyd, .so, .dylib or .pth file, or a package's __init__ file, that is not committed stops the day.
#      Other untracked files outside the core directories (a working note, a data file) are not refused; inside the core directories
#      v1's status read refuses any. Ignored files are not read: the lab ignores only __pycache__/, obj_dir/, node_modules/, /build/,
#      /external/ and a few named files, and a module there is never imported in a day-2 script's place (the system python here keeps
#      its byte-code cache outside the tree, and a cached file is only ever read beside its own source).
# m1: v1's gate for an M1 reader, unchanged but for its tree check, which is this file's (no pull).
# paths: the day's paths, one a line (the desk test's coverage case).
#
# Exit codes (the runbooks'): 0 passed; 10 usage; 16 a gate says stop (the STOP line names why). It imports Python's own modules only.
# SPDX-License-Identifier: Apache-2.0
import argparse
import hashlib
import importlib.util
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(HERE, "check_day2_v1.py")
V1_SHA256 = "8b49ddee192076ca1b647eaa90a724062bcb28f602332929f23c05fab864cda2"   # rb/check_day2_v1.py as 1e74546a committed it
CLOSURE = "tools/claims-v3/e185/rb/SHA256SUMS-day2-closure-v2"
# (list, base, pinned count, its own sha256, role), as v1's LISTS
ADDED_LISTS = [
    ("docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS", "top", 16,
     "fa274e3673865d5681d83c2fc3deb38e76fde001fd6931cef332c6119df85013", "gate"),
    ("docs/reports/data/2026-11-05-q142x-pool8-freeze/SHA256SUMS", "top", 160,
     "26eb0b2511e6f4ed3e6e9cc0646f24106a06cfffd402b388ddb110a5e10ab8d2", "gate"),
    ("docs/reports/data/2026-11-05-q145a-a3-idle-floor/SHA256SUMS", "beside", 7,
     "29108efff0a9ec270e6ea91305c1c98c4a9308e41d8cd9e5bc55da4db59f5121", "gate"),
    ("docs/reports/data/2026-11-05-q145a-a3-idle-floor/SHA256SUMS-note1", "beside", 4,
     "b613d3f8f3eca9936cb6d7347ad3eed882d179b42c84a48c94338f9160b40eae", "gate"),
    ("tools/claims-v3/m10/SHA256SUMS", "top", 174, "a3ef8786ded8c54ea73e17e08cdd5898b0f75a8d56e458088da871bcbfa531f5", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-h2-reader", "top", 16, "25027b481c2e4d1843e646e2f85dde16b64c5a1e846c36a7cfb46888eadebe52", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-h2-reader-v2", "top", 129, "51cc3b88595010cd8f298a8c33ef564f2e1674655f7bdef35767a5be670966ce", "gate"),
    ("tools/claims-v3/m11/SHA256SUMS-h2-refit", "top", 6, "0337a1804a2716652480bf25c790b2945a7135546c4da0b172ca1651a1ba0de3", "gate"),
    ("tools/claims-v3/p8-600/SHA256SUMS", "top", 5, "dc52c3a035504f7cd6e66186214e3c828f2d3a7bb05b043b86fd0f3824b593ea", "gate"),
    ("tools/claims-v3/p8-600/SHA256SUMS-v2", "top", 4, "e3b56ce62e9e614768f11b0097deba76bb1fbe42e3e9bebb4e8b85b5d74a9a7d", "gate"),
    ("tools/claims-v3/p8-600/SHA256SUMS-v3", "top", 4, "2194f2b4cd2a82673ac246beb10cd1a4c408472f3cc0afc0cafed1a9f62c8bcb", "gate"),
    ("tools/claims-v3/q141k-runbook/k6/SHA256SUMS-drivers-v3", "top", 39,
     "673de2ca66e2bf6cef9bbf0fa99bffdd94d48d0fbe851ad30485697359a4b0cb", "gate"),
    (CLOSURE, "top", 168, "b4a98c5b4238460164283b9277d3cfabcfd9019ae610eedef6201ff0ad0268db", "gate"),
    ("tools/claims-v3/e185/SHA256SUMS-e185-kit-note3", "top", 16, "bd0a8898e662f0c4bfa4db57f15585c8ffa6d6f117780b1c15f36010e1b3014a", "gate"),
    ("tools/claims-v3/e183/SHA256SUMS-e183-kit-note2", "top", 15, "6ebc97dbcf3923398451741936d31d7d4ffbdaf6928ba097a1aa3c370412c9cd", "gate"),
]
# the in-repo directories the day's desk-side scripts put on sys.path (the run-time trace of steps 14 and 11, the scorers and the readers)
SYSPATH_DIRS = [
    "docs/reports/data/2026-11-02-q138t-heat-model", "docs/reports/data/2026-11-03-q139e-heat-end-to-end",
    "docs/reports/data/2026-11-04-q140e-heat-replicates", "docs/reports/data/2026-11-04-q140l-a2-session-terms",
    "tools/claims-v3/ccheck", "tools/claims-v3/e119", "tools/claims-v3/e164", "tools/claims-v3/e166", "tools/claims-v3/e178",
    "tools/claims-v3/e180", "tools/claims-v3/e183", "tools/claims-v3/e185", "tools/claims-v3/e185/rb", "tools/claims-v3/hpl",
    "tools/claims-v3/kspeed/e83", "tools/claims-v3/m10/pool8", "tools/claims-v3/m11", "tools/claims-v3/q141k-runbook/v3.1",
]
MOD_SUFFIXES = (".py", ".pyc", ".pyo", ".pyd", ".so", ".dylib", ".pth")


class Ctx:
    def __init__(self, repo, step, log):
        self.repo, self.step, self.log = repo, step or "check_day2_v2", log

    def say(self, msg):
        print(f"[{self.step}] {msg}", flush=True)

    def logline(self, msg):
        if self.log:
            try:
                with open(self.log, "a") as f:
                    f.write(time.strftime("%Y-%m-%d %H:%M:%S %Z") + f" step={self.step} {msg}\n")
            except OSError:
                pass


def load_v1():
    """v1, loaded by its path once its bytes are the committed ones, with its LISTS widened; (module, None) or (None, why)."""
    try:
        h = hashlib.sha256(open(V1, "rb").read()).hexdigest()
    except OSError as e:
        return None, f"rb/check_day2_v1.py cannot be read ({e.__class__.__name__})"
    if h != V1_SHA256:
        return None, f"rb/check_day2_v1.py is not at its committed bytes (sha256 {h[:16]}..., pinned {V1_SHA256[:16]}...)"
    spec = importlib.util.spec_from_file_location("check_day2_v1", V1)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    have = {x[0] for x in mod.LISTS}
    mod.LISTS = list(mod.LISTS) + [x for x in ADDED_LISTS if x[0] not in have]
    return mod, None


def perimeter(ctx, v1, m1_gate=None):
    """(problems, reports, paths, dirs): every list at its pin; the day's paths (each list itself among them); the directories"""
    lp, lr, named = v1.check_lists(ctx, m1_gate=m1_gate)
    named = set(named) | {x[0] for x in v1.LISTS}
    paths, dirs = v1.day_paths(ctx, named)
    dirs = sorted(set(dirs) | set(SYSPATH_DIRS))
    return lp, lr, paths, dirs


def untracked_modules(ctx, v1, dirs):
    """(untracked files in the day's directories, [the modules among them]); None for the count if git status failed"""
    rc, so, se = v1.git(ctx, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--", *dirs)
    if rc != 0:
        return None, [f"git status (untracked) failed (rc {rc}): {se.strip()[:200]}"]
    n, mods = 0, []
    for e in so.split("\0"):
        if not e.startswith("?? "):
            continue
        p = e[3:]
        n += 1
        b = os.path.basename(p.rstrip("/"))
        if b.endswith(MOD_SUFFIXES) or b.startswith("__init__."):
            mods.append(p)
    return n, mods


def tree_check(ctx, v1, pull, m1_gate=None):
    """v1's tree check on v2's perimeter, plus the untracked-module read. Returns (problems, reports, head)."""
    problems, reports = [], []
    if pull:
        p, words = v1.do_pull(ctx)
        if p:
            problems.append(p)
            ctx.say(f"the pull: {words.splitlines()[-1][:200] if words else ''}")
            return problems, reports, ""
        reports.append(f"pulled ({words[:80]})")
    rc, so, _ = v1.git(ctx, "rev-parse", "HEAD")
    head = so.strip() if rc == 0 else ""
    if v1.git(ctx, "merge-base", "--is-ancestor", v1.ANCHOR, "HEAD")[0] != 0:
        problems.append(f"ancestry (HEAD does not descend from {v1.ANCHOR[:8]})")
    lp, lr, paths, dirs = perimeter(ctx, v1, m1_gate=m1_gate)
    problems += lp
    reports += lr
    hg, hm = v1.history(ctx, paths)
    if hg:
        problems.append(f"history: {len(hg)} change(s) other than an addition since {v1.ANCHOR[:8]} on the day's paths: " +
                        "; ".join(hg[:6]) + (" ..." if len(hg) > 6 else ""))
    if hm:
        reports.append(f"M1 files changed since {v1.ANCHOR[:8]} (reported; that M1 arm is not read on this day): " + "; ".join(hm[:6]))
    else:
        reports.append(f"M1 files: none changed since {v1.ANCHOR[:8]}")
    nadd, sp = v1.shadows(ctx, dirs)
    if sp:
        problems.append("additions: " + "; ".join(sp[:6]))
    reports.append(f"{nadd} file(s) added since {v1.ANCHOR[:8]} in the day's {len(dirs)} directories, none a shadowing module"
                   if not sp else f"{nadd} file(s) added since {v1.ANCHOR[:8]}")
    st = v1.status(ctx, paths)
    if st:
        problems.append(f"status: {len(st)} uncommitted change(s) on the day's paths: " + "; ".join(s.strip() for s in st[:6]))
    nu, um = untracked_modules(ctx, v1, dirs)
    if nu is None:
        problems += um
    elif um:
        problems.append(f"untracked: {len(um)} untracked module(s) in the day's directories: " + "; ".join(um[:6]) +
                        (" ..." if len(um) > 6 else ""))
    else:
        reports.append(f"untracked: {nu} untracked file(s) in the day's {len(dirs)} directories, none a module")
    reports.append(f"the day's paths: {len(v1.CORE_DIRS)} directories and {len(paths) - len(v1.CORE_DIRS)} named files outside them "
                   f"({len(v1.LISTS)} lists); {len(dirs)} directories read for additions and untracked modules")
    return problems, reports, head


def main():
    ap = argparse.ArgumentParser(prog="check_day2_v2.py")
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
    repo = a.repo or os.environ.get("RB_REPO") or os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
    ctx = Ctx(repo, a.step, a.log)
    if not os.path.isdir(os.path.join(repo, ".git")) and not os.path.isfile(os.path.join(repo, ".git")):
        ctx.say(f"STOP: not a lab clone: {os.path.basename(repo)}")
        return 10
    v1, why = load_v1()
    if v1 is None:
        ctx.say("DAY2-CHECK-V2 STOP: " + why)
        ctx.logline(f"exit=16 {why}")
        return 16
    if a.mode == "paths":
        _, _, paths, _ = perimeter(ctx, v1)
        for p in paths:
            print(p)
        return 0
    if a.mode == "tree":
        if a.dry:
            ctx.say("--- the day-2 check v2 (dry listing; nothing is run): " + ("git pull --ff-only, bounded at 600 s; " if a.pull else "") +
                    f"v1 at its committed bytes; HEAD descends from {v1.ANCHOR[:8]}; {len(v1.LISTS)} lists at their counts and own bytes "
                    f"(v1's {len(v1.LISTS) - len(ADDED_LISTS)} and {len(ADDED_LISTS)} more); no change but an addition since "
                    f"{v1.ANCHOR[:8]} on the day's paths; no shadowing addition; no uncommitted change; no untracked module in the day's "
                    f"directories")
            return 0
        problems, reports, head = tree_check(ctx, v1, a.pull)
        for r in reports:
            ctx.say("  " + r)
        if problems:
            msg = "the day-2 check v2 failed: " + " | ".join(problems)
            ctx.say("DAY2-CHECK-V2 STOP: " + msg)
            ctx.logline(f"exit=16 {msg}")
            return 16
        ctx.say(f"DAY2-CHECK-V2 OK at {head[:12]}: v1 at its committed bytes; HEAD descends from {v1.ANCHOR[:8]}; {len(v1.LISTS) - 2} lists "
                f"at their counts, own bytes and entries (E183's brief list's M1 entries and the two M1 lists reported); no change but an "
                f"addition since {v1.ANCHOR[:8]} on the day's paths; no shadowing addition; no uncommitted change; no untracked module")
        ctx.logline(f"day-2 check v2 passed at {head}")
        return 0
    # m1: v1's gate, with v2's tree check
    if not a.run or not a.data:
        ctx.say("usage: check_day2_v2.py m1 e185|e183 --data <data dir> [--rb-out <E185's RB_OUT>]")
        return 10
    R = v1.READERS[a.run]
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
        ctx.say(f"--- the M1 reader gate v2 for {a.run.upper()} (dry listing; nothing is run): the day-2 check v2 (no pull); its M1 files "
                f"unchanged since {v1.ANCHOR[:8]}; its M1 list at {R['pin']} and its own bytes" +
                ("; step 2 v3's last M1 line '21 of 21 at its pinned bytes'" if a.run == "e185" else "") +
                f"; {data} committed and clean; then /usr/bin/python3 -B " + " ".join(R["argv"](data)))
        return 0
    problems, reports, head = tree_check(ctx, v1, False, m1_gate="m1-" + a.run)
    for r in reports:
        ctx.say("  " + r)
    rc, so, _ = v1.git(ctx, "log", "-m", "--full-history", "--diff-filter=a", "--name-status", "--format=@@%H", f"{v1.ANCHOR}..HEAD",
                       "--", *v1.M1_OWN[a.run])
    changed = [x for x in v1.parse_name_status(so) if x[1]]
    if rc != 0 or changed:
        problems.append(f"{a.run.upper()}'s M1 files changed since {v1.ANCHOR[:8]}: " +
                        "; ".join(f"{st} {' '.join(ps)}" for _, st, ps in changed[:6]))
    st = v1.status(ctx, v1.M1_OWN[a.run])
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
        rc, so, _ = v1.git(ctx, "ls-files", "--", data)
        if rc != 0 or not so.strip():
            problems.append(f"{data}: not committed (the reader runs after the data commit)")
        sd = v1.status(ctx, [data])
        if sd:
            problems.append(f"{data}: {len(sd)} uncommitted change(s): " + "; ".join(s.strip() for s in sd[:4]))
        for o in R["outs"]:
            if os.path.exists(os.path.join(repo, data, o)):
                problems.append(f"{data}/{o} exists already")
    if problems:
        msg = f"the M1 reader gate v2 for {a.run.upper()} refused, the reader not run: " + " | ".join(problems)
        ctx.say("M1-READER-GATE STOP: " + msg)
        ctx.logline(f"exit=16 {msg}")
        return 16
    ctx.say(f"M1-READER-GATE-V2 {a.run} OK at {head[:12]}: running /usr/bin/python3 -B " + " ".join(R["argv"](data)))
    ctx.logline(f"M1 reader gate v2 {a.run} passed at {head}")
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    try:
        p = subprocess.run(["/usr/bin/python3", "-B"] + R["argv"](data), cwd=repo, stdin=subprocess.DEVNULL, capture_output=True,
                           text=True, timeout=v1.READER_BOUND_S, env=env)
        rrc, rout = p.returncode, (p.stdout + p.stderr)
    except subprocess.TimeoutExpired:
        rrc, rout = 124, f"(killed at its {v1.READER_BOUND_S} s bound)"
    for line in rout.splitlines():
        print("    | " + line)
    ctx.say(f"READER-RC {rrc} (a refusal or a non-zero exit is recorded, never a block)")
    ctx.logline(f"M1 reader {a.run} rc {rrc}")
    expect = {f"?? {data}/{o}" for o in R["outs"]}
    after = v1.status(ctx, [data])
    extra = [s for s in after if s.strip() not in expect]
    rest = v1.status(ctx, perimeter(ctx, v1)[2])
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
