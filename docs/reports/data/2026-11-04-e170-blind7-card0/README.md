# E170: blind pool 7 on aifoundry1 card 0 under its own governor, in 6 s bursts at the 800 MHz cap - through a card term set blind, M9 predicts the burst board power of 39 tiles on a card no model had seen to 0.727 W rms (E170-W PASS, the primary), without bias (E170-B PASS, mean −0.090 W), and is resolved better than M6 (−0.158 W [−0.242, −0.094]) and M8 there; the switching scale reads 0.977 against κ0 0.9463 (X0 FAIL), and the die rose about 1.7 times faster per watt than the burst heat law (H1, H3 FAIL); every launch's C bit-exact (2,373 of 2,373); card 0 behaved (E170-S PASS, peak 59.38 W)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, "a power model across kinds". It answers the Q139 critic's **rank 1** (M9 against M6 on new kinds) on a third card, and the question
of **a card nobody has measured** (the Q139 critic's rank 4; M8's card-scale predictor from cheap reads, the Q138 critic's rank 5). The complaint
that kept card 0 out since 31 October is E84's PMIC over-power alarm
([`../2026-10-31-e84-speed-aifoundry1-card0/README.md`](../2026-10-31-e84-speed-aifoundry1-card0/README.md), "Post hoc, never a verdict: the PMIC's
over-power alarm"). Wed 4 Nov 2026 (week 45), the card half of Q141, on the owner's words of that day: about 13:55 PST, "go, feel free to use all
four cards because they're not being used right now", then about 13:56, "There was a problem with card 0, but that's been fixed". What the fix was
is not known. Parents: **E165** (the governed-burst form, [`../2026-11-04-e165-blind7-aifoundry2/`](../2026-11-04-e165-blind7-aifoundry2/README.md))
and **E164** (the stops), with card 0's own records E84, E114 and E118. The mandate: his words of 2 November 2026 ("settle any unanswered questions
regarding horace's power model"), with his goal "to be able to predict the power requirement and heat generation of various kinds of numeric
computations as accurately as possible".*

- **Card:** aifoundry1 card 0 (`V3_DEVICE=0` / `ET_DEVICES=0`, card 0's lock, the `~/nekko` tree), under its own governor at its static TDP:
  `ettelem config` at the state gate (16:19:41 PST) and at the end (16:48:53): TDP 65 W, threshold 65 °C, power state 3 (low_power), the
  clock at its 600 MHz idle, 519 mV, both times. **Nothing was set.** `since_reset_ms` −1 in every sample: no statistics reset. The residency
  query was refused by E170's guard (exit 97) in all 135 runs, before its reader started.
- **Card 0's state, read first on READ paths: GO** ([`aifoundry1-c0/state-gate.json`](aifoundry1-c0/state-gate.json)). Card 0's module uptime
  read 13,098 min against E84's 7,240 + 5,857.7 = 13,097.7 min (tolerance 2), so no service-processor reset since E84 identified the image
  (release 1.4.0, BL2 0.22.0); the host booted 2026-10-26 15:02:04, before E84's read. The owner's "that's been fixed" therefore involved no
  service-processor reset of card 0 and no host reboot.
- **Card session** 16:19:41-16:48:53 PST, **29.2 card-minutes** (the die stop-path test 0.0, the board stop-path test 0.1, the ramped smoke 0.8,
  the session 28.3), inside the cap of 40 and the 45-minute slot (to 17:04:41): **the full registered plan, 135 of 135 bursts**, every launch rc
  0, every run complete and counted (6 s bursts at 12.6 s each against E160's 11.94 s planned; the 55 °C cool gate reached before every
  burst, held at most 2.0 s; E105 admitted all 135: [`aifoundry1-c0/s1/run.log`](aifoundry1-c0/s1/run.log)).
- **Every launch's C is bit-exact:** 2,373 of 2,373 PASS in the session ([`ccheck-s1.json.gz`](ccheck-s1.json.gz); the smoke's and the board
  stop-path test's in [`ccheck-smoke.json`](ccheck-smoke.json), [`ccheck-stoptest-board.json`](ccheck-stoptest-board.json)). **E170-C PASS.**
- **No stop fired** outside the two stop-path tests, and **E170-S PASS**: no safety stop, no sampler line under 590 MHz, no run's highest board
  sample at or above 62 W. The highest sample was **59.38 W** (BURST-116, `fp32.b_onebit_b22_third`): 6.52 W under the 65.9 W one-sample stop,
  2.62 W under E105's 62 W lock line, which never acted. The shires' mean read at most 63 °C; the hottest-sensor field carried 69 °C from before
  the session in every sample (no statistics reset).
- **The SP trace ring**, dumped after every run and read at the desk as E170.md § The stops asks: **no PMIC over-power alarm line, no entry naming
  the PMIC and no POWER_SAFE record** in 1,704 new ring entries over 144 dumps; the clock points set were 600, 700 and 800 MHz only
  ([`posthoc/readings_e170.txt`](posthoc/readings_e170.txt) § 1, decoded with the lab's `tools/claims-v3/hpl/sptrace_full.py`).
- **Every device-management command sent was a read** (§ Device commands sent).
- E164 ran on card 1 of this host first and had ended (14:19:34-15:17:53 PST,
  [`../2026-11-04-e164-blind7-card1/`](../2026-11-04-e164-blind7-card1/README.md)): never two sessions of ours on aifoundry1 at once.

## Results

**In plain words.** On a card no model had seen, M9's frozen aifoundry2 relation, carried to card 0 by a term fixed before any card-0 burst (the
session's own zeros level in full, and a switching scale κ0 = 0.9463 read off two committed ladders), predicted the board power of 39 new kinds in
6 s bursts at the 800 MHz cap to 0.73 W rms with no resolved bias, inside the line set by M9's own end-to-end error on aifoundry2, and M9 beat
M6 and M8 on the same bursts. The switching scale itself reads higher than κ0 when each tile is measured against its pass's zeros anchor, but
lower when the zeros level is referred to each tile's own die start; the board, which carries that referral, holds. The die rose about 1.7 times
faster per board watt than on aifoundry2, so the burst heat law does not carry to this card. Nothing tripped: card 0 at these powers behaved.

**The registered verdicts** ([`results.md`](results.md), [`results.json`](results.json) › `score.rules`, `c_check`, `safety`; the scorer of record
`score_e170_a1.py`, amendment E170-A1, over `score_e170.py` as frozen in `574dc5b5`; [`score.txt`](score.txt)):

| rule | set | reading | line or reference | verdict |
|---|---|---|---|---|
| E170-C | every launch of every BURST run | 2,373 of 2,373 bit-exact | all PASS | PASS |
| **E170-W** (the primary) | board W in the burst, 39 tiles | **rms 0.727 W** | bootstrap of Q140(l)'s 42 end-to-end pinned errors: [0.599, 1.040] | **PASS** |
| E170-B | the same | mean −0.090 W, rms 0.727 W | \|mean\| ≤ 0.5 and rms ≤ 1.0 | PASS |
| **E170-M1** (rank 1's primary on card 0) | burst D, 34 priority-1 new kinds | M9 − M6 **−0.158 W [−0.242, −0.094]** (M9 0.791, M6 0.949 W rms) | resolved below zero | **BETTER** |
| E170-M2 | the same | M9 − M8 −0.246 W [−0.436, −0.090] (M8 1.037) | the same | BETTER |
| E170-X0 (the card term) | measured burst D / M9's burst D, 36 tiles | median **0.9766 [0.963, 0.987]**, +3.2% from κ0 | holds κ0 0.9463 | **FAIL** |
| E170-F | burst clock, 39 | rms 3.98 MHz, mean −1.13 MHz | bootstrap of the 42 pinned clock errors: [0.29, 4.10] | PASS |
| E170-W3 | board in the frozen band (±1.264 W) | 34 of 39 | at least 34 | PASS |
| E170-H1 | burst die rise, 39 | rms 2.457 °C, mean **+2.382 °C** | bootstrap of the 112 residuals: [0.531, 0.827] | **FAIL** |
| E170-H3 | die rise in ±1.406 °C | 1 of 39 | at least 34 | **FAIL** |
| E170-S | the day's behaviour | no safety stop; no line under 590 MHz; highest run 59.38 W | none; none; under 62 W | PASS |

**Against the registered forecast** (E170.md § Precision, "frozen so it can be wrong", widened as information by E170-A1 A1-3 and E170-A2 A2-2):
C, W, B, F and S PASS as forecast (W passed in 69% of the forecast's draws, B in 54%); **M1 and M2 read BETTER where NOT RESOLVED was forecast**;
**X0 read FAIL high**, where "PASS or FAIL low" was forecast and A1-3 / A2-2 had widened it to a possible high reading; H1 FAIL (forecast "PASS or
FAIL"). A1-3's risk, that the zeros level in full would read card 0's boards about 2.3 W low (B and W FAIL LOW), did not happen (mean −0.09 W):
card 0's zeros offset is shared by its loaded tiles in full. A2-2's risk, class S reading high, did happen (below), without failing W.

**Each model through the same card term** (`results.json` › `score.reported`, reported; board and burst D, W, 39 tiles; D over the 34 of M1):

| model | board rms | board mean | burst D rms | burst D mean |
|---|---|---|---|---|
| **M9** | **0.727** | −0.090 | **0.791** | +0.486 |
| M8 | 0.844 | +0.139 | 1.037 | +0.696 |
| M7 | 0.804 | +0.054 | 0.937 | +0.597 |
| M6 | 0.816 | +0.093 | 0.949 | +0.623 |

**By format, half and class** (M9's board error, W, rms (mean)): int8 26 tiles 0.549 (−0.395), fp32 11 0.917 (+0.394), fp16 2 1.333 (+1.214);
half A (29 tiles, card-0 estimate ≤ 52 W) 0.524 (−0.338), half B (10, 52-60 W) 1.126 (+0.632); class S (single high bits) 8 tiles 1.251
(+0.719), H 7 0.648 (−0.475), L 7 0.432 (−0.348), E 4 0.235 (+0.194), unaimed 11 0.291 (−0.204), pool 7's int8 random anchors 2 1.165 (−1.007).

**The arms** (reported, never a verdict): E165's form unchanged (β 0.648, κ 1) reads the boards **3.25 W rms, mean −3.19 W**; the level alone (κ 1)
1.10 W, −0.91 W; κ from E84's 800 MHz pairs 1.11 W, +0.77 W; a leave-one-tile-out session scale per family puts M9's burst D at 0.425 W rms and
keeps M1 and M2 BETTER (−0.146 W [−0.290, −0.000]; −0.300 W). The card's zeros anchors at the cap: fp32 29.26 W, fp16 28.83 W, int8 30.21 W (6
bursts each), 6.1-6.5 W under M9's part's aifoundry2 fallback (35.36 / 35.29 / 36.66 W).

**What carries the misses.**
- **X0: the switching scale's footing.** Measured as registered, a tile's burst D is its board less its pass's zeros anchor of the format, with no
  die-start referral. X0's 36 tiles started their runs **1.35 °C hotter** on average than their pass's zeros anchor, about +0.53 W of leakage at
  the card term's kT 0.3954 W/°C, and their median ratio to M9's burst D is 0.9766. Referred instead to the card's zeros level at each tile's own
  die starts, as the board prediction is, the same ratio reads **0.9312** ([`posthoc/readings_e170.txt`](posthoc/readings_e170.txt) § 5, post
  hoc). κ0 = 0.9463 lies between the two; the registered verdict stays FAIL.
- **Class S and half B read high, as A2-2 said.** All 13 runs whose highest sample exceeded the tile's card-0 admission estimate are class S of half
  B, by +0.59 to +2.24 W (`fp32.b_onebit_b20_pi` 58.19 W against 55.95, `fp32.b_onebit_b20_seventh` 57.85 against 55.73,
  `fp32.b_onebit_b22_third` 59.38 against 57.35; `posthoc/readings_e170.txt` § 4): the same sign as E165's class-S board errors on aifoundry2
  (+1.80 to +2.52 W) and as the single high bits' misses at 600 MHz on both other cards. A2-1's implied peaks (57.89-60.79 W) over-stated card 0.
- **int8 reads low, the floats high**, as on card 1 the same day (E164's B2 and B1): int8 −0.395 W over 26 tiles, fp32 +0.394 W over 11.
- **F: the governor's dips.** Four runs' burst clock read under 795 MHz (`fp16.anchor7_zeros` 754.2, `int8.anchor7_full_b` 756,
  `fp32.b_onebit_b20_full` 759.2, `fp32.b_onebit_b20_third_a1p5` 756 MHz; `posthoc/readings_e170.txt` § 3), the governor's fall inside a burst
  that A2-2 flagged; they count, as registered, and F still passes (3.98 MHz against the 4.10 line).
- **H1 and H3: card 0's die rises faster.** The 6 s burst rise per board W over the law's 21.5 W knee is **0.24 °C/W** on card 0 against the frozen
  law's 0.1400 °C/W from aifoundry2 (least squares 0.2415, median 0.2449; `posthoc/readings_e170.txt` § 2): the hottest admitted tiles rose 7.3-8.0
  °C where 4.4-4.8 °C was predicted. E170.md allowed "H1 PASS or FAIL" (card 0's die runs hotter per board W than aifoundry2's in sustained runs,
  E84 C1); the burst law needs a per-card coefficient.

## What it does to predicting power and heat

- **The term tested:** M9's frozen aifoundry2 relation (Q140(l), `m9_a2.json`) carried to a third card by a card term set before any card-0 burst:
  the session's own zeros level in full and κ0 = 0.9463 (the median of five committed card 0 / aifoundry2 ratios at 600 MHz, E118 against E72);
  M9's 600 MHz D (`1f244140`) inside it; the burst heat law (0.1400 °C/W over 21.5 W) on a third card.
- **Before:** card 0 had no blind power score at all; the 600 MHz blind record is 0.24-0.32 W rms per card; aifoundry2's governed bursts end to
  end read 0.80 W (E160) and 0.87 W (E143) on the pinned board, and E165 today 0.99 W pinned and 0.71 W governed (0.98 W on E170's own 39 tiles);
  M8's card-scale predictor from cheap reads missed the held-out cards by 1.5-8.5%.
- **After (blind, this session):** **0.727 W rms on the board, mean −0.090 W**, over 39 tiles on a card the models never saw, from the bytes, three
  zeros bursts per format and one constant; M9 better than M6 (−0.158 W) and M8 (−0.246 W) on the burst D, resolved. The card term's level in full
  is what carries it: E165's form unchanged reads 3.25 W rms. Heat does not carry: the burst rise reads 2.46 °C rms, the die rising about 0.24 °C
  per board W against aifoundry2's 0.14.
- **What it says to change:** the burst heat law needs a per-card coefficient (card 0's about 1.7 times aifoundry2's); κ0's footing should be
  stated with the die-start referral (0.931 referred, 0.977 as registered, κ0 between); the single high bits read high again at 800 MHz. **Nothing
  frozen changes here.**

## Registered before any data, and what the box ran

- **Frozen first:** blind pool 7 with every model's aifoundry2 predictions and the 82 W list, Q140(x) `75802201` and notes `3c9bb2ba`; M9
  `1f244140` / `8dfafae3`; M9's aifoundry2 part `5b98bd5c`, registered `245caffe`, corrected `5c98c0c5`; E165's references
  (`predictions-e165.json`, `3ef06839`). Nothing was fitted here.
- **Registered** (Q141(w)), every commit before any E170 data, claim or launch: [`E170.md`](../../../../tools/claims-v3/e170/E170.md),
  `b5ca3e78` (14:41:25 PST: the design, the card term set blind, the rules, the admission, the stops, the order); the scorer and its
  self-test on E160's committed session, `574dc5b5` (14:48:30); the run kit and amendment E170-A1 (the scorer of record,
  `score_e170_a1.py`), `57e1c6c4` (15:13:43); amendment E170-A2 after the desk verifier and E165's data (E165's live class-S peaks
  disclosed, run as registered; the forecast widened), `6147a9c7` (16:08:53); the kit's corrections (the 18:15 / 19:00 window, the
  run-queue refusal, the subset's 30-minute slot), `0e35ec58` (16:09:38). E165's data `4c6665f0` (15:49:29) preceded A2.
- **The box steps** (the kit's step driver `box/step_e170.sh` over Q141(k)'s bounded runner; the card lane's own log): the look at
  16:17:48 PST (the host booted 2026-10-26 15:02:04, before E84's read; et-who "No process holds an ET-SoC-1 device node or card lock.";
  E164's `session end` 15:17:53; the binaries `4f0956ce…` (the C-logging host), `990807f4…` (E78's kernel), `87c1c38c…` (E84's
  `ettelem`) equal to their pins; nothing of ours running); the sync 16:18:00-02 (one `rsync -a -c -R`); the check on the box
  16:18:14-34 (`check_e170.py` **HARNESS OK, 107 files and 3 binaries**; `preflight_e170.sh` **GO, 33 send sites, 0 disallowed**; 61
  tiles; κ0 0.9463; pool 7's SHA256SUMS **91 OK**; the box's dry pass: stoptest-die rc 4, the smoke rc 0, 135 BURST runs listed; et-who
  clean); the look again at 16:19:33-34; **the launch 16:19:40-46** (`step_e170.sh launch '2026-11-04 18:55 PST'`, after reading E170-A2
  § A2-1): the holders at launch all 0 on both cards, nothing of ours running ([`logs/holders-at-launch.txt`](logs/holders-at-launch.txt)),
  the slot 16:19:41-17:04:41 PST ([`logs/slot.txt`](logs/slot.txt)), the full plan, the cap 40.

## Registered against what happened

| | registered | happened |
|---|---|---|
| order | the registration (`b5ca3e78`), the scorer (`574dc5b5`), the kit and A1 (`57e1c6c4`), A2 (`6147a9c7`) and the kit's corrections (`0e35ec58`) before the claim and the first launch, each descending from the frozen commits | all before the launch at 16:19:40 PST; the lab's main was `efaaa726` (16:14:52) at the start; the day's post already named aifoundry1 (14:11:27) |
| window | start after E164's end and by 18:15 PST, end by 19:00; the slot `min(launch + 45 min, 18:55)` | started 16:19:41 (E164 ended 15:17:53), ended 16:48:53, 15.8 min before the slot's end |
| state gate | et-holders clean on card 0 and nothing of ours on either card; the host's boot before E84's read; module uptime ≥ E84's identity read plus the elapsed minutes, less 2; config 65 W / 65 °C at the 600 MHz idle | **GO** on every part (above) |
| stop-path tests | STOPTEST-DIE (`abs_stop_c` 30 °C) ends exit 4 for "die" before any launch; STOPTEST-BOARD (25 W on one sample) ends exit 4 for "board" while its `int8.anchor7_zeros` launch runs | **PASS both**: exit 4 "safety:die 69 C >= 30 C" on the carried hottest field, 35 ms after the first live line, no launch; exit 4 "safety:board 28.6 W > 25 W on 1 samples", 39 ms after the line, inside the launch, which ended 238 ms after the trip ([`aifoundry1-c0/queue.jsonl`](aifoundry1-c0/queue.jsonl)) |
| the ramped smoke | the idle card 30 s, `int8.anchor7_zeros` 2 s, `fp32.randn_a24k` 2 s, under the live stops; its gate | **GO**: exit 0; 458 sampler lines, the board at most 51.5 W, none under 590 MHz or over the stop; 12 C records for 12 SPARSITY lines, 2 host records, the DMA gap's median 3.0 ms, the projected hold 6.604 s against 7.2 s (`queue.jsonl` › `smoke_tel`, `smoke_check`) |
| the session | 135 bursts in the registered order, the zeros anchors first in each pass, half B's hottest last; the cap 40 | 135 of 135, all complete and counted; s1 exit 0 "done", 28.3 card-minutes; E105 admitted every run |
| stops | one die reading ≥ 72 °C or one board sample > 65.9 W ends the session; any line under 590 MHz ends it; E105's lock after a run reaching 62 W | none fired; the highest board sample 59.38 W, the shires' mean at most 63 °C, no line under 590 MHz |
| the C check | every launch bit-exact; a run is counted only if all its lines PASS | 2,373 of 2,373 PASS; 135 runs counted |
| departures | — | **None.** The registered collector `collect_e170.sh` ran unchanged over the card lane's digest-checked copy (`build/e170-raw/`, read 16:50:33 PST), with the C check's content-keyed cache placed in the gitignored `build/` (`CCHECK_CACHE`; the default is a cache directory in the home folder) and the box login as `--owner`. Of the collector's three C-check JSONs, each kept beside its gzip, this directory keeps E165's committed layout: `ccheck-s1.json.gz` alone (byte-checked against the JSON) and the two small JSONs uncompressed. |

## Device commands sent

As registered ([`E170.md`](../../../../tools/claims-v3/e170/E170.md) § Device commands sent): `ettelem sample` every 100 ms through E170's
guard (GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**, **GET_MODULE_VOLTAGE**),
`ettelem config` (GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES,
**GET_ASIC_VOLTAGE**) at the state read, after every run and at the end, `ettelem uptime` (GET_MODULE_UPTIME) at the state read, and
`ettelem sptrace` (the trace region's copy, no DM command) after every run: **all READs**, classified from et-platform `836a4ab` (BL2
0.22.0), carried by the module uptime's continuity; the three in bold are PMIC voltage-register reads, which the owner's rule of 2 November
2026 allows. **Refused by the guard before the reader started**: the residency query, in every one of the 135 runs (`residency_rc` 97).
**Never sent**: the statistics reset (`since_reset_ms` −1 in every sample), any SET_*, the firmware-revisions query, any governor, TDP,
threshold or clock set, any reset, any PMIC write, and `dev_mngt_service`. The checker (`dmcmd_audit.py`, unchanged) on the box before the
launch: **GO**, 33 send sites, 0 disallowed, with E165's one reviewed exception (`run_hpl.py:622`, the residency query the guard refuses)
([`logs/e170-preflight.txt`](logs/e170-preflight.txt)).

## Card and post

`et-who` at the look-first reads (16:17:48 and 16:19:33 PST), at the state gate (16:19:41) and after the session (16:49:40): no process held a
device node or card lock on card 0, and nothing of ours on card 1 (E164 had ended at 15:17:53); one other account's two logins, idle for over 24
h, were present and do not block (the owner's ruling of 1 November 2026; E111's record, counts only, in
[`aifoundry1-c0/idle_logins.jsonl`](aifoundry1-c0/idle_logins.jsonl)). The collector's scrub (`scrub_etwho_e164.py` over this whole directory
with the owner's login: 0 files rewritten) and its `--check`, run again on `logs/` and on the whole directory, leave no other account's login in
any file (0 left; [`logs/scrub.txt`](logs/scrub.txt)). Nothing ran on card 1 during E170.

Wed 4 Nov's one `#community-lab` post is message `1567662592850399304` (created 14:11:27 PST). aifoundry1's clause, `using aifoundry1 for 3 h,
until ~17:11 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, covered card 1's E164 and card 0's E170; E170's slot
ended at 17:04:41, inside ~17:11, so no rewrite was due at the claim. **The release, 16:50:09-15 PST**, by E170's card lane under the Discord
lock and `EXPECT_TEXT` (dry run, saved, read back at 16:50:15: one post that day, its text equal to the intended one): aifoundry1's clause
dropped, aifoundry2's kept word for word as the last one held, so no " — released" yet:
`<ai> **Claude says:** using aifoundry2 for 4.25 h, until ~18:26 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`.

## How to reproduce

```bash
# from the lab clone, over the pulled copy build/e170-raw (aifoundry1:nekko/build/e170/ and nekko/build/e170-preflight.txt;
# this directory's aifoundry1-c0/ and logs/ hold the same files, gzipped where the collector gzips them)
E170_DATE=2026-11-04 nice -n 10 bash tools/claims-v3/e170/collect_e170.sh build/e170-raw    # refuses if aifoundry1-c0/ exists here
# the registered score alone, over this directory (gunzip each session's c-log.jsonl.gz, launches.jsonl.gz and tel/*.jsonl.gz first):
python3 -B tools/claims-v3/e170/score_e170_a1.py docs/reports/data/2026-11-04-e170-blind7-card0/aifoundry1-c0/s1 \
  --ccheck <ccheck-s1.json> --out results.json --md results.md
python3 -B docs/reports/data/2026-11-04-e170-blind7-card0/posthoc/readings_e170.py      # the post hoc readings
```

Collected and scored on the Intel at `nice -n 10`, 17:18:17-17:21:42 PST, the C check at 2 jobs and the scorer single-threaded.

## Files

| file | what |
|---|---|
| `results.json`, `results.md`, `score.txt` | the scorer of record's output (`score_e170_a1.py`, A1): every rule, the reported arms, per format, half and class, the zeros levels, the peaks against the estimates, every tile's cell and every run's row |
| `ccheck-s1.json.gz`, `ccheck-smoke.json`, `ccheck-stoptest-board.json` | `ccheck.py`'s verdicts on every launch of the session, the smoke and the board stop-path test |
| `aifoundry1-c0/` | the box's `build/e170/runs/` as written: `queue.jsonl`, `status.json`, `state-gate.json`, `admission.json`, the config reads, snapshots and sensors at both ends, `history-before.jsonl`, `idle_logins.jsonl` (counts only), the two stop-path tests, the smoke and `s1/` (`runs.jsonl`, `launches.jsonl.gz`, `c-log.jsonl.gz`, `tel/*.jsonl.gz`, `sp/*.bin` the SP trace dumps, `queries.jsonl`, `run.log`, `end.json`, `e170.json`, …) |
| `logs/` | `queue.out`, `slot.txt`, `holders-at-launch.txt` (counts only), `e170-preflight.txt` (the device-command audit on the box), `scrub.txt` |
| `et-who-summary.txt` | the scrub's count of et-who readings in this directory, by card and without names (none are logged here: the queue records counts) |
| `posthoc/readings_e170.py` → `posthoc/readings_e170.txt` | post hoc, never a verdict: the SP ring's decode, the burst rise per board W, the runs under 795 MHz, the peaks against the estimates, X0's ratio on the die-start-referred footing |

SPDX-License-Identifier: Apache-2.0
