#!/usr/bin/env python3
"""The matmul model report, second version (Q226, lane report-v2-final): its MIRROR.md edits, text only.

    python3 docs/reports/data/2026-11-19-matmul-model-v2/mirror_v2.py docs/reports/MIRROR.md                  this version's commit's edit
    python3 docs/reports/data/2026-11-19-matmul-model-v2/mirror_v2.py docs/reports/MIRROR.md --after-deploy   the edit after its deploy
(exit 3, nothing written, if an anchor is not found exactly once)

Before the deploy (this lane's commit): (1) a dated note in the space's row (its Page cell) that the second version is committed and is
deployed to this space by the orchestrator, when this row's repo file changes to the new page; the row's repo file stays the first
version's, which is what the space serves until then, so scripts/check-mirror.py keeps reading equal; (2) a new line in "How each page
is built" for the second version's page, beside the first version's (whose page file stays in the repository).
After the deploy (--after-deploy, the orchestrator's): the row's repo file becomes the second version's page and the note says when.
Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import sys

ROW_HEAD = ("| [The lab's matmul model, MM1](https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-model) (17 Nov, Q215: MM1, the lab's matmul model, "
            "a GEMM's cycles, joules and transistor switches from its sizes, format, data and card; the timing simulation and the energy checked "
            "against the card; five blind card days, E206 to E211, and E210's switch test; built by "
            "`docs/reports/data/2026-11-17-matmul-model/build_page.py` from that folder's README)")
NOTE = ("; **second version committed Thu 19 Nov 2026, Q226**: `docs/reports/2026-11-19-matmul-model-v2/index.html`, built by "
        "`docs/reports/data/2026-11-19-matmul-model-v2/build_page.py` from that folder's README (MM1-v3 and MM1-v3.1, E212 to E215, one "
        "scorecard of every blind and unread test); the orchestrator deploys it to this space, and this row's repo file changes to it then")
OLD_FILE = " | `fcc90c64-d0e5-404e-9b1c-fcebf8e8c4ae` | public | `docs/reports/2026-11-17-matmul-model/index.html` | folder: `index.html` |"
NEW_FILE = " | `fcc90c64-d0e5-404e-9b1c-fcebf8e8c4ae` | public | `docs/reports/2026-11-19-matmul-model-v2/index.html` | folder: `index.html` |"
BUILD_V1 = ("| The lab's matmul model, MM1 (17 Nov, Q215) | `docs/reports/data/2026-11-17-matmul-model/README.md` and its five figures | "
            "`python3 docs/reports/data/2026-11-17-matmul-model/build_page.py --out docs/reports/2026-11-17-matmul-model/index.html` | "
            "`python3 docs/reports/data/2026-11-17-matmul-model/make_figures.py --repo . --out docs/reports/data/2026-11-17-matmul-model` "
            "(the figures and `numbers.json`, from committed files only), then `readme_numbers.py` (the check list) |")
BUILD_V2 = ("| The lab's matmul model, MM1, second version (19 Nov, Q226; the first version's space) | "
            "`docs/reports/data/2026-11-19-matmul-model-v2/README.md` and its five figures | "
            "`python3 docs/reports/data/2026-11-19-matmul-model-v2/build_page.py --out docs/reports/2026-11-19-matmul-model-v2/index.html` | "
            "`python3 docs/reports/data/2026-11-19-matmul-model-v2/make_figures.py --repo . --out <dir>` (`numbers.json`, `tables.md` and the "
            "five figures, from committed files only, into a new folder), then `check_numbers.py --repo . --numbers <dir>/numbers.json "
            "--readme docs/reports/data/2026-11-19-matmul-model-v2/README.md` (every number against its committed source) |")


def once(s, a, what):
    n = s.count(a)
    if n != 1:
        print(f"mirror_v2: {what} found {n} times, not once: nothing written")
        sys.exit(3)


def main():
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    if "--after-deploy" in sys.argv:
        once(s, ROW_HEAD + NOTE + OLD_FILE, "the space's row with this lane's note")
        s = s.replace(ROW_HEAD + NOTE + OLD_FILE, ROW_HEAD + NOTE.replace(
            "the orchestrator deploys it to this space, and this row's repo file changes to it then",
            "deployed to this space by the orchestrator, this row's repo file since then") + NEW_FILE)
    else:
        once(s, ROW_HEAD + OLD_FILE, "the space's row")
        once(s, BUILD_V1 + "\n", "the first version's build row")
        if BUILD_V2 in s:
            print("mirror_v2: the second version's build row is already there: nothing written")
            sys.exit(3)
        s = s.replace(ROW_HEAD + OLD_FILE, ROW_HEAD + NOTE + OLD_FILE)
        s = s.replace(BUILD_V1 + "\n", BUILD_V1 + "\n" + BUILD_V2 + "\n")
    open(p, "w", encoding="utf-8").write(s)
    print("mirror_v2: written", p)


if __name__ == "__main__":
    main()
