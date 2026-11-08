# E182: where a held 1-bit costs power, on aifoundry3 card 0 - held operand bits cost on BOTH sides (E182-SPLIT A+B: beta_A +0.0083, beta_B +0.0099 W a held 1-bit a byte), where every forecast said B's side only; his int8 pair read in a train at +0.047 W [+0.040, +0.054] (E182-HT POSITIVE, SIZE FAIL HIGH against P's +0.187 W, REPEAT AGREES with E178); the fp32 swap of 23 held bits costs +0.236 W (E182-F POSITIVE, every forecast 0); E182-W-int8 FAIL HIGH against P (3.79 fJ a flip against 7.04); the train method reads as forecast

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**item 6**, "a power model across kinds". It answers, a second time, the owner's ask of Thu 5 Nov 2026, about 19:30 PST ("here's a matrix
filled with one number, and here's a matrix filled with another number, and they require different number of transistor flips, therefore
they will use different power, and I have a model which actually tracks it down"), as registered in
[`tools/claims-v3/e182/E182.md`](../../../../tools/claims-v3/e182/E182.md) with its dated notes 1-3 and M1, and kitted by
[`KIT.md`](../../../../tools/claims-v3/e182/KIT.md) with its dated notes 1-4. Sun 8 Nov 2026 (week 45), on the owner's go of Sat 7 Nov
about 21:30 PST ("I just refreshed the cards, continue"), aifoundry3 card 0 at 600 MHz pinned, the day's first session there.
**Blind:** every forecast and rule below was committed before the session's opening config read on the card (00:15:42 PST).*

- **Card:** aifoundry3 card 0, **600 MHz in all 57,500 samples**; `ettelem config` through E128's guard at the session's start (00:15:42
  PST) and end (01:53:47): TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV both times. **Nothing was set.** `since_reset_ms` −1 in
  every sample: no statistics reset.
- **Card session** 00:15:41-01:53:47 PST, **98.1 card-minutes** (T0 + 5,886 s), inside FULL's cap of 100: the stop-path test 18202, the
  smoke 18201 and both of its gates (passed at 00:16:52), then **FULL as registered**: the six trains in the registered order, 18210 (T4),
  18211 (T5), 18212 (T3), 18213 (T6), 18214 (T2) and 18215 (T1), then the kinds passes 18220, 18221, 18222 and **18223**, the fourth
  admitted by the budget rule (623 s; the session ended at T0 + 5,886 s against the budget's T0 + 5,940 s). **Every train ran whole** (64
  int8 processes, 32 units; 76 fp32 processes, 38 units), **all four kinds passes kept**; nothing set aside; no kind left out by E182-C.
- **Every launch's C is bit-exact:** 8,820 of 8,820 PASS against the RTL's arithmetic (Q139(k)'s `ccheck.py`; fp32 3,102, fp16 246, int8
  5,472; no ROUNDING, UNMODELLED or FAIL), every train launch against its own tiles. The eleven sessions that must carry a C log each carried
  one, checked to its end (`ccsessions_e182.py`: FINISHED); the stop-path test carried none. **E182-C PASS.**
- **No stop fired:** the highest live readings were **54.17 W board** (00:35:27, train T5) and **65 °C `minshire[0]`** (in the two fp32
  trains), against the stops 65 W / 70 °C. The stop-path test fired its die, board and watch stops on live samples with no launch.
- **Every device-management command sent was a read** (§ Device commands sent).
- **Two kinds-pass runs were skipped by E78's own rule**, each "launch reading not reached", not retried: 18221 #20 `int8.e182_am1_bm127` and
  18223 #16 `fp32.e182_a1_b3fffffff` (`aifoundry3/e182/p182NN/run.log`). So `int8.e182_am1_bm127` is measured in three passes and every
  other kind in four, and the reported quartet fit (E182-Q) reads three passes.

## The answer (the registered rules, blind)

