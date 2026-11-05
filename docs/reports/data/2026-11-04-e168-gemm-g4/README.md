# E168: G4's blind test on aifoundry2 - a governed large GEMM's sustained board to 0.82 W rms and window die to 0.51 °C (both PASS, 9 of 9), but its clock to 30.2 MHz rms (FAIL, 6 of 9 within 15 MHz: S3's shape runs 59-63 MHz under G4); both int8 increments PASS; A2's cold int8 zeros hold reads OPPOSITE SIGN

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 1** ("where a large GEMM falls") and **item 6** (the power model). It answers **rank 5 of Q139's final critic** (the large GEMM's
sustained path, G3 to G4) and Q140's and Q141's critics' E168 entry (`card_half[5]`).*

*Wed 4 Nov 2026 (week 45), the card half of Q141, aifoundry2 card 0 under its own governor (65 W / 65 °C read at the queue's start and
end and after every run, nothing set), E136's `rgm136` binaries (`76475508` / `aace138c` / `77a46171`). Registered before any E168 data:
Q140(q)'s design, G4 and its scorer `49575094` (02:26:25 PST), `e39d06da` (02:49:40) and `1bfaa4e4` (04:03:20); amendment A2, the cold
int8 zeros hold ([`REGISTRATION-A2-cold-int8-zeros.md`](../../../../tools/claims-v3/e168/REGISTRATION-A2-cold-int8-zeros.md)) `226249e1`
(09:18:35); the kit and its README, which is E168's registration of the run, `a0310012` (09:38:43); the notes `d86cafa6` (09:40:30) and
`983e9499` (10:31:55). It ran after E165 and E167 on the same card, from the checkout at `5e1bb309` (E165's README, D1). The day's one
`#community-lab` post (message 1567662592850399304) named aifoundry2 from 14:11:27 PST.*

## The answer

| rule (Q140(q)'s A7, its frozen scorer) | measured − G4 | line | verdict |
|---|---|---|---|
| **G4, the window clock**, all 9 scored holds | **30.2 MHz rms** (mean −21.3); 6 of 9 inside | within 15 MHz on at least 8 of 9 | **FAIL** |
| **G4, the board**, all 9 | **0.82 W rms** (mean +0.18); 9 of 9 inside | within 2 W on at least 8 of 9 | **PASS** |
| **G4, the window die**, all 9 | **0.51 °C rms** (mean +0.46); 9 of 9 inside | within 1 °C on at least 8 of 9 | **PASS** |
| the increment rule, S2 W8A8 real over S2 int8 zeros | +7.74 W measured, +7.64 W G4: **+0.10 W** | ±1.328 W | **PASS** |
| the increment rule, S2 sparse50 over S2 int8 zeros | +8.51 W measured, +7.71 W G4: **+0.80 W** | ±1.328 W | **PASS** |
| the registered subset (the six fp32 random holds) | clock 36.3 MHz rms, 4 of 6; board 0.93 W, 6 of 6; die 0.39 °C, 6 of 6 | as above | clock **FAIL**, board **PASS**, die **PASS** |
| R0, the check of C | 2,425 kernel records in 125 work launches, every one ok; no work launch without its record | all ok | **PASS** |
| A2 (reported, not in A7): the cold minus warm int8 zeros window board | **−0.777 W** (starts 49 and 56 °C); G4 +1.079 W at those starts (+1.334 nominal), G3 +0.517, E136's law 0; h = 0.54 W | | **OPPOSITE SIGN**: the window board falls with the start, the direction of a leakage law in the absolute die |

Source: [`results.json`](results.json) and [`reduce.txt`](reduce.txt), by the registered reduction
[`reduce_e168.py`](../../../../tools/claims-v3/e168/reduce_e168.py) (the freeze checked first: `score_e168.check` 9 files, the sidecar 18
of 18, A2's predictions as registered), with E165's zeros-anchor reads passed as `--anchors` for the reported `G4_own_anchors` arm. Every
hold ran complete; none was cut, none refused by the 82 W admission, no peak lock.

| hold | measured MHz / W / °C | G4 | measured − G4 | G3 as frozen | E136's law | start °C |
|---|---|---|---|---|---|---|
| S1 fp32 random, cold | 626.5 / 52.04 / 65.78 | 639.5 / 52.96 / 65.47 | −13.0 / −0.93 / +0.31 | 643.5 / 52.56 / 65.50 | 745.3 / 62.06 / 62.76 | 49 |
| S1 fp32 random, warm55 | 606.7 / 50.63 / 66.00 | 614.6 / 49.31 / 65.48 | −7.9 / +1.32 / +0.52 | 613.4 / 49.24 / 65.50 | 745.3 / 62.06 / 65.42 | 56 |
| S2 fp32 random, cold | 629.3 / 52.93 / 65.79 | 640.4 / 53.58 / 65.45 | −11.1 / −0.65 / +0.34 | 644.5 / 53.20 / 65.50 | 738.6 / 62.06 / 62.38 | 48 |
| S2 fp32 random, warm55 | 604.4 / 51.18 / 65.97 | 617.0 / 50.00 / 65.48 | −12.6 / +1.18 / +0.49 | 616.0 / 49.94 / 65.50 | 738.6 / 62.06 / 65.42 | 56 |
| **S3 fp32 random, cold** | 646.3 / 52.10 / 65.65 | 705.1 / 52.92 / 65.41 | **−58.9** / −0.83 / +0.24 | 707.8 / 52.32 / 65.49 | 796.6 / 59.37 / 61.65 | 49 |
| **S3 fp32 random, warm55** | 624.3 / 50.23 / 65.81 | 686.8 / 49.91 / 65.44 | **−62.5** / +0.32 / +0.37 | 686.0 / 49.80 / 65.50 | 796.6 / 59.37 / 64.30 | 56 |
| S2 int8 zeros, warm55 | 794.6 / 36.60 / 57.95 | 800.0 / 36.51 / 57.38 | −5.4 / +0.10 / +0.58 | 800.0 / 37.36 / 57.80 | 800.0 / 37.13 / 55.05 | 56 |
| S2 int8 W8A8 real, warm55 | 794.9 / 44.34 / 61.59 | 800.0 / 44.15 / 61.30 | −5.1 / +0.20 / +0.29 | 800.0 / 44.58 / 61.55 | 800.0 / 43.97 / 57.52 | 55 |
| S2 int8 sparse50, warm55 | 784.5 / 45.12 / 62.37 | 800.0 / 44.21 / 61.39 | **−15.5** / +0.90 / +0.98 | 800.0 / 44.66 / 61.64 | 800.0 / 44.06 / 57.93 | 56 |
| A2: S2 int8 zeros, cold (reported) | 794.9 / 35.83 / 55.67 | 800.0 / 37.59 / 56.27 | −5.1 / −1.76 / −0.60 | 800.0 / 37.87 / 56.47 | 800.0 / 37.13 / 52.39 | 49 |

## What this does to predicting power and heat

The term tested is G4, a governed large GEMM's sustained path (G3's chain and trip rule, Q140(l)'s zeros level, the governor's dip at each
process, M8's span fraction), blind for the first time.

| | clock | board | window die |
|---|---|---|---|
| **before**: G4 held out over five sessions (Q140(q)) | 10.3-11.1 MHz | 1.33-1.47 W | 0.58-0.63 °C |
| before: G3, blind on E159 | 8.7 MHz | 1.94 W | 0.99 °C |
| **after**: G4, blind on E168 (9 holds) | **30.2 MHz** (mean −21.3) | **0.82 W** (+0.18) | **0.51 °C** (+0.46) |
| beside it, E168: G3 as frozen / E136's law / the chain on the measured trace | 30.9 / 113.5 MHz | 0.74 / 7.97 W | 0.38 / 3.06 / 0.53 °C |

(`results.json` › `all_scored.summary`.) **The board and the die from the bits now hold blind** on a governed large GEMM: 0.82 W and
0.51 °C, every hold inside the lines, both int8 increments inside ±1.33 W. G4 is not better than G3 as frozen on the board or the die
here (G3 0.74 W, 0.38 °C), and it is far better than E136's law (7.97 W, 3.06 °C). **The clock is where it misses, and only on one
shape:** S3 (`gemmL3x5x3`) ran 59-63 MHz under every model's sustained clock (G4, G3 and E136's law alike), while S1 and S2 fp32 random
held to −7.9 to −13.0 MHz. Post hoc, labelled, from the table above: without S3's two holds, G4's clock error is 10.8 MHz rms over the
other seven, the size its held-out estimate gave. So the next clock term is a per-shape one at S3's geometry, not a session or start term.
**A2** says the start dependence G4 carries has the wrong sign on this card: a cold start (49 °C) gave a window board 0.78 W *lower* than a
warm one (56 °C), where G4's start-referenced leakage law expects +1.08 W at those starts. The day's zeros anchors from E165
(`G4_own_anchors`, reported) move nothing: 29.8 MHz, 0.83 W, 0.51 °C.

## The session

| | PST | card-minutes | |
|---|---|---|---|
| queue | 16:18:49-17:06:09 | | `queue_e168.py --slots ~/claude/work/q141-a2-e168-slot.txt --runs build/e168/runs`, detached; slot 16:18:49-17:24:49 (66 minutes) |
| smoke | 16:18:49-16:19:49 | 1.0 | rc 0; the check of C on all four launches |
| stop test, board | to 16:19:53 | 0.1 | `board_cap_w` 30 W: `board 36.1 W > 30 W on 3 samples`, 65 ms after the third line |
| stop test, die | to 16:19:55 | 0.0 | `abs_stop_c` 30 °C: `die 70 C >= 30 C` on the first live line (the hottest-sensor latch) |
| `s1` | 16:19:55-17:06:08 | 46.2 | R, the nine holds, A2's hold, all complete; exit 0 "done" |
| in all | | **47.3** | the session cap 58, at most 63 in all |

**The gates:** every cold gate (the die at or under 46 °C, at most 360 s) timed out after 360.1 s at 48-49 °C (S1, S2 and S3 cold, and
A2's), so the cold holds started at 48-49 °C, not 46; every warm55 gate reached 55 °C, in 0-42 s. The kit's dated note foresaw a rest floor
above 46 °C and showed A2 keeps all three readings there; the scorer reads each hold's measured start. **Peaks:** board 76.59 W, the shires'
mean 67 °C, the hottest-sensor field 70 °C (its latch). The registered stops (one die reading at or above 76 °C, or the board above 85 W on
three live samples) never came near; both fired on live samples in their tests.

## Departures and notes (dated, Wed 4 Nov 2026)

- **None from the registration.** The protocol, the order, the slot, the stops, the admission, the scorer and the cut rule are as
  registered; nothing was re-run.
- **The tree**: fast-forwarded to `5e1bb309` before the day's first session (E165's README, D1); the preflight then read E136's three
  binaries and `run_e168.py --list` (11 runs, 9 tiles verified) clean on the box, and the dry pass into `build/e168/dry` ended rc 0 at
  14:26:30 PST, before E165's session.
- **Collection**: the runbook's v2 step (`tools/claims-v3/q141k-runbook/v2/s22_collect.sh e168`): a bounded copy of `build/e168/runs` only,
  E111's login scrub, `launches.jsonl` and `tel/*.jsonl` gzipped as E159's sessions, then `reduce_e168.py --anchors` with E165's
  `anchors-for-e167-e168.json`.

## Device commands sent

Exactly the registered set ([`README.md` § Device commands sent](../../../../tools/claims-v3/e168/README.md#device-commands-sent);
[`logs/dmcmd-audit-2.txt`](../../../../tools/claims-v3/e168/logs/dmcmd-audit-2.txt): GO, 19 send sites, every one READ): `ettelem sample`
and `ettelem config` reads (the PMIC voltage reads among them, the owner's allowed read-only reads), the trace copy, and the residency
read this build refuses before opening the device. No statistics reset, no firmware-revisions query, no governor, TDP, threshold or clock
set.

## Files

| file | what |
|---|---|
| [`results.json`](results.json), [`reduce.txt`](reduce.txt) | the registered reduction (A7, A2 reported, R0, the safety record, every hold's gate) |
| `aifoundry2/` | the queue's records (`queue.jsonl`, `status.json`, the admission, the start and end snapshots) and the smoke, the two stop tests and `s1` (launches and the sampler lines gzipped) |
| `logs/` | `queue.out` and the slot file |

SPDX-License-Identifier: Apache-2.0
