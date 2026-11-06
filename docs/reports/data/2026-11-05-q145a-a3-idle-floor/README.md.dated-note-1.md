# aifoundry3's idle floor, dated note 1 (post hoc): "settled" where it was meant, every November floor under both gates, what a short rest leaves, and the loop gain by either law

*Beside [`README.md`](README.md) (`95c75047`, committed 23:11:50 PST Thu 5 Nov 2026; its "about 22:55-23:20 PST" overruns its own commit).
It edits none of the study's files (`SHA256SUMS` 7 of 7 still pass). Written Fri 6 Nov 2026 (week 45), from about 00:00 PST until its
commit, on the Intel, desk only, by the lane fix-heat-q145a of Q145(a), round A, from an adversarial verifier's faults. **Post hoc and
descriptive, like the study:** it reads the study's committed `floors.json` and `floor_analysis.json`, and two committed model files,
and decides nothing. M11's dated amendment A7
([`REGISTRATION.md.dated-note-A7.md`](../../../../tools/claims-v3/m11/REGISTRATION.md.dated-note-A7.md)), committed with it, carries
what it changes in A6.*

## 1. "Settled", where it was meant

Section 4's counts are on the settled sessions (rest at least an hour), as it says: G0 17 of 26 and 11 of 12 in November; G0-A6 21 of 26
and 12 of 12. **On every November floor, settled or not** (`floor_note1.py` item 1), the counts are lower:

| November 2026 | sessions | G0 as registered passes | G0-A6 passes |
|---|---|---|---|
| settled (rest at least 1 h) | 12 | 11 | 12 |
| all | 24 | 21 | 22 |

A6-1 would stop two of them before the smoke:
- Sun 1 Nov 00:35: firmware 54 °C, est 54.94 °C, rest 0.68 h;
- Mon 2 Nov 16:43: firmware 53 °C, est 53.94 °C, rest 0.66 h.

So section 4's "Before noon in November every floor would pass" means every **settled** floor.

## 2. What a short rest leaves

Item 2 compares each session's firmware floor with the lowest floor of the settled sessions (rest at least 2 h) that started within
6 h of it:

| rest | sessions with such a neighbour | most above it (firmware, °C) | 2 °C or more above |
|---|---|---|---|
| under 0.75 h | 15 | 4 | 2: the two floors of section 1 (54 against 51; 53 against 49) |
| 0.75-1 h | 1 | 1 | 0 |
| 1-2 h | 2 | 1 | 0 |
| 2-4 h | 7 | 1 | 0 |
| 4 h and more | 7 | 3 | 1: E176 (52 against E171's 49 that morning), the room |

M6's slowest pole leaves 0.050 °C at 40 minutes, 0.023 °C at an hour and 0.002 °C at two hours, for a 25 °C plateau (item 3). Section
1's "bounds the tail of any earlier run at 0.005 °C there" (at an hour) should read 0.023 °C. The two floors 3-4 °C up after 40-41
minutes are far beyond that pole, and the cause is not identified. The sessions after 0.75-2 h of rest show no such excess, but there
are only three of them.

## 3. The loop gain at the floor, by either law

The README takes the loop gain at the floor from E97's law (g = R × k(T), R 0.8695 °C per board W). Item 4 reads it also by the footing
law's FL1, built from E44's and E71's dedicated cycles, on the firmware reading (each floor less the study's mean offset, 0.94 °C):

| raw-code floor | 34-sensor mean (°C) | g by E97's law | g by FL1 |
|---|---|---|---|
| E89, Sat 31 Oct 17:59 | 51.773 | 0.237 | 0.232 |
| E144, Mon 2 Nov 22:37 | 50.888 | 0.228 | 0.223 |
| E154, Tue 3 Nov 17:53 | 50.982 | 0.229 | 0.224 |
| E166, Wed 4 Nov 14:20 | 51.838 | 0.238 | 0.232 |
| E176, Thu 5 Nov 17:21 | 53.202 | 0.253 | 0.246 |

FL1's band starts at 52 °C, so these floors (49.9-52.3 °C on the firmware reading) are extrapolated by up to 2 °C. Section 2's split
(E176: +1.92 °C room, +0.39 °C the card's own) rests on the board's measured idle draw, not on a law; the law's g beside it moves by
0.005-0.007 between the two laws.

## Files and how to reproduce (`SHA256SUMS-note1`)

| file | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| `floor_note1.py` | items 1-4, from this study's `floors.json` and `floor_analysis.json`, Q138(t)'s `model-q138t.json` and the footing law's `footing-law.json` |
| `floor-note1.json`, `floor-note1.txt` | its output and printout |

```bash
# from the lab clone's top (no numpy needed); under a second
python3 -B docs/reports/data/2026-11-05-q145a-a3-idle-floor/floor_note1.py . <scratch>/floor-note1.json
```

SPDX-License-Identifier: Apache-2.0
