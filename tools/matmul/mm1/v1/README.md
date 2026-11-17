# MM1-v1: the lab's matmul model, frozen for the blind matmul day (Mon 16 Nov 2026)

MM1-v1 predicts a matmul's clock cycles, seconds, joules (over idle and with the card at rest) and transistor switches on the ET-SoC-1
cards from the matrix size, the format, the data kind, the shire mask, the card and the clock, with the timing simulation's two columns
beside every forecast. It is MM1-v0 (`../v0/`, frozen before E206) rebuilt after E206 arm A's data: it answers the adversarial check of
v0's spec and the blind score of v0 on E206, and it is fitted on every measured point, E206 included. This folder holds the model as
frozen: the code, every input it reads (vendored and hashed), its fit and held-out record, and **its forecasts for the blind matmul day's
53 never-run points, with today's models F1 and F2 frozen beside**. Desk only: this commit measured nothing.

The owner's words that started the matmul model (Mon 16 Nov 2026, at or before 09:48:24 PST; a voice transcription, where "matte mold"
is the matmul): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number
of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See
check how well the timing simulation for the matte mold matches reality and the energy."

**Labels.** *Measured*: a card's committed reading. *Desk*: arithmetic or a fit made at a desk. *Post hoc*: fitted after its data existed
(every constant of MM1-v1 is). *Held out*: left out of that fit (one experiment or one card at a time); held out is not blind. *Blind*:
scored on data that did not exist when the model was frozen. *In sample*: the data were in the fit. A check not run is NOT RUN. Error =
forecast / measured - 1; rms and bias in %. Interpreter for every number: `/usr/bin/python3` 3.12.3, numpy 1.26.4, scipy 1.11.4, run `-I -B`.

## 0. On one screen

- **Scope** (in every output's `scope` field): rgm136's GEMM `gemmL<MB>x<NB>x<KB>` on its grid (M = 1,024 MB, N = 512 NB, K = 512 KB w,
  w = 1/2/4 for fp32/fp16/int8; off-grid sizes padded) and the run_gemm calibrating arms; a shire mask runs the masked shires only.
- **What changed from v0** (section 4): an L2 time in the gemmL loop (fixes int8 at one K block); two power-of-two stride terms (fix the
  E206 stride step and the power-of-two split); a shire-count contention term and a row-group imbalance on the counter's mean (subsets);
  a memory-path awake power that does not scale with the minions (subset energy); the kind term (real tiles, e37, designed tiles); a rest
  law (REPORTED); the switch estimate's scope (the die, the fresh-line path apart); every input of MM1-v1 vendored (F1/F2's route pinned and
  recorded). **The masked map was built, tied exactly to E206's
  registered lines, then tested: it lost on every fold, so MM1-v1's own subset forecasts use the full chip's lines; F1 and F2 use it.**
- **Held out, the same folds for both** (desk, post hoc; section 5): cycles LOEO **4.70%** for v1 against **5.91%** for v0's form
  refitted; E206 held out 6.47% against v0 blind 9.00%. J over idle with seconds forecast LOEO 7.33% against 8.12%.
- **On E206** (section 5.2): v0 BLIND 9.0% cycles, 8.4% J over idle given the seconds; v1 IN SAMPLE 4.5% and 5.7%; v1 HELD OUT (E206's
  fold) 6.5% and 7.0%.
- **The blind day** (section 8): 53 points on aifoundry3 card 0, every one never run anywhere (47 distinct (shape, format, mask) cases for
  time); v1 and F1 differ by 15.5% rms in cycles (51 of 53 points by more than 3%); v1 and F1 by 38% in W over idle, v1 and F2 by 37% in J
  over idle. **These forecasts are blind only once the orchestrator records their sha256 (section 1) before the day's first datum.**
