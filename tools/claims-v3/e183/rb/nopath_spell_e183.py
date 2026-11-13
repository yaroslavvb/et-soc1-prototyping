#!/usr/bin/env python3
"""E183 (the kit's dated note 5, KIT.md.dated-note-5.md, Fri 13 Nov 2026, before any E183 datum; added by the lane fix-note5 of Q170 after
the verifier verify-note5): the second half of step 11 v3's desk-path gate (rb/nopath_desk_e183.sh), for a desk whose home has the box
account's shape. The first half is v3.1's nopath_q142s.py, unchanged, with each entry of the desk's home forbidden by name; this file
catches what those names cannot:

  1. a path written from the desk's home with a '.', '..' or empty component (<home>/../<login>/x, <home>/./x, <home>//x,
     <home>/<tree>/../x, <home>/<tree>/build/../../x, and the home's own directory spelled so, /home//<login>/x or /home/./<login>/x)
     that resolves, lexically, under the home and outside the box's tree. A path that resolves inside the tree passes, however it is
     spelled (<home>/<tree>/build/../include), and so does the home itself (HOME=<home>);
  2. a path under an entry of the desk's home that the gate cannot forbid by name: a symbolic link (nopath would also forbid its target),
     or a name that begins the box's tree (nopath matches substrings, so <home>/a would match <home>/aifoundry/...). Here it is matched as
     a whole path component, so <home>/a/x stops and <home>/aifoundry/x does not.

    python3 -B nopath_spell_e183.py --home <a spelling of the desk's home> [--home ...] --tree <the box's tree, e.g. aifoundry>
        [--left-out <entry name>] ... <file or dir> ...

It reads every file under the paths given as nopath does (a .gz file decompressed, a symbolic link skipped, a path that is not there a
hit), cuts each place where a spelling of the home occurs into a path (up to the next blank, quote, bracket or separator), and prints one
HIT line per file and kind (the file, what was found, how many times; never the text around it). Exit 3 on any hit, 0 when clean, 2 on a
usage error. Standard library only; it reads, and never writes, anything it scans.
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import os
import posixpath
import re
import sys

# A path ends at one of these bytes (blanks, quotes, brackets, separators): what a log, a JSON or CSV file or a shell line puts around it.
DELIM = re.compile(rb"[\s\x00'\"`<>|;,(){}\[\]=:&*?!$\\^]")
BACK = 4096  # at most this many bytes are read back from a match to the start of its path

WHY_SPELL = "a path under the desk's home written with '.', '..' or '//', outside the box's tree"
WHY_LEFT = "a path under an entry of the desk's home the gate leaves out by name (a link, or a name that begins the box's tree)"


def norm(p):
    """The path as written, lexically resolved: leading slashes made one (POSIX keeps a leading '//'), then posixpath.normpath."""
    return posixpath.normpath(re.sub(rb"^/{2,}", b"/", p))


def under(p, top):
    return p == top or p.startswith(top + b"/")


def path_end(blob, i):
    m = DELIM.search(blob, i)
    return m.start() if m else len(blob)


def path_start(blob, i):
    s = i
    lim = max(0, i - BACK)
    while s > lim and not DELIM.match(blob, s - 1):
        s -= 1
    return s


def judge(p, homes, left_out):
    """The kinds found in one path p, which begins with a spelling of the home or holds the home's last component."""
    kinds = set()
    n = norm(p)
    plain = n == p.rstrip(b"/") and not p.startswith(b"//")
    for h, tree in homes:
        if not under(n, h) or n == h:
            continue
        if not plain and not under(n, tree):
            kinds.add(WHY_SPELL)
        for x in left_out:
            if under(n, h + b"/" + x):
                kinds.add(WHY_LEFT)
    return kinds


def scan(blob, homes, left_out):
    found = {}
    seen = set()
    for h, _tree in homes:
        # 1. each place the home is written as is, cut from there to the path's end
        for m in re.finditer(re.escape(h), blob):
            j = m.end()
            if j < len(blob) and blob[j:j + 1] != b"/" and not DELIM.match(blob, j):
                continue                                   # <home>2/...: another name
            key = m.start()                                # a path is judged once, by where it starts
            if key in seen:
                continue
            seen.add(key)
            for k in judge(blob[m.start():path_end(blob, j)], homes, left_out):
                found[k] = found.get(k, 0) + 1
        # 2. each place the home's last component is written as a path component: the whole path around it, when it is not plain
        last = b"/" + h.rsplit(b"/", 1)[-1]
        for m in re.finditer(re.escape(last), blob):
            j = m.end()
            if j < len(blob) and blob[j:j + 1] != b"/" and not DELIM.match(blob, j):
                continue
            s = path_start(blob, m.start())
            key = s
            if key in seen:
                continue
            seen.add(key)
            p = blob[s:path_end(blob, j)]
            if norm(p) == p.rstrip(b"/") and not p.startswith(b"//"):
                continue                                   # plain: the first pass and nopath's names read it
            for k in judge(p, homes, left_out):
                found[k] = found.get(k, 0) + 1
    return found


def read(path):
    if path.endswith(".gz"):
        with gzip.open(path, "rb") as f:
            return f.read()
    with open(path, "rb") as f:
        return f.read()


def main(argv):
    homes, tree, left_out, paths, i = [], None, [], [], 0
    while i < len(argv):
        a = argv[i]
        if a in ("--home", "--tree", "--left-out") and i + 1 < len(argv):
            v = argv[i + 1]
            if a == "--home":
                homes.append(v)
            elif a == "--tree":
                tree = v
            else:
                left_out.append(v)
            i += 2
            continue
        paths.append(a)
        i += 1
    bad = (not paths or not homes or not tree or "/" in tree or tree in (".", "..")
           or any(not h.startswith("/") or h.rstrip("/") in ("", "/") for h in homes)
           or any(not x or "/" in x or x in (".", "..") for x in left_out))
    if bad:
        print("usage: nopath_spell_e183.py --home <absolute path> [--home ...] --tree <name> [--left-out <name>] ... <file or dir> ...")
        return 2
    hs = []
    for h in homes:
        hb = norm(h.encode())
        if hb not in [x for x, _ in hs]:
            hs.append((hb, hb + b"/" + tree.encode()))
    lo = sorted({x.encode() for x in left_out})
    files, hits, missing = 0, 0, []
    for top in paths:
        if not os.path.exists(top):
            missing.append(top)
            continue
        walk = [(os.path.dirname(top), [], [os.path.basename(top)])] if os.path.isfile(top) else os.walk(top)
        for d, _, fs in walk:
            for fn in sorted(fs):
                p = os.path.join(d, fn)
                if os.path.islink(p):
                    continue
                try:
                    blob = read(p)
                except (OSError, EOFError) as e:
                    print(f"UNREAD {p}: {type(e).__name__}")
                    hits += 1
                    continue
                files += 1
                for why, c in sorted(scan(blob, hs, lo).items()):
                    print(f"HIT {p}: {why} ({c} times)")
                    hits += 1
    for m in missing:
        print(f"MISSING {m}: nothing there to read (a hit: the gate never passes an output it did not read)")
        hits += 1
    print(f"nopath_spell: {files} files read under {len(paths) - len(missing)} path(s); {len(hs)} spelling(s) of the home, "
          f"{len(lo)} entr{'y' if len(lo) == 1 else 'ies'} left out by name; {len(missing)} missing; {hits} hit(s): "
          f"{'CLEAN' if not hits else 'NOT CLEAN'}")
    return 3 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
