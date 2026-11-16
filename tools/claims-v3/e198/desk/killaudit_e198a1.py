#!/usr/bin/env python3
"""E198 dated amendment A1 (Q196, lane a1-e198, Mon 16 Nov 2026, before any E198 datum): THE KILL AUDIT, a grep and a code reading, no
strace. It shows that no code path of the lab's runner copy or of the kit names or arranges a SIGKILL, a `kill -9` or a `timeout -k` around
a device process (the orchestrator's standing ruling of Mon 16 Nov 2026 02:56:14 PST: no run of ours sends or arranges a SIGKILL to a
device process; the lab's AGENT.md: "never kill -9"). The runtime half of the proof is the real-path test's HG cases (a stand-in host that
outlives its TERM is alive when the session has ended, holds TERMs only in its signal log, and writes its own end line).

    /usr/bin/python3 -I -B tools/claims-v3/e198/desk/killaudit_e198a1.py        (from the repository's top; reads files only)

  1. THE A1 PATH: every file the A1 card day runs or reads on the box (harness-e198-a1.json's files, the tree's E191 guard), every runbook
     file A1's steps run or source at the desk (A1's steps, the v1 steps A1 keeps, rb_e198.sh, k6's rb_common.sh, v3.1's rb_run.py and
     nopath_q142s.py, E191's rest rule, the history check, the collector, the scorer), and A1's desk tests and stand-ins. Every line of a
     code file is matched against the kill patterns (SIGKILL; the word KILL; kill -9, -KILL, -s KILL or a computed -s; timeout -k,
     --kill-after, -s KILL; "timeout", "-k" in a list; .kill(), os.kill(, os.killpg(; subprocess.run/communicate with timeout=, whose
     expiry sends the child a SIGKILL; bubblewrap's --die-with-parent, whose parent-death signal is a KILL; pkill, killall). EVERY HIT MUST
     BE CLASSIFIED by the table below, with why it is not a kill of a device process; an unclassified hit, or one around a device process,
     FAILS. A text file (a listing, a README, a diff) is never run: its hits are counted, not classified.
  2. THE REST OF E198'S FOLDER: the kit's v1 files that A1 supersedes (not run for E198 after A1) and E198's registration files, each hit
     listed with its class, so nothing in the folder is unread.
  3. THE RUNNER COPY READ AS CODE (ast): the device command is the list literal ["timeout", "10", a.host, ...]; no call of .kill(),
     os.kill() or os.killpg(); every .send_signal() sends signal.SIGTERM; the one subprocess.run(..., timeout=) is the holder check's.
  4. The A1 steps' remote scripts and the A1 session name no `timeout -k` in any code line.
  5. EVERY PYTHON FILE of scopes 1 and 2 READ AS CODE (ast), whatever its line layout: every call of subprocess.run, call, check_call or
     check_output with a timeout= keyword (their expiry sends the child a SIGKILL), every .communicate(timeout=), every .kill(), os.kill(),
     os.killpg() or signal.pthread_kill() call, and every .send_signal() whose signal is not SIGTERM, SIGINT or SIGHUP. Each such call is
     an AST hit, classified by the same table on the call's own source text (its lines joined), so a call split over lines cannot hide;
     an unclassified AST hit FAILS. A file that does not parse FAILS.
Dated fix (Q196, lane fix-a1e198, Mon 16 Nov 2026, before the land and before any E198 datum), answering verify-a1e198's finding 4: item 5
is new (its break tests M6, a timed subprocess.run with timeout= on a later line, and M7, a subprocess.call with timeout=, passed the grep);
the grep half gains bash's `kill -n` (its M9) and subprocess.call/check_call with timeout=.
Prints every hit with its class, then KILLAUDIT-E198-A1 PASS (or FAIL). Exit 0 / 1. SPDX-License-Identifier: Apache-2.0
"""
import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
K = "tools/claims-v3/e198/"
CODE = (".sh", ".py", ".c", ".cpp", ".h", ".S", ".inc", ".ld")
PATS = [
    ("SIGKILL", re.compile(r"SIGKILL")),
    ("KILL", re.compile(r"\bKILL\b")),
    ("kill -9/-KILL/-s/-n", re.compile(r"\bkill\s+-(9|KILL|SIGKILL|s\s*(9|KILL|SIGKILL|\"?\$\()|n\s*(9|KILL|SIGKILL|\"?\$))")),
    ("timeout -k", re.compile(r"\btimeout\s+(-k|--kill-after|-s\s*(9|KILL)|--signal[= ](9|KILL))|-k 1\b")),
    ("\"timeout\", \"-k\"", re.compile(r"[\"']timeout[\"'],\s*[\"']-k[\"']")),
    ("kill call", re.compile(r"\.kill\(\)|\bos\.kill\(|\bos\.killpg\(|\bkillpg\b|\bpthread_kill\(")),
    ("subprocess timeout", re.compile(r"subprocess\.(run|call|check_call|check_output)\([^#\n]*timeout=|\.communicate\([^)\n]*timeout=|"
                                      r"\b(check_call|check_output)\([^)\n]*timeout=")),
    ("--die-with-parent", re.compile(r"--die-with-parent")),
    ("pkill/killall", re.compile(r"\bpkill\b|\bkillall\b")),
]
# (path regex, line regex, class, why). DOC: prose (a comment, a docstring, an echoed or printed sentence), no code. EXIST: signal 0, which
# sends nothing (a process's existence). TEXT-MATCH: the words as text a checker looks for, never run. SELF: a process re-raising on itself
# the signal its child already died of. NOTDEV: a timed child that is not a device process (it opens no device node). DESK: a desk-side
# process on aifoundry2 (an ssh, rsync or git client), never a device process. DESKTEST: a stand-in in a desk test's sandbox, never on a box.
# NOTRUN: a file the A1 path never runs (synced or kept, never executed for E198 after A1).
TABLE = [
    (r"tools/claims-v3/e198/run_x04_e198a1\.py$", r"^`timeout 10` after|E198 A1: no KILL follows|E198 A1: never a KILL|TERM at 10 s, never a KILL|is the same stop: reported at once, never killed",
     "DOC", "the runner copy's own doc lines and comments saying no KILL is sent"),
    (r"tools/claims-v3/e198/run_x04_e198a1\.py$", r"p = subprocess\.run\(\[a\.holder_check, \"--check\"\], capture_output=True, text=True, timeout=30",
     "NOTDEV", "the runner's holder check (E193's line, unchanged): Python sends its child a KILL past 30 s; the child is holdercheck_e198.sh, which opens "
     "no device node (it asks the warden outside) and ends by itself within 28 s, exit 2"),
    (r"tools/claims-v3/e198/warden_e198\.py$", r"os\.kill\(pid, 0\)", "EXIST", "signal 0: the warden reads whether the session is alive; nothing is sent"),
    (r"tools/claims-v3/e198/warden_e198\.py$", r"subprocess\.run\(\[etwho, \"--check\"\], capture_output=True, text=True, timeout=25",
     "NOTDEV", "the warden's et-who (the box's holder listing: sudo et-holders, fuser on /proc): Python sends it a KILL past 25 s; it opens no device node"),
    (r"tools/claims-v3/e198/x04host_e198\.sh$", r"^#", "DOC", "the host wrapper's header comment on the v1 runner's -k (A1 sends no KILL)"),
    (r"tools/claims-v3/e198/x04host_e198\.sh$", r'kill -s "\$\(kill -l \$\(\(rc - 128\)\)\)" "\$\$"', "SELF",
     "the host wrapper, after the host has ENDED, re-raises on its own process ($$) the signal the host died of, so timeout reads the status it would "
     "have read; it signals no device process, and it can reach a KILL only if something outside E198's code killed the host"),
    (r"tools/claims-v3/e198/privdev_e198\.sh$", r"^# .*(--die-with-parent|SIGKILL)", "DOC", "a comment: the private /dev deliberately has no --die-with-parent"),
    (r"tools/claims-v3/e198/(session_e198a1|build_e198a1)\.sh$|tools/claims-v3/e198/rb/s(08_a1_build|10_a1_dry)_e198a1\.sh$", r"^#", "DOC", "A1's header comments"),
    (r"tools/claims-v3/e198/rb/list_steps_e198a1\.sh$", r"echo; echo \"################ inside the sitting", "DOC", "an echoed sentence of the dry listing (never a KILL)"),
    (r"tools/claims-v3/e198/check_e198a1\.py$", r"timeout -k|--kill-after", "TEXT-MATCH",
     "the listing checker's doc and its text: it maps A1's `timeout 10` to E193's `timeout -k 1 10` text, and refuses a listing naming `timeout -k`"),
    (r"tools/claims-v3/q141k-runbook/v3\.1/rb_run\.py$", r"TERM then KILL 2 s later|TERM, then KILL 10 s later", "DOC", "rb_run.py's docstring"),
    (r"tools/claims-v3/q141k-runbook/v3\.1/rb_run\.py$", r"def kill_tree|for sig in \(signal\.SIGTERM, signal\.SIGKILL\)|os\.killpg\(proc\.pid, sig\)|os\.kill\(p, sig\)|kill_tree\(proc",
     "DESK", "k6's bounded runner on aifoundry2 ends a desk-side call past its bound or on a login link (TERM, then KILL): the ssh, rsync or git client "
     "and its children on the desk; no E198 device process runs on the desk, and the box side of a cut call gets no KILL (a launch has detached; a "
     "read runs under its own plain timeout)"),
    (r"tools/claims-v3/q141k-runbook/v3\.1/rb_run\.py$", r"os\.kill\(pid, 0\)", "EXIST", "signal 0 (alive?)"),
    (r"tools/claims-v3/q141k-runbook/v3\.1/rb_run\.py$", r'subprocess\.run\(\["ps", "-A"', "NOTDEV", "a desk-side ps under timeout=10"),
    (r"tools/claims-v3/e198/desk/desktest_realpath_e198a1\.py$", r".*", "DESKTEST",
     "the A1 real-path test's own words and its sandboxes (bubblewrap's --die-with-parent ends a case's stand-ins only if the test itself dies; a case past "
     "its bound gets a TERM): stand-ins over /dev/null in the no-device sandbox, never a device process, never on a box"),
    (r"tools/claims-v3/e198/rb/selftest_rb_e198a1\.sh$", r".*", "DESKTEST", "the A1 runbook test's sandbox (bubblewrap --die-with-parent) and stand-ins, desk only"),
    (r"tools/claims-v3/e198/fake_card_e198a1\.py$", r".*", "DESKTEST", "the A1 stand-ins' doc (they send no KILL; the stand-in sampler's end knob is its own TERM)"),
    (r"tools/claims-v3/e198/desk/(killaudit|make_runner)_e198a1\.py$", r".*", "TEXT-MATCH", "this audit's and the runner maker's patterns and doc: text they look for"),
    (r"tools/claims-v3/e198/desk/realbytes_e198a1\.py$", r".*", "DOC", "the real-bytes test's doc"),
    # ---- scope 2: E198's folder outside the A1 path
    (r"tools/claims-v3/e193/proposal/src/run_x04\.py$", r".*", "NOTRUN",
     "E193's runner: synced to the box as part of E193's registration, never run for E198 after A1 (the session, the build's listing and the desk tests run the lab's copy)"),
    (r"tools/claims-v3/e193/desk/compare_arms_e193\.py$", r"DEF = \"timeout -k 1 10", "TEXT-MATCH", "E193's desk arms comparer's listing text; not run on the A1 path"),
    (r"tools/claims-v3/e198/rb/s08_a1_build_e198\.sh$", r"timeout -k 15 900", "NOTRUN",
     "v1's step 6 (`timeout -k 15 900` around the build job, whose tree runs the host's refusal checks): superseded by A1's step 6 (plain `timeout 900`), never run for E198 after A1"),
    (r"tools/claims-v3/e198/rb/s08_a1_build_e198a1\.sh$", r"^# .*timeout -k 15 900", "DOC", "v1's header kept below A1's (its job name and `timeout -k 15 900` are v1's)"),
    (r"tools/claims-v3/e198/(desk/desktest_realpath_e198\.py|rb/selftest_rb_e198\.sh|fake_card_e198\.py)$", r".*", "NOTRUN",
     "v1's desk tests (stand-ins only, desk only), superseded by A1's versions"),
    (r"tools/claims-v3/e198/(session_e198|privdev_e198|build_e198)\.sh$|tools/claims-v3/e198/(dropruntime_e198|collect_e198|ident_e198|check_e198)\.py$|tools/claims-v3/e198/rb/s(11_a1_session|20_wait)_e198\.sh$",
     r"^#|^\s*#|\"\"\"|kill nothing|killed by timeout|SIGKILL and orphaning|never killed", "DOC", "v1 prose (comments, messages saying kill nothing)"),
    (r"tools/claims-v3/e198/E198\.md$|tools/claims-v3/e198/[^/]+\.md$", r".*", "DOC", "a document"),
]


