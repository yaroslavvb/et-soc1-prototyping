#!/usr/bin/env python3
"""E222 (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum): NO SIGKILL TOWARD A DEVICE PROCESS, read in the code - E220's widened
audit (tools/claims-v3/e220/desk/nokill_e220.py, kit 2f0ab9cd, as fix-e220 widened it on verify-e220's F4), line for line for E222's files: every
line of the kit's .py and .sh files and of the code the kit runs unchanged (k6's library and the q141k runbook folder it sits in) that could send
SIGKILL is listed, and each is CLASSED BY WHAT IT CAN REACH. A line that only STATES the rule (a comment, a docstring, a message or a test's
check naming it as never done) is listed apart. The forms read:
  - Popen.kill(); os.kill or send_signal with 9 or SIGKILL; `kill -9`, `kill -KILL`, `kill -s KILL`; `timeout -k`, `--kill-after`; `pkill -9`,
    `killall -9`;
  - (fix-e220's) os.killpg with any signal but 0 or a named signal other than KILL; os.kill and send_signal with a signal held in a VARIABLE (any
    argument but 0, 15 or a named signal other than KILL); SIGKILL named in code (signal.SIGKILL in a tuple, a list or an assignment);
    `kill -SIGKILL`, `kill -s 9`, `kill -s SIGKILL`, `kill -n 9`; `pkill`/`killall` with `-KILL`, `-SIGKILL` or `--signal KILL`;
    `timeout -s KILL` / `--signal=KILL`. Comments and docstrings are statements; the forms are matched in the code part of a line.
THE TARGETS: a sending line inside k6's runner rb_run.py's kill_tree() (any version of it in tools/claims-v3/q141k-runbook) reaches only THE
DESK'S OWN CALL TREE: rb_run.py runs every E222 runbook call on the desk (aifoundry2) in a new session of its own, and kill_tree() signals that
call's process group, its descendants by ps and the pids it saw in that group (a reused pid never), once a login link appears (KILL 2 s after
TERM) or the call passes its bound (KILL 10 s after TERM; the probe 2 s): the desk's own ssh client, rsync, git or desk Python. E222 runs no
device process on the desk (its card is aifoundry3 card 0, reached only through ssh; every device process there runs under the runner's own plain
`timeout 10`, which sends SIGTERM only, and a host alive past its TERM is HUNG, reported and left; the desk tests that run hosts or stand-ins run
inside W/nodev.sh, with no card node). Every other sending line COULD REACH A DEVICE PROCESS (want 0).
Prints, last: "NOKILL-E222: <n> lines that could send SIGKILL toward a device process (want 0); <d> lines that send SIGKILL to the desk's own
call tree only (...); <s> lines state the rule; read: ...". Exit 0 when n is 0, else 1.
    /usr/bin/python3 -I -B tools/claims-v3/e222/desk/nokill_e222.py <the lab clone>      (> logs/nokill-e222.txt)
Standard library only; reads only. SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import sys

R = sys.argv[1] if len(sys.argv) > 1 else os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
roots = [os.path.join(R, "tools/claims-v3/e222"), os.path.join(R, "tools/claims-v3/q141k-runbook")]
# kit-e220's forms, classed as kit-e220 classed them (STATE on the whole line)
SEND = re.compile(r"\.kill\(\)|os\.kill\([^)]*(SIGKILL|,\s*9\))|send_signal\([^)]*(SIGKILL|9\))|\bkill\s+-(9|KILL)\b|\bkill\s+-s\s+KILL\b|"
                  r"\btimeout\s+(-k|--kill-after)\b|\bp?kill(all)?\s+-9\b")
STATE = re.compile(r"#|never|no SIGKILL|no kill|not .*kill|\"\"\"|'never|kill -9 a|rule|words|statement", re.I)
# fix-e220's forms, matched in the CODE PART of a line (comments and docstrings removed)
SAFE_SIG = r"(?:0|15|2|1|signal\.SIG(?:TERM|INT|HUP|CONT|STOP|USR1|USR2|QUIT|ALRM)|SIG(?:TERM|INT|HUP|CONT|STOP|USR1|USR2|QUIT|ALRM))"
PYFORM = re.compile(r"os\.killpg\(\s*[^,()]+(?:\([^()]*\))?\s*,(?!\s*" + SAFE_SIG + r"\s*\))"     # os.killpg with a variable or KILL
                    r"|os\.kill\(\s*[^,()]+(?:\([^()]*\))?\s*,(?!\s*" + SAFE_SIG + r"\s*\))"      # os.kill with a variable or KILL
                    r"|\.send_signal\((?!\s*" + SAFE_SIG + r"\s*\))"                              # send_signal with a variable or KILL
                    r"|\bSIGKILL\b")                                                              # SIGKILL named in code
SHFORM = re.compile(r"\bkill\s+(?:-SIGKILL|-s\s*(?:9|SIGKILL|KILL)|-n\s*9)\b"
                    r"|\bp?kill(?:all)?\s+(?:-KILL|-SIGKILL|--signal[ =]?(?:KILL|9|SIGKILL))\b"
                    r"|\btimeout\b[^\n#]*?(?:-s\s*|--signal[ =])(?:KILL|9|SIGKILL)\b")
DEF = re.compile(r"^\s*def\s+(\w+)\s*\(")
DESK_ONLY = ("kill_tree",)          # k6's runner's kill_tree(): the desk's own call tree only (above)


def strip_strings(code):
    """the code without its string literals ('...' and "...", one line)"""
    out, q, i = [], None, 0
    while i < len(code):
        ch = code[i]
        if q:
            if ch == "\\":
                i += 2
                continue
            if ch == q:
                q = None
        elif ch in "'\"":
            q = ch
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def code_part(ln, py):
    """the line without its comment (a '#' outside quotes; in shell only at the start or after a blank)"""
    q, i = None, 0
    while i < len(ln):
        ch = ln[i]
        if q:
            if ch == "\\":
                i += 2
                continue
            if ch == q:
                q = None
        elif ch in "'\"":
            q = ch
        elif ch == "#" and (py or i == 0 or ln[i - 1] in " \t;"):
            return ln[:i]
        i += 1
    return ln


send, desk, state, nfiles = [], [], [], 0
for top in roots:
    for dp, dn, fn in os.walk(top):
        if "/logs" in dp:
            continue
        dn.sort()
        for f in sorted(fn):
            if not f.endswith((".py", ".sh")):
                continue
            p = os.path.join(dp, f)
            if os.path.realpath(p) == os.path.realpath(__file__):
                continue        # this reader's own docstring and patterns name every form it looks for
            nfiles += 1
            py = f.endswith(".py")
            in_doc, cur_def = False, None
            for i, ln in enumerate(open(p, errors="replace"), 1):
                rel = f"{os.path.relpath(p, R)}:{i}: {ln.strip()[:150]}"
                was_doc = in_doc
                if py:
                    m = DEF.match(ln)
                    if m and not in_doc:
                        cur_def = m.group(1)
                    if ln.count('"""') % 2 == 1:
                        in_doc = not in_doc
                doc_line = py and (was_doc or ('"""' in ln))
                old = bool(SEND.search(ln))
                code = "" if doc_line else code_part(ln, py)
                py_hit = py and bool(PYFORM.search(strip_strings(code)))
                sh_hit = bool(SHFORM.search(code))
                if not (old or py_hit or sh_hit):
                    continue
                if py_hit:                                   # a kill form in Python code itself: never a statement
                    if cur_def in DESK_ONLY and os.path.basename(p) == "rb_run.py" and "q141k-runbook" in p:
                        desk.append(f"{rel}   [in {cur_def}(): the desk's own call tree only]")
                    else:
                        send.append(rel)
                elif sh_hit and not STATE.search(code):      # a shell kill form in code that does not state the rule
                    send.append(rel)
                elif old and not STATE.search(ln):           # kit-e220's forms, classed as kit-e220 classed them
                    send.append(rel)
                else:
                    state.append(rel)
for x in state:
    print("states the rule:", x)
for x in desk:
    print("SENDS TO THE DESK'S OWN CALL TREE ONLY:", x)
for x in send:
    print("SENDS (could reach a device process):", x)
print(f"NOKILL-E222: {len(send)} lines that could send SIGKILL toward a device process (want 0); {len(desk)} lines that send SIGKILL to the desk's own "
      f"call tree only (k6's rb_run.py kill_tree(), TERM then KILL past a call's bound or on a login link: the desk's ssh, rsync, git or desk Python on "
      f"aifoundry2, where E222 runs no device process); {len(state)} lines state the rule; read: {nfiles} files under tools/claims-v3/e222 (the kit "
      f"and the registration) and the q141k runbook folder (k6's library and rb_run.py)")
sys.exit(0 if not send else 1)
