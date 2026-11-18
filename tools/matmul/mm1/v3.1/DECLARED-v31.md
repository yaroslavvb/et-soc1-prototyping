# MM1-v3.1: every form, input, bound, start, fold, rule and reported figure, declared before any E213 datum

*Written Wed 18 Nov 2026 (week 47) from about 04:40 PST (Pacific), round Q217, lane v31-declare, at aifoundry2's desk. No fit, no card, no
simulator. **No E213 datum existed or was opened:** E213's two arms hold their bookings until 07:30 PST at the earliest, and its points were
read from its registration only (`tools/claims-v3/e213/points-e213.csv`, sha256 `8bab9165...`). This file and `declared-v31.json` (the
machine-readable half: every form, bound, start and rule, the seeded start values as numbers, and the two desk tables of sections 6 and 8)
are posted by their sha256 on the owner's coordination thread before E213's data: that post is their freeze line, and it and the land
commit's message give the time they were final. Neither file holds its own hash.*

*Corrected the same morning, from about 05:39 PST, by lane fix-v31decl (round Q217), answering this declaration's verification (three
medium findings, six low and one nit), before any E213 datum; section 14 lists every change, each resting on its finding and on MM1-v3's own
files alone. T7 is now code (`t7_v31.py`, sha256 `893ae962174678fcd1560dfc423722361e706319a188687f8f572a4e3ca89242`) and rule 4(a)'s
comparator a script (`comparator_4a_v31.py`, sha256 `17b336e10b9f4b0a521c0cb83630575f9f54b5d1d993436677aedefdcf38f960`), both beside this
file and frozen with it. The corrected pair is posted again by its sha256 before E213's data; that post is its freeze line.*

The owner's words that started the matmul model (Mon 16 Nov 2026, at or before 09:48:24 PST; a voice transcription in which "matte mold" is
the matmul): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of
transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See check how
well the timing simulation for the matte mold matches reality and the energy."

**Labels.** *Registered*: a form, bound, start, threshold or rule declared here, before any E213 datum. *Desk*: arithmetic or a computation
from committed files at a desk. *Post hoc*: fitted or read after its data existed (every constant of MM1-v3 is). *Held out*: left out of the
fit that scores it (not blind). *Blind*: scored on data that did not exist when the forecast was frozen. *REPORTED*: printed beside a rule,
never deciding it. *NOT RUN*: a check that did not run. Error = forecast / measured - 1; rms and bias in %. Interpreter for every number
here and for v3.1's fit: `/usr/bin/python3` 3.12.3, numpy 1.26.4, scipy 1.11.4, `-I -B`, single-threaded.

**What this file fixes, and why now.** MM1-v3 (`tools/matmul/mm1/v3/`, landed `b1493082`) left named items for v3.1 in its README section 8
and in the open issues of its spec, fit, verification and fix lanes. E213, MM1-v3's blind matmul day (registration with amendment A1
`291c8201`, kit `6efdb002`), runs from about 07:30 PST today. **E213's data enter v3.1 only as training data, and only after E213's blind scores
are committed** (the `scores-e213` lane's commit). Every choice v3.1 makes from them is made by a rule written here, so that nothing of v3.1 is
chosen after E213's data are seen. v3.1 is MM1-v3 as landed (time form v3+T5r, 19 constants; energy form v3, 26 constants, lambda pinned 0.0048;
every input as vendored there) with only the changes items 1-8 declare.

## 0. On one screen

