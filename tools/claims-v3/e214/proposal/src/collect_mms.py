#!/usr/bin/env python3
"""1118-mmsweep3: the collection, at the desk, of a session directory pulled from its box (Python's own modules only; it changes
nothing it reads).

    python3 -I -B src/collect_mms.py <pulled sessions/<sid> folder> --out <dir> [--login NAME] [--home PATH]

  1. COPY-BACK EXACT: every file MANIFEST.sha256 lists is present at its sha256; files outside the manifest are named (the
     wrapper's runner.rc and runner.out are expected there);
  2. THE PRIVACY READ: every text file, and the text inside every .gz, read for a home-directory path (/home/, or --home PATH)
     and for --login NAME (the box login); hits are counted by file, never printed; a hit makes the copy NOT CLEAN (the lab
     session's commit scrubs; this says what it must scrub);
  3. the reducer (src/reduce_mms.py) into <dir>/data-mms-<sid>.json and <dir>/reduce-mms-<sid>.txt;
  4. the last line: COLLECT OK <sid> (exact, clean, reduced), or COLLECT NOT OK <sid>: <why>.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_mms as R  # noqa: E402

EXPECTED_OUTSIDE = {"runner.rc", "runner.out", "MANIFEST.sha256", "box.lock"}     # box.lock: a dry session's stand-in


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def text_of(p):
    try:
        if p.endswith(".gz"):
            with gzip.open(p, "rb") as f:
                return f.read().decode("utf-8", "replace")
        with open(p, "rb") as f:
            b = f.read()
        if b"\0" in b[:4096]:
            return None
        return b.decode("utf-8", "replace")
    except OSError:
        return None


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("session")
    parser.add_argument("--out", required=True)
    parser.add_argument("--login")
    parser.add_argument("--home")
    a = parser.parse_args(argv)
    sd = os.path.normpath(a.session)
    sid = os.path.basename(sd)
    why = []
    man = os.path.join(sd, "MANIFEST.sha256")
    listed = {}
    if not os.path.exists(man):
        why.append("no MANIFEST.sha256 (the session has not ended, or the copy is short)")
    else:
        for ln in open(man):
            ln = ln.rstrip("\n")
            if ln:
                h, r = ln.split("  ", 1)
                listed[r] = h
    bad = [r for r, h in listed.items() if not os.path.isfile(os.path.join(sd, r)) or sha(os.path.join(sd, r)) != h]
    present = []
    for dp, dn, fn in os.walk(sd):
        dn.sort()
        for n in sorted(fn):
            present.append(os.path.relpath(os.path.join(dp, n), sd))
    outside = [r for r in present if r not in listed and r not in EXPECTED_OUTSIDE and not r.startswith("fakedev")]
    print(f"COPY-BACK {'EXACT' if listed and not bad else 'NOT EXACT'}: {len(listed)} files listed, {len(bad)} missing or differing"
          + (f" ({', '.join(bad[:5])})" if bad else "") + f"; outside the manifest: {sorted(set(present) - set(listed))}")
    if bad:
        why.append(f"{len(bad)} listed files missing or differing")
    if outside:
        why.append(f"unexpected files outside the manifest: {outside[:5]}")
    pats = ["/home/"] + ([a.home] if a.home else []) + ([a.login] if a.login else [])
    hits = {}
    for r in present:
        t = text_of(os.path.join(sd, r))
        if t is None:
            continue
        n = sum(t.count(p) for p in pats)
        if n:
            hits[r] = n
    print(f"PRIVACY READ: {sum(hits.values())} hit(s) of a home path{' or the login' if a.login else ''} in {len(hits)} file(s)"
          + (f": {sorted(hits.items())[:8]}" if hits else ""))
    if hits:
        why.append(f"NOT CLEAN: {sum(hits.values())} home-path or login hits in {len(hits)} files (scrub before any commit)")
    os.makedirs(a.out, exist_ok=True)
    try:
        d = R.reduce_session(sd)
        with open(os.path.join(a.out, f"data-mms-{sid}.json"), "w") as f:
            json.dump(d, f, indent=1, sort_keys=True)
        t = R.table(d)
        with open(os.path.join(a.out, f"reduce-mms-{sid}.txt"), "w") as f:
            f.write(t)
        print(t, end="")
    except (OSError, ValueError, KeyError, SystemExit) as e:
        why.append(f"the reducer failed ({type(e).__name__}: {e})")
    print(f"COLLECT {'OK' if not why else 'NOT OK'} {sid}" + (": " + "; ".join(why) if why else " (exact, clean, reduced)"))
    return 0 if not why else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
