# MM1-v3.3 candidate L3S: the L3's set overflow for the A operand, on MM1-v3.2

*Lane l3-edge, round Q234, Fri 20 Nov 2026 (week 47), Pacific time, at aifoundry2's desk. Desk only: no card, no simulator, no commit. Interpreter for every number: /usr/bin/python3 3.12.3, numpy 1.26.4, scipy 1.11.4, single-threaded inside the round's CPU slots. MM1-v3.2 (`tools/matmul/mm1/v3.2/`, landed 4e386f75; its declaration f8e00a57) is the base, imported unchanged. No E220 datum was opened.*

The owner's words that started the matmul model (Mon 16 Nov 2026, a voice transcription in which "matte mold" is the matmul): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained."

**Labels.** *Registered*: in `DECLARED-l3s.md` (sha256 `1e6e1c52d790bc35dcb03415f22564c5592d620026420c3ad0df3ff58ebc8b26`, hashed 2026-11-20 05:52:57 PST) before the fit. *Post hoc*: the term's constant and every fit here (made after its data existed). *Held out*: left out of the fit that scores it (two-stage: MM1-v3.2's own fold constants, lam refitted per fold). *Blind*: E220, whose forecasts are frozen here before any datum. *REPORTED*: printed, never deciding. Error = ln(forecast / measured), rms and bias in %.

## 0. On one screen

| item | value |
|---|---|
| the term | A's place (L3 or DRAM) moved by lam x (MM1-v3.2's A fresh share - the 4-way set-associative L3's), per row half, at full-mask gemmL-family points; one new constant |
| lam (all data, 3408 points, 2203 in the domain) | **0.6909** |
| K1 the lead (gemmL2x1x7, LOEO E215, held out) | 14.49% -> **8.68%** (drop 5.81 points; needed 3.0): PASS |
| K2 pooled LOEO wall cycles, no twins (n 2378) | 5.576% -> **5.423%** (-0.153 points; allowed +0.05): PASS |
| K3 placebo (feature permuted, lam refitted) | beaten in **100 of 100** (needed 95): PASS |
| verdict | **KEPT** |
| E220 forecasts | frozen 2026-11-20 05:56:55 PST: `forecasts-e220-l3s.csv` ff46a16ec6c83eb3..., `forecasts-e220-l3s.json` ac65c9596f5611c9... |

## 1. The lead

