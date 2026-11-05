# E164: blind pool 7 on aifoundry1 card 1 - M9 predicts 48 new kinds to 0.273 W rms on the second 600 MHz card, but is not resolved better than M6 there (−0.048 W [−0.111, +0.013]) and E164-RANK1 FAILS (resolved worse than M6 on the 12 kinds aimed at nothing; the floats read +0.164 W above M9, int8 −0.076 W below; 41 of 48 inside its bands); every launch's C bit-exact (3,896 of 3,896); the card term holds on floats (X1 0.9621) but not on int8 (X2 0.9418), while rank 4's paired-anchor scale passes on both families

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, "a power model across kinds". It answers the Q139 critic's **rank 1** on this card (M9 against M6 on pool 7's 48 priority-1
kinds, blind; E163 is aifoundry3's half, [`../2026-11-04-e163-blind7-aifoundry3/`](../2026-11-04-e163-blind7-aifoundry3/README.md)),
**rank 4** (a card's scale from a short run of random anchors, scored on the E163 / E164 pair), **rank 7** (card 1's day-to-day repeat of
8 pool-6 tiles against E157; the complaint was first written in E157's README, K1 FAIL,
[`../2026-11-03-e157-blind6-card1/README.md`](../2026-11-03-e157-blind6-card1/README.md)), rank 9 (the real tiles) and the card term on
pool 7 (X1 / X2), with Q141(t)'s reported 27-point arm, as Q140's and Q141's critics left E164 (`card_half[1]`). Wed 4 Nov 2026 (week 45),
the card half of Q141, on the owner's go of that day (about 13:55 PST). The mandate: his words of 2 November 2026 ("settle any unanswered
questions regarding horace's power model"), with his goal "to be able to predict the power requirement and heat generation of various kinds
of numeric computations as accurately as possible".*

- **Card:** aifoundry1 card 1 (`V3_DEVICE=1` / `ET_DEVICES=1`, its own lock, the `~/nekko` tree), **600 MHz in all 34,396 samples**;
  `ettelem config` through E128's guard at the session's start (14:19:35 PST) and end (15:17:53): TDP 65 W, threshold 65 °C,
  managed_power, 600 MHz, 499 mV both times. **Nothing was set.** `since_reset_ms` −1 in every sample: no statistics reset.
- **Card session** 14:19:34-15:17:53 PST, **58.3 card-minutes** (T0+3,499 s), inside the cap of 65 (planned 57.6, 56.7-58.2: the third
  pass took 869 s against the 848 s scaled from E157): the stop-path test 16402, the smoke 16401 and its gate (PASS at 14:20:35), then
  **the registered full design**: passes 16410 (837 s), 16411 (849 s), 16412 (869 s) and 16413 (843 s); the budget rule stopped before
  16414 (it would have ended at T0+4,368 s against T0+3,840 s), as registered. **All four passes kept** on the registered primary; nothing
  set aside; all 61 pool-7 tiles scored.
- **Every launch's C is bit-exact:** 3,896 of 3,896 PASS against the RTL's arithmetic (Q139(k)'s `ccheck.py`, `--jobs 2`; fp32 1,406,
  fp16 832, int8 1,658; no ROUNDING, UNMODELLED or FAIL; no broken record), the smoke's 66 included. **E164-PC** (2,550 pool-7 launches),
  **E164-K7C** (316) and **E164-PCa** (920) **PASS**; no tile left the scored set.
- **No stop fired** outside the stop-path test: the highest live readings were **61.20 W board** and **63 °C** `minshire[0]` (stops 66 W /
  72 °C); the hottest-sensor field carries a 65 °C maximum from before the session (no statistics reset) in every sample. The stop-path
  test fired all three stops on live samples with no launch.
- **Nine of the 384 planned runs were skipped by E78's launch rule** ("launch reading not reached ... skipped": the die did not settle to
  its 58 °C launch reading in the protocol's wait; three in 16411, one in 16412, five in 16413, in each pass's `run.log`, listed in
  [`posthoc/readings_e164.txt`](posthoc/readings_e164.txt)). So five tiles
  carry three kept passes (`fp32.anchor7_randn_b`, `fp32.exp_b_alt_b26`, `int8.b_line_7f_80_aconst`, `int8.bheld_33`, `int8.bheld_bit1`),
  four anchors 11 of their 12 runs, and every other tile four. The rule is E78's, registered with the frame; no run was retried.
