# E172's kit, dated note 1: step 7's collection adds the scale anchors' C status, the pooled KA read is v2's, and a fifth pass can run

*Written Thu 5 Nov 2026 (week 45), PST, on the Intel, in Q142(k6)'s fix pass (lane `fix-desk-q142k6-kits`), desk only. [`README.md`](README.md)
and every kit file stay as committed. Nothing the box runs changes, so `harness-e172.json` (103 files) and the device-command audits stand
as committed. It follows the registration's note [`E172.md.dated-note-1.md`](E172.md.dated-note-1.md) (`2502ba81`: N1, N2 and N4) and the
scorer's v2 (`86d10a75`), for item 6 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open).*

- **Step 7, pull then collect: one more call after the C-session gate.** It writes each scale anchor's C status beside `scored.json`:
  `/usr/bin/python3 -B tools/claims-v3/p8-600/score_p8_600_v2.py scale-c --run E172 --scored <out>/scored.json --reduction <out>/e172.json
  --raw build/e172-raw --ccheck <out>/ccheck/ccheck-session.json --json <out>/scale-c.json --md <out>/scale-c.md --work <out>/scale-c`.
  - It must exit 0 and print a `SCALE-C` line.
  - `scale-c.json` and `scale-c.md` go into the data directory with the rest. `scale-c/e172-c-clean-scale.json` goes there too when it
    exists, which is only when an anchor in s is not C all PASS.
  - The runbook's step 22 v2 runs it: `../q141k-runbook/k6/s22_collect_k6_v2.sh e172`.
- **KA pooled with E171:** `score_p8_600_v2.py ka-pooled <E171 scored.json> <E172 scored.json> --scale-c <E171 scale-c.json> <E172
  scale-c.json>`. Never use the committed `score_p8_600.py ka-pooled`, which reads any two files. Through the runbook it is
  `s22_collect_k6_v2.sh ka`.
- **Card-minutes and the cap.** The paragraph's last sentence is wrong: "a fifth would end past 3,840 s and the queue's rule stops before
  it". The queue lists 17210-17214 and starts a pass when its start plus the longest pass so far is at or before T0 + 3,840 s.
  - So a fifth pass runs when d1 + d2 + d3 + d4 + max(d) is about 3,742 s or less: with equal passes, about 748 s each or less. The
    forecast is 735-763 s a pass.
  - E172 runs **four passes, or five if every pass takes about 748 s or less**. Five take about 63-64 card-minutes, inside the 65 cap.
  - A fifth pass delays card 0's E174 by about 12-13 minutes. The aifoundry1 clause of the day's post is sized for that.
  - The rule, the cap and the plan file are unchanged (`E172.md.dated-note-1.md`, N4).

SPDX-License-Identifier: Apache-2.0