| item | MM1-v3 (post hoc) | MM1-v3.1 declares (registered) | decided by |
|---|---|---|---|
| 1 energy split | b2 -88.9, d2 -291.7 pJ a line, unbounded; xi 0.000 at its bound | E1b: b2, d2 >= 0 (primary); E1t: b2 = d2 = 0; E1m: b2, d2 = 0.3734 x b3, d3; E1u (v3) the reference | LOEO W given t, no twins; 0.10 / 0.30 points |
| 2 a card left out | the training cards' mean kc pinned to 1 (A2, post hoc) | the anchor route: each card's kc from its committed gemmL1x1x4 int8 random points alone; A2 the fallback | both routes scored; rule 2 reads the anchor route |
| 3 gamma, T_coop | pinned 0 | G0, Gplace (primary, 5 constants), Goperand (5), Gcoop (3) | LOEO on the points of the other loops; 0.25 points; a 0.05-point guard |
| 4 subset layout | none (T7L lost) | T7, the masked walk (0 constants, frozen as code: `t7_v31.py`), only after its trace check passes; else T7L against n/32 | the trace check, then LOLO and LOEO |
| 5 fits | 6 starts a fold, 1e-8 | 18 starts a fit (6 declared + 12 seeded), the best three continued at 1e-12; 9 energy starts | lowest training cost, reported per fold |
| 6 census | gemmLnc -45.66 pJ | -39.64 pJ (the census's own rule) | desk |
| 7 switch counts | committed counts only | v31-counts' verified counts as inputs; b0, m fitted as v3; no count, no energy forecast | v31-counts' verified tables |
| 8 one K block | T5r won by 0.14 points | T5r or tC by a sign test on E213 family C and arm B's BK, both frozen before any E213 datum | E213's measured cycles; else LOEO |
| 9 data, folds | 1,737 time points, 17 experiments | + E212 a2c0-S4 and E213; folds through E213; no-twin headlines; v3's four rules against v3 refitted on v3.1's inputs; rule 4(a) on the same E212 records (`comparator_4a_v31.py`) | as v3, restated |
| 10 v3.1's blind day | - | five families, a never-run scan, half by model gap and half by a seeded draw | at that registration |

## 1. The energy split: the L2 line energy against the per-op base

**The problem** (MM1-v3 README section 8, post hoc): b2 and d2 come out negative. The L2 lines an op are nearly constant across the L2-served
shapes (the closed-form map gives L2 hits only at KB <= 2, and in run_gemm's c-arms), so the L2 term trades with the per-op ungated base, the
gate and the data term; xi sits at its lower bound 0.

**The forms** (registered; every other energy constant, bound and pin as MM1-v3's `DECLARED-v3.md` section 5; xi free in [0, 1], pinned 1 in a fold
with no governed card):

| form | b2 | d2 | free energy constants | reading |
|---|---|---|---|---|
| E1u (the reference: MM1-v3) | free | free | 26 | as fitted in v3 |
| **E1b (the bound, primary)** | in [0, +inf) | in [0, +inf) | 26 | no line costs negative energy; at the bound the L2 line is priced inside the per-op base |
| E1t (the tie to zero) | 0 | 0 | 24 | the L2 line inside the per-op base by construction |
| E1m (the tie to the energy manual) | 0.3734 x b3 | 0.3734 x d3 | 24 | an L2 line costs the energy manual's L2 / L3 ratio of an L3 line |

r_L2 = 0.3734 is desk: 4.051 / 10.849 pJ a byte over idle, the energy manual's committed L2 and L3 read prices (`docs/reports/data/2026-09-23-energy-manual/manual.json`,
`memory_reads.rows`, measured 18 Sep 2026 on aifoundry2), made before any matmul fit.

**The rule** (registered): fit the four forms on all the data and on every LOEO fold (and E210's), on the final time form's lines and op times,
from item 5's energy starts. Score each by LOEO W over idle given the measured op time: the rms of forecast / measured - 1 over the points all four price at 3 W
or more, configuration twins excluded. Among E1b, E1t and E1m, the candidates are the forms whose score lies within 0.10 points of the
lowest of the three; of the candidates, the form with the fewest free constants wins (E1t and E1m 24, E1b 26), and at equal constants E1t
before E1m. **That winner enters v3.1 unless E1u's score is lower by more than 0.30 points**;
then E1u enters and the README reports the split as not identified, as in v3, with the winner's figures beside.
**Not wanted:** if E1b's all-data fit puts b2 and d2 at 0, E1b equals E1t and E1t wins by the constant count.
**REPORTED:** the four forms' LOEO and LOCO (both routes of item 2), with and without twins; b2, d2 and xi per fold with their bound activity;
the joules by class at E213's points.

## 2. The energy scale of a card left out: the anchor route, with A2's pin as the fallback

**The problem** (post hoc): kc is each card's factor on the per-op energy relative to aifoundry3 card 0 (kc = 1). With aifoundry3 held out, the
training cards' kc and the per-op constants they multiply (Eub, a_op, a_lane, a8, b0) trade exactly, and the held-out card's forecast moves
along that line (pooled LOCO W given t 6.8% to 43.5% at one training cost); `AMENDMENT-A2.md` pins the training cards' mean kc to 1.

**The anchor** (registered; chosen before any E213 datum and without scoring the route): **rgm136 gemmL1x1x4, int8, random data, full chip**, at the
card's own clock (600 MHz on the pinned cards; the measured governed clock on aifoundry2 card 0 and aifoundry1 card 0). Of the three rgm136
int8 random configurations at KB >= 3 whose energy is committed on all four cards (gemmL1x1x4, 1x1x8, 1x1x16), it has the smallest footprint
(14 MB, against 26 and 50; desk): at KB >= 3 its L2 line count is 0, so item 1 cannot move it; far inside the L3's first edge (about 37 MB),
its lines are L3-served at any fitted retention; with random data the kc-multiplied per-op term carries most of its W. Each card's anchor
points (scored runs only; the sessions' smoke processes of that arm are not points):

| card | anchor points (committed folders under `docs/reports/data/`) | points |
|---|---|---|
| aifoundry3 card 0 | E206 arm A p035 (`2026-11-16-e206-matmul-sweep-aifoundry3`, data commit `d7e4f35e`) | 1 |
| aifoundry1 card 1 | E206 arm B p035 (`2026-11-17-e206-matmul-sweep-aifoundry1-c1`, `79340bfa`); E208 a1c1-S1 run 035 and a1c1-S2 run 053 (`2026-11-16-e208-mmsweep-a1c1-S1`, `-S2`); E212 a1c1-S1's runs (`2026-11-17-e212-mmsweep2-a1c1-S1`) | 3 |
| aifoundry2 card 0 | E208 a2c0-S1 run 032, a2c0-S2 run 055 and the repeat a2c0-S1r run 032 (`2026-11-16-e208-mmsweep-a2c0-S1`, `-S2`, `2026-11-17-e208-mmsweep-a2c0-S1r`); E212 a2c0-S1's runs (`2026-11-17-e212-mmsweep2-a2c0-S1`) | 2 |
| aifoundry1 card 0 | E208 a1c0-S1 run 019 (`2026-11-16-e208-mmsweep-a1c0-S1`); E212 a1c0-S1's runs (`2026-11-17-e212-mmsweep2-a1c0-S1`) | 2 |

A point is what v3.1's data loader makes (MM1-v3's `data_v3` extended): one energy point a (experiment, card, configuration), the mean of its
runs; MM1-v3's own table names them E206|p035, E206B|p035, E208|c1|..., E212|c1|..., E208|a2|..., E212|a2|..., E208|c0|..., E212|c0|...
A scored run of the configuration committed at GitHub main before the fit starts joins its card's anchor set.

**kc from the anchor alone** (registered). At each anchor point i of the held-out card, at its measured op time, volts and die,
W_i = D_i (R0_i + kc K1_i): D_i the die factor, K1_i the kc-multiplied per-op term at kc = 1, R0_i every other term with the held-out card's awake
power Pa set to the training cards' mean (MM1-v3's rule). Then kc = sum w_i^2 D_i K1_i (W_i - D_i R0_i) / sum w_i^2 D_i^2 K1_i^2 with
w_i = 1 / max(W_i, 3 W): the energy fit's own weighted least squares, in closed form. In the fold without aifoundry3 the forecast R0 + kc K1 is
the same at every point of the flat line (kc scales as 1 / K1), so the forecast needs no pin there; the solved kc does move along the line, so
**A2's rescale comes first**: that fold's fitted point is rescaled exactly as `AMENDMENT-A2.md` does (the training cards' mean kc set to 1:
every kc / s and the per-op constants Eub, a_op, a_lane, a8 and b0 x s, s the training cards' mean kc as fitted), and only then is the held-out
card's kc solved and the validity test below applied, at that scale. **Valid** when kc lies in [0.5, 2] and the
kc-multiplied term's share of the predicted W at the solved kc, kc K1_i / (R0_i + kc K1_i), averages at least 25% over the anchor points;
otherwise that fold takes the fallback and is flagged.

**The fallback** (registered): MM1-v3's declared rule (the held-out card takes the training cards' mean Pa and kc = 1), with A2's pin in the fold
without aifoundry3.

**The rule** (registered): the anchor route is v3.1's held-out-card route; the fallback applies where the held-out card has no anchor point or
the validity test fails. Every LOCO energy figure is computed and printed under **both** routes, for v3.1 and for v3 refitted. The held-out
card's anchor points leave that fold's scored set under both routes (both are scored on the same points; with them, REPORTED beside).
Acceptance rule 2 (section 9) reads the anchor route for both models, the fallback beside. **Not wanted** (REPORTED, the route stays): the
anchor route's pooled LOCO above the fallback's. **REPORTED** per LOCO fold: kc from the anchor and under the fallback, the anchor points'
residuals, both routes' rms and bias.

## 3. gamma (the path's exposure) and T_coop (the cooperation cost)

**MM1-v3** (post hoc): D_A, D_B = the census's path from the tensor wait's return to each operand's request, less rgm136 gemmL's (cycles / f),
no fitted constant; gamma and T_coop pinned 0. E211's controls showed both post hoc (design b, Q214: the path's saving read 0.62 times the census
where B was fresh and 1.64 times where A was fresh; gemmLnc ran about 6 cycles an op faster than its census path inside the L3 and about 121
faster past it), never fitted.