- **Every device-management command sent was a read** (§ Device commands sent).
- E170 ran on card 0 of this host after this session had ended (16:19:41-16:48:53 PST,
  [`../2026-11-04-e170-blind7-card0/`](../2026-11-04-e170-blind7-card0/README.md)).

## Results

**In plain words.** A designer who never saw the model wrote 61 new tiles; M9, frozen before them, predicted each one's power and its
4.5 s die rise on this card through M8's kept card term (0.9616 of aifoundry3's). Over the 48 priority-1 kinds M9's error is 0.273 W rms
(E163 on aifoundry3: 0.278 W), better than M8 by a resolved margin, but on this card M6 sits within the noise of M9 (M1 not resolved) and
is resolved better than M9 on the 12 kinds aimed at nothing. As on aifoundry3, the floats read higher than M9 predicts (+0.16 W), but here
int8 reads lower (−0.08 W): card 1's int8 runs at 0.942 of aifoundry3's, not the 0.962 M9 carries, and a short run of random anchors finds
that scale (rank 4 PASS). The single high B bits are again the largest miss, and the die rose more per board watt than M9 carries for this
card, so int8's heat misses its rule.

**The registered verdicts** ([`results.md`](results.md), [`scored.json`](scored.json) › `verdicts`; the scorer `score_e164.py` as frozen in
`f4e75c95`, on Q139(u)'s footing, card 1's leakage 0.3134106532552718 W/°C, E82 A2's dips removed once; E164-RANK1 by
[`rank1_e164.py`](../../../../tools/claims-v3/e164/rank1_e164.py) → [`rank1-e164.json`](rank1-e164.json); RK4 by Q140(x)'s
`score_rank4.py`, unchanged):

