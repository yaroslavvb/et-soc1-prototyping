# E141: M7 against blind pool 5 on aifoundry3 card 0 - heat holds and M7's power bands cover 28 of 30, but the floats read 0.23 W too high (B1 FAIL HIGH) and fp16 misses its rms rule (P2 FAIL) on the registered primary

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
item 6, "a power model across kinds", tested out of sample on a fifth pool written by someone else, on the card M7's power has no card term
for. Mon 2 Nov 2026 (week 45), Q138. Pre-registered in `87a64409` (committed 21:21:27, pushed by 21:21:30 PST), before the claim and before
any card ran a tile of pool 5 on aifoundry3: [`tools/claims-v3/e141/README.md`](../../../../tools/claims-v3/e141/README.md). The model is
Q138(m)'s M7, frozen in `3a210f2b` (19:21 PST); the pool, [blind pool 5](../../../../tools/claims-v3/kinds/blind5/README.md), 36 tiles by an
independent designer, and M7's, M6's and M5's frozen predictions for this card, in `dac39d97` (20:24:02 PST), an ancestor of `87a64409`
(checked: `logs/push-and-claim-times.txt`). aifoundry3 card 0 at 600 MHz in every sample; `ettelem config` read at the session's start
(21:23:33), at both ends of the stop-path test, the smoke and every pass, and at the session's end (22:04:32): TDP 0 W, threshold 65 °C,
max_power, 600 MHz, 522–523 mV, never set. **Every device-management command sent was a read** (nine kinds, two of them PMIC voltage-register
reads, which the owner's rule of 2 November 2026 allows; `since_reset_ms` −1 in all 24,014 samples). Card session 21:23:33–22:04:32 PST,
**41.0 of the 50 card-minutes allowed**: the stop-path test 14102, the smoke 14101 and four passes, 14110–14113 (574–623 s each); the budget
rule stopped before 14114.*

*Corrected after verification (a dated note, Mon 2 Nov 2026, about 23:10 PST; desk only: no card opened, no device command, no pass
re-run). An independent verifier re-derived every registered number and verdict from the committed raw passes, and confirmed that every
command sent was a read and that the blind order held. It found six faults. None changes a measured number, a rule, a prediction or a
registered verdict, and none is an unsafe or disallowed command. Each is corrected by a dated note beside the text it concerns, the frozen
text left as it was, and set out in full in [§ Corrections after verification](#corrections-after-verification-mon-2-nov-2026) at the end.
The numbers they quote are printed by [`corrections-numbers.py`](corrections-numbers.py) → [`corrections-numbers.txt`](corrections-numbers.txt);
the post hoc reductions are in [`posthoc-after-verification/`](posthoc-after-verification/README.md). **The main one, C1:** the floats'
−0.23 W bias (B1 FAIL HIGH) and fp16's excess (P2 FAIL) are read on this session's own leakage fit, 0.263 W/°C, while M7's aifoundry3
training rows were reduced on a mixed footing: their sessions' slopes average 0.210–0.222 W/°C, 80 of the 247 float rows sit at a fixed
0.1994, and 93 had the meter's dips removed. Read post hoc on that footing, the floats' bias is between +0.001 W (dips removed) and
−0.133 W (dips kept), so the registered FAILs follow the reduction's footing; E141 does not measure a float offset in M7, and cannot
exclude one of up to about −0.13 W. The "0.23 W too high" of the title and of "In plain words" is the registered reading on this session's
footing, not a model offset. The registration ([`tools/claims-v3/e141/`](../../../../tools/claims-v3/e141/README.md), `87a64409`) is frozen
and unchanged.*

**In plain words.** M7 is the lab's power-and-heat model: from the bytes a matmul multiplies it predicts the watts the chip draws over the
same kernel on zeros, and how far the die warms in a 4.5 s run. E141 ran 36 new kinds of numbers, written by someone who never saw the
model, on the card M7's power numbers are written for. **Heat holds again**: the die's rise is predicted to 0.13 °C rms in every format and
all 30 tiles land inside M7's 95% bands (H1–H4 PASS). **Power's bands now hold**: 28 of 30 tiles land inside M7's bands (C1 PASS), where the
older models' bands held 22 (M6) and 19 (M5) of the same 30. **But M7 still predicts the floats about 0.23 W too high** (B1 FAIL HIGH: the
same direction as M6's −0.28 W on pool 4), and on fp16 its error, 0.32 W rms, is about twice what its nested score claims (P2 FAIL). With the
board meter's dips removed, a reported arm, fp16 passes (0.20 W) and the float bias shrinks to −0.15 W but still fails. M7 is not told apart
from M6 or M5 on these tiles (M1, M2 NOT RESOLVED).

*Note after verification (C1, C2, C3; Mon 2 Nov 2026). Of the 36 tiles, 30 are new kinds and 6 are the pool's anchors: three of those are
byte-identical to E78's own zeros tiles, which M7 was fitted on, and the other three are fresh draws of the random and full kinds it was
fitted on. "M7 still predicts the floats about 0.23 W too high" is the registered reading on this session's leakage fit; on the footing M7's
training rows were reduced on, the floats read between +0.00 and −0.13 W (C1), so E141 does not show that M7 itself runs high. "Power's
bands now hold" is calibration, not accuracy: M7's float bands are 1.6 times M6's, with the same errors (C3).*

## Results

**Three of four passes kept on the registered primary** (E140's frame: E78's reduction unchanged, leakage `auto` (0.263 W/°C, fitted on
this session's 165 runs), dips kept, E78's run and pass gates): 14111, 14112, 14113. **14110 was set aside by E78's registered random-range
gate** (`fp32.randn` spans 1.704 W, over the 1.0 W line), a reading of the size the board meter's dips make (E82 A2; E140's D1 was the same);
the dips-removed arm keeps all four passes. Every tile has at least two kept passes (`fp16.exp_only` two: E78's runner skipped it once, D2),
so every rule is scored ([`results.md`](results.md), [`scored.json`](scored.json)).

**1. The registered verdicts** (primary; the arms are reported, never the verdict).

| rule | quantity | set | reading | the nested score's interval | verdict | dips removed (4 passes) | leak 0.1994 | leak 0 | gates off (4) |
|---|---|---|---|---|---|---|---|---|---|
| **E141-P1** | power | priority-1 fp32 (9) | rms **0.325 W** | 0.087–0.545 | **PASS** | PASS 0.201 | PASS 0.260 | PASS 0.487 | PASS 0.342 |
| **E141-P2** | power | priority-1 fp16 (8) | rms **0.317 W** | 0.071–0.247 | **FAIL** | PASS 0.195 | PASS 0.233 | FAIL 0.463 | FAIL 0.278 |
| **E141-P3** | power | priority-1 int8 (7) | rms **0.356 W** | 0.093–0.361 | **PASS** | PASS 0.352 | PASS 0.342 | PASS 0.324 | PASS 0.349 |
| **E141-B1** | bias | priority-1 floats (17) | mean(measured − M7) **−0.230 W** | −0.117 to +0.085 | **FAIL HIGH** | FAIL HIGH −0.151 | PASS −0.082 | FAIL LOW +0.381 | FAIL HIGH −0.233 |
| **E141-B2** | bias | priority-1 int8 (7) | **−0.110 W** | −0.225 to +0.103 | **PASS** | PASS −0.126 | PASS −0.076 | PASS +0.031 | PASS −0.119 |
| **E141-C1** | power coverage | 30 non-anchor tiles | **28 of 30** inside | ≥ 26 | **PASS** | PASS 28 | PASS 30 | PASS 27 | PASS 28 |
| **E141-M1** | M7 against M6 | 24 priority-1 | rms(M7) − rms(M6) **−0.009 W** [−0.047, +0.024] | | **NOT RESOLVED** | NOT RESOLVED −0.007 | NOT RESOLVED | NOT RESOLVED | NOT RESOLVED |
| **E141-M2** | M7 against M5 | 24 priority-1 | **−0.040 W** [−0.091, +0.004] | | **NOT RESOLVED** | BETTER −0.049 [−0.106, −0.007] | NOT RESOLVED | NOT RESOLVED | BETTER −0.044 |
| **E141-H1** | die rise | priority-1 fp32 (9) | rms **0.128 °C** | 0.102–0.261 | **PASS** | PASS 0.087 | PASS | PASS | PASS 0.088 |
| **E141-H2** | die rise | priority-1 fp16 (8) | rms **0.129 °C** | 0.083–0.235 | **PASS** | PASS 0.126 | PASS | PASS | PASS 0.127 |
| **E141-H3** | die rise | priority-1 int8 (7) | rms **0.135 °C** | 0.095–0.309 | **PASS** | PASS 0.129 | PASS | PASS | PASS 0.129 |
| **E141-H4** | heat coverage | 30 non-anchor tiles | **30 of 30** inside | ≥ 26 | **PASS** | PASS 30 | PASS 30 | PASS 30 | PASS 30 |

At leakage 0.3803 W/°C (an arm) E78's zeros-line gate sets three passes aside and every rule is NOT SCORED. **Arm-sensitive**: P2 (passes
with dips removed and at 0.1994), B1 (passes at 0.1994, reverses at 0), M2 (BETTER with dips removed and with the gates off). Heat is not
arm-sensitive. Against both cards' reference rows (reported) P1–P3 read the same. **The frozen expectation** was P1–P3 PASS, B1 PASS or FAIL
HIGH, B2 and C1 PASS, M1 NOT RESOLVED, M2 NOT RESOLVED or BETTER, H1–H4 PASS: **P2 did not**; everything else fell as frozen.

**2. M7, M6 and M5 on the same tiles** (reported; measured − model, W; heat °C; primary unless marked):

| model | fp32 rms / bias | fp16 rms / bias | int8 rms / bias | all 30: rms / bias | inside its own 95% band | heat rms fp32 / fp16 / int8 |
|---|---|---|---|---|---|---|
| **M7** | 0.325 / −0.233 | 0.317 / −0.227 | 0.356 / −0.110 | 0.365 / −0.233 | **28 of 30** | 0.128 / 0.129 / 0.135 (30 of 30 inside) |
| M6 | 0.311 / −0.194 | 0.353 / −0.293 | 0.360 / −0.124 | 0.367 / −0.237 | 22 of 30 | 0.128 / 0.123 / 0.140 (30 of 30) |
| M5 | 0.375 / −0.256 | 0.359 / −0.150 | 0.382 / −0.154 | 0.408 / −0.244 | 19 of 30 | — (no heat term) |
| M7, dips removed | 0.201 / −0.163 | 0.195 / −0.137 | 0.352 / −0.126 | 0.266 / −0.164 | 28 of 30 | 0.087 / 0.126 / 0.129 |
| M6, dips removed | 0.158 / −0.124 | 0.249 / −0.203 | 0.358 / −0.140 | 0.266 / −0.168 | 26 of 30 | 0.088 / 0.120 / 0.135 |
| M5, dips removed | 0.269 / −0.186 | 0.256 / −0.060 | 0.380 / −0.170 | 0.315 / −0.175 | 23 of 30 | — |

The three models' power errors are close (their predictions differ by at most 0.6 W on this pool). **What changed with M7 is the band**:
rule B's half-width (k 3.179 floats, 2.483 int8, times the pool rms with the constants' covariance) covers 28 of 30 on the primary and on the
dips-removed arm, where M6's 1.96σ bands cover 22 and 26 and M5's 19 and 23.

*Note after verification (C3, Mon 2 Nov 2026): the coverage gain is the bands' width, not smaller errors. Over the 30 non-anchor tiles,
M7's mean 95% half-width is 0.81 W on fp32, 0.54 on fp16 and 0.60 on int8, against M6's 0.50, 0.34 and 0.52 and M5's 0.39, 0.34 and 0.47
(1.6 times M6's on the floats, 1.15 times on int8), while M7's and M6's errors are the same (rms 0.365 against 0.367 W, bias −0.233 against
−0.237). The largest error is 1.14 of M7's half-width, 1.61 of M6's and 2.20 of M5's. So M7's power bands are better calibrated, not more
accurate. Heat is the other way round: M7's float heat bands are narrower than M6's (0.34 against 0.58 °C mean half-width) and still hold
all 30 tiles, a sharper heat prediction (`corrections-numbers.txt` § C3, from `predictions-e141.json` › `tiles.*.D_95`, `dT_win_95`).*

**3. Where power misses** (measured − M7, W; per-pass D in `e141.json` › `per_pass`). The primary's largest misses, −0.52 to −0.75 W on
`fp32.lowrank2_w`, `fp32.block_sparse_k4`, `fp32.exp_only_both`, `fp16.real_pythia_qk` and `fp32.sorted_k`, are each one low pass of three:
`fp32.lowrank2_w` read 22.33 W in 14111 against 24.43 and 24.50, and 24.41–24.56 W in all four passes with dips removed (−0.04 W there). The
board meter's dips again (E140's C2). The misses that are steady on both arms:

