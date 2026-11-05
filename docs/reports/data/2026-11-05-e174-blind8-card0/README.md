# E174: blind pool 8 on aifoundry1 card 0 under its own governor, in 6 s bursts at the 800 MHz cap - M10 carried predicts 21 new kinds' burst board power to 0.689 W rms (C0-W PASS) without bias (C0-B PASS, mean +0.102 W), not resolved against M9 carried (−0.099 W [−0.222, +0.057]); term c2 holds on a second session (C0-H1 PASS, 0.334 °C; C0-HK BETTER, −2.109 °C [−2.269, −1.953]); the burst clock misses its line by 0.003 MHz (C0-F FAIL, 4.543 MHz, two tiles' governor dips); every launch's C bit-exact (2,206 of 2,206); card 0 behaved (E174-S PASS, peak 57.86 W)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, "a power model across kinds", with items 8 and 9 (heat) through card 0's burst rise. It answers the Q142(r)/(p)/(d) critic's `next`
rank 2 for card 0 (E170's form, its admission and the 66 W / 72 °C stops) and that critic's `pool8` card-day plan (C0-W, C0-B, C0-M1, C0-F, C0-H1,
C0-HK), as registered in [`E174.md`](../../../../tools/claims-v3/e174/E174.md). Thu 5 Nov 2026 (week 45), the pool-8 card day, on the owner's go of
that day (about 11:15 PST: "feel free to use all 4 cards for experiments, no need to wait"). Parent: **E170**
([`../2026-11-04-e170-blind7-card0/`](../2026-11-04-e170-blind7-card0/README.md)), whose form, card term, admission and stops E174 keeps. The
mandate: his words of 2 November 2026 ("settle any unanswered questions regarding horace's power model"), with his goal "to be able to predict the
power requirement and heat generation of various kinds of numeric computations as accurately as possible".*

- **Card:** aifoundry1 card 0 (`V3_DEVICE=0` / `ET_DEVICES=0`, card 0's lock, the `~/nekko` tree), under its own governor at its static TDP:
  `ettelem config` at the state gate (12:44:43 PST), after every run and at the end (13:11:49): TDP 65 W, threshold 65 °C, power state 3
  (low_power), the clock at its 600 MHz idle, 519 mV. **Nothing was set.** `since_reset_ms` −1 in all 15,832 samples: no statistics reset. The
  residency query was refused by E170's guard (rc 97) in all 126 runs, before its reader started.
- **Card 0's state, read first on READ paths: GO** ([`aifoundry1-c0/state-gate.json`](aifoundry1-c0/state-gate.json)). Card 0's module uptime
  read **14,323 min** against E84's 7,240 + 7,082.7 = 14,322.7 min (tolerance 2): no service-processor reset since E84 identified the image
  (release 1.4.0, BL2 0.22.0), and none since E170's gate on 4 Nov (13,098 min then); the host booted 2026-10-26 15:02:04, before E84's read.
  Neither of the kit's NO-GO conditions arose.
- **Card session** 12:44:43-13:11:49 PST, **27.1 card-minutes** (the die stop-path test 0.0, the board stop-path test 0.1, the ramped smoke 0.8,
  the session s1 26.2), inside the cap of 40 and the 45-minute slot (to 13:29:43; the queue ended 1,073.8 s before it): **the full registered
  plan, 126 of 126 bursts** in the registered order (half A passes 1-3, then half B passes 4-6, each opening with the three zeros anchors, the
  hottest last), every run complete and counted; E105 admitted every run; the 55 °C cool gate reached before every burst.
- **Every launch's C is bit-exact:** 2,206 of 2,206 PASS in s1 ([`ccheck-s1.json.gz`](ccheck-s1.json.gz)), with the smoke's 12
  ([`ccheck-smoke.json`](ccheck-smoke.json)) and the board stop-path test's 5 ([`ccheck-stoptest-board.json`](ccheck-stoptest-board.json)); no
  ROUNDING, UNMODELLED or FAIL. **E174-C PASS.** The C-log list (v3's, [`logs/cclist.txt`](logs/cclist.txt)): stoptest-board, smoke and s1
  required, none missing.
- **No stop fired** outside the two stop-path tests, and **E174-S PASS**: no safety stop, no sampler line under 590 MHz in any BURST run, no
  run's highest board sample at or above 62 W. The highest sample was **57.86 W** (`fp32.s8_onebit_b19_c11b3dd2`, BURST-119): 8.04 W under
  the 65.9 W one-sample stop, 4.14 W under E105's 62 W lock line, about 17 W under the 75 W alarm. The shires' mean read at most 62 °C; the
  hottest-sensor field carried 69 °C from before the session in every sample (no statistics reset).
- **Every device-management command sent was a read** (§ Device commands sent).
- **One departure, D1, dated before any E174 data** ([`E174.md.dated-note-3.md`](../../../../tools/claims-v3/e174/E174.md.dated-note-3.md),
  lab `0a14c7bb`, 12:42:29 PST): the box check's tiles line first read BAD because 18 desk-only frozen inputs were not in the box's tree; one
  bounded copy of exactly those committed files, then the same check read clean (§ Registered against what happened).
- E172 ran on card 1 of this host first and had ended (11:40:14-12:33:55 PST,
  [`../2026-11-05-e172-blind8-card1/`](../2026-11-05-e172-blind8-card1/README.md)): never two sessions of ours on aifoundry1 at once.

## Results

**In plain words.** On card 0, a card no model's power fit has seen, M10's frozen power model carried by E170's card term (the session's own
zeros level in full and the switching scale κ0 = 0.9463) predicted the burst board power of 21 new kinds of numbers at the 800 MHz cap to 0.69 W
rms, with no resolved bias: inside the line set by M10's end-to-end error on aifoundry2, and a little better than E170's 0.73 W for M9 on pool 7.
On the burst switching power itself, M10 and M9 were not told apart at this n. The heat law M10 fitted to card 0 on one session (0.2415 °C of
burst rise per board watt over 21.5 W) held on a second session: 0.33 °C rms, inside its reference spread, where M9's aifoundry2 law misses by
2.4 °C. The governor held the cap on 19 of 21 tiles; two tiles' bursts dipped to a mean of 785-786 MHz, enough to push the clock's rms 0.003 MHz
over its line. Nothing came near the alarm.

**The registered verdicts** ([`results.json`](results.json) › `score.rules`, `c_check`, `safety_E174_S`; the scorer of record
[`score_e174.py`](../../../../tools/claims-v3/e174/score_e174.py), `99e5777e`; [`score.txt`](score.txt)):

| rule | set | reading | line or reference | verdict |
|---|---|---|---|---|
| E174-C | every launch of every BURST run, and every listed session | 2,206 of 2,206 bit-exact (smoke 12, board stop test 5) | all PASS | PASS |
| **P8-C0-W** | board W, M10 carried through the card term, 21 tiles | **rms 0.689 W** (mean +0.102 W) | bootstrap of Q140(l)'s 42 end-to-end pinned errors (0.8214 W): [0.521, 1.118] | **PASS** |
| P8-C0-B | the same errors | mean +0.102 W, rms 0.689 W | \|mean\| ≤ 0.5 W and rms ≤ 1.0 W | PASS |
| **P8-C0-M1** | burst D, M10 carried against M9 carried, 21 | **−0.099 W [−0.222, +0.057]** (M10 1.041, M9 1.140 W rms) | paired (seed 80,467) | **NOT RESOLVED** |
| **P8-C0-F** | burst clock, 21 | **rms 4.543 MHz**, mean −1.605 MHz | the 42 pinned clock errors (2.334 MHz): [0.172, 4.540] | **FAIL** |
| **P8-C0-H1** | die rise, M10's 0.2415 °C/W on the predicted board, 21 | **rms 0.334 °C**, mean +0.101 °C | term c2's 39 residuals on E170 (0.3385 °C): [0.216, 0.472] | **PASS** |
| **P8-C0-HK** | die rise at the measured board: M10's k 0.2415 against M9's 0.1400 | **−2.109 °C [−2.269, −1.953]** (M10 0.308, M9 2.417 °C rms) | paired (seed 80,488) | **BETTER** |
| P8-HM | heat over minutes | — | — | NOT SCORED (no hold runs in E174) |
| E174-S | the day's behaviour | no safety stop; no line under 590 MHz; highest run 57.86 W | none; none; under 62 W | PASS |

**Against the registered forecast** (E174.md § Precision, "frozen so it can be wrong"): C, S, W, B, M1, H1 and HK read as forecast. W read "PASS
with measured above predicted" (+0.102 W); B passed (forecast in 88.5% of draws); M1 NOT RESOLVED, as forecast; **H1 PASS and HK BETTER: c2 is
the card's**, not E170's session (the forecast's first branch). **F read FAIL where PASS was forecast**, by 0.003 MHz over the line (below).

**Each model through the same card term** (`results.json` › `score.reported`, reported, never a verdict; 21 tiles): M10 carried, board **0.689 W
rms** (mean +0.102), burst D 1.041 W rms; M9 carried, board 0.774 W rms (mean +0.130), burst D 1.140 W rms; the clock is the relation's for both
(4.543 MHz rms). Heat: M10's c2 on the predicted board 0.334 °C rms; M9's burst law 2.448 °C rms (mean +2.403 °C), as on E170. The rise per
board W over 21.5 W, least squares: **0.2434 °C/W** this session, against c2's 0.2415 from E170.

**By format, tier and class** (M10's board error, W, rms (mean)): int8 12 tiles 0.486 (−0.271), fp32 4 0.639 (+0.555), fp16 5 1.050 (+0.636);
tier A (16, card-0 estimate ≤ 52 W) 0.510 (−0.112), tier B (5, 52-60 W) 1.078 (+0.785); class S (single high bits) 8 tiles 0.939 (+0.713), L 4
0.683 (−0.427), R 4 0.297 (−0.222), U 4 0.416 (−0.216), H 1 0.100 (−0.100). The card's zeros anchors at the cap: fp32 28.54 W, fp16 28.87 W,
int8 30.10 W (6 bursts each). The switching scale against M10's burst D, reported as E170-X0's ratio: median 0.9766 [0.960, 1.010] over 21
tiles (E170: 0.9766 [0.963, 0.987] against κ0 0.9463).

**What carries the misses.**
- **F: two tiles' governor dips.** `int8.l8_flip_d2p2c16_231d` read a mean burst clock of 785.0 MHz and `fp16.s8_onebit_b4_c2e2c2e2` 786.0
  MHz over their passes (errors −15.0 and −14.0 MHz); every other tile held the 800 MHz cap within 3.4 MHz (`results.json` ›
  `score.reported.tiles`). These are the governor's falls inside a burst that E170 showed (four runs under 795 MHz there) and that E174.md calls
  a session term; they count, as registered. Two zeros-anchor bursts dipped the same way (754 and 788 MHz, `score.anchors`).
- **Class S and tier B read high, as on E170.** The single high bits read +0.71 W over M10 carried (E170: +0.72 W over M9), and the runs that
  passed their card-0 admission estimate are the single high bits of tier B: `fp32.s8_onebit_b19_c11b3dd2` 57.86 W against 55.38 W,
  `fp16.b_onebit_b8_pi` 57.61 against 55.76, `fp16.s8_onebit_b7_b945b945` 57.42 against 55.52 (`score.reported.peaks_vs_estimates`), as
  E170-A2's caution said; all under E105's 62 W line.
- **int8 reads low, the floats high**, as on card 0 and card 1 before (E170, E164): int8 −0.271 W over 12 tiles, fp32 +0.555 W over 4, fp16
  +0.636 W over 5.

## What it does to predicting power and heat

- **The terms tested:** M10's power model (Q142(m), frozen `6829c9ba`; its D for pool 8 frozen `4576fb90`) carried to card 0 by rule E through
  E170's card term (κ0 0.9463 and the session's zeros level), in governed bursts at the 800 MHz cap; M10's term c2, card 0's burst rise per board
  W, on its second session; the governor's cap on this card.
- **Before:** card 0's only blind power score was E170 (pool 7, M9 carried): board 0.727 W rms, mean −0.090 W over 39 tiles; c2 = 0.2415 °C/W was
  fitted in sample on that one session (leave one tile out 0.3385 °C), and M9's burst law missed there by 2.457 °C rms.
- **After (blind, this session):** M10 carried **0.689 W rms** on 21 new kinds (M9 carried 0.774 W on the same bursts, not resolved apart on D);
  **c2 holds blind: 0.334 °C rms** on a second session, least squares 0.2434 °C/W against 0.2415; the clock 4.54 MHz rms with two dipping tiles.
- **What it says:** card 0's burst heat per watt is a card constant the next model can carry (C0-H1 PASS, C0-HK BETTER), not E170's session; the
  card term carries M10's D to card 0 as well as aifoundry2's end-to-end error says (C0-W PASS); the governor's dips inside a burst stay a session
  term no model predicts. **Nothing frozen changes here.**

## Registered before any data, and what the box ran

- **Frozen first:** blind pool 8 with M10 carried's and M9 carried's card-0 predictions
  ([`predictions-pool8-aifoundry1c0.json`](../../../../tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry1c0.json), `4576fb90`, 02:30:56
  PST; the freeze's note `dfe226f1` changes no number); the card term, the admission formula, the stops and the identity rule are E170's
  ([`e170_common.py`](../../../../tools/claims-v3/e170/e170_common.py), `b5ca3e78`); term c2 is M10's (`6829c9ba`); pool 8's registration
  `3e97f583` with A1 `8a8fa34c` and A2 `68a7c322`; the predictor `9d81d254` and `97765c0a`. Nothing was fitted here.
- **Registered** (Q142(kg)), every commit before any E174 data, claim or launch: [`E174.md`](../../../../tools/claims-v3/e174/E174.md) with
  `predictions-e174.json` and `frozen-sha256-e174.json`, `c8064454` (03:45:13 PST); the scorer and its self-test `99e5777e` (03:54:39); the kit
  `5a2a9ba0` (04:35:57); [dated note 1](../../../../tools/claims-v3/e174/E174.md.dated-note-1.md) `5db9df6b` (05:45:17) and the v2 step drivers
  `34436d68` (05:49:03); [dated note 2](../../../../tools/claims-v3/e174/E174.md.dated-note-2.md) `c9a3e40a` (08:23:02: "E174 runs after E172 has
  ended, or if E172 never starts, and never beside it"), the v3 code `e2b48f5a` (08:27:12) and `6f4b48e4` (08:31:18);
  [dated note 3](../../../../tools/claims-v3/e174/E174.md.dated-note-3.md), D1, `0a14c7bb` (12:42:29). The lab's main at the launch was `0a14c7bb`.
- **The box steps** (the q142kg runbook through `box/step_e174_v3.sh`, every call after a 15 s probe and under its bound), after E172's end was
  read (12:34:16 PST): the look 12:38:03-04 (the host booted before E84's identity read; et-who "No process holds an ET-SoC-1 device node or card
  lock."; E172's `session end` recorded; the binaries `4f0956ce…`, `990807f4…`, `87c1c38c…` at their pins); the sync 12:38:32-34; the box check
  12:38:41-12:39:11, unclean on its tiles line only (D1); the D1 copy 12:43:00-02; the box check again 12:43:09-12:44:22, **clean**
  (`HARNESS OK 110 + 3 binaries`; the preflight `dmcmd_audit: GO (33 send site(s), 0 disallowed)`; `64 tiles; frozen inputs, Q139(k)'s files
  and tiles: OK`; pool 8's 89; the dry stop-path test rc 4; the dry smoke rc 0; 126 BURST runs listed); the look again 12:44:35; **the launch
  12:44:42-48** (`launch`, the full plan: the deadline 15:55 PST, the window's last start 15:00 and last end 16:00; the holders at launch all 0
  on both cards, [`logs/holders-at-launch.txt`](logs/holders-at-launch.txt)); four bounded waits 12:44:57-13:11:58; the pull 13:13:01-07; the
  collection 13:13:25-13:18:58 (`collect`, v3's C-log list, as the readiness critic's go items say, whatever the pull's printed hint named).

## Registered against what happened

| | registered | happened |
|---|---|---|
| order | the registration, the scorer, the kit, notes 1 and 2 and the v3 drivers before the claim and the first launch | all ancestors of the lab's main at the launch (`0a14c7bb`); the claim 11:29:08 PST; E174 after E172's end (12:33:55, read 12:34:16), never beside it |
| state gate | et-holders free; host booted before E84's read; module uptime ≥ E84's + minutes since − 2; config 65 W / 65 °C | **GO** at 12:44:43: 14,323 min against 14,322.7; booted 2026-10-26 15:02:04; 65 / 65 at 600 MHz |
| stop-path tests | STOPTEST-DIE exit 4 before any launch; STOPTEST-BOARD exit 4 inside its launch | **PASS**: die 69 °C ≥ 30 °C, 39 ms after the first line; board 28.7 W > 25 W on one sample, 44 ms after its line, the launch ended 366 ms after the trip |
| smoke | ramped: idle, `int8.anchor7_zeros`, `fp32.b_onebit_b20_one`; checked as E170's | **PASS**: 456 lines, board max 51.69 W, none under 590 MHz or over the stop; 12 C records for 12 launches; DMA gap median 3 ms |
| design | 126 bursts, half A then half B, the hottest last; the subset only if chosen before the launch | the full plan, 126 of 126 counted; the subset was not used (the 45-min slot fitted) |
| card time | about 28 card-minutes, the cap 40, the slot 45; no start after 15:00, every run ends by 16:00 | **27.1 card-minutes**, 12:44:43-13:11:49 PST |
| stops | one die reading ≥ 72 °C or one board sample > 65.9 W; any line under 590 MHz; E105's 62 W lock | none fired; highest 57.86 W |
| the C check | every launch, bit-exact; every listed session's log checked | 2,223 of 2,223 PASS over the three sessions; v3's list 3 of 3 |
| departures | — | **D1, the box check's tiles line** (dated before any E174 data in [`E174.md.dated-note-3.md`](../../../../tools/claims-v3/e174/E174.md.dated-note-3.md), lab `0a14c7bb`, 12:42:29 PST): the first box check (12:38:41-12:39:11) read every line clean but `64 tiles; frozen inputs, Q139(k)'s files and tiles: BAD`; a read-only run of `e174_common.py` on the box (12:40:13) found 18 of `frozen-sha256-e174.json`'s 32 files absent from the box's tree, every one desk-only (the session reads only `run_e174.py`'s 8 `BOX_FROZEN` files there), none differing; one bounded `rsync -a -c -R` of exactly those 18 committed files, each first checked on the Intel at its frozen sha256 (12:43:00-02, after the runbook's probe and a quiet read); then the same v3 check, unchanged, read clean. Nothing the session ran changed. No other departure. |

## Device commands sent

As registered ([`E174.md`](../../../../tools/claims-v3/e174/E174.md) § Device commands sent, E170.md's unchanged): `ettelem sample` every 100 ms
through E170's guard (GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**,
**GET_MODULE_VOLTAGE**), `ettelem config` (GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**) at the state read, after every run and at the end, `ettelem uptime` (GET_MODULE_UPTIME) at the
state read, and `ettelem sptrace` (the trace region's copy, no DM command) after every run: **all READs**, classified from et-platform `836a4ab`
(BL2 0.22.0), carried by the module uptime's continuity; the three in bold are PMIC voltage-register reads, which the owner's rule of 2 November
2026 allows. **Refused by the guard before the reader started**: the residency query, in every one of the 126 runs (`residency_rc` 97).
**Never sent**: the statistics reset (`since_reset_ms` −1 in every sample), any SET_*, the firmware-revisions query, any governor, TDP,
threshold or clock set, any reset, any PMIC write, and `dev_mngt_service`. The checker (`dmcmd_audit.py`, unchanged) on the box before the
launch: **GO**, 33 send sites, 0 disallowed ([`logs/e174-preflight.txt`](logs/e174-preflight.txt)).

## Card and post

`et-who` at the look-first reads (12:38:04 and 12:44:35 PST), at the state gate (12:44:43) and after the session: no process held a device node
or card lock on card 0, and nothing of ours on card 1 (E172 had ended at 12:33:55). Another account's two terminals, idle since 26 October, were
present, its logind session closing, its processes at 0.4% CPU with none a device or CI process; an idle login does not block (the owner's ruling
of 1 November 2026). Nothing of ours was busy on the host before the launch. The collector's scrub (`scrub_etwho_e164.py` over this whole directory
with the owner's login: 0 files rewritten) and its `--check` leave no other account's login in any file (0 left; [`logs/scrub.txt`](logs/scrub.txt)).

Thu 5 Nov's one `#community-lab` post is message `1567984130841641044`, created at 11:29:08 PST by the card day's claim. Its aifoundry1 clause,
`using aifoundry1 for 3 h, until ~14:29 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, covered card 1's E172 and then
card 0's E174. **At E172's end** (12:34:44-50 PST), under the post's shared lock with `EXPECT_TEXT`, dry run then saved, it became card 0's:
`using aifoundry1 card 0 for 1 h, until ~13:34 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, the aifoundry3 clause kept
word for word. The read-back plan's source text lagged that save (the client's message props; its rendered text was current), so the read-back
was taken from the post's own edit box at 12:36:24, nothing saved: the source read card 0's clause as written, after the aifoundry3 lane's
release at 12:36 had dropped its own clause. **At E174's end** (13:12:22-28 PST), card 0's clause was the last one held, so ` — released` was
appended, every word kept, and read back from the edit box (13:12:31) and a fresh plan, both equal:
`<ai> **Claude says:** using aifoundry1 card 0 for 1 h, until ~13:34 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>) — released`.

## How to reproduce

```bash
# from the lab clone, over the pulled copy build/e174-raw (aifoundry1:nekko/build/e174/ and nekko/build/e174-preflight.txt;
# this directory's aifoundry1-c0/ and logs/ hold the same files, gzipped where the collector gzips them)
E174_DATE=2026-11-05 nice -n 10 bash tools/claims-v3/e174/collect_e174.sh build/e174-raw    # refuses if aifoundry1-c0/ exists here
# the registered score alone, over this directory (gunzip each session's c-log.jsonl.gz, launches.jsonl.gz and tel/*.jsonl.gz first):
python3 -B tools/claims-v3/e174/score_e174.py docs/reports/data/2026-11-05-e174-blind8-card0/aifoundry1-c0/s1 \
  --ccheck <ccheck-s1.json> <ccheck-smoke.json> <ccheck-stoptest-board.json> --out results.json
```

Through the runbook this is `tools/claims-v3/e174/box/step_e174_v3.sh collect` (v3's C-log list, then the desk-path gate). Collected and scored on
the Intel at `nice -n 10`, 13:13:25-13:18:58 PST, the C check at 2 jobs and the scorer single-threaded.

## Files

| file | what |
|---|---|
| `results.json`, `score.txt` | the registered scorer's output: the rules, the C check, E174-S, every reported reading, each tile's measured and predicted values |
| `ccheck-s1.json.gz`, `ccheck-smoke.json`, `ccheck-stoptest-board.json` | `ccheck.py`'s check of C over each session's log |
| `et-who-summary.txt` | the scrub's count of et-who readings, by card, without names |
| `aifoundry1-c0/` | the queue as the box wrote it: `queue.jsonl`, `state-gate.json`, `admission.json`, the snapshots, the config reads, `idle_logins.jsonl` (counts only), and the sessions `stoptest-die`, `stoptest-board`, `smoke`, `s1` (each with `runs.jsonl`, `run.log`, `tel/`, `sp/`, `c-log.jsonl.gz`, `launches.jsonl.gz`, `session.json`, `e174.json`) |
| `logs/` | the box's `queue.out`, `slot.txt`, `holders-at-launch.txt`, the device-command preflight, the C-log list and the scrub's record |

SPDX-License-Identifier: Apache-2.0