| rule | reading | interval (registered draws) | verdict |
|---|---|---|---|
| E164-P1 (fp32 power, 17) | rms 0.376 W | [0.114, 0.328] | **FAIL** |
| E164-P2 (fp16 power, 9) | rms 0.175 W | [0.088, 0.291] | PASS |
| E164-P3 (int8 power, 22) | rms 0.200 W | [0.131, 0.235] | PASS |
| E164-B1 (floats bias, 26) | mean(measured − M9) +0.164 W | [−0.085, +0.068] | **FAIL LOW** (M9 predicts too little) |
| E164-B2 (int8 bias, 22) | −0.076 W | [−0.071, +0.084] | **FAIL HIGH** (M9 predicts too much) |
| E164-C1 (coverage, 48) | 41 of 48 inside M9's 95% bands | low end 42 | **FAIL** (outside: five fp32 single-high-bit tiles, `int8.bheld_01`, `int8.bheld_ff`) |
| **E164-M1** (M9 − M6, 48) | **−0.048 W** | **[−0.111, +0.013]** | **NOT RESOLVED** |
| E164-M2 (M9 − M8, 48) | −0.118 W | [−0.196, −0.039] | BETTER |
| E164-U1 (M9 − M6 on the 12 unaimed) | +0.078 W | [+0.033, +0.111] | **FAIL** (M9 resolved worse; U17 beside +0.074 [+0.034, +0.104]) |
| E164-H1 / H2 / H3 (4.5 s rise) | rms 0.334 / 0.352 / 0.212 °C | [0.239, 0.473] / [0.195, 0.518] / [0.101, 0.185] | PASS / PASS / **FAIL** |
| E164-H4 (heat coverage) | 44 of 48 inside | low end 42 | PASS |
| E164-R1 (10 real tiles) | rms 0.171 W | [0.111, 0.371] | PASS |
| E164-R2 (10 real tiles inside) | 10 of 10 | — | PASS |
| E164-X1 (card term, floats, 28 tiles) | median D(card 1) / D(aifoundry3) 0.9621 | [0.9603, 0.9651] | PASS (holds M9's 0.9616; M7's and M6's 0.9711 outside) |
| E164-X2 (card term, int8, 24 tiles) | 0.9418 | [0.9367, 0.9467] | **FAIL** (M9's 0.9616 and M7's 0.9735 outside) |
| **RK4** (rank 4, the E163 / E164 pair) | floats s_anchor 0.9628 vs s_pool 0.9621, offset +0.07%; int8 0.9368 vs 0.9418, −0.54% | lines ±1% / ±2% | **PASS** (both families) |
| E164-PC / K7C / PCa (the C check) | 2,550 / 316 / 920 launches, all PASS | — | PASS / PASS / PASS |
| E164-K7D (8 repeat tiles, flat 0.05 W) | 2 of 8 within 0.05 W after the anchor scale | — | **FAIL** |
| E164-K7W (Welch) | 8 of 8 inside | half-widths 0.19-0.31 W floats, 0.22-0.33 W int8 | PASS |
| E164-K7 / K7′ | K7C and K7D / K7C and K7W | — | **FAIL** / PASS |
| **E164-RANK1** | M1 NOT RESOLVED, **U1 FAIL, B1 FAIL LOW, B2 FAIL HIGH, C1 FAIL** | needs M1 BETTER and the four PASS | **FAIL** |

**Rank 1 on both 600 MHz cards does not hold:** E163-RANK1 FAIL (on B1 / B2) and E164-RANK1 FAIL (on M1, U1, B1, B2 and C1).

**Against the registered forecast** (E164.md § What I expect, "frozen so it can be wrong"): P2 and P3 PASS, P1 FAIL (allowed), R1 and R2
PASS, PC, K7C and PCa PASS, M1 NOT RESOLVED, M2 BETTER, RK4 PASS on both families, K7D FAIL and K7W PASS, **as forecast**; **B1 read FAIL
LOW where PASS or FAIL HIGH was forecast; B2 FAIL HIGH, C1 FAIL, U1 FAIL, H3 FAIL and X2 FAIL where PASS was forecast.**

**Each model on the same 48 priority-1 kinds** (`results.md`, reported):

| model | fp32 rms | fp16 rms | int8 rms | rms (48) | bias (48) | real tiles rms | inside 95% | heat rms fp32 / fp16 / int8 (°C) |
|---|---|---|---|---|---|---|---|---|
| **M9** | 0.376 | 0.175 | 0.200 | **0.273** | +0.054 | 0.171 | 41 of 48 | 0.334 / 0.352 / 0.212 |
| M8 | 0.361 | 0.160 | 0.470 | 0.390 | +0.140 | 0.171 | 42 of 48 | 0.336 / 0.350 / 0.239 |
| M7 | 0.307 | 0.134 | 0.401 | 0.332 | +0.002 | 0.136 | 45 of 48 | 0.323 / 0.338 / 0.220 |
| M6 | 0.332 | 0.127 | 0.365 | 0.321 | +0.008 | 0.131 | 42 of 48 | 0.319 / 0.330 / 0.211 |

Beside (reported, never a verdict): M9 − M7 over the 48, −0.060 W [−0.145, +0.032], not resolved; M9 − M6 over all 52 non-anchor tiles,
−0.057 W [−0.117, +0.003], not resolved.

**By class** (priority 1, W; rms (bias), and the paired M9 − M6):

| class | n | M9 | M8 | M7 | M6 | M9 − M6 |
|---|---|---|---|---|---|---|
| S (single high bits) | 7 | 0.543 (+0.292) | 0.489 (+0.237) | 0.459 (+0.141) | 0.495 (+0.212) | +0.048 [−0.002, +0.089] |
| E (exponent-heavy) | 6 | 0.164 (+0.059) | 0.218 (+0.158) | 0.135 (+0.022) | 0.158 (+0.056) | +0.006 [−0.009, +0.053] |
| L (whole-line int8) | 7 | 0.154 (−0.008) | 0.564 (+0.492) | 0.269 (+0.191) | 0.266 (−0.029) | **−0.112 [−0.202, −0.031]** |
| H (int8, B held) | 6 | 0.321 (−0.183) | 0.654 (−0.204) | 0.699 (−0.414) | 0.626 (−0.202) | **−0.305 [−0.401, −0.200]** |
| U (aimed at nothing) | 12 | 0.148 (+0.087) | 0.148 (+0.093) | 0.090 (+0.007) | 0.070 (−0.004) | **+0.078 [+0.034, +0.113]** |
| R (real tiles) | 10 | 0.171 (+0.029) | 0.171 (+0.077) | 0.136 (+0.006) | 0.131 (+0.003) | +0.040 [−0.020, +0.093] |

**What carries the misses.**
- **P1, C1 and class S: the single high B bits.** `fp32.b_onebit_b20_seventh` +0.691 W, `_full` +0.687, `fp32.b_onebit_b22_third`
  +0.625, `fp32.b_onebit_b20_one` −0.612 and `_pi` +0.452 W are five of C1's seven tiles outside M9's bands; the other two are int8 with B
  held, `int8.bheld_01` −0.651 W and `int8.bheld_ff` −0.400 W. The byte twin `fp32.b_onebit_b20_pi` (= `fp32.cal_pi_b20`) read +0.452 W
  against the counting-only expectation of +0.311 ± 0.198 W (reported, `scored.json` › `primary.reported_byte_twin_A1_2`). **Q141(t)'s
  27-point arm** (reported, `primary.reported_s_recount_arm`): over its 8 tiles the rms is 0.509 W with the three-point counts and **0.313 W
  with 27 points**.
- **B1: the floats sit above M9, as on aifoundry3.** The full-density random float tiles read above M9, fp32's four by +0.26 to +0.31 W
  (`fp32.anchor7_randn_b` +0.313, `fp32.laplace_both` +0.288, `fp32.anchor7_randn_a` +0.266, `fp32.uniform_pm1` +0.261 W) and fp16's five by
  +0.08 to +0.20 W, and so do the fp32 real tiles (+0.145 to +0.389 W). E163 read the same sign and size on aifoundry3 (+0.151 W), so the
  excess is not card 1's alone.
- **U1 is B1 on the unaimed kinds.** On the 8 float U tiles M9 reads +0.146 W low (rms 0.171 W) where M6 is on the mark (−0.002 W, rms
  0.081 W); on the 4 int8 U tiles both are close (M9 −0.032, M6 −0.008 W) ([`posthoc/readings_e164.txt`](posthoc/readings_e164.txt), a
  post hoc split of `scored.json`). Over the 12, M6 0.070 W rms (bias −0.004) against M9's 0.148 (+0.087).
- **B2 and X2: card 1's int8 scale.** The int8 tiles read below M9 (the anchors −0.15 to −0.18 W, `int8.b_line_7f_80_aconst` −0.271 W):
  card 1's int8 D is **0.9418** of aifoundry3's today (24 tiles), where M9 carries M8's 0.9616 for every format (E157 read 0.9681 [0.9534,
  0.9783] on pool 6). The floats' ratio holds (0.9621). **Rank 4's anchors catch it:** the two int8 random anchors give 0.9368, −0.54% from
  the pool's 0.9418, inside the 2% line; the int8 difference's standard error from the passes is 0.51% (the registered forecast 1.35-1.64%,
  Q140's critic's planning estimate 0.95%), so four passes with the int8 anchors three times a pass did what the design asked.
