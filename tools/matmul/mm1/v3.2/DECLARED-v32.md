# MM1-v3.2: every form, input, bound, start, fold, rule, acceptance test and blind-day rule, declared before any fit and before any E215 result was opened

*Written Thu 19 Nov 2026 (week 47) from 14:25 PST (Pacific, the real clock), round Q230, lane decl-v32, at aifoundry2's desk. No fit of
MM1-v3.2, no card, no simulator, no commit. **No E215 result was opened before this file and `declared-v32.json` were hashed:** no E215 data
file, no E215 scorer output (`OUT/card-e215a/rb-*`, `OUT/card-e215b/rb-*`), no `OUT/verify-e215d`, no `OUT/scores-e215`, no E215 score. E215's
two committed data folders are named here by their git object ids alone (`git rev-parse` on the commit trees; no byte of their files was
read, printed or hashed by this lane). The round's log was read only as `W/out/orch/q230/CONTEXT-before-e215-results.md` (CONTEXT.md cut
before its first line that reports an E215 result); `W/CONTEXT.md` and `OUT/decl-v32.stopped-1426` (this lane's first attempt, stopped at
14:26) were not opened. This file and `declared-v32.json` (the same declaration for a script) are frozen by their sha256 in
`DECLARED-v32.sha256` and the lane's `FROZEN.txt`; neither holds its own hash. `layout_rule_v32.py` (the layout rule as code) is frozen with
them.*

**DISCLOSURE (stated before the rules).** The orchestrator wrote this round's brief at about 14:30 PST after reading E215 arm A's and arm
B's scorer words. The candidate set, the gemmLnc term and the base form it names were fixed before any E215 datum by the frozen posts
**#1.29** (the gemmLnc term F3, 09:32:02 PST), **#1.29.1** (the layout term F1, 09:32:47 PST) and **#1.29.1.1** (verify-lay's controls,
10:31:36 PST) and by MM1-v3.1's declaration (`../v3.1/DECLARED-v31.md`, landed 7375bc9c). This lane's own choices (every threshold, margin,
seed, quota and rule below) were written from those frozen files, MM1-v3.1's landed records and the round log before E215's results; its
thresholds were fixed at 14:41:36 PST (the lane's progress log, step 12) after reading verify-lay's and lay-contention's post hoc held-out
figures on MM1-v3.1's pre-E215 data (`../v3.2-terms/layout/`), and before the code that applies them was run on anything.

The owner's words that started the matmul model (Mon 16 Nov 2026, at or before 09:48:24 PST; a voice transcription in which "matte mold" is
the matmul): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of
transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See check how
well the timing simulation for the matte mold matches reality and the energy." His words relayed on the coordination thread: "use all the
cards without restriction, all night if needed." The owner's checkpoint's step 5: fix what the blind day names, then test the fix in one card
session (E218, section 9).

**Labels.** *Registered*: a form, bound, start, threshold or rule declared here, before any fit of MM1-v3.2. *Desk*: arithmetic or a
computation from committed files at a desk. *Post hoc*: fitted or read after its data existed (every constant of MM1-v3.2 will be). *Held
out*: left out of the fit that scores it (not blind). *Blind*: scored on data that did not exist when the forecast was frozen. *Unread*:
scored on data that existed but no lane shaping the model read. *REPORTED*: printed beside a rule, never deciding it. *NOT RUN*: a check that
did not run. Error = forecast / measured - 1; rms and bias in %. Interpreter for every number here and for MM1-v3.2's fit: `/usr/bin/python3`
3.12.3, numpy 1.26.4, scipy 1.11.4, `-I -B`, single-threaded (OMP_NUM_THREADS = OPENBLAS_NUM_THREADS = MKL_NUM_THREADS = NUMEXPR_NUM_THREADS =
1), every numerical job inside the round's CPU slots (`W/slot.sh`), one slot job of the fit lane at a time, waiting while the 1-minute load is
above 6 (THE CPU RULE).

**What this file fixes, and why now.** MM1-v3.1 (`../v3.1/`, landed `2c971828`) was fitted exactly by its declaration on every committed
matmul point through E213 and frozen as built: its time model is MM1-v3's form refitted (T5r+G0+n32), its energy E1t, and two of its
acceptance rules failed (rule 1's time half was equal by construction, not lower; rule 2's LOCO energy by the anchor route read 10.92%
against 8.85%). Since then: E214, the model session's third sweep (seven sessions on aifoundry1, committed and verified, notes 10f662e3), was
scored UNREAD (`../v3.1/unread-e214/`, 21ba4b45: its declared pass rule FAILED on part A, five time and energy band rules); two candidate
terms were frozen before E215 (`../v3.2-terms/gemmlnc/`, aaeaa495: F3; `../v3.2-terms/layout/`, 595fcb59: F1 and the controls); E215,
MM1-v3.1's blind day, ran on both arms (data 8355db15 and 4f648f24). **MM1-v3.2 is MM1-v3.1's forms refitted on every committed matmul point
through E215, plus the gemmLnc energy term F3 with its two constants refitted, plus at most one layout time term chosen by section 3's rule.**
Every choice MM1-v3.2 makes from data is made by a rule written here, so nothing of MM1-v3.2 is chosen after its data are seen, and E215's
blind scores are recorded before E215 enters any fit (section 4, the gate).

## 0. On one screen

