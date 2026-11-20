# DECLARED-lnc-form: the replacement for MM1-v3.2's gemmLnc term F3 - the protocol and every candidate form, written before any fit

*Fri 20 Nov 2026 (week 47), Pacific time. Round Q234, lane lnc-form (track G), on aifoundry2's desk. Written and hashed BEFORE any fit of
any form below. Interpreter for every number to come: `/usr/bin/python3` 3.12.3 with numpy 1.26.4 and scipy 1.11.4, `-I -B`, single
threaded (OMP / OPENBLAS / MKL / NUMEXPR threads 1) inside the round's CPU slots. Desk only: no card, no simulator, no E220 datum.*

## 0. What has been seen before this declaration (disclosure)

- The lead (the brief): F3 (MM1-v3.2: c1 247.72, c2 448.65 pJ a line) over-predicts the extra power where the real excess is small
  (E216's g01 and g07-g10; E218's G family; aifoundry3's 1.4-1.55x on E215) and is right where it is large.
- This lane's step 1 table (`scripts/s01_data.py` -> `work/s01_points.json`, sha256 `cc23fbce0d2137287f21c21f2c254e39f48e970bdcc5ca13984e82d50e1be415`)
  and three exploratory listings of it (`s01b_show.py`, `s01c_feat.py`, `s01d_groups.py`: no fit, no constant estimated): every committed
  gemmLnc point's measured excess over MM1-v3.2's base in pJ a minion-op beside MM1-v3.2's own map features (the L2/L3/fresh shares of A and
  B, MM1-v3's line-map groups and their retention, NB, KB, MB, footprint), the measured gemmLnc/gemmL op-time ratio and the twins.
  **So every new form below was designed after its data were seen: post hoc in design.** What this declaration fixes before any fit is the
  set of forms, their features (each a function of the token, the format and MM1-v3.2's frozen map only: no measured quantity enters a
  feature), the fit, the folds, the margin, the placebo and the choice. The listings' only arithmetic: excess = (W_meas - base) / S, and an
  eyeball "refetch count" (excess - 26 x 208 pJ) / 600 pJ with two round numbers that are not fitted and enter nothing below.
- E220's registered point list (OUT/reg-e220/POINTS.txt, FINAL 05:24:17 PST; tokens, cards, clocks only) was read; no E220 datum exists and
  none will be opened.

## 1. The data (every committed gemmLnc energy point through E219, and its twins)

36 points, all rgm136 gemmLnc on the full chip, random data (34 fp32, 2 int8), each with its cooperative gemmL twin where one ran:

| experiment | card | points | source |
|---|---|---|---|
| E211 | aifoundry3 card 0, 600 MHz | c01c, c02c | MM1-v3.2's `out/points_energy_v32.csv` (its fit's own records) |
| E213 | aifoundry3 card 0 (a075, a079, a082, a086, a087); aifoundry1 card 1 (k37, k40) | 7 | the same |
| E215 | aifoundry3 card 0 (a024, a026, a031, a032); aifoundry1 card 1 (b013) | 5 | the same |
| E216 | aifoundry2 card 0, governed, 799 MHz (route c) | g01-g10 | data-e216.json (E208's reducer, view 'win'), equal to the frozen scorer's measured_route_c |
| E218 | aifoundry3 card 0, 600 MHz | g01-g12 | data-e218.json, E215's reading |

E212, E214, E217 and E219 hold no gemmLnc arm (their hosts cannot run it; E212 and E214 hold none by their registrations): their folds are
named below and change nothing (the term is 0 there). The twins (33) and every cooperative point are priced 0 by every form below.

## 2. The base and the term's footing (shared by every form)

- **The base**: MM1-v3.2 frozen (`tools/matmul/mm1/v3.2/out/mm1_v32_params.json`, landed 4e386f75; its predictor `mm1_v32.Model`) with F3
  removed: base(t) = W_v32(t) - F3_v32(t), W_v32(t) = A + B / t at the point's measured clock, die (t0_c), minion volts and governed base, as
  MM1-v3.2's own data path prices it (`s01_data.py`; it re-makes MM1-v3.2's in-sample W given t at the 14 in-fit gemmLnc points to 7e-15 W).
  **No constant of MM1-v3.2 is refitted** (its E1t, time, rest law: unchanged). The term replaces F3 only.
