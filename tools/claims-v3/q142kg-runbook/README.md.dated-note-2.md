# The q142kg runbook, dated note 2: v3 drivers that change the collection only, a C-log list that reads session_end names, a dry listing that prints its prelude (Q142(v2) fix pass)

*Written Thu 5 Nov 2026 (week 45), about 08:30 PST, on the Intel, desk only, after the code it describes was committed (lab `e2b48f5a`,
08:27:12 PST) and before any E173 or E174 data. It sits beside [`README.md`](README.md) (`5a2a9ba0`) and its
[dated note 1](README.md.dated-note-1.md) (`34436d68`), which stay as committed. Registered by dated notes 2 beside
[`E173.md`](../e173/E173.md.dated-note-2.md) and [`E174.md`](../e174/E174.md.dated-note-2.md) (`c9a3e40a`, before the code). It answers the first
verifier of v2 (`verify-q142v2-code`, Thu 5 Nov 2026: its faults 3 and 5) and serves item 6 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open).*

## The drivers the card day runs (supersedes note 1's v2 drivers and the readiness critic's "the v2 drivers only")

- **E173 (aifoundry2):** `bash tools/claims-v3/e173/box/step_e173_v3.sh look | tree | dry start | dry wait | launch [full|subset] | wait | collect`.
- **E174 (aifoundry1 card 0, after E172 or without it, never beside it):** `bash tools/claims-v3/e174/box/step_e174_v3.sh look | sync |
  check start | check wait | launch [subset] | wait | pull | collect`.
- The window first, once: `s02_window_q142kg.sh` (unchanged).

Every step but collect is handed to `step_e17N_v2.sh` with the same arguments (exec), so its gates are v2's, line for line: the dry listing of
each of the 15 through v3 is byte for byte v2's. **collect** sources `rb_common_v3.sh`, whose C-log gate reads `cclist_q142kg_v3.py`. Never
`step_e17N.sh` (v1) on the card day; `step_e17N_v2.sh` is reached through v3.

## The C-log list, v3 (the verifier's fault 3)

v2's list never read the names in the queue's `session_end` lines (`cclist_q142kg_v2.py` line 107), so a session known only from its
`session_end`, its start line and directory lost, passed the gate (the verifier's D3). v3 adds those names under v1's own rule for a started
session with no directory (smoke, stoptest-board, s1 or a BURST session: required; stoptest-die: not), so with no C log the collection stops
(14). The queues write a session's `session_end` only after its `session_start`, so v3 can stop only a record that lost lines; it never removes a
session from v2's list.

Its desk test, `selftest_steps_q142kg_v3.sh` (`logs/selftest-steps-v3.txt`): **19 of 19**: the v3 listing (below); the 15 delegated steps byte
for byte v2's; v2's list cases L0-L7 through v3's gate, each with v2's result; L8, the verifier's D3, now 14 (v2's gate 0); L9, its D4 control, 14
as in v2; L10, a stoptest-die known only from its `session_end`, not required (0); L11, on every case v3's list less its V3-ADDED sessions is
v2's; the parents' committed sessions (E165, E170) give v1's list through the whole v3 gate, with nothing added. v2's own desk test re-run at
this pass: 49 of 49 (not committed).

## The dry listing, v3 (the verifier's fault 5)

`logs/dry-listing-v3.txt` (`list_steps_q142kg_v3.sh`: the window and all 17 steps, each exit 0, no call) prints the prelude for aifoundry2 and
aifoundry1 once at the top, where the 13 marker lines point: the remote `ours_live` (v3.1's and the q142kg redefinition that names E171-E174's
processes), `jobs_live` and `hold_read` are in the record. `logs/dry-listing-v2.txt` and v1's say the same on 13 lines and never print it: read
them as the steps' calls without the prelude.

## Device commands

`dmcmd_audit.py` on the v3 files, the v2 files they hand steps to or source, and `../kinds/e78_common.py`, no allow-list: **GO, 0 send sites**
(`logs/dmcmd-audit-v3.txt`). No kit file changed, so the kits' own audits stand as the first verifier of v2 re-read them (E173 GO 19,
E174 GO 33, each NO-GO only at `run_hpl.py:622` without its reviewed exception).

SPDX-License-Identifier: Apache-2.0