| item | MM1-v3.1 (as landed, post hoc) | MM1-v3.2 declares (registered) | decided by |
|---|---|---|---|
| T time form | T5r+G0+n32 (MM1-v3's form refitted), 19 constants | the same form and code (`../v3.1/time_v31.py`), refitted; no v3.1 item reopened | fixed (section 1) |
| E energy form | E1t (b2 = d2 = 0), 24 free constants | E1t plus F3's two constants c1, c2 in [0, 10,000] pJ a line: 26 | fixed; F3's pin rule (section 1.3) |
| L layout term | none (n/32 and the row imbalance) | at most one of N3, N1+N2, G1, G1+N1, F1, fresh24 (their frozen forms), two-stage | `layout_rule_v32.py`: LOLO margin 0.20 points, paired bootstrap, LOEO, LOCO and L3 guards, selection placebo p <= 0.05 (section 3) |
| P pins | v3.1's identifying sets | v3.1's, plus eta pinned 0 in a fold with no training point carrying the row imbalance, plus F3's | registered (section 2) |
| D data | 1,906 time and 1,832 energy points through E213 | + E214's seven sessions + E215's two arms; E216, E217 and later out | registered (section 4) |
| F folds | LOEO 18, LOCO (both routes), LOKO, leave rgm211 out, LOLO | LOEO 20 (with E214's and E215's folds and sub-folds), LOCO (the fallback route), LOKO, leave rgm211 out, LOLO | registered (section 5) |
| A acceptance | four rules in five parts; rules 1 and 2 failed | rules 1-3 restated (two changes, section 7), 4(a)-4(d), 5 (the gemmLnc points) | a script, against MM1-v3 refitted on the same data (section 7) |
| B the blind day | E215 (60 + 30 points, two arms) | **E218**: 54 points on aifoundry3 card 0 at 600 MHz: G 12 + Gt 12, Y 16 (8 pairs), F 14; about 47 card-minutes, cap 70 | its point rule at E218's registration (section 9) |

## 1. The model

### 1.1 Time (registered)

MM1-v3.1's chosen form **T5r+G0+n32** exactly as `../v3.1/time_v31.py` (`Engine31`, sha256 `4a7147eb...`) computes it: MM1-v3's op time
(`../v3/engine_v3.py`: the closed-form map, subsets mapped at the full chip's lines, the two-edge retention, T5r's shire-cache share r2 at KB <= 2
with MB x NB >= 2, G0's census path with no fitted constant from `../v3.1/inputs/census/census-v3.1.json`, n/32 in X3 and XF, the row
imbalance eta), its 19 constants (F2, T2, c3, cF, chi3, chiF, d8, eta, kA, m3, mF, pB, piF0, r2, w1, w2, x1, x2, zeta), their bounds and
start boxes as `../v3.1/declared-v31.json` item 5 gives them. **No item of MM1-v3.1's declaration is reopened**: item 8's T5r (its step 3),
item 3's G0 and item 4's n/32 (T7 out) stand as v3.1's rules chose them on v3.1's data; reopening any of them on data that hold E215 would add
a choice made after E215's data. The only change to the time model is section 3's layout factor, if one enters:

    T = T_base x clip(1 + sum_i a_i x_i, 0.3, 3.0)   at the subset points of rgm136's gemmL loop; T = T_base everywhere else

with T_base the refitted T5r+G0+n32 and the x_i the chosen candidate's features (every x_i = 0 at the full mask 0xffffffff). 'v3.1 with T7'
is not refitted (REPORTED only where earlier files froze it).

### 1.2 Energy (registered)

MM1-v3.1's chosen energy form **E1t** exactly as `../v3.1/energy_v31.py` (sha256 `21082cbf...`) computes it (`W31(p, X, sel, n2, n3, nF,
t_us, rC, 'E1t')`: W = D (R0 + kc K1), MM1-v3's switch route, the census of item 6, b2 = d2 = 0), **plus the gemmLnc term F3 in its frozen
form** (`../v3.2-terms/gemmlnc/term-gemmlnc.json`, sha256 `2ee478f8...`, posted #1.29 before any E215 datum), read with its dated note 1's
three readings:

    dW = D x sL x (n / t_op) x 1e-12 x (c1 x dup + c2 x first)          [W over idle]
    dup   = 26 duplicate line reads a minion-op at every rgm136 gemmLnc point; 0 at every cooperative loop (rgm136 gemmL, rgm211's gemmL and
            gemmLn, run_gemm) by construction
    first = (14 qA_b + 12 qB_b) / NB, with qA_b, qB_b = 1 - the L2 marginals of Q = (Q0 + Q1) / 2, the point's map at the fold's time
            constants (the same Q its line energies read), NB the arm's N blocks
    t_op  = the op time in seconds (the measured one for every 'given t' quantity and in the energy fit; the forecast one otherwise)
    D     = 1 + 0.0048 (die - 50 C), the die at the run's start (50 C at a forecast with none given); sL = 1 + xi (s_V - 1); n the minions

**c1 and c2** (pJ a duplicate line) are linear constants of the energy fit: each start's linear solve includes their two columns, the result
clipped into **[0, 10,000]** (a duplicate read returns no energy; the upper bound is about five times MM1-v3.1's fresh-line price for random
data, bF + dF = 2,024 pJ); they are not multiplied by the card's kc nor by phi (F3's frozen form has no card factor and no data term). **26
free energy constants** (E1t's 24 + c1, c2). lambda pinned 0.0048 a C; xi free in [0, 1], pinned 1 in a fold with no governed card (v3.1's
rule). **How c1 and c2 are refitted on every committed gemmLnc point and its gemmL twins:** jointly with every other energy constant on all
of a fold's training energy points; their two columns are zero everywhere but at the gemmLnc points (E211's c01c and c02c, E213's a075, a079,
a082, a086, a087, k37 and k40, and E215's a024, a026, a031, a032 and b013, those that ran), so only those identify them, while the gemmL twins
of those shapes (the cooperative points at the same shapes and cards where the data hold them; F3's Table 1 names E211's and E213's) price the
base the term sits on, as every other point does.
F3 is in MM1-v3.2 by construction (the brief's model); acceptance rule 5 (section 7) tests it held out where it acts. F3 changes no op time.

**Inputs of the energy** (registered): `census-v3.1.json` (sha256 `3e5a088e...`, v3.1's item 6); the switch counts of
`../v3.1/counts/` (landed 3e8991d0, SHA256SUMS `c74c2d49...`) and `../v3.1/counts-e214/` (landed 37ae4a87, SHA256SUMS `4c39d0d3...`,
verified HOLDS), merged in memory as `../v3.1/unread-e214/DECLARED-unread-e214.md` section e merges them (no key collides: asserted); phi by
v3.1's item 7 precedence, with E214's kinds read as that declaration read them before any E214 measurement (phi = `kinds_v3.phi` over each
new kind's registered tile file, sha256-checked against E214's `arms.json`; `pattern:sparse50f`, `sparse50h`, `sparse50i` as the committed
sparse50 kind; `fp32 pattern:sp_ar4`'s gate (g_op, g_lane, g8) = (0.5, 0, 0), arow50's); a kind with no committed count or no phi: NOT
FORECAST in energy (its time is forecast), never a nearest-kind guess. The energy fit's footing is E1t's: W over idle given the measured op
time, every point at 3 W and above weighted 1 / W_meas, below 3 W 1 / 3 W (v3.1's).

### 1.3 F3's pin rule (registered)

In every fold, let G be the fold's training energy points of rgm136 gemmLnc. **c1** is free when G holds at least one point; else pinned 0.
**c2** is free when G holds at least 3 points, its values of `first` take at least 2 distinct values (rounded to 1e-9), and the two columns
[w_i S_i dup_i, w_i S_i first_i] over G (S_i = D_i sL_i n_i / t_i x 1e-12 at the fold's lines and the measured op times; w_i the fit's weight;
each column scaled to unit Euclidean norm) have a condition number of at most 100; else c2 is pinned 0 (c1 alone, F3's one-constant reading).
Every pin is printed with its fold. (F3's frozen fit read its E213-out fold NOT IDENTIFIED on two E211 points; under this rule such a fold
takes c1 alone.)

### 1.4 The held-out card's energy scale (registered): the fallback route decides, the anchor route is REPORTED

In a LOCO fold the held-out card takes **v3.1's item 2 fallback** (MM1-v3's declared rule: the training cards' mean awake power Pa and kc = 1,
with `AMENDMENT-A2.md`'s pin in the fold without aifoundry3). v3.1's anchor route (each card's kc from its committed rgm136 gemmL1x1x4 int8
random points) is computed and printed beside, never deciding. **Why:** v3.1's own declared 'not wanted' condition for the anchor route (its
pooled LOCO above the fallback's) read True in v3.1's fit (10.92% against 9.64%), so the route that condition rejected does not decide
v3.2's acceptance. The change rescues nothing by itself: under the fallback route v3.1 still fails its rule 2 (9.64% against 9.11%, +0.53 >
0.30).

## 2. The fits: starts, seeds, tolerances and pins (registered)

**Time:** v3.1's item 5 exactly (`../v3.1/fit_v31.py` `fit_time`, sha256 `ea680db9...`, unchanged): **18 starts a fit**, the same for every
fold and form (S0-S5 MM1-v3's declared starts, S6-S17 the twelve seeded draws recorded as numbers in `../v3.1/declared-v31.json` > items >
item 5 > start_values, each restricted to T5r+G0+n32's 19 names); bounds as item 5's; phase 1 `scipy.optimize.least_squares` on forecast /
measured - 1 of the wall op time, weight 1, `x_scale='jac'`, `diff_step` 1e-4, ftol = xtol = gtol = 1e-8, at most 4,000 evaluations, from
each start; phase 2 the three lowest phase-1 costs continued at 1e-12 (at most five legs of 4,000, restarted while the cost falls by more
than 1e-9 relative); **the lowest phase-2 training cost wins** (ties within 1e-9 relative to the lower start index); every start's cost,
status and evaluations, and the flag "a winner one start alone reached", printed per fold. E146's 87 store-cadence rungs are in no training
set (scored apart).

**The pin rule:** v3.1's (`fit_v31.pins_for`: MM1-v3's identifying sets) **plus one set: eta** (the row imbalance) is pinned at its neutral
0 in any fold whose training set holds no point with engine_v3's row-imbalance flag (a subset mask with all four column groups active and
fewer than eight row groups). **Why:** in v3.1's LOLO compact fold no training point carried the term, eta stopped at its bound 2.0 where the
optimizer left it, and the compact class read 118.2% (v3.1 README, its finding); re-read with eta at 0 it read 6.17%. The pin makes that
reading the declared one (it is verify-lay's and lay-contention's LOLO (b)); it binds MM1-v3 refitted alike. **F3's pins:** section 1.3.

**Energy:** v3.1's item 5 energy procedure exactly (`fit_v31.fit_energy`): nine starts (MM1-v3's three and the six seeded draws recorded in
`declared-v31.json`), each start's linear constants (c1, c2 among them) by the linear solve at its nonlinear values, clipped into bounds;
`least_squares` on (W - W_meas) / max(W_meas, 3 W), ftol = xtol = gtol = 1e-12, at most 3,000 evaluations; the lowest cost wins; **each energy
fold reads its own time fold's phase-2 winner** (lines, op times, retention, and F3's `first` from the same map).

**The layout term** is fitted two-stage on each fold's time winner (section 3); it changes only the op time of the subset points of rgm136
gemmL, so only the quantities 'with the seconds forecast' (and the wall cycles) see it; the energy fit and every 'given t' quantity read the
measured op time.

**Cost** (desk, from v3.1's record): about 2.5 minutes a time fit with phase 2; 42 time fits (20 LOEO folds and 9 sub-folds, 4 LOCO, 4 LOKO,
leave rgm211 out, 3 LOLO, all data) and their energy fits under two forms: about 2-4 hours in one slot; the layout rule a few minutes
(two-stage, closed form; the placebo 1,000 re-runs).

## 3. The layout term: at most one, by a declared rule (item L; `layout_rule_v32.py`)

### 3.1 The candidates (their frozen forms, registered)

Each is T = T_base x clip(1 + sum a_i x_i, 0.3, 3.0) at the subset points of rgm136's gemmL loop (every subset point of MM1-v3.1's data is
one, 212 points of E206-E213, and E214 and E215 run rgm136 gemmL at their masks; a subset point of another loop, if any, takes no term),
every x_i exactly 0 at the full mask:

| candidate | features x_i | constants | where frozen | its frozen all-data constants on MM1-v3.1's data (REPORTED) |
|---|---|---|---|---|
| none | - | 0 | MM1-v3.1's n/32 form | - |
| N3 | 32/n - 1 (shire count only) | 1 | `controls-e215/v02_fits.py`, post #1.29.1.1 | +0.00100737 |
| N1+N2 | 1 - n/32, (1 - n/32)^2 (shire count only) | 2 | the same | -0.0934896, +0.117657 |
| G1 | (110 + 12 h_mean(mask)) / (110 + 12 h_mean(full)) - 1 (the active shires' mean hops to the 32 L3 homes) | 1 | `DECLARED-layout-addendum-1.md`, the same | +0.303143 |
| G1+N1 | G1 and 1 - n/32 | 2 | `controls-e215/v02_fits.py` | +0.602213, -0.0216757 |
| F1 | Phi_fresh: the walk's strict-LRU 32 MB L3 DRAM lines a step over the line requests a step, minus the full chip's | 1 | `DECLARED-layout.md`, post #1.29.1 | -0.0831659 |
| fresh24 | Phi_fresh with a 24 MB L3 | 1 | `controls-e215/v02_fits.py`, post #1.29.1.1 | -0.0899132 |

n = the mask's active shires; h_mean on the public mesh map in `workloads/nocbench/analyze.py`, as verify-lay's `v01_map.py` computes it. **Every feature is computed by verify-lay's `controls-e215/v01_map.py` functions** (sha256 `b5a88d33...`; its request generator
equals the masked walk's chip steps at 148 of 148 configurations, its fresh lines lay-contention's to 4.6e-7 lines a step: verify-lay's check
1; Q229's `controls_e216.py` called the same functions for E216's points), for every subset configuration of the data (E206-E215) and of
E218's Y candidates, keyed as `rgm136.gemmL|<MB>x<NB>x<KB>|0x<mask>` with the shape's full-chip configuration beside it. **F1's feature is
lay-contention's frozen Phi_fresh**; at the fit's start the lane checks that v01_map's fresh32 Phi equals `features_layout.py` +
`eval_layout.phi_of`'s Phi_fresh within 1e-5 at every subset configuration of the data, and a configuration that fails takes
features_layout.py's value for F1 (named). **The L3 conventions are a condition of F1 and fresh24** (verify-lay's finding 4): the walk's
lock-step stream, strict LRU at the stated capacity, C stores allocating in the L3, pools 4 KiB aligned, lines interleaved over the 32 L3 homes
by PA[10:6] and over the eight memory shires by PA[8:6]; v01_map also gives fresh at 16, 48 and 64 MB (16 and 64 REPORTED; 48 enters
condition (v)).

### 3.2 The fit and the scores (registered)

**Two-stage**, exactly as verify-lay's `v02_fits.evaluate` (reproduced by `layout_rule_v32.py`, section 3.5): in each fold the base is the
fold's own refitted T5r+G0+n32 (section 2); the term's constants are the normal-equation solution of the fold's training residuals,
minimising sum over the fold's training subset points (E146's store rungs out) of (r_i (1 + M_i a) - 1)^2 with r_i = T_base,i / T_meas,i
(least squares where the normal matrix is singular); the held-out points get T_base x clip(1 + M a, 0.3, 3.0); the all-data constants solve the
same on every training subset point. The base's constants are not refitted with the term (a joint refit of the winner is REPORTED, section 8).

**Scores** (every one over MM1-v3.2's own fits; the bundle `layout_rule_v32.py` reads, its docstring):
- **LOEO_nt**: the pooled wall-cycle rms over every point the 20 main LOEO folds hold out (section 5), configuration twins excluded;
- **LOLO**: the wall-cycle rms over every subset point, each scored by its layout class's LOLO fold (v3.1's item 4 classes: compact if
  n = 4R, spread if R = min(8, n), else other; n = 1 other), the compact fold under section 2's eta pin;
- **LOCO_sub[card]**: the rms over each card's subset points in its LOCO fold, and the term's constants in each of the four LOCO folds.

### 3.3 The rule (registered; in this order)

**Eligibility.** A candidate c is eligible when every condition holds:
1. **(i) the margin:** LOLO_c <= LOLO_none - **0.20** points;
2. **(ii) the paired bootstrap:** over 10,000 resamples of the LOLO points with replacement (`numpy.random.default_rng(20261121).integers(0, n,
   size=(10000, n))`, one index matrix for every candidate), the 97.5th percentile (`numpy.percentile`, linear) of rms_c - rms_none is below 0;
3. **(iii) the pooled guard:** LOEO_nt_c <= LOEO_nt_none + **0.02** points;
4. **(iv) the card dependence** (verify-lay's finding 5: F1's constant ran -0.167 on aifoundry2 card 0, -0.087 on aifoundry1 card 1, -0.017 on
   aifoundry3 card 0 and +0.008 on aifoundry1 card 0, and E213 alone gave +0.109): LOCO_sub_c[k] <= LOCO_sub_none[k] + **0.30** points for
   every card k with a subset point, **and** each constant of c has one strict sign in all four LOCO folds;
5. **(v) the L3 conventions** (verify-lay's finding 4: F1's constant flips sign at 16 MB and fails at 48 and 64 MB), for F1 and fresh24 only:
   the all-data constant of the one-feature form has one strict sign at **24, 32 and 48 MB** alike.

**Choice.** Among the eligible candidates, the lowest LOLO; within **0.10** points of it, the fewest constants, then the lower LOEO_nt, then the
fixed order **N3, N1+N2, G1, G1+N1, F1, fresh24** (the forms that assume no placement model first). No eligible candidate: **none**.

**The selection placebo** (the whole selection, verify-lay's finding 3: F1's gain read -0.071 points with a 95% interval [-0.171, +0.032],
and its whole-selection placebo p = 0.050). For i = 0 ... 999 the subset points' feature rows are permuted jointly
(`numpy.random.default_rng(20261122 + i).permutation(n_sub)`, one permutation applied to every feature column alike, the 24 and 48 MB
features included) and the eligibility and the choice are re-run unchanged; d_i = LOLO(winner_i) - LOLO_none, 0 with no winner;
**p_sel = (1 + #{d_i <= d_obs}) / 1,001. The rule's winner enters MM1-v3.2 only if p_sel <= 0.05; else none.**

**Labels** (REPORTED, never deciding; verify-lay's findings 1 and 2): N3 and N1+N2 are *shire-count corrections* (no placement information); a
placement candidate that enters (G1, G1+N1, F1, fresh24) is called a *placement term* only if its LOLO is below that of at least 950 of 1,000
permutations of its own features within (n, arm token, card) groups (`numpy.random.default_rng(20261123 + i)`), else *a shire-count and shape
correction*.

**Why these numbers.** The margin 0.20 points is twice the half-width (0.10) of verify-lay's 95% interval for F1's LOLO gain and larger than
every one-constant candidate's gain on MM1-v3.1's data (F1 0.071, fresh24 0.129, G1 0.147, N3 0.192; REPORTED, post hoc); a term must also
win significantly on the LOLO points (ii), not raise the pooled held-out error by more than the 0.02 points within which F1's LOEO change
sat (iii), hold its sign and its gain on every card (iv), and, for the Phi_fresh forms, not hinge on the L3's size within 24-48 MB (v). The
placebo charges the choice among six. The tie order prefers fewer assumptions.

### 3.4 What shows the term is not wanted (registered)

None enters when no candidate is eligible or the winner's p_sel exceeds 0.05: MM1-v3.2's time is then MM1-v3 refitted's by construction
(section 7, rule 1). A term that enters with a factor within 1% of 1 at every point of the data (|sum a_i x_i| <= 0.01 everywhere) is
reported as not identified (no change).

### 3.5 The code and its desk check (desk, REPORTED)

`layout_rule_v32.py` implements 3.2-3.3 exactly (its docstring is the rule). Before any fit of MM1-v3.2 and before any E215 result was
opened, this lane ran (in the round's CPU slots, one thread, `/usr/bin/python3` 3.12.3, numpy 1.26.4):
- `layout_rule_v32.py selftest`: two synthetic bundles (600 points, 240 subset points, 4 cards): with no layout effect the rule chooses
  **none**; with a planted N3 effect it chooses **N3** with p_sel 0.005 (200 placebo permutations in the selftest): **PASS**;
- `layout_rule_v32_deskcheck.py`: the bundle built from MM1-v3.1's committed fold record (`../v3.1/out/fits/time_T5r+G0+n32.json`, sha256
  `2db8c958...`; 25 fold bases from verify-lay's cache, each equal to the record's stored predictions: worst relative difference 0.0) and
  verify-lay's committed features (`controls-e215/work/v01_map.json`, sha256 `096fa1a9...`) re-makes verify-lay's held-out figures for all
  seven candidates (LOEO_nt, LOLO with the compact fold's eta at 0, the all-data constants): **worst absolute difference 0.0** (none 4.7228 /
  6.3195; N3 4.7016 / 6.1274; N1+N2 4.6986 / 6.0662; G1 4.7030 / 6.1725; G1+N1 4.7002 / 5.8881; F1 4.7101 / 6.2480; fresh24 4.7180 / 6.1900,
  in %, LOEO_nt / LOLO). **The rule's eligibility, bootstrap, placebo and choice were not run on any real data**: they decide only on
  MM1-v3.2's own fits.

## 4. The data (registered)

**The rule.** MM1-v3.2's data are, and are only:
1. **every point MM1-v3.1 read** (its fit at GitHub main f0d58c84: 1,906 time and 1,832 energy points, E105-E213 with E212's ten sessions and
   E213's two arms), from the same vendored inputs (`../v3/inputs/SOURCES.tsv`, sha256 `3e7009e8690018805c91fb2658a5dea4aeb7e45a1e5931f44b1ad897a7708731`;
   `../v3.1/inputs/SOURCES.tsv`, sha256 `76f5e7af41021f518cfcec6bc9431e50fcdd3be35bf1dad50682f8dc52c4570f`; `../v2/inputs/MANIFEST.json` as
   MM1-v3 vendored it), every file checked against its listed sha256 at the fit's start;
2. **E214's seven sessions** (the model session's third sweep, registered 95eb8069, data verified HOLDS WITH FIXES, notes 10f662e3), read
   from these reductions, each checked by its sha256 at the fit's start:

| session | data folder (`docs/reports/data/`) | reduction | sha256 | data commit |
|---|---|---|---|---|
| a1c0-S1 | `2026-11-18-e214-mmsweep3-a1c0-S1` | `data-e214-a1c0-S1.json` | `10bf37ac692097be692000c36ab6c49eedc8e11298eef915e7f761fe09094442` | 3b3e4182 |
| a1c0-S2 | `2026-11-18-e214-mmsweep3-a1c0-S2` | `data-e214-a1c0-S2.json` | `1d85c3f84e5216b5ccf64b1ec6d37b00b071770b342d8949025a62e282ddfb2e` | 317ce38c |
| a1c0-S3 | `2026-11-18-e214-mmsweep3-a1c0-S3` | `data-e214-a1c0-S3.json` | `e22515115a4f712cf08a3b9a1940c5244473d7bf1db93f2aa58f8fb1f8d094ea` | 117ca637 |
| a1c1-S1 | `2026-11-18-e214-mmsweep3-a1c1-S1` | `data-e214-a1c1-S1.json` | `e292c5b24adf311326cd207824a93c13f951851570c8590063f0436649300ea6` | f7f3257c |
| a1c1-S2 | `2026-11-18-e214-mmsweep3-a1c1-S2` | `data-e214-a1c1-S2.json` | `4220077f668729bd97a772f6bdb84f1f5e2ccbd0169570356305894804d63128` | a457d7fc |
| a1c1-S3 | `2026-11-18-e214-mmsweep3-a1c1-S3` | `data-e214-a1c1-S3.json` | `8fbb1d36a95f80aee92a74ac5d14330b49610a9f8e7b524b087fd814c9d710b0` | 9ac3c338 |
| a1c1-S4 | `2026-11-18-e214-mmsweep3-a1c1-S4` | `data-e214-a1c1-S4.json` | `a7691bd90b934ca5a4b4fa993fd5d13a5b94bba17ee5e5cc182934f855155848` | 0e95201d |

3. **E215's two arms** (MM1-v3.1's blind day, registered 4cb2c2ad, kit 8bde0182), named by git object ids (no byte read by this lane):

| arm | data folder (`docs/reports/data/`) | data commit | the folder's tree id | `data-e215.json` blob id |
|---|---|---|---|---|
| A, aifoundry3 card 0 | `2026-11-19-e215-blind-matmul-aifoundry3` | `8355db15874ab349d7f7a466a6365c88180fc9e2` | `8d8b2f940c45e08fdd6c6223e4dee9ac52dca081` | `d88420610ecb17f87f984ce5e94f2c3f10db7b97` |
| B, aifoundry1 card 1 | `2026-11-19-e215-blind-matmul-aifoundry1-c1` | `4f648f24b9ab49db9eecfc0269231faa0cb2305a` | `19282fc4b4bc5fc7e294c10169a94e2ec98a35ab` | `f6cc1cff2314c02dfb8a46221253e0b25d706069` |

   The fit lane checks at its start that `git hash-object` of each `data-e215.json` equals its blob id here and records the file's sha256 in
   its README inputs table and fit record before any MM1-v3.2 residual is read; a mismatch stops the fit. A dated note committed later in an
   E215 data folder (a 'ran before' label, a wording note) changes no datum and no point's membership.

**Nothing else.** E216, E217 and any later matmul experiment are not MM1-v3.2's data, even if committed before the fit starts; one enters
only by a dated amendment before the fit. **The fit lane opens no E216 or E217 data file** (they stay tests MM1-v3.2 can be scored on later).

**The readers** (registered):
- **E214** by E212's reader (`../v3/data_v3.py` `mms_runs` for time, `../v3.1/data_v31.py` `mms_runs_all` for energy, unchanged; desk check:
  E214's reductions carry E212's keys, `card`, `primary_view`, `session`, `runs` with `values`, `shires`, `role`, `ran`); **one time point a
  (card, case)** over that card's E214 sessions (a case run in two sessions is one record, the form `comparator_4a_v31.py` makes for E212), at
  the runs' measured clock, volts and die as the reader gives them; one energy point a (experiment, card, configuration, kind).
- **E215** by `data_v31.py`'s E213 reader applied to each arm's `data-e215.json` with `tools/claims-v3/e215/points-e215.csv` (sha256
  `4abea340...`; E215's reducer writes E213's form: its scorer's `--selftest-real` read E213's committed bytes equal to MM1-v3.1's reading);
  one time point a (card, case), the case as E215's registration spells it (loop|arm|format|mask), the mean over the case's runs of each kept
  run's cycles a GEMM / ops a minion; one energy point a (card, configuration, kind); a run whose host record differs from its registered point,
  or whose identity or walk gate is not good, is set aside as E215's reducer flags it; the references (r01, r02, r11, r12) and ties (t01,
  t02) are points (twins wherever their configuration is in training); smoke processes are not points. A field the reader needs that E215's
  form names otherwise is mapped by a dated departure written before any MM1-v3.2 residual is read.
- **Twins** (MM1-v3's definition): a scored point is a twin when its card, kernel, arm, format, mask and clock (to 25 MHz) are in the
  training set that priced it (energy adds the kind). **Headline figures exclude twins; the figures with them are printed beside.**

**The gate** (registered): E215 enters only after **E215's blind scores are committed on GitHub main** (Q224's scores lane: arm A's, arm
B's and the pooled verdicts), so the blind record precedes any fit; if they are not committed by 06:00 PST Fri 20 Nov 2026, the fit starts
without waiting and its README says so. The fit reads GitHub main at its start (named in its README) and checks that both E215 data commits
are ancestors of it.

## 5. The folds (registered; every constant refitted from section 2's starts in every fold, the pin rule, each energy fold on its time fold)

- **LOEO, 20 folds:** E105, E107, E119, E126, E136, E146, E158, E159, E168, E169, E190, E206 (A and B), E207, E208, E209, E211, E212, E213 (A and
  B), **E214**, **E215** (A and B); sub-folds E212 by card (a1c1, a1c0, a2c0), E213 by arm (A aifoundry3 card 0, B aifoundry1 card 1), **E214 by
  card** (a1c0, a1c1) and **E215 by arm** (A aifoundry3 card 0, B aifoundry1 card 1); E210 for energy.
- **LOCO**, 4 cards; energy under the fallback route (section 1.4), the anchor route REPORTED.
- **LOKO:** rgm211 gemmLn, rgm211 gemmL, rgm136 gemmLnc, run_gemm; **leave rgm211 out** (every rgm211 point in one fold).
- **LOLO:** compact, spread, other (section 3.2), under section 2's eta pin.
- **Labels of the newest folds:** the E214 fold is held out for every constant and post hoc for the layout choice (its subset points are in
  the rule's LOLO and LOEO); the E215 fold the same (its registered family-L subset points and gemmLnc points, those that ran, enter the
  layout rule and F3's constants in every other fold).

**The baseline, "MM1-v3 refitted"** (registered): MM1-v3's forms, time T5r+G0+n32 (MM1-v3.2's base) and energy E1u (b2 and d2 free, no F3),
on exactly MM1-v3.2's inputs (census-v3.1, every count of section 1.2 and its phi rule, the data, folds, twins, pins including eta's, starts,
seeds and tolerances, the fallback route). Its time fits are MM1-v3.2's base fits (one set of time fits serves both); its energy fits are its
own.

## 6. Scores (registered)

Wall cycles, the counter's mean, seconds, J over idle given t and with t forecast, J at rest both ways; per point (MM1's points: one a card and
case for time, one a configuration and kind for energy), rms and bias; J over idle at 3 W and above, watts below. Every LOEO, LOCO, LOKO,
LOLO and leave-rgm211-out figure for MM1-v3.2 and MM1-v3 refitted on the same points, without twins and with them.

## 7. Acceptance (registered; against MM1-v3 refitted on the same points and folds; a script decides from the two models' fold tables)

1. **LOEO** wall cycles (every point, no twin) and LOEO W over idle given t (no twin, at 3 W and above, the points both price): MM1-v3.2's
   energy rms **lower**; its time rms **lower**, or, when section 3's rule chose none, **EQUAL BY CONSTRUCTION** (MM1-v3.2's time is MM1-v3
   refitted's: PASS, printed so).
2. **LOCO** wall cycles (every point) and LOCO W over idle given t (the fallback route for both models; every point both price at 3 W and
   above): not worse than MM1-v3 refitted's by more than **0.30** points in either; the anchor route's figures beside.
3. **Leave rgm211 out:** wall rms at or under **8.0%** over its points, and at least **7 of E211's 10** W pairs inside 0.05 in ln.
4. Each newest fold against the frozen predecessor's error on the same points, per case (time, wall cycles) and per point (W over idle given
   t at 3 W and above, both pricing); twins included as MM1-v3's rule 4 was scored, without twins REPORTED; PASS when MM1-v3.2's rms is lower
   in both:
   - **(a)** the E212 fold against MM1-v2's unread error on the same nine-session E212 records, by `../v3.1/comparator_4a_v31.py` unchanged
     (sha256 `17b336e1...`);
   - **(b)** the E213 fold (both arms, the 127 points; the four references REPORTED) against MM1-v3's blind error from scores-e213's committed
     outputs, as v3.1's rule 4(b);
   - **(c)** the E214 fold against **MM1-v3.1's UNREAD error**: MM1-v3.1's frozen predictor (`../v3.1/mm1_v31.py` with
     `out/mm1_v31_params.json`, sha256 `d01009a0...`, unchanged) called at each of MM1-v3.2's E214 points with the inputs that point's fold
     prediction is given (card, arm, format, kind, mask, its mean clock, its volts and die as the reader gives them; W at the measured op
     time); `../v3.1/unread-e214/scores-unread-e214-cases.csv` (sha256 `3840e93f...`) REPORTED beside as a check of the call;
   - **(d)** the E215 fold (both arms, every registered and post hoc point; references and ties excluded) against **MM1-v3.1's BLIND error**, by
     the same call at MM1-v3.2's E215 points; E215's registered scorer figures REPORTED beside.
5. **The gemmLnc points:** LOEO W over idle given t over every rgm136 gemmLnc energy point (no twin): MM1-v3.2's rms **at most half** of MM1-v3
   refitted's **and at most 15.0%**.

**Accepted** when every rule passes. If one fails, MM1-v3.2 is still frozen as built, the verdict names the rule, and E218 still runs (the
checkpoint's step 5: the fix is tested in one card session either way).

**How these differ from MM1-v3.1's rules, and why.** (1) Rule 1's time half passes when the time forms are identical by construction: v3.1's
FAIL there was a tie of identical forms fitted on identical data, fixed before any fit, which tested nothing; where a layout term enters the
strict 'lower' stands. (2) Rule 2 reads the fallback route (section 1.4): v3.1's own condition rejected the anchor route, and v3.1 fails rule 2
under the fallback route too, so the change does not rescue a failure of that kind by itself. (3) Rules 4(c) and 4(d) are new: a refit must hold
out at least as well, on the newest data, as its frozen predecessor forecast them unread and blind. (4) Rule 5 is new: it tests MM1-v3.2's one
energy change where it acts (MM1-v3.1 alone read 32.6% rms in W over idle at the nine committed gemmLnc points; F3 held out 9.6-12.8%,
post hoc). Rules 3, 4(a) and 4(b) are v3.1's, unchanged.

## 8. REPORTED (never deciding a rule)

- Every candidate's LOEO_nt, LOLO, LOLO by class, LOCO_sub by card, the LOCO-fold and all-data constants, each condition of 3.3, the bootstrap
  interval, the placebo's p_sel and its winners' counts; the label check; the chosen term's in-sample constant by card; **the chosen term
  refitted jointly** with every time constant (`fit_v31.fit_time` unchanged, 18 starts, the constant free in [-3, 3] from 0) on the LOEO and
  LOLO folds, if the slots allow (else NOT RUN).
- F3: c1 and c2 in every fold with their pins; F3's frozen E215 forecasts (`forecasts-gemmlnc-e215.csv`, sha256 `00fcaf5d...`) against E215's
  measured gemmLnc points (a024, a026, a031, a032, b013; NO DATA where a point did not run) beside MM1-v3.2's E215-fold figures; the NB 12-15
  points a024 and a026 as the clean test of F3's 1/NB form; the self-heating share named by verify-lnc (c1, c2 are effective constants).
- MM1-v3.1's and MM1-v3's blind error on E215 by family (P, C, R registered; L, S post hoc), and 'v3.1 + gemmLnc term', 'v3.1 + contention' and
  verify-lay's controls on E215's points (their frozen columns), as a reading beside rule 4(d).
- The anchor route's LOCO; v3-ledger refitted (as v3.1 did).
- For every constant of the final fit: its all-data value, bound activity and relative standard error from the Jacobian (central
  differences, s^2 pinv(J^T J)); above 100% not identified (no change of the fit).

## 9. E218: MM1-v3.2's blind day (registered here: the point rule and the forecasts to freeze; its scoring rules at its registration)

**When and where.** Registered after MM1-v3.2 lands (the land's push is its forecasts' freeze line); aifoundry3 card 0 at its pinned 600 MHz
(read, never set), one arm, E215 arm A's card-day form (`tools/claims-v3/e215/`, `OUT/card-e215a` as the form of a day on that card); as the
lab's bookings allow.

### 9.1 Common to every family (registered)

- **The kernel:** rgm136, E136's binary unchanged (ELF `aace138caf8071cc...`, `.text` `61315bf6a449c282...`, the loadable identity aifoundry3's
  kit gates on, as E215 arm A): its gemmL loop and its gemmLnc branch. ops a minion a GEMM = 64 MB NB KB; M = 1,024 MB, N = 512 NB, K = KB x
  the format's K block (fp32 512, fp16 1,024, int8 2,048).
- **Never ran (E215's form):** E215's scanner (`tools/claims-v3/e215/desk/neverrun_e215.py`, sha256 `9e68b001...`, with E213's
  `neverrun_e213.py` at its pin: its token rule, roots, folder classes and reader) re-run at E218's registration on the lab at GitHub main then
  and every round lane folder then, E218's own subtracted, plus MM1-v3.2's measured points. Readings: **F** the shape token never ran on
  **any** card (no hit anywhere and no MM1-v3.2 point of the token); **G and Gt** the token (`gemmLnc<..>` for G, `gemmL<..>` for its twin)
  never ran on **aifoundry3 card 0** (no hit counted for it by E213's classes: a folder naming aifoundry3 or a3, or naming no card; and no
  MM1-v3.2 point of the token on that card); **Y** the configuration (shape, mask) never ran on aifoundry3 card 0 (E215's post hoc L reading
  on this card: no MM1-v3.2 point holds it there and no scanned file counted for the card holding the shape token names the mask). The card
  lane repeats the scan right before its first card command (E215's step 6n form).
- **One shape, one slot:** no two E218 points share (MB, NB, KB), except a G point and its twin and a Y pair's two masks.
- **The planning line (the brief's 3 W rule):** a point's planning peak PP = the largest W over idle at its own seconds at 600 MHz over MM1-v3.2,
  MM1-v3.1, MM1-v3, MM1-v2, 'v3.1 + gemmLnc term' and 'v3.1 + contention' (each where it prices), plus aifoundry3 card 0's rest law at its T0
  forecast (MM1-v3.2's params: the ledger v2 footing law, 54.4 C), plus 2 W; for a G point MM1-v3.2's W is taken x (1 + 2 eps_G), eps_G =
  MM1-v3.2's LOEO no-twin W-over-idle-given-t rms over the gemmLnc points (rule 5's figure, as a fraction). **No point qualifies whose PP
  is at or above 67.0 W** (within 3 W of the 70 W board stop); every candidate's energy must be priced by MM1-v3.2.
- **Ties** in a ranking: scores within 1e-12 relative of each other are one tie, broken by the sorted string `loop|token|format|kind|mask`
  (this settles E215's one-ulp reading, D2 (i), before the draw). **Draws:** `random.Random("v3.2-blind|E218|<family>|<stratum>").sample` of
  the stratum's remaining qualifying candidates sorted by that string.
- **The draw order:** G (with Gt), then Y, then F; 'new to E218' means a shape not already drawn.

### 9.2 Family G (rgm136 gemmLnc) and its cooperative twins Gt (12 + 12)

- **Grid:** `gemmLnc<MB>x<NB>x<KB>`, MB 1-8, NB in {1, 2, 3, 5, 6, 12, 13, 14, 15}, KB in {1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28,
  32, 40, 48}, the full chip, random data; fp32 in every regime, int8 also in regime L2 (F3's fit holds int8 only there).
- **Regimes** (MM1-v3.2's map at 600 MHz, Q = (Q0 + Q1) / 2; beyond = 14 (1 - qA_L2) + 12 (1 - qB_L2), E216's reading): **L2** beyond < 2.6
  (L2-resident); **NB1-3** NB <= 3 and beyond >= 2.6; **NB5-6** NB in {5, 6} and beyond >= 2.6; **NB12-15** NB in {12, ..., 15} and beyond
  >= 2.6. Quotas **L2 2, NB1-3 4, NB5-6 3, NB12-15 3**; an unfilled quota passes on in the order L2, NB5-6, NB12-15, NB1-3 (then L2 again).
  Fewer than 9 G points in all: the family is short (a gap, said).
- **Score:** s = |ln(W_v3.2 / W_v3.1)| of W over idle at its own seconds (where the refitted term and MM1-v3.1 part most); in each regime
  ceil(q / 2) by descending s, the rest by the regime's draw. A candidate qualifies when its token and its twin's never ran on the card, both
  PPs are under 67.0 W, its shape is new to E218, and no G point already drawn shares its (NB, KB, format) (E216's draw concentrated on two
  shape families whose per-op forecasts are identical across MB: this clause spreads the per-op forecasts).
- **Gt:** each G point's twin, rgm136 `gemmL<MB>x<NB>x<KB>` at the same format and data, the full chip (F3 is exactly 0 there): a control
  for the term (the same models, minus the term).
- **The G block runs LAST** in the session, after its own smoke (s03 gemmLnc2x2x2 fp32, its family's stop path, E215's form), its points by
  PP ascending, then reversed; the Gt points run in passes 1 and 2 with the rest.

### 9.3 Family Y (subset masks in equal-count pairs; 8 pairs, 16 points)

- **Grid:** rgm136 `gemmL<MB>x<NB>x<KB>`, MB in {1, 2, 4}, NB in {2, 4, 8, 16}, KB in {4, 8, 12, 16, 24}, fp32, random; masks (every one a
  product of row groups and column groups, as E215's `points_e215.py` requires): n = 2: 0x3, 0x5, 0x11, 0x101, 0x10001, 0x1000001; n = 4: 0xf,
  0x33, 0x1111, 0x3030, 0xf000, 0x1010101; n = 8: 0xff, 0xf0f, 0x3333, 0x5555, 0xff0000, 0x11111111; n = 16: 0xffff, 0xff00ff, 0xf0f0f0f,
  0x33333333, 0x55555555, 0xffff0000. A pair is two masks of one n at one shape (15 a shape and count).
- **Score:** with every candidate of section 3 at MM1-v3.2's all-data two-stage constants (the rule computes them for all seven, whichever
  entered), d_c(p) = ln(T_c(mask a) / T_c(mask b)) at 600 MHz and **D_p = max_c d_c(p) - min_c d_c(p)**: where the layout candidates disagree
  most. **Six pairs by descending D_p** (at most one pair a shape), then **two control pairs**: the smallest D_p among pairs where MM1-v3.2's
  base also prices both masks alike (|d_none| <= 0.0005), at shapes new to E218. Each point passes section 9.1. Fewer than 6 + 2: short.
- **Ids:** y01a/y01b ... y08b, the pair's lower mask first; y01-y06 in rank order, y07-y08 the controls.

### 9.4 Family F (the full chip, new sizes and formats; 14)

- **Grid:** rgm136 `gemmL<MB>x<NB>x<KB>`, MB 1-16, NB 1-16, KB in {1, 2, 3, 4, 6, 8, 12, 16, 24, 32}, the full chip, random, in fp32, fp16 and
  int8; the shape token never ran on any card.
- **Score:** s = |ln(cycles_v3.2 / cycles_v3.1)| of the wall cycles at 600 MHz (where the refit moved the forecast most). Quotas **fp32 4, fp16
  5, int8 5**; in each, ceil(q / 2) by descending s, the rest by the format's draw; each passing section 9.1.

### 9.5 The order, the run, the stops, the card time (registered for E218's kit, in E215 arm A's form)

- **The order:** the opening smoke s01 (gemmL2x2x2 fp32, the session's gate); tie t01 (E206's p001, gemmL2x4x4 fp32 random, the full chip:
  the bridge to earlier days on this card); pass 1 (Gt, Y and F in `random.Random("E218|A|pass1")`'s shuffle of their sorted ids); tie; pass 2
  (pass 1 reversed); tie; then the G block (s03, the G points by PP ascending, then reversed). 54 points: 42 in each pass, 12 x 2 in the G
  block, 3 ties: **111 runs** and 2 smoke processes.
- **A run** (E206's form): its die gate (min(60, the session's rest die + 4) C, waited at most 300 s, else NO DATA), 10 s at rest, one host
  process `--seconds 6 --budget 7.5` under a plain `timeout 10` (never `-k`; no SIGKILL to a device process, sent or arranged), a 4 s tail.
- **The stops (arm A's):** the board strictly above **70 W on 3 samples** in a row; the shires' mean die at or above **70 C**; the
  hottest-sensor latch at or above 70 C once it has risen during the session; a stop touches the host's stop file, never a kill.
- **Card time:** planned at the pace of the last committed session in this run form on aifoundry3 card 0 (E215 arm A's, read by E218's
  registration; else E213 arm A's 24.47 s a run): about **47 card-minutes** at 24.47 s; **no run starts after 60 card-minutes** from the first
  card command; **the session ends at 70** (the cap), after the run in progress. If the plan exceeds 55 card-minutes, F's drawn points are
  dropped first in reverse draw order, then F's scored ones (never G or Y).
- **Reads only**, as E215 arm A: the start config gate (TDP 0 W, threshold 65 C, minion 600 MHz, as found), nothing set, the card's lock held,
  et-who empty, one session of ours on aifoundry3.

### 9.6 The forecasts to freeze (by E218's registration's commit, from the landed predictors unchanged; each given exactly this)

Every model is called at **card 'aifoundry3 card 0', the point's arm token, format, kind ('random'), mask, f = 600.0 MHz, kernel 'rgm136'**;
volts not given (the card's own, `mm1_core_v3.volts`), the governed base not given (0 W on a pinned card), the start die not given (energy at
a 50 C die; J at rest at the rest law's T0 forecast, 54.4 C); ops a minion 64 MB NB KB, 32 minions a shire of the mask:

| column | what it is given |
|---|---|
| **MM1-v3.2** | `mm1_v32.Model(out/mm1_v32_params.json).predict_many([...])`: the land's predictor (MM1-v3.1's code with F3 in its energy and the chosen layout factor, if any, in its time), the call above |
| **MM1-v3.1** | `../v3.1/mm1_v31.py` with `out/mm1_v31_params.json` (`d01009a0...`), `predict_many`, the call above |
| **MM1-v3** | `../v3/mm1_v3.py` `Model(out/mm1_v3_params.json).predict(card, arm, fmt, kind, mask, 600.0, kernel=kernel, t0_c=None)`, its SHA256SUMS checked first; a kind without its committed count NOT FORECAST in energy |
| **MM1-v2** | `e213_v3.v2_model().predict(card, arm with gemmLnc read as gemmL, fmt, kind, mask, 600.0, V=None, t0_c=None)` (E215's form: a gemmLnc point priced as its rgm136 gemmL twin, literally) |
| **'v3.1 + gemmLnc term'** | MM1-v3.1's call plus F3 at its frozen constants (c1 254.4, c2 552.1 pJ: `term-gemmlnc.json`) with dated note 1's readings (Q = (Q0 + Q1) / 2 of the predictor's output; t_op its op time x 1e-6 s; D at the predictor's 50 C die), added to W over idle at MM1-v3.1's op time (in given() it adds dW t_op to B); exactly 0 at every cooperative point |
| **'v3.1 + contention'** | MM1-v3.1's wall op time x (1 + a Phi_fresh), a = -0.08316593007433395, Phi_fresh by `features_layout.py` and `eval_layout.phi_of` as frozen (1 at the full chip); seconds = its op time x the ops a minion; W over idle by MM1-v3.1's affine form A + B / t_op at that op time |
| **verify-lay's controls** | N3, N1+N2, G1, G1+N1, fresh24 at verify-lay's frozen all-data constants (`OUT/verify-lay/work/v02_fits.json`, sha256 `1bfec7fc...`; Q229's `constants-verify-lay.json`, `eb7f2733...`), T = T_v3.1 x (1 + sum a x) on `v01_map.py`'s features, made by Q229's caller's method (`controls_e216.py`, sha256 `475e1ce0...`, its point list E218's): wall cycles and seconds, 1 at the full chip |
| REPORTED beside | 'v3.1 + both terms' (E216's form: MM1-v3.1 with both frozen terms); 'v3.1 with T7' (`../v3.1/out/fits/time_T5r+G0+T7.json`, E215's form); MM1-v3 refitted (section 5's baseline at its all-data constants); and, if a layout term entered, MM1-v3.2 without it |

### 9.7 Its rules (registered by E218's registration, in E215's and E216's forms; stated here so the day tests v3.2's changes)

Bands twice the larger of MM1-v3.2's no-twin LOEO error over every point and over aifoundry3 card 0's points, per quantity, rounded up to a
whole percent (T1-T3, E1-E4; watts for points under 3 W; 90% of cases to pass); head-to-head by the exact two-sided sign test with the card's
ties: **MM1-v3.2 against MM1-v3.1** on every registered point (H1-H5); **against 'v3.1 + gemmLnc term'** on family G (W over idle given t,
J over idle with t forecast); **against 'v3.1 + contention'** on family Y (wall); **E216's pair rule P1** on the eight Y pairs for MM1-v3.2's
layout term (if none entered: P1 for each candidate REPORTED); the Gt twins and F scored by the same bands; MM1-v3 and MM1-v2 beside;
the power of each test stated before the data.

## 10. The order of decisions (registered)

1. At the fit's start: every input's sha256 (sections 1, 4), E215's blob ids, E215's scores committed (the gate), the feature agreement check
   (3.1), the census-path record as v3.1 left it.
2. Time: T5r+G0+n32 on every fold (section 2, the eta pin): MM1-v3.2's base and MM1-v3 refitted's time.
3. The layout term: the bundle written from step 2's fits; `layout_rule_v32.py decide` -> the term or none (section 3).
4. Energy: E1t + F3 on every fold (F3's pins), E1u (MM1-v3 refitted) on every fold, each on its time fold.
5. The acceptance rules (section 7).
6. Freeze MM1-v3.2 (its land); then E218's points and forecasts by section 9 at E218's registration.

| decided later | by | when |
|---|---|---|
| the layout term (or none) | section 3's rule on MM1-v3.2's fits | at the fit |
| F3's pins per fold | section 1.3 | at the fit |
| E218's points | section 9's rule on the landed MM1-v3.2 and a fresh never-run scan | at E218's registration |
| a gemmLnc time term (MM1-v3.1 overprices gemmLnc's cycles at NB 5-6 by 9.6-16.4% in sample) | a later declaration | not in v3.2 |
| a card factor for F3 (card 1 reads 6-10% above it) | a later declaration | not in v3.2 |

## 11. Not built in MM1-v3.2, and NOT RUN here

**Not built** (registered): T7 refitted (it stays out by v3.1's rule; REPORTED only where frozen); T6A, T8, a_row; lambda fitted (0.0048 a C);
a kappa of their own for the scalar instruction classes; tensor-queue blocking and the second hart; a gemmLnc time term; F3's card factor.
**NOT RUN by this lane:** any fit, card, simulator or commit; any score of a declared rule; the layout rule's eligibility, bootstrap, placebo
or choice on real data. **Desk, run here before any E215 result was opened:** the hashes of section 4 (E215 by git object ids only); the
layout rule's selftest and its desk check on MM1-v3.1's committed records (section 3.5).

## 12. Files

- `DECLARED-v32.md`: this file. `declared-v32.json`: the same declaration for a script (items, forms, bounds, pins, rules, folds, data with
  their hashes, acceptance, E218's point rule and forecasts, the decision order).
- `layout_rule_v32.py`: section 3's rule as code (`decide <bundle.npz> <out.json>`; `selftest <out.json>`).
- `layout_rule_v32_deskcheck.py`: its desk check on MM1-v3.1's committed records (metrics only); outputs `out/deskcheck-layout-rule.json`,
  `out/selftest-layout-rule.json`.
- `DECLARED-v32.sha256`: the sha256 of the files above (frozen together).
