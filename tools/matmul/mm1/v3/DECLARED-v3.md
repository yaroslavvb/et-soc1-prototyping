# MM1-v3: every form, bound, pin, fold and decision rule, declared before the fit

*Written Tue 17 Nov 2026 about 15:30 PST (Pacific), round Q214, lane mm1-v3, at aifoundry2's desk, before any MM1-v3 fit ran; its sha256 is
in the lane's progress log ahead of the first fit. It follows the spec (`v3-spec`, Q214: sections 5, 6, 9, 10, 11) and says where it departs.
Every constant of MM1-v3 is post hoc as an act (E212's and E211's data were read by the spec lane and its designs); declaring the forms first
keeps the choice among them honest, not blind.*

## 1. Data (data_v3.py)

Time: one point a (card, case), the mean of its runs: MM1-v2's 1,072 points' sources (E105-E190 rgm136 gemmL and run_gemm c-arms, E206 arm A,
E208's six sessions) with E208's seventh session a2c0-S1r pooled into its cases, E206 arm B, E207, E209, E211 (rgm136 twins as rgm136
points; rgm211 gemmLn and rgm136 gemmLnc with their kernels), E212's eight committed sessions (every kind: time is kind-blind): 1,737 points.
Energy: the same cases with an energy figure, plus E210 (energy only) and E206's sparse50 points; E212's switch-pattern arms are not read for
energy. E146's store rungs: MM1-v2's points include E146; the spec asks its store rungs be held out of every fit, so **every E146 point whose
id names a store-cadence rung (`-L1-`, `-L4-`, `-L8-`, `-D1-`, `-D2-`, `-D4-`, `-D8-`, the smoke's included: 87 time points) is dropped from
every training set, time and energy, and scored apart**; E146's L2 and F6 rungs stay (MM1-v2 trained on all of E146: the v2form baseline
here drops the same points, so both forms see the same training sets).
**The data's commit:** the final fit reads everything committed at GitHub main when it starts; if E212 sessions land after this file, they
are vendored, the unread table (step 1) is re-made and re-hashed first, and the commit is named in the README.

## 2. Time forms (engine_v3.py)

| form | retention | path term | int8 L3 | C store | subsets | free constants |
|---|---|---|---|---|---|---|
| **v3** (primary) | B two edges (x1, w1, pB, x2, w2), A one edge at (x1, w1) | census D (0 fitted) | d8 | tC | n/32 (chi3, chiF) | c3 m3 cF mF kA F2 T2 x1 w1 pB x2 w2 zeta piF0 chi3 chiF eta d8 tC (19) |
| v3-T5r | as v3 | as v3 | d8 | r2 (L2 share at KB <= 2, MB x NB >= 2) | as v3 | as v3 with r2 for tC (19) |
| v3-T6A | B two edges, A its own edge (xA, wA) | as v3 | d8 | tC | as v3 | v3 + xA wA (21) |
| v3-T7L | as v3 | as v3 | d8 | tC | layout fallback n_eff = (64 R/8 + 128 C/4) / 192 | as v3 (19) |
| **v2form** (baseline) | one logistic (x50, s) | none | none | none | n/32 | c3 m3 cF mF kA x50 s zeta piF0 F2 T2 chi3 chiF eta (14) |

- **Departure from the spec's T5 weight:** w_dest uses the full latency ratio of a fresh line to an L3 line at the point's clock and the full
  chip, (cF/f + mF) / (c3/f + m3), not the cycle parts cF/c3 alone: c3 may approach 0 inside the bounds, where cF/c3 diverges; the latency
  ratio is the same reading ("costlier when C goes to DRAM") with no new constant. The C stays in the L3 at the A edge's retention of the pass
  footprint, r_C = 1/(1 + exp((F - xA)/wA)).
- **Not built in v3.0 (pinned, with the reason):** T4g gamma and T4c T_coop (0; unidentified, the spec's v3.1); T8 A_eff (no device addresses:
  MM1-v2's piF0 and zeta kept); T7's masked walk (needs traced simulator runs: the declared fallback T7L is the only layout form tried).
- **Bounds:** MM1-v2's for every shared name (c3, cF in [-3000, 3000] cycles; m3, mF [-5, 10] us; kA [0, 3]; x50 [20, 120] MB; s [0.3, 40];
  zeta [0, 1]; piF0 [-0.5, 3]; F2 [0, 1000] cycles; T2 [0, 2] us; chi3, chiF [-2, 0.95]; eta [0, 2]); new: x1 [20, 120] MB, w1 [0.3, 40],
  pB [0, 0.95], x2 [30, 400] MB, w2 [0.3, 80], xA [20, 120], wA [0.3, 40], d8 [0, 0.2], tC [0, 400] cycles a line, r2 [0, 1].
- **Starts:** six per fit, the same for every fold: MM1-v2's TH0 and its five spread starts for the shared names; for the new names
  (x1, w1, pB, x2, w2, xA, wA, d8, tC, r2) = (40, 4.5, 0.3, 90, 10, 40, 4.5, 0.06, 40, 0.5), (36, 3, 0.2, 70, 6, 36, 3, 0.03, 20, 0.3),
  (44, 6, 0.4, 110, 15, 44, 6, 0.09, 80, 0.7), (38, 2, 0.1, 60, 4, 38, 2, 0.0, 10, 0.1), (46, 8, 0.5, 130, 20, 46, 8, 0.12, 120, 0.9),
  (42, 5, 0.25, 80, 8, 42, 5, 0.05, 60, 0.5); none read off any fit. The x50/s of MM1-v2's starts seed the v2form.
- **The fit:** least squares on forecast / measured - 1 of the wall op time, every training point weight 1 (as MM1-v2); scipy least_squares,
  x_scale 'jac', diff_step 1e-4, ftol = xtol = gtol = 1e-10, at most 4,000 evaluations a start; the lowest training cost kept; every start's
  cost, evaluations, status and held-out rms recorded. **The all-data fit converges from the same six starts** (the spec's 9.6; MM1-v2 froze
  one start), and the spread of the starts that reach the best cost is reported.
- **The pin rule** (a constant whose identifying set has no point in the fold's training set is held at its neutral value; every pin printed
  with its fold), identifying sets as predicates on the training points:

| constant | identifying set | neutral |
|---|---|---|
| F2 | gemmL-loop points (rgm136 / rgm211 loops) with MB = NB = KB = 1 in int8, at f >= 700 MHz **and** at f < 700 MHz | 0 |
| chi3 | subset points with footprint <= 32 MB | 0 |
| chiF | subset points with footprint > 48 MB | 0 |
| d8 | int8 points with footprint <= 32 MB and KB >= 2 | 0 |
| tC (r2) | gemmL points with KB = 1 and MB x NB >= 2, or run_gemm points | 0 (r2 = 1) |
| pB (then x2, w2 held at the start's) | full-chip gemmL points with NB <= 2 and footprint >= 70 MB | 0 |
| xA, wA (v3-T6A) | full-chip gemmL points with NB = 1 and footprint in (32, 70] MB | x1, w1 |
| zeta, piF0, eta, kA, c3, m3, cF, mF, T2, x1, w1 (x50, s) | never pinned (as MM1-v2) | - |

## 3. Folds

LOEO, 17 folds: E105, E107, E119, E126, E136, E146, E158, E159, E168, E169, E190, E206 (arms A and B), E207, E208 (seven sessions), E209, E211,
E212; **E212 by card**, 3 folds (its aifoundry1 card 1, card 0 and aifoundry2 points apart); **LOCO**, 4 cards; **LOKO**, 3 kernels: rgm211
gemmLn (kernel rgm211), rgm136 gemmLnc (arm prefix gemmLnc), run_gemm (its c-arms); **leave one layout out**, 3 classes of subset masks:
compact (0xf, 0xff, 0xffff, 0xffffff), spread (0x1111, 0x11111111, 0x33333333, 0x77777777), other (every other subset mask). Every constant
refitted in every fold from the six starts; the energy fold on its own time fold's lines and seconds. E202's MNIST kernel (the spec's fourth
LOKO): NOT RUN (no census of its kernel). E211 is never in the training of a fold that scores it.

## 4. Decision rules (time), declared now

Each alternative changes one choice of the primary v3. For each pair: the lower **LOEO wall rms over all 1,737 points** (both forms price
every point); within 0.05 points, the form with fewer constants; equal constants, the primary. The frozen v3 is the primary with every
winning alternative; if any wins, that combined form is fitted on every fold.

## 5. Energy forms

**v3** (the spec's section 6, design c's switch route), W over idle at the point's op time t (us):

```
W = [ Pa(card) n/1,024 + Pm u + g G + (n / t) { sV kc [ Eub(fmt) - Gate(fmt, kind) + m(fmt) b0 S(fmt, kind, KB) ] + sV dEi(loop)
      + sL 1e-12 [ sum_l (n_l/32)(b_l + d_l phi) + eC nC ( rC (b3 + d3 phi) + (1 - rC)(bF + dF phi) ) ] } ] x (1 + lam (T0 - 50 C))
sV = (V / 0.517 V)^2 (MM1-v2's volts), sL = 1 + xi (sV - 1), lam = 0.0048 a C pinned, T0 the run's die at start (50 C when absent)
```

- S = the counted signal fin edges an op (zero-delay, MM1-v1's units): fp32 from E210's desk counts at GEMM states (KB = 1: its S1, KB >= 2:
  its S2; zeros, ones, randn, sparse50 and E210's nine patterns), fp16 and int8 from MM1-v1's switch table at the launch points (zeros, ones,
  randn / full, sparse50). Gate: floats a_op g_op + a_lane g_lane (J an op, shared by fp32 and fp16: the same clocks an op), g_op the share of
  micro-ops gated on every lane, g_lane the share of lanes gated inside micro-ops that run (zeros 1 / 0; arow50 0.5 / 0; sparse50 with lane
  valid share v gated at random over 8 lanes (1-v)^8 / (1-v) - (1-v)^8; ungated kinds 0 / 0); int8 a8 (1 - v); v from the counts' valid
  slots (fp32) or clocked bits (fp16, int8: (bits - bits_zeros) / (bits_ungated - bits_zeros)). dEi: the census's instruction energy
  (0 fitted). nC, rC: the C store's lines and their L3 share (as the time form). phi: MM1-v2's (zeros 0, random 1, ones and sparse50 from
  their tiles / generator; E210's patterns from E210's frozen forecast file).
- Free (26): Pa x 4 cards, Pm, g, Eub x 3, b0, m_fp16, m_int8, a_op, a_lane, a8, kc x 3 (aifoundry3 = 1), b2 d2 b3 d3 bF dF, eC, xi.
  **Not built in v3.0:** E7 a_row (no address or row model of the walk: pinned 0); lambda fitted (pinned 0.0048).
- **v3-ledger** (the spec's 'E2 against the ledger fallback'): v3 with MM1-v2's resident term (ledger v2's anchors x k_res, D_ones) in place
  of Eub, Gate, b0 and m; it prices zeros, random and ones only.
- **v2form**: MM1-v2's energy design exactly (fit_v2's 'v2' rows: Pmin x 4, Pmem, g, b/d x 6, k_res x 5, D_ones x 3; linear), on its own
  time fold's theta.
- Kinds with no count and no ledger row, and 'real' (ledger rows on aifoundry3 only): NOT FORECAST by v3 in the fit and in the folds (never a
  nearest-kind guess); the predictor's labelled ledger fallback for 'real' is scored apart.
- The fit: least squares on (W - W_meas) / max(W_meas, 3 W); v2form linear; v3 and v3-ledger nonlinear (least_squares from the linear solve
  at kc = 1, xi = 1, m = 1, and two more starts with kc, xi, m set to 1.05 / 0.5 / 1.2 and 0.95 / 0.9 / 2.0); bounds kc [0.5, 2], xi [0, 1],
  m [0.2, 5], eC [0, 10], others free.
- **Energy pins:** a held-out card takes the other cards' mean Pa and kc 1 (MM1-v2's rule); xi 1 without governed-card points; eC 0 without a
  KB = 1, MB x NB >= 2 point; a_lane 0 without a sparse50 point; a8 0 without an int8 zeros point; m of a format 1 without its points.
- **Decision (energy):** v3 against v3-ledger by the lower LOEO W given t (>= 3 W) on the points both price; within 0.1 point, fewer constants.

## 6. Scores and the acceptance rules (the spec's section 11, declared there; restated)

Scores: wall cycles, the counter's mean (MM1-v2's rho), seconds, J over idle given t and with t forecast, J at rest both ways, per point
(= per case), bias and rms; J over idle at 3 W and above (watts below). **v3 is accepted for freezing only if, on the same points and folds:**
(1) LOEO wall and LOEO J over idle given t both below v2form's; (2) LOCO not worse than v2form's by more than 0.3 points in either;
(3) LOKO rgm211: wall rms at or under 8.0% and at least 7 of 10 W pairs inside 0.05 in ln; (4) the E212 fold under MM1-v2's UNREAD error on
the same E212 points in the same unit (per case, from unread_v2_e212.py, hashed before this fit: wall 6.65%, W given t 7.76%).
**If a rule fails, v3 is still frozen as built and the verdict says which rule failed** (the spec gives no fallback model); the record
v3 is measured against (MM1-v2's held-out and blind figures) is reported beside.

## 7. E213 (the spec's section 12)

The points: the spec's candidate families I, R, C, M, P, E at aifoundry3 card 0, 600 MHz (rgm136 unless named; rgm211's gemmLn and its own
gemmL, and gemmLnc, for family P), each kept only if a scan of every committed data folder and every lane and work folder on this box finds
no run of that kernel and shape on aifoundry3 card 0 (any run of the shape on any card is recorded beside). v3's forecasts (as frozen),
MM1-v2's (as frozen, its predictor unchanged) beside; the registration lane fixes the final points.

## A1. Amendment, Tue 17 Nov 2026 15:4x PST, before any fold fit or any decision (numerics only)

The tolerances become **ftol = xtol = gtol = 1e-8** (not 1e-10), at most 4,000 evaluations a start, for every time fit of every form. Why:
two desk test fits of the all-data set (in sample only, no fold, nothing read held out) showed MM1-v2's form from its start 0 creeping for
4,000 evaluations (90 s) at 1e-10 to a training cost of 1.8362616, while its start 1 reached 1.8361955 in 11 evaluations at 1e-8; at 1e-8
the six starts' best cost is the same or lower and a fold fit takes seconds, not minutes, so all 32 fits a form x 6 starts can run in one CPU
slot. The same tests showed MM1-v3's form has at least two minima (training cost 1.4181 from start 0, 1.5191 from starts 1 and 2): the six
starts and the lowest-cost rule stand as declared. Nothing else changes.