The scorer's words govern: **FAIL HIGH = the forecast is above the measured interval: the model prices more than the card reads; FAIL LOW =
below.** A train's interval is t(0.975, n − 1) over its units (two processes each); beta_A and beta_B combine T3 and T2 by Welch-Satterthwaite;
the kinds-pass rules read E178's footing over the four kept passes. P is M10 frozen, P + ACC adds M10-ACC's term, E is E178's measured price,
each scored at the session's rates (`scored.json` > `rules`).

| rule | what | measured, W (95%) | forecast P / P + ACC / E, W | verdict |
|---|---|---|---|---|
| **E182-C** | every launch of every E182 kind, trains included, C-checked against its own tiles | 8,820 of 8,820 PASS | all | **PASS** |
| **E182-HT**, his pair (T1) | int8 5s − 4s, a train of 64 processes | **+0.0470 [+0.0403, +0.0537]** | +0.1867 / +0.1849 / +0.0705 | **POSITIVE**; SIZE **FAIL HIGH** against all three; REPEAT **AGREES** (E178-H-int8 +0.0532 [+0.0217, +0.0848]) |
| **E182-A**, A's side | beta_A = (T3 − T2) / 14, W a held 1-bit a byte | **+0.00834 [+0.00786, +0.00881]** | 0 / 0 / 0 | **POSITIVE** |
| **E182-B**, B's side | beta_B = (T3 + T2) / 14 | **+0.00988 [+0.00940, +0.01035]** | +0.01570 / +0.01570 / +0.00547 | **POSITIVE**; SIZE **FAIL HIGH** against P and P + ACC, **FAIL LOW** against E |
| **E182-SPLIT** | E182-A's and E182-B's words | beta_A / beta_B = 0.84 | B-ONLY (every forecast) | **A+B** |
| **E182-X**, the one-bit swap (T4) | T4 − T2 / 7 | −0.0049 [−0.0102, +0.0004]; T4 itself −0.0033 [−0.0086, +0.0019] | 0 under every split | **CONSISTENT**; T4 NOT RESOLVED |
| **E182-F**, the fp32 swap (T5) | (A 1.0, B 0x3FFFFFFF) − (A 0x3FFFFFFF, B 1.0), 76 processes | **+0.2359 [+0.2299, +0.2419]** | 0 / 0 / 0 (band ±0.015) | **POSITIVE** |
| **E182-H32T**, his fp32 pair (T6) | fp32 5.0s − 4.0s | **+0.0285 [+0.0225, +0.0346]** | +0.0105 / +0.0110 / +0.0022 | **POSITIVE**; SIZE **FAIL LOW** against all three; REPEAT **AGREES** (E178-H-fp32 +0.0523 [−0.0459, +0.1505]) |
| **E182-TR-N**, the train method's noise | the pooled quad residual sd over its forecast sigma_q | int8 0.03578 against 0.03485 (1.027); fp32 0.04017 against 0.03804 (1.056) | at most 1.25 | **AS FORECAST** |
| **E182-TR-H**, the train method's reach | one int8 pair's half-width projected from the units' sd (0.0151 W) and the period (6.603 s) | 0.0026 W at 30 min, 0.0022 W at 40 | 0.003 / 0.006 W | **BETTER** |
| **E182-W-int8** | OLS slope of the measured D on (i)'s launch-mean flips over the 20 int8 kinds, t(18) | **3.789 fJ a flip [1.447, 6.131]** | P's line 7.044 fJ; E's 2.781 | **FAIL HIGH** (its SIZE word against P, the verdict: E182.md.dated-note-1.md section 2); arm E's reading PASS |
| **E182-R-int8** | Spearman rho of P against the measured D, 20 int8 kinds | **rho +0.556** | ≥ 0.4421 (size 0.026) | **PASS** |

**The verdict words to quote.** E182-W-int8's verdict is `size_P`, **FAIL HIGH**. The scorer's `rules["E182-W-int8"]["verdict"]` field and
the verdict column of `results.md` carry `size_E` (**PASS**), which is arm E's reading, as E182.md.dated-note-1.md section 2 says. A train's
forecast half-width is 0.0051 W (doubled, 0.0102), never 0.0049: the measured half-widths here are 0.0045-0.0067 W.

