# E171: blind pool 8 on aifoundry3 card 0 - M10 resolved better than M9 on 31 new kinds (−0.065 W [−0.122, −0.012]) and its float scale term carries blind (A1 BETTER, KA PASS), every launch's C bit-exact, the 4.5 s heat inside in every format (H1-H4 PASS); but P8-G FAIL: fp16 misses its rms line by 0.0007 W, carried by one single high bit (+0.518 W), and the floats read +0.092 W above M10 (B1 FAIL LOW); the 12 re-runs agree with their earlier sessions (LG NOT SEPARATED)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, "a power model across kinds", with items 8 and 9 (heat). It is the aifoundry3 half of pool 8's card day (E171 here, E172 on
aifoundry1 card 1), the Q142(r)/(p)/(d) critic's `next` rank 2 and the readiness critic's card day, run as registered in
[`tools/claims-v3/e171/E171.md`](../../../../tools/claims-v3/e171/E171.md) with its dated notes 1 and 2. Thu 5 Nov 2026 (week 45), PST, on the
owner's go of that day (about 11:15 PST: "feel free to use all 4 cards for experiments"). The mandate: his words of 2 November 2026 ("settle
any unanswered questions regarding horace's power model"), with his goal "to be able to predict the power requirement and heat generation of
various kinds of numeric computations as accurately as possible".*

- **Card:** aifoundry3 card 0, **600 MHz in all 33,818 samples**; `ettelem config` through E128's guard at the session's start (11:38:12 PST)
  and end (12:35:32): TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV both times. **Nothing was set.** `since_reset_ms` −1 in every
  sample: no statistics reset.
- **Card session** 11:38:12-12:35:33 PST, **57.4 card-minutes** (T0+3,441 s), inside FULL's cap of 70: the stop-path test 17102, the smoke
  17101 and its gate (PASS at 11:39:09), then **FULL as registered**: kinds passes 17110 (862 s), 17111 (818 s), 17112 (830 s) and 17113
  (833 s), the fourth admitted by the budget rule (it started at T0+2,597 s, projected 862 s, against the last end T0+4,140 s). **All four
  passes kept** on the registered primary; nothing set aside; no tile left out.
- **Every launch's C is bit-exact:** 3,490 of 3,490 PASS against the RTL's arithmetic (Q139(k)'s `ccheck.py`, `--jobs 2`; fp32 1,476, fp16
  1,012, int8 1,002; no ROUNDING, UNMODELLED or FAIL; no broken record): 60 in the smoke, 850 in pass 17110 and 860 in each other pass. The
  five sessions that must carry a C log each carried one, checked to its end (`ccsessions_p8.py`: FINISHED); the stop-path test carried none.
  **P8-KC PASS.** Every anchor in the float scale is C all PASS (`scale-c.md`): the arm `c_clean_scale` is the primary.
- **No stop fired** in any pass: the highest live readings were 54.77 W board and 63 °C `minshire[0]` (stops 65 W / 70 °C), 51.11 W and
  55 °C in the smoke. The stop-path test fired all three stops on live samples with no launch.
- **Every device-management command sent was a read** (§ Device commands sent).
- **One run was skipped by E78's own rule:** in pass 17110, item 41 (`int8.l8_cycle3_d3p3c15_c6d5`) did not reach its launch reading (its
  approach ended at 59 °C, above the 58 °C launch line, after 1.4 s, quiet 1.41 s) and was marked skipped, not retried
  (`aifoundry3/e171/p17110/run.log`, `marks.jsonl`); that tile is measured in three kept passes, every other tile in four. E163 skipped none.

## Results

**In plain words.** A designer who never saw any model's errors wrote pool 8; M10, frozen before it, predicted each tile's power and its 4.5 s
die rise on this card, with M9 beside it. Over the 31 priority-1 new kinds M10's error is **0.180 W rms**, clearly better than M9's 0.245 W on
the same tiles (resolved by the paired bootstrap), its bands hold 30 of 31 and its heat is inside on every format. The session's own random
anchors set a float scale of 1.00615, and that scale improves the new float kinds over the a-priori arm and carries to the two check anchors it
never read. But the session still reads above M10 on the floats (+0.092 W, beyond the registered line), and fp16's error lands 0.0007 W over
its line, almost all of it one tile: a single high B bit at position 2 on the base word `c46e`, +0.518 W, the only tile outside its band. The
twelve tiles re-run from two earlier sessions read the same as then, within 0.055 W, so the re-runs show neither a gain nor a level.