| tile | case | M7 D, W [95%] | primary (passes) | dips removed | M6 / M5 (primary) |
|---|---|---|---|---|---|
| `int8.b_line_zero_one` | 6 whole-line flip-flops (named in advance) | 3.96 [3.35, 4.57] | **−0.61** (3.30, 3.41, 3.34) | −0.62, **outside** | −0.55 / −0.53 |
| `int8.powerlaw_w` | 8 seeded realistic weights (priority 2) | 6.38 [5.79, 6.96] | **−0.60, outside** | −0.59, **outside** | −0.63 / −0.61 |
| `fp16.real_pythia_softmax_v` | 5 real model | 17.35 [16.83, 17.88] | **−0.60, outside** | −0.41 | −0.53 / −0.59 |
| `fp32.wideexp48_bgate_kblk` | 2 spread exponents beside gated zeros (named) | 13.33 [12.54, 14.13] | −0.35 | −0.36 | −0.20 / −0.41 |
| `fp32.wideexp48_bgate_alt` | 2 (named) | 15.13 [14.30, 15.95] | −0.36 | −0.26 | −0.37 / **+0.19** |
| `int8.real_pythia_w8a8_down` | 5 real model | 6.19 [5.61, 6.77] | **+0.50** | +0.45 | +0.46 / +0.47 |

