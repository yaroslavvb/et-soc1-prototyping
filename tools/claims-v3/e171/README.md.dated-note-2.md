# E171's kit, dated note 2: step 22 is v3, and the pooled KA read is v3's

*Written Thu 5 Nov 2026 (week 45), about 08:35 PST, on the Intel, desk only, after the code it names was committed (lab `e2b48f5a`, 08:27:12
PST) and before any E171 data. It sits beside [`README.md`](README.md) and its [dated note 1](README.md.dated-note-1.md), which stay as
committed; the change is registered by [`E171.md.dated-note-2.md`](E171.md.dated-note-2.md) (`c9a3e40a`, before the code). It answers the
first verifier of v2 (`verify-q142v2-code`, Thu 5 Nov 2026) and serves item 6 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open).*

- **At the go**, after `../q141k-runbook/k6/s03_desk_k6.sh`: `../q141k-runbook/k6/s03b_lists_k6.sh`, all 22 hash lists the readiness critic
  checked and this pass's two (`../p8-600/SHA256SUMS-v3` and the drivers' `../q141k-runbook/k6/SHA256SUMS-drivers-v3`); 16 on any mismatch.
- **The collection**: `../q141k-runbook/k6/s22_collect_k6_v3.sh e171` (note 1's `s22_collect_k6_v2.sh e171`, line for line: the copies, the
  collector, the C gate, `score_p8_600_v2.py scale-c` and the desk-path gate).
- **KA pooled, after E172 is collected**: `s22_collect_k6_v3.sh ka`, which calls `../p8-600/score_p8_600_v3.py ka-pooled <E171 scored.json>
  <E172 scored.json> --scale-c <both scale-c.json>` (never v2's or the committed scorer's ka-pooled). A session that kept fewer than 2
  passes reads NOT SCORED, as E171.md registers; two files carrying the same measured D are refused (16).

SPDX-License-Identifier: Apache-2.0