def files_a1():
    h = json.load(open(os.path.join(E, "harness-e198-a1.json")))
    box = sorted(h["files"]) + ["tools/claims-v3/e191/ettelem_guard_e191.sh"]
    rb = [K + "rb/" + x for x in ("rb_e198a1.sh", "rb_e198.sh", "s02_window_e198.sh", "s03_desk_e198a1.sh", "s05_look_e198.sh", "s07_a1_sync_e198a1.sh",
                                  "s08_a1_build_e198a1.sh", "s09_a1_reads_e198.sh", "s10_a1_dry_e198a1.sh", "s11_a1_session_e198a1.sh",
                                  "s20_wait_e198a1.sh", "s22_collect_e198a1.sh", "s24_reduce_e198.sh", "check_history_e198.py", "list_steps_e198a1.sh",
                                  "selftest_rb_e198a1.sh")]
    rb += ["tools/claims-v3/q141k-runbook/k6/rb_common.sh", "tools/claims-v3/q141k-runbook/v3.1/rb_run.py",
           "tools/claims-v3/q141k-runbook/v3.1/nopath_q142s.py", "tools/claims-v3/e191/rb/rest_rule_e191.sh", K + "collect_e198.py", K + "score_e198.py"]
    desk = [K + x for x in ("desk/desktest_realpath_e198a1.py", "desk/realbytes_e198a1.py", "desk/make_runner_e198a1.py", "desk/killaudit_e198a1.py",
                            "fake_card_e198a1.py", "fake_card_e198.py")]
    return sorted(set(box + rb + desk))


