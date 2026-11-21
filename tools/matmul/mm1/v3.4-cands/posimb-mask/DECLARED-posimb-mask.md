# DECLARED: 'MM1-v3.2 + posimb-mask', posimb's layout term refitted on the mask data through E224, with one alignment constant (round Q238, lane mask-posimb)

Written Sat 21 Nov 2026 (week 47), Pacific time, at aifoundry2's desk, BEFORE any fit of this form's constants (and before any fit of posimb's
form on this lane's data). Desk only: no card, no simulator, no ssh, no E226 file. Interpreter for every number: /usr/bin/python3 3.12.3,
numpy 1.26.4, `-I -B`, single-threaded (OMP / OPENBLAS / MKL / NUMEXPR_NUM_THREADS = 1), every job in the round's CPU slots, one at a time.

The owner's words that put the matmul first (Mon 16 Nov 2026; a voice transcription in which "matte mold" is the matmul): "I want you to focus
on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles.
From based on what I know about the size of a matrix and which operations are contained."

**The lead.** The lab's blind test of E221 (tools/matmul/mm1/v3.1/blind-e221-scores/, 5eb23fd4): 152 of MM1-v3.2's 175 T1 misses are
core-group mask placements; the MASK class reads 12.41% wall rms on its 363 no-twin cases (every other class at most 9.05%). Q234's frozen
posimb read better there (REPORTED, H1 108/28/325) but was NOT DECIDED in E222.

## 0. What this lane looked at before this file was hashed (disclosed; post hoc, in sample; no constant of any candidate form fitted)

- `x01_e221_look.py`: blind-e221's committed case and run tables (classes against shape and mask; the sessions of each case: 721 cases in one
  session, 12 in two or three; MM1-v3.2's committed per-case wall errors: 12.4090% rms on the 363 MASK no-twin cases).
- `x02_e221_resid.py`: MM1-v3.2's and the frozen posimb's COMMITTED blind wall errors on those 363 cases by shire count, shape, card, kind,
  placement subfamily and single shire (MM1-v3.2 12.41%, frozen posimb 12.14%; one shire 14.19% (+10.32% bias); gemmL3x4x6 28.19%
  (+24.95%), gemmL2x6x10 12.58%; at one shire, gemmL2x6x10's error is -8% to +3% at shires 0, 5, 10, 15, 16, 21, 26 and +9 to +20% at
  the others).
- `x03_check_scan.py`: every committed matmul data JSON E206-E224 scanned for runs whose check of C is missing or not exact/approx: E218 f04's
  run 77 (no check) and E224's p3a/p3b (wrong, both arms) only.
- `x04_look.py`: (1) this lane's MASK-class rule (section 5) against blind-e221's committed classes: equal at all 733 E221 cases (392 MASK,
  341 not); (2) posimb's frozen features made here against layout2's committed `out/private_shared.json`: 306 common configurations, 0
  difference; (3) MM1-v3.2's held-out-base residual ln(T_meas / T_v32) at every MASK point (all-data base for E216-E224, its stored LOEO
  base for its own experiments) by experiment, shire count, single shire (row group s>>2, column group s&3), the share of active shires with
  (s>>2)&3 == s&3, and (row groups, column groups): at one shire, the 79 points at shires with (s>>2)&3 == s&3 read +1.15% mean, the 126
  others -11.73%; at multi-shire masks with no such shire -9.49% (n 90), with one or more +1.3%.
- `x05_look.py`: at the 936 subset MASK points: A1 (no active shire with (s>>2)&3 == s&3) and A2 (no active row group R and column group C
  with R&3 == C) agree at 935 of 936; A1 = 1: rms 13.91%, bias -10.80% (n 216); A1 = 0: 7.24%, +1.27% (n 720); the balance of the walk's
  DRAM-served A and B requests (strict LRU at 32 MB) does not carry the shape dependence (correlation with the residual -0.03); by shape the
  A1 = 1 offset ranges from about 0 (gemmL4x1x10, gemmL2x1x16) to about -25% (gemmL3x4x6).
- `x06_baseline.py`: MM1-v3.2's all-data base at E221's 363 MASK no-twin cases re-made here: 12.4090% rms (the committed 12.4090%; the
  largest case difference 3.3e-6, the case's mean clock against each run's); A1 = 1 at 160 of them (16.59% rms), A1 = 0 at 203 (7.64%).