Every case's mean error is negative (M7 too high): seeded realistic weights −0.68 W (2 tiles), whole-line flip-flops −0.36 (3), exponent-only
activity −0.32 (3), structured streams −0.20 (8), fp16 pairs that cancel −0.17 (2), spread exponents beside gated zeros −0.16 (4), real model
tiles −0.14 (7), few mantissa bits −0.08 (1). **Where the models differ** (Q138(x)'s list): on `fp16.sparse24_aligned` M7 reads −0.07 W where
M6 reads −0.33; on `int8.b_line_flipflop_nogate` M7 −0.18 where M6 −0.45 and M5 −0.44; on `fp32.block_sparse_k4` M7 −0.61 where M6 −0.43;
on the wide-exponent gate tiles M5 differs (`fp32.wideexp48_bgate_alt` M5 +0.19 against M7 −0.36; `fp16.wideexp_bgate_alt` M5 +0.52 against
M7 −0.08).

**4. The float bias and the leakage slope.** B1's reading moves with the leakage slope the reduction subtracts: −0.230 W at the session's
own fitted 0.263 W/°C (the registered `auto`, the footing every M7 training session used with its own fit), −0.082 W at E78's 0.1994 (a
PASS), +0.381 W with none (FAIL LOW). A run warms the die about 0.12 °C per board W, so the slope takes about 0.12 × k of every watt: a change
of 0.064 W/°C moves a 20 W float tile by about 0.15 W (the arms move B1 by 0.148 W between 0.263 and 0.1994, and by 0.611 W between 0.263
and 0). The aifoundry3 sessions in M7's training rows that reduced with `auto` fitted between 0.140 (E92) and 0.296 W/°C (E95; E78 0.199,
E115 0.230, E140 0.286), a spread that moves this pool's float bias by about 0.35 W. So the −0.23 W (about 1.2% of the floats' D) is real on
the registered footing, in E140's direction, and of the size the session-to-session leakage fit makes; E141 alone cannot tell a model term
from that footing.