**Definitions** (registered). dT_path,X = the census's `D_X_cycles_vs_rgm136` (desk, census: rgm136 gemmL 0 / 0; gemmLnc -12.5 / -22.0; rgm211
gemmL -10.5 / -13.75; rgm211 gemmLn -37.0 / -49.75 for A / B). p = operand X's place in each op class of the map (L2, L3 or F, fresh); D enters per
op class. dcoop_X = coop_X(loop) - coop_X(rgm136 gemmL), coop_X = 1 when the loop loads X in tensor_coop groups (8 minions for A, 4 for B), else 0:
-1 for gemmLnc, 0 for the other three loops. gamma is dimensionless; T_coop is in minion-clock cycles, added to D and divided by f.

| form | D_X in op class with X at place p | constants (bounds) |
|---|---|---|
| G0 (the null: v3) | dT_path,X | none |
| **Gplace (primary)** | dT_path,X (1 + gamma_p) + dcoop_X T_coop,p, with gamma_L2 = 0 | gamma_3, gamma_F in [-1, 3]; T_coop,2, T_coop,3, T_coop,F in [-300, 600] cycles (5) |
| Goperand | dT_path,X (1 + gamma_X [p != L2]) + dcoop_X T_coop,p | gamma_A, gamma_B in [-1, 3]; the same three T_coop (5) |
| Gcoop | dT_path,X + dcoop_X T_coop,p | the three T_coop (3) |

gamma = -1 hides the path wholly; gamma = 3 exposes it four times. **The pin sets** (registered; a constant whose set is empty in a fold is
pinned at 0 there and printed with the fold): gamma_3 (and the L3 part of gamma_A, gamma_B): training points of a loop with dT_path != 0 (rgm211
gemmLn, rgm211 gemmL, gemmLnc) at footprint <= 48 MB; gamma_F (the fresh part): the same at footprint > 32 MB; T_coop,2: training gemmLnc points
with KB <= 2; T_coop,3: training gemmLnc points at footprint <= 48 MB; T_coop,F: training gemmLnc points at footprint > 32 MB. gamma_A and gamma_B
are pinned only when both parts are empty.

**How E213's family P identifies them** (as training data, once scores-e213 is committed). At each of four one-stream shapes (MB = 1 or NB = 1,
so every loop sees one map: 3x1x3 at 27 MB inside the L3, 1x6x5 at 52 MB and 4x1x6 at 62 MB at the knee, 1x1x44 at 134 MB past the L3) E213
runs four codes: rgm136 gemmL (path to B 77.75 cycles; desk, census), rgm211's own gemmL (64.0, never run on a card before), rgm211 gemmLn (28.0)
and gemmLnc (55.75, no cooperation). So ln(T_loop / T_rgm136 gemmL) at one shape is the code-side term alone: rgm211's two loops give the
exposure by regime (gamma), and gemmLnc against rgm211's gemmL (paths about 8 cycles apart, cooperation off and on) gives T_coop by regime; a087
against a088 (gemmLnc and gemmL at 1x1x1 int8) reads the L2 place; arm B's gemmLnc points k37-k40 against their gemmL twins read the same on
card 1. E211's rgm211 points, controls and gemmLnc pair (c01, c02) are already in the data.

**The rule** (registered): fit G0, Gplace, Goperand and Gcoop on all the data and on every LOEO fold of the time data (section 9) from item 5's
starts. Score each by
the LOEO wall-cycle rms over the touched points (every point whose loop is rgm211 gemmLn, rgm211 gemmL or gemmLnc), twins excluded. The lowest
score wins; within 0.25 points the form with fewer constants (G0 0, Gcoop 3, Gplace and Goperand 5); at equal constants Gplace before Goperand.
**Guard:** the winner's pooled LOEO wall rms over all points may not exceed G0's by more than 0.05 points, else G0. **Not wanted:** G0 wins,
or every constant of the winner sits within 1% of 0 in the all-data fit (then reported as not identified). **REPORTED:** each form's constants
per fold; E211's and E213's per-shape ratios ln(T_loop / T_rgm136) measured beside each form's.

## 4. The subset layout: T7's masked walk, its trace check against simulator traces, and T7L

**MM1-v3** (post hoc): no layout model. At an equal shire count E212's layouts move the time by up to 15%; spread masks held out read 6.74%
against MM1-v2's form's 5.40%. T7L lost v3's rule (4.64% against the primary form's 4.67%: within 0.05 points at equal constants, the
primary kept). E213's family M (fp32 zeros at 2x8x8 and 1x3x12 on eleven masks with each shape's full chip; shapes never run) tests the gap.

