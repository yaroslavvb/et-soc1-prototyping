# The matmul model report: its entry for `docs/reports/MIRROR.md`, to add when the page is first deployed

*Tue 17 Nov 2026 (week 47), PST; written by the round's lane `report-final` (Q215) with the report, before any deploy. MIRROR.md's form asks
for one row a page in its mirrored tables, with the space's uuid from `spacesheep list --json` and the page's file here; the uuid exists only
after the first deploy, so the row waits in this file, ready to paste. The page is not deployed by this commit.*

**The page:** `docs/reports/2026-11-17-matmul-model/index.html` (sha256 `663f805a9d757aecedd403f27cf7f2142042a5a4fd784026471a8c15d690b5d9`), one self-contained file built by
[`build_page.py`](build_page.py) from this folder's `README.md` and figures (`build_page.py --check` exits 0 while it equals what the
build writes). The proposed slug is `et-soc1-matmul-model`, public, as MIRROR.md's rule for a new report page asks.

**The row** (for the table "The measurement set: the pages the hub indexes"; put the uuid in place of `<uuid>`):

| Page | Space | Visibility | Repo file | Deploy |
|---|---|---|---|---|
| [The lab's matmul model, MM1](https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-model) (17 Nov, Q215: MM1, the lab's matmul model, a GEMM's cycles, joules and transistor switches from its sizes, format, data and card; the timing simulation and the energy checked against the card; five blind card days, E206 to E211, and E210's switch test; built by `docs/reports/data/2026-11-17-matmul-model/build_page.py` from that folder's README) | `<uuid>` | public | `docs/reports/2026-11-17-matmul-model/index.html` | folder: `index.html` |

**The build row** (for the table under "How each page is built"):

| Page | Source | Final build step (from the repository root) | Earlier steps |
|---|---|---|---|
| The lab's matmul model, MM1 (17 Nov, Q215) | `docs/reports/data/2026-11-17-matmul-model/README.md` and its five figures | `python3 docs/reports/data/2026-11-17-matmul-model/build_page.py --out docs/reports/2026-11-17-matmul-model/index.html` | `python3 docs/reports/data/2026-11-17-matmul-model/make_figures.py --repo . --out docs/reports/data/2026-11-17-matmul-model` (the figures and `numbers.json`, from committed files only), then `readme_numbers.py` (the check list) |

SPDX-License-Identifier: Apache-2.0
