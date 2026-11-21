# DECLARED: 'MM1-v3.2 + mask-ceiling', a nonparametric REFERENCE for core-group mask placement (round Q238, track C, lane mask-ceiling)

Written Sat 21 Nov 2026 (week 47), Pacific time, at aifoundry2's desk, BEFORE any fit of the reference to any lab residual. Desk only. Interpreter
/usr/bin/python3 3.12.3, numpy 1.26.4, `-I -B`, single-threaded (OMP/OPENBLAS/MKL/NUMEXPR_NUM_THREADS = 1), every numerical job in the
round's CPU slots, one at a time.

**What this is, and what it is not.** A REFERENCE, REPORTED: a random forest of small regression trees that predicts MM1-v3.2's ln wall
residual at core-group mask placements from mask features (and the shape's own context), held out exactly as the round's COMMON says. It
bounds what a mask term built from these features can reach and ranks the features. **It is never a model candidate**: whatever its keep
rule reads, it is frozen as 'reference, REPORTED' and never joins MM1.

**What was looked at before this was written (disclosed).** The input FORMS only (keys and counts of every file read; `scripts/p00_probe.py`);
the round's published lead (blind-e221: MM1-v3.2's MASK class 12.41% rms on E221's 363 no-twin cases, its per-class table); MM1-v3.2's base
at every point and its exact agreement with the stored fits (every stored fold check 0.0; E221's case errors equal blind-e221's
`v32_e_wall` to 3.4e-6: an equality check, no residual was studied); the feature RANGES (`logs/f01.log`, no residual); this lane's class rule
against blind-e221's E221 labels (392 MASK and 341 other cases, all agreeing); MM1-v3.2's elasticity of its op time to its memory costs at
the in-scope points (0.967-1.000 everywhere: a base-model quantity, no residual), which is why no elasticity feature is used; the learners
on SYNTHETIC data only (`rf_core.py` self-test). No feature was compared with any residual; nothing was fitted to a lab residual.

## 1. The base, the data and the scope

- **The base:** MM1-v3.2 (tools/matmul/mm1/v3.2/, declaration f8e00a57, model 4e386f75) unchanged: its op time by `time_v31.Engine31`
  (T5r+G0+n32) at its constants, computed at every point by `scripts/e01_base.py` (sha256 `ddd1620a28d6010caecaedcb4b4264bb83334a3df8dabd9a57556c434af31ea0`;
  output `work/base.npz` `c19c3a64280b3d03fc648ed6a0ca38ad9547143c2733a8989b2351bfe979a22e`). **No MM1-v3.2 constant is refitted.**
- **The data:** every committed matmul time point through E224 in `work/points_all.json` (sha256
  `0090bbddae5e0ceb575248139fd1c01799bd219198708d911b98651b4e3e3d0f`, by `scripts/d01_points.py` `21e57b981dc30dad4e6122d37dce0e570d6d45f1aafb423bf264aa5858c6a470`
  at GitHub main cfd7e641): 4311 points: MM1-v3.2's 2508 (E105-E215), E216 46, E217 486, E218 52, E219 139 (in domain), E220 156 (arm A 84,
  arm B 72 route c), E221 733 cases, E222 70, E224 121 (arm A 62, arm B 59; **p3a and p3b excluded on both arms**); runs whose check of C was
  not 'exact' or 'approx' excluded (one, in E218); E224 arm B reduced by E208's registered reducer (b9e32618) by
  `scripts/s02_reduce_e224b.sh` (`a8a934bc094b695eb891da504ecbe332d45afa5062500a792bc38a5308463be1`; `work/e224b/data-e224b.json`
  `e5cf09f2b36e61a910d4b794f276ad5a9497031159075c620e6a68e830d804c3`). A run a verifier of E222 or E224 later names faulty is dropped by a
  dated note, never silently.
- **Scope (the points the reference may move):** rgm136's cooperative gemmL loop at a shire SUBSET with MB x NB >= 2 (`r_common.in_scope`):
  888 points. Every other point, every full-chip point included, keeps MM1-v3.2's op time to the last bit.
- **THE MASK CLASS** (blind-e221's definition, applied by `r_common.classes` to every point): the scope's points plus their whole-chip twins
  (a full-chip rgm136 gemmL point of the same experiment, card, arm, format and kind): 975 points (E221 392, E214 149, E217 130, E212 86,
  E220 50, E215 28, E206 24, E213 24, E222 22, E224 19, E216 16, E218 15, E209 12, E207 8). On E221 it reproduces blind-e221's labels exactly.

## 2. The features (`scripts/f01_features.py` `da86122b20a37ad651928633218d583cd7053d47474efb30e62560b500864ea3`, output `work/features.json`
`688ce17ef9a56745ed3e20bf769954cca193b67d8a21592dc32cf92efe009fd4`; `scripts/r_common.py` `4a43e05482775f1599c2e05b39ba20d04c9d1b7eb3c0c4fa11d1b3adbb1771ce`)