**T7, the masked walk** (registered; no fitted constant). Inputs: the mask (shire s in row group s >> 2 of 8 and column group s & 3 of 4), the
shape (MB, NB, KB) and the kernel's C-block walk (mn for rgm136's gemmL and gemmLnc and rgm211's gemmL; nm for rgm211's gemmLn at MB, NB >= 2).
What it computes:
1. The chip's lock-step request stream with only the mask's shires. At every step (each C block in the walk's order, row half r, kb, k < 32)
   each active shire of row group g and column group c asks the A tiles 2 (4 g + d) + r (d < 4) and the B tiles 8 c + p (p < 8) of that step, as
   E211's desk map (`map_e211.shire_ops`) numbers them. The step's distinct A and B tiles are the union over the active shires (an A tile shared
   by its row group's active shires, a B tile by its column group's). The C TensorStores are the active shires' C tiles of each half block.
2. Exact LRU stack distances of every request over that stream (E211's Fenwick method, steady second pass).
3. The fold's retention gives each step's place shares by engine_v3's procedure for rgm211 gemmLn (`engine_v3.WalkShape.Qhalves`): per step,
   each operand's mean retention over the step's requests (r_A one edge, r_B two edges, at the fold's theta; each tile weighted by the number
   of active shires that ask it, which is the plain mean at every product mask), B's mean x zeta in row half 1 where NB is a power of
   two, at least 4, and the full-chip footprint passes 32 MB (v3's rule); pA = [hA, (1 - hA) mA, (1 - hA)(1 - mA)] and pB alike, with hA and hB the L2
   model's hit shares of that row half (`map_e211.l2_model`: each shire's own line stream, which the mask does not change), multiplied by r2
   under T5r exactly where engine_v3 applies r2 at that arm's full-chip map (walk mn, KB <= 2, MB x NB >= 2; never on the nm walk). Q0 and
   Q1 = the mean over the half's steps of outer(pA, pB).
4. n_eff,3 and n_eff,F = the masked stream's L3-served and fresh distinct lines a step (16 x (1 - h) x the sum over the step's distinct
   tiles of r(d), and of 1 - r(d); zeta and r2 as in step 3), averaged over the steps, over **the same code's average at mask 0xffffffff**
   (same shape, walk and theta), each min(1, ratio), and 1 where the full-chip average is 0. X3 = 1 - chi3 (1 - n_eff,3) and XF = 1 - chiF
   (1 - n_eff,F) replace v3's n/32 (each clipped at 0.05 as in v3). MM1-v3's row-imbalance term, T_C (at the full-chip footprint) and the
   rest of the op time are unchanged; item 3's forms change only D_A and D_B per op class and compose with T7 unchanged.

**T7 is frozen as code** (registered): `t7_v31.py` (sha256 `893ae962174678fcd1560dfc423722361e706319a188687f8f572a4e3ca89242`, final at
06:11:05 PST, beside this file) is T7's only implementation, written from MM1-v3's own files (engine_v3.py, mm1_core_v3.py and the vendored
map_e211.py, each pinned by its sha256 inside it) and evaluated on no measured value. v3.1's fit imports it unchanged: `T7Bank(points).arrays(theta,
form)` gives Q0, Q1, n_eff,3 and n_eff,F at each T7 point for a fold's theta, in place of v3's Q0, Q1 and n/32 in X3 and XF; `op_time` is
TimeEngine.predict with exactly those replacements (item 3's G0).

T7 applies to subset points of the gemmL family only: every full-chip point, and run_gemm's c-arms, keep MM1-v3's map and n/32 exactly.
**Desk precondition:** at mask 0xffffffff the walk's request stream equals `map_e211.chip_steps` for both walks, request for request; **a failed
precondition makes the trace check NOT RUN** (T7 stays out). v3.1's fit lane re-runs `t7_v31.py --check` at its start with every subset shape
of its data (`--extra-shapes`); a failure there is a failed precondition. Desk, run here before any E213 datum (`t7_v31.py --check`, 06:10:04 to
06:11:05 PST, /usr/bin/python3 3.12.3, numpy 1.26.4, one thread): the precondition held at 36 shapes x 2 walks (every subset shape of MM1-v3's
data, of E212 a2c0-S4 and of E213's registration, and E211's 13); the masked distances at 0xffffffff equal map_e211's at 5 shapes x 2 walks;
on the nm walk at 0xffffffff the code reproduces engine_v3.WalkShape.Qhalves exactly (4 shapes, difference 0); its op time with nothing
replaced equals TimeEngine.predict at E213's 131 registered points under both landed time forms (relative difference 0); n_eff of a full-chip
walk over itself is 1. REPORTED: the masked distances equal lane v31-trace's independent walk (walk_v31.py, sha256 `87736da2...`) at 8
cases (E212's trace pair 0xf / 0x1111 at 2x4x16 on both walks, and four E213 family M shape-mask cases on both walks).

**The trace check** (registered). Data: lane v31-trace's sys_emu traces on aifoundry3 at two masks of one E212 layout pair (equal shire count,
different layout) at a shape E212 ran, for each kernel it can trace, with verify-v31trace's verdict. Pass rule:
- (a) **over the logged harts, with a minimum log set.** The walk enables hart 0 of all 32 minions of every shire in the mask (hart 1 enters
  and returns; no other shire is launched). At each mask the traces log at least (i) every hart (all 64) of every shire the mask enables and
  (ii) every hart (all 64) of at least one shire it does not enable; one run per mask that logs every hart of the chip also meets this. (a)
  holds when, at both masks, every logged hart 0 of an enabled shire issues tensor loads, no logged hart 1 issues one, and no logged hart of a
  shire outside the mask retires a U-mode instruction. A log set below the minimum leaves (a) undecided;
- (b) for every traced minion (a minion whose hart 0 is logged), the ordered sequence of its tensor-load requests (operand, tile index relative
  to the operand's base) over the traced window equals the walk's sequence for that minion: zero mismatches;
- (c) for every traced minion, the request counts by operand equal the walk's.

**PASS** = (a), (b) and (c) at both masks, and verify-v31trace HOLDS (or HOLDS WITH FIXES, with its fixes applied and the check re-run).
**FAIL** = any mismatch. **NOT RUN** = the traces cannot show (a) to (c) (v31-trace NOT TRACED, TRACED WITH GAPS that leave one undecided, or a
log set below (a)'s minimum), or T7's desk precondition failed.

**T7L, as v3 declared it:** n/32 replaced by n_eff = (64 R/8 + 128 C/4) / 192 (R of 8 row groups and C of 4 column groups active; an A tile
shared by a row group's shires, a B tile by a column group's) in X3 and XF, the map at the full chip's lines, no new constant.

**Layout classes for LOLO** (registered; decidable for any subset mask; a full-chip point, mask 0xffffffff, is in no class): n = 1 is other; compact if n = 4 R (every active row group whole); else spread
if R = min(8, n) (the shires in as many row groups as they can be); else other. v3's compact set (0xf, 0xff, 0xffff, 0xffffff) and spread set
(0x1111, 0x11111111, 0x33333333, 0x77777777) fall in the same classes; 8 of MM1-v3's 37 'other' subset points (masks 0xf000, 0xfff, 0xf0f0f0f,
0xf0f0f0f0, 0xffff0000) are compact here (desk: compact 104, spread 37, other 29 of v3's 170 subset points). v3.1 and v3 refitted are scored on
the same classes; v3's own LOLO sets are REPORTED beside. E213's family M: compact 0xf0000, 0xf0f, 0xfff, 0xf0f0f0f; spread 0x11, 0x1010101,
0x22222222, 0x55555555; other 0x3, 0x3030303, 0x7070707.

**The rule** (registered):
1. If the trace check is PASS: fit T7, T7L and v3's n/32 form on all the data and on every LOEO and LOLO fold. **T7 enters v3.1** if its LOLO wall rms over all
   subset points is lower than both others' **and** its pooled LOEO wall rms is not more than 0.05 points above the best of the three.
2. Otherwise (FAIL, NOT RUN, or T7 losing step 1): T7 stays out; T7L against n/32 by v3's declared time rule (the lower pooled LOEO wall rms over
   all points; within 0.05 points the fewer constants; equal constants, n/32).

**REPORTED:** family M's measured spread among masks of one shire count beside each form; LOLO by class for all three forms.

## 5. The fits: starts, seeds, basins, tolerances

**MM1-v3** (post hoc): six declared starts a fold; one start reached the lower basin, the global one, in 27 of 30 folds; the 1e-8 tolerance
stopped three folds short.

**Time** (registered):
- **18 starts a fit**, the same for every fold and form (a form takes the constants it has; a pinned constant takes its pinned value):
  S0-S5 are MM1-v3's six declared starts (`fit_v3.STARTS`) for its constants, with six declared values for the new ones (gamma_3 or gamma_A:
  0, -0.3, 0.3, -0.6, 0.6, 0; gamma_F or gamma_B: 0, 0.3, -0.3, 0.8, 1.2, 0.5; T_coop,2: 0, 10, 30, 0, 60, 20; T_coop,3: 0, 10, 30, 20, 60, 5;
  T_coop,F: 0, 50, 150, 100, 250, 120 cycles). S6-S17 are twelve draws of `numpy.random.default_rng(20261118).uniform` over each constant's
  start box, recorded in `declared-v31.json` as numbers (the fit uses the recorded numbers; re-drawing is a check). The draw order is
  start-major: S6's value for each of the 27 names of the box table in `sorted()` order (every name, whatever a form uses), then S7's, and so
  on to S17, each value rounded to 6 decimals.
- **Bounds:** MM1-v3's for every shared constant (c3, cF in [-3000, 3000] cycles; m3, mF in [-5, 10] us; kA [0, 3]; F2 [0, 1000] cycles; T2 [0, 2] us;
  x1 [20, 120] MB; w1 [0.3, 40]; pB [0, 0.95]; x2 [30, 400]; w2 [0.3, 80]; zeta [0, 1]; piF0 [-0.5, 3]; chi3, chiF [-2, 0.95]; eta [0, 2];
  d8 [0, 0.2]; tC [0, 400] cycles a line; r2 [0, 1]); item 3's for gamma and T_coop. The start boxes are in `declared-v31.json`.
- **Phase 1:** scipy `least_squares` on forecast / measured - 1 of the wall op time, every training point weight 1, `x_scale='jac'`, `diff_step`
  1e-4, ftol = xtol = gtol = 1e-8, at most 4,000 evaluations, from each of the 18 starts.
- **Phase 2:** the three lowest phase-1 costs continued from their end points at ftol = xtol = gtol = 1e-12, at most 4,000 evaluations a leg,
  restarted from the last point while the cost falls by more than 1e-9 relative, at most five legs.
- **Between basins: the lowest phase-2 training cost wins** (ties within 1e-9 relative to the lower start index). Two continued solutions share a
  basin when their costs agree within 1e-6 relative. Reported per fold: every start's phase-1 cost, status and evaluations; the three continued
  costs and held-out rms; the winner's start; how many of the 18 phase-1 costs lie within 1e-3 relative of the winner's. A fold whose winner one
  start alone reached is flagged (no change of rule).
- **The pin rule:** MM1-v3's identifying sets (`DECLARED-v3.md` section 2) plus item 3's; every pin printed with its fold.

**Energy** (registered): nine starts a fit: MM1-v3's three (the linear solve at kc 1, xi 1, m 1, eC 1; then kc / xi / m at 1.05 / 0.5 / 1.2 and
0.95 / 0.9 / 2.0) and six draws of `numpy.random.default_rng(20261119).uniform` over the nonlinear constants' boxes (recorded as numbers;
start-major over the seven names in `sorted()` order, each rounded to 6 decimals); each
start's linear constants from the linear solve at its nonlinear values, clipped into bounds (E1b's b2, d2 to >= 0); `least_squares` on
(W - W_meas) / max(W_meas, 3 W), ftol = xtol = gtol = 1e-12, at most 3,000 evaluations; the lowest cost wins. Each energy fold reads its own time
fold's phase-2 winner (lines, op times, retention): MM1-v3's README listed "the converged time folds carried into the energy folds" as NOT RUN.

**Cost** (desk, from MM1-v3's record of about 8 s a start-fit on one core): about 2.5 minutes a fit with phase 2, about 50 minutes for one form's
LOEO, about 90 minutes for every fold of one form; every fit inside the round's CPU slots, single-threaded.

## 6. The census's gemmLnc instruction energy

MM1-v3's census gives gemmLnc -45.66 pJ a minion-op relative to rgm136's gemmL: its two removed tensor_coop issue slots are not credited
(verify-mm1v3's nit, fix-mm1v3's item). **The correction** (desk): the census's own stated rule applied to every class, dE = sum over classes
dn_c (e_c - cpi p_awake), with the tensor CSRs priced e_c = 0, so a removed CSR issue slot returns its awake share cpi p_awake = 3.0087 pJ
(p_awake = 1.379 W / 1,024 / 600 MHz = 2.2445 pJ a minion-cycle, cpi = 1 / (2 x 0.373) = 1.3405).

| loop | dn (classes against rgm136 gemmL) | census-v3 (pJ) | v3.1 (pJ, desk) |
|---|---|---|---|
| rgm136 gemmLnc | tensor_coop -2, ld_stack -4, sd_stack -1 | -45.6567 | **-39.6393** |
| rgm211 gemmL | alu +1, ld_stack -4, sd_stack -3 | -62.4480 | -62.4480 (unchanged) |
| rgm211 gemmLn | alu +1, ld_stack -12, sd_stack -4 | -142.0700 | -142.0700 (unchanged) |

**The rule** (registered): v3.1 reads `census-v3.1.json` = `census-v3.json` (sha256 `cad5250c...`) with gemmLnc's
`dE_instr_pJ_per_minion_op_vs_rgm136` set to -39.6393 and a note; the time paths and every other loop unchanged; its sha256 recorded by the fit
lane. The size (desk): about +6.0 pJ a minion-op, about 4 mW at 1,024 minions and a 1.5 us op.

## 7. The new switch counts (lane v31-counts)

- **Inputs only** (registered): each new count enters as S(fmt, kind, KB) (signal fin edges an op, lo, zero delay) with its valid share v,
  exactly as MM1-v3's committed counts do (`energy_v3.counts`), never fitted or adjusted. **phi, in this order of precedence:** MM1-v3's
  `energy_v3.phi_of` where it gives a value (zeros 0, random 1, ones, sparse50 and E210's kinds, unchanged); else the mean of `kinds_v3.phi`
  over the kind's committed tile files (the tiles its runs delivered); else `kinds_v3.phi`'s generator law, only for a law it defines (randn,
  sparse50, sparse25, e37); else no phi, and the kind is NOT FORECAST in energy.
- **Which counts:** v31-counts' committed tables (under `tools/matmul/mm1/v3.1/counts/`), and only if its re-count of two committed points
  matched and verify-v31counts HOLDS (or its fixes are applied). Their sha256 are recorded, from the committed `counts/` folder at GitHub main,
  in v3.1's README inputs table and in its fit record at the fit's start, before any v3.1 residual on those kinds is read.
- **Footings** (as MM1-v3 README section 7): fp32 counted at GEMM accumulator states (gate level); fp16 estimated (RTL toggles times the fp32
  gate/RTL ratio); int8 counted around the arithmetic only, so m_int8 carries the rest (a reading, not a count).
- **The energy-calibrated constant:** b0 (J a fin edge), with m_fp16 and m_int8, fitted jointly with the other energy constants on every energy
  point whose kind has a committed count, one b0 for every card and kind, as v3; kappa = 1 / (m b0) is reported.
- **No count, no energy forecast:** a kind with no committed count stays NOT FORECAST in energy (its time is forecast), never a nearest-kind guess.
- E212's switch-pattern arms and its plan and real tiles enter v3.1's energy fit once counted; E213's zeros, ones and sparse50 points enter as
  counted kinds.

## 8. One K block: T5r against tC, decided by E213's family C

**MM1-v3** (post hoc): T5r (the shire cache delivers a share r2 = 0.641 of the desk L2 model's hits at KB <= 2 with MB x NB >= 2) beat tC (the C
store, t_C 15.6 cycles a line in the primary fit) by 0.14 points of LOEO (4.53% against 4.67%), but E146's store rungs, never trained, read
T5r 5.29% against tC 3.57%: the two forms read different data well.

**Both forms frozen before any E213 datum.** T5r's forecasts are MM1-v3's frozen ones (`out/mm1_v3_e213.csv`, arm B in
`tools/claims-v3/e213/forecast-e213b-v3.csv`). tC's are made here (desk) from MM1-v3's primary form with its frozen all-data constants
(`out/fits/time_v3.json`, `theta_all`, landed `b1493082`), by `engine_v3.TimeEngine` at E213's registered points at 600 MHz; the same harness
reproduced MM1-v3's frozen T5r forecasts at all 131 points to 9.9e-07 (relative) before the tC column was written. The rule's 20 cases (wall
cycles an op; desk):

| case | arm, shape, format | T5r | tC | | case | arm, shape, format | T5r | tC |
|---|---|---|---|---|---|---|---|---|
| a037 | A 3x2x1 int8 | 888.5 | 856.8 | | a047 | A 14x12x1 int8 | 1020.6 | 962.2 |
| a038 | A 3x2x1 fp32 | 857.0 | 834.5 | | a048 | A 14x12x1 fp32 | 1007.8 | 973.6 |
| a039 | A 4x5x1 int8 | 972.4 | 926.0 | | k20 | B 2x3x1 int8 | 881.3 | 837.2 |
| a040 | A 4x5x1 fp32 | 954.8 | 928.1 | | k21 | B 2x3x1 fp32 | 853.0 | 823.3 |
| a041 | A 7x3x1 int8 | 1045.6 | 1010.9 | | k22 | B 4x4x1 int8 | 971.0 | 896.3 |
| a042 | A 7x3x1 fp32 | 1030.9 | 1012.8 | | k23 | B 4x4x1 fp32 | 951.5 | 892.5 |
| a043 | A 9x7x1 int8 | 945.9 | 895.1 | | k24 | B 7x3x1 int8 | 1045.6 | 1010.9 |
| a044 | A 9x7x1 fp32 | 927.4 | 897.8 | | k25 | B 7x3x1 fp32 | 1030.9 | 1012.8 |
| a045 | A 10x10x1 int8 | 939.0 | 884.6 | | k26 | B 4x3x2 int8 | 1077.1 | 1087.8 |
| a046 | A 10x10x1 fp32 | 920.5 | 888.7 | | k27 | B 4x3x2 fp32 | 1047.7 | 1053.6 |

ln(tC / T5r) runs from -0.080 to +0.010 at these cases (desk): the forms part by 2-8% at one K block and agree within 1% at k26, k27 (KB = 2).

**The rule** (registered), after scores-e213 is committed:
1. Per case (a case per arm: 12 in arm A's family C, 8 in arm B's BK), d = |ln(m / F_T5r)| - |ln(m / F_tC)|, with m the measured wall cycles an op
   as E213's frozen scorer reports it; a tie when |d| <= 0.005.
2. The exact two-sided sign test on the untied cases at alpha 0.05: **tC enters v3.1 if it is closer significantly, T5r if T5r is.**
3. NOT DECIDED, or fewer than 10 untied cases: both forms refitted on v3.1's data (E213 included) on every LOEO fold, with the other terms as
   steps 3 and 4 of section 11 chose them; the lower pooled LOEO wall rms over all points wins, within 0.05 points T5r (the incumbent; equal constants).

**r2's reading** (registered, if T5r stays): as MM1-v3's code applies it, to the closed-form map's L2 hits only, never to E211's exact walk map
for rgm211's gemmLn (the reading v3 was frozen under; README section 3); the literal reading is REPORTED beside. At a subset point mapped by
T7, r2 multiplies T7's L2 hit shares exactly where it would multiply the closed form's at that arm (section 4, step 3).
**REPORTED:** E146's store rungs (never trained) under both forms; family C's rms and bias by format under both frozen forms.

## 9. The data, the folds, the scores and the acceptance rules

**Data** (registered):
- **Time:** every point MM1-v3 read (1,737: E105-E190, E206 arms A and B, E207, E208's seven sessions, E209, E211, E212's eight sessions), plus E212
  a2c0-S4 (committed `724e8f39`, unread by v3) and **E213's arms A and B**, and any further committed session of E206-E213 at GitHub main when
  the fit starts; a new matmul experiment enters only by a dated amendment before the fit.
  One time point a (card, case), the mean of its runs. E146's store rungs stay in no training set, scored apart.
- **Energy:** MM1-v3's energy points (E210 included) plus those sessions' and E213's, and the switch-pattern kinds once counted (item 7). One
  energy point a (experiment, card, configuration, kind).
- **The gate:** E213 enters only after scores-e213's commit is on GitHub main; v3.1's fit starts after that commit (or after E213 is recorded as
  not run, when v3.1 is fitted without it, item 8 takes its step 3, and the README says so) and reads GitHub main at its start (named in its
  README). E212 a2c0-S3 (NOT RUN, cut by the box's crash) is included only if re-run and committed before the fit starts.

**Folds** (registered; every constant refitted from item 5's starts in every fold; the pin rule; the energy folds on their own time folds):
- **LOEO**, 18 folds: E105, E107, E119, E126, E136, E146, E158, E159, E168, E169, E190, E206 (A and B), E207, E208, E209, E211, E212, **E213** (A and
  B); sub-folds E212 by card (a1c1, a1c0, a2c0) and E213 by arm (A aifoundry3 card 0, B aifoundry1 card 1); E210 for energy.
- **LOCO**, 4 cards; energy under both routes of item 2.
- **LOKO:** rgm211 gemmLn, rgm211 gemmL (new: E213's four points), rgm136 gemmLnc, run_gemm; **leave rgm211 out:** every rgm211 point (gemmLn
  and gemmL) in one fold.
- **LOLO:** compact, spread, other (item 4's classes).

**Twins** (registered, MM1-v3's definition): a scored point is a twin when its card, kernel, arm, format, mask and clock (to 25 MHz) are in the
training set that priced it (energy adds the kind). **Headline figures exclude twins; the figures with them are printed beside.** E213's 127
points (role 'point' in `points-e213.csv`, 117 cases) are configurations never run on their card, so none of them is a twin. Its four
references (a088, a089 and a090 on arm A, k41 on arm B: rgm136 gemmL1x1x1 and gemmL4x8x8, int8 random) ran before on those cards: they are
twins wherever those runs are in training, and leave the headline figures like any twin.

**Scores:** wall cycles, the counter's mean, seconds, J over idle given t and with t forecast, J at rest both ways; per case (time) and per point
(energy), rms and bias; J over idle at 3 W and above, watts below. **The baseline, "v3 refitted":** MM1-v3's forms (time v3+T5r, energy v3,
which is E1u: b2 and d2 unbounded) refitted on exactly v3.1's inputs (census-v3.1.json of item 6, item 7's counts and phi rule, the same data,
folds, twins and pins) by item 5's procedure (the same starts, seeds and tolerances), its LOCO energy scored under both routes of item 2 as
v3.1's is.

**Acceptance** (MM1-v3's four rules restated; registered; on the same points and folds):
1. LOEO wall cycles (no twin) and LOEO W over idle given t (no twin, >= 3 W, the points both price): both lower than v3 refitted's.
2. LOCO wall cycles (every point) and LOCO W over idle given t (the anchor route for both models, the held-out card's anchor points excluded):
   not worse than v3 refitted's by more than 0.30 points in either; the fallback route's figures beside.
3. Leave rgm211 out: wall rms at or under 8.0% over its points, and at least 7 of E211's 10 W pairs inside 0.05 in ln (E213's rgm211 / rgm136 pairs
   REPORTED).
4. (a) The E212 fold under MM1-v2's unread error on **the same E212 case records**, computed by `comparator_4a_v31.py` (sha256
   `17b336e10b9f4b0a521c0cb83630575f9f54b5d1d993436677aedefdcf38f960`, beside this file, frozen before the fit). The records are the (card,
   case) means over the runs of E212's nine committed sessions (a case run in two sessions is one record: 27 such cases); MM1-v2 is called on
   each record as MM1-v3's `unread_v2_e212.py` calls it. Time per case (wall cycles) over every record v3.1's E212 fold scores; W over idle
   given t per record where both models price W at 3 W and above; a v3.1 record with another measured value (a session the script does not
   read) leaves the comparison and is listed; twins included, as MM1-v3's rule 4 was scored (without v3.1's twins REPORTED); PASS when v3.1's
   rms is lower in both. Desk, 05:58 PST: MM1-v2 unread on the nine-session records reads wall 6.645% (n 456) and W 7.597% (n 389); beside
   it, never deciding, MM1-v3's eight-session comparator (wall 6.65%, n 427; W 7.76%, n 362; the same code reproduces its committed table to
   5e-07) and a2c0-S4 alone (wall 5.80%, n 56; W 5.14%, n 54). (b) The E213 fold (both arms) under MM1-v3's **blind** error on the same E213
   points in the same unit (per case wall cycles; per point W over idle given t at 3 W and above), on E213's 127 points (117 cases; the four
   references excluded, REPORTED beside), from scores-e213's committed outputs.

If a rule fails, v3.1 is still frozen as built and the verdict names the rule that failed; v3's record and MM1-v3's blind E213 score are
printed beside. **The E213 fold's label:** held out for every constant, post hoc for the form choices E213 helps decide (item 8, and items 1, 3
and 4, whose rules include the E213 fold).

**What shows a term is not wanted** (registered): a term stays out when its declared rule picks the form without it. A term in v3.1 whose every
constant sits within 1% of its neutral value (or at a bound that makes it neutral) in the all-data fit is reported as not identified. For every
constant of the final fit the README gives its all-data value, its bound activity and its relative standard error from the Jacobian; above 100%
it is reported as not identified (as eta and T2 were in v3), with no change of the fit. v3-ledger is refitted and its LOEO and LOKO energy
REPORTED beside, never chosen (v3's energy decision stands).

## 10. v3.1's own blind day (a later experiment)

**When and where** (registered): registered after v3.1 lands, numbered the next free experiment then; v3.1's and v3's forecasts (both frozen)
with MM1-v2's beside. aifoundry3 card 0 (arm A) and aifoundry1 card 1 (arm B) at 600 MHz, as the lab's bookings and the model session's claims
allow. aifoundry2 card 0 is not an arm of that day (its host went down on 13 and 17 Nov 2026 with no stated cause); adding it takes a dated
amendment to that registration.

| family | tests | grid (candidates) | points, arm A / arm B |
|---|---|---|---|
| L | the layout term (T7 or its fallback) | rgm136 gemmL fp32, zeros and random, at shapes of 40-160 MB (MB, NB, KB up to 16) whose full-chip configuration ran on the arm's card; masks {4 g + c : g in G, c in C} for every row-group set G and column-group set C with n from 2 to 28 | 20 / 8 |
| P | item 3's winner | rgm211 gemmLn, rgm211 gemmL, gemmLnc and rgm136 gemmL, fp32 random (int8 at KB <= 2), at one-stream shapes (MB = 1 or NB = 1, the other up to 16), 5-200 MB, KB 1-48 | 12 / 6 |
| C | item 8's winner | rgm136 gemmL, KB 1-2, MB x NB >= 2, MB and NB up to 16, int8 and fp32 random | 10 / 6 |
| R | the two-edge retention | rgm136 gemmL, MB and NB up to 4, 36-140 MB, fp32 and int8 random | 10 / 6 |
| S | the switch route on newly counted kinds | kinds v31-counts counted that never ran in a GEMM on that card, at gemmL3x1x3 fp32 (and int8 if counted), each beside random in A B B A blocks | 8 / 6 |

**The point rule** (registered):
1. Candidates = the family's grid less every token E213's shape-level never-run scan finds (every committed data folder and lane folder; any card
   for arm A, the arm's card for arm B), re-run at the registration.
2. Score each candidate by |ln(F_v3.1 / F_v3)| of the wall cycles (family S: of W over idle, where F_v3 is MM1-v3's energy form at its landed
   constants with the new kinds' counts from item 7's verified tables as inputs and phi by item 7's rule; a candidate either model cannot
   price leaves family S's grid).
3. Take ceil(q / 2) of the family's quota q by descending score (ties by the sorted token) and the rest by
   `random.Random("v3.1-blind|<arm>|<family>").sample` of the remaining candidates sorted by token (ascending, as E213's never-run scan spells
   it): the day tests both where the models part and where they agree.
4. A family with fewer candidates than its quota takes all of them. Caps: arm A at most 70 card-minutes, arm B 48 (E213's), by the registration's
   plan in E213's run form; over a cap, drop from the random half first, in reverse draw order.

**Its rules:** bands twice v3.1's no-twin LOEO error per quantity (E213's form); v3.1 against v3 head to head by the exact sign test per arm and
pooled; MM1-v2 beside.

## 11. The order of decisions, and what is decided later (each by a rule above)

1. Item 8: family C decides T5r or tC from the frozen forecasts (no fit), after scores-e213; NOT DECIDED moves the choice to step 4.
2. Item 4: the trace check read from v31-trace and verify-v31trace (PASS, FAIL or NOT RUN).
3. Item 3: G0, Gplace, Goperand, Gcoop on the time form from step 1 (T5r if step 1 is NOT DECIDED), LOEO.
4. Item 4: the layout forms on the form from step 3, LOEO and LOLO; then, if step 1 was NOT DECIDED, item 8's step 3 on that form.
5. The final time form fitted on every fold (item 5), v3 refitted beside.
6. Item 1: the energy split on the final time form's folds, with item 7's counts and item 6's census as inputs.
7. Item 2: both LOCO routes on the final energy form; then the acceptance rules (section 9).

| decided later | by | when |
|---|---|---|
| T5r or tC | item 8's rule on E213's measured family C and BK | after scores-e213 is committed |
| T7 in or out | item 4's trace check, then item 4's fit rule | at v3.1's fit |
| which kinds carry counts | v31-counts' verified, committed tables (item 7) | at v3.1's fit start |
| the data set | GitHub main at v3.1's fit start, after scores-e213's commit (section 9) | at v3.1's fit start |
| the blind day's points | section 10's point rule on both frozen models and a fresh never-run scan | at that registration |
| T8 (address conflicts), a_row (DRAM row locality) | not built until a committed run logs the pools' device addresses; then a dated amendment before any fit | not in v3.1 |
| run_gemm's census; E202's kernel as a fourth kernel out | a counted census of their loops (none committed): until then run_gemm's path 0 and E202 NOT RUN | not in v3.1 |
| card 0's awake power against its governed base | a card-0 run at two clocks (none committed); v3's confound stands | not in v3.1 |
| a census path (gemmLnc, rgm211 gemmL, rgm211 gemmLn are desk; only rgm136 gemmL was checked against a counted run) | the comparison the census made for rgm136 gemmL (`census-v3.json`, `check_against_counted_run`): the PCs hart 0 ran at least 60 times in a committed counted simulator run of that loop against the census's steady path for it, the same set and the same length; if they differ, a dated amendment before any v3.1 fit replaces that loop's entry. Made by v3.1's fit lane as its first step, from committed runs only; with no such run at the fit's start the census entry stands and the README says so | before v3.1's fit |

## 12. Not built in v3.1, and NOT RUN here

**Not built** (registered): T6A (lost in v3); T8; a_row; lambda fitted (pinned 0.0048 a C); a kappa of their own for the scalar instruction
classes (one kappa, an assumption, stated); tensor-queue blocking and the second hart (not modelled, as in v3).
**NOT RUN by this lane:** any fit, card, simulator or commit; any score of a declared rule; the anchor route, the energy forms and the gamma /
T_coop forms on any data (nothing was scored before it was declared). **Desk, run here before any E213 datum:** tC's and T5r's wall cycles at
E213's 131 registered points from their frozen constants (section 8); the census correction (section 6); the layout classes of MM1-v3's 170
subset points and E213's family M masks (section 4); the seeded start values (section 5). **Desk, run by fix-v31decl before any E213 datum:**
`t7_v31.py --check` (section 4) and `comparator_4a_v31.py --desk` (section 9); T7 was evaluated on no measured value, and no v3.1 rule was
scored.

## 13. Files

- `DECLARED-v31.md`: this file.
- `declared-v31.json`: the same declaration for a script: `items` (each with its forms, constants, bounds, pins, rule and reports),
  `decision_order`, `deferred`, item 5's `bounds_and_boxes` and `start_values` (18 time starts, 9 energy starts, as numbers), item 6's per-loop
  values, item 8's 20 cases, and `embedded_desk_tables` (both frozen time forms at all 131 E213 points, with their inputs' sha256 and the
  reproduction check); since the correction also `corrections` (section 14 for a script) and `frozen_code` (the two files below).
- `t7_v31.py`: T7, the masked walk, as code (section 4); `python3 -I -B t7_v31.py --check` re-runs its desk checks.
- `comparator_4a_v31.py`: acceptance rule 4(a) with its comparator on the same E212 records (section 9); `--desk` prints MM1-v2's figures,
  `--score` decides the rule from v3.1's E212-fold table.

## 14. Change log

Every change below was made by lane fix-v31decl (round Q217) at aifoundry2's desk on Wed 18 Nov 2026 between 05:39 and the final time given
with the post, before any E213 datum: no E213 data file or data folder existed or was opened. Names and times only were listed, at 05:40:37
and 06:09:12 PST: at both, no E213 data folder in the lab clone or at GitHub main 6efdb002; at 05:40:37 no E213 card lane and no booking; by
06:09:12 E213's two card lanes had started (their lane folders existed; none was opened) and both cards were held for the sealed forecast
since 05:52:24. Each change answers one finding of the declaration's verification and rests on that finding and on MM1-v3's own files alone
(tools/matmul/mm1/v3 at b1493082 and E213's registration); nothing else changed.

| finding | where | change |
|---|---|---|
| 1 (medium) rule 4(a)'s comparator covered eight E212 sessions while v3.1's fold has nine | section 9, rule 4(a) | the comparator is MM1-v2's unread per-case error on the same nine-session case records, computed by `comparator_4a_v31.py` (new, hashed before the fit); desk 6.645% / 7.597%, the eight-session 6.65% / 7.76% beside |
| 2 (medium) trace criterion (a) could not be decided from sampled harts | section 4, the trace check | (a) restated over the logged harts with a minimum log set (every hart of every enabled shire and of at least one shire outside the mask, at both masks); below it, NOT RUN; "traced minion" defined |
| 3 (medium) T7's steps 3 and 4 had no frozen code | section 4 | T7 frozen as `t7_v31.py` (new): engine_v3's WalkShape procedure named, n_eff's denominator the same walk at 0xffffffff, r2's and zeta's reach stated; a failed desk precondition makes the trace check NOT RUN; its desk checks; section 8's r2 reading notes T7 |
| 4 (low) item 2's validity range had no fixed scale without aifoundry3 | section 2 | A2's rescale is applied before the anchor kc is solved and tested |
| 5 (low) item 1's tie-break chain was ambiguous | section 1 | candidates within 0.10 points of the lowest; fewest constants; at equal constants E1t before E1m |
| 6 (low) "v3 refitted" left its inputs open | section 9 | v3 refitted takes exactly v3.1's inputs (census-v3.1, item 7's counts and phi rule, data, folds, twins, pins, starts) |
| 7 (low) 0xffffffff fell in 'compact' | section 4, layout classes | the classes are for subset points; a full-chip point is in no class |
| 8 (low) E213's four references are twins | section 9 | reworded; rule 4(b) on E213's 127 points (117 cases), the references REPORTED |
| 9 (low) family S's score and the sample order | section 10 | F_v3 for family S defined (v3's landed energy form with item 7's counts as inputs); the sampled candidates sorted by token |
| 10 (nit) small gaps | sections 5, 7, 10, 11 | the seeded draws start-major; the counts' sha256 recorded in the README inputs table and fit record; phi's precedence; aifoundry2 not an arm of v3.1's blind day without a dated amendment; the census-path check's comparison and lane |