- **H3: the die rose more per watt than M9 carries.** Measured over the 52 non-anchor tiles, card 1's 4.5 s rise is **0.131 °C per board W**
  against the 0.1151 °C/W M9 carries for this card (`primary.reported_rise_per_board_w`); the floats' heat reads +0.26 °C above M9 at the
  measured run length (int8 +0.04 °C, coverage 47 of 48; `primary.reported_heat_at_measured_run_length`). E157's heat on pool 6 here was
  0.180 / 0.183 / 0.123 °C rms.
- **The arms** (reported, never the verdict): with the session's own leakage and with the anchor gates relaxed every rule reads as the
  primary; with the dips kept (E78's pass gate then sets 16410 aside on `fp32.randn`'s 2.26 W span) P1, B1, U1 pass and P2, P3, R2 fail; at
  leakage 0.2955 W/°C B2 passes and X1 and R2 fail; at 0.3320 W/°C C1 and U1 pass (`results.md`, the arm lines).

**Rank 7's repeat** (one new session of the two rank 7 asks; E164-A1 A1-1's reading, registered before the data). After the per-session
anchor scale (floats 0.9981 ± 0.0024, int8 1.0050 ± 0.0128), the four float tiles repeated E157 by −0.015 to +0.075 W and the four int8
tiles by −0.075 to +0.116 W. **K7W PASS: every tile inside its Welch half-width, 0.19-0.31 W on the floats and 0.22-0.33 W on int8**,
wider than A1-1's planned ±0.09-0.16 / ±0.25-0.29 W, so this session bounds card 1's day-to-day change only to those widths. **K7D FAIL**
(2 of 8 within 0.05 W); by A1-1, a K7D FAIL alone is no evidence that card 1 changed (with nothing changed it fails 83% of the time). Rank
7 still needs a second new card-1 session; this one cannot resolve a 0.1-0.2 W floor on int8.

