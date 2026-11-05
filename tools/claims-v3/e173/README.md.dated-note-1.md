# E173's kit README, dated note 1: the box steps run through step_e173_v2.sh (Q142(kg) fix pass)

*Thu 5 Nov 2026 (week 45), PST, on the Intel, desk only. [`README.md`](README.md) (lab `5a2a9ba0`) stays as committed. This note supersedes three
of its lines for the card day, after the kits' verifier. The rules are in [`E173.md.dated-note-1.md`](E173.md.dated-note-1.md) (lab `5db9df6b`,
committed before this note and before any E173 data). It answers item 6 of the kinds page's section 11
([§ 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)), as the kit does.*

- **Every box step is `bash tools/claims-v3/e173/box/step_e173_v2.sh <step>`**, in the README's order: `look`, `tree`, `dry start` and
  `dry wait`, the day's post, `launch [subset]`, `wait`, `collect`. It is `step_e173.sh` line for line, except that it sources
  `../q142kg-runbook/rb_common_v2.sh`; its own name appears in its usage lines and messages.
- **Step 2, `tree`:** `RB_BASE` now defaults to the kit's commit, `5a2a9ba0`, so it need not be passed by hand; the README said "default
  `c8064454`; pass `RB_BASE=<this kit's commit>` on the day".
- **Step 7, `collect`:** the C-log gate reads `../q142kg-runbook/cclist_q142kg_v2.py`, not `cclist_q142kg.py` (E173.md.dated-note-1.md
  section 3, the verifier's fault 7). The queue's record must be in the collected runs dir. A session whose records show it ran a launch must
  carry a C log and a finished check, even when its `launches.jsonl` is lost. Then v3.1's `ccdone_q142s.py`, as before.
- **"One departure from the registration's Files table"** is now recorded beside the registration (E173.md.dated-note-1.md section 1, the
  verifier's fault 2): `check_e173.py` with `harness-e173.json` does the job of the `check_path_e173.py` that the table names.

The kit itself is unchanged. `step_e173_v2.sh` runs on the Intel and is pinned by no harness, so `harness-e173.json` (135 files) still reads
HARNESS OK. Its tests are `../q142kg-runbook/logs/selftest-steps-v2.txt` (v1's cases on the v2 drivers, with v2's C-log list) and its dry listing,
`../q142kg-runbook/logs/dry-listing-v2.txt`.

SPDX-License-Identifier: Apache-2.0
