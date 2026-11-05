# E171's kit, dated note 1: step 11's collection adds the scale anchors' C status, and the pooled KA read is v2's

*Written Thu 5 Nov 2026 (week 45), PST, on the Intel, in Q142(k6)'s fix pass (lane `fix-desk-q142k6-kits`), desk only. [`README.md`](README.md)
and every kit file stay as committed. Nothing the box runs changes, so `harness-e171.json` (101 files) and the device-command audits stand
as committed. It follows the registration's note [`E171.md.dated-note-1.md`](E171.md.dated-note-1.md) (`2502ba81`: N1 and N2) and the
scorer's v2 (`86d10a75`), for item 6 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open).*

- **Step 11, collect: one more call after the C-session gate.** It writes each scale anchor's C status beside `scored.json`:
  `/usr/bin/python3 -B tools/claims-v3/p8-600/score_p8_600_v2.py scale-c --run E171 --scored <out>/scored.json --reduction <out>/e171.json
  --raw build/e171-raw --ccheck <out>/ccheck/ccheck-all.json --json <out>/scale-c.json --md <out>/scale-c.md --work <out>/scale-c`.
  - It must exit 0 and print a `SCALE-C` line.
  - `scale-c.json` and `scale-c.md` go into the data directory with the rest. `scale-c/e171-c-clean-scale.json` goes there too when it
    exists, which is only when an anchor in s is not C all PASS.
  - The runbook's step 22 v2 runs it: `../q141k-runbook/k6/s22_collect_k6_v2.sh e171`.
- **KA pooled, after E172 is collected:** `score_p8_600_v2.py ka-pooled <E171 scored.json> <E172 scored.json> --scale-c <E171
  scale-c.json> <E172 scale-c.json>`. Never use the committed `score_p8_600.py ka-pooled`, which reads any two files. Through the
  runbook it is `s22_collect_k6_v2.sh ka`.
- **The card-minutes and the cap are unchanged.** E171's queue lists four passes, so no fifth can start.

SPDX-License-Identifier: Apache-2.0
