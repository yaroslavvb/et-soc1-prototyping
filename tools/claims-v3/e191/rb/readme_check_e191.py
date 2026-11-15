#!/usr/bin/env python3
"""E191's check of a data README against its form (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191
datum): rb/data-readme-form-e191.md's sections in their order, and THE FILES TABLE against FILES.txt (E189's card lane's incident 1: its
committed README's Files table left out sparse parity's host.rec, which SHA256SUMS listed). Every file FILES.txt names must be named in the
README's Files section, by its basename (a placeholder row like `passes/<configuration>/p<k>/` covers its directory; each file kind in it
must still be named). Desk only; standard library only.

    /usr/bin/python3 -I -B tools/claims-v3/e191/rb/readme_check_e191.py <the data directory>      (prints README-CHECK-E191 OK or FAIL)
    /usr/bin/python3 -I -B tools/claims-v3/e191/rb/readme_check_e191.py --selftest                (its own cases: README-CHECK-E191 SELFTEST PASS)
SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import sys
import tempfile

SECTIONS = ["## What ran (measured)", "## The passes (measured", "## Registered against happened", "## Departures and notes",
            "## Device commands sent", "## Privacy and the public-text scan", "## Files", "## Next"]


def check(readme_text, files):
    why = []
    if not re.match(r"^# E191\b", readme_text):
        why.append("the title does not begin '# E191'")
    pos = [readme_text.find("\n" + s) for s in SECTIONS]
    for s, p in zip(SECTIONS, pos):
        if p < 0:
            why.append(f"no section '{s}'")
    found = [p for p in pos if p >= 0]
    if found != sorted(found):
        why.append("the sections are not in the form's order")
    if "RAPL is root-only" not in readme_text and any(f.endswith("energy.json") for f in files):
        why.append("the reducer's fixed note (RAPL is root-only) is not named in the privacy section (E189's incident 2)")
    fi = readme_text.find("\n## Files")
    table = readme_text[fi:readme_text.find("\n## ", fi + 5)] if fi >= 0 else ""
    names = sorted({os.path.basename(f) for f in files if f not in ("README.md",)})
    missing = [n for n in names if n not in table and not (n.endswith(".txt") and "stdout.txt" == n and "stdout.txt" in table)]
    if missing:
        why.append("the Files table does not name: " + ", ".join(missing[:12]))
    return why


def selftest():
    good_files = ["passes/sparse-parity/p1/host.rec", "passes/sparse-parity/p1/energy.json", "session/session.log", "SHA256SUMS", "FILES.txt"]
    body = ("# E191: x\n\npara\n\n## What ran (measured)\n\n## The passes (measured; x)\n\n## Registered against happened\n\n"
            "## Departures and notes (dated)\n\n## Device commands sent\n\n## Privacy and the public-text scan\nRAPL is root-only\n\n"
            "## Files\n| `passes/` | `host.rec`, `energy.json` |\n| `session/` | `session.log` |\n| `SHA256SUMS` | x |\n| `FILES.txt` | x |\n\n## Next\n")
    bad = []
    if check(body, good_files):
        bad.append(f"a good README refused: {check(body, good_files)}")
    if not any("host.rec" in w for w in check(body.replace("`host.rec`, ", ""), good_files)):
        bad.append("a README without host.rec passed (E189's incident 1)")
    if not check(body.replace("RAPL is root-only", "x"), good_files):
        bad.append("a README without the reducer's note passed (E189's incident 2)")
    if not check(body.replace("## Next\n", "").replace("## What ran", "## Next\n\n## What ran"), good_files):
        bad.append("sections out of order passed")
    return bad


def main(argv):
    if argv == ["--selftest"]:
        b = selftest()
        print("README-CHECK-E191 SELFTEST " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
        return 0 if not b else 1
    if len(argv) != 1:
        print(__doc__)
        return 2
    d = argv[0]
    try:
        text = open(os.path.join(d, "README.md")).read()
        files = [ln.strip() for ln in open(os.path.join(d, "FILES.txt")) if ln.strip()]
    except OSError as e:
        print(f"README-CHECK-E191 FAIL: {e}")
        return 1
    why = check(text, files)
    print("README-CHECK-E191 " + ("OK: the form's sections in order, every file FILES.txt names in the Files table" if not why
                                  else "FAIL: " + "; ".join(why)))
    return 0 if not why else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
