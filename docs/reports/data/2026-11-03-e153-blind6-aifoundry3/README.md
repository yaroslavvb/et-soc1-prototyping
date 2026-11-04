# E153: M8 against blind pool 6 on aifoundry3 card 0 - all 3,140 launches' C bit-exact and the six pool-5 re-runs within 0.04 W of E141's (K1 PASS); M8's floats unbiased and its bands cover 29 of 30, but fp32 misses its rms rule (P1 FAIL), M8 is resolved worse than M7 (M2 WORSE) and not better than M6; heat holds (H1-H4 PASS)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, "a power model across kinds", tested out of sample on a sixth pool written by someone else, on the card M8's units are. It bears on
three ranks of Q138's final critic: **rank 2** (M8 scored on a sixth blind pool; this is the aifoundry3 card), **rank 14** ("no file tile's
results are checked": the C-checked re-run of 6 pool-5 tiles, K1, and the check of every pool-6 launch) and **rank 5** (the card scale; card 1's
half waits on E157), with **rank 8**'s real-tile sub-rule carried by the pool. Tue 3 Nov 2026 (week 45), Q139. Pre-registered in `359c96b2`
(committed 16:18:58, on origin/main by 16:19:13 PST), before the claim and before any card ran a pool-6 tile at 600 MHz:
[`tools/claims-v3/e153/README.md`](../../../../tools/claims-v3/e153/README.md); its amendment A1 (`e6ca949d`, 16:42:11, before the registered
reduction and scoring; below) changed the scorer's handling of a tile that never ran, and nothing else. The model is Q139(m)'s M8, frozen in
`122da8b6` (04:57:59 PST); the pool, [blind pool 6](../../../../tools/claims-v3/kinds/blind6/README.md), 50 tiles by an independent designer,
and M8's, M7's and M6's frozen predictions for this card, in `d98d2e34` (05:39:23 PST); the check of C, Q139(k)'s, in `4946a992`; the footing,
Q139(u)'s, in `d4c36bfe`/`f47669d1`; each an ancestor of `359c96b2` ([`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt)).
aifoundry3 card 0 at 600 MHz in every sample; `ettelem config` read at the session's start (16:21:44), at both ends of the stop-path test, the
smoke and every pass, and at the session's end (17:11:40): TDP 0 W, threshold 65 °C, max_power, 600 MHz, 522–523 mV, never set. **Every
device-management command sent was a read** (nine kinds, two of them PMIC voltage-register reads, which the owner's rule of 2 November 2026
allows; `since_reset_ms` −1 in all 29,385 samples). Card session 16:21:44–17:11:40 PST, **49.9 of the 55 card-minutes allowed**: the
stop-path test 15302, the smoke 15301 and four passes, 15310–15313 (703–746 s each).*

**In plain words.** M8 is the lab's power-and-heat model: from the bytes a matmul multiplies it predicts the watts the chip draws over the same
kernel on zeros, and how far the die warms in a 4.5 s run. E153 ran 44 new kinds of numbers (and 6 anchors), written by someone who never saw
the model, on the card M8's numbers are written for, **with every launch's result C read back and compared bit for bit with the RTL's
arithmetic**. **The arithmetic is right**: all 3,140 launches (four passes and the smoke, fp32, fp16 and int8, up to 923,021 operations a
launch) matched exactly, including the first silicon reads of full-range int8, its 32-bit wrap, wide float exponents and real model tiles.
**The six pool-5 tiles re-run with C checked land within 0.04 W of E141's** on the same footing (K1 PASS), so pool 5's file-tile rows, and
every model's file-tile training rows, stand as measured. **On one footing M8 has no float bias** (−0.014 W; E141's M7 read −0.23 W on its own
session footing, as this session's own footing reads M8, −0.21 W) and **its 95% bands hold 29 of 30 new kinds**; heat is predicted to 0.10–0.13
°C. **But M8 is no better than the models it replaced**: fp32's error, 0.330 W rms, exceeds what its nested score allows (P1 FAIL; one tile,
a single high mantissa bit flipping on a 1/3 base word, is 0.81 W over-predicted by every model), int8 reads 0.296 W against M7's 0.231 and
M6's 0.199, because M8's new discount for B bytes that flip all eight bits over-corrects (+0.36 to +1.31 W on the three tiles where it acts
most), and **M8 is resolved worse than M7** (M2 WORSE, +0.034 W) and **not resolved from M6** (M1, +0.043 W).