- **Fixed before the land** (verify-mm1v1: HOLDS WITH FIXES; section 11), the record only: E206's held-out counter mean is 7.87%, not 6.37%
  (that figure fits the row-group imbalance on 4 of E206's own points); the subset terms held out by mask with every constant refitted give
  7.53% against 10.61% with no subset term (not 6.77% against 11.67%); the never-run scan was redone at E206's own standard; F1/F2's route is
  pinned and recorded. **No forecast changed: the seven freeze-line files are byte for byte the same.**

## 1. The freeze line

| file | sha256 | what |
|---|---|---|
| `out/mm1_v1_blind_day.csv` | `90dffe943d611d139e091f481a32f6e04207d17937fd6cca96744658488032c6` | **MM1-v1's forecasts for the 53 points** |
| `out/mm1_v1_params.json` | `4e97654ea01e293bc61fab0fa73e8c25128af574a602e7384a14683d3b208408` | the frozen constants |
| `mm1_v1.py` | `6bed4a5b2b441b4464a4c320cb0b5ecb09f42aa1403ff8fb25e705cf5a680a52` | the predictor |
| `mm1_core.py` | `3e6ff68dfe4f7eb7e2af5873a8b6df52823cc5daa95066d8292d827ada0d84aa` | the equations |
| `kinds_v1.py` | `29728e43ce3a17ad8cdfbe8a60ba12f4a5a9aa73fb603b71b62b9b4e7d742e6a` | the kind term |
| `out/f1f2_blind_day.json` | `2f252ebdfd0ada66684a71adceb2f227ca559818b1bfb188322378296641a3d0` | F1 and F2 generalized with the masked map (beside) |
| `out/f1f2_blind_day.csv` | `8ff5e73a077e02513b15ff15a4067ab839186b3b56519118e6774376b5a46645` | the same, one row a point |

`SHA256SUMS` lists every file here. `out/mm1_v1_blind_day.json` carries the parameter file's sha256 and every point's full record. The seven
files above are byte for byte those of mm1-v1's first freeze (its local commit c3130350); fix-mm1v1 changed records, wording and two scripts
and added four files; every forecast file reproduces byte for byte from the fixed code (section 11).

## 2. What MM1-v1 computes (mm1_core.py)

**The map** (closed form; no constant fitted to a shape):
- an op of a shire requests 192 lines: A 64 (4 tiles x 16 lines) and B 128 (8 tiles x 16); each line is served by the L2, the L3 or fresh
  from DRAM;
- design B's LRU stack distances (`inputs/linemap.py`), the lab's desk L2 model per shape for KB <= 2 (`inputs/l2_lab.json`, or a run of
  `inputs/reuse_e136.py` for a shape not there), a logistic L3 retention `r(d) = 1 / (1 + exp((d - x50)/s))`;
- **with the mask** (`groups_masked`): every distance is a sum of A terms (row panels), B terms (column panels) and C terms (blocks); a mask
  touches R of 8 row groups' A tiles, C of 4 column groups' B tiles and n of 32 shires' C tiles, so each term scales by R/8, C/4 and n/32. At
  the full mask it is design B's map number for number. **The tie** (`out/tie_masked_map.json`, run before any fit): at strict caps of 32, 28
  and 24 MB it gives E206's registered LRU lines (`inputs/reuse-e206.json`) on all 21 subset shape-cap rows with a difference of 0.000
  lines, and stays within 0.23 lines on the 114 full-chip rows. MM1-v1's frozen form maps subsets at the full chip's lines (section 4.1).

**Cycles** (wall basis, the slowest minion; us an op at the launch clock f in MHz):
```
T_op = 1/2 sum_ab Q0[a,b] max(Tc, kA tau_A[a], tau_B0[b]) + 1/2 sum_ab Q1[a,b] max(Tc, kA tau_A[a], tau[b])
tau[L2] = T2 (the gemmL loop; 0 in run_gemm's); tau[L3] = c3/f + m3 X; tau[F] = cF/f + mF X; tau_B0[F] = tau[F] (1 + piF0 [NB a power of two >= 4])
Q0: the row half r = 0 (A with B's far group B_r0); Q1: r = 1 (A with B's second use B_r1); B_r1's L3 retention x zeta when NB is a power of
two >= 4 and the footprint exceeds 32 MB; Tc = E119's c1 law, never below the floor (529 / 270 cycles); X = 1 - chi (1 - n/32) on a subset
cycles (wall) = T_op f; the counter's mean = wall / rho (the scorecard's regime medians) / rho_imb (row-group imbalance, R < 4 of 8 with C = 4)
seconds a GEMM = 64 MB NB KB x T_op
```
**Joules over idle** (`W = A + B / t_op`, the affine form the given-seconds score uses):
```
W = Pmin(card) n/1,024 + Pmem u + g [B(f) - B(600)] + (n / t_op) s_V [e_res(card, fmt, kind) + sum_l n_l/32 (b_l + d_l phi(kind))]
u = (n_L3 + n_F) / 192 (the memory path awake for any active shire); s_V = (V / 0.517 V)^2; J over idle = W t; J at rest = P_rest t + J over idle
```
- `e_res` (nJ an op at 600 MHz) is never refitted: ledger v2's frozen resident price `(Z_w + D_w) / R` (`inputs/ledger_frozen-v2.json`); for a
  kind with no ledger row, a committed per-tile frozen prediction (blind4: M6; blind3: M5); otherwise energy NOT FORECAST.
- `phi` (random 1, zeros 0): `(64 h(A) + 128 h(B)) / 192` over the format's randn, `h = 0.70 rho/0.5 + 0.30 tau/0.5` (E101's w_set form):
  rho the share of set bits, tau the share that change line to line; a tile file from its bytes, a generator kind (randn, sparse50, sparse25,
  e37) from its law (rgm136's host draws every element independently).
- **The rest law (REPORTED):** ledger v2's frozen idle law for aifoundry3 at a forecast die of 54.4 C (E206 arm A's median start, 52.5-55.0
  C); on E206's 119 points at each run's own die it reads +0.054 W mean, 0.077 W rms against the measured rest. The scored J at rest uses
  the run's measured rest.

**The timing simulation's two columns** beside every forecast: sys_emu's instruction count (mm-timing's step law, 46.625 an op + 24.25 a
C-tile row + 92 a launch; one step an instruction, not time) and the floor: `floor_cycles_measured_tenb` (529 / 270, **measured**: E101's tenb
loop, a post hoc closed form) and `bench_resident_cycles_simulated` (546 / 318: the RTL bench with A and B resident, exact, 306 points blind).

