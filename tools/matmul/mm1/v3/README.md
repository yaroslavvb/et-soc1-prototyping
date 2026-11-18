# MM1-v3: the lab's matmul model with the kernel's operations as an input, refitted with E206-E212, frozen for E213 (Tue 17 Nov 2026)

MM1-v3 predicts a matmul's clock cycles, seconds, joules (over idle and with the card at rest) and transistor switches on the ET-SoC-1
cards from the matrix size, the format, the data kind, the shire mask, the card, the clock **and the operations the kernel contains** (the
kernel's counted census: `inputs/census/census-v3.json`). It is MM1-v2 (`../v2/`, landed 3ca4b717) with the four changes the Q214
specification asked for (the operations census and its code-path term; the int8 L3 factor and the one-K-block term; the L3 retention with
two edges; design c's switch-route energy and the switch classes), fitted on everything committed at GitHub main **58f01105** when the final
fit started (Tue 17 Nov 2026 15:34:00 PST): E105-E190, E206 arms A and B, E207, E208 (seven sessions), E209, E210 (energy), E211 and eight
E212 sessions. This folder holds the model as frozen: the code, every input it reads (vendored and hashed in `inputs/SOURCES.tsv`), the
declaration of every form, bound, start, pin, fold and rule written before any fit (`DECLARED-v3.md`), the fits of every fold
(`out/fits/`), the held-out record beside MM1-v2's form refitted on the same folds, MM1-v2's unread scores on E212 made before any fit,
v3's unread scores on E212 a2c0-S4 (committed eight minutes after the final fit started), and **its forecasts for E213's 126 candidate
points with MM1-v2's beside**. Desk only: this commit measured nothing.

**Fixed after its verification, before any push** (verify-mm1v3: HOLDS WITH FIXES; fix-mm1v3, Tue 17 Nov 2026 about 20:00-20:45 PST):
- the energy fold with aifoundry3 held out is pinned by `AMENDMENT-A2.md` (post hoc; sections 3 and 4);
- the held-out and unread figures are split by configuration twins (sections 3, 5 and 6);
- the three time folds that amendment A1's tolerance stopped short are reported converged beside the record (section 3);
- the switch output's labels and the count footings are corrected (sections 6 and 7);
- notes on r2's reading, the minima, eta and T2, and the census (sections 3 and 8).

No fitted constant of the frozen model and no forecast value changed. `out/mm1_v3_e213.json` was re-frozen for its labels alone (section 6);
the checks are in `postcheck_v3.py` and `out/postcheck_*.json`.

The owner's words that started the matmul model (Mon 16 Nov 2026, at or before 09:48:24 PST; a voice transcription, where "matte mold"
is the matmul): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number
of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See
check how well the timing simulation for the matte mold matches reality and the energy."

**Labels.** *Measured*: a card's committed reading. *Desk*: arithmetic or a fit made at a desk. *Post hoc*: fitted after its data existed
(every constant of MM1-v3 is; its forms were chosen after the spec's lane read E211 and seven E212 sessions). *Unread*: scored on data that
existed but that the model never read. *Held out*: left out of that fit (one experiment, card, kernel or mask layout at a time); held out
is not blind. *Blind*: scored on data that did not exist when the model was frozen. A check not run is NOT RUN. Error = forecast /
measured - 1; rms and bias in %; joules over idle scored at 3 W and above (watts below). Interpreter for every number: `/usr/bin/python3`
3.12.3, numpy 1.26.4, scipy 1.11.4, run `-I -B`, single-threaded, on the lab box aifoundry2 (its desk).

## 0. On one screen

- **First, before any fit** (section 1): MM1-v2 as frozen, on E212's eight committed sessions (595 runs, 427 cases; UNREAD), per case:
  wall cycles **6.65%** (-3.36), W over idle given the seconds **7.76%** (+2.01, 362 cases at 3 W or more); per run 5.98% / 7.54%. The
  table was hashed into the lane's log at 15:22:24 PST, before any MM1-v3 fit.
- **What changed** (section 2): (1) **the operations are an input**: the census's code path from the tensor wait's return to each
  operand's request, relative to rgm136's gemmL loop, enters the op time at **zero fitted constants** (rgm211's gemmLn -37.0 / -49.75 cycles
  for A / B; gemmLnc -12.5 / -22.0; rgm211's own gemmL -10.5 / -13.75); (2) **the int8 factor on the L3-served stream**, d8 = **+4.8%**;
  (3) **the one-K-block term**: by the declared rule the alternative T5r won (the shire cache delivers a share r2 = **0.64** of the desk L2
  model's hits at KB <= 2 with MB x NB >= 2), not the C-store term; (4) **the L3 retention with two edges** for the B streams: the first
  edge at x1 = 37.4 MB (width 1.9 MB) down to a **plateau of half the stream (pB 0.50)** that ends at x2 = 72.3 MB (width 15.2 MB);
  (5) **energy by design c's switch route**: above an ungated base, energy follows the counted signal fin edges at one constant (b0 = 6.33e-17
  J a fin edge, so 1.58e16 fin edges a joule), with the zero gate in two classes, per-card awake power fitted jointly, a C-store energy and
  a voltage share for the lines (fitted at its bound 0); (6) **switches in the spec's six labelled classes**.
- **Held out, the same points and folds for v3 and for MM1-v2's form refitted** (section 3; 1,737 time points, 17 experiments, 4 cards,
  3 kernels, 3 mask layouts; six cold starts a fold; the declared pin rule, which no fold triggered). Wall cycles:
  - **LOEO 4.53%** v3 against **5.20%** v2form (4.54% with the three folds that A1's tolerance stopped short continued to convergence);
  - **LOCO 4.18%** against 5.05%;
  - **leave rgm211 out 7.78%** against 9.31%, its W pairs **8 of 10** inside 0.05 in ln against 3 of 10;
  - the E212 fold **5.40%** against 6.35%;
  - without configuration twins, LOEO reads **5.04%** against 5.55%. A twin is a point whose card, kernel, arm, format, mask and clock are
    also in its fold's training set; 578 of the 1,737 LOEO points have one.

  Worse than v2form: **spread shire masks held out 6.74%** against 5.40%, and E146's store rungs (in no training set) 5.29% against 3.85%.
  Energy, W over idle given the seconds on the 1,525 points both price: **LOEO 4.85%** against 6.14%; **LOCO 7.66%** against 11.59%; card
  1's all-zero data **5.32% (+0.10)** against 8.50% (+2.97). With aifoundry3 held out, the energy scale is not identified: `AMENDMENT-A2.md`
  pins it (post hoc); unpinned, the same training cost allows a pooled LOCO anywhere from 6.8% to 43.5%.
- **Acceptance** (section 4, rules declared by the spec and in `DECLARED-v3.md` before the fit): all four rules PASS.
  - Rule 2's energy half passes under `AMENDMENT-A2.md`'s pin (7.66% against a bar of 11.89%), and would pass for any mean training kc from
    0.87 to 1.49.
  - Rule 3 first read FAIL from a scoring bug (no W pair was formed under leave-one-kernel-out). Fixed, it passes under every reading (8, 7
    and 8 of 10 pairs) in the time fit's lower basin, the global one; in the upper basin it would fail (8.67%, 5 of 10).
- **UNREAD on E212 a2c0-S4** (section 5; aifoundry2 under its governor, 56 cases, data committed 15:42:15 PST, after the fit started):
  wall cycles **v3 4.75%** (+0.61) against frozen MM1-v2 5.80% (-2.12); W over idle given the seconds **3.07%** against 5.14%; v3 closer
  per case 26 to 21 (9 ties) and 28 to 19 (7 ties). 38 of the 56 cases repeat a configuration already in the fit data; on the other 18,
  wall cycles read **5.40%** against 6.86%.
- **E213** (section 6): 126 candidate points of the spec's six families (90 on aifoundry3 card 0 at 600 MHz, 36 on aifoundry2 card 0 at
  799 MHz given), **123 never run on their card** by a scan of 52,113 committed and lane files (the other 3 are declared references);
  MM1-v3's forecasts and MM1-v2's beside. **They are blind only once their sha256 (section 6) is in a pushed commit before E213's first
  card command.** Also frozen: E212 a2c0-S3's 46 scheduled arms (S3's first try was cut by the box's reboot at 15:45 PST; blind only if
  pushed before its re-run's first card command).
- **Not built or not identified** (section 8): the subset-layout model (the declared fallback lost); address conflicts; the path's exposure
  and the cooperation cost (pinned 0); switch counts for kinds never counted; the split of the L2 line energy from the per-op base (b2, d2
  negative); the energy scale with aifoundry3 held out (pinned by A2); two minima in the time fit, the lower reached by one start of six
  (and two in the energy fit); eta (at its bound) and T2 (not identified).

## 1. MM1-v2 on E212, UNREAD, before any fit (`unread_v2_e212.py`, `out/unread_v2_e212.*`)

**Why unread, not blind.** MM1-v2's predictor and constants were pushed at 01:44:48 PST Tue 17 Nov 2026, before E212's first datum (05:30
PST), but no forecast for E212's points was frozen then: these are made now by the frozen code, the call's arguments chosen now (its four
freeze-table files pinned by sha256 and its 114-line `SHA256SUMS` checked on every call). The run's primary view (the 600 MHz band on card 1,
the window on the governed cards) at its measured kernel clock and minion volts; time for every kind, energy for random, zeros and ones
(E212's switch-pattern arms are not read for energy: their counts are not made).

| E212, MM1-v2 UNREAD | cases | wall cycles rms (bias) | counter mean | W over idle given t (>= 3 W) |
|---|---|---|---|---|
| all eight sessions | 427 | **6.65% (-3.36)** | 7.39% (-2.58) | **7.76% (+2.01)**, n 362 |
| aifoundry1 card 1 (S1-S4, 600 MHz) | 203 | 5.99% (-2.96) | 6.84% | 9.32% (+1.30), n 152 |
| aifoundry1 card 0 (S1, S2, governed, low power) | 100 | 7.45% (-4.07) | 8.04% | 7.31% (+4.41), n 98 |
| aifoundry2 card 0 (S1, S2, governed) | 124 | 6.98% (-3.44) | 7.70% | 5.47% (+0.87), n 112 |
| per run (595 runs) | - | 5.98% (-2.97) | 6.71% | 7.54% (+2.17), n 505; J at rest given t 2.20% |

Sha256 (logged at 15:22:24 PST, before the first fit at 15:34:00): `unread_v2_e212_runs.csv` 51654af2..., `unread_v2_e212_cases.csv`
138758b4..., `unread_v2_e212.json` 83c21ac7.... This table is the E212 reference of acceptance rule 4 (section 4).

## 2. What MM1-v3 computes, and what changed and why (`engine_v3.py`, `energy_v3.py`, `mm1_v3.py`)

**Time** (wall basis, microseconds an op at clock f; MM1-v2's notation, the changes in bold):

```
T_op = 1/2 sum_Q0 max(Tc, kA tau_A + D_A, tau_B0 + D_B) + 1/2 sum_Q1 max(Tc, kA tau_A + D_A, tau_B + D_B), x the subset row imbalance
tau[L2] = F2/f + T2      tau[L3] = (c3/f + m3 X3) (1 + d8 [int8])      tau[F] = cF/f + mF XF      X = 1 - chi (1 - n/32) on subsets
D_A, D_B = the census path of the kernel's loop less rgm136 gemmL's (cycles / f; no fitted constant; 0 for run_gemm, whose census is NOT RUN)
the closed-form map's L2 hits at KB <= 2, MB x NB >= 2 scaled by r2 (the rest go to the L3 or DRAM by the retention; not E211's walk map)
r_B(d) = (1 - pB) / (1 + exp((d - x1)/w1)) + pB / (1 + exp((d - x2)/w2));   r_A(d) = 1 / (1 + exp((d - x1)/w1))
```

| term | physical reading | constants (frozen, all data) | why (the spec's evidence, post hoc) |
|---|---|---|---|
| tensor floor Tc | the multiply-add op with A and B resident: the RTL bench + 7.75 cycles | 0 (as v2) | exact for the resident op (mm-timing) |
| L2 stream | the shire cache on the minion clock | F2 382.8 cycles, T2 0.012 us | as v2 |
| L3 and fresh streams | fixed latency in cycles and in time | c3 401.8 cycles, m3 0.826 us, cF 358.4 cycles, mF 2.010 us, kA 0.898 | as v2 |
| **code path D** | the instructions between the tensor wait's return and each operand's request: one cycle an instruction plus E33's 5.25-cycle L1 load-to-use stalls | **0 fitted** (the census) | E211: rgm211's code path explains its controls (design b; the spec's 2.1) |
| **int8 L3 factor d8** | the int8 op's L3-served stream runs longer at equal lines | **d8 0.0476** | E212 (unread by design a): int8 -5.5% against floats +1.7% under v2 inside the L3 |
| **L2 share r2** (T5r, declared alternative; won) | the shire cache delivers only part of the desk L2 model's hits when KB <= 2 and the tile grid is wider than one | **r2 0.641** | E212's one-K-block miss in every format (-4 to -18% under v2) |
| **two-edge retention** | the far-B stream partly retained on a plateau past the L3's first edge, then fresh | **x1 37.42, w1 1.92, pB 0.497, x2 72.29, w2 15.21** (MB) | E212's K ladders: two plateaus on three cards; v2's one edge reads the second -9% |
| power-of-two rule, subsets, imbalance | v2's (zeta, piF0; chi3, chiF; eta) | zeta 0.707, piF0 0.050, chi3 0.067, chiF 0.100, eta 0.000 | as v2 |
| the counter's mean | v2's imbalance law (rho) | as v2 | as v2 |
| the governor | v2's clock model, carried (the clock is an input) | as v2 | as v2 |

**Energy** (W over idle at the op time t; design c's route, the spec's section 6; `DECLARED-v3.md` section 5):

```
W = [ Pa(card) n/1,024 + Pm u + g G + (n / t) { sV kc [ Eub(fmt) - Gate(fmt, kind) + m(fmt) b0 S(fmt, kind, KB) ] + sV dEi(loop)
      + sL [ sum_l (n_l/32)(b_l + d_l phi) + eC nC (rC (b3 + d3 phi) + (1 - rC)(bF + dF phi)) ] } ] x (1 + 0.0048 (T0 - 50 C))
sV = (V / 0.517 V)^2, sL = 1 + xi (sV - 1); S = the committed desk counts of signal fin edges an op (E210's at GEMM states for fp32, MM1-v1's
switch table for fp16 and int8); dEi the census's instruction energy relative to rgm136 (0 fitted)
```

Frozen (all data, 26 constants): awake power Pa 0.740 W (aifoundry3), 1.221 (card 1), 1.469 (aifoundry2), 0.911 (card 0) at 1,024 minions;
Pm 0.252 W; g 0.759; the ungated base Eub 10.33 nJ an op (fp32), 10.34 (fp16), 3.18 (int8); the data constant b0 6.33e-17 J a fin edge
(m_fp16 1.091, **m_int8 3.747**); the gate a_op 7.99, a_lane 3.24, a8 1.51 nJ; kc 1.029 (card 1), 1.068 (aifoundry2), 1.077 (card 0);
lines b2 **-88.9**, d2 **-291.7**, b3 339.1, d3 571.3, bF 981.4, dF 679.0 pJ a line; eC 4.07; **xi 0.000** (its lower bound). The declared
alternative v3-ledger (MM1-v2's resident term inside v3's form) lost by the declared rule (section 4). Kinds with no committed count are
NOT FORECAST by v3's energy (never a nearest-kind guess); their time is forecast.

**Switches** (the spec's section 7; `mm1_v3.Model.switches`): counted signal fin edges (lo, zero delay; hi, timed; each format's count footing
in section 7), counted clock fin edges, the data term's energy equivalent (estimated: its joules x 1.58e16, which is s_V x kc x m x the die
factor times the counted signal fin edges, not the counted edges themselves), the ungated base (its energy fitted, its count estimated, never merged
with the bench's clock count), the gate (counted clock fin edges removed and the energy saved), the lines (estimated, band x0.5 to x2) and
what is not converted (awake, memory path awake, governed base, instructions: joules only). Scorable through energy only, as E210 scored
the route (registered, blind: 1.87% of the data range); no absolute count is scorable.

**What did not change:** the map (MM1-v1's closed form for rgm136's walk; E211's exact walk map for rgm211's gemmLn at MB, NB >= 2), the
rest law per card (REPORTED), the volts and the governed base relations, the counter-mean imbalance, the governor's clock model.

## 3. Held out: the same points and folds for v3 and for MM1-v2's form refitted (`fit_v3.py`, `out/holdout_v3.json`, `out/fits/`)

**The data** (`data_v3.py`): one time point a (card, case), the mean of its runs: 1,737 points (MM1-v2's 1,072 sources with E208's seventh
session pooled, E206 arm B, E207, E209, E211 with its kernels, E212's eight sessions: 427 cases). E146's 87 store-cadence rungs are in no
training set and are scored apart (the spec's rule). Energy: 1,603 points v3 prices (with E210's sixteen pattern cases), 1,579 that v2form
also prices, 1,525 of them at 3 W or more. **The fits:** least squares on forecast / measured - 1 of the wall op time from the six declared starts a
fold (MM1-v2's six for the shared constants, declared starts for the new ones; none read off a fit), ftol = xtol = gtol = 1e-8 (amendment
A1, before any fold fit), at most 4,000 evaluations; the lowest training cost kept; every constant refitted in every fold; the pin rule
holds a constant at its neutral value in a fold with none of its identifying points (no fold triggered it); the energy folds on their own
time folds' lines and seconds.

**Wall cycles, held out** (MM1-v3 = the final form v3+T5r; v2form = MM1-v2's form refitted on the same points and folds):

| set | n | MM1-v3 | v2form | v3 with tC (the primary, beside) |
|---|---|---|---|---|
| in sample (training points) | 1,650 | 3.96% | 4.72% | 4.15% |
| **LOEO, every point by its experiment's fold** | 1,737 | **4.53% (-0.40)** | **5.20% (-0.61)** | 4.67% |
| **LOCO, every point by its card's fold** | 1,737 | **4.18% (-0.13)** | 5.05% (+0.29) | 4.32% |
| LOCO folds: aifoundry3 / card 1 / aifoundry2 / card 0 | 464 / 408 / 727 / 138 | 3.80 / 4.02 / 4.45 / 4.35% | 4.44 / 5.15 / 5.21 / 5.71% | 4.06 / 4.41 / 4.37 / 4.65% |
| **leave rgm211 out (gemmLn, 12 points)** | 12 | **7.78% (-1.66)** | 9.31% (+4.51) | 7.84% |
| leave gemmLnc out (2 points) | 2 | 11.66% | 12.20% | 10.96% |
| leave run_gemm out | 426 | 3.12% | 4.12% | 3.37% |
| leave a mask layout out: compact / spread / other | 96 / 37 / 37 | 5.45 / **6.74** / 7.32% | 5.64 / **5.40** / 7.54% | 5.52 / 6.52 / 7.36% |
| the E212 fold (whole) / by card: card 1, card 0, aifoundry2 | 427 / 203, 100, 124 | **5.40%** / 4.45, 4.92, 4.95% | 6.35% / 5.42, 5.93, 5.61% | 5.83% |
| E146's store rungs (never trained; LOEO) | 87 | 5.29% (+0.98) | 3.85% (-0.89) | 3.57% |

LOEO by experiment (MM1-v3 / v2form): E105 2.64 / 2.36%, E107 3.02 / 4.05, E119 2.53 / 3.20, E126 3.49 / 4.86, E136 1.44 / 3.11, E146 4.96 /
4.49, E158 4.46 / 5.05, E159 5.56 / 5.09, E168 0.94 / 2.33, E169 7.31 / 7.08, E190 5.88 / 5.42, E206 4.51 / 4.87, E207 4.32 / 4.66, E208
3.43 / 5.03, E209 5.25 / 6.37, E211 6.83 / 7.51, E212 5.40 / 6.35. E212's groups (the residual lane's predicates, LOEO): int8 inside the L3
at KB >= 2 **2.60% (-2.51)** against 5.95% (-5.73); floats there 0.94 / 3.96%; one K block with MB x NB >= 2 **5.78% (+0.04)** against 8.09%
(-6.08); the knee at NB 1 4.03 / 2.77% (worse); past the L3 5.19% (-1.56) against 6.67% (-4.00); subsets past the L3 or at the knee 9.21%
(-4.99) against 9.24% (-6.54).

**Converged folds** (verify-mm1v3's finding 5; `postcheck_v3.py converge`, `out/postcheck_converged.json`; post hoc). Amendment A1's 1e-8
tolerances stopped the chosen start of three LOEO folds of v3+T5r at status 3 (E119, E126, E209). They did the same to three folds of the
primary v3 (E208, E209 and E212's aifoundry1 card 1 fold). Continued from the recorded point at 1e-12, restarted until the cost stopped
falling:

| fold (v3+T5r) | training cost, recorded / converged | held out, recorded / converged |
|---|---|---|
| E119 | 1.2738208 / 1.2732777 | 2.533 / 2.636% |
| E126 | 1.2664943 / 1.2664940 | 3.495 / 3.495% |
| E209 | 1.2324414 / 1.2308976 | 5.245 / 5.421% |

- Pooled LOEO moves from 4.529% to 4.537%, and the primary's from 4.666% to 4.667%. T5r's decision margin shrinks from 0.137 to 0.130
  points: T5r still wins.
- Every converged fold stays in the lower basin (kA 0.90).
- The record above stays as declared (A1), and the converged fold constants are not carried into the energy folds.
- verify-mm1v3's independent cold starts found the same converged figures.

**Configuration twins** (finding 3; `postcheck_v3.py twins`, `out/postcheck_twins.json`). A scored point is a twin when its card, kernel,
arm, format, shire mask and clock (to 25 MHz) are also in the training set that priced it; for energy the data kind must match too. A
held-out figure that includes twins reads partly like an in-sample one:

| wall cycles, LOEO | n | MM1-v3 | v2form | v3 with tC |
|---|---|---|---|---|
| all | 1,737 | 4.53% | 5.20% | 4.67% |
| with a twin in training | 578 | 3.28% | 4.41% | 3.50% |
| **no twin** | 1,159 | **5.04%** | **5.55%** | 5.15% |

LOCO holds no twin by construction (the card is part of the configuration). Energy LOEO, W over idle given t on the 1,525 points both
price:
- 385 points have a twin: v3 4.58% against v2form 6.05%;
- the 1,140 without one: **4.94%** against 6.17%.

**E211's ten W pairs** (ln of the forecast rgm211 / rgm136 ratio over the measured; inside 0.05): MM1-v3 8 of 10 under leave rgm211 out
(rms ln 0.070), 7 of 10 with both members held out by the E211 fold, 8 of 10 in sample; v2form 3 of 10 under each. w03 and w04 stay the
worst (-0.145, -0.152 in ln: the shapes where rgm136's far operand was B's large panel), as design b found.

**r2's reading** (finding 6). The declared form reads "r2 at KB <= 2, MB x NB >= 2". The code applies r2 only to the closed-form map's L2
hits (rgm136's walk, also used for gemmLnc and for rgm211's own gemmL loop). It never applies r2 to E211's exact walk map for rgm211's
gemmLn, whose L2 hits come from the walk itself. The model was fitted and frozen under this reading, and it stands.
- Among the fitted points, the choice touches only rgm211's gemmLn2x3x2 (w01n).
- Read literally (r2 on the walk map too), verify-mm1v3's independent code gives leave rgm211 out 7.767% (this code: 7.780%) and an ln error
  for w01 of -0.0048 (this code: -0.0115). The pairs count 8 of 10 either way.
- No E213 point is touched: every E213 gemmLn point has KB >= 3 or MB x NB = 1.

**Energy, held out** (W over idle given the measured seconds, at 3 W or more; MM1-v3's energy form v3 on the final time form; v2form on its
own; the points both price, n 1,525, unless named):

| set | MM1-v3 | v2form | v3-ledger (beside) |
|---|---|---|---|
| in sample | 4.29% | 5.49% | 4.57% |
| **LOEO** | **4.85% (+0.37)** | **6.14% (+0.12)** | 5.02% |
| **LOCO** (the aifoundry3 fold under `AMENDMENT-A2.md`'s pin) | **7.66% (-1.29)** | 11.59% (-3.31) | 10.10% |
| LOCO folds: aifoundry3 / card 1 / aifoundry2 / card 0 (n 376 / 336 / 677 / 136) | 9.70 / 7.50 / 6.75 / 5.70% | 13.39 / 13.02 / 10.41 / 7.25% | 10.70 / 9.99 / 10.44 / 6.22% |
| LOEO, MM1-v3's own points (n 1,549): J over idle with t forecast / J at rest given t / J at rest with t forecast | 5.53 / 1.69 / 4.39% | 6.88 / 2.05 / 5.03% (its own) | - |
| LOEO card 1 all-zero data (n 102) | **5.32% (+0.10)** | 8.50% (+2.97) | 5.86% |
| LOEO the E212 fold (n 362) | 5.09% (+0.24) | 7.02% (+1.18) | 5.29% |
| LOEO E212 KB >= 16 / one K block (n 118 / 41) | 4.82 / 5.35% | 8.13 / 9.58% | 5.07 / 6.18% |
| LOEO E210's sixteen pattern cases (v3 only) | 4.67% (-3.22) | not priced | not priced |
| LOEO E211 (n 26) | 7.23% | 7.35% | 7.34% |
| leave a kernel out (n 363) / a mask layout out (n 114) | **7.40%** / 6.77% | 7.79 / 6.68% | **5.91** / 6.58% |

**The LOCO fold without aifoundry3** (verify-mm1v3's finding 1; `AMENDMENT-A2.md`, post hoc; `postcheck_v3.py line`,
`out/postcheck_loco_a3_line.json`).
- **The flat direction.** kc is relative to aifoundry3, so with aifoundry3 held out, the training cards' kc and the per-op constants they
  multiply trade exactly. Every point on that line has one training cost (1.000131025), and the pooled LOCO runs anywhere from 6.77% to
  43.53% while every kc stays in bounds. The first record's 7.01% (aifoundry3 7.44%) was where its optimizer stopped.
- **The pin.** The training cards' mean kc is set to 1, so the held-out card sits at their mean, as an absent card takes the others' mean
  awake power. It gives the rows above: aifoundry3 9.70% (+7.32), pooled 7.66%.
- **The alternatives.** Setting one training card's kc to 1 instead gives 7.39%, 7.98% or 7.65%. Rule 2's energy half passes for any mean
  training kc from 0.868 to 1.491.
- **Unchanged.** Every other energy fold, both all-data fits and the parameter file (re-run 20:04:57-20:05:44 PST). v2form needs no pin: it
  prices a held-out card from that card's own ledger anchor.

**Two minima** (`minima_v3.py`, `out/minima_v3_T5r.json`, in sample, post hoc): from the six starts the all-data fit of v3+T5r reaches
training cost 1.2923 (start 0: x2 72.3 MB, w2 15.2, pB 0.497, kA 0.898; in-sample rms 3.96%) and 1.4548 (starts 1, 2, 4, 5: x2 54.6 MB,
w2 22.4, pB 0.455, kA 1.055; 4.20%; start 3 1.4715). Both are two-edge solutions; they differ in where the plateau ends and in A's latency
multiplier. In every fold the chosen fit is in the lower basin (kA 0.889-0.917): start 0 alone reached it in 27 of 30 folds, two starts in
3, and where one start reached it the next start's training cost is 5-16% higher. The held-out record therefore rests on one start a fold; six starts are not many for
a 19-constant fit with two basins, and a third, lower basin is not excluded. MM1-v3 with tC shows the same pattern (1.4181 against 1.5191).
- **The lower basin is the global one.** verify-mm1v3's 24 cold starts a fold, from its own code, reach it in every fold (9-15 of 24 a
  fold), and find no lower one: the record stands.
- **Rule 3 holds only in the lower basin.** In the upper one, leaving rgm211 out reads 8.67% with 5 of 10 pairs, a FAIL (section 4).
- **The energy fit has two minima too.** In 30 of v3's 32 energy fits (the all-data fit and 31 folds), a single start of the three reached
  the best cost. verify-mm1v3's 27 starts a fold reach the lower minimum with 17-27 of them. LOEO energy is the same in either basin (4.85%
  and 4.83%).
- **For v3.1:** declare more starts a fold, before the fit.

**The record v3 is measured against** (MM1-v2's own figures, different point sets: LOEO 5.41% / 6.59% on 1,072 / 940 points; LOCO 5.50% /
10.13%; blind E207 4.80% / 4.82%; blind E209 7.22% / 5.42%; blind E211 rgm211 8.93% / 3.21%; unread E212 per case 6.65% / 7.76%; the
card's repeat 0.38% / 1.16%). MM1-v3's held-out errors (4.5% cycles, 4.9% energy) stay well above the card's repeat: model error, not noise.

## 4. The declared decisions, the acceptance rules, and the departures (`out/decisions_v3.json`, `out/acceptance_v3.json`)

**Declared before any fit** (`DECLARED-v3.md`, sha256 05232c6a... at 15:24:52 PST; amendment A1, tolerances only, 8365e655... at 15:32:42,
before any fold fit; A1's own header reads "15:4x PST", but its sha256 was logged at 15:32:42, before the first fit at 15:34). **Amended
after the fits:** `AMENDMENT-A2.md` (post hoc: the energy pin for the fold without aifoundry3, section 3).

**The time decision** (each alternative against the primary v3; the lower LOEO wall rms over all 1,737 points, within 0.05 points the form
with fewer constants, equal constants the primary): **T5r 4.53% against 4.67%: T5r wins**; T6A (A's own edge, 21
constants) 4.70%: v3; T7L (the layout fallback) 4.64%, within 0.05 with equal constants: v3. **The final time form is v3+T5r**, refitted on
every fold. **The energy decision** (v3 against v3-ledger, LOEO W over idle given t on the points both price, within 0.1 point the form with
fewer constants): 4.85% against 5.02%: **v3**.

**Acceptance** (the spec's section 11, restated in `DECLARED-v3.md` section 6; on the same points and folds):

| rule | MM1-v3 | v2form / reference | verdict |
|---|---|---|---|
| 1 LOEO wall cycles below v2form's | 4.53% | 5.20% | PASS |
| 1 LOEO J over idle given t below v2form's (points both price) | 4.85% | 6.14% | PASS |
| 2 LOCO wall not worse by more than 0.3 points | 4.18% | 5.05% | PASS |
| 2 LOCO J over idle given t not worse by more than 0.3 points | 7.66% (aifoundry3's fold pinned by A2; passes for any mean training kc 0.87-1.49) | 11.59% | PASS |
| 3 leave rgm211 out: wall at or under 8.0% and at least 7 of 10 W pairs inside 0.05 | 7.78%; 8 of 10 (the lower basin, the global one; upper basin 8.67%, 5 of 10) | - | PASS |
| 4 the E212 fold under MM1-v2's unread error (per case) | wall 5.40%, W given t 5.09% | 6.65%, 7.76% | PASS |

**Departures and repairs, all after the fits and none changing a fitted number or a forecast:**
1. **The resume.** The box went down at about 15:45 PST with the final fit part done (the primary v3's folds finished at 15:36:10; MM1-v2's
   form had finished 12 folds, through E206). After the reboot (16:33, 16:37) the fit continued on the same vendored data (58f01105): MM1-v2's form was
   re-run whole (16:59-17:12; every fold it had reached before reproduced its numbers), then the three alternatives, then v3+T5r and the
   energy. E212 a2c0-S4, committed at 15:42:15 after the final fit started, was left out of every fit and scored unread (section 5).
2. **Rule 3's W pairs.** `summary_v3.py` first formed the leave-rgm211-out pairs from that fold's held-out predictions only, which hold no
   rgm136 twin, so it counted 0 of 0 pairs and read FAIL. Fixed (17:27): the fold's constants price both members (the twin is in that
   fold's training set). Every reading is reported above (8 of 10 under the fixed rule, 7 of 10 with both members held out, 8 of 10 in
   sample), and each passes the declared bar; the parameter file came out byte for byte the same (sha256 1fdc0749...).
3. `summary_v3.py`'s last line failed on the LOEO-only alternatives' empty LOCO record (KeyError); fixed by a `.get`, before any output
   was used.
4. Not built, as declared (section 8): T7's masked walk, T8, gamma, T_coop, a_row; the spec's fourth kernel out (E202's MNIST kernel) NOT
   RUN (no census of its kernel).

**After the verification (fix-mm1v3, before any push).** None of these changes a constant of the frozen model or a forecast value; item 5
moves one held-out fold's constants along its flat line.

5. **`AMENDMENT-A2.md`** (post hoc). The energy pin for the LOCO aifoundry3 fold (section 3). Only that fold's record and the LOCO energy
   rows changed; rule 2's energy half reads 7.66% (was 7.01%) and still passes.
6. **The switch labels** (finding 4). `mm1_v3.py`'s labels for the counted signal fin edges and the data term's energy equivalent are
   corrected, each count's footing is added, and so is the equivalent's factor over the counted edges. `out/mm1_v3_e213.json` is re-frozen:
   labels and two added fields only, its 9,815 numeric leaves identical. The CSV forecast files are byte for byte the same (section 6).
7. **The census's gemmLnc instruction energy** (a nit). The census gives -45.66 pJ an op; its own stated rule gives -39.64 pJ, because the
   removed tensor_coop issue slots are not credited (verify-mm1v3). The difference is about 4 mW at 1,024 minions. The census stays as frozen
   (a freeze-line input), for v3.1 to correct.

## 5. UNREAD on E212 a2c0-S4 (`unread_v3_e212s4.py`, `out/unread_v3_e212s4.*`)

E212 a2c0-S4 (aifoundry2 card 0 under its governor, the model session's sweep) ran 15:03-15:33 PST; its data were committed in 724e8f39
(15:42:15 PST), eight minutes after MM1-v3's final fit started on 58f01105. No fit, form choice or constant of MM1-v3 read it: it was
vendored into `inputs/e212-unread/` (a folder no data loader reads) after the time fits, and scored after the freeze (the parameter file's
and E213's forecasts' sha256 logged at 17:28:51 PST, the scorer run at about 17:29). The data existed before the freeze: unread, not blind.
Each model called at the run's measured clock, minion volts and die at start (the window view).

| a2c0-S4, UNREAD | MM1-v3 (frozen) | MM1-v2 (frozen) | v2form (refitted, all data) |
|---|---|---|---|
| wall cycles, 56 cases | **4.75% (+0.61)** | 5.80% (-2.12) | 5.93% (-0.28) |
| counter mean, 56 cases | 5.90% | 6.32% | - |
| W over idle given t, 54 cases | **3.07% (-1.46)** | 5.14% (+0.54) | 4.42% |
| J over idle with t forecast, 54 cases | 4.06% | 5.68% | 5.23% |
| per run (62 runs; 60 with energy): wall / W given t / J at rest given t / J at rest t forecast | 4.52 / 2.96 / 1.13 / 3.91% | 5.57 / 5.09 / 2.06 / 4.77% | - |
| per case, closer to measured (ties within 0.5% in cycles, 1% in W) | v3 26, v2 21, ties 9 (cycles); v3 28, v2 19, ties 7 (W) | | |

**Twins in S4** (finding 3; `out/postcheck_twins.json`). 38 of the 56 cases repeat a configuration already in the fit data at the same
card and clock (to 25 MHz; time is kind-blind, energy adds the kind). Those cases test the model less than a new configuration does:

| a2c0-S4, UNREAD, split | cases | MM1-v3 | MM1-v2 | v2form |
|---|---|---|---|---|
| wall cycles, configuration in the fit data | 38 | 4.42% (+0.61) | 5.22% (-2.19) | 4.96% |
| **wall cycles, new configuration** | 18 | **5.40% (+0.59)** | **6.86% (-1.97)** | 7.58% |
| W over idle given t, configuration and kind in the fit data | 32 | 3.25% (-1.30) | 5.25% (-0.53) | 4.87% |
| **W over idle given t, new configuration or kind** | 22 | **2.81% (-1.68)** | 4.98% (+2.09) | 3.67% |

On the 18 new configurations, v3 is closer than MM1-v2 in cycles on 11 cases, farther on 5, with 2 ties.

MM1-v3's predictor equals the fit code on every case (op time max relative difference 0.0; W 7e-15 W).

## 6. E213 and E212 a2c0-S3: the points and the forecasts (`e213_v3.py`, `out/e213_points.csv`, `out/mm1_v3_e213.*`, `out/mm1_v2_e213.csv`, `out/neverrun_e213.json`, `out/mm1_v3_e212_s3s4.csv`)

**The points** (the spec's section 12 candidates; the registration lane fixes the final list and its runs): arm A on aifoundry3 card 0 at
its pinned 600 MHz, 90 points: I, int8 / fp32 pairs at 2x1x2, 4x1x2, 3x1x3, 1x2x7 (inside the L3) and 1x2x11, 2x2x7, 1x3x9, 2x3x6 (the
knee); R, the two-edge retention, 1x1x18 ... 1x1x34, 1x2x13, 1x2x18, 1x2x22, 2x1x8, 2x1x10, 3x1x6, 3x1x7, 3x1x9, 4x1x6; C, one K block at
3x2x1, 4x5x1, 7x3x1, 9x7x1, 10x10x1, 14x12x1 in int8 and fp32 (C from 12 to 336 MiB); M, fp32 zeros at 2x8x8 and 1x3x12 on eleven never-run
masks with each shape's full chip; P, rgm136's gemmL, rgm211's gemmLn and rgm211's own gemmL at 3x1x3, 1x6x5, 4x1x6, 1x1x44 (one op stream)
and gemmLnc at those four and at 1x1x1 int8; E, deep K 1x3x40, 2x2x44, 1x4x36 in zeros and random, and the anchor gemmL4x8x8 int8 at
two die gates (48, 56 C). The optional arm B on aifoundry2 card 0 at 799 MHz given, 36 points: families I, R and E's deep-K pairs.

**Never run** (`neverrun_e213.json`): a point is kept for its card when no committed data folder (`docs/reports/data` at GitHub main
600a8fb9, every experiment of the lab's and the model session's committed ones), no committed E212 schedule and no card lane's folder of the
round names its arm token on that card or on no named card, and MM1-v3's own measured points do not hold it: 52,113 files read; **123 of
126 never run on their card**, and no candidate token appears in any file on any card. The 3 that ran are the declared references
(gemmL1x1x1 int8 random, gemmLnc1x1x1's twin, and the anchor gemmL4x8x8 at the two die gates). rgm211's own gemmL loop has run on no card
(E211's controls ran its gemmLn at 1x5x5 and 3x1x8).

**The forecasts**: every field of MM1-v3's predictor (cycles wall and counter mean, seconds, W over idle with its A + B / t form, J over idle,
J at rest REPORTED, the six switch classes, the joules by class, the census path, the floor and the simulated bench beside) in
`mm1_v3_e213.json` and the main columns in `mm1_v3_e213.csv`; MM1-v2 as frozen beside in `mm1_v2_e213.csv` (a kernel it has no term for is
priced as its rgm136 twin, literally). Every point has an energy forecast (random and zeros only). v3 / v2 in cycles: 0.92-1.15 (the
largest: family C up to 1.13, family M up to 1.15); in W over idle 0.92-1.18.

| file (the freeze line: to be in a pushed commit before E213's first card command) | sha256 |
|---|---|
| `out/mm1_v3_e213.csv` (126 points) | `01a2fdaef0b506b218fad1975dacf397a2c728010a595c8b4dadcbf569c07a49` |
| `out/mm1_v3_e213.json` (re-frozen by fix-mm1v3 for its switch labels, section 7; every number as first frozen in `fe97610b...`) | `932c5a18472fd5a16ddcc0338f481b6227409c1fd276606eb604480154f0bd4b` |
| `out/mm1_v2_e213.csv` (MM1-v2 beside) | `e1b99f682f303eaeaa818bc09a95e6484d8db5811c43991ae9d1b078476a43af` |
| `out/e213_points.csv` | `be9049299641ccaf764225c9b390997cc53a2885d9bf350ae12212d14503ee21` |
| `out/mm1_v3_params.json` | `1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db` |
| `out/mm1_v3_e212_s3s4.csv` (E212 a2c0-S3's 46 and S4's 56 scheduled arms, 799 MHz given, v3 and v2) | `002226651404b291739894cc187d528e68b741d4e4df8b8d53d37172f4933faf` |
| the predictor and its code: `mm1_v3.py` (its switch labels corrected by fix-mm1v3), `engine_v3.py`, `energy_v3.py`, `mm1_core_v3.py`, `kinds_v3.py`, `inputs/census/census-v3.json` | `SHA256SUMS` |

**E212 a2c0-S3** (the model session's last E212 session, its committed schedule `inputs/e212/sched__a2c0-S3.json`): its first try at 15:44
PST was cut at or near its start by the box's reboot; its data, if any, are uncommitted and unread here. The forecast for its 46 arms is
**blind only if pushed before its re-run's first card command**; S4's 56 are unread (section 5 scores S4 at its measured clocks). S3 would
be a weak blind test of time (finding 3; `out/postcheck_twins.json`): 10 of its 25 distinct configurations (kind-blind) are already in the
fit data on aifoundry2 at 800 MHz, and all 25 on some card. For S4's schedule the counts are 32 and 48 of 50.

## 7. Transistor switches

The six classes of section 2, for every forecast point (E213's JSON). The counted classes come from committed desk counts only: E210's at
GEMM states for fp32 (zeros, ones, random, sparse50 and E210's nine patterns) and MM1-v1's switch table at the launch points for fp16 and
int8 (zeros, ones, random, sparse50). **No new count was made this round** (no simulator here), so E212's plan tiles, the real tiles and any
new pattern are NOT FORECAST in energy and carry no count. The energy-calibrated constant (1.58e16 fin edges a joule) is fitted on all
energy data; E210 registered it per shape at 1.67e16 and 1.64e16.

**What each count covers** (corrected after verify-mm1v3's finding 4). These are the count files' own footings, now also in each point's
label (`counts_footing`):
- **fp32: counted (desk).** The gate-level bench's VPU net toggles a MAC at GEMM states, times the fin edges a toggle calibrated on the fp32
  unit's gate-level run (E210's counts, in MM1-v1's units).
- **fp16: estimated (desk), not counted.** fp16's RTL toggles times the fp32 gate/RTL ratio; there is no fp16 gate-level run.
- **int8: counted (desk) around the arithmetic only.** The behavioural RTL has no nets inside the int8 multiply, product sum and add, so the
  count covers only the VPU around them. That gives m_int8 = 3.75 a reading: it scales the counted edges up to the data term the card
  shows, so it carries the uncounted arithmetic. That is a reading, not a count.

**The data term's energy equivalent** (the JSON's `data_term_energy_equivalent`, the CSV's `switches_data_term_equivalent`) is the data
term's joules times kappa, that is s_V x kc x m x the die factor x the counted signal fin edges (lo). It equals the counted edges only where
all four factors are 1 (fp32 on aifoundry3 at 0.517 V and 50 C).
- At E213's points the factor runs from 1.02 to 5.71: 1.02 for fp32 on aifoundry3, 3.78-3.93 for int8 there (a001 3.82), 1.52 for fp32 on
  aifoundry2 at 799 MHz (b092) and 5.71 for int8 there.
- The first label said it "equals the counted signal fin edges for fp32". The label now gives the product, and the JSON carries the factor
  (`factor_over_counted_signal_lo`).
- The values themselves, and the CSV column, are unchanged.

## 8. What the data cannot identify, the gaps, and NOT RUN

- **The subset layout.** E212 shows that at an equal shire count the layout moves the time by up to 15%; MM1-v3 has no layout model: the
  masked walk (the spec's T7) needs traced simulator runs (none this round), and the declared fallback (T7L) did not win. Spread masks held
  out read 6.74% against v2form's 5.40%; E213's family M tests the gap.
- **The one-K-block term.** T5r (r2) won the declared rule over the C-store term (tC) by 0.14 points of LOEO, but it reads E146's store
  rungs (never trained) at 5.29% against 3.57% for tC and 3.85% for v2form: the two forms read different data well, and E213's family C is
  where they part.
- **Two minima** (section 3): one start of six reaches the lower basin in most folds. That basin is the global one, and rule 3 holds only
  there. The energy fit has two minima as well.
- **The energy split.** b2 and d2 come out negative (-88.9 and -291.7 pJ a line). The L2 lines an op are nearly constant across the
  L2-served shapes, so the L2 term trades with the per-op ungated base and the data term: their sum is identified, not the split (the joules
  by class show a negative L2 share).
  - xi sits at its bound 0: the lines do not follow V^2 at all in this fit.
  - m_int8 = 3.75 has a reading, not a count: int8's counted edges leave out the arithmetic (section 7), and m_int8 carries it. The spec's
    guess of 1.5-3 was made before that footing was read.
- **The energy scale with aifoundry3 held out** (section 3, `AMENDMENT-A2.md`): there, kc against the per-op constants is a flat direction,
  pinned post hoc.
- **eta and T2.** eta sits at its lower bound 0 in 30 of the 31 time fits, so it does nothing in v3. T2 is not identified: verify-mm1v3's
  Jacobian at the all-data fit gives it a relative standard error of 273% and a correlation of -0.99 with F2. Both are still counted among the
  19 constants.
- **The census's gemmLnc instruction energy** carries a small error, left as frozen (section 4, item 7: about 4 mW).
- **Energy across kernels and layouts.** With a kernel held out (run_gemm's arms, rgm211, gemmLnc; n 363) v3's energy reads 7.40%
  against v3-ledger's 5.91% and v2form's 7.79%; with a mask layout held out 6.77% against 6.58% and 6.68%. The switch route wins on every
  experiment and card fold but carries across kernels less well than the ledger's resident term.
- **Pinned, as declared:** the path's exposure gamma and the cooperation cost T_coop (0; E211's gemmLnc at 12.1% LOEO is the miss they
  would address); address conflicts (T8; v2's piF0 and zeta kept); DRAM row locality a_row (0); the die coefficient lambda (0.0048 a C).
- **The census** covers rgm136's gemmL and gemmLnc and rgm211's gemmLn and gemmL (desk, from design b, checked against one counted
  simulator run); run_gemm's loops have no census (path 0), and no kernel outside these has one.
- **NOT RUN:** any simulator or card; new switch counts; the masked walk; E202's MNIST kernel as a fourth kernel out; a fit with more than
  six starts a fold in this folder's code (verify-mm1v3 ran 30 a fold in its own); the converged time folds carried into the energy folds;
  MM1-v3 on E212's switch-pattern arms' energy (no count).

## 9. Files and how to reproduce

**Code:** `mm1_v3.py` (the predictor), `engine_v3.py` (time), `energy_v3.py` (energy), `mm1_core_v3.py`, `kinds_v3.py`, `data_e208_v3.py`,
`data_v1pts_v3.py` (MM1-v2's files with their inputs' folder moved), `data_v3.py` (the points), `fit_v3.py` (the fits and folds),
`summary_v3.py` (scores, decisions, acceptance, the parameter file), `unread_v2_e212.py`, `unread_v3_e212s4.py`, `minima_v3.py`,
`e213_v3.py`, `postcheck_v3.py` (the checks made after the verification: the A2 line, the twins, the converged folds). **Inputs:** `inputs/`
(`SOURCES.tsv`: the 109 vendored files, each with its source path, last commit and sha256; `v2/` MM1-v2's inputs and its predictor's inputs,
`census/` (the census, a desk transcription from design b, not vendored), `e206b/`, `e207/`, `e208r/`, `e209/`, `e210/`, `e211/`, `e212/`,
`e212-unread/`). **Outputs:** `out/` (the fits in `out/fits/`; the checks in `out/postcheck_*.json`). `DECLARED-v3.md` (before any fit),
`AMENDMENT-A2.md` (post hoc); `SHA256SUMS` (every file here but itself).

From this folder, single-threaded (`OPENBLAS_NUM_THREADS=1` and the like), each with `/usr/bin/python3 -I -B`:
1. `unread_v2_e212.py --out out` (section 1; needs `../v2/` as landed);
2. `fit_v3.py time --form v3 --folds all --out out/fits`, the same for `v2form`; `--form v3_T5r --folds loeo` (and `v3_T6A`, `v3_T7L`);
   `--form v3+T5r --folds all`; `fit_v3.py energy --time-form v3+T5r --energy-forms v3,ledger --out out/fits` (with AMENDMENT-A2's pin
   in the LOCO aifoundry3 fold) and `--time-form v2form --energy-forms v2form` (the time fits about 25 minutes in one core, the energy
   fits about a minute each);
3. `summary_v3.py --fits out/fits --final v3+T5r --out out`;
4. `e213_v3.py scan --lab <the lab's top> --lanes <the round's lane folders> --out out` (depends on what is committed when it runs),
   `e213_v3.py forecast --params out/mm1_v3_params.json --scan out/neverrun_e213.json --out out`, `e213_v3.py e212 --params
   out/mm1_v3_params.json --out out`;
5. `unread_v3_e212s4.py --out out`; `minima_v3.py --out out v3+T5r v3`;
6. `postcheck_v3.py line --fits out/fits --out out`, the same with `twins` and with `converge` (about a minute in all).

**Reproduced at the freeze** (Tue 17 Nov 2026, 17:38 PST): 18 of 18 outputs byte for byte from this folder's own files into a scratch
folder (`summary_v3.py` 7, `unread_v2_e212.py` 3, `e213_v3.py` forecast and e212 5, `unread_v3_e212s4.py` 3). Not re-run there: the fits
(their record is `out/fits/`; MM1-v2's form, re-run after the reboot, reproduced the 12 folds it had finished before it), the never-run scan
(it reads the live repository and lane folders) and `minima_v3.py`.

**Reproduced after the fixes** (fix-mm1v3, Tue 17 Nov 2026 20:24:44-20:31:20 PST). The run used a `git archive` of this folder and `../v2`
as committed, taken before this paragraph went into README.md and SHA256SUMS. 24 of 26 outputs came out byte for byte:
- the two energy records, re-fitted on the re-run time record;
- `summary_v3.py`'s six outputs other than `holdout_v3.json`;
- `unread_v2_e212.py` 3, `e213_v3.py` 5, `unread_v3_e212s4.py` 3, `postcheck_v3.py` 3 and `minima_v3.py` 2.

The other two are `out/fits/time_v3+T5r.json` (the final form's time fits, re-run whole) and `out/holdout_v3.json`. Each is equal in every
leaf (14,253 and 23,852 of them) except each start's wall-clock seconds (`secs`). Not re-run: the other time forms' fits (their records are
unchanged since mm1-v3) and the never-run scan.