**Q141(t)'s 27-point arm across both cards** (`score_s7arm_a1.py`, A1, run on E163's committed `scored.json` and this directory's:
[`score-s7arm-a1.txt`](score-s7arm-a1.txt), [`score-s7arm-a1.json`](score-s7arm-a1.json); reported only, no verdict on M9). Over the 7
priority-1 S tiles: card 1 r3 0.543 → r27 **0.318 W** rms (d −0.225 [−0.341, −0.123], counting share +0.66); aifoundry3 0.577 → 0.396 W
(d −0.181 [−0.280, −0.091], +0.53); pooled 0.560 → 0.359 W (d −0.201 [−0.295, −0.113], +0.59). R4 not separated on either card; R5 (the
four bit-20 base words) reads a base-word price on both (χ² 20.4 and 23.7 on 3 df); R5m, with M9's ordinary error added, reads it on
aifoundry3 (p 0.023) and not on card 1 (p 0.079). The 27-point counts move the 4.5 s heat by about 0.02 °C rms only (card 1 0.330 → 0.307
°C). So the 27-point counts remove 53-66% of the S class's power rms (the scorer's counting share, 1 − r27 / r3), and R5 still reads a
base-word price.

## What it does to predicting power and heat

- **The term tested:** M9's whole 600 MHz power model (Q140(m), frozen in `1f244140`) and its bands on 48 kinds written by an independent
  designer, carried to the second 600 MHz card by M8's kept card term (0.9616), with M7's heat law at card 1's 0.1151 °C/W for the 4.5 s
  rise; the card term itself (X1 / X2); a card's scale from its random anchors (RK4); card 1's day-to-day repeat (K7).
- **Before:** M9's nested leave-one-kind-out error on card 1's rows, 0.211 / 0.178 / 0.185 W (fp32 / fp16 / int8); the blind record on this
  card, M8 on pool 6 (E157), 0.386 / 0.098 / 0.327 W, M6 0.283 W over 30 kinds; heat 0.180 / 0.183 / 0.123 °C; the blind record of a new
  kind's 600 MHz power, 0.24-0.32 W rms per card; the 4.5 s rise, 0.10-0.18 °C.
- **After (blind, this session):** M9 **0.376 / 0.175 / 0.200 W** (0.273 W over the 48, +0.054 W bias), resolved better than M8 (−0.118 W),
  not resolved against M6 (−0.048 W) or M7; heat **0.334 / 0.352 / 0.212 °C**, above the record. On the blind record (different pools and
  models), int8's error on this card fell from 0.327 W (M8, pool 6) to 0.200 W (M9, pool 7); fp32's stayed at about 0.38 W, carried by the
  single high bits and the floats' level.
- **What it says to change:** (1) **the card term should be read per family from the session's random anchors**, as rank 4's rule does: the
  frozen 0.9616 holds for floats and is 2% high for int8 today, and the anchors find both scales, to +0.07% and −0.54%; (2) a level term for the
  floats (both 600 MHz cards read about +0.15-0.16 W today); (3) the single-high-bit counts (27 points take the S class from 0.54 to 0.32 W rms
  here, reported); (4) card 1's heat per board W (0.131 measured against 0.115 °C/W carried). **Nothing frozen changes here.**

## Registered before any data, and what the box ran

- **Frozen first:** blind pool 7 with M9's, M8's, M7's and M6's card-1 predictions
  ([`predictions-blind7-aifoundry1c1.json`](../../../../tools/claims-v3/kinds/blind7/predictions-blind7-aifoundry1c1.json)), Q140(x)
  `75802201` (03:27:39 PST) and its notes `3c9bb2ba` (04:18:24); M9 `1f244140` (01:12:04), registration `8dfafae3` (00:45:51). Q141(t)'s
  reported arm M9_27pt, `67d5e44f` (10:07:40), and its amendment A1, `c31e7ae3` (12:16:56). Nothing was fitted here.