## 3. The constants (out/mm1_v1_params.json; desk fits, post hoc)

| constant | value | fitted on / identified by |
|---|---|---|
| c3, m3 (the L3 stream) | 324.4 cycles, 0.822 us | 888 time points; two clocks only on aifoundry2's governed windows |
| cF, mF (the fresh stream) | 401.7 cycles, 1.661 us | the same |
| kA (A's stream over B's) | 1.067 | shapes whose A and B places differ; the operand split is unmeasured (section 6) |
| x50, s (L3 retention) | 43.6 MB, 7.14 MB | shapes past 32 MB |
| T2 (the L2 time in the gemmL loop) | 0.614 us (368 cycles at 600 MHz) | int8 gemmL at KB <= 2 (E136, E146 at 730-793 MHz; E206 at 600) |
| zeta (B_r1's L3 retention, power-of-two NB past 32 MB) | 0.679 | E158, E169, E206 |
| piF0 (B_r0's fresh stream, power-of-two NB) | 0.169 (17% slower) | the same |
| chi (subset contention on the fixed latencies) | 0.200 | E206's 14 subset points only |
| eta (row-group imbalance on the wall) | 0 (fitted) | the same |
| rho_imb (the counter's mean only): eta_m, gamma | 0.214, 2.54 | E206's wall / mean at 0xf and 0xff (4 points) |
| Pmin (awake, per minion) | aifoundry3 1.439 W, aifoundry2 1.956 W, card 1 3.257 W (at 1,024 minions) | 791 energy points |
| Pmem (memory path awake, one for every card) | 0.278 W at u = 1 | mainly E206's subsets |
| b2, d2 / b3, d3 / bF, dF | 50.5, 499.6 / 201.5, 1,063.5 / 754.7, 1,282.1 pJ a line a shire-op | zeros (b) and random (d) at every place |
| g (governed base share) | 0.810 | aifoundry2's governed windows |
| Tc (c1 law), the floors, rho by regime, volts | E119's fit; 529 / 270; 1.006 / 1.126 / 1.011 / 1.143 / 1.001 | fixed, as in v0 |

## 4. What changed from MM1-v0, finding by finding

### 4.1 The adversarial check of v0's spec (mm-critic, HOLDS WITH FIXES)

| finding | what v1 does |
|---|---|
| F1 MAJOR: subsets mapped at the full chip's footprint | **Built and tied the masked map** (above: exact on E206's 21 subset rows, before any fit). **Then tested it as v1's subset map on the same folds (the chosen form and its masked twin): it lost every time** (in sample on E206's subsets 10.8% against 5.7%; LOEO all 4.82% against 4.70%; E206 held out 7.05% against 6.47%), as v0's blind score had read: a one-shire GEMM runs at 0.88 of the full chip, not at the all-L3 speed the masked lines give. v1 maps subsets at the full chip's lines with a contention term on the fixed latencies (chi) and a row-group imbalance on the counter's mean. Leave one mask out with every constant refitted from a cold start without the mask (`subset_lomo_v1.py`, `out/subset_lomo_v1.json`): **7.53%** (bias +1.0%; 0x1 7.1, 0x11111111 2.5, 0xf 6.1, 0xff 7.4, 0xffff 12.0%) against **10.61%** for the form with no subset term held out the same way (10.27% refitted on all 888 points, in sample); at 0x1 alone the form without the term is closer (5.3%). (mm1-v1's first figures, 6.77% against 11.67%, refit chi alone at the all-data fit and zeroed chi without a refit: `holdout_v1.json`, `subset_leave_one_mask_out`, chi only; verify-mm1v1 finding 2.) The masked map stays in the code (`Shape(..., masked_map=True)`), and F1 and F2 use it on the blind day. |
| F2 MEDIUM: no head-to-head rule | F1 and F2 are generalized to the 53 points with the masked map and frozen beside (`out/f1f2_blind_day.*`). The paired rule itself is E207's registration. |
| F3 MEDIUM: switch scope | Section 7: the die, with the whole fresh-line path set apart (the DRAM devices and the on-die memory-shire and PHY share alike); the regulators' loss out at the low and central estimates (the high one keeps it); leakage out; the counted netlist's own energy is what is subtracted; the int8 arithmetic is an estimated class. |
| F4 MEDIUM: "from sizes and operations" holds for rgm136 only | Stated in every output's `scope`; a new kernel needs its own map (a stack-distance desk run over its tile order: NOT RUN here). |
| F5 MINOR: the TenB floor labelled as simulated | Two columns, labelled: measured (E101 tenb, post hoc closed form) and simulated (the bench, resident B). |
| F6 MINOR: the pooled time score repeats shapes | Every blind-day point carries its case (`arm|format|mask`): 47 cases for 53 points. |
| F7 MINOR: points under the meter's floor | Flagged `scored_in_watts` (W over idle under 3 W): b34, b38, b40. On E206's 8 such points v1 is 0.14 W rms held out (v0 blind about 0.3 W). |
| F8 MINOR: the form question stays open | Three long-K points added (n04-n06); **v1 carries no RSW second forecast: the day does not decide MAXAB against RSW.** |
| F9 MINOR: unhashed inputs; the predictor refits at load | Every input of MM1-v1 vendored with its source and sha256 (`inputs/MANIFEST.json`, 44 files; F1 and F2 read the lab at run time, pinned and recorded: section 8); the predictor reads only the frozen parameter file and `inputs/`; the parameter file is written by `fit_v1.py` from `inputs/` and reproduced byte for byte from this folder. |
| F10 NIT: three held-out claims | Reworded in section 5.3. |