- **The term**: dW = S x E, S = D sL (n / t_op) 1e-12 [W per pJ a minion-op] exactly as F3's (D = 1 + 0.0048 (die - 50 C), sL = 1 + xi
  (s_V - 1) at MM1-v3.2's xi, n the minions, t_op the op time: measured for 'given t', MM1-v3.2's forecast otherwise); E in pJ a minion-op;
  E = 0 at every cooperative loop; not multiplied by kc nor phi (F3's convention).
- **Features** (per point, from the token, the format and MM1-v3.2's frozen map Q = (Q0 + Q1) / 2 at its all-data constants):
  - dup = 26 (the duplicate line reads a minion-op of rgm136's gemmLnc: 14 A + 12 B; the kernel source);
  - beyond = 14 (1 - qA_L2) + 12 (1 - qB_L2) (the duplicates of lines the map serves beyond the L2); first = beyond / NB (F3's);
  - qBF = B's fresh share of the map (Q summed over A's place, the fresh column); qA_b = 1 - qA_L2, A's beyond-L2 share;
  - phi = 1 if MB = 1 else (NB - 1) / NB (the share of A reads that are near reuse within a row of C blocks: MM1-v3's line map,
    `mm1_core_v3.groups_masked`);
  - m = 1 if 2 KB sa + KB sb > x1 else 0: the near reuse misses the L3 when the row's A panel (2 KB MB) and one C block's B panel (KB MB)
    together exceed MM1-v3.2's own first L3 edge x1 = 37.334 MB (its time theta; sa, sb the mask's shares, 1 on the full chip);
  - a_f = (1 - phi) + phi x m: the share of A reads that come fresh into the row (its first C block, every block when NB = 1, all of them
    when the near reuse misses);
  - Lres = 1 if the GEMM's footprint (MM1's `footprint(MB, NB, KB)` with the mask) <= x1 else 0 (the whole GEMM L3-resident across
    launches).

## 3. The forms (each at most two constants, c1 and c2 in pJ a line, bounds [0, 10,000])

| name | E (pJ a minion-op) | constants | reading |
|---|---|---|---|
| **F3r** (comparator) | c1 dup + c2 first | 2 | F3 itself, refitted on the same data (the incumbent) |
| F1r | c1 dup | 1 | verify-lnc's F1: one price for every duplicate |
| F2r | c1 dup + c2 beyond | 2 | F2: every duplicate of a beyond-L2 line re-fetched |
| F4r | c2 beyond | 1 | F4 |
| STEPr | c1 dup + c2 beyond [NB <= 3] | 2 | verify-lnc's step form (G3/G4) |
| **AF1** | c1 dup + c2 R1, R1 = a_f (14 qA_b + 12 qBF) | 2 | the A-fresh lockstep: while A comes fresh into the row, the 8 minions sharing an A line wait on one fetch and re-fetch its 14 duplicates, and the 12 B duplicates of B lines from DRAM are re-fetched too; while A is re-used from the L3 (near), the minions run free and every duplicate hits the L2 |
| **AF2** | c1 dup + c2 R2, R2 = Lres x beyond + (1 - Lres) x R1 | 2 | AF1, and a GEMM wholly L3-resident runs in lockstep: every beyond-L2 duplicate re-fetched |
| **AF3** | c1 dup + c2 R3, R3 = a3 (14 qA_b + 12 qBF), a3 = 1 if (NB = 1 or m = 1), else (1 - phi) if NB = 2, else 0 (NB >= 3 and m = 0) | 2 | AF1 where two or more near C blocks between fresh ones are enough to desynchronise (no re-fetch even on the row's first block) |
| **AF4** | c1 dup + c2 R4, R4 = Lres x beyond + (1 - Lres) x R3 | 2 | AF3 with AF2's L3-resident clause |

(qA_b keeps an L2-served A stream out of R1 and R3: at the L2-resident 1x1x1, qA_b = qBF = 0, so R1 = R3 = 0; R2 and R4 read beyond = 0 there.) AF1-AF4 are this lane's new forms; F1r, F2r, F4r and STEPr are verify-lnc's siblings refitted. Every form is identically 0 off gemmLnc.

## 4. The fit (post hoc, every form the same way)

Weighted linear least squares of the relative W error over the gemmLnc points in the training set: minimise sum_i ((base_i + S_i E_i) /
W_i - 1)^2 over the form's constants within [0, 10,000] pJ (`scipy.optimize.lsq_linear`, method 'bvls', tol 1e-12), base_i and S_i at the
measured op time. All data: the 36 points (twins enter with a 0 term: they cannot move a constant).

## 5. Held out (each fold refits the form's constants on the other gemmLnc points; the base is MM1-v3.2's frozen base throughout)

- **LOEO** (the lead's held-out error, deciding): folds E211, E213, E215, E216, E218, each holding out all its gemmLnc points; E212, E214,
  E217 and E219 named, with no gemmLnc point (nothing to hold out: the term is 0 at all their points). The metric: rms and bias over the 36
  held-out points of (W forecast / W measured - 1), W over idle given the measured op time, in %.
- **The folds the lead names** (REPORTED beside, never deciding alone): E216's fold and E218's fold apart (the small-excess points); and
  LOCO by card (aifoundry3 card 0: 23 points; aifoundry1 card 1: 3; aifoundry2 card 0: 10); LOPO (each point alone) REPORTED.
- **Twins split**: the twins' errors (MM1-v3.2's base, term 0) REPORTED apart; no gemmLnc point has a configuration twin in another
  experiment's training set (E213's a075/k37 and a087/k40 sit in one experiment and leave together).

## 6. Keep rule (stated before fitting)

A form other than F3r is **kept** only if all three hold:

1. **margin**: its LOEO rms over the 36 gemmLnc points is at least **1.0 percentage point lower** than F3r's (F3 refitted the same way);
2. **pooled guard**: MM1-v3.2's pooled held-out error (LOEO without twins, W over idle given t at >= 3 W, MM1-v3.2's own record: 1,829
   points E105-E215 with E214, rms 4.976%), with E216's and E218's 22 gemmLnc points added at MM1-v3.2's frozen forecasts, rises by at most
   **0.05 points** when the form replaces F3: in-fit gemmLnc points (14) priced at MM1-v3.2's own LOEO fold base (its fold W minus its fold
   F3, the fold's c1 and c2 from `out/holdout_v32.json`) plus the form's term fitted without that experiment; E216's and E218's points at
   MM1-v3.2's all-data base plus the form's term fitted without that experiment. E217's and E219's points are equal for both by
   construction (no gemmLnc point) and are left out, which makes the guard stricter, not looser.
