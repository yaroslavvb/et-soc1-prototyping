# The matmul model report, second version: its rows in `docs/reports/MIRROR.md`

*Thu 19 Nov 2026 (week 47), PST; written by the round's lane `report-v2-final` (Q226) with the report, before any deploy. The second version
is published to the same space as the first (slug `et-soc1-matmul-model`, space `fcc90c64-d0e5-404e-9b1c-fcebf8e8c4ae`, as MIRROR.md's row
committed in `95ff5098` names it), so MIRROR.md keeps one row a space in its mirrored tables. The commit that adds this folder also changes
MIRROR.md in two places, and nothing else there: a dated note in that space's row (its repo file stays the first version's page, which the
space serves until the deploy, so `scripts/check-mirror.py` keeps reading equal), and a new line in "How each page is built" for this
version's page, beside the first version's line (whose page file stays in the repository as committed). The page is not deployed by that
commit.*

**The page:** `docs/reports/2026-11-19-matmul-model-v2/index.html`, one self-contained file built by [`build_page.py`](build_page.py) from
this folder's `README.md` and figures (`build_page.py --check` exits 0 while it equals what the build writes).

**At the deploy** (the orchestrator's step), the space's row changes its repo file to this version's page, and its note says so:

| Page | Space | Visibility | Repo file | Deploy |
|---|---|---|---|---|
| [The lab's matmul model, MM1](https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-model) (17 Nov, Q215: ...; **second version committed Thu 19 Nov 2026, Q226**: ...; deployed to this space by the orchestrator, this row's repo file since then) | `fcc90c64-d0e5-404e-9b1c-fcebf8e8c4ae` | public | `docs/reports/2026-11-19-matmul-model-v2/index.html` | folder: `index.html` |

(The full text of both versions of that row is in [`mirror_v2.py`](mirror_v2.py), which makes both edits, text only, and refuses unless each
anchor is found exactly once: `python3 docs/reports/data/2026-11-19-matmul-model-v2/mirror_v2.py docs/reports/MIRROR.md` made this commit's,
and `... --after-deploy` makes the deploy-time one.)

**The build line added now** (the table under "How each page is built"):

| Page | Source | Final build step (from the repository root) | Earlier steps |
|---|---|---|---|
| The lab's matmul model, MM1, second version (19 Nov, Q226; the first version's space) | `docs/reports/data/2026-11-19-matmul-model-v2/README.md` and its five figures | `python3 docs/reports/data/2026-11-19-matmul-model-v2/build_page.py --out docs/reports/2026-11-19-matmul-model-v2/index.html` | `python3 docs/reports/data/2026-11-19-matmul-model-v2/make_figures.py --repo . --out <dir>` (`numbers.json`, `tables.md` and the five figures, from committed files only, into a new folder), then `check_numbers.py --repo . --numbers <dir>/numbers.json --readme docs/reports/data/2026-11-19-matmul-model-v2/README.md` (every number against its committed source) |

SPDX-License-Identifier: Apache-2.0
