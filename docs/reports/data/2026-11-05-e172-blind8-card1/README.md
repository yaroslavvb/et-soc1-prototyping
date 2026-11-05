# E172: blind pool 8 on aifoundry1 card 1 at 600 MHz - M10 predicts 31 new kinds to 0.185 W rms (M9 0.266 W) and is resolved better than M9 (−0.080 W [−0.134, −0.034]), better on the floats (M1f) and through the session's own scale (A1); every format inside its line (P1-P3 PASS) and every 4.5 s heat rule PASS (H1-H4), but the floats read +0.105 W above M10 (B1 FAIL LOW), so P8-G FAILS; the re-runs' level or gain NOT SEPARATED; every launch's C bit-exact (3,470 of 3,470); P8-KA PASS, and pooled with E171 PASS (4 check anchors)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, "a power model across kinds", with items 8 and 9 (heat). It answers the Q142(r)/(p)/(d) critic's `next` rank 2 (pool 8's card kits and
P8 scorers) for the second 600 MHz card, as registered in [`E172.md`](../../../../tools/claims-v3/e172/E172.md) with its dated notes
[1](../../../../tools/claims-v3/e172/E172.md.dated-note-1.md) and [2](../../../../tools/claims-v3/e172/E172.md.dated-note-2.md): M10's held-out
figures made blind on this card. E171 is aifoundry3's half ([`../2026-11-05-e171-blind8-aifoundry3/`](../2026-11-05-e171-blind8-aifoundry3/README.md)).
Thu 5 Nov 2026 (week 45), the pool-8 card day, on the owner's go of that day (about 11:15 PST: "feel free to use all 4 cards for experiments, no
need to wait"). Parent: **E164** ([`../2026-11-04-e164-blind7-card1/`](../2026-11-04-e164-blind7-card1/README.md)), whose protocol E172 keeps. The
mandate: his words of 2 November 2026 ("settle any unanswered questions regarding horace's power model"), with his goal "to be able to predict the
power requirement and heat generation of various kinds of numeric computations as accurately as possible".*

- **Card:** aifoundry1 card 1 (`V3_DEVICE=1` / `ET_DEVICES=1`, its own lock, the `~/nekko` tree), **600 MHz in all 31,614 samples**;
  `ettelem config` through E128's guard at the session's start (11:40:15 PST) and end (12:33:55): TDP 65 W, threshold 65 °C, 600 MHz, 499 mV both
  times (power state low_power at the start, managed_power at the end). **Nothing was set.** `since_reset_ms` −1 in every sample: no statistics
  reset.
- **Card session** 11:40:14-12:33:55 PST, **53.7 card-minutes** (T0+3,221 s), inside the cap of 65 (forecast 51-53; dated note 1's N4: four
  passes, or five if each took about 748 s or less): the stop-path test 17202, the smoke 17201 and its gate (PASS at 11:41:12), then passes
  17210 (756 s), 17211 (778 s), 17212 (788 s) and 17213 (801 s); the budget rule stopped before 17214 (it would have ended at T0+4,022 s against
  T0+3,840 s), as registered.
- **The registered reduction kept three of the four passes.** E78's pass gate, unchanged, set 17213 aside ("fp32.zeros departs −0.260 W from its
  straight line", against the gate's 0.25 W): the scores rest on passes 17210-17212, 249 of the 333 runs that launched, above the registered
  minimum of two kept passes; every pool-8 tile scored, none short. The relaxed arm (the anchor and tie gates relaxed, all four passes) gives the
  same verdict on every rule (`scored.json` › `arms.relaxed`).
- **Three of the 336 planned runs were skipped by E78's launch rule** ("launch reading not reached": the die did not settle to its 58 °C launch
  reading; p17211 #27 `fp16.zeros`, p17212 #39 `fp32.s8_onebit_b19_c11b3dd2` and #52 `fp32.real_smol_softmax_v_causal`, each pass's `run.log`).
  No run was retried.