## Results

**All four passes kept on the registered primary** (Q139(u)'s one footing: E78's reduction unchanged through `reduce_e153.py`, leakage frozen at
aifoundry3's 0.20563713796102187 W/°C, read through `reduce_footing.K_FROZEN["a3"]`, no refit, E82 A2's dip rule once, E78's run and pass
gates): 15310–15313, none set aside, every one of the 300 runs passing every per-run gate. E78's runner skipped four runs by its own rule
("launch reading not reached": `int8.b_line_zero_full` in 15310, `fp16.a_zeros_b_complement` and `int8.gray_a` in 15312, `fp32.zeros` in
15313), so those keep three passes; every tile has at least three, and every rule is scored ([`results.md`](results.md),
[`scored.json`](scored.json)). **The check of C left no tile out** (E153-KC PASS).

**0. The check of C and K1 first** (rank 14; Q139(k)'s `ccheck.py check` at the desk on all five C logs in one call,
[`ccheck/ccheck-all.json`](ccheck/ccheck-all.json), [`ccheck/ccheck.txt`](ccheck/ccheck.txt)):

| what | result |
|---|---|
| launches with a C record, the four passes and the smoke | **3,140 of 3,140 PASS** (bit-exact against the RTL's arithmetic over every word of every participating minion): fp32 1,226, fp16 842, int8 1,072; ROUNDING 0, UNMODELLED 0, FAIL 0, broken records 0; one host and kernel throughout (`99ed75fb…`, `d521e432…`) |
| pairing | every launch record of every pool-6 and K1 tile in a kept pass has its C record (`t_start_ms`, `t_end_ms`): 0 unpaired; 236 launches on the six K1 tiles; n from 20,000 (each run's calibration launch) to 923,021 |
| first silicon reads | the 36 tiles with first-read notes (`tools/claims-v3/e153/logs/ccheck-domain.txt`: wide exponent spreads, many distinct magnitudes, int8 operands to ±127 and −128, words that wrap by n) all PASS |
| **E153-K1-C** | **PASS** (the critic's looser reading, PASS or ROUNDING: PASS) |
| **E153-K1-D** (the critic's ±0.05 W) | **PASS**: every K1 tile within 0.05 W of E141's D on Q139(u)'s footing |
| **E153-K1-W** (Q139(k)'s Welch interval) | **PASS** |
| **E153-K1** (K1-C and K1-D) / **K1′** (K1-C and K1-W) | **PASS** / **PASS** |
| **E153-KC** | **PASS**: no pool-6 tile left out |

| K1 tile (pool 5) | E153 D, W (passes) | E141 D on the footing (passes) | E153 − E141 | Welch half-width | session-own footings (reported): E153 / E141 / diff |
|---|---|---|---|---|---|
| `fp32.b_exp_busy_a_const` | 15.496 (4) | 15.498 (4) | **−0.001** | 0.058 | 15.364 / 15.393 / −0.030 |
| `fp32.real_pythia_ln1_q` | 22.078 (4) | 22.118 (4) | **−0.040** | 0.145 | 21.897 / 21.964 / −0.067 |
| `fp16.sparse24_aligned` | 12.812 (4) | 12.830 (4) | **−0.018** | 0.064 | 12.453 / 12.716 / −0.263 |
| `fp16.exp_only` | 16.329 (4) | 16.341 (3) | **−0.012** | 0.180 | 16.020 / 16.247 / −0.227 |
| `int8.gray_a` | 4.078 (3) | 4.100 (4) | **−0.022** | 0.123 | 3.987 / 4.034 / −0.047 |
| `int8.b_line_zero_one` | 3.361 (4) | 3.380 (4) | **−0.019** | 0.178 | 3.321 / 3.351 / −0.029 |

On the footing the six differ from E141's by −0.040 to −0.001 W (mean −0.019 W, a ratio of 0.9975; [`posthoc.txt`](posthoc.txt) § 4). **The C
log's extra DMA** (1 MiB of poison written before each launch, 1 MiB of C read after it) widened the gap between launches from E141's 1 ms to a
median 3 ms (the smoke gate: max 5 ms; E78's duty gate binds near 14 ms), so each run's duty fell from E141's median 0.9963 to 0.9932
([`posthoc.txt`](posthoc.txt) § 4), which would lower D by about 0.3% (about 0.05 W on a 17 W float kind), the size of the K1 differences. On
each session's own leakage fit (E141 0.263, E153 0.275 W/°C), the two sessions' fp16 K1 tiles differ by 0.23–0.26 W: the K1-D FAIL there
(reported) is the footing, not the card.

**1. The registered verdicts** (primary; the arms are reported, never the verdict; [`results.md`](results.md), `scored.json`):

| rule | quantity | set | reading | the reference's interval | verdict | session-own footing | leak auto, dips removed | frozen slope, dips kept | leak 0.1994 | leak 0 | gates off |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **E153-P1** | power | priority-1 fp32 (12) | rms **0.330 W** | 0.094–0.285 | **FAIL** | FAIL 0.365 | FAIL 0.355 | FAIL 0.329 | FAIL 0.331 | FAIL 0.524 | FAIL 0.330 |
| **E153-P2** | power | priority-1 fp16 (6) | rms **0.125 W** | 0.048–0.253 | **PASS** | FAIL 0.424 | PASS 0.227 | FAIL 0.329 | PASS 0.122 | FAIL 0.457 | PASS 0.125 |
| **E153-P3** | power | priority-1 int8 (12) | rms **0.296 W** | 0.135–0.356 | **PASS** | PASS 0.336 | PASS 0.319 | PASS 0.316 | PASS 0.294 | PASS 0.267 | PASS 0.296 |
| **E153-B1** | bias | priority-1 floats (18) | mean(measured − M8) **−0.014 W** | −0.108 to +0.053 | **PASS** | FAIL HIGH −0.210 | FAIL HIGH −0.155 | PASS −0.073 | PASS −0.002 | FAIL LOW +0.395 | PASS −0.014 |
| **E153-B2** | bias | priority-1 int8 (12) | **−0.071 W** | −0.192 to +0.079 | **PASS** | PASS −0.115 | PASS −0.115 | PASS −0.077 | PASS −0.067 | PASS +0.057 | PASS −0.071 |
| **E153-C1** | power coverage | 30 priority-1 new kinds | **29 of 30** inside (out: `fp32.b_onebit_b20_third`) | ≥ 26 | **PASS** | PASS 26 | PASS 27 | PASS 28 | PASS 29 | FAIL 19 | PASS 29 |
| **E153-M1** | M8 against M6 | the 30 | rms(M8) − rms(M6) **+0.043 W** [−0.006, +0.091] | | **NOT RESOLVED** | NOT RESOLVED +0.044 | NOT RESOLVED +0.047 | NOT RESOLVED +0.043 | NOT RESOLVED +0.042 | NOT RESOLVED +0.010 | NOT RESOLVED +0.043 |
| **E153-M2** | M8 against M7 | the 30 | **+0.034 W** [+0.001, +0.085] | | **WORSE** | WORSE +0.031 | WORSE +0.036 | WORSE +0.031 | WORSE +0.034 | NOT RESOLVED +0.012 | WORSE +0.034 |
| **E153-H1** | die rise | priority-1 fp32 (12) | rms **0.098 °C** | 0.110–0.251 | **PASS** (below the 2.5% point: better than the nested score says) | PASS 0.088 | PASS 0.098 | PASS 0.088 | PASS 0.098 | PASS 0.098 | PASS 0.098 |
| **E153-H2** | die rise | priority-1 fp16 (6) | rms **0.106 °C** | 0.073–0.246 | **PASS** | PASS 0.111 | PASS 0.106 | PASS 0.111 | PASS 0.106 | PASS 0.106 | PASS 0.106 |
| **E153-H3** | die rise | priority-1 int8 (12) | rms **0.128 °C** | 0.123–0.286 | **PASS** | PASS 0.124 | PASS 0.128 | PASS 0.124 | PASS 0.128 | PASS 0.128 | PASS 0.128 |
| **E153-H4** | heat coverage | the 30 | **30 of 30** | ≥ 26 | **PASS** | PASS 30 | PASS 30 | PASS 30 | PASS 30 | PASS 30 | PASS 30 |
| **E153-R1** | real tiles | all 12 | rms **0.155 W** | ≤ 0.602 (the pool's own: 0.186–0.602) | **PASS** (below the pool's own range) | PASS 0.428 | PASS 0.249 | PASS 0.328 | PASS 0.151 | PASS 0.381 | PASS 0.155 |
| **E153-R2** | real tiles | all 12 | **12 of 12** inside | all | **PASS** | FAIL 9 | FAIL 10 | FAIL 11 | PASS 12 | FAIL 8 | PASS 12 |
| **E153-CS0** | card scale, this card | floats with D ≥ 5 W (27) / int8 with D ≥ 1 W (17) | median D / M8: floats **0.9995** [0.9980, 1.0078]; int8 **0.9738** [0.9560, 0.9961] | within 1% of 1 | floats **PASS**; int8 **FAIL** | 0.9901 PASS / 0.9662 FAIL | 0.9899 FAIL / 0.9647 FAIL | 0.9988 PASS / 0.9743 FAIL | 1.0003 PASS / 0.9746 FAIL | 1.026 FAIL / 1.004 PASS | as primary |
| **E153-CS1** | card scale, card 1 | | | | **NOT SCORED** (E157's reduction did not exist at collection; E157 scores it against this `e153.json`) | | | | | | |

The session-own footing set pass 15311 aside (E78's random-range gate: `fp32.randn` spans 1.171 W) and fitted leakage 0.275 W/°C on its own
191 runs; the frozen-slope dips-kept arm set 15311 aside too; the leakage 0.3803 arm set 15312 aside (int8's zeros line) and reads P1 0.461,
P2 0.479, P3 0.387 (FAIL), B1 FAIL HIGH −0.376, B2 FAIL HIGH −0.222, C1 22, R2 5, M2 WORSE (`scored.json` › `arms`). **Arm-sensitive**: P2,
B1, R2 and K1-D move with the footing; **P1's FAIL, M1, M2 and every heat rule do not** (M2 except at leakage 0). **The frozen expectation**
was KC and K1-C PASS, K1-D FAIL on at least one tile, K1-W PASS, P1–P3 PASS, B1 and B2 PASS, C1 PASS, M1 and M2 NOT RESOLVED, H1–H4 PASS, R1
PASS, R2 either, CS0 floats PASS and int8 either: **K1-D passed** (the expectation was wrong on the footing; it fails on the session-own
footing), **P1 failed**, and **M2 read WORSE**; everything else fell as frozen.

**2. M8, M7 and M6 on the same tiles** (reported; measured − model, W; heat °C; primary; `scored.json` › `primary.primary.reported`,
[`posthoc.txt`](posthoc.txt) § 5):

| model | fp32 rms / bias (12) | fp16 rms / bias (6) | int8 rms / bias (12) | priority 1: rms / bias (30) | all 44 new kinds: rms / bias | real tiles rms (12) | inside its own 95% band (30 / 44) | heat rms fp32 / fp16 / int8 |
|---|---|---|---|---|---|---|---|---|
| **M8** (scored) | 0.330 / −0.007 | 0.125 / −0.029 | 0.296 / −0.071 | **0.286 / −0.037** | **0.339 / −0.004** | 0.155 | 29 / 40 | 0.098 / 0.106 / 0.128 |
| M7 | 0.313 / −0.005 | 0.121 / +0.013 | 0.231 / −0.097 | 0.252 / −0.038 | 0.281 / −0.006 | 0.153 | 29 / 42 | 0.100 / 0.103 / 0.126 |
| M6 | 0.310 / −0.022 | 0.154 / +0.052 | 0.199 / −0.133 | 0.243 / −0.052 | 0.245 / −0.030 | 0.141 | 29 / 42 | 0.106 / 0.096 / 0.122 |

Over all 44 new kinds (priority 2's tests included; reported), the paired M8 − M6 rms is **+0.093 W [+0.014, +0.179], WORSE**. The three models
differ by a median 0.11 W a tile here, so the floats cannot tell them apart; int8 can.

**3. Where the misses are** (M8's error by the pool's case, all 44 new kinds; n, rms, mean; [`results.md`](results.md), `posthoc.txt` §§ 1–3):

| case | n | M8 rms / mean | M7 rms / mean | M6 rms / mean | the tiles that carry it |
|---|---:|---|---|---|---|
| L int8 whole-line / whole-word | 4 | **0.680 / +0.382** | 0.418 / +0.243 | 0.333 / +0.074 | `int8.b_line_55_aa` +1.307 W (priority 2, outside M8's band; M7 +0.821, M6 +0.561), `int8.b_line_zero_ff` +0.360 |
| S single bits on other base words | 5 | 0.431 / −0.247 | 0.421 / −0.216 | 0.369 / −0.154 | `fp32.b_onebit_b20_third` −0.808 (outside every model's band: bit 20 and bit 12 on the 1/3 base word read 2.92 W apart, every model says 3.85–3.91), `fp16.b_onebit_b6_third` −0.482 |
| Z zeros' transport | 4 | 0.382 / +0.164 | 0.229 / +0.050 | 0.289 / −0.276 | `int8.a_zeros_b_lineflip` +0.615: measured **+0.276 W**, M8 −0.339 (inside its wide band), M7 +0.049, M6 +0.505; `fp32.negzero_a_b_complement` +0.383 |
| B int8 B-position | 5 | 0.323 / −0.298 | 0.348 / −0.325 | 0.236 / −0.211 | `int8.bheld_bit4` −0.543, `bheld_bit1` −0.276, `bheld_bit7` −0.242: every model over-predicts a held one-bit B |
| E exponent-heavy | 10 | 0.284 / +0.183 | 0.275 / +0.167 | 0.244 / +0.166 | `fp32.exp_a_pow2wide_b_randn` +0.618 (priority 2, outside), `fp32.exp_a_walk_fixedmant` +0.367, `fp32.exp_b_alt_shift` +0.324: the card pays **more** than M8 on 7 of 10 (than M7 on 7, M6 on 8) |
| R real tiles | 12 | 0.155 / −0.084 | 0.153 / −0.006 | 0.141 / +0.014 | none above 0.38 W (`fp32.real_smol_softmax_v_causal` −0.376) |
| W power-law weights | 2 | 0.150 / −0.147 | 0.134 / −0.130 | 0.130 / −0.122 | |
| C the C-register candidate | 2 | 0.101 / −0.087 | 0.082 / −0.038 | 0.141 / −0.132 | |

*Post hoc (not verdicts; `posthoc.txt`):* without `fp32.b_onebit_b20_third` the fp32 rms is 0.245 W over 11, inside P1's 0.285 W line, so P1's FAIL is
that one tile, which every model misses alike. Without the two priority-1 int8 tiles whose B bytes flip all eight bits, M8's int8 rms is 0.233 W
(M7 0.242, M6 0.173): M8's int8 deficit is its near-whole-byte discount (`bsat`, −56.8 fJ a bit), which Q139(m)'s README warned over-corrects
whole-line flip-flops; on `int8.a_zeros_b_lineflip`, the tile built to test it, the card draws +0.28 W where M8 said −0.34.

**4. Heat.** The die's rise over the 4.5 s window is predicted to 0.098 / 0.106 / 0.128 °C rms (fp32 / fp16 / int8), all 30 inside M8's band;
the measured rise per board W over the 30 is **0.1185 °C/W** against M7's (and M8's) 0.1186 (`scored.json` › `reported_rise_per_board_w`). At
the measured run length (M7's ST term; median T_run 4.51 / 4.51 / 4.44 s) it reads 0.123 / 0.100 / 0.153 °C, 30 of 30 (reported). int8's
rises sit at whole-degree readings (1.000 °C on most tiles), so H3 tests little below 0.5 °C.

**5. The pool's anchors and E78's.** Pool 6's random anchors read fp32 24.919 W (M8 24.728), fp16 22.044 (22.075), int8 full 7.138 (7.026);
its three zero anchors (byte-identical to E78's zeros) read −0.053, +0.021 and +0.058 W over E78's interpolated zeros, inside every band.
E78's own random anchors: fp32 24.703 W, fp16 22.154, int8 full 7.106 (per pass within 0.04, 0.14 and 0.13 W). The tie's drift over a pass
was 0.20–0.26 W (`e153.json` › `tie_drift_w`); carry-over 0.0013 ± 0.0005 W per W; idle consistency median 0.058 W.

## What it does to predicting power and heat

**The terms tested** are M8's: its constants refitted on Q139(u)'s one footing, its C-register term for the floats (6.44 fJ a flip), its
near-whole-byte discount for int8 B bytes (−56.8 fJ a bit), its card scale (1 on this card) and M7's heat law, carried; and, underneath them,
the validity of every file-tile row (the C check). **Out-of-sample error, before → after** (power of a new kind at 600 MHz on aifoundry3,
rms over priority-1 kinds; floats' bias):

| | fp32 | fp16 | int8 | floats' bias | heat fp32 / fp16 / int8 | source |
|---|---|---|---|---|---|---|
| before: M8's nested claim (leave one kind out, aifoundry3's rows) | 0.193 W | 0.147 W | 0.244 W | — | 0.181 / 0.159 / 0.205 °C | `nested-m8.json`; `tools/claims-v3/e153/ref-errors-m8.json` |
| before: M7 blind on pool 5 here (E141), its session's footing | 0.325 W | 0.317 W | 0.356 W | −0.230 W | 0.128 / 0.129 / 0.135 °C | E141 `scored.json` |
| before: the same, post hoc on Q139(u)'s footing | 0.146 W | 0.149 W | 0.336 W | +0.012 W | — | Q139(u) `scores-m7u.json` |
| **after: M8 blind on pool 6 here, on the footing (registered)** | **0.330 W** | **0.125 W** | **0.296 W** | **−0.014 W** | **0.098 / 0.106 / 0.128 °C** | `scored.json` |
| after: M7 / M6 on the same pool and footing (reported) | 0.313 / 0.310 W | 0.121 / 0.154 W | 0.231 / 0.199 W | +0.001 / +0.002 W | M7 0.100 / 0.103 / 0.126; M6 0.106 / 0.096 / 0.122 °C | `scored.json` › `reported` |

So: (1) **the one footing is confirmed as the term that mattered**: on it the float bias is gone (−0.014 W, against −0.210 W for the same data
on its own session's fit) and the K1 re-run agrees with E141 to 0.04 W where the two sessions' own fits disagree by up to 0.26 W; (2) **M8's
int8 discount is falsified** on the tiles it was built for (int8 0.296 W against M7's 0.231 W, and +0.36 to +1.31 W on the three whole-byte
flip-flops), so the next fit should drop it or bound it; (3) **M8's float terms add nothing measurable** over M7 and M6 on new kinds (fp32 0.330
against 0.313 / 0.310 W; fp16 0.125 against 0.121 / 0.154 W): fp32's error is one single-bit tile every model misses by 0.7–0.8 W and an
exponent-heavy excess every model shares (+0.17 to +0.18 W mean), which a next term (an exponent-field price and a bit-position price that
depends on the base word) would have to carry; (4) **heat from the bits over 4.5 s is predicted to about 0.1 °C** on new kinds, as before;
(5) **the rows are valid**: 3,140 of 3,140 launches computed exactly what the RTL says, so no training or test row on this card is biased by a
silent kernel error. Prediction of a new kind's power on this card now stands at about 0.13 W (fp16) to 0.30–0.33 W (fp32, int8) rms, 1–2% of a
float kind's watts and about 6% of an int8 kind's, with covering bands; M8 is not the model to quote over M7 or M6.

## Registered against what happened

| | registered | happened |
|---|---|---|
| order | `d98d2e34`, `122da8b6`, `4946a992` before the registration; the registration before the claim and the first launch | all ancestors of `359c96b2` (16:18:58, pushed by 16:19:13); claim saved 16:21:29; first device access 16:21:44 |
| passes | 15310–15312, 15313 if it fits (3,240 s from T0, before 21:50 PST); at least 2 kept | four ran (746, 733, 717, 703 s), faster than the registered estimate (880 s; E141's scaled 779–846 s), so the budget rule admitted 15313; queue done at T0+2996 s; **four kept** |
| card time | ≤ 55 min; no session after 21:00, every run ends by 22:00 PST | **49.9 min** (16:21:44–17:11:40 PST) |
| stop-path test 15302 | die, board and watcher each end `run_e153.py` with EXIT_HOT on a live sample ≤ 2.0 s old, no launch | **PASS**: the die stop on `minshire[0]` 50 °C read 0.081 s after the sample, the board stop on 23.51 W at 0.12 s, the watcher on 23.57 W at 0.049 s (`aifoundry3/e153-stoptest/p15302/STOP.*`); no launch record |
| smoke 15301 | the gate (`smoke_gate_e153.py`) | **PASS**: 546.001 / 318.0 cycles per op, 0.599–0.600 GHz, config 0 W / 65 °C / 600 MHz at both ends, every pool tile's dump equal to its sha256, 408 live samples, `since_reset_ms` −1, board 23.05–50.45 W; C log: 10 host records naming the registered host and kernel, 60 C records for 60 launch records, 0 flagged; launch gaps median 3 ms, max 5 ms |
| stops | board ≥ 65 W or `minshire[0]` ≥ 70 °C, live, main path and in-run watcher | highest board 54.26 W (15311), highest `minshire[0]` 62 °C; no stop fired |
| the C check | every pool-6 launch and the K1 re-run, bit-exact | 3,140 of 3,140 PASS |
| expectation | (the registration's § Precision) | **K1-D passed, P1 failed, M2 read WORSE**; the rest as frozen |
| departures | — | **A1** (registered as an amendment before the registered scoring): a pipeline test on pass 15310 alone (16:36–16:40 PST; a scratch copy, one pass, below every rule's minimum, its numbers reported nowhere) showed the scorer counting a tile with no launch as a C failure; the code was aligned with the rule's words. **D1**: E78's runner skipped four runs by its own rule (listed above), as E141's D2. **D2**: the collector's Python was the Intel's `/usr/bin/python3` 3.9.6 with numpy 1.26.4 (E141's D3). **D3**: the committed raw passes keep `c-log.jsonl` gzipped (`c-log.jsonl.gz`, 0.2 MB a pass against 2.2 MB); `ccheck/` holds the per-pass copies `ccheck.py` read, also gzipped. **D4**: the card budget section of the registration said a fourth pass "will not start"; that was its estimate, not a rule, and the budget rule started it |

## Device commands sent

As registered ([`tools/claims-v3/e153/README.md`](../../../../tools/claims-v3/e153/README.md) § Device commands sent): E78's harness unchanged,
every telemetry call through E128's guard (`ettelem config` with no argument, `ettelem sample --seconds --every-ms` and nothing else), `ettelem
config` at the session's start, at both ends of the stop-path test, the smoke and every pass, and at the session's end, `ettelem sample` at 10 Hz
in every block. Sent: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES,
**GET_ASIC_VOLTAGE**, GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, **GET_MODULE_VOLTAGE**: **all READs**, classified from
et-platform `836a4ab` (BL2 0.22.0), the two in bold PMIC voltage-register reads, which the owner's rule of 2 November 2026 allows. **Never
sent**: the statistics reset (`SET_STATS_RUN_CONTROL`; `since_reset_ms` −1 in every one of the session's 29,385 samples), any SET_*, the
firmware-revisions query, any residency read, any governor, TDP, threshold or clock set, any reset, and `dev_mngt_service` (lib.sh's drain is
replaced by a refusal). The host programs (E78's `sparsity_host` `20e760c2…` as the heater; the C-logging host `99ed75fb…` through
`sparsity_ccheck.sh` for every measured launch) open the ops node only; the C log adds runtime DMA (a 1 MiB write and a 1 MiB read a launch),
no device-management command. The checker (`dmcmd_audit.py`, unchanged), run by the session on the box before any device opened: **GO**, 32 send
sites, 0 disallowed, with the one reviewed exception (`lib.sh:154`, the conditional `--reset-ms` forward that `block_e153.sh`'s only
`start_sampler` call never uses), the patched host source scanned too ([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt); the
registration's `dmcmd-audit*.txt`). Residual, as registered: aifoundry3's thermal firmware build is not public, so the classes rest on
`836a4ab`'s handlers; the config reads and the telemetry came back in the form E141 read on this card (the smoke gate checks it).

## Card and post

`et-who` before the claim (16:21:06), at the session's start (16:21:43) and at its end (17:11:40): no process held a device node or card lock;
other users' idle logins were present (D1 of `hl/README.md`: an idle login does not block on aifoundry3), no device process of theirs.
Tue 3 Nov's one card post was message 1567332504330051616, created at 16:19 PST by E157's lane (the morning's post had been deleted, and Mon 2
Nov's was not touched). Rewritten under EXPECT_TEXT and the Discord lock, each edit dry-run, saved and read back: at 16:21:29 PST this lane's
clause, "using aifoundry3 for 1.5 h, until ~17:51 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)", was added to the
aifoundry1 card 1 clause then held; at 17:12:14 PST, the release, rebuilt from the edit box's own text after a refusal with exit 7 (the plan's
text had lagged another lane's edit), dropped it and kept the aifoundry2 clause word for word, with no " — released" because that card is still
held: "<ai> **Claude says:** using aifoundry2 for 1.5 h, until ~17:54 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)"
([`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt) holds every before and after).

## What it changes

- **Item 6** (the critic's rank 2, on this card): the critic's rules read **M8 − M6 not resolved below zero** (M1 NOT RESOLVED, +0.043 W), **bias
  inside B1/B2** (PASS, PASS), **26 of 30 inside** (29, PASS), **heat rms and coverage** (H1–H4 PASS), **the card scale as predicted** (floats
  0.9995, PASS; int8 0.974, FAIL, a rule the registration called weak). M8 does not improve on M7 or M6 here and is resolved worse than M7. The
  item stays open, now narrowed: the footing is settled, the int8 near-whole-byte discount should go, and the floats need an exponent-field term
  and base-word-dependent single-bit prices (cases E and S) that no model has.
- **Rank 14** closes on this card: the six pool-5 re-runs PASS bit-exact and reproduce E141's D on one footing (K1 PASS), and every pool-6 launch
  is checked. E157 holds the second card.
- **Rank 5**: this card's floats keep M8's scale (0.9995); card 1's scale against this session's D is E157's to score (CS1), and aifoundry2's
  (E160) reads this `e153.json`.
- **For E157 and E160**: [`e153.json`](e153.json) is the aifoundry3 footing their card-term and card-scale rules divide by.

## Files

`scored.json` and `results.md` (primary, with every arm's verdicts), `scored-session.json` and `results-session.md` (E141's session-own
footing, scored alone), `e153*.json`, `runs*.csv`, `reduce*.txt|log` (the reduction and each arm: session-own; leakage auto with dips removed;
the frozen slope with dips kept; leakage 0.1994, 0.3803, 0 with dips removed; gates off), `score*.log`, `code.sha256`, `ccheck/` (the C check:
`ccheck-all.json`, `ccheck.txt`, the five C logs it read, gzipped), `posthoc_e153.py` → `posthoc.txt` (every post hoc number above), `logs/`
(the session log, the queue, the session's two config reads, the device-command preflight, the binaries' hashes, the pre-commit dry runs, the
order of events), `aifoundry3/e153/p1531*`, `aifoundry3/e153-smoke/p15301`, `aifoundry3/e153-stoptest/p15302` (raw, as copied from the box;
`c-log.jsonl` gzipped; the reductions' `dir` fields point here), `aifoundry3/logs/` (the box's copy of the logs).
