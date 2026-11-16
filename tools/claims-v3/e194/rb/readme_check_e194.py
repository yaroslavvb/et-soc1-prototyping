#!/usr/bin/env python3
"""E194's check of a data README against its form (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194
datum; E191's checker, tools/claims-v3/e191/rb/readme_check_e191.py, unchanged beside it): rb/data-readme-form-e194.md's sections in their order, and THE FILES TABLE against FILES.txt (E189's card lane's incident 1: its
committed README's Files table left out sparse parity's host.rec, which SHA256SUMS listed). Every file FILES.txt names must be named in the
README's Files section, by its basename (a placeholder row like `passes/<configuration>/p<k>/` covers its directory; each file kind in it
must still be named). Desk only; standard library only.

    /usr/bin/python3 -I -B tools/claims-v3/e194/rb/readme_check_e194.py <the data directory>      (prints README-CHECK-E194 OK or FAIL)
    /usr/bin/python3 -I -B tools/claims-v3/e194/rb/readme_check_e194.py --selftest                (its own cases: README-CHECK-E194 SELFTEST PASS)
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
    if not re.match(r"^# E194\b", readme_text):
        why.append("the title does not begin '# E194'")
    if "his words, Sun 15 Nov 2026 10:22:36 PST" not in readme_text and "the owner waived the post" not in readme_text:
        why.append("the post's waiver is not recorded in his words with its time (E194.md 13)")
    pos = [readme_text.find("\n" + s) for s in SECTIONS]
    for s, p in zip(SECTIONS, pos):
        if p < 0:
            why.append(f"no section '{s}'")
    found = [p for p in pos if p >= 0]
    if found != sorted(found):
        why.append("the sections are not in the form's order")
    if "RAPL is root-only" not in readme_text and any(f.endswith("energy.json") for f in files):
        why.append("the reducer's fixed note (RAPL is root-only) is not named in the privacy section (E189's incident 2)")
    wi = readme_text.find("\n## What ran (measured)")             # fix-e194 (verify-e194's finding 3): the runner's exit status named
    what_ran = readme_text[wi:readme_text.find("\n## ", wi + 5)] if wi >= 0 else ""
    if any(f.endswith("runner.rc") for f in files) and "runner.rc" not in what_ran:
        why.append("the runner's exit status (runner.rc) is not named in 'What ran' (fix-e194: a crash after the gate reads as an ordinary end otherwise)")
    fi = readme_text.find("\n## Files")
    table = readme_text[fi:readme_text.find("\n## ", fi + 5)] if fi >= 0 else ""
    names = sorted({os.path.basename(f) for f in files if f not in ("README.md",)})
    missing = [n for n in names if n not in table and not (n.endswith(".txt") and "stdout.txt" == n and "stdout.txt" in table)]
    if missing:
        why.append("the Files table does not name: " + ", ".join(missing[:12]))
    return why


def selftest():
    good_files = ["passes/sparse-parity/p1/host.rec", "passes/sparse-parity/p1/energy.json", "session/session.log", "session/runner.rc",
                  "SHA256SUMS", "FILES.txt"]
    body = ("# E194: x\n\nthe owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST\n\n## What ran (measured)\nthe runner exited 0 (runner.rc)\n\n"
            "## The passes (measured; x)\n\n## Registered against happened\n\n"
            "## Departures and notes (dated)\n\n## Device commands sent\n\n## Privacy and the public-text scan\nRAPL is root-only\n\n"
            "## Files\n| `passes/` | `host.rec`, `energy.json` |\n| `session/` | `session.log`, `runner.rc` |\n| `SHA256SUMS` | x |\n| `FILES.txt` | x |\n\n## Next\n")
    bad = []
    if check(body, good_files):
        bad.append(f"a good README refused: {check(body, good_files)}")
    if not any("host.rec" in w for w in check(body.replace("`host.rec`, ", ""), good_files)):
        bad.append("a README without host.rec passed (E189's incident 1)")
    if not check(body.replace("RAPL is root-only", "x"), good_files):
        bad.append("a README without the reducer's note passed (E189's incident 2)")
    if not check(body.replace("## Next\n", "").replace("## What ran", "## Next\n\n## What ran"), good_files):
        bad.append("sections out of order passed")
    if not check(body.replace("the owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST", "no post"), good_files):
        bad.append("a README without the post's waiver in his words passed")
    if not any("runner.rc" in w for w in check(body.replace("the runner exited 0 (runner.rc)", "the session ran"), good_files)):
        bad.append("a README whose 'What ran' does not name runner.rc passed (fix-e194)")
    return bad


def main(argv):
    if argv == ["--selftest"]:
        b = selftest()
        print("README-CHECK-E194 SELFTEST " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
        return 0 if not b else 1
    if len(argv) != 1:
        print(__doc__)
        return 2
    d = argv[0]
    try:
        text = open(os.path.join(d, "README.md")).read()
        files = [ln.strip() for ln in open(os.path.join(d, "FILES.txt")) if ln.strip()]
    except OSError as e:
        print(f"README-CHECK-E194 FAIL: {e}")
        return 1
    why = check(text, files)
    print("README-CHECK-E194 " + ("OK: the form's sections in order, every file FILES.txt names in the Files table" if not why
                                  else "FAIL: " + "; ".join(why)))
    return 0 if not why else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