**What the card says, in plain words.**
- **Held operand bits cost on both sides.** A matrix whose A words carry seven more 1-bits a byte than its B words costs nearly what the swap
  costs: A's held bit +0.0083 W a bit a byte, B's +0.0099. Every registered forecast put all of it on B's side (int8's TenB bypass, the one
  bus that returns to zero in E178's flip model) and none on A's. So a path the open RTL's model does not hold, in the full-custom register
  file or scratchpad, or another bus that returns to zero, prices A's held bits too (E182.md section 5.4, "What each outcome means").
- **The total is about M10's, split differently.** T3 (−1s against 1s, both sides from 1 to 8 bits a byte) reads +0.127 W, near P's +0.110
  and three times E's +0.038; T2 (the same bits moved from B to A) reads +0.011 W, where P says +0.110. B's price lies between E178's and M10's.
- **His pair, 5s against 4s, again:** +0.047 W, inside E178's +0.053 [+0.022, +0.085] and at about a quarter of M10's frozen price. A train
  reads it about five times more finely than E178's couples did (±0.0067 W against ±0.032).
- **In fp32, where the bits sit matters a lot.** The same 23 held 1-bits cost 0.236 W more on B's side than on A's (A is the float
  multiplier's recoded side in the open RTL); every forecast said the two orders cost the same. His pair in fp32 reads +0.029 W, above all
  three forecasts.
- **The int8 price per flip** over 20 kinds is 3.8 fJ [1.4, 6.1]: M10's 7.0 fJ is too high, E178's measured 2.8 fJ lies inside. The kinds
  order as P orders them (rho +0.556).
- **The method works.** The trains' noise is as forecast, and one int8 pair is read to ±0.0026 W in 30 card-minutes.

## Reported beside, never a verdict

- **E182-Q**, the quartet fit's split from the kinds passes (three passes with all 16 quartet kinds): beta_A +0.0098 [−0.0006, +0.0203],
  beta_B +0.0107 [−0.0025, +0.0238] W a bit a byte. It sits on the trains' A+B reading, at the kinds passes' resolution (half-width about 0.01).
- **E182-K**, each pair's kinds-pass couples (four passes) against its train (W, train − kinds pass): T1 +0.032 [−0.057, +0.121]; T2 +0.062
  [+0.008, +0.115]; T3 +0.032 [−0.040, +0.104]; T4 −0.004 [−0.115, +0.106]; T5 +0.036 [+0.013, +0.060]; T6 −0.008 [−0.034, +0.019]. The
  kinds-pass couples read T2 at −0.051 [−0.105, +0.003] and T5 at +0.200 [+0.174, +0.225].
- **The couples' order term**, the first run's D less the second's net of the pair's difference: T1 +0.059 [−0.006, +0.123], T2 +0.026,
  T3 +0.017, T4 −0.002, T5 +0.017, T6 +0.018 W, every interval holding 0.
- **Beside E182-HT's REPEAT:** the train against E178-H-int8's raw-footing interval, +0.0746 [+0.0421, +0.1072]: AGREES.
- **In each train** (`scored.json` > `reported` > `trains`): the two orientations' means (T1 0.0453 FSSF, 0.0487 SFFS; T3 0.1260, 0.1290; T5
  0.2335, 0.2383), the halves (T1 0.0441 then 0.0499; T3 0.133 then 0.122; T5 0.227 then 0.245), the carry-over reading L2 − L3 (at most
  0.015 W in magnitude; four of the twelve exclude 0: T1's SFFS +0.011, T4's FSSF −0.010, and T5's −0.012 and −0.015), the minion rail's
  level over the train (11.6-11.9 W int8, 17.6-18.0 W fp32), and the median process period, 6.60-6.69 s.
- **The seven reduction arms of the kinds passes** (E178's arms; `scored.json` > `reported` > `arms`): E182-W-int8 reads 3.74-4.25 fJ a flip,
  FAIL HIGH against P in six of seven (PASS at leak 0.3803, three passes, [0.88, 7.62]) and PASS against E in all seven; E182-R-int8 PASS in
  six of seven (FAIL at leak 0.3803, rho +0.397).
- **Every kind's D against P, P + ACC and E** (`scored.json` > `reported` > `kinds`). The largest misses against P: `fp32.e182_a1_b3fffffff`
  +0.382 W, `int8.e182_am1_b1` +0.219, `int8.e182_a85_b1` −0.210.
- **october-forecast-model's arm** (E182.md.dated-note-M1.md, committed before T0; REPORTED, read by M1-4's words, never a rule): its reader
  is [`arm_m1_read_e182.py`](arm_m1_read_e182.py), written at the desk during the session (finished 00:18:47 PST, before any E182 datum
  reached the desk; sha256 `2afcb703…`), and its readings are [`arm-m1-e182.txt`](arm-m1-e182.txt) and `.json`. The model's figures are at
  the card rail, the measurements at the board; nothing is scaled.

  | | model, W (card rail) | measured, W (board) | the model reads |
  |---|---:|---|---|
  | T1, his pair | +0.0391 | +0.0470 [+0.0403, +0.0537] | below, the same sign |
  | T2 | +0.0111 | +0.0108 [+0.0063, +0.0153] | **inside** |
  | T3 | −0.0096 | +0.1275 [+0.1225, +0.1325] | below, the other sign |
  | T4 | +0.0018 | −0.0033 [−0.0086, +0.0019] | inside, the other sign |
  | T6, his fp32 pair | +0.0127 | +0.0285 [+0.0225, +0.0346] | below |
  | beta_A / beta_B | −0.0015 / +0.0001 | +0.0083 / +0.0099 | below / below |

  Its own statement, "neither side, at E182's resolution", against E182-SPLIT's A+B. Over its 12 covered int8 kinds, rho +0.231 (n 12). T5
  and ten kinds are not covered. Its quartet swaps, (1, 85) − (85, 1) +0.0126 and (1, 127) − (127, 1) −0.0056 W, beside the measured D
  differences +0.076 and +0.007 W.

## The readings, labelled

- **Blind:** every registered rule above; every forecast (P, P + ACC, E) was frozen before T0 (E182.md, `58b88850`), and october-forecast-model's
  figures before T0 (`c958e33b`, 00:03:19 PST). T2 and T5 are blind for every forecast; T1, T4 and T6 for P only; T3 re-measures fitted kinds
  for all three (E182.md.dated-note-1.md section 2); E182-W-int8 against E is blind for 14 of its 20 int8 kinds.
- **Reported:** E182-Q, E182-K, the order term, the trains' reported readings, the seven arms, the kinds' levels against the forecasts, and
  october-forecast-model's arm.
- **Post hoc:** nothing here was fitted to these data.

## Registered before any data, and what the box ran

Every forecast, rule, threshold, statistic, power figure, kind, tile, plan, cap and stop is the registration's, [`E182.md`](../../../../tools/claims-v3/e182/E182.md)
(`58b88850`, Sat 7 Nov 2026 13:57:12 PST, committed alone), read with its dated notes
[1](../../../../tools/claims-v3/e182/E182.md.dated-note-1.md) (`6c158cd2`), [2](../../../../tools/claims-v3/e182/E182.md.dated-note-2.md)
(`e0d31903`) and [3](../../../../tools/claims-v3/e182/E182.md.dated-note-3.md) (`6b2d2ae6`), and october-forecast-model's dated note
[M1](../../../../tools/claims-v3/e182/E182.md.dated-note-M1.md) (`c958e33b`, Sun 8 Nov 2026 00:03:19 PST), all committed before this
session's T0. The kit is [`KIT.md`](../../../../tools/claims-v3/e182/KIT.md) (`41865c18`) with its dated notes 1-4 (`6c158cd2`, `22da6a7b`,
`e0d31903`, `6b2d2ae6`); the card day ran by note 4's section 5 and the card lane's brief
([`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e182/CARD-LANE-BRIEF.md) with its dated notes 1 and 2). The window: day 2026-11-08, last
start 05:30, last end 07:45 PST.

The runbook as it ran (the Intel's lab clone, one `RB_OUT` for E182 and the day's one `RB_LOCK`; every remote call after a 15 s hard-killed
probe and under its bound; **no login link appeared**):

| KIT.md box step | file | when (PST, Sun 8 Nov 2026) | exit |
|---|---|---|---|
| 1, the window | `rb/s02_window_e182.sh 2026-11-08 05:30 07:45` | 00:01:55 | 0 |
| 2, the desk check | `rb/s03_desk_e182_v5.sh` | 00:01:55-00:02:00 (at `45e514e3`: "note M1 absent"), and again at 00:13:32 (at `c958e33b`: "note M1 present (scored beside, by its reader)") | 0, 0 |
| 4, the look | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | 00:03:03, and again at 00:15:28, right before the session | FREE, FREE |
| 3, the post | the card lane's, after the look | 00:03:23 | |
| 5, the sync | `rb/s07_a3_sync_e182_v2.sh` | 00:13:40-00:13:42: 40 paths; 116 files' contents sent, none under `workloads/sparsity/` | 0 |
| 6, the train host's build and the box's checks | `rb/s08_a3_preflight_e182_v5.sh start`, then `wait` | 00:13:46-00:13:57 (below) | 0, 0 |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | 00:14:19-00:14:20: TDP 0 W, 65 °C, max_power, 600 MHz, 523 mV; et-who clean | 0 |
| 8, the dry pass | `rb/s10_a3_dry_e182_v2.sh start`, then `wait` | 00:14:24-00:14:51: 18220, 18215 and the smoke rc 0 under V3_DRY, the start gate 8 (want 8) | 0, 0 |
| 9, the session | `rb/s11_a3_session_e182_v2.sh FULL yes` | launched 00:15:41-00:15:46 (T0 00:15:41) | 0 |
| 10, the wait | `rb/s20_wait_e182.sh`, again while it said 17 | twelve bounded calls, 00:15:53-01:53:55 | 17 eleven times, then 0 |
| 11, the release, then the collection | the post's handover, then `rb/s22_collect_e182_v3.sh` | 01:54:29; 01:56:18-01:58:15 | 0 |

**Departures and their dates:**
- **Step 2 ran twice.** Its first run (00:01:55-00:02:00, at `45e514e3`) came before M1's commit (00:03:19) and printed "october-forecast-model
  note M1 absent (not scored: E182.md section 8)". M1 was committed before every E182 box step and before T0, so by section 8 it is scored
  beside. Step 2 v5 was run once more at 00:13:32, at `c958e33b`, before the sync: rc 0, the six lists at their pins (32, 79, 50, 49, 89,
  19), "note M1 present". That second line supersedes the first.
- **The look ran twice:** before the post (00:03:03) and again right before the session (00:15:28), both FREE.
- **None of the kit's registered departures fired:** one build and no re-run; the trains ran, so no fallback; nothing was retried.

## Step 6's outcome (the train host's first compile on the box)

From [`logs/e182-build-attempts.txt`](logs/e182-build-attempts.txt) and [`logs/e182-build-host-start1.txt`](logs/e182-build-host-start1.txt),
copied by step 11 v3: **one build on the day, TRAIN-HOST-BUILT.** The detached job `a3-build-e182` started at 00:13:48 PST and ended rc 0 at
00:13:51: BUILD INPUTS OK (the 9 inputs at their pins in the build's copy, and nothing else), BUILD OK after 3 s of its own 500 s bound, the
patched source's sha256 `37ca98ad…` the registered one, the binary's `94e38742…`. Then, each in its own 60 s read: NOTE1 FILES OK 10,
HARNESS OK 73, the preflight's `dmcmd_audit` GO (32 send sites, 0 disallowed), `e182_common.py --verify` rc 0. No re-run, no
TRAIN-HOST-INPUTS-DIFFER, no fallback: E182.md.dated-note-2.md's re-run rule never fired.

## Who checked it

The kit's own gates, run by step 11 v3 before it said done: the check of C over every listed session (FINISHED, 8,820 PASS), the desk-path
gate (`nopath_q142s.py`: 462 files, 0 hits) and the login scrub (`scrub_tree_e178.py --check`: 275 files in 35 directories, 0 left). No
verifier has read these data yet; an adversarial data verifier comes next.

## Device commands sent

As registered (E182.md section 7, "Device commands"): E178's harness and E78's card code unchanged, every telemetry call through E128's guard
(`ettelem config` with no argument, `ettelem sample --seconds --every-ms` and nothing else), and once before the session the runbook's
step-7 read (`ettelem config` through the same guard, under card 0's lock). The patched train host opens the card through the runtime only
(kernel load, copies, launches). Sent: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**, GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, **GET_MODULE_VOLTAGE**: **all
READs**, the two in bold PMIC voltage-register reads, which the owner's rule of 2 November 2026 allows. **Never sent:** the statistics reset
(`since_reset_ms` −1 in all 57,500 samples), any SET_*, the firmware-revisions query, any residency read, any governor, TDP, threshold or
clock set, any reset. The checker (`dmcmd_audit.py`, unchanged), run by the session on the box before any device opened: **GO**, 32 send
sites, 0 disallowed ([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt)); the same at step 6. No power cycle, and nothing near card 0's
75 W alarm (the board's highest live reading 54.17 W).

## Card and post

`et-who` at the looks (00:03:03 and 00:15:28 PST), at the step-7 read (00:14:19) and at the session's start (00:15:42) and end (01:53:47):
no process held a device node or card lock. At the looks and the step-7 read no other account ran a device process; 12 terminal logins
were counted, and an idle login does not block. No login is named in any file. This was the day's first session of ours on aifoundry3; the
day's next run there, E184's arm S, follows this run's step 11. Nothing of ours ran on aifoundry2; E184's arm B, a separate session of ours,
was launched on aifoundry1 card 1 at 00:15:24 PST, never on this card.

Sun 8 Nov's one `#community-lab` post is message `1568898719959744554`, created at 00:03:23 PST after the look, reading
`<ai> **Claude says:** using aifoundry3 for 2 h, until ~02:03 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`; it
was read back at 00:13:14 with that text. **At this run's end, 01:54:29 PST**, under the Discord lock and `EXPECT_TEXT`, dry-run, saved and
read back (from the edit box, and from a fresh plan at about 01:56: one post that day, its text equal to the intended one), the clause became
the next run's, every other word kept:
`<ai> **Claude says:** using aifoundry3 for 2.5 h, until ~04:24 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`.
No earlier day's post was touched.

## Privacy and the public-text scan (before the commit)

- **Logins.** Step 11 v3's last gate read every directory of the collection with `scrub_tree_e178.py --check` (0 left). Before this commit
  the final bytes were read again with files outside `tools/claims-v3/e182/`: E164's `scrub_etwho_e164.py --check` (unchanged; `--owner` the
  box login of this repository's owner) in every directory of this one and of a scratch copy of the text inside its 23 `.gz` files (75
  directories, every one rc 0), and a search of both for run_e78's "another user on this card" stop line and lib.sh's "others present" line
  (0 lines).
- **The public-text scan** (`tools/timeline/sanitize_extracts.py`'s fixed list, plus the private-network, Mac-home, scratch and e-mail
  patterns) over every text file and the text inside every `.gz` of this directory: 349 text files and 23 `.gz` files, 44,473 matches, 44,455
  of them the owner's own box home path and 18 the configs' tree key that names it, the reviewed class earlier card days' committed data
  carry; no other match. The runbook's desk-path gate (`nopath_q142s.py`) read the directory too: 462 files, 0 hits. This README, `SHA256SUMS`
  and the commit's message were scanned on their own afterwards. The lab's private name table is absent on the Intel, so names were checked
  against the fixed list only (a stated coverage limit).

## Files

All files of step 11 v3's collection and score are here as step 11 left them (equal to `build/e182-out/`, file for file), with
october-forecast-model's arm (three files) beside them, plus this README and [`SHA256SUMS`](SHA256SUMS), which pins every file but this
README and itself.

| file | what |
|---|---|
| `scored.json`, `results.md`, `score.log` | the registered scorer's output: every rule, every arm and every reported reading |
| `trains-e182.json`, `reduce-trains.log` | the trains' reduction (`e182_stats.py`'s statistic) |
| `e182.json`, `runs.csv`, `reduce.txt`, `reduce.log` | the registered primary reduction of the four kinds passes |
| `e182-session.json`, `e182-auto-nodips.json`, `e182-kfrozen-dips.json`, `e182-leak*.json`, `e182-gatesoff.json` (with their `runs-*.csv`, `reduce-*.txt`, `reduce-*.log`) | the seven arms |
| `arm_m1_read_e182.py`, `arm-m1-e182.json`, `arm-m1-e182.txt` | october-forecast-model's arm, read by M1-4 |
| `ccheck/` | the C logs (`c-log-p182*.jsonl.gz`) and `ccheck.py`'s output (`ccheck-all.json`, `ccheck.txt`) |
| `aifoundry3/e182/p18210`-`p18215` | the trains as the box wrote them (`telemetry.jsonl.gz`, `train.jsonl`, `run.log`, `marks.jsonl`, `block.json`, the config reads, the tiles' and code's hashes, `manifest.txt`, the anchors' `a0`/`a1`) |
| `aifoundry3/e182/p18220`-`p18223` | the kinds passes as the box wrote them |
| `aifoundry3/e182-smoke/p18201`, `aifoundry3/e182-stoptest/p18202` | the smoke and the stop-path test |
| `logs/` | the session's own logs (`session.log`, with step 8's dry start-gate line at its top, `queue.out`, `session.out`), the session config reads with their times, `dmcmd-preflight.txt`, `binaries.sha256`, the train host's record (`SHA256`), the day's step-6 record (`e182-build-attempts.txt`, `e182-build-host-start1.txt`, `e182-build-host.txt`) and `absent-on-box.txt` (none absent) |
| `code.sha256` | the sha256 of every registered file the collection read |