gemmL2x1x7 (39 MiB: A 28, B 7, C 4) ran 12.7-14.9% slower than MM1-v3.1 forecast on aifoundry3 card 0 and aifoundry1 card 1 (E215; the matmul report v2's verify finding M4). MM1-v3.2's own held-out op times (its LOEO E215 fold) at the four points (fp32, int8; both cards): -13.90, -15.50, -13.83, -14.65%.

## 2. The mechanism

**Known** (public sources): the L3 in the shire cache's reset mode M0 is 1 MB a shire, 32 MB in all; a line's home shire is PA[10:6] (also the lab's own measurement, `docs/et-soc1-notes.md`); it is **4-way set-associative with true LRU per set, 64-byte lines, write-back and write-allocate**; within the home the set is bank PA[12:11], sub-bank PA[14:13], set PA[22:15] (256 sets a sub-bank in M0). So the chip's 2^17 L3 sets are indexed by PA[22:6] and **repeat every 8 MiB**: every 8 MiB of addresses puts one line in each set, and a set holds four (the public core-et repository's `docs/CORE-ET-Shire-Cache-Specification.pdf`, sections 1.1, 1.3 tables 4-7, 1.4.1.2, 2.14.4; the lab's notes cite the same document). The kernel's request stream is MM1-v3.1's walk (`../../v3.1/walk/`, traced EXACT at 448 of 448 working harts). rgm136's host allocates C (MB NB 2 MiB), then A (MB KB 2 MiB), then B (KB NB 1 MiB) (`tools/claims-v3/e136/rgm136/host/main.cpp`, testArm).

**Assumed:** the cards run M0; one arm a device process, the pools contiguous in that order; a tile's 16 lines share its fate; the chip in lock step as the walk counts it; L2 hits (KB <= 2) counted as L3 accesses; B's extra retention (MM1-v3.2's plateau) not modelled, so the term moves A only. **Not known:** whether the card's firmware leaves M0 (no ESR read here); the replacement's behaviour under the RBUF and victim buffers; the DRAM side.

**What the walk shows** (`scripts/walk_explore.py`, `out/explore/walk_explore.json`; desk, no constant): at NB = 1 and MB >= 2 every A tile is used once a pass, so its exact LRU stack distance is the whole footprint (39.0 MiB at gemmL2x1x7, B 15.0 MiB). A fully associative 32 MiB LRU misses all of it; MM1-v3.2's logistic edge (x1 37.33 MB, w1 2.39 MB) keeps 38%; **the 4-way set model keeps 14.3%**: a set keeps its A lines only where its 8 MiB position holds at most four of the pass's lines. Just past 32 MiB, whole-pass reuse falls off LRU's cliff set by set; the retention is a property of how many lines each 8 MiB position holds, not a smooth function of the distance. The feature (`scripts/l3s_feature.py`) is that set model run on the kernel's own addresses, per row half, for every full-mask shape (600 shapes in `out/feature/l3s_cache.json`, about 2 minutes in all).

Single-distance ("cliff") shapes at the full mask, every committed point of each (held-out errors by LOEO; post hoc table, `out/fit/fit-l3s.json` edge_rows):

| shape | footprint MiB | set model: A kept | points | MM1-v3.2 held out | candidate held out |
|---|---|---|---|---|---|
| gemmL1x1x10 | 32 | 100.0% | 11 | 5.04% rms | 0.98% rms |
| gemmL1x1x11 | 35 | 68.2% | 8 | 2.60% rms | 1.21% rms |
| gemmL1x1x12 | 38 | 25.0% | 9 | 5.86% rms | 1.03% rms |
| gemmL1x1x13 | 41 | 0.0% | 1 | 6.84% rms | 1.40% rms |
| gemmL1x1x14 | 44 | 0.0% | 8 | 3.51% rms | 1.63% rms |
| gemmL2x1x5 | 29 | 100.0% | 3 | 0.59% rms | 0.82% rms |
| gemmL2x1x6 | 34 | 75.0% | 1 | 3.39% rms | 6.22% rms |
| gemmL2x1x7 | 39 | 14.3% | 5 | 14.58% rms | 8.46% rms |
| gemmL2x1x8 | 44 | 0.0% | 2 | 2.31% rms | 0.76% rms |
| gemmL3x1x5 | 41 | 0.0% | 1 | 9.75% rms | 3.23% rms |
| gemmL3x1x6 | 48 | 0.0% | 1 | 0.87% rms | 0.60% rms |
| gemmL3x1x7 | 55 | 0.0% | 2 | 0.25% rms | 0.24% rms |
| gemmL4x1x4 | 44 | 0.0% | 2 | 4.54% rms | 1.73% rms |

Before the declaration (disclosed, post hoc): at 338 full-mask rgm136 gemmL points with KB >= 3 and footprints of 25-60 MiB, MM1-v3.2 3.92% rms; A's place from the set model 3.62%; every place from it 7.90% (too pessimistic for B). `out/explore/edge_cstar_25_60.txt`.

## 3. The form (registered: `DECLARED-l3s.md` section 3)

Per row half r: dA_r = clip(f_v32,r - f_sa,r, -l3_v32,r, f_v32,r) with f_sa,r the set model's A fresh share and f_v32,r, l3_v32,r MM1-v3.2's own A shares at the constants in use; Q'_r = Q_r + lam dA_r outer((0, 1, -1), B's marginal). Time: MM1-v3.2's engine prices Q' (T' = T + price(Q') - price(Q); lam = 0 is MM1-v3.2 bit for bit). Energy: MM1-v3.2's predictor on Q' (its lines from Q'). Domain: rgm136 gemmL and gemmLnc, rgm211 gemmL and gemmLn at the full mask, any KB; every other point unchanged. Points clipped at the all-data lam: 3.

## 4. The fit (post hoc; every committed time point through E219)

3408 points (E105-E215 as MM1-v3.2's table, E216 46, E217 599, E218 52, E219 203 in-domain runs), 2203 in the domain. lam = 0.690893; in-sample SSE of ln over the domain 4.8770 -> 4.3496. In sample, all points: MM1-v3.2 4.82%, candidate 4.66%; the domain 4.71% -> 4.44%.

## 5. Held out (two-stage)

LOEO (wall cycles; lam refitted without the experiment; MM1-v3.2 at its own fold constants, all-data for E216-E219, which it never saw):

| fold | n | lam | MM1-v3.2 | candidate | no twin n | MM1-v3.2 no twin | candidate no twin |
|---|---|---|---|---|---|---|---|
| LOEO E105 | 73 | 0.695 | 2.47 | 2.47 | 16 | 2.04 | 2.04 |
| LOEO E107 | 224 | 0.685 | 2.85 | 2.85 | 125 | 1.95 | 1.95 |
| LOEO E119 | 63 | 0.697 | 2.55 | 2.55 | 51 | 2.53 | 2.53 |
| LOEO E126 | 46 | 0.682 | 3.27 | 3.27 | 40 | 3.44 | 3.44 |
| LOEO E136 | 36 | 0.697 | 2.03 | 1.09 | 18 | 2.41 | 1.20 |
| LOEO E146 | 108 | 0.686 | 4.78 | 4.74 | 62 | 5.52 | 5.44 |
| LOEO E158 | 102 | 0.729 | 4.53 | 4.47 | 76 | 4.20 | 3.98 |
| LOEO E159 | 13 | 0.685 | 6.39 | 4.40 | 11 | 6.29 | 4.44 |
| LOEO E168 | 14 | 0.692 | 1.11 | 1.30 | 14 | 1.11 | 1.30 |
| LOEO E169 | 54 | 0.677 | 8.04 | 6.56 | 47 | 8.13 | 6.63 |
| LOEO E190 | 36 | 0.670 | 5.24 | 3.47 | 18 | 5.59 | 3.81 |
| LOEO E206 | 232 | 0.673 | 4.11 | 3.79 | 160 | 4.39 | 4.04 |
| LOEO E207 | 53 | 0.691 | 4.35 | 4.01 | 50 | 4.45 | 4.09 |
| LOEO E208 | 184 | 0.693 | 3.44 | 2.66 | 72 | 3.92 | 3.01 |
| LOEO E209 | 46 | 0.700 | 5.34 | 4.97 | 40 | 5.44 | 5.04 |
| LOEO E211 | 26 | 0.684 | 6.90 | 6.12 | 19 | 7.74 | 6.86 |
| LOEO E212 | 478 | 0.734 | 4.70 | 4.59 | 327 | 5.39 | 5.32 |
| LOEO E213 | 118 | 0.716 | 4.31 | 4.38 | 108 | 4.46 | 4.51 |
| LOEO E214 | 518 | 0.631 | 5.84 | 5.72 | 400 | 6.42 | 6.30 |
| LOEO E215 | 84 | 0.657 | 7.02 | 6.54 | 78 | 7.27 | 6.75 |
| LOEO E216 | 46 | 0.694 | 7.10 | 7.05 | 46 | 7.10 | 7.05 |
| LOEO E217 | 599 | 0.766 | 5.68 | 5.73 | 403 | 6.72 | 6.84 |
| LOEO E218 | 52 | 0.705 | 7.24 | 7.48 | 52 | 7.24 | 7.48 |
| LOEO E219 | 203 | 0.691 | 3.31 | 3.22 | 145 | 3.84 | 3.79 |

**Pooled LOEO, no twins (K2):** MM1-v3.2 5.576%, candidate 5.423% (n 2378); with twins (REPORTED) 4.957% / 4.788% (n 3408); E105-E215 only, no twins (REPORTED) 5.293% / 5.030% (MM1-v3.2's own published LOEO no-twin figure is 5.295%; the twin rule here also counts E216-E219 as training, agreeing with MM1-v3.2's flags at 98.5% of E105-E215's points).

LOCO, the EDGE fold and MM1-v3.2's other folds (REPORTED):

| fold | n | lam | MM1-v3.2 | candidate | domain n | MM1-v3.2 domain | candidate domain |
|---|---|---|---|---|---|---|---|
| LOCO aifoundry1 card 0 | 695 | 0.716 | 5.58 | 5.53 | 428 | 5.28 | 5.20 |
| LOCO aifoundry1 card 1 | 1232 | 0.689 | 4.78 | 4.65 | 876 | 4.34 | 4.13 |
| LOCO aifoundry2 card 0 | 824 | 0.710 | 4.89 | 4.43 | 598 | 4.98 | 4.35 |
| LOCO aifoundry3 card 0 | 657 | 0.680 | 4.73 | 4.63 | 301 | 5.53 | 5.36 |
| EDGE (32, 48] MiB | 187 | 0.722 | 4.89 | 4.47 | 187 | 4.89 | 4.47 |
| REPORTED LOEO E212 a1c1 | 203 | 0.719 | 4.32 | 4.23 | 156 | 3.84 | 3.70 |
| REPORTED LOEO E212 a1c0 | 100 | 0.699 | 5.02 | 4.87 | 76 | 4.21 | 3.97 |
| REPORTED LOEO E212 a2c0 | 175 | 0.723 | 4.73 | 4.60 | 124 | 4.19 | 3.98 |
| REPORTED LOEO E213 A | 86 | 0.713 | 4.67 | 4.70 | 64 | 4.13 | 4.17 |
| REPORTED LOEO E213 B | 32 | 0.714 | 3.18 | 3.38 | 32 | 3.18 | 3.38 |
| REPORTED LOEO E214 a1c0 | 221 | 0.663 | 6.19 | 6.10 | 140 | 5.82 | 5.66 |
| REPORTED LOEO E214 a1c1 | 297 | 0.665 | 5.36 | 5.18 | 211 | 4.77 | 4.48 |
| REPORTED LOEO E215 A | 55 | 0.684 | 6.80 | 6.50 | 35 | 6.05 | 5.51 |
| REPORTED LOEO E215 B | 29 | 0.674 | 6.43 | 5.39 | 21 | 5.73 | 3.98 |
| REPORTED LOKO rgm211 gemmLn | 24 | 0.683 | 6.71 | 5.80 | 24 | 6.71 | 5.80 |
| REPORTED LOKO rgm211 gemmL | 5 | 0.691 | 3.55 | 3.66 | 5 | 3.55 | 3.66 |
| REPORTED LOKO gemmLnc | 14 | 0.690 | 6.49 | 6.63 | 14 | 6.49 | 6.63 |
| REPORTED LOKO run_gemm | 426 | 0.683 | 2.85 | 2.85 | 0 | - | - |
| REPORTED LEAVE rgm211 out | 29 | 0.683 | 6.27 | 5.49 | 29 | 6.27 | 5.49 |
| REPORTED LOLO compact | 227 | 0.662 | 5.58 | 5.58 | 0 | - | - |
| REPORTED LOLO spread | 107 | 0.705 | 7.50 | 7.50 | 0 | - | - |
| REPORTED LOLO other | 73 | 0.687 | 7.16 | 7.16 | 0 | - | - |

**The lead's fold (K1):** LOEO E215 (lam 0.6568) at the four gemmL2x1x7 points: MM1-v3.2 14.49%, candidate 8.68% (each: -13.90, -15.50, -13.83, -14.65% -> -7.74, -9.97, -7.68, -9.11%).

**Placebo (K3):** the real feature's in-sample SSE gain 0.5274; the placebos' median 0.0020, largest 0.0137; beaten in 100 of 100.

**Where it is worse (held out):** LOEO E168, E213, E217, E218 (the table); E218's domain points 8.01% -> 8.33% and E217's 4.99% -> 5.08%. The set model is too pessimistic for A at small overflows (34-38 MiB), and lam is one number for every shape.

## 6. Energy (REPORTED, never deciding)

W over idle given the measured op time, both by MM1-v3.2's predictor at its all-data energy constants (none refitted), at points of 3 W and above (`scripts/energy_rep.py`, `out/fit/energy-l3s.json`):

| set | n | MM1-v3.2 | candidate |
|---|---|---|---|
| E105-E215 (in sample), re-made to 1e-6, all | 1598 | 4.70 | 4.66 |
| E105-E215 (in sample), re-made to 1e-6, domain | 1168 | 3.99 | 3.91 |
| E105-E215 (in sample), not re-made (this call's MM1-v3.2 differs from its table), all | 496 | 5.58 | 5.57 |
| E105-E215 (in sample), not re-made (this call's MM1-v3.2 differs from its table), domain | 319 | 3.99 | 3.97 |
| E216-E219 (MM1-v3.2 held out), all | 722 | 6.03 | 5.91 |
| E216-E219 (MM1-v3.2 held out), domain | 468 | 5.51 | 5.32 |

This call re-makes MM1-v3.2's own table at 1598 of E105-E215's 2,094 energy points to 1e-6; the others take per-run minions, governed base or volts this call does not pass (the largest difference 88%), so their rows compare the two models under one call only.

## 7. E220's frozen forecasts (blind)

`forecasts-e220-l3s.csv` (sha256 `ff46a16ec6c83eb3464090db1c9295d9b75338309785f0f965d3d99039f42a2e`) and `forecasts-e220-l3s.json` (sha256 `ac65c9596f5611c95899b1c5105eee137602d5afbe00dfa316582ea651b753a8`), final **2026-11-20 05:56:55 PST**, before any E220 datum: 'MM1-v3.2 + L3S' at lam 0.690893306 with MM1-v3.2 beside, for every point of reg-e220's POINTS.txt (sha256 `058984a04b90cd8585cb41cc6618430306d7bf1c7e230159e7719b9e9e1e9bdc`): arm A aifoundry1 card 1 at 600 MHz (84 points), arm B aifoundry2 card 0 at 799 MHz (74) with 700 and 600 MHz columns: 306 rows. Each row: wall cycles an op, the counter's mean, the op time, seconds a GEMM, W over idle at the forecast t and its A + B / t form (W given a measured t), J over idle with t forecast, J at rest by the rest law (REPORTED). The MM1-v3.2 column equals reg-e220's registered MM1-v3.2 forecasts to 5e-9 (relative) at all 306 rows.

E220's L3 family at its registered clocks (the term's blind test; op time and W over idle at the forecast t):

| arm | id | token | MHz | set model: A kept (r0, r1) | MM1-v3.2 T_op us | candidate T_op us | change | MM1-v3.2 W | candidate W |
|---|---|---|---|---|---|---|---|---|---|
| A | l01 | gemmL10x1x1 | 600 | 0.00, 0.00 | 2.1511 | 2.2899 | +6.25% | 17.54 | 16.67 |
| A | l02 | gemmL4x1x3 | 600 | 0.62, 0.62 | 1.6965 | 1.7799 | +4.80% | 22.08 | 21.21 |
| A | l03 | gemmL3x1x4 | 600 | 0.75, 0.75 | 1.6395 | 1.6883 | +2.94% | 22.60 | 22.05 |
| A | l04 | gemmL7x1x2 | 600 | 0.00, 0.00 | 2.2900 | 2.3329 | +1.86% | 17.21 | 16.96 |
| A | l05 | gemmL11x1x1 | 600 | 0.00, 0.00 | 2.3066 | 2.3380 | +1.35% | 16.64 | 16.46 |
| A | l06 | gemmL2x5x9 | 600 | 0.52, 0.48 | 2.0727 | 2.1265 | +2.57% | 18.80 | 18.43 |
| A | l07 | gemmL12x2x2 | 600 | 0.50, 0.50 | 1.9178 | 1.9178 | -0.00% | 20.14 | 20.14 |
| A | l08 | gemmL2x13x3 | 600 | 0.92, 0.92 | 1.8992 | 1.8992 | -0.00% | 20.47 | 20.47 |
| B | l01 | gemmL10x1x1 | 799 | 0.00, 0.00 | 2.0002 | 2.1400 | +6.76% | 32.33 | 30.85 |
| B | l02 | gemmL4x1x3 | 799 | 0.62, 0.62 | 1.5331 | 1.6183 | +5.41% | 40.09 | 38.50 |
| B | l03 | gemmL3x1x4 | 799 | 0.75, 0.75 | 1.4749 | 1.5248 | +3.33% | 41.12 | 40.10 |
| B | l04 | gemmL7x1x2 | 799 | 0.00, 0.00 | 2.1394 | 2.1831 | +2.02% | 31.47 | 31.03 |
| B | l05 | gemmL11x1x1 | 799 | 0.00, 0.00 | 2.1568 | 2.1884 | +1.46% | 30.77 | 30.46 |
| B | l06 | gemmL2x5x9 | 799 | 0.52, 0.48 | 1.9100 | 1.9650 | +2.84% | 34.25 | 33.59 |
| B | l07 | gemmL12x2x2 | 799 | 0.50, 0.50 | 1.7600 | 1.7600 | -0.00% | 36.44 | 36.44 |
| B | l08 | gemmL2x13x3 | 799 | 0.92, 0.92 | 1.7329 | 1.7329 | -0.00% | 37.08 | 37.08 |

Points the term moves by more than 0.5% in op time (both arms): l01 (gemmL10x1x1), l02 (gemmL4x1x3), l03 (gemmL3x1x4), l04 (gemmL7x1x2), l05 (gemmL11x1x1), l06 (gemmL2x5x9), xf01 (gemmL2x16x3), xf02 (gemmL10x16x3), xf05 (gemmL11x16x3), xf06 (gemmL12x16x3), xf07 (gemmL13x16x3), xf10 (gemmL14x16x3), xf11 (gemmL15x16x3), xf12 (gemmL16x16x3), xg01 (gemmLnc2x6x8), xg01t (gemmL2x6x8), xg02 (gemmLnc2x6x7), xg02t (gemmL2x6x7), xg03 (gemmLnc2x5x8), xg03t (gemmL2x5x8), xg09 (gemmLnc5x1x3), xg09t (gemmL5x1x3). Every subset-mask point (Y2, the X family's Y twins) is MM1-v3.2 unchanged.

## 8. Checks

- Before the declaration (`scripts/validate.py`, `out/data/validate.json`): MM1-v3.2's engine re-makes its table's all-data op times (max relative difference 0) and its frozen E218 forecasts (0); the price split re-makes the engine (4.4e-16); lam = 0 equals MM1-v3.2 bit for bit (True).
- `scripts/l3s_feature.py --check`: the fast feature equals the general set model (`scripts/l3sim.py`) at 6 of 6 shapes (difference 0).
- Every LOEO fold's MM1-v3.2 constants re-make MM1-v3.2's own held-out predictions at its test points (worst relative difference 0.0e+00).
- `scripts/crosscheck.py` (`out/fit/crosscheck-l3s.json`): the predictor path the freeze uses re-makes the fit's op times (max relative difference 0); a 1,001-value grid puts the SSE minimum at lam 0.691 (the fit 0.6909); the lead's four held-out errors re-made from scratch to 2.5e-14 points.
- This folder's own scripts, run from a scratch copy of it with ET_LAB set to the lab clone (`out/checks/landtest.txt`): the feature check PASS; `out/data/points_all.json`, `out/data/validate.json` and `out/fit/crosscheck-l3s.json` re-made byte for byte; `forecasts-e220-l3s.csv` re-made byte for byte; the fit re-run (`out/checks/landtest-fit.txt`) equals `fit-l3s.json` in every field but its two times and its elapsed-time log line.
- NOT RUN: an independent verifier of this lane (the round's check and verify lanes); a re-fit of MM1-v3.2's own constants jointly with lam; the held-out energy by fold.

## 9. Departures, gaps

- No departure from `DECLARED-l3s.md` in the fit, the folds, the keep rule or the freeze. `scripts/energy_rep.py` was changed after its first run to split the energy rows by whether the predictor call re-makes MM1-v3.2's table (REPORTED only).
- The term moves A only, at the full mask only; the set model is too pessimistic for B (7.90% with every place from it) and for A at small overflows (gemmL2x1x6: 75% kept against about 89% implied), which a single lam (0.69) averages.
- The pool layout is an assumption (one arm a device process); a kit that runs several arms in one process grows its buffers and can move the pools' relative addresses, and so the sets.
- Mode M0 is the reset mode and the lab's documented split; no shire-cache ESR was read on any card this round.
- KB <= 2: the set model counts the shires' L2 hits as L3 accesses (the term uses fresh shares, so an L2 hit sits inside the set model's hits); four of E220's eight L3 points are at KB <= 2.

## 10. Files, and how to re-run

- `DECLARED-l3s.md`, `DECLARED-l3s.sha256`: the declaration, hashed before the fit.
- `scripts/`: the feature (`l3s_feature.py`, `l3sim.py`), MM1-v3.2's prices split (`costs.py`), the term (`term_l3s.py`), the data (`data_all.py`), the checks (`validate.py`, `crosscheck.py`), the fit (`fit_l3s.py`), the freeze (`e220_l3s.py`), energy (`energy_rep.py`), the exploration (`walk_explore.py`, `edge_cstar.py`), and `REWRITES.tsv` (each script's sha256 as run and here: the round's folder paths rewritten to this folder's layout, nothing else).
- `out/`: the points (`data/points_all.json`), the feature (`feature/l3s_cache.json`), the fit and held-out record (`fit/fit-l3s.json`, `.txt`), energy, the checks, the exploration.
- `fit-l3s.json`, `fit-l3s.txt` (a copy at this level, as frozen with the forecasts), `forecasts-e220-l3s.csv`, `.json`.
- Re-run from the lab root with ET_LAB set to it: `python3 -I -B scripts/data_all.py`, `scripts/l3s_feature.py --points out/data/points_all.json --cache out/feature/l3s_cache.json`, `scripts/validate.py`, `scripts/fit_l3s.py`, then `E220_POINTS_TXT=<reg-e220 POINTS.txt> scripts/e220_l3s.py`, each with the four thread variables at 1.