- `x07_cells.py`: MM1-v3.2's elasticity e (section 2) is 0 at all 257 in-scope 1x1x1 cells and 0.967-1.000 at the 936 other in-scope points.
- `x08_a1share.py` (a count, no residual): A1 = 1 (section 2) at 8 of the 331 in-scope multi-tile points of MM1-v3.2's own experiments
  E206-E215 (E214 4, E215 4), and at E217 34 of 122, E221 162 of 360, E222 6 of 22, E224 6 of 20 (E216, E218, E220: 0).
- Seen, not made here: the frozen posimb's committed constants (a_hop 0.1333, a_lag 0.4367) and records (tools/matmul/mm1/v3.3-cands/posimb/,
  its README and dated note 1), and the round log's result lines on E220, E221, E222 and E224.

The inputs as hashed now (sha256): `work/points_all.json` c3725b15d189658bec1ad888cb093d17f222589e1c70cbdf676ef57d3d8ea657 (by `d01_points.py`
6efcaec4...), `work/base.npz` 3872ff1ac5f1ba58e4389923b218abea6cd249708634bc7ef1f6f7110d386992 (by `e01_base.py` 73522a06...),
`work/private_shared.json` db6829484a71abc29de06ff6ce65e1497999aa8db4e3f6a36861747a1ef72911 (by `f02_run.sh` f974fe7b..., the landed
posimb `f02_private.py` 183a354a... unchanged).

## 1. The base and the scope

- **The base: MM1-v3.2** (tools/matmul/mm1/v3.2/, declaration f8e00a57, model 4e386f75) unchanged: its op time by `time_v31.Engine31`
  (T5r+G0+n32) at its stored constants. **No MM1-v3.2 constant is refitted** (two-stage, as posimb): the term multiplies MM1-v3.2's op time;
  its three constants are fitted on the residuals of MM1-v3.2's own fold bases.
