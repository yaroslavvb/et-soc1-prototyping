# Dated note beside README.md, Wed 4 Nov 2026 (week 45), about 18:30 PST: the rest floors the kit's note checked, and which runbook launched E168 (the fix pass after aifoundry2's verifier)

*Written beside [`README.md`](README.md) and not inside it. It records what the verifier of aifoundry2's card day (E165, E167, E168 and
E169; finished about 18:09 PST) found in this README. Its verdict was "holds with fixes": the data, the stops, the device commands, the
order, the window, the post and the public-text scan all hold, and the registered reduction, re-run from the committed data with E165's
anchors, reproduced `results.json` (1,141 fields, 0 differ) and `reduce.txt` (33 lines, identical). Its items are wording and records
only. Desk only: no verdict, number, band, prediction, rule or frozen file changes, and no device command is involved. It answers the
same items as the README: the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) items 1 and 6, and rank 5 of Q139's final
critic.*

## 1. The kit's note checked rest floors of 46-48 °C, with its conclusion stated at 47 °C

§ The session, **The gates**, reads: *"The kit's dated note foresaw a rest floor above 46 °C and showed A2 keeps all three readings
there"*. The kit's note ([`README.md.dated-note.md`](../../../../tools/claims-v3/e168/README.md.dated-note.md), its bullet "A rest
floor above 46 °C", a desk check, not registered) ran Q140(q)'s frozen model with the rest anchor at 46.0-48.0 °C
([`logs/posthoc-floor.txt`](../../../../tools/claims-v3/e168/logs/posthoc-floor.txt)) and stated its conclusion for a 47 °C floor: *"So
on a day when the cold gates time out at a 47 °C floor, A2 keeps all three readings."* The day's cold holds started at 48-49 °C, A2's
own cold hold at 49 °C, at and past the top of that range. So the sentence should read: *"The kit's dated note checked rest floors of
46-48 °C (its conclusion stated for 47 °C) and found that A2 keeps all three readings there; the day's cold holds started at 48-49 °C,
A2's at 49 °C."*

The day's reading is not in doubt. The registered reduction sets A2's band at the holds' measured starts, 49 °C cold and 56 °C warm
(`results.json` › `A2_reported.start_dependence`): there G4 predicts the cold minus warm window board at +1.079 W (+1.334 W at the nominal
46 / 55 °C), so h = 0.54 W, and the measured −0.777 W lies 0.24 W below −h. That is **OPPOSITE SIGN**, the reading the README gives, and
it is unambiguous at the day's starts.

## 2. Which runbook launched E168

The README names the runbook for the collection only (v2, right as written). E168's launch was Q141(k)'s v1 step 18
(`s18_a2_e168.sh`, the queue started 16:18:49 PST), after v2 (`16771f36`) was committed at 15:34:42 with a dated note that says to use v2
for any later step. v2's step 18 differs from v1's only in requiring that E168's dry pass ended rc 0 *today*; it had, at 14:26:30 PST
(§ Departures and notes), so v2 would have launched it the same. The waits on the run: v1's first (16:19:06-16:27:51 PST), then v2's
from 16:21:01 to the end, the two overlapping from 16:21:01 to 16:27:51. Both only read the queue's state, and v2's step 20 differs only
in counting a launch made today.

SPDX-License-Identifier: Apache-2.0