*Corrected after verification (C1, Mon 2 Nov 2026; post hoc, never a verdict). "The footing every M7 training session used with its own
fit" is wrong, and so is the registration's "That is the frame of M7's aifoundry3 training rows". Of M7's 247 aifoundry3 float training
rows, 80 (E121, E122, E123) were reduced at a fixed 0.1994 W/°C with the board meter's dips removed, 13 (E127) at their own fit with the
dips removed, and 154 at their sessions' own fits (0.140–0.296) with the dips kept. Their sessions' slopes average 0.210 W/°C counted by
rows, 0.216 weighted by each row's D and 0.222 weighted by D² (the weighting a common scale error carries), against this session's 0.263.
E141's four passes reduced again at those slopes by the frozen code
([`posthoc-after-verification/`](posthoc-after-verification/README.md)):*

| footing (post hoc except the first row) | B1 floats bias, W (line −0.117) | P2 fp16 rms, W (line 0.247) | P1 fp32 rms, W | C1 |
|---|---|---|---|---|
| registered primary: auto 0.263, dips kept | **−0.230 FAIL HIGH** | **0.317 FAIL** | 0.325 PASS | 28/30 |
| 0.210 / 0.216 / 0.222, dips kept | −0.107 PASS / −0.121 FAIL HIGH / −0.133 FAIL HIGH | 0.243 PASS / 0.249 FAIL / 0.255 FAIL | 0.266 / 0.271 / 0.275, PASS | 30/30 |
| 0.210 / 0.216 / 0.222, dips removed | +0.001 / −0.013 / −0.026, all PASS | 0.147 / 0.145 / 0.145, all PASS | 0.145 / 0.144 / 0.145, PASS | 30/30 |

*The slope gap alone accounts for 42–53% of the registered −0.230 W, and 89–100% once the dips are removed as 93 of the training rows had
them. A footing matched to the training rows lies between the table's last two rows: B1 between +0.00 and −0.13 W, at or inside its line,
and P2 between 0.145 and 0.255 W. So the registered B1 FAIL HIGH and P2 FAIL follow this session's own leakage fit against M7's training
footing: E141 does not measure a float offset in M7, and it cannot exclude one of up to about −0.13 W. The other blind tests read the same
way. E142 on card 1 reads +0.050 W (PASS) at its training-matched fixed 0.2414 W/°C and −0.354 W (FAIL HIGH) at its own fit, 0.408
([`../2026-11-02-e142-blind5-card1/scored.json`](../2026-11-02-e142-blind5-card1/scored.json) › `primary`, `arms.auto`). E140's −0.28 W on
pool 4 was read at its session's 0.286 W/°C: over its 25 rows the mean error is −0.275 W there and −0.124 W at 0.1994
([`../2026-11-02-e140-blind4/scored.json`](../2026-11-02-e140-blind4/scored.json) › `primary`, `arms.leak0.1994`). int8 does not move
with the footing (P3 0.337–0.356 W, B2 −0.08 to −0.13 W, PASS at every footing), and neither does heat. These readings were chosen after the
data: they correct the interpretation, never a verdict (`corrections-numbers.txt` § C1).*

