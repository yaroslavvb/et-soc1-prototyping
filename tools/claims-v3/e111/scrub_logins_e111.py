#!/usr/bin/env python3
"""E111 (Q133): replace any other user's login that a runner's other-user mark recorded with `<another lab user>`, before anything
is committed (E98's rule; a login never goes in a committed file). The runners write such marks as `users:<login>[,<login>...]`
(run_hpl.py's and run_hlc.py's check_others). Text files only (.json .jsonl .log .out .txt), before they are gzipped.

    python3 tools/claims-v3/e111/scrub_logins_e111.py <data dir>      # prints how many marks each file had, never a login
"""
import os
import re
import sys

PAT = re.compile(r"(users:)(?!<another lab user>)[^;\"'\s\]\)]+")
EXT = (".json", ".jsonl", ".log", ".out", ".txt")


def main():
    top = sys.argv[1]
    total = 0
    for d, _, fs in os.walk(top):
        for f in fs:
            if not f.endswith(EXT):
                continue
            p = os.path.join(d, f)
            if os.path.getsize(p) > 200 * 1024 * 1024:
                continue
            s = open(p, encoding="utf-8", errors="surrogateescape").read()
            t, n = PAT.subn(r"\1<another lab user>", s)
            if n:
                open(p, "w", encoding="utf-8", errors="surrogateescape").write(t)
                total += n
                print(f"{os.path.relpath(p, top)}: {n} mark(s) replaced")
    left = 0
    for d, _, fs in os.walk(top):
        for f in fs:
            if f.endswith(EXT):
                p = os.path.join(d, f)
                if os.path.getsize(p) <= 200 * 1024 * 1024 and PAT.search(open(p, encoding="utf-8", errors="surrogateescape").read()):
                    left += 1
    print(f"scrub: {total} mark(s) replaced; files still matching: {left}")
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main())