### 4.2 v0's blind score on E206 (mm1v0-e206, SCORED WITH GAPS)

| finding | what v1 does | on E206 |
|---|---|---|
| int8 gemmL at one K block 25% slow | **T2**, an L2 time per op in the gemmL loop, clock-free (0.614 us: in cycles it would not carry from aifoundry2's 780 MHz points to aifoundry3's 600 MHz ones, a fold showed). Above int8's 270-cycle floor, under fp32's and fp16's 529: it moves int8 only. run_gemm's c1 loop keeps its own law. | int8 gemmL KB <= 2: v0 blind 19.1%, v1 in sample 6.9%, held out 11.0%; blind test n01-n03 |
| powers of two: the stride step at NB 16 | **zeta** (set conflicts on B's second-use lines in the L3) and **piF0** (B's first-touch fresh stream slower) when NB is a power of two >= 4: B's column panel blocks sit NB MB apart. piF0 alone over-priced long-K shapes (E190 fp32 +10%); with zeta the long-K power-of-two bias is +5%. | the 1x15x4 / 1x16x4 pair: v0 blind 12.9%, v1 held out 3.2% (learnt without E206); blind tests b27-b33, n04/n05 |
| subset cause not the footprint | the masked map tested by fold and rejected (4.1); contention by shire count + row-group imbalance | subsets: v0 blind 11.0%, v1 in sample 5.7%; no fold without E206 can test them (by mask, every constant refitted: 7.53%, section 4.1) |
| subset energy | **Pmem**: the memory path awake for any active shire, not scaled by minions | J over idle on E206's subsets (>= 3 W) 6.0% |
| aifoundry3 energy by regime | refitted with E206 in the fit | J over idle given t on E206: 5.7% in sample (v0 blind 8.4%) |
| gaps: no kind term, no rest law, law arms without ops | the kind term (E206's 6 real points scored, nothing fitted for the kind: 5.6% rms); the rest law (REPORTED); every blind-day point carries its ops | |

## 5. Held out, and E206

### 5.1 The same points and folds for v1 and for v0's form refitted

888 time points (MM1-v0's 769: E105, E107, E119, E126, E136, E146, E158, E159, E168, E169, E190; and E206 arm A's 119, each the mean of its
pass-1 and pass-2 runs) and 791 energy points (design C's 682 zeros/random points and E206's 109). Leave one experiment out (12 folds), leave
one card out (3); cold starts; every constant refitted in every fold, the energy fold on its own time fold's lines and seconds.

| | v1 | v0's form, refitted |
|---|---|---|
| cycles, in sample | 3.82% (-0.3) | 5.31% (-0.5) |
| cycles, LOEO all | **4.70% (-0.0)** | 5.91% (-0.1) |
| cycles, LOEO the 769 pre-E206 points | 4.37% | 5.27% |
| cycles, LOEO gemmL / c-arms | 5.55% / 3.51% | 7.34% / 3.66% |
| cycles, E206 held out (its fold) | 6.47% (+0.3) | 9.00% (-2.5) |
| cycles, LOEO by experiment | E105 2.6, E107 3.6, E119 3.8, E126 3.8, E136 2.4, E146 4.1, E158 6.1, E159 3.2, E168 2.1, E169 7.3, E190 5.0, E206 6.5 | E105 2.1, E107 3.2, E119 1.0, E126 7.7, E136 4.9, E146 6.1, E158 6.1, E159 5.4, E168 2.7, E169 10.2, E190 5.5, E206 9.0 |
| cycles, LOCO aifoundry3 / card 1 | 4.3% / 4.2% | 6.1% / 5.5% |
| cycles, LOCO aifoundry2 (unidentified: see 5.3) | 36.9% | 44.4% |
| W = J over idle given t, LOEO (>= 3 W) | **6.31% (-0.2)** | 6.77% (-0.1) |
| J over idle, seconds forecast, LOEO | **7.33%** | 8.12% |
| J at rest given t / seconds forecast, LOEO | 2.06% / 4.90% | 2.14% / 5.86% |
| W over idle, E206 held out | 7.02% (-3.6) | 8.34% (-5.5) |
| W over idle under 3 W, E206 held out (watts) | 0.14 W rms (n 8) | 0.31 W |
| W over idle, LOCO aifoundry3 / card 1 / aifoundry2 | 21.2% / 14.2% / 42.1% | 24.6% / 15.0% / 41.2% |

LOCO of energy says what v0 found: **the awake power does not carry across cards; every card needs its own GEMM anchor** (aifoundry3 has
E206; card 1 has one shape; aifoundry1 card 0 none).

### 5.2 On E206 arm A, one footing (`out/compare_e206.md`, `compare_e206.py`)

| quantity (n) | MM1-v0 **blind** | MM1-v1 **in sample** | MM1-v1 **held out** (E206 fold) |
|---|---|---|---|
| cycles an op, wall (119) | 9.0% (-2.5) | 4.46% (-0.7) | 6.47% (+0.3) |
| cycles an op, the counter's mean (119) | 9.54% (-2.8) | 4.63% (-1.6) | **7.87% (+0.0)**; 6.37% (-0.7) with the imbalance in sample |
| seconds a GEMM (119) | 9.02% (-2.6) | 4.48% (-0.8) | 6.48% (+0.2) |
| J over idle given t (>= 3 W; v0 and v1-held 101, v1 in sample 107 with the real points) | 8.42% (-5.6) | 5.74% (-1.9) | 7.02% (-3.5) |
| J over idle, seconds forecast (>= 3 W) | 9.15% (-6.0) | 6.10% (-2.1) | 7.57% (-3.7) |
| J at rest given t (measured rest; 109 / 115 / 109) | 2.55% (-1.7) | 1.89% (-0.7) | 2.33% (-1.2) |
| J at rest, seconds forecast (measured rest) | 7.6% (-3.4) | 4.26% (-1.3) | 6.25% (-0.8) |

v0 is blind (frozen 13:04:57 PST Mon 16 Nov 2026, 3 h 48 min before E206's first card command); v1's in-sample column is not a test; its
held-out column is v1 refitted without E206 from a cold start, held out but not blind. The v0 column reproduces the blind scorer's numbers.

**The held-out counter mean** (verify-mm1v1 finding 1) uses the E206 fold's own map and no row-group imbalance: the imbalance
(`fit_v1.fit_imbalance`) is fitted on four of E206's own points (p096-p099, gemmL4x8x4 at 0xf and 0xff), so a fold without E206 leaves it
neutral. With it, the column read 6.37%, in sample for those points: they read 32.3 / 28.0 / 27.9 / 23.5% held out against 9.0 / 5.4 / 18.9 /
14.8% with it, and E206's 14 subset points 17.5% (+14.2) against 11.1% (+8.6). `out/compare_e206.md` carries both rows.

### 5.3 The three held-out claims, reworded (mm-critic F10)

1. **Every constant is refitted in every fold**, time and energy alike (the energy fold uses its own time fold's retention, lines and
   seconds). A constant no training point can move stays at its neutral cold-start value: with E206 held out, chi and eta stay 0, so that
   fold predicts subsets with no subset term. The row-group imbalance on the counter's mean is fitted on four E206 points, so E206's
   held-out counter mean is quoted without it (5.2). Fixed constants fitted on points the folds score (verify-mm1v1's desk checks): Tc
   (E119's c1 law) scores E119's three c1 points in sample (0.47%; 0.20% and 2.6% with the law refitted without E119; E119's fold moves by
   less than 0.1 point); TH0, the cold start, is aifoundry2's own E119/E126 arm laws (from a neutral start the E119, E126 and E206 folds
   move by less than 0.03%, LOCO aifoundry2 from 36.9% to 33.9%); rho (the scorecard's wall / mean medians) touches only the counter mean.
2. **LOCO aifoundry2 is reported from a cold start (36.9% for v1, 44.4% for v0's form) and flagged as unidentified**: with aifoundry2 held
   out only 600 MHz points remain, so no stream's c/f against m split is identified; the number measures the optimizer's path, not the
   model.
3. **The headline numbers are post hoc model selection.** v1's time form is the best of 23 forms and its energy form the second best of 4
   on these same folds (`out/model_selection.json`, recomputed by `select_forms.py`; the energy form with a P_mem per card read 6.22% but
   split card 1's two awake terms arbitrarily (one shape) and gave aifoundry2 a negative one, so v1 keeps one P_mem). The held-out numbers
   are therefore optimistic for the chosen forms. The blind day is the test.

## 6. The operand split, stated

An op's 192 lines a shire-op are 64 A lines and 128 B lines. The walk's two row halves split them: half the ops (r = 0) pair A with B's far
group B_r0, half (r = 1) with B's second use B_r1; A's place does not depend on the half. The run_gemm arms take the lab's own split
(`reuse_e146.arm_split`): c8s and c16 miss A 64 and B 64 lines a shire-op, the other 64 B lines being the second row half's L2 hits. An op
takes the slowest of the compute, A's stream x kA and B's stream; **kA = 1.067 is a desk fit** (v0: 0.840): no card run has isolated A's
stream from B's. Arms where only A misses, or only B, need a kernel arm rgm136 does not have, so the split stays unmeasured.

## 7. Transistor switches: the die, the fresh-line path apart (mm1_core.switches)

**The scope, stated exactly** (verify-mm1v1 finding 5; `mm1_core.py` is frozen and its labels still say "die only"): the estimate is the die's
energy less the whole fresh-line energy, which is set apart unconverted. That energy holds the DRAM devices and also the on-die memory-shire
and PHY share of those lines, so the on-die part of the fresh-line path is not in the count: 0.2-52% of a blind-day point's J over idle
(median 9.7%). The regulators' loss comes out of the low and central estimates; the high estimate divides by 1 + 0 (the band's low end), so
it keeps the regulators' loss as die energy.

One switch is one fin charged or discharged by a net transition. For a GEMM:
- **counted**: the tensor unit's open-flow fin edges a MAC x MACs (fp32 at gate level; fp16 by the RTL ratio; int8 the vector unit only);
- **estimated** (every on-die class with no public netlist, **the int8 arithmetic included**, reported as `of_which_int8_arithmetic`):
  the board's J over idle split by MM1-v1's own terms; **the fresh lines' energy apart** (DRAM devices, the on-die memory-shire and PHY share
  and the path, `fresh_lines_J_apart`, not converted); the rest divided by `1 + c_reg` (the minion regulator's delivery loss from lab finding
  19, E46: 0.181 / 0.188 / 0.102 of the rail on aifoundry3 / aifoundry2 / card 1; band 0 to 0.294, the high estimate at 0); less the in-run
  leakage `0.47 W/C x (0.12-0.145 C/W x W) x t`, less the
  governed base's leakage share (finding 16: 55-80% of an idle card, 65% central), **less only the counted netlist's own energy** (the
  glitch README's measured end to end 1.925 pJ zero delay / 2.706 pJ timed for a random fp32 multiply-add, scaled by fin edges and volts);
  then `/ s_V x kappa_die` (2.20, 3.97, 4.86 x 10^16 fin edges a die joule: the counted fin edges over the resident op's die energy; the
  counted netlist's own; every joule on signal nets).
- Worked example, MM1-v1 on E190's 8,192^3 random GEMM (in sample), at the fit's own footing (card 1 at s_V = 1, i.e. 0.517 V, as the fit
  carries every card-1 energy point; the clock of the run's committed row, 599.0 MHz): card 1 fp32 1,538 cycles an op (measured 1,450),
  0.336 s, 5.75 J over idle (measured 5.31-5.38 J in the bursts, 6.50-6.51 J sustained); counted 3.9-5.9 x 10^16, estimated 3.5 / 9.7 / 15.0
  x 10^16 (low / central / high), fresh lines 1.27 J apart. Card 1 int8 (gemmL8x16x4): 1,357 cycles an op (measured 1,374), 0.074 s, 0.75 J
  over idle (measured 0.72-0.83 J); counted 1.1-1.5 x 10^15 (the vector unit), estimated 0.76 / 1.7 / 2.4 x 10^16, of which the int8
  arithmetic 4.6 x 10^15 (central), fresh lines 0.19 J apart. (mm1-v1's first README printed this example off the fit's footing, at about
  0.50 V: 5.44 J, 3.6 / 9.9 / 15.4 x 10^16, 1.18 J; verify-mm1v1 finding 6. The blind day is unaffected: aifoundry3 at 0.522 V.)
- **Not scorable**: nothing on a card measures switches.

## 8. The blind matmul day (out/mm1_v1_blind_day.csv, blind_day_v1.py)

**Card**: aifoundry3 card 0 at its pinned 600 MHz, rgm136 unchanged (E206's build and host flags), reads only. **53 points, 47 cases**:

| family | points | shapes (gemmL MBxNBxKB) |
|---|---:|---|
| inside the L3 | 9 | 1x3x2 (fp32, int8, fp16), 2x3x2, 3x2x2, 1x4x3 (fp32, int8) |
| the knee | 9 | 1x9x3, 3x3x4, 5x2x3 (fp32, int8), 2x3x5 (fp32, int8, fp16) |
| past the L3 | 8 | 3x5x5 (fp32, int8), 5x3x6, 2x6x10 (fp32), 1x3x24 (fp32, int8), 6x6x6 (fp32, fp16) |
| stride | 7 | 1x7x6 / 1x8x6 / 1x9x6 (fp32; 1x7x6, 1x8x6 int8), 1x4x12 against 1x5x10 |
| subsets | 8 | 3x6x4 at 0x3, 0xfff, 0xffffff, 0x0f0f0f0f (fp32; 0x3, 0xffffff int8); 1x2x2 at 0x3, 0xfff |
| kinds | 6 | e37 (the host's +-1/+-2 generator) at 1x3x2, 3x5x5; blind4's real tiles at 1x3x2 (fp32, fp16, int8); blind3's constant-column A at 3x5x5 |
| int8 one K block (new) | 3 | 1x3x1 int8, 3x5x1 int8 and fp32 |
| long K (new, mm-critic F8) | 3 | 1x7x16, 1x8x16 (fp32), 2x3x16 int8 |

- **Revised from mm-synth's 54-point plan**: per-case time scoring; b34, b38, b40 flagged for watts; the int8 one-K-block and long-K points
  added; seven points dropped with their reasons (`out/mm1_v1_blind_day.json`, `dropped_from_mm_synth_plan`): int8 e37 and sparse25 and ones
  have no resident price anywhere, and the designed row-permuted pair's tiles do not exist yet; each dropped point's time duplicated a kept
  case.
- **Never run**: all 53 as points and all 47 cases (`out/neverrun_blind_day.json`; `out/scan_summary.json`), by E206's own scanner at E206's
  own standard (fix-mm1v1, 20:37-20:38 PST Mon 16 Nov 2026): all of the lab at GitHub main 76fb5344 (64,491 files, E208's five released
  sessions' data among them), the round's lane folders (306,628), all of the lab account's work folder on aifoundry2 (124,501), aifoundry3's
  run folders (1,981, read only by verify-mm1v1 at 20:19 PST), and the model session's planned sweep (E208, 1116-mmsweep, its arms.json,
  planned or run). mm1-v1's first scan (about 19:31-19:32 PST; its record said 20:3x) read only the lab's docs and tools, the lane folders and
  the sweep folder (958 files of the work folder), with the same verdict. Not scanned: aifoundry1's own folders (the model session's box;
  its three released sessions are in the lab's data). **Re-check at E207's registration and right before its first card command.**
- **Planning** (not forecasts of the peak): 26.0 W high-side rest + 1.10 x W over idle + 1 W gives at most 53.3 W (n03, b01); about 106
  scored runs + 3 ties at E206's 21-30 s a run, about 45-50 card-minutes with the smoke.
- **Each point's record**: cycles an op (wall and the counter's mean), cycles and seconds a GEMM, W over idle at v1's own rate, the affine W
  (`A + B / t_us`, for scoring given the measured seconds), J over idle, J at rest by the rest law (REPORTED; the scored J at rest uses the
  run's measured rest), lines by place, switches (counted, estimated, int8 arithmetic, fresh lines apart), sys_emu's count and the floors.
- **F1 and F2 beside** (`out/f1f2_blind_day.*`, `f1f2_blind_day.py`): E206's registered routes run unchanged on these points, their lines
  from E136's LRU model at 32/28/24 MB and E206's subset function (the masked map). F1 prices every point's cycles and seconds, and the
  energy of the random and blind4 real points (its real rule); F2 prices random and e37 fp32 (the ledger's `fp32.small_int`, whose own text
  names E37's fill; rho = tau = 0.1406 from e37's bits). NOT PRICED: F1 energy for e37 and blind3; F2 for blind4 and blind3. **Their route
  is not vendored** (verify-mm1v1 finding 4): `f1f2_blind_day.py` imports E206's `forecast_e206.py` (and through it E190's route, ledger v3
  and their data) from the lab at run time. It pins the three files it names by full sha256 and stops on any difference; `out/f1f2_route.json`
  (`f1f2_route.py`) records all 33 files the route reads (13 modules, 20 data files) with their sha256, and `f1f2_route.py --repo <the lab's
  top> --check` compares a lab copy with that record (33 of 33 at GitHub main 76fb5344).

## 9. Gaps and NOT RUN

- One card and one clock on the blind day; card 1 and aifoundry1 card 0 have no awake anchor beyond one shape / none.
- No RSW second forecast: the day does not decide MAXAB against RSW.
- The masked map, the subset terms and the row-group imbalance rest on E206's 14 subset points (5 masks); a mask holding 2 of 4 column
  groups (0x3) gets no imbalance term (untested layout).
- kA, the operand split, is a desk fit; no operand-split arm exists in rgm136.
- The kind term's phi convention (line-to-line changes within a tile) is untested on the card's real line order; blind4's and blind3's
  resident prices are frozen predictions (M6, M5), not measured anchors.
- The rest law's forecast die (54.4 C) is E206's; the blind day's own start die may differ.
- The governed base's leakage share and the regulator share are bands read from findings 16 and 19, not measurements.
- F1 and F2 are not vendored: they read the lab at run time, pinned and recorded (section 8).
- NOT RUN: any card or simulator; any remote command by MM1-v1 or its fix (the aifoundry3 scan is verify-mm1v1's, read only); a scan of
  aifoundry1's own folders; a counted sys_emu run of a blind-day shape; leave one format out; a stack-distance desk run for any other kernel;
  F1/F2's own registered given-seconds evaluation on the blind day (that is E207's scorer's).

## 10. Files and how to reproduce

- **Code**: `mm1_core.py` (the equations), `mm1_v1.py` (the predictor), `kinds_v1.py` (the kind term), `data_v1.py` (the measured points),
  `fit_time.py`, `fit_energy.py`, `fit_v1.py` (the fit and folds), `select_forms.py` (the selection table), `tie_masked_map.py` (the tie),
  `blind_day_v1.py` (the day), `f1f2_blind_day.py` (today's models), `compare_e206.py` (v1 beside v0), `subset_lomo_v1.py` (the subset terms
  held out by mask, every constant refitted), `f1f2_route.py` (F1/F2's route recorded and checked).
- **inputs/**: 44 files, each with its source and sha256 in `inputs/MANIFEST.json` (byte for byte from GitHub main d7e4f35e, except two
  extracts: `time_points.json`, the 769 points from the round's design-B table, and `predictions-blind3-extract.json`, the one blind3 entry read).
  "Every input vendored" covers MM1-v1; F1 and F2 read the lab at run time (section 8).
- **out/**: `mm1_v1_params.json`, `holdout_v1.json`, `points_time_v1.csv`, `points_energy_v1.csv`, `e206_v0_v1.csv`, `compare_e206.json` /
  `.md`, `tie_masked_map.json`, `model_selection.json`, `mm1_v1_blind_day.csv` / `.json`, `neverrun_blind_day.json`, `scan_summary.json`,
  `f1f2_blind_day.json` / `.csv`, `f1f2_route.json`, `subset_lomo_v1.json`.
- **Reproduce** (from this folder, `/usr/bin/python3 -I -B`): `tie_masked_map.py --out out`; `fit_v1.py --out out`; `blind_day_v1.py --out
  out --params out/mm1_v1_params.json [--found <scanner output> --e208-arms <arms.json>]`; `compare_e206.py --params out/mm1_v1_params.json
  --fit out --out out`; `f1f2_blind_day.py --repo <the lab's top> --out out`; `select_forms.py --out out` (about 6 minutes);
  `subset_lomo_v1.py --out out` (about a minute); `f1f2_route.py --repo <the lab's top> --out out` (F1/F2 again under the route recorder: its
  two outputs must come out byte for byte) and `f1f2_route.py --repo <the lab's top> --check`. Run on aifoundry2 at the freeze, every output
  came out byte for byte the same as the lane's own runs; at the fixes, see section 11. Write each into a scratch folder and compare.
- The six CSV files have CRLF line ends (Python's csv module): a patch of this folder applies with `git am --keep-cr`; without it the frozen
  CSV's sha256 changes.

## 11. Fixes before the land (fix-mm1v1, Mon 16 Nov 2026, from 20:27 PST)

verify-mm1v1 read MM1-v1 as HOLDS WITH FIXES (desk, 19:58-20:26 PST): every output reproduced, its own folds gave the held-out numbers, no
point both fits and scores, the tie is exact, no blind-day point ever ran. Its findings were all to the record; the eight about this folder
are answered here (the ninth concerns a lane's own log). **No forecast changed** (no finding names a fault in one), so the seven
freeze-line files of section 1 are byte for byte those of mm1-v1's first freeze and nothing was re-frozen.

| # | finding | what changed |
|---|---|---|
| 1 | E206's held-out counter mean (6.37%) fits the row-group imbalance on 4 of E206's own points | `compare_e206.py`: the held-out counter mean from the E206 fold's own map with no imbalance, **7.87%**; the old figure beside it, labelled in sample (`out/compare_e206.*`; section 5.2) |
| 2 | the subset leave-one-mask-out refit chi only | `subset_lomo_v1.py` (new): every constant refitted from a cold start, **7.53%** against 10.61% held out with no subset term (10.27% in sample); section 4.1 |
| 3 | the never-run scan was narrower than E206's standard; its time was wrong | redone at E206's standard: 0 of 53 points, 0 of 47 cases; `out/scan_summary.json` re-made, the first scan's time corrected (about 19:31-19:32 PST); `out/neverrun_blind_day.json` came out byte for byte the same; section 8 |
| 4 | F1/F2 read the lab at run time, partly unpinned | `f1f2_blind_day.py` pins its three files by full sha256 with an exact check; `f1f2_route.py` and `out/f1f2_route.json` (new) record the route's 33 files; "every input vendored" now says MM1-v1 |
| 5 | "die only" also leaves out the on-die part of the fresh lines; the high end keeps the regulators | section 7's scope stated exactly (the code's label is frozen) |
| 6 | the worked example was off the fit's volts | recomputed at the fit's footing (section 7) |
| 7 | `MANIFEST.json` said `reuse_e206.py` is imported | the line reworded |
| 8 | fixed constants fitted on scored points | named in section 5.3 |

**Re-run from the fixed tree** (`/usr/bin/python3 -I -B`, aifoundry2, into scratch folders): 16 of 16 outputs came out byte for byte: `tie_masked_map.json`; `mm1_v1_params.json`, `holdout_v1.json`, `points_time_v1.csv`, `points_energy_v1.csv` and `e206_v0_v1.csv` (`fit_v1.py`); `mm1_v1_blind_day.csv` / `.json` and `neverrun_blind_day.json` (`blind_day_v1.py` with the wide scan's output); `compare_e206.json` / `.md` (`compare_e206.py` on the fresh fit); `f1f2_blind_day.json` / `.csv` (`f1f2_blind_day.py` with its full pins, and again under `f1f2_route.py`) and `f1f2_route.json`; `subset_lomo_v1.json`; `model_selection.json` (`select_forms.py`, about 7 minutes). `f1f2_route.py --check`: 33 of 33 route files equal at GitHub main 76fb5344. `out/scan_summary.json` is the scans' record, not a generator's output.

SPDX-License-Identifier: Apache-2.0