## What it does to predicting power

- **The flip model's account of a one-number int8 tile is incomplete.** It prices held operand bits only where a bus returns to zero, on
  B's side (TenB). The card charges A's held bits nearly as much (beta_A / beta_B = 0.84). The next model needs a per-held-bit term on A's
  side, on a path the open RTL does not reach; E182.md section 3 named the candidates (the full-custom register file and scratchpad, a read
  port, another return-to-zero bus).
- **M10's int8 total is about right, its split is wrong:** T3 reads near P (+0.127 against +0.110) while T2, the same bits moved across, reads
  a tenth of P. A forecast that moves bits between A and B under M10 will be wrong by up to about 0.1 W.
- **M10's per-flip int8 price stays too high** (3.8 fJ [1.4, 6.1] against 7.0; E178's measured 2.8 inside), as E178 found.
- **Float operand placement is a large, unmodelled term:** +0.236 W for 23 held bits moved from A to B at one product, where every model
  says 0.
- **Trains are the instrument for one-number pairs:** noise as forecast, about ±0.0026 W a pair in 30 card-minutes, against about ±0.03 W
  from E178's couples.
- **october-forecast-model (reported):** it lands inside T2 and T4 and below T1, T3, T6 and both betas; it reads neither side for the held bits
  where the card reads both.

SPDX-License-Identifier: Apache-2.0