- **Every launch's C is bit-exact:** 3,470 of 3,470 PASS against the RTL's arithmetic (Q139(k)'s `ccheck.py`, `--jobs 2`; fp32 1,456, fp16 1,002,
  int8 1,012; no ROUNDING, UNMODELLED or FAIL), the smoke's 60 included ([`ccheck/`](ccheck/)). **P8-KC PASS**: no tile left the scored sets.
  The sessions that must carry a C log (the smoke and the four passes) each carried one, checked to its end (5 of 5); the stop-path test carried no
  launch and no C record. Each of the six anchors in the float scale is C all PASS, so the c_clean_scale arm is the primary ([`scale-c.md`](scale-c.md)).
- **No stop fired** outside the stop-path test: the highest live readings were **61.67 W board** and **63 °C** `minshire[0]` (stops 66 W /
  72 °C); the hottest-sensor field carries a 65 °C maximum from before the session (no statistics reset) in every sample. The stop-path test fired
  the die stop (65.0 °C ≥ 1.0 °C, read 0.033 s after its sample), the board stop (29.74 W ≥ 1.0 W, 0.027 s) and the watcher's board stop (29.74 W,
  0.056 s) on live samples with no launch.
- **Every device-management command sent was a read** (§ Device commands sent).
- E174 ran on card 0 of this host after this session had ended (12:44:43-13:11:49 PST,
  [`../2026-11-05-e174-blind8-card0/`](../2026-11-05-e174-blind8-card0/README.md)), and this session was copied back only after E174's end.

## Results