**5. Heat** (measured − M7, °C): bias +0.004 (fp32), +0.110 (fp16), +0.032 (int8), rms 0.13 in each format, all 30 tiles inside M7's bands
and all six pool anchors inside too. **The rise against M7's 0.1186 °C per board W** (reported): a line through the origin of each tile's
mean `dT_win` on its mean S gives 0.1220 °C/W over the 30 tiles (+2.9%). At the measured run length (median T_run 4.49 s fp32 and fp16, 4.42
s int8, with M7's ST term, −0.0490 °C/W/s): rms 0.124 / 0.124 / 0.134 °C, 30 of 30 inside. M6's heat term, the same rule, reads the same.
The small int8 rises still land on whole degrees (`dT_win` exactly 1.0 °C on eight int8 tiles), the readout floor.

**6. What it does to predicting power and heat** (the before/after the owner's goal asks for; aifoundry3 card 0, 600 MHz):

| | before: M7's nested leave-one-kind-out score, aifoundry3 rows | after: blind pool 5, primary | dips removed (reported) |
|---|---:|---:|---:|
| power, fp32 | 0.247 W rms | **0.325 W** (bias −0.233) | 0.201 W (−0.163) |
| power, fp16 | 0.162 W | **0.317 W** (−0.227) | 0.195 W (−0.137) |
| power, int8 | 0.226 W | **0.356 W** (−0.110) | 0.352 W (−0.126) |
| power, 95% bands | 95% (rule B, calibrated, not tested) | **93% (28 of 30)** | 93% (28 of 30) |
| heat, fp32 / fp16 / int8 | 0.181 / 0.159 / 0.205 °C | **0.128 / 0.129 / 0.135 °C** | 0.087 / 0.126 / 0.129 °C |
| heat, 95% bands | 95% | **100% (30 of 30)** | 100% |

The blind record before this, on this card: M6 on pool 4 (E140) read 0.406 W (priority-1 floats) and 0.384 W (int8), biased −0.28 W, its
bands holding 19 of 25; heat 0.204 / 0.164 °C. So: **the heat term (0.1186 °C per board W over a 4.5 s run) can be quoted for new kinds on this
card**, with two blind pools and two models behind it. **M7's power bands can be quoted** (28 of 30, where M6's held 19 of 25 on pool 4 and 22
of 30 here). **M7's power point estimate cannot yet, as stated**: on new kinds it runs 1.3× (fp32), 2.0× (fp16) and 1.6× (int8) its nested rms
on the registered primary and reads the floats 0.23 W high; the meter's dips carry most of the fp32 and fp16 excess (0.201 and 0.195 W with
them removed: inside the rules' intervals, fp32 below its nested 0.247 W, fp16 still above its 0.162 W), not int8's, whose misses are steady.

*Note after verification (C1, C3; Mon 2 Nov 2026; post hoc). On M7's training footing with the dips removed, the floats read 0.144–0.145 W
rms on fp32 and 0.145–0.147 W on fp16, below their nested 0.247 and 0.162 W, with a bias of +0.00 to −0.03 W; with the dips kept, 0.266–0.275
and 0.243–0.255 W. So on the floats the excess over the nested score and the 0.23 W are the reduction's footing and the meter's dips, not
shown to be M7's. int8's 1.5–1.6 times its nested 0.226 W is steady at every footing (0.337–0.356 W; its three steady misses, result 3).
M7's 28 of 30 against M6's 22 is calibration: its float bands are 1.6 times M6's, with the same errors (C3).*

**The anchors** (reported, D in W): E78's anchors on the kept passes, `fp32.randn` 24.52, `fp16.randn` 21.91, `int8.full` 7.15, against
E140's 24.44, 21.85 and 7.01 on this card this afternoon; the pool's own random anchors inside M7's bands (fp32 +0.11, fp16 −0.04, int8
−0.00 W) and its zeros tiles within 0.03 W of E78's built-in zeros (fp32 +0.024, fp16 0.000, int8 −0.002 W).

## Registered against what happened

| | registered | happened |
|---|---|---|
| order | `dac39d97` before the registration; the registration before the claim and the first launch | `dac39d97` (20:24:02) an ancestor of `87a64409` (21:21:27, pushed by 21:21:30); claim saved 21:23:12; first device access 21:23:33 |
| passes | 14110–14113, 14114 if it fits (2,940 s from T0, before 23:40 PST); at least 2 kept | four ran (623, 574, 586, 582 s); the budget rule stopped before 14114 at T0+2459 s (projected end T0+3082 s); **three kept** (14111–14113) |
| card time | ≤ 50 min | **41.0 min** (21:23:33–22:04:32 PST) |
| stop-path test 14102 | die, board and watcher each end `run_e141.py` with EXIT_HOT on a live sample ≤ 2.0 s old, no launch | **PASS**: die on `minshire[0]` 50 °C read 0.081 s after the sample, board 23.31 W at 0.023 s, the watcher 23.38 W at 0.052 s; no launch record |
| smoke 14101 | the gate (`smoke_gate_e141.py`) | **PASS**: 546.001 / 318.0 cycles per op, 0.599–0.600 GHz, config 0 W / 65 °C / 600 MHz at both ends, every pool tile's dump equal to its sha256, 373 live samples, `since_reset_ms` −1, board 23.05–51.98 W |
| stops | board ≥ 65 W or `minshire[0]` ≥ 70 °C, live, main path and in-run watcher | highest board 55.33 W, highest `minshire[0]` 63 °C; no stop fired |
| expectation | P1–P3 PASS; B1 PASS or FAIL HIGH; B2, C1 PASS; M1 NOT RESOLVED; M2 NOT RESOLVED or BETTER; H1–H4 PASS | **P2 FAIL**; the rest as frozen (B1 FAIL HIGH) |
| departures | — | **D1**: E78's random-range gate set 14110 aside (as E140's D1); the dips-removed arm keeps it. **D2**: E78's runner skipped two runs by its own rule, "launch reading not reached" (`fp16.exp_only` in 14111, `int8.full` in 14112); `fp16.exp_only` keeps two passes on the primary. **D3**: the collector's Python was the Intel's `/usr/bin/python3` 3.9.6 with numpy 1.26.4. **D4**: a Tailscale check appeared at 22:05:48, after the session's end (22:04:32); the probe at 22:06:33 needed it and the one at 22:09:33 passed; nothing on the box waited. **D5**: a reduction of the three passes then on the Intel was read at about 22:07, after the queue had ended (no pass could be added); the registered numbers are the collect over all four passes from this directory, which reproduces it |

