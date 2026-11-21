#!/usr/bin/env python3
"""E224's KIT DATED NOTE 1 (lane fix-e224, round Q237, Fri 20 Nov 2026, before any E224 datum; verify-e224's finding 6): THE NO-KILL AUDIT
WITH EVERY FORM DECIDED ON A LINE'S CODE PART. The kit's own reader (tools/claims-v3/e224/desk/nokill_e224.py, unchanged, still in the kit's
list) classes a line that holds one of kit-e224's old forms as a statement whenever the WHOLE LINE matches its STATE words ('#', 'never',
'rule', 'words' ...), so a real kill with a trailing comment, or with a code token such as '--rules', read as a statement (verify-e224's
mutations M4, M4c and M4d). This reader, standard library only and read only:
  1. splits each line into its parts - code, string literals, comment and (Python) docstring - tracking triple-quoted blocks across lines and
     telling a docstring (a triple-quoted string standing alone at the start of its line) from a string constant (one assigned, passed or
     listed: read as a string);
  2. matches the forms in the code part WITH its string literals (a command handed to a shell sits in a string): kit-e224's old forms,
     fix-e220's shell forms and, new here, argv lists (a 'timeout' token followed in the same list by '-k', '--kill-after', '-s KILL' or
     '--signal=KILL'; a 'kill', 'pkill' or 'killall' token followed by '-9', '-KILL', '-SIGKILL' or '-s KILL'); and fix-e220's Python forms
     (os.kill, os.killpg or send_signal with a variable or KILL; SIGKILL named in code) in the code part WITHOUT its string literals;
  3. decides each hit by WHERE IT STANDS: in code -> SENDS, whatever words the line holds; in a string literal -> a statement only when a
     statement word stands before the hit inside that same string ('never kill -9', 'no SIGKILL, kill -9 or timeout -k'), or, in a .py file,
     when the string holds nothing but the form itself (a needle searched for, as in ("kill -9", "timeout -k")); else SENDS (a command
     string); an argv list -> SENDS; in a comment or a docstring -> a statement.
THE TARGETS are kit-e224's (fix-e220's): a Python-form line inside k6's rb_run.py kill_tree() (any version under tools/claims-v3/q141k-runbook)
reaches only the desk's own call tree; every other sending line COULD REACH A DEVICE PROCESS (want 0). THE ROOTS: kit-e224's three
(tools/claims-v3/e224 both arms and A2, E208's runner src/, the q141k runbook folder) and, widened here, tools/claims-v3/fwgate (the reboot
gate both arms run on their boxes). Folders named logs are not read (as kit-e224's reader). Known limits: a kill assembled from pieces held in
variables, a needle string later joined into a command in a .py file, a multi-line shell string, a triple-quoted string standing alone at its
line's start (read as a docstring even where it is a value), and code this reader does not read.
Prints every hit with its class and reason, then, last: "NOKILL-E224-NOTE1: <n> lines that could send SIGKILL toward a device process (want
0); <d> lines that send SIGKILL to the desk's own call tree only (...); <s> lines state the rule (...); read: ...". Exit 0 when n is 0, else 1.
    /usr/bin/python3 -I -B tools/claims-v3/e224-notes/nokill_e224_note1.py <the lab clone> [--json <file>]
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import re
import sys

ROOTS = ("tools/claims-v3/e224", "tools/claims-v3/e208/proposal/src", "tools/claims-v3/q141k-runbook", "tools/claims-v3/fwgate")
# kit-e224's old forms (tools/claims-v3/e224/desk/nokill_e224.py SEND, byte for byte)
SEND = re.compile(r"\.kill\(\)|os\.kill\([^)]*(SIGKILL|,\s*9\))|send_signal\([^)]*(SIGKILL|9\))|\bkill\s+-(9|KILL)\b|\bkill\s+-s\s+KILL\b|"
                  r"\btimeout\s+(-k|--kill-after)\b|\bp?kill(all)?\s+-9\b")
# fix-e220's forms (nokill_e224.py SAFE_SIG, PYFORM and SHFORM, byte for byte)
SAFE_SIG = r"(?:0|15|2|1|signal\.SIG(?:TERM|INT|HUP|CONT|STOP|USR1|USR2|QUIT|ALRM)|SIG(?:TERM|INT|HUP|CONT|STOP|USR1|USR2|QUIT|ALRM))"
PYFORM = re.compile(r"os\.killpg\(\s*[^,()]+(?:\([^()]*\))?\s*,(?!\s*" + SAFE_SIG + r"\s*\))"
                    r"|os\.kill\(\s*[^,()]+(?:\([^()]*\))?\s*,(?!\s*" + SAFE_SIG + r"\s*\))"
                    r"|\.send_signal\((?!\s*" + SAFE_SIG + r"\s*\))"
                    r"|\bSIGKILL\b")
SHFORM = re.compile(r"\bkill\s+(?:-SIGKILL|-s\s*(?:9|SIGKILL|KILL)|-n\s*9)\b"
                    r"|\bp?kill(?:all)?\s+(?:-KILL|-SIGKILL|--signal[ =]?(?:KILL|9|SIGKILL))\b"
                    r"|\btimeout\b[^\n#]*?(?:-s\s*|--signal[ =])(?:KILL|9|SIGKILL)\b")
# new here: argv lists (string tokens of one list or tuple, in code)
Q = r"""(["'])"""
ARGV = re.compile(Q + r"timeout\1[^\]\)]*?" + r"""(["'])(?:-k|--kill-after(?:=[^"']*)?)\2"""
                  r"|" + r"""(["'])timeout\3[^\]\)]*?(["'])(?:-s|--signal)\4\s*,\s*(["'])(?:KILL|9|SIGKILL)\5"""
                  r"|" + r"""(["'])timeout\6[^\]\)]*?(["'])--signal=(?:KILL|9|SIGKILL)\7"""
                  r"|" + r"""(["'])(?:kill|pkill|killall)\8\s*,\s*(["'])-(?:9|KILL|SIGKILL)\9"""
                  r"|" + r"""(["'])(?:kill|pkill|killall)\10\s*,\s*(["'])(?:-s|-n|--signal)\11\s*,\s*(["'])(?:9|KILL|SIGKILL)\12"""
                  r"|" + r"""(["'])(?:kill|pkill|killall)\13\s*,\s*(["'])--signal=(?:9|KILL|SIGKILL)\14""")
STMT = re.compile(r"\b(?:never|no|not|nor|without|rule|rules|words|statement|statements|forbid\w*|ban|banned)\b", re.I)
DEF = re.compile(r"^\s*def\s+(\w+)\s*\(")
DESK_ONLY = ("kill_tree",)          # k6's runner's kill_tree(): the desk's own call tree only (kit-e224's reading, unchanged)


def find_close(ln, i, q):
    """the index just past the closing quote q (one or three characters) from i, backslash escapes skipped; -1 if the line has none"""
    while i < len(ln):
        if ln[i] == "\\":
            i += 2
            continue
        if ln.startswith(q, i):
            return i + len(q)
        i += 1
    return -1


def py_segments(ln, state):
    """(parts, state) for one Python line: parts are (kind, start, end) with kind 'code', 'str', 'com' or 'doc'; state carries a
    triple-quoted block across lines: None or (quote, kind)"""
    parts, i, n = [], 0, len(ln)
    if state:
        q3, kind = state
        j = find_close(ln, 0, q3)
        if j < 0:
            return [(kind, 0, n)], state
        parts.append((kind, 0, j))
        i = j
    cs = i
    while i < n:
        ch = ln[i]
        if ch == "#":
            if cs < i:
                parts.append(("code", cs, i))
            parts.append(("com", i, n))
            return parts, None
        if ch in "'\"":
            if cs < i:
                parts.append(("code", cs, i))
            if ln.startswith(ch * 3, i):
                kind = "doc" if ln[:i].strip() == "" else "str"
                j = find_close(ln, i + 3, ch * 3)
                if j < 0:
                    parts.append((kind, i, n))
                    return parts, (ch * 3, kind)
            else:
                j = find_close(ln, i + 1, ch)
                if j < 0:
                    j = n
                kind = "str"
            parts.append((kind, i, j))
            i = cs = j
            continue
        i += 1
    if cs < n:
        parts.append(("code", cs, n))
    return parts, None


def sh_segments(ln):
    """the parts of one shell line: a comment from a '#' at the line's start or after a blank, ';', '(', '|' or '&' outside quotes;
    '...' and "..." strings; the rest code"""
    parts, i, n, cs = [], 0, len(ln), 0
    while i < n:
        ch = ln[i]
        if ch == "\\":
            i += 2
            continue
        if ch == "#" and (i == 0 or ln[i - 1] in " \t;(|&"):
            if cs < i:
                parts.append(("code", cs, i))
            parts.append(("com", i, n))
            return parts
        if ch in "'\"":
            if cs < i:
                parts.append(("code", cs, i))
            if ch == "'":
                j = ln.find("'", i + 1)
                j = n if j < 0 else j + 1
            else:
                j = find_close(ln, i + 1, '"')
                j = n if j < 0 else j
            parts.append(("str", i, j))
            i = cs = j
            continue
        i += 1
    if cs < n:
        parts.append(("code", cs, n))
    return parts


def blank(ln, parts, keep):
    """the line with every part whose kind is not in keep replaced by blanks (positions kept)"""
    out = list(ln)
    for kind, a, b in parts:
        if kind not in keep:
            for k in range(a, min(b, len(out))):
                if out[k] != "\n":
                    out[k] = " "
    return "".join(out)


def part_at(parts, p):
    for kind, a, b in parts:
        if a <= p < b:
            return kind, a, b
    return "code", p, p


def in_string(ln, part, m, py):
    """a hit inside a string literal: its reason if a statement, else None"""
    _, a, b = part
    if STMT.search(ln[a:m.start()]):
        return "a string with a statement word before the form"
    if py:
        body = ln[a:b].strip()
        body = re.sub(r"""^[rRbBuUfF]*("{3}|'{3}|"|')""", "", body)
        body = re.sub(r"""("{3}|'{3}|"|')$""", "", body)
        if body.strip(" `") == m.group(0).strip():
            return "a needle (a string holding the form alone)"
    return None


def audit(R, skip=None):
    send, desk, state = [], [], []
    for top in ROOTS:
        base_dir = os.path.join(R, top)
        for dp, dn, fn in os.walk(base_dir):
            if "/logs" in dp:
                continue
            dn.sort()
            for f in sorted(fn):
                if not f.endswith((".py", ".sh")):
                    continue
                p = os.path.join(dp, f)
                if skip and os.path.realpath(p) == os.path.realpath(skip):
                    continue
                py = f.endswith(".py")
                st, cur_def = None, None
                for i, ln in enumerate(open(p, errors="replace"), 1):
                    ln = ln.rstrip("\n")
                    if py:
                        was = st
                        parts, st = py_segments(ln, st)
                        m = DEF.match(ln)
                        if m and not was:
                            cur_def = m.group(1)
                    else:
                        parts = sh_segments(ln)
                    full_hits = [(m, "old") for m in SEND.finditer(ln)] + [(m, "shell") for m in SHFORM.finditer(ln)] + \
                                [(m, "argv") for m in ARGV.finditer(ln)] + ([(m, "python") for m in PYFORM.finditer(ln)] if py else [])
                    if not full_hits:
                        continue
                    rel = f"{os.path.relpath(p, R)}:{i}: {ln.strip()[:150]}"
                    codestr = blank(ln, parts, ("code", "str"))
                    codeonly = blank(ln, parts, ("code",))
                    sends, reasons = [], []
                    for rx, form in ((SEND, "old"), (SHFORM, "shell"), (ARGV, "argv")):
                        for m in rx.finditer(codestr):
                            kind = part_at(parts, m.start())
                            if form == "argv" or kind[0] == "code":
                                sends.append(f"{form} form in code: {m.group(0)[:40]!r}")
                            elif kind[0] == "str":
                                why = in_string(ln, kind, m, py)
                                if why:
                                    reasons.append(why)
                                else:
                                    sends.append(f"{form} form in a string with no statement word before it: {m.group(0)[:40]!r}")
                    pyhit = py and bool(PYFORM.search(codeonly))
                    if pyhit:
                        if cur_def in DESK_ONLY and os.path.basename(p) == "rb_run.py" and "q141k-runbook" in p:
                            desk.append({"line": rel, "def": cur_def})
                            continue
                        sends.append("python form in code")
                    if sends:
                        send.append({"line": rel, "why": sends})
                        continue
                    if not reasons:
                        kinds = {part_at(parts, m.start())[0] for m, _ in full_hits}
                        if "code" in kinds or ("str" in kinds and not py):
                            # a form seen on the whole line from a code position (or in a shell string) that the parts did not
                            # reproduce: never taken for a statement
                            send.append({"line": rel, "why": ["a form on the whole line, from code or a shell string, not decided by "
                                                              "its parts (taken as sending)"]})
                            continue
                        if "str" in kinds:
                            reasons.append("SIGKILL named in a Python string (text)")
                        elif "doc" in kinds:
                            reasons.append("a docstring")
                        else:
                            reasons.append("a comment")
                    state.append({"line": rel, "why": sorted(set(reasons))})
    return send, desk, state


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    R = argv[0]
    send, desk, state = audit(R, skip=__file__)
    by = {}
    for x in state:
        for w in x["why"]:
            by[w] = by.get(w, 0) + 1
    for x in state:
        print(f"states the rule ({'; '.join(x['why'])}): {x['line']}")
    for x in desk:
        print(f"SENDS TO THE DESK'S OWN CALL TREE ONLY: {x['line']}   [in {x['def']}(): the desk's own call tree only]")
    for x in send:
        print(f"SENDS (could reach a device process; {'; '.join(x['why'])}): {x['line']}")
    print(f"NOKILL-E224-NOTE1: {len(send)} lines that could send SIGKILL toward a device process (want 0); {len(desk)} lines that send SIGKILL "
          f"to the desk's own call tree only (k6's rb_run.py kill_tree(), TERM then KILL past a call's bound or on a login link: the desk's "
          f"ssh, rsync, git or desk Python); {len(state)} lines state the rule ("
          + ", ".join(f"{k}: {v}" for k, v in sorted(by.items())) + "); read: " + ", ".join(ROOTS) + " (every .py and .sh file, logs folders not read)")
    if "--json" in argv:
        json.dump({"send": send, "desk": desk, "state": state}, open(argv[argv.index("--json") + 1], "w"), indent=1, sort_keys=True)
    return 0 if not send else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