def files_rest(a1):
    out = []
    for root, _dirs, fs in os.walk(os.path.join(REPO, K)):
        for f in fs:
            p = os.path.relpath(os.path.join(root, f), REPO)
            if p not in a1 and "/logs/" not in p and not f.endswith(".pyc"):
                out.append(p)
    return sorted(out)


def classify(path, line):
    for pr, lr, cls, why in TABLE:
        if re.search(pr, path) and re.search(lr, line):
            return cls, why
    return None, None


def scan(paths, scope, rows, texts):
    for p in paths:
        full = os.path.join(REPO, p)
        if not os.path.isfile(full):
            rows.append((scope, p, 0, "(missing)", "MISSING", "a file of the scope is missing"))
            continue
        lines = open(full, errors="replace").read().splitlines()
        code = p.endswith(CODE)
        for i, ln in enumerate(lines, 1):
            hit = [n for n, r in PATS if r.search(ln)]
            if not hit:
                continue
            if not code:
                texts[p] = texts.get(p, 0) + 1
                continue
            cls, why = classify(p, ln.strip())
            rows.append((scope, p, i, ln.strip()[:150], cls or "UNCLASSIFIED", why or "no row of the table reads it", ",".join(hit)))


TIMED = ("run", "call", "check_call", "check_output")
SAFE_SIGS = ("signal.SIGTERM", "signal.SIGINT", "signal.SIGHUP")