**In plain words.** A designer who never saw either model wrote pool 8; M10 and M9, frozen before any of it was measured, predicted each tile's
power and its 4.5 s die rise on this card. Over the 31 priority-1 new kinds, M10's error is **0.185 W rms** (M9's 0.266 W on the same tiles), the
size its held-out score said (0.187 W on pool 7's kinds on this card). M10 is resolved better than M9, and better on the floats, where its two new
power terms act: the session's own scale from its random anchors (s = 1.0080 here) and the single high bits counted by the convergence rule
(class S: 0.238 W against M9's 0.385 W). The 4.5 s heat law holds blind in every format. What fails is the floats' level: after the session's
scale, the 19 float kinds still read 0.105 W above M10 on average, outside the bias line, so P8-G fails on B1 (not on P1, as forecast). Whether that
excess is a level or a gain between sessions is not separated by the 12 re-runs.

**The registered verdicts** ([`results.md`](results.md), [`scored.json`](scored.json) › `primary`; the scorer of record
[`score_p8_600.py`](../../../../tools/claims-v3/p8-600/score_p8_600.py), `a518aa11`, with `score_p8_600_v2.py scale-c` and
`score_p8_600_v3.py ka-pooled` beside, as dated notes 1 and 2 register):

| rule | set | reading | line at the scored n | verdict |
|---|---|---|---|---|
| P8-KC | every launch of every pool-8 tile in a kept pass | 3,470 of 3,470 bit-exact in the session | bit-exact | PASS |
| **P8-P1** | rms(D − M10 primary), fp32, 11 | **0.209 W** | [0.098, 0.308] | **PASS** |
| **P8-P2** | the same, fp16, 8 | **0.224 W** | [0.075, 0.268] | **PASS** |
| **P8-P3** | the same, int8, 12 | **0.125 W** | [0.105, 0.269] | **PASS** |
| **P8-B1** | mean(D − M10 primary), floats, 19 | **+0.105 W** | [−0.097, +0.070] | **FAIL LOW** |
| P8-B2 | the same, int8, 12 | +0.005 W | [−0.115, +0.096] | PASS |
| P8-C1 | M10's 95% power band, 31 | 29 of 31 inside | at least 27 | PASS |
| **P8-M1** | M10 primary against M9, both at the measured rate, 31 | **−0.080 W [−0.134, −0.034]** | paired, 20,000 draws | **BETTER** |
| P8-M1f | the same, floats, 19 | −0.112 W [−0.179, −0.053] | paired | BETTER |
| P8-M1i | the same, int8, 12 | +0.009 W [−0.004, +0.019] | paired | NOT RESOLVED |
| **P8-A1** | the session scale against s = 1, floats, 19 | **−0.095 W [−0.135, −0.050]** | paired | **BETTER** |
| P8-KA | the check anchors (2) | Σe_p² 0.0369 < Σe_0² 0.1970; both inside M10's band | — | PASS |
| P8-H1 | rms(dT_win − M10's 4.5 s rise), fp32, 11 | 0.214 °C | [0.179, 0.431] | PASS |
| P8-H2 | the same, fp16, 8 | 0.250 °C | [0.163, 0.455] | PASS |
| P8-H3 | the same, int8, 12 | 0.101 °C | [0.091, 0.212] | PASS |
| P8-H4 | M10's 4.5 s heat band, 31 | 31 of 31 inside | at least 27 | PASS |
| **P8-LG** | the 12 float re-runs in 2 groups (E157 8, E164 4) | F_level 1.024, F_slope 0.541 (null 0.599) | F point 4.459 at df (2, 8) | **NOT SEPARATED** |
| **P8-G** | P1-P3, B1, B2, C1 and M1 | B1 FAIL LOW | — | **FAIL** |
| P8-HM | heat over minutes | — | — | NOT SCORED (no hold ran in this session) |

**P8-KA pooled over E171 and E172** (the registered read, `score_p8_600_v3.py ka-pooled`, dated note 2; [`ka-pooled.json`](ka-pooled.json)):
**PASS**, 4 check anchors, Σe_p² 0.0836 against Σe_0² 0.3255, all four inside M10's primary 95% band (E171 `fp16` −0.075 W, `fp32` +0.203 W;
E172 `fp16` +0.108 W, `fp32` +0.159 W); the c_clean_scale arm beside reads PASS. Read at 13:37:41-43 PST, after E171's data and results were
committed (`91f8ae40`, 13:10:18), from E171's collected files (byte-identical to the committed `scored.json` and `scale-c.json`).

**Against the registered forecast** (E172.md § What I expect, "frozen so it can be wrong"): KC, P2, P3, B2, M1i, KA, H1-H4 and HM read as forecast;
P1 PASS (forecast PASS or FAIL); M1 and A1 BETTER (forecast NOT RESOLVED or BETTER); M1f BETTER, as forecast; B1 FAIL LOW, one of the two forecast
readings; LG NOT SEPARATED, one of its two; **G FAIL, but on B1 rather than on P1**; the lane's added B2 "PASS or FAIL HIGH" read PASS.

**Each arm against M10's primary** (`scored.json` › `primary.reported.N1`, reported, 31 tiles, rms (mean) in W): **the primary 0.185 (+0.066)**;
the a-priori arm (s = 1) 0.255 (+0.147); M9 at the measured rate 0.266 (+0.134), at its nominal rate 0.238 (+0.092); M10 at the stated rate
0.254 (+0.146). **By class** (M10 against M9, rms in W): single high bits S 8 tiles 0.238 / 0.385; unaimed U 10 0.194 / 0.264; real tiles R 8
0.163 / 0.188; whole-line L 4 0.074 / 0.071; held-B H 1 0.030 / 0.036. **The session's float scale** s = 1.0080 from its six random anchors
(`fp32.randn` 1.0118, `fp16.randn` 1.0078, pool 8's four 1.0060-1.0123).

**The re-runs** (LG, reported per group): E157's eight float tiles read a level a = −0.103 W [−0.269, +0.063] and a gain g = +0.55% [−0.67%,
+1.77%]; E164's four a = +0.017 W [−0.309, +0.343], g = +0.05% [−2.07%, +2.17%]; residual sd 0.103 W. At the registered design LG reads NOT
SEPARATED in 92.8% of draws when the sessions agree.

**The arms of the reduction** (`scored.json` › `arms`, reported, never a verdict): leakage 0.2955 and 0.3320 W/°C and the relaxed gates give
the primary's verdict on every rule; the session's own leakage slope (`session_own_slope`) moves M1, M1f and A1 to NOT RESOLVED, M1i to WORSE and
KA to FAIL; the dips-kept arm keeps one pass (17210), so it scores nothing (NOT SCORED throughout).

## What it does to predicting power and heat

- **The terms tested:** M10's whole 600 MHz power model (Q142(m), frozen `6829c9ba`; its pool-8 predictions frozen `4576fb90`) on 31 kinds no
  model had seen, with its three new terms: (a) the session's own float scale, (b) the single high bits by the convergence rule, (c) the 4.5 s
  heat per board W; and M9 on the same tiles.
- **Before:** M10 held out, not blind: floats 0.185 W rms over 737 rows; pool 7's 48 kinds 0.187 W on this card; int8 0.177 W; card 1's 4.5 s
  law 0.31-0.32 °C for floats. M9 blind on pool 7 on this card: 0.273 W; the 4.5 s heat 0.21-0.35 °C.
- **After (blind, this session):** M10 **0.185 W rms** on 31 new kinds (fp32 0.209, fp16 0.224, int8 0.125 W), resolved better than M9 (0.266 W);
  the session scale resolved better than s = 1 (A1); the 4.5 s rise **0.214 / 0.250 / 0.101 °C** (fp32 / fp16 / int8), every tile inside M10's
  heat band. The held-out power figure held blind on this card; the heat law's blind error is below its held-out figure.
- **What it says to change:** the floats carry a session excess that the anchors' scale does not remove (+0.105 W after s = 1.008, B1); the 12
  re-runs cannot yet say whether such an excess is a level or a gain (LG NOT SEPARATED), so the next model's float term needs more sessions per
  card (term a is a session scale). **Nothing frozen changes here.**

## Registered before any data, and what the box ran

- **Frozen first:** blind pool 8 (64 tiles by an independent designer: design `153b720f`, Wed 4 Nov 23:22:03 PST; the pool, `blind8.json` and
  every model's predictions `4576fb90`, Thu 5 Nov 02:30:56, under the converter's rule `ebf68c52`, 01:38:29; the freeze's note `dfe226f1`,
  03:11:24), with M10's and M9's card-1 predictions
  ([`predictions-pool8-aifoundry1c1.json`](../../../../tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry1c1.json)); M10 (registration
  `e9367b66`, fit `6829c9ba`, `d1581099`, `c996d135`); pool 8's registration `3e97f583` with A1 `8a8fa34c` and A2 `68a7c322`; the frozen predictor
  `9d81d254` and `97765c0a`. Nothing was fitted here.
- **Registered** (Q142(k6)), every commit before any E172 data, claim or launch: [`E172.md`](../../../../tools/claims-v3/e172/E172.md),
  `4441083f` (03:38:53 PST); the P8 scorer `a518aa11` (03:55:27); the kit `14fcb30d` (04:19:20); the k6 runbook `9a2630ff` (04:30:38);
  [dated note 1](../../../../tools/claims-v3/e172/E172.md.dated-note-1.md) `2502ba81` (05:38:09), the scorer's v2 `86d10a75` (05:49:09) and
  step 22 v2 `1a76a870` (06:00:15); [dated note 2](../../../../tools/claims-v3/e172/E172.md.dated-note-2.md) `c9a3e40a` (08:23:02), the v3 code
  `e2b48f5a` (08:27:12) and `6f4b48e4` (08:31:18). M11's HC1-B and I8P-B (card 1's heat scale and paired int8 term, to be read from this
  session's committed files) were registered in `3c31a91d` (07:41:57), amended `f49b7ddd` (08:44:59), and their reader committed in `2b33103c`
  (10:15:36) and `ea12f108` (11:13:51), all before this session. The lab's main at the launch was `ea12f108` = origin/main.
- **At the go** (the card day's claim, 11:25:18-11:25:23 PST): the window (last start 15:00, last end 16:00 PST; E172's deadline 15:50), the desk
  step (HEAD descends from `14fcb30d`, the kit paths clean, blind8 89, the freeze 160, the scorer 5, the predictor 16 / 9 / 209) and step 3b
  (`LISTS22: 22 of 22 PASS`, `LISTS-V3: 2 of 2 PASS`, the checker's sha256 `8a201b20…`).
- **The box steps** (the k6 runbook, every call after a 15 s probe and under its bound): the look 11:38:13-14 PST (`s05_look_k6.sh`, through
  `box/look_e172.sh`: the host booted 2026-10-26 15:02:04, before E82's firmware read of 2026-10-31 13:45:24 PDT; et-who "No process holds an
  ET-SoC-1 device node or card lock."; the binaries `e0fbecce…`, `8008f96f…`, `990807f4…`, `4f0956ce…` at E164's pins; HOLDER-RULE FREE); the
  sync 11:39:08-09 (`s12_a1_check_k6.sh sync`: `tools/claims-v3/e172/`, pool 8 and the three pinned watcher files into `~/nekko`); the check on
  the box as a detached job 11:39:19-51 (`HARNESS OK: 103 files`; the preflight `GO (32 send sites, 0 disallowed)`; the tiles 0 problems;
  pool 8's 89; the dry pass of 17210 rc 0 with 86 device calls listed; the dry smoke rc 0; the dry stop-path test rc 1, as a dry run ends);
  **the launch 11:40:13-22** (`s13_a1_launch_k6.sh`, the full plan, `E172_DROP_P2=0`: the runbook's guard read GUARD-OK; `box/launch_e172.sh` with
  the deadline `2026-11-05 15:50 PST`, 14,986 s away, "4 of the 4 planned", the holders at launch all 0 on both cards
  ([`logs/holders-at-launch.txt`](logs/holders-at-launch.txt)), `HARNESS OK: 103 files`, T0 11:40:14 PST); six bounded waits 11:40:34-12:34:16
  (`s20_wait_k6.sh e172`, the session's end read at 12:34:16); E174 on card 0 after it (12:44:43-13:11:49); then the collection, after E174's end,
  through `s22_collect_k6_v3.sh e172`, 13:19:36-13:35:38 (its quiet read at 13:19:37: no card session of ours and no dry pass on aifoundry1; the
  pull 13:19:37-40; the collector, the C-session gate, `scale-c` and the desk-path gate), and `s22_collect_k6_v3.sh ka` at 13:37:41-43.

## Registered against what happened

| | registered | happened |
|---|---|---|
| order | the registration, the scorer, the kit, the runbook, notes 1 and 2 and the v3 code before the claim and the first launch, each descending from the frozen pool and M10 | all ancestors of the lab's main at the launch (`ea12f108`); the claim 11:29:08 PST; `E172_T0`, the session's first device access, 11:40:14 |
| design | passes 17210-17214 as the budget allows (N4: four, or five if each takes about 748 s or less); at least two kept | four passes ran (756-801 s), the budget rule stopped before 17214; the reduction kept three (17213 set aside by E78's pass gate); 3 runs skipped by E78's launch rule |
| card time | the cap 65 card-minutes; no session after 15:00, every run ends by 16:00 PST (E172_DEADLINE 15:50) | **53.7 card-minutes** (11:40:14-12:33:55 PST) |
| stop-path test 17202 | the guard's die stop at 1.0 °C, its board stop at 1.0 W and the watcher's board stop at 1.0 W each end the runner on a live sample, no launch | **PASS**: each `run_e172` exit 6 on a live sample read 0.027-0.056 s after it was taken ([`logs/session.log`](logs/session.log)) |
| smoke 17201 | the gate (`smoke_gate_e172.py`) | **PASS** (11:41:12): 10 items × 5 launch records, 546.001 / 318.0 cycles per op, 0.5992-0.5996 GHz, every dump equal to its sha256, config 65 / 65 / 600 at both ends, 404 samples, board 29.61-57.70 W, `since_reset_ms` −1, 60 C records for 60 launches, launch gaps median 3 ms |
| stops | board ≥ 66 W or any `temp_c.minshire` field ≥ 72 °C, live, main path and in-run watcher | highest 61.67 W and 63 °C live; no stop fired |
| the C check | every launch, bit-exact; every listed session checked to its end | 3,470 of 3,470 PASS; 5 of 5 sessions; no tile left out |
| collection | E172 collected only when nothing of ours runs on aifoundry1 (dated note 2, 2.5) | after E174's end; the quiet read QUIET-OK at 13:19:37 |
| departures | — | none. This directory is the collector's output (`build/e172-out/2026-11-05-e172-blind8-card1/`), copied unchanged but for `ccheck/`: `ccheck-session.json` gzipped, as E164's, and the collector's five `c-log-<pass>.jsonl.gz` copies left out (each pass's own `c-log.jsonl.gz` is in `aifoundry1-c1/`) |

## Device commands sent

As registered ([`E172.md`](../../../../tools/claims-v3/e172/E172.md) § Device commands sent): E164's sending code on this card, unchanged
(`lib.sh`, the same `ettelem` binary through E128's guard, the block's config reads and its one `start_sampler` call). `ettelem config` at the
session's start (11:40:15 PST) and end (12:33:55), and at both ends of the stop-path test, the smoke and every pass; `ettelem sample` at 10 Hz
in every block. Sent: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES,
**GET_ASIC_VOLTAGE**, GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, **GET_MODULE_VOLTAGE**: **all READs**, classified from
et-platform `836a4ab` (BL2 0.22.0), the build card 1 has reported since E82's read (identity by the host's boot time, as registered); the two in
bold are PMIC voltage-register reads, which the owner's rule of 2 November 2026 allows. **Never sent**: the statistics reset (`since_reset_ms` −1
in every one of the session's 31,614 samples), any SET_*, the firmware-revisions query, any residency read, any governor, TDP, threshold or clock
set, any reset, and `dev_mngt_service`. The checker (`dmcmd_audit.py`, unchanged), run by the session on the box before any device opened:
**GO**, 32 send sites, 0 disallowed ([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt)).

## Card and post

`et-who` at the look-first reads (11:38:14 PST, and the lane's finer read at 11:38:41), at the session's start (11:40:14) and at its end
(12:33:55): no process held a device node or card lock on either card. Another account's two terminals, idle since 26 October, were present, its
logind session closing, its processes at 0.4% CPU with none a device or CI process; an idle login does not block (the owner's ruling of 1 November
2026). Nothing of ours was busy on the host before the launch. The collector's scrub (`scrub_etwho_e164.py`: 0 files rewritten) and its
`--check`, run on `logs/`, by step 22, and again on this whole directory, leave no other account's login in any file (0 left);
[`logs/et-who-summary.txt`](logs/et-who-summary.txt) counts the session's two et-who readings by card, without names: no holder on either card.

Thu 5 Nov's one `#community-lab` post is message `1567984130841641044`, created at 11:29:08 PST by the card day's claim. Its aifoundry1 clause,
`using aifoundry1 for 3 h, until ~14:29 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, covered both cards of this
host; at E172's end (12:34:44-50 PST) it became card 0's, `using aifoundry1 card 0 for 1 h, until ~13:34 PST [doc](<…>)`, and at E174's end
(13:12:22-28) ` — released` was appended, card 0's clause being the last one held (E174's README, § Card and post, has the read-backs).

## How to reproduce

```bash
# from the lab clone, over the raw copy (build/e172-raw: aifoundry1:nekko/build/claims-v3/aifoundry1-c1/e172{,-smoke,-stoptest}/ and
# nekko/build/e172/ as logs/; this directory's aifoundry1-c1/ and logs/ hold the same files)
PY=/usr/bin/python3 E172_DATE=2026-11-05 E172_OWNER=<the box login of record> nice -n 10 bash tools/claims-v3/e172/collect_e172.sh build/e172-raw
# it writes build/e172-out/2026-11-05-e172-blind8-card1/; then the C-session gate and the scale anchors' C status:
python3 -B tools/claims-v3/p8-600/ccsessions_p8.py --run E172 --raw build/e172-raw \
  --ccheck build/e172-out/2026-11-05-e172-blind8-card1/ccheck/ccheck-session.json
/usr/bin/python3 -B tools/claims-v3/p8-600/score_p8_600_v2.py scale-c --run E172 --scored <out>/scored.json --reduction <out>/e172.json \
  --raw build/e172-raw --ccheck <out>/ccheck/ccheck-session.json --json <out>/scale-c.json --md <out>/scale-c.md --work <out>/scale-c
# P8-KA pooled with E171 (the registered read, dated note 2):
/usr/bin/python3 -B tools/claims-v3/p8-600/score_p8_600_v3.py ka-pooled <E171 scored.json> <E172 scored.json> \
  --scale-c <E171 scale-c.json> <E172 scale-c.json> --json <out>/ka-pooled.json
```

Through the runbook these are `tools/claims-v3/q141k-runbook/k6/s22_collect_k6_v3.sh e172`, then `ka`. Collected and scored on the Intel at
`nice -n 10`, 13:19:36-13:35:38 PST, the C check at 2 jobs (from a cold reference cache) and the scorer single-threaded.

## Files

| file | what |
|---|---|
| `scored.json`, `results.md` | the registered scorer's output on the registered primary (Q139(u)'s footing, `--leak 0.3134106532552718 --no-refit`), every arm beside |
| `scale-c.json`, `scale-c.md` | each scale anchor's C status (`score_p8_600_v2.py scale-c`, dated note 1's N2): all six anchors in s C all PASS |
| `ka-pooled.json` | P8-KA pooled over E171 and E172 (`score_p8_600_v3.py ka-pooled`), the c_clean_scale arm beside |
| `e172.json`, `runs.csv`, `reduce.txt`, `reduce.log` | the registered primary reduction of the four passes (three kept) |
| `e172-auto.json`, `e172-dipskept.json`, `e172-leak0.2955.json`, `e172-leak0.3320.json`, `e172-relaxed.json` (with their `runs-*.csv`, `reduce-*.txt`, `reduce-*.log`) | the arms |
| `ccheck/` | `ccheck.py`'s output over every listed session (`ccheck-session.json.gz`, `ccheck-session.txt`) |
| `aifoundry1-c1/e172/p17210`-`p17213` | the passes as the box wrote them (`telemetry.jsonl.gz`, `runs.jsonl`, `run.log`, `block.json`, the config reads, `c-log.jsonl.gz`, the tiles, …) |
| `aifoundry1-c1/e172-smoke/p17201`, `aifoundry1-c1/e172-stoptest/p17202` | the smoke and the stop-path test |
| `logs/` | the box's `build/e172/` (`session.log`, `session.out`, `queue.out`, `T0`, the session's config reads, `holders-at-launch.txt`, the device-command preflight, `binaries.sha256`) and the scrub's `et-who-summary.txt` |
| `code.sha256`, `score.log` | the code the collector ran, hashed; the scorer's log |

SPDX-License-Identifier: Apache-2.0
