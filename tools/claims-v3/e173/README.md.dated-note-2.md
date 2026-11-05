# E173's kit, dated note 2: the box steps through step_e173_v3.sh; the collection's C-log list reads session_end names

*Written Thu 5 Nov 2026 (week 45), about 08:35 PST, on the Intel, desk only, after the code it names was committed (lab `e2b48f5a`, 08:27:12
PST) and before any E173 data. It sits beside [`README.md`](README.md) and its [dated note 1](README.md.dated-note-1.md), which stay as
committed; the change is registered by [`E173.md.dated-note-2.md`](E173.md.dated-note-2.md) (`c9a3e40a`, before the code). It answers the
first verifier of v2 (`verify-q142v2-code`, Thu 5 Nov 2026) and serves item 6 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open).*

- **Every step**: `bash tools/claims-v3/e173/box/step_e173_v3.sh look | tree | dry start | dry wait | launch [full|subset] | wait | collect`.
  Every step but collect is note 1's `step_e173_v2.sh`, handed the same arguments; collect's C-log gate reads
  `../q142kg-runbook/cclist_q142kg_v3.py` (a session the queue's record names only in a `session_end` line, its start line and directory
  lost, stops the collection: 14).

SPDX-License-Identifier: Apache-2.0