## Device commands sent

As registered ([`tools/claims-v3/e141/README.md`](../../../../tools/claims-v3/e141/README.md) § Device commands sent): E78's harness
unchanged, every telemetry call through E128's guard (`ettelem config` with no argument, `ettelem sample --seconds --every-ms` and nothing
else), `ettelem config` at the session's start, at both ends of the stop-path test, the smoke and every pass, and at the session's end,
`ettelem sample` at 10 Hz in every block. Sent: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**, GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, **GET_MODULE_VOLTAGE**: **all
READs**, classified from et-platform `836a4ab` (BL2 0.22.0), the two in bold PMIC voltage-register reads, which the owner's rule of 2 November
2026 allows. **Never sent**: the statistics reset (`SET_STATS_RUN_CONTROL`; `since_reset_ms` −1 in every one of the session's 24,014
samples), any SET_*, the firmware-revisions query, any residency read, any governor, TDP, threshold or clock set, any reset, and
`dev_mngt_service` (lib.sh's drain is replaced by a refusal; never needed). The host program (`sparsity_host`, `20e760c2…`) opens the ops node
only. The checker (`dmcmd_audit.py`, unchanged), run by the session on the box before any device opened: **GO**, 32 send sites, 0 disallowed,
with the one reviewed exception (`lib.sh:154`, the conditional `--reset-ms` forward that `block_e141.sh`'s only `start_sampler` call never
uses); NO-GO without it ([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt); the registration's `dmcmd-audit*.txt`). Residual, as
registered: aifoundry3's thermal firmware build is not public, so the classes rest on `836a4ab`'s handlers; the config reads and the telemetry
came back in the form E147 read on this card tonight (the smoke gate checks it).

*Added after verification (C5, Mon 2 Nov 2026): the host-binary residual. The `ettelem` that ran, aifoundry3's `build/ettelem/ettelem`
(`16037641…`, [`logs/binaries.sha256`](logs/binaries.sha256)), was built on 25 September from lab `de262730`'s `tools/ettelem/ettelem.cpp`
(`ba9a0ac3…`), which predates the reviewed source Q136(w)'s table and `dmcmd_audit.py` bind to that path (`a6cf931b…`, `efa3e8cd`). Its
`config()`, `sample()`, `Dm::get()` and `Dm::resetStats()` are byte-identical to the reviewed source's, and the reviewed source's extra
sends sit in a `temp` subcommand that the binary's source lacks and E128's guard refuses, so every class above stands
([`docs/findings/14-card-behaviour.md`](../../../findings/14-card-behaviour.md), E132 C1 and E134 C6; `corrections-numbers.txt` § C5).*

## Card and post

`et-who` at the session's start (21:23:33) and at its end (22:04:32): no process held a device node or card lock; other users' idle logins
were present, no device process of theirs. The previous aifoundry3 lane (E147) had released card 0 at 20:57:44. The day's post (message
1566837317765963987) was rewritten under EXPECT_TEXT and the Discord lock, each edit dry-run, saved and read back: at 21:23:12 PST this lane's
clause, "using aifoundry3 for 1 h, until ~22:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)", was added to the
two clauses then held (aifoundry1 card 1, aifoundry2); at 22:10:14 PST, the release, rebuilt after a refusal with exit 7 (another lane had
rewritten the post meanwhile), dropped it and kept the aifoundry2 clause word for word, with no " — released" because that card is still held:
"<ai> **Claude says:** using aifoundry2 for 1.5 h, until ~23:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)"
(`logs/push-and-claim-times.txt` holds every before and after).

## What it changes

- **Item 6**: on this card, the item's "a power model whose bands cover on new kinds" is met by M7 (28 of 30, registered C1 PASS; M6's
  held 19 of 25 on pool 4), and heat is answered again out of sample (H1–H4 PASS on a second blind pool). Still open: M7's power is biased high
  on the floats (−0.23 W, registered B1 FAIL HIGH, of the size the session's leakage fit makes), fp16's rms is twice its nested claim on the
  registered primary (P2 FAIL; the meter's dips carry it), M7 is not resolved from M6 or M5, and int8 has three steady misses (whole-line
  zero/one flip-flops and power-law weights 0.6 W high, a real w8a8 tile 0.5 W low).
- **The model**: a next fit should carry a float offset or a leakage footing shared across sessions, and int8's line flip-flop; the bands
  (rule B) stand as they are. **For E142**: `e141.json` is the aifoundry3 footing its card-term rules X1 and X2 read.

*Corrected after verification (C1, C3; Mon 2 Nov 2026). For item 6, read "M7's power is biased high on the floats (−0.23 W, registered B1
FAIL HIGH ...)" as the registered reading on this session's leakage fit; on M7's training footing it is +0.00 to −0.13 W, and fp16's
P2 FAIL is the same footing (on that footing fp16 reads 0.243–0.255 W with the dips kept, 0.145–0.147 W with them removed, against the
0.247 W line). For the model, read instead of "a next fit
should carry a float offset or a leakage footing shared across sessions": **a next fit should first put its training rows and its tests on
one footing, a leakage slope shared across sessions (or the slope as a model term) and one rule for the meter's dips, which the evidence
favours over a float offset**; only then can a residual float offset of up to about −0.13 W be tested. The bands' gain over M6 is
calibration, not accuracy (C3). int8's three steady misses and the line flip-flop stand.*

