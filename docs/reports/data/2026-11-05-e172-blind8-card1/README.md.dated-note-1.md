# E172's data README, dated note 1: the login scrub's --check ran on logs/ only, as logged, and the whole directory was read only after the commit (no number, rule or verdict changes)

*Written Thu 5 Nov 2026 (week 45), about 15:20-15:40 PST, on the Intel, desk only, by the fix pass of the pool-8 card day's aifoundry1 lane,
after that lane's data verifier (Thu 5 Nov 2026, about 13:50-15:03 PST: the data holds, with four minor faults to fix; this note answers its
fault 2, part b). [`README.md`](README.md) (lab `b3255af1`) stays as committed; this note sits beside it. Everything here is **post hoc**. **No
number, rule, line or verdict changes**, and no data file is touched. The evidence is § 6 of
[`../2026-11-05-e174-blind8-card0/posthoc-note1-e174.txt`](../2026-11-05-e174-blind8-card0/posthoc-note1-e174.txt), which is written by
[`posthoc_note1_e174.py`](../2026-11-05-e174-blind8-card0/posthoc_note1_e174.py) and reads this directory as committed. The run answers item 6 of the
kinds page's section 11 ([horace-kinds-of-numbers § 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)),
with items 8 and 9, as the README says.*

## What the README says, and what was logged

- **The README's sentence** (§ Card and post): "The collector's scrub (`scrub_etwho_e164.py`: 0 files rewritten) and its `--check`, run on
  `logs/`, by step 22, and again on this whole directory, leave no other account's login in any file (0 left)".
- **What was logged.** [`collect_e172.sh`](../../../../tools/claims-v3/e172/collect_e172.sh), called by step 22 between 13:19:36 and 13:35:38 PST,
  ran the scrub and then its `--check` on `logs/`. The scrub's record is [`logs/et-who-summary.txt`](logs/et-who-summary.txt) (two et-who readings,
  no holder on either card). Step 22's log reads "0 file(s) rewritten", "2 et-who reading(s)" and "scrub check: OK (0 left)".
- **What was not logged.** No output of a second run "on this whole directory" was kept.
- **What such a run would have read.** The tool reads only the files directly in the directory it is given (`files_in`: `os.listdir`, files only;
  posthoc § 6). Run on this directory, it would have read the top-level files only, not `aifoundry1-c1/`.

## What stands for "in any file"

- **The data verifier's independent scan** of all 780 files added by the lane's three commits (433 of them in this directory), read from the
  committed blobs with every `.gz` decompressed. It found no login but the owner's box login.
- **This pass's run of the scrub's own `--check`**, unchanged, in **every** directory of this directory as committed at HEAD `d34f2be6`
  (posthoc § 6). It covered 18 directories, with the 12 `.gz` files unpacked and the 292 binary tiles left out, and found **0 left**. Every box home
  path in the directory is the owner's (14,959).

No other account's login is in any file here. The README's figures, verdicts and files are unchanged.

## What the records take from this note

Quote the scrub as "run on `logs/` by the collector (logged; `logs/et-who-summary.txt`)". Then add: "the whole directory, every subdirectory
included, was read after the commit by the data verifier's scan and by the scrub's own `--check` in every directory: 0 left
(`../2026-11-05-e174-blind8-card0/posthoc-note1-e174.txt` § 6)". The collector's one-level reach is a kit matter, recorded beside E174's kit in
[`E174.md.dated-note-4.md`](../../../../tools/claims-v3/e174/E174.md.dated-note-4.md) § 3.

SPDX-License-Identifier: Apache-2.0
