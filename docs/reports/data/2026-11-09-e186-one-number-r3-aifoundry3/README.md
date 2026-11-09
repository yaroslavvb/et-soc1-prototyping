# E186: M12's frozen forecasts tested blind against M10 in ten A B B A trains on aifoundry3 card 0 - fp16 prices a held bit as fp32 does (E186-H16 F16-SAME: +0.2031 W [+0.1978, +0.2084] against M12's +0.2051); fp32's held-bit prices land inside M12's bands on both sides (E186-GB +0.0139, E186-GA +0.0042 W a held bit, SIZE PASS, M10 FAIL LOW); E186-SPLIT3 and E186-SPLIT63 A+B; but E186-M reads NEITHER (M12 Q 32.5 against 16.9 over nine trains, M10 Q 10,230): four trains miss M12's narrow bands and E186-S23R DIFFERS LOW; every launch's C bit-exact; the train method reads as forecast

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**item 6**, "a power model across kinds". It answers, a third time, the owner's ask of Thu 5 Nov 2026, about 19:30 PST ("here's a matrix
filled with one number, and here's a matrix filled with another number, and they require different number of transistor flips, therefore
they will use different power, and I have a model which actually tracks it down"), as registered in
[`tools/claims-v3/e186/E186.md`](../../../../tools/claims-v3/e186/E186.md) with its dated amendments A1 and A2 and october-forecast-model's
dated notes M1 and M2, and kitted by [`KIT.md`](../../../../tools/claims-v3/e186/KIT.md) with its dated notes 1-4. Mon 9 Nov 2026 (week 46),
aifoundry3 card 0 at 600 MHz pinned. **E186 ran before day 2 (E185, then E183), on the owner's go of Mon 9 Nov 2026 about 11:52 PST**, as
E186.md's dated amendment [A2](../../../../tools/claims-v3/e186/E186.md.dated-amendment-A2.md) records (committed `1456f6d8`, 12:26:15 PST,
before any box step of the day): only the order changed. **Blind:** every forecast and rule below was committed before the session's opening
config read on the card (12:40:53 PST); M12's and M10's forecasts were frozen on Sun 8 Nov (`8b85b498`, `80d53792`), before any E186 datum.*

- **Card:** aifoundry3 card 0, **600 MHz in all 57,589 samples**; `ettelem config` through E128's guard at the session's start (12:40:53
  PST) and end (14:19:07): TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV both times. **Nothing was set.** `since_reset_ms` −1 in
  every sample: no statistics reset.
- **Card session** 12:40:53-14:19:08 PST, **98.2 card-minutes** (the queue done at T0 + 5,894 s), inside FULL's cap of 100: the stop-path
  test 18602, the smoke 18601 and both of its gates (passed at 12:42:06), then **FULL as registered**: the ten trains in the registered
  order, 18610 (H16), 18611 (S23), 18612 (Q63-sign), 18613 (Q63-swap), 18614 (B15-B7), 18615 (B23-B15), 18616 (Q3-sign), 18617 (Q3-swap),
  18618 (A15-A7) and **18619 (A23-A15)**, the tenth admitted by the budget rule (it ended at T0 + 5,884 s against the budget's T0 + 5,940
  s). **Every train ran whole** (64 int8 processes, 32 units; 76 float processes, 38 units; 14 launch records a process); block times 644,
  624, 478, 484, 634, 633, 478, 479, 642 and 625 s. No kinds pass (FULL runs none).
- **Every launch's C is bit-exact:** 10,462 of 10,462 PASS against the RTL's arithmetic (Q139(k)'s `ccheck.py`; fp32 5,544, fp16 1,150,
  int8 3,768; no ROUNDING, UNMODELLED or FAIL). The eleven sessions that must carry a C log each carried one, checked to its end
  (`ccsessions_e186.py`: FINISHED); the stop-path test carried none. **E186-C PASS.**
- **Every train launch paired** with the registered schedule, its type, its tile and a C record of that tile's bytes: 9,968 launch records in
  the ten train blocks, 0 not paired. **E186-PAIR PASS** (A1-2).
