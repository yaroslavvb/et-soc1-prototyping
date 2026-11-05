# E172's kit, dated note 2: step 22 is v3, the pooled KA read is v3's, and the pull waits for a quiet aifoundry1

*Written Thu 5 Nov 2026 (week 45), about 08:35 PST, on the Intel, desk only, after the code it names was committed (lab `e2b48f5a`, 08:27:12
PST) and before any E172 data. It sits beside [`README.md`](README.md) and its [dated note 1](README.md.dated-note-1.md), which stay as
committed; the change is registered by [`E172.md.dated-note-2.md`](E172.md.dated-note-2.md) (`c9a3e40a`, before the code). It answers the
first verifier of v2 (`verify-q142v2-code`, Thu 5 Nov 2026) and serves item 6 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open).*

- **At the go**, after `../q141k-runbook/k6/s03_desk_k6.sh`: `../q141k-runbook/k6/s03b_lists_k6.sh`, all 22 hash lists the readiness critic
  checked and this pass's two (`../p8-600/SHA256SUMS-v3` and the drivers' `../q141k-runbook/k6/SHA256SUMS-drivers-v3`); 16 on any mismatch.
- **The collection**: `../q141k-runbook/k6/s22_collect_k6_v3.sh e172`, after E174 has ended or been skipped: before `box/pull_e172.sh` it
  reads aifoundry1 once, and while a card session of ours (E174's queue on card 0, or E172's own) or a dry pass of either runbook runs there
  it pulls nothing and exits 17 (call it again). Everything else is note 1's `s22_collect_k6_v2.sh e172`, line for line.
- **KA pooled, after both collections**: `s22_collect_k6_v3.sh ka` (`../p8-600/score_p8_600_v3.py ka-pooled`), never v2's.
- **The fifth pass**: four passes, or five if every pass takes about 748 s or less; E172.md's lines 92 and 121 are both superseded
  (E172.md.dated-note-2.md, section 2.4).

SPDX-License-Identifier: Apache-2.0