3. **placebo**: its feature (the c2 column; F4r's beyond) permuted across the 36 points (100 draws, numpy default_rng(20261120 + j), j = 0..99),
   refitted and scored by the same LOEO: the real form beats the placebo in at least **95 of 100** draws. F1r has no non-constant feature
   (dup = 26 at every point): its placebo is NOT APPLICABLE and it cannot be kept.

**The choice**: among kept forms, the lowest LOEO rms; within 0.25 points of it, the fewer constants, then this order: AF4, AF3, AF2, AF1,
STEPr, F2r, F4r. **If none is kept**, the form with the lowest LOEO rms among the eight non-comparator forms is frozen as a REJECTED
CANDIDATE, reported the same way.

## 7. The frozen forecasts (E220, both arms, every point of POINTS.txt)

'MM1-v3.2 + <term>' = MM1-v3.2's predictor at E220's registered call (card, token, fmt, kind random, mask, f = the arm's clock: arm A
600.0 MHz; arm B 799.0 MHz, with 700.0 and 600.0 MHz columns; kernel rgm136; V, G, t0_c, minions, ops not given), F3 removed, the chosen
form's term at its all-data constants added: wall cycles an op and the counter's mean (MM1-v3.2's, unchanged), seconds a GEMM, W over idle
at the forecast op time, the affine form for W over idle given a measured op time t (A, B' with B' = B - F3 t_op + dW t_op: W(t) = A + B' /
t), J over idle a GEMM with t forecast, and J at rest a GEMM (MM1-v3.2's rest law at its T0 forecast plus W, times the seconds). Cooperative
points equal MM1-v3.2 exactly. Every other form's E220 W and J columns beside, REPORTED. Files new, sha256 and the time they were final in
OUT/lnc-form/FROZEN.txt, before any E220 datum.