def ast_all(paths, scope, rows):
    """Item 5: every Python file read as code. A timed subprocess call, a .communicate(timeout=), a kill call or a .send_signal() of
    another signal than TERM, INT or HUP is an AST hit, classified by the table on the call's source lines joined into one."""
    n_files = 0
    for p in paths:
        if not p.endswith(".py"):
            continue
        full = os.path.join(REPO, p)
        if not os.path.isfile(full):
            continue
        src = open(full, errors="replace").read()
        try:
            t = ast.parse(src)
        except SyntaxError as e:
            rows.append((scope, p, getattr(e, "lineno", 0) or 0, "(does not parse)", "UNPARSED", str(e)[:120], "ast"))
            continue
        n_files += 1
        lines = src.splitlines()
        from_sub = {a.asname or a.name for n in ast.walk(t) if isinstance(n, ast.ImportFrom) and n.module == "subprocess" for a in n.names}
        for n in ast.walk(t):
            if not isinstance(n, ast.Call):
                continue
            f = ast.unparse(n.func)
            kws = {k.arg for k in n.keywords}
            what = None
            last = f.split(".")[-1]
            if last in TIMED and "timeout" in kws and (f.startswith("subprocess.") or f in from_sub):
                what = "subprocess timeout (ast)"
            elif last == "communicate" and "timeout" in kws:
                what = "communicate timeout (ast)"
            elif f.endswith(".kill") or f in ("os.kill", "os.killpg", "signal.pthread_kill", "killpg", "pthread_kill"):
                what = "kill call (ast)"
            elif last == "send_signal" and (not n.args or ast.unparse(n.args[0]) not in SAFE_SIGS):
                what = "send_signal (ast)"
            if what is None:
                continue
            text = re.sub(r"\s+", " ", " ".join(ln.strip() for ln in lines[n.lineno - 1:(n.end_lineno or n.lineno)])).strip()
            cls, why = classify(p, text)
            rows.append((scope, p, n.lineno, text[:150], cls or "UNCLASSIFIED", why or "no row of the table reads it", what))
    return n_files


