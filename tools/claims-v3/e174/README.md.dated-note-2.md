# E174's kit, dated note 2: the box steps through step_e174_v3.sh; E174 after E172 or without it, never beside it

*Written Thu 5 Nov 2026 (week 45), about 08:35 PST, on the Intel, desk only, after the code it names was committed (lab `e2b48f5a`, 08:27:12
PST) and before any E174 data. It sits beside [`README.md`](README.md) and its [dated note 1](README.md.dated-note-1.md), which stay as
committed; the change is registered by [`E174.md.dated-note-2.md`](E174.md.dated-note-2.md) (`c9a3e40a`, before the code). It answers the
first verifier of v2 (`verify-q142v2-code`, Thu 5 Nov 2026) and serves item 6 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open).*

- **The order**: E174 runs after E172 has ended, or if E172 never starts, and never beside it (E174.md.dated-note-2.md, section 1).
- **Every step**: `bash tools/claims-v3/e174/box/step_e174_v3.sh look | sync | check start | check wait | launch [subset] | wait | pull |
  collect`. Every step but collect is note 1's `step_e174_v2.sh`, handed the same arguments; collect's C-log gate reads
  `../q142kg-runbook/cclist_q142kg_v3.py` (14 when the queue's record names, only in a `session_end` line, a session whose start line and
  directory are lost).
- **E172's collection waits for E174**: `../q141k-runbook/k6/s22_collect_k6_v3.sh e172` pulls nothing while E174 or its box check runs (17).

SPDX-License-Identifier: Apache-2.0