- **Scope** (posimb's, unchanged): a point takes the term iff its mask is a subset (not 0xffffffff), its kernel rgm136 and its arm
  `gemmL<MB>x<NB>x<KB>` (rgm136's cooperative gemmL loop; never gemmLn, gemmLnc or run_gemm). Every other point, and every full-chip point,
  keeps MM1-v3.2's forecast to the last bit. At the in-scope 1x1x1 cells e = 0, so every Phi is 0 there (the cells keep MM1-v3.2's forecast).

## 2. The features (each exactly 0 at the full mask)

- **posimb's two, unchanged** (its DECLARED-posimb.md section 2, a7cd74a0...): per configuration (arm, mask) by the landed
  `f02_private.py` (183a354a...): L(s) = 110 + 12 hbar(s) (shire s's mean hop to the 32 L3 homes on the MARTY map), Lmean_act, Lmax_act over
  the active shires, Lmean_full = 154.953125; Fp, Fs the walk's private and shared DRAM-served request shares (strict LRU at 32 MB, pass 2).
  **G1core = Lmean_act / Lmean_full - 1**; **LAGcore = ((Lmax_act - Lmean_act) / Lmean_full) x Fp / (Fp + Fs)** (0 when Fp + Fs = 0).
- **The new one: A1(mask) = 1 if no active shire s has ((s >> 2) & 3) == (s & 3), else 0.** s >> 2 is the kernel's row group and s & 3 its
  column group (verify-lay's committed `v01_map.groups`: A tiles are shared within a row group, B tiles within a column group); the
  shires with (s >> 2) & 3 == s & 3 are 0, 5, 10, 15, 16, 21, 26 and 31. A1 is 0 at the full chip (all of them active).
- **e** (posimb's): MM1-v3.2's elasticity of its op time to its four mesh-served memory constants at the fold's base constants:
  e = ln(T(theta with c3, m3, cF, mF x 1.01) / T(theta)) / ln(1.01) (`e01_base.py`).
- **Phi_hop = e x G1core; Phi_lag = e x LAGcore; Phi_al = e x A1.**

## 3. The form (three constants: a_hop, a_lag as posimb's, refitted; a_al new)

- wall op time: **T = T_v32 x g_w**, g_w = clip(1 + a_hop Phi_hop + a_lag Phi_lag + a_al Phi_al, 0.3, 3.0) (wall cycles an op, the op time,
  seconds a GEMM);
- the counter's mean cycles an op: MM1-v3.2's mean x g_m, g_m = clip(1 + a_hop Phi_hop + a_al Phi_al, 0.3, 3.0) (posimb's position part, and
  the alignment part: when no active shire sits on (s>>2)&3 == s&3, every active shire takes it; Phi_lag is the wall's excess over the mean);
- energy: MM1-v3.2's W over idle at an op time t (A_W + B_W / t, its own A_W and B_W unchanged) at the term's t, J over idle = W x seconds,
  J at rest = (P_rest + W) x seconds (MM1-v3.2's rest law): posimb's `h01_freeze.compose`.
- **Why the third constant (stated before the fit, from section 0's looks):** MM1-v3.2 prices a shire subset at the speed of masks that hold a
  shire with (s>>2)&3 == s&3 (its own subset data: 323 of the 331 in-scope multi-tile points of E206-E215 hold such a shire), while masks
  holding none run about 11% faster on average (E221's single shires off that set, e.g. gemmL3x4x6 at 0x4000 forecast +45%; the gemmL2x6x10
  pair 0x44 against 0x22 that posimb's README names as unexplained, 0.21 ln); posimb's two features cannot see it (G1core is a mesh-latency
  mean; LAGcore is 0 at one shire). A reading, NOT established here (it needs the panels' base addresses and the caches' set and the DRAM's
  bank mapping): in `v01_map.my_steps` a row group R's A tiles sit at tile offsets (8R + 2d + r) KT + k from their block base and a column
  group C's B tiles at (8C + p) KT + k, so a shire with R = C mod 4 has its A and B streams at equal offsets modulo 32 KT tiles; if the bases
  agree there too, the two streams would compete for the same cache sets or DRAM banks. The wall is the slowest active shire's, so one such
  shire sets it.
- **Expected signs (reported, not a rule):** a_al < 0 (A1 masks faster than MM1-v3.2 forecasts); a_hop > 0; a_lag > 0.
- **Bounds:** none on the constants; the factors clipped to [0.3, 3.0] (posimb's). **Starts:** none (linear least squares, one minimum).

## 4. The fit (post hoc as an act)

a = argmin over the fold's training points of sum_j (rho_j (1 + Phi_j a) - 1)^2, rho_j = T_base,j / T_meas,j (posimb's `fit_consts`, numpy
lstsq), over every training point (out-of-scope points have Phi = 0 and do not move a), E146's 87 store rungs out (MM1-v3.2's own
`store_rung_ids`). The data: every committed matmul time point through E224, `work/points_all.json` (4311 points): MM1-v3.2's 2508
(E105-E215 with E214, its fit's ids), E216 46, E217 486 cases, E218 52, E219 139, E220 156 (arm A 84; arm B 72 at route c), E221 733 cases,
E222 70, E224 121 (arm A 62, arm B 59: p3a and p3b out, every run's check of C wrong; arm B's route-m-only d06, d17 out); every run whose check
of C is missing or not exact/approx dropped first (E218 f04's run 77).

## 5. The MASK class (blind-e221's definition, applied by this lane's code to every point)

A point is **MASK** iff (a) it is an rgm136 gemmL point at a subset mask whose shape is not 1x1x1, or (b) it is an rgm136 gemmL point at the
full mask and a point of (a) in the same experiment has its card, arm, format and kind (its whole-chip twin). At E221 this equals blind-e221's
committed class at all 733 cases (section 0). Everything else is non-MASK.

## 6. The folds (held out) and the bases (`work/base.npz`)

- **LOSO-E221** (the lead's folds): nine folds, one per E221 session (a1c1-S1..S3, a1c0-S1..S3, a2c0-S1..S3): test = the E221 cases with a run
  in that session; train = every point but the E221 cases with any run in it; base = MM1-v3.2's all-data constants (E221 never in its fit). A
  case run in two or three sessions is tested in each of their folds; its held-out prediction is the mean of those folds' predicted op times.
- **LOEO**: one fold per experiment (29: E105 ... E224; E215-E224 named in every table); base = MM1-v3.2's stored 'LOEO <exp>' constants for its
  own 20 experiments, its all-data constants for E216-E224.
- **LOCO**: one fold per card (4); base = MM1-v3.2's stored 'LOCO <card>' constants.
- **LOMO**: one fold per subset mask that E221, E217 or E224 ran: test = every rgm136 gemmL point at that mask (every experiment and card);
  train = the rest; base = MM1-v3.2's all-data constants (disclosed: E212/E214/E215 points at such masks were in MM1-v3.2's fit; MM1-v3.2 has
  no mask-specific constant). The masks are listed in the fit record.
- REPORTED beside: LOLO (compact / spread / other by `fit_v31.lolo_class`, at MM1-v3.2's stored LOLO constants) and posimb's lead fold LO-Y
  (E216 + E218 out, all-data base) with posimb's 15 lead pairs.
- **Twins:** (a) the headline set is E221's 363 MASK cases that blind-e221 scored as no-twin for MM1-v3.2 (`twin_time_v32` 0); (b) everywhere
  else posimb's definition: a point is a twin if another experiment holds a point of the same card, kernel, arm, format and mask; every
  pooled figure is printed with and without twins; the guards read without.

## 7. The metrics, the margins and the keep rule (stated before fitting)

- **M1** (the lead, held out by LOSO-E221): rms of T^ / T_meas - 1 (%) over E221's 363 cases. MM1-v3.2's M1 = 12.4090%.
- **M1L** (new masks, held out by LOMO): the same 363 cases with the LOMO predictions (a full-chip case keeps MM1-v3.2's forecast).
- **M2** (the brief's guard): rms (%) of the LOEO prediction's error over every non-MASK point without a twin, pooled over the LOEO folds.
  (By section 1, the term moves no non-MASK point with e > 0: M2 is expected to equal MM1-v3.2's; it is computed, not assumed.)
- **M4** (this lane's added guard): the same over every MASK point outside E221 without a twin (the other experiments' masks).
- **M3** (the placebo): 100 draws i = 0..99; in draw i, within each arm, the in-scope points' feature triples (G1core, LAGcore, A1) are
  permuted among that arm's in-scope points by numpy.random.default_rng(20261121 + i).permutation; Phi = e x the permuted triple; the nine
  LOSO-E221 folds refitted; M1 recomputed.
- **KEEP iff all five:** **K1** M1 <= 12.4090 - 1.00 = **11.4090%** (the margin: one point, a twelfth of the lead's error); **K1L** M1L <=
  12.4090 - 0.50 = **11.9090%**; **K2** M2 <= MM1-v3.2's M2 + 0.05 points; **K4** M4 <= MM1-v3.2's M4 + 0.05 points; **K3** the real M1 below
  the placebo's M1 in at least 95 of the 100 draws. Otherwise the term is a rejected candidate: frozen and reported as such.
- **REPORTED beside (never deciding):** posimb's frozen form refitted with its two constants only ('posimb-refit': a_al fixed at 0) and the
  alignment term alone ('align-only': a_hop = a_lag = 0), by the same procedure on the same folds (M1, M1L, M2, M4, the placebo for
  posimb-refit with the pair (G1core, LAGcore) permuted the same way); the frozen posimb at its own constants (no fit); every fold's
  constants and their signs; LOEO by fold, LOCO by card, LOLO, LO-Y with posimb's lead pairs; the MASK held-out rms by experiment, card,
  shire count, row groups, column groups, spread and shape (what the features miss); the counter's mean where measured.

## 8. The freeze and the composition with AF4

- The all-data constants (the fit on every point at MM1-v3.2's all-data base) are the term's parameters. FROZEN.txt names the sha256 of
  this declaration, the code (the predictor module and the fit script), the params, the fits (every fold's constants) and the held-out record,
  and the time they were final; labelled 'MM1-v3.2 + posimb-mask' if KEPT, 'MM1-v3.2 + posimb-mask (rejected candidate)' if not.
- 'MM1-v3.2 + AF4 + posimb-mask' **by construction, no refit**: the term acts only at rgm136 gemmL subset points (time, and MM1-v3.2's affine
  energy at the term's op time), AF4 (tools/matmul/mm1/v3.3-cands/gemmlnc-af4/, its frozen per-row form as E222's `desk/models_e222.py`
  applies it) only at gemmLnc points (energy, F3 replaced): disjoint scopes, so each row is the one that acts (refused, exit 5, if any row
  had both in scope or a term moved a row outside its scope). Shown on E222's 70 and E224's 127 registered points at their registered clocks
  (post hoc: their data are in the fit; REPORTED, not a forecast).

SPDX-License-Identifier: Apache-2.0
