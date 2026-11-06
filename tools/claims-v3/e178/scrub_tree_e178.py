#!/usr/bin/env python3
"""E178 (Q146; the kit's dated note 1, KIT.md.dated-note-1.md section 3): the login scrub over EVERY directory of a collection, before
the data commit. Written Fri 6 Nov 2026, before any E178 datum.

The kit's step 22 (rb/s22_collect_e178.sh, which stays as committed) ran E164's scrub_etwho_e164.py --check on the output's logs/ only,
and that scrub reads one directory level (the kit verifier's fault 3; the card day critic's kit v4 item 2). Two holes:
  (a) nothing reads the pass directories (aifoundry3/e178/p178NN/, the smoke's and the stop-path test's), where run_e78.py writes run.log
      and STOP;
  (b) run_e78.py's own mid-pass stop line, "another user on this card: [...]" (others_on_card, unchanged since 31 Oct), is not a form
      E164's scrub knows, so its --check reads 0 left on it. Each entry of that list is "<uid>:<pid>:<comm>" when ET_DEVICES is unset
      (E178's case: session_e178.sh unsets it on aifoundry3, so run_e78 reads ps) or "<node> <login> <pid>" when it is set (et-holders).
This reads every file in every directory under <dir> (os.walk; *.gz and *.bin are skipped: compressed C logs, telemetry and tile dumps,
which carry no account) and reports, by file and line:
  - E164's leftovers, with E164's own function, unchanged (another account's et-who holder line, others-present list entry or /home path);
  - every entry of a run_e78 stop list that is not already withheld (any form it cannot read counts as left: it never under-reports).
Without --owner every login counts as another account's (the strictest reading; nothing is hidden by a missing owner).

--check rewrites nothing and exits 1 if anything is left, else 0. Without --check it rewrites in place: E164's scrub_text on each file,
and in a run_e78 stop list each uid -> <another-uid> and each login -> <another-user> (the node, pid and command kept, as E164 keeps them);
then every login seen in those places is replaced as a whole word in every text file of the tree (E164's rule, widened from one
directory to the tree), and the check is run again. Standard library and scrub_etwho_e164.py only; nothing outside <dir> is read or
written.

    python3 -B tools/claims-v3/e178/scrub_tree_e178.py --check <dir> [--owner LOGIN]
    python3 -B tools/claims-v3/e178/scrub_tree_e178.py <dir> [--owner LOGIN]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e164"))
import scrub_etwho_e164 as S  # noqa: E402  (E164's patterns and functions, unchanged: 45aeda12)

STOPLIST = re.compile(r"another user on this card: \[(?P<body>[^\]]*)\]")
ENTRY = re.compile(r"'(?P<a>[^']*)'|\"(?P<b>[^\"]*)\"")
PS_FORM = re.compile(r"^(?P<uid>[^:\s]+):(?P<pid>\d+):(?P<comm>.*)$")
SKIP_EXT = (".gz", ".bin")


def files_under(top):
    for root, dirs, files in os.walk(top):
        dirs.sort()
        for name in sorted(files):
            p = os.path.join(root, name)
            if os.path.isfile(p) and not os.path.islink(p) and not name.endswith(SKIP_EXT):
                yield p


def stop_entries(line):
    """[(entry text, (start, end) in the line)] for every entry of every run_e78 stop list in the line"""
    out = []
    for m in STOPLIST.finditer(line):
        base = m.start("body")
        for e in ENTRY.finditer(m.group("body")):
            g = "a" if e.group("a") is not None else "b"
            out.append((e.group(g), (base + e.start(g), base + e.end(g))))
    return out


def entry_left(e, owner):
    """True if the entry still names another account (a uid or a login); unreadable entries count as left"""
    t = e.strip()
    if t.startswith("et-holders unreadable"):
        return False                                 # run_e78's own message when sudo -n fails: names no one
    m = PS_FORM.match(t)
    if m:
        return m.group("uid") != S.OTHER_UID
    f = t.split()
    if len(f) >= 2 and (f[0].startswith("/dev/et") or f[0].startswith("lock:")):
        return S.other(f[1], owner)
    return True


def entry_scrubbed(e, owner, others):
    t = e.strip()
    m = PS_FORM.match(t)
    if m:
        return f"{S.OTHER_UID}:{m.group('pid')}:{m.group('comm')}"
    f = t.split()
    if len(f) >= 2 and (f[0].startswith("/dev/et") or f[0].startswith("lock:")):
        if S.other(f[1], owner):
            S.note(others, f[1])
            f[1] = S.OTHER
        return " ".join(f)
    return e


def check_text(txt, owner):
    bad = [(n, w) for n, w in S.leftovers(txt, owner)]
    for n, ln in enumerate(txt.split("\n"), 1):
        bad += [(n, "uid or login in run_e78's stop list") for e, _ in stop_entries(ln) if entry_left(e, owner)]
    return sorted(bad)


def scrub_stop_lines(txt, owner, others):
    lines = txt.split("\n")
    for i, ln in enumerate(lines):
        ents = stop_entries(ln)
        for e, (a, b) in reversed(ents):              # right to left, so earlier offsets stay valid
            ln = ln[:a] + entry_scrubbed(e, owner, others) + ln[b:]
        lines[i] = ln
    return "\n".join(lines)


def run_check(top, owner):
    bad, nf, dirs = [], 0, set()
    for p in files_under(top):
        nf += 1
        dirs.add(os.path.dirname(p))
        bad += [(os.path.relpath(p, top), n, w) for n, w in check_text(S.read(p)[0], owner)]
    return bad, nf, len(dirs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--owner", default="")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not os.path.isdir(a.dir):
        print(f"scrub-tree: no directory {a.dir}")
        sys.exit(3)
    owner = a.owner
    if not a.check:
        others, texts = set(), {}
        for p in files_under(a.dir):
            b = open(p, "rb").read()
            try:
                txt, enc = b.decode("utf-8"), "utf-8"
            except UnicodeDecodeError:
                continue                              # never rewrite a file that is not UTF-8 text
            new = scrub_stop_lines(S.scrub_text(txt, owner, others), owner, others)
            texts[p] = (txt, new, enc)
        if others:
            rx = re.compile(r"(?<![\w.-])(" + "|".join(re.escape(o) for o in sorted(others, key=len, reverse=True)) + r")(?![\w-])")
            texts = {p: (t, rx.sub(S.OTHER, s), e) for p, (t, s, e) in texts.items()}
        changed = []
        for p, (txt, new, enc) in texts.items():
            if new != txt:
                with open(p, "wb") as f:
                    f.write(new.encode(enc))
                changed.append(os.path.relpath(p, a.dir))
        print(f"scrub-tree: rewrote {len(changed)} file(s): {', '.join(changed) if changed else 'none'}; "
              f"{len(others)} other account(s) seen (not named)")
    bad, nf, nd = run_check(a.dir, owner)
    for f, n, w in bad:
        print(f"scrub-tree: {f}:{n}: another account's {w} is left")
    print(f"scrub-tree: {'FAIL' if bad else 'OK'} ({nf} files in {nd} directories read, {len(bad)} left)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