**The registered verdicts** ([`results.md`](results.md), [`scored.json`](scored.json) › `verdicts` and `primary.rules`; the scorer
`score_p8_600.py` as committed in `a518aa11`, on Q139(u)'s footing, leakage 0.20563713796102187 W/°C, dips removed; every rule scored at its
planned n, so each line is `intervals-pool8.json`'s):

| rule | reading | line (registered draws) | verdict |
|---|---|---|---|
| P8-KC (the C check) | 3,490 of 3,490 PASS; 5 of 5 listed sessions checked to the end | — | **PASS** |
| P8-P1 (fp32 power, 11) | rms 0.176 W | [0.098, 0.300] | PASS |
| P8-P2 (fp16 power, 8) | rms 0.2381 W | [0.063, 0.2374] | **FAIL** (0.0007 W over the 97.5% point) |
| P8-P3 (int8 power, 12) | rms 0.131 W | [0.101, 0.249] | PASS |
| P8-B1 (floats bias, F1 19) | mean(D − M10) +0.092 W | [−0.097, +0.064] | **FAIL LOW** (M10 predicts too little) |
| P8-B2 (int8 bias, I1 12) | +0.035 W | [−0.105, +0.089] | PASS |
| P8-C1 (power bands, 31) | 30 of 31 inside M10's 95% bands | at least 27 | PASS (outside: `fp16.s8_onebit_b2_c46ec46e`) |
| **P8-M1** (M10 − M9, N1 31) | **−0.065 W** | **[−0.122, −0.012]** | **BETTER** |
| P8-M1f (floats, F1 19) | −0.091 W | [−0.164, −0.020] | BETTER |
| P8-M1i (int8, I1 12) | +0.002 W | [−0.018, +0.018] | NOT RESOLVED (as forecast) |
| **P8-A1** (session scale − a priori, F1 19) | **−0.062 W** | **[−0.093, −0.033]** | **BETTER** |
| P8-KA (the 2 check anchors) | Σe_p² 0.047 < Σe_0² 0.128 W²; both inside M10's band | — | PASS |
| P8-H1 / H2 / H3 (4.5 s rise) | rms 0.187 / 0.193 / 0.123 °C | [0.104, 0.248] / [0.083, 0.225] / [0.116, 0.261] | PASS / PASS / PASS |
| P8-H4 (heat bands, 31) | 28 of 31 inside | at least 27 | PASS (outside: `fp16.s8_onebit_b2_c46ec46e`, `fp16.s8_onebit_b4_c2e2c2e2`, `fp32.u8_bimodal_1f57eb`) |
| P8-LG (12 re-runs, 2 groups) | F_slope 1.026, F_level 0.081 (F point 4.459, df 2 and 8); the null 2.60 (point 3.84): the sessions agree | — | NOT SEPARATED |
| **P8-G** | P1, P3, B2, C1 PASS, M1 BETTER; **P2 FAIL, B1 FAIL LOW** | needs those six PASS and M1 not WORSE | **FAIL** |
| P8-HM (heat over minutes) | no hold in this session | — | NOT SCORED (as registered) |

**Against the frozen expectation** (E171.md, "What I expect, frozen so it can be wrong"): KC, P3, B2 (the lane's own line, "B2 PASS or FAIL
LOW"), KA and H1-H3 PASS; P1 PASS (forecast PASS or FAIL); B1 FAIL LOW (forecast PASS or FAIL LOW); M1f BETTER and M1 BETTER (forecast BETTER,
and NOT RESOLVED or BETTER); M1i NOT RESOLVED; A1 BETTER (forecast NOT RESOLVED or BETTER); LG NOT SEPARATED (forecast LEVEL or NOT SEPARATED);
HM NOT SCORED, all as forecast. **P2 read FAIL where PASS was forecast**, and so **G read FAIL on P2 and B1, where "PASS or FAIL on P1" was
forecast.** No other reading departs from the forecast.

**Each model on the same 31 priority-1 kinds** (`scored.json` › `primary.rows`, reported; M10's primary at the session's scale and the measured
rate, its a-priori arm at s = 1, M9 at the measured rate; heat at each model's own law):

| model | fp32 rms | fp16 rms | int8 rms | rms (31) | bias (31) | inside 95% | heat rms fp32 / fp16 / int8 (°C) |
|---|---|---|---|---|---|---|---|
| **M10 primary** | 0.176 | 0.238 | 0.131 | **0.180** | +0.070 | 30 of 31 | 0.187 / 0.193 / 0.123 |
| M10 a priori (s = 1) | 0.266 | 0.266 | 0.131 | 0.224 | +0.135 | — | — |
| M9 | 0.275 | 0.321 | 0.130 | 0.245 | +0.122 | 28 of 31 | 0.197 / 0.207 / 0.114 |
| M10 held out on this card (the lines' references, `intervals-pool8.json`) | 0.202 (260 rows) | 0.148 (133) | 0.170 (114) | — | — | — | 0.176 / 0.153 / 0.190 (the heat references) |

**By class** (N1, W; M10 rms / bias, and M9's rms; `scored.json` › `primary.reported.N1_by_case`):

| class | n | M10 | M9 |
|---|---|---|---|
| S (single high B bits) | 8 | 0.273 / +0.195 | 0.402 |
| U (aimed at nothing) | 10 | 0.137 / +0.043 | 0.165 |
| R (real tiles) | 8 | 0.144 / −0.006 | 0.166 |
| L (whole-line int8) | 4 | 0.105 / +0.036 | 0.128 |
| H (int8, B held) | 1 | 0.089 / +0.089 | 0.082 |

**What carries the misses.**
- **P2 and C1's one miss: a single high bit in fp16.** `fp16.s8_onebit_b2_c46ec46e` measured 11.503 W against M10's 10.986 W (+0.518 W, outside
  its band; its heat +0.335 °C, also outside), and M9 missed it by +0.551 W. Without it fp16's rms would be 0.163 W. The other fp16 single
  high bits read +0.12 to +0.19 W (`_b4_c2e2c2e2` +0.185, `_b7_b945b945` +0.176, `_b10_c127c127` +0.122 W), where M9 missed `_b7` by
  +0.608 W. Class S is still each model's largest miss, but M10's counts cut it from M9's 0.402 to 0.273 W rms.
- **B1: the floats sit above M10.** F1's mean error is +0.092 W with the scale applied (+0.197 W at s = 1); the fp32 single high bits
  (`_b19_c11b3dd2` +0.334, `_b7_3ee13961` +0.284 W) and `fp32.r8_dsqwen_l1_qk_f0161a` (+0.185 W) lead it, against
  `fp16.r8_dsqwen_l1_pv_188e98` −0.283 W. int8 is level (+0.035 W, PASS).
- **The scale, term a:** s = 1.00615 from six anchors, every one C all PASS (`fp32.randn` 1.00781, `fp16.randn` 1.00348, pool 8's four
  1.00521-1.00800). It lowers the floats' rms from 0.266 to 0.204 W over F1 (A1 BETTER; int8 is not scaled, so its a-priori arm is its primary), and both held-out check anchors land inside M10's
  band, closer than a priori (`fp32.anchor8_check_randn_319f73` +0.203 W against +0.353 W; `fp16.anchor8_check_randn_84631a` −0.075 W
  against +0.060 W; KA PASS on the squared sum).
- **LG: the re-runs agree with their earlier sessions.** Δ = D (today) − D (then) runs from −0.147 W (`fp32.b_onebit_b20_one`, E163) to
  +0.072 W (`fp16.exp_b_alt_shift`, E153), every one inside Welch's 95% interval (12 of 12); E153's group a −0.015 W [−0.104, +0.075], g
  +0.0018 [−0.0045, +0.0081]; E163's a +0.011 W [−0.165, +0.188], g −0.0061 [−0.0171, +0.0049]; residual sd 0.055 W. At this design the test
  sees a 0.6% gain in 76.4% of draws and a 0.11 W level in 90.0%: neither is there between these sessions.
- **The arms** (reported, never the verdict): with leakage 0.1994 W/°C and with E78's pass gates opened, every rule reads as the primary.
  With the leakage fitted on this session and the dips removed (s 0.996), P2 reads PASS, KA FAIL and LG GAIN; at 0.3803 W/°C (three passes
  kept), P2 PASS, B2 FAIL HIGH and LG BOTH; at leakage 0, B2 FAIL LOW and LG GAIN. The session-own footing and the frozen slope with the dips
  kept each kept two passes (17110 and 17113: E78's pass gates set the other two aside with the dips in), and read P1 FAIL, B1 PASS and M1,
  M1f, A1 NOT RESOLVED. So P2's and B1's verdicts, and LG's, move with the footing; the registered primary is the footing frozen beforehand.

## What it does to predicting power and heat

- **The term tested:** M10 as frozen (Q142(m), `m10.json` and `m10-s7.json`), with its three new terms (a: a float scale per session from the
  session's own random anchors; b: the single high B bits counted at 9-243 launch points by the convergence rule; c: heat per board W over
  4.5 s), against M9, on 31 new kinds written by an independent designer, at 600 MHz on aifoundry3.
- **Before (held out, not blind):** M10 on this card's rows 0.202 / 0.148 / 0.170 W (fp32 / fp16 / int8; the lines' references); over every
  card, floats 0.185 W rms over 737 rows, pool 7's 48 kinds 0.205 W here, int8 0.177 W. **Before (blind, the last model):** M9 on pool 7 here
  (E163), 0.278 W over 48 kinds (0.389 / 0.192 / 0.191 W), with the session +0.151 W above it on the floats; the 4.5 s rise 0.12-0.23 °C.
- **After (blind, this session):** M10 **0.176 / 0.238 / 0.131 W** (0.180 W over the 31, +0.070 W bias), M9 0.275 / 0.321 / 0.130 W (0.245 W)
  on the same tiles; heat **0.187 / 0.193 / 0.123 °C**. So on this card M10's blind error is the size of its held-out error overall, lower for
  fp32 and int8, higher for fp16 (one tile); the float scale term generalises to kinds and draws it never read; M10 beats M9 on the floats
  (M1f −0.091 W) and ties it on int8, as forecast; the 4.5 s heat law holds blind in every format.
- **What it says to change:** the single high B bits stay the largest class miss (+0.195 W bias over class S), so their price at a bit
  position and base word is still short; and the floats keep a positive bias of about 0.09 W after the session scale. LG says today's session
  did not differ from E153's or E163's on the re-run tiles, so this bias is not a day's level against those sessions. **Nothing frozen changes
  here.** P8-KA pooled waits for E172's collection (`s22_collect_k6_v3.sh ka`); M11's HC1-B and I8P-B read E172 with this session later.

**For the blog material and the hub:** this is the first blind score of M10. On 31 kinds nobody had fitted, it predicts a matmul's power at
600 MHz to 0.18 W rms on a 4.6-25.4 W range (0.7-4% of the switching power), better than M9 on the floats, and its 4.5 s die rise to
0.12-0.19 °C; it does not yet price a single high bit in fp16 or fp32 to within its bands every time.

## Registered before any data, and what the box ran

- **Frozen first:** blind pool 8 by an independent designer (design `153b720f`, 23:22:03 PST Wed 4 Nov), M10's and M9's predictions for it
  with every section-7 line at the planned n, Q142(x) `4576fb90` (02:30:56 PST Thu 5 Nov), the converter's rule `ebf68c52` (01:38:29) and the
  freeze's note `dfe226f1` (03:11:24); pool 8's registration (the P8 rules) `3e97f583` (23:11:53 Wed), A1 `8a8fa34c` (23:26:44) and A2
  `68a7c322` (00:21:34 Thu); the predictor `9d81d254` (23:30:18) and its entry point after A2 `97765c0a` (00:36:23); M10's registration
  `e9367b66` (19:33:42 Wed) and fit `6829c9ba` (20:24:58). Nothing was fitted here.
- **Registered** (Q142(k6)), every commit before any E171 data, claim or launch: [`E171.md`](../../../../tools/claims-v3/e171/E171.md) with
  E172's, alone, `4441083f` (03:38:53 PST); the P8 scorer and its C-session check `a518aa11` (03:55:27); the run kit `1b80da20` (04:05:05),
  E172's kit `14fcb30d` (04:19:20) and the k6 runbook `9a2630ff` (04:30:38); dated note 1 `2502ba81` (05:38:09), the scorer's v2 `86d10a75`
  (05:49:09) and step 22 v2 `1a76a870` (06:00:15); dated note 2 `c9a3e40a` (08:23:02, alone, before the code it names), the v3 code
  `e2b48f5a` (08:27:12) and its notes `6f4b48e4` (08:31:18). `git log --all` showed no E171 data in any ref before this commit.
- **At the go** (the owner's words of about 11:15 PST, "feel free to use all 4 cards for experiments"), at the desk, 11:25:18-11:25:23 PST:
  the window (no session starts after 15:00 PST, every run ends by 16:00), `s03_desk_k6.sh` (the pull at `ea12f108`, HEAD descending from
  `14fcb30d`, the kit paths clean, blind8 89, the freeze 160, the scorer 5, the predictor 16 / 9 / 209) and `s03b_lists_k6.sh` (22 of 22 and 2
  of 2 lists PASS; the checker's sha256 `8a201b20…`). The day's one post named aifoundry3 from 11:29:08 PST (§ Card and post).
- **The box steps**, the k6 runbook's (`tools/claims-v3/q141k-runbook/k6/`), each behind a 15 s probe with its bound, no login link at any:
  - 11:37:05 look first (`s05_look_k6.sh`): et-who rc 0, no holder line, no device process of ours or of any other account; 12 logins,
    none holding a device node or lock (an idle login does not block: the owner's ruling of 1 November 2026); booted 2026-10-26 15:18:24;
  - 11:37:14 the one rsync of E171's kit, pool 8 and the pinned watcher files into the binaries tree (`s07_a3_sync_k6.sh`; the paths clean
    at `ea12f108`);
  - 11:37:24 the checks on the box (`s08_a3_preflight_k6.sh`): blind8 `sha256sum -c` **89 OK**; `check_e171.py` **HARNESS OK: 101 files**;
    `preflight_e171.sh` **GO, 32 send sites, 0 disallowed**; `e171_common.py --verify` 0 problems (64 tiles, 40 of priority 1, 12 pool
    anchors, the 9 priority-2 kinds SHORT drops, E78's 6 items);
  - 11:37:32 the reads (`s09_a3_reads_k6.sh`): `et-lab-manifest` kept on the box; `ettelem config` through E128's guard under card 0's
    lock: TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV; et-who clean;
  - 11:37:39-11:37:56 the V3_DRY pass on the box as one detached job (`s10_a3_dry_k6.sh`, no device opened): block 17110 (86 launches
    through the C wrapper) rc 0, the smoke 17101 rc 0, the session's start gate refusing with exit 8 at a past `E171_LATEST_START`;
  - 11:38:10 look first again: FREE, as above;
  - 11:38:17 the session, detached (`s11_a3_session_k6.sh FULL`: `E171_T0` 11:38:12, `E171_PLAN=FULL`, `E171_LATEST_START` 15:00 PST,
    `E171_DEADLINE` 16:00 PST); it re-ran the harness check and the device-command preflight before any device opened.

## Registered against what happened

| | registered | happened |
|---|---|---|
| order | the registration (`4441083f`), the scorer (`a518aa11`), the kit (`1b80da20`), the runbook (`9a2630ff`), notes 1 (`2502ba81`) and 2 (`c9a3e40a`) with their code (`86d10a75`, `1a76a870`, `e2b48f5a`, `6f4b48e4`) before the claim and the first launch, each descending from the frozen pool and predictions (`4576fb90`) | all ancestors of the synced tree (`ea12f108`, 11:13:51 PST); the claim 11:29:08 PST; the day's first device access on this card 11:37:32 (the step-9 config read); the session's 11:38:12 (its start config read); the stop-path test 11:38:13-11:38:26 (no kernel launch); the first kernel launch in the smoke at about 11:38:27 |
| plan | FULL if 70 minutes remain before `E171_DEADLINE`, else TWO or SHORT; 4,200 s from T0 with a 60 s reserve; at least 2 kept passes | 262 minutes remained before the 16:00 PST last end: FULL; four kinds passes ran and were kept |
| card time | the cap 70 card-minutes; no session after 15:00, every run ends by 16:00 PST | **57.4 card-minutes** (11:38:12-12:35:33 PST); the passes took 818-862 s against the kit's 870-890 s estimate |
| stop-path test 17102 | the guard's die and board stops and the in-run watcher each end `run_e171.py` with EXIT_HOT on a live sample at most 2.0 s old, no launch | **PASS**: the die stop on `minshire[0]` 49.0 °C read 0.08 s after the sample, the board stop on 23.34 W at 0.121 s, the watcher on 23.24 W at 0.049 s (`aifoundry3/e171-stoptest/p17102/STOP.*`), each exit 6; no launch record and no C record |
| smoke 17101 | the gate (`smoke_gate_e171.py`) | **PASS** (`SMOKE-GATE PASS {'bad': []}`, 11:39:09): ten items, cycles per op 546.001 (floats) and 318.0 (int8), 0.5994-0.5997 GHz, every dumped tile equal to its sha256, 404 live samples (board 22.97-51.11 W), `since_reset_ms` −1, the config at both ends 0 W / 65 °C / 600 MHz; the C log 10 host records, 60 C records for 60 launch records, none unpaired or flagged, launch gaps median 3.0 ms (max 9) |
| stops | board ≥ 65 W or `minshire[0]` ≥ 70 °C, live, main path and in-run watcher | highest 54.77 W and 63 °C in the kinds passes; no stop fired |
| the C check | every pool-8 launch, bit-exact; every listed session's C log checked to its end | 3,490 of 3,490 PASS; 5 of 5 sessions; no tile left out |
| the reduction | Q139(u)'s footing, leakage 0.20563713796102187 W/°C, no refit, the dips removed; E78's run and pass gates | all four passes kept, none set aside; the scale's check `ok` (six allowed anchors) |
| departures | — | **D1, the post's span** (recorded here, Thu 5 Nov 2026, after the session and before the data commit; it touches no data and no rule): E171.md and its README give the day's post as `using aifoundry3 for 1.5 h` for FULL; the card day's claim posted aifoundry3's clause as `using aifoundry3 for 2 h, until ~13:29 PST`, the longer hold also covering the box steps before the session (the claim's own record names it). The card was released at 12:36:19 PST, 53 minutes before that estimate. No rule, stop, cap, plan or deadline changed. No other departure. |

## Device commands sent

As registered ([`tools/claims-v3/e171/E171.md`](../../../../tools/claims-v3/e171/E171.md) § Device commands sent): E163's harness and E78's
card code unchanged, every telemetry call through E128's guard (`ettelem config` with no argument, `ettelem sample --seconds --every-ms` and
nothing else): `ettelem config` at the session's start and end and at both ends of the stop-path test, the smoke and every pass, `ettelem
sample` at 10 Hz in every block; and once before the session, the runbook's step-9 read (`ettelem config` through the same
guard, under card 0's lock). Sent: GET_MODULE_STATIC_TDP_LEVEL,
GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**, GET_MODULE_POWER, GET_SP_STATS,
GET_MODULE_CURRENT_TEMPERATURE, **GET_MODULE_VOLTAGE**: **all READs**, classified from et-platform `836a4ab` (BL2 0.22.0), the two in bold
PMIC voltage-register reads, which the owner's rule of 2 November 2026 allows. **Never sent**: the statistics reset (`SET_STATS_RUN_CONTROL`;
`since_reset_ms` −1 in every sample), any SET_*, the firmware-revisions query, any residency read, any governor, TDP, threshold or clock set,
any reset, and `dev_mngt_service`. The checker (`dmcmd_audit.py`, unchanged), run by the session on the box before any device opened:
**GO**, 32 send sites, 0 disallowed, with E163's one reviewed exception (`lib.sh:154`, the conditional `--reset-ms` forward no call uses)
([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt)). Residual, as registered: aifoundry3's thermal firmware build is not public, so the
classes rest on `836a4ab`'s handlers.

## Card and post

`et-who` at the look-first reads (11:37:05 and 11:38:10 PST), at the step-9 read (11:37:32), and at the session's start (11:38:12) and end
(12:35:33): no process held a device node or card lock, and no other account ran a device process. Other accounts' logins were present
(12 terminals on the box, the other accounts' idle since 26 October by the claim's finer look at 11:26:54), which do not block (the owner's
ruling of 1 November 2026). No other session or dry pass of ours ran on aifoundry3 beside E171's (the launch's guard read none); the card day's other runs use
aifoundry1 (E172, then E174) and aifoundry2 (E173).

Thu 5 Nov's one `#community-lab` post is message `1567984130841641044`, created at 11:29:08 PST by the card day's claim with one clause per
box: aifoundry3's read `using aifoundry3 for 2 h, until ~13:29 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`.
**The release, 12:36:19 PST**, under the Discord lock and `EXPECT_TEXT`, dry-run, saved and read back (12:36:19-12:36:24: one post that day,
its text equal to the intended one). The first attempt's dry run stopped with exit 7, "changed since read", because the aifoundry1 lane had
rewritten its own clause at 12:34; the step re-read the post and rebuilt the text from what it then said. The aifoundry3 clause was dropped
and the one other clause kept word for word, with no " — released", because that card was still held:
`<ai> **Claude says:** using aifoundry1 card 0 for 1 h, until ~13:34 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`.
Wed 4 Nov's, Tue 3 Nov's and Mon 2 Nov's posts were not touched.

## How to reproduce

```bash
# from the lab clone: rebuild the runbook's raw copy from this directory, then the registered collector over it (Python 3.9 with numpy)
D=docs/reports/data/2026-11-05-e171-blind8-aifoundry3
mkdir -p build/e171-raw/logs && cp -R $D/aifoundry3/. build/e171-raw/ && cp $D/logs/* build/e171-raw/logs/
PY=/usr/bin/python3 E171_DATE=2026-11-05 nice -n 10 bash tools/claims-v3/e171/collect_e171.sh build/e171-raw
# (it reads c-log.jsonl.gz and telemetry.jsonl.gz as they are, and writes build/e171-out/2026-11-05-e171-blind8-aifoundry3/;
#  the reductions record the pass directories as build/e171-raw/e171/p171NN, the runbook's route)
python3 -B tools/claims-v3/p8-600/ccsessions_p8.py --run E171 --raw build/e171-raw \
  --ccheck build/e171-out/2026-11-05-e171-blind8-aifoundry3/ccheck/ccheck-all.json    # the C-session gate
```

The card day ran it as the k6 runbook's step 22 v3, `tools/claims-v3/q141k-runbook/k6/s22_collect_k6_v3.sh e171` (12:36:56-12:56:59
PST): the two bounded copies, `collect_e171.sh` at nice 10 (its C check `--jobs 2`), the C-session gate, `score_p8_600_v2.py scale-c`, the
logs' scrub check (0 left) and the desk-path gate (442 files, clean). This directory is that output, byte for byte (`diff -r` against `build/e171-out/`), with this README added.

## Files

| file | what |
|---|---|
| `scored.json`, `results.md` | the registered scorer's output on the registered primary (Q139(u)'s footing), every arm beside |
| `scale-c.json`, `scale-c.md` | the scale anchors' C status (dated note 1, N2): six anchors in s, every one C all PASS, so the arm `c_clean_scale` is the primary |
| `e171.json`, `runs.csv`, `reduce.txt`, `reduce.log` | the registered primary reduction of the four kinds passes |
| `e171-session.json`, `e171-auto-nodips.json`, `e171-kfrozen-dips.json`, `e171-leak*.json`, `e171-gatesoff.json` (with their `runs-*.csv`, `reduce-*.txt`, `reduce-*.log`) | the arms |
| `score.log` | the scorer's own output |
| `ccheck/` | the C logs (`c-log-p171*.jsonl.gz`) and `ccheck.py`'s output (`ccheck-all.json`, `ccheck.txt`) |
| `aifoundry3/e171/p17110`-`p17113` | the passes as the box wrote them (`telemetry.jsonl.gz`, `runs.jsonl`, `run.log`, `marks.jsonl`, `block.json`, the config reads, `c-log.jsonl.gz`, the tiles' hashes, …) |
| `aifoundry3/e171-smoke/p17101`, `aifoundry3/e171-stoptest/p17102` | the smoke and the stop-path test (its `STOP.die`, `STOP.board`, `STOP.watch`) |
| `logs/` | the session's own logs: `session.log` (with et-who's readings, no holder), `queue.out`, `session.out`, the session config reads, `dmcmd-preflight.txt`, `binaries.sha256` |
| `code.sha256` | the sha256 of every registered file the collection read |

SPDX-License-Identifier: Apache-2.0
