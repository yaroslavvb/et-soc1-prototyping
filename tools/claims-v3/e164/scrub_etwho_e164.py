#!/usr/bin/env python3
"""E164 (Q141(b)'s fix pass, Wed 4 Nov 2026, before any E164 data; README.md.dated-note.md § 2): take other people's logins out of the
session logs before they enter the public lab repo, and keep a count of who held what, by card, without names.

session_e164.sh appends et-who's output to build/e164/session.log at the session's start and end, and a block that finds someone on card 1
logs lib.sh's or block_e164.sh's "others present: ..." line there too. pull_e164.sh copies those logs to the Intel and collect_e164.sh
copies them into the data directory. et-who's holder lines carry a login, a pid, an elapsed time and a command line
(tools/lab/et-holders: `printf '%-14s %s' <node or lock> "$(ps -o user:14=,pid=,etime=,args=)"`). This keeps every line that names
nobody, keeps the owner's own holder lines, and rewrites every other account's:

  - an et-who holder line of another login:    the login -> `<another-user>`, the command -> `<command withheld>` (node, pid, time kept);
  - "others present: ... holders=[login:pid ...]" (block_e164.sh, hl/block.sh) and "users=[holders:login:pid ...]" (lib.sh):
                                                another login -> `<another-user>`;
  - "procs=[uid:pid:comm ...]" (only other users' processes are listed there): the uid -> `<another-uid>`;
  - `/home/<login>/` of another login:          `/home/<another-user>/`;
  - then any other whole-word occurrence, in any file of the directory, of a login seen in those places (not `root`, not a number):
                                                `<another-user>`.

The owner is `--owner LOGIN`, or else the one login in the session's own paths (`/home/<login>/nekko/`, written by lib.sh's block lines);
none or several and no --owner: it refuses (exit 2). `--check` rewrites nothing and exits 1 if any other login is left in a holder line,
an others-present list or a /home path. A summary of every et-who reading (counts by card, ours and another user's, no names) is written
to <dir>/et-who-summary.txt unless --check. Standard library only; text files only; nothing outside <dir> is read or written.

    python3 -B tools/claims-v3/e164/scrub_etwho_e164.py <logs dir> [--owner LOGIN]
    python3 -B tools/claims-v3/e164/scrub_etwho_e164.py --check <logs dir> [--owner LOGIN]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import os
import re
import sys

OTHER = "<another-user>"
OTHER_UID = "<another-uid>"
WITHHELD = "<command withheld>"
NONE_LINE = "No process holds an ET-SoC-1 device node or card lock."
SUMMARY = "et-who-summary.txt"
# et-holders: '%-14s %s' of the node (/dev/et<N>_mgmt|ops) or lock:<file>, then ps's user (14 wide), pid, etime and args
HOLDER = re.compile(r"^(?P<lead>\s*)(?P<node>/dev/et\d+_\S+|lock:\S+)(?P<s1>\s+)(?P<user>\S+)(?P<s2>\s+)(?P<pid>\d+)(?P<s3>\s+)"
                    r"(?P<etime>[\d:.-]+)(?P<rest>.*)$")
LIST = re.compile(r"(?P<key>holders|users|procs)=\[(?P<body>[^\]]*)\]")
HOME = re.compile(r"/home/(?P<login>[^/\s\]\[:'\"]+)/")
NEKKO = re.compile(r"/home/(?P<login>[^/\s\]\[:'\"<>]+)/nekko/")
PLACEHOLDERS = {OTHER, OTHER_UID}


def files_in(d):
    for name in sorted(os.listdir(d)):
        p = os.path.join(d, name)
        if os.path.isfile(p) and not os.path.islink(p) and name != SUMMARY:
            yield p


def read(p):
    b = open(p, "rb").read()
    try:
        return b.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return b.decode("latin-1"), "latin-1"


def owner_of(d, given):
    if given:
        return given
    seen = set()
    for p in files_in(d):
        seen.update(m.group("login") for m in NEKKO.finditer(read(p)[0]))
    if len(seen) != 1:
        print(f"scrub_etwho_e164: the owner's login is not settled by the logs ({len(seen)} found in /home/<login>/nekko/ paths): "
              "pass --owner LOGIN", file=sys.stderr)
        sys.exit(2)
    return seen.pop()


def other(login, owner):
    return login != owner and login not in PLACEHOLDERS and not login.startswith("<")


def note(others, login):
    if login != "root" and not login.isdigit():   # a system account or a bare uid is never matched as a word elsewhere
        others.add(login)


def scrub_list(key, body, owner, others):
    out = []
    for tok in body.split():
        parts = tok.split(":")
        if key == "procs" and len(parts) >= 3:          # uid:pid:comm, other users' processes only (lib.sh, block_e164.sh)
            parts[0] = OTHER_UID
        elif key == "holders" and len(parts) >= 2:      # login:pid
            if other(parts[0], owner):
                note(others, parts[0])
                parts[0] = OTHER
        elif key == "users":                            # lib.sh: 'holders:login:pid ...' with V3_DEVICE, or plain logins without
            i = 1 if parts[0] == "holders" and len(parts) >= 2 else 0
            if other(parts[i], owner):
                note(others, parts[i])
                parts[i] = OTHER
        out.append(":".join(parts))
    return " ".join(out) + (" " if body.endswith(" ") else "")


def scrub_text(txt, owner, others):
    lines = txt.split("\n")
    for i, ln in enumerate(lines):
        m = HOLDER.match(ln)
        if m and other(m.group("user"), owner):
            note(others, m.group("user"))
            ln = f"{m.group('lead')}{m.group('node')}{m.group('s1')}{OTHER}{m.group('s2')}{m.group('pid')}{m.group('s3')}{m.group('etime')} {WITHHELD}"
        if "others present" in ln:
            ln = LIST.sub(lambda x: f"{x.group('key')}=[{scrub_list(x.group('key'), x.group('body'), owner, others)}]", ln)

        def home(x):
            lg = x.group("login")
            if not other(lg, owner):
                return x.group(0)
            note(others, lg)
            return f"/home/{OTHER}/"
        lines[i] = HOME.sub(home, ln)
    return "\n".join(lines)


def leftovers(txt, owner):
    bad = []
    for n, ln in enumerate(txt.split("\n"), 1):
        m = HOLDER.match(ln)
        if m and other(m.group("user"), owner):
            bad.append((n, "holder line"))
        if "others present" in ln:
            for x in LIST.finditer(ln):
                for tok in x.group("body").split():
                    parts = tok.split(":")
                    if x.group("key") == "procs" and len(parts) >= 3 and parts[0] != OTHER_UID:
                        bad.append((n, "procs uid"))
                    elif x.group("key") == "holders" and len(parts) >= 2 and other(parts[0], owner):
                        bad.append((n, "holders login"))
                    elif x.group("key") == "users":
                        j = 1 if parts[0] == "holders" and len(parts) >= 2 else 0
                        if other(parts[j], owner):
                            bad.append((n, "users login"))
        bad += [(n, "/home path") for x in HOME.finditer(ln) if other(x.group("login"), owner)]
    return bad


def summary(txt, owner):
    """Each et-who reading in the file: a run of holder lines, or the 'No process holds' line, counted by card; no names."""
    out, run = [], []

    def flush():
        if run:
            c = {}
            for _, m in run:
                card = re.match(r"/dev/et(\d+)_|lock:etsoc-shire(\d+)\.lock$", m.group("node"))
                k = f"card {card.group(1) or card.group(2)}" if card else "other node or lock"
                who = "ours" if m.group("user") == owner else "another user"
                c[(k, who)] = c.get((k, who), 0) + 1
            out.append((run[0][0], "held: " + ", ".join(f"{k} {w} {v}" for (k, w), v in sorted(c.items()))))
    for n, ln in enumerate(txt.split("\n"), 1):
        m = HOLDER.match(ln)
        if m:
            run.append((n, m))
            continue
        flush()
        run = []
        if ln.strip() == NONE_LINE:
            out.append((n, "no holder on either card"))
    flush()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--owner")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    owner = owner_of(a.dir, a.owner)
    if a.check:
        bad = []
        for p in files_in(a.dir):
            bad += [(os.path.basename(p), n, w) for n, w in leftovers(read(p)[0], owner)]
        for f, n, w in bad:
            print(f"scrub check: {f}:{n}: another account's {w} is left")
        print(f"scrub check: {'FAIL' if bad else 'OK'} ({len(bad)} left)")
        sys.exit(1 if bad else 0)
    others, changed, readings, texts = set(), [], [], {}
    for p in files_in(a.dir):
        txt, enc = read(p)
        texts[p] = (txt, scrub_text(txt, owner, others), enc)
    if others:   # a login seen in a holder line, a list or a path: every other whole-word occurrence, in every file
        rx = re.compile(r"(?<![\w.-])(" + "|".join(re.escape(o) for o in sorted(others, key=len, reverse=True)) + r")(?![\w-])")
        texts = {p: (t, rx.sub(OTHER, s), e) for p, (t, s, e) in texts.items()}
    for p, (txt, new, enc) in texts.items():
        readings += [(os.path.basename(p), n, s) for n, s in summary(txt, owner)]
        if new != txt:
            with open(p, "wb") as f:
                f.write(new.encode(enc))
            changed.append(os.path.basename(p))
    with open(os.path.join(a.dir, SUMMARY), "w") as f:
        f.write("E164: every et-who reading in the session's logs, counted by card (scrub_etwho_e164.py; no names)\n")
        for name, n, s in readings:
            f.write(f"{name}:{n}: {s}\n")
    print(f"scrub: {len(changed)} file(s) rewritten ({', '.join(changed) or 'none'}); {len(others)} other login(s) replaced as words; "
          f"{len(readings)} et-who reading(s) summarised in {SUMMARY}")


if __name__ == "__main__":
    main()
