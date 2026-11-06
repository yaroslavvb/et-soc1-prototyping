# Dated note beside `manifest.sha256` (Thu 5 Nov 2026; the records round Q143(r)): its README entry names the README as first committed; the README was corrected after it

*Written on the Intel at about 19:55 PST on Thu 5 Nov 2026, desk only. [`manifest.sha256`](manifest.sha256) and every file it lists stay as
committed. This answers the critic of Q142(h2), (a2) and (r3), its minor fault on hash lists, which found this one.*

`manifest.sha256` was written with E111's data in lab `ea74a2ef` (Sun 1 Nov 2026, 17:32:01 PST), and its line 76 pins `./README.md` at
`6205d2f7…`. The README was then corrected after verification in lab **`b7dbc81d`** (Sun 1 Nov 2026, 18:10:05 PST, "E111: corrections after
verification"), and it reads `9d3e0b5c…` since. So a check of the list reads 217 of its 218 in-repo entries OK, and the README line
differs. **That line is the README as first committed, not a fault in the data:** every data file is as committed in `ea74a2ef`. The README's
text at `6205d2f7…` is `git show ea74a2ef:docs/reports/data/2026-11-01-e111-heat-steady/README.md`.

SPDX-License-Identifier: Apache-2.0
