# DECLARED: 'MM1-v3.2 + mesh', a placement term for core-group masks from the L3's set map and the mesh (round Q238, lane mask-mesh, track M)

Written Sat 21 Nov 2026 (week 47), Pacific time, at aifoundry2's desk, BEFORE any fit of this form's constants and before any held-out
number of it exists. Desk only: no card, no simulator, no ssh. Interpreter `/usr/bin/python3` 3.12.3, numpy 1.26.4, scipy 1.11.4, `-I -B`,
single-threaded (OMP / OPENBLAS / MKL / NUMEXPR_NUM_THREADS = 1), every numerical job inside the round's CPU slots, one at a time.
Labels: *known* (a committed measurement or a documented fact, cited), *assumed* (named as such), *post hoc* (every constant; the form was
chosen after the looks disclosed in section 0), *held out* (left out of the fit that scores it; not blind), *REPORTED* (printed beside a
rule, never deciding it).

## 0. What was looked at before this was written (disclosed)

1. `scripts/x01_e221_look.py` (log `logs/x01.log`): MM1-v3.2's committed BLIND wall errors on E221's MASK class by placement family and
   mask, all three cards (blind-e221's case table, 5eb23fd4). Seen: at gemmL2x6x10 (PLA, PLX, PLK, PLK3) all 26 single-shire masks read,
   and the shires split into two sets on all three cards alike: shires 0, 5, 10, 15, 16, 21, 26, 31 (those whose row group s >> 2 equals
   their column group s & 3 modulo 4) read about MM1-v3.2 (-7.8 to +3.6%), the other 18 read 8.6-20.3% faster than it; the same split at
   gemmL1x12x8 (PLB) and gemmL3x4x6 (PLM, +10 vs +34 to +46%); no split at gemmL2x1x16, 2x4x24, 1x16x6, 4x1x10 (PLC, PLD, PLE) nor at the
   L3-resident 4x6x2 and 1x3x4 (PLH, PLL, which read a uniform +6 to +22%); within the fast set the error falls as the shire's mean hop to
   the L3 homes grows (14 at 2.81 hops +18%, 28 at 4.5 hops +11%); same-row pairs run balanced (wall / mean 1.000), same-column pairs with
   one shire of the first set do not (1.08-1.10); the 8-24-shire masks with fewer than four column groups read 10-19% SLOWER than MM1-v3.2.
2. `scripts/x02_single_look.py` (log `logs/x02.log`): the mechanism's own numbers (section 1, no fitted constant) at those shapes' single
   shires and full chips. Seen: the set-associative L3 model reproduces the split exactly (at gemmL2x6x10 the eight shires above miss
   0.61-0.62 of their A requests and 0.565 of B; the other 24 miss 0.167 and 0.500; the full chip's laggard 0.66 and 0.65; the fully
   associative LRU reads 0 at every single shire); at 1x16x6 and 4x1x10 one operand misses at 1.0 at every shire (no split); at 2x4x24
   everything misses at both ends.
3. `scripts/m02_features.py`: this form's features at all 458 subset configurations of the data and their 142 full-chip references
   (`work/features-mesh.json`, sha256 in `DECLARED.sha256.json`): computed, NOT compared with any residual.
4. `scripts/t02_smoke.py` (log `logs/t02.log`): the re-made engine equals MM1-v3.2's at zero term at the all-data constants and two stored
   folds (max relative difference 0.0 over the 1,193 scope points); the fit recovers constants from STAND-IN op times made by the term
   itself (a_set 0.70 -> 0.706, a_hop 0.30 -> 0.311 at 1% noise). No measured op time entered t02.
No constant of this form was fitted and no held-out number of it was computed before this file and the code were hashed.

## 1. The mechanism: what is known and what is assumed

- **Known (the lab's committed memory-levels report, 2026-09-28, citing the shire cache specification v1.1; default swizzle0):** a line's L3
  home shire is PA[10:6]; within the home, bank PA[12:11], sub-bank PA[14:13], set PA[22:15] (256 L3 sets a sub-bank in Mode 0), 4 ways.
  So the 32 MiB L3 is 4-way set associative over 131,072 sets with an 8 MiB aliasing period: a 1 KiB tile's 16 lines lie in 16 homes at one
  set index, and two tiles compete for the same 4 ways iff their tile index (PA >> 10) agrees mod 8,192. **Assumed:** the cards run that
  default decode, and LRU replacement.
- **Known (MM1-v3.1's masked walk, tools/matmul/mm1/v3.1/walk/, trace check PASS):** every active minion's tile order and addresses
  (pool-relative), the cooperation groups, which active shires share each tile (an A tile by the active shires of its row group, a B tile by
  those of its column group). `scripts/test_mesh_l3.py` checks this lane's stream against `walk_v31.chip_steps` request for request (7 of 7
  shapes and masks EQUAL).
- **Known for the simulator, assumed for the card:** the host's pools sit back to back, C, then A, then B (A0 = C0 + 2 MiB MB NB,
  B0 = A0 + 2 MiB MB KB), in every traced sys_emu run (walk/traces/runs/*/check.json bases); the card's host runs the same runtime allocator.
  Only the pools' offsets mod 8 MiB matter.
- **Known (docs/et-soc1-notes.md, measured on three cards):** the 32 compute shires sit on marty1885's map; an L3 hit costs
  110 + 12 x hops(requester, home) cycles; the DRAM leg past the L3 91 + 12 x hops(home, memory shire PA[8:6]); lines interleave uniformly
  over the 32 homes (so a shire's mean L3 latency is L(s) = 110 + 12 hbar(s), hbar its mean hop to the homes) and over the 8 memory shires
  (so no slice or controller is hotter than another at any mask: verify-lay's finding, max = mean). **Assumed, REPORTED only:** dimension-
  order routes (X then Y on that map) for the per-link loads.
- **Assumed (the walk's convention):** the steady state is the second pass; a tile asked by w shires in one step is one L3 request (the
  others in flight); every distinct tile request of a step enters the L3 (the shires' L2s are not filtered here); C's TensorStores allocate.
- **What the mechanism says:** for rgm136's gemmL tiles, A's tile at (row, k) and B's at (col, k) fall in the same 4-way L3 sets exactly
  when row ≡ col (mod 32) at the pools' offsets, i.e. for a shire whose row group is its column group mod 4, its own A and B streams evict
  each other; and a subset's mask decides which A and B tiles are live at all. MM1-v3.2's place map (Q0, Q1) is the same at every mask
  (its ShapeBank is keyed by arm only) and its subset terms are n / 32 contention (chi3, chiF) and the row term eta, so it sees neither.

## 2. The base and the scope

- **The base:** MM1-v3.2 (tools/matmul/mm1/v3.2/, declaration f8e00a57, model 4e386f75, params c991de16) unchanged: its op time by
  `time_v31.Engine31` (T5r+G0+n32) at each fold's constants (section 5). **No MM1-v3.2 constant is refitted** (two-stage): the term's two
  constants are fitted on the residuals of MM1-v3.2's own fold bases. Why two-stage: the term acts only at subset points; MM1-v3.2's time fit
  takes 18 starts a fold over 19 constants; the term is priced by MM1-v3.2's own place times, so a joint refit would let those times absorb it.
- **Scope:** a point takes the term iff `layout_v32.is_layout_point` (a subset mask, kernel rgm136, arm gemmL<MB>x<NB>x<KB>). Every other
  point - every full-chip point, every gemmLnc, rgm211 and run_gemm point - keeps MM1-v3.2's op time to the last bit.

## 3. The features (no fitted constant; `scripts/mesh_l3.py`, `scripts/mesh_term.py` point_features 'laggard')

Per configuration (arm, mask), from the walk's stream through the set-associative L3 (SA, section 1), second pass: for each active shire s,
xA(s) = the share of its A tile requests (its row group's) that miss, xB(s) = of its B requests (its column group's). **The laggard** s* =
the active shire with the largest xA + xB (ties: the larger hbar, then the lower id). The same arm at the full chip has its own laggard.
- dA = xA(s*) - xA_full(s*_full), dB = xB(s*) - xB_full(s*_full);
- g3 = 12 (hbar(s*) - hbar(s*_full)) / (110 + 12 hbar(s*_full)); gF = 12 (hbar(s*) - hbar(s*_full)) / (110 + 12 hbar(s*_full) + 91 + 12 hmem),
  hmem = 2.625 the mean hop from a home to its memory shire (PA[8:6] = the home's low three bits).
All four are exactly 0 at the full chip (and off the scope).

## 4. The form (two new constants: a_set, a_hop)

MM1-v3.2's op time re-made by its own engine (`mesh_term.Base`, equal to Engine31.predict at zero term) with:
- **the place map moved:** a_set dA of A's ops moved from MM1-v3.2's L3 place to its fresh (DRAM) place when positive, from fresh to L3 when
  negative, proportionally over B's places, never more than the place holds; then a_set dB of B's (over A's places);
- **the latencies moved:** c3 -> c3 (1 + a_hop g3), cF -> cF (1 + a_hop gF) in MM1-v3.2's L3 and DRAM place times;
- everything else (m3, mF, chi3, chiF, the L2, the census path, kA, the max structure, eta) MM1-v3.2's.
**Wall op time T = that engine's output.** The counter's mean = T / MM1-v3.2's rho (unchanged); seconds a GEMM = ops x T. Energy: MM1-v3.2's
W over idle at an op time t is its W_affine A + B / t, unchanged: given a measured t it is MM1-v3.2's; with t forecast it is read at this T.
**Bounds:** a_set in [-1, 4], a_hop in [-2, 4]. **Expected signs (physics, stated before the fit; reported, not a rule):** both positive,
each near 1 if the walk's L3 and the latency laws are the card's in size.
**Starts:** (a_set, a_hop) = (1, 1) (the mechanism's own size) and (0, 0) (no term); the lower cost wins (ties: the first).
**The fit:** scipy.optimize.least_squares ('trf', bounded, diff_step 1e-6) of ln(T / T_measured) over the fold's training points in the
scope (the out-of-scope points have no term and do not move a constant).

## 5. The data, the classes, the twins

- Every committed matmul time point through E224 (`work/points-mesh.json`, `scripts/m01_points.py`, from the snapshot of GitHub main at
  cfd7e641): 4,311 points; E105-E219 as Q234's layout2 lane landed them (3,231, `posimb/out/points_all.json` 79345900...: MM1-v3.2's own
  2,508, E216, E217's and E219's blind case tables, E218); E220 both arms (the committed scorer's measured record, route c on arm B); E221's
  733 cases (blind-e221's case table, with each case's sessions); E222 (70); E224 arm A (62) and arm B (59, by E208's registered reducer
  b9e32618 / c3fc7883 on the committed session, route c). **Excluded:** every run whose check of C is not exact or approx (4 a card at E224:
  p3a, p3b both passes), and E224's p3a and p3b by name; E146's store rungs are full-chip points (out of the scope). 1,193 points are in the
  scope (160 masks).
- **The MASK class** (this lane's rule, applied by its code to every point): E221's cases take decl-e221's class (MASK = arm family PL); any
  other point is MASK iff a subset point of rgm136 gemmL that is neither a 1x1x1 cell nor an int8 gemmL1x1xKB point, or a full-chip rgm136
  gemmL point whose (experiment, card, arm, format, kind) also holds such a subset point. The rule reproduces decl-e221's column at all 733
  of E221's cases (392 MASK). 1,013 points are MASK.
- **The lead:** E221's 363 MASK cases without an MM1-v3.2 twin (blind-e221's flag; MM1-v3.2 12.41% wall rms there, BLIND).
- **Twins:** (i) the lead's flag above; (ii) for every point, a twin iff another experiment holds a point of the same card, kernel, arm,
  format and mask (posimb's rule); every pooled figure is printed with and without (ii); the guard reads without.

## 6. The folds and their bases

- **LOMO (the primary):** one fold per distinct subset mask that E221, E217 or E224 ran (115): test = every scope point at that mask (every
  experiment, card and shape), train = every other scope point; base = MM1-v3.2's all-data constants (E216-E224 never entered its fit).
- **LOSO:** one fold per E221 session (9): test = the E221 cases with a run in it; train = every scope point but those; each case's held-out
  op time from the fold of its first session; base all-data.
- **LOEO:** one fold per experiment (E105 ... E224): test = its points; train = the other experiments' scope points; base = MM1-v3.2's stored
  'LOEO <exp>' constants where they exist (E105-E215), else all-data; the term fitted at that base. The MASK figures read over E215-E224.
- **LOCO:** one fold per card (4): test = every point of the card; base = MM1-v3.2's stored 'LOCO <card>' constants for every point; train =
  the other cards' scope points at that base.
- Points out of the scope read the fold base's MM1-v3.2 op time in every fold.

## 7. The metrics, the margin, the keep rule, the placebo (stated before fitting)

Error = forecast / measured - 1 of the wall op time; rms in %.
- **K1 (the margin):** the lead's (363 cases) LOMO rms <= MM1-v3.2's rms on the same cases minus **1.0 point** (12.41% -> at most about 11.4%).
- **K2:** the lead's rms under LOSO, under LOEO and under LOCO each below MM1-v3.2's on the same cases (no margin).
- **K3 (the guard):** the rms over every non-MASK point without a twin (ii), under LOEO, at most MM1-v3.2's own LOEO rms there + 0.05 points.
- **K4 (the placebo):** 100 draws d = 0..99: within each arm, its subset masks' feature vectors (dA, dB, g3, gF) permuted among its masks by
  numpy.random.default_rng(20261121 + d).permutation over the arm's sorted masks (every point at a mask takes the permuted mask's vector);
  LOMO refitted; K1's rms recomputed. The real K1 rms below the placebo's in **at least 95 of 100** draws.
- **KEEP iff K1, K2, K3 and K4.** Otherwise the term is a **rejected candidate**: frozen and REPORTED as such.

## 8. REPORTED beside (never deciding)

The in-sample fit and its constants; each fold's constants; the lead and every MASK point under each fold, with and without twins; the
non-MASK scope points; five controls fitted and held out (LOMO) by the same procedure: the chip's request-weighted SA shares with the active
mean's hop, the fully associative LRU instead of the sets (the walk's strict LRU: lay-contention's F1 kind), the form with the active mean's
hop, sets only (a_hop = 0), hop only (a_set = 0); **posimb beside** on the lead's subset cases (its frozen, blind errors from blind-e221's
case table against this term's LOMO ones, post hoc), by placement family and shire count: the rms of each and the cases each brings closer
than MM1-v3.2 by more than 1 point (which masks each explains); the per-link loads (XY) and the memory-shire distance as features beside.

## 9. What freezes

`FROZEN.txt` lists the sha256 of this file, the code (`scripts/*.py` and `*.sh` the procedure ran), the params (`params-mesh.json`), the fits
(`fit-mesh.json`), the held-out record (`holdout-mesh.json`), the per-point record, the features cache and the point table, and the time
they were final - also when the term is not kept (then labelled a rejected candidate). The composition with AF4 ('MM1-v3.2 + AF4 + mesh')
is shown by construction, no refit (`scripts/compose_af4.py`): AF4 changes W over idle at rgm136 gemmLnc points only and no op time; this
term changes the op time of cooperative gemmL subset points only; no point is in both.

SPDX-License-Identifier: Apache-2.0