def ast_runner():
    src = open(os.path.join(E, "run_x04_e198a1.py")).read()
    t = ast.parse(src)
    bad, notes = [], []
    dev = [n for n in ast.walk(t) if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "cmd" for x in n.targets)
           and isinstance(n.value, ast.List) and n.value.elts and isinstance(n.value.elts[0], ast.Constant) and n.value.elts[0].value == "timeout"]
    if len(dev) != 1:
        bad.append(f"{len(dev)} device command list(s) beginning 'timeout', not one")
    else:
        e = dev[0].value.elts
        first = [x.value if isinstance(x, ast.Constant) else ast.unparse(x) for x in e[:3]]
        notes.append(f"the device command: {first} ... (line {dev[0].lineno})")
        if first != ["timeout", "10", "a.host"]:
            bad.append(f"the device command begins {first}, not ['timeout', '10', 'a.host']")
    sub_t = []
    for n in ast.walk(t):
        if not isinstance(n, ast.Call):
            continue
        f = ast.unparse(n.func)
        if f.endswith(".kill") or f in ("os.kill", "os.killpg"):
            bad.append(f"line {n.lineno}: a call of {f}")
        if f.endswith(".send_signal"):
            a = ast.unparse(n.args[0]) if n.args else ""
            notes.append(f"line {n.lineno}: {f}({a})")
            if a != "signal.SIGTERM":
                bad.append(f"line {n.lineno}: {f}({a}), not SIGTERM")
        if f in ("subprocess.run", "subprocess.check_output") and any(k.arg == "timeout" for k in n.keywords):
            sub_t.append((n.lineno, ast.unparse(n.args[0]) if n.args else ""))
    notes.append(f"subprocess calls with a timeout: {sub_t}")
    if [a for _, a in sub_t] != ["[a.holder_check, '--check']"]:
        bad.append(f"timed subprocess calls {sub_t}, not the holder check's alone")
    return bad, notes


def main():
    a1 = files_a1()
    rest = files_rest(set(a1))
    rows, texts = [], {}
    scan(a1, "A1-PATH", rows, texts)
    scan(rest, "REST", rows, texts)
    na = ast_all(a1, "AST-A1", rows)
    nr = ast_all(rest, "AST-REST", rows)
    print(f"KILLAUDIT-E198-A1 ({os.uname().nodename}; python {sys.version.split()[0]}): {len(a1)} files on the A1 path, {len(rest)} more in E198's folder; "
          f"Python files read as code (ast): {na} on the A1 path, {nr} in the rest")
    for r in rows:
        print(f"  {r[0]:8s} {r[4]:12s} {r[1]}:{r[2]}: [{r[6] if len(r) > 6 else ''}] {r[3]}")
    for c in sorted({r[4] for r in rows}):
        print(f"  class {c}: {sum(1 for r in rows if r[4] == c)} hit(s)" + (f" - {next(r[5] for r in rows if r[4] == c)[:230]}" if c not in ("DOC",) else ""))
    print(f"  text files (never run) with a kill word: {len(texts)}: " + ", ".join(f"{os.path.basename(p)} {n}" for p, n in sorted(texts.items())))
    bad = [r for r in rows if r[4] in ("UNCLASSIFIED", "MISSING", "UNPARSED")]
    a1k = [r for r in rows if r[0] == "A1-PATH" and "timeout -k" in (r[6] if len(r) > 6 else "") and r[4] not in ("DOC", "TEXT-MATCH", "DESKTEST", "NOTRUN")]
    if a1k:
        bad += a1k
    rbad, notes = ast_runner()
    for n in notes:
        print("  runner (ast): " + n)
    for r in bad:
        print(f"  FAIL: {r[1]}:{r[2]}: {r[4]}: {r[3]}")
    for b in rbad:
        print(f"  FAIL (runner ast): {b}")
    dev = [r for r in rows if r[0] in ("A1-PATH", "AST-A1") and r[4] not in ("DOC", "EXIST", "TEXT-MATCH", "SELF", "NOTDEV", "DESK", "DESKTEST", "NOTRUN")]
    if not bad and not rbad and not dev:
        print(f"KILLAUDIT-E198-A1 PASS: {sum(1 for r in rows if r[0] == 'A1-PATH')} hit(s) on the A1 path and {sum(1 for r in rows if r[0] == 'REST')} in the rest "
              f"of E198's folder, every one classified, none a SIGKILL, kill -9 or timeout -k around a device process; the Python files read as code: "
              f"{sum(1 for r in rows if r[0] == 'AST-A1')} AST hit(s) on the A1 path and {sum(1 for r in rows if r[0] == 'AST-REST')} in the rest, every one "
              f"classified; the runner copy read as code: the device command is ['timeout', '10', a.host, ...], no kill call, every send_signal a SIGTERM")
        return 0
    print("KILLAUDIT-E198-A1 FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
