# E183: the one-number vector add, its second round, on aifoundry3 card 0 - both sides of the add pay (E183-MECH BOTH): a result 1-bit +0.0076 W [+0.0065, +0.0087] and an operand 1-bit +0.0031 W [+0.0017, +0.0045]; his pair, 5s against 4s, reads +0.0112 W [+0.0053, +0.0171], POSITIVE and at E180's measured price

*It answers, a third time, the owner's ask of Thu 5 Nov 2026, about 19:30 PST ("adding a matrix filled with 4s is a different than adding
a matrix filled with 5s ... Ideally it's one number, and then be able to forecast the number of flips and then be able to test this
experimentally"), as registered in [`tools/claims-v3/e183/E183.md`](../../../../tools/claims-v3/e183/E183.md) (`c98a7287`, committed
alone, Sat 7 Nov 2026) with its dated notes 1, M1 (and M1's dated note 1) and M2, and its dated amendment
[A1](../../../../tools/claims-v3/e183/E183.md.dated-amendment-A1.md) (`977c63d1`: this day's second session), and kitted by
[`KIT.md`](../../../../tools/claims-v3/e183/KIT.md) with its dated notes 1-6. Fri 13 Nov 2026 (week 46), aifoundry3 card 0 at 600 MHz
pinned, nothing set, on the owner's go that day: *"Continue the experiments."* (about 11:03 PST) and *"Feel free to use all four cards, and
you don't need to post on Discord."* (about 11:30 PST). **Blind:** every forecast and rule below was committed before the session's opening
config read on the card (15:45:05 PST), and these are the first E183 trains on any card.*

- **Card:** aifoundry3 card 0, **600 MHz in all 30,060 samples** of the session's 10 Hz telemetry. `ettelem config` through E128's guard at
  the session's start (15:45:05 PST) and end (16:36:43): TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV then 522 mV. **Nothing was
  set.** `since_reset_ms` −1 in every sample: no statistics reset.
- **Card session** T0 1794613504 = 15:45:04 PST to its `session end` at 16:36:43 PST: **3,099 s, 51.65 card-minutes**, inside FULL's cap of 65
  (3,900 s from T0). The stop-path test 18302, the smoke 18301 and its registered gate, then **FULL as registered**: the six trains in the
  registered order, 18310 (T3), 18311 (T1), 18312 (T4), 18313 (T6), 18314 (T2) and 18315 (T5); the queue's last line reads `e183: done, 6
  items, at T0+3099 s`. **Every train ran whole:** 52 of 52 processes with a value in each of T3, T1, T4, T6 and T2 (26 units each), 202 of
  202 in T5 (101 units), and each block's four anchors; no block or process was set aside.
- **The smoke's registered gate:** `SMOKE GO: 4 bursts, rates 4.5884e+11-4.5928e+11 a second; 2 train processes of 13 launches by the
  schedule, at 600 MHz`, then `smoke gate passed: queue starts (plan FULL)` (15:46:05). The stop-path test fired its board and die stops on
  live samples, before a run and in the watcher, with no launch.
- **No stop fired:** the highest live readings were **48.28 W board** and **65 °C `minshire[0]`** (both at 16:36:15, T5's closing random anchor),
  against the stops 65 W and 70 °C. The train blocks' own notes read the die at 62.1-64.2 °C at most.
- **Every device-management command sent was a read:** `dmcmd_audit` GO on the session's files before any device opened (32 send sites,
  0 disallowed); the one conditional statistics reset in lib.sh was never reached (`since_reset_ms` above).
- **This day's first session is not in this directory.** It launched at 13:14:18 PST and stopped at its smoke gate by a defect of the kit
  before any train block (61 s, 1.0 card-minute). Amendment A1 sets its smoke and stop-path test aside (no rule reads them), and the kit's
  step 5b moved them on the box, before this session, to `build/claims-v3/aifoundry3/e183-aside-2026-11-13-t1794604458/` (`ASIDE-DONE`, 19
  files, each at the desk copy's sha256, nothing removed). **The day's card time on aifoundry3 card 0: 1.0 + 51.65 = 52.7 card-minutes**
  (3,160 s), beside the two sessions' reads steps (a config read of about a second each).
- **The day's post and its release were waived by the owner** (his words above); every other etiquette check stood: the look before the
  session read the card free (no holder of its nodes or lock, no other user's device process), and the kit takes the card's lock for each
  block (lib.sh) and runs every device process under `timeout 10` (the kit's design, which its note 6's real-path desk test counts; this
  session's files do not print either).

## The answer (the registered rules, blind)

The scorer's words govern ([`scored-e183.md`](scored-e183.md); `scored-e183.json` > `rules`): **FAIL HIGH = the forecast lies above the
measured interval; FAIL LOW = below.** A train's interval is t(0.975, units − 1) over its units (two processes each, one of each
orientation); b = (T1 + T3) / 14 and c = (T2 + T4) / 14, each with its Welch-Satterthwaite interval (E183.md section 5.1). P is E180's frozen
primary, BLIND E180's measured price (E180-L), OPER and BOTH post hoc fits on E180's data (forecasts for E183).

| rule | what | measured, W (95%) | forecast lines, W | verdict |
|---|---|---|---|---|
| **E183-B** | b, a result 1-bit (T1, T3) | **+0.007576 [+0.006471, +0.008682]** | BLIND +0.009693, P +0.164915; REPEAT: E180-L [+0.002734, +0.016652] | **POSITIVE**; SIZE **FAIL HIGH** against BLIND and against P; REPEAT **AGREES** |
| **E183-C** | c, an operand 1-bit (T2, T4) | **+0.003118 [+0.001702, +0.004534]** | OPER +0.008301; REPEAT: the operand-only fit [+0.002333, +0.014269] | **POSITIVE**; SIZE **FAIL HIGH** against OPER; REPEAT **AGREES** |
| **E183-MECH** | E183-B's and E183-C's words | B POSITIVE, C POSITIVE | RESULT if BLIND, OPERAND if OPER, BOTH if BOTH | **BOTH** |
| **E183-HT**, his pair (T5) | 5s − 4s, 202 processes | **+0.011165 [+0.005261, +0.017068]** | P +0.1649, BLIND +0.0097, OPER +0.0083, BOTH +0.0092; REPEAT: E180-H [−0.0503, +0.1043] | **POSITIVE**; SIZE **FAIL HIGH** against P, **PASS** against BLIND, OPER and BOTH; REPEAT **AGREES** |
| **E183-X**, the exponent control (T6) | T6 − (6 b − c) | −0.007260 [−0.023461, +0.008941] | 0 | **CONSISTENT**; T6 **POSITIVE** |
| **E183-J**, the fill | T3 − T1; T4 − T2 | −0.00875 [−0.02423, +0.00673]; −0.00845 [−0.02827, +0.01138] | 0 | **CONSISTENT**; **CONSISTENT** |
| **E183-TR-N**, the train method's noise | the pooled quad sd over sigma_q (0.06249 W) | 0.06890 W: **1.103** | at most 1.25 | **AS FORECAST** |
| **E183-TR-H**, its reach | the median over the six trains of the measured half-width over the plan's base half-width | **1.300** (1.089-1.524) | 0.8-1.25 AS PLANNED, 1.25-2.0 WORSE | **WORSE** |

E183-HT's SIZE word against the OFM line (a reported arm, E183.md section 8) is in [`scored-e183.md`](scored-e183.md). **The owner's
sentence for the add, measured** (the scorer's flag: E183-HT POSITIVE with SIZE PASS against BLIND, and E183-MECH RESULT or BOTH): **yes**
(`owners_sentence_measured: true`).

**The trains' half-widths, by the registered t statistic** (E183.md's dated note 1): a 52-process train was planned to read its pair to
about ±0.0103 W at E180's noise (0.0205 W at twice it), and T5 to about ±0.0051 W (0.0101 W). Measured: T3 0.0107, T1 0.0117, T4 0.0138,
T6 0.0149, T2 0.0150 and T5 0.0059 W. E183-TR-H divides by the plan's z values (0.00981 and 0.00498 W, its registered denominator; dated note 1
names that offset: a median ratio of about 1.035 at E180's noise when the method works as planned), so its six ratios read 1.09-1.52, median
1.30: WORSE, below FAILS (2.0).

**What the card says, in plain words** (the registration's words for each verdict, E183.md section 5.4; the ratios and sums marked
*arithmetic* are desk arithmetic on the numbers above, post hoc, deciding nothing):
- **Both sides of the add pay** (MECH BOTH: "each side pays"). A result 1-bit costs +0.0076 W and an operand 1-bit +0.0031 W, and the two
  intervals do not overlap: the result's bit is the dearer, about 2.4 times the operand's (*arithmetic*). E180's one slope, +0.0097 W a
  result bit, read on kinds whose result and operand popcounts moved together, lies above b's interval (SIZE FAIL HIGH against BLIND), and
  b's interval lies inside E180-L's own (REPEAT AGREES); b + c is +0.0107 W (*arithmetic*).
- **His pair, 5s against 4s, reads +0.0112 W** [+0.0053, +0.0171]: a matrix of 5s costs more to add than a matrix of 4s. The pair moves one
  result bit and one operand bit, and b + c (+0.0107 W) lies inside its interval (*arithmetic*). BLIND, OPER and BOTH each read inside it;
  P, the named-net price, reads about 15 times too high (*arithmetic*: 0.1649 / 0.0112).
- **The exponent field's bits cost as the mantissa's do** at this resolution (E183-X CONSISTENT, T6 POSITIVE), and **a bit's price does not
  move with 16 more bits held** (E183-J CONSISTENT for the result's side and the operands').
- **The method:** the trains' noise is as forecast (TR-N 1.10); their reach is worse than planned (TR-H 1.30), the widest half-widths being
  T4's, T6's and T2's (0.014-0.015 W).

## Reported beside, never a verdict

- **Each train against every line** (`scored-e183.json` > `reported` > `trains` > `against`: where each forecast lies against the measured
  interval):

  | train | first − second | measured, W (95%) | units | BLIND | OPER | BOTH | P |
  |---|---|---|---:|---|---|---|---|
  | T3 | R(16): 0x407FFFFE − 0x3FFFFF80 | +0.0487 [+0.0380, +0.0593] | 26 | above (+0.0678) | below (0) | below (+0.0322) | above (+1.1544) |
  | T1 | R(0): 3.96875s − 1.0s | +0.0574 [+0.0457, +0.0691] | 26 | inside (+0.0678) | below (0) | below (+0.0322) | above (+1.1544) |
  | T4 | O(16): 0x3FFFFFC0 − 0x407FFF80 | +0.0176 [+0.0038, +0.0314] | 26 | below (0) | above (+0.0581) | above (+0.0320) | below (0) |
  | T6 | the exponent control: 0.5s − 1.0s | +0.0351 [+0.0202, +0.0500] | 26 | above (+0.0582) | below (−0.0083) | inside (+0.0230) | above (+0.9895) |
  | T2 | O(0): 1.5s − 2.0s | +0.0260 [+0.0111, +0.0410] | 26 | below (0) | above (+0.0581) | inside (+0.0320) | below (0) |
  | T5 | his pair: 5s − 4s | +0.0112 [+0.0053, +0.0171] | 101 | inside (+0.0097) | inside (+0.0083) | inside (+0.0092) | above (+0.1649) |

- **The joint fit** (weighted least squares of the six trains on (dR, dO), through the origin): b +0.007341 (se 0.000492) and c +0.003160
  (se 0.000681) W a bit, beside the registered pairs' b +0.007576 and c +0.003118.
- **The anchors**, fadd.ps random − fadd.ps zeros (E180's catalogue reduction of each train block's anchor bursts, at its open and close):
  +8.493 W [+8.052, +8.935] over the 12 readings, against E180's RA5 board reading +8.455 [+8.342, +8.568]: AGREES (RA5's mean inside). By
  block, open / close: T3 6.373 / 8.930, T1 8.438 / 8.717, T4 9.124 / 8.684, T6 8.550 / 8.648, T2 8.521 / 8.812, T5 8.509 / 8.614 W; T3's
  opening reading, the session's first train block's, is the lowest of the twelve.
- **In each train** (`scored-e183.json` > `reported` > `trains`): its two halves, first then second (T3 +0.0581 then +0.0392; T1 +0.0560,
  +0.0588; T4 +0.0124, +0.0228; T6 +0.0384, +0.0317; T2 +0.0272, +0.0249; T5 +0.0134, +0.0090 W); its orientations' means, FSSF / SFFS (T3
  +0.0443 / +0.0531; T1 +0.0489 / +0.0659; T4 +0.0100 / +0.0252; T6 +0.0377 / +0.0325; T2 +0.0183 / +0.0338; T5 +0.0080 / +0.0143 W); its
  carry-over reading, the kit's (the SFFS quads' mean L3 − L2 less the FSSF quads', over twice the train's estimate): T3 +0.089, T1 +0.050,
  T4 −0.454, T6 +0.071, T2 +0.011, T5 −0.037; each launch's rate, F over S, 0.99975-1.00021 (the timing does not depend on the number); and
  the minion rail's mean over the train, 17.09-17.67 W.
- **The kernel's loop** ([`logs/loopcmp-e183.txt`](logs/loopcmp-e183.txt)): `LOOP-SAME: mode 160's loop, 72 instructions, equals E180's
  instruction by instruction`.
- **october-forecast-model's arms** (E183.md's dated note M1, with its dated note 1, and note M2; reported, never a rule) are read after this
  directory's commit, through the day-2 check v2's gate, as the card lane's brief's dated note 2 says; the reader's run line, `READER-RC` and
  outputs go in a dated note beside this file.

## The readings, labelled

- **Blind:** every registered rule above. Every forecast line (P, BLIND, OPER, BOTH, OFM), statistic, band and threshold was frozen in E183.md
  (`c98a7287`, Sat 7 Nov 2026) before any E183 datum. BLIND is E180's measurement, blind on 6 Nov; OPER and BOTH are post hoc for their fits
  on E180's data, and forecasts for E183.
- **Measured:** the session's readings (`raw/`, `logs/`), reduced by `reduce_e183_v2.py` with the session's T0 and scored by `score_e183.py`,
  both as committed.
- **Reported:** the joint fit, the anchors, the trains' halves, orientations, carry-over, rates and rail, the loop compare, and
  october-forecast-model's arms.
- **Desk arithmetic, post hoc:** the ratios and sums marked *arithmetic* above. **Nothing here was fitted to these data.**

## What ran (Fri 13 Nov 2026, PST; orchestrated from aifoundry2)

The card lane's brief's dated note 5 (its table) and the kit's dated note 6 (section 10). Every step's file is in
`tools/claims-v3/e183/rb/` (k6's in `tools/claims-v3/q141k-runbook/k6/`); each exited 0.

| step | time | what it read |
|---|---|---|
| 0 | 15:43:56-15:43:58 | the day-2 check v2 (`check_day2_v2.py tree --pull`): DAY2-CHECK-V2 OK at `977c63d1`; the go's anchor lines (note 4's 1-6, note 5's 1-5, note 6's 1-5), each true |
| 1 | 15:44:05 | the window (amendment A1-3): day 2026-11-13, last start 21:00, last end 22:30 PST, in a new runbook directory |
| 2 | 15:44:08-15:44:12 | step 2 v7 (`s03_desk_e183_v7.sh`) at `977c63d1`: note 6's list 47 of 47 and A1's 5 of 5 at their own bytes; HARNESS OK 92 files; note 6's four desk tests' logs |
| 4 | 15:44:14-15:44:15 | the look (`s05_look_k6.sh`): FREE |
| 3 | - | the post: waived by the owner |
| 5a | 15:44:19 | the build records (`s06_a3_records_e183.sh`): RECORDS COPIED, 12 files; the box's compiler GNU 13.3.0 |
| 5b | 15:44:23 | the aside (`s06b_a3_aside_e183.sh`): ASIDE-DONE |
| 5 | 15:44:37 | the sync (`s07_a3_sync_e183.sh`): 80 files, HARNESS OK 80 |
| 6 | - | not run: the day's one good build (13:13:41-13:13:45 PST, `TRAIN-HOST-BUILT rc=0`) stands |
| 7 | 15:44:42 | the reads (`s09_a3_reads_k6.sh`): TDP 0 W / 65 °C / 600 MHz / 523 mV; et-who clean |
| 8 | 15:44:45-15:44:50 | the dry pass v3 (`s10_a3_dry_e183_v3.sh`, job `a3-dry-e183-v3`): rc 0 (18310, the smoke and the stop test each rc 0; the start gate 8, as wanted) |
| 9 | 15:45:04-15:45:10 | the session (`s11_a3_session_e183_v3.sh FULL`): `rest: 149 minutes since E183's session end (2026-11-13 13:15:19 PST; ...)`; LAUNCHED, T0 1794613504; the log's first line ends `kit note 6; plan FULL` |
| 10 | 15:45:14-16:36:47 | the wait v2 (`s20_wait_e183_v2.sh`): RUN-RUNNING (17) five times, then RUN-ENDED (0) |
| 11 | 16:36:58-16:37:00 | the collection v3 (`s22_collect_e183_v3.sh`; the release waived): COPY EXACT, 99 files; the frozen inputs at their pins (20, 46, 46); LOOP-SAME; the desk-path gate CLEAN (105 files); the login scrub OK (83 files in 13 directories) |

**Before this commit, at the desk:** a second login scrub (E164's check in each of 30 directories, the text inside the 22 `.gz` files
included; no other user's holder line, list entry or path; no stop line): CLEAN. The public-text scan (the lab scanner's fixed list and its
local table, over every text file and the text inside every `.gz`): 8 hits, each the box's own block path in
`logs/queue-t1794613504.out` and `logs/session-t1794613504.log`, the form E180's and E185's committed data carry; 0 other. The reduction and
the score, run again from `raw/` with the session's T0, equal `reduced-e183.json`, `scored-e183.json` and `scored-e183.md` byte for byte.
**Interpreter:** every desk reader here (the reduction v2, the scorer, the copy check, the loop compare, the scrubs and the scans) ran under
`/usr/bin/python3` 3.12.3 on aifoundry2; the kit was written under 3.9 (its dated note 5's
[`logs/port-aifoundry2-e183.txt`](../../../../tools/claims-v3/e183/logs/port-aifoundry2-e183.txt) records its readers' self-tests on both).

## Files

- `raw/e183/p18310`-`p18315`: the six train blocks (each `block.json`, `run.log`, `runs.jsonl.gz`, `telemetry.jsonl.gz`, `train.jsonl.gz`,
  `marks.jsonl`, `configs.json`, `check.json`, `code.sha256`, `pass.json`, `runner.out`); `raw/e183-smoke/p18301` and
  `raw/e183-stoptest/p18302`: this session's smoke and stop-path test.
- `logs/`: the session's T0-named files (`session-t1794613504.log` and `.out`, `queue-t1794613504.out`, `dmcmd-preflight-t1794613504.txt`,
  the config reads at both ends with their times and error streams); the train host's build record (`BUILD-E183.json`,
  `e183-build-host.txt`, `e183-build-attempts.txt`, `e183-build-logs/2026-11-13/`); the kernel's listing (`e183-kernel-dis.txt`); the loop
  compare; the box's manifest of the copy-back (`box-manifest.txt`) and `absent-on-box.txt` (none absent).
- `reduced-e183.json` (the reduction v2), `scored-e183.json` and `scored-e183.md` (the scorer).
- [`SHA256SUMS`](SHA256SUMS): every file here but this README and itself (105 entries).

## Re-make it

```
cd docs/reports/data/2026-11-13-e183-vector-add-r2-aifoundry3 && shasum -a 256 -c SHA256SUMS && cd -     # 105 OK
D=tools/claims-v3/e183; R=docs/reports/data/2026-11-13-e183-vector-add-r2-aifoundry3
/usr/bin/python3 -B $D/reduce_e183_v2.py --raw $R/raw --t0 1794613504 --out <scratch>/reduced-e183.json
/usr/bin/python3 -B $D/score_e183.py --reduced <scratch>/reduced-e183.json --out <scratch>/scored-e183     # equal to the committed bytes
```

SPDX-License-Identifier: Apache-2.0