- **The session's float scale was read:** s = **1.00873** from the float trains' own anchors (fp32.randn 1.01208, fp16.randn 1.00539; E78's
  reduction on E182's footing, `e186-anchors.json`). So A1-1's branch for an unread s did **not** apply: the four ladder trains carry their
  SIZE words, E186-GB and E186-GA are scored, and E186-M reads over all nine trains other than H16.
- **No stop fired:** the highest live readings were **54.31 W board** (14:07:52, train A15-A7) and **65 °C `minshire[0]`** (in B23-B15 and
  A15-A7), against the stops 65 W / 70 °C. The stop-path test fired its die, board and watch stops on live samples with no launch.
- **Every device-management command sent was a read** (§ Device commands sent).

## The answer (the registered rules, blind)

The scorer's words govern: **FAIL HIGH = the forecast is above the measured interval's band: the model prices more than the card reads; FAIL
LOW = below.** A train's interval is t(0.975, n − 1) over its units (two processes each). SIZE against M12 is the band (estimate − M12's line)
± sqrt(hw² + (1.96 se_M12)²) holding 0; against M10, se 0. Each line is the registered one at the session's s and each train's measured rate
(`scored-e186.json` > `rules`; `forecast_e186.lines_at`).

| rule | train (first − second) | measured, W (95%) | M12 (se) | M10 | verdict |
|---|---|---|---:|---:|---|
| **E186-H16** | fp16 (1.0, 0x3fff) − (0x3fff, 1.0) | **+0.2031 [+0.1978, +0.2084]** | +0.2051 (0.0026); scaled arm +0.1019 (0.0176) | 0 | SIGN POSITIVE; SIZE M12 **PASS**, SCALED FAIL LOW, M10 FAIL LOW; **H16: F16-SAME** |
| **E186-S23** | fp32 (1.0, 0x3f80ffff) − (0x3f80ffff, 1.0) | **+0.1545 [+0.1491, +0.1599]** | +0.1640 (0.0021) | 0 | POSITIVE; M12 FAIL HIGH, M10 FAIL LOW; **NEITHER** |
| **E186-Q63SIGN** | int8 (−1, −63) − (1, 63) | **+0.0364 [+0.0308, +0.0421]** | +0.0292 (0.0017) | −0.0471 | POSITIVE; M12 FAIL LOW, M10 FAIL LOW; **NEITHER** |
| **E186-Q63SWAP** | int8 (1, 63) − (63, 1) | **+0.0107 [+0.0054, +0.0160]** | +0.0073 (0.0016) | +0.0785 | POSITIVE; M12 PASS, M10 FAIL HIGH; **M12** |
| **E186-B15B7** | fp32 (1.0, 0x3f8000ff) − (1.0, 1.0) | **+0.1398 [+0.1355, +0.1441]** | +0.1264 (0.0069) | +0.0201 | POSITIVE; M12 PASS, M10 FAIL LOW; **M12** |
| **E186-B23B15** | fp32 (1.0, 0x3f80ffff) − (1.0, 0x3f8000ff) | **+0.1368 [+0.1316, +0.1421]** | +0.1408 (0.0069) | +0.0346 | POSITIVE; M12 PASS, M10 FAIL LOW; **M12** |
| **E186-Q3SIGN** | int8 (−1, −3) − (1, 3) | **+0.1083 [+0.1027, +0.1140]** | +0.1080 (0.0021) | +0.0785 | POSITIVE; M12 PASS, M10 FAIL LOW; **M12** |
| **E186-Q3SWAP** | int8 (1, 3) − (3, 1) | **+0.0086 [+0.0035, +0.0138]** | +0.0015 (0.0003) | +0.0157 | POSITIVE; M12 FAIL LOW, M10 FAIL HIGH; **NEITHER** |
| **E186-A15A7** | fp32 (0x3f8000ff, 1.0) − (1.0, 1.0) | **+0.0630 [+0.0577, +0.0683]** | +0.0443 (0.0069) | +0.0201 | POSITIVE; M12 FAIL LOW, M10 FAIL LOW; **NEITHER** |
| **E186-A23A15** | fp32 (0x3f80ffff, 1.0) − (0x3f8000ff, 1.0) | **+0.0591 [+0.0534, +0.0648]** | +0.0588 (0.0069) | +0.0346 | POSITIVE; M12 PASS, M10 FAIL LOW; **M12** |