- **Registered** (Q141(b)), every commit before any E164 data, claim or launch: [`E164.md`](../../../../tools/claims-v3/e164/E164.md) and
  rank 7's pick, `4286f0a8` (09:18:57 PST); M9's card-1 reference errors, the machine freeze, the scorer and its reproduction of E157,
  `f4e75c95` (09:41:51); the run kit, `ce10e301` (10:05:44); amendment E164-A1 ([`E164.md.dated-note.md`](../../../../tools/claims-v3/e164/E164.md.dated-note.md):
  K7W's planned width, who blocks, every gate that differs from E163's, **E164-RANK1**), the README's dated note (`box/launch_e164_a1.sh`,
  `collect_e164_a1.sh` and its scrub), `45aeda12` (11:41:49). Q141(f), the readiness critic, re-ran the notes' self-test (53 of 53) and the
  Intel dry pass before his go.
- **The box steps** (Q141(k)'s runbook `e962227a`, each call after a 15 s probe and under its bound; the card lane's own log): the look
  14:18:07-09 PST (the host booted 2026-10-26 15:02:04, before E82's firmware read of 2026-10-31 13:45:24 PDT, so nothing can have
  flashed the card since; et-who "No process holds an ET-SoC-1 device node or card lock."; the binaries `e0fbecce…`, `8008f96f…`,
  `990807f4…`, `4f0956ce…` equal to E157's pins); the sync 14:18:17-19 (`tools/claims-v3/e164/` and pool 7 into `~/nekko`); the check
  on the box 14:18:24-52 (`check_e164.py` **HARNESS OK, 107 files**; `preflight_e164.sh` **GO, 32 send sites, 0 disallowed**; the tiles
  OK; pool 7's SHA256SUMS **91 OK**; the dry pass of 16410, rc 0, 98 device calls listed; the dry smoke rc 0; the dry stop-path test
  rc 1, as a dry run ends); the look again at 14:19:24-25; **the launch 14:19:33-42** with
  `ssh … aifoundry1 "bash -s -- '2026-11-04 18:50 PST'" < tools/claims-v3/e164/box/launch_e164_a1.sh` (never `box/launch_e164.sh`): the
  deadline 18:50:00 PST, "4 of the 4 planned", the holders at launch all 0 on both cards
  ([`logs/holders-at-launch.txt`](logs/holders-at-launch.txt)).

## Registered against what happened

| | registered | happened |
|---|---|---|
| order | the registration (`4286f0a8`), the freeze and scorer (`f4e75c95`), the kit (`ce10e301`) and E164-A1 (`45aeda12`) before the claim and the first launch, each descending from the frozen pool (`75802201`, `3c9bb2ba`) and M9 (`1f244140`, `8dfafae3`) | all ancestors of the lab's main at the launch (`5e1bb309`); the claim 14:11:27 PST; `E164_T0`, the session's first device access, 14:19:34, the opening config read 14:19:35 |
| design | four passes of 96 runs as the budget allows (E164_DROP_P2=0), at least two kept; a fifth does not fit | four passes ran, the budget rule stopped before 16414; all four kept; nine runs skipped by E78's launch rule (above) |
| card time | the cap 65 card-minutes; no session after 18:15, every run ends by 19:00 PST (E164_DEADLINE 18:50) | **58.3 card-minutes** (14:19:34-15:17:53 PST), 0.1 above the plan's 56.7-58.2 |
| stop-path test 16402 | the guard's die stop at 1.0 °C, its board stop at 1.0 W and the watcher's board stop at 1.0 W each end the runner with EXIT_HOT on a live sample, no launch | **PASS** (rc 0): the die stop on the hottest minion-shire reading 65.0 °C, read 0.042 s after its sample; the board stop on 30.56 W at 0.044 s; the watcher on 30.56 W at 0.08 s; each `run_e164` exit 6 ([`logs/session.log`](logs/session.log)) |
| smoke 16401 | the gate (`smoke_gate_e164.py`) | **PASS** (`SMOKE-GATE PASS {'bad': []}`, 14:20:35): 11 items × 5 launch records, 546.001 / 318.0 cycles per op, 0.5992-0.5995 GHz, every dump equal to its sha256, config 65 / 65 / 600 at both ends, 432 samples, board 30.42-58.41 W, `since_reset_ms` −1, 66 C records for 66 launches |
| stops | board ≥ 66 W or any `temp_c.minshire` field ≥ 72 °C, live, main path and in-run watcher | highest 61.20 W and 63 °C live; no stop fired |
| the C check | every launch, bit-exact | 3,896 of 3,896 PASS; no tile left out |
| departures | — | **D1, the collection route** (dated here, Wed 4 Nov 2026, before the registered reduction ran): the card lane made a copy-only pull (the runbook's `s22_collect.sh e164` would also have collected), into `build/e164-raw/` on the Intel, every per-directory digest equal to the box's (read 15:18 PST); the registered collector `collect_e164_a1.sh` was then run over that copy, as the kit README's dated note, step 7, gives, with `E164_S_RECOUNT` naming Q141(t)'s card-1 arm (Q141(f)'s F2) and E163's committed `e163.json` and `scored.json` (byte for byte `build/e163-out`'s; E163's C check excluded no tile, so the drop list is empty). The reduction records the passes as given, `build/e164-raw/e164/p164<nn>` (repo-relative, as E157's `build/e157-raw/…`). This directory is that collector's output (`build/e164-out/2026-11-04-e164-blind7-card1/`), copied unchanged but for `ccheck/ccheck-session.json`, gzipped as E157's; the go checklist's two pair scorers were run beside it (§ Files). No other departure. |

## Device commands sent

As registered ([`E164.md`](../../../../tools/claims-v3/e164/E164.md) § Device commands sent): E157's sending code on this card, unchanged
(`lib.sh`, the same `ettelem` binary through E128's guard, the block's config reads and its one `start_sampler` call). `ettelem config` at
the session's start (14:19:35 PST) and end (15:17:53), and at both ends of the stop-path test, the smoke and every pass; `ettelem sample`
at 10 Hz in every block. Sent: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**, GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, **GET_MODULE_VOLTAGE**: **all
READs**, classified from et-platform `836a4ab` (BL2 0.22.0), the build card 1 has reported since E82's read (identity by the host's boot
time, as registered); the two in bold are PMIC voltage-register reads, which the owner's rule of 2 November 2026 allows. **Never sent**:
the statistics reset (`since_reset_ms` −1 in every one of the session's 34,396 samples), any SET_*, the firmware-revisions query, any
residency read, any governor, TDP, threshold or clock set, any reset, and `dev_mngt_service`. The checker (`dmcmd_audit.py`, unchanged),
run by the session on the box before any device opened: **GO**, 32 send sites, 0 disallowed, with the one reviewed exception (`lib.sh:154`,
the conditional `--reset-ms` forward that `block_e164.sh` never uses) ([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt)).

## Card and post

`et-who` at the look-first reads (14:18:07 and 14:19:24 PST), at the session's start (14:19:34) and at its end (15:17:53): no process held
a device node or card lock on either card; idle logins of other accounts were present, which do not block (the owner's ruling of 1 November
2026), and none held a node or a lock. The collector's scrub (`scrub_etwho_e164.py`: 0 files rewritten) and its `--check`, run again on
`logs/` and on this whole directory, leave no other account's login in any file (0 left); [`logs/et-who-summary.txt`](logs/et-who-summary.txt)
counts the session's two et-who readings by card, without names: no holder on either card. E170 ran on card 0 of this host after this
session had ended: never two sessions of ours on aifoundry1 at once.

Wed 4 Nov's one `#community-lab` post is message `1567662592850399304`, created at 14:11:27 PST by the card half's claim. aifoundry1's clause,
`using aifoundry1 for 3 h, until ~17:11 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, covered both cards of
this host (card 1's E164, then card 0's E170). E164's lane did not edit it: E164 ended at 15:17:53, inside the clause's ~17:11, and the
clause stayed for E170; E170's lane dropped it at 16:50:09-15 PST, after E170's end, under the Discord lock with `EXPECT_TEXT`, leaving
aifoundry2's clause.

## How to reproduce

```bash
# from the lab clone, over the raw copy (build/e164-raw: aifoundry1:nekko/build/claims-v3/aifoundry1-c1/e164{,-smoke,-stoptest}/ and
# nekko/build/e164/ as logs/; this directory's aifoundry1-c1/ and logs/ hold the same files)
PY=/usr/bin/python3 PYS=python3 E164_DATE=2026-11-04 \
  E164_S_RECOUNT=docs/reports/data/2026-11-04-q141t-s7-recount/arm/arm27-aifoundry1c1.json \
  nice -n 10 bash tools/claims-v3/e164/collect_e164_a1.sh build/e164-raw \
  docs/reports/data/2026-11-04-e163-blind7-aifoundry3/e163.json "" docs/reports/data/2026-11-04-e163-blind7-aifoundry3/scored.json
# (PY: Python 3.9.6 with numpy 1.26.4; PYS: Python 3.12 or later, here 3.13.11; it writes build/e164-out/2026-11-04-e164-blind7-card1/)
python3 -B tools/claims-v3/kinds/blind7/score_rank4.py --a3 docs/reports/data/2026-11-04-e163-blind7-aifoundry3/scored.json \
  --c1 docs/reports/data/2026-11-04-e164-blind7-card1/scored.json --pair E163/E164
/usr/bin/python3 -B docs/reports/data/2026-11-04-q141t-s7-recount/score_s7arm_a1.py \
  --a3 docs/reports/data/2026-11-04-e163-blind7-aifoundry3/scored.json --c1 docs/reports/data/2026-11-04-e164-blind7-card1/scored.json
```

Collected and scored on the Intel at `nice -n 10`, 17:04:25-17:14:34 PST, the C check at 2 jobs and the scorers single-threaded.

## Files

| file | what |
|---|---|
| `scored.json`, `results.md` | the registered scorer's output on the registered primary (Q139(u)'s footing), every arm beside, X1 / X2 with E163's reduction, K7, Q141(t)'s card-1 arm (`primary.reported_s_recount_arm`) |
| `rank1-e164.json` | E164-RANK1 (`rank1_e164.py`, E164-A1 A1-3) |
| `rank4-e163-e164.json`, `.txt`, `rank4.log` | rank 4's pair score through `pair_rank4_e164.py` (Q140(x)'s `score_rank4.py`, pinned), with the int8 difference's standard error beside |
| `rank4-direct.json`, `.txt` | the same rule run directly with `score_rank4.py --pair E163/E164` (the go checklist's line): the same verdicts and numbers |
| `score-s7arm-a1.json`, `.txt` | Q141(t)'s arm read on both cards with amendment A1's wrapper (reported only) |
| `e164.json`, `runs.csv`, `reduce.txt`, `reduce.log` | the registered primary reduction of the four passes |
| `e164-auto.json`, `e164-dipskept.json`, `e164-leak0.2955.json`, `e164-leak0.3320.json`, `e164-relaxed.json` (with their `runs-*.csv`, `reduce-*.txt`, `reduce-*.log`) | the arms |
| `ccheck/` | `ccheck.py`'s output over every pass and the smoke (`ccheck-session.json.gz`, `ccheck-session.txt`) |
| `aifoundry1-c1/e164/p16410`-`p16413` | the passes as the box wrote them (`telemetry.jsonl.gz`, `runs.jsonl`, `run.log`, `block.json`, the config reads, `c-log.jsonl.gz`, the tiles, …) |
| `aifoundry1-c1/e164-smoke-p16401`, `aifoundry1-c1/e164-stoptest-p16402` | the smoke and the stop-path test |
| `logs/` | the box's `build/e164/` (`session.log`, `session.out`, `queue.out`, `T0`, the session's config reads, `holders-at-launch.txt`, the device-command preflight, `binaries.sha256`) and the scrub's `et-who-summary.txt` |
| `code.sha256`, `score.log` | the code the collector ran, hashed; the scorer's log |
| `posthoc/readings_e164.py` → `posthoc/readings_e164.txt` | post hoc, never a verdict: E164-U1's tiles split by family, and the nine runs E78's launch rule skipped |

SPDX-License-Identifier: Apache-2.0
