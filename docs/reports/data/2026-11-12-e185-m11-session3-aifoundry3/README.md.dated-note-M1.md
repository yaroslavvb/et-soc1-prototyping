# E185's data README, dated note M1 (Thu 12 Nov 2026): october-forecast-model's reported arms v3 and v4, read after the data commit through the day-2 check v2's gate - READER-RC 0; both versions read alike; their rises run 0.35 °C high on average (rms 0.53 °C over six), beside E185's own arms at 0.21-0.26 °C

*Beside [README.md](README.md), which it edits nothing of. Written on the Intel, desk only, by the card lane `card-e185` of Q163 (day 2), after
the data commit `190bad0d` (git 06:27:38 PST Thu 12 Nov 2026, pushed). The day's brief places the reader after the data commit and behind
the day-2 check v2's gate, never by hand: [CARD-LANE-BRIEF.md.dated-note-2.md](../../../../tools/claims-v3/e185/CARD-LANE-BRIEF.md.dated-note-2.md)
section 3 and [KIT.md.dated-note-4.md](../../../../tools/claims-v3/e185/KIT.md.dated-note-4.md)'s last row. It records the reader's run
line, its `READER-RC` line and its two outputs, as those notes say. **Reported, never a rule:** october-forecast-model's arms are never
one of E185's rules, never one of E185-BEST's arms, and their words (inside, above, below) are their own, never a scorer's verdict
([E185.md.dated-note-M1.md](../../../../tools/claims-v3/e185/E185.md.dated-note-M1.md), M1-4).*

## The run

- **The gate:** `/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py m1 e185 --data docs/reports/data/2026-11-12-e185-m11-session3-aifoundry3 --rb-out <E185's RB_OUT>`.
  It ran under the Intel's lab-git lock, through the round's local slot, 06:27:51-06:27:55 PST.
  - It ran the day-2 check v2's tree check with no pull: E185's box list 27 of 27 repo entries OK, and E183's brief list's 10 non-M1 entries
    and 5 M1 entries OK.
  - The M1 lists were at their pinned bytes, and no M1 file had changed since `6860643c`.
  - It found 40 files added since `6860643c` in the day's 156 directories, none a shadowing module, and 0 untracked files there.
  - Step 2 v3's last M1 line in E185's runbook log read "21 of 21 at its pinned bytes".
  - The data directory was committed and clean. The gate's line: `M1-READER-GATE-V2 e185 OK at 190bad0df547`.
- **The reader:** `/usr/bin/python3 -B tools/claims-v3/e185/arm_m1_read_e185.py --data docs/reports/data/2026-11-12-e185-m11-session3-aifoundry3 --out docs/reports/data/2026-11-12-e185-m11-session3-aifoundry3/arm-m1-e185`.
- **`READER-RC 0`** (a refusal or a non-zero exit is recorded, never a block). The gate then read "2 new file(s) in
  docs/reports/data/2026-11-12-e185-m11-session3-aifoundry3, nothing else changed".
- **Its two outputs**, the only new files: [`arm-m1-e185.json`](arm-m1-e185.json) (12,680 bytes, sha256 `685dd979...`) and
  [`arm-m1-e185.txt`](arm-m1-e185.txt) (5,371 bytes, sha256 `a1c32b00...`). [`SHA256SUMS-m1`](SHA256SUMS-m1) pins both and this note.

## What it read (the reader's words; modelled against measured; blind for E185)

The session's room was 52.098 °C and it ran the warm pattern (the room mark's 2.6 s every 7.98 s). The model's figures at that room come
from the warm plan rooms 52.5 and 53.0 °C, extrapolated 0.402 °C below 52.5 °C, as the reader says. **v4 reads exactly as v3** (its
forecasts equal v3's at every room), so the table is both.

| hold | the model's rise | E185's R (± 1.96 σ_c) | the model's centre | R against the model's 95% band | the model's cool-down | E185's (recovered, ± 1.96 σ_c) | the cool-down's words |
|---|---|---|---|---|---|---|---|
| H_E | 11.914 ± 0.139 | 11.122 [10.949, 11.296] | above | below, z −5.69 | 2.130 ± 0.089 | 1.994 [1.820, 2.167] | centre inside; R inside the band, z −1.53 |
| L1 | 10.818 ± 0.115 | 10.501 [10.328, 10.674] | above | below, z −2.76 | 1.396 ± 0.089 | 1.697 [1.524, 1.870] | centre below; R above the band, z +3.38 |
| L2 | 10.846 ± 0.117 | 10.427 [10.253, 10.600] | above | below, z −3.58 | 1.424 ± 0.089 | 1.374 [1.200, 1.547] | centre inside; R inside the band, z −0.57 |
| H_E2 | 11.442 ± 0.137 | 10.630 [10.457, 10.803] | above | below, z −5.92 | 1.627 ± 0.089 | 1.181 [1.008, 1.354] | centre above; R below the band, z −5.02 |
| S | 4.262 ± 0.106 | 4.190 [4.017, 4.363] | inside | inside, z −0.67 | not covered | | |
| S2 | 2.130 ± 0.093 | 2.462 [2.288, 2.635] | below | above, z +3.56 | not covered | | |

- **Over the six rises:** rms **0.5287 °C**, mean miss **−0.3466 °C** (R less the model), for v3 and v4 alike. **Over the four cool-downs:**
  rms 0.2787 °C, mean −0.0832 °C.
- **Beside it, as M1-4 sets them** (words of their own, never E185's): E185-BEST's rms on the measured watts, F 0.2146, B 0.2578 and Rl
  0.2158 °C (NOT SEPARATED (F, Rl)). The registered arms' planned forecasts at this room by the same room rule, from the plan's watts as the
  model's are: rise rms F 0.4083, B 0.5900 and Rl 0.4710 °C.
- *Post hoc, deciding nothing:* the model reads the fp32 holds about 0.8 °C high (H_E, H_E2) and the int8.full holds 0.3-0.4 °C high, from
  the plan's watts at an extrapolated room. Its S reads inside and its S2 low.

## Labels

- **Modelled:** every figure of october-forecast-model, as frozen (v3 Sat 7 Nov 2026 23:32:50 PST, v4 Sun 8 Nov 2026 03:59:42 PST; sha256 as
  note M1 gives them), before any E185 datum.
- **Measured, blind:** E185's rises, as the committed `scored-m11.json` gives them. The cool-downs are recovered from the score's 4-decimal
  misses, to about ±0.004 °C (M1-4).
- **Reported:** both arms. Nothing here changes a rule, a verdict, what M11 carries, or README.md.

SPDX-License-Identifier: Apache-2.0