| rule | what | measured (95%) | M12 / M10 | verdict |
|---|---|---|---|---|
| **E186-SPLIT3** | product 3: beta_A, beta_B from Q3-swap and Q3-sign, W a held 1-bit a byte | beta_A **+0.00544 [+0.00325, +0.00763]**; beta_B **+0.01406 [+0.01102, +0.01709]** | +0.00839 / +0.00986 (se 0.00023); M10 0 / +0.01570 | **A+B** (both POSITIVE); beta_A SIZE M12 FAIL HIGH, beta_B FAIL LOW |
| **E186-SPLIT63** | product 63: from Q63-swap and Q63-sign | beta_A **+0.01071 [+0.00912, +0.01230]**; beta_B **+0.01285 [+0.01057, +0.01513]** | the same | **A+B**; both SIZE M12 FAIL LOW |
| **E186-GB** | fp32's held mantissa bit on B's side: the B ladder less its P10 offsets, over 16 bits | **+0.01387 [+0.01345, +0.01429]** W a held bit | +0.01328 (0.00086) / 0 | **POSITIVE**; SIZE M12 **PASS**, M10 FAIL LOW |
| **E186-GA** | the same on A's side | **+0.00421 [+0.00373, +0.00469]** | +0.00303 (0.00086) / 0 | **POSITIVE**; SIZE M12 **PASS**, M10 FAIL LOW |
| **E186-S23R** | S23 × 23/16, a repeat of E182's T5 at 16 of its 23 bits | +0.2221 [+0.2144, +0.2298] | E182-F's T5 [+0.2299, +0.2419] | **DIFFERS LOW** |
| **E186-M** | Q = Σ z² over the nine session trains other than H16 (s read: none left out) | M12 Q **32.48**, M10 Q **10,229.8** | χ²(9) 95% point 16.92 | **NEITHER** (both INCONSISTENT) |
| **E186-TR-N** | the pooled quad residual sd over its forecast σ_q | int8 0.03561 against 0.03485 (1.022); float 0.03938 against 0.03804 (1.035) | at most 1.25 | **AS FORECAST** |
| **E186-C** | every launch of every E186 kind, trains included, C-checked against its own tiles | 10,462 of 10,462 PASS | all | **PASS** |
| **E186-PAIR** | every train block's launch records on the registered schedule, type, tile and C record (A1-2) | 9,968 of 9,968 paired, 10 blocks | all | **PASS** |
| **E186-LV** | the fallback's levels | no kinds pass in FULL | | **NOT SCORED** (FULL reads no level, E186.md section 5.5) |

**What the card says, in plain words.**
- **fp16 holds a bit as fp32 does.** Moving 20 held 1-bits a 32-bit word from A to B in fp16 costs +0.203 W, M12's F16-SAME extrapolation
  to within 0.002 W; the fp16-scaled arm (+0.102) and M10 (0) are far below. E186-H16 reads F16-SAME, and only F16-SAME.
- **In fp32, a held B-side mantissa bit costs about three times an A-side one,** +0.0139 against +0.0042 W a bit (ratio 3.3; M12 said
  4.4), and both lie inside M12's bands; M10, with no placement term, fails low on every fp32 train. Three of the four ladder trains read
  M12; A's first eight bits (A15-A7) cost more than M12 says (+0.063 against +0.044 W).
- **Held int8 bits cost on both sides again** (A+B at products 3 and 63, as E182 read at its products), but **the price per bit moves with
  the word:** beta_A +0.0054 at product 3 and +0.0107 at 63, beta_B +0.0141 and +0.0129, where M12 has one pair (+0.0084, +0.0099) and M10
  puts it all on B. So Q3-sign and Q63-swap read M12 while Q63-sign and Q3-swap miss its narrow bands.