Known (read from committed sources) and assumed (this lane's choice) are named in f01's docstring: row group s >> 2 (A tiles shared within it)
and column group s & 3 (B tiles); the MARTY mesh positions (workloads/nocbench/analyze.py); the L3 law 110 + 12 x hops to the home (PA[10:6]);
the memory shires off the north and south edges at x = 1-4 (the lab's notes; placed as layout2's x01_hops.py places them); from the kernel's
addresses, every tile of an op step has the same PA[10], so a step's requests fall evenly on one half of the homes (no within-step slice
imbalance for this kernel: the slice loads reduce to 12 n requested and 4 R + 8 C distinct lines per receiving home); ASSUMED: X-then-Y
routing, data flowing home -> shire, each active shire's traffic spread evenly over the 32 homes, for the link loads.

- **M, the 17 mask features (the placebo permutes these):** n; R; C; rmax; cmax; rimb = rmax / (n/R); cimb = cmax / (n/C);
  G1 = (110 + 12 hbar_act) / Lmean_full - 1; hlag = (Lmax_act - Lmean_act) / Lmean_full; spread (mean pairwise hop of the active shires);
  bbox (their bounding box cells / 36); memd (mean hop to the 8 memory shires); link (the hottest directed link's load over the full
  chip's, the assumed routing); dist_rel = (4 R + 8 C) / 64; Fp, Fs (layout2's private and shared DRAM-served request shares at a 32 MB
  strict LRU, by its committed `f02_private.private_shared`, imported unchanged; 306 configurations read from its committed
  private_shared.json, 5 of them re-made equal, 152 made here); LAG = hlag x Fp / (Fp + Fs) (layout2's LAGcore, 0 with no fresh line).
- **X, the 5 shape-context features (never permuted):** MB, NB, ln KB, the format (fp32 0, fp16 1, int8 2), the point's clock f (MHz).

## 3. The form (the bounds; the two constants; the fixed settings)

- **Target:** y_j = ln(T_meas,j / T_base,j) at the fold's base. **Wall op time:** T = T_v32 x exp(clip(yhat(x), -0.5, +0.5)) at in-scope
  points (the bounds: the factor within e^-0.5 .. e^0.5), T_v32 elsewhere; yhat = the forest's mean of its trees' leaf means.
  Wall cycles an op, the op time and seconds a GEMM all take the factor; the counter's mean cycles an op is NOT forecast by the reference
  (MM1-v3.2's own, REPORTED as such); energy for the composition only: MM1-v3.2's W over idle at an op time t (A_W + B_W / t, its own A_W and
  B_W) at the reference's t (W given a measured t is MM1-v3.2's own).
- **The learner (`scripts/rf_core.py` `5f92ba5af3d2f3fde39e5d2e9bba493ace193611ee983a62a7315fbb72523c97`, this lane's numpy code):** a random
  forest of CART regression trees. **Its two constants, fixed here, not tuned:** maximum depth **D = 6** and minimum leaf **L = 5** points.
  **Fixed settings (not constants: they set Monte Carlo noise and the standard regression default, not a fit):** 200 trees, each on a
  bootstrap of the fold's training points, **mtry = 8** of the 22 features drawn at each node (ceil(22/3)), least-squares splits at midpoints.
  A nonparametric reference has no fitted constant beyond its stored training set: its 'params' are the all-data forest (section 7).
- **The starts (seeds):** fold k (0-based, in r_common.folds order) of family phi (LOSO 0, LOEO 1, LOCO 2, LOMO 3):
  numpy.random.default_rng(20261121 + 100000 phi + k); the all-data forest default_rng(20261121). A fold with no in-scope test point is not fitted
  (its predictions are the base).

## 4. The folds (held out exactly as COMMON says; `r_common.folds`)

- **LOSO**, leave one E221 session out (9 folds; a case's session = its first run's: 12 of 733 cases span sessions); base = all-data constants.
- **LOEO**, leave one experiment out (28 folds, every experiment; **E215-E224's named**); base = MM1-v3.2's stored 'LOEO <exp>' constants for
  E105-E215, its all-data constants for E216-E224 (never in its fit).
- **LOCO**, leave one card out (4 folds); base = MM1-v3.2's stored 'LOCO <card>' constants.
- **LOMO**, leave one mask out over the 115 subset masks E217, E221 and E224 ran; test = every point at that mask from any experiment;
  base = all-data constants.
- In every fold the reference trains on the fold's NON-test in-scope points (targets at the fold's base).
- **Twins split (per fold):** a test point is a twin when a non-test point has its card, kernel, arm, format and mask (layout2's key); LOCO
  and LOMO have none by construction. Every figure is printed with and without twins; the rules read without.

## 5. The metrics, the margin and the keep rule (stated before fitting)

- **M1(phi)**, the MASK class's held-out wall rms (%, error = forecast / measured - 1, blind-e221's form) over family phi's MASK test points
  without twins; **MM1-v3.2's M1(phi)** on the same points at the same fold bases. **The share explained:** 1 - (M1_ref / M1_v32)^2.
- **M2**, the non-MASK classes' LOEO held-out wall rms without twins (the guard), MM1-v3.2 against 'MM1-v3.2 + mask-ceiling'.
- **The E221 footing (REPORTED):** under LOSO, the 363 E221 MASK cases blind-e221 counts as no-twin (its own twin flags): MM1-v3.2 must read
  12.41% there (a check), the reference's figure beside.
- **KEEP (meets the rule) iff all three:** **K1** M1_ref(phi) <= **0.90** x MM1-v3.2's M1(phi) on **every** family (LOSO, LOEO, LOCO, LOMO): the
  margin, a tenth of the MASK error everywhere; **K2** M2_ref <= M2_v32 + 0.05 points; **K3 the placebo**: 100 draws i = 0..99, in draw i the
  17 mask features are permuted as one block among the in-scope points WITHIN EACH SHAPE (same arm and format), group by group in sorted
  group order, by numpy.random.default_rng(20261121 + 7000 + i).permutation; the context left in place; the LOSO family refitted with the
  real folds' seeds; the real M1_ref(LOSO) must be below the placebo's in at least 95 of the 100 draws. **Either way the reference is frozen
  as 'reference, REPORTED'** and its verdict line says 'meets the keep rule' or names the rule it fails.
- **REPORTED beside (never deciding):** every family's M1 with twins, bias, ln rms, per fold, per card, per E221 placement family; the LOMO
  placebo, 10 draws (default_rng(20261121 + 8000 + i)); **four other learners on the same folds:** a single CART (depth 4, leaf 10, every
  feature, the 'small regression tree', its all-data splits printed), k nearest neighbours (k = 10, features standardized on the training
  rows), the forest on the 17 mask features alone (mtry 6), and **the shape-only control**, the forest on the 5 context features alone
  (mtry 2): the part of the gain no mask feature is needed for; **the feature ranking:** permutation importance (each feature permuted across
  all in-scope points, 3 draws by default_rng(20261121 + 9000 + 100 j + d), re-predicted by every fold's trained forest; the rise in M1 on
  LOSO and LOMO), group drop-out refits on LOSO (count, groups, position, memory distance, link, DRAM private/shared, context), and the
  all-data forest's impurity share per feature.

## 6. The composition with AF4

AF4 (tools/matmul/mm1/v3.3-cands/gemmlnc-af4/, MM1-v3.3 = MM1-v3.2 + AF4 as E222's selection rule chose it) changes the energy of gemmLnc
tokens only and no op time; the reference changes the op time of rgm136 gemmL tokens at subsets only. Their scopes are disjoint by token, so
**'MM1-v3.2 + AF4 + mask-ceiling' is built with no refit**: per point AF4's row at a gemmLnc token, the reference's op time (with MM1-v3.2's
energy law at that time) at an in-scope point, MM1-v3.2 elsewhere. Shown by construction in `scripts/c01_af4.py`: no point of the data or of
E222's and E224's registered point lists is in both scopes, and AF4's frozen E220 forecasts carry MM1-v3.2's op time at every row.

## 7. What is frozen

FROZEN.txt: the sha256 of this file, the code, the params (the all-data forest trained on all 888 in-scope points at the all-data base,
default_rng(20261121), as JSON), the fits (each fold's predictions) and the held-out record, and the time they were final; the land under
tools/matmul/mm1/v3.4-cands/mask-ceiling/ with a predictor for new points (`mask_ceiling.py`: features by f01's code, the factor by the
all-data forest, times MM1-v3.2's own op time). Labelled **'MM1-v3.2 + mask-ceiling (reference, REPORTED)'** whatever the keep rule reads.

SPDX-License-Identifier: Apache-2.0