## Files

`scored.json` and `results.md` (primary, with every arm's verdicts), `scored-nodips.json` and `results-nodips.md` (dips removed, scored alone),
`e141*.json`, `runs*.csv`, `reduce*.txt|log` (the reduction and each arm: leakage 0.1994, 0.3803, 0; dips removed; gates off), `score*.log`,
`code.sha256`, `logs/` (the session log, the queue, the session's two config reads, the device-command preflight, the binaries' hashes, the
pre-commit dry runs, the order of events), `aifoundry3/e141/p1411*`, `aifoundry3/e141-smoke/p14101`, `aifoundry3/e141-stoptest/p14102` (raw,
as copied from the box; the reduction's `dir` fields point here), `aifoundry3/logs/` (the box's copy of the logs).

*Added after verification (Mon 2 Nov 2026):* `corrections-numbers.py` → `corrections-numbers.txt` (every number the corrections quote, from
committed files); `posthoc-after-verification/` (six post hoc reductions of the four passes at the training rows' footing, each scored
alone; its README). Nothing listed above changed.

## Corrections after verification (Mon 2 Nov 2026)

An independent verifier (Q138's, about 22:20–22:48 PST) re-ran E141's reducer on the committed passes (0 differences from `e141.json`),
scored it again with its own scorer (every rule and every arm reproduced), re-ran the frozen predictor (0 differences from the predictions
file), checked the commits' order and the blind protocol, audited every device-command site again down to the firmware handlers, and read
the box (read-only) and the day's post. Its verdict: the result holds, with six faults to fix. None is a measured number, a rule, a
prediction or a registered verdict, and none is a disallowed command. They are corrected here, desk only, at about 23:10 PST, by the dated
notes above and this section; the frozen text is unedited.

- **C1 (major): the footing behind B1 and P2.** The registration says leakage `auto` with the dips kept "is the frame of M7's aifoundry3
  training rows", and result 4 calls it "the footing every M7 training session used with its own fit". Neither is true. Of the 247
  aifoundry3 float rows M7 was fitted on (`docs/reports/data/2026-11-02-q138m-model/loko-m7.json` › `families.float.row_errors`, card `a3`),
  80 (E121 15, E122 25, E123 40) were reduced at a fixed 0.1994 W/°C with the meter's dips removed (each one's `e1xx.json` › `leak.mode`
  `0.1994`, `reducer.dips` "removed"), 13 (E127) at their own fit, 0.1913, with the dips removed, and 154 (E78 33, E86 8, E90 21, E92 34,
  E95 21, E115 19, E140 18) at their sessions' own fits, 0.1396–0.2959, with the dips kept. Their sessions' slopes average 0.2104 W/°C over
  rows, 0.2163 weighted by D and 0.2217 weighted by D², against this session's fitted 0.2634. Reduced post hoc at those slopes, E141's floats
  read a bias of −0.107 / −0.121 / −0.133 W with the dips kept and +0.001 / −0.013 / −0.026 W with them removed (B1's line −0.117), and
  fp16 0.243 / 0.249 / 0.255 W and 0.147 / 0.145 / 0.145 W (P2's line 0.247); C1 30 of 30 at all six. So between about half and all of
  the registered −0.230 W is the reduction's footing, and the registered B1 FAIL HIGH and P2 FAIL follow the session's own leakage fit
  against M7's training footing, as E142's auto arm shows on card 1 (−0.354 W FAIL HIGH at 0.408, against +0.050 PASS at its
  training-matched 0.2414) and E140's 0.1994 arm on pool 4 (−0.124 W over 25 rows, against −0.275 at its fit, 0.286). **Corrected
  reading:** E141 does not measure a float offset in M7; it cannot exclude one of up to about −0.13 W. **Corrected correction for the next
  fit:** not "a float offset of about −0.2 W" but one footing for training rows and tests, a leakage slope shared across sessions (or the
  slope as a model term) and one rule for the meter's dips, which the evidence favours; a residual float offset is then testable. The
  verifier's own post hoc arm, 0.2104 with the dips kept ("every power rule passes"), is reproduced byte for byte; the D-weighted
  slopes and the dips-removed readings are this fix's, added because B1 crosses its line at 0.2144 W/°C, between the row-weighted and
  the D-weighted footing. All post hoc, never a verdict: [`posthoc-after-verification/`](posthoc-after-verification/README.md),
  `corrections-numbers.txt` § C1.
- **C2 (minor): 30 new kinds, not 36.** The 36 tiles are 30 new kinds and 6 anchors; the three zeros anchors are byte-identical to E78's
  own zeros tiles (sha256 `e5a00aa9…`, `tools/claims-v3/kinds/blind5/tiles/*/*.anchor_zeros.bin` and `tools/claims-v3/kinds/tiles/*/zeros.bin`),
  on which M7 was fitted, and the random and full anchors are fresh draws of kinds it was fitted on. Heat rms is 0.130 °C over the 24
  priority-1 tiles (0.128 / 0.129 / 0.135 per format, the rules), 0.132 over the 30 new kinds and 0.132 over all 36, so "about an eighth of
  a degree" stands (§ C2).
- **C3 (minor): the bands' width.** M7's mean 95% half-width over the 30 non-anchor tiles is 0.807 / 0.536 / 0.595 W (fp32 / fp16 / int8)
  against M6's 0.498 / 0.344 / 0.517 and M5's 0.385 / 0.340 / 0.467, while M7's and M6's errors are the same (rms 0.365 against 0.367 W,
  bias −0.233 against −0.237); the largest |error| is 1.14 of M7's half-width, 1.61 of M6's, 2.20 of M5's. M7's 28 of 30 against M6's 22
  is calibration, not accuracy. M7's float heat bands are narrower than M6's (0.335 against 0.579 °C) and hold 30 of 30 (§ C3).
- **C4 (minor): the kinds-table cells.** The lane's result named no kinds-table cells. It now carries one per tile and quantity, from
  `e141.json` › `items.<tile>.D` (switching W over the type's zeros, 600 MHz) and `.dT_win` (the die's rise over the 4.5 s run), each with its
  95% half-width and kept passes (three; two for `fp16.exp_only`): the 30 new kinds and the 6 anchors, marked (§ C4). The int8 rises sit on
  the readout's whole-degree steps (exactly 1.0 °C with no spread on eight tiles): there the zero interval is the 1 °C step, not a precision.
- **C5 (minor): the `ettelem` binary predates its reviewed source.** As the note in § Device commands sent says: built from `de262730`'s
  source (`ba9a0ac3…`), not the reviewed `a6cf931b…`; its four sending functions are byte-identical and the extra sends of the reviewed
  source are in a `temp` subcommand the guard refuses, so every class stands (§ C5).
- **C6 (minor): M2 by arm.** The lane's result said M7 beats M5 "only with the dips removed". It reads BETTER with the pass gates opened too
  (−0.044 W [−0.095, −0.002], `scored.json` › `arms.gates_off`), as result 1's table shows; the verdict is NOT RESOLVED (−0.040 W
  [−0.091, +0.004]) (§ C6).

**Unchanged:** the registration (`tools/claims-v3/e141/`, `87a64409`), `scored.json`, `results.md`, `scored-nodips.json`,
`results-nodips.md`, every reduction and arm in this directory, the raw passes and the logs, and every registered verdict: P1 PASS, **P2
FAIL**, P3 PASS, **B1 FAIL HIGH**, B2 PASS, C1 PASS, M1 and M2 NOT RESOLVED, H1–H4 PASS.

**What the corrections do to predicting power and heat.** Heat: nothing; the term H2 (0.1186 °C per board W over a 4.5 s run) holds at
every footing, 0.13 °C rms against a nested 0.16–0.21 °C, with bands narrower than M6's. Power on the floats: the blind error over the nested
score and the 0.23 W bias are not shown to be M7's; read on M7's training footing the floats come to 0.144–0.275 W rms (fp32) and
0.145–0.255 W (fp16), against nested 0.247 and 0.162, and the next step is a fit and its tests on one footing, not an offset. Power on int8:
unchanged, 0.34–0.36 W against a nested 0.226 W at every footing, with three steady misses. The bands: they cover new kinds because they are
wider, and can be quoted as calibrated bands, not as a sharper model.