- **Moving 16 bits costs less than 16/23 of moving 23** (S23R DIFFERS LOW): S23 reads +0.155 W, M12 said +0.164, and scaled by 23/16 it
  falls below E182's T5 interval.
- **Jointly, neither model holds** (E186-M NEITHER): M12's Q is 32.5 against 16.9; M10's is 10,230. M12's lines miss the ten trains by 0.0087
  W rms, M10's by 0.102 W (post hoc arithmetic from `scored-e186.json`, below), so M12 is about twelve times closer, and the trains'
  ±0.005 W half-widths resolve what it still misses.
- **The method works.** The trains' noise is as forecast (ratios 1.022 int8 and 1.035 float), and every launch's C is exact and paired.

## Reported beside, never a verdict

- **The joint word over all ten trains** (H16 included): NEITHER; M12 Q 32.78 against χ²(10) 18.31, M10 Q 16,268. **By family:** float
  (six trains) M12 Q 18.63 against 12.59, int8 (four) M12 Q 14.15 against 9.49; M10 14,543 and 1,725. All INCONSISTENT.
- **gamma_B / gamma_A** = 3.29 (M12's ratio 4.4).
- **Each line less the measured estimate** (post hoc arithmetic on the scorer's lines; no rule reads it): M12 +0.0020 (H16), +0.0096 (S23),
  −0.0073 (Q63-sign), −0.0034 (Q63-swap), −0.0135 (B15-B7), +0.0040 (B23-B15), −0.0003 (Q3-sign), −0.0071 (Q3-swap), −0.0187 (A15-A7),
  −0.0003 W (A23-A15); rms 0.0087 W over the ten, 0.0091 over E186-M's nine. M10's rms 0.1024 and 0.0841 W.
- **In each train** (`scored-e186.json` > `reported` > `trains`): the two orientations' means (H16 0.2011 FSSF, 0.2050 SFFS; S23 0.1516,
  0.1574; B23-B15 0.1321, 0.1415; Q63-sign 0.0334, 0.0395), the halves, the carry-over reading L2 − L3 (at most 0.014 W in magnitude; four of
  the twenty exclude 0, all negative: S23's, Q63-sign's and Q63-swap's SFFS, A23-A15's FSSF), the anchors' raw levels, the quads by
  orientation and their residual sd, the median process period and wall time.
- **Each train's lines at s = 1 and the candidates' rates** (`reported` > `lines_at_s1_and_candidate_rates`) beside the scored ones; the
  measured rates are 1.0016-1.0017 of the candidates' for the float trains (1.11896e9-1.11906e9 TensorFMA ops a second) and 1.0004 for the
  int8 trains (1.92117e9-1.92125e9).
- **october-forecast-model's arms** (reported, never a rule; read after the score by the kit's step 11 v4 through each note's gate):
  - **Note M1, v4** ([`arm-m1-e186.txt`](arm-m1-e186.txt)): v4 covers none of the ten session trains and FULL reads no kind, so it reads
    nothing: every train "not covered" (14) or "not run" (8), every kind "not covered" (18) or "not run" (21), as M1-4 said it would.
  - **Note M2** ([`arm-m2-e186.txt`](arm-m2-e186.txt), its reader v2; M2-READ): the four arms carry the same int8 and fp32 figures and
    differ only on H16. Each arm's centre lies **inside** the measured interval on S23, Q3-sign, Q3-swap and Q63-swap, and **below** it on
    B15-B7, B23-B15, A15-A7, A23-A15 and Q63-sign (by 0.011-0.050 W), always with the estimate's sign.

    | arm | trains read | centre inside | H16: model, W | mean error, W | rms error, W |
    |---|---:|---:|---|---:|---:|
    | v4 on M12's set | 9 (H16 not covered) | 4 | not covered | −0.0228 | 0.0316 |
    | v5 | 10 | 4 | +0.1295, below (error −0.0736) | −0.0279 | 0.0379 |
    | v6 | 10 | 4 | +0.1482, below (−0.0549) | −0.0260 | 0.0346 |
    | v7 | 10 | 4 | +0.1488, below (−0.0543) | −0.0260 | 0.0345 |

    (error = the arm's figure less the measured one; the reader's words and every figure are in `arm-m2-e186.txt` and `.json`.)

## The readings, labelled

- **Blind:** every registered rule above. M12's and M10's lines were frozen on Sun 8 Nov 2026 (`8b85b498`, `80d53792`, 06:56:00 PST) and
  registered (`a41408d9`) before any E186 datum; M12 is a post hoc model for E182 and blind here. october-forecast-model's figures were
  committed before T0 (note M1 `3adb8bfe`, note M2 `8c808677`, its dated note 1 `565523d3`). The order departure (A2) came before any box step
  of the day.
- **Reported:** the joint words over ten and by family, gamma_B / gamma_A, each line's error, the trains' reported readings, and
  october-forecast-model's arms.
- **Post hoc:** only the plain-words arithmetic of each line's error and its rms; nothing here was fitted to these data.

## Registered before any data, and what the box ran

Every forecast, rule, threshold, statistic, power figure, kind, tile, plan, cap and stop is the registration's,
[`E186.md`](../../../../tools/claims-v3/e186/E186.md) (`a41408d9`, Sun 8 Nov 2026 07:15:08 PST, committed alone), read with its dated
amendments [A1](../../../../tools/claims-v3/e186/E186.md.dated-amendment-A1.md) (`17cf100f`, 10:18:16) and
[A2](../../../../tools/claims-v3/e186/E186.md.dated-amendment-A2.md) (`1456f6d8`, Mon 9 Nov 2026 12:26:15 PST), and
october-forecast-model's dated notes [M1](../../../../tools/claims-v3/e186/E186.md.dated-note-M1.md) (`3adb8bfe`, Sun 07:18:53) and
[M2](../../../../tools/claims-v3/e186/E186.md.dated-note-M2.md) (`8c808677`, 13:03:15) with
[M2's dated note 1](../../../../tools/claims-v3/e186/E186.md.dated-note-M2.md.dated-note-1.md) (`565523d3`, 14:36:50), all committed before
this session's T0. The kit is [`KIT.md`](../../../../tools/claims-v3/e186/KIT.md) (`523002be`, 08:57:34) with its dated notes 1-4
(`88750359`, `e8e9f4e1`, `8c808677`, `565523d3`); the card day ran by the kit's dated note 4, section 4, and the card lane's brief
([`KIT-BRIEF.md`](../../../../tools/claims-v3/e186/KIT-BRIEF.md) with its dated notes 1-4).

**The day, before day 2, on the owner's go (A2).** E186.md registered the session for after day 2 (E185, then E183). On Mon 9 Nov 2026, about
11:52 PST, the owner chose to run E186 that afternoon, before day 2, with the window below; A2 quotes his go and records that only the order
changes. It was committed at 12:26:15 PST, before any box step of the day and before any datum, and the brief's dated note 4 carried it to the
card lane. Nothing else changed: no rule, forecast, threshold, statistic, power figure, plan, cap or stop. None of E183's or E185's rules
reads E186's data, and E186's rules read only this session (A2-3). The window: day 2026-11-09, last start 16:00, last end 18:00 PST.

The runbook as it ran (the Intel's lab clone at `1456f6d8`, one `RB_OUT` for E186 and the round's one `RB_LOCK`; every remote call after a 15 s
hard-killed probe and under its bound; **no login link appeared**):

| KIT.md box step | file | when (PST, Mon 9 Nov 2026) | exit |
|---|---|---|---|
| 1, the window | `rb/s02_window_e186.sh 2026-11-09 16:00 18:00` | 12:27:22 | 0 |
| 2, the desk check | `rb/s03_desk_e186_v2.sh` (step 2 v1 inside it, first; the pull under the lab-git lock) | 12:27:26-12:27:39, at `1456f6d8`: HISTORY OK v1 (55 named files) and v2 (501), HARNESS OK 71, NOTE1 FILES OK 10, the eleven lists and the scale route's six at their pins, note M1's list 5 of 5 and note M2's lists 8 and 9 OK (reported), no E186 data in any ref | 0 |
| 4, the look | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | 12:28:41-12:28:42 | FREE |
| 3, the post | the card lane's, after the look | 12:30:43 | |
| 5, the sync | `rb/s07_a3_sync_e186_v2.sh` | 12:39:13-12:39:15: NOT-BESIDE-OURS, then step 5 v1: 55 paths, 120 files' contents sent, none under `workloads/sparsity/` | 0 |
| 6, the train host's build and the box's checks | `rb/s08_a3_build_e186.sh start`, then `wait` | 12:39:23-12:39:34 (below) | 0, 0 |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | 12:39:43-12:39:44: TDP 0 W, 65 °C, max_power, 600 MHz, 523 mV; et-who clean (HOLDER-RULE FREE) | 0 |
| 8, the dry pass | `rb/s10_a3_dry_e186.sh start`, then `wait` | 12:39:49-12:40:37: 18610, 18611, 18612, 18620 and the smoke 18601 rc 0 under V3_DRY, the start gate 8 (want 8) | 0, 0 |
| 9, the session | `rb/s11_a3_session_e186.sh FULL yes` | launched 12:40:52-12:40:58 (T0 12:40:53) | 0 |
| 10, the wait | `rb/s20_wait_e186.sh`, again while it said 17 | eleven bounded calls logged, 12:46:05-14:19:19 (and a first, below) | 17 ten times, then 0 (RUN-ENDED, MANIFEST-WRITTEN 351 files) |
| 11, the release, then the collection | the post's release, then `rb/s22_collect_e186_v4.sh` | 14:19:26-14:19:43; 14:20:00-14:23:43 | 0 |

Step 11 v4 ran step 11 v2 first and unchanged: the copies by name, **COPY-BACK EXACT** (351 files, every manifest line read back and nothing
else), **the history check v2 HISTORY OK** (5 directories and 501 named files; 118 files added since `a41408d9`, none a shadowing module, no
change but an addition, nothing uncommitted), the collector v2 (the check of C, the trains' reduction, the float trains' anchors, the scorer v2
with the pairing check), the C-session gate (11 of 11 FINISHED), the desk-path gate (370 files, 0 hits), the login scrub (285 files in 48
directories, 0 left) and note M1's reader through its gate (M1-READ); then note M2's gate v2 and its reader v2 (M2-READ).

**Departures and their dates:**
- **The day's order (A2):** the session ran on Mon 9 Nov 2026, before day 2, on the owner's go, recorded in A2 and the brief's dated note 4
  before any box step of the day (above). It is the one registered departure; no rule, forecast or cap moved.
- **The first wait call was stopped at the desk.** Step 10's first call (12:41:17) was stopped on the Intel at about 12:45:50, when this lane
  moved its waits from a background loop to one call at a time. It was a read (pgrep and the session log on the box), its remote loop ended
  with its connection, and it has no line in the runbook's log; the next call began at 12:46:05. Nothing on the card was touched.
- **None of the kit's registered departures fired:** one build and no re-run; both smoke gates passed, so no fallback; nothing was retried.

## Step 6's outcome (the train host's first compile on the box)

From [`logs/step6/`](logs/step6/) (the box's count file and the day's build log, copied by step 11): **one build on the day,
TRAIN-HOST-BUILT.** The detached job `a3-build-e186` began at 12:39:25 PST and ended rc 0 at 12:39:28: BUILD INPUTS OK (the 9 inputs at
their pins in the build's copy, and nothing else), `build_host_e186` rc 0 after 3 s of its own 500 s bound, the patched source's sha256
`37ca98ad…` (E182's registered one), the binary's `f1a30615…`. Then, each in its own 60 s read: NOTE1 FILES OK 10, HARNESS OK 78, the
preflight's `dmcmd_audit` GO (32 send sites, 0 disallowed), `e186_common.py --verify` 0 problems. No re-run, no TRAIN-HOST-INPUTS-DIFFER,
no fallback. The fp16 train's first launches on the card were the smoke's two H16 processes: 28 launch records, median 546.001 cycles an op,
median gap 3 ms, every launch with its C record (SMOKE-GATE (train) PASS).

## Who checked it

The kit's own gates, run by step 11 before it said done: COPY-BACK EXACT, the history check v2, the check of C over every listed session
(FINISHED, 10,462 PASS), the pairing check (9,968 paired), the desk-path gate (`nopath_q142s.py`) and the login scrub
(`scrub_tree_e178.py --check`). No verifier has read these data yet; an adversarial data verifier comes next.

## Device commands sent

As registered (E186.md section 7, "Device commands"): E182's harness and E78's card code unchanged, every telemetry call through E128's
guard (`ettelem config` with no argument, `ettelem sample --seconds --every-ms` and nothing else), and once before the session the runbook's
step-7 read (`ettelem config` through the same guard, under card 0's lock). The patched train host opens the card through the runtime only
(kernel load, copies, launches). Sent: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**, GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, **GET_MODULE_VOLTAGE**: **all
READs**, the two in bold PMIC voltage-register reads, which the owner's rule of 2 November 2026 allows. **Never sent:** the statistics reset
(`since_reset_ms` −1 in all 57,589 samples), any SET_*, the firmware-revisions query, any residency read, any governor, TDP, threshold or
clock set, any reset. The checker (`dmcmd_audit.py`, unchanged), run by the session on the box before any device opened: **GO**, 32 send
sites, 0 disallowed ([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt)); the same at step 6. No power cycle, and nothing near card 0's
75 W alarm (the board's highest live reading 54.31 W).

## Card and post

`et-who` at the look (12:28:42 PST), at the step-7 read (12:39:44), at the session's start (12:40:53) and end (14:19:07), and at a look after
the collection (14:24:23): no process held a device node or card lock. At both looks no other account ran a device process; idle terminal
logins were counted, and an idle login does not block (the owner's ruling of 1 November 2026). No login is named in any file. This was the day's only
session of ours on aifoundry3; nothing of ours ran on aifoundry1 or aifoundry2, and nothing of ours was left running on the box (the look
after the collection: our device processes 0; the build and dry-pass jobs had ended rc 0).

Mon 9 Nov's one `#community-lab` post is message `1569449181905682575`, created at 12:30:43 PST after the look, reading
`<ai> **Claude says:** using aifoundry3 for 2 h, until ~14:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`;
it was read back with that text at 12:30:46 and again at 12:37:58, before the sync. The session ended at 14:19:08, inside the post's
estimate, so the clause was never re-estimated. **At its end, 14:19:26-14:19:43 PST**, under the Discord lock and `EXPECT_TEXT`, dry-run,
saved and read back (from a fresh plan: one post that day, its text equal to the intended one, released), the post became, every word kept:
`<ai> **Claude says:** using aifoundry3 for 2 h, until ~14:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>) — released`.
No earlier day's post was touched.

## Privacy and the public-text scan (before the commit)

- **Logins.** Step 11's last gate read every directory of the collection with `scrub_tree_e178.py --check` (0 left). Before this commit the
  final bytes were read again with files outside `tools/claims-v3/e186/`: E164's `scrub_etwho_e164.py --check` (unchanged; `--owner` the box
  login of this repository's owner) in every directory of this one and of a scratch copy of the text inside its 23 `.gz` files (92
  directories, every one rc 0), and a search of both for run_e78's "another user on this card" stop line and lib.sh's "others present" line
  (0 lines).
- **The public-text scan** (`tools/timeline/sanitize_extracts.py`'s fixed list, plus the private-network, Mac-home, scratch and e-mail
  patterns) over every text file and the text inside every `.gz` of this directory: 310 text files and 23 `.gz` files, 56,429 matches,
  56,407 of them the owner's own box home path and 22 the configs' tree key that names it, the reviewed class earlier card days' committed
  data carry; no other match. The runbook's desk-path gate (`nopath_q142s.py`) read the directory too: 376 files, 0 hits. This README,
  `SHA256SUMS` and the commit's message were scanned on their own afterwards. The lab's private name table is absent on the Intel, so names
  were checked against the fixed list only (a stated coverage limit).

## Files

All files of step 11 v4's collection and score are here as step 11 left them (equal to `build/e186-out/`, file for file: 376 files, 23 MB),
plus this README and [`SHA256SUMS`](SHA256SUMS), which pins every file but this README and itself.

| file | what |
|---|---|
| `scored-e186.json`, `results-e186.md`, `score.log` | the registered scorer's output (`score_e186_v2.py`, which runs `score_e186.py` unchanged): every rule, the pairing check and every reported reading |
| `trains-e186.json`, `reduce-trains.log` | the trains' reduction (E182's `reduce_train`, `e186_stats.py`'s statistic) |
| `e186-anchors.json`, `runs-anchors.csv`, `reduce-anchors.txt`, `reduce-anchors.log` | the float trains' anchors, reduced by E78's reduction on E182's footing: the session's s |
| `pairing-e186.status.txt` | the pairing check's reading (E186-PAIR) |
| `arm-m1-e186.json`, `.txt`, `.status.txt` | october-forecast-model's note M1 arm (v4), read through its gate |
| `arm-m2-e186.json`, `.txt`, `.status.txt` | note M2's four arms (v4 on M12's set, v5, v6, v7), read by its reader v2 through the gate v2 |
| `ccheck/` | the C logs (`c-log-p186*.jsonl.gz`) and `ccheck.py`'s output (`ccheck-all.json`, `ccheck.txt`) |
| `aifoundry3/e186/p18610`-`p18619` | the ten trains as the box wrote them (`telemetry.jsonl.gz`, `train.jsonl`, `run.log`, `marks.jsonl`, `block.json`, the config reads, the tiles' and code's hashes, `manifest.txt`, the anchors' `a0`/`a1`) |
| `aifoundry3/e186-smoke/p18601`, `aifoundry3/e186-stoptest/p18602` | the smoke and the stop-path test |
| `logs/` | the session's own files (`session.log`, `queue.out`, `blocks.txt`, `MANIFEST.sha256`, the session config reads with their times, `dmcmd-preflight.txt`, `binaries.sha256`), the day's step-6 record (`step6/`: the count file, the build's log, the build record `SHA256`) and `absent-on-box.txt` (none absent) |
| `code.sha256` | the sha256 of every registered file the collection read |

## What it does to predicting power

- **Held-bit placement is real, and it prices like M12, not M10.** In fp32 a held mantissa bit on B's side costs +0.0139 W and on A's side
  +0.0042 W, both inside M12's bands, blind; M10, which prices no held bit, is low on every float train. In fp16 the same placement costs what
  M12's F16-SAME said (+0.203 W against +0.205). A model of a one-number matmul's power needs a per-held-bit term by operand side, in all
  three formats.
- **M12's structure carries, its single prices do not.** M12 is about twelve times closer than M10 (0.0087 against 0.102 W rms over the ten
  trains), but jointly it is still refused: the int8 price per held bit moves with the word (beta_A 0.0054 at product 3, 0.0107 at 63), A's
  first eight mantissa bits cost more than its gamma_A says, and moving 16 bits costs less than 16/23 of moving 23. The next model needs a
  held-bit price that depends on where the bits sit and on the other operand, not one price per side.
- **october-forecast-model (reported):** its v4-v7 figures lie inside the measured interval on four of ten trains, all small-swap or sign
  trains, and below on the fp32 ladders and H16 by 0.04-0.07 W (rms 0.035 W for v6 and v7), so on these trains it prices held bits lower
  than the card reads.
- **E186 is the first blind test of M12 and of october-forecast-model v4-v7;** day 2 (E185, then E183) follows on its own go.

SPDX-License-Identifier: Apache-2.0
